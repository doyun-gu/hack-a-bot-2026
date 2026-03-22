"""
GridBox — Master Pico A Full Hardware Test
Tests: I2C scan → PCA9685 → Servo (CH15) → DC Motor (CH1) → BMI160 IMU → nRF24L01+

Wiring (actual):
  - PCA9685 CH15 = Servo
  - PCA9685 CH1  = DC Motor
  - BMI160 IMU on I2C 0x68
  - nRF24L01+ on SPI0

Upload: mpremote cp src/master-pico/tests/test_hw_all.py :main.py && mpremote reset
"""

from machine import Pin, I2C, SPI
import struct
import time

# ── Pin config ──
I2C_SDA, I2C_SCL = 4, 5
SPI_SCK, SPI_MOSI, SPI_MISO = 2, 3, 16
NRF_CE, NRF_CSN = 0, 1
LED = Pin(25, Pin.OUT)

# ── PCA9685 constants ──
PCA_ADDR = 0x40
SERVO_CH = 15
MOTOR_CH = 1
PCA_MODE1 = 0x00
PCA_PRESCALE = 0xFE
PCA_LED0_ON_L = 0x06

# ── BMI160 ──
BMI_ADDR = 0x68

# ── Helpers ──
def blink(n=3, t=0.1):
    for _ in range(n):
        LED.on(); time.sleep(t); LED.off(); time.sleep(t)

def pca_init(i2c):
    """Init PCA9685 at 50Hz for servos."""
    i2c.writeto_mem(PCA_ADDR, PCA_MODE1, b'\x10')  # sleep
    time.sleep_ms(5)
    # prescale for 50Hz: round(25MHz / (4096 * 50)) - 1 = 121
    i2c.writeto_mem(PCA_ADDR, PCA_PRESCALE, bytes([121]))
    i2c.writeto_mem(PCA_ADDR, PCA_MODE1, b'\x00')  # wake
    time.sleep_ms(5)
    i2c.writeto_mem(PCA_ADDR, PCA_MODE1, b'\xA0')  # auto-increment + restart

def pca_set_pwm(i2c, ch, on, off):
    """Set PCA9685 channel PWM."""
    reg = PCA_LED0_ON_L + 4 * ch
    i2c.writeto_mem(PCA_ADDR, reg, struct.pack('<HH', on, off))

def servo_us(i2c, ch, pulse_us):
    """Set servo pulse width in microseconds (500-2500)."""
    # At 50Hz, period = 20000us, 4096 ticks
    ticks = int(pulse_us * 4096 / 20000)
    pca_set_pwm(i2c, ch, 0, ticks)

def motor_pct(i2c, ch, pct):
    """Set DC motor speed 0-100%."""
    off_val = int(pct / 100 * 4095)
    if off_val == 0:
        pca_set_pwm(i2c, ch, 0, 0)
    else:
        pca_set_pwm(i2c, ch, 0, off_val)

def motor_off(i2c, ch):
    """Stop motor."""
    pca_set_pwm(i2c, ch, 0, 0)

# ══════════════════════════════════════════
#  TEST 1: I2C SCAN
# ══════════════════════════════════════════
print("=" * 50)
print("  GRIDBOX MASTER — FULL HARDWARE TEST")
print("=" * 50)
print()

i2c = I2C(0, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=400_000)
devices = i2c.scan()
print(f"[1/6] I2C SCAN: found {len(devices)} devices")
for d in devices:
    name = {0x40: "PCA9685", 0x68: "BMI160", 0x69: "BMI160-alt", 0x3C: "OLED"}.get(d, "?")
    print(f"  0x{d:02X} = {name}")

has_pca = 0x40 in devices
has_imu = 0x68 in devices
print(f"  PCA9685: {'FOUND' if has_pca else 'MISSING'}")
print(f"  BMI160:  {'FOUND' if has_imu else 'MISSING'}")
print()

# ══════════════════════════════════════════
#  TEST 2: PCA9685 INIT
# ══════════════════════════════════════════
if has_pca:
    print("[2/6] PCA9685 INIT...")
    try:
        pca_init(i2c)
        print("  PCA9685 initialised at 50Hz — PASS")
    except Exception as e:
        print(f"  PCA9685 init FAILED: {e}")
        has_pca = False
else:
    print("[2/6] PCA9685 INIT — SKIPPED (not found)")
print()

# ══════════════════════════════════════════
#  TEST 3: SERVO (CH15) — sweep 0° → 90° → 180° → 90°
# ══════════════════════════════════════════
if has_pca:
    print(f"[3/6] SERVO TEST (CH{SERVO_CH})...")
    angles = [
        (0,   500,  "0°   (500us)"),
        (90,  1500, "90°  (1500us)"),
        (180, 2500, "180° (2500us)"),
        (90,  1500, "90°  (1500us) — centre"),
    ]
    for deg, us, label in angles:
        servo_us(i2c, SERVO_CH, us)
        print(f"  → {label}")
        time.sleep(1)
    # Park servo
    servo_us(i2c, SERVO_CH, 1500)
    print("  Servo test — PASS (check if arm moved)")
