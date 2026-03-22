"""
Test: MG90D rotate exactly 90 degrees and stop.
Since MG90D has no position sensor, we TIME the rotation.
You'll need to calibrate the timing for your specific servo.

Usage: mpremote run src/master-pico/tests/test_servo_90step.py
"""

from machine import Pin, PWM
import time

print("=" * 40)
print("  MG90D — 90 Degree Step Test")
print("  Calibrate: adjust QUARTER_TURN_MS")
print("=" * 40)

servo = PWM(Pin(0))
servo.freq(50)

STOP_DUTY = 4500
SLOW_CW = 3500       # slow clockwise
QUARTER_TURN_MS = 500  # <-- ADJUST THIS: time for 90° at slow speed

print(f"\nSettings:")
print(f"  Stop duty:  {STOP_DUTY}")
print(f"  Spin duty:  {SLOW_CW}")
print(f"  90° time:   {QUARTER_TURN_MS}ms")
print(f"\nIf 90° is wrong, change QUARTER_TURN_MS")
print(f"  Too far  → decrease the number")
print(f"  Too short → increase the number")

# Start stopped
servo.duty_u16(STOP_DUTY)
time.sleep(1)

for step in range(4):
    angle = (step + 1) * 90
    print(f"\nRotating to {angle}°...")

    # Spin for exactly QUARTER_TURN_MS
    servo.duty_u16(SLOW_CW)
    time.sleep_ms(QUARTER_TURN_MS)

    # Stop
    servo.duty_u16(STOP_DUTY)
    print(f"  Stopped at {angle}°")
    time.sleep(2)  # pause so you can see each position

print("\nFull 360° complete!")
servo.deinit()
print("Done.")
print(f"\nIf positions were wrong, edit QUARTER_TURN_MS")
print(f"  Current: {QUARTER_TURN_MS}ms")
print(f"  Try: {QUARTER_TURN_MS - 100}ms or {QUARTER_TURN_MS + 100}ms")
