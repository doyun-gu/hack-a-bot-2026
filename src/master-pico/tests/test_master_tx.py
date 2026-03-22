"""
GridBox — Master Pico A: Transmit Test
Reads real sensors (IMU, PCA9685 servo/motor status) and sends via nRF to slave.
Slave (test_slave_rx.py) receives and prints to laptop USB serial.

Wiring:
  - PCA9685 CH15 = Servo, CH1 = DC Motor
  - BMI160 on I2C 0x68
  - nRF24L01+ on SPI0 (CE=GP0, CSN=GP1)

Upload: mpremote cp src/master-pico/tests/test_master_tx.py :main.py && mpremote reset
"""

from machine import Pin, I2C, SPI
import struct
import time

# ── Pins ──
LED = Pin(25, Pin.OUT)
ce = Pin(0, Pin.OUT, value=0)
csn = Pin(1, Pin.OUT, value=1)
spi = SPI(0, baudrate=4_000_000, sck=Pin(2), mosi=Pin(3), miso=Pin(16))
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400_000)

# ── Config ──
PCA_ADDR = 0x40
BMI_ADDR = 0x68
SERVO_CH = 15
MOTOR_CH = 1
CHANNEL = 100
TX_ADDR = b'GRIDM'
RX_ADDR = b'GRIDS'

# ── nRF24 minimal driver ──
def nrf_write(reg, val):
    csn.value(0)
    if isinstance(val, int):
        spi.write(bytes([0x20 | reg, val]))
    else:
        spi.write(bytes([0x20 | reg]) + val)
    csn.value(1)

def nrf_read(reg, n=1):
    csn.value(0)
    spi.write(bytes([reg & 0x1F]))
    data = spi.read(n)
    csn.value(1)
    return data[0] if n == 1 else data

def nrf_send(payload):
    """Send 32-byte payload. Returns True if ACK received."""
    ce.value(0)
    csn.value(0)
    spi.write(b'\xE1')  # flush TX
    csn.value(1)

    csn.value(0)
    spi.write(b'\xA0' + payload)  # write TX payload
    csn.value(1)

    ce.value(1)
    time.sleep_us(15)
    ce.value(0)

    # Wait for TX complete or max retries
    for _ in range(100):
        status = nrf_read(0x07)
        if status & 0x20:  # TX_DS — sent OK
            nrf_write(0x07, 0x70)  # clear flags
            return True
        if status & 0x10:  # MAX_RT — failed
            nrf_write(0x07, 0x70)
            csn.value(0)
            spi.write(b'\xE1')  # flush TX
            csn.value(1)
            return False
        time.sleep_us(100)
    return False

def nrf_init_tx():
    """Init nRF as transmitter with auto-ACK."""
    ce.value(0)
    nrf_write(0x00, 0x0E)  # PWR_UP, EN_CRC, CRC 2-byte, PTX
    nrf_write(0x01, 0x01)  # EN_AA on pipe 0
    nrf_write(0x02, 0x01)  # EN_RXADDR pipe 0
    nrf_write(0x03, 0x03)  # 5-byte address
    nrf_write(0x04, 0x4A)  # 500us retry, 10 retries
    nrf_write(0x05, CHANNEL)
    nrf_write(0x06, 0x26)  # 250kbps, 0dBm
    nrf_write(0x11, 32)    # RX payload width pipe 0
    # Set TX address
    csn.value(0)
    spi.write(b'\x30' + TX_ADDR)  # TX_ADDR
    csn.value(1)
    # Set RX pipe 0 to same (for ACK)
    csn.value(0)
    spi.write(b'\x2A' + TX_ADDR)  # RX_ADDR_P0
    csn.value(1)
    nrf_write(0x07, 0x70)  # clear flags
    time.sleep_ms(5)
    print(f"  nRF TX mode, channel {CHANNEL}")

# ── PCA9685 ──
PCA_LED0_ON_L = 0x06

def pca_init():
    i2c.writeto_mem(PCA_ADDR, 0x00, b'\x10')
    time.sleep_ms(5)
    i2c.writeto_mem(PCA_ADDR, 0xFE, bytes([121]))  # 50Hz
    i2c.writeto_mem(PCA_ADDR, 0x00, b'\x00')
    time.sleep_ms(5)
    i2c.writeto_mem(PCA_ADDR, 0x00, b'\xA0')