else:
    print("[3/6] SERVO TEST — SKIPPED")
print()

# ══════════════════════════════════════════
#  TEST 4: DC MOTOR (CH1) — ramp 0% → 50% → 100% → 0%
# ══════════════════════════════════════════
if has_pca:
    print(f"[4/6] DC MOTOR TEST (CH{MOTOR_CH})...")
    speeds = [0, 20, 40, 60, 80, 100, 80, 60, 40, 20, 0]
    for spd in speeds:
        motor_pct(i2c, MOTOR_CH, spd)
        print(f"  → {spd}%")
        time.sleep(0.5)
    motor_off(i2c, MOTOR_CH)
    print("  Motor test — PASS (check if motor ramped)")
else:
    print("[4/6] DC MOTOR TEST — SKIPPED")
print()

# ══════════════════════════════════════════
#  TEST 5: BMI160 IMU — read accel for 3 seconds
# ══════════════════════════════════════════
if has_imu:
    print("[5/6] BMI160 IMU TEST...")
    try:
        # Init: set accel to normal mode
        i2c.writeto_mem(BMI_ADDR, 0x7E, b'\x11')  # CMD: accel normal
        time.sleep_ms(100)
        i2c.writeto_mem(BMI_ADDR, 0x7E, b'\x15')  # CMD: gyro normal
        time.sleep_ms(100)

        chip_id = i2c.readfrom_mem(BMI_ADDR, 0x00, 1)[0]
        print(f"  Chip ID: 0x{chip_id:02X} (expected 0xD1)")

        print("  Reading accel for 3 seconds (shake to test)...")
        max_rms = 0
        shakes = 0
        for _ in range(30):
            raw = i2c.readfrom_mem(BMI_ADDR, 0x0C, 6)  # accel X/Y/Z
            ax, ay, az = struct.unpack('<hhh', raw)
            # Convert to g (±4g range, 16384 LSB/g for ±2g, 8192 for ±4g)
            gx = ax / 8192.0
            gy = ay / 8192.0
            gz = az / 8192.0
            rms = (gx**2 + gy**2 + gz**2) ** 0.5
            if rms > max_rms:
                max_rms = rms
            if rms > 2.0:
                shakes += 1
            print(f"  X={gx:+.2f}g Y={gy:+.2f}g Z={gz:+.2f}g RMS={rms:.2f}g", end="")
            if rms > 2.0:
                print(" ← SHAKE!", end="")
            print()
            time.sleep_ms(100)

        print(f"  Max RMS: {max_rms:.2f}g, Shakes detected: {shakes}")
        print(f"  IMU test — PASS")
    except Exception as e:
        print(f"  IMU test FAILED: {e}")
else:
    print("[5/6] BMI160 IMU TEST — SKIPPED (not found)")
print()

# ══════════════════════════════════════════
#  TEST 6: nRF24L01+ SPI CHECK
# ══════════════════════════════════════════
print("[6/6] nRF24L01+ SPI TEST...")
try:
    ce = Pin(NRF_CE, Pin.OUT, value=0)
    csn = Pin(NRF_CSN, Pin.OUT, value=1)
    spi = SPI(0, baudrate=4_000_000, sck=Pin(SPI_SCK), mosi=Pin(SPI_MOSI), miso=Pin(SPI_MISO))

    def nrf_read_reg(reg):
        csn.value(0)
        spi.write(bytes([reg & 0x1F]))
        val = spi.read(1)
        csn.value(1)
        return val[0]

    def nrf_write_reg(reg, val):
        csn.value(0)
        spi.write(bytes([0x20 | (reg & 0x1F), val]))
        csn.value(1)

    status = nrf_read_reg(0x07)
    print(f"  Status register: 0x{status:02X}")

    # Write then read channel to verify SPI
    nrf_write_reg(0x05, 100)  # set channel 100
    ch = nrf_read_reg(0x05)
    print(f"  Channel write/read: wrote 100, read {ch}")

    if status in (0x00, 0xFF):
        print("  nRF NOT responding (check wiring)")
    elif ch == 100:
        print("  nRF SPI — PASS")
    else:
        print(f"  nRF SPI — FAIL (channel mismatch)")
except Exception as e:
    print(f"  nRF test FAILED: {e}")
print()

# ══════════════════════════════════════════
#  SUMMARY
# ══════════════════════════════════════════
print("=" * 50)
print("  TEST COMPLETE")
print(f"  PCA9685: {'OK' if has_pca else 'MISSING'}")
print(f"  Servo CH{SERVO_CH}: {'TESTED' if has_pca else 'SKIPPED'}")
print(f"  Motor CH{MOTOR_CH}: {'TESTED' if has_pca else 'SKIPPED'}")
print(f"  BMI160:  {'OK' if has_imu else 'MISSING'}")
print(f"  nRF24:   CHECK ABOVE")
print("=" * 50)

blink(5, 0.1)  # success blink
