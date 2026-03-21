# Wiring Connection Table — Every Wire in the System

> Print this and check off each connection as you wire it. Every wire is listed once.

---

## Power Supply Chain

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| P1 | **12V PSU +** | LM2596S buck converter IN+ | Red 16AWG | Main power input |
| P2 | **12V PSU +** | 300W buck-boost IN+ | Red 16AWG | Motor power input |
| P3 | **12V PSU –** | Common GND rail on breadboard | Black 16AWG | System ground |
| P4 | **LM2596S OUT+** (adjust to 5V) | Breadboard 5V rail | Orange | Logic power for Picos, PCA9685, servos |
| P5 | **LM2596S OUT–** | Common GND rail | Black | Buck converter ground |
| P6 | **Buck-boost OUT+** (adjust to 6-9V) | Motor power rail (separate from logic) | Red | Motor drive voltage |
| P7 | **Buck-boost OUT–** | Common GND rail | Black | Motor power ground |

**Verify with multimeter before connecting Picos:** 5V rail = 4.9-5.1V, Motor rail = 6-9V

---

## Pico A — Grid Controller

### Power

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| A1 | **5V rail** | Pico A **VSYS** pin | Orange | Powers Pico A (internal 3.3V regulator) |
| A2 | **GND rail** | Pico A **GND** pin | Black | Pico A ground |

### I2C Bus (shared: IMU + PCA9685)

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| A3 | **Pico A GP4** | BMI160 **SDA** | White | I2C data line |
| A4 | **Pico A GP4** | PCA9685 **SDA** | White | I2C data line (same bus) |
| A5 | **Pico A GP5** | BMI160 **SCL** | Grey | I2C clock line |
| A6 | **Pico A GP5** | PCA9685 **SCL** | Grey | I2C clock line (same bus) |
| A7 | **3.3V** → 4.7kΩ → **GP4 (SDA)** | Pull-up resistor | — | I2C requires pull-ups |
| A8 | **3.3V** → 4.7kΩ → **GP5 (SCL)** | Pull-up resistor | — | I2C requires pull-ups |
| A9 | **3.3V** | BMI160 **VCC** | Red thin | IMU power |
| A10 | **GND** | BMI160 **GND** | Black thin | IMU ground |
| A11 | **5V rail** | PCA9685 **VCC** | Orange | PCA9685 logic power |
| A12 | **GND** | PCA9685 **GND** | Black | PCA9685 ground |
| A13 | **5V rail** | PCA9685 **V+** (motor power input) | Orange | Servo power supply |

### SPI Bus (nRF24L01+)

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| A14 | **Pico A GP0** | nRF24L01+ **CE** | Purple | Chip enable |
| A15 | **Pico A GP1** | nRF24L01+ **CSN** | Blue | Chip select |
| A16 | **Pico A GP2** | nRF24L01+ **SCK** | Yellow | SPI clock |
| A17 | **Pico A GP3** | nRF24L01+ **MOSI** | Green | SPI data out |
| A18 | **Pico A GP16** | nRF24L01+ **MISO** | Brown | SPI data in |
| A19 | **3.3V** | nRF24L01+ **VCC** | Red thin | nRF power (**3.3V ONLY — 5V will kill it!**) |
| A20 | **GND** | nRF24L01+ **GND** | Black | nRF ground |

### Motor Switching (GPIO → MOSFET → Motor)

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| A21 | **Pico A GP10** → 1kΩ → | MOSFET 1 **gate** | Yellow | Motor 1 power switch control |
| A22 | Motor power rail → Motor 1 + terminal | Motor 1 **positive** | Red | Motor 1 power supply |
| A23 | Motor 1 – terminal → **1Ω sense R** → | MOSFET 1 **drain** | Blue | Motor 1 current path + sensing |
| A24 | MOSFET 1 **source** | **GND** | Black | Motor 1 ground return |
| A25 | **Pico A GP11** → 1kΩ → | MOSFET 2 **gate** | Yellow | Motor 2 power switch control |
| A26 | Motor power rail → Motor 2 + terminal | Motor 2 **positive** | Red | Motor 2 power supply |
| A27 | Motor 2 – terminal → **1Ω sense R** → | MOSFET 2 **drain** | Blue | Motor 2 current path + sensing |
| A28 | MOSFET 2 **source** | **GND** | Black | Motor 2 ground return |

