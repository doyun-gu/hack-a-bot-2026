"""
GridBox — Multi-Type Datagram Protocol v2
Shared between master (Pico A) and slave (Pico B).

6 packet types, all exactly 32 bytes, rotating at 50Hz.
See docs/02-electrical/datagram-design.md for full spec.

Packet layout: 2-byte header (type + sequence) + payload + padding.
"""

import struct

# ============ PACKET TYPES ============
PKT_POWER = 0x01       # power measurements (A->B)
PKT_STATUS = 0x02      # system health (A->B)
PKT_PRODUCTION = 0x03  # sort stats (A->B)
PKT_HEARTBEAT = 0x04   # alive check (A->B)
PKT_ALERT = 0x05       # fault alert (A->B, breaks rotation)
PKT_COMMAND = 0x10     # operator command (B->A)

# Backward compat aliases
PKT_DATA = PKT_POWER
PKT_ACK = PKT_HEARTBEAT

# ============ OPERATING MODES ============
MODE_IDLE = 0
MODE_NORMAL = 1
MODE_DUMB = 2
MODE_MANUAL = 3
MODE_CALIBRATE = 4
MODE_LEARNING = 5
MODE_EMERGENCY = 6

# ============ COMMAND TYPES (inside PKT_COMMAND) ============
CMD_SET_SPEED = 0x01
CMD_SET_SERVO = 0x02
CMD_SET_THRESHOLD = 0x03
CMD_RESET_FAULT = 0x04
CMD_SET_MODE = 0x05
CMD_EMERGENCY_STOP = 0x06
CMD_START_CALIBRATION = 0x07
CMD_START_LEARNING = 0x08

# Backward compat aliases
CMD_SET_MOTOR_SPEED = CMD_SET_SPEED

# ============ FLAGS ============
FLAG_FAULT_ALERT = 0x01
FLAG_BUTTON = 0x02
FLAG_CALIBRATED = 0x04

# ============ SYSTEM STATES ============
SYS_NORMAL = 0
SYS_DRIFT = 1
SYS_WARNING = 2
SYS_FAULT = 3
SYS_EMERGENCY = 4

# ============ FAULT SOURCES ============
FAULT_NONE = 0
FAULT_VIBRATION = 1
FAULT_OVERCURRENT = 2
FAULT_UNDERVOLTAGE = 3
FAULT_INTERMITTENT = 4
FAULT_JAM = 5

# ============ ALERT LEVELS ============
ALERT_INFO = 0
ALERT_WARNING = 1
ALERT_FAULT = 2
ALERT_EMERGENCY = 3

# ============ ALERT ACTIONS (bitfield) ============
ACT_MOTOR_STOPPED = 0x01
ACT_LOAD_SHED = 0x02
ACT_REROUTED = 0x04

# ============ IMU STATES ============
IMU_HEALTHY = 0
IMU_WARNING = 1
IMU_FAULT = 2

# ============ ES CLASSIFICATIONS ============
ES_HEALTHY = 0
ES_DRIFT = 1
ES_PREFAULT = 2
ES_FAULT = 3

# ============ PACK FORMATS (all 32 bytes) ============
PACK_SIZE = 32

FMT_POWER = '<BBHHHHHHHBBBBBBB9s'
FMT_STATUS = '<BBBBHBHBHHBBIBB10s'
FMT_PRODUCTION = '<BBHHHBHBBHHBB13s'
FMT_HEARTBEAT = '<BBIIBB20s'
FMT_ALERT = '<BBBBIHHHB17s'
FMT_COMMAND = '<BBBBHB25s'

# ============ ROTATION SCHEDULE ============
ROTATION = [PKT_POWER, PKT_STATUS, PKT_POWER, PKT_PRODUCTION,
            PKT_POWER, PKT_STATUS, PKT_POWER, PKT_HEARTBEAT]

# Pre-allocated padding
_PAD9 = b'\x00' * 9
_PAD10 = b'\x00' * 10
_PAD13 = b'\x00' * 13
_PAD17 = b'\x00' * 17
_PAD20 = b'\x00' * 20
_PAD25 = b'\x00' * 25

# Sequence counter
_seq = 0


def _next_seq():
    global _seq
    _seq = (_seq + 1) & 0xFF
    return _seq


# ============ PACK FUNCTIONS ============

def pack_power(bus_mv, m1_ma, m2_ma, m1_mw, m2_mw, total_mw, excess_mw,
               m1_spd, m2_spd, s1_ang, s2_ang, eff, leds, mosfets):
    """Pack POWER packet (0x01)."""
    return struct.pack(FMT_POWER, PKT_POWER, _next_seq(),
                       int(bus_mv), int(m1_ma), int(m2_ma),
                       int(m1_mw), int(m2_mw), int(total_mw), int(excess_mw),
                       int(m1_spd), int(m2_spd), int(s1_ang), int(s2_ang),
                       int(eff), int(leds), int(mosfets), _PAD9)


