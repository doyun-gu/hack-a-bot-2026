# Firmware v4 — Wireless Verified

**Snapshot date:** 2026-03-22
**Status:** Wireless link + datagram protocol fully tested and working

## What's new since v3

- **Heartbeat LED** — timer-driven, activity-aware (boot/normal/active/fault)
- **MAX7219 7-segment display** — SPI1 driver + indicator system
- **Boot scripts** — both Picos have boot.py for pre-main setup
- **Packet tracker** — wireless reliability stats
- **Datagram protocol tested** — all 6 types verified over wireless (200+ packets, 0 bad)
- **C SDK** — added MAX7219 driver, SSD1306 driver, config.h, combined test (test_hw.c)
- **35 test scripts** — nRF debug, wireless PING/PONG, datagram protocol, display, IMU, servo, motor

## Test Results

| Test | Result |
|---|---|
| nRF SPI (Pico A) | PASS — status 0x0E, channel write/read OK |
| nRF SPI (Pico B) | PASS — status 0x0E, channel write/read OK |
| MAX7219 display | PASS — all digits, brightness, flash working |
| C SDK combined test | PASS — nRF + MAX7219 + heartbeat LED |
| Two-Pico wireless | PASS — standalone master + USB slave |
| Datagram protocol | PASS — all 6 types, bidirectional, 0 bad packets |

## File Counts

| Directory | Files | Description |
|---|---|---|
| master/ | 16 .py | Grid Controller MicroPython firmware |
| slave/ | 12 .py | SCADA Station MicroPython firmware |
| shared/ | 1 .py | Protocol (6 datagram types, 32-byte packets) |
| c_sdk/ | 10 files | C SDK production firmware + test |
| tests/ | 35 .py | All hardware test scripts |

## Changes from v3

- master: +heartbeat.py, +boot.py, +packet_tracker.py, config.py updated (PCA9685 motor PWM, LED bank removed)
- slave: +heartbeat.py, +boot.py, +seg_display.py, +oled_default.py, +packet_tracker.py, config.py updated (SPI1 for MAX7219)
- c_sdk: +max7219.c/h, +ssd1306.c/h, +config.h, +test_hw.c, CMakeLists.txt updated
- tests: +28 new test scripts (was 1 in v3)
