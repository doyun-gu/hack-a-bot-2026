# Development Workflow

## Environment

- **OS:** macOS (MacBook Pro = commander, Mac Mini = worker)
- **Pico SDK:** `~/Developer/pico-sdk` (set `PICO_SDK_PATH` before building)
- **ARM toolchain:** `/Applications/ArmGNUToolchain/13.3.rel1/arm-none-eabi/bin/`
- **Python:** system Python 3 for Flask dashboard
- **mpremote:** MicroPython remote tool (pip install mpremote)

## Flash MicroPython Firmware

```bash
# Flash master Pico (all 16 modules)
./src/tools/flash.sh master

# Flash slave Pico (all 12 modules)
./src/tools/flash.sh slave
```

flash.sh handles:
- Soft-reset before upload (avoids timer-interrupt USB blocking)
- Retry logic (up to 3 attempts per file)
- Uploads main.py last (so dependencies are ready)

## Flash C SDK Firmware

```bash
# Set up environment
export PICO_SDK_PATH=~/Developer/pico-sdk
export PATH="/Applications/ArmGNUToolchain/13.3.rel1/arm-none-eabi/bin:$PATH"

# Build
cd src/slave-pico/c_sdk
mkdir -p build && cd build
cmake ..
make -j4

# Flash — hold BOOTSEL on Pico, plug USB, then:
cp gridbox_slave.uf2 /Volumes/RP2350/    # Production firmware
# or
cp test_hw.uf2 /Volumes/RP2350/          # Combined hardware test
```

**Important:** Pico 2 mounts as `RP2350`, not `RPI-RP2`.

## Hardware Tests

### Single-Pico Tests (no second Pico needed)

```bash
# nRF24L01+ SPI register read/write (master pinout)
./src/tools/flash.sh test

# MAX7219 7-segment display
./src/tools/flash.sh test-display

# nRF + MAX7219 combined (with display feedback)
./src/tools/flash.sh test-nrf-display

# C SDK combined test (nRF + 7-seg + heartbeat LED)
# → Build test_hw.uf2 and drag to RP2350 drive
```

### Two-Pico Wireless Tests

```bash
# Step 1: Flash PING sender to Pico A
./src/tools/flash.sh test-wireless-master

# Step 2: Unplug Pico A, plug in Pico B
# Step 3: Flash PONG responder to Pico B
./src/tools/flash.sh test-wireless-slave

# Step 4: Power both Picos — they find each other and test wireless link
```

## Web Dashboard

```bash
cd src/web
python3 app.py
# Open http://localhost:5000

# Test without hardware:
python3 ../tools/mock-data.py
```

## REPL Debugging (MicroPython)

```bash
# Connect to Pico REPL
mpremote repl

# Run a single test script without uploading
mpremote run src/master-pico/tests/test_nrf_debug.py

# Upload a single file
mpremote cp src/shared/protocol.py :protocol.py
```

## Git Workflow

- **Branches:** `main` (Doyun), `wooseong/electronics`, `billy/mechanical`
- **Commits:** Auto-commit and push after every meaningful change
- **Worker branches:** `worker/<task>-<date>` (Mac Mini autonomous tasks)
- **217 commits** as of 2026-03-22, mostly by Doyun (210)

## Common Issues

| Problem | Fix |
|---|---|
| mpremote stuck at upload | Timer interrupt blocking USB. Unplug/replug Pico |
| `PICO_SDK_PATH` not found | `export PICO_SDK_PATH=~/Developer/pico-sdk` |
| `RP2350` drive not appearing | Hold BOOTSEL before plugging USB |
| nRF reads 0xFF | Module not connected — check VCC, GND, MISO |
| nRF reads 0x00 | SPI bus issue — check SCK, MOSI, MISO |
| MAX7219 dim/flickery | Power from VBUS (5V) instead of 3V3 |
| MicroPython `rjust` error | Use manual padding — MicroPython lacks `str.rjust()` |

## Heartbeat LED Convention

All firmware (MicroPython and C) uses the same heartbeat LED pattern:

| State | Rate | Meaning |
|---|---|---|
| HB_BOOT | 80ms | Starting up |
| HB_NORMAL | 400ms | All good |
| HB_ACTIVE | 100ms | SPI/wireless activity (auto-reverts) |
| HB_FAULT | 120ms | Error detected |

Implemented via timer interrupt — zero CPU cost. The LED blinks independently of the main loop.
