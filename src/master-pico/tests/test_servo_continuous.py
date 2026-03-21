"""
Test: MG90D continuous rotation servo on GP0.
Controls speed and direction. NOT a position servo.

Usage: mpremote run src/master-pico/tests/test_servo_continuous.py
"""

from machine import Pin, PWM
import time

print("=" * 40)
print("  MG90D Continuous Rotation Servo")
print("  GP0 — Speed + Direction control")
print("=" * 40)

servo = PWM(Pin(0))
servo.freq(50)

# Find stop point first
print("\n1. STOP")
servo.duty_u16(4500)
time.sleep(2)

print("2. SLOW clockwise")
servo.duty_u16(3800)
time.sleep(2)

print("3. FAST clockwise")
servo.duty_u16(2000)
time.sleep(2)

print("4. STOP")
servo.duty_u16(4500)
time.sleep(2)

print("5. SLOW counter-clockwise")
servo.duty_u16(5200)
time.sleep(2)

print("6. FAST counter-clockwise")
servo.duty_u16(7000)
time.sleep(2)

print("7. STOP")
servo.duty_u16(4500)
time.sleep(1)

servo.deinit()
print("\nDone. Servo stopped.")
print("\nFor your project:")
print("  STOP         = duty 4500")
print("  CW slow      = duty 3800")
print("  CW fast      = duty 2000")
print("  CCW slow     = duty 5200")
print("  CCW fast     = duty 7000")
