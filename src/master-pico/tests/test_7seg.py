"""
Test: MAX7219 8-digit 7-segment display
Shows numbers to verify it works, then shows power data.

Wiring: VCC=5V, GND=GND, DIN=GP17, CS=GP18, CLK=GP19

Usage: mpremote run src/master-pico/tests/test_7seg.py
"""

from machine import Pin
import time

# Pins — using spare GPIOs (not conflicting with nRF SPI)
DIN = Pin(17, Pin.OUT)
CS = Pin(18, Pin.OUT, value=1)
CLK = Pin(19, Pin.OUT)

def send_byte(data):
    """Send one byte MSB first."""
    for i in range(8):
        CLK.value(0)
        DIN.value((data >> (7 - i)) & 1)
        CLK.value(1)

def send_cmd(reg, data):
    """Send command to MAX7219."""
    CS.value(0)
    send_byte(reg)
    send_byte(data)
    CS.value(1)

def init_display():
    """Initialise MAX7219."""
    send_cmd(0x0C, 1)  # shutdown off (normal operation)
    send_cmd(0x0B, 7)  # scan limit = all 8 digits
    send_cmd(0x09, 0xFF)  # decode mode = BCD for all digits
    send_cmd(0x0A, 4)  # intensity (0-15, 4 = medium)
    send_cmd(0x0F, 0)  # display test off

def clear():
    """Clear all digits."""
    for i in range(1, 9):
        send_cmd(i, 0x0F)  # blank

def show_number(num, decimals=0):
    """Display a number across 8 digits."""
    # Handle negative
    neg = num < 0
    num = abs(num)

    # Scale by decimals
    if decimals > 0:
        num = int(num * (10 ** decimals))
    else:
        num = int(num)

    # Fill digits right to left
    for digit in range(1, 9):
        if num > 0 or digit == 1:
            d = num % 10
            # Add decimal point
            if decimals > 0 and digit == decimals + 1:
                d |= 0x80  # set DP bit
            send_cmd(digit, d)
            num //= 10
        elif neg and digit == (len(str(int(abs(num)))) + 2 if decimals else len(str(int(abs(num)))) + 1):
            send_cmd(digit, 0x0A)  # dash for negative
        else:
            send_cmd(digit, 0x0F)  # blank

def show_text_raw(segments):
    """Show raw segment data for each digit (for custom characters)."""
    for i, seg in enumerate(segments):
        send_cmd(8 - i, seg)  # digit 8 = leftmost

print("=" * 40)
print("  MAX7219 7-Segment Display Test")
print("  DIN=GP17  CS=GP18  CLK=GP19")
print("=" * 40)

init_display()
clear()

# Test 1: Count up
print("\n1. Counting 0-99...")
for i in range(100):
    show_number(i)
    time.sleep_ms(50)

# Test 2: Show voltage
print("2. Showing voltage: 4.90V")
clear()
# Show "4.90" on right 4 digits, "U" pattern on left
send_cmd(1, 0x0F)  # blank
send_cmd(2, 0x0F)  # blank
send_cmd(3, 0x0F)  # blank
send_cmd(4, 0x0F)  # blank
send_cmd(5, 0)      # 0
send_cmd(6, 9)      # 9
send_cmd(7, 4 | 0x80)  # 4 with decimal point = "4."
send_cmd(8, 0x0F)  # blank
time.sleep(2)

# Test 3: Show current
print("3. Showing current: 350 mA")
clear()
send_cmd(1, 0x0F)
send_cmd(2, 0x0F)
send_cmd(3, 0x0F)
send_cmd(4, 0x0F)
send_cmd(5, 0x0F)
send_cmd(6, 0)      # 0
send_cmd(7, 5)      # 5
send_cmd(8, 3)      # 3 = "350"
time.sleep(2)

# Test 4: Live ADC reading
print("4. Live ADC reading on GP26 (Ctrl+C to stop)")
from machine import ADC
adc = ADC(Pin(26))
led = Pin(25, Pin.OUT)

tick = 0
try:
    while True:
        raw = adc.read_u16()
        voltage = raw * 3.3 / 65535 * 2  # with voltage divider
        mv = int(voltage * 1000)  # millivolts

        # Show millivolts: e.g., "4923" = 4.923V
        clear()
        for digit in range(1, 5):
            d = mv % 10
            if digit == 4:
                d |= 0x80  # decimal point after first digit
            send_cmd(digit, d)
            mv //= 10

        # Right side: tick counter
        t = tick % 10000
        for digit in range(5, 9):
            send_cmd(digit, t % 10)
            t //= 10

        led.toggle()
        tick += 1
        time.sleep_ms(200)

except KeyboardInterrupt:
    clear()
    send_cmd(0x0C, 0)  # shutdown
    led.value(0)
    print("\nStopped.")
