/**
 * GridBox — nRF24L01+ Wireless Driver (C SDK)
 * SPI driver for nRF24L01+ PA+LNA 2.4GHz transceiver.
 * Mirrors the MicroPython API in nrf24l01.py.
 */

#ifndef NRF24L01_H
#define NRF24L01_H

#include "hardware/spi.h"
#include <stdbool.h>
#include <stdint.h>

/* nRF24L01+ register addresses */
#define NRF_CONFIG       0x00
#define NRF_EN_AA        0x01
#define NRF_EN_RXADDR    0x02
#define NRF_SETUP_AW     0x03
#define NRF_SETUP_RETR   0x04
#define NRF_RF_CH        0x05
#define NRF_RF_SETUP     0x06
#define NRF_STATUS       0x07
#define NRF_OBSERVE_TX   0x08
#define NRF_RX_ADDR_P0   0x0A
#define NRF_RX_ADDR_P1   0x0B
#define NRF_TX_ADDR      0x10
#define NRF_RX_PW_P0     0x11
#define NRF_RX_PW_P1     0x12
#define NRF_FIFO_STATUS  0x17

/* SPI commands */
#define NRF_R_REGISTER    0x00
#define NRF_W_REGISTER    0x20
#define NRF_R_RX_PAYLOAD  0x61
#define NRF_W_TX_PAYLOAD  0xA0
#define NRF_FLUSH_TX      0xE1
#define NRF_FLUSH_RX      0xE2
#define NRF_NOP           0xFF

/* Status bits */
#define NRF_RX_DR         0x40
#define NRF_TX_DS         0x20
#define NRF_MAX_RT        0x10

/* Config bits */
#define NRF_EN_CRC        0x08
#define NRF_CRCO          0x04
#define NRF_PWR_UP        0x02
#define NRF_PRIM_RX       0x01

/* Default payload size */
#define NRF_PAYLOAD_SIZE  32
#define NRF_ADDR_SIZE     5

/* Device handle */
typedef struct {
    spi_inst_t *spi;
    uint csn_pin;
    uint ce_pin;
    uint8_t payload_size;
} nrf24l01_t;

/**
 * Initialise nRF24L01+.
 * @param dev          Device handle to populate
 * @param spi          SPI instance
 * @param csn_pin      Chip select GPIO pin
 * @param ce_pin       Chip enable GPIO pin
 * @param channel      RF channel 0-125 (freq = 2400 + ch MHz)
 * @param payload_size Bytes per packet (1-32)
 * @param data_rate    250, 1000, or 2000 kbps
 * @param tx_addr      5-byte TX address
 * @param rx_addr      5-byte RX address
 * @return true on success
 */
bool nrf24l01_init(nrf24l01_t *dev, spi_inst_t *spi, uint csn_pin, uint ce_pin,
                   uint8_t channel, uint8_t payload_size, uint16_t data_rate,
                   const uint8_t tx_addr[NRF_ADDR_SIZE],
                   const uint8_t rx_addr[NRF_ADDR_SIZE]);

/** Set RF channel (0-125). */
void nrf24l01_set_channel(nrf24l01_t *dev, uint8_t ch);

/** Set data rate: 250, 1000, or 2000 kbps. */
void nrf24l01_set_data_rate(nrf24l01_t *dev, uint16_t rate);

/** Set TX power level 0-3 (min to max). */
void nrf24l01_set_power(nrf24l01_t *dev, uint8_t level);

/** Set TX address (5 bytes). Also sets RX pipe 0 for auto-ack. */
void nrf24l01_set_tx_addr(nrf24l01_t *dev, const uint8_t addr[NRF_ADDR_SIZE]);

/** Set RX address on pipe 1 (5 bytes). */
void nrf24l01_set_rx_addr(nrf24l01_t *dev, const uint8_t addr[NRF_ADDR_SIZE]);

/**
 * Transmit a packet.
 * @param dev  Device handle
 * @param data Payload of payload_size bytes
 * @return true if ACK received, false if max retries
 */
bool nrf24l01_send(nrf24l01_t *dev, const uint8_t *data);

/** Switch to RX mode and start listening. */
void nrf24l01_start_listening(nrf24l01_t *dev);

/** Switch out of RX mode. */
void nrf24l01_stop_listening(nrf24l01_t *dev);

/** Check if data is waiting in RX FIFO. */
bool nrf24l01_available(nrf24l01_t *dev);

/**
 * Read received packet.
 * @param dev  Device handle
 * @param buf  Buffer of payload_size bytes to receive into
 * @return true if data was read, false if FIFO empty
 */
bool nrf24l01_recv(nrf24l01_t *dev, uint8_t *buf);

/** Clear RX FIFO. */
void nrf24l01_flush_rx(nrf24l01_t *dev);

/** Clear TX FIFO. */
void nrf24l01_flush_tx(nrf24l01_t *dev);

/** Read STATUS register. */
uint8_t nrf24l01_get_status(nrf24l01_t *dev);

#endif /* NRF24L01_H */
