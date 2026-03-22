"""
Test: LED blink — works on both Pico 1 (RP2040) and Pico 2 (RP2350).
No soldering needed. Just USB.

Usage: mpremote run src/master-pico/tests/test_led_blink.py
"""

from machine import Pin
import time
import sys

print("=" * 40)
print("  LED Blink Test")
print(f"  Platform: {sys.platform}")
print(f"  MicroPython: {sys.version}")
print("=" * 40)

led = Pin("LED", Pin.OUT)

print("\nBlinking LED 10 times...")
for i in range(10):
    led.value(1)
    print(f"  ON  ({i+1}/10)")
    time.sleep_ms(300)
    led.value(0)
    time.sleep_ms(300)

print("\nLED test passed!")
