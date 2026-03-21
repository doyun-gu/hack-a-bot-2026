/**
 * GridBox C SDK — Wireless Test (Master side)
 * Sends PING every 500ms, listens for PONG.
 * Flash this on the master Pico, flash MicroPython wireless test on slave.
 *
 * nRF24L01+ wiring: CE=GP0, CSN=GP1, SCK=GP2, MOSI=GP3, MISO=GP16
 * Power: 3.3V ONLY + 10µF capacitor
 */

#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "hardware/gpio.h"

// nRF24L01+ pins
#define NRF_CE   0
#define NRF_CSN  1
#define SPI_SCK  2
#define SPI_MOSI 3
#define SPI_MISO 16
#define NRF_CHANNEL 100

// nRF24L01+ registers
#define REG_CONFIG      0x00
#define REG_EN_AA       0x01
#define REG_EN_RXADDR   0x02
#define REG_SETUP_AW    0x03
#define REG_SETUP_RETR  0x04
#define REG_RF_CH       0x05
#define REG_RF_SETUP    0x06
#define REG_STATUS      0x07
#define REG_RX_ADDR_P0  0x0A
#define REG_TX_ADDR     0x10
#define REG_RX_PW_P0    0x11

#define CMD_R_RX_PAYLOAD  0x61
#define CMD_W_TX_PAYLOAD  0xA0
#define CMD_FLUSH_TX      0xE1
#define CMD_FLUSH_RX      0xE2

static spi_inst_t *spi = spi0;

static void csn_low(void) { gpio_put(NRF_CSN, 0); sleep_us(5); }
static void csn_high(void) { gpio_put(NRF_CSN, 1); sleep_us(5); }
static void ce_low(void) { gpio_put(NRF_CE, 0); }
static void ce_high(void) { gpio_put(NRF_CE, 1); }

static uint8_t nrf_read_reg(uint8_t reg) {
    uint8_t tx[2] = {reg, 0xFF};
    uint8_t rx[2];
    csn_low();
    spi_write_read_blocking(spi, tx, rx, 2);
    csn_high();
    return rx[1];
}

static void nrf_write_reg(uint8_t reg, uint8_t val) {
    uint8_t tx[2] = {0x20 | reg, val};
    csn_low();
    spi_write_blocking(spi, tx, 2);
    csn_high();
}

static void nrf_write_addr(uint8_t reg, const uint8_t *addr, uint8_t len) {
    uint8_t cmd = 0x20 | reg;
    csn_low();
    spi_write_blocking(spi, &cmd, 1);
    spi_write_blocking(spi, addr, len);
    csn_high();
}

static bool nrf_send(const uint8_t *data, uint8_t len) {
    ce_low();

    // Clear status flags
    nrf_write_reg(REG_STATUS, 0x70);

    // Flush TX
    csn_low();
    uint8_t cmd = CMD_FLUSH_TX;
    spi_write_blocking(spi, &cmd, 1);
    csn_high();

    // Write payload
    csn_low();
    cmd = CMD_W_TX_PAYLOAD;
    spi_write_blocking(spi, &cmd, 1);
    spi_write_blocking(spi, data, len);
    csn_high();

    // TX mode
    nrf_write_reg(REG_CONFIG, 0x0E);  // PWR_UP, EN_CRC, PTX
    ce_high();
    sleep_us(15);
    ce_low();

    // Wait for TX complete or timeout
    for (int i = 0; i < 100; i++) {
        uint8_t status = nrf_read_reg(REG_STATUS);
        if (status & 0x20) {  // TX_DS
            nrf_write_reg(REG_STATUS, 0x20);
            return true;
        }
        if (status & 0x10) {  // MAX_RT
            nrf_write_reg(REG_STATUS, 0x10);
            csn_low();
            cmd = CMD_FLUSH_TX;
            spi_write_blocking(spi, &cmd, 1);
            csn_high();
            return false;
        }
        sleep_us(100);
    }
    return false;
}

static void nrf_start_listening(void) {
    nrf_write_reg(REG_CONFIG, 0x0F);  // PWR_UP, EN_CRC, PRX
    ce_high();
    sleep_us(130);
}

static bool nrf_available(void) {
    uint8_t status = nrf_read_reg(REG_STATUS);
    return (status & 0x40) != 0;  // RX_DR
}

