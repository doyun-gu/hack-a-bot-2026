# Firmware Development Task — Autonomous Worker

> This file is the complete instruction set for an autonomous Claude Code session.
> It builds all GridBox firmware from scratch, commits after each module.

---

## Context

You are building firmware for **GridBox** — a smart infrastructure control system for a 24-hour hackathon (Hack-A-Bot 2026). Read these files first:

1. `CLAUDE.md` — project context, pin mapping, conventions
2. `src/firmware-dev-plan.md` — architecture, module dependency map, technical decisions
3. `docs/01-overview/gridbox-design.md` — main design doc (sections 3-5 for pin mapping + wiring + software)
4. `docs/02-electrical/power-system.md` — power flow, waste targets, fault escalation
5. `docs/02-electrical/energy-signature/energy-signature-proposal.md` — Wooseong's current sensing design
6. `docs/03-factory/factory-design/weight-sensing-sorting.md` — weight detection + sorting logic
7. `src/shared/protocol.py` — existing wireless packet format (verify and update if needed)

---

## Rules

1. Write **production-quality MicroPython** for Raspberry Pi Pico 2 (RP2350)
2. Every module must be **importable standalone** — no circular imports
3. Pin assignments come from `config.py` — **never hardcode pin numbers**
4. Use `try/except` for I2C/SPI failures — print error and continue, don't crash
5. Commit and push after completing **each numbered task** below
6. Use clear commit messages: `"Add nRF24L01+ wireless driver with TX/RX"`
7. **Don't modify docs/** — only work in `src/`
8. Test files go in `src/master-pico/tests/` or `src/slave-pico/tests/`
9. Every driver must have a `if __name__ == "__main__":` test block
10. Use constants from `config.py` — import at top of every module

---

## Pin Mapping Reference (from gridbox-design.md)

### Pico A — Grid Controller

| Pin | Function | Protocol |
|---|---|---|
| GP0 | nRF CE | GPIO |
| GP1 | nRF CSN | GPIO |
| GP2 | nRF SCK | SPI0 |
| GP3 | nRF MOSI | SPI0 |
| GP4 | I2C SDA (IMU + PCA9685) | I2C0 |
| GP5 | I2C SCL (IMU + PCA9685) | I2C0 |
| GP10 | MOSFET gate → Motor 1 | GPIO |
| GP11 | MOSFET gate → Motor 2 | GPIO |
| GP12 | MOSFET gate → LED bank | GPIO |
| GP13 | MOSFET gate → Recycle path | GPIO |
| GP14 | Status LED red | GPIO |
| GP15 | Status LED green | GPIO |
| GP16 | nRF MISO | SPI0 |
| GP26 | ADC0: bus voltage (via 10kΩ+10kΩ divider) |
| GP27 | ADC1: Motor 1 current (via 1Ω sense R) |
| GP28 | ADC2: Motor 2 current (via 1Ω sense R) |

### Pico B — SCADA Station

| Pin | Function | Protocol |
|---|---|---|
| GP0 | nRF CE | GPIO |
| GP1 | nRF CSN | GPIO |
| GP2 | nRF SCK | SPI0 |
| GP3 | nRF MOSI | SPI0 |
| GP4 | I2C SDA (OLED) | I2C0 |
| GP5 | I2C SCL (OLED) | I2C0 |
| GP14 | Status LED red | GPIO |
| GP15 | Status LED green | GPIO |
| GP16 | nRF MISO | SPI0 |
| GP22 | Joystick button (pull-up) | GPIO |
| GP26 | ADC0: Joystick X | ADC |
| GP27 | ADC1: Joystick Y | ADC |
| GP28 | ADC2: Potentiometer | ADC |

### I2C Addresses

| Device | Address |
|---|---|
| BMI160 IMU | 0x68 (or 0x69 if SDO high) |
| PCA9685 | 0x40 |
| SSD1306 OLED | 0x3C |

### Wireless Settings

| Setting | Value |
|---|---|
| Channel | 100 |
| Payload size | 32 bytes |
| Data rate | 250 kbps |
| TX address | b'NSYNT' |
| RX address | b'NSYNR' |

---

## Task List (complete in order)

