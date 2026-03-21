"""
Test: Analog joystick reading
Reads X/Y axes and button. Shows raw ADC values + direction.

Usage: mpremote run test_joystick.py
"""

from machine import Pin, ADC
import time

JOY_X = 26
JOY_Y = 27
JOY_BTN = 22

joy_x = ADC(Pin(JOY_X))
joy_y = ADC(Pin(JOY_Y))
joy_btn = Pin(JOY_BTN, Pin.IN, Pin.PULL_UP)

CENTRE = 32768
DEADZONE = 5000

print("=" * 40)
print("  Joystick Test")
print(f"  X=GP{JOY_X}, Y=GP{JOY_Y}, BTN=GP{JOY_BTN}")
print("=" * 40)

while True:
    x = joy_x.read_u16()
    y = joy_y.read_u16()
    btn = not joy_btn.value()  # active low

    # Direction
    dx = x - CENTRE
    dy = y - CENTRE
    direction = "CENTRE"
    if abs(dx) > DEADZONE or abs(dy) > DEADZONE:
        if abs(dx) > abs(dy):
            direction = "RIGHT" if dx > 0 else "LEFT"
        else:
            direction = "DOWN" if dy > 0 else "UP"

    btn_str = "PRESSED" if btn else ""
    print(f"X={x:5d}  Y={y:5d}  Dir={direction:6s}  {btn_str}")
    time.sleep(0.1)
