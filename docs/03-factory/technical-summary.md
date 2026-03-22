# GridBox — Technical Summary

> Quick reference of every technical feature, protocol, and EEE theory used in the project.

---

## Communication Protocols

| Protocol | Bus | Devices | Speed | Notes |
|---|---|---|---|---|
| **SPI0** | GP2/GP3/GP16 | nRF24L01+ PA+LNA | 10MHz | Both Picos, wireless 2.4GHz link |
| **SPI1** | GP10/GP11/GP13 | MAX7219 8-digit 7-seg | 10MHz | Pico B only, status display |
| **I2C0** | GP4/GP5 | BMI160 (0x68) + PCA9685 (0x40) | 400kHz | Pico A, shared bus with pull-ups |
| **I2C0** | GP4/GP5 | SSD1306 OLED (0x3C) | 400kHz | Pico B, dashboard display |
| **UART/USB** | — | Mac serial | 115200 | Debug + web dashboard data |

---

## Wireless Protocol

| Feature | Detail |
|---|---|
| **Radio** | nRF24L01+ PA+LNA, 2.4GHz ISM band |
| **Channel** | 100 (2.500GHz) |
| **Data rate** | 250kbps |
| **Payload** | 32 bytes per packet |
| **Direction** | Bidirectional (A→B telemetry, B→A commands) |
| **Error rate** | 0% (200+ packets tested) |
| **Addresses** | TX: `NSYNT`, RX: `NSYNR` (swapped on slave) |

### 6 Datagram Types

| Type | Direction | Contents |
|---|---|---|
| **POWER** | A → B | Bus voltage, motor currents, total power, efficiency % |
| **STATUS** | A → B | System state, fault source, IMU data, mode, uptime |
| **PRODUCTION** | A → B | Items processed, pass/reject count, belt speed |
| **HEARTBEAT** | A → B | Timestamp, CPU load, wireless reliability |
| **ALERT** | A → B | Fault code, severity, affected subsystem |
| **COMMAND** | B → A | Motor speed, servo position, mode switch, e-stop |

### Packet Rotation

```
POWER → STATUS → POWER → PRODUCTION → POWER → STATUS → POWER → HEARTBEAT → repeat
(ALERT breaks rotation when fault detected)
```

---

## Sensing

### ADC Power Sensing (3 channels)

| Channel | Pin | Measurement | Circuit | Formula |
|---|---|---|---|---|
| ADC0 | GP26 | Bus voltage | 10kΩ + 10kΩ voltage divider | V_bus = V_adc × 2 |
| ADC1 | GP27 | Motor 1 current | 1Ω sense resistor | I = V_sense / R_sense |
| ADC2 | GP28 | Motor 2 current | 1Ω sense resistor | I = V_sense / R_sense |

- **Resolution:** 16-bit (65,536 steps)
- **Reference:** 3.3V
- **Averaging:** 10 samples per reading (noise reduction)
- **Power calculation:** P = V × I (per branch, summed for total)

### BMI160 IMU (6-axis)

| Feature | Detail |
|---|---|
| **Accelerometer** | ±4g range, 100Hz sample rate |
| **Gyroscope** | ±500°/s range |
| **Vibration RMS** | a_rms = √(ax² + ay² + az²) |
| **Fault threshold** | > 2.0g = WARNING, sustained = FAULT |
| **Classification** | ISO 10816 vibration severity |
| **I2C address** | 0x68 (SDO to GND) |
| **Chip ID** | 0xD1 |

**What one BMI160 detects (£2 replaces £18,000 equipment):**

| Detection | Method | Replaces |
|---|---|---|
| Bearing wear | Vibration RMS trend | £10K vibration analyser |
| Motor RPM | Gyroscope rotation | £200 tachometer |
| Pump cavitation | High-freq vibration spikes | £5K flow sensor |
| Conveyor jam | Sudden acceleration stop | £500 proximity sensor |
| Valve position | Tilt angle | £300 position sensor |
| Belt tension | Vibration frequency shift | £800 tension monitor |
| Equipment fall | Free-fall detection (RMS → 0) | £200 tilt switch |
| Door/hatch open | Orientation change | £100 reed switch |
| Earthquake/impact | All-axis spike | £500 seismic sensor |
| Motor imbalance | Periodic vibration pattern | £1K balance analyser |

---

## Control

### PCA9685 PWM Driver

| Feature | Detail |
|---|---|
| **Channels** | 16 (using 4: CH0-CH3) |
| **Resolution** | 12-bit (4,096 steps per channel) |
| **Frequency** | 50Hz (servos), adjustable |
| **I2C address** | 0x40 |
| **VCC** | 3.3V (logic, matches Pico I2C) |
| **V+** | 5V (output power for servos/gates) |

| Channel | Connected to | Purpose |
|---|---|---|
| CH0 | Servo 1 (MG90S) | Fill valve open/close |
| CH1 | Servo 2 (MG90S) | Sort gate pass/reject |
| CH2 | Motor driver IN1/ENA | Motor 1 speed (pump) |
| CH3 | Motor driver IN3/ENB | Motor 2 speed (conveyor) |

### Motor Driver Module

| Feature | Detail |
|---|---|
| **Input** | PCA9685 CH2/CH3 PWM signals |
| **Output** | 2x DC motors (bidirectional) |
| **Logic power** | 5V from logic rail |
| **Motor power** | 6-9V from buck-boost converter |

### NPN Transistor Switching (2N2222)