### Task 1: Update config files

Update `src/master-pico/micropython/config.py` and `src/slave-pico/micropython/config.py` to match the pin mapping above exactly. Include all constants: pin numbers, I2C addresses, ADC channels, timing values, thresholds.

Commit: `"Update config.py pin mapping to match design doc"`

---

### Task 2: Wireless protocol

Verify and update `src/shared/protocol.py`. The 32-byte packet must include:
- packet_type (uint8): DATA=0x01, HEARTBEAT=0x02, ALERT=0x03, ACK=0x04, COMMAND=0x05
- roll (float): IMU roll angle
- pitch (float): IMU pitch angle
- gyro_rate (float): rotation speed
- joy_x (uint16): joystick X
- joy_y (uint16): joystick Y
- mode (uint8): current operating mode
- test_level (uint8): difficulty level
- flags (uint8): bit flags (fall_alert, button, calibrated)
- timestamp_ms (uint32): millisecond timestamp
- padding to 32 bytes

Include `pack_data()`, `pack_heartbeat()`, `pack_alert()`, `pack_command()`, `unpack()` functions.

Commit: `"Update wireless protocol with all packet types"`

---

### Task 3: nRF24L01+ wireless driver

Write `src/master-pico/micropython/nrf24l01.py` — a complete nRF24L01+ driver using SPI.

Must support:
- `__init__(spi, csn_pin, ce_pin)` — configure SPI, set channel, address, payload size
- `send(data)` — transmit a 32-byte packet, return True/False for ACK
- `recv()` — check for received packet, return data or None
- `set_channel(ch)` — change RF channel
- `set_power(level)` — set TX power (0-3)
- `available()` — check if data is waiting
- `flush_rx()`, `flush_tx()` — clear buffers

Reference: nRF24L01+ datasheet register map. Use the standard MicroPython nRF24L01 approach.

Copy the same driver to `src/slave-pico/micropython/nrf24l01.py`.

Write `src/master-pico/tests/test_wireless.py`:
- Master sends "PING" packet every second
- Prints "Sent PING, waiting for PONG..."
- If slave responds, prints "PONG received!"

Write `src/slave-pico/tests/test_wireless.py`:
- Slave listens for packets
- When "PING" received, sends back "PONG"
- Prints "Received PING, sent PONG"

Commit: `"Add nRF24L01+ wireless driver with ping-pong test"`

---

### Task 4: BMI160 IMU driver

Write `src/master-pico/micropython/bmi160.py`:
- `__init__(i2c, addr=0x68)` — init sensor, set accel range ±4g, gyro range ±500°/s, sample rate 100Hz
- `read_accel()` — return (ax, ay, az) in g units
- `read_gyro()` — return (gx, gy, gz) in °/s
- `read_all()` — return dict with all 6 values
- `accel_rms()` — return √(ax²+ay²+az²)
- `who_am_i()` — read chip ID register (should return 0xD1)

BMI160 register map:
- CHIP_ID = 0x00 (expect 0xD1)
- CMD = 0x7E (write 0x11 for accel normal, 0x15 for gyro normal)
- DATA = 0x0C-0x17 (gyro XYZ then accel XYZ, 2 bytes each, little-endian)
- ACC_CONF = 0x40, ACC_RANGE = 0x41
- GYR_CONF = 0x42, GYR_RANGE = 0x43

Write `src/master-pico/tests/test_imu.py`:
- Read and print accel + gyro + a_rms every 100ms
- Print "SHAKE DETECTED!" when a_rms > 2.0

Commit: `"Add BMI160 IMU driver with vibration detection"`

---

### Task 5: PCA9685 PWM driver

Write `src/master-pico/micropython/pca9685.py`:
- `__init__(i2c, addr=0x40)` — init PCA9685, set PWM frequency to 50Hz (for servos) or configurable
- `set_pwm(channel, on, off)` — set raw PWM values for a channel (0-15)
- `set_duty(channel, duty_percent)` — set duty cycle 0-100%
- `set_servo_angle(channel, angle)` — convert angle (0-180°) to PWM pulse (500-2500µs)
- `set_motor_speed(channel, speed_percent)` — set motor speed 0-100%
- `off(channel)` — turn off a channel
- `all_off()` — turn off all channels
- `set_frequency(freq_hz)` — change PWM frequency

