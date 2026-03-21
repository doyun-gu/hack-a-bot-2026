"""
GridBox — SCADA Commander
Sends control commands from Pico B (SCADA) to Pico A (Grid Controller).
Uses COMMAND packet type from shared protocol.
"""

import time

# Import protocol constants — protocol.py is in src/shared/
# On Pico, copy protocol.py to /micropython/ alongside this file
try:
    from protocol import (pack_command, CMD_SET_SPEED, CMD_SET_THRESHOLD,
                          CMD_RESET_FAULT, CMD_SET_MODE, CMD_EMERGENCY_STOP)
except ImportError:
    # Fallback: define locally if protocol.py not available
    CMD_SET_SPEED = 0x01
    CMD_SET_THRESHOLD = 0x03
    CMD_RESET_FAULT = 0x04
    CMD_SET_MODE = 0x05
    CMD_EMERGENCY_STOP = 0x06


class Commander:
    """SCADA commander for bidirectional wireless control."""

    def __init__(self, nrf_driver):
        """
        Args:
            nrf_driver: NRF24L01 instance (already configured)
        """
        self.nrf = nrf_driver
        self._last_send_ms = 0
        self._send_interval_ms = 50  # don't flood

    def _can_send(self):
        """Rate limit outgoing commands."""
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_send_ms) < self._send_interval_ms:
            return False
        return True

    def _send_command(self, cmd_type, target=0, value=0, mode=0):
        """Send a command packet to Pico A.

        Returns True if ACK received.
        """
        if not self._can_send():
            return False

        try:
            pkt = pack_command(cmd_type, target=target, value=value, mode=mode)
        except NameError:
            # pack_command not available, build manually
            import struct
            pkt = struct.pack('<BBBBHB25s',
                              0x10, 0,  # type, seq
                              cmd_type, target, value, mode,
                              b'\x00' * 25)

        # Switch to TX, send, switch back to RX
        self.nrf.stop_listening()
        ok = self.nrf.send(pkt)
        self.nrf.start_listening()

        self._last_send_ms = time.ticks_ms()
        return ok

    def send_override(self, motor_id, speed):
        """Command Pico A to set motor speed.

        Args:
            motor_id: 1 or 2
            speed: 0-100%
        """
        return self._send_command(CMD_SET_SPEED,
                                  target=motor_id, value=speed)

    def send_threshold(self, value):
        """Send new weight threshold to Pico A.

        Args:
            value: threshold value (0-100, mapped from potentiometer)
        """
        return self._send_command(CMD_SET_THRESHOLD, value=value)

    def send_reset(self):
        """Command fault reset on Pico A."""
        return self._send_command(CMD_RESET_FAULT)

    def send_mode(self, mode):
        """Switch operating mode on Pico A.

        Args:
            mode: MODE_IDLE, MODE_NORMAL, MODE_DUMB, MODE_MANUAL, etc.
        """
        return self._send_command(CMD_SET_MODE, mode=mode)

    def send_emergency_stop(self):
        """Emergency stop all motors on Pico A."""
        # Override rate limit for emergency
        self._last_send_ms = 0
        return self._send_command(CMD_EMERGENCY_STOP)


if __name__ == "__main__":
    import config
    from machine import Pin, SPI
    from nrf24l01 import NRF24L01

    print("=" * 40)
    print("  SCADA Commander Test")
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

    cmd = Commander(nrf)

    # Test sending commands
    print("\nSending motor speed command (M1=50%)...")
    ok = cmd.send_override(1, 50)
    print(f"  ACK: {ok}")

    time.sleep_ms(100)

    print("Sending threshold command (value=75)...")
    ok = cmd.send_threshold(75)
    print(f"  ACK: {ok}")

    time.sleep_ms(100)

    print("Sending fault reset...")
    ok = cmd.send_reset()
    print(f"  ACK: {ok}")

    time.sleep_ms(100)

    print("Sending emergency stop...")
    ok = cmd.send_emergency_stop()
    print(f"  ACK: {ok}")

    print("\nCommander test complete")
