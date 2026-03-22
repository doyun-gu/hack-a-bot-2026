"""
Test: I2C bus scan
Run this FIRST when wiring up I2C devices (IMU, PCA9685, OLED).
Shows all detected addresses.

Expected addresses:
  0x68 or 0x69 = BMI160 IMU
  0x40 = PCA9685 servo driver
  0x3C = SSD1306 OLED

Usage: mpremote run test_i2c_scan.py
"""

from machine import Pin, I2C
import time

I2C_SDA = 4
I2C_SCL = 5

print("=" * 40)
print("  I2C Bus Scanner")
print("=" * 40)

i2c = I2C(0, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=400_000)

KNOWN = {
    0x3C: "SSD1306 OLED",
    0x40: "PCA9685 Servo Driver",
    0x68: "BMI160 IMU (SDO=GND)",
    0x69: "BMI160 IMU (SDO=VCC)",
}

while True:
    devices = i2c.scan()
    if devices:
        print(f"\nFound {len(devices)} device(s):")
        for addr in devices:
            name = KNOWN.get(addr, "Unknown")
            print(f"  0x{addr:02X} = {name}")
    else:
        print("\nNo I2C devices found! Check wiring:")
        print(f"  SDA = GP{I2C_SDA}")
        print(f"  SCL = GP{I2C_SCL}")
        print("  VCC = 3.3V")
        print("  GND = GND")

    time.sleep(2)
