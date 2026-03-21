"""
Test: ADC voltage and current sensing
Reads bus voltage (GP26), motor 1 current (GP27), motor 2 current (GP28).
Calculates and prints voltage, current, and power every 200ms.

Usage: mpremote run test_adc.py
"""

import sys
sys.path.append('/micropython')

from machine import Pin, ADC
import time
import config

print("=" * 40)
print("  ADC Power Sensing Test")
print("  GP26: Bus voltage (10k+10k divider)")
print("  GP27: Motor 1 current (1Ω sense R)")
print("  GP28: Motor 2 current (1Ω sense R)")
print("=" * 40)
print()

# Init ADC channels
adc_bus = ADC(Pin(config.ADC_BUS_VOLTAGE))
adc_m1 = ADC(Pin(config.ADC_MOTOR1_CURRENT))
adc_m2 = ADC(Pin(config.ADC_MOTOR2_CURRENT))

reading_count = 0

while True:
    reading_count += 1

    # Read raw ADC values (average 10 samples for noise reduction)
    bus_raw = 0
    m1_raw = 0
    m2_raw = 0
    for _ in range(config.ADC_SAMPLES_AVG):
        bus_raw += adc_bus.read_u16()
        m1_raw += adc_m1.read_u16()
        m2_raw += adc_m2.read_u16()
    bus_raw //= config.ADC_SAMPLES_AVG
    m1_raw //= config.ADC_SAMPLES_AVG
    m2_raw //= config.ADC_SAMPLES_AVG

    # Convert to physical units
    # Bus voltage: ADC → volts, then multiply by divider ratio
    bus_voltage = (bus_raw * config.ADC_VREF / config.ADC_RESOLUTION) * config.VOLTAGE_DIVIDER_RATIO

    # Motor current: V_sense = ADC voltage, I = V / R_sense
    m1_voltage = m1_raw * config.ADC_VREF / config.ADC_RESOLUTION
    m1_current_mA = (m1_voltage / config.CURRENT_SENSE_R) * 1000

    m2_voltage = m2_raw * config.ADC_VREF / config.ADC_RESOLUTION
    m2_current_mA = (m2_voltage / config.CURRENT_SENSE_R) * 1000

    # Calculate power: P = V * I
    m1_power_mW = bus_voltage * m1_current_mA
    m2_power_mW = bus_voltage * m2_current_mA
    total_power_mW = m1_power_mW + m2_power_mW

    # Print
    print(f"[{reading_count:4d}] "
          f"Bus={bus_voltage:.2f}V | "
          f"M1={m1_current_mA:.0f}mA ({m1_power_mW:.0f}mW) | "
          f"M2={m2_current_mA:.0f}mA ({m2_power_mW:.0f}mW) | "
          f"Total={total_power_mW:.0f}mW")

    time.sleep_ms(200)
