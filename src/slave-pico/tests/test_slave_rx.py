"""
GridBox — Slave Pico B: Receive Test
Receives telemetry from master (test_master_tx.py) via nRF and prints to USB serial.
Connect this Pico to laptop via USB — open serial monitor to see data.

Upload: mpremote cp src/slave-pico/tests/test_slave_rx.py :main.py && mpremote reset
Then:  mpremote connect /dev/tty.usbmodem* repl
"""

from machine import Pin, SPI
import struct
import time

# ── Pins ──
LED = Pin(25, Pin.OUT)
ce = Pin(0, Pin.OUT, value=0)
csn = Pin(1, Pin.OUT, value=1)
spi = SPI(0, baudrate=4_000_000, sck=Pin(2), mosi=Pin(3), miso=Pin(16))

# ── Config (must match master) ──
CHANNEL = 100
TX_ADDR = b'GRIDM'  # master's TX = our RX

# ── nRF24 minimal driver ──
def nrf_write(reg, val):
    csn.value(0)
    if isinstance(val, int):
        spi.write(bytes([0x20 | reg, val]))
    else:
        spi.write(bytes([0x20 | reg]) + val)
    csn.value(1)

def nrf_read(reg, n=1):
    csn.value(0)
    spi.write(bytes([reg & 0x1F]))
    data = spi.read(n)
    csn.value(1)
    return data[0] if n == 1 else data

def nrf_recv():
    """Check for received payload. Returns 32 bytes or None."""
    status = nrf_read(0x07)
    if status & 0x40:  # RX_DR — data ready
        csn.value(0)
        spi.write(b'\x61')  # R_RX_PAYLOAD
        payload = spi.read(32)
        csn.value(1)
        nrf_write(0x07, 0x70)  # clear flags
        return payload
    return None

def nrf_init_rx():
    """Init nRF as receiver."""
    ce.value(0)
    nrf_write(0x00, 0x0F)  # PWR_UP, EN_CRC, CRC 2-byte, PRX
    nrf_write(0x01, 0x01)  # EN_AA pipe 0
    nrf_write(0x02, 0x01)  # EN_RXADDR pipe 0
    nrf_write(0x03, 0x03)  # 5-byte address
    nrf_write(0x04, 0x4A)  # retry settings (for ACK)
    nrf_write(0x05, CHANNEL)
    nrf_write(0x06, 0x26)  # 250kbps, 0dBm
    nrf_write(0x11, 32)    # RX payload width pipe 0 = 32 bytes
    # Set RX address pipe 0 = master's TX address
    csn.value(0)
    spi.write(b'\x2A' + TX_ADDR)
    csn.value(1)
    nrf_write(0x07, 0x70)  # clear flags
    # Flush RX
    csn.value(0)
    spi.write(b'\xE2')
    csn.value(1)
    ce.value(1)  # start listening
    time.sleep_ms(5)
    print(f"  nRF RX mode, channel {CHANNEL}, listening...")

# ══════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════
print("=" * 50)
print("  SLAVE RX — Receive from Master")
print("  Connect this Pico to laptop USB")
print("=" * 50)
print()

nrf_init_rx()

count = 0
last_seq = -1
missed = 0
t_start = time.ticks_ms()
t_last = time.ticks_ms()

print("Waiting for packets from master...")
print("  Format: seq | servo | motor | IMU RMS")
print()

while True:
    payload = nrf_recv()

    if payload:
        LED.toggle()
        t_last = time.ticks_ms()

        # Unpack: type, seq, servo_deg*10, motor%, imu_rms, servo_ch, motor_ch
        try:
            ptype, seq, servo_raw, motor_pct, imu_rms, servo_ch, motor_ch = \
                struct.unpack('<BBHHfBB', payload[:12])

            servo_deg = servo_raw / 10.0
            count += 1

            # Track missed packets
            if last_seq >= 0:
                expected = (last_seq + 1) & 0xFF
                if seq != expected:
                    gap = (seq - expected) & 0xFF
                    missed += gap
            last_seq = seq

            elapsed = time.ticks_diff(time.ticks_ms(), t_start) // 1000
            reliability = count / (count + missed) * 100 if (count + missed) > 0 else 0

            print(f"[{count:4d}] seq={seq:3d} servo={servo_deg:5.1f}° motor={motor_pct:3d}% "
                  f"imu={imu_rms:.2f}g  ch:s={servo_ch}/m={motor_ch}  "
                  f"rx={reliability:.1f}% ({elapsed}s)")

        except Exception as e:
            print(f"  Unpack error: {e}")

    else:
        # Check for link timeout
        age = time.ticks_diff(time.ticks_ms(), t_last)
        if age > 3000 and count > 0:
            print(f"  ⚠ No packet for {age}ms — LINK LOST?")
            t_last = time.ticks_ms()  # reset to avoid spam

    time.sleep_ms(10)