static void nrf_read_payload(uint8_t *buf, uint8_t len) {
    csn_low();
    uint8_t cmd = CMD_R_RX_PAYLOAD;
    spi_write_blocking(spi, &cmd, 1);
    spi_read_blocking(spi, 0xFF, buf, len);
    csn_high();
    nrf_write_reg(REG_STATUS, 0x40);  // Clear RX_DR
}

static void nrf_init(void) {
    // SPI init
    spi_init(spi, 10000000);
    gpio_set_function(SPI_SCK, GPIO_FUNC_SPI);
    gpio_set_function(SPI_MOSI, GPIO_FUNC_SPI);
    gpio_set_function(SPI_MISO, GPIO_FUNC_SPI);

    // CE and CSN
    gpio_init(NRF_CE); gpio_set_dir(NRF_CE, GPIO_OUT); ce_low();
    gpio_init(NRF_CSN); gpio_set_dir(NRF_CSN, GPIO_OUT); csn_high();

    sleep_ms(100);  // nRF power-on delay

    // Configure
    nrf_write_reg(REG_CONFIG, 0x0C);      // EN_CRC, CRC 2 bytes
    nrf_write_reg(REG_EN_AA, 0x01);       // Auto-ACK on pipe 0
    nrf_write_reg(REG_EN_RXADDR, 0x01);   // Enable pipe 0
    nrf_write_reg(REG_SETUP_AW, 0x03);    // 5-byte address
    nrf_write_reg(REG_SETUP_RETR, 0x1A);  // 500us delay, 10 retries
    nrf_write_reg(REG_RF_CH, NRF_CHANNEL);
    nrf_write_reg(REG_RF_SETUP, 0x26);    // 250kbps, 0dBm
    nrf_write_reg(REG_RX_PW_P0, 32);     // 32-byte payload

    // Set addresses
    const uint8_t tx_addr[] = {'N','S','Y','N','T'};
    const uint8_t rx_addr[] = {'N','S','Y','N','R'};
    nrf_write_addr(REG_TX_ADDR, tx_addr, 5);
    nrf_write_addr(REG_RX_ADDR_P0, tx_addr, 5);  // RX on pipe 0 = TX addr for auto-ACK

    // Flush
    csn_low(); uint8_t cmd = CMD_FLUSH_TX; spi_write_blocking(spi, &cmd, 1); csn_high();
    csn_low(); cmd = CMD_FLUSH_RX; spi_write_blocking(spi, &cmd, 1); csn_high();

    // Clear status
    nrf_write_reg(REG_STATUS, 0x70);

    // Power up
    nrf_write_reg(REG_CONFIG, 0x0E);
    sleep_ms(2);
}

int main(void) {
    stdio_init_all();
    sleep_ms(2000);

    printf("================================\n");
    printf("  GridBox C SDK — Wireless Test\n");
    printf("  Master: PING every 500ms\n");
    printf("================================\n");

    // LED
    gpio_init(PICO_DEFAULT_LED_PIN);
    gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);

    // Init nRF
    nrf_init();
    printf("[NRF] Initialised on channel %d\n", NRF_CHANNEL);

    int sent = 0, acked = 0, failed = 0;

    while (true) {
        // Build PING packet
        uint8_t pkt[32];
        memset(pkt, 0, 32);
        pkt[0] = 0x01;  // packet type
        pkt[1] = (uint8_t)(sent & 0xFF);  // sequence
        memcpy(&pkt[2], "PING", 4);

        // Send
        uint32_t t1 = time_us_32();
        bool ok = nrf_send(pkt, 32);
        uint32_t t2 = time_us_32();

        sent++;
        if (ok) {
            acked++;
            gpio_put(PICO_DEFAULT_LED_PIN, 1);
            printf("[C SDK] PING #%d ACK in %dus | success: %d/%d (%.1f%%)\n",
                   sent, t2 - t1, acked, sent, (float)acked / sent * 100.0f);
        } else {
            failed++;
            gpio_put(PICO_DEFAULT_LED_PIN, 0);
            printf("[C SDK] PING #%d FAILED (%dus) | lost: %d/%d\n",
                   sent, t2 - t1, failed, sent);
        }

        sleep_ms(500);
    }

    return 0;
}
