"""
Wireless packet protocol — shared between master and slave.
Both Picos must use the same packet format.

Packet structure (32 bytes):
  Byte 0:     packet_type (uint8)
  Byte 1-4:   roll (float, 4 bytes)
  Byte 5-8:   pitch (float, 4 bytes)
  Byte 9-12:  gyro_rate (float, 4 bytes)
  Byte 13-14: joy_x (uint16)
  Byte 15-16: joy_y (uint16)
  Byte 17:    mode (uint8)
  Byte 18:    test_level (uint8)
  Byte 19:    flags (uint8) — bit 0: fall_alert, bit 1: button_pressed
  Byte 20-23: timestamp_ms (uint32)
  Byte 24-31: reserved (padding to 32 bytes)
"""

import struct

# Packet types
PKT_DATA = 0x01        # sensor data packet
PKT_HEARTBEAT = 0x02   # alive check
PKT_ALERT = 0x03       # fall detected / SOS
PKT_ACK = 0x04         # acknowledgement from slave
PKT_COMMAND = 0x05     # command from slave to master

# Modes
MODE_IDLE = 0
MODE_STABILITY = 1
MODE_TRACKING = 2
MODE_REACTION = 3
MODE_PATTERN = 4
MODE_BIOMETRIC = 5
MODE_CALIBRATE = 6

# Flags (bit field)
FLAG_FALL_ALERT = 0x01
FLAG_BUTTON = 0x02
FLAG_CALIBRATED = 0x04

# Pack format: type(B) roll(f) pitch(f) gyro(f) jx(H) jy(H) mode(B) level(B) flags(B) time(I) pad(8s)
PACK_FORMAT = '<BfffHHBBBI8s'
PACK_SIZE = 32  # bytes


def pack_data(roll, pitch, gyro_rate, joy_x, joy_y, mode, test_level, flags, timestamp_ms):
    """Pack sensor data into a 32-byte packet."""
    return struct.pack(PACK_FORMAT,
                       PKT_DATA, roll, pitch, gyro_rate,
                       joy_x, joy_y, mode, test_level, flags,
                       timestamp_ms, b'\x00' * 8)


def pack_heartbeat(timestamp_ms):
    """Pack a heartbeat packet."""
    return struct.pack(PACK_FORMAT,
                       PKT_HEARTBEAT, 0.0, 0.0, 0.0,
                       0, 0, 0, 0, 0,
                       timestamp_ms, b'\x00' * 8)


def pack_alert(roll, pitch, timestamp_ms):
    """Pack a fall alert packet."""
    return struct.pack(PACK_FORMAT,
                       PKT_ALERT, roll, pitch, 0.0,
                       0, 0, 0, 0, FLAG_FALL_ALERT,
                       timestamp_ms, b'\x00' * 8)


def unpack(data):
    """Unpack a 32-byte packet into a dict."""
    if len(data) != PACK_SIZE:
        return None
    values = struct.unpack(PACK_FORMAT, data)
    return {
        'type': values[0],
        'roll': values[1],
        'pitch': values[2],
        'gyro_rate': values[3],
        'joy_x': values[4],
        'joy_y': values[5],
        'mode': values[6],
        'test_level': values[7],
        'flags': values[8],
        'timestamp_ms': values[9],
        'fall_alert': bool(values[8] & FLAG_FALL_ALERT),
        'button': bool(values[8] & FLAG_BUTTON),
    }
