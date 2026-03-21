"""
Test: SSD1306 OLED Display
Shows "GridBox SCADA" title with mock status data.

Usage: mpremote run test_oled.py
"""

import sys
sys.path.append('/micropython')

from machine import Pin, I2C
import time
import config
from ssd1306 import SSD1306

print("=" * 40)
print("  SSD1306 OLED Display Test")
print("=" * 40)

i2c = I2C(config.I2C_ID, sda=Pin(config.I2C_SDA),
          scl=Pin(config.I2C_SCL), freq=config.I2C_FREQ)

try:
    oled = SSD1306(i2c, width=config.OLED_WIDTH,
                   height=config.OLED_HEIGHT, addr=config.SSD1306_ADDR)
    print(f"OLED OK: {config.OLED_WIDTH}x{config.OLED_HEIGHT}\n")

    # Screen 1: Title + status
    oled.fill(0)
    oled.rect(0, 0, 128, 64, 1)
    oled.text("GridBox SCADA", 12, 4, 1)
    oled.hline(4, 14, 120, 1)
    oled.text("Motor 1: OK", 8, 20, 1)
    oled.text("Motor 2: OK", 8, 32, 1)
    oled.text("Bus: 4.9V", 8, 44, 1)
    oled.show()
    print("Screen 1: System status")
    time.sleep(3)

    # Screen 2: Power bars
    oled.fill(0)
    oled.rect(0, 0, 128, 64, 1)
    oled.text("Power Flow", 24, 4, 1)
    oled.hline(4, 14, 120, 1)

    # Draw power bars
    oled.text("M1", 4, 20, 1)
    oled.rect(24, 20, 100, 8, 1)
    oled.fill_rect(24, 20, 65, 8, 1)  # 65% power

    oled.text("M2", 4, 34, 1)
    oled.rect(24, 34, 100, 8, 1)
    oled.fill_rect(24, 34, 40, 8, 1)  # 40% power

    oled.text("Total: 1.9W", 8, 50, 1)
    oled.show()
    print("Screen 2: Power flow")
    time.sleep(3)

    # Screen 3: Invert test
    oled.invert(True)
    print("Screen 3: Inverted")
    time.sleep(2)
    oled.invert(False)
    print("Reverted to normal")

    print("\nOLED test complete")

except OSError as e:
    print(f"I2C error: {e}")
    print("Check OLED wiring: SDA=GP4, SCL=GP5, VCC=3.3V, GND=GND")
