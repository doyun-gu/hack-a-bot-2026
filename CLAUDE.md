# Hack-A-Bot 2026 — Project 6: Creative

24-hour hackathon: build a working physical prototype using two Raspberry Pi Pico 2 boards with wireless coordination.

## Tech Stack

- **Platform:** 2x Raspberry Pi Pico 2 (ARM Cortex-M33, dual-core)
- **Language:** C/C++ with Pico SDK (MicroPython as fallback)
- **Wireless:** nRF24L01+ PA+LNA 2.4 GHz (SPI)
- **Sensors:** BMI160 IMU 6-axis (I2C), Analog Joystick (ADC)
- **Actuators:** PCA9685 16-ch servo driver (I2C) + MG90S servos
- **Display:** 0.96" OLED SSD1306 (I2C)
- **Power:** 12V 6A PSU → LM2596S buck (logic) + 300W buck-boost (motors)

## File Structure

```
hack-a-bot-2026/
├── CLAUDE.md              # This file — project context for Claude
├── README.md              # Public-facing project README
├── .gitignore             # Excludes notes/ from repo
├── src/                   # Firmware source code
│   ├── pico_controller/   # Pico A — sensor/input side
│   └── pico_actuator/     # Pico B — actuator/output side
├── docs/                  # Documentation
│   ├── README.md          # Docs index
│   ├── idea-shortlist.md  # All project ideas scored against rubric
│   └── hardware-reference.md  # Component table + pinout interfaces
├── notes/                 # LOCAL ONLY (gitignored) — brainstorming, diagrams
└── media/                 # Photos and videos of prototype
```

## Key Interfaces (Pin Mapping)

| Interface | Protocol | Components |
|-----------|----------|------------|
| SPI | MOSI, MISO, SCK, CSN, CE | nRF24L01+ wireless modules |
| I2C | SDA (GP4), SCL (GP5) | PCA9685, BMI160, OLED |
| ADC | GP26, GP27 | Joystick X/Y axes |
| PWM | PCA9685 outputs | MG90S servos |

## Scoring Rubric

| Category | Points |
|----------|--------|
| Problem Definition & Solution Fit | 30 |
| Live Demo & Effectiveness | 25 |
| Technical Implementation | 20 |
| Innovation & Creativity | 15 |
| Documentation | 10 |

**Score caps:** 60-point cap without wireless coordination. 50-point cap without live demo.

## Current State

- **Phase:** Idea development — two lead proposals with full Mermaid diagrams
- **Lead idea: TremorTray** (96pts) — hand tremor diagnostic tool
  - Full proposal: `docs/tremortray-proposal.md`
  - Dual-sensor: IMU (on tray) + joystick (under tray as position sensor)
  - Servo-controlled difficulty levels (flat → tilt → dynamic rocking)
  - Clinical severity scoring (replaces subjective UPDRS scale)
  - Judge holds tray and gets their own tremor score = best possible demo
- **Alternative: SteadyHand** (95pts) — tremor stabiliser
  - Full proposal: `docs/steadyhand-proposal.md`
- **Other ideas:** `docs/idea-shortlist.md` (10 ideas scored)
- **Next:** Develop TremorTray further, scaffold firmware, wireless link first

## Dev Commands

```bash
# Build (once SDK is set up)
cd src/pico_controller && mkdir -p build && cd build && cmake .. && make

# Flash to Pico (hold BOOTSEL, plug USB, copy .uf2)
cp build/main.uf2 /Volumes/RPI-RP2/

# Git workflow — full permissions granted
git add <files> && git commit -m "message" && git push origin main
```

## Conventions

- Commit and push automatically after completing work — full permissions granted
- Keep `docs/idea-shortlist.md` updated as ideas evolve
- Local brainstorming goes in `notes/` (gitignored)
- Test wireless link FIRST before any other feature — it's the score-cap requirement
- Use both Pico cores: Core 0 for main logic, Core 1 for time-critical tasks (wireless/IMU)
