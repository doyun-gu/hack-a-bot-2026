# Hack-A-Bot 2026 — Project Context

## What This Is

24-hour hackathon (ARM + EEESoc sponsored). Build a working physical prototype using 2x Raspberry Pi Pico 2 with wireless coordination. Judged on: Problem Fit (30), Live Demo (25), Technical (20), Innovation (15), Docs (10).

## Chosen Idea: GridBox — Smart Infrastructure Control System

**Theme:** Sustainability + Autonomy | **Score: 96/100**

A £15 smart infrastructure controller powered by recycled energy. Senses power usage at every branch via ADC, autonomously reroutes excess via GPIO-controlled MOSFETs, detects equipment faults via IMU vibration, and reports wirelessly to a SCADA dashboard. Replaces £162K of industrial systems.

**Demo scenario:** Miniature smart water bottling plant — pump, fill valve, conveyor, quality gate, all running autonomously with fault detection.

## Key Design Documents

| Document | Location | Contents |
|---|---|---|
| **Main design doc** | `docs/01-overview/gridbox-design.md` | Architecture, pin mapping, wiring, software structure, algorithms, demo script, BOM — **single source of truth** |
| **Full proposal** | `docs/01-overview/gridbox-proposal.md` | Factory problems, cost comparison, creativity defense, IMU applications, EEE theory, all Mermaid diagrams |
| **Idea shortlist** | `docs/05-archive/ideas/idea-shortlist-v2.md` | All 14 ideas ranked (GridBox chosen) |
| **Alternative ideas** | `docs/05-archive/ideas/tremortray-proposal.md` | NeuroSync (98pts) — kept for reference |

## Hardware

- **2x Pico 2** (RP2350, ARM Cortex-M33, dual-core)
- **2x nRF24L01+ PA+LNA** (2.4GHz wireless, SPI)
- **BMI160 IMU** (6-axis, I2C 0x68)
- **PCA9685** (16-ch PWM servo driver, I2C 0x40)
- **2x MG90S Servos** (valve + gate)
- **2x DC Motors** (fan + pump/conveyor)
- **0.96" OLED SSD1306** (I2C 0x3C)
- **Joystick** (ADC + button)
- **Potentiometer** (ADC)
- **12V 6A PSU + LM2596S buck + 300W buck-boost**
- **Assorted:** LEDs, resistors, transistors/MOSFETs, capacitors, breadboards, wire

## Pin Mapping (Quick Reference)

### Pico A — Grid Controller
| Pin | Function |
|---|---|
| GP0/GP1 | nRF CE/CSN |
| GP2/GP3/GP16 | SPI (SCK/MOSI/MISO) |
| GP4/GP5 | I2C (SDA/SCL) → BMI160 + PCA9685 |
| GP10-13 | GPIO → MOSFET switches (Motor 1, Motor 2, LEDs, Recycle) |
| GP14/GP15 | Status LEDs (red/green) |
| GP26/GP27/GP28 | ADC (bus voltage, M1 current, M2 current) |

### Pico B — SCADA
| Pin | Function |
|---|---|
| GP0-3,GP16 | SPI → nRF24L01+ |
| GP4/GP5 | I2C → OLED |
| GP14/GP15 | Status LEDs |
| GP22 | Joystick button |
| GP26/GP27/GP28 | ADC (Joystick X/Y, Potentiometer) |

## Software

- **Development:** MicroPython (fast iteration, REPL debugging)
- **Production:** C/C++ Pico SDK (demo day — rock-solid timing)
- **Both versions** in `src/master-pico/` and `src/slave-pico/`
- **Web dashboard:** `src/web/app.py` (Flask, reads USB serial, localhost:5000)
- **Flash tool:** `src/tools/flash.sh master|slave`
- **Shared protocol:** `src/shared/protocol.py` (32-byte wireless packets)

## Core Innovation

The Pico IS the power grid's switching fabric:
- ADC pins = power sensors at every branch
- GPIO pins → MOSFETs = electronic switches routing power
- Firmware = brain that decides where power goes
- Closed loop: sense → calculate → decide → route → verify

## Key EEE Theory Used

- Affinity Laws: $P \propto n^3$ (20% slower = 49% less power)
- KCL/KVL on power bus
- Voltage divider for safe ADC measurement
- Current sensing via sense resistors ($I = V/R$)
- ISO 10816 vibration classification
- PWM motor speed control ($V_{eff} = D \times V_{supply}$)

## Development Workflow

1. I write firmware (MicroPython + C)
2. Team handles hardware wiring
3. Test each component individually via `src/master-pico/tests/`
4. Flash via `mpremote` or `src/tools/flash.sh`
5. Web dashboard on Mac for live monitoring
6. Commit + push automatically (full permissions granted)

## Conventions

- Commit and push after every meaningful change — full permissions
- Keep `docs/01-overview/gridbox-design.md` as single source of truth
- All diagrams in Mermaid (LR layout preferred for visibility)
- All equations in LaTeX ($..$ and $$..$$)
- Local brainstorming in `notes/` (gitignored)
- Test wireless link FIRST — score capped at 60 without it
- Use both Pico cores: Core 0 = main loop, Core 1 = fault detection
- Pin assignments in code MUST match `docs/01-overview/gridbox-design.md`

## Current State

- **Phase:** Design complete, ready for firmware development
- **Done:** Full architecture, pin mapping, wiring plan, demo scenario, all docs
- **Next:** Update firmware config files to match design, implement core features
- **Hackathon date:** TBD