PCA9685 register map:
- MODE1 = 0x00 (write 0x20 for auto-increment)
- PRE_SCALE = 0xFE (set frequency: prescale = 25MHz / (4096 * freq) - 1)
- LED0_ON_L = 0x06 (each channel: ON_L, ON_H, OFF_L, OFF_H, 4 bytes, channels at +4 offset)

Write `src/master-pico/tests/test_servo.py`:
- Sweep servo on channel 0 from 0° to 180° and back
- Print angle at each step

Write `src/master-pico/tests/test_motor.py`:
- Ramp motor on channel 2 from 0% to 100% and back down
- Print speed at each step

Commit: `"Add PCA9685 PWM driver for servos and motors"`

---

### Task 6: SSD1306 OLED driver

Write `src/slave-pico/micropython/ssd1306.py`:
- `__init__(i2c, width=128, height=64, addr=0x3C)` — init display
- `text(string, x, y, color=1)` — draw text at position
- `line(x1, y1, x2, y2, color=1)` — draw line
- `rect(x, y, w, h, color=1)` — draw rectangle outline
- `fill_rect(x, y, w, h, color=1)` — draw filled rectangle
- `pixel(x, y, color=1)` — set single pixel
- `hline(x, y, w, color=1)` — horizontal line
- `vline(x, y, h, color=1)` — vertical line
- `fill(color)` — fill entire screen
- `show()` — push framebuffer to display
- `clear()` — fill(0) + show()
- `contrast(value)` — set brightness 0-255
- `invert(on)` — invert display
- `poweroff()` / `poweron()`

Use `framebuf.FrameBuffer` internally. SSD1306 I2C protocol: send 0x00 (command) or 0x40 (data) prefix byte.

Note: There's a well-known MicroPython SSD1306 driver. You can use that as reference but write a clean version.

Write `src/slave-pico/tests/test_oled.py`:
- Display "GridBox SCADA" centered
- Draw a border rectangle
- Show mock status: "Motor 1: OK" "Motor 2: OK" "Bus: 4.9V"

Commit: `"Add SSD1306 OLED driver with text and graphics"`

---

### Task 7: ADC test

Write `src/master-pico/tests/test_adc.py`:
- Read GP26 (bus voltage via divider): actual voltage = ADC * 3.3 / 65535 * 2
- Read GP27 (motor 1 current): current_mA = ADC * 3.3 / 65535 / 1.0 * 1000
- Read GP28 (motor 2 current): same formula
- Print all three every 200ms with labels
- Calculate and print power: P = V * I for each motor

Commit: `"Add ADC test for voltage and current sensing"`

---

### Task 8: Power manager

Write `src/master-pico/micropython/power_manager.py`:
- `__init__(adc_bus_pin, adc_m1_pin, adc_m2_pin, r_sense=1.0, divider_ratio=2.0)` — init ADC channels
- `read_bus_voltage()` — return voltage in V (with divider correction)
- `read_motor_current(motor_id)` — return current in mA (motor 1 or 2)
- `read_all()` — return dict: {bus_v, m1_mA, m2_mA, m1_W, m2_W, total_W, excess_W, efficiency}
- `get_efficiency()` — return percentage (useful power / total)
- `is_overloaded()` — return True if bus voltage < threshold
- `get_excess_power()` — return watts available for rerouting
- Average 10 ADC samples per reading for noise reduction

Commit: `"Add power manager with ADC sensing and calculations"`

---

### Task 9: Motor control

Write `src/master-pico/micropython/motor_control.py`:
- `__init__(pca9685, mosfet_pins)` — takes PCA9685 instance + GPIO pin dict for MOSFETs
- `set_speed(motor_id, speed_percent)` — set motor speed 0-100% via PCA9685 PWM
- `set_servo_angle(servo_id, angle)` — set servo position 0-180°
- `emergency_stop(motor_id)` — immediately stop a motor (MOSFET off + PWM off)
- `emergency_stop_all()` — stop everything
- `enable_motor(motor_id)` — MOSFET on (GPIO high)
- `disable_motor(motor_id)` — MOSFET off (GPIO low)
- `ramp_speed(motor_id, target, duration_ms)` — gradually change speed
- LED bank control: `set_led_bank(on)`, `set_recycle(on)`

