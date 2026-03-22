# Hack-A-Bot 2026 — Project Context

## What This Is

24-hour hackathon (ARM + EEESoc sponsored). Build a working physical prototype using 2x Raspberry Pi Pico 2 with wireless coordination. Judged on: Problem Fit (30), Live Demo (25), Technical (20), Innovation (15), Docs (10).

## Chosen Idea: GridBox — Smart Infrastructure Control System

**Theme:** Sustainability + Autonomy | **Score: 96/100**

A £15 smart infrastructure controller powered by recycled energy. Senses power usage at every branch via ADC, autonomously reroutes excess via GPIO-controlled MOSFETs, detects equipment faults via IMU vibration, and reports wirelessly to a SCADA dashboard. Replaces £162K of industrial systems.

**Demo scenario:** Miniature smart water bottling plant — pump, fill valve, conveyor, quality gate, all running autonomously with fault detection.

## Deep Context (read after /compact)

For full project context after compaction or in a new session, read `.context/`:

| File | Contents |
|---|---|
| `.context/project-overview.md` | Hackathon rules, scoring, team, GridBox concept |
| `.context/architecture.md` | Two-Pico design, protocol, software layers, dual-core strategy |
| `.context/file-map.md` | Complete annotated file tree (what every file does) |
| `.context/hardware.md` | Pin mapping, wiring, SPI/I2C buses, components |
| `.context/dev-workflow.md` | Build, flash, test, debug commands + common issues |
| `.context/status.md` | **Current state** — done/todo checklists (update frequently) |

## Key Design Documents

| Document | Location | Contents |
|---|---|---|
| **Main design doc** | `docs/01-overview/gridbox-design.md` | Architecture, pin mapping, wiring, software structure, algorithms, demo script, BOM — **single source of truth** |
| **Full proposal** | `docs/01-overview/gridbox-proposal.md` | Factory problems, cost comparison, creativity defense, IMU applications, EEE theory, all Mermaid diagrams |
| **Idea shortlist** | `docs/05-archive/ideas/idea-shortlist-v2.md` | All 14 ideas ranked (GridBox chosen) |
| **Alternative ideas** | `docs/05-archive/ideas/tremortray-proposal.md`, `docs/05-archive/ideas/steadyhand-proposal.md` | NeuroSync (98pts) and SteadyHand (95pts) — kept for reference |

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
- **Web dashboard:** `src/web/app.py` (Flask + SQLite, reads USB serial, localhost:5000)
- **Flash tool:** `src/tools/flash.sh master|slave` + `src/tools/setup-pico.sh`
- **Shared protocol:** `src/shared/protocol.py` (32-byte wireless packets, 6 datagram types)
- **Mock data:** `src/tools/mock-data.py` (dashboard testing without hardware)
- **Firmware snapshots:** `firmware/01-v1/` and `firmware/02-v2/` (frozen releases)

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

- **Phase:** Hardware testing + integration
- **Commits:** 130+ on main
- **Team PRs merged:** Wooseong (4 PRs — electronics circuits, wiring, testing), Billy (1 PR — chassis)

### Done

- [x] Full architecture, pin mapping, wiring plan, demo scenario
- [x] All 21 MicroPython modules (13 master + 7 slave + 1 shared)
- [x] Firmware v1 snapshot (basic) and v2 snapshot (datagram protocol + self-test)
- [x] Protocol v2: 6 datagram types (POWER, STATUS, PRODUCTION, HEARTBEAT, ALERT, COMMAND)
- [x] Debug system with LED blink codes + OLED error messages
- [x] Failure handling protocol (F1-F6) + fault simulator for demo
- [x] Startup self-test with error reporting
- [x] Dumb vs Smart A/B comparison mode
- [x] Web dashboard with SQLite database + mock data generator
- [x] Documentation organised in numbered folders (01-overview through 05-archive)
- [x] Pico hardware tested (LED + ADC confirmed working on partial-solder board)
- [x] C SDK drivers created (nRF, BMI160, PCA9685, SSD1306, power manager)
- [x] Heartbeat LED system — timer-driven, activity-aware (normal/active/fault/boot)
- [x] nRF24L01+ single-Pico SPI test — PASS (status register read/write verified)
- [x] MAX7219 7-segment display — wired on SPI1, driver + test working
- [x] Display indicator system — shows LINK On/OFF, FAULT codes, power readings
- [x] C SDK combined test (test_hw.uf2) — nRF + MAX7219 + heartbeat in one binary
- [x] Flash tool (flash.sh) with soft-reset, retry logic, test modes
- [x] Wiring docs with pinout reference images (nRF + Pico 2 + MAX7219)

### Todo — Testing (do in this order)

- [ ] **1. Wire nRF to Pico A** (same pinout as Pico B: CE=GP0, CSN=GP1, SCK=GP2, MOSI=GP3, MISO=GP16)
- [ ] **2. Test nRF on Pico A** — `./src/tools/flash.sh test` (single-Pico SPI check)
- [ ] **3. Two-Pico wireless link** — PING/PONG handshake test (Pico A sends, Pico B replies)
- [ ] **4. Protocol datagram test** — verify all 6 packet types pack/unpack correctly over wireless
- [ ] **5. Telemetry end-to-end** — Pico A sends real sensor data, Pico B displays on OLED + 7-segment
- [ ] **6. Command test** — Pico B sends joystick/pot commands, Pico A responds (motor speed, servo, mode)
- [ ] **7. Fault injection test** — trigger each fault (F1-F6), verify display + LED + wireless alert

### Todo — Hardware

- [ ] Complete hardware wiring (81 wires per wiring-connections.md)
- [ ] Connect BMI160 IMU to Pico A (I2C: SDA=GP4, SCL=GP5)
- [ ] Connect PCA9685 PWM driver to Pico A (I2C: same bus, addr 0x40)
- [ ] Connect OLED SSD1306 to Pico B (I2C: SDA=GP4, SCL=GP5)
- [ ] Connect joystick + potentiometer to Pico B (ADC: GP26, GP27, GP28)
- [ ] Connect DC motors + MOSFETs to Pico A (GP10-13)
- [ ] Connect servos to PCA9685 (channels 0-1)
- [ ] Power supply: 12V PSU → LM2596S buck → 5V bus

### Todo — Production

- [ ] C SDK production firmware for both Picos (demo day — rock-solid timing)
- [ ] Factory chassis assembly (Billy)
- [ ] Full system demo rehearsal
- [ ] A/B comparison demo: dumb vs smart mode live on display

- **Hackathon date:** TBD
