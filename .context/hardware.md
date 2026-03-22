# Hardware Reference

## Components

| Component | Qty | Interface | Address/Bus | Role |
|---|---|---|---|---|
| Pico 2 (RP2350) | 2 | — | — | Main controllers |
| nRF24L01+ PA+LNA | 2 | SPI0 | — | 2.4GHz wireless |
| BMI160 IMU | 1 | I2C0 | 0x68 | Vibration/fault detection |
| PCA9685 | 1 | I2C0 | 0x40 | 16-ch PWM driver (servos + motor MOSFETs) |
| SSD1306 OLED | 1 | I2C0 | 0x3C | 128x64 display |
| MAX7219 7-seg | 1 | SPI1 | — | 8-digit status display |
| MG90S Servo | 2 | PCA9685 | Ch 0-1 | Valve + quality gate |
| DC Motor | 2 | PCA9685→MOSFET | — | Fan + pump/conveyor |
| Joystick | 1 | ADC+GPIO | — | Operator X/Y + button |
| Potentiometer | 1 | ADC | — | Operator speed control |
| Red/Green LEDs | 4 | GPIO | — | Status indicators |

## Pin Mapping — Pico A (Master / Grid Controller)

| GP Pin | Function | Bus | Notes |
|---|---|---|---|
| GP0 | nRF CE | SPI0 | Chip Enable |
| GP1 | nRF CSN | SPI0 | Chip Select |
| GP2 | SPI SCK | SPI0 | Clock |
| GP3 | SPI MOSI | SPI0 | Data out |
| GP4 | I2C SDA | I2C0 | BMI160 + PCA9685 |
| GP5 | I2C SCL | I2C0 | BMI160 + PCA9685 |
| GP10 | ~~FREE~~ | — | Was Motor 1 MOSFET (now PCA9685 CH2) |
| GP11 | ~~FREE~~ | — | Was Motor 2 MOSFET (now PCA9685 CH3) |
| GP12 | ~~FREE~~ | — | Was LED bank (REMOVED — replaced by MAX7219 on Pico B) |
| GP13 | MOSFET 3 | GPIO | Recycle path switch |
| GP14 | ~~FREE~~ | — | Was red LED (REMOVED — replaced by MAX7219) |
| GP15 | ~~FREE~~ | — | Was green LED (REMOVED — replaced by MAX7219) |
| GP16 | SPI MISO | SPI0 | Data in |
| GP25 | Onboard LED | GPIO | Heartbeat |
| GP26 | ADC0 | ADC | Bus voltage |
| GP27 | ADC1 | ADC | Motor 1 current |
| GP28 | ADC2 | ADC | Motor 2 current |

## Pin Mapping — Pico B (Slave / SCADA Station)

| GP Pin | Function | Bus | Notes |
|---|---|---|---|
| GP0 | nRF CE | SPI0 | Chip Enable |
| GP1 | nRF CSN | SPI0 | Chip Select |
| GP2 | SPI SCK | SPI0 | Clock |
| GP3 | SPI MOSI | SPI0 | Data out |
| GP4 | I2C SDA | I2C0 | SSD1306 OLED |
| GP5 | I2C SCL | I2C0 | SSD1306 OLED |
| GP10 | SPI1 SCK | SPI1 | MAX7219 clock |
| GP11 | SPI1 MOSI | SPI1 | MAX7219 data |
| GP13 | MAX7219 CS | SPI1 | 7-seg chip select |
| GP14 | ~~FREE~~ | — | Was red LED (REMOVED — replaced by MAX7219) |
| GP15 | ~~FREE~~ | — | Was green LED (REMOVED — replaced by MAX7219) |
| GP16 | SPI MISO | SPI0 | Data in (nRF only) |
| GP22 | Joystick BTN | GPIO | Button (pull-up) |
| GP25 | Onboard LED | GPIO | Heartbeat |
| GP26 | ADC0 | ADC | Joystick X |
| GP27 | ADC1 | ADC | Joystick Y |
| GP28 | ADC2 | ADC | Potentiometer |

## SPI Bus Summary

| Bus | Pico | Device | SCK | MOSI | MISO | CS | Baud |
|---|---|---|---|---|---|---|---|
| SPI0 | A + B | nRF24L01+ | GP2 | GP3 | GP16 | GP1 (CSN) | 10MHz |
| SPI1 | B only | MAX7219 | GP10 | GP11 | — | GP13 | 10MHz |

## I2C Bus Summary

| Bus | Pico | Devices | SDA | SCL | Freq |
|---|---|---|---|---|---|
| I2C0 | A | BMI160 (0x68) + PCA9685 (0x40) | GP4 | GP5 | 400kHz |
| I2C0 | B | SSD1306 OLED (0x3C) | GP4 | GP5 | 400kHz |

## nRF24L01+ Wireless Config

| Setting | Value |
|---|---|
| Channel | 100 |
| Data rate | 250kbps |
| Payload size | 32 bytes |
| Master TX addr | `NSYNT` |
| Master RX addr | `NSYNR` |
| Slave TX addr | `NSYNR` |
| Slave RX addr | `NSYNT` |

## Power

- **12V 6A PSU** → LM2596S buck converter → 5V bus
- **300W buck-boost** for motor power
- **3V3** from Pico's onboard regulator for logic
- **5V (VBUS)** recommended for MAX7219 (3.3V causes dim display due to multiplexing)

## Key Notes

- nRF24L01+ uses **same pinout on both Picos** (CE=GP0, CSN=GP1, SCK=GP2, MOSI=GP3, MISO=GP16)
- MAX7219 on SPI1 to avoid bus conflict with nRF on SPI0
- Pico 2 mounts as `RP2350` in BOOTSEL mode (not `RPI-RP2` like Pico 1)
- Full ~78-wire wiring plan in `docs/02-electrical/wiring-connections.md`
- Motor MOSFET gates driven by PCA9685 Ch2/Ch3 (12-bit PWM speed control), not GPIO
- LED bank REMOVED — replaced by MAX7219 display, status shown wirelessly
- 3 MOSFETs total: Motor 1, Motor 2, Recycle path (was 4)
