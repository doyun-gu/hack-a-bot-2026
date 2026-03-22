"""
GridBox — Demo Slave (Pico B)
Receives telemetry from Pico A, displays on MAX7219 + OLED.

REAL: nRF wireless, MAX7219 7-segment display, heartbeat LED
OPTIONAL: SSD1306 OLED (skips if not connected)

Flash as main.py for standalone demo day operation.
Usage: mpremote run src/demo/demo_slave.py
"""

from machine import Pin, SPI, I2C
import struct
import time

# ============ PIN CONFIG ============
SPI_SCK = 2
SPI_MOSI = 3
SPI_MISO = 16
NRF_CE = 0
NRF_CSN = 1
LED_PIN = 25

# SPI1 for MAX7219
SPI1_SCK = 10
SPI1_MOSI = 11
MAX7219_CS = 13

# I2C for OLED
I2C_SDA = 4
I2C_SCL = 5
OLED_ADDR = 0x3C

# nRF settings (reversed from master)
NRF_CHANNEL = 100
TX_ADDR = b'NSYNR'
RX_ADDR = b'NSYNT'

# ============ PACKET TYPES ============
PKT_POWER = 0x01
PKT_STATUS = 0x02
PKT_PRODUCTION = 0x03
PKT_HEARTBEAT = 0x04
PKT_ALERT = 0x05

# States
STATE_NAMES = ['BOOT', 'READY', 'RUN', 'FAULT', 'RECOVER', 'RECYCLE', 'DONE']

# ============ MAX7219 DRIVER ============
class SevenSeg:
    # Character map for 7-segment
    CHARS = {
        '0': 0x7E, '1': 0x30, '2': 0x6D, '3': 0x79, '4': 0x33,
        '5': 0x5B, '6': 0x5F, '7': 0x70, '8': 0x7F, '9': 0x7B,
        'A': 0x77, 'b': 0x1F, 'C': 0x4E, 'c': 0x0D, 'd': 0x3D,
        'E': 0x4F, 'F': 0x47, 'G': 0x5E, 'H': 0x37, 'h': 0x17,
        'I': 0x06, 'J': 0x3C, 'L': 0x0E, 'n': 0x15, 'O': 0x7E,
        'o': 0x1D, 'P': 0x67, 'r': 0x05, 'S': 0x5B, 't': 0x0F,
        'U': 0x3E, 'u': 0x1C, 'Y': 0x3B, '-': 0x01, '_': 0x08,
        ' ': 0x00, '.': 0x80, 'V': 0x3E, 'W': 0x3E,
    }

    def __init__(self):
        self.spi = SPI(1, baudrate=10_000_000, polarity=0, phase=0,
                       sck=Pin(SPI1_SCK), mosi=Pin(SPI1_MOSI))
        self.cs = Pin(MAX7219_CS, Pin.OUT, value=1)
        self._cmd(0x0C, 1)  # shutdown off (normal)
        self._cmd(0x09, 0)  # no decode
        self._cmd(0x0B, 7)  # scan all 8 digits
        self._cmd(0x0A, 8)  # brightness 8/15
        self._cmd(0x0F, 0)  # test mode off
        self.clear()

    def _cmd(self, reg, data):
        self.cs(0)
        self.spi.write(bytes([reg, data]))
        self.cs(1)

    def clear(self):
        for i in range(8):
            self._cmd(i + 1, 0x00)

    def brightness(self, level):
        self._cmd(0x0A, min(15, max(0, level)))

    def show(self, text):
        """Display up to 8 chars, right-aligned."""
        text = str(text).upper()[:8]
        text = text.rjust(8)
        for i, ch in enumerate(text):
            val = self.CHARS.get(ch, 0x00)
            self._cmd(8 - i, val)

    def flash(self, text, times=3, on_ms=300, off_ms=200):
        for _ in range(times):
            self.show(text)
            time.sleep_ms(on_ms)
            self.clear()
            time.sleep_ms(off_ms)
        self.show(text)


