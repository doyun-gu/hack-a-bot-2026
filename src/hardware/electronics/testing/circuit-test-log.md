# Circuit Test Log — Wooseong Jung

> Fill this in during wiring. Test after each group.
> A fault found early costs 5 minutes. A fault found at demo costs everything.

---

## Test Environment

| Field | Value |
|---|---|
| Tester | Wooseong Jung |
| Date | |
| PSU voltage set to | 12V |
| Buck converter output | V (target: 5.0V) |
| Buck-boost output | V (target: 6.0V) |
| Multimeter model | |

---

## Group 1 — Power Supply Chain

Test with multimeter BEFORE connecting any Pico.

| # | Test | Expected | Measured | Pass? |
|---|---|---|---|---|
| P1 | 5V rail (buck converter output) | 4.9–5.1V | | ☐ |
| P2 | Motor rail (buck-boost output) | 5.5–6.5V | | ☐ |
| P3 | GND rail continuity | 0Ω to PSU − | | ☐ |
| P4 | 5V rail to GND (no short) | > 1kΩ | | ☐ |
| P5 | Motor rail to GND (no short) | > 1kΩ | | ☐ |
| P6 | 5V rail to motor rail isolated | No continuity | | ☐ |

Notes:

---

## Group 2 — Pico A Power

| # | Test | Expected | Measured | Pass? |
|---|---|---|---|---|
| A1 | VSYS pin voltage | 4.9–5.1V | | ☐ |
| A2 | 3.3V pin voltage (Pico internal reg) | 3.28–3.32V | | ☐ |
| A3 | Pico A boots (onboard LED blinks) | LED blinks | | ☐ |

Notes:

---

## Group 3 — I2C Bus (BMI160 + PCA9685)

Run `test_i2c_scan.py` on Pico A via serial REPL.

```python
import machine
i2c = machine.I2C(0, sda=machine.Pin(4), scl=machine.Pin(5), freq=400000)
print(i2c.scan())
# Expected: [64, 104]  →  0x40=PCA9685, 0x68=BMI160
```

| # | Test | Expected | Result | Pass? |
|---|---|---|---|---|
| I1 | I2C scan finds PCA9685 | 0x40 (64) in list | | ☐ |
| I2 | I2C scan finds BMI160 | 0x68 (104) in list | | ☐ |
| I3 | No I2C errors (no OSError) | Clean list | | ☐ |
| I4 | SDA pull-up voltage | 3.28–3.32V (idle high) | | ☐ |
| I5 | SCL pull-up voltage | 3.28–3.32V (idle high) | | ☐ |

Notes:

---

## Group 4 — SPI / nRF24L01+ (Pico A)

| # | Test | Expected | Result | Pass? |
|---|---|---|---|---|
| S1 | nRF VCC voltage | 3.28–3.32V (**NOT 5V**) | | ☐ |
| S2 | nRF responds to STATUS register read | 0x0E (default) | | ☐ |
| S3 | Wireless ping from Pico A to Pico B | Pico B receives packet | | ☐ |

⚠️ nRF24L01+ is powered at 3.3V ONLY. 5V will permanently damage it.

Notes:

---

## Group 5 — Pico B (OLED + nRF + Joystick + Pot)

| # | Test | Expected | Result | Pass? |
|---|---|---|---|---|
| B1 | OLED displays text | Text visible | | ☐ |
| B2 | Joystick X axis (ADC GP26) | 28000–38000 at centre | | ☐ |
| B3 | Joystick Y axis (ADC GP27) | 28000–38000 at centre | | ☐ |
| B4 | Joystick button (GP22) | LOW when pressed | | ☐ |
| B5 | Potentiometer (ADC GP28) | 0–65535 across full range | | ☐ |
| B6 | nRF receives from Pico A | Packet count increments | | ☐ |

Notes:

---

## Group 6 — Motor 1 Switching (GP10 + 1Ω sense → GP27)

```python
# Run on Pico A serial REPL to test
import machine, time
m1 = machine.Pin(10, machine.Pin.OUT)
adc = machine.ADC(27)

m1.value(0)
time.sleep(0.5)
off_reading = adc.read_u16()
print(f"Motor 1 OFF: {off_reading} counts ({off_reading/65535*3300:.0f} mV)")

m1.value(1)
time.sleep(1.0)
on_reading = adc.read_u16()
print(f"Motor 1 ON:  {on_reading} counts ({on_reading/65535*3300:.0f} mV)")
print(f"Current est: {on_reading/65535*3300:.0f} mA")

m1.value(0)
```

| # | Test | Expected | Measured | Pass? |
|---|---|---|---|---|
| M1 | Motor 1 OFF — ADC GP27 reading | < 200 counts | | ☐ |
| M2 | Motor 1 ON — motor spins | Audible spin | | ☐ |
| M3 | Motor 1 ON — ADC GP27 reading | 3000–18000 counts | | ☐ |
| M4 | Motor 1 current estimate | 150–900 mA | mA | ☐ |
| M5 | GP10 LOW — motor stops immediately | Motor stops | | ☐ |
| M6 | Flyback diode in place | Visible on circuit | | ☐ |

Notes:

---

## Group 7 — Motor 2 Switching (GP11 + 1Ω sense → GP28)

Same test as Motor 1 but using GP11 and GP28.

