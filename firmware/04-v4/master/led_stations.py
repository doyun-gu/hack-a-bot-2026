"""
GridBox — LED Production Stations
4 LEDs showing product journey: INTAKE → WEIGH → RESULT → SORTED.
Uses the P1-P4 load GPIO pins via MOSFET switches.
"""

from machine import Pin, Timer
import time
import config

# Station IDs
STATION_INTAKE = 0    # Item detected on belt
STATION_WEIGH = 1     # Measuring weight
STATION_RESULT = 2    # Pass (green blink) / Reject (red blink)
STATION_SORTED = 3    # Item sorted into correct bin

# Map stations to GPIO pins (reuse MOSFET load pins)
STATION_PINS = [
    config.MOSFET_MOTOR1,     # Station 0: INTAKE
    config.MOSFET_MOTOR2,     # Station 1: WEIGH
    config.MOSFET_LED_BANK,   # Station 2: RESULT
    config.MOSFET_RECYCLE,    # Station 3: SORTED
]


class LEDStations:
    """4-LED production station sequence controller."""

    def __init__(self, pin_list=None):
        """
        Args:
            pin_list: list of 4 GPIO pin numbers, or None for defaults
        """
        pins = pin_list or STATION_PINS
        self.leds = []
        for p in pins:
            self.leds.append(Pin(p, Pin.OUT, value=0))

        # Status LED for pass/fail indication
        self.led_green = Pin(config.LED_GREEN, Pin.OUT, value=0)
        self.led_red = Pin(config.LED_RED, Pin.OUT, value=0)

        # Timing
        self.station_duration_ms = 500  # how long each station stays lit
        self._sequence_active = False
        self._timer = Timer(-1)

    def set_station(self, station_id, on):
        """Turn a station LED on/off.

        Args:
            station_id: 0-3
            on: True/False
        """
        if 0 <= station_id < len(self.leds):
            self.leds[station_id].value(1 if on else 0)

    def all_off(self):
        """Turn off all station LEDs."""
        for led in self.leds:
            led.value(0)
        self.led_green.value(0)
        self.led_red.value(0)

    def run_sequence(self, weight_class, blocking=True):
        """Light LEDs in order showing item's journey.

        Sequence:
            1. INTAKE lights up (item detected)
            2. WEIGH lights up (measuring)
            3. RESULT lights up (green=pass, red=reject)
            4. SORTED lights up (item sorted)

        Args:
            weight_class: "PASS", "REJECT_HEAVY", "REJECT_LIGHT", "JAM"
            blocking: if True, blocks until sequence complete
        """
        self._sequence_active = True
        is_pass = (weight_class == "PASS")

        if blocking:
            self._run_blocking(is_pass)
        else:
            self._run_nonblocking(is_pass)

    def _run_blocking(self, is_pass):
        """Run LED sequence (blocking)."""
        # Station 0: INTAKE
        self.all_off()
        self.set_station(STATION_INTAKE, True)
        time.sleep_ms(self.station_duration_ms)

        # Station 1: WEIGH
        self.set_station(STATION_INTAKE, False)
        self.set_station(STATION_WEIGH, True)
        time.sleep_ms(self.station_duration_ms)

        # Station 2: RESULT (green or red)
        self.set_station(STATION_WEIGH, False)
        self.set_station(STATION_RESULT, True)
        if is_pass:
            self.led_green.value(1)
        else:
            self.led_red.value(1)
        time.sleep_ms(self.station_duration_ms)

        # Station 3: SORTED
        self.set_station(STATION_RESULT, False)
        self.set_station(STATION_SORTED, True)
        time.sleep_ms(self.station_duration_ms)

        # All off
        self.all_off()
        self._sequence_active = False

    def _run_nonblocking(self, is_pass):
        """Start LED sequence (non-blocking via timer chain)."""
        self._nb_step = 0
        self._nb_pass = is_pass
        self._nb_tick(None)

    def _nb_tick(self, timer):
        """Timer callback for non-blocking sequence."""
        step = self._nb_step

        self.all_off()

        if step == 0:
            self.set_station(STATION_INTAKE, True)
        elif step == 1:
            self.set_station(STATION_WEIGH, True)
        elif step == 2:
            self.set_station(STATION_RESULT, True)
            if self._nb_pass:
                self.led_green.value(1)
            else:
                self.led_red.value(1)
        elif step == 3:
            self.set_station(STATION_SORTED, True)
        else:
            self.all_off()
            self._sequence_active = False
            return

        self._nb_step += 1
        self._timer.init(period=self.station_duration_ms, mode=Timer.ONE_SHOT,
                         callback=self._nb_tick)

    def is_active(self):
        """Return True if a sequence is currently running."""
        return self._sequence_active


if __name__ == "__main__":
    print("=" * 40)
    print("  LED Station Sequence Test")
    print("=" * 40)

    stations = LEDStations()

    # Test PASS sequence
    print("\nRunning PASS sequence...")
    stations.run_sequence("PASS", blocking=True)
    print("PASS sequence complete")

    time.sleep(1)

    # Test REJECT sequence
    print("\nRunning REJECT sequence...")
    stations.run_sequence("REJECT_HEAVY", blocking=True)
    print("REJECT sequence complete")

    time.sleep(1)

    # Test individual stations
    print("\nIndividual station test:")
    for i in range(4):
        name = ["INTAKE", "WEIGH", "RESULT", "SORTED"][i]
        print(f"  Station {i}: {name}")
        stations.set_station(i, True)
        time.sleep_ms(500)
        stations.set_station(i, False)

    stations.all_off()
    print("\nLED station test complete")
