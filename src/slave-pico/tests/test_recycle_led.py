# Test: Recycle path LED with 2N2222 + capacitor
# Wiring: GP22 → 1kΩ → Base (Pin 2), 5V → Collector (Pin 3),
#         Emitter (Pin 1) → Cap(+) → LED → 150Ω → GND
#
# GP22 HIGH = transistor ON = cap charges, LED on
# GP22 LOW  = transistor OFF = cap discharges through LED, LED fades

from machine import Pin
import time

RECYCLE_PIN = 22
pin = Pin(RECYCLE_PIN, Pin.OUT)

print("=== Recycle Path LED Test (GP22 + 2N2222) ===")
print("Watch the LED: should light on HIGH, fade on LOW")
print()

cycle = 0
while True:
    cycle += 1

    # ON
    pin.high()
    print(f"[{cycle}] HIGH — ON")
    time.sleep(1)

    # OFF
    pin.low()
    print(f"[{cycle}] LOW  — OFF")
    time.sleep(1)

    print()
