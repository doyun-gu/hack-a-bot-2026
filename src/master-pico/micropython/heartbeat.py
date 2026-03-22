"""
Heartbeat LED — blinks like a computer status LED.
Different patterns for different system states.

Usage:
    import heartbeat
    # LED blinks automatically — slow pulse = normal

    heartbeat.set_state("boot")      # fast blink — booting
    heartbeat.set_state("normal")    # slow pulse — all good
    heartbeat.set_state("busy")      # medium blink — processing
    heartbeat.set_state("warning")   # double blink — warning
    heartbeat.set_state("fault")     # rapid flash — error
    heartbeat.set_state("off")       # LED off

Works on both Pico 1 (RP2040) and Pico 2 (RP2350).
"""

from machine import Pin, Timer
import time

# Find the LED pin
try:
    _led = Pin("LED", Pin.OUT)
except:
    _led = Pin(25, Pin.OUT)

_state = "boot"
_tick = 0
_timer = Timer()

# Pattern definitions: list of (on_ms, off_ms) pairs that repeat
_patterns = {
    "boot":    [(50, 50)],                          # fast blink — starting up
    "normal":  [(100, 900)],                        # short pulse every 1s — like server LED
    "busy":    [(200, 200)],                        # medium blink — working
    "warning": [(100, 100), (100, 500)],            # double blink — attention needed
    "fault":   [(30, 30)],                          # rapid flash — error
    "off":     [(0, 1000)],                         # LED stays off
}

_pattern_step = 0
_next_change = 0
_led_on = False

def _update(t):
    global _pattern_step, _next_change, _led_on, _tick

    _tick += 1
    now = _tick * 10  # each tick = 10ms

    if now >= _next_change:
        pattern = _patterns.get(_state, _patterns["normal"])
        step = pattern[_pattern_step % len(pattern)]

        if _led_on:
            _led.value(0)
            _led_on = False
            _next_change = now + step[1]
            _pattern_step += 1
        else:
            on_time = step[0]
            if on_time > 0:
                _led.value(1)
                _led_on = True
            _next_change = now + (on_time if on_time > 0 else step[1])
            if on_time == 0:
                _pattern_step += 1

def set_state(state):
    """Change LED blink pattern: boot, normal, busy, warning, fault, off"""
    global _state, _pattern_step, _next_change, _led_on
    _state = state
    _pattern_step = 0
    _next_change = 0
    _led_on = False

# Start timer at 100Hz (10ms resolution)
_timer.init(freq=100, mode=Timer.PERIODIC, callback=_update)

# Default: boot mode (fast blink until code sets it to normal)
set_state("boot")
