"""
GridBox — Integration Test (runs on laptop, not Pico)
Verifies all modules work together without hardware.

Usage:
    cd src/master-pico
    python tests/test_integration.py

Tests:
    1. Import every module
    2. Verify config.py has all expected constants
    3. Protocol pack/unpack round-trips for all 6 packet types
    4. Fault manager state transitions
    5. Sorter weight classification logic
    6. Power manager calculations with fake ADC values
    7. Energy signature compute + divergence
"""

import sys
import os
import math

# Add module paths so imports work on laptop
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'micropython'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

# ============ TEST FRAMEWORK ============

_pass = 0
_fail = 0
_errors = []


def check(name, condition, detail=""):
    global _pass, _fail
    if condition:
        _pass += 1
        print(f"  PASS  {name}")
    else:
        _fail += 1
        msg = f"  FAIL  {name}"
        if detail:
            msg += f" — {detail}"
        print(msg)
        _errors.append(name)


# ============ MOCK: fake `machine` module for laptop ============
# Modules import `from machine import ...` — provide stubs so they load.

import types
machine_mod = types.ModuleType('machine')

class _FakePin:
    OUT = 1
    IN = 0
    def __init__(self, *a, **kw): pass
    def init(self, *a, **kw): pass
    def value(self, *a): return 0

class _FakeADC:
    def __init__(self, *a, **kw): pass
    def read_u16(self): return 32768

class _FakeI2C:
    def __init__(self, *a, **kw): pass
    def readfrom_mem(self, addr, reg, n): return bytes(n)
    def writeto_mem(self, addr, reg, data): pass
    def scan(self): return []

class _FakeSPI:
    def __init__(self, *a, **kw): pass
    def readinto(self, buf, val=0):
        for i in range(len(buf)):
            buf[i] = val & 0xFF
    def write(self, data): pass

class _FakeTimer:
    ONE_SHOT = 0
    PERIODIC = 1
    def __init__(self, *a, **kw): pass
    def init(self, **kw): pass
    def deinit(self): pass

class _FakeTime:
    @staticmethod
    def ticks_ms(): return 0
    @staticmethod
    def ticks_diff(a, b): return a - b
    @staticmethod
    def ticks_add(a, b): return a + b
    @staticmethod
    def sleep_ms(ms): pass
    @staticmethod
    def sleep_us(us): pass
    @staticmethod
    def sleep(s): pass

machine_mod.Pin = _FakePin
machine_mod.ADC = _FakeADC
machine_mod.I2C = _FakeI2C
machine_mod.SPI = _FakeSPI
machine_mod.Timer = _FakeTimer
sys.modules['machine'] = machine_mod

# Also patch time module with MicroPython-specific functions
import time as _real_time
if not hasattr(_real_time, 'ticks_ms'):
    _real_time.ticks_ms = lambda: int(_real_time.time() * 1000)
    _real_time.ticks_diff = lambda a, b: a - b
    _real_time.ticks_add = lambda a, b: a + b
    _real_time.sleep_ms = lambda ms: None
    _real_time.sleep_us = lambda us: None


# ============ TEST 1: IMPORTS ============

print("\n" + "=" * 50)
print("  TEST 1: Module Imports")
print("=" * 50)

modules_to_import = [
    'config',
    'protocol',
    'fault_manager',
    'sorter',
    'power_manager',
    'energy_signature',
]

imported = {}
for mod_name in modules_to_import:
    try:
        imported[mod_name] = __import__(mod_name)
        check(f"import {mod_name}", True)
    except Exception as e:
        check(f"import {mod_name}", False, str(e))

config = imported.get('config')
protocol = imported.get('protocol')
fault_manager = imported.get('fault_manager')
sorter_mod = imported.get('sorter')
power_manager = imported.get('power_manager')
energy_sig = imported.get('energy_signature')


# ============ TEST 2: CONFIG CONSTANTS ============

print("\n" + "=" * 50)
print("  TEST 2: Config Constants")
print("=" * 50)