| Feature | Detail |
|---|---|
| **Transistor** | 2N2222 NPN (TO-92 package) |
| **Pin 1 (E)** | Emitter → capacitor (+) and LED |
| **Pin 2 (B)** | Base → 1kΩ → GP13/GP22 |
| **Pin 3 (C)** | Collector → 5V rail |
| **Base current** | ~2.6mA (3.3V - 0.7V) / 1kΩ |
| **Purpose** | Energy recycle path switch |

### Recycle Path Circuit

```
5V → Collector (Pin 3) → Emitter (Pin 1) → Cap(+) → LED → 150Ω → GND
                                              │
GP13 → 1kΩ → Base (Pin 2)                 Cap(-) → GND
```

- **GP13 HIGH:** Transistor ON → cap charges from 5V → LED dim
- **GP13 LOW:** Transistor OFF → 5V disconnected → cap discharges through LED → **LED fades**
- **Capacitance:** 200µF (parallel combination)
- **Energy stored:** E = ½CV² = ½ × 200µF × 5² = 2.5mJ

---

## Dual-Core Architecture (RP2350)

| Core | Function | Rate |
|---|---|---|
| **Core 0** | Main control loop: ADC → KCL → routing → PWM → wireless TX | 100Hz (10ms) |
| **Core 1** | Fault detection: IMU read → RMS → ISO 10816 → alert | Continuous |

---

## Fault Detection System (F1-F6)

| Code | Fault | Detection | Response |
|---|---|---|---|
| F1 | Vibration | IMU RMS > 2g sustained | Stop motor, wireless ALERT |
| F2 | Overcurrent | ADC > 800mA on any branch | Reduce PWM, shed loads |
| F3 | Undervoltage | Bus voltage < 4.2V | Shed non-critical loads |
| F4 | Intermittent | Current fluctuation pattern | Log + warning |
| F5 | Jam | Motor current spike + no motion | Stop motor, reverse briefly |
| F6 | Supply fault | Bus voltage < 3.8V | Emergency shutdown |

### State Machine

```
NORMAL → DRIFT → WARNING → FAULT → EMERGENCY
   ↑                                    │
   └──── AUTO RECOVERY (if safe) ───────┘
```

---

## EEE Theory Applied

### 1. Affinity Laws (Fan/Pump)
```
P ∝ n³
```
- 20% speed reduction → 49% power saving
- Applied via PCA9685 PWM duty cycle control
- Demonstrated in smart vs dumb mode comparison

### 2. Kirchhoff's Current Law (KCL)
```
ΣI_in = ΣI_out at every node
```
- Verified every 10ms via ADC readings
- If currents don't balance → fault detected
- Applied to power bus with multiple branches

### 3. Voltage Divider
```
V_out = V_in × R2 / (R1 + R2)
```
- 10kΩ + 10kΩ → halves bus voltage for safe ADC reading
- 12V bus → 6V at divider → 3.3V ADC range (with safety margin)

### 4. Current Sensing
```
I = V_sense / R_sense
```
- 1Ω sense resistors on each motor branch
- ADC reads voltage drop across resistor
- Gives real-time current per motor

### 5. PWM Motor Control
```
V_eff = D × V_supply
```
- PCA9685 provides 12-bit duty cycle (0-4095)
- D = 0.65 → motor runs at 65% speed
- Combined with Affinity Laws for energy optimisation

### 6. ISO 10816 Vibration Classification

| Class | RMS (mm/s) | Our threshold (g) | Status |
|---|---|---|---|
| Good | < 1.8 | < 1.0 | NORMAL |
| Acceptable | 1.8 - 4.5 | 1.0 - 2.0 | DRIFT |
| Warning | 4.5 - 11.2 | 2.0 - 4.0 | WARNING |
| Dangerous | > 11.2 | > 4.0 | FAULT |

### 7. Capacitor Energy Storage
```
E = ½CV²
```
- 200µF × 5V² = 2.5mJ stored energy
- Demonstrates energy recycling principle at bench scale
- Production: replace with supercapacitor bank (same firmware)

---

## Software Stack

| Layer | Technology | Files |
|---|---|---|
| **Development firmware** | MicroPython | 28 modules (16 master + 12 slave) |
| **Production firmware** | C/C++ Pico SDK | 10 files (drivers + test) |
| **Shared protocol** | MicroPython | 1 file (6 datagram types) |
| **Web dashboard** | Flask + SQLite | Real-time charts, fault log, history |
| **Test suite** | MicroPython | 35+ test scripts |
| **Flash tool** | Bash | 12 commands (flash, test, persist) |

---

## Bill of Materials

| Component | Qty | Cost | Purpose |
|---|---|---|---|
| Raspberry Pi Pico 2 | 2 | £8 | Controllers (RP2350, dual-core ARM Cortex-M33) |
| nRF24L01+ PA+LNA | 2 | £3 | 2.4GHz wireless link |
| BMI160 IMU | 1 | £2 | 6-axis vibration/fault detection |
| PCA9685 | 1 | £1 | 16-ch PWM driver |
| Motor driver module | 1 | £1 | DC motor switching |
| **Total** | | **~£15** | **vs £162,000 industrial SCADA** |

---

## Key Metrics

| Metric | Value |
|---|---|
| Control loop | 100Hz (10ms) |
| Wireless rate | 250kbps, 0% error |
| PWM resolution | 12-bit (4,096 steps) |
| ADC resolution | 16-bit (65,536 steps) |
| Fault response | < 100ms |
| IMU sample rate | 100Hz |
| Packet size | 32 bytes |
| Protocol types | 6 (bidirectional) |
| Firmware modules | 28 MicroPython + 10 C SDK |
| Test scripts | 35+ |
| Wiring progress | 77% (48/66 wires) |
