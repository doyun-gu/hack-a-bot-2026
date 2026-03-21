"""
Test: Find your servo's exact PWM values for 0°, 90°, 180°.
Slowly sweeps through duty values. Watch the servo and note
which values give you the positions you want.

Usage: mpremote run src/master-pico/tests/test_servo_tune.py
"""

from machine import Pin, PWM
import time

print("=" * 40)
print("  Servo Tuning — GP0")
print("  Watch servo position at each value")
print("=" * 40)

servo = PWM(Pin(0))
servo.freq(50)

# Standard range for most servos:
# 0°   = duty 1000-2000
# 90°  = duty 4500-5500
# 180° = duty 7500-9000

positions = [
    ("MIN (should be 0°)", 1000),
    ("", 1500),
    ("", 2000),
    ("", 2500),
    ("", 3000),
    ("MID (should be ~90°)", 3500),
    ("", 4000),
    ("", 4500),
    ("", 5000),
    ("", 5500),
    ("", 6000),
    ("", 6500),
    ("", 7000),
    ("MAX (should be ~180°)", 7500),
    ("", 8000),
    ("", 8500),
]

for label, duty in positions:
    servo.duty_u16(duty)
    if label:
        print(f"  duty={duty:5d}  <<<  {label}")
    else:
        print(f"  duty={duty:5d}")
    time.sleep(1)

# Stop
servo.duty_u16(4500)
time.sleep(0.5)
servo.deinit()
print("\nDone. Note which duty values = 0°, 90°, 180°")
