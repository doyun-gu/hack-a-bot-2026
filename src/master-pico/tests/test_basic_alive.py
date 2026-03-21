"""
Test: Is the Pico alive and MicroPython running?
No specific pins needed — just USB connection.

Tests:
1. Print system info
2. Blink onboard LED (GP25 — no soldering needed, it's on the board)
3. Read internal temperature sensor
4. Test that imports work

Usage: mpremote run test_basic_alive.py
"""

import sys
import time
from machine import Pin, ADC

print("=" * 40)
print("  Pico Basic Alive Test")
print("=" * 40)

# System info
print(f"MicroPython: {sys.version}")
print(f"Platform: {sys.platform}")

# Onboard LED (GP25 — built into the board, no soldering needed)
led = Pin(25, Pin.OUT)
print("\nBlinking onboard LED 5 times...")
for i in range(5):
    led.value(1)
    print(f"  LED ON  ({i+1}/5)")
    time.sleep_ms(300)
    led.value(0)
    time.sleep_ms(300)

# Internal temperature sensor (ADC channel 4 — no pin needed)
temp_adc = ADC(4)
raw = temp_adc.read_u16()
# RP2350 internal temp: voltage = raw * 3.3 / 65535, temp = 27 - (voltage - 0.706) / 0.001721
voltage = raw * 3.3 / 65535
temp_c = 27 - (voltage - 0.706) / 0.001721
print(f"\nInternal temp: {temp_c:.1f}°C (ADC raw: {raw})")

# Test imports
print("\nTesting module imports...")
try:
    import config
    print("  config.py: OK")
except ImportError:
    print("  config.py: NOT FOUND (flash firmware first)")

try:
    from protocol import PACK_SIZE
    print(f"  protocol.py: OK (packet size: {PACK_SIZE})")
except ImportError:
    print("  protocol.py: NOT FOUND (flash firmware first)")

print("\n" + "=" * 40)
print("  Pico is ALIVE and working!")
print("=" * 40)
