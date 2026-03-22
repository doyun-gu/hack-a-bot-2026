"""
GridBox — System Test Slave (Pico B)
Receives test status from Pico A, displays on MAX7219.
Also prints to USB serial for laptop monitoring.

Run this FIRST, then run test_system.py on Pico A.
Usage: mpremote run src/demo/test_system_slave.py
"""

from machine import Pin, SPI
import time

# ============ PINS ============
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

NRF_CHANNEL = 100
TX_ADDR = b'NSYNR'
RX_ADDR = b'NSYNT'

MSG_TEXT = 0x01
MSG_RESULT = 0x02


# ============ MAX7219 ============
class Seg:
    CHARS = {
        '0': 0x7E, '1': 0x30, '2': 0x6D, '3': 0x79, '4': 0x33,
        '5': 0x5B, '6': 0x5F, '7': 0x70, '8': 0x7F, '9': 0x7B,
        'A': 0x77, 'B': 0x1F, 'C': 0x4E, 'D': 0x3D, 'E': 0x4F,
        'F': 0x47, 'G': 0x5E, 'H': 0x37, 'I': 0x06, 'J': 0x3C,
        'K': 0x37, 'L': 0x0E, 'M': 0x76, 'N': 0x15, 'O': 0x7E,
        'P': 0x67, 'Q': 0x73, 'R': 0x05, 'S': 0x5B, 'T': 0x0F,
        'U': 0x3E, 'V': 0x3E, 'W': 0x3E, 'X': 0x37, 'Y': 0x3B,
        'Z': 0x6D, '-': 0x01, '_': 0x08, ' ': 0x00, '.': 0x80,
    }

    def __init__(self):
        self.spi = SPI(1, baudrate=10_000_000, polarity=0, phase=0,
                       sck=Pin(SPI1_SCK), mosi=Pin(SPI1_MOSI))
        self.cs = Pin(MAX7219_CS, Pin.OUT, value=1)
        self._cmd(0x0C, 1)
        self._cmd(0x09, 0)
        self._cmd(0x0B, 7)
        self._cmd(0x0A, 8)
        self._cmd(0x0F, 0)
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
        text = str(text).upper()[:8].rjust(8)
        for i, ch in enumerate(text):
            self._cmd(8 - i, self.CHARS.get(ch, 0x00))

    def flash(self, text, times=3):
        for _ in range(times):
            self.show(text)
            time.sleep_ms(250)
            self.clear()
            time.sleep_ms(150)
        self.show(text)


# ============ nRF RX ============
class NRF_RX:
    def __init__(self):
        self.spi = SPI(0, baudrate=10_000_000, polarity=0, phase=0,
                       sck=Pin(SPI_SCK), mosi=Pin(SPI_MOSI), miso=Pin(SPI_MISO))
        self.ce = Pin(NRF_CE, Pin.OUT, value=0)
        self.csn = Pin(NRF_CSN, Pin.OUT, value=1)
        self._init()

    def _w(self, reg, val):
        self.csn(0)
        self.spi.readinto(bytearray(1), 0x20 | reg)
        self.spi.readinto(bytearray(1), val)
        self.csn(1)

    def _wb(self, reg, data):
        self.csn(0)
        self.spi.readinto(bytearray(1), 0x20 | reg)
        self.spi.write(data)
        self.csn(1)

    def _r(self, reg):
        self.csn(0)
        self.spi.readinto(bytearray(1), reg)
        r = bytearray(1)
        self.spi.readinto(r)
        self.csn(1)
        return r[0]

    def _init(self):
        time.sleep_ms(100)
        self._w(0x00, 0x0C)
        self._w(0x01, 0x00)
        self._w(0x02, 0x03)
        self._w(0x03, 0x03)
        self._w(0x04, 0x00)
        self._w(0x05, NRF_CHANNEL)
        self._w(0x06, 0x26)
        self._w(0x11, 32)
        self._w(0x12, 32)
        self._wb(0x10, TX_ADDR)
        self._wb(0x0A, RX_ADDR)
        self._wb(0x0B, TX_ADDR)
        self.csn(0)
        self.spi.readinto(bytearray(1), 0xE2)
        self.csn(1)
        self._w(0x07, 0x70)
        self._w(0x00, 0x0F)
        time.sleep_ms(2)
        self.ce(1)

    def available(self):
        return (self._r(0x07) & 0x40) != 0

    def receive(self):
        self.csn(0)
        self.spi.readinto(bytearray(1), 0x61)
        buf = bytearray(32)
        self.spi.readinto(buf)
        self.csn(1)
        self._w(0x07, 0x70)
        return bytes(buf)


# ============ MAIN ============
def main():
    print()
    print("=" * 50)
    print("  GridBox — System Test Slave")
    print("  Pico B (displays on MAX7219)")
    print("=" * 50)
    print()

    led = Pin(LED_PIN, Pin.OUT, value=1)

    print("[INIT] MAX7219...")
    seg = Seg()
    seg.show("GRIDBOX")
    time.sleep(1)
    seg.show("WAIT")

    print("[INIT] nRF24L01+ (RX)...")
    nrf = NRF_RX()
    print(f"  Status: 0x{nrf._r(0x07):02X}")
    print()
    print("[LISTEN] Waiting for Pico A...")
    print()

    count = 0
    results = []

    while True:
        if nrf.available():
            data = nrf.receive()
            count += 1
            led.toggle()
            msg_type = data[0]

            if msg_type == MSG_TEXT:
                length = data[1]
                text = data[2:2+length].decode()
                seg.show(text)
                print(f"  [{count:4d}] DISPLAY: {text}")

                # Flash for fault
                if 'FAULT' in text.upper():
                    seg.brightness(15)
                    seg.flash(text, times=5)
                elif 'RECOVER' in text.upper():
                    seg.brightness(8)
                elif 'PASS' in text.upper() and 'ALL' in text.upper():
                    seg.brightness(15)
                    seg.flash(text, times=3)
                    seg.brightness(8)

            elif msg_type == MSG_RESULT:
                test_num = data[1]
                passed = data[2] == 1
                length = data[3]
                name = data[4:4+length].decode()
                icon = "PASS" if passed else "FAIL"
                results.append((test_num, name, passed))
                print(f"  [{count:4d}] TEST {test_num}: {name} = {icon}")

                if passed:
                    seg.show(f"{name} OK")
                else:
                    seg.flash(f"{name}FAIL", times=3)

            else:
                print(f"  [{count:4d}] Unknown type: 0x{msg_type:02X}")

        time.sleep_ms(10)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped")
        Seg().show("STOP")
    except Exception as e:
        print(f"\nERROR: {e}")
        try:
            Seg().show("ERR")
        except Exception:
            pass
