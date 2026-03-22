"""
GridBox — Slave Pico B: Full Receiver + MAX7219 Display + USB Serial
Receives mock telemetry from master, shows on 7-segment display, prints to laptop.

Display modes (cycles automatically):
  Normal:  "SP60 A 90"  (motor speed + servo angle)
  Fault:   "FAULt"      (flashing, when IMU > 2g)
  Link:    "LInE OFF"   (no packet for 3s)
  Stats:   " 42 PASS"   (items passed) / " 5 rEJ" (items rejected)

nRF:     CE=GP0, CSN=GP1, SCK=GP2, MOSI=GP3, MISO=GP16
MAX7219: CLK=GP10, DIN=GP11, CS=GP13

Upload slave:  mpremote cp src/slave-pico/tests/test_slave_full.py :main.py && mpremote reset
Upload master: mpremote cp src/master-pico/tests/test_master_mock_tx.py :main.py && mpremote reset
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
#  MAX7219 DRIVER (raw segment mode)
# ══════════════════════════════════════════

SEG = {
    '0': 0x7E, '1': 0x30, '2': 0x6D, '3': 0x79, '4': 0x33,
    '5': 0x5B, '6': 0x5F, '7': 0x70, '8': 0x7F, '9': 0x7B,
    'A': 0x77, 'b': 0x1F, 'C': 0x4E, 'd': 0x3D, 'E': 0x4F, 'F': 0x47,
    'G': 0x5E, 'H': 0x37, 'I': 0x30, 'J': 0x38, 'L': 0x0E,
    'n': 0x15, 'O': 0x7E, 'P': 0x67, 'r': 0x05, 'S': 0x5B,
    't': 0x0F, 'U': 0x3E, 'u': 0x1C, 'y': 0x3B,
    '-': 0x01, ' ': 0x00, '_': 0x08, '.': 0x80,
}

def m_write(addr, data):
    cs7.value(0)
    spi1.write(bytes([addr, data]))
    cs7.value(1)

def m_init():
    m_write(0x0F, 0x00)
    m_write(0x0C, 0x01)
    m_write(0x0B, 0x07)
    m_write(0x09, 0x00)  # raw segment mode
    m_write(0x0A, 0x08)
    m_clear()

def m_clear():
    for d in range(1, 9):
        m_write(d, 0x00)

def m_show(text):
    """Show up to 8 chars (right-aligned)."""
    text = text[:8]
    while len(text) < 8:
        text = ' ' + text
    for i, ch in enumerate(text):
        seg = SEG.get(ch, 0x00)
        m_write(8 - i, seg)

def m_brightness(level):
    m_write(0x0A, min(15, max(0, level)))

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
    nrf_write(0x00, 0x0F)
    nrf_write(0x01, 0x01)
    nrf_write(0x02, 0x01)
    nrf_write(0x03, 0x03)
    nrf_write(0x04, 0x4A)
    nrf_write(0x05, CHANNEL)
    nrf_write(0x06, 0x26)
    nrf_write(0x11, 32)
    csn.value(0); spi0.write(b'\x2A' + TX_ADDR); csn.value(1)
    nrf_write(0x07, 0x70)
    csn.value(0); spi0.write(b'\xE2'); csn.value(1)
    ce.value(1)
    time.sleep_ms(5)

# ══════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════
print("=" * 50)
print("  SLAVE — Wireless Receiver + Display")
print("=" * 50)

# Init display
m_init()
m_show("BOOT    ")
print("MAX7219 OK")
time.sleep(1)

# Init nRF
nrf_init_rx()
m_show("LIStEn  ")
print("nRF RX ready, channel", CHANNEL)
print()
time.sleep(1)

count = 0
last_seq = -1
missed = 0
t_start = time.ticks_ms()
t_last = time.ticks_ms()
link_lost = False

# Display rotation
display_page = 0
t_display = time.ticks_ms()
DISPLAY_INTERVAL = 2000  # rotate every 2 seconds

# Latest data
latest = {
    'state': 0, 'servo': 0, 'motor': 0, 'bus_mV': 0,
    'm1_mA': 0, 'm2_mA': 0, 'imu': 0, 'total_W': 0,
    'eff': 0, 'items': 0, 'passed': 0, 'rejected': 0
}

STATE_NAMES = ['?', 'NORMAL', 'WARNING', 'FAULT']

print("Waiting for packets...")
print()

while True:
    now = time.ticks_ms()
    payload = nrf_recv()

    if payload:
        LED.toggle()
        t_last = now
        link_lost = False

        try:
            ptype, seq, state, servo, motor, bus_mV, m1_mA, m2_mA, \
                imu_100, watt_100, eff, items, passed, rejected = \
                struct.unpack('<BBBBBHHHHHBHHh', payload[:22])

            count += 1

            if last_seq >= 0:
                expected = (last_seq + 1) & 0xFF
                if seq != expected:
                    missed += (seq - expected) & 0xFF
            last_seq = seq

            latest['state'] = state
            latest['servo'] = servo
            latest['motor'] = motor
            latest['bus_mV'] = bus_mV
            latest['m1_mA'] = m1_mA
            latest['m2_mA'] = m2_mA
            latest['imu'] = imu_100 / 100.0
            latest['total_W'] = watt_100 / 100.0
            latest['eff'] = eff
            latest['items'] = items
            latest['passed'] = passed
            latest['rejected'] = rejected

            reliability = count / (count + missed) * 100 if (count + missed) > 0 else 0
            elapsed = time.ticks_diff(now, t_start) // 1000
            st = STATE_NAMES[state] if state < 4 else '?'

            print(f"[{count:4d}] {st:7s} servo={servo:3d}° motor={motor:3d}% "
                  f"bus={bus_mV}mV m1={m1_mA}mA imu={latest['imu']:.2f}g "
                  f"items={items}(P:{passed}/R:{rejected}) "
                  f"rx={reliability:.1f}% ({elapsed}s)")

        except Exception as e:
            print(f"  Unpack error: {e}")

    else:
        # Link timeout
        age = time.ticks_diff(now, t_last)
        if age > 3000 and not link_lost and count > 0:
            link_lost = True
            m_show("LInE OFF")
            print("  LINK LOST")

    # ── Update display ──
    if not link_lost and count > 0:
        # FAULT — show immediately, override everything
        if latest['state'] == 3:
            # Flash effect: alternate bright/dim
            if (now // 300) % 2 == 0:
                m_show("FAULt   ")
                m_brightness(15)
            else:
                m_clear()
                m_brightness(0)
        else:
            m_brightness(8)
            # Rotate pages every 2 seconds
            if time.ticks_diff(now, t_display) > DISPLAY_INTERVAL:
                t_display = now
                display_page = (display_page + 1) % 5

            if display_page == 0:
                m_show(f"SP{latest['motor']:3d}A{latest['servo']:3d}")
            elif display_page == 1:
                m_show(f"{latest['bus_mV']:4d}  mU")
            elif display_page == 2:
                m_show(f"{latest['passed']:3d} PASS")
            elif display_page == 3:
                m_show(f"  {latest['rejected']:2d} rEJ")
            elif display_page == 4:
                imu_int = int(latest['imu'] * 100)
                m_show(f"I{imu_int:3d}E{latest['eff']:3d}")

    time.sleep_ms(10)
