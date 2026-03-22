"""
nRF test using ALTERNATIVE SPI pins.
If the normal pins (GP2,3,16) don't work, try SPI1 on different pins.

REWIRE the nRF for this test:
  SCK  → GP10 (physical pin 14)
  MOSI → GP11 (physical pin 15)
  MISO → GP12 (physical pin 16)
  CE   → GP0  (same as before, pin 1)
  CSN  → GP1  (same as before, pin 2)
  VCC  → 3V3  (same, pin 36)
  GND  → GND  (same)

Usage: mpremote run src/master-pico/tests/test_nrf_alt_pins.py
"""

from machine import Pin, SPI
import time

print("=" * 50)
print("  nRF Test — ALTERNATIVE SPI1 Pins")
print("  SCK=GP10, MOSI=GP11, MISO=GP12")
print("=" * 50)

ce = Pin(0, Pin.OUT, value=0)
csn = Pin(1, Pin.OUT, value=1)

spi = SPI(1, baudrate=1000000, polarity=0, phase=0,
          sck=Pin(10), mosi=Pin(11), miso=Pin(12))

print("\nReading status 5 times...")
for i in range(5):
    csn.value(0)
    time.sleep_us(10)
    buf = bytearray(2)
    spi.write_readinto(b'\x07\xFF', buf)
    csn.value(1)
    print(f"  Status = 0x{buf[1]:02X}")
    time.sleep_ms(200)

# Write/read test
csn.value(0)
spi.write(b'\x25\x64')
csn.value(1)
time.sleep_ms(1)
csn.value(0)
buf = bytearray(2)
spi.write_readinto(b'\x05\xFF', buf)
csn.value(1)
print(f"\nChannel write=100, read={buf[1]}")

if buf[1] == 100:
    print("nRF WORKS on alt pins!")
elif buf[1] == 0:
    print("Still 0x00 — might be the nRF module itself")
    print("Try a different nRF module if you have one")
else:
    print(f"Got 0x{buf[1]:02X}")