if config:
    expected_constants = [
        # I2C
        'I2C_SDA', 'I2C_SCL', 'I2C_FREQ', 'BMI160_ADDR', 'PCA9685_ADDR',
        # SPI
        'SPI_SCK', 'SPI_MOSI', 'SPI_MISO', 'NRF_CE', 'NRF_CSN',
        'NRF_CHANNEL', 'NRF_PAYLOAD_SIZE',
        # MOSFET
        'MOSFET_MOTOR1', 'MOSFET_MOTOR2', 'MOSFET_LED_BANK', 'MOSFET_RECYCLE',
        # LEDs
        'LED_RED', 'LED_GREEN',
        # ADC
        'ADC_BUS_VOLTAGE', 'ADC_MOTOR1_CURRENT', 'ADC_MOTOR2_CURRENT',
        'ADC_VREF', 'ADC_RESOLUTION', 'VOLTAGE_DIVIDER_RATIO', 'CURRENT_SENSE_R',
        # Thresholds
        'BUS_VOLTAGE_NOMINAL', 'BUS_VOLTAGE_LOW', 'BUS_VOLTAGE_CRITICAL',
        'MOTOR_CURRENT_MAX_MA',
        # Sorting
        'WEIGHT_THRESHOLD_MIN', 'WEIGHT_THRESHOLD_LIGHT',
        'WEIGHT_THRESHOLD_HEAVY', 'WEIGHT_THRESHOLD_JAM',
        # Energy signature
        'ES_SAMPLE_RATE_HZ', 'ES_WINDOW_SIZE', 'ES_ANOMALY_THRESHOLD',
        'ES_WEIGHT_MEAN', 'ES_WEIGHT_STD', 'ES_WEIGHT_CROSSING', 'ES_WEIGHT_MAXDEV',
        # Timing
        'MAIN_LOOP_MS', 'WIRELESS_SEND_MS',
    ]

    for const in expected_constants:
        check(f"config.{const}", hasattr(config, const),
              "missing" if not hasattr(config, const) else "")

    # Verify key values
    check("NRF_PAYLOAD_SIZE == 32", config.NRF_PAYLOAD_SIZE == 32)
    check("ADC_VREF == 3.3", config.ADC_VREF == 3.3)
    check("BUS_VOLTAGE_NOMINAL == 5.0", config.BUS_VOLTAGE_NOMINAL == 5.0)
    check("MAIN_LOOP_MS == 10", config.MAIN_LOOP_MS == 10)
    check("ES weights sum to 1.0",
          abs(config.ES_WEIGHT_MEAN + config.ES_WEIGHT_STD +
              config.ES_WEIGHT_CROSSING + config.ES_WEIGHT_MAXDEV - 1.0) < 0.01)
else:
    check("config module loaded", False, "could not import config")


# ============ TEST 3: PROTOCOL PACK/UNPACK ============

print("\n" + "=" * 50)
print("  TEST 3: Protocol Pack/Unpack Round-Trips")
print("=" * 50)

