# Source Code

## Status: All MicroPython Modules Implemented

All 21 firmware modules are complete and integrated. See [`firmware-dev-plan.md`](firmware-dev-plan.md) for architecture details.

## Structure

```
src/
├── firmware-dev-plan.md          ← Development roadmap
├── master-pico/                  ← Pico A — Grid Controller
│   ├── micropython/
│   │   ├── main.py               ✅ Full 100Hz control loop (all modules integrated)
│   │   ├── config.py             ✅ Pin mapping + thresholds (matches design doc)
│   │   ├── nrf24l01.py           ✅ nRF24L01+ SPI driver (TX/RX, auto-ack)
│   │   ├── bmi160.py             ✅ BMI160 6-axis IMU (accel ±4g, gyro ±500°/s)
│   │   ├── pca9685.py            ✅ PCA9685 16-ch PWM (servos + motors)
│   │   ├── power_manager.py      ✅ ADC sensing (bus V, motor I, power calcs)
│   │   ├── motor_control.py      ✅ MOSFET switching + PCA9685 speed + ramping
│   │   ├── imu_reader.py         ✅ Core 1 thread (100Hz, vibration classification)
│   │   ├── fault_manager.py      ✅ State machine (NORMAL→DRIFT→WARNING→FAULT→EMERGENCY)
│   │   ├── energy_signature.py   ✅ 500Hz ADC sampling, 4-metric divergence scoring
│   │   ├── sorter.py             ✅ Weight detection + timed servo gate
│   │   ├── led_stations.py       ✅ 4-LED INTAKE→WEIGH→RESULT→SORTED sequence
│   │   └── calibration.py        ✅ Empty-belt baseline + JSON flash storage
│   ├── c_sdk/                    ⬜ Production firmware (demo day)
│   └── tests/
│       ├── test_wireless.py      ✅ PING-PONG test (pair with slave)
│       ├── test_imu.py           ✅ Accel + gyro + shake detection
│       ├── test_servo.py         ✅ Servo sweep 0°→180°→0°
│       ├── test_motor.py         ✅ Motor ramp 0%→100%→0%
│       ├── test_adc.py           ✅ Voltage + current + power readings
│       ├── test_led.py           ✅ Onboard LED blink
│       ├── test_i2c_scan.py      ✅ I2C device discovery
│       └── test_joystick.py      ✅ Joystick ADC + direction
│
├── slave-pico/                   ← Pico B — SCADA Station
│   ├── micropython/
│   │   ├── main.py               ✅ SCADA display + control loop
│   │   ├── config.py             ✅ Pin mapping (matches design doc)
│   │   ├── nrf24l01.py           ✅ Same driver as master
│   │   ├── ssd1306.py            ✅ 128x64 OLED (framebuf-based)
│   │   ├── dashboard.py          ✅ 5 OLED views + LINK LOST screen
│   │   ├── operator.py           ✅ Joystick debounce + pot + long press
│   │   └── commander.py          ✅ Wireless commands to Pico A
│   ├── c_sdk/                    ⬜ Production firmware
│   └── tests/
│       ├── test_wireless.py      ✅ PONG responder (pair with master)
│       └── test_oled.py          ✅ Display test screens
│
├── shared/
│   └── protocol.py               ✅ 32-byte packets (DATA/HEARTBEAT/ALERT/ACK/COMMAND)
│
├── web/                          ← Laptop dashboard
│   ├── app.py                    ✅ Flask + serial reader (parses GridBox JSON)
│   └── templates/
│       └── index.html            ✅ Live graphs, colour-coded status, production stats
│
├── hardware/                     ← Physical design files
│   ├── electronics/              ← Wooseong's workspace
│   └── chassis/                  ← Billy's workspace
│
└── tools/
    └── flash.sh                  ✅ Upload to Pico (master|slave)
```

## Quick Commands

```bash
# Flash master Pico
./tools/flash.sh master

# Flash slave Pico
./tools/flash.sh slave

# Run a test
mpremote run master-pico/tests/test_imu.py

# Open REPL on Pico
mpremote repl

# Start web dashboard
python web/app.py --no-serial

# Start web dashboard with serial
python web/app.py --port /dev/tty.usbmodem*
```

## Module Dependency Map

```
main.py (master)
├── config.py
├── nrf24l01.py
├── bmi160.py → imu_reader.py (Core 1)
├── pca9685.py → motor_control.py
├── power_manager.py
├── fault_manager.py (uses power_manager + imu_reader)
├── energy_signature.py (uses ADC, runs on Core 1)
├── sorter.py (uses motor_control + power_manager)
├── led_stations.py
├── calibration.py
└── protocol.py (shared)

main.py (slave)
├── config.py
├── nrf24l01.py
├── ssd1306.py → dashboard.py
├── operator.py
├── commander.py
└── protocol.py (shared)
```
