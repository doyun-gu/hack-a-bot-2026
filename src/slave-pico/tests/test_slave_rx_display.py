"""
GridBox — Slave Pico B: Receive + MAX7219 Display
Receives telemetry from master via nRF, shows on 7-segment display AND USB serial.

Display shows:
  - Normal: motor speed + servo angle (e.g. "SP 60 A 90")
  - Fault:  "FAULT" flashing when IMU RMS > 2.0g
  - Link:   "LINK OFF" if no packet for 3 seconds

MAX7219 wiring: CLK=GP10, DIN=GP11, CS=GP13
nRF wiring:     CE=GP0, CSN=GP1, SCK=GP2, MOSI=GP3, MISO=GP16

Upload slave:  mpremote cp src/slave-pico/tests/test_slave_rx_display.py :main.py && mpremote reset
Upload master: mpremote cp src/master-pico/tests/test_master_tx.py :main.py && mpremote reset
"""

from machine import Pin, SPI
import struct
import time

# ── Pins ──
LED = Pin(25, Pin.OUT)

# nRF on SPI0
ce = Pin(0, Pin.OUT, value=0)
csn = Pin(1, Pin.OUT, value=1)
spi0 = SPI(0, baudrate=4_000_000, sck=Pin(2), mosi=Pin(3), miso=Pin(16))

# MAX7219 on SPI1
spi1 = SPI(1, baudrate=10_000_000, polarity=0, phase=0, sck=Pin(10), mosi=Pin(11))
cs7 = Pin(13, Pin.OUT, value=1)

CHANNEL = 100
TX_ADDR = b'GRIDM'

# ══════════════════════════════════════════
#  MAX7219 DRIVER
# ══════════════════════════════════════════

# Segment patterns for letters (no-decode mode)
#   bit: DP A B C D E F G
SEG = {
    '0': 0x7E, '1': 0x30, '2': 0x6D, '3': 0x79, '4': 0x33,
    '5': 0x5B, '6': 0x5F, '7': 0x70, '8': 0x7F, '9': 0x7B,
    'A': 0x77, 'b': 0x1F, 'C': 0x4E, 'd': 0x3D, 'E': 0x4F, 'F': 0x47,
    'H': 0x37, 'L': 0x0E, 'n': 0x15, 'O': 0x7E, 'P': 0x67,
    'r': 0x05, 'S': 0x5B, 't': 0x0F, 'U': 0x3E, 'u': 0x1C,
    '-': 0x01, ' ': 0x00, '_': 0x08,
}

def m_write(addr, data):
    cs7.value(0)
    spi1.write(bytes([addr, data]))
    cs7.value(1)

def m_init():
    m_write(0x0F, 0x00)  # display test off
    m_write(0x0C, 0x01)  # normal operation
    m_write(0x0B, 0x07)  # scan all 8 digits
    m_write(0x09, 0x00)  # NO decode — raw segment control
    m_write(0x0A, 0x08)  # brightness medium
    m_clear()

def m_clear():
    for d in range(1, 9):
        m_write(d, 0x00)

def m_show(text):
    """Show up to 8 chars on display (right-aligned)."""
    text = text[:8]
    while len(text) < 8:
        text = ' ' + text
    for i, ch in enumerate(text):
        m_write(8 - i, SEG.get(ch, 0x00))

def m_show_number(n, digits=4, pos=1):
    """Show number at position (1=rightmost digit)."""
    s = str(abs(int(n))).rjust(digits)
    for i, ch in enumerate(s):
        m_write(pos + (digits - 1 - i), SEG.get(ch, 0x00))

def m_flash(text, times=3, on_ms=200, off_ms=200):
    for _ in range(times):
        m_show(text)
        time.sleep_ms(on_ms)
        m_clear()
        time.sleep_ms(off_ms)
    m_show(text)

# ══════════════════════════════════════════
#  nRF24 DRIVER (RX)
# ══════════════════════════════════════════

