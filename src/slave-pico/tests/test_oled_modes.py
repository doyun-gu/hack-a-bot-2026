"""
Test: OLED display modes — see which looks best on your screen.
Cycles through 4 display modes. Pick the one easiest on your eyes.

Usage: mpremote cp src/slave-pico/micropython/ssd1306.py :ssd1306.py
       mpremote cp src/slave-pico/micropython/config.py :config.py
       mpremote run src/slave-pico/tests/test_oled_modes.py
"""

import sys
sys.path.append('/micropython')

from machine import Pin, I2C
import time
import config
from ssd1306 import SSD1306

led = Pin(25, Pin.OUT)

i2c = I2C(config.I2C_ID, sda=Pin(config.I2C_SDA),
          scl=Pin(config.I2C_SCL), freq=config.I2C_FREQ)

oled = SSD1306(i2c, width=config.OLED_WIDTH,
               height=config.OLED_HEIGHT, addr=config.SSD1306_ADDR)

def draw_sample(oled, mode_name, inverted):
    """Draw a sample dashboard screen."""
    fg = 0 if inverted else 1
    bg = 1 if inverted else 0

    oled.fill(bg)

    # Yellow zone (y=0-15) — header only, nothing else
    oled.text("GridBox", 0, 4, fg)
    oled.fill_rect(60, 6, 4, 4, fg)  # status dot
    oled.text("LIVE", 100, 4, fg)

    # Blue zone (y=16-63) — all content below the yellow band
    oled.text(f"Mode: {mode_name}", 0, 18, fg)
    oled.text("M1: 350mA  65%", 0, 28, fg)
    oled.text("M2: 280mA  45%", 0, 38, fg)
    oled.text("Bus: 4.9V  OK", 0, 48, fg)
    oled.text("IMU: 0.3g  OK", 0, 58, fg)

    oled.show()


print("=" * 40)
print("  OLED Display Mode Test")
print("  5 seconds per mode")
print("  Pick your favourite!")
print("=" * 40)

modes = [
    ("NORMAL", False, False),
    ("INVERTED", False, True),
    ("DIM", True, False),
    ("DIM+INV", True, True),
]

while True:
    for name, dim, inverted in modes:
        print(f"\n>> Mode: {name}")
        print(f"   Inverted: {inverted}, Dim: {dim}")
        print(f"   Showing for 5 seconds...")

        oled.invert(inverted)

        if dim:
            oled.contrast(30)
        else:
            oled.contrast(255)

        draw_sample(oled, name, False)
        led.toggle()

        # Count down
        for i in range(5, 0, -1):
            print(f"   {i}...")
            time.sleep(1)

    print("\n>> Cycling again. Press Ctrl+C to stop.")
    print(">> Tell me which mode you prefer!")
