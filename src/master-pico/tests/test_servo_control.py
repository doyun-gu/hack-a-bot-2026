"""
MG90D Continuous Servo — calibrated angle control.
Calibrated for YOUR servo: stop=4700, 45°=300ms at duty 4400.

Usage: mpremote run src/master-pico/tests/test_servo_control.py
"""

from machine import Pin, PWM
import time

servo = PWM(Pin(0))
servo.freq(50)

# YOUR servo's calibration values
STOP_DUTY = 4700
SLOW_CW = 4400      # clockwise
SLOW_CCW = 5300      # counter-clockwise — further from stop for more torque
MS_PER_45_CW = 340    # clockwise timing
MS_PER_45_CCW = 380   # counter-clockwise is slower — needs more time

def rotate(degrees):
    """Rotate the servo by N degrees. Positive=CW, Negative=CCW."""
    if degrees == 0:
        return

    if degrees > 0:
        ms = abs(degrees) * MS_PER_45_CW / 45
        duty = SLOW_CW
    else:
        ms = abs(degrees) * MS_PER_45_CCW / 45
        duty = SLOW_CCW

    print(f"  Rotating {degrees}° ({int(ms)}ms)...")
    servo.duty_u16(duty)
    time.sleep_ms(int(ms))
    servo.duty_u16(STOP_DUTY)

def stop():
    servo.duty_u16(STOP_DUTY)

print("=" * 40)
print("  MG90D Calibrated Control")
print(f"  Stop: {STOP_DUTY}")
print(f"  Speed CW: {MS_PER_45_CW}ms  CCW: {MS_PER_45_CCW}ms per 45°")
print("=" * 40)

# Stop first
stop()
time.sleep(1)

print("\n--- Test: 90° clockwise ---")
rotate(90)
time.sleep(2)

print("\n--- Test: 90° counter-clockwise (back) ---")
rotate(-90)
time.sleep(2)

print("\n--- Test: 180° clockwise ---")
rotate(180)
time.sleep(2)

print("\n--- Test: 180° counter-clockwise (back) ---")
rotate(-180)
time.sleep(2)

print("\n--- Test: 45° steps (full circle) ---")
for i in range(8):
    print(f"\n  Step {i+1}/8:")
    rotate(45)
    time.sleep(1)

servo.deinit()
print("\n\nDone!")
print(f"\nCalibration values for config.py:")
print(f"  SERVO_STOP = {STOP_DUTY}")
print(f"  SERVO_CW = {SLOW_CW}")
print(f"  SERVO_CCW = {SLOW_CCW}")
print(f"  SERVO_MS_PER_DEG_CW = {MS_PER_45_CW / 45:.1f}")
print(f"  SERVO_MS_PER_DEG_CCW = {MS_PER_45_CCW / 45:.1f}")
