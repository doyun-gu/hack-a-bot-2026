"""
nRF24L01+ test with MAX7219 display showing live status.

Display shows:  BOOT → tESt → LINK On / LINK OFF → PASS / FAIL

Usage: mpremote run src/slave-pico/tests/test_nrf_with_display.py
"""

from machine import Pin, SPI
import time

import heartbeat
import seg_display

# Init display
seg_display.init()
seg_display.show("BOOT")
time.sleep(1)

print("=" * 50)
print("  nRF24L01+ Test (with display)")
print("=" * 50)

# Step 1: Init nRF SPI
seg_display.show("tESt SPI")
print("\n1. Init SPI0 for nRF...")
ce = Pin(0, Pin.OUT, value=0)
csn = Pin(1, Pin.OUT, value=1)

try:
    spi = SPI(0, baudrate=1000000, polarity=0, phase=0,
              sck=Pin(2), mosi=Pin(3), miso=Pin(16))
    print("   SPI0 — OK")
except Exception as e:
    print(f"   FAILED: {e}")
    seg_display.flash("SPI FAIL")
    heartbeat.set_state("fault")
    raise

# Step 2: Read status register
seg_display.show("rEAd nrF")
time.sleep_ms(500)

print("\n2. Reading nRF status (10 attempts)...")
results = []
for i in range(10):
    csn.value(0)
    time.sleep_us(10)
    buf = bytearray(2)
    spi.write_readinto(b'\x07\xFF', buf)
    csn.value(1)
    time.sleep_us(10)
    results.append(buf[1])
    heartbeat.activity(200)

    # Show each result on display
    seg_display.show(f"  0x{buf[1]:02X}  ")
    print(f"   #{i+1}: status = 0x{buf[1]:02X}")
    time.sleep_ms(200)

# Step 3: Write/read test
seg_display.show("CHAnnEL")
time.sleep_ms(500)

print("\n3. Write/read channel test...")
csn.value(0)
time.sleep_us(10)
spi.write(b'\x25\x64')  # write channel = 100
csn.value(1)
time.sleep_ms(1)

csn.value(0)
time.sleep_us(10)
buf = bytearray(2)
spi.write_readinto(b'\x05\xFF', buf)
csn.value(1)
channel = buf[1]
heartbeat.activity(200)
print(f"   Wrote 100, read {channel}")

# Step 4: Verdict
print("\n" + "=" * 50)
unique = set(results)
ok = any(0x01 <= r <= 0x7F for r in results) and channel == 100

if ok:
    print("  PASS — nRF24L01+ is working!")
    seg_display.flash("LINK On", times=3)
    seg_display.show("PASS")
    heartbeat.set_state("normal")
elif all(r == 0xFF for r in results):
    print("  FAIL — 0xFF: not connected")
    seg_display.flash("LINK OFF", times=5)
    seg_display.show("FAIL  FF")
    heartbeat.set_state("fault")
elif all(r == 0x00 for r in results):
    print("  FAIL — 0x00: SPI issue")
    seg_display.flash("SPI FAIL", times=5)
    seg_display.show("FAIL  00")
    heartbeat.set_state("fault")
else:
    print("  UNSTABLE — loose wire")
    seg_display.flash("LoOSE", times=5)
    seg_display.show("FAIL")
    heartbeat.set_state("fault")

print("=" * 50)
print("\nPress Ctrl+C to stop.")

while True:
    time.sleep(1)
