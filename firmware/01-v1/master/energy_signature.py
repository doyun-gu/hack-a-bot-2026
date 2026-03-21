"""
GridBox — Energy Signature Anomaly Detection
Wooseong's design: detect motor faults from current draw patterns.
Samples ADC at 500Hz, computes 4-metric signature, scores divergence.
"""

from machine import Pin, ADC
import time
import math
import config


class EnergySignature:
    """Represents a current draw signature (4 metrics)."""

    def __init__(self, mean_current=0.0, std_current=0.0,
                 crossing_rate=0.0, max_deviation=0.0):
        self.mean_current = mean_current
        self.std_current = std_current
        self.crossing_rate = crossing_rate
        self.max_deviation = max_deviation

    def __repr__(self):
        return (f"Sig(mean={self.mean_current:.3f}, std={self.std_current:.3f}, "
                f"xing={self.crossing_rate:.1f}, maxdev={self.max_deviation:.3f})")


def zero_crossings(samples, mean_val):
    """Count how many times signal crosses the mean per window."""
    count = 0
    above = samples[0] > mean_val
    for s in samples[1:]:
        now_above = s > mean_val
        if now_above != above:
            count += 1
            above = now_above
    return count


def compute_signature(samples):
    """Calculate 4-metric signature from raw ADC samples.

    Args:
        samples: list of float current values

    Returns:
        EnergySignature
    """
    n = len(samples)
    if n == 0:
        return EnergySignature()

    # Mean
    mean_val = sum(samples) / n

    # Standard deviation
    variance = sum((s - mean_val) ** 2 for s in samples) / n
    std_val = math.sqrt(variance)

    # Zero crossings (relative to mean)
    xing = zero_crossings(samples, mean_val)

    # Max deviation from mean
    max_dev = max(abs(s - mean_val) for s in samples)

    return EnergySignature(mean_val, std_val, xing, max_dev)


def divergence_score(baseline, current):
    """Compute weighted divergence score between baseline and current signature.

    Weights from Wooseong's design:
        mean=0.30, std=0.25, crossing=0.25, maxdev=0.20

    Returns:
        float 0.0 (identical) to 1.0+ (very different)
    """
    def _metric_div(base, curr, cap=2.0):
        if base == 0:
            return min(curr, cap)
        return min(abs(curr - base) / base, cap)

    d_mean = _metric_div(baseline.mean_current, current.mean_current)
    d_std = _metric_div(baseline.std_current, current.std_current)
    d_xing = _metric_div(baseline.crossing_rate, current.crossing_rate)
    d_maxdev = _metric_div(baseline.max_deviation, current.max_deviation)

    score = (d_mean * config.ES_WEIGHT_MEAN +
             d_std * config.ES_WEIGHT_STD +
             d_xing * config.ES_WEIGHT_CROSSING +
             d_maxdev * config.ES_WEIGHT_MAXDEV)

    return score


class EnergySignatureMonitor:
    """Continuous energy signature monitoring.

    Designed to run on Core 1 alongside IMU reader.
    """

    def __init__(self, adc_pin=None):
        pin = adc_pin or config.ADC_MOTOR1_CURRENT
        self.adc = ADC(Pin(pin))
        self.baseline = None
        self._current_sig = EnergySignature()
        self._score = 0.0
        self._is_anomaly = False
        self._learning = False
        self._samples = []

    def _read_current_mA(self):
        """Read single ADC sample as current in mA."""
        raw = self.adc.read_u16()
        voltage = raw * config.ADC_VREF / config.ADC_RESOLUTION
        return (voltage / config.CURRENT_SENSE_R) * 1000

    def learn_baseline(self, duration_s=None):
        """Capture healthy baseline signature.

        Args:
            duration_s: learning duration (default from config)
        """
        duration_s = duration_s or config.ES_LEARNING_DURATION_S
        total_samples = config.ES_SAMPLE_RATE_HZ * duration_s
        interval_us = 1_000_000 // config.ES_SAMPLE_RATE_HZ

        print(f"[ES] Learning baseline ({duration_s}s, {total_samples} samples)...")
        self._learning = True

        samples = []
        for i in range(total_samples):
            samples.append(self._read_current_mA())
            time.sleep_us(interval_us)

            # Progress every 5 seconds
            if (i + 1) % (config.ES_SAMPLE_RATE_HZ * 5) == 0:
                elapsed = (i + 1) // config.ES_SAMPLE_RATE_HZ
                print(f"[ES] Learning... {elapsed}/{duration_s}s")

        self.baseline = compute_signature(samples)
        self._learning = False
        print(f"[ES] Baseline: {self.baseline}")

    def sample_window(self):
        """Sample one window (1 second) and update signature + score.

        Call this periodically from the main loop or Core 1.
        """
        interval_us = 1_000_000 // config.ES_SAMPLE_RATE_HZ
        samples = []

        for _ in range(config.ES_WINDOW_SIZE):
            samples.append(self._read_current_mA())
            time.sleep_us(interval_us)

        self._current_sig = compute_signature(samples)

        if self.baseline is not None:
            self._score = divergence_score(self.baseline, self._current_sig)
            self._is_anomaly = self._score > config.ES_ANOMALY_THRESHOLD
        else:
            self._score = 0.0
            self._is_anomaly = False

    def get_score(self):
        """Return current divergence score (0.0 = healthy)."""
        return self._score

    def get_signature(self):
        """Return current EnergySignature."""
        return self._current_sig

    def is_anomaly(self):
        """Return True if divergence exceeds threshold."""
        return self._is_anomaly

    def is_learning(self):
        """Return True if currently learning baseline."""
        return self._learning


if __name__ == "__main__":
    print("=" * 40)
    print("  Energy Signature Test")
    print("=" * 40)

    mon = EnergySignatureMonitor(adc_pin=config.ADC_MOTOR1_CURRENT)

    # Learn baseline (short for testing)
    mon.learn_baseline(duration_s=5)

    # Monitor
    print("\nMonitoring... (press Ctrl+C to stop)")
    while True:
        mon.sample_window()
        sig = mon.get_signature()
        score = mon.get_score()
        anomaly = "ANOMALY!" if mon.is_anomaly() else "OK"

        print(f"Score={score:.3f} [{anomaly}] | "
              f"mean={sig.mean_current:.1f}mA "
              f"std={sig.std_current:.2f} "
              f"xing={sig.crossing_rate:.0f} "
              f"maxdev={sig.max_deviation:.2f}")

        time.sleep_ms(100)
