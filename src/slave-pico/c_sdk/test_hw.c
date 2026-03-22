/**
 * GridBox — Combined Hardware Test (C SDK)
 * Tests: Heartbeat LED + nRF24L01+ + MAX7219 7-Segment Display
 *
 * LED blinks throughout (timer interrupt, zero CPU cost).
 * Display shows live test status.
 * nRF SPI is verified with register read/write.
 *
 * Build: cmake --build build --target test_hw
 * Flash: copy build/test_hw.uf2 to RPI-RP2 drive
 */

#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "hardware/gpio.h"
#include "hardware/timer.h"

#include "config.h"
#include "max7219.h"

/* ============ Heartbeat LED (Timer-driven) ============ */

#define HB_PIN LED_ONBOARD  /* GP25 onboard LED */

typedef enum {
    HB_BOOT,     /* fast 80ms — starting up */
    HB_NORMAL,   /* slow 400ms — all good */
    HB_ACTIVE,   /* medium 100ms — SPI activity */
    HB_FAULT,    /* rapid 120ms — error */
} hb_state_t;

static volatile hb_state_t hb_state = HB_BOOT;
static volatile hb_state_t hb_base_state = HB_BOOT;
static volatile uint32_t hb_active_until = 0;
static volatile bool hb_led_on = false;
static volatile uint32_t hb_last_toggle = 0;

static uint32_t hb_rate_ms(hb_state_t s) {
    switch (s) {
        case HB_BOOT:   return 80;
        case HB_NORMAL: return 400;
        case HB_ACTIVE: return 100;
        case HB_FAULT:  return 120;
        default:        return 400;
    }
}

static bool hb_timer_callback(repeating_timer_t *rt) {
    (void)rt;
    uint32_t now = to_ms_since_boot(get_absolute_time());

    /* Auto-revert from active to base state */
    if (hb_state == HB_ACTIVE && now >= hb_active_until) {
        hb_state = hb_base_state;
    }

    uint32_t rate = hb_rate_ms(hb_state);
    if (now - hb_last_toggle >= rate) {
        hb_led_on = !hb_led_on;
        gpio_put(HB_PIN, hb_led_on);
        hb_last_toggle = now;
    }
    return true;  /* keep repeating */
}

static repeating_timer_t hb_timer;

static void heartbeat_init(void) {
    gpio_init(HB_PIN);
    gpio_set_dir(HB_PIN, GPIO_OUT);
    /* 10ms timer = 100Hz check rate */
    add_repeating_timer_ms(-10, hb_timer_callback, NULL, &hb_timer);
}

static void heartbeat_set_state(hb_state_t state) {
    hb_base_state = state;
    hb_state = state;
}

static void heartbeat_activity(uint32_t duration_ms) {
    hb_state = HB_ACTIVE;
    hb_active_until = to_ms_since_boot(get_absolute_time()) + duration_ms;
}

/* ============ nRF24L01+ bare SPI (test only) ============ */

static void nrf_spi_init(void) {
    spi_init(spi0, 1000000);
    gpio_set_function(SPI_SCK,  GPIO_FUNC_SPI);
    gpio_set_function(SPI_MOSI, GPIO_FUNC_SPI);
    gpio_set_function(SPI_MISO, GPIO_FUNC_SPI);

    gpio_init(NRF_CSN);
    gpio_set_dir(NRF_CSN, GPIO_OUT);
    gpio_put(NRF_CSN, 1);

    gpio_init(NRF_CE);
    gpio_set_dir(NRF_CE, GPIO_OUT);
    gpio_put(NRF_CE, 0);
}

static uint8_t nrf_read_reg(uint8_t reg) {
    uint8_t tx[2] = {reg & 0x1F, 0xFF};
    uint8_t rx[2] = {0, 0};
    gpio_put(NRF_CSN, 0);
    sleep_us(10);
    spi_write_read_blocking(spi0, tx, rx, 2);
    gpio_put(NRF_CSN, 1);
    sleep_us(10);
    return rx[1];
}

static void nrf_write_reg(uint8_t reg, uint8_t val) {
    uint8_t tx[2] = {0x20 | (reg & 0x1F), val};
    gpio_put(NRF_CSN, 0);
    sleep_us(10);
    spi_write_blocking(spi0, tx, 2);
    gpio_put(NRF_CSN, 1);
    sleep_us(10);
}

/* ============ Status LEDs ============ */

static void status_leds_init(void) {
    gpio_init(LED_RED);
    gpio_set_dir(LED_RED, GPIO_OUT);
    gpio_put(LED_RED, 0);

    gpio_init(LED_GREEN);
    gpio_set_dir(LED_GREEN, GPIO_OUT);
    gpio_put(LED_GREEN, 0);
}

/* ============ Main Test ============ */

