"""
Test: MG90D — single 90° rotation only.
Mark the servo horn position BEFORE running.
Then see how far it actually moved.

Runs ONCE and stops. No looping.

Usage: mpremote run src/master-pico/tests/test_servo_single90.py
"""

from machine import Pin, PWM
import time

servo = PWM(Pin(0))
servo.freq(50)

STOP_DUTY = 4700  # your servo's actual stop point
SLOW_CW = 4400    # just below stop = very slow clockwise
MS = 300           # adjust until exactly 90°

print("Mark the servo horn position NOW")
print("Starting in 3 seconds...")
servo.duty_u16(STOP_DUTY)
time.sleep(3)

print(f"Rotating for {MS}ms...")
servo.duty_u16(SLOW_CW)
time.sleep_ms(MS)

servo.duty_u16(STOP_DUTY)
time.sleep(1)
servo.deinit()

print(f"Done. Used {MS}ms")
print(f"")
print(f"Did it go exactly 90 degrees?")
print(f"  Too far  → try {MS - 50}ms")
print(f"  Too short → try {MS + 50}ms")
