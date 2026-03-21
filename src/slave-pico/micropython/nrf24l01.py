"""
GridBox — nRF24L01+ Wireless Driver
SPI-based driver for nRF24L01+ PA+LNA 2.4GHz transceiver.
Uses register-level SPI commands per the nRF24L01+ datasheet.
"""

from machine import Pin, SPI
import time

# ============ nRF24L01+ REGISTERS ============
CONFIG = 0x00
EN_AA = 0x01
EN_RXADDR = 0x02
SETUP_AW = 0x03
SETUP_RETR = 0x04
RF_CH = 0x05
RF_SETUP = 0x06
STATUS = 0x07
OBSERVE_TX = 0x08
RX_ADDR_P0 = 0x0A
RX_ADDR_P1 = 0x0B
TX_ADDR = 0x10
RX_PW_P0 = 0x11
RX_PW_P1 = 0x12
FIFO_STATUS = 0x17
DYNPD = 0x1C
FEATURE = 0x1D

# ============ SPI COMMANDS ============
R_REGISTER = 0x00
W_REGISTER = 0x20
R_RX_PAYLOAD = 0x61
W_TX_PAYLOAD = 0xA0
FLUSH_TX = 0xE1
FLUSH_RX = 0xE2
NOP = 0xFF

# ============ CONFIG BITS ============
MASK_RX_DR = 0x40
MASK_TX_DS = 0x20
MASK_MAX_RT = 0x10
EN_CRC = 0x08
CRCO = 0x04
PWR_UP = 0x02
PRIM_RX = 0x01

# ============ STATUS BITS ============
RX_DR = 0x40
TX_DS = 0x20
MAX_RT = 0x10
RX_P_NO_MASK = 0x0E

# ============ RF_SETUP BITS ============
RF_DR_LOW = 0x20    # 250kbps
RF_DR_HIGH = 0x08   # 2Mbps
RF_PWR_MASK = 0x06
RF_PWR_MIN = 0x00   # -18dBm
RF_PWR_LOW = 0x02   # -12dBm
RF_PWR_MED = 0x04   # -6dBm
RF_PWR_MAX = 0x06   # 0dBm


