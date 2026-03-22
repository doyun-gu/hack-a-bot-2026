"""
GridBox — System Integration Test (Pico A Master)
Tests each component one by one, sends status wirelessly to Pico B.
Pico B shows results on MAX7219 7-segment display.

Test order:
  1. nRF wireless link
  2. I2C scan (IMU + PCA9685)
  3. BMI160 IMU read
  4. PCA9685 init
  5. Motor 1 ON/OFF
  6. Motor 2 ON/OFF
  7. Servo 1 sweep
  8. Servo 2 sweep
  9. Recycle LED blink
  10. IMU shake detection
  11. Full telemetry stream

Usage:
  Pico B: mpremote run src/demo/test_system_slave.py
  Pico A: mpremote run src/demo/test_system.py
"""

from machine import Pin, SPI, I2C
import struct
import time
import math

# ============ PINS ============
SPI_SCK = 2
SPI_MOSI = 3
SPI_MISO = 16
NRF_CE = 0
NRF_CSN = 1
I2C_SDA = 4
I2C_SCL = 5
RECYCLE_PIN = 13
LED_PIN = 25

NRF_CHANNEL = 100
TX_ADDR = b'NSYNT'
RX_ADDR = b'NSYNR'

BMI160_ADDR = 0x68
PCA9685_ADDR = 0x40

# Message types for display
MSG_TEXT = 0x01      # 8-char text for MAX7219
MSG_RESULT = 0x02    # test result: pass/fail


# ============ nRF DRIVER (TX) ============
class NRF:
    def __init__(self):
        self.spi = SPI(0, baudrate=10_000_000, polarity=0, phase=0,
                       sck=Pin(SPI_SCK), mosi=Pin(SPI_MOSI), miso=Pin(SPI_MISO))
        self.ce = Pin(NRF_CE, Pin.OUT, value=0)
        self.csn = Pin(NRF_CSN, Pin.OUT, value=1)
        self._init()

    def _w(self, reg, val):
        self.csn(0)
        self.spi.readinto(bytearray(1), 0x20 | reg)
        self.spi.readinto(bytearray(1), val)
        self.csn(1)

    def _wb(self, reg, data):
        self.csn(0)
        self.spi.readinto(bytearray(1), 0x20 | reg)
        self.spi.write(data)
        self.csn(1)

    def _r(self, reg):
        self.csn(0)
        self.spi.readinto(bytearray(1), reg)
        r = bytearray(1)
        self.spi.readinto(r)
        self.csn(1)
        return r[0]

    def _init(self):
        time.sleep_ms(100)
        self._w(0x00, 0x0C)
        self._w(0x01, 0x00)
        self._w(0x02, 0x03)
        self._w(0x03, 0x03)
        self._w(0x04, 0x00)
        self._w(0x05, NRF_CHANNEL)
        self._w(0x06, 0x26)
        self._w(0x11, 32)
        self._w(0x12, 32)
        self._wb(0x10, TX_ADDR)
        self._wb(0x0A, TX_ADDR)
        self._wb(0x0B, RX_ADDR)
        self.csn(0)
        self.spi.readinto(bytearray(1), 0xE1)
        self.csn(1)
        self._w(0x07, 0x70)

    def send(self, data):
        buf = bytearray(32)
        buf[:len(data)] = data[:32]
        self.ce(0)
        self._w(0x00, 0x0E)
        time.sleep_ms(2)
        self.csn(0)
        self.spi.readinto(bytearray(1), 0xE1)
        self.csn(1)
        self.csn(0)
        self.spi.readinto(bytearray(1), 0xA0)
        self.spi.write(buf)
        self.csn(1)
        self.ce(1)
        time.sleep_ms(1)
        self.ce(0)
        self._w(0x07, 0x70)

    def send_text(self, text):
        """Send text to display on MAX7219."""
        msg = bytearray(32)
        msg[0] = MSG_TEXT
        t = text.encode()[:8]
        msg[1] = len(t)
        msg[2:2+len(t)] = t
        self.send(msg)

    def send_result(self, test_num, passed, text=""):
        """Send test result."""
        msg = bytearray(32)
        msg[0] = MSG_RESULT
        msg[1] = test_num
        msg[2] = 1 if passed else 0
        t = text.encode()[:8]
        msg[3] = len(t)
        msg[4:4+len(t)] = t
        self.send(msg)


# ============ TEST FUNCTIONS ============

