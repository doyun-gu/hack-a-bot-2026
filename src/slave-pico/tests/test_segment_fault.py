from machine import Pin, SPI
import time

spi1 = SPI(1, baudrate=10000000, polarity=0, phase=0, sck=Pin(10), mosi=Pin(11))
cs = Pin(13, Pin.OUT, value=1)

def w(a, d):
    cs.value(0)
    spi1.write(bytes([a, d]))
    cs.value(1)
    time.sleep_ms(10)

# Force display test OFF first
w(0x0F, 0x00)
time.sleep_ms(50)
w(0x0F, 0x00)
time.sleep_ms(50)

# Init
w(0x0C, 0x01)  # normal operation
time.sleep_ms(50)
w(0x0B, 0x07)  # scan all 8 digits
w(0x0A, 0x08)  # brightness medium

# Try BCD decode first — show "1234" to confirm display works
w(0x09, 0xFF)  # BCD decode all digits
w(8, 0x0F)  # blank
w(7, 0x0F)  # blank
w(6, 0x0F)  # blank
w(5, 1)
w(4, 2)
w(3, 3)
w(2, 4)
w(1, 0x0F)  # blank
print("Should show: 1234")
print("If you see 1234, BCD mode works")
time.sleep(3)

# Now switch to raw segment mode for letters
w(0x09, 0x00)  # NO decode — raw segments
time.sleep_ms(50)

# Clear all
for d in range(1, 9):
    w(d, 0x00)
time.sleep_ms(50)

# Show "FAULt" using raw segments
w(8, 0x47)  # F
w(7, 0x77)  # A
w(6, 0x3E)  # U
w(5, 0x0E)  # L
w(4, 0x0F)  # t
w(3, 0x00)  # blank
w(2, 0x00)  # blank
w(1, 0x00)  # blank
print("Should show: FAULt")
print("Ctrl+C to stop")

while True:
    time.sleep(1)
