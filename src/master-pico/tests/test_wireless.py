"""
Test: Wireless PING from Master
Master sends "PING" every second, waits for "PONG" reply from slave.

Usage: mpremote run test_wireless.py
Pair with: src/slave-pico/tests/test_wireless.py on Pico B
"""

import sys
sys.path.append('/micropython')

from machine import Pin, SPI
import time
import config
from nrf24l01 import NRF24L01

print("=" * 40)
print("  Wireless Test — MASTER (PING)")
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
print()

ping_count = 0
pong_count = 0

while True:
    # Send PING
    ping_count += 1
    payload = b'PING' + b'\x00' * 28  # pad to 32 bytes
    ok = nrf.send(payload)

    if ok:
        print(f"[{ping_count}] Sent PING, ACK received. Waiting for PONG...")
    else:
        print(f"[{ping_count}] Sent PING, no ACK. Slave may be offline.")
        led_red.value(1)
        led_green.value(0)
        time.sleep(1)
        continue

    # Listen for PONG response
    nrf.start_listening()
    deadline = time.ticks_add(time.ticks_ms(), 500)  # 500ms timeout

    got_pong = False
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        data = nrf.recv()
        if data and data[:4] == b'PONG':
            pong_count += 1
            print(f"  PONG received! ({pong_count}/{ping_count} success)")
            led_green.value(1)
            led_red.value(0)
            got_pong = True
            break
        time.sleep_us(500)

    if not got_pong:
        print("  No PONG reply (timeout)")
        led_red.value(1)
        led_green.value(0)

    nrf.stop_listening()
    time.sleep(1)