def test_nrf(nrf):
    """Test 1: nRF wireless link."""
    print("[TEST 1] nRF wireless link...")
    status = nrf._r(0x07)
    ok = status in (0x0E, 0x0F)
    print(f"  Status: 0x{status:02X} {'PASS' if ok else 'FAIL'}")
    nrf.send_text("nRF  OK" if ok else "nRF FAIL")
    time.sleep(1)
    nrf.send_result(1, ok, "nRF")
    return ok


def test_i2c_scan(i2c, nrf):
    """Test 2: I2C bus scan."""
    print("[TEST 2] I2C scan...")
    devices = i2c.scan()
    found_imu = BMI160_ADDR in devices
    found_pca = PCA9685_ADDR in devices
    print(f"  Devices: {['0x{:02X}'.format(d) for d in devices]}")
    print(f"  IMU: {'FOUND' if found_imu else 'MISSING'}")
    print(f"  PCA: {'FOUND' if found_pca else 'MISSING'}")

    if found_imu and found_pca:
        nrf.send_text("I2C 2 OK")
    elif found_imu:
        nrf.send_text("I2C IMU")
    elif found_pca:
        nrf.send_text("I2C PCA")
    else:
        nrf.send_text("I2C NONE")
    time.sleep(1)
    nrf.send_result(2, found_imu and found_pca, "I2C")
    return found_imu, found_pca


def test_imu(i2c, nrf):
    """Test 3: BMI160 IMU read."""
    print("[TEST 3] BMI160 IMU...")
    try:
        chip = i2c.readfrom_mem(BMI160_ADDR, 0x00, 1)[0]
        if chip != 0xD1:
            print(f"  Wrong chip: 0x{chip:02X}")
            nrf.send_text("IMU BAd")
            nrf.send_result(3, False, "IMU")
            return False

        i2c.writeto_mem(BMI160_ADDR, 0x7E, bytes([0x11]))
        time.sleep_ms(50)
        data = i2c.readfrom_mem(BMI160_ADDR, 0x12, 6)
        ax = (data[1] << 8 | data[0])
        ay = (data[3] << 8 | data[2])
        az = (data[5] << 8 | data[4])
        if ax > 32767: ax -= 65536
        if ay > 32767: ay -= 65536
        if az > 32767: az -= 65536
        s = 4.0 / 32768.0
        rms = math.sqrt((ax*s)**2 + (ay*s)**2 + (az*s)**2)
        print(f"  RMS: {rms:.2f}g (expect ~1.0g at rest)")
        nrf.send_text(f"IMU {rms:.1f}G")
        time.sleep(1)
        nrf.send_result(3, True, "IMU")
        return True
    except OSError as e:
        print(f"  Error: {e}")
        nrf.send_text("IMU ERR")
        nrf.send_result(3, False, "IMU")
        return False


def test_pca9685(i2c, nrf):
    """Test 4: PCA9685 init."""
    print("[TEST 4] PCA9685 PWM driver...")
    try:
        i2c.writeto_mem(PCA9685_ADDR, 0x00, bytes([0x00]))
        time.sleep_ms(10)
        i2c.writeto_mem(PCA9685_ADDR, 0x00, bytes([0x10]))
        time.sleep_ms(5)
        i2c.writeto_mem(PCA9685_ADDR, 0xFE, bytes([121]))  # 50Hz
        i2c.writeto_mem(PCA9685_ADDR, 0x00, bytes([0x00]))
        time.sleep_ms(5)
        prescale = i2c.readfrom_mem(PCA9685_ADDR, 0xFE, 1)[0]
        ok = prescale == 121
        print(f"  Prescale: {prescale} {'PASS' if ok else 'FAIL'}")
        nrf.send_text("PCA  OK" if ok else "PCA FAIL")
        time.sleep(1)
        nrf.send_result(4, ok, "PCA")
        return ok
    except OSError as e:
        print(f"  Error: {e}")
        nrf.send_text("PCA ERR")
        nrf.send_result(4, False, "PCA")
        return False


def pca_set(i2c, ch, on, off):
    reg = 0x06 + 4 * ch
    i2c.writeto_mem(PCA9685_ADDR, reg, bytes([
        on & 0xFF, (on >> 8) & 0xFF,
        off & 0xFF, (off >> 8) & 0xFF
    ]))

def pca_duty(i2c, ch, pct):
    val = int(pct * 4095 / 100)
    pca_set(i2c, ch, 0, max(1, min(val, 4095)))

def pca_servo(i2c, ch, angle):
    pulse = int(205 + (angle / 180) * 205)
    pca_set(i2c, ch, 0, pulse)

def pca_off(i2c, ch):
    pca_set(i2c, ch, 0, 0)