def pack_status(sys_state, fault_src, imu_rms_mg, imu_state,
                es_score_x100, es_class, es_mean_ma, es_std_ma,
                shed_level, mode, uptime_s, faults_today, reroute):
    """Pack STATUS packet (0x02)."""
    return struct.pack(FMT_STATUS, PKT_STATUS, _next_seq(),
                       int(sys_state), int(fault_src),
                       int(imu_rms_mg), int(imu_state),
                       int(es_score_x100), int(es_class),
                       int(es_mean_ma), int(es_std_ma),
                       int(shed_level), int(mode),
                       int(uptime_s), int(faults_today), int(reroute),
                       _PAD10)


def pack_production(total, passed, rejected, reject_pct,
                    last_weight_mg, last_result, belt_spd,
                    thresh_min_mg, thresh_max_mg,
                    station_active, sorting_active):
    """Pack PRODUCTION packet (0x03)."""
    return struct.pack(FMT_PRODUCTION, PKT_PRODUCTION, _next_seq(),
                       int(total), int(passed), int(rejected),
                       int(reject_pct), int(last_weight_mg), int(last_result),
                       int(belt_spd), int(thresh_min_mg), int(thresh_max_mg),
                       int(station_active), int(sorting_active), _PAD13)


def pack_heartbeat(timestamp_ms, uptime_s, core0_pct=0, core1_pct=0):
    """Pack HEARTBEAT packet (0x04)."""
    return struct.pack(FMT_HEARTBEAT, PKT_HEARTBEAT, _next_seq(),
                       int(timestamp_ms), int(uptime_s),
                       int(core0_pct), int(core1_pct), _PAD20)


def pack_alert(level, source, timestamp_ms, imu_mg, motor_ma, bus_mv, action):
    """Pack ALERT packet (0x05). Breaks rotation — sent immediately on fault."""
    return struct.pack(FMT_ALERT, PKT_ALERT, _next_seq(),
                       int(level), int(source), int(timestamp_ms),
                       int(imu_mg), int(motor_ma), int(bus_mv),
                       int(action), _PAD17)


def pack_command(cmd_type, target=0, value=0, mode=0):
    """Pack COMMAND packet (0x10). Sent B->A on operator input."""
    return struct.pack(FMT_COMMAND, PKT_COMMAND, _next_seq(),
                       int(cmd_type), int(target), int(value), int(mode),
                       _PAD25)


# ============ UNPACK FUNCTIONS ============

def unpack_power(data):
    v = struct.unpack(FMT_POWER, data)
    return {
        'type': v[0], 'seq': v[1],
        'bus_voltage_mv': v[2], 'motor1_current_ma': v[3], 'motor2_current_ma': v[4],
        'motor1_power_mw': v[5], 'motor2_power_mw': v[6],
        'total_power_mw': v[7], 'excess_power_mw': v[8],
        'motor1_speed_pct': v[9], 'motor2_speed_pct': v[10],
        'servo1_angle': v[11], 'servo2_angle': v[12],
        'efficiency_pct': v[13], 'led_bank_state': v[14], 'mosfet_state': v[15],
    }


def unpack_status(data):
    v = struct.unpack(FMT_STATUS, data)
    return {
        'type': v[0], 'seq': v[1],
        'system_state': v[2], 'fault_source': v[3],
        'imu_rms_mg': v[4], 'imu_state': v[5],
        'es_score_x100': v[6], 'es_classification': v[7],
        'es_mean_current_ma': v[8], 'es_std_current_ma': v[9],
        'shedding_level': v[10], 'mode': v[11],
        'uptime_s': v[12], 'faults_today': v[13], 'reroute_active': v[14],
    }


def unpack_production(data):
    v = struct.unpack(FMT_PRODUCTION, data)
    return {
        'type': v[0], 'seq': v[1],
        'total_items': v[2], 'passed_items': v[3], 'rejected_items': v[4],
        'reject_rate_pct': v[5], 'last_weight_mg': v[6], 'last_result': v[7],
        'belt_speed_pct': v[8], 'threshold_min_mg': v[9], 'threshold_max_mg': v[10],
        'station_active': v[11], 'sorting_active': v[12],
    }


def unpack_heartbeat(data):
    v = struct.unpack(FMT_HEARTBEAT, data)
    return {
        'type': v[0], 'seq': v[1],
        'timestamp_ms': v[2], 'uptime_s': v[3],
        'core0_load_pct': v[4], 'core1_load_pct': v[5],
    }


