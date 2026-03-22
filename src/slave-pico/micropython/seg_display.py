"""
MAX7219 7-Segment Display Driver
Simple API: show("LINK On"), show_number(4.8), clear()

Wiring: CLK=GP10, DIN=GP11, CS=GP13 (SPI1)
"""

from machine import Pin, SPI

# Segment encoding:  dp g f e d c b a
_CHARS = {
    '0': 0x7E, '1': 0x30, '2': 0x6D, '3': 0x79, '4': 0x33,
    '5': 0x5B, '6': 0x5F, '7': 0x70, '8': 0x7F, '9': 0x7B,
    'A': 0x77, 'b': 0x1F, 'C': 0x4E, 'd': 0x3D, 'E': 0x4F,
    'F': 0x47, 'H': 0x37, 'L': 0x0E, 'n': 0x15, 'o': 0x1D,
    'P': 0x67, 'r': 0x05, 't': 0x0F, 'U': 0x3E, 'S': 0x5B,
    '-': 0x01, '_': 0x08, ' ': 0x00,
    'i': 0x10, 'c': 0x0D, 'J': 0x38, 'G': 0x5E, 'y': 0x3B,
}

_spi = None
_cs = None


def init():
    """Initialise SPI1 and MAX7219."""
    global _spi, _cs
    _spi = SPI(1, baudrate=10_000_000, polarity=0, phase=0,
               sck=Pin(10), mosi=Pin(11))
    _cs = Pin(13, Pin.OUT, value=1)

    _write(0x0F, 0x00)  # display test off
    _write(0x0C, 0x01)  # normal operation
    _write(0x0B, 0x07)  # scan all 8 digits
    _write(0x09, 0x00)  # NO decode — raw segment mode
    _write(0x0A, 0x08)  # medium brightness


def _write(addr, data):
    _cs.value(0)
    _spi.write(bytes([addr, data]))
    _cs.value(1)


def brightness(level):
    """Set brightness 0-15."""
    _write(0x0A, level & 0x0F)


def clear():
    """Blank all digits."""
    for d in range(1, 9):
        _write(d, 0x00)


def show(text):
    """Display up to 8 characters. Right-aligned if shorter.

    Examples: show("LINK On"), show("FAULT 1"), show("PASS")
    """
    # Pad to 8 chars, right-aligned
    text = text[:8].rjust(8)

    # MAX7219 digit 1 = rightmost, digit 8 = leftmost
    for i, ch in enumerate(text):
        seg = _CHARS.get(ch, 0x00)
        _write(8 - i, seg)


def show_left(text):
    """Display up to 8 characters. Left-aligned."""
    text = text[:8].ljust(8)
    for i, ch in enumerate(text):
        seg = _CHARS.get(ch, 0x00)
        _write(8 - i, seg)


def flash(text, times=3, on_ms=300, off_ms=200):
    """Flash a message on/off."""
    import time
    for _ in range(times):
        show(text)
        time.sleep_ms(on_ms)
        clear()
        time.sleep_ms(off_ms)
    show(text)
