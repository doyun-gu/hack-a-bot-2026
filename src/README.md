# Source Code

## Project Structure

```
src/
├── master-pico/              # Pico A — primary sensing + processing unit
│   ├── micropython/          # Development firmware (Python — fast iteration)
│   │   ├── main.py           # Entry point
│   │   ├── config.py         # Pin assignments + constants
│   │   └── [driver].py       # Component drivers (added as needed)
│   ├── c_sdk/                # Production firmware (C — maximum performance)
│   │   ├── CMakeLists.txt    # Build configuration
│   │   ├── main.c            # Entry point
│   │   └── [driver].c/.h    # Component drivers (ported from Python)
│   └── tests/                # Individual component test scripts
│       ├── test_i2c_scan.py  # Scan I2C bus for connected devices
│       ├── test_joystick.py  # Read joystick X/Y/button
│       └── test_led.py       # Blink LED (alive check)
│
├── slave-pico/               # Pico B — display + base station
│   ├── micropython/          # Development firmware
│   ├── c_sdk/                # Production firmware
│   └── tests/                # Component tests
│
├── shared/                   # Shared between both Picos
│   └── protocol.py           # Wireless packet format (32-byte struct)
│
├── web/                      # Mac-side web dashboard
│   ├── app.py                # Flask server — reads serial, serves UI
│   └── templates/
│       └── index.html        # Live dashboard (roll, pitch, score, etc.)
│
├── hardware/                 # Physical design files
│   ├── README.md             # Pin mapping reference
│   ├── cad/                  # 3D models, chassis (collaborator-managed)
│   ├── wiring/               # Wiring diagrams
│   └── datasheets/           # Component datasheets
│
└── tools/                    # Development utilities
    └── flash.sh              # Upload firmware to Pico via mpremote
```

## Development Workflow

### Two-Version Strategy

| Version | Language | Purpose | When |
|---|---|---|---|
| **MicroPython** | Python | Development + testing — instant feedback via REPL | Build phase |
| **C SDK** | C/C++ | Production demo — maximum performance + stability | Demo day |

Develop in Python first (fast iteration). Port to C once working (rock-solid demo).

### Quick Commands

```bash
# Flash master pico with MicroPython firmware
./tools/flash.sh master

# Flash slave pico
./tools/flash.sh slave

# Run a test on connected Pico
mpremote run master-pico/tests/test_i2c_scan.py

# Open live REPL on Pico
mpremote repl

# Start web dashboard
python web/app.py --port /dev/tty.usbmodem*

# Build C firmware (requires PICO_SDK_PATH set)
cd master-pico/c_sdk && mkdir -p build && cd build && cmake .. && make
```

### Testing Strategy

Test each component individually BEFORE integrating:

```
1. test_led.py          → Pico is alive
2. test_i2c_scan.py     → I2C bus working, devices detected
3. test_joystick.py     → ADC reading correctly
4. test_imu.py          → IMU returning valid data (added when IMU wired)
5. test_servo.py        → Servos moving correctly (added when servos wired)
6. test_wireless.py     → nRF24L01+ link between two Picos (added when both wired)
7. test_oled.py         → OLED displaying text/graphics (added when OLED wired)
8. test_all.py          → Full integration test
```