```python
import machine, time
m2 = machine.Pin(11, machine.Pin.OUT)
adc = machine.ADC(28)

m2.value(0); time.sleep(0.5)
print(f"Motor 2 OFF: {adc.read_u16()} counts")

m2.value(1); time.sleep(1.0)
on_reading = adc.read_u16()
print(f"Motor 2 ON:  {on_reading} counts")
print(f"Current est: {on_reading/65535*3300:.0f} mA")
m2.value(0)
```

| # | Test | Expected | Measured | Pass? |
|---|---|---|---|---|
| M7 | Motor 2 OFF — ADC GP28 reading | < 200 counts | | ☐ |
| M8 | Motor 2 ON — belt moves | Belt moves | | ☐ |
| M9 | Motor 2 ON — ADC GP28 reading | 3000–18000 counts | | ☐ |
| M10 | Motor 2 current estimate | 150–900 mA | mA | ☐ |
| M11 | Load test — press belt, GP28 rises | Measurable increase | counts | ☐ |
| M12 | Release belt — GP28 returns to baseline | Returns within 3s | | ☐ |

**M11 is the key test for smart sorting.** If it fails, the sorting system will not work.

Notes:

---

## Group 8 — Bus Voltage Sensing (GP26 divider)

```python
import machine
adc_bus = machine.ADC(26)
raw = adc_bus.read_u16()
v_adc = raw / 65535 * 3.3
v_bus = v_adc * 2.0        # 10kΩ + 10kΩ divider
print(f"Bus voltage: {v_bus:.2f}V  (ADC raw: {raw})")
```

| # | Test | Expected | Measured | Pass? |
|---|---|---|---|---|
| V1 | Bus voltage (multimeter) | 5.5–6.5V | V | ☐ |
| V2 | GP26 ADC raw (Python) | 32000–40000 counts at 6V | | ☐ |
| V3 | Calculated v_bus matches multimeter | ±5% | V | ☐ |

Notes:

---

## Group 9 — LED Bank + Recycle Path

| # | Test | Expected | Result | Pass? |
|---|---|---|---|---|
| L1 | GP12 HIGH — all 4 LEDs light | All 4 on | | ☐ |
| L2 | GP12 LOW — all 4 LEDs off | All 4 off | | ☐ |
| L3 | Each LED current (multimeter in series) | 8–12 mA per LED | mA | ☐ |
| L4 | GP13 HIGH — capacitor charges | Multimeter reads ~5V on cap | V | ☐ |
| L5 | GP13 LOW — capacitor holds charge | Voltage holds for >5s | | ☐ |
| L6 | Capacitor polarity correct | (+) toward 5V rail | | ☐ |

Notes:

---

## Group 10 — Servos (via PCA9685)

```python
from pca9685 import PCA9685
import machine

i2c = machine.I2C(0, sda=machine.Pin(4), scl=machine.Pin(5))
pca = PCA9685(i2c)
pca.freq(50)

# Channel 0 = Servo 1 (fill valve), Channel 1 = Servo 2 (sort gate)
# Pulse: 1000µs = 0°, 1500µs = 90°, 2000µs = 180°
def set_servo(ch, angle):
    pulse = int(1000 + (angle / 180) * 1000)
    pca.duty(ch, int(pulse / 20000 * 4096))

set_servo(0, 0);   # Servo 1 to 0°
set_servo(1, 0);   # Servo 2 to 0°  (pass position)
```

| # | Test | Expected | Result | Pass? |
|---|---|---|---|---|
| SV1 | Servo 1 moves to 0° | At rest position | | ☐ |
| SV2 | Servo 1 moves to 90° | 90° deflection | | ☐ |
| SV3 | Servo 1 moves to 180° | Full deflection | | ☐ |
| SV4 | Servo 2 moves to 0° (pass lane) | At rest / pass position | | ☐ |
| SV5 | Servo 2 moves to 90° (sort lane) | Diverts to sort lane | | ☐ |
| SV6 | Servo 2 returns to 0° after 0.8s | Returns smoothly | | ☐ |

**SV5 + SV6 are the sort gate test — critical for smart sorting demo.**

Notes:

---

## Group 11 — Status LEDs (Pico A + Pico B)

| # | Test | Expected | Result | Pass? |
|---|---|---|---|---|
| LED1 | Pico A GP14 HIGH — red LED on | Red LED on | | ☐ |
| LED2 | Pico A GP15 HIGH — green LED on | Green LED on | | ☐ |
| LED3 | Pico B GP14 HIGH — red LED on | Red LED on | | ☐ |
| LED4 | Pico B GP15 HIGH — green LED on | Green LED on | | ☐ |

Notes:

---

## Integration Test Summary

After all groups pass, run the full system with Doyun's firmware.

| # | Test | Expected | Pass? |
|---|---|---|---|
| INT1 | Boot sequence — both Picos start | OLED shows startup message | ☐ |
| INT2 | Motors spin automatically on boot | Both motors running | ☐ |
| INT3 | Wireless link active | OLED shows telemetry data | ☐ |
| INT4 | Potentiometer changes motor speed | Speed changes visibly | ☐ |
| INT5 | Shake Motor 1 — IMU fault triggers | OLED: FAULT, motor stops | ☐ |
| INT6 | Press conveyor belt — GP28 rises, score increases | OLED shows score rising | ☐ |
| INT7 | Smart sort — place heavy object, servo fires at gate | Servo triggers at correct time | ☐ |
| INT8 | Joystick button resets fault | System recovers | ☐ |

---

## Issues Log

| Time | Issue | Fix Applied | Resolved? |
|---|---|---|---|
| | | | |
| | | | |
| | | | |
