# Firmware v2 — Datagram + Self-Test + Comparison + Quality Fixes

> Multi-type datagram protocol, startup diagnostics, A/B comparison, hardened error handling.

**Date:** 2026-03-21
**Status:** Code complete, untested on hardware

---

## What's New in v2 (vs v1)

| Feature | Description |
|---|---|
| **Multi-type datagram protocol** | 6 packet types (POWER, STATUS, PRODUCTION, HEARTBEAT, ALERT, COMMAND) rotating at 50Hz. 4.5x more data in the same 32-byte bandwidth. |
| **Packet rotation schedule** | POWER x4, STATUS x2, PRODUCTION x1, HEARTBEAT x1 per 8-cycle rotation. ALERT breaks rotation on fault. |
| **Startup self-test** | Tests I2C, SPI, IMU, PCA9685, nRF24L01+, ADC on boot. Blink codes on red LED identify failures without a laptop. |
| **LED blink error codes** | 1=I2C, 2=SPI, 3=IMU, 4=PCA, 5=nRF, 6=ADC, 8=OLED. Count the blinks. |
| **Dumb vs Smart comparison** | Run motors at 100% (dumb) then optimised (smart) for 10s each, measure power, show savings on OLED. |
| **COMPARISON dashboard view** | New 6th OLED view shows dumb/smart power and savings percentage with bar graph. |
| **I2C error handling** | BMI160 and PCA9685 I2C calls wrapped in try/except — no more crashes on bus glitch. |
| **SPI error handling** | nRF24L01+ SPI calls wrapped in try/finally — CSN always returns high even on error. |
| **Duplicate code removal** | Removed duplicate `set_frequency` in PCA9685 driver. |
| **Unused memory cleanup** | Removed unused `_samples` list in energy signature monitor. |

---

## All Features (v1 + v2)

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

---

## How to Flash This Version

```bash
# Master Pico (plug in Pico A via USB)
cd firmware/02-v2
mpremote cp shared/protocol.py :protocol.py
for f in master/*.py; do mpremote cp "$f" ":$(basename $f)"; done
mpremote reset

# Slave Pico (plug in Pico B via USB)
mpremote cp shared/protocol.py :protocol.py
for f in slave/*.py; do mpremote cp "$f" ":$(basename $f)"; done
mpremote reset
```

---

## Known Limitations

- Not yet tested on real hardware
- Energy signature baseline needs real motor calibration
- A/B comparison blocks the main loop for ~20s (acceptable for demo)
- `time.ticks_diff` uptime calculation wraps after ~4.5 minutes
- OLED comparison view needs actual data from a completed comparison run

---

## What v3 Should Include

- [ ] Bug fixes from hardware testing
- [ ] Calibrated thresholds for real motor/belt setup
- [ ] Proper uptime counter that doesn't wrap
- [ ] OLED pixel-drawn power bars with fill_rect (not just text)
- [ ] Wireless link quality indicator (packet loss %)
- [ ] Servo position feedback in PRODUCTION view
- [ ] Save comparison results to flash for persistence across reboot
