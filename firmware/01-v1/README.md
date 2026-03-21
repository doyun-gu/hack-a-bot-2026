# Firmware v1 — Full Feature Set (Untested)

> First complete build. All modules integrated. Not yet tested on real hardware.

**Date:** 2026-03-21
**Status:** Code complete, awaiting hardware test

---

## What's In This Version

### Master Pico (Pico A — Grid Controller)

| Module | Feature | Status |
|---|---|---|
| `main.py` | 100Hz control loop: sense → decide → act → report | Written |
| `config.py` | All pin assignments matching design doc | Written |
| `nrf24l01.py` | nRF24L01+ wireless TX/RX with auto-ack | Written |
| `bmi160.py` | BMI160 IMU: accel ±4g, gyro ±500°/s, a_rms calculation | Written |
| `pca9685.py` | PCA9685 16-ch PWM: servo angles + motor speed % | Written |
| `power_manager.py` | ADC sensing: bus voltage, motor currents, power calcs | Written |
| `motor_control.py` | MOSFET GPIO switching + PCA9685 speed + ramping | Written |
| `imu_reader.py` | Core 1 thread: 100Hz IMU, vibration classification | Written |
| `fault_manager.py` | State machine: NORMAL→DRIFT→WARNING→FAULT→EMERGENCY | Written |
| `energy_signature.py` | 500Hz ADC sampling, baseline learning, divergence score | Written |
| `sorter.py` | Weight detection via current spike + timed servo gate | Written |
| `led_stations.py` | 4-LED sequence: INTAKE→WEIGH→RESULT→SORTED | Written |
| `calibration.py` | Empty-belt baseline + JSON flash storage | Written |

### Slave Pico (Pico B — SCADA Station)

| Module | Feature | Status |
|---|---|---|
| `main.py` | SCADA loop: receive → display → input → command | Written |
| `config.py` | Pin assignments for Pico B | Written |
| `nrf24l01.py` | nRF24L01+ wireless RX + command TX | Written |
| `ssd1306.py` | SSD1306 128×64 OLED driver (framebuf-based) | Written |
| `dashboard.py` | 5 OLED views + LINK LOST screen | Written |
| `operator.py` | Joystick debounce + potentiometer + long press | Written |
| `commander.py` | Send commands back to Pico A (override, reset, mode) | Written |

### Shared

| Module | Feature |
|---|---|
| `protocol.py` | 32-byte wireless packets: DATA, HEARTBEAT, ALERT, ACK, COMMAND |

---

## How to Flash This Version

```bash
# Master Pico (plug in Pico A via USB)
cd firmware/01-v1
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

- Not tested on real hardware — may have I2C/SPI timing issues
- Single packet type protocol — not yet upgraded to multi-type datagram rotation
- No startup self-test or LED blink error codes yet
- No dumb-vs-smart A/B comparison mode yet
- Energy signature baseline hardcoded — needs real motor calibration

---

## What to Test First

1. `test_led.py` — Pico alive?
2. `test_i2c_scan.py` — I2C devices found?
3. `test_imu.py` — IMU reads values?
4. `test_servo.py` — Servo moves?
5. `test_motor.py` — Motor spins?
6. `test_adc.py` — ADC reads voltage/current?
7. `test_wireless.py` — Two Picos talk?
8. Flash full firmware — does main.py run without crash?

---

## Next Version (v2) Should Include

- [ ] Multi-type datagram protocol (POWER/STATUS/PRODUCTION/HEARTBEAT/ALERT/COMMAND)
- [ ] Startup self-test with LED blink error codes
- [ ] Dumb vs Smart A/B comparison mode
- [ ] Pixel-drawn power bars on OLED (fill_rect, not text)
- [ ] Calibration from real motor baseline
- [ ] Bug fixes from hardware testing
