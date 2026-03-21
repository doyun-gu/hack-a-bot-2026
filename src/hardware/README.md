# Hardware

This folder contains all physical design files for the project.

| Folder | Contents |
|---|---|
| `cad/` | 3D models, chassis designs, enclosure files (collaborator-managed) |
| `wiring/` | Wiring diagrams, pin mapping, schematic drawings |
| `datasheets/` | Component datasheets (BMI160, nRF24L01+, PCA9685, MG90S, etc.) |

## Pin Mapping (Default)

Both Picos use the same pin layout for consistency:

| Function | Pin | Protocol |
|---|---|---|
| I2C SDA | GP4 | I2C0 |
| I2C SCL | GP5 | I2C0 |
| SPI SCK | GP2 | SPI0 |
| SPI MOSI | GP3 | SPI0 |
| SPI MISO | GP4 | SPI0 |
| nRF CSN | GP1 | GPIO |
| nRF CE | GP0 | GPIO |
| Joystick X | GP26 | ADC0 |
| Joystick Y | GP27 | ADC1 |
| Joystick BTN | GP22 | GPIO (pull-up) |
| LED Green | GP15 | GPIO |
| LED Red | GP14 | GPIO |

**Note:** GP4 is shared between I2C SDA and SPI MISO. If both I2C and SPI are used on the same Pico, reassign SPI MISO to a different pin (e.g., GP16).
