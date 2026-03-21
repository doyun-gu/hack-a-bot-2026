# GridBox — Project Context (Copy-Paste to AI)

> Paste this at the start of any AI chat to give full project context.
> Last updated: 2026-03-21

---

## What We're Building

**GridBox** — a £15 smart infrastructure controller for a 24-hour hackathon (Hack-A-Bot 2026, sponsored by ARM + EEESoc at University of Manchester).

**Theme:** Sustainability + Autonomy

**One-liner:** A smart system powered by recycled energy that senses where power is wasted, autonomously reroutes it to where it's needed, detects equipment faults via vibration monitoring, and reports everything wirelessly to a SCADA dashboard.

**Demo scenario:** Miniature smart water bottling plant — water pump, fill valve, conveyor belt, quality gate — all running autonomously with fault detection and energy optimization.

---

## Hardware

| Component | Qty | Role in GridBox |
|---|---|---|
| Raspberry Pi Pico 2 (RP2350) | 2 | Pico A = grid controller, Pico B = SCADA station |
| nRF24L01+ PA+LNA | 2 | Wireless telemetry link (SPI, 2.4GHz) |
| BMI160 IMU (6-axis) | 1 | Vibration monitoring on motors — fault detection (I2C 0x68) |
| PCA9685 Servo Driver | 1 | 16-ch PWM for motors + servos (I2C 0x40) |
| MG90S Servo | 2 | Servo 1 = fill valve, Servo 2 = quality/sorting gate |
| DC Motor | 2 | Motor 1 = water pump/fan, Motor 2 = conveyor belt |
| 0.96" OLED SSD1306 | 1 | SCADA dashboard on Pico B (I2C 0x3C) |
| Analog Joystick | 1 | Manual override on SCADA station (ADC + button) |
| Potentiometer | 1 | Setpoint control — production speed / threshold (ADC) |
| LM2596S Buck Converter | 1 | 12V → 5V for logic power |
| 300W Buck-Boost Converter | 1 | Motor power (6-12V adjustable) |
| 12V 6A PSU | 1 | Main power input (represents recycled energy) |
| LEDs, resistors, transistors | Various | Status indicators + MOSFET power switches + sense resistors |
| Breadboards, wire, screws | Various | Power bus, wiring, mechanical mounting |

---

## Architecture

```
POWER INPUT (12V PSU = recycled energy)
    │
    ├── Buck Converter → 5V → Pico A, PCA9685, Servos
    └── Buck-Boost → 6-12V → DC Motors

PICO A — Grid Controller (factory floor)
    ├── ADC GP26: bus voltage (via 10kΩ+10kΩ divider)
    ├── ADC GP27: motor 1 current (via 1Ω sense resistor)
    ├── ADC GP28: motor 2 current (via 1Ω sense resistor)
    ├── I2C GP4/GP5: BMI160 IMU (vibration) + PCA9685 (PWM)
    ├── SPI GP0-3,GP16: nRF24L01+ TX
    ├── GPIO GP10: MOSFET → Motor 1 power switch
    ├── GPIO GP11: MOSFET → Motor 2 power switch
    ├── GPIO GP12: MOSFET → LED bank switch
    ├── GPIO GP13: MOSFET → Recycle path (capacitor)
    ├── GPIO GP14/15: Status LEDs (red/green)
    ├── Core 0: main control loop (100Hz)
    └── Core 1: fault detection (IMU vibration)

        ──── nRF24L01+ wireless (bidirectional) ────

PICO B — SCADA Station (control room)
    ├── I2C GP4/GP5: OLED SSD1306 dashboard
    ├── SPI GP0-3,GP16: nRF24L01+ RX
    ├── ADC GP26/27: Joystick X/Y
    ├── ADC GP28: Potentiometer
    ├── GPIO GP22: Joystick button
    └── GPIO GP14/15: Status LEDs
```

---

## Core Innovation

The Pico IS the power grid — not just monitoring, but physically routing power:
- **ADC pins** = sensors measuring voltage/current at every branch
- **GPIO pins** → MOSFETs = electronic switches that route power
- **Firmware** = brain that decides where power goes
- **Closed loop:** sense → calculate → decide → route → verify

**Energy recycling:** When a branch draws less than allocated, excess is redirected to other branches or stored in a capacitor. Utilization goes from ~60% to ~95%.

---

