/**
 * GridBox — nRF24L01+ Wireless Driver (C SDK)
 * Full SPI register-level implementation for nRF24L01+ PA+LNA.
 * Ported from MicroPython nrf24l01.py.
 */

#include "nrf24l01.h"
#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"

/* ---- Low-level SPI helpers ---- */

static inline void csn_low(nrf24l01_t *dev) {
    gpio_put(dev->csn_pin, 0);
    sleep_us(5);
}

static inline void csn_high(nrf24l01_t *dev) {
    gpio_put(dev->csn_pin, 1);
    sleep_us(5);
}

static inline void ce_high(nrf24l01_t *dev) {
    gpio_put(dev->ce_pin, 1);
}

static inline void ce_low(nrf24l01_t *dev) {
    gpio_put(dev->ce_pin, 0);
}

static uint8_t nrf_read_reg(nrf24l01_t *dev, uint8_t reg) {
    uint8_t cmd = NRF_R_REGISTER | (reg & 0x1F);
    uint8_t val = 0;

    csn_low(dev);
    spi_write_blocking(dev->spi, &cmd, 1);
    spi_read_blocking(dev->spi, 0xFF, &val, 1);
    csn_high(dev);

    return val;
}

static void nrf_write_reg(nrf24l01_t *dev, uint8_t reg, uint8_t val) {
    uint8_t buf[2] = {NRF_W_REGISTER | (reg & 0x1F), val};

    csn_low(dev);
    spi_write_blocking(dev->spi, buf, 2);
    csn_high(dev);
}

static void nrf_read_multi(nrf24l01_t *dev, uint8_t reg, uint8_t *buf, uint8_t len) {
    uint8_t cmd = NRF_R_REGISTER | (reg & 0x1F);

    csn_low(dev);
    spi_write_blocking(dev->spi, &cmd, 1);
    spi_read_blocking(dev->spi, 0xFF, buf, len);
    csn_high(dev);
}

static void nrf_write_multi(nrf24l01_t *dev, uint8_t reg, const uint8_t *data, uint8_t len) {
    uint8_t cmd = NRF_W_REGISTER | (reg & 0x1F);

    csn_low(dev);
    spi_write_blocking(dev->spi, &cmd, 1);
    spi_write_blocking(dev->spi, data, len);
    csn_high(dev);
}

static void nrf_send_command(nrf24l01_t *dev, uint8_t cmd) {
    csn_low(dev);
    spi_write_blocking(dev->spi, &cmd, 1);
    csn_high(dev);
}

/* ---- Public API ---- */

bool nrf24l01_init(nrf24l01_t *dev, spi_inst_t *spi, uint csn_pin, uint ce_pin,
                   uint8_t channel, uint8_t payload_size, uint16_t data_rate,
                   const uint8_t tx_addr[NRF_ADDR_SIZE],
                   const uint8_t rx_addr[NRF_ADDR_SIZE]) {
    dev->spi = spi;
    dev->csn_pin = csn_pin;
    dev->ce_pin = ce_pin;
    dev->payload_size = payload_size;

    /* Init GPIO for CSN and CE */
    gpio_init(csn_pin);
    gpio_set_dir(csn_pin, GPIO_OUT);
    gpio_put(csn_pin, 1);

    gpio_init(ce_pin);
    gpio_set_dir(ce_pin, GPIO_OUT);
    gpio_put(ce_pin, 0);

    sleep_ms(5);  /* power-on delay */

    /* Reset: flush FIFOs and clear status flags */
    nrf_send_command(dev, NRF_FLUSH_TX);
    nrf_send_command(dev, NRF_FLUSH_RX);
    nrf_write_reg(dev, NRF_STATUS, NRF_RX_DR | NRF_TX_DS | NRF_MAX_RT);

    /* Enable auto-ack on pipe 0 and pipe 1 */
    nrf_write_reg(dev, NRF_EN_AA, 0x03);

    /* Enable RX pipe 0 (for auto-ack) and pipe 1 (for receiving) */
    nrf_write_reg(dev, NRF_EN_RXADDR, 0x03);

    /* Address width: 5 bytes */
    nrf_write_reg(dev, NRF_SETUP_AW, 0x03);

    /* Auto-retransmit: 500µs delay, up to 15 retries */
    nrf_write_reg(dev, NRF_SETUP_RETR, 0x1F);

    /* RF channel */
    nrf24l01_set_channel(dev, channel);

    /* Data rate and TX power */
    nrf24l01_set_data_rate(dev, data_rate);
    nrf24l01_set_power(dev, 3);  /* max power */

    /* Set TX and RX addresses */
    nrf24l01_set_tx_addr(dev, tx_addr);
    nrf24l01_set_rx_addr(dev, rx_addr);

    /* Set RX payload size on pipe 0 and pipe 1 */
    nrf_write_reg(dev, NRF_RX_PW_P0, payload_size);
    nrf_write_reg(dev, NRF_RX_PW_P1, payload_size);

    /* Config: enable CRC (2-byte), power up, PTX mode */
    nrf_write_reg(dev, NRF_CONFIG, NRF_EN_CRC | NRF_CRCO | NRF_PWR_UP);
    sleep_ms(2);  /* 1.5ms power-up delay */

    printf("[nRF24] Init OK: ch=%d, payload=%d, rate=%dkbps\n",
           channel, payload_size, data_rate);
    return true;
}

void nrf24l01_set_channel(nrf24l01_t *dev, uint8_t ch) {
    if (ch > 125) ch = 125;
    nrf_write_reg(dev, NRF_RF_CH, ch);
}