def test_motor1(i2c, nrf):
    """Test 5: Motor 1 ON/OFF."""
    print("[TEST 5] Motor 1 (PCA9685 CH2)...")
    nrf.send_text("M1 ON")
    pca_duty(i2c, 2, 50)  # 50% speed
    print("  Motor 1 ON at 50%")
    time.sleep(2)

    nrf.send_text("M1 OFF")
    pca_off(i2c, 2)
    print("  Motor 1 OFF")
    time.sleep(1)
    nrf.send_result(5, True, "MOT1")
    return True


def test_motor2(i2c, nrf):
    """Test 6: Motor 2 ON/OFF."""
    print("[TEST 6] Motor 2 (PCA9685 CH3)...")
    nrf.send_text("M2 ON")
    pca_duty(i2c, 3, 50)
    print("  Motor 2 ON at 50%")
    time.sleep(2)

    nrf.send_text("M2 OFF")
    pca_off(i2c, 3)
    print("  Motor 2 OFF")
    time.sleep(1)
    nrf.send_result(6, True, "MOT2")
    return True


def test_servo1(i2c, nrf):
    """Test 7: Servo 1 sweep."""
    print("[TEST 7] Servo 1 (PCA9685 CH0) — valve...")
    nrf.send_text("SV1 0")
    pca_servo(i2c, 0, 0)
    print("  Servo 1 → 0°")
    time.sleep(1)

    nrf.send_text("SV1 90")
    pca_servo(i2c, 0, 90)
    print("  Servo 1 → 90°")
    time.sleep(1)

    nrf.send_text("SV1 180")
    pca_servo(i2c, 0, 180)
    print("  Servo 1 → 180°")
    time.sleep(1)

    pca_servo(i2c, 0, 90)
    nrf.send_result(7, True, "SRV1")
    return True


def test_servo2(i2c, nrf):
    """Test 8: Servo 2 sweep."""
    print("[TEST 8] Servo 2 (PCA9685 CH1) — gate...")
    nrf.send_text("SV2 0")
    pca_servo(i2c, 1, 0)
    print("  Servo 2 → 0° (REJECT)")
    time.sleep(1)

    nrf.send_text("SV2 180")
    pca_servo(i2c, 1, 180)
    print("  Servo 2 → 180° (PASS)")
    time.sleep(1)

    nrf.send_text("SV2 90")
    pca_servo(i2c, 1, 90)
    print("  Servo 2 → 90° (CENTRE)")
    time.sleep(1)
    nrf.send_result(8, True, "SRV2")
    return True


def test_recycle(nrf):
    """Test 9: Recycle LED blink."""
    print("[TEST 9] Recycle path (GP13)...")
    recycle = Pin(RECYCLE_PIN, Pin.OUT)

    for i in range(4):
        recycle.high()
        nrf.send_text("REC ON")
        print(f"  [{i+1}] ON")
        time.sleep_ms(500)
        recycle.low()
        nrf.send_text("REC OFF")
        print(f"  [{i+1}] OFF")
        time.sleep_ms(500)

    recycle.low()
    nrf.send_result(9, True, "RECYCLE")
    return True


def test_shake(i2c, nrf):
    """Test 10: IMU shake detection."""
    print("[TEST 10] Shake detection — SHAKE THE BOARD!")
    nrf.send_text("SHAKE")

    detected = False
    for i in range(50):  # 5 seconds
        try:
            data = i2c.readfrom_mem(BMI160_ADDR, 0x12, 6)
            ax = (data[1] << 8 | data[0])
            ay = (data[3] << 8 | data[2])
            az = (data[5] << 8 | data[4])
            if ax > 32767: ax -= 65536
            if ay > 32767: ay -= 65536
            if az > 32767: az -= 65536
            s = 4.0 / 32768.0
            rms = math.sqrt((ax*s)**2 + (ay*s)**2 + (az*s)**2)

            if rms > 2.0:
                detected = True
                print(f"  SHAKE! RMS={rms:.2f}g")
                nrf.send_text("FAULT")
                time.sleep_ms(500)
                nrf.send_text(f"F1 {rms:.1f}G")
                time.sleep(2)
                nrf.send_text("RECOVER")
                time.sleep(1)
                break

            if i % 10 == 0:
                nrf.send_text(f"  {rms:.1f}G")
                print(f"  Waiting... RMS={rms:.2f}g")
        except:
            pass
        time.sleep_ms(100)

    if not detected:
        print("  No shake detected — auto-triggering fault")
        nrf.send_text("FAULT")
        time.sleep(1)
        nrf.send_text("F1 AUTO")
        time.sleep(1)
        nrf.send_text("RECOVER")
        time.sleep(1)

    nrf.send_result(10, detected, "SHAKE")
    return detected


