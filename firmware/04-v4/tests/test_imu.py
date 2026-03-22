"""
Test: BMI160 IMU — accel + gyro + shake detection
Reads and prints all axes at 100ms intervals.
Prints "SHAKE DETECTED!" when a_rms > 2.0g.

Usage: mpremote run test_imu.py
"""

import sys
sys.path.append('/micropython')

from machine import Pin, I2C
import time
import math
import config
from bmi160 import BMI160, ACC_RANGE_4G, GYR_RANGE_500

print("=" * 40)
print("  BMI160 IMU Test")
print("  Shake the board to trigger alert!")
print("=" * 40)

i2c = I2C(config.I2C_ID, sda=Pin(config.I2C_SDA),
          scl=Pin(config.I2C_SCL), freq=config.I2C_FREQ)

try:
    imu = BMI160(i2c, addr=config.BMI160_ADDR,
                 accel_range=ACC_RANGE_4G,
                 gyro_range=GYR_RANGE_500,
                 sample_rate=config.IMU_SAMPLE_RATE)

    chip_id = imu.who_am_i()
    print(f"Chip ID: 0x{chip_id:02X} {'(OK)' if chip_id == 0xD1 else '(UNEXPECTED)'}")
    print(f"Temperature: {imu.read_temperature():.1f}°C")
    print()

    led_red = Pin(config.LED_RED, Pin.OUT)
    shake_count = 0

    while True:
        d = imu.read_all()
        a_rms = math.sqrt(d['ax']**2 + d['ay']**2 + d['az']**2)

        if a_rms > 2.0:
            shake_count += 1
            led_red.value(1)
            print(f"!!! SHAKE DETECTED !!! RMS={a_rms:.2f}g (count={shake_count})")
        else:
            led_red.value(0)
            print(f"Accel: X={d['ax']:+.2f} Y={d['ay']:+.2f} Z={d['az']:+.2f} "
                  f"| Gyro: X={d['gx']:+.1f} Y={d['gy']:+.1f} Z={d['gz']:+.1f} "
                  f"| RMS={a_rms:.2f}g")

        time.sleep_ms(100)

except OSError as e:
    print(f"I2C error: {e}")
    print("Check wiring: SDA=GP4, SCL=GP5, VCC=3.3V, GND=GND")
    print("Expected I2C address: 0x68 (or 0x69 if SDO=VCC)")
