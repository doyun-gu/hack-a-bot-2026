# Electronics — Wooseong's Workspace

## Folder Structure

| Folder | What Goes Here |
|---|---|
| `circuits/` | Circuit diagrams, schematics (Fritzing, KiCad, hand-drawn scans) |
| `testing/` | Test results, multimeter readings, oscilloscope captures |
| `photos/` | Photos of wiring progress, completed circuits |

## Your Tasks (from team-plan.md)

| # | Task | Time |
|---|---|---|
| W1 | Power supply chain (PSU → buck → 5V, PSU → boost → 6-12V) | Hour 0-1.5 |
| W2 | Pico A wiring (I2C + SPI + ADC) | Hour 1.5-3 |
| W3 | MOSFET switching circuits (×4) | Hour 3-5 |
| W4 | Voltage divider (10kΩ + 10kΩ) | Hour 5-5.5 |
| W5 | Current sense resistors (×2, 1Ω each) | Hour 5.5-6 |
| W6 | IMU mounting + wiring | Hour 6-6.5 |
| W7 | Pico B wiring (OLED + joystick + pot + nRF) | Hour 6.5-8 |
| W8 | LED status tower | Hour 8-9 |
| W9 | Integration test with Doyun | Hour 9-10 |
| W10-12 | Debug, wire management, backups | Hour 10-14 |

## Pin Reference (must match exactly)

### Pico A

| Pin | Wire To | Colour |
|---|---|---|
| GP0 | nRF CE | — |
| GP1 | nRF CSN | — |
| GP2 | nRF SCK | — |
| GP3 | nRF MOSI | — |
| GP4 | I2C SDA → BMI160 + PCA9685 | White |
| GP5 | I2C SCL → BMI160 + PCA9685 | Grey |
| GP10 | 1kΩ → MOSFET gate (Motor 1 switch) | Yellow |
| GP11 | 1kΩ → MOSFET gate (Motor 2 switch) | Yellow |
| GP12 | 1kΩ → MOSFET gate (LED bank) | Yellow |
| GP13 | 1kΩ → MOSFET gate (Recycle path) | Yellow |
| GP14 | 330Ω → Red LED → GND | Red wire |
| GP15 | 330Ω → Green LED → GND | Green wire |
| GP16 | nRF MISO | — |
| GP26 | Voltage divider junction (10kΩ+10kΩ from bus) | Green |
| GP27 | Across 1Ω sense resistor (Motor 1) | Green |
| GP28 | Across 1Ω sense resistor (Motor 2) | Green |
| VSYS | 5V from buck converter | Orange |
| GND | Common ground rail | Black |

### Pico B

| Pin | Wire To | Colour |
|---|---|---|
| GP0 | nRF CE | — |
| GP1 | nRF CSN | — |
| GP2 | nRF SCK | — |
| GP3 | nRF MOSI | — |
| GP4 | I2C SDA → OLED | White |
| GP5 | I2C SCL → OLED | Grey |
| GP14 | 330Ω → Red LED → GND | Red |
| GP15 | 330Ω → Green LED → GND | Green |
| GP16 | nRF MISO | — |
| GP22 | Joystick button (pull-up) | — |
| GP26 | Joystick X axis | — |
| GP27 | Joystick Y axis | — |
| GP28 | Potentiometer wiper | — |

## How to Commit Your Work

```bash
git checkout wooseong/electronics
git add .
git commit -m "describe what you did"
git push
# Then create a PR on GitHub for Doyun to review
```