def test_telemetry(i2c, nrf):
    """Test 11: Full telemetry stream (10 seconds)."""
    print("[TEST 11] Full telemetry stream...")
    nrf.send_text("LIVE")

    pca_duty(i2c, 2, 40)  # Motor 1 at 40%
    pca_duty(i2c, 3, 30)  # Motor 2 at 30%

    for i in range(20):
        # Read IMU
        try:
            data = i2c.readfrom_mem(BMI160_ADDR, 0x12, 6)
            ax = (data[1] << 8 | data[0])
            if ax > 32767: ax -= 65536
            rms_val = abs(ax * 4.0 / 32768.0)
        except:
            rms_val = 1.0

        # Simulated power
        bus_v = 5.02
        m1_ma = 380 + (i % 20) - 10
        m2_ma = 260 + (i % 15) - 7
        total = int(bus_v * (m1_ma + m2_ma))

        # Cycle display
        cycle = i % 5
        if cycle == 0:
            nrf.send_text(f"{bus_v:.1f}V")
        elif cycle == 1:
            nrf.send_text(f"A {m1_ma:4d}")
        elif cycle == 2:
            nrf.send_text(f"b {m2_ma:4d}")
        elif cycle == 3:
            nrf.send_text(f"P {total:4d}")
        else:
            nrf.send_text(f"G {rms_val:.1f}")

        print(f"  [{i+1:2d}] V={bus_v} M1={m1_ma}mA M2={m2_ma}mA P={total}mW IMU={rms_val:.1f}g")
        time.sleep_ms(500)

    pca_off(i2c, 2)
    pca_off(i2c, 3)
    nrf.send_result(11, True, "LIVE")
    return True


# ============ MAIN ============
def main():
    print()
    print("=" * 50)
    print("  GridBox — System Integration Test")
    print("  Pico A (Master)")
    print("=" * 50)
    print()

    led = Pin(LED_PIN, Pin.OUT, value=1)

    # Init
    print("[INIT] nRF24L01+...")
    nrf = NRF()
    nrf.send_text("GRIDBOX")
    time.sleep(1)
    nrf.send_text("TEST")
    time.sleep(1)

    print("[INIT] I2C...")
    i2c = I2C(0, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=400_000)

    results = {}
    print()

    # Run tests
    results['nrf'] = test_nrf(nrf)
    time.sleep_ms(500)

    has_imu, has_pca = test_i2c_scan(i2c, nrf)
    results['i2c'] = has_imu and has_pca
    time.sleep_ms(500)

    if has_imu:
        results['imu'] = test_imu(i2c, nrf)
        time.sleep_ms(500)
    else:
        results['imu'] = False
        print("[TEST 3] SKIP — no IMU")

    if has_pca:
        results['pca'] = test_pca9685(i2c, nrf)
        time.sleep_ms(500)

        results['motor1'] = test_motor1(i2c, nrf)
        time.sleep_ms(500)

        results['motor2'] = test_motor2(i2c, nrf)
        time.sleep_ms(500)

        results['servo1'] = test_servo1(i2c, nrf)
        time.sleep_ms(500)

        results['servo2'] = test_servo2(i2c, nrf)
        time.sleep_ms(500)
    else:
        for k in ['pca', 'motor1', 'motor2', 'servo1', 'servo2']:
            results[k] = False
        print("[TEST 4-8] SKIP — no PCA9685")

    results['recycle'] = test_recycle(nrf)
    time.sleep_ms(500)

    if has_imu:
        results['shake'] = test_shake(i2c, nrf)
        time.sleep_ms(500)
    else:
        results['shake'] = False

    if has_pca and has_imu:
        results['telemetry'] = test_telemetry(i2c, nrf)
    else:
        results['telemetry'] = False

    # Summary
    print()
    print("=" * 50)
    print("  RESULTS")
    print("=" * 50)

    passed = 0
    total = len(results)
    for name, ok in results.items():
        icon = "PASS" if ok else "FAIL"
        print(f"  [{icon}] {name}")
        if ok:
            passed += 1

    print()
    print(f"  {passed}/{total} tests passed")
    print("=" * 50)

    nrf.send_text(f"{passed:2d}OF{total:2d}")
    time.sleep(2)

    if passed == total:
        nrf.send_text("ALL PASS")
    else:
        nrf.send_text(f"  {passed} OK")

    # Done — slow blink
    while True:
        led.toggle()
        time.sleep(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest interrupted")
    except Exception as e:
        print(f"\nERROR: {e}")
        led = Pin(LED_PIN, Pin.OUT)
        for _ in range(20):
            led.toggle()
            time.sleep_ms(100)
