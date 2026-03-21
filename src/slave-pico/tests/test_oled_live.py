"""
Test: OLED live monitoring display — DIM mode with activity spinner.

Yellow zone: GridBox + rotating spinner (proves system is alive)
Blue zone: key metrics only — what an operator needs at a glance

Usage: mpremote cp src/slave-pico/micropython/ssd1306.py :ssd1306.py
       mpremote cp src/slave-pico/micropython/config.py :config.py
       mpremote run src/slave-pico/tests/test_oled_live.py
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

# DIM mode — easier on the eyes
oled.contrast(40)

# Spinner frames: ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏ (can't use unicode on OLED, use pixel patterns)
# Simple 4-frame spinner drawn with pixels: | / - \
SPINNER = [
    [(2,0),(2,1),(2,2),(2,3),(2,4)],           # |
    [(0,4),(1,3),(2,2),(3,1),(4,0)],            # /
    [(0,2),(1,2),(2,2),(3,2),(4,2)],            # -
    [(0,0),(1,1),(2,2),(3,3),(4,4)],            # \
]

def draw_spinner(oled, x, y, frame):
    """Draw a 5x5 pixel spinner at position."""
    # Clear spinner area
    oled.fill_rect(x, y, 5, 5, 0)
    # Draw current frame
    for px, py in SPINNER[frame % 4]:
        oled.pixel(x + px, y + py, 1)

# Boot sequence — engineering style
oled.fill(0)
oled.text("GridBox v2", 24, 4, 1)
oled.show()
time.sleep_ms(500)

checks = ["I2C", "OLED", "Sensors", "Ready"]
for i, name in enumerate(checks):
    oled.text(f"{name}", 4, 18 + i * 10, 1)
    oled.show()
    time.sleep_ms(200)
    oled.text("OK", 108, 18 + i * 10, 1)
    oled.show()
    led.toggle()
    time.sleep_ms(200)

time.sleep_ms(500)

print("=" * 40)
print("  OLED Live Monitor — DIM mode")
print("  LED heartbeat + spinner")
print("  Ctrl+C to stop")
print("=" * 40)

tick = 0
try:
    while True:
        oled.fill(0)

        # === YELLOW ZONE (y=0-15) — status bar ===
        oled.text("GridBox", 0, 4, 1)
        draw_spinner(oled, 56, 5, tick)  # rotating spinner
        # Connection indicator: solid square = connected
        oled.fill_rect(72, 5, 5, 5, 1)
        oled.text("LIVE", 100, 4, 1)

        # === BLUE ZONE (y=16-63) — metrics ===

        # Motor status — compact, scannable
        m1 = 340 + (tick * 7) % 60
        m2 = 270 + (tick * 5) % 40
        m1_pct = 60 + (tick * 3) % 20

        oled.text("M1", 0, 18, 1)
        # Mini bar for M1
        bar_w = int(m1_pct * 40 / 100)
        oled.rect(20, 18, 42, 7, 1)
        oled.fill_rect(21, 19, bar_w, 5, 1)
        oled.text(f"{m1}mA", 66, 18, 1)

        m2_pct = 40 + (tick * 2) % 15
        oled.text("M2", 0, 28, 1)
        bar_w2 = int(m2_pct * 40 / 100)
        oled.rect(20, 28, 42, 7, 1)
        oled.fill_rect(21, 29, bar_w2, 5, 1)
        oled.text(f"{m2}mA", 66, 28, 1)

        # Power + Voltage — single line
        bus = 4.85 + (tick % 10) * 0.01
        total_w = bus * (m1 + m2) / 1000
        oled.text(f"{bus:.1f}V", 0, 39, 1)
        oled.text(f"{total_w:.1f}W", 40, 39, 1)

        # IMU — small with status
        imu = 0.25 + (tick % 5) * 0.05
        status = "OK" if imu < 1.0 else "!"
        oled.text(f"IMU:{imu:.1f}g", 80, 39, 1)

        # Production — bottom section
        items = tick // 3
        passed = int(items * 0.87)
        rejected = items - passed
        oled.hline(0, 49, 128, 1)
        oled.text(f"P:{passed}", 0, 52, 1)
        oled.text(f"R:{rejected}", 40, 52, 1)

        # State indicator — bottom right
        if tick % 30 < 25:
            oled.text("NORMAL", 80, 52, 1)
        else:
            # Blink WARNING
            if tick % 2 == 0:
                oled.text("WARN", 88, 52, 1)

        oled.show()

        # LED heartbeat — toggle every cycle
        led.toggle()
        tick += 1

        # Serial output every 2 seconds
        if tick % 4 == 0:
            print(f"[LIVE] t={tick} M1={m1}mA M2={m2}mA Bus={bus:.2f}V Items={items}")

        time.sleep_ms(500)

except KeyboardInterrupt:
    led.value(0)
    oled.contrast(255)
    oled.fill(0)
    oled.text("Stopped", 36, 28, 1)
    oled.show()
    print("\nStopped. Brightness restored.")