### LED Bank Switch

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| A29 | **Pico A GP12** → 1kΩ → | MOSFET 3 **gate** | Yellow | LED bank power switch |
| A30 | 5V rail → 330Ω → LED P1 → | MOSFET 3 drain | Various | Load LED 1 (critical — white) |
| A31 | 5V rail → 330Ω → LED P2 → | MOSFET 3 drain | Various | Load LED 2 (primary — green) |
| A32 | 5V rail → 330Ω → LED P3 → | MOSFET 3 drain | Various | Load LED 3 (secondary — yellow) |
| A33 | 5V rail → 330Ω → LED P4 → | MOSFET 3 drain | Various | Load LED 4 (non-essential — red) |
| A34 | MOSFET 3 **source** | **GND** | Black | LED bank ground |

### Recycle Path Switch

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| A35 | **Pico A GP13** → 1kΩ → | MOSFET 4 **gate** | Yellow | Recycle path switch |
| A36 | 5V rail → | **100µF capacitor +** | Orange | Energy storage |
| A37 | MOSFET 4 **drain** → | Capacitor – | Blue | Controlled charge path |
| A38 | MOSFET 4 **source** | **GND** | Black | Recycle ground |

### ADC Sensing

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| A39 | 5V rail → **10kΩ** → junction → **10kΩ** → GND | Junction → **Pico A GP26** | Green | Bus voltage sensing (V/2 divider) |
| A40 | Across Motor 1 **1Ω sense R** | **Pico A GP27** | Green | Motor 1 current sensing |
| A41 | Across Motor 2 **1Ω sense R** | **Pico A GP28** | Green | Motor 2 current sensing |

### Status LEDs

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| A42 | **Pico A GP14** → 330Ω → | Red LED → GND | Red | Fault indicator |
| A43 | **Pico A GP15** → 330Ω → | Green LED → GND | Green | OK indicator |

---

## Pico B — SCADA Station

### Power

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| B1 | **5V rail** (or separate USB) | Pico B **VSYS** | Orange | Powers Pico B |
| B2 | **GND** | Pico B **GND** | Black | Pico B ground |

### I2C Bus (OLED)

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| B3 | **Pico B GP4** | OLED **SDA** | White | I2C data |
| B4 | **Pico B GP5** | OLED **SCL** | Grey | I2C clock |
| B5 | **3.3V** → 4.7kΩ → **GP4** | Pull-up resistor | — | I2C pull-up |
| B6 | **3.3V** → 4.7kΩ → **GP5** | Pull-up resistor | — | I2C pull-up |
| B7 | **3.3V** | OLED **VCC** | Red thin | OLED power |
| B8 | **GND** | OLED **GND** | Black | OLED ground |

### SPI Bus (nRF24L01+)

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| B9 | **Pico B GP0** | nRF24L01+ **CE** | Purple | Chip enable |
| B10 | **Pico B GP1** | nRF24L01+ **CSN** | Blue | Chip select |
| B11 | **Pico B GP2** | nRF24L01+ **SCK** | Yellow | SPI clock |
| B12 | **Pico B GP3** | nRF24L01+ **MOSI** | Green | SPI data out |
| B13 | **Pico B GP16** | nRF24L01+ **MISO** | Brown | SPI data in |
| B14 | **3.3V** | nRF24L01+ **VCC** | Red thin | **3.3V ONLY!** |
| B15 | **GND** | nRF24L01+ **GND** | Black | nRF ground |

### Joystick

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| B16 | **Pico B GP26** | Joystick **VRx** | Green | X-axis analog |
| B17 | **Pico B GP27** | Joystick **VRy** | Green | Y-axis analog |
| B18 | **Pico B GP22** | Joystick **SW** | Blue | Button (active low) |
| B19 | **3.3V** | Joystick **VCC** | Red thin | Joystick power |
| B20 | **GND** | Joystick **GND** | Black | Joystick ground |

