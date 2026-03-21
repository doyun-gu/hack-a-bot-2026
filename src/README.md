# Source Code

## Development Plan

See [`firmware-dev-plan.md`](firmware-dev-plan.md) for the full roadmap: architecture, module dependency map, 4 development phases, line estimates, and technical decisions.

## Structure

```
src/
├── firmware-dev-plan.md          ← Development roadmap (start here)
├── master-pico/                  ← Pico A — Grid Controller
│   ├── micropython/              ← Dev firmware (fast iteration)
│   │   ├── main.py               ← Entry point + 100Hz main loop
│   │   ├── config.py             ← Pin assignments + thresholds
│   │   ├── bmi160.py             ← IMU driver (I2C)
│   │   ├── nrf24l01.py           ← Wireless driver (SPI)
│   │   ├── pca9685.py            ← PWM driver (I2C)
│   │   ├── power_manager.py      ← ADC sensing + power calcs
│   │   ├── motor_control.py      ← Motor speed + servo angles
│   │   ├── imu_reader.py         ← Core 1: vibration monitoring
│   │   ├── fault_manager.py      ← State machine + load shedding
│   │   ├── energy_signature.py   ← Current analysis (Wooseong's design)
│   │   ├── sorter.py             ← Weight detection + timed sorting
│   │   ├── led_stations.py       ← 4-LED production sequence
│   │   └── calibration.py        ← Startup calibration
│   ├── c_sdk/                    ← Production firmware (demo day)
│   └── tests/                    ← Individual component tests
│
├── slave-pico/                   ← Pico B — SCADA Station
│   ├── micropython/
│   │   ├── main.py               ← SCADA display loop
│   │   ├── config.py             ← Pin assignments
│   │   ├── nrf24l01.py           ← Wireless RX + commands
│   │   ├── ssd1306.py            ← OLED driver
│   │   ├── dashboard.py          ← 4+ OLED views
│   │   ├── operator.py           ← Joystick + pot input
│   │   └── commander.py          ← Commands to Pico A
│   └── c_sdk/
│
├── shared/
│   └── protocol.py               ← 32-byte wireless packet format
│
├── web/                          ← Laptop dashboard
│   ├── app.py
│   └── templates/index.html
│
├── hardware/                     ← Physical design files
│   ├── electronics/              ← Wooseong's workspace
│   └── chassis/                  ← Billy's workspace
│
└── tools/
    └── flash.sh                  ← Upload to Pico (master|slave)
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

# Build C firmware
cd master-pico/c_sdk && mkdir -p build && cd build && cmake .. && make
```

## Development Order

1. `nrf24l01.py` — wireless link (FIRST — score-capped without it)
2. `bmi160.py` — IMU vibration sensing
3. `pca9685.py` — servo + motor PWM control
4. ADC sensing in `power_manager.py`
5. `ssd1306.py` — OLED display
6. Integration: fault detection + load shedding + dashboard
7. Factory-specific: sorting + LED stations + calibration
8. C SDK port of core modules
