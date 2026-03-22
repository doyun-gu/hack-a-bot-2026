"""
GridBox — Calibration
Record empty-belt baseline and reference weight for weight-based sorting.
Save/load calibration to Pico flash as JSON.
"""

import json
import time
from machine import Pin, ADC
import config


class Calibration:
    """ADC calibration for weight sensing."""

    def __init__(self, power_manager=None):
        self.pm = power_manager
        self._baseline_mA = 0.0
        self._scale_factor = 1.0  # mA per gram
        self._reference_weight_g = 0.0
        self._calibrated = False

    def calibrate_empty(self):
        """Record empty belt/turntable current baseline.

        Averages CALIBRATION_SAMPLES readings.
        """
        print("[CAL] Calibrating empty belt... keep belt clear")
        time.sleep(1)

        total = 0.0
        n = config.CALIBRATION_SAMPLES

        for i in range(n):
            total += self.pm.read_motor_current(2)  # Motor 2 = conveyor
            time.sleep_ms(20)
            if (i + 1) % 25 == 0:
                print(f"[CAL] {i + 1}/{n} samples")

        self._baseline_mA = total / n
        print(f"[CAL] Empty baseline: {self._baseline_mA:.2f} mA")
        return self._baseline_mA

    def calibrate_reference(self, known_weight_g):
        """Record current with known weight, calculate scale factor.

        Args:
            known_weight_g: weight of reference item in grams
        """
        if self._baseline_mA == 0:
            print("[CAL] ERROR: calibrate empty belt first!")
            return 0.0

        print(f"[CAL] Place {known_weight_g}g reference item on belt...")
        time.sleep(2)

        total = 0.0
        n = config.CALIBRATION_SAMPLES

        for i in range(n):
            total += self.pm.read_motor_current(2)
            time.sleep_ms(20)
            if (i + 1) % 25 == 0:
                print(f"[CAL] {i + 1}/{n} samples")

        ref_mA = total / n
        delta_mA = ref_mA - self._baseline_mA

        if delta_mA > 0 and known_weight_g > 0:
            self._scale_factor = delta_mA / known_weight_g
            self._reference_weight_g = known_weight_g
            self._calibrated = True
            print(f"[CAL] Reference: {ref_mA:.2f} mA (delta={delta_mA:.2f} mA)")
            print(f"[CAL] Scale: {self._scale_factor:.4f} mA/g")
        else:
            print(f"[CAL] WARNING: invalid delta ({delta_mA:.2f} mA). Retry?")

        return self._scale_factor

    def save(self, filename=None):
        """Save calibration data to JSON file on Pico flash."""
        filename = filename or config.CALIBRATION_FILE
        data = {
            'baseline_mA': self._baseline_mA,
            'scale_factor': self._scale_factor,
            'reference_weight_g': self._reference_weight_g,
            'calibrated': self._calibrated,
        }
        try:
            with open(filename, 'w') as f:
                json.dump(data, f)
            print(f"[CAL] Saved to {filename}")
        except OSError as e:
            print(f"[CAL] Save error: {e}")

    def load(self, filename=None):
        """Load saved calibration from JSON file.

        Returns True if loaded successfully.
        """
        filename = filename or config.CALIBRATION_FILE
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self._baseline_mA = data.get('baseline_mA', 0.0)
            self._scale_factor = data.get('scale_factor', 1.0)
            self._reference_weight_g = data.get('reference_weight_g', 0.0)
            self._calibrated = data.get('calibrated', False)
            print(f"[CAL] Loaded: baseline={self._baseline_mA:.2f}mA, "
                  f"scale={self._scale_factor:.4f}mA/g")
            return True
        except OSError:
            print(f"[CAL] No calibration file found ({filename})")
            return False

    def get_baseline(self):
        """Return baseline current in mA."""
        return self._baseline_mA

    def get_scale(self):
        """Return scale factor (mA per gram)."""
        return self._scale_factor

    def is_calibrated(self):
        """Return True if valid calibration loaded or performed."""
        return self._calibrated

    def current_to_weight(self, current_mA):
        """Convert motor current to estimated weight in grams.

        Args:
            current_mA: raw motor current reading

        Returns:
            estimated weight in grams (0 if below baseline)
        """
        delta = current_mA - self._baseline_mA
        if delta <= 0 or self._scale_factor <= 0:
            return 0.0
        return delta / self._scale_factor

    def auto_load(self):
        """Try to load saved calibration on startup.

        Returns True if calibration was loaded.
        """
        return self.load()


if __name__ == "__main__":
    print("=" * 40)
    print("  Calibration Test")
    print("=" * 40)

    # Test save/load without hardware
    cal = Calibration.__new__(Calibration)
    cal.pm = None
    cal._baseline_mA = 300.0
    cal._scale_factor = 0.5
    cal._reference_weight_g = 50.0
    cal._calibrated = True

    # Save
    print("\nSaving test calibration...")
    cal.save('test_cal.json')

    # Load into new instance
    cal2 = Calibration.__new__(Calibration)
    cal2.pm = None
    cal2._baseline_mA = 0.0
    cal2._scale_factor = 1.0
    cal2._reference_weight_g = 0.0
    cal2._calibrated = False

    print("\nLoading test calibration...")
    loaded = cal2.load('test_cal.json')
    print(f"Loaded: {loaded}")
    print(f"Baseline: {cal2.get_baseline():.2f} mA")
    print(f"Scale: {cal2.get_scale():.4f} mA/g")
    print(f"Calibrated: {cal2.is_calibrated()}")

    # Test conversion
    print(f"\n350 mA → {cal2.current_to_weight(350):.1f}g")
    print(f"400 mA → {cal2.current_to_weight(400):.1f}g")
    print(f"250 mA → {cal2.current_to_weight(250):.1f}g (below baseline)")

    # Cleanup
    import os
    try:
        os.remove('test_cal.json')
    except OSError:
        pass

    print("\nCalibration test complete")