if protocol:
    # POWER
    pkt = protocol.pack_power(4900, 350, 200, 1700, 980, 2680, 1320, 65, 40, 90, 45, 37, 0x0F, 0x03)
    check("POWER packet size == 32", len(pkt) == 32)
    d = protocol.unpack(pkt)
    check("POWER round-trip type", d is not None and d['type'] == protocol.PKT_POWER)
    check("POWER bus_voltage_mv == 4900", d is not None and d['bus_voltage_mv'] == 4900)
    check("POWER motor1_speed == 65", d is not None and d['motor1_speed_pct'] == 65)

    # STATUS
    pkt = protocol.pack_status(0, 0, 1500, 1, 45, 0, 350, 20, 0, 1, 3600, 2, 0)
    check("STATUS packet size == 32", len(pkt) == 32)
    d = protocol.unpack(pkt)
    check("STATUS round-trip type", d is not None and d['type'] == protocol.PKT_STATUS)
    check("STATUS imu_rms_mg == 1500", d is not None and d['imu_rms_mg'] == 1500)
    check("STATUS uptime == 3600", d is not None and d['uptime_s'] == 3600)

    # PRODUCTION
    pkt = protocol.pack_production(47, 42, 5, 11, 1500, 0, 60, 500, 5000, 2, 1)
    check("PRODUCTION packet size == 32", len(pkt) == 32)
    d = protocol.unpack(pkt)
    check("PRODUCTION round-trip type", d is not None and d['type'] == protocol.PKT_PRODUCTION)
    check("PRODUCTION total_items == 47", d is not None and d['total_items'] == 47)
    check("PRODUCTION reject_rate == 11", d is not None and d['reject_rate_pct'] == 11)

    # HEARTBEAT
    pkt = protocol.pack_heartbeat(123456, 3600, 45, 80)
    check("HEARTBEAT packet size == 32", len(pkt) == 32)
    d = protocol.unpack(pkt)
    check("HEARTBEAT round-trip type", d is not None and d['type'] == protocol.PKT_HEARTBEAT)
    check("HEARTBEAT timestamp == 123456", d is not None and d['timestamp_ms'] == 123456)
    check("HEARTBEAT core0 == 45", d is not None and d['core0_load_pct'] == 45)

    # ALERT
    pkt = protocol.pack_alert(2, 1, 99999, 2500, 850, 4100, 0x01)
    check("ALERT packet size == 32", len(pkt) == 32)
    d = protocol.unpack(pkt)
    check("ALERT round-trip type", d is not None and d['type'] == protocol.PKT_ALERT)
    check("ALERT level == FAULT", d is not None and d['alert_level'] == 2)
    check("ALERT imu_rms == 2500", d is not None and d['imu_rms_mg'] == 2500)

    # COMMAND
    pkt = protocol.pack_command(0x01, target=1, value=75, mode=0)
    check("COMMAND packet size == 32", len(pkt) == 32)
    d = protocol.unpack(pkt)
    check("COMMAND round-trip type", d is not None and d['type'] == protocol.PKT_COMMAND)
    check("COMMAND cmd_type == SET_SPEED", d is not None and d['cmd_type'] == 0x01)
    check("COMMAND value == 75", d is not None and d['value'] == 75)

    # Bad data
    check("unpack(short data) == None", protocol.unpack(b'\x00' * 10) is None)
    check("unpack(bad type) == None", protocol.unpack(b'\xFF' * 32) is None)

    # Rotation schedule
    check("ROTATION length == 8", len(protocol.ROTATION) == 8)
    check("ROTATION has 4 POWER", protocol.ROTATION.count(protocol.PKT_POWER) == 4)
else:
    check("protocol module loaded", False, "could not import protocol")


# ============ TEST 4: FAULT MANAGER STATE TRANSITIONS ============

print("\n" + "=" * 50)
print("  TEST 4: Fault Manager State Transitions")
print("=" * 50)