void nrf24l01_set_data_rate(nrf24l01_t *dev, uint16_t rate) {
    uint8_t setup = nrf_read_reg(dev, NRF_RF_SETUP);
    setup &= ~0x28;  /* clear RF_DR_LOW (bit 5) and RF_DR_HIGH (bit 3) */

    if (rate == 250) {
        setup |= 0x20;  /* RF_DR_LOW = 1 → 250kbps */
    } else if (rate == 2000) {
        setup |= 0x08;  /* RF_DR_HIGH = 1 → 2Mbps */
    }
    /* else: both 0 → 1Mbps */

    nrf_write_reg(dev, NRF_RF_SETUP, setup);
}

void nrf24l01_set_power(nrf24l01_t *dev, uint8_t level) {
    if (level > 3) level = 3;
    uint8_t setup = nrf_read_reg(dev, NRF_RF_SETUP);
    setup &= ~0x06;           /* clear RF_PWR bits [2:1] */
    setup |= (level << 1);
    nrf_write_reg(dev, NRF_RF_SETUP, setup);
}

void nrf24l01_set_tx_addr(nrf24l01_t *dev, const uint8_t addr[NRF_ADDR_SIZE]) {
    nrf_write_multi(dev, NRF_TX_ADDR, addr, NRF_ADDR_SIZE);
    /* Also set RX pipe 0 to same address for auto-ack */
    nrf_write_multi(dev, NRF_RX_ADDR_P0, addr, NRF_ADDR_SIZE);
}

void nrf24l01_set_rx_addr(nrf24l01_t *dev, const uint8_t addr[NRF_ADDR_SIZE]) {
    nrf_write_multi(dev, NRF_RX_ADDR_P1, addr, NRF_ADDR_SIZE);
}

bool nrf24l01_send(nrf24l01_t *dev, const uint8_t *data) {
    /* Ensure TX mode */
    ce_low(dev);
    uint8_t config = nrf_read_reg(dev, NRF_CONFIG);
    config &= ~NRF_PRIM_RX;  /* clear PRIM_RX = TX mode */
    config |= NRF_PWR_UP;
    nrf_write_reg(dev, NRF_CONFIG, config);

    /* Flush TX FIFO */
    nrf_send_command(dev, NRF_FLUSH_TX);

    /* Write TX payload */
    uint8_t cmd = NRF_W_TX_PAYLOAD;
    csn_low(dev);
    spi_write_blocking(dev->spi, &cmd, 1);
    spi_write_blocking(dev->spi, data, dev->payload_size);
    csn_high(dev);

    /* Pulse CE to trigger transmission (>10µs) */
    ce_high(dev);
    sleep_us(15);
    ce_low(dev);

    /* Wait for TX_DS or MAX_RT (timeout ~10ms) */
    uint32_t start = time_us_32();
    uint8_t status;
    while ((time_us_32() - start) < 10000) {
        status = nrf_read_reg(dev, NRF_STATUS);
        if (status & (NRF_TX_DS | NRF_MAX_RT)) break;
        sleep_us(10);
    }

    /* Clear status flags */
    nrf_write_reg(dev, NRF_STATUS, NRF_RX_DR | NRF_TX_DS | NRF_MAX_RT);

    if (status & NRF_MAX_RT) {
        nrf_send_command(dev, NRF_FLUSH_TX);
        return false;
    }

    return (status & NRF_TX_DS) != 0;
}

void nrf24l01_start_listening(nrf24l01_t *dev) {
    /* Set PRIM_RX and power up */
    uint8_t config = nrf_read_reg(dev, NRF_CONFIG);
    config |= NRF_PRIM_RX | NRF_PWR_UP;
    nrf_write_reg(dev, NRF_CONFIG, config);

    /* Clear status flags */
    nrf_write_reg(dev, NRF_STATUS, NRF_RX_DR | NRF_TX_DS | NRF_MAX_RT);

    /* Flush RX FIFO */
    nrf_send_command(dev, NRF_FLUSH_RX);

    /* CE high = start listening */
    ce_high(dev);
    sleep_us(130);  /* RX settling time */
}

void nrf24l01_stop_listening(nrf24l01_t *dev) {
    ce_low(dev);

    /* Clear PRIM_RX */
    uint8_t config = nrf_read_reg(dev, NRF_CONFIG);
    config &= ~NRF_PRIM_RX;
    nrf_write_reg(dev, NRF_CONFIG, config);
}

bool nrf24l01_available(nrf24l01_t *dev) {
    uint8_t status = nrf_read_reg(dev, NRF_STATUS);
    /* RX_P_NO bits [3:1]: 0b111 = FIFO empty, anything else = data available */
    uint8_t pipe = (status >> 1) & 0x07;
    return pipe < 6;
}

bool nrf24l01_recv(nrf24l01_t *dev, uint8_t *buf) {
    if (!nrf24l01_available(dev)) return false;

    /* Read RX payload */
    uint8_t cmd = NRF_R_RX_PAYLOAD;
    csn_low(dev);
    spi_write_blocking(dev->spi, &cmd, 1);
    spi_read_blocking(dev->spi, 0xFF, buf, dev->payload_size);
    csn_high(dev);

    /* Clear RX_DR flag */
    nrf_write_reg(dev, NRF_STATUS, NRF_RX_DR);

    return true;
}

void nrf24l01_flush_rx(nrf24l01_t *dev) {
    nrf_send_command(dev, NRF_FLUSH_RX);
}

void nrf24l01_flush_tx(nrf24l01_t *dev) {
    nrf_send_command(dev, NRF_FLUSH_TX);
}

uint8_t nrf24l01_get_status(nrf24l01_t *dev) {
    /* NOP command returns STATUS register */
    uint8_t cmd = NRF_NOP;
    uint8_t status = 0;

    csn_low(dev);
    spi_write_read_blocking(dev->spi, &cmd, &status, 1);
    csn_high(dev);

    return status;
}