def nrf_write(reg, val):
    csn.value(0)
    if isinstance(val, int):
        spi0.write(bytes([0x20 | reg, val]))
    else:
        spi0.write(bytes([0x20 | reg]) + val)
    csn.value(1)

def nrf_read(reg, n=1):
    csn.value(0)
    spi0.write(bytes([reg & 0x1F]))
    data = spi0.read(n)
    csn.value(1)
    return data[0] if n == 1 else data

def nrf_recv():
    status = nrf_read(0x07)
    if status & 0x40:
        csn.value(0)
        spi0.write(b'\x61')
        payload = spi0.read(32)
        csn.value(1)
        nrf_write(0x07, 0x70)
        return payload
    return None

def nrf_init_rx():
    ce.value(0)
    nrf_write(0x00, 0x0F)  # PRX, PWR_UP, CRC
    nrf_write(0x01, 0x01)
    nrf_write(0x02, 0x01)
    nrf_write(0x03, 0x03)
    nrf_write(0x04, 0x4A)
    nrf_write(0x05, CHANNEL)
    nrf_write(0x06, 0x26)  # 250kbps
    nrf_write(0x11, 32)
    csn.value(0)
    spi0.write(b'\x2A' + TX_ADDR)
    csn.value(1)
    nrf_write(0x07, 0x70)
    csn.value(0)
    spi0.write(b'\xE2')  # flush RX
    csn.value(1)
    ce.value(1)
    time.sleep_ms(5)

# ══════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════
print("=" * 50)
print("  SLAVE RX + MAX7219 DISPLAY")
print("=" * 50)

# Init display
print("Init MAX7219...")
m_init()
m_show("BOOT    ")
time.sleep(1)

# Init nRF
print("Init nRF RX...")
nrf_init_rx()
m_show("LIStEn  ")
time.sleep(1)

print("Listening for master packets...")
print()

count = 0
last_seq = -1
missed = 0
t_start = time.ticks_ms()
t_last = time.ticks_ms()
link_lost = False
display_mode = "data"  # "data", "fault", "link_lost"

while True:
    now = time.ticks_ms()
    payload = nrf_recv()

    if payload:
        LED.toggle()
        t_last = now
        link_lost = False

        try:
            ptype, seq, servo_raw, motor_pct, imu_rms, servo_ch, motor_ch = \
                struct.unpack('<BBHHfBB', payload[:12])

            servo_deg = servo_raw / 10.0
            count += 1

            if last_seq >= 0:
                expected = (last_seq + 1) & 0xFF
                if seq != expected:
                    missed += (seq - expected) & 0xFF
            last_seq = seq

            reliability = count / (count + missed) * 100 if (count + missed) > 0 else 0

            # Decide what to show on display
            if imu_rms > 2.0:
                # FAULT — IMU vibration detected
                display_mode = "fault"
                m_show("FAULt   ")
                print(f"[{count:4d}] !! FAULT imu={imu_rms:.2f}g !!")
            else:
                display_mode = "data"
                # Show: "SP" + motor% on left, "A" + servo angle on right
                # e.g. motor=60%, servo=90° → "SP60 A 90" (approximate)
                m_text = f"SP{motor_pct:3d}A{int(servo_deg):3d}"
                m_show(m_text)

            # Print to USB serial
            elapsed = time.ticks_diff(now, t_start) // 1000
            print(f"[{count:4d}] seq={seq:3d} servo={servo_deg:5.1f}° "
                  f"motor={motor_pct:3d}% imu={imu_rms:.2f}g "
                  f"rx={reliability:.1f}% ({elapsed}s)")

        except Exception as e:
            print(f"  Unpack error: {e}")

    else:
        # Link timeout check
        age = time.ticks_diff(now, t_last)
        if age > 3000 and not link_lost:
            link_lost = True
            display_mode = "link_lost"
            m_show("LInE OFF")
            print(f"  LINK LOST — no packet for {age}ms")

    time.sleep_ms(10)