int main(void) {
    stdio_init_all();
    sleep_ms(1000);  /* wait for USB serial */

    /* Start heartbeat (boot = fast blink) */
    heartbeat_init();

    /* Init status LEDs */
    status_leds_init();

    printf("==================================================\n");
    printf("  GridBox C SDK — Combined Hardware Test\n");
    printf("  nRF24L01+ (SPI0) + MAX7219 (SPI1) + LED\n");
    printf("==================================================\n");

    /* ---- Init MAX7219 display ---- */
    printf("\n1. Init MAX7219 display (SPI1)...\n");
    max7219_t disp;
    if (max7219_init(&disp, spi1, 13)) {
        printf("   MAX7219 — OK\n");
        max7219_show(&disp, "BOOT");
    } else {
        printf("   MAX7219 — FAILED\n");
    }
    sleep_ms(1000);

    /* ---- Init nRF24L01+ ---- */
    printf("\n2. Init nRF24L01+ (SPI0)...\n");
    max7219_show(&disp, "tESt SPI");
    nrf_spi_init();
    printf("   SPI0 — OK\n");
    sleep_ms(500);

    /* ---- Read status register 10 times ---- */
    printf("\n3. Reading nRF status register (10 attempts)...\n");
    max7219_show(&disp, "rEAd nrF");
    sleep_ms(500);

    uint8_t results[10];
    for (int i = 0; i < 10; i++) {
        results[i] = nrf_read_reg(NRF_STATUS);
        heartbeat_activity(200);

        /* Show hex value on display */
        char buf[9];
        snprintf(buf, sizeof(buf), "  0x%02X  ", results[i]);
        max7219_show(&disp, buf);

        printf("   #%d: status = 0x%02X\n", i + 1, results[i]);
        sleep_ms(200);
    }

    /* ---- Write/read channel test ---- */
    printf("\n4. Write/read channel test...\n");
    max7219_show(&disp, "CHAnnEL");
    sleep_ms(500);

    nrf_write_reg(NRF_RF_CH, 100);
    sleep_ms(1);
    uint8_t channel = nrf_read_reg(NRF_RF_CH);
    heartbeat_activity(200);
    printf("   Wrote channel=100, read back=%d\n", channel);

    /* ---- Verdict ---- */
    printf("\n==================================================\n");

    bool has_valid = false;
    bool all_ff = true;
    bool all_00 = true;

    for (int i = 0; i < 10; i++) {
        if (results[i] >= 0x01 && results[i] <= 0x7F) has_valid = true;
        if (results[i] != 0xFF) all_ff = false;
        if (results[i] != 0x00) all_00 = false;
    }

    if (has_valid && channel == 100) {
        printf("  PASS — nRF24L01+ is working!\n");
        printf("  Status OK + write/read verified\n");
        max7219_flash(&disp, "LINK On", 3, 300, 200);
        max7219_show(&disp, "PASS");
        heartbeat_set_state(HB_NORMAL);
        gpio_put(LED_GREEN, 1);
        gpio_put(LED_RED, 0);

    } else if (all_ff) {
        printf("  FAIL — 0xFF: module not responding\n");
        printf("  Check: VCC->3V3, GND, MISO->GP16, CSN->GP1\n");
        max7219_flash(&disp, "LINK OFF", 5, 300, 200);
        max7219_show(&disp, "FAIL  FF");
        heartbeat_set_state(HB_FAULT);
        gpio_put(LED_GREEN, 0);
        gpio_put(LED_RED, 1);

    } else if (all_00) {
        printf("  FAIL — 0x00: SPI issue\n");
        printf("  Check: SCK->GP2, MOSI->GP3, MISO->GP16\n");
        max7219_flash(&disp, "SPI FAIL", 5, 300, 200);
        max7219_show(&disp, "FAIL  00");
        heartbeat_set_state(HB_FAULT);
        gpio_put(LED_GREEN, 0);
        gpio_put(LED_RED, 1);

    } else if (has_valid && channel != 100) {
        printf("  PARTIAL — status OK but channel=%d (expected 100)\n", channel);
        max7219_flash(&disp, "LoOSE", 5, 300, 200);
        max7219_show(&disp, "FAIL");
        heartbeat_set_state(HB_FAULT);
        gpio_put(LED_GREEN, 0);
        gpio_put(LED_RED, 1);

    } else {
        printf("  UNSTABLE — loose wire\n");
        max7219_flash(&disp, "LoOSE", 5, 300, 200);
        max7219_show(&disp, "FAIL");
        heartbeat_set_state(HB_FAULT);
        gpio_put(LED_GREEN, 0);
        gpio_put(LED_RED, 1);
    }

    printf("==================================================\n");
    printf("\nLED + display will keep running. Reset to stop.\n");

    /* Keep running forever */
    while (true) {
        sleep_ms(1000);
    }

    return 0;
}
