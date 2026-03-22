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

        # === YELLOW ZONE (y=0-15) — 16 chars max ===
        # "GridBox  . LIVE" = 15 chars, fits perfectly
        oled.text("GridBox", 0, 4, 1)
        draw_spinner(oled, 84, 5, tick)  # spinner next to LIVE
        oled.text("LIVE", 96, 4, 1)

        # === BLUE ZONE (y=16-63) — 16 chars per line ===

        m1 = 340 + (tick * 7) % 60
        m2 = 270 + (tick * 5) % 40
        m1_pct = 60 + (tick * 3) % 20
        m2_pct = 40 + (tick * 2) % 15

        # M1 with mini bar
        oled.text("M1", 0, 18, 1)
        bar_w = int(m1_pct * 36 / 100)
        oled.rect(20, 18, 38, 7, 1)
        oled.fill_rect(21, 19, bar_w, 5, 1)
        oled.text(f"{m1}mA", 62, 18, 1)

        # M2 with mini bar
        oled.text("M2", 0, 28, 1)
        bar_w2 = int(m2_pct * 36 / 100)
        oled.rect(20, 28, 38, 7, 1)
        oled.fill_rect(21, 29, bar_w2, 5, 1)
        oled.text(f"{m2}mA", 62, 28, 1)

        # Voltage + Power + IMU — fits in 16 chars
        bus = 4.85 + (tick % 10) * 0.01
        total_w = bus * (m1 + m2) / 1000
        imu = 0.25 + (tick % 5) * 0.05
        oled.text(f"{bus:.1f}V {total_w:.1f}W", 0, 39, 1)
        oled.text(f"{imu:.1f}g", 104, 39, 1)

        # Production + state — bottom
        items = tick // 3
        passed = int(items * 0.87)
        rejected = items - passed
        oled.hline(0, 49, 128, 1)
        oled.text(f"P:{passed}", 0, 52, 1)
        oled.text(f"R:{rejected}", 48, 52, 1)

        if tick % 30 < 25:
            oled.text("OK", 112, 52, 1)
        else:
            if tick % 2 == 0:
                oled.text("!!", 112, 52, 1)

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
