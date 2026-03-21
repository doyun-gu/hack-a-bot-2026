"""
GridBox — Power Manager
ADC-based power monitoring: bus voltage, motor currents, power calculations.
"""

from machine import Pin, ADC
import config


class PowerManager:
    """Reads ADC channels and computes voltage, current, power, efficiency."""

    def __init__(self, adc_bus_pin=None, adc_m1_pin=None, adc_m2_pin=None,
                 r_sense=None, divider_ratio=None):
        self.adc_bus = ADC(Pin(adc_bus_pin or config.ADC_BUS_VOLTAGE))
        self.adc_m1 = ADC(Pin(adc_m1_pin or config.ADC_MOTOR1_CURRENT))
        self.adc_m2 = ADC(Pin(adc_m2_pin or config.ADC_MOTOR2_CURRENT))
        self.r_sense = r_sense or config.CURRENT_SENSE_R
        self.divider_ratio = divider_ratio or config.VOLTAGE_DIVIDER_RATIO
        self.n_samples = config.ADC_SAMPLES_AVG

        # Tracking
        self._total_energy_mWs = 0.0
        self._useful_energy_mWs = 0.0
        self._last_read_ms = 0

    def _read_adc_avg(self, adc):
        """Read ADC with N-sample averaging for noise reduction."""
        total = 0
        for _ in range(self.n_samples):
            total += adc.read_u16()
        return total / self.n_samples

    def _adc_to_voltage(self, raw):
        """Convert raw ADC reading to voltage."""
        return raw * config.ADC_VREF / config.ADC_RESOLUTION

    def read_bus_voltage(self):
        """Read bus voltage in V (with divider correction)."""
        raw = self._read_adc_avg(self.adc_bus)
        return self._adc_to_voltage(raw) * self.divider_ratio

    def read_motor_current(self, motor_id):
        """Read motor current in mA.

        Args:
            motor_id: 1 or 2
        """
        adc = self.adc_m1 if motor_id == 1 else self.adc_m2
        raw = self._read_adc_avg(adc)
        v_sense = self._adc_to_voltage(raw)
        return (v_sense / self.r_sense) * 1000  # mA

    def read_all(self):
        """Read all channels and compute power metrics.

        Returns dict:
            bus_v: bus voltage (V)
            m1_mA: motor 1 current (mA)
            m2_mA: motor 2 current (mA)
            m1_W: motor 1 power (W)
            m2_W: motor 2 power (W)
            total_W: total power (W)
            excess_W: available excess power (W)
            efficiency: useful/total percentage
        """
        bus_v = self.read_bus_voltage()
        m1_mA = self.read_motor_current(1)
        m2_mA = self.read_motor_current(2)

        m1_W = bus_v * m1_mA / 1000
        m2_W = bus_v * m2_mA / 1000
        total_W = m1_W + m2_W

        # Excess = what's available vs nominal capacity
        nominal_W = bus_v * config.MOTOR_CURRENT_MAX_MA / 1000 * 2
        excess_W = max(0, nominal_W - total_W) if nominal_W > 0 else 0

        # Efficiency: assume useful = actual, total = nominal
        efficiency = (total_W / nominal_W * 100) if nominal_W > 0 else 0

        return {
            'bus_v': round(bus_v, 2),
            'm1_mA': round(m1_mA, 1),
            'm2_mA': round(m2_mA, 1),
            'm1_W': round(m1_W, 3),
            'm2_W': round(m2_W, 3),
            'total_W': round(total_W, 3),
            'excess_W': round(excess_W, 3),
            'efficiency': round(efficiency, 1),
        }

    def get_efficiency(self):
        """Return power efficiency percentage."""
        data = self.read_all()
        return data['efficiency']

    def is_overloaded(self):
        """Return True if bus voltage is below critical threshold."""
        return self.read_bus_voltage() < config.BUS_VOLTAGE_CRITICAL

    def is_low_voltage(self):
        """Return True if bus voltage is below warning threshold."""
        return self.read_bus_voltage() < config.BUS_VOLTAGE_LOW

    def get_excess_power(self):
        """Return watts available for rerouting."""
        data = self.read_all()
        return data['excess_W']


if __name__ == "__main__":
    import time

    print("=" * 40)
    print("  Power Manager Test")
    print("=" * 40)

    pm = PowerManager()

    while True:
        data = pm.read_all()
        overloaded = pm.is_overloaded()
        low = pm.is_low_voltage()

        status = "OVERLOADED!" if overloaded else ("LOW" if low else "OK")
        print(f"Bus={data['bus_v']:.2f}V [{status}] | "
              f"M1={data['m1_mA']:.0f}mA ({data['m1_W']:.2f}W) | "
              f"M2={data['m2_mA']:.0f}mA ({data['m2_W']:.2f}W) | "
              f"Total={data['total_W']:.2f}W | "
              f"Excess={data['excess_W']:.2f}W | "
              f"Eff={data['efficiency']:.0f}%")

        time.sleep_ms(200)
