"""
GridBox — Motor Control
Manages motors (via PCA9685 PWM + MOSFET GPIO), servos, LED bank, recycle path.
"""

from machine import Pin
import time
import config


class MotorControl:
    """Motor and actuator controller using PCA9685 + MOSFET switches."""

    def __init__(self, pca9685, mosfet_pins=None):
        """
        Args:
            pca9685: PCA9685 driver instance
            mosfet_pins: dict of {name: gpio_pin_number} or None for defaults
        """
        self.pca = pca9685

        # MOSFET GPIO switches
        pins = mosfet_pins or {
            'motor1': config.MOSFET_MOTOR1,
            'motor2': config.MOSFET_MOTOR2,
            'leds': config.MOSFET_LED_BANK,
            'recycle': config.MOSFET_RECYCLE,
        }
        self.mosfets = {}
        for name, pin_num in pins.items():
            self.mosfets[name] = Pin(pin_num, Pin.OUT, value=0)

        # Track state
        self.motor_speeds = {1: 0, 2: 0}
        self.servo_angles = {1: 90, 2: 90}
        self.motor_enabled = {1: False, 2: False}

    def enable_motor(self, motor_id):
        """Enable motor by switching MOSFET on (GPIO high)."""
        key = 'motor1' if motor_id == 1 else 'motor2'
        self.mosfets[key].value(1)
        self.motor_enabled[motor_id] = True

    def disable_motor(self, motor_id):
        """Disable motor by switching MOSFET off (GPIO low)."""
        key = 'motor1' if motor_id == 1 else 'motor2'
        self.mosfets[key].value(0)
        self.motor_enabled[motor_id] = False

    def set_speed(self, motor_id, speed_percent):
        """Set motor speed 0-100% via PCA9685 PWM.

        Automatically enables the MOSFET if speed > 0.
        """
        speed_percent = max(0, min(100, speed_percent))

        if speed_percent > 0 and not self.motor_enabled[motor_id]:
            self.enable_motor(motor_id)

        ch = config.MOTOR1_PWM_CH if motor_id == 1 else config.MOTOR2_PWM_CH
        self.pca.set_motor_speed(ch, speed_percent)
        self.motor_speeds[motor_id] = speed_percent

    def get_speed(self, motor_id):
        """Return current speed of motor."""
        return self.motor_speeds.get(motor_id, 0)

    def set_servo_angle(self, servo_id, angle):
        """Set servo position 0-180°.

        Args:
            servo_id: 1 (valve) or 2 (gate)
        """
        angle = max(0, min(180, angle))
        ch = config.SERVO_VALVE_CH if servo_id == 1 else config.SERVO_GATE_CH
        self.pca.set_servo_angle(ch, angle)
        self.servo_angles[servo_id] = angle

    def get_servo_angle(self, servo_id):
        """Return current servo angle."""
        return self.servo_angles.get(servo_id, 90)

    def emergency_stop(self, motor_id):
        """Immediately stop a motor: MOSFET off + PWM off."""
        ch = config.MOTOR1_PWM_CH if motor_id == 1 else config.MOTOR2_PWM_CH
        self.pca.off(ch)
        self.disable_motor(motor_id)
        self.motor_speeds[motor_id] = 0

    def emergency_stop_all(self):
        """Stop all motors and actuators immediately."""
        self.pca.all_off()
        for name in self.mosfets:
            self.mosfets[name].value(0)
        self.motor_speeds = {1: 0, 2: 0}
        self.motor_enabled = {1: False, 2: False}

    def ramp_speed(self, motor_id, target, duration_ms=1000):
        """Gradually change motor speed from current to target.

        Args:
            motor_id: 1 or 2
            target: target speed 0-100%
            duration_ms: ramp duration in milliseconds
        """
        current = self.motor_speeds[motor_id]
        target = max(0, min(100, target))
        diff = target - current

        if diff == 0:
            return

        steps = max(1, abs(diff) // 2)
        step_size = diff / steps
        step_delay = duration_ms // steps

        for i in range(steps):
            speed = int(current + step_size * (i + 1))
            self.set_speed(motor_id, speed)
            time.sleep_ms(step_delay)

        # Ensure we hit exact target
        self.set_speed(motor_id, target)

    def set_led_bank(self, on):
        """Turn LED bank MOSFET on/off."""
        self.mosfets['leds'].value(1 if on else 0)

    def set_recycle(self, on):
        """Turn recycle path MOSFET on/off."""
        self.mosfets['recycle'].value(1 if on else 0)

    def get_state(self):
        """Return dict with current state of all outputs."""
        return {
            'm1_speed': self.motor_speeds[1],
            'm2_speed': self.motor_speeds[2],
            'm1_enabled': self.motor_enabled[1],
            'm2_enabled': self.motor_enabled[2],
            'servo1_angle': self.servo_angles[1],
            'servo2_angle': self.servo_angles[2],
            'leds_on': bool(self.mosfets['leds'].value()),
            'recycle_on': bool(self.mosfets['recycle'].value()),
        }


if __name__ == "__main__":
    from machine import I2C
    from pca9685 import PCA9685

    print("=" * 40)
    print("  Motor Control Test")
    print("=" * 40)

    i2c = I2C(config.I2C_ID, sda=Pin(config.I2C_SDA),
              scl=Pin(config.I2C_SCL), freq=config.I2C_FREQ)

    try:
        pca = PCA9685(i2c, addr=config.PCA9685_ADDR, freq=50)
        mc = MotorControl(pca)
        print("Motor control initialised\n")

        # Test servo
        print("Servo 1 (valve): 0° → 90° → 180° → 90°")
        for angle in [0, 90, 180, 90]:
            mc.set_servo_angle(1, angle)
            print(f"  Angle: {angle}°")
            time.sleep_ms(500)

        # Test motor ramp
        print("\nMotor 1: ramp 0% → 50% over 2s")
        mc.ramp_speed(1, 50, 2000)
        print(f"  Speed: {mc.get_speed(1)}%")

        print("Motor 1: ramp 50% → 0% over 1s")
        mc.ramp_speed(1, 0, 1000)
        print(f"  Speed: {mc.get_speed(1)}%")

        # Test LED bank
        print("\nLED bank: ON")
        mc.set_led_bank(True)
        time.sleep(1)
        print("LED bank: OFF")
        mc.set_led_bank(False)

        # Emergency stop
        print("\nEmergency stop all")
        mc.emergency_stop_all()
        print(f"State: {mc.get_state()}")

        print("\nMotor control test complete")

    except OSError as e:
        print(f"I2C error: {e}")
