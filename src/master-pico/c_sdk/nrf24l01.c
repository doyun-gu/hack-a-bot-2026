/**
 * GridBox — nRF24L01+ Wireless Driver (C SDK)
 * Stub implementation — prints function calls for testing.
 */

#include "nrf24l01.h"
#include <stdio.h>
#include <string.h>

bool nrf24l01_init(nrf24l01_t *dev, spi_inst_t *spi, uint csn_pin, uint ce_pin,
                   uint8_t channel, uint8_t payload_size, uint16_t data_rate,
                   const uint8_t tx_addr[NRF_ADDR_SIZE],
                   const uint8_t rx_addr[NRF_ADDR_SIZE]) {
    printf("[STUB] nrf24l01_init(ch=%d, payload=%d, rate=%d)\n",
           channel, payload_size, data_rate);

    dev->spi = spi;
    dev->csn_pin = csn_pin;
    dev->ce_pin = ce_pin;
    dev->payload_size = payload_size;

    /* TODO: Init CSN and CE as GPIO outputs */
    /* TODO: Configure: CRC, auto-ack, addresses, retries */
    /* TODO: Set channel, data rate, power level */
    /* TODO: Set TX/RX addresses */
    /* TODO: Clear status flags, flush FIFOs */
    /* TODO: Power up (PWR_UP bit in CONFIG) */

    return true;
}

void nrf24l01_set_channel(nrf24l01_t *dev, uint8_t ch) {
    printf("[STUB] nrf24l01_set_channel(%d)\n", ch);
    /* TODO: Write RF_CH register via SPI */
}

void nrf24l01_set_data_rate(nrf24l01_t *dev, uint16_t rate) {
    printf("[STUB] nrf24l01_set_data_rate(%d kbps)\n", rate);
    /* TODO: Read/modify/write RF_SETUP register */
}

void nrf24l01_set_power(nrf24l01_t *dev, uint8_t level) {
    printf("[STUB] nrf24l01_set_power(%d)\n", level);
    /* TODO: Read/modify/write RF_SETUP register */
}

void nrf24l01_set_tx_addr(nrf24l01_t *dev, const uint8_t addr[NRF_ADDR_SIZE]) {
    printf("[STUB] nrf24l01_set_tx_addr()\n");
    /* TODO: Write 5 bytes to TX_ADDR and RX_ADDR_P0 via SPI */
}

void nrf24l01_set_rx_addr(nrf24l01_t *dev, const uint8_t addr[NRF_ADDR_SIZE]) {
    printf("[STUB] nrf24l01_set_rx_addr()\n");
    /* TODO: Write 5 bytes to RX_ADDR_P1 via SPI */
}

bool nrf24l01_send(nrf24l01_t *dev, const uint8_t *data) {
    printf("[STUB] nrf24l01_send(%d bytes)\n", dev->payload_size);
    /* TODO: Switch to TX mode (clear PRIM_RX) */
    /* TODO: Write payload via W_TX_PAYLOAD */
    /* TODO: Pulse CE pin for >10us */
    /* TODO: Wait for TX_DS or MAX_RT in STATUS */
    /* TODO: Clear flags, return true if TX_DS */
    return true;
}

void nrf24l01_start_listening(nrf24l01_t *dev) {
    printf("[STUB] nrf24l01_start_listening()\n");
    /* TODO: Set PRIM_RX | PWR_UP in CONFIG */
    /* TODO: Clear status flags, flush RX FIFO */
    /* TODO: Set CE high */
}

void nrf24l01_stop_listening(nrf24l01_t *dev) {
    printf("[STUB] nrf24l01_stop_listening()\n");
    /* TODO: Set CE low */
    /* TODO: Clear PRIM_RX in CONFIG */
}

bool nrf24l01_available(nrf24l01_t *dev) {
    printf("[STUB] nrf24l01_available()\n");
    /* TODO: Read STATUS, check RX_P_NO bits */
    return false;
}

bool nrf24l01_recv(nrf24l01_t *dev, uint8_t *buf) {
    printf("[STUB] nrf24l01_recv()\n");
    /* TODO: Check available(), read R_RX_PAYLOAD, clear RX_DR flag */
    memset(buf, 0, dev->payload_size);
    return false;
}

void nrf24l01_flush_rx(nrf24l01_t *dev) {
    printf("[STUB] nrf24l01_flush_rx()\n");
    /* TODO: Send FLUSH_RX command via SPI */
}

void nrf24l01_flush_tx(nrf24l01_t *dev) {
    printf("[STUB] nrf24l01_flush_tx()\n");
    /* TODO: Send FLUSH_TX command via SPI */
}

uint8_t nrf24l01_get_status(nrf24l01_t *dev) {
    printf("[STUB] nrf24l01_get_status()\n");
    /* TODO: Read STATUS register via SPI NOP */
    return 0x0E;
}
