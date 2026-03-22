# Wiring Connection Table — Every Wire in the System

> Print this and check off each connection as you wire it. Every wire is listed once.
>
> **Revision 2 (2026-03-22):** LED bank REMOVED (replaced by MAX7219 display on Pico B). Motor MOSFET gates now driven by PCA9685 PWM instead of direct GPIO. See [Change Log](#change-log) at bottom.

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
| A13 | **5V rail** | PCA9685 **V+** (motor power input) | Orange | Servo + motor power supply |

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

### Motor Switching (PCA9685 PWM → MOSFET → Motor)

> **Changed:** Motor MOSFET gates are now driven by PCA9685 PWM channels (12-bit, 4096-step speed control) instead of Pico GPIO pins. The PCA9685 is already on the I2C bus (wires A3-A13). MOSFETs + flyback diodes + sense resistors stay the same.

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| A21 | **PCA9685 CH2** → 1kΩ → | MOSFET 1 **gate** | Yellow | Motor 1 PWM speed control |
| A22 | Motor power rail → Motor 1 + terminal | Motor 1 **positive** | Red | Motor 1 power supply |
| A23 | Motor 1 – terminal → **1Ω sense R** → | MOSFET 1 **drain** | Blue | Motor 1 current path + sensing |
| A24 | MOSFET 1 **source** | **GND** | Black | Motor 1 ground return |
| A25 | **PCA9685 CH3** → 1kΩ → | MOSFET 2 **gate** | Yellow | Motor 2 PWM speed control |
| A26 | Motor power rail → Motor 2 + terminal | Motor 2 **positive** | Red | Motor 2 power supply |
| A27 | Motor 2 – terminal → **1Ω sense R** → | MOSFET 2 **drain** | Blue | Motor 2 current path + sensing |
| A28 | MOSFET 2 **source** | **GND** | Black | Motor 2 ground return |

### ~~LED Bank Switch~~ — REMOVED

> **CANCELLED:** LED bank (wires A29-A34) replaced by MAX7219 8-digit 7-segment display on Pico B SPI1. Status indicators now shown wirelessly on the display. See `docs/02-electrical/max7219-wiring.md`.

### Recycle Path Switch

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| A29 | **Pico A GP13** → 1kΩ → | MOSFET 3 **gate** | Yellow | Recycle path switch |
| A30 | 5V rail → | **100µF capacitor +** | Orange | Energy storage |
| A31 | MOSFET 3 **drain** → | Capacitor – | Blue | Controlled charge path |
| A32 | MOSFET 3 **source** | **GND** | Black | Recycle ground |

### ADC Sensing

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| A33 | 5V rail → **10kΩ** → junction → **10kΩ** → GND | Junction → **Pico A GP26** | Green | Bus voltage sensing (V/2 divider) |
| A34 | Across Motor 1 **1Ω sense R** | **Pico A GP27** | Green | Motor 1 current sensing |
| A35 | Across Motor 2 **1Ω sense R** | **Pico A GP28** | Green | Motor 2 current sensing |

### Status LEDs

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| A36 | **Pico A GP14** → 330Ω → | Red LED → GND | Red | Fault indicator |
| A37 | **Pico A GP15** → 330Ω → | Green LED → GND | Green | OK indicator |

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

### SPI0 Bus (nRF24L01+)

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| B9 | **Pico B GP0** | nRF24L01+ **CE** | Purple | Chip enable |
| B10 | **Pico B GP1** | nRF24L01+ **CSN** | Blue | Chip select |
| B11 | **Pico B GP2** | nRF24L01+ **SCK** | Yellow | SPI clock |
| B12 | **Pico B GP3** | nRF24L01+ **MOSI** | Green | SPI data out |
| B13 | **Pico B GP16** | nRF24L01+ **MISO** | Brown | SPI data in |
| B14 | **3.3V** | nRF24L01+ **VCC** | Red thin | **3.3V ONLY!** |
| B15 | **GND** | nRF24L01+ **GND** | Black | nRF ground |

### SPI1 Bus (MAX7219 7-Segment Display)

> **NEW:** Replaces LED bank on Pico A. Shows system status, wireless link, fault codes, power readings. See `docs/02-electrical/max7219-wiring.md` for full details.

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| B16 | **Pico B GP10** | MAX7219 **CLK** | Yellow | SPI1 clock |
| B17 | **Pico B GP11** | MAX7219 **DIN** | Green | SPI1 data |
| B18 | **Pico B GP13** | MAX7219 **CS** | Blue | Chip select |
| B19 | **5V (VBUS)** | MAX7219 **VCC** | Red | Display power (**5V for brightness**) |
| B20 | **GND** | MAX7219 **GND** | Black | Display ground |

### Joystick

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| B21 | **Pico B GP26** | Joystick **VRx** | Green | X-axis analog |
| B22 | **Pico B GP27** | Joystick **VRy** | Green | Y-axis analog |
| B23 | **Pico B GP22** | Joystick **SW** | Blue | Button (active low) |
| B24 | **3.3V** | Joystick **VCC** | Red thin | Joystick power |
| B25 | **GND** | Joystick **GND** | Black | Joystick ground |

### Potentiometer

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| B26 | **3.3V** | Potentiometer pin 1 | Red thin | Pot power |
| B27 | **GND** | Potentiometer pin 3 | Black | Pot ground |
| B28 | **Pico B GP28** | Potentiometer pin 2 (wiper) | Green | Analog reading |

### Status LEDs

| # | From | To | Wire | Purpose |
|---|---|---|---|---|
| B29 | **Pico B GP14** → 330Ω → | Red LED → GND | Red | Fault indicator |
| B30 | **Pico B GP15** → 330Ω → | Green LED → GND | Green | OK indicator |

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
| Pico A power | 2 | VSYS + GND |
| Pico A I2C | 11 | IMU + PCA9685 + pull-ups |
| Pico A SPI | 7 | nRF24L01+ |
| Pico A motor switching | 8 | 2 motors × (PCA9685→gate + power + sense + GND) |
| ~~Pico A LED bank~~ | ~~6~~ | ~~REMOVED — replaced by MAX7219 on Pico B~~ |
| Pico A recycle path | 4 | MOSFET + capacitor |
| Pico A ADC | 3 | Bus voltage + 2 current sense |
| Pico A status LEDs | 2 | Red + green |
| Pico B power | 2 | VSYS + GND |
| Pico B I2C | 6 | OLED |
| Pico B SPI0 | 7 | nRF24L01+ |
| Pico B SPI1 | 5 | MAX7219 7-segment display (NEW) |
| Pico B joystick | 5 | X + Y + button + VCC + GND |
| Pico B potentiometer | 3 | Wiper + VCC + GND |
| Pico B status LEDs | 2 | Red + green |
| Servos | 4 | 2 servos × signal, shared VCC + GND |
| **Total** | **~78 wires** | |

---

## Wiring Order (for Wooseong)

Wire in this order — test after each group:

| Order | Group | Wires | Test |
|---|---|---|---|
| 1 | Power supply chain | P1-P7 | Multimeter: 5V and 6-9V on rails |
| 2 | Pico A power | A1-A2 | Pico A boots, onboard LED blinks |
| 3 | Pico A SPI/nRF | A14-A20 | `./flash.sh test` — nRF reads status register |
| 4 | Pico B power | B1-B2 | Pico B boots, onboard LED blinks |
| 5 | Pico B SPI0/nRF | B9-B15 | `./flash.sh test` — nRF reads status register |
| 6 | **Wireless test** | (no new wires) | `./flash.sh test-wireless-master` + `test-wireless-slave` |
| 7 | Pico B SPI1/MAX7219 | B16-B20 | `./flash.sh test-display` — shows 12345678 |
| 8 | Pico A I2C (PCA9685 + IMU) | A3-A13 | `test_i2c_scan.py` — finds 0x68 + 0x40 |
| 9 | Motors via PCA9685 | A21-A28, A34-A35 | Motor spins when PCA9685 Ch2/Ch3 set |
| 10 | Recycle path | A29-A32 | Capacitor charges when GP13 HIGH |
| 11 | ADC bus voltage | A33 | ADC reads ~half of bus voltage |
| 12 | Pico B I2C/OLED | B3-B8 | OLED displays text |
| 13 | Pico B inputs | B21-B28 | `test_joystick.py` — values change |
| 14 | Servos | S1-S4 | Servos move to test angles |
| 15 | Status LEDs | A36-A37, B29-B30 | All 4 LEDs blink |

**Test after EVERY group.** Don't wire everything then test — find problems early.

**Priority order:** Steps 1-6 are CRITICAL (wireless link needed for demo). Steps 7-15 add features.

---

## Change Log

| Date | Change | Reason |
|---|---|---|
| 2026-03-22 | **LED bank (old A29-A34) REMOVED** | Replaced by MAX7219 8-digit 7-segment display on Pico B SPI1. Status info now shown wirelessly. |
| 2026-03-22 | **Motor gates: GPIO → PCA9685 PWM** | PCA9685 Ch2/Ch3 drive MOSFET gates instead of GP10/GP11. Gives 12-bit PWM speed control (4096 steps). GP10-GP12 freed on Pico A. |
| 2026-03-22 | **MAX7219 display added to Pico B** | 5 new wires (B16-B20) on SPI1 bus. |
| 2026-03-22 | **Wire numbers renumbered** | A29+ renumbered after LED bank removal. Pico B wires renumbered to include MAX7219 (B16-B20). |
| 2026-03-22 | **Wiring order revised** | Wireless-first priority. nRF on both Picos tested before anything else. |