Commit: `"Add motor control with MOSFET switching and ramping"`

---

### Task 10: IMU reader (Core 1)

Write `src/master-pico/micropython/imu_reader.py`:
- Runs on Core 1 via `_thread.start_new_thread()`
- Continuously reads BMI160 at 100Hz
- Maintains rolling window of last 100 a_rms values
- Classifies vibration: HEALTHY (<1g), WARNING (1-2g), FAULT (>2g for 3s)
- Exposes: `get_status()`, `get_rms()`, `get_peak()`, `is_fault()`, `reset_fault()`
- Thread-safe: uses `_thread.allocate_lock()` for shared data

Commit: `"Add IMU reader running on Core 1 with fault classification"`

---

### Task 11: Fault manager

Write `src/master-pico/micropython/fault_manager.py`:
- State machine: NORMAL → DRIFT → WARNING → FAULT → EMERGENCY
- `update(power_data, imu_status)` — called every loop iteration, transitions states
- `get_state()` — return current state string
- `get_actions()` — return list of actions to take (shed loads, stop motors, alert)
- Load shedding: when bus voltage drops, disable loads by priority (P4 → P3 → P2)
- Rerouting: when motor stops, increase other motor speed or enable LED bank
- `reset()` — manual reset from FAULT/EMERGENCY back to NORMAL
- Integrates with motor_control for actuating the decisions

Commit: `"Add fault manager state machine with load shedding"`

---

### Task 12: Energy signature (Wooseong's design)

Write `src/master-pico/micropython/energy_signature.py`:
- Runs on Core 1 (interleaved with IMU reader, or in same thread)
- Samples ADC at 500Hz in 1-second windows (500 samples)
- `EnergySignature` class: mean_current, std_current, crossing_rate, max_deviation
- `learn_baseline(duration_s=30)` — capture healthy baseline
- `compute_signature(samples)` — calculate 4 metrics from raw samples
- `divergence_score(baseline, current)` — weighted score 0.0-1.0
  - Weights: mean=0.30, std=0.25, crossing=0.25, maxdev=0.20
  - Per-metric cap at 2.0 before weighting
- `zero_crossings(samples, mean_val)` — count crossings
- Exposes: `get_score()`, `get_signature()`, `is_anomaly()`

Commit: `"Add energy signature fault detection (Wooseong's design)"`

---

### Task 13: Sorter

Write `src/master-pico/micropython/sorter.py`:
- `__init__(motor_control, power_manager, config)` — takes motor and power instances
- `detect_item()` — returns True if current spike detected (item on belt)
- `classify_weight(current_reading)` — returns "PASS", "REJECT_HEAVY", "REJECT_LIGHT", "JAM"
- `schedule_sort(weight_class)` — calculate travel time, set timer to fire servo
- `get_stats()` — return dict: {total_items, passed, rejected, reject_rate}
- Belt timing: `travel_time = belt_length_cm / speed_cm_per_s`
- Threshold adjustable via potentiometer value from SCADA

Commit: `"Add weight-based sorter with timed servo gate"`

---

### Task 14: LED stations

Write `src/master-pico/micropython/led_stations.py`:
- 4 LEDs representing production stations
- `set_station(station_id, on)` — turn station LED on/off
- `run_sequence(weight_class)` — light LEDs in order: INTAKE→WEIGH→RESULT(green/red)→SORTED(green/red)
- Each station stays lit for a configurable duration
- Uses GPIO pins from config.py (reuse the P1-P4 load LED pins)

Commit: `"Add 4-LED production station sequence"`

---

### Task 15: Calibration

Write `src/master-pico/micropython/calibration.py`:
- `calibrate_empty()` — record empty belt/turntable current baseline (average 100 readings)
- `calibrate_reference(known_weight_g)` — record current with known weight, calculate scale factor
- `save(filename)` — save calibration to JSON file on Pico flash
- `load(filename)` — load saved calibration
- `get_baseline()`, `get_scale()` — return calibration values
- Auto-load on startup if calibration file exists

