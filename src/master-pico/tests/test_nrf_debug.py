"""
nRF24L01+ Debug — tests each wire individually.
Helps find which wire is wrong. Heartbeat LED runs throughout.

Wiring: CE=GP0, CSN=GP1, SCK=GP2, MOSI=GP3, MISO=GP16, VCC=3V3, GND=GND

Usage: mpremote run src/master-pico/tests/test_nrf_debug.py
"""

from machine import Pin, SPI
import time

# Start heartbeat (boot mode = fast blink)
import heartbeat

print("=" * 50)
print("  nRF24L01+ Wire-by-Wire Debug")
print("=" * 50)

# Step 1: Check CSN and CE pins respond
print("\n1. Testing CE (GP0) and CSN (GP1)...")
ce = Pin(0, Pin.OUT, value=0)
csn = Pin(1, Pin.OUT, value=1)
print("   CE=LOW, CSN=HIGH — OK")

# Step 2: Init SPI
print("\n2. Init SPI (SCK=GP2, MOSI=GP3, MISO=GP16)...")
try:
    spi = SPI(0, baudrate=1000000, polarity=0, phase=0,
              sck=Pin(2), mosi=Pin(3), miso=Pin(16))
    print("   SPI init — OK")
except Exception as e:
    print(f"   SPI FAILED: {e}")
    print("   Check: GP2=SCK, GP3=MOSI, GP16=MISO")
    heartbeat.set_state("fault")

# Step 3: Try reading status register multiple times
print("\n3. Reading nRF status register (10 attempts)...")
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
    print(f"   Attempt {i+1}: status = 0x{buf[1]:02X}")
    time.sleep_ms(100)

# Step 4: Analyse results
print("\n4. Analysis:")
unique = set(results)

if len(unique) == 1 and 0xFF in unique:
    print("   ALL 0xFF — nRF is NOT connected or NOT powered")
    print("")
    print("   Check:")
    print("   a) Is VCC wire going to Pico 3V3 pin (physical pin 36)?")
    print("   b) Is GND wire going to any Pico GND pin?")
    print("   c) Is MISO wire going to GP16 (physical pin 21)?")
    print("   d) Is CSN wire going to GP1 (physical pin 2)?")
    print("   e) Are all wires pushed firmly into breadboard?")
    heartbeat.set_state("fault")

elif len(unique) == 1 and 0x00 in unique:
    print("   ALL 0x00 — nRF has power but SPI not communicating")
    print("")
    print("   Check:")
    print("   a) Is SCK wire going to GP2 (physical pin 4)?")
    print("   b) Is MOSI wire going to GP3 (physical pin 5)?")
    print("   c) Is MISO wire going to GP16 (physical pin 21)?")
    print("   d) Are SCK/MOSI/MISO swapped?")
    print("   e) Try swapping MOSI and MISO wires")
    print("   f) Add 10uF capacitor between VCC and GND")
    heartbeat.set_state("fault")

elif any(0x01 <= r <= 0x7F for r in results):
    good = [r for r in results if 0x01 <= r <= 0x7F]
    print(f"   nRF RESPONDING! Status = 0x{good[0]:02X}")
    print("   The module is alive and communicating!")

    # Try reading config register
    csn.value(0)
    time.sleep_us(10)
    buf = bytearray(2)
    spi.write_readinto(b'\x00\xFF', buf)
    csn.value(1)
    heartbeat.activity(200)
    print(f"   Config register = 0x{buf[1]:02X}")
    heartbeat.set_state("normal")

else:
    print(f"   Mixed results: {[hex(r) for r in results]}")
    print("   Unstable connection — check for loose wires")
    heartbeat.set_state("fault")

# Step 5: Try writing and reading back
print("\n5. Write/read test...")
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
if channel == 100:
    print("   WRITE/READ OK — nRF is fully working!")
    heartbeat.set_state("normal")
elif channel == 0xFF:
    print("   Read 0xFF — module not responding (power issue)")
    heartbeat.set_state("fault")
elif channel == 0x00:
    print("   Read 0x00 — SPI communication issue (check MOSI/MISO)")
    heartbeat.set_state("fault")
else:
    print(f"   Unexpected value — partial communication")
    heartbeat.set_state("fault")

print("\n" + "=" * 50)
print("LED: slow blink = PASS, rapid blink = FAIL")
print("Press Ctrl+C to stop.")

while True:
    time.sleep(1)
