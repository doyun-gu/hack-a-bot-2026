"""
Test: ADC on GP26 + GP27 only (partial solder — GP16 to GP27 available)

What to try:
- Touch GP26 with a wire connected to 3.3V → reading jumps to ~65535
- Touch GP26 with a wire connected to GND → reading drops to ~0
- Same for GP27
- Leave floating → reads random noise (~30000-40000)

If voltage divider is wired (10kΩ+10kΩ from 5V bus to GP26):
  → should read ~half of bus voltage

If 1Ω sense resistor is wired (motor return path to GP27):
  → should read voltage proportional to motor current

Usage: mpremote run test_adc_partial.py
"""

from machine import Pin, ADC
import time

adc26 = ADC(Pin(26))
adc27 = ADC(Pin(27))

print("=" * 40)
print("  ADC Test (GP26 + GP27 only)")
print("  Touch pins with 3.3V or GND wire")
print("  Ctrl+C to stop")
print("=" * 40)

while True:
    raw26 = adc26.read_u16()
    raw27 = adc27.read_u16()

    # Convert to voltage (0-3.3V range)
    v26 = raw26 * 3.3 / 65535
    v27 = raw27 * 3.3 / 65535

    # If voltage divider on GP26: actual bus voltage = v26 * 2
    bus_v = v26 * 2.0

    # If 1Ω sense resistor on GP27: current in mA
    current_ma = v27 / 1.0 * 1000

    print(f"GP26: {raw26:5d} ({v26:.3f}V) Bus:{bus_v:.2f}V  |  "
          f"GP27: {raw27:5d} ({v27:.3f}V) I:{current_ma:.1f}mA")

    time.sleep_ms(200)
