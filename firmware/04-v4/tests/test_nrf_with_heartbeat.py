"""
nRF24L01+ test WITH heartbeat LED running.
Uses the heartbeat module — same LED behavior as production firmware.

LED patterns:
  boot (fast 80ms)   = test starting
  active (100ms)     = SPI activity detected
  normal (400ms)     = PASS
  fault (120ms)      = FAIL

Usage: mpremote run src/master-pico/tests/test_nrf_with_heartbeat.py
"""

from machine import Pin, SPI
import time

# Start heartbeat (auto-starts in boot mode = fast blink)
import heartbeat

# ---- nRF Test ----
print("=" * 50)
print("  nRF24L01+ Test (with heartbeat LED)")
print("  LED: fast=testing, slow=PASS, rapid=FAIL")
print("=" * 50)

# Step 1: Init pins
print("\n1. Init CE (GP0) and CSN (GP1)...")
ce = Pin(0, Pin.OUT, value=0)
csn = Pin(1, Pin.OUT, value=1)
print("   OK")

# Step 2: Init SPI
print("\n2. Init SPI (SCK=GP2, MOSI=GP3, MISO=GP16)...")
try:
    spi = SPI(0, baudrate=1000000, polarity=0, phase=0,
              sck=Pin(2), mosi=Pin(3), miso=Pin(16))
    print("   OK")
except Exception as e:
    print(f"   FAILED: {e}")
    heartbeat.set_state("fault")
    raise

# Step 3: Read status register
print("\n3. Reading status register (10 attempts)...")
results = []
for i in range(10):
    csn.value(0)
    time.sleep_us(10)
    buf = bytearray(2)
    spi.write_readinto(b'\x07\xFF', buf)
    csn.value(1)
    time.sleep_us(10)
    results.append(buf[1])
    # Flash activity on each SPI read
    heartbeat.activity(200)
    print(f"   #{i+1}: status = 0x{buf[1]:02X}")
    time.sleep_ms(100)

# Step 4: Write/read test
print("\n4. Write/read channel test...")
csn.value(0)
time.sleep_us(10)
spi.write(b'\x25\x64')  # write channel = 100
csn.value(1)
time.sleep_ms(1)

csn.value(0)
time.sleep_us(10)
buf = bytearray(2)
spi.write_readinto(b'\x05\xFF', buf)  # read channel
csn.value(1)
channel = buf[1]
heartbeat.activity(200)
print(f"   Wrote channel=100, read back={channel}")

# Step 5: Verdict
print("\n" + "=" * 50)
unique = set(results)
ok = any(0x01 <= r <= 0x7F for r in results) and channel == 100

if ok:
    print("  PASS — nRF24L01+ is working!")
    print("  Status OK + write/read verified")
    heartbeat.set_state("normal")
    print("  LED: slow blink (400ms) = ALL GOOD")
elif all(r == 0xFF for r in results):
    print("  FAIL — 0xFF: module not responding")
    print("  Check: VCC->3V3, GND, MISO->GP16, CSN->GP1")
    print("  Check: 10uF capacitor across VCC-GND")
    heartbeat.set_state("fault")
    print("  LED: rapid blink (120ms) = FAULT")
elif all(r == 0x00 for r in results):
    print("  FAIL — 0x00: power OK but SPI not talking")
    print("  Check: SCK->GP2, MOSI->GP3, MISO->GP16")
    print("  Try: swap MOSI and MISO wires")
    heartbeat.set_state("fault")
    print("  LED: rapid blink (120ms) = FAULT")
elif any(0x01 <= r <= 0x7F for r in results) and channel != 100:
    print(f"  PARTIAL — status OK but channel read={channel} (expected 100)")
    print("  MOSI may be loose or noisy")
    heartbeat.set_state("fault")
    print("  LED: rapid blink (120ms) = CHECK WIRING")
else:
    print(f"  UNSTABLE — mixed results: {[hex(r) for r in results]}")
    print("  Loose wire or bad solder joint")
    heartbeat.set_state("fault")
    print("  LED: rapid blink (120ms) = UNSTABLE")

print("=" * 50)
print("\nLED will keep blinking. Press Ctrl+C to stop.")

# Keep running so LED stays blinking
while True:
    time.sleep(1)
