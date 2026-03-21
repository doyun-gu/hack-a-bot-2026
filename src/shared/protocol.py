"""
GridBox — Wireless Packet Protocol
Shared between master (Pico A) and slave (Pico B).
Both Picos must use the same packet format.

Packet structure (32 bytes):
  Byte 0:      packet_type (uint8)
  Byte 1-4:    roll (float) — IMU roll angle
  Byte 5-8:    pitch (float) — IMU pitch angle
  Byte 9-12:   gyro_rate (float) — rotation speed
  Byte 13-14:  joy_x (uint16) — joystick X
  Byte 15-16:  joy_y (uint16) — joystick Y
  Byte 17:     mode (uint8) — operating mode
  Byte 18:     test_level (uint8) — difficulty / threshold level
  Byte 19:     flags (uint8) — bit flags
  Byte 20-23:  timestamp_ms (uint32) — millisecond timestamp
  Byte 24-31:  padding (8 bytes)
"""

import struct

# ============ PACKET TYPES ============
PKT_DATA = 0x01          # telemetry data from master → slave
PKT_HEARTBEAT = 0x02     # alive check
PKT_ALERT = 0x03         # fault alert
PKT_ACK = 0x04           # acknowledgement
PKT_COMMAND = 0x05       # command from slave → master

# ============ OPERATING MODES ============
MODE_IDLE = 0            # system idle
MODE_NORMAL = 1          # normal autonomous operation
MODE_DUMB = 2            # dumb mode (all 100% for comparison)
MODE_MANUAL = 3          # manual override from SCADA
MODE_CALIBRATE = 4       # calibration mode
MODE_LEARNING = 5        # energy signature learning
MODE_EMERGENCY = 6       # emergency stop active

# ============ FLAGS (bit field) ============
FLAG_FAULT_ALERT = 0x01  # bit 0: fault detected
FLAG_BUTTON = 0x02       # bit 1: button pressed
FLAG_CALIBRATED = 0x04   # bit 2: calibration loaded

# ============ COMMAND TYPES (encoded in test_level field for PKT_COMMAND) ============
CMD_SET_MOTOR_SPEED = 0x10  # joy_x=motor_id, joy_y=speed%
CMD_SET_THRESHOLD = 0x11    # joy_x=threshold value
CMD_RESET_FAULT = 0x12      # reset fault state
CMD_SET_MODE = 0x13         # mode field = new mode
CMD_EMERGENCY_STOP = 0x14   # stop everything

# ============ PACK FORMAT ============
# type(B) roll(f) pitch(f) gyro(f) jx(H) jy(H) mode(B) level(B) flags(B) time(I) pad(8s)
PACK_FORMAT = '<BfffHHBBBI8s'
PACK_SIZE = 32  # bytes


def pack_data(roll, pitch, gyro_rate, joy_x, joy_y, mode, test_level, flags, timestamp_ms):
    """Pack telemetry data into a 32-byte packet."""
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
    """Pack a fault alert packet."""
    return struct.pack(PACK_FORMAT,
                       PKT_ALERT, roll, pitch, 0.0,
                       0, 0, 0, 0, FLAG_FAULT_ALERT,
                       timestamp_ms, b'\x00' * 8)


def pack_command(cmd_type, mode=0, param1=0, param2=0, timestamp_ms=0):
    """Pack a command from SCADA to master.

    Args:
        cmd_type: CMD_SET_MOTOR_SPEED, CMD_SET_THRESHOLD, etc.
        mode: operating mode (for CMD_SET_MODE)
        param1: first parameter (mapped to joy_x)
        param2: second parameter (mapped to joy_y)
        timestamp_ms: millisecond timestamp
    """
    return struct.pack(PACK_FORMAT,
                       PKT_COMMAND, 0.0, 0.0, 0.0,
                       param1, param2, mode, cmd_type, 0,
                       timestamp_ms, b'\x00' * 8)


def unpack(data):
    """Unpack a 32-byte packet into a dict."""
    if len(data) != PACK_SIZE:
        return None
    try:
        values = struct.unpack(PACK_FORMAT, data)
    except Exception:
        return None
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
        'fault_alert': bool(values[8] & FLAG_FAULT_ALERT),
        'button': bool(values[8] & FLAG_BUTTON),
        'calibrated': bool(values[8] & FLAG_CALIBRATED),
    }


if __name__ == "__main__":
    # Quick self-test
    print("Protocol self-test...")

    # Test pack/unpack data
    pkt = pack_data(1.5, -2.3, 10.0, 100, 200, MODE_NORMAL, 0, FLAG_CALIBRATED, 12345)
    assert len(pkt) == 32, f"Data packet size: {len(pkt)}"
    d = unpack(pkt)
    assert d['type'] == PKT_DATA
    assert abs(d['roll'] - 1.5) < 0.01
    assert d['joy_x'] == 100
    assert d['mode'] == MODE_NORMAL
    assert d['calibrated'] is True
    print("  pack_data / unpack: OK")

    # Test heartbeat
    pkt = pack_heartbeat(99999)
    assert len(pkt) == 32
    d = unpack(pkt)
    assert d['type'] == PKT_HEARTBEAT
    assert d['timestamp_ms'] == 99999
    print("  pack_heartbeat: OK")

    # Test alert
    pkt = pack_alert(45.0, -30.0, 55555)
    d = unpack(pkt)
    assert d['type'] == PKT_ALERT
    assert d['fault_alert'] is True
    print("  pack_alert: OK")

    # Test command
    pkt = pack_command(CMD_SET_MOTOR_SPEED, param1=1, param2=75, timestamp_ms=11111)
    d = unpack(pkt)
    assert d['type'] == PKT_COMMAND
    assert d['test_level'] == CMD_SET_MOTOR_SPEED
    assert d['joy_x'] == 1   # motor_id
    assert d['joy_y'] == 75  # speed
    print("  pack_command: OK")

    # Test bad data
    assert unpack(b'\x00' * 10) is None
    print("  bad data handling: OK")

    print("All protocol tests passed!")
