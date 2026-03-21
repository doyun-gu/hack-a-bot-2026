"""
GridBox — BMI160 IMU Driver
I2C driver for BMI160 6-axis IMU (accelerometer + gyroscope).
"""

from machine import I2C
import time
import struct
import math

# ============ BMI160 REGISTERS ============
CHIP_ID = 0x00       # expect 0xD1
ERR_REG = 0x02
PMU_STATUS = 0x03
DATA_MAG = 0x04      # magnetometer data (not used)
DATA_GYR = 0x0C      # gyro X low byte (6 bytes: XL,XH,YL,YH,ZL,ZH)
DATA_ACC = 0x12      # accel X low byte (6 bytes: XL,XH,YL,YH,ZL,ZH)
STATUS = 0x1B
INT_STATUS_0 = 0x1C
INT_STATUS_1 = 0x1D
TEMPERATURE = 0x20   # 2 bytes, little-endian
ACC_CONF = 0x40
ACC_RANGE = 0x41
GYR_CONF = 0x42
GYR_RANGE = 0x43
INT_EN_0 = 0x50
INT_OUT_CTRL = 0x53
INT_MAP_0 = 0x55
CMD = 0x7E

# ============ CMD VALUES ============
CMD_SOFT_RESET = 0xB6
CMD_ACC_NORMAL = 0x11
CMD_ACC_LOW = 0x12
CMD_GYR_NORMAL = 0x15
CMD_GYR_LOW = 0x17

# ============ ACC_RANGE VALUES ============
ACC_RANGE_2G = 0x03
ACC_RANGE_4G = 0x05
ACC_RANGE_8G = 0x08
ACC_RANGE_16G = 0x0C

# ============ GYR_RANGE VALUES ============
GYR_RANGE_2000 = 0x00  # ±2000°/s
GYR_RANGE_1000 = 0x01  # ±1000°/s
GYR_RANGE_500 = 0x02   # ±500°/s
GYR_RANGE_250 = 0x03   # ±250°/s
GYR_RANGE_125 = 0x04   # ±125°/s

# Scale factors
_ACC_SCALE = {
    ACC_RANGE_2G: 16384.0,
    ACC_RANGE_4G: 8192.0,
    ACC_RANGE_8G: 4096.0,
    ACC_RANGE_16G: 2048.0,
}

_GYR_SCALE = {
    GYR_RANGE_2000: 16.4,
    GYR_RANGE_1000: 32.8,
    GYR_RANGE_500: 65.6,
    GYR_RANGE_250: 131.2,
    GYR_RANGE_125: 262.4,
}


