# Firmware v3 — Mock Data, C SDK Stubs, Integration Tests

> Mock data injection for dashboard testing, C SDK scaffolding for production firmware, integration test suite.

**Date:** 2026-03-21
**Status:** Code complete, untested on hardware

---

## What's New in v3 (vs v2)

| Feature | Description |
|---|---|
| **Mock data injection** | Web dashboard now accepts POST to `/api/inject`. Run `python app.py --no-serial --mock` for one-command demo — no second terminal needed. |
| **Internal mock generator** | `/api/mock/start` and `/api/mock/stop` endpoints control built-in 5Hz mock data generation. |
| **External mock data tool** | `mock-data.py` now POSTs to `/api/inject` instead of writing to a file. Three modes: normal, fault, full demo. |
| **C SDK header files** | Production firmware headers for BMI160, PCA9685, nRF24L01+, and Power Manager — all matching the MicroPython API. |
| **C SDK stub implementations** | Each `.c` file prints `[STUB]` with TODO comments for real implementation. Ready to fill in during C port. |
| **CMakeLists.txt updated** | Project renamed to `gridbox_master`, all 4 driver source files included in build. |
| **Integration test suite** | 115 tests verify all modules without hardware: imports, config, protocol round-trips, fault manager states, sorter classification, power math, energy signatures. |

---

## All Features (v1 + v2 + v3)

### Master Pico (Pico A — Grid Controller)

| Module | Feature |
|---|---|
| `main.py` | 100Hz control loop + self-test + rotation sending + A/B comparison |
| `config.py` | All pin assignments matching design doc |
| `nrf24l01.py` | nRF24L01+ wireless TX/RX with error-safe SPI |
| `bmi160.py` | BMI160 IMU with error-safe I2C reads |
| `pca9685.py` | PCA9685 PWM with error-safe I2C writes |
| `power_manager.py` | ADC sensing: bus voltage, motor currents, power calcs |
| `motor_control.py` | MOSFET GPIO switching + PCA9685 speed + ramping |
| `imu_reader.py` | Core 1 thread: 100Hz IMU, vibration classification (thread-safe) |
| `fault_manager.py` | State machine: NORMAL -> DRIFT -> WARNING -> FAULT -> EMERGENCY |
| `energy_signature.py` | 500Hz ADC sampling, baseline learning, divergence score |
| `sorter.py` | Weight detection via current spike + timed servo gate |
| `led_stations.py` | 4-LED sequence: INTAKE -> WEIGH -> RESULT -> SORTED |
| `calibration.py` | Empty-belt baseline + JSON flash storage |

### Slave Pico (Pico B — SCADA Station)

| Module | Feature |
|---|---|
| `main.py` | SCADA loop: multi-type packet handling + self-test + comparison trigger |
| `config.py` | Pin assignments for Pico B (6 dashboard views) |
| `nrf24l01.py` | nRF24L01+ wireless RX + command TX with error-safe SPI |
| `ssd1306.py` | SSD1306 128x64 OLED driver (framebuf-based) |
| `dashboard.py` | 6 OLED views: Status, Power, Faults, Production, Manual, Comparison |
| `operator.py` | Joystick debounce + potentiometer + long press |
| `commander.py` | Send commands to Pico A (speed, servo, threshold, mode, reset, e-stop) |

### Shared

| Module | Feature |
|---|---|
| `protocol.py` | 6 packet types, 32 bytes each, rotation schedule, pack/unpack for all types |

### C SDK (new in v3)

| File | Description |
|---|---|
| `bmi160.h/.c` | IMU driver: init, read accel/gyro, RMS, temperature |
| `pca9685.h/.c` | PWM driver: servos, motors, duty cycle, all-off |
| `nrf24l01.h/.c` | Wireless driver: send, recv, channel/rate config |
| `power_manager.h/.c` | ADC sensing: voltage, current, power calculations |
| `CMakeLists.txt` | Pico SDK build config with all sources |

### Tests (new in v3)

| File | Description |
|---|---|
| `test_integration.py` | 115 checks: imports, config, protocol, fault manager, sorter, power, energy signature |

---

## How to Flash This Version

```bash
# Master Pico (plug in Pico A via USB)
cd firmware/03-v3
mpremote cp shared/protocol.py :protocol.py
for f in master/*.py; do mpremote cp "$f" ":$(basename $f)"; done
mpremote reset

# Slave Pico (plug in Pico B via USB)
mpremote cp shared/protocol.py :protocol.py
for f in slave/*.py; do mpremote cp "$f" ":$(basename $f)"; done
mpremote reset
```

### Run Integration Tests (on laptop)

```bash
cd firmware/03-v3
python3 tests/test_integration.py
# Expected: 115/115 tests passed
```

---

## Known Limitations

- Not yet tested on real hardware
- C SDK files are stubs — print `[STUB]` instead of real I2C/SPI operations
- Energy signature baseline needs real motor calibration
- A/B comparison blocks the main loop for ~20s (acceptable for demo)

---

## What v4 (demo) Should Include

- [ ] Bug fixes from hardware testing
- [ ] Calibrated thresholds for real motor/belt setup
- [ ] C SDK implementations filled in
- [ ] Demo script rehearsed and timed
- [ ] Final polish for judging
