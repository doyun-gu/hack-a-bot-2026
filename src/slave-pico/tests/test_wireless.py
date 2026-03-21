"""
Test: Wireless PONG from Slave
Slave listens for "PING" from master, replies with "PONG".

Usage: mpremote run test_wireless.py
Pair with: src/master-pico/tests/test_wireless.py on Pico A
"""

import sys
sys.path.append('/micropython')

from machine import Pin, SPI
import time
import config
from nrf24l01 import NRF24L01

print("=" * 40)
print("  Wireless Test — SLAVE (PONG)")
print("=" * 40)

# Init SPI + nRF
spi = SPI(config.SPI_ID, baudrate=config.SPI_BAUD, polarity=0, phase=0,
          sck=Pin(config.SPI_SCK), mosi=Pin(config.SPI_MOSI),
          miso=Pin(config.SPI_MISO))

nrf = NRF24L01(spi, Pin(config.NRF_CSN), Pin(config.NRF_CE),
               channel=config.NRF_CHANNEL,
               payload_size=config.NRF_PAYLOAD_SIZE,
               data_rate=config.NRF_DATA_RATE,
               tx_addr=config.NRF_TX_ADDR,
               rx_addr=config.NRF_RX_ADDR)

led_green = Pin(config.LED_GREEN, Pin.OUT)
led_red = Pin(config.LED_RED, Pin.OUT)

print(f"TX addr: {config.NRF_TX_ADDR}")
print(f"RX addr: {config.NRF_RX_ADDR}")
print(f"Channel: {config.NRF_CHANNEL}")
print("Listening for PING...")
print()

ping_count = 0

# Start listening
nrf.start_listening()

while True:
    data = nrf.recv()
    if data and data[:4] == b'PING':
        ping_count += 1
        print(f"[{ping_count}] Received PING! Sending PONG...")
        led_green.value(1)

        # Stop listening to send reply
        nrf.stop_listening()

        # Send PONG
        payload = b'PONG' + b'\x00' * 28  # pad to 32 bytes
        ok = nrf.send(payload)

        if ok:
            print(f"  PONG sent (ACK received)")
        else:
            print(f"  PONG sent (no ACK)")

        # Resume listening
        nrf.start_listening()
        led_green.value(0)

    time.sleep_ms(10)