if fault_manager:
    FM = fault_manager.FaultManager

    # Normal operation
    fm = FM()
    power = {'bus_v': 5.0, 'm1_mA': 200, 'm2_mA': 150, 'excess_W': 0.0}
    actions = fm.update(power, "HEALTHY")
    check("normal → NORMAL", fm.get_state() == "NORMAL")
    check("normal → no emergency actions",
          "emergency_stop" not in actions and "alert" not in actions)

    # Low voltage → DRIFT
    fm = FM()
    power = {'bus_v': 4.0, 'm1_mA': 200, 'm2_mA': 150, 'excess_W': 0.0}
    fm.update(power, "HEALTHY")
    check("low voltage → DRIFT", fm.get_state() == "DRIFT")

    # Sustained low voltage → WARNING (simulate elapsed time)
    fm._drift_start_ms = _real_time.ticks_ms() - 6000
    fm.update(power, "HEALTHY")
    check("sustained low voltage → WARNING", fm.get_state() == "WARNING")

    # Overcurrent → FAULT
    fm = FM()
    power = {'bus_v': 5.0, 'm1_mA': 900, 'm2_mA': 150, 'excess_W': 0.0}
    actions = fm.update(power, "HEALTHY")
    check("overcurrent → FAULT", fm.get_state() == "FAULT")
    check("overcurrent → stop_motor action",
          any("stop_motor" in a for a in actions))

    # IMU fault → EMERGENCY
    fm = FM()
    power = {'bus_v': 5.0, 'm1_mA': 200, 'm2_mA': 150, 'excess_W': 0.0}
    actions = fm.update(power, "FAULT")
    check("IMU fault → EMERGENCY", fm.get_state() == "EMERGENCY")
    check("IMU fault → emergency_stop action", "emergency_stop" in actions)

    # Critical voltage → EMERGENCY
    fm = FM()
    power = {'bus_v': 3.5, 'm1_mA': 200, 'm2_mA': 150, 'excess_W': 0.0}
    actions = fm.update(power, "HEALTHY")
    check("critical voltage → EMERGENCY", fm.get_state() == "EMERGENCY")

    # Reset
    fm.reset()
    check("reset → NORMAL", fm.get_state() == "NORMAL")

    # Stats
    stats = fm.get_stats()
    check("get_stats has 'state'", 'state' in stats)
    check("get_stats has 'faults_today'", 'faults_today' in stats)

    # Vibration warning → DRIFT
    fm = FM()
    power = {'bus_v': 5.0, 'm1_mA': 200, 'm2_mA': 150, 'excess_W': 0.0}
    fm.update(power, "WARNING")
    check("vibration warning → DRIFT", fm.get_state() == "DRIFT")
else:
    check("fault_manager module loaded", False, "could not import fault_manager")


# ============ TEST 5: SORTER WEIGHT CLASSIFICATION ============

print("\n" + "=" * 50)
print("  TEST 5: Sorter Weight Classification")
print("=" * 50)

if sorter_mod and config:
    # Create sorter without hardware dependencies
    s = sorter_mod.Sorter.__new__(sorter_mod.Sorter)
    s._baseline_mA = 300.0
    s.threshold_light = config.WEIGHT_THRESHOLD_LIGHT
    s.threshold_heavy = config.WEIGHT_THRESHOLD_HEAVY
    s.threshold_jam = config.WEIGHT_THRESHOLD_JAM
    s.total_items = 0
    s.passed = 0
    s.rejected = 0
    s.jams = 0
    s.last_weight_class = sorter_mod.CLASS_NONE
    s.last_current_delta = 0.0

    # Classification tests
    check("delta 0.02 → REJECT_LIGHT (below light threshold)",
          s.classify_weight(0.02) == sorter_mod.CLASS_REJECT_LIGHT)
    check("delta 0.10 → PASS (between light and heavy)",
          s.classify_weight(0.10) == sorter_mod.CLASS_PASS)
    check("delta 0.20 → REJECT_HEAVY (above heavy threshold)",
          s.classify_weight(0.20) == sorter_mod.CLASS_REJECT_HEAVY)
    check("delta 0.35 → JAM (above jam threshold)",
          s.classify_weight(0.35) == sorter_mod.CLASS_JAM)

    # Threshold adjustment
    s.set_threshold(0)  # tightest
    tight_heavy = s.threshold_heavy
    s.set_threshold(100)  # loosest
    loose_heavy = s.threshold_heavy
    check("threshold 0% < threshold 100%", tight_heavy < loose_heavy)

    # Stats tracking
    s.total_items = 10
    s.passed = 8
    s.rejected = 2
    stats = s.get_stats()
    check("stats total_items == 10", stats['total_items'] == 10)
    check("stats reject_rate == 20.0", stats['reject_rate'] == 20.0)
else:
    check("sorter module loaded", False, "could not import sorter")


# ============ TEST 6: POWER MANAGER CALCULATIONS ============

print("\n" + "=" * 50)
print("  TEST 6: Power Manager Calculations")
print("=" * 50)

