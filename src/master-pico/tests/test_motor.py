"""
Test: PCA9685 Motor Speed Ramp
Ramps motor on channel 2 from 0% to 100% and back down.

Usage: mpremote run test_motor.py
"""

import sys
sys.path.append('/micropython')

from machine import Pin, I2C
import time
import config
from pca9685 import PCA9685

print("=" * 40)
print("  PCA9685 Motor Speed Ramp Test")
print("  Channel 2: 0% → 100% → 0%")
print("=" * 40)

i2c = I2C(config.I2C_ID, sda=Pin(config.I2C_SDA),
          scl=Pin(config.I2C_SCL), freq=config.I2C_FREQ)

try:
    pca = PCA9685(i2c, addr=config.PCA9685_ADDR, freq=1000)  # 1kHz for motors
    print("PCA9685 OK (1kHz motor mode)\n")

    cycle = 0
    while True:
        cycle += 1
        print(f"--- Cycle {cycle} ---")

        # Ramp up
        for speed in range(0, 101, 5):
            pca.set_motor_speed(config.MOTOR1_PWM_CH, speed)
            print(f"  Speed: {speed:3d}%")
            time.sleep_ms(100)

        time.sleep_ms(1000)

        # Ramp down
        for speed in range(100, -1, -5):
            pca.set_motor_speed(config.MOTOR1_PWM_CH, speed)
            print(f"  Speed: {speed:3d}%")
            time.sleep_ms(100)

        time.sleep_ms(1000)

except OSError as e:
    print(f"I2C error: {e}")
    print("Check PCA9685 wiring")
