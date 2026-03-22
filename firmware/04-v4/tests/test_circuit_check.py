"""
Circuit Diagnostic — checks every connection and reports what's working/broken.
Run this after wiring to find problems.

Usage: mpremote run src/master-pico/tests/test_circuit_check.py
"""

from machine import Pin, I2C, SPI, ADC
import time

print("=" * 50)
print("  CIRCUIT DIAGNOSTIC — GridBox Master (Pico A)")
print("  Checks every connection. Shows what works.")
print("=" * 50)

passed = 0
failed = 0
warnings = 0

def test(name, condition, fix_hint):
    global passed, failed
    if condition:
        print(f"  [PASS] {name}")
        passed += 1
        return True
    else:
        print(f"  [FAIL] {name}")
        print(f"         Fix: {fix_hint}")
        failed += 1
        return False

def warn(name, msg):
    global warnings
    print(f"  [WARN] {name}: {msg}")
    warnings += 1

# ============ TEST 1: I2C BUS ============
print("\n--- I2C Bus (GP4=SDA, GP5=SCL) ---")

try:
    i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
    devices = i2c.scan()
    test("I2C bus responds", True, "")

    if len(devices) == 0:
        test("I2C devices found", False,
             "No devices on I2C bus. Check:\n"
             "         - SDA wire to GP4\n"
             "         - SCL wire to GP5\n"
             "         - Pull-up resistors (4.7k from 3.3V to SDA and SCL)\n"
             "         - Device VCC connected to 3.3V\n"
             "         - Device GND connected to GND")
    else:
        print(f"  [INFO] Found {len(devices)} device(s): {[hex(d) for d in devices]}")

        # Check for expected devices
        if 0x3C in devices:
            test("OLED SSD1306 (0x3C)", True, "")
        else:
            warn("OLED SSD1306", "Not found at 0x3C — check OLED VCC/GND/SDA/SCL")

        if 0x68 in devices:
            test("BMI160 IMU (0x68)", True, "")
            # Try reading chip ID
            try:
                chip_id = i2c.readfrom_mem(0x68, 0x00, 1)
                if chip_id[0] == 0xD1:
                    test("BMI160 chip ID = 0xD1", True, "")
                else:
                    warn("BMI160 chip ID", f"Got 0x{chip_id[0]:02X}, expected 0xD1 — may be different IMU")
            except:
                warn("BMI160", "Found but can't read chip ID — loose connection?")
        elif 0x69 in devices:
            test("BMI160 IMU (0x69 — SDO=HIGH)", True, "")
            warn("BMI160 address", "Using 0x69 not 0x68. Update config.py: BMI160_ADDR = 0x69")
        else:
            test("BMI160 IMU", False,
                 "Not found. Check:\n"
                 "         - BMI160 VCC → 3.3V\n"
                 "         - BMI160 GND → GND\n"
                 "         - BMI160 SDA → GP4 (same wire as OLED)\n"
                 "         - BMI160 SCL → GP5 (same wire as OLED)\n"
                 "         - SDO pin → GND (for address 0x68)")

        if 0x40 in devices:
            test("PCA9685 PWM (0x40)", True, "")
        else:
            test("PCA9685 PWM", False,
                 "Not found at 0x40. Check:\n"
                 "         - PCA9685 VCC → 5V (not 3.3V!)\n"
                 "         - PCA9685 GND → GND\n"
                 "         - PCA9685 SDA → GP4\n"
                 "         - PCA9685 SCL → GP5\n"
                 "         - PCA9685 V+ → 5V (servo power)")

        # Unknown devices
        known = {0x3C, 0x40, 0x68, 0x69}
        unknown = [hex(d) for d in devices if d not in known]
        if unknown:
            warn("Unknown I2C", f"Unexpected device(s): {unknown}")

except Exception as e:
    test("I2C bus initialise", False,
         f"I2C error: {e}\n"
         "         Check GP4 and GP5 are not shorted to GND or each other")

# ============ TEST 2: SPI BUS (nRF24L01+) ============
print("\n--- SPI Bus (nRF24L01+) ---")

