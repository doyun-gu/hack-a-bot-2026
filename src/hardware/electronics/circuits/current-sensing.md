# Current Sensing Circuit — Motor 1 & Motor 2

> Author: Wooseong Jung (Electronics)
> Covers the 1Ω sense resistor + voltage divider ADC connection for GP27 and GP28.
> Critical for Model A fault detection and smart sorting system.

---

## Principle

A 1Ω resistor is placed in series with the motor current path. By measuring the voltage across it with the Pico ADC, we calculate current using Ohm's Law:

```
V_sense = I_motor × R_sense = I_motor × 1.0Ω

I_motor (mA) = V_sense (mV) / 1.0Ω
```

The Pico ADC reads 0–3.3V in 65,536 steps (16-bit). At 500mA motor current:

```
V_sense = 0.5A × 1.0Ω = 0.5V

ADC counts = (0.5V / 3.3V) × 65535 = 9930 counts   ✓ readable
```

---

## Full Circuit — Motor 2 (GP28) — Primary Sorting Sense

```
                       Motor Power Rail (+6–9V)
                               │
                               ▼
                       Motor 2 (+) terminal
                       ┌───────────────────┐
                       │    DC MOTOR 2     │
                       │    (conveyor)     │
                       └───────────────────┘
                       Motor 2 (−) terminal
                               │
              ┌────────────────┴────────────────────────┐
              │                                         │
              │    R_sense = 1.0Ω, 1W (1% tolerance)   │
              │    ───────[ 1Ω ]─────                   │
              │                │                        │
              │                └──── ADC SENSE POINT    │
              │                           │             │
              │                          [R1]           │
              │                          10kΩ           │
              │                           │             │
              │                      GP28 (ADC2) ───────┘
              │                           │
              │                          [R2]
              │                          10kΩ
              │                           │
              └────────────────────── GND ┘

Wait — for motor current sensing, the sense resistor voltage is already
within ADC range (max ~0.9V at 900mA stall current).
A voltage divider is NOT needed for the sense resistor.

The voltage divider (10kΩ + 10kΩ) is used ONLY for GP26 bus voltage sensing
(which can be up to 9V — needs dividing to keep under 3.3V).

SIMPLIFIED CORRECT CIRCUIT — Motor 2 sense (GP28):

Motor 2 (−) terminal
        │
       [1Ω / 1W]          ← in series with motor ground return
        │
        ├──────────── GP28 (ADC2) on Pico A   ← tap voltage here
        │
   MOSFET drain (IRF540N)
        │
       GND
```

---

## Bus Voltage Sensing — GP26 (Voltage Divider Required)

The motor bus voltage (6–9V) must be divided before it reaches the ADC (max 3.3V input). A 1:2 divider halves the voltage.

```
Motor Power Rail (+6–9V)
        │
       [R1 = 10kΩ]
        │
        ├──────────── GP26 (ADC0) on Pico A   ← V_adc = V_bus / 2
        │
       [R2 = 10kΩ]
        │
       GND

V_adc = V_bus × R2 / (R1 + R2) = V_bus × 10k / 20k = V_bus / 2

At V_bus = 9V:    V_adc = 4.5V  ← TOO HIGH, exceeds 3.3V, damages ADC!

Correction: use 10kΩ + 20kΩ divider for safe margin:
  V_adc = 9V × 20k / 30k = 6V  ← still too high

Use 10kΩ + 30kΩ:
  V_adc = 9V × 30k / 40k = 6.75V  ← still too high

Correct approach — use 3.3V as reference and measure fraction of bus:
  R1 = 47kΩ, R2 = 10kΩ
  V_adc = 9V × 10k / 57k = 1.58V  ✓ safe
  V_adc = 6V × 10k / 57k = 1.05V  ✓ safe

Or set the buck-boost to max 6V and use the original 10kΩ + 10kΩ:
  V_adc = 6V × 10k / 20k = 3.0V  ✓ just within range (keep motor rail ≤6V)

ACTION: Wire 10kΩ + 10kΩ divider but cap buck-boost output at 6V max.
        If running motors at higher voltage, switch to 47kΩ + 10kΩ.
```

---

## ADC Reading → Current Conversion (MicroPython)

```python
import machine

adc_m2 = machine.ADC(28)   # GP28 — Motor 2 current
adc_m1 = machine.ADC(27)   # GP27 — Motor 1 current
adc_bus = machine.ADC(26)  # GP26 — Bus voltage

VREF      = 3.3            # Pico ADC reference voltage
ADC_MAX   = 65535          # 16-bit
R_SENSE   = 1.0            # ohms
R_DIVIDER = 2.0            # bus voltage divider ratio (10k + 10k)

def read_current_mA(adc_pin):
    raw = adc_pin.read_u16()
    v_sense = (raw / ADC_MAX) * VREF       # voltage across sense resistor
    i_mA = (v_sense / R_SENSE) * 1000     # convert to milliamps
    return i_mA

def read_bus_voltage():
    raw = adc_bus.read_u16()
    v_adc = (raw / ADC_MAX) * VREF
    v_bus = v_adc * R_DIVIDER              # undo the divider
    return v_bus

# Example readings
i_motor2 = read_current_mA(adc_m2)   # e.g. 420.5 mA
i_motor1 = read_current_mA(adc_m1)   # e.g. 312.0 mA
v_bus    = read_bus_voltage()         # e.g. 6.02 V
```

---

## Calibration Procedure

Before the demo, verify the sense circuit is reading correctly:

### Step 1 — Zero check (motor off)
```
1. GP10 LOW and GP11 LOW (both motors off)
2. Read GP27 and GP28 via serial REPL
3. Expected: < 50 counts (≈ 0mA offset, just noise)
4. If reading > 200 counts with motor off: sense resistor is shorted to a voltage source
```

### Step 2 — Live reading (motor running)
```
1. GP11 HIGH (Motor 2 on, conveyor running, no load)
2. Read GP28
3. Expected: 5000–15000 counts (≈ 250–750 mA range for typical DC motor)
4. If reading = 0: MOSFET not switching, check GP11 wiring
5. If reading = 65535: ADC saturated, sense resistor not in circuit or shorted
```

### Step 3 — Load test (press belt)
```
1. Motor 2 running at steady state
2. Press finger firmly on conveyor belt
3. GP28 reading should rise visibly (50–200 counts increase)
4. Release — reading returns to baseline within 2s
5. If no change: sense resistor in wrong position (not in motor ground return)
```

### Step 4 — Bus voltage check
```
1. Measure motor rail voltage with multimeter
2. Read GP26 via serial REPL: v_bus = read_bus_voltage()
3. Compare — should match within ±5% (0.3V at 6V)
4. If large discrepancy: check R1/R2 values (measure with multimeter)
```

---

## Component Checklist

| Component | Value | Qty | Location in circuit |
|---|---|---|---|
| Sense resistor R1 (Motor 1) | 1.0Ω, 1W, 1% | 1 | Motor 1 ground return → GP27 |
| Sense resistor R2 (Motor 2) | 1.0Ω, 1W, 1% | 1 | Motor 2 ground return → GP28 |
| Bus divider R_high | 10kΩ, 0.25W | 1 | Motor rail (+) → GP26 junction |
| Bus divider R_low | 10kΩ, 0.25W | 1 | GP26 junction → GND |
| I2C pull-up (SDA) | 4.7kΩ, 0.25W | 1 | 3.3V → GP4 |
| I2C pull-up (SCL) | 4.7kΩ, 0.25W | 1 | 3.3V → GP5 |

All resistors are in the assorted components kit. Verify value with multimeter before placing — colour bands are easy to misread under hackathon lighting.
