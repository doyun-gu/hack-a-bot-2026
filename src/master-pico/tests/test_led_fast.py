"""
Fast LED blink — works on both Pico 1 and Pico 2.

Usage: mpremote run src/master-pico/tests/test_led_fast.py
"""

from machine import Pin
import time

# Try both LED pin methods (Pico 1 vs Pico 2)
try:
    led = Pin("LED", Pin.OUT)
except:
    led = Pin(25, Pin.OUT)

print("Fast blink — 20 times")
for i in range(20):
    led.value(1)
    time.sleep_ms(50)
    led.value(0)
    time.sleep_ms(50)

print("Slow blink — 5 times")
for i in range(5):
    led.value(1)
    time.sleep_ms(200)
    led.value(0)
    time.sleep_ms(200)

# Leave LED on so you know it's running
led.value(1)
print("Pico is ALIVE! LED stays ON.")