if power_manager and config:
    # Test ADC conversion math (without real ADC)
    # Simulate: raw ADC mid-point → voltage
    adc_vref = config.ADC_VREF
    adc_res = config.ADC_RESOLUTION
    divider = config.VOLTAGE_DIVIDER_RATIO
    r_sense = config.CURRENT_SENSE_R

    # ADC mid-point (32768) should give ~1.65V
    raw_mid = 32768
    v_mid = raw_mid * adc_vref / adc_res
    check("ADC midpoint ≈ 1.65V", abs(v_mid - 1.65) < 0.01,
          f"got {v_mid:.4f}")

    # Bus voltage with divider: 1.65V * 2.0 = 3.30V
    bus_v = v_mid * divider
    check("bus voltage with divider ≈ 3.30V", abs(bus_v - 3.30) < 0.01,
          f"got {bus_v:.4f}")

    # Current: 1.65V across 1Ω = 1650mA
    current_mA = (v_mid / r_sense) * 1000
    check("current sense ≈ 1650mA", abs(current_mA - 1650) < 1,
          f"got {current_mA:.1f}")

    # Power: 3.3V * 1.65A = 5.445W
    power_W = bus_v * current_mA / 1000
    check("power calc ≈ 5.45W", abs(power_W - 5.445) < 0.01,
          f"got {power_W:.3f}")

    # Efficiency: total / nominal * 100
    nominal_W = bus_v * config.MOTOR_CURRENT_MAX_MA / 1000 * 2
    eff = (power_W / nominal_W * 100) if nominal_W > 0 else 0
    check("efficiency formula produces valid %", 0 < eff < 200,
          f"got {eff:.1f}%")
else:
    check("power_manager module loaded", False, "could not import power_manager")


# ============ TEST 7: ENERGY SIGNATURE ============

print("\n" + "=" * 50)
print("  TEST 7: Energy Signature Compute + Divergence")
print("=" * 50)

if energy_sig and config:
    # Test compute_signature with known data
    samples = [100.0, 102.0, 98.0, 101.0, 99.0, 103.0, 97.0, 100.0, 102.0, 98.0]
    sig = energy_sig.compute_signature(samples)
    check("signature mean ≈ 100.0", abs(sig.mean_current - 100.0) < 0.1,
          f"got {sig.mean_current:.3f}")
    check("signature std > 0", sig.std_current > 0,
          f"got {sig.std_current:.3f}")
    check("signature crossings > 0", sig.crossing_rate > 0,
          f"got {sig.crossing_rate}")
    check("signature max_dev > 0", sig.max_deviation > 0,
          f"got {sig.max_deviation:.3f}")

    # Test divergence between identical signatures → 0
    score = energy_sig.divergence_score(sig, sig)
    check("identical signatures → score 0.0", abs(score) < 0.001,
          f"got {score:.4f}")

    # Test divergence between very different signatures
    sig2 = energy_sig.compute_signature([500.0, 510.0, 490.0, 505.0, 495.0])
    score2 = energy_sig.divergence_score(sig, sig2)
    check("different signatures → score > 0.5", score2 > 0.5,
          f"got {score2:.4f}")

    # Test zero_crossings
    xings = energy_sig.zero_crossings([1, -1, 1, -1, 1], 0)
    check("zero_crossings count == 4", xings == 4, f"got {xings}")

    # Test empty samples
    empty_sig = energy_sig.compute_signature([])
    check("empty samples → zero signature", empty_sig.mean_current == 0.0)

    # Test EnergySignature repr
    repr_str = repr(sig)
    check("EnergySignature has repr", "Sig(" in repr_str)
else:
    check("energy_signature module loaded", False, "could not import energy_signature")


# ============ SUMMARY ============

print("\n" + "=" * 50)
total = _pass + _fail
print(f"  RESULTS: {_pass}/{total} tests passed")
if _fail > 0:
    print(f"  FAILURES ({_fail}):")
    for e in _errors:
        print(f"    - {e}")
print("=" * 50)

sys.exit(0 if _fail == 0 else 1)
