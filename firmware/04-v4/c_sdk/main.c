/**
 * GridBox — Slave Pico (Pico B) — C SDK Production Firmware
 * SCADA station: receives wireless telemetry, displays on OLED,
 * reads joystick/pot, sends commands to master.
 * Ported from MicroPython slave firmware.
 */

#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include "hardware/spi.h"
#include "hardware/adc.h"
#include "hardware/gpio.h"

#include "config.h"
#include "ssd1306.h"
#include "nrf24l01.h"

/* ============ Device handles ============ */

static ssd1306_t oled;
static nrf24l01_t radio;

/* ============ Received telemetry state ============ */

typedef struct {
    float bus_v;
    float m1_mA, m2_mA;
    float m1_W, m2_W, total_W;
    float accel_rms;
    float temperature;
    uint8_t fault_level;
    uint8_t efficiency;
    uint8_t mosfet_states;
    bool connected;
    uint32_t last_rx_ms;
} telemetry_t;

static telemetry_t telem = {0};

/* ============ Joystick + Potentiometer ============ */

typedef struct {
    int16_t x;       /* -100 to +100 */
    int16_t y;       /* -100 to +100 */
    bool button;
    uint8_t pot;     /* 0-100% */
} input_t;

static input_t read_inputs(void) {
    input_t in;

    /* Joystick X */
    adc_select_input(0);  /* GP26 */
    uint16_t raw_x = adc_read();
    /* Joystick Y */
    adc_select_input(1);  /* GP27 */
    uint16_t raw_y = adc_read();
    /* Potentiometer */
    adc_select_input(2);  /* GP28 */
    uint16_t raw_pot = adc_read();

    /* Map to -100..+100 with deadzone */
    int16_t cx = (int16_t)raw_x - JOY_CENTRE;
    int16_t cy = (int16_t)raw_y - JOY_CENTRE;

    if (cx > -JOY_DEADZONE && cx < JOY_DEADZONE) cx = 0;
    if (cy > -JOY_DEADZONE && cy < JOY_DEADZONE) cy = 0;

    in.x = (cx * 100) / JOY_CENTRE;
    in.y = (cy * 100) / JOY_CENTRE;
    if (in.x > 100) in.x = 100;
    if (in.x < -100) in.x = -100;
    if (in.y > 100) in.y = 100;
    if (in.y < -100) in.y = -100;

    in.button = !gpio_get(JOY_BTN_PIN);  /* active low */
    in.pot = (uint8_t)((uint32_t)raw_pot * 100 / 4095);

    return in;
}

/* ============ Parse telemetry packet ============ */

static void parse_telemetry(uint8_t *pkt) {
    if (pkt[0] != 0x01 && pkt[0] != 0x02) return;  /* DATA or HEARTBEAT */

    telem.fault_level = pkt[1];
    telem.bus_v = (float)(pkt[2] | (pkt[3] << 8)) / 100.0f;
    telem.m1_mA = (float)(pkt[4] | (pkt[5] << 8));
    telem.m2_mA = (float)(pkt[6] | (pkt[7] << 8));
    telem.m1_W = (float)(pkt[8] | (pkt[9] << 8)) / 100.0f;
    telem.m2_W = (float)(pkt[10] | (pkt[11] << 8)) / 100.0f;
    telem.total_W = (float)(pkt[12] | (pkt[13] << 8)) / 100.0f;
    telem.accel_rms = (float)(pkt[14] | (pkt[15] << 8)) / 1000.0f;
    telem.temperature = (float)(int16_t)(pkt[16] | (pkt[17] << 8)) / 10.0f;
    telem.mosfet_states = pkt[18];
    telem.efficiency = pkt[19];
    telem.connected = true;
    telem.last_rx_ms = to_ms_since_boot(get_absolute_time());
}

/* ============ Build command packet ============ */

static void build_command(uint8_t *pkt, uint8_t cmd, uint8_t param) {
    memset(pkt, 0, NRF_PAYLOAD_SIZE);
    pkt[0] = 0x05;   /* COMMAND type */
    pkt[1] = cmd;
    pkt[2] = param;
}

/* ============ OLED display ============ */

static const char *fault_str[] = {"OK", "WARN", "CRIT", "FAIL"};

static void update_display(input_t *in) {
    ssd1306_fill(&oled, 0);

    /* Header */
    ssd1306_text(&oled, "GridBox SCADA", 20, 0, 1);
    ssd1306_hline(&oled, 0, 9, 128, 1);

    if (!telem.connected) {
        ssd1306_text(&oled, "NO SIGNAL", 28, 28, 1);
        ssd1306_show(&oled);
        return;
    }

    /* Line 1: Bus voltage + fault */
    char line[22];
    snprintf(line, sizeof(line), "Bus:%.1fV %s",
             telem.bus_v, fault_str[telem.fault_level & 0x03]);
    ssd1306_text(&oled, line, 0, 12, 1);

    /* Line 2: Motor currents */
    snprintf(line, sizeof(line), "M1:%3.0fmA M2:%3.0fmA",
             telem.m1_mA, telem.m2_mA);
    ssd1306_text(&oled, line, 0, 22, 1);

    /* Line 3: Power + efficiency */
    snprintf(line, sizeof(line), "P:%.1fW Eff:%d%%",
             telem.total_W, telem.efficiency);
    ssd1306_text(&oled, line, 0, 32, 1);

    /* Line 4: Vibration + temp */
    snprintf(line, sizeof(line), "Vib:%.2fg T:%.1fC",
             telem.accel_rms, telem.temperature);
    ssd1306_text(&oled, line, 0, 42, 1);

    /* Line 5: Joystick + pot */
    snprintf(line, sizeof(line), "J:%+4d,%+4d P:%d%%",
             in->x, in->y, in->pot);
    ssd1306_text(&oled, line, 0, 54, 1);

    ssd1306_show(&oled);
}