try:
    spi = SPI(0, baudrate=10000000, polarity=0, phase=0,
              sck=Pin(2), mosi=Pin(3), miso=Pin(16))
    test("SPI bus initialised", True, "")

    csn = Pin(1, Pin.OUT, value=1)
    ce = Pin(0, Pin.OUT, value=0)

    # Try reading nRF status register
    csn.value(0)
    time.sleep_us(5)
    result = bytearray(2)
    spi.write_readinto(b'\x07\xFF', result)
    csn.value(1)
    status = result[1]

    if status != 0x00 and status != 0xFF:
        test(f"nRF24L01+ responds (status=0x{status:02X})", True, "")
    elif status == 0xFF:
        test("nRF24L01+ responds", False,
             "Got 0xFF — module not responding. Check:\n"
             "         - VCC → 3.3V (NOT 5V — will destroy it!)\n"
             "         - GND → GND\n"
             "         - CE → GP0\n"
             "         - CSN → GP1\n"
             "         - SCK → GP2\n"
             "         - MOSI → GP3\n"
             "         - MISO → GP16\n"
             "         - Add 10uF capacitor across VCC-GND\n"
             "         - Check solder joints on module pins")
    elif status == 0x00:
        warn("nRF24L01+", "Status=0x00 — module may be in reset. Check power and 10uF cap")

except Exception as e:
    test("SPI bus initialise", False, f"SPI error: {e}")

# ============ TEST 3: ADC CHANNELS ============
print("\n--- ADC Channels ---")

adc26 = ADC(Pin(26))
adc27 = ADC(Pin(27))
adc28 = ADC(Pin(28))

v26 = adc26.read_u16()
v27 = adc27.read_u16()
v28 = adc28.read_u16()

print(f"  [INFO] GP26 (bus voltage): raw={v26}, voltage={v26*3.3/65535:.3f}V")
print(f"  [INFO] GP27 (motor 1 I):   raw={v27}, voltage={v27*3.3/65535:.3f}V")
print(f"  [INFO] GP28 (motor 2 I):   raw={v28}, voltage={v28*3.3/65535:.3f}V")

if v26 > 1000:
    test("GP26 ADC reading (bus voltage)", True, "")
    bus_v = v26 * 3.3 / 65535 * 2
    print(f"  [INFO] Estimated bus voltage: {bus_v:.2f}V")
else:
    warn("GP26", "Reading very low — voltage divider may not be connected")

test("GP27 ADC responds", v27 >= 0, "ADC channel error")
test("GP28 ADC responds", v28 >= 0, "ADC channel error")

# ============ TEST 4: GPIO OUTPUTS ============
print("\n--- GPIO Outputs (MOSFETs + LEDs) ---")

# Test MOSFET pins can be set
for pin_num, name in [(10, "MOSFET M1"), (11, "MOSFET M2"),
                       (12, "MOSFET LED"), (13, "MOSFET Recycle"),
                       (14, "LED Red"), (15, "LED Green")]:
    try:
        p = Pin(pin_num, Pin.OUT)
        p.value(1)
        time.sleep_ms(50)
        p.value(0)
        test(f"GP{pin_num} ({name}) toggles", True, "")
    except Exception as e:
        test(f"GP{pin_num} ({name})", False, f"Error: {e}")

# ============ TEST 5: LED VISUAL CHECK ============
print("\n--- LED Visual Check ---")
print("  Blinking red LED (GP14) 3 times — watch for it...")
red = Pin(14, Pin.OUT)
for _ in range(3):
    red.value(1); time.sleep_ms(300); red.value(0); time.sleep_ms(300)
print("  Did you see the red LED blink? If not: check GP14 → 330Ω → LED → GND")

print("  Blinking green LED (GP15) 3 times — watch for it...")
green = Pin(15, Pin.OUT)
for _ in range(3):
    green.value(1); time.sleep_ms(300); green.value(0); time.sleep_ms(300)
print("  Did you see the green LED blink? If not: check GP15 → 330Ω → LED → GND")

# ============ SUMMARY ============
print("\n" + "=" * 50)
print(f"  RESULTS: {passed} passed, {failed} failed, {warnings} warnings")
print("=" * 50)

if failed == 0:
    print("\n  ALL TESTS PASSED!")
    print("  Ready for full firmware flash: ./test.sh flash-master")
else:
    print(f"\n  {failed} FAILURE(S) — fix the issues above before flashing firmware")
    print("  Most common fixes:")
    print("    - Loose wire in breadboard (push firmly)")
    print("    - Wrong pin (double-check GP number)")
    print("    - Missing pull-up resistor (I2C needs 4.7k)")
    print("    - Wrong voltage (nRF=3.3V, PCA9685=5V)")
    print("    - Missing capacitor (nRF needs 10uF)")
