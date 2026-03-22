# Project Status

**Last updated:** 2026-03-22

## Phase: Hardware Testing + Integration

All firmware modules written. Now testing hardware and building toward demo.

## Done

- [x] Full architecture, pin mapping, wiring plan, demo scenario
- [x] All 16 master MicroPython modules
- [x] All 12 slave MicroPython modules (including seg_display.py)
- [x] Shared protocol (6 datagram types, 32-byte packets)
- [x] Firmware v1 snapshot (basic), v2 snapshot (datagram + self-test), v3 snapshot (C SDK)
- [x] Debug system with LED blink codes + OLED error messages
- [x] Failure handling protocol (F1-F6) + fault simulator
- [x] Startup self-test with error reporting
- [x] Dumb vs Smart A/B comparison mode
- [x] Web dashboard (Flask + SQLite + mock data generator)
- [x] Documentation (35+ docs in numbered folders)
- [x] C SDK drivers: nRF24L01, BMI160, PCA9685, SSD1306, MAX7219, power manager
- [x] Heartbeat LED — timer-driven, activity-aware (boot/normal/active/fault)
- [x] nRF24L01+ single-Pico SPI test — PASS (Pico B)
- [x] MAX7219 7-segment display — wired on SPI1, driver + test working (Pico B)
- [x] C SDK combined test (test_hw.uf2) — nRF + MAX7219 + heartbeat LED
- [x] Flash tool (flash.sh) with soft-reset, retry, 7 test modes
- [x] Wiring docs with pinout reference images

## Todo — Testing (in order)

1. [ ] **Wire nRF to Pico A** (same pinout: CE=GP0, CSN=GP1, SCK=GP2, MOSI=GP3, MISO=GP16)
2. [ ] **Test nRF on Pico A** — `./src/tools/flash.sh test`
3. [ ] **Two-Pico wireless link** — PING/PONG handshake
   - `./src/tools/flash.sh test-wireless-master` (Pico A)
   - `./src/tools/flash.sh test-wireless-slave` (Pico B)
4. [ ] **Protocol datagram test** — verify all 6 packet types over wireless
5. [ ] **Telemetry end-to-end** — Pico A sends sensor data, Pico B displays
6. [ ] **Command test** — Pico B sends joystick/pot commands, Pico A responds
7. [ ] **Fault injection** — trigger F1-F6, verify display + LED + wireless alert

## Todo — Hardware

- [ ] Complete ~78-wire wiring (per wiring-connections.md Rev 2)
- [ ] Connect BMI160 IMU to Pico A (I2C: SDA=GP4, SCL=GP5)
- [ ] Connect PCA9685 PWM driver to Pico A (I2C: same bus, addr 0x40)
- [ ] Connect DC motors: PCA9685 CH2/CH3 → 1kΩ → MOSFET gates (+ sense resistors + flyback diodes)
- [ ] Connect OLED SSD1306 to Pico B (I2C: SDA=GP4, SCL=GP5)
- [ ] Connect joystick + potentiometer to Pico B (ADC: GP26, GP27, GP28)
- [ ] Connect recycle path MOSFET on GP13
- [ ] Connect servos to PCA9685 (channels 0-1)
- [ ] Power supply: 12V PSU → LM2596S buck → 5V bus
- [x] ~~Connect LED bank on GP12~~ — **REPLACED** by MAX7219 display on Pico B SPI1
- [x] ~~Motor MOSFETs on GP10/GP11~~ — **REPLACED** by PCA9685 Ch2/Ch3 → MOSFET

## Todo — Production

- [ ] C SDK production firmware for both Picos
- [ ] Factory chassis assembly (Billy)
- [ ] Full system demo rehearsal
- [ ] A/B comparison demo: dumb vs smart mode

## Critical Path

**Wireless link is the #1 priority.** Without it, the demo score is capped at 60/100 (no Live Demo + no wireless Technical points). Everything else depends on the two Picos talking to each other.

## Team Status

- **Wooseong:** 5 commits — electronics circuits, wiring, testing
- **Billy:** 2 commits — mechanical chassis
- **Doyun:** 210 commits — firmware, docs, tools, AI-assisted development
