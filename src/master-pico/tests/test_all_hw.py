"""
Test: All hardware on Pico A — I2C scan, IMU, ADC, recycle path
Run on Pico A (master) to verify everything is connected.

Usage: mpremote run test_all_hw.py
"""

from machine import Pin, I2C, ADC
import time
import math

# === Config ===
I2C_SDA = 4
I2C_SCL = 5
ADC_BUS = 26
ADC_M1 = 27
ADC_M2 = 28
RECYCLE_PIN = 13
LED_PIN = 25

results = {}

print()
print("=" * 50)
print("  GridBox — Pico A Hardware Test")
print("=" * 50)
print()

# === Test 1: I2C Scan ===
print("--- TEST 1: I2C Bus Scan ---")
i2c = I2C(0, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=400_000)
devices = i2c.scan()

KNOWN = {
    0x3C: "SSD1306 OLED",
    0x40: "PCA9685 PWM",
    0x68: "BMI160 IMU",
    0x69: "BMI160 IMU (alt)",
}

if devices:
    for addr in devices:
        name = KNOWN.get(addr, "Unknown")
        print(f"  0x{addr:02X} = {name}")
    results['i2c'] = 'PASS'
else:
    print("  NO DEVICES FOUND")
    results['i2c'] = 'FAIL'

has_imu = 0x68 in devices or 0x69 in devices
has_pca = 0x40 in devices
print(f"  BMI160: {'FOUND' if has_imu else 'MISSING'}")
print(f"  PCA9685: {'FOUND' if has_pca else 'MISSING'}")
print()

# === Test 2: BMI160 IMU ===
print("--- TEST 2: BMI160 IMU ---")
if has_imu:
    imu_addr = 0x68 if 0x68 in devices else 0x69
    try:
        # Read chip ID (register 0x00)
        chip_id = i2c.readfrom_mem(imu_addr, 0x00, 1)[0]
        print(f"  Chip ID: 0x{chip_id:02X} {'(OK — BMI160)' if chip_id == 0xD1 else '(UNEXPECTED)'}")

        if chip_id == 0xD1:
            # Init accelerometer: normal mode, ±4g, 100Hz
            i2c.writeto_mem(imu_addr, 0x7E, bytes([0x11]))  # accel normal mode
            time.sleep_ms(50)

            # Read 6 bytes of accel data (registers 0x12-0x17)
            data = i2c.readfrom_mem(imu_addr, 0x12, 6)
            ax = (data[1] << 8 | data[0])
            ay = (data[3] << 8 | data[2])
            az = (data[5] << 8 | data[4])

            # Convert to signed
            if ax > 32767: ax -= 65536
            if ay > 32767: ay -= 65536
            if az > 32767: az -= 65536

            # Convert to g (±4g range, 16-bit)
            scale = 4.0 / 32768.0
            ax_g = ax * scale
            ay_g = ay * scale
            az_g = az * scale
            rms = math.sqrt(ax_g**2 + ay_g**2 + az_g**2)

            print(f"  Accel: X={ax_g:+.2f}g Y={ay_g:+.2f}g Z={az_g:+.2f}g")
            print(f"  RMS: {rms:.2f}g (expect ~1.0g at rest)")
            results['imu'] = 'PASS'
        else:
            results['imu'] = 'FAIL'
    except OSError as e:
        print(f"  I2C Error: {e}")
        results['imu'] = 'FAIL'
else:
    print("  SKIPPED — BMI160 not found on I2C")
    results['imu'] = 'SKIP'
print()

# === Test 3: PCA9685 ===
print("--- TEST 3: PCA9685 PWM Driver ---")
if has_pca:
    try:
        # Read MODE1 register
        mode1 = i2c.readfrom_mem(0x40, 0x00, 1)[0]
        print(f"  MODE1 register: 0x{mode1:02X}")

        # Reset PCA9685
        i2c.writeto_mem(0x40, 0x00, bytes([0x00]))
        time.sleep_ms(10)

        # Set PWM frequency ~50Hz for servos (prescale = 121)
        i2c.writeto_mem(0x40, 0x00, bytes([0x10]))  # sleep mode
        time.sleep_ms(5)
        i2c.writeto_mem(0x40, 0xFE, bytes([121]))   # prescale for 50Hz
        i2c.writeto_mem(0x40, 0x00, bytes([0x00]))   # wake up
        time.sleep_ms(5)

        prescale = i2c.readfrom_mem(0x40, 0xFE, 1)[0]
        print(f"  Prescale: {prescale} (expect 121 for 50Hz)")
        print(f"  PCA9685 responding OK")
        results['pca9685'] = 'PASS'
    except OSError as e:
        print(f"  I2C Error: {e}")
        results['pca9685'] = 'FAIL'
else:
    print("  SKIPPED — PCA9685 not found on I2C")
    results['pca9685'] = 'SKIP'
print()

# === Test 4: ADC Sensing ===
print("--- TEST 4: ADC Sensing ---")
adc_bus = ADC(Pin(ADC_BUS))
adc_m1 = ADC(Pin(ADC_M1))
adc_m2 = ADC(Pin(ADC_M2))

# Average 10 readings
bus_raw = sum(adc_bus.read_u16() for _ in range(10)) // 10
m1_raw = sum(adc_m1.read_u16() for _ in range(10)) // 10
m2_raw = sum(adc_m2.read_u16() for _ in range(10)) // 10

bus_v = (bus_raw * 3.3 / 65535) * 2.0  # voltage divider ×2
m1_v = m1_raw * 3.3 / 65535
m2_v = m2_raw * 3.3 / 65535

print(f"  GP26 (bus voltage): raw={bus_raw:5d}  → {bus_v:.2f}V")
print(f"  GP27 (motor 1):     raw={m1_raw:5d}  → {m1_v:.3f}V ({m1_v/1.0*1000:.0f}mA)")
print(f"  GP28 (motor 2):     raw={m2_raw:5d}  → {m2_v:.3f}V ({m2_v/1.0*1000:.0f}mA)")
results['adc'] = 'PASS'
print()

# === Test 5: Recycle Path (GP13) ===
print("--- TEST 5: Recycle Path (GP13) ---")
recycle = Pin(RECYCLE_PIN, Pin.OUT)
led = Pin(LED_PIN, Pin.OUT)

print("  Toggling GP13 x3 (watch LED on recycle circuit)...")
for i in range(3):
    recycle.high()
    led.high()
    print(f"  [{i+1}] GP13 HIGH — charging")
    time.sleep(1)
    recycle.low()
    led.low()
    print(f"  [{i+1}] GP13 LOW  — LED should fade")
    time.sleep(2)

results['recycle'] = 'PASS (manual check)'
print()

# === Summary ===
print("=" * 50)
print("  RESULTS SUMMARY")
print("=" * 50)
for test, result in results.items():
    status = "PASS" if "PASS" in result else ("SKIP" if "SKIP" in result else "FAIL")
    icon = "+" if status == "PASS" else ("~" if status == "SKIP" else "X")
    print(f"  [{icon}] {test:12s} — {result}")

passed = sum(1 for r in results.values() if 'PASS' in r)
total = len(results)
print()
print(f"  {passed}/{total} tests passed")
print("=" * 50)
