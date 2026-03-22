# GridBox Demo Firmware

## Quick Start

### 1. Flash Pico B (Slave) first
```bash
mpremote connect /dev/tty.usbmodem* run src/demo/demo_slave.py
```
MAX7219 shows `GRIDBOX` then `LINK---` — waiting for packets.

### 2. Flash Pico A (Master) — starts demo automatically
```bash
mpremote connect /dev/tty.usbmodem* run src/demo/demo_master.py
```

### For standalone demo (no USB):
```bash
# Save as main.py on each Pico — runs on power-up
mpremote connect /dev/tty.usbmodem* cp src/demo/demo_slave.py :main.py
mpremote connect /dev/tty.usbmodem* cp src/demo/demo_master.py :main.py
```

## Demo Sequence (~35 seconds)

| Stage | Duration | Pico A (Master) | MAX7219 Shows |
|---|---|---|---|
| 1. BOOT | 3s | Self-test, LED blinks | `bOOt` |
| 2. READY | 2s | System ready | `rEAdY` |
| 3. MOTOR 1 | 5s | Pump ON 65%, valve open | `5.0V` → `A 380` → `P 1900` |
| 4. MOTOR 2 | 5s | Conveyor ON 45%, sorting | `b 280` → `P3 r0` |
| 5. FAULT | 5s | Shake = IMU detects >2g | `F1  VIb` (flashing) |
| 6. RECOVERY | 3s | Motors restart in priority | `rECOVEr` |
| 7. RECYCLE | 4s | Cap charge/discharge x3 | `rECYCLE` |
| 8. DONE | — | All off, stats printed | `donE` |

## What's Real vs Simulated

| Component | Real | Simulated |
|---|---|---|
| nRF24L01+ wireless | YES | — |
| MAX7219 display | YES | — |
| BMI160 IMU | YES | — |
| PCA9685 PWM | YES | — |
| Motor driver | YES | — |
| Recycle LED | YES | — |
| Heartbeat LED | YES | — |
| ADC current/voltage | — | Preset values responding to motor state |

## Files

| File | Size | Purpose |
|---|---|---|
| `demo_master.py` | ~8KB | Pico A — runs full demo sequence |
| `demo_slave.py` | ~7KB | Pico B — receives and displays |
| `README.md` | — | This file |
