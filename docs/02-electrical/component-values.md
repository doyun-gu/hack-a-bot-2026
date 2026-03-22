# Component Values — Resistors, Capacitors & Protection

> Print this and keep it next to you while wiring. Every component value in one place.

---

## Reference Pinout

> Use this to locate the GP pins referenced in the table below.

<p>
<img src="../images/pico2_pinout_reference.png" alt="Pico 2 Pinout" width="600"/>
</p>

---

## Resistors Required

| # | Value | Colour Bands | Qty | Purpose | Connected Between |
|---|---|---|---|---|---|
| R1 | **10kΩ** | Brown-Black-Orange | 1 | Voltage divider (upper) | 5V bus → GP26 junction |
| R2 | **10kΩ** | Brown-Black-Orange | 1 | Voltage divider (lower) | GP26 junction → GND |
| R3 | **1Ω** | Brown-Black-Gold | 1 | Motor 1 current sense | Motor 1 return → MOSFET 1 drain |
| R4 | **1Ω** | Brown-Black-Gold | 1 | Motor 2 current sense | Motor 2 return → MOSFET 2 drain |
| R5 | **4.7kΩ** | Yellow-Violet-Red | 1 | I2C SDA pull-up | 3.3V → GP4 (SDA line) |
| R6 | **4.7kΩ** | Yellow-Violet-Red | 1 | I2C SCL pull-up | 3.3V → GP5 (SCL line) |
| R7 | **1kΩ** | Brown-Black-Red | 1 | MOSFET 1 gate resistor | GP10 → MOSFET 1 gate |
| R8 | **1kΩ** | Brown-Black-Red | 1 | MOSFET 2 gate resistor | GP11 → MOSFET 2 gate |
| R9 | **1kΩ** | Brown-Black-Red | 1 | MOSFET 3 gate resistor | GP12 → MOSFET 3 gate |
| R10 | **1kΩ** | Brown-Black-Red | 1 | MOSFET 4 gate resistor | GP13 → MOSFET 4 gate |
| R11 | **330Ω** | Orange-Orange-Brown | 1 | Red LED current limit | GP14 → Red LED anode |
| R12 | **330Ω** | Orange-Orange-Brown | 1 | Green LED current limit | GP15 → Green LED anode |
| R13-16 | **330Ω** | Orange-Orange-Brown | 4 | Load LED current limit (P1-P4) | 5V → each load LED |

**Total resistors: 16**

### If You Don't Have Exact Values

| Need | Acceptable Alternatives |
|---|---|
| 10kΩ | 8.2kΩ – 15kΩ (use matching pair for divider) |
| 1Ω | 0.5Ω – 2.2Ω (adjust formula in config.py: `CURRENT_SENSE_R = your_value`) |
| 4.7kΩ | 2.2kΩ – 10kΩ for I2C pull-ups |
| 1kΩ | 470Ω – 2.2kΩ for MOSFET gates |
| 330Ω | 220Ω – 1kΩ for LEDs (dimmer/brighter but safe) |

---

## Capacitors Required

| # | Value | Type | Purpose | Connected Between |
|---|---|---|---|---|
| C1 | **100µF** | Electrolytic | Main power bus smoothing — prevents voltage spikes when motors start/stop | 5V rail (+) → GND (−) |
| C2 | **100nF (0.1µF)** | Ceramic | Pico VSYS decoupling — filters high-frequency noise from power supply | Pico VSYS pin → GND (as close to Pico as possible) |
| C3 | **100nF (0.1µF)** | Ceramic | PCA9685 decoupling — stable I2C communication | PCA9685 VCC → GND (next to the chip) |
| C4 | **100nF (0.1µF)** | Ceramic | BMI160 decoupling — stable IMU readings | BMI160 VCC → GND (next to the sensor) |
| C5 | **10µF** | Electrolytic or ceramic | nRF24L01+ power stabilisation — nRF is very sensitive to power noise | nRF VCC (3.3V) → GND (directly on the nRF module pins) |
| C6 | **100nF (0.1µF)** | Ceramic | OLED decoupling | OLED VCC → GND |
| C7 | **100µF** | Electrolytic | Motor power rail smoothing | Motor rail (+) → GND (−) |

**Total capacitors: 7** (2 × 100µF electrolytic, 4 × 100nF ceramic, 1 × 10µF)

### Why Decoupling Matters

Without decoupling capacitors:
- Motors starting can cause **voltage dips** → Pico resets
- nRF24L01+ is **extremely sensitive** to power noise → random packet loss or complete failure
- I2C communication can get **corrupted** → IMU/PCA9685/OLED errors

