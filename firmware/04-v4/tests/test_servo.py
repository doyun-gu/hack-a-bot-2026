"""
Test: PCA9685 Servo Sweep
Sweeps servo on channel 0 from 0° to 180° and back.

Usage: mpremote run test_servo.py
"""

import sys
sys.path.append('/micropython')

from machine import Pin, I2C
import time
import config
from pca9685 import PCA9685

print("=" * 40)
print("  PCA9685 Servo Sweep Test")
print("  Channel 0: 0° → 180° → 0°")
print("=" * 40)

i2c = I2C(config.I2C_ID, sda=Pin(config.I2C_SDA),
          scl=Pin(config.I2C_SCL), freq=config.I2C_FREQ)

try:
    pca = PCA9685(i2c, addr=config.PCA9685_ADDR, freq=50)
    print("PCA9685 OK\n")

    cycle = 0
    while True:
        cycle += 1
        print(f"--- Cycle {cycle} ---")

        # Sweep up
        for angle in range(0, 181, 5):
            pca.set_servo_angle(config.SERVO_VALVE_CH, angle)
            print(f"  Angle: {angle:3d}°")
            time.sleep_ms(50)

        time.sleep_ms(500)

        # Sweep down
        for angle in range(180, -1, -5):
            pca.set_servo_angle(config.SERVO_VALVE_CH, angle)
            print(f"  Angle: {angle:3d}°")
            time.sleep_ms(50)

        time.sleep_ms(500)

except OSError as e:
    print(f"I2C error: {e}")
    print("Check PCA9685 wiring")
