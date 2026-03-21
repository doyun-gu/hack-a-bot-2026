"""
Test: Servo on GP0 — direct PWM, no PCA9685 needed.
Moves servo to 3 positions: 0°, 90°, 180° and repeats.

Usage: mpremote run src/master-pico/tests/test_servo_direct.py
"""

from machine import Pin, PWM
import time

print("=" * 40)
print("  Servo Test — GP0 Direct PWM")
print("  Ctrl+C to stop")
print("=" * 40)

servo = PWM(Pin(0))
servo.freq(50)

print("\n0 degrees...")
servo.duty_u16(1640)
time.sleep(3)

print("90 degrees...")
servo.duty_u16(4915)
time.sleep(3)

print("180 degrees...")
servo.duty_u16(8190)
time.sleep(3)

print("Back to 90 (centre)...")
servo.duty_u16(4915)
time.sleep(1)

# Stop PWM signal — servo holds position
servo.deinit()
print("\nDone. Servo holding position.")
