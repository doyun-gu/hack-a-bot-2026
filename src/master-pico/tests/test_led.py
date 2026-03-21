"""
Test: LED blink
Simplest possible test — verifies Pico is running and GPIO works.

Usage: mpremote run test_led.py
"""

from machine import Pin
import time

led = Pin(25, Pin.OUT)  # onboard LED

print("=" * 40)
print("  LED Blink Test (onboard LED)")
print("  If LED blinks, Pico is alive!")
print("=" * 40)

while True:
    led.toggle()
    print("blink")
    time.sleep(0.5)