Commit: `"Add calibration routine with flash storage"`

---

### Task 16: SCADA dashboard

Write `src/slave-pico/micropython/dashboard.py`:
- 5 OLED views, joystick Y-axis scrolls between them
- Use `fill_rect()` for power bars — NOT text block characters (unicode won't render on SSD1306)
- Only ASCII chars 32-127 work for text. For rating indicators, draw small filled/empty squares
- Display is 128×64 pixels = 16 chars × 8 lines at 8×8 default font
- Each view has a `render(oled, data_dict)` method
- Dashboard class manages view index + joystick scrolling
- Helper methods: `draw_bar(oled, x, y, width, height, percent)`, `draw_divider(oled, y)`, `draw_rating(oled, x, y, score_out_of_5)`

**View 1: System Status** (pixel layout)
```
Row 0  (y=0):  "GRIDBOX    [LIVE]"          oled.text()
Row 1  (y=8):  "────────────────"           oled.hline(0, 8, 128, 1)
Row 2  (y=16): "M1:380mA 2.3W ON"          oled.text()
Row 3  (y=24): "M2:OFF    0W  --"          oled.text()
Row 4  (y=32): "S1:OPEN  S2:PASS"          oled.text()
Row 5  (y=40): "Bus:4.9V  NORMAL"          oled.text()
Row 6  (y=48): "────────────────"           oled.hline()
Row 7  (y=56): "Items:23  R:12/m"          oled.text()
```

**View 2: Power Flow** (pixel-drawn bars — this is the visual showcase)
```
Row 0  (y=0):  "POWER FLOW"                oled.text()
Row 1  (y=8):  "────────────────"           oled.hline()
Row 2  (y=16): "M1:" [████████████░░░░░] "80%"
                      fill_rect(24,16, bar_w, 6, 1) inside rect(24,16, 80, 6, 1)
Row 3  (y=24): "M2:" [████████░░░░░░░░░] "40%"
                      same pattern, bar_w = percent * 80 / 100
Row 4  (y=32): "SV:" [███░░░░░░░░░░░░░░] "15%"
Row 5  (y=40): "LD:" [█░░░░░░░░░░░░░░░░] " 5%"
Row 6  (y=48): "────────────────"           oled.hline()
Row 7  (y=56): "Tot:3.7W  Sv:69%"          + draw_rating(oled, 108, 56, 3)
                                              3 filled squares + 2 empty = ■■■□□
```

Helper for power bars:
```python
def draw_bar(oled, x, y, max_width, height, percent):
    """Draw a power bar with outline and fill."""
    fill_w = int(percent * max_width / 100)
    oled.rect(x, y, max_width, height, 1)        # outline (full range)
    oled.fill_rect(x, y, fill_w, height, 1)       # filled portion

def draw_rating(oled, x, y, score, max_score=5):
    """Draw filled/empty squares as rating."""
    for i in range(max_score):
        sx = x + i * 5
        if i < score:
            oled.fill_rect(sx, y, 3, 3, 1)        # filled = earned
        else:
            oled.rect(sx, y, 3, 3, 1)              # outline = not earned
```

**View 3: Fault Monitor**
```
Row 0  (y=0):  "FAULT MONITOR"             oled.text()
Row 1  (y=8):  "────────────────"
Row 2  (y=16): "Vib: 0.3g    OK"           show "OK"/"WARN"/"FAULT"
Row 3  (y=24): "Cur: 340mA   OK"
Row 4  (y=32): "Std:  30mA   OK"
Row 5  (y=40): "Bus: 4.9V    OK"
Row 6  (y=48): "────────────────"
Row 7  (y=56): "State:NORMAL  F:0"         fault count
```

**View 4: Production**
```
Row 0  (y=0):  "PRODUCTION"
Row 1  (y=8):  "Last: 47g   PASS"          or "REJECT"
Row 2  (y=16): "────────────────"
Row 3  (y=24): "Total:  23 items"
Row 4  (y=32): "Pass:   20 (87%)"
Row 5  (y=40): "Reject:  3 (13%)"
Row 6  (y=48): "Thresh: 30-80g"            from potentiometer
Row 7  (y=56): "Belt:5cm/s   RUN"
```

**View 5: Manual Override**
```
Row 0  (y=0):  "MANUAL OVERRIDE"
Row 1  (y=8):  "────────────────"
Row 2  (y=16): "M1:" [bar drawn] "80%"     joystick X controls this
Row 3  (y=24): "  < JoyX adjust >"
Row 4  (y=32): "M2:" [bar drawn] "60%"     joystick Y controls this
Row 5  (y=40): "  < JoyY adjust >"
Row 6  (y=48): "S1:[OPEN] btn=tog"         button toggles servo
Row 7  (y=56): "Pot:65% Btn=reset"         potentiometer value + button = fault reset
```

In Manual Override view, joystick X/Y directly controls motor speeds (values sent to Pico A via commander). Button short-press toggles servo position. Long-press (3s) resets fault state.

Commit: `"Add SCADA dashboard with 5 pixel-drawn OLED views"`

---

### Task 17: Operator input

Write `src/slave-pico/micropython/operator.py`:
- `__init__(joy_x_pin, joy_y_pin, joy_btn_pin, pot_pin)` — init ADC + button
- `read_joystick()` — return (x, y, button) with deadzone filtering
- `read_potentiometer()` — return 0-100% value
- `get_direction()` — return "UP", "DOWN", "LEFT", "RIGHT", "CENTRE", "PRESS"
- `get_threshold()` — return potentiometer mapped to weight threshold range
- Debounce button: require 50ms stable before registering press
- Long press detection (3s) for mode changes

Commit: `"Add operator input with joystick debounce and pot reading"`

---

### Task 18: Commander

Write `src/slave-pico/micropython/commander.py`:
- `__init__(nrf_driver)` — takes wireless instance
- `send_override(motor_id, speed)` — command Pico A to set motor speed
- `send_threshold(value)` — send new weight threshold to Pico A
- `send_reset()` — command fault reset
- `send_mode(mode)` — switch operating mode
- `send_emergency_stop()` — stop everything
- Uses COMMAND packet type from protocol.py

Commit: `"Add SCADA commander for bidirectional wireless control"`

---

### Task 19: Master main.py

Write `src/master-pico/micropython/main.py` — full integration:
- Init all hardware (I2C, SPI, ADC, GPIO)
- Start Core 1 thread (imu_reader + energy_signature)
- Main loop at 100Hz:
  1. Read power manager (ADC values)
  2. Read wireless commands from SCADA
  3. Run fault manager (state machine)
  4. Run sorter (weight detection + timing)
  5. Update LED stations
  6. Execute fault manager actions (speed changes, load shedding)
  7. Pack and send telemetry via wireless
  8. Print serial JSON for web dashboard
- Handle graceful shutdown on KeyboardInterrupt
- Startup calibration if no saved calibration exists

Commit: `"Add master Pico main.py — full integrated control loop"`

---

### Task 20: Slave main.py

Write `src/slave-pico/micropython/main.py` — full integration:
- Init all hardware (I2C for OLED, SPI for nRF, ADC for joystick + pot)
- Main loop:
  1. Receive wireless packet from Pico A
  2. Unpack telemetry data
  3. Read operator input (joystick + pot)
  4. Update dashboard (current view with live data)
  5. If operator input changed → send command to Pico A
  6. Update status LEDs
  7. Handle view switching (joystick up/down)
- Heartbeat timeout: if no packet for 3s → display "LINK LOST"

Commit: `"Add slave Pico main.py — SCADA display and control loop"`

---

### Task 21: Web dashboard update

Update `src/web/app.py` and `src/web/templates/index.html`:
- Parse the JSON serial output from master Pico main.py
- Display: bus voltage, motor currents, power per branch, fault state, production stats
- Live updating graphs (last 60 seconds of data)
- Colour-coded: green = normal, yellow = warning, red = fault

Commit: `"Update web dashboard to parse GridBox serial data"`

---

## After All Tasks

Final commit: `"GridBox firmware complete — all 21 modules implemented"`

Then update `src/README.md` to reflect the actual implemented modules (not just planned).