# ============ nRF24L01+ MINIMAL DRIVER (RX MODE) ============
class NRF_RX:
    def __init__(self):
        self.spi = SPI(0, baudrate=10_000_000, polarity=0, phase=0,
                       sck=Pin(SPI_SCK), mosi=Pin(SPI_MOSI), miso=Pin(SPI_MISO))
        self.ce = Pin(NRF_CE, Pin.OUT, value=0)
        self.csn = Pin(NRF_CSN, Pin.OUT, value=1)
        self._init_radio()

    def _reg_write(self, reg, val):
        self.csn(0)
        self.spi.readinto(bytearray(1), 0x20 | reg)
        self.spi.readinto(bytearray(1), val)
        self.csn(1)

    def _reg_write_bytes(self, reg, data):
        self.csn(0)
        self.spi.readinto(bytearray(1), 0x20 | reg)
        self.spi.write(data)
        self.csn(1)

    def _reg_read(self, reg):
        self.csn(0)
        self.spi.readinto(bytearray(1), reg)
        result = bytearray(1)
        self.spi.readinto(result)
        self.csn(1)
        return result[0]

    def _flush_rx(self):
        self.csn(0)
        self.spi.readinto(bytearray(1), 0xE2)
        self.csn(1)

    def _init_radio(self):
        time.sleep_ms(100)
        self._reg_write(0x00, 0x0C)
        self._reg_write(0x01, 0x00)
        self._reg_write(0x02, 0x03)
        self._reg_write(0x03, 0x03)
        self._reg_write(0x04, 0x00)
        self._reg_write(0x05, NRF_CHANNEL)
        self._reg_write(0x06, 0x26)
        self._reg_write(0x11, 32)
        self._reg_write(0x12, 32)
        self._reg_write_bytes(0x10, TX_ADDR)
        self._reg_write_bytes(0x0A, RX_ADDR)
        self._reg_write_bytes(0x0B, TX_ADDR)
        self._flush_rx()
        self._reg_write(0x07, 0x70)
        # Enter RX mode
        self._reg_write(0x00, 0x0F)  # PWR_UP + PRIM_RX
        time.sleep_ms(2)
        self.ce(1)  # start listening
        status = self._reg_read(0x07)
        print(f"  nRF RX status: 0x{status:02X}")

    def available(self):
        status = self._reg_read(0x07)
        return (status & 0x40) != 0  # RX_DR flag

    def receive(self):
        """Read 32-byte payload."""
        self.csn(0)
        self.spi.readinto(bytearray(1), 0x61)  # R_RX_PAYLOAD
        buf = bytearray(32)
        self.spi.readinto(buf)
        self.csn(1)
        self._reg_write(0x07, 0x70)  # clear flags
        return bytes(buf)


# ============ PACKET DISPLAY ============
def display_packet(seg, pkt_type, data, stats):
    """Update MAX7219 based on packet type."""

    if pkt_type == PKT_POWER:
        bus_v = struct.unpack_from('<H', data, 2)[0] / 100
        m1_ma = struct.unpack_from('<H', data, 4)[0]
        m2_ma = struct.unpack_from('<H', data, 6)[0]
        total_mw = struct.unpack_from('<H', data, 8)[0]
        state = data[11]

        # Alternate between displays
        cycle = stats['display_cycle'] % 4
        if cycle == 0:
            seg.show(f"{bus_v:.1f}V")
        elif cycle == 1:
            seg.show(f"A {m1_ma:4d}")  # Motor 1 current
        elif cycle == 2:
            seg.show(f"b {m2_ma:4d}")  # Motor 2 current
        else:
            seg.show(f"P {total_mw:4d}")  # Total power mW
        stats['display_cycle'] += 1

        stats['bus_v'] = bus_v
        stats['m1_ma'] = m1_ma
        stats['m2_ma'] = m2_ma
        stats['total_mw'] = total_mw
        stats['state'] = state
        return f"POWER: {bus_v}V M1={m1_ma}mA M2={m2_ma}mA P={total_mw}mW"

    elif pkt_type == PKT_STATUS:
        state = data[2]
        fault = data[3]
        imu_rms = struct.unpack_from('<H', data, 4)[0] / 100
        uptime = struct.unpack_from('<I', data, 8)[0] // 1000

        state_name = STATE_NAMES[state] if state < len(STATE_NAMES) else '??'

        if state == 3:  # FAULT
            seg.show(f"F1  VIb")
            seg.brightness(15)
        elif state == 4:  # RECOVERY
            seg.show("rECOVEr")
        elif state == 5:  # RECYCLE
            seg.show("rECYCLE")
        elif state == 6:  # DONE
            seg.show("donE")
        elif state == 0:  # BOOT
            seg.show("bOOt")
        elif state == 1:  # READY
            seg.show("rEAdY")
            seg.brightness(8)
        else:
            seg.show(f"  {state_name}")

        stats['state'] = state
        stats['imu_rms'] = imu_rms
        return f"STATUS: {state_name} IMU={imu_rms:.2f}g uptime={uptime}s"

    elif pkt_type == PKT_PRODUCTION:
        produced = struct.unpack_from('<H', data, 2)[0]
        passed = struct.unpack_from('<H', data, 4)[0]
        rejected = struct.unpack_from('<H', data, 6)[0]

        seg.show(f"P{passed:3d}r{rejected:2d}")
        stats['produced'] = produced
        stats['passed'] = passed
        stats['rejected'] = rejected
        return f"PROD: produced={produced} pass={passed} reject={rejected}"

    elif pkt_type == PKT_HEARTBEAT:
        seg.show("LIVE")
        return "HEARTBEAT"

    elif pkt_type == PKT_ALERT:
        fault_code = data[2]
        severity = data[3]
        imu_val = struct.unpack_from('<H', data, 4)[0] / 100

        seg.brightness(15)
        seg.flash(f"F{fault_code}  VIb", times=5, on_ms=200, off_ms=100)
        stats['fault_count'] = stats.get('fault_count', 0) + 1
        return f"ALERT! F{fault_code} sev={severity} IMU={imu_val:.2f}g"

    return f"UNKNOWN type 0x{pkt_type:02X}"


