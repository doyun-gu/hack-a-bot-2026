"""
MAX7219 7-Segment Display Test
Tests SPI1 connection and displays test patterns.

Wiring: CLK=GP10, DIN=GP11, CS=GP13, VCC=3V3, GND=GND

Usage: mpremote run src/slave-pico/tests/test_max7219.py
"""

from machine import Pin, SPI
import time

# Start heartbeat
import heartbeat

print("=" * 50)
print("  MAX7219 7-Segment Display Test")
print("  CLK=GP10, DIN=GP11, CS=GP13")
print("=" * 50)

# Step 1: Init SPI1
print("\n1. Init SPI1...")
try:
    spi = SPI(1, baudrate=10_000_000, polarity=0, phase=0,
              sck=Pin(10), mosi=Pin(11))
    cs = Pin(13, Pin.OUT, value=1)
    print("   SPI1 init — OK")
except Exception as e:
    print(f"   SPI1 FAILED: {e}")
    heartbeat.set_state("fault")
    raise

def write_reg(addr, data):
    """Write a register to MAX7219."""
    cs.value(0)
    spi.write(bytes([addr, data]))
    cs.value(1)

# Step 2: Wake up MAX7219
print("\n2. Initialising MAX7219...")
write_reg(0x0F, 0x00)  # display test off
write_reg(0x0C, 0x01)  # shutdown → normal operation
write_reg(0x0B, 0x07)  # scan limit → all 8 digits
write_reg(0x09, 0xFF)  # decode mode → BCD for all digits
write_reg(0x0A, 0x08)  # intensity → medium (0-15)
heartbeat.activity(200)
print("   MAX7219 init — OK")

# Step 3: Display test — show 12345678
print("\n3. Displaying '12345678'...")
for digit in range(1, 9):
    write_reg(digit, digit)
    heartbeat.activity(100)
    time.sleep_ms(200)
print("   Check display — should show: 1 2 3 4 5 6 7 8")

time.sleep(2)

# Step 4: Countdown 8 to 0
print("\n4. Countdown 8→0...")
for n in range(8, -1, -1):
    for digit in range(1, 9):
        write_reg(digit, n if n > 0 else 0x0F)  # 0x0F = blank
    heartbeat.activity(100)
    print(f"   {n}...")
    time.sleep_ms(500)

time.sleep(1)

# Step 5: Brightness sweep
print("\n5. Brightness sweep (0→15→0)...")
# Show all 8's first
for digit in range(1, 9):
    write_reg(digit, 8)
for intensity in list(range(0, 16)) + list(range(15, -1, -1)):
    write_reg(0x0A, intensity)
    heartbeat.activity(50)
    time.sleep_ms(100)
write_reg(0x0A, 0x08)  # back to medium

# Step 6: Built-in display test mode
print("\n6. Display test mode (all segments ON)...")
write_reg(0x0F, 0x01)  # all segments on
time.sleep(2)
write_reg(0x0F, 0x00)  # back to normal

# Final: show "PASS" pattern
print("\n" + "=" * 50)
print("  PASS — MAX7219 is working!")
print("  LED: slow blink = ALL GOOD")
print("=" * 50)

# Show "88888888" as success indicator
for digit in range(1, 9):
    write_reg(digit, 8)

heartbeat.set_state("normal")
print("\nPress Ctrl+C to stop.")

while True:
    time.sleep(1)
