# GridBox — Quick Start Guide

> Get from zero to understanding in 30 minutes.

---

## 1. Read the README (2 min)

Start with the project [README](../../README.md) for a high-level overview of what GridBox is and why it exists.

## 2. Read the project summary (2 min)

[`project-summary.md`](project-summary.md) — a 2-page executive summary covering the problem, solution, key metrics, technical depth, and demo plan. Written for judges.

## 3. See the design doc for architecture (5 min)

[`gridbox-design.md`](gridbox-design.md) — the **single source of truth**. Contains system architecture diagrams, pin mapping for both Picos, wiring schematics, software structure, energy recycling algorithm, fault detection, demo script, and BOM.

## 4. See the wiring guide for hardware (5 min)

[`../02-electrical/wiring-connections.md`](../02-electrical/wiring-connections.md) — ~66 wires numbered with test order and progress tracking. Follow this when wiring the breadboards.

## 5. Flash firmware to a Pico

```bash
# First-time setup (installs mpremote)
./src/tools/setup-pico.sh install

# Flash master Pico (Pico A — Grid Controller)
./src/tools/setup-pico.sh master

# Flash slave Pico (Pico B — SCADA Station)
./src/tools/setup-pico.sh slave
```

## 6. Run the web dashboard

```bash
# Without hardware (uses mock data)
python src/web/app.py --no-serial --mock

# With Pico connected via USB
python src/web/app.py --port /dev/tty.usbmodem*
```

Open [http://localhost:8080](http://localhost:8080) in your browser.

## 7. Run tests on the Pico

```bash
# Basic alive test (LED blink)
mpremote run src/master-pico/tests/test_basic_alive.py

# I2C device scan (expects BMI160 @ 0x68, PCA9685 @ 0x40)
mpremote run src/master-pico/tests/test_i2c_scan.py

# ADC readings (bus voltage + motor currents)
mpremote run src/master-pico/tests/test_adc.py

# All available tests
ls src/master-pico/tests/
ls src/slave-pico/tests/
```

## 8. See the team plan

[`../04-team/team-plan.md`](../04-team/team-plan.md) — who does what, 24-hour timeline with per-member tasks, coordination milestones.

## 9. See the demo script

In [`gridbox-design.md` § 8](gridbox-design.md#8-demo-scenario-water-bottling-plant) — 6-step demo with specific actions, what judges see, and what they learn at each step.

## 10. See failure handling

[`../02-electrical/failure-handling.md`](../02-electrical/failure-handling.md) — 6 failure scenarios (F1–F6) with autonomous responses, plus a joystick-triggered fault simulator for the demo.

---

## Key Files at a Glance

| What | Where |
|---|---|
| Master firmware | `src/master-pico/micropython/` (13 modules) |
| Slave firmware | `src/slave-pico/micropython/` (7 modules) |
| Wireless protocol | `src/shared/protocol.py` |
| Web dashboard | `src/web/app.py` |
| Pin assignments | `src/master-pico/micropython/config.py` |
| Flash tool | `src/tools/flash.sh master\|slave` |
| Mock data | `src/tools/mock-data.py` |
| Frozen firmware | `firmware/01-v1/` through `firmware/04-v4/` |
