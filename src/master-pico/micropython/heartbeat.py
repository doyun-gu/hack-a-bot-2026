"""
Heartbeat LED — always-on system status indicator.

Works like a network switch LED:
- Normal:   steady comfortable blink (400ms) — system alive
- Activity: brief fast burst on nRF TX/RX — data moving
- Fault:    rapid blink (100ms) — something wrong
- Boot:     fast blink (80ms) — starting up

Usage:
    import heartbeat

    heartbeat.set_state("normal")    # comfortable blink — all good
    heartbeat.set_state("fault")     # rapid blink — error
    heartbeat.set_state("boot")      # fast blink — starting up
    heartbeat.set_state("off")       # LED off

    heartbeat.activity()             # brief fast burst (auto-reverts)

Works on both Pico 1 (RP2040) and Pico 2 (RP2350).
"""

from machine import Pin, Timer
import time

# Find the LED pin
try:
    _led = Pin("LED", Pin.OUT)
except (ValueError, TypeError):
    _led = Pin(25, Pin.OUT)

# State
_state = "boot"
_tick = 0
_timer = Timer()

# Activity tracking — brief speed-up on TX/RX
_activity_until = 0  # ticks_ms when activity burst ends

# Blink rates (half-period in ms — full cycle = 2x this value)
_rates = {
    "boot":    80,    # fast — starting up
    "normal":  400,   # comfortable — clearly alive, easy to see
    "active":  100,   # brief burst — data is moving (TX/RX)
    "fault":   120,   # rapid — something wrong, still readable
    "off":     0,     # LED stays off
}


def _update(t):
    global _tick, _activity_until

    _tick += 1
    now_ms = _tick * 10  # each tick = 10ms

    # Determine current blink rate
    if _state == "off":
        _led.value(0)
        return

    # Check if we're in an activity burst
    if _activity_until > 0 and now_ms < _activity_until:
        rate = _rates["active"]
    else:
        _activity_until = 0
        rate = _rates.get(_state, _rates["normal"])

    if rate == 0:
        _led.value(0)
        return

    # Simple square wave blink
    phase = now_ms % (rate * 2)
    _led.value(1 if phase < rate else 0)


def set_state(state):
    """Set base LED state: boot, normal, fault, off"""
    global _state
    _state = state


def activity(duration_ms=500):
    """Brief fast blink burst — call on nRF TX/RX.

    LED speeds up for duration_ms then auto-reverts to base state.
    Multiple calls extend the burst.
    """
    global _activity_until
    now_ms = _tick * 10
    _activity_until = now_ms + duration_ms


def get_state():
    """Return current base state."""
    return _state


# Start timer at 100Hz (10ms resolution)
_timer.init(freq=100, mode=Timer.PERIODIC, callback=_update)

# Default: boot mode (fast blink until main.py sets it to normal)
set_state("boot")
