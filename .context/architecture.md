# System Architecture

## Two-Pico Design

```
┌─────────────────────┐     nRF24L01+ 2.4GHz     ┌─────────────────────┐
│   PICO A (Master)   │◄──────────────────────────►│   PICO B (Slave)    │
│   Grid Controller   │      32-byte packets       │   SCADA Station     │
│                     │      Channel 100            │                     │
│ - Power sensing     │      250kbps                │ - OLED display      │
│ - Motor control     │                             │ - 7-seg display     │
│ - Fault detection   │                             │ - Joystick input    │
│ - LED stations      │                             │ - Operator commands │
└─────────────────────┘                             └─────────────────────┘
        │                                                   │
        ├── SPI0: nRF24L01+                                 ├── SPI0: nRF24L01+
        ├── SPI1: (unused)                                  ├── SPI1: MAX7219 7-seg
        ├── I2C0: BMI160 + PCA9685                          ├── I2C0: SSD1306 OLED
        ├── ADC: voltage + current sensing                  ├── ADC: joystick + pot
        └── GPIO: MOSFET switches + LEDs                    └── GPIO: status LEDs
```

## Communication Protocol

**32-byte wireless packets** over nRF24L01+ at 250kbps on channel 100.

6 datagram types:

| Type | Direction | Content |
|---|---|---|
| POWER | A → B | Bus voltage, motor currents, total power, efficiency % |
| STATUS | A → B | System mode, motor states, fault flags, uptime |
| PRODUCTION | A → B | Items processed, good/rejected counts, throughput |
| HEARTBEAT | A ↔ B | Alive signal with sequence number |
| ALERT | A → B | Fault code, severity, affected subsystem |
| COMMAND | B → A | Operator commands (mode switch, motor speed, servo pos) |

**Addresses:**
- Master TX / Slave RX: `NSYNT` (5 bytes)
- Slave TX / Master RX: `NSYNR` (5 bytes)

## Software Layers

### MicroPython (Development)
Fast iteration, REPL debugging. Used during hardware testing and prototyping.

### C SDK (Production)
Rock-solid timing for demo day. Eliminates MicroPython overhead.

### Both versions mirror the same module structure:

**Master (Pico A):**
- `main.py` — dual-core orchestrator (Core 0: main loop, Core 1: fault detection)
- `config.py` — pin assignments, constants
- `power_manager.py` — ADC sensing, power routing, efficiency calculation
- `motor_control.py` — PWM speed control for DC motors
- `fault_manager.py` — failure handling (F1-F6), fault simulation
- `energy_signature.py` — vibration-based fault classification
- `bmi160.py` — IMU driver (I2C)
- `pca9685.py` — PWM servo driver (I2C)
- `nrf24l01.py` — wireless transceiver (SPI)
- `heartbeat.py` — timer-driven LED with state-based blink patterns
- `sorter.py` — quality gate logic
- `calibration.py` — ADC/sensor calibration
- `led_stations.py` — status LED management
- `imu_reader.py` — raw IMU data reader

**Slave (Pico B):**
- `main.py` — display + wireless + operator input loop
- `config.py` — pin assignments
- `dashboard.py` — OLED display layouts
- `commander.py` — command packet builder
- `operator.py` — joystick/pot input handler
- `ssd1306.py` — OLED driver (I2C)
- `nrf24l01.py` — wireless transceiver (SPI)
- `heartbeat.py` — timer-driven LED
- `seg_display.py` — MAX7219 7-segment driver (SPI1)

**Shared:**
- `protocol.py` — packet packing/unpacking for all 6 datagram types

## Web Dashboard

Flask app reads Pico B's USB serial → SQLite → web UI at localhost:5000.
- `app.py` — Flask routes + serial reader
- `database.py` — SQLite schema + queries
- `templates/index.html` — live dashboard UI

## Firmware Snapshots

Frozen releases in `firmware/`:
- `01-v1/` — basic (direct pin control, simple protocol)
- `02-v2/` — datagram protocol + self-test + fault handling
- `03-v3/` — C SDK drivers + integration tests

## Dual-Core Strategy

- **Core 0:** Main loop — power sensing, motor control, wireless, commands
- **Core 1:** Fault detection — IMU reading, vibration FFT, energy signature matching