### Potentiometer

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| B21 | **3.3V** | Potentiometer pin 1 | Red thin | Pot power |
| B22 | **GND** | Potentiometer pin 3 | Black | Pot ground |
| B23 | **Pico B GP28** | Potentiometer pin 2 (wiper) | Green | Analog reading |

### Status LEDs

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| B24 | **Pico B GP14** → 330Ω → | Red LED → GND | Red | Fault indicator |
| B25 | **Pico B GP15** → 330Ω → | Green LED → GND | Green | OK indicator |

---

## Servo Connections (via PCA9685)

| # | PCA9685 Channel | Connected To | Signal Wire | Purpose |
|---|---|---|---|---|
| S1 | **CH0** | Servo 1 signal (orange/white wire) | White | Fill valve / vent damper |
| S2 | **CH1** | Servo 2 signal (orange/white wire) | White | Sort gate / quality gate |
| S3 | All servo **VCC** (red wire) | 5V rail via PCA9685 V+ | Red | Servo power |
| S4 | All servo **GND** (brown wire) | GND rail via PCA9685 GND | Brown | Servo ground |

---

## IMU Placement

| # | Detail |
|---|---|
| Mount | BMI160 attached to **DC Motor 1 body** with double-sided tape |
| Orientation | Flat against motor housing — Z-axis perpendicular to motor surface |
| Purpose | Vibration = bearing health. Shake motor = fault demo |
| Wiring | I2C (SDA/SCL) runs from motor down to Pico A breadboard |

---

## Wire Count Summary

| Category | Wires | Notes |
|---|---|---|
| Power supply | 7 | PSU → buck → boost → rails |
| Pico A I2C | 11 | IMU + PCA9685 + pull-ups |
| Pico A SPI | 7 | nRF24L01+ |
| Pico A motor switching | 14 | 2 motors × (gate + power + sense + drain + GND) |
| Pico A LED bank | 6 | MOSFET + 4 LEDs |
| Pico A recycle path | 4 | MOSFET + capacitor |
| Pico A ADC | 3 | Bus voltage + 2 current sense |
| Pico A status LEDs | 2 | Red + green |
| Pico B I2C | 6 | OLED |
| Pico B SPI | 7 | nRF24L01+ |
| Pico B joystick | 5 | X + Y + button + VCC + GND |
| Pico B potentiometer | 3 | Wiper + VCC + GND |
| Pico B status LEDs | 2 | Red + green |
| Servos | 4 | 2 servos × signal, shared VCC + GND |
| **Total** | **~81 wires** | Wooseong's main job |

---

## Wiring Order (for Wooseong)

Wire in this order — test after each group:

| Order | Group | Test |
|---|---|---|
| 1 | Power supply chain (P1-P7) | Multimeter: 5V and 6-9V on rails |
| 2 | Pico A power (A1-A2) | Pico A boots, onboard LED blinks |
| 3 | Pico A I2C (A3-A13) | Run `test_i2c_scan.py` — should find 0x68 + 0x40 |
| 4 | Pico A SPI/nRF (A14-A20) | Run `test_wireless.py` on both Picos |
| 5 | Pico B power + I2C + SPI (B1-B15) | OLED displays text, nRF responds |
| 6 | Pico B inputs (B16-B25) | Run `test_joystick.py` — values change |
| 7 | Motor 1 switching (A21-A24, A40) | Motor 1 spins when GP10 HIGH |
| 8 | Motor 2 switching (A25-A28, A41) | Motor 2 spins when GP11 HIGH |
| 9 | ADC bus voltage (A39) | ADC reads ~half of bus voltage |
| 10 | LED bank + recycle (A29-A38) | LEDs light when GP12 HIGH |
| 11 | Servos (S1-S4) | Servos move to test angles |
| 12 | Status LEDs (A42-A43, B24-B25) | All 4 LEDs blink |

**Test after EVERY group.** Don't wire everything then test — find problems early.
