# Hack-A-Bot 2026 — Project 6: Creative

<p align="center">
  <img src="https://hackabot-2026.com/live/assets/images/projects/badges/creative.png" alt="Project 6 Creative Badge" width="200"/>
</p>

<p align="center">
  <strong>An open-ended embedded systems & robotics challenge</strong><br/>
  Design a problem-driven device using two Raspberry Pi Pico 2 microcontrollers with wireless coordination
</p>

---

## Supported By

<p align="center">
  <img src="https://hackabot-2026.com/live/assets/images/projects/sponsors/ARM.svg" alt="ARM" height="60"/>&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://hackabot-2026.com/live/assets/images/projects/sponsors/eeesoc.svg" alt="EEESoc" height="60"/>
</p>

<p align="center">
  <a href="https://www.arm.com">ARM</a> · <a href="#">EEESoc</a>
</p>

---

## Challenge Brief

Teams have **24 hours** to design and build a working physical prototype that uses **two Raspberry Pi Pico 2 boards** communicating wirelessly to address a real-world need. The device must be demonstrated live to judges.

### Theme Prompts (Choose One)

| Theme | Description |
|-------|-------------|
| **Assistive Technology** | Improve accessibility, safety, independence, or usability for people who need it |
| **Autonomy** | Sense, decide, and act with minimal human input |
| **Interactive Play** | Create engaging, physical interactive experiences |
| **Sustainability** | Reduce waste, save energy, or monitor resources |

### Core Requirements

- Two Pi Pico 2 boards with **wireless coordination** to address a real need
- Working **physical prototype** completed within 24 hours
- **Live demonstration** of core functionality to judges
- Clear **problem definition** with identified end-user or context

---

## Hardware Kit

Every team is provided with the following components:

### Microcontrollers & Wireless

| Component | Qty | Description |
|-----------|-----|-------------|
| <img src="https://hackabot-2026.com/live/assets/images/projects/project-2/materials/raspberry-pi-pico-2.webp" alt="Raspberry Pi Pico 2" width="80"/> | 2 | **Raspberry Pi Pico 2** — Dual-core ARM Cortex-M33 microcontroller, the brain of the project |
| <img src="https://hackabot-2026.com/live/assets/images/projects/project-6/materials/nrf24l01-pa-lna-module.webp" alt="nRF24L01+" width="80"/> | 2 | **nRF24L01+ PA+LNA 2.4 GHz** — Long-range wireless transceiver modules for Pico-to-Pico communication |

### Actuators & Drivers

| Component | Qty | Description |
|-----------|-----|-------------|
| <img src="https://hackabot-2026.com/live/assets/images/projects/project-6/materials/pca9685-servo-driver.webp" alt="PCA9685" width="80"/> | 1 | **PCA9685 Servo Driver** — 16-channel PWM driver over I2C, controls multiple servos from a single bus |
| <img src="https://hackabot-2026.com/live/assets/images/projects/project-2/materials/mg90s-servo.webp" alt="MG90S Servo" width="80"/> | — | **MG90S Servo Motors** — Compact metal-gear servos for precise mechanical actuation |

### Sensors & Input

| Component | Qty | Description |
|-----------|-----|-------------|
| <img src="https://hackabot-2026.com/live/assets/images/projects/project-1/materials/analog-joystick.webp" alt="Joystick" width="80"/> | — | **Analog Joystick Modules** — Dual-axis analog input for manual control |
| <img src="https://hackabot-2026.com/live/assets/images/projects/project-6/materials/bmi160-imu.webp" alt="BMI160 IMU" width="80"/> | 1 | **BMI160 IMU** — 6-axis inertial measurement unit (gyroscope + accelerometer) for motion sensing |

### Display

| Component | Qty | Description |
|-----------|-----|-------------|
| <img src="https://hackabot-2026.com/live/assets/images/projects/project-2/materials/oled-display-096.webp" alt="OLED Display" width="80"/> | 1 | **0.96" OLED Display** — I2C status screen for feedback and debugging |

