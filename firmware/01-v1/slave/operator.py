"""
GridBox — Operator Input
Joystick (X/Y + button) and potentiometer reading with debounce.
"""

from machine import Pin, ADC
import time
import config


class OperatorInput:
    """Joystick + potentiometer input handler with debounce."""

    def __init__(self, joy_x_pin=None, joy_y_pin=None, joy_btn_pin=None, pot_pin=None):
        self.joy_x = ADC(Pin(joy_x_pin or config.JOY_X_PIN))
        self.joy_y = ADC(Pin(joy_y_pin or config.JOY_Y_PIN))
        self.joy_btn = Pin(joy_btn_pin or config.JOY_BTN_PIN, Pin.IN, Pin.PULL_UP)
        self.pot = ADC(Pin(pot_pin or config.POT_PIN))

        # Deadzone
        self.centre = config.JOY_CENTRE
        self.deadzone = config.JOY_DEADZONE

        # Button debounce
        self._btn_state = False
        self._btn_last_change_ms = 0
        self._btn_raw = False

        # Long press
        self._btn_press_start_ms = 0
        self._long_press_detected = False

        # Previous direction (for change detection)
        self._prev_direction = "CENTRE"

    def read_joystick(self):
        """Read joystick X, Y, and button with deadzone filtering.

        Returns:
            tuple (x, y, button) where x/y are 0-100 (50=centre),
            button is True/False
        """
        raw_x = self.joy_x.read_u16()
        raw_y = self.joy_y.read_u16()

        # Apply deadzone and map to 0-100
        x = self._apply_deadzone(raw_x)
        y = self._apply_deadzone(raw_y)

        # Debounce button
        button = self._debounce_button()

        return (x, y, button)

    def _apply_deadzone(self, raw):
        """Apply deadzone and map ADC value to 0-100."""
        delta = raw - self.centre
        if abs(delta) < self.deadzone:
            return 50  # centre

        # Map remaining range to 0-100
        max_range = self.centre - self.deadzone
        if max_range <= 0:
            return 50

        normalized = delta / max_range  # -1.0 to 1.0
        result = int(50 + normalized * 50)
        return max(0, min(100, result))

    def _debounce_button(self):
        """Debounce button press. Requires stable reading for DEBOUNCE_MS."""
        current_raw = not self.joy_btn.value()  # active low
        now = time.ticks_ms()

        if current_raw != self._btn_raw:
            self._btn_raw = current_raw
            self._btn_last_change_ms = now

        if time.ticks_diff(now, self._btn_last_change_ms) >= config.DEBOUNCE_MS:
            if current_raw != self._btn_state:
                self._btn_state = current_raw

                # Track press start for long press detection
                if self._btn_state:
                    self._btn_press_start_ms = now
                    self._long_press_detected = False
                else:
                    self._btn_press_start_ms = 0

        return self._btn_state

    def read_potentiometer(self):
        """Read potentiometer as 0-100% value."""
        raw = self.pot.read_u16()
        return int(raw / 65535 * 100)

    def get_direction(self):
        """Return joystick direction string.

        Returns:
            "UP", "DOWN", "LEFT", "RIGHT", "CENTRE", or "PRESS"
        """
        x, y, btn = self.read_joystick()

        if btn:
            return "PRESS"

        dx = x - 50
        dy = y - 50

        if abs(dx) < 10 and abs(dy) < 10:
            return "CENTRE"

        if abs(dx) > abs(dy):
            return "RIGHT" if dx > 0 else "LEFT"
        else:
            return "DOWN" if dy > 0 else "UP"

    def get_threshold(self):
        """Return potentiometer mapped to weight threshold range.

        Maps 0-100% pot to config.POT_MIN_THRESHOLD to POT_MAX_THRESHOLD grams.
        """
        pot_pct = self.read_potentiometer()
        range_g = config.POT_MAX_THRESHOLD - config.POT_MIN_THRESHOLD
        return config.POT_MIN_THRESHOLD + (pot_pct / 100.0) * range_g

    def is_long_press(self):
        """Detect long press (held for LONG_PRESS_MS).

        Returns True once per long press (resets after release).
        """
        if not self._btn_state or self._long_press_detected:
            return False

        if self._btn_press_start_ms == 0:
            return False

        elapsed = time.ticks_diff(time.ticks_ms(), self._btn_press_start_ms)
        if elapsed >= config.LONG_PRESS_MS:
            self._long_press_detected = True
            return True

        return False

    def direction_changed(self):
        """Return True if joystick direction changed since last call."""
        direction = self.get_direction()
        changed = direction != self._prev_direction
        self._prev_direction = direction
        return changed


if __name__ == "__main__":
    print("=" * 40)
    print("  Operator Input Test")
    print("  Move joystick + turn pot")
    print("=" * 40)

    op = OperatorInput()

    while True:
        x, y, btn = op.read_joystick()
        pot = op.read_potentiometer()
        direction = op.get_direction()
        threshold = op.get_threshold()
        long_press = op.is_long_press()

        btn_str = " BTN" if btn else ""
        long_str = " LONG!" if long_press else ""

        print(f"Joy: X={x:3d} Y={y:3d} Dir={direction:6s}{btn_str}{long_str} | "
              f"Pot={pot:3d}% Thr={threshold:.0f}g")

        time.sleep_ms(100)