## Key EEE Theory

| Theory | Equation | Application |
|---|---|---|
| Affinity Laws | P ∝ n³ | 20% speed reduction = 49% power saving |
| KCL | I_in = I_m1 + I_m2 + I_loads | Power bus current balance |
| Ohm's Law | I = V / R | Current sensing via 1Ω sense resistor |
| Voltage Divider | V_adc = V_bus × R2/(R1+R2) | Safe ADC measurement (10kΩ+10kΩ) |
| PWM | V_eff = D × V_supply | Variable motor speed control |
| ISO 10816 | a_rms = √(ax²+ay²+az²) | Vibration fault classification |

---

## Software

| Language | Purpose | Location |
|---|---|---|
| MicroPython | Development + testing (fast iteration) | `src/master-pico/micropython/`, `src/slave-pico/micropython/` |
| C/C++ (Pico SDK) | Production demo (maximum performance) | `src/master-pico/c_sdk/`, `src/slave-pico/c_sdk/` |
| Python (Flask) | Web dashboard on laptop | `src/web/app.py` |

**Key files:**
- `src/shared/protocol.py` — 32-byte wireless packet format
- `src/master-pico/micropython/config.py` — Pico A pin assignments
- `src/slave-pico/micropython/config.py` — Pico B pin assignments
- `src/tools/flash.sh master|slave` — upload firmware via mpremote

---

## Scoring Rubric

| Category | Points | Our Strategy |
|---|---|---|
| Problem Definition & Solution Fit | 30 | 68% energy wasted globally. £162K systems inaccessible. UK regulations (ESOS, Net Zero) require this |
| Live Demo & Effectiveness | 25 | 6-step interactive demo: motors spin, turn dial, shake motor (fault), auto-recovery, show savings |
| Technical Implementation | 20 | Dual-core, PWM, ADC sensing, IMU vibration (ISO 10816), GPIO switching, wireless SCADA, PID control |
| Innovation & Creativity | 15 | Pico as switching fabric, Affinity Laws in firmware, £15 vs £162K, platform (water/greenhouse/HVAC/factory) |
| Documentation | 10 | Mermaid architecture, wiring diagrams, LaTeX equations, SCADA mockups |

**Score caps:** 60-point cap without wireless coordination. 50-point cap without live demo.

---

## Demo Script (6 Steps)

1. **Power on** — plug in PSU. "This is recycled energy powering a water plant"
2. **Auto-start** — motors spin, servos move, LEDs light. No buttons pressed (autonomous)
3. **Turn dial** — potentiometer changes motor speeds live. OLED updates. "Like a thermostat"
4. **Fault inject** — shake Motor 1. IMU detects → motor stops → power reroutes → OLED: FAULT
5. **Recovery** — press joystick to reset. System recovers automatically
6. **Show savings** — OLED: "Smart mode saved 52% energy vs dumb mode"

**Pitch:** "We didn't build a gadget. We built an infrastructure company in a box."

---

## Repository Structure

```
hack-a-bot-2026/
├── docs/
│   ├── gridbox-design.md       ← MAIN DESIGN DOC (start here)
│   ├── gridbox-proposal.md     ← detailed proposal + creativity defense
│   ├── context.md              ← THIS FILE (paste to AI for context)
│   ├── hardware-reference.md   ← kit components
│   └── ideas/                  ← archived brainstorming (14 ideas explored)
├── src/
│   ├── master-pico/            ← Pico A firmware (MicroPython + C)
│   ├── slave-pico/             ← Pico B firmware (MicroPython + C)
│   ├── shared/                 ← Wireless protocol definition
│   ├── web/                    ← Flask dashboard
│   ├── hardware/               ← CAD, wiring diagrams, datasheets
│   └── tools/                  ← flash.sh, serial monitor
├── README.md                   ← Public-facing project README
└── .gitignore                  ← notes/, CLAUDE.md, build artifacts
```

---

## Team Instructions

- **To understand the project:** Read this file
- **To see the full architecture:** Read `docs/gridbox-design.md`
- **To work on firmware:** Check `src/README.md` for dev workflow
- **To see why GridBox was chosen:** Check `docs/ideas/` for all 14 ideas explored
- **To wire hardware:** Follow pin mapping in `docs/gridbox-design.md` section 3-4
- **Questions about design decisions:** Check `docs/gridbox-proposal.md`