def pca_set(ch, on, off):
    reg = PCA_LED0_ON_L + 4 * ch
    i2c.writeto_mem(PCA_ADDR, reg, struct.pack('<HH', on, off))

def servo_us(ch, us):
    pca_set(ch, 0, int(us * 4096 / 20000))

def motor_pct(ch, pct):
    pca_set(ch, 0, int(pct / 100 * 4095))

# ── BMI160 ──
def imu_init():
    i2c.writeto_mem(BMI_ADDR, 0x7E, b'\x11')  # accel normal
    time.sleep_ms(100)
    i2c.writeto_mem(BMI_ADDR, 0x7E, b'\x15')  # gyro normal
    time.sleep_ms(100)

def imu_read():
    raw = i2c.readfrom_mem(BMI_ADDR, 0x0C, 6)
    ax, ay, az = struct.unpack('<hhh', raw)
    gx, gy, gz = ax / 8192.0, ay / 8192.0, az / 8192.0
    return gx, gy, gz, (gx**2 + gy**2 + gz**2) ** 0.5

# ══════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════
print("=" * 50)
print("  MASTER TX — Servo + Motor + IMU → Wireless")
print("=" * 50)

# Init hardware
has_pca = PCA_ADDR in i2c.scan()
has_imu = BMI_ADDR in i2c.scan()

if has_pca:
    pca_init()
    print("  PCA9685 OK")
if has_imu:
    imu_init()
    print("  BMI160 OK")

nrf_init_tx()
print()

# Demo loop: cycle servo + motor, read IMU, send to slave
seq = 0
servo_pos = 0  # 0=left, 1=centre, 2=right
servo_angles = [500, 1500, 2500]  # pulse widths
motor_speed = 0
motor_dir = 5  # increment

print("Sending telemetry to slave every 200ms...")
print("  Servo cycles: 0° → 90° → 180°")
print("  Motor ramps: 0% → 100% → 0%")
print("  IMU: live acceleration")
print()

t_servo = time.ticks_ms()
t_start = time.ticks_ms()

while True:
    now = time.ticks_ms()

    # Cycle servo every 2 seconds
    if time.ticks_diff(now, t_servo) > 2000:
        servo_pos = (servo_pos + 1) % 3
        if has_pca:
            servo_us(SERVO_CH, servo_angles[servo_pos])
        t_servo = now

    # Ramp motor speed
    motor_speed += motor_dir
    if motor_speed >= 100:
        motor_dir = -5
    elif motor_speed <= 0:
        motor_dir = 5
    motor_speed = max(0, min(100, motor_speed))
    if has_pca:
        motor_pct(MOTOR_CH, motor_speed)

    # Read IMU
    imu_rms = 0.0
    if has_imu:
        _, _, _, imu_rms = imu_read()

    # Build 32-byte packet:
    # [0]    = packet type (0x01 = telemetry)
    # [1]    = sequence number
    # [2-3]  = servo angle (degrees * 10)
    # [4-5]  = motor speed (%)
    # [6-9]  = IMU RMS (float)
    # [10]   = servo channel
    # [11]   = motor channel
    # [12-31] = padding
    servo_deg = [0, 90, 180][servo_pos]
    payload = struct.pack('<BBHHfBB20s',
        0x01,           # type
        seq & 0xFF,     # seq
        servo_deg * 10, # servo angle * 10
        motor_speed,    # motor %
        imu_rms,        # IMU RMS
        SERVO_CH,       # servo channel
        MOTOR_CH,       # motor channel
        b'\x00' * 20    # padding
    )

    ok = nrf_send(payload)
    LED.toggle()

    elapsed = time.ticks_diff(now, t_start) // 1000
    status = "ACK" if ok else "FAIL"
    print(f"[{seq:4d}] servo={servo_deg:3d}° motor={motor_speed:3d}% imu={imu_rms:.2f}g → {status}  ({elapsed}s)")

    seq += 1
    time.sleep_ms(200)
