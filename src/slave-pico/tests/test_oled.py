"""
Test: SSD1306 OLED Display with live heartbeat
- OLED shows status screens
- Onboard LED toggles on every update (like airplane wing light)
- Small dot on OLED toggles to show it's live

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
print("  LED heartbeat + OLED live dot")
print("=" * 40)

# Onboard LED for heartbeat
led = Pin(25, Pin.OUT)

i2c = I2C(config.I2C_ID, sda=Pin(config.I2C_SDA),
          scl=Pin(config.I2C_SCL), freq=config.I2C_FREQ)

try:
    oled = SSD1306(i2c, width=config.OLED_WIDTH,
                   height=config.OLED_HEIGHT, addr=config.SSD1306_ADDR)
    print(f"OLED OK: {config.OLED_WIDTH}x{config.OLED_HEIGHT}\n")

    # Boot animation — loading sequence
    print("Boot animation...")

    # Phase 1: Logo fade in (GridBox text appears letter by letter)
    oled.fill(0)
    oled.show()
    time.sleep_ms(300)

    title = "GridBox"
    for i in range(len(title) + 1):
        oled.fill(0)
        oled.text(title[:i], 36, 24, 1)
        oled.show()
        led.toggle()
        time.sleep_ms(150)
    time.sleep_ms(500)

    # Phase 2: Subtitle slides in
    oled.text("SCADA System", 20, 38, 1)
    oled.show()
    time.sleep_ms(800)

    # Phase 3: Loading bar animation
    oled.fill(0)
    oled.text("GridBox", 36, 8, 1)
    oled.text("SCADA System", 20, 20, 1)
    oled.hline(14, 36, 100, 1)
    oled.show()
    time.sleep_ms(300)

    steps = [
        ("I2C Bus", 15),
        ("OLED", 30),
        ("IMU", 45),
        ("PCA9685", 55),
        ("nRF24L01+", 70),
        ("ADC", 80),
        ("MOSFETs", 90),
        ("Ready", 100),
    ]

    for label, pct in steps:
        bar_w = int(pct * 100 / 100)
        oled.fill_rect(14, 38, 100, 6, 0)  # clear bar area
        oled.rect(14, 38, 100, 6, 1)  # bar outline
        oled.fill_rect(14, 38, bar_w, 6, 1)  # fill
        oled.fill_rect(0, 50, 128, 14, 0)  # clear text area
        oled.text(f"{label}...", 14, 52, 1)
        oled.show()
        led.toggle()
        print(f"  [{pct:3d}%] {label}")
        time.sleep_ms(250)

    # Phase 4: Ready flash
    for _ in range(3):
        oled.invert(True)
        time.sleep_ms(80)
        oled.invert(False)
        time.sleep_ms(80)

    oled.fill(0)
    oled.text("  SYSTEM READY", 0, 28, 1)
    oled.show()
    led.value(1)
    time.sleep(1)
    print("Boot complete!\n")

    # Screen 1: Title + status (3 seconds)
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

    # Screen 2: Power bars (3 seconds)
    oled.fill(0)
    oled.rect(0, 0, 128, 64, 1)
    oled.text("Power Flow", 24, 4, 1)
    oled.hline(4, 14, 120, 1)
    oled.text("M1", 4, 20, 1)
    oled.rect(24, 20, 100, 8, 1)
    oled.fill_rect(24, 20, 65, 8, 1)
    oled.text("M2", 4, 34, 1)
    oled.rect(24, 34, 100, 8, 1)
    oled.fill_rect(24, 34, 40, 8, 1)
    oled.text("Total: 1.9W", 8, 50, 1)
    oled.show()
    print("Screen 2: Power flow")
    time.sleep(3)

    # Screen 3: Live heartbeat loop — runs continuously
    print("Screen 3: Live heartbeat (Ctrl+C to stop)")
    print("  LED toggles every 500ms")
    print("  OLED dot toggles every 500ms")

    tick = 0
    while True:
        # Toggle onboard LED — visible heartbeat
        led.toggle()

        # Draw live status screen with toggling dot
        oled.fill(0)
        oled.text("GridBox", 0, 0, 1)
        oled.text("LIVE", 104, 0, 1)

        # Toggling dot — proves OLED is updating
        if tick % 2 == 0:
            oled.fill_rect(96, 2, 4, 4, 1)  # dot ON
        # else: dot is OFF (blank)

        oled.hline(0, 10, 128, 1)

        # Simulated live values
        import random
        m1 = 340 + (tick * 7) % 60
        m2 = 270 + (tick * 5) % 40
        bus = 4.85 + (tick % 10) * 0.01

        oled.text(f"M1: {m1}mA  ON", 0, 14, 1)
        oled.text(f"M2: {m2}mA  ON", 0, 24, 1)
        oled.text(f"Bus: {bus:.2f}V", 0, 34, 1)
        oled.text(f"IMU: 0.3g  OK", 0, 44, 1)

        # Bottom status bar
        oled.hline(0, 54, 128, 1)
        oled.text(f"Tick:{tick:4d}", 0, 56, 1)
        status = "NORMAL" if tick % 20 < 15 else "CHECK"
        oled.text(status, 80, 56, 1)

        oled.show()
        tick += 1

        # Print to serial too
        if tick % 4 == 0:
            print(f"[LIVE] tick={tick} M1={m1}mA M2={m2}mA Bus={bus:.2f}V LED={'ON' if led.value() else 'OFF'}")

        time.sleep_ms(500)

except OSError as e:
    print(f"I2C error: {e}")
    print("Check OLED wiring: SDA=GP4, SCL=GP5, VCC=3.3V, GND=GND")
except KeyboardInterrupt:
    led.value(0)
    oled.fill(0)
    oled.text("Test stopped", 16, 28, 1)
    oled.show()
    print("\nTest stopped cleanly")
