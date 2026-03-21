# Hardware Reference

## Components Provided

| Category | Component | Qty | Purpose |
|----------|-----------|-----|---------|
| **Microcontroller** | Raspberry Pi Pico 2 | 2 | Dual-core ARM Cortex-M33 — main processing units for controller and actuator |
| **Wireless** | nRF24L01+ PA+LNA (2.4 GHz) | 2 | Long-range wireless transceiver for Pico-to-Pico communication |
| **Actuator Driver** | PCA9685 Servo Driver | 1 | 16-channel PWM driver over I2C — controls multiple servos from a single bus |
| **Actuator** | MG90S Servo Motors | — | Compact metal-gear servos for precise mechanical actuation |
| **Input** | Analog Joystick Module | — | Dual-axis analog input for manual directional control |
| **Sensor** | BMI160 IMU (6-axis) | 1 | Gyroscope + accelerometer for motion/orientation sensing |
| **Display** | 0.96" OLED Display (I2C) | 1 | Status feedback and debugging output |
| **Power** | LM2596S Buck Converter | 1 | Adjustable step-down regulator for powering logic (3.3V/5V from 12V) |
| **Power** | 300W 20A Buck-Boost Converter | 1 | High-power voltage conversion for motors and actuators |
| **Power** | 12V 6A Power Supply | 1 | Bench power source — up to 72W total budget |
| **Prototyping** | 400-Tie Breadboards | — | Solderless prototyping surfaces |
| **Prototyping** | 7×9 cm Perfboard | — | For permanent soldered circuits |
| **Wiring** | 22 AWG Solid-Core Wire | — | Hookup wiring for connections |
| **Mechanical** | M3×8 mm Self-Tapping Screws | — | Structural fasteners for assembly |
| **Misc** | Assorted Components Kit | 1 | Resistors, LEDs, capacitors, diodes, and other essentials |
| **Tools** | Precision Screwdriver Set | 1 | Hand tools for assembly and adjustments |

## Key Interfaces

| Interface | Pins/Protocol | Used By |
|-----------|---------------|---------|
| **SPI** | MOSI, MISO, SCK, CSN, CE | nRF24L01+ wireless modules |
| **I2C** | SDA, SCL | PCA9685 servo driver, BMI160 IMU, OLED display |
| **ADC** | Analog pins | Joystick (X/Y axes) |
| **PWM** | PCA9685 outputs | MG90S servos |
| **Power** | VSYS / 3V3 | Pico power input (from buck converter) |