def unpack_alert(data):
    v = struct.unpack(FMT_ALERT, data)
    return {
        'type': v[0], 'seq': v[1],
        'alert_level': v[2], 'alert_source': v[3],
        'timestamp_ms': v[4],
        'imu_rms_mg': v[5], 'motor_current_ma': v[6], 'bus_voltage_mv': v[7],
        'action_taken': v[8],
    }


def unpack_command(data):
    v = struct.unpack(FMT_COMMAND, data)
    return {
        'type': v[0], 'seq': v[1],
        'cmd_type': v[2], 'target': v[3], 'value': v[4], 'mode': v[5],
    }


# ============ GENERIC UNPACK ============

_UNPACKERS = {
    PKT_POWER: unpack_power,
    PKT_STATUS: unpack_status,
    PKT_PRODUCTION: unpack_production,
    PKT_HEARTBEAT: unpack_heartbeat,
    PKT_ALERT: unpack_alert,
    PKT_COMMAND: unpack_command,
}


def unpack(data):
    """Unpack any 32-byte packet by reading the type byte."""
    if len(data) != PACK_SIZE:
        return None
    pkt_type = data[0]
    fn = _UNPACKERS.get(pkt_type)
    if fn is None:
        return None
    try:
        return fn(data)
    except Exception:
        return None


# ============ SELF-TEST ============
if __name__ == "__main__":
    print("Protocol v2 self-test...")

    # POWER
    pkt = pack_power(4900, 350, 200, 1700, 980, 2680, 1320, 65, 40, 90, 45, 37, 0x0F, 0x03)
    assert len(pkt) == 32, f"POWER size: {len(pkt)}"
    d = unpack(pkt)
    assert d['type'] == PKT_POWER
    assert d['bus_voltage_mv'] == 4900
    assert d['motor1_speed_pct'] == 65
    assert d['servo1_angle'] == 90
    print("  pack_power / unpack: OK")

    # STATUS
    pkt = pack_status(SYS_NORMAL, FAULT_NONE, 1500, IMU_WARNING, 45, ES_HEALTHY, 350, 20,
                      0, MODE_NORMAL, 3600, 2, 0)
    assert len(pkt) == 32, f"STATUS size: {len(pkt)}"
    d = unpack(pkt)
    assert d['type'] == PKT_STATUS
    assert d['imu_rms_mg'] == 1500
    assert d['uptime_s'] == 3600
    print("  pack_status / unpack: OK")

    # PRODUCTION
    pkt = pack_production(47, 42, 5, 11, 1500, 0, 60, 500, 5000, 2, 1)
    assert len(pkt) == 32, f"PRODUCTION size: {len(pkt)}"
    d = unpack(pkt)
    assert d['type'] == PKT_PRODUCTION
    assert d['total_items'] == 47
    assert d['reject_rate_pct'] == 11
    print("  pack_production / unpack: OK")

    # HEARTBEAT
    pkt = pack_heartbeat(123456, 3600, 45, 80)
    assert len(pkt) == 32, f"HEARTBEAT size: {len(pkt)}"
    d = unpack(pkt)
    assert d['type'] == PKT_HEARTBEAT
    assert d['timestamp_ms'] == 123456
    assert d['core0_load_pct'] == 45
    print("  pack_heartbeat / unpack: OK")

    # ALERT
    pkt = pack_alert(ALERT_FAULT, FAULT_VIBRATION, 99999, 2500, 850, 4100, ACT_MOTOR_STOPPED)
    assert len(pkt) == 32, f"ALERT size: {len(pkt)}"
    d = unpack(pkt)
    assert d['type'] == PKT_ALERT
    assert d['alert_level'] == ALERT_FAULT
    assert d['imu_rms_mg'] == 2500
    print("  pack_alert / unpack: OK")

    # COMMAND
    pkt = pack_command(CMD_SET_SPEED, target=1, value=75, mode=0)
    assert len(pkt) == 32, f"COMMAND size: {len(pkt)}"
    d = unpack(pkt)
    assert d['type'] == PKT_COMMAND
    assert d['cmd_type'] == CMD_SET_SPEED
    assert d['value'] == 75
    assert d['target'] == 1
    print("  pack_command / unpack: OK")

    # Bad data
    assert unpack(b'\x00' * 10) is None
    assert unpack(b'\xFF' * 32) is None
    print("  bad data handling: OK")

    # Rotation
    assert len(ROTATION) == 8
    assert ROTATION.count(PKT_POWER) == 4
    assert ROTATION.count(PKT_STATUS) == 2
    assert ROTATION.count(PKT_PRODUCTION) == 1
    assert ROTATION.count(PKT_HEARTBEAT) == 1
    print("  rotation schedule: OK")

    print("\nAll protocol v2 tests passed!")