class NRF24L01:
    """nRF24L01+ driver using SPI."""

    def __init__(self, spi, csn_pin, ce_pin, channel=100, payload_size=32,
                 data_rate=250, tx_addr=b'NSYNT', rx_addr=b'NSYNR'):
        self.spi = spi
        self.csn = csn_pin
        self.ce = ce_pin
        self.payload_size = payload_size

        # Ensure pins are configured
        self.csn.init(Pin.OUT, value=1)
        self.ce.init(Pin.OUT, value=0)
        self.buf1 = bytearray(1)

        time.sleep_ms(5)  # power-on reset

        # Configure the radio
        self._write_reg(CONFIG, EN_CRC | CRCO)  # CRC enabled, 2-byte CRC, PWR_DOWN
        self._write_reg(EN_AA, 0x03)             # auto-ack on pipe 0 and 1
        self._write_reg(EN_RXADDR, 0x03)         # enable pipe 0 and 1
        self._write_reg(SETUP_AW, 0x03)          # 5-byte address
        self._write_reg(SETUP_RETR, 0x3F)        # 1000µs delay, 15 retries
        self.set_channel(channel)
        self.set_data_rate(data_rate)
        self.set_power(3)  # max power
        self._write_reg(RX_PW_P0, payload_size)
        self._write_reg(RX_PW_P1, payload_size)
        self._write_reg(DYNPD, 0x00)             # fixed payload
        self._write_reg(FEATURE, 0x00)

        # Set addresses
        self.set_tx_addr(tx_addr)
        self.set_rx_addr(rx_addr)

        # Clear status flags and FIFOs
        self._write_reg(STATUS, RX_DR | TX_DS | MAX_RT)
        self.flush_tx()
        self.flush_rx()

        # Power up
        config = self._read_reg(CONFIG)
        self._write_reg(CONFIG, config | PWR_UP)
        time.sleep_ms(2)  # standby-I

    def _csn_low(self):
        self.csn.value(0)

    def _csn_high(self):
        self.csn.value(1)

    def _read_reg(self, reg):
        self._csn_low()
        try:
            self.spi.readinto(self.buf1, R_REGISTER | reg)
            self.spi.readinto(self.buf1)
        except OSError:
            self.buf1[0] = 0
        finally:
            self._csn_high()
        return self.buf1[0]

    def _write_reg(self, reg, value):
        self._csn_low()
        try:
            self.spi.readinto(self.buf1, W_REGISTER | reg)
            self.spi.readinto(self.buf1, value)
        except OSError:
            pass
        finally:
            self._csn_high()

    def _read_reg_bytes(self, reg, length):
        buf = bytearray(length)
        self._csn_low()
        try:
            self.spi.readinto(self.buf1, R_REGISTER | reg)
            self.spi.readinto(buf)
        except OSError:
            pass
        finally:
            self._csn_high()
        return buf

    def _write_reg_bytes(self, reg, data):
        self._csn_low()
        try:
            self.spi.readinto(self.buf1, W_REGISTER | reg)
            self.spi.write(data)
        except OSError:
            pass
        finally:
            self._csn_high()

    def set_channel(self, ch):
        """Set RF channel (0-125). Frequency = 2400 + ch MHz."""
        self._write_reg(RF_CH, min(ch, 125))

    def set_data_rate(self, rate):
        """Set data rate: 250 (kbps), 1000, or 2000."""
        setup = self._read_reg(RF_SETUP) & ~(RF_DR_LOW | RF_DR_HIGH)
        if rate == 250:
            setup |= RF_DR_LOW
        elif rate == 2000:
            setup |= RF_DR_HIGH
        # else 1000kbps = both bits clear
        self._write_reg(RF_SETUP, setup)

    def set_power(self, level):
        """Set TX power level 0-3 (min to max)."""
        setup = self._read_reg(RF_SETUP) & ~RF_PWR_MASK
        setup |= (min(level, 3) << 1) & RF_PWR_MASK
        self._write_reg(RF_SETUP, setup)

    def set_tx_addr(self, addr):
        """Set TX address (5 bytes)."""
        self._write_reg_bytes(TX_ADDR, addr)
        # Also set RX pipe 0 to TX addr for auto-ack
        self._write_reg_bytes(RX_ADDR_P0, addr)

    def set_rx_addr(self, addr):
        """Set RX address on pipe 1 (5 bytes)."""
        self._write_reg_bytes(RX_ADDR_P1, addr)

    def send(self, data):
        """Transmit a packet. Returns True if ACK received, False if max retries.

        Args:
            data: bytes/bytearray of payload_size length
        """
        if len(data) != self.payload_size:
            data = data[:self.payload_size].ljust(self.payload_size, b'\x00')

        # Switch to TX mode
        config = self._read_reg(CONFIG)
        self._write_reg(CONFIG, (config | PWR_UP) & ~PRIM_RX)
        time.sleep_us(150)

        # Write payload
        self._csn_low()
        try:
            self.spi.readinto(self.buf1, W_TX_PAYLOAD)
            self.spi.write(data)
        except OSError:
            self._csn_high()
            return False
        finally:
            self._csn_high()

        # Pulse CE to transmit
        self.ce.value(1)
        time.sleep_us(15)
        self.ce.value(0)

        # Wait for TX complete or max retries (timeout 50ms)
        deadline = time.ticks_add(time.ticks_ms(), 50)
        while time.ticks_diff(deadline, time.ticks_ms()) > 0:
            status = self._read_reg(STATUS)
            if status & TX_DS:
                # TX success — clear flag
                self._write_reg(STATUS, TX_DS)
                return True
            if status & MAX_RT:
                # Max retries — clear flag, flush TX
                self._write_reg(STATUS, MAX_RT)
                self.flush_tx()
                return False
            time.sleep_us(100)

        # Timeout
        self.flush_tx()
        return False

    def start_listening(self):
        """Switch to RX mode and start listening."""
        config = self._read_reg(CONFIG)
        self._write_reg(CONFIG, config | PWR_UP | PRIM_RX)
        self._write_reg(STATUS, RX_DR | TX_DS | MAX_RT)
        self.flush_rx()
        self.ce.value(1)
        time.sleep_us(150)

    def stop_listening(self):
        """Switch out of RX mode."""
        self.ce.value(0)
        time.sleep_us(100)
        config = self._read_reg(CONFIG)
        self._write_reg(CONFIG, (config | PWR_UP) & ~PRIM_RX)

    def available(self):
        """Check if data is waiting in RX FIFO."""
        status = self._read_reg(STATUS)
        return (status & RX_P_NO_MASK) != RX_P_NO_MASK

    def recv(self):
        """Read received packet. Returns data bytes or None."""
        if not self.available():
            return None

        # Read payload
        self._csn_low()
        self.spi.readinto(self.buf1, R_RX_PAYLOAD)
        buf = bytearray(self.payload_size)
        self.spi.readinto(buf)
        self._csn_high()

        # Clear RX_DR flag
        self._write_reg(STATUS, RX_DR)

        return bytes(buf)

    def flush_rx(self):
        """Clear RX FIFO."""
        self._csn_low()
        self.spi.readinto(self.buf1, FLUSH_RX)
        self._csn_high()

    def flush_tx(self):
        """Clear TX FIFO."""
        self._csn_low()
        self.spi.readinto(self.buf1, FLUSH_TX)
        self._csn_high()

    def get_status(self):
        """Read STATUS register."""
        return self._read_reg(STATUS)


if __name__ == "__main__":
    import config

    print("=" * 40)
    print("  nRF24L01+ Driver Test")
    print("=" * 40)

    spi = SPI(config.SPI_ID, baudrate=config.SPI_BAUD, polarity=0, phase=0,
              sck=Pin(config.SPI_SCK), mosi=Pin(config.SPI_MOSI),
              miso=Pin(config.SPI_MISO))

    nrf = NRF24L01(spi, Pin(config.NRF_CSN), Pin(config.NRF_CE),
                   channel=config.NRF_CHANNEL,
                   payload_size=config.NRF_PAYLOAD_SIZE,
                   data_rate=config.NRF_DATA_RATE,
                   tx_addr=config.NRF_TX_ADDR,
                   rx_addr=config.NRF_RX_ADDR)

    status = nrf.get_status()
    print(f"STATUS register: 0x{status:02X}")
    print(f"Channel: {config.NRF_CHANNEL}")
    print(f"Payload size: {config.NRF_PAYLOAD_SIZE}")
    print("Driver initialised OK")