**The 10µF on nRF24L01+ is critical.** If you only add one capacitor, make it this one. Many nRF problems are actually power problems.

---

## Circuit Diagrams

### Voltage Divider (GP26)

```
5V Bus ──── R1 (10kΩ) ──── Junction ──── R2 (10kΩ) ──── GND
                              │
                           GP26 (ADC)
                              │
                   V_ADC = 5V × 10k/(10k+10k) = 2.5V
```

$$V_{ADC} = V_{bus} \times \frac{R_2}{R_1 + R_2} = V_{bus} \times \frac{10k}{20k} = \frac{V_{bus}}{2}$$

**In firmware:** `bus_voltage = adc_reading * 3.3 / 65535 * 2`

### Current Sense (GP27, GP28)

```
Motor Rail ──→ Motor (+) ──→ Motor (−) ──→ R_sense (1Ω) ──→ MOSFET drain
                                               │
                                            GP27 (ADC)
                                               │
                                     V = I × R = I × 1Ω
```

$$I_{motor} = \frac{V_{ADC}}{R_{sense}} = \frac{V_{ADC}}{1.0\Omega}$$

**In firmware:** `current_mA = adc_reading * 3.3 / 65535 / 1.0 * 1000`

| Motor Current | Voltage on ADC | Safe? |
|---|---|---|
| 100mA | 0.1V | Yes |
| 350mA (normal) | 0.35V | Yes |
| 500mA (loaded) | 0.5V | Yes |
| 800mA (stall) | 0.8V | Yes |
| 1200mA (max stall) | 1.2V | Yes — still under 3.3V |

### MOSFET Switching (GP10-13)

```
Pico GPIO ──── R_gate (1kΩ) ──── MOSFET Gate
                                  MOSFET Drain ──── Load (Motor/LED)
                                  MOSFET Source ──── GND
```

The 1kΩ gate resistor:
- Limits inrush current to the MOSFET gate
- Prevents oscillation/ringing
- Protects Pico GPIO (max 12mA output)

$$I_{gate} = \frac{3.3V}{1k\Omega} = 3.3mA$$ (safe for Pico GPIO)

### nRF24L01+ Power (Critical)

```
3.3V ──────┬──── nRF VCC
           │
         C5 (10µF)     ← ADD THIS or wireless will be unreliable
           │
GND ───────┴──── nRF GND
```

**WARNING: nRF24L01+ MUST use 3.3V, NOT 5V. 5V will destroy it.**

### I2C Pull-ups

```
3.3V ──── R5 (4.7kΩ) ──── SDA line (GP4) ──── BMI160 SDA ──── PCA9685 SDA ──── OLED SDA
3.3V ──── R6 (4.7kΩ) ──── SCL line (GP5) ──── BMI160 SCL ──── PCA9685 SCL ──── OLED SCL
```

Some breakout boards have built-in pull-ups. If I2C already works without external pull-ups (like your OLED test), you can skip R5 and R6.

---

## ADC Pin Protection Summary

| Pin | What It Reads | Max Voltage | Protection | Safe? |
|---|---|---|---|---|
| GP26 | Bus voltage | 2.5V (after divider) | 10kΩ+10kΩ voltage divider | Yes — 2.5V < 3.3V |
| GP27 | Motor 1 current | 0.8V (at 800mA stall) | 1Ω sense resistor limits voltage | Yes — 0.8V < 3.3V |
| GP28 | Motor 2 current | 0.8V (at 800mA stall) | 1Ω sense resistor limits voltage | Yes — 0.8V < 3.3V |

**No additional protection circuitry needed.** The resistor values inherently keep all ADC inputs well under 3.3V.

### What If Motor Draws More Than Expected?

If motor stall current exceeds 1.2A (unlikely with our 200RPM motor):

$$V_{ADC\_{max}} = 1.2A \times 1\Omega = 1.2V$$ — still safe

Even at 3.3A (impossible with our motor): $V = 3.3V$ — at the ADC limit but Pico has internal clamping diodes.

---

## Shopping List (If Kit Is Missing Anything)

| Component | Qty | Approximate Cost |
|---|---|---|
| 10kΩ resistor | 2 | £0.01 |
| 1Ω resistor | 2 | £0.05 |
| 4.7kΩ resistor | 2 | £0.01 |
| 1kΩ resistor | 4 | £0.02 |
| 330Ω resistor | 6 | £0.03 |
| 100µF electrolytic capacitor | 2 | £0.10 |
| 100nF ceramic capacitor | 4 | £0.04 |
| 10µF capacitor | 1 | £0.05 |
| N-channel MOSFET (logic level) | 4 | £0.40 |
| **Total** | | **~£0.71** |
