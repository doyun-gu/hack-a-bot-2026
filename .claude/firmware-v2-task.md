# Firmware v2 Improvements — Autonomous Worker Task

> Read CLAUDE.md for project context. Apply these 4 improvements to the source code in src/, then snapshot to firmware/02-v2/.

---

## Rules

1. Edit files in `src/master-pico/micropython/` and `src/slave-pico/micropython/` and `src/shared/`
2. Commit and push after each completed task
3. After all tasks done, copy the updated code to `firmware/02-v2/` with a README
4. Don't modify `firmware/01-v1/` — that's a frozen snapshot
5. Don't modify `docs/` — only work in `src/` and `firmware/`

---

## Task 1: Multi-Type Datagram Protocol

Read `docs/02-electrical/datagram-design.md` for the full specification.

Update `src/shared/protocol.py` to implement 6 packet types with rotation:

**Packet types:**
- `PKT_POWER = 0x01` — bus voltage (uint16 mV), motor currents (uint16 mA × 2), motor power (uint16 mW × 2), total power, excess, motor speeds (uint8 % × 2), servo angles (uint8 × 2), efficiency, LED state, MOSFET state
- `PKT_STATUS = 0x02` — system state (uint8 enum), fault source, IMU rms (uint16 mg), IMU state, energy signature score (uint16 ×100), ES classification, ES mean/std current, shedding level, mode, uptime (uint32), faults count, reroute active
- `PKT_PRODUCTION = 0x03` — total/passed/rejected items (uint16), reject rate (uint8 %), last weight (uint16 mg), last result, belt speed, thresholds, station active, sorting active
- `PKT_HEARTBEAT = 0x04` — timestamp (uint32), uptime (uint32), core load estimates
- `PKT_ALERT = 0x05` — alert level, source, timestamp, IMU/current/voltage at fault time, action taken
- `PKT_COMMAND = 0x10` — cmd type, target device, value (uint16), mode

Each packet is exactly 32 bytes with a 2-byte header (type + sequence number).

Add pack/unpack functions for each type: `pack_power()`, `unpack_power()`, `pack_status()`, etc.

Add rotation schedule:
```python
ROTATION = [PKT_POWER, PKT_STATUS, PKT_POWER, PKT_PRODUCTION,
            PKT_POWER, PKT_STATUS, PKT_POWER, PKT_HEARTBEAT]
```

Update `src/master-pico/micropython/main.py` to use the rotation when sending packets.
Update `src/slave-pico/micropython/main.py` to handle all packet types when receiving.

Commit: `"Implement multi-type datagram protocol with 6 packet types"`

---

## Task 2: Startup Self-Test with LED Blink Error Codes

Read `docs/02-electrical/debug-system.md` for the full specification.

Add to `src/master-pico/micropython/main.py`:

Before entering the main loop, run a self-test that checks each component:

```python
def blink_error(led_pin, code, repeat=3):
    for _ in range(repeat):
        for _ in range(code):
            led_pin.value(1)
            time.sleep_ms(150)
            led_pin.value(0)
            time.sleep_ms(150)
        time.sleep_ms(800)

def startup_selftest(hw):
    failures = []
    # Test I2C bus
    if hw['i2c'] is None:
        failures.append(('I2C', 1))
    else:
        devices = hw['i2c'].scan()
        if config.BMI160_ADDR not in devices:
            failures.append(('IMU', 3))
        if config.PCA9685_ADDR not in devices:
            failures.append(('PCA', 4))
    # Test nRF
    if hw['nrf'] is None:
        failures.append(('NRF', 5))
    # Test ADC
    adc_val = ADC(Pin(config.ADC_BUS_VOLTAGE)).read_u16()
    if adc_val < 100:
        failures.append(('ADC', 6))
    return failures
```

If any failures, blink the error code on the red LED and print the error to serial. Continue running with degraded functionality (skip the broken component).

Also add to slave Pico main.py — check I2C (OLED), SPI (nRF).

Blink code reference:
- 1 = I2C bus fail
- 2 = SPI bus fail
- 3 = IMU not found
- 4 = PCA9685 not found
- 5 = nRF24L01+ fail
- 6 = ADC readings invalid
- 7 = Motor stall detected
- 8 = OLED not found

Commit: `"Add startup self-test with LED blink error codes"`

---

## Task 3: Dumb vs Smart A/B Comparison Mode

Add `MODE_DUMB = 2` support to master main.py.

When mode is DUMB:
- All motors run at 100% PWM
- All LEDs ON
- No fault detection
- No load shedding
- No sorting
- Just measure total power consumption via ADC

When mode is NORMAL (smart):
- Normal intelligent control
- Measure total power consumption

Add a comparison function:
```python
def run_comparison(power_mgr, motor_ctrl, duration_s=10):
    """Run dumb mode, then smart mode, calculate savings."""
    # Dumb mode
    motor_ctrl.set_speed(1, 100)
    motor_ctrl.set_speed(2, 100)
    dumb_readings = []
    for _ in range(duration_s * 10):
        dumb_readings.append(power_mgr.read_all()['total_W'])
        time.sleep_ms(100)
    dumb_avg = sum(dumb_readings) / len(dumb_readings)

    # Smart mode
    motor_ctrl.set_speed(1, 60)
    motor_ctrl.set_speed(2, 40)
    smart_readings = []
    for _ in range(duration_s * 10):
        smart_readings.append(power_mgr.read_all()['total_W'])
        time.sleep_ms(100)
    smart_avg = sum(smart_readings) / len(smart_readings)

    savings = (1 - smart_avg / max(dumb_avg, 0.01)) * 100
    return dumb_avg, smart_avg, savings
```

Add a COMPARISON view to the slave OLED dashboard showing the dumb vs smart results.

The comparison can be triggered by a COMMAND from SCADA (joystick long-press in a specific view).

Commit: `"Add dumb vs smart A/B comparison mode"`

---

## Task 4: Code Quality Review + Fixes

Review all modules in `src/master-pico/micropython/` and `src/slave-pico/micropython/` for:

1. **Missing error handling** — any I2C/SPI call without try/except? Fix it
2. **Hardcoded pin numbers** — any pin number not from config.py? Fix it
3. **Import errors** — any module importing something that doesn't exist? Fix it
4. **Thread safety** — imu_reader.py uses _thread. Are shared variables protected with locks? Fix if not
5. **Memory leaks** — any lists that grow forever without bounds? Add maxlen or clearing
6. **Division by zero** — any division without checking denominator? Add guards
7. **Type mismatches** — ADC returns uint16, but protocol expects float in some places? Fix packing

Fix all issues found. Document what was fixed in the commit message.

Commit: `"Code quality review — fix error handling, thread safety, type issues"`

---

## Task 5: Create v2 Snapshot

After all tasks above are done:

1. Create `firmware/02-v2/` directory with `master/`, `slave/`, `shared/` subfolders
2. Copy all updated files from `src/` into `firmware/02-v2/`
3. Write `firmware/02-v2/README.md` listing:
   - All features from v1 PLUS the new v2 features
   - What changed from v1
   - Flash instructions
   - Known limitations
   - What v3 should include
4. Update `firmware/README.md` table to show v2 status

Commit: `"Create firmware v2 snapshot — datagram + self-test + comparison + fixes"`