class BMI160:
    """BMI160 6-axis IMU driver."""

    def __init__(self, i2c, addr=0x68, accel_range=ACC_RANGE_4G,
                 gyro_range=GYR_RANGE_500, sample_rate=100):
        self.i2c = i2c
        self.addr = addr
        self.acc_scale = _ACC_SCALE[accel_range]
        self.gyr_scale = _GYR_SCALE[gyro_range]

        # Verify chip ID
        chip_id = self.who_am_i()
        if chip_id != 0xD1:
            print(f"[BMI160] WARNING: unexpected chip ID 0x{chip_id:02X} (expected 0xD1)")

        # Set accelerometer to normal mode
        self._write_reg(CMD, CMD_ACC_NORMAL)
        time.sleep_ms(4)

        # Set gyroscope to normal mode
        self._write_reg(CMD, CMD_GYR_NORMAL)
        time.sleep_ms(80)

        # Configure accelerometer
        # ACC_CONF: ODR=100Hz (0x08), BWP=normal (0x20)
        odr = self._rate_to_odr(sample_rate)
        self._write_reg(ACC_CONF, 0x20 | odr)
        self._write_reg(ACC_RANGE, accel_range)

        # Configure gyroscope
        self._write_reg(GYR_CONF, 0x20 | odr)
        self._write_reg(GYR_RANGE, gyro_range)

        time.sleep_ms(10)

    def _rate_to_odr(self, rate):
        """Convert sample rate to ODR register value."""
        if rate <= 25:
            return 0x06   # 25Hz
        elif rate <= 50:
            return 0x07   # 50Hz
        elif rate <= 100:
            return 0x08   # 100Hz
        elif rate <= 200:
            return 0x09   # 200Hz
        elif rate <= 400:
            return 0x0A   # 400Hz
        else:
            return 0x0B   # 800Hz

    def _read_reg(self, reg):
        return self.i2c.readfrom_mem(self.addr, reg, 1)[0]

    def _read_reg_bytes(self, reg, length):
        return self.i2c.readfrom_mem(self.addr, reg, length)

    def _write_reg(self, reg, value):
        self.i2c.writeto_mem(self.addr, reg, bytes([value]))

    def who_am_i(self):
        """Read chip ID register. Should return 0xD1 for BMI160."""
        return self._read_reg(CHIP_ID)

    def read_accel(self):
        """Read accelerometer. Returns (ax, ay, az) in g units."""
        data = self._read_reg_bytes(DATA_ACC, 6)
        ax = struct.unpack_from('<h', data, 0)[0] / self.acc_scale
        ay = struct.unpack_from('<h', data, 2)[0] / self.acc_scale
        az = struct.unpack_from('<h', data, 4)[0] / self.acc_scale
        return (ax, ay, az)

    def read_gyro(self):
        """Read gyroscope. Returns (gx, gy, gz) in °/s."""
        data = self._read_reg_bytes(DATA_GYR, 6)
        gx = struct.unpack_from('<h', data, 0)[0] / self.gyr_scale
        gy = struct.unpack_from('<h', data, 2)[0] / self.gyr_scale
        gz = struct.unpack_from('<h', data, 4)[0] / self.gyr_scale
        return (gx, gy, gz)

    def read_all(self):
        """Read all 6 axes at once. Returns dict with accel + gyro values."""
        # Read gyro + accel in one burst (12 bytes from DATA_GYR)
        data = self._read_reg_bytes(DATA_GYR, 12)
        gx = struct.unpack_from('<h', data, 0)[0] / self.gyr_scale
        gy = struct.unpack_from('<h', data, 2)[0] / self.gyr_scale
        gz = struct.unpack_from('<h', data, 4)[0] / self.gyr_scale
        ax = struct.unpack_from('<h', data, 6)[0] / self.acc_scale
        ay = struct.unpack_from('<h', data, 8)[0] / self.acc_scale
        az = struct.unpack_from('<h', data, 10)[0] / self.acc_scale
        return {
            'ax': ax, 'ay': ay, 'az': az,
            'gx': gx, 'gy': gy, 'gz': gz,
        }

    def accel_rms(self):
        """Return RMS acceleration magnitude: sqrt(ax² + ay² + az²)."""
        ax, ay, az = self.read_accel()
        return math.sqrt(ax * ax + ay * ay + az * az)

    def read_temperature(self):
        """Read temperature in °C."""
        data = self._read_reg_bytes(TEMPERATURE, 2)
        raw = struct.unpack_from('<h', data, 0)[0]
        # BMI160: 0x0000 = 23°C, resolution = 1/512 °C per LSB
        return 23.0 + raw / 512.0


if __name__ == "__main__":
    from machine import Pin
    import config

    print("=" * 40)
    print("  BMI160 IMU Driver Test")
    print("=" * 40)

    i2c = I2C(config.I2C_ID, sda=Pin(config.I2C_SDA),
              scl=Pin(config.I2C_SCL), freq=config.I2C_FREQ)

    try:
        imu = BMI160(i2c, addr=config.BMI160_ADDR,
                     accel_range=ACC_RANGE_4G,
                     gyro_range=GYR_RANGE_500,
                     sample_rate=config.IMU_SAMPLE_RATE)
        print(f"Chip ID: 0x{imu.who_am_i():02X}")
        print(f"Temperature: {imu.read_temperature():.1f}°C")
        print()

        while True:
            d = imu.read_all()
            a_rms = math.sqrt(d['ax']**2 + d['ay']**2 + d['az']**2)
            shake = "SHAKE DETECTED!" if a_rms > 2.0 else ""
            print(f"Accel: X={d['ax']:+.2f} Y={d['ay']:+.2f} Z={d['az']:+.2f} "
                  f"| Gyro: X={d['gx']:+.1f} Y={d['gy']:+.1f} Z={d['gz']:+.1f} "
                  f"| RMS={a_rms:.2f}g {shake}")
            time.sleep_ms(100)

    except OSError as e:
        print(f"[BMI160] I2C error: {e}")
        print("Check wiring: SDA=GP4, SCL=GP5, VCC=3.3V, GND=GND")