### Power

| Component | Qty | Description |
|-----------|-----|-------------|
| <img src="https://hackabot-2026.com/live/assets/images/projects/project-2/materials/lm2596s-buck-converter.webp" alt="LM2596S" width="80"/> | 1 | **LM2596S Buck Converter** — Adjustable step-down voltage regulator for powering logic |
| <img src="https://hackabot-2026.com/live/assets/images/projects/project-6/materials/300w-20a-buck-boost-converter.webp" alt="Buck-Boost Converter" width="80"/> | 1 | **300W 20A Buck-Boost Converter** — High-power voltage conversion for driving motors and actuators |
| <img src="https://hackabot-2026.com/live/assets/images/projects/project-2/materials/12v-6a-power-supply.webp" alt="12V PSU" width="80"/> | 1 | **12V 6A Power Supply** — Bench power source providing up to 72W |

### Prototyping & Wiring

| Component | Qty | Description |
|-----------|-----|-------------|
| <img src="https://hackabot-2026.com/live/assets/images/projects/project-6/materials/breadboard-400-tie-points.webp" alt="Breadboard" width="80"/> | — | **400-Tie Breadboards** — Solderless prototyping surfaces |
| <img src="https://hackabot-2026.com/live/assets/images/projects/project-2/materials/perfboard-7x9cm.webp" alt="Perfboard" width="80"/> | — | **7×9 cm Perfboard** — For permanent soldered circuits |
| <img src="https://hackabot-2026.com/live/assets/images/projects/project-6/materials/wire-22awg-solid-core.webp" alt="Wire" width="80"/> | — | **22 AWG Solid-Core Wire** — Hookup wiring for connections |

### Mechanical & Tools

| Component | Qty | Description |
|-----------|-----|-------------|
| <img src="https://hackabot-2026.com/live/assets/images/projects/project-6/materials/m3x8-self-tapping-screws.webp" alt="Screws" width="80"/> | — | **M3×8 mm Self-Tapping Screws** — Mechanical fasteners for structural assembly |
| <img src="https://hackabot-2026.com/live/assets/images/projects/project-6/materials/assorted-electronic-components-kit.webp" alt="Components Kit" width="80"/> | 1 | **Assorted Components Kit** — Resistors, LEDs, capacitors, diodes, and other essentials |
| <img src="https://hackabot-2026.com/live/assets/images/projects/project-6/materials/precision-screwdriver-set.webp" alt="Screwdriver Set" width="80"/> | 1 | **Precision Screwdriver Set** — Hand tools for assembly and adjustments |

---

## Scoring Rubric

| Category | Points | What Judges Look For |
|----------|--------|----------------------|
| **Problem Definition & Solution Fit** | 30 | Clear problem statement, identified end-user, convincing rationale for why this solution addresses the need |
| **Live Demo & Effectiveness** | 25 | Core functionality works reliably during demonstration, system responds as intended |
| **Technical Implementation & Engineering** | 20 | Clean wiring, good code structure, effective use of wireless comms, appropriate sensor/actuator integration |
| **Innovation & Creativity** | 15 | Novel approach, creative use of available components, original problem framing |
| **Communication & Documentation** | 10 | README, wiring diagrams, CAD files, clear explanation of design decisions |
| **Total** | **100** | |

### Score Caps (Critical)

> **60-point cap** — If the two-Pico wireless coordination requirement is not met
> **50-point cap** — If core functionality cannot be demonstrated live

---

## Repository Structure

```
hack-a-bot-2026/
├── README.md              # This file
├── src/                   # Source code for both Picos
│   ├── pico_controller/   # Controller Pico firmware
│   └── pico_actuator/     # Actuator Pico firmware
├── docs/                  # Wiring diagrams, CAD files, design notes
└── media/                 # Photos and videos of the prototype
```

---

## Team

*Team members to be added*

---

## License

This project was built during **Hack-A-Bot 2026**, supported by **ARM** and **EEESoc**.
