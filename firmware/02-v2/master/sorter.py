"""
GridBox — Weight-Based Sorter
Detects items on conveyor via motor current spikes, classifies weight,
fires servo gate after timed travel delay.
"""

import time
from machine import Timer
import config


# Weight classifications
CLASS_PASS = "PASS"
CLASS_REJECT_HEAVY = "REJECT_HEAVY"
CLASS_REJECT_LIGHT = "REJECT_LIGHT"
CLASS_JAM = "JAM"
CLASS_NONE = "NONE"


class Sorter:
    """Weight-based sorting using motor current sensing + timed servo gate."""

    def __init__(self, motor_control, power_manager, calibration=None):
        """
        Args:
            motor_control: MotorControl instance
            power_manager: PowerManager instance
            calibration: Calibration instance (optional)
        """
        self.mc = motor_control
        self.pm = power_manager
        self.cal = calibration

        # Baseline current (empty belt)
        self._baseline_mA = 0.0

        # Thresholds (can be adjusted via potentiometer)
        self.threshold_light = config.WEIGHT_THRESHOLD_LIGHT
        self.threshold_heavy = config.WEIGHT_THRESHOLD_HEAVY
        self.threshold_jam = config.WEIGHT_THRESHOLD_JAM

        # Belt timing
        self.belt_length_cm = config.BELT_LENGTH_CM
        self.belt_speed_cm_s = config.BELT_SPEED_CM_PER_S

        # Stats
        self.total_items = 0
        self.passed = 0
        self.rejected = 0
        self.jams = 0
        self.last_weight_class = CLASS_NONE
        self.last_current_delta = 0.0

        # Timer for delayed gate firing
        self._sort_timer = Timer(-1)
        self._pending_sort = None

        # Debounce: ignore new items for this duration after detection
        self._last_detect_ms = 0
        self._detect_cooldown_ms = 2000

    def set_baseline(self, baseline_mA):
        """Set empty-belt baseline current (from calibration)."""
        self._baseline_mA = baseline_mA

    def set_threshold(self, threshold_percent):
        """Adjust threshold from SCADA potentiometer (0-100%).

        Maps to range: tighter (lower %) → looser (higher %).
        """
        # Scale heavy threshold: 50% pot → default, 0%=tighter, 100%=looser
        scale = 0.5 + (threshold_percent / 100.0)
        self.threshold_heavy = config.WEIGHT_THRESHOLD_HEAVY * scale
        self.threshold_light = config.WEIGHT_THRESHOLD_LIGHT * scale

    def detect_item(self):
        """Check if current spike indicates item on belt.

        Returns True if item detected (above minimum threshold).
        """
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_detect_ms) < self._detect_cooldown_ms:
            return False

        current_mA = self.pm.read_motor_current(2)  # Motor 2 = conveyor
        delta = abs(current_mA - self._baseline_mA)

        if self._baseline_mA > 0:
            delta_ratio = delta / self._baseline_mA
        else:
            delta_ratio = 0.0

        if delta_ratio > config.WEIGHT_THRESHOLD_MIN:
            self._last_detect_ms = now
            self.last_current_delta = delta_ratio
            return True

        return False

    def classify_weight(self, current_reading=None):
        """Classify item weight from current delta.

        Args:
            current_reading: current delta ratio, or None to use last detected

        Returns:
            CLASS_PASS, CLASS_REJECT_HEAVY, CLASS_REJECT_LIGHT, or CLASS_JAM
        """
        delta = current_reading if current_reading is not None else self.last_current_delta

        if delta > self.threshold_jam:
            return CLASS_JAM
        elif delta > self.threshold_heavy:
            return CLASS_REJECT_HEAVY
        elif delta < self.threshold_light:
            return CLASS_REJECT_LIGHT
        else:
            return CLASS_PASS

    def schedule_sort(self, weight_class):
        """Calculate travel time and schedule servo gate firing.

        Args:
            weight_class: CLASS_PASS, CLASS_REJECT_HEAVY, etc.
        """
        self.last_weight_class = weight_class
        self.total_items += 1

        if weight_class == CLASS_JAM:
            # Immediate: stop belt
            self.mc.emergency_stop(2)
            self.jams += 1
            return

        # Calculate travel time
        if self.belt_speed_cm_s > 0:
            travel_time_ms = int((self.belt_length_cm / self.belt_speed_cm_s) * 1000)
        else:
            travel_time_ms = 4000  # fallback 4s

        # Store what to do when timer fires
        self._pending_sort = weight_class

        # Schedule gate firing
        self._sort_timer.init(period=travel_time_ms, mode=Timer.ONE_SHOT,
                              callback=self._fire_gate)

    def _fire_gate(self, timer):
        """Timer callback: actuate servo gate based on pending sort."""
        if self._pending_sort is None:
            return

        if self._pending_sort == CLASS_PASS:
            # Servo to PASS position (0°)
            self.mc.set_servo_angle(2, 0)
            self.passed += 1
        else:
            # Servo to REJECT position (180°)
            self.mc.set_servo_angle(2, 180)
            self.rejected += 1

        self._pending_sort = None

        # Reset gate after 1 second
        self._sort_timer.init(period=1000, mode=Timer.ONE_SHOT,
                              callback=self._reset_gate)

    def _reset_gate(self, timer):
        """Reset gate servo to neutral position."""
        self.mc.set_servo_angle(2, 90)

    def process(self):
        """Run one sort cycle: detect → classify → schedule.

        Call this every main loop iteration.
        Returns weight_class if item detected, None otherwise.
        """
        if not self.detect_item():
            return None

        weight_class = self.classify_weight()
        self.schedule_sort(weight_class)
        return weight_class

    def get_stats(self):
        """Return sorting statistics."""
        reject_rate = (self.rejected / self.total_items * 100) if self.total_items > 0 else 0
        return {
            'total_items': self.total_items,
            'passed': self.passed,
            'rejected': self.rejected,
            'jams': self.jams,
            'reject_rate': round(reject_rate, 1),
            'last_weight_class': self.last_weight_class,
            'last_current_delta': round(self.last_current_delta, 4),
            'threshold_heavy': round(self.threshold_heavy, 4),
        }