# ============ MAIN LOOP ============
def run_slave():
    print()
    print("=" * 50)
    print("  GridBox Demo — Pico B (Slave / SCADA)")
    print("=" * 50)
    print()

    led = Pin(LED_PIN, Pin.OUT)
    led.on()

    # Init displays
    print("[INIT] MAX7219...")
    seg = SevenSeg()
    seg.show("GRIDBOX")
    time.sleep(1)
    seg.show("LINK---")

    print("[INIT] nRF24L01+ (RX mode)...")
    nrf = NRF_RX()

    # Stats
    stats = {
        'packets': 0,
        'display_cycle': 0,
        'bus_v': 0, 'm1_ma': 0, 'm2_ma': 0, 'total_mw': 0,
        'state': 0, 'imu_rms': 0,
        'produced': 0, 'passed': 0, 'rejected': 0,
        'fault_count': 0,
        'last_rx': 0,
    }

    PKT_NAMES = {
        PKT_POWER: 'POWER', PKT_STATUS: 'STATUS', PKT_PRODUCTION: 'PROD',
        PKT_HEARTBEAT: 'HBEAT', PKT_ALERT: 'ALERT'
    }

    print()
    print("[LISTEN] Waiting for packets from Pico A...")
    print()

    waiting_shown = False

    while True:
        now = time.ticks_ms()

        if nrf.available():
            data = nrf.receive()
            pkt_type = data[0]
            pkt_seq = data[1]
            stats['packets'] += 1
            stats['last_rx'] = now

            pkt_name = PKT_NAMES.get(pkt_type, f'0x{pkt_type:02X}')
            desc = display_packet(seg, pkt_type, data, stats)

            print(f"  [{stats['packets']:4d}] {pkt_name:6s} seq={pkt_seq:3d} | {desc}")

            led.toggle()
            waiting_shown = False

        else:
            # No packet — check timeout
            if stats['last_rx'] > 0 and time.ticks_diff(now, stats['last_rx']) > 5000:
                if not waiting_shown:
                    seg.show("NO LINK")
                    print("  [WARN] No packets for 5s — link lost?")
                    waiting_shown = True
            elif stats['last_rx'] == 0 and not waiting_shown:
                if time.ticks_diff(now, 0) > 10000:
                    seg.show("WAIT")
                    waiting_shown = True

            time.sleep_ms(10)


# ============ MAIN ============
if __name__ == '__main__':
    try:
        run_slave()
    except KeyboardInterrupt:
        print(f"\nSlave stopped")
        SevenSeg().show("STOP")
    except Exception as e:
        print(f"\nSLAVE ERROR: {e}")
        try:
            seg = SevenSeg()
            seg.show("Err")
        except Exception:
            pass
        led = Pin(LED_PIN, Pin.OUT)
        for _ in range(20):
            led.toggle()
            time.sleep_ms(100)
