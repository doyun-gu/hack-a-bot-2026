"""
GridBox — PCA9685 16-Channel PWM Driver
I2C driver for PCA9685 servo/motor controller.
"""

from machine import I2C
import time
import struct

# ============ PCA9685 REGISTERS ============
MODE1 = 0x00
MODE2 = 0x01
SUBADR1 = 0x02
PRE_SCALE = 0xFE
LED0_ON_L = 0x06    # each channel: ON_L, ON_H, OFF_L, OFF_H (4 bytes)
ALL_LED_ON_L = 0xFA
ALL_LED_OFF_L = 0xFC

# MODE1 bits
RESTART = 0x80
SLEEP = 0x10
AI = 0x20           # auto-increment
ALLCALL = 0x01

# Constants
CLOCK_FREQ = 25_000_000  # 25MHz internal oscillator
RESOLUTION = 4096         # 12-bit PWM


class PCA9685:
    """PCA9685 16-channel PWM driver."""

    def __init__(self, i2c, addr=0x40, freq=50):
        self.i2c = i2c
        self.addr = addr

        # Reset
        self._write_reg(MODE1, RESTART)
        time.sleep_ms(5)

        # Set auto-increment
        self._write_reg(MODE1, AI | ALLCALL)
        time.sleep_ms(1)

        # Set PWM frequency
        self.set_frequency(freq)

    def _read_reg(self, reg):
        return self.i2c.readfrom_mem(self.addr, reg, 1)[0]

    def _write_reg(self, reg, value):
        self.i2c.writeto_mem(self.addr, reg, bytes([value]))

    def set_frequency(self, freq_hz):
        """Set PWM frequency in Hz. Valid range: 24-1526 Hz."""
        prescale = int(CLOCK_FREQ / (RESOLUTION * freq_hz) + 0.5) - 1
        prescale = max(3, min(255, prescale))

        # Must sleep to change prescaler
        old_mode = self._read_reg(MODE1)
        self._write_reg(MODE1, (old_mode & ~RESTART) | SLEEP)
        self._write_reg(PRE_SCALE, prescale)
        self._write_reg(MODE1, old_mode)
        time.sleep_us(500)
        self._write_reg(MODE1, old_mode | RESTART)

    def set_pwm(self, channel, on, off):
        """Set raw PWM on/off values for a channel (0-15).

        Args:
            channel: 0-15
            on: 0-4095 (when to turn on in the 4096-step cycle)
            off: 0-4095 (when to turn off)
        """
        reg = LED0_ON_L + 4 * channel
        data = struct.pack('<HH', on & 0xFFF, off & 0xFFF)
        self.i2c.writeto_mem(self.addr, reg, data)

    def set_duty(self, channel, duty_percent):
        """Set duty cycle 0-100% for a channel."""
        if duty_percent <= 0:
            self.set_pwm(channel, 0, 0)
        elif duty_percent >= 100:
            self.set_pwm(channel, 4096, 0)  # full on
        else:
            off = int(duty_percent * RESOLUTION / 100)
            self.set_pwm(channel, 0, off)

    def set_servo_angle(self, channel, angle):
        """Set servo position by angle (0-180°).

        Maps angle to pulse width: 500µs (0°) to 2500µs (180°).
        Assumes 50Hz PWM (20ms period).
        """
        # Pulse width in µs
        pulse_us = 500 + (angle / 180.0) * 2000
        # Convert to 12-bit value (20ms = 4096 steps)
        off = int(pulse_us / 20000.0 * RESOLUTION)
        off = max(0, min(RESOLUTION - 1, off))
        self.set_pwm(channel, 0, off)

    def set_motor_speed(self, channel, speed_percent):
        """Set motor speed 0-100% via PWM duty cycle."""
        self.set_duty(channel, max(0, min(100, speed_percent)))

    def off(self, channel):
        """Turn off a single channel."""
        self.set_pwm(channel, 0, 0)

    def all_off(self):
        """Turn off all 16 channels."""
        data = struct.pack('<HH', 0, 0)
        self.i2c.writeto_mem(self.addr, ALL_LED_ON_L, data)

    def set_frequency(self, freq_hz):
        """Set PWM frequency in Hz."""
        prescale = int(CLOCK_FREQ / (RESOLUTION * freq_hz) + 0.5) - 1
        prescale = max(3, min(255, prescale))

        old_mode = self._read_reg(MODE1)
        self._write_reg(MODE1, (old_mode & ~RESTART) | SLEEP)
        self._write_reg(PRE_SCALE, prescale)
        self._write_reg(MODE1, old_mode)
        time.sleep_us(500)
        self._write_reg(MODE1, old_mode | RESTART)


if __name__ == "__main__":
    from machine import Pin
    import config

    print("=" * 40)
    print("  PCA9685 PWM Driver Test")
    print("=" * 40)

    i2c = I2C(config.I2C_ID, sda=Pin(config.I2C_SDA),
              scl=Pin(config.I2C_SCL), freq=config.I2C_FREQ)

    try:
        pca = PCA9685(i2c, addr=config.PCA9685_ADDR, freq=50)
        print(f"PCA9685 initialised at 0x{config.PCA9685_ADDR:02X}")
        print("PWM frequency: 50Hz (servo mode)")

        # Test servo sweep on channel 0
        print("\nSweeping servo on channel 0: 0° → 180° → 0°")
        for angle in range(0, 181, 10):
            pca.set_servo_angle(0, angle)
            print(f"  Angle: {angle}°")
            time.sleep_ms(100)
        for angle in range(180, -1, -10):
            pca.set_servo_angle(0, angle)
            print(f"  Angle: {angle}°")
            time.sleep_ms(100)

        pca.all_off()
        print("\nAll channels off. Test complete.")

    except OSError as e:
        print(f"I2C error: {e}")
        print("Check wiring: SDA=GP4, SCL=GP5, VCC=5V, GND=GND")