/* ============ Status LEDs ============ */

static void leds_init(void) {
    gpio_init(LED_RED);
    gpio_set_dir(LED_RED, GPIO_OUT);
    gpio_init(LED_GREEN);
    gpio_set_dir(LED_GREEN, GPIO_OUT);
    gpio_init(LED_ONBOARD);
    gpio_set_dir(LED_ONBOARD, GPIO_OUT);
}

/* ============ Main ============ */

int main(void) {
    stdio_init_all();
    sleep_ms(1000);

    printf("================================\n");
    printf("  GridBox SCADA (C SDK)\n");
    printf("  Production Firmware\n");
    printf("================================\n");

    /* LEDs */
    leds_init();
    gpio_put(LED_RED, 1);

    /* I2C for OLED */
    i2c_init(I2C_PORT, I2C_FREQ);
    gpio_set_function(I2C_SDA, GPIO_FUNC_I2C);
    gpio_set_function(I2C_SCL, GPIO_FUNC_I2C);
    gpio_pull_up(I2C_SDA);
    gpio_pull_up(I2C_SCL);

    /* SPI for nRF24L01+ */
    spi_init(SPI_PORT, SPI_BAUD);
    gpio_set_function(SPI_SCK, GPIO_FUNC_SPI);
    gpio_set_function(SPI_MOSI, GPIO_FUNC_SPI);
    gpio_set_function(SPI_MISO, GPIO_FUNC_SPI);

    /* ADC for joystick + pot */
    adc_init();
    adc_gpio_init(JOY_X_PIN);
    adc_gpio_init(JOY_Y_PIN);
    adc_gpio_init(POT_PIN);

    /* Joystick button */
    gpio_init(JOY_BTN_PIN);
    gpio_set_dir(JOY_BTN_PIN, GPIO_IN);
    gpio_pull_up(JOY_BTN_PIN);

    /* Init OLED */
    ssd1306_init(&oled, I2C_PORT, SSD1306_ADDR);

    /* Init wireless (addresses reversed from master) */
    const uint8_t tx_addr[] = NRF_TX_ADDR_STR;
    const uint8_t rx_addr[] = NRF_RX_ADDR_STR;
    nrf24l01_init(&radio, SPI_PORT, NRF_CSN, NRF_CE,
                  NRF_CHANNEL, NRF_PAYLOAD_SIZE, NRF_DATA_RATE,
                  tx_addr, rx_addr);

    /* Start listening for master telemetry */
    nrf24l01_start_listening(&radio);

    gpio_put(LED_RED, 0);
    gpio_put(LED_GREEN, 1);
    printf("[SCADA] Ready — listening for master\n");

    /* Timing */
    uint32_t last_display_ms = 0;
    uint32_t last_cmd_ms = 0;

    while (true) {
        uint32_t now_ms = to_ms_since_boot(get_absolute_time());

        /* 1. Check for incoming telemetry */
        if (nrf24l01_available(&radio)) {
            uint8_t rx_buf[NRF_PAYLOAD_SIZE];
            if (nrf24l01_recv(&radio, rx_buf)) {
                parse_telemetry(rx_buf);
                gpio_put(LED_ONBOARD, !gpio_get(LED_ONBOARD));
            }
        }

        /* 2. Check connection timeout */
        if (telem.connected && (now_ms - telem.last_rx_ms > HEARTBEAT_TIMEOUT_MS)) {
            telem.connected = false;
            gpio_put(LED_RED, 1);
            gpio_put(LED_GREEN, 0);
            printf("[SCADA] Connection lost\n");
        } else if (telem.connected) {
            /* Update LEDs based on fault level */
            if (telem.fault_level == 0) {
                gpio_put(LED_GREEN, 1);
                gpio_put(LED_RED, 0);
            } else {
                gpio_put(LED_RED, 1);
                gpio_put(LED_GREEN, telem.fault_level < 2);
            }
        }

        /* 3. Read joystick + pot */
        input_t in = read_inputs();

        /* 4. Update OLED display */
        if (now_ms - last_display_ms >= DISPLAY_UPDATE_MS) {
            last_display_ms = now_ms;
            update_display(&in);
        }

        /* 5. Send joystick commands to master */
        if (now_ms - last_cmd_ms >= COMMAND_SEND_MS) {
            last_cmd_ms = now_ms;

            if (in.button) {
                /* Button press: emergency stop */
                uint8_t pkt[NRF_PAYLOAD_SIZE];
                build_command(pkt, 0xFF, 0);
                nrf24l01_stop_listening(&radio);
                nrf24l01_send(&radio, pkt);
                nrf24l01_start_listening(&radio);
            } else if (in.x != 0 || in.y != 0) {
                /* Joystick: motor speed control */
                uint8_t pkt[NRF_PAYLOAD_SIZE];
                uint8_t speed = (uint8_t)(50 + in.y / 2);  /* 0-100 based on Y */
                build_command(pkt, 0x01, speed);  /* motor 1 speed */
                nrf24l01_stop_listening(&radio);
                nrf24l01_send(&radio, pkt);
                nrf24l01_start_listening(&radio);
            }
        }

        /* 6. Print to USB serial */
        if (telem.connected && (now_ms % 500 < MAIN_LOOP_MS)) {
            printf("{\"bus_v\":%.2f,\"m1_mA\":%.0f,\"m2_mA\":%.0f,"
                   "\"total_W\":%.2f,\"fault\":%d,\"connected\":true}\n",
                   telem.bus_v, telem.m1_mA, telem.m2_mA,
                   telem.total_W, telem.fault_level);
        }

        sleep_ms(MAIN_LOOP_MS);
    }

    return 0;
}
