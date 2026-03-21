"""
GridBox — IMU Reader (Core 1)
Runs BMI160 sampling on Core 1, classifies vibration levels.
Thread-safe shared data via locks.
"""

import _thread
import time
import math
import config


# Vibration states
VIB_HEALTHY = "HEALTHY"
VIB_WARNING = "WARNING"
VIB_FAULT = "FAULT"


class IMUReader:
    """Continuous IMU sampling on Core 1 with vibration classification."""

    def __init__(self, bmi160):
        self.imu = bmi160
        self.lock = _thread.allocate_lock()

        # Shared data (protected by lock)
        self._rms = 0.0
        self._peak = 0.0
        self._status = VIB_HEALTHY
        self._is_fault = False
        self._accel = (0.0, 0.0, 0.0)
        self._gyro = (0.0, 0.0, 0.0)

        # Rolling window
        self._window = [0.0] * config.IMU_WINDOW_SIZE
        self._window_idx = 0

        # Fault timing
        self._warning_start_ms = 0
        self._running = False

    def start(self):
        """Start the IMU reader on Core 1."""
        if self._running:
            return
        self._running = True
        _thread.start_new_thread(self._read_loop, ())

    def stop(self):
        """Stop the reader thread."""
        self._running = False

    def _read_loop(self):
        """Core 1 loop: read IMU at 100Hz, classify vibration."""
        interval_ms = 1000 // config.IMU_SAMPLE_RATE

        while self._running:
            try:
                # Read all axes
                data = self.imu.read_all()
                ax, ay, az = data['ax'], data['ay'], data['az']
                gx, gy, gz = data['gx'], data['gy'], data['gz']
                a_rms = math.sqrt(ax * ax + ay * ay + az * az)

                # Update rolling window
                self._window[self._window_idx] = a_rms
                self._window_idx = (self._window_idx + 1) % config.IMU_WINDOW_SIZE

                # Calculate peak from window
                peak = max(self._window)

                # Classify vibration
                status = VIB_HEALTHY
                is_fault = False

                if a_rms > config.IMU_WARNING_THRESHOLD:
                    # Check if sustained for FAULT duration
                    now = time.ticks_ms()
                    if self._warning_start_ms == 0:
                        self._warning_start_ms = now

                    elapsed = time.ticks_diff(now, self._warning_start_ms)
                    if elapsed >= config.IMU_FAULT_DURATION_MS:
                        status = VIB_FAULT
                        is_fault = True
                    else:
                        status = VIB_WARNING
                elif a_rms > config.IMU_HEALTHY_THRESHOLD:
                    status = VIB_WARNING
                    self._warning_start_ms = 0
                else:
                    status = VIB_HEALTHY
                    self._warning_start_ms = 0

                # Thread-safe update
                self.lock.acquire()
                self._rms = a_rms
                self._peak = peak
                self._status = status
                self._is_fault = is_fault
                self._accel = (ax, ay, az)
                self._gyro = (gx, gy, gz)
                self.lock.release()

            except Exception as e:
                print(f"[IMU Core1] Error: {e}")

            time.sleep_ms(interval_ms)

    def get_rms(self):
        """Return current acceleration RMS (thread-safe)."""
        self.lock.acquire()
        val = self._rms
        self.lock.release()
        return val

    def get_peak(self):
        """Return peak RMS from rolling window (thread-safe)."""
        self.lock.acquire()
        val = self._peak
        self.lock.release()
        return val

    def get_status(self):
        """Return vibration status: HEALTHY, WARNING, or FAULT."""
        self.lock.acquire()
        val = self._status
        self.lock.release()
        return val

    def is_fault(self):
        """Return True if sustained vibration fault detected."""
        self.lock.acquire()
        val = self._is_fault
        self.lock.release()
        return val

    def reset_fault(self):
        """Manually reset fault state."""
        self.lock.acquire()
        self._is_fault = False
        self._status = VIB_HEALTHY
        self._warning_start_ms = 0
        self.lock.release()

    def get_data(self):
        """Return dict with all current IMU data (thread-safe)."""
        self.lock.acquire()
        data = {
            'rms': self._rms,
            'peak': self._peak,
            'status': self._status,
            'is_fault': self._is_fault,
            'ax': self._accel[0],
            'ay': self._accel[1],
            'az': self._accel[2],
            'gx': self._gyro[0],
            'gy': self._gyro[1],
            'gz': self._gyro[2],
        }
        self.lock.release()
        return data


if __name__ == "__main__":
    from machine import Pin, I2C
    from bmi160 import BMI160, ACC_RANGE_4G, GYR_RANGE_500

    print("=" * 40)
    print("  IMU Reader (Core 1) Test")
    print("=" * 40)

    i2c = I2C(config.I2C_ID, sda=Pin(config.I2C_SDA),
              scl=Pin(config.I2C_SCL), freq=config.I2C_FREQ)

    try:
        imu = BMI160(i2c, addr=config.BMI160_ADDR,
                     accel_range=ACC_RANGE_4G,
                     gyro_range=GYR_RANGE_500)

        reader = IMUReader(imu)
        reader.start()
        print("Core 1 IMU reader started\n")

        led_red = Pin(config.LED_RED, Pin.OUT)

        while True:
            data = reader.get_data()
            led_red.value(1 if data['is_fault'] else 0)

            print(f"RMS={data['rms']:.2f}g Peak={data['peak']:.2f}g "
                  f"Status={data['status']} "
                  f"A=({data['ax']:+.2f},{data['ay']:+.2f},{data['az']:+.2f})")

            time.sleep_ms(200)

    except OSError as e:
        print(f"I2C error: {e}")
    except KeyboardInterrupt:
        reader.stop()
        print("\nStopped")