if __name__ == "__main__":
    print("=" * 40)
    print("  Sorter Test (simulated)")
    print("=" * 40)

    # Simulated test without hardware
    sorter = Sorter.__new__(Sorter)
    sorter._baseline_mA = 300.0
    sorter.threshold_light = config.WEIGHT_THRESHOLD_LIGHT
    sorter.threshold_heavy = config.WEIGHT_THRESHOLD_HEAVY
    sorter.threshold_jam = config.WEIGHT_THRESHOLD_JAM
    sorter.total_items = 0
    sorter.passed = 0
    sorter.rejected = 0
    sorter.jams = 0
    sorter.last_weight_class = CLASS_NONE
    sorter.last_current_delta = 0.0

    # Test classification
    test_deltas = [0.02, 0.08, 0.10, 0.20, 0.35]
    labels = ["too small", "light reject", "PASS", "heavy reject", "JAM"]

    print(f"\nBaseline: {sorter._baseline_mA}mA")
    print(f"Thresholds: light={sorter.threshold_light}, heavy={sorter.threshold_heavy}, jam={sorter.threshold_jam}")
    print()

    for delta, label in zip(test_deltas, labels):
        result = sorter.classify_weight(delta)
        print(f"  Delta={delta:.2f} → {result:15s} (expected: {label})")

    # Test threshold adjustment
    print("\nThreshold adjustment test:")
    for pot_pct in [0, 25, 50, 75, 100]:
        sorter.set_threshold(pot_pct)
        print(f"  Pot={pot_pct:3d}% → heavy_threshold={sorter.threshold_heavy:.4f}")

    print("\nSorter test complete")
