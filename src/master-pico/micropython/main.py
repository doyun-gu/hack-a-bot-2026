"""
GridBox — Master Pico (Pico A) Main
Full integrated control loop for the Grid Controller.

Core 0: main loop (100Hz) — sensing, control, wireless, serial
Core 1: IMU reader + energy signature sampling
"""

from machine import Pin, I2C, SPI, ADC, Timer
import time
import json

import config
from nrf24l01 import NRF24L01
from bmi160 import BMI160, ACC_RANGE_4G, GYR_RANGE_500
from pca9685 import PCA9685
from power_manager import PowerManager
from motor_control import MotorControl
from imu_reader import IMUReader
from fault_manager import FaultManager
from energy_signature import EnergySignatureMonitor
from sorter import Sorter
from led_stations import LEDStations
from calibration import Calibration

# Import protocol (copied to micropython dir from src/shared/)
try:
    from protocol import (
        pack_power, pack_status, pack_production, pack_heartbeat,
        pack_alert, unpack, ROTATION,
        PKT_POWER, PKT_STATUS, PKT_PRODUCTION, PKT_HEARTBEAT, PKT_COMMAND,
        CMD_SET_SPEED, CMD_SET_SERVO, CMD_SET_THRESHOLD,
        CMD_RESET_FAULT, CMD_SET_MODE, CMD_EMERGENCY_STOP,
        MODE_NORMAL, MODE_DUMB, MODE_MANUAL, MODE_CALIBRATE,
        MODE_IDLE, MODE_EMERGENCY, FLAG_CALIBRATED,
        SYS_NORMAL, SYS_DRIFT, SYS_WARNING, SYS_FAULT, SYS_EMERGENCY,
        IMU_HEALTHY, IMU_WARNING, IMU_FAULT,
        ES_HEALTHY, ES_DRIFT, ES_PREFAULT, ES_FAULT,
        FAULT_NONE, FAULT_VIBRATION, FAULT_OVERCURRENT, FAULT_UNDERVOLTAGE,
        ALERT_FAULT, ALERT_EMERGENCY,
        ACT_MOTOR_STOPPED, ACT_LOAD_SHED, ACT_REROUTED,
    )
except ImportError:
    print("[MASTER] WARNING: protocol.py not found, wireless disabled")
    pack_power = None

# Track send success/fail
wireless_stats = {'sent': 0, 'failed': 0, 'consecutive_fail': 0}


def send_packet(nrf, pkt, critical=False):
    """Send a wireless packet with optional retries for critical packets.

    ALERT packets: 3 attempts. COMMAND packets: 2 attempts. Others: 1.
    """
    nrf.stop_listening()
    attempts = 3 if critical else 1
    success = False
    for _ in range(attempts):
        if nrf.send(pkt):
            success = True
            wireless_stats['sent'] += 1
            wireless_stats['consecutive_fail'] = 0
            break
        time.sleep_ms(1)
    if not success:
        wireless_stats['failed'] += 1
        wireless_stats['consecutive_fail'] += 1
    nrf.start_listening()
    return success


# State string -> enum mappings
_STATE_MAP = {"NORMAL": 0, "DRIFT": 1, "WARNING": 2, "FAULT": 3, "EMERGENCY": 4}
_IMU_MAP = {"HEALTHY": 0, "WARNING": 1, "FAULT": 2}
_RESULT_MAP = {"PASS": 0, "REJECT_HEAVY": 1, "REJECT_LIGHT": 2, "JAM": 3, "NONE": 0}


def blink_error(led_pin, code, repeat=3):
    """Blink error code on LED. N blinks = error type.

    Pattern: [N fast blinks] — [pause] — [repeat]
    """
    for _ in range(repeat):
        for _ in range(code):
            led_pin.value(1)
            time.sleep_ms(150)
            led_pin.value(0)
            time.sleep_ms(150)
        time.sleep_ms(800)


def startup_selftest(hw):
    """Run self-test on all hardware. Returns list of (name, code, msg) failures.

    Blink codes:
        1 = I2C bus fail
        2 = SPI bus fail
        3 = IMU not found
        4 = PCA9685 not found
        5 = nRF24L01+ fail
        6 = ADC readings invalid
    """
    failures = []

    # Test I2C bus
    if hw['i2c'] is None:
        failures.append(('I2C', 1, 'No I2C bus'))
    else:
        devices = hw['i2c'].scan()
        if config.BMI160_ADDR not in devices:
            failures.append(('IMU', 3, f'BMI160 not at 0x{config.BMI160_ADDR:02X}. Found: {[hex(d) for d in devices]}'))
        if config.PCA9685_ADDR not in devices:
            failures.append(('PCA', 4, f'PCA9685 not at 0x{config.PCA9685_ADDR:02X}. Found: {[hex(d) for d in devices]}'))

    # Test SPI / nRF
    if hw.get('spi') is None:
        failures.append(('SPI', 2, 'SPI bus init failed'))
    if hw['nrf'] is None:
        failures.append(('NRF', 5, 'nRF24L01+ init failed'))

    # Test ADC
    try:
        adc_val = ADC(Pin(config.ADC_BUS_VOLTAGE)).read_u16()
        if adc_val < 100:
            failures.append(('ADC', 6, f'Bus voltage ADC reads {adc_val} — check divider'))
    except Exception as e:
        failures.append(('ADC', 6, f'ADC read error: {e}'))

    if failures:
        print(f"[MASTER] SELFTEST FAILED: {len(failures)} issue(s)")
        for name, code, msg in failures:
            print(f"  [{name}] Blink {code}: {msg}")
            blink_error(hw['led_red'], code, repeat=3)
    else:
        print("[MASTER] SELFTEST PASSED — all hardware OK")
        # Green LED flash to confirm
        for _ in range(3):
            hw['led_green'].value(1)
            time.sleep_ms(100)
            hw['led_green'].value(0)
            time.sleep_ms(100)

    return failures


def init_hardware():
    """Initialise all hardware peripherals."""
    print("[MASTER] Initialising hardware...")
    hw = {}

    # I2C bus (BMI160 + PCA9685)
    try:
        hw['i2c'] = I2C(config.I2C_ID, sda=Pin(config.I2C_SDA),
                        scl=Pin(config.I2C_SCL), freq=config.I2C_FREQ)
        devices = hw['i2c'].scan()
        print(f"[MASTER] I2C devices: {[hex(d) for d in devices]}")
    except Exception as e:
        print(f"[MASTER] I2C error: {e}")
        hw['i2c'] = None

    # SPI bus (nRF24L01+)
    try:
        hw['spi'] = SPI(config.SPI_ID, baudrate=config.SPI_BAUD, polarity=0, phase=0,
                        sck=Pin(config.SPI_SCK), mosi=Pin(config.SPI_MOSI),
                        miso=Pin(config.SPI_MISO))
    except Exception as e:
        print(f"[MASTER] SPI error: {e}")
        hw['spi'] = None

    # Status LEDs
    hw['led_green'] = Pin(config.LED_GREEN, Pin.OUT, value=0)
    hw['led_red'] = Pin(config.LED_RED, Pin.OUT, value=0)

    # nRF24L01+ wireless
    hw['nrf'] = None
    if hw['spi']:
        try:
            hw['nrf'] = NRF24L01(hw['spi'], Pin(config.NRF_CSN), Pin(config.NRF_CE),
                                 channel=config.NRF_CHANNEL,
                                 payload_size=config.NRF_PAYLOAD_SIZE,
                                 data_rate=config.NRF_DATA_RATE,
                                 tx_addr=config.NRF_TX_ADDR,
                                 rx_addr=config.NRF_RX_ADDR)
            print("[MASTER] nRF24L01+ OK")
        except Exception as e:
            print(f"[MASTER] nRF error: {e}")

    # BMI160 IMU
    hw['imu'] = None
    if hw['i2c']:
        try:
            hw['imu'] = BMI160(hw['i2c'], addr=config.BMI160_ADDR,
                               accel_range=ACC_RANGE_4G,
                               gyro_range=GYR_RANGE_500,
                               sample_rate=config.IMU_SAMPLE_RATE)
            print(f"[MASTER] BMI160 OK (ID=0x{hw['imu'].who_am_i():02X})")
        except Exception as e:
            print(f"[MASTER] BMI160 error: {e}")

    # PCA9685 PWM driver
    hw['pca'] = None
    if hw['i2c']:
        try:
            hw['pca'] = PCA9685(hw['i2c'], addr=config.PCA9685_ADDR, freq=50)
            print("[MASTER] PCA9685 OK")
        except Exception as e:
            print(f"[MASTER] PCA9685 error: {e}")

    print("[MASTER] Hardware init complete")
    return hw


def handle_command(pkt, motor_ctrl, fault_mgr, sorter_inst, mode):
    """Process a wireless command from SCADA.

    Returns new mode if changed, else current mode.
    """
    cmd_type = pkt.get('cmd_type', 0)

    if cmd_type == CMD_SET_SPEED:
        motor_id = pkt.get('target', 1)
        speed = pkt.get('value', 0)
        if motor_ctrl:
            motor_ctrl.set_speed(motor_id, speed)
    elif cmd_type == CMD_SET_SERVO:
        servo_id = pkt.get('target', 1)
        angle = pkt.get('value', 90)
        if motor_ctrl:
            motor_ctrl.set_servo_angle(servo_id, angle)
    elif cmd_type == CMD_SET_THRESHOLD:
        value = pkt.get('value', 50)
        if sorter_inst:
            sorter_inst.set_threshold(value)
    elif cmd_type == CMD_RESET_FAULT:
        fault_mgr.reset()
    elif cmd_type == CMD_SET_MODE:
        mode = pkt.get('mode', MODE_NORMAL)
    elif cmd_type == CMD_EMERGENCY_STOP:
        if motor_ctrl:
            motor_ctrl.emergency_stop_all()
        mode = MODE_IDLE

    return mode


def run_comparison(power_mgr, motor_ctrl, duration_s=10):
    """Run dumb mode, then smart mode, calculate savings.

    Returns (dumb_avg_W, smart_avg_W, savings_pct).
    """
    print("[MASTER] A/B Comparison: starting DUMB mode...")

    # Dumb mode — all motors 100%
    motor_ctrl.set_speed(1, 100)
    motor_ctrl.set_speed(2, 100)
    dumb_readings = []
    for _ in range(duration_s * 10):
        dumb_readings.append(power_mgr.read_all()['total_W'])
        time.sleep_ms(100)
    dumb_avg = sum(dumb_readings) / max(len(dumb_readings), 1)
    print(f"[MASTER] DUMB avg: {dumb_avg:.3f}W")

    # Smart mode — intelligent speeds
    print("[MASTER] A/B Comparison: starting SMART mode...")
    motor_ctrl.set_speed(1, 60)
    motor_ctrl.set_speed(2, 40)
    smart_readings = []
    for _ in range(duration_s * 10):
        smart_readings.append(power_mgr.read_all()['total_W'])
        time.sleep_ms(100)
    smart_avg = sum(smart_readings) / max(len(smart_readings), 1)
    print(f"[MASTER] SMART avg: {smart_avg:.3f}W")

    savings = (1 - smart_avg / max(dumb_avg, 0.001)) * 100
    print(f"[MASTER] Savings: {savings:.1f}%")

    return dumb_avg, smart_avg, savings


def main():
    """Main entry point."""
    print("=" * 40)
    print("  GridBox — Grid Controller")
    print("  Master Pico (Pico A)")
    print("=" * 40)

    # Init hardware
    hw = init_hardware()

    # Run self-test before anything else
    selftest_failures = startup_selftest(hw)
    if selftest_failures:
        print(f"[MASTER] Continuing with {len(selftest_failures)} degraded component(s)")

    # Init subsystems
    power_mgr = PowerManager()
    print("[MASTER] Power manager OK")

    motor_ctrl = None
    if hw['pca']:
        motor_ctrl = MotorControl(hw['pca'])
        print("[MASTER] Motor control OK")

    imu_reader = None
    if hw['imu']:
        imu_reader = IMUReader(hw['imu'])
        imu_reader.start()
        print("[MASTER] IMU reader started (Core 1)")

    fault_mgr = FaultManager(motor_ctrl)
    print("[MASTER] Fault manager OK")

    es_monitor = EnergySignatureMonitor(adc_pin=config.ADC_MOTOR1_CURRENT)
    print("[MASTER] Energy signature monitor OK")

    sorter_inst = None
    if motor_ctrl:
        sorter_inst = Sorter(motor_ctrl, power_mgr)
        print("[MASTER] Sorter OK")

    led_stations = LEDStations()
    print("[MASTER] LED stations OK")

    # Calibration
    cal = Calibration(power_mgr)
    if cal.auto_load():
        print("[MASTER] Calibration loaded from flash")
        if sorter_inst:
            sorter_inst.set_baseline(cal.get_baseline())
    else:
        print("[MASTER] No saved calibration — using defaults")

    # Start listening for SCADA commands
    if hw['nrf']:
        hw['nrf'].start_listening()

    # Operating mode
    mode = MODE_NORMAL
    calibrated = cal.is_calibrated()

    # A/B comparison results (shared via serial JSON)
    comparison = {'dumb_avg_W': 0, 'smart_avg_W': 0, 'savings_pct': 0, 'done': False}

    # Timing
    boot_ms = time.ticks_ms()
    last_wireless_ms = 0
    last_serial_ms = 0
    loop_count = 0
    cycle_index = 0

    print("\n[MASTER] Entering main loop (100Hz)")
    print("=" * 40)

    try:
        while True:
            now = time.ticks_ms()
            loop_count += 1

            # === 1. Read power manager ===
            power_data = power_mgr.read_all()

            # === 2. Read wireless commands from SCADA ===
            if hw['nrf']:
                data = hw['nrf'].recv()
                if data:
                    pkt = unpack(data) if unpack else None
                    if pkt and pkt['type'] == PKT_COMMAND:
                        mode = handle_command(pkt, motor_ctrl, fault_mgr,
                                              sorter_inst, mode)

            # === 3. Read IMU status ===
            imu_status = "HEALTHY"
            imu_data = {}
            if imu_reader:
                imu_data = imu_reader.get_data()
                imu_status = imu_data.get('status', 'HEALTHY')

            # === 4. Handle DUMB mode (A/B comparison trigger) ===
            if mode == MODE_DUMB and motor_ctrl and not comparison['done']:
                # Run blocking comparison, then return to normal
                dumb_w, smart_w, savings = run_comparison(power_mgr, motor_ctrl)
                comparison['dumb_avg_W'] = round(dumb_w, 3)
                comparison['smart_avg_W'] = round(smart_w, 3)
                comparison['savings_pct'] = round(savings, 1)
                comparison['done'] = True
                mode = MODE_NORMAL
                print(f"[MASTER] Comparison done: {savings:.1f}% savings")

            # === 5. Run fault manager ===
            actions = fault_mgr.update(power_data, imu_status)

            # === 6. Run sorter (only in NORMAL mode) ===
            weight_class = None
            if sorter_inst and mode == MODE_NORMAL:
                weight_class = sorter_inst.process()

            # === 7. Update LED stations ===
            if weight_class and not led_stations.is_active():
                led_stations.run_sequence(weight_class, blocking=False)

            # === 8. Execute fault manager actions ===
            if actions and motor_ctrl:
                fault_mgr.execute_actions(actions)

            # === 9. Status LEDs ===
            state = fault_mgr.get_state()
            if state in ("FAULT", "EMERGENCY"):
                hw['led_red'].value(1)
                hw['led_green'].value(0)
            elif state in ("WARNING", "DRIFT"):
                hw['led_red'].value(loop_count % 10 < 5)  # blink
                hw['led_green'].value(0)
            else:
                hw['led_red'].value(0)
                hw['led_green'].value(1)

            # === 10. Send telemetry via wireless (rotation schedule) ===
            if (hw['nrf'] and pack_power and
                    time.ticks_diff(now, last_wireless_ms) >= config.WIRELESS_SEND_MS):
                last_wireless_ms = now

                # Determine fault source for status/alert packets
                fault_src = FAULT_NONE
                if imu_status == "FAULT":
                    fault_src = FAULT_VIBRATION
                elif (power_data.get('m1_mA', 0) > config.MOTOR_CURRENT_MAX_MA or
                      power_data.get('m2_mA', 0) > config.MOTOR_CURRENT_MAX_MA):
                    fault_src = FAULT_OVERCURRENT
                elif power_data.get('bus_v', 5.0) < config.BUS_VOLTAGE_LOW:
                    fault_src = FAULT_UNDERVOLTAGE

                # ALERT breaks rotation — send immediately on fault
                if "alert" in actions:
                    alert_lvl = ALERT_EMERGENCY if state == "EMERGENCY" else ALERT_FAULT
                    act_bits = 0
                    for a in actions:
                        if a.startswith("stop_motor"):
                            act_bits |= ACT_MOTOR_STOPPED
                        elif a.startswith("shed_"):
                            act_bits |= ACT_LOAD_SHED
                        elif a == "reroute":
                            act_bits |= ACT_REROUTED
                    pkt = pack_alert(
                        alert_lvl, fault_src, now,
                        int(imu_data.get('rms', 0) * 1000),
                        int(max(power_data.get('m1_mA', 0), power_data.get('m2_mA', 0))),
                        int(power_data.get('bus_v', 0) * 1000),
                        act_bits)
                else:
                    # Normal rotation
                    pkt_type = ROTATION[cycle_index % len(ROTATION)]
                    cycle_index += 1

                    if pkt_type == PKT_POWER:
                        mc_st = motor_ctrl.get_state() if motor_ctrl else {}
                        mosfet_bits = 0
                        if mc_st.get('m1_enabled'):
                            mosfet_bits |= 0x01
                        if mc_st.get('m2_enabled'):
                            mosfet_bits |= 0x02
                        if mc_st.get('leds_on'):
                            mosfet_bits |= 0x04
                        if mc_st.get('recycle_on'):
                            mosfet_bits |= 0x08
                        pkt = pack_power(
                            int(power_data.get('bus_v', 0) * 1000),
                            int(power_data.get('m1_mA', 0)),
                            int(power_data.get('m2_mA', 0)),
                            int(power_data.get('m1_W', 0) * 1000),
                            int(power_data.get('m2_W', 0) * 1000),
                            int(power_data.get('total_W', 0) * 1000),
                            int(power_data.get('excess_W', 0) * 1000),
                            motor_ctrl.get_speed(1) if motor_ctrl else 0,
                            motor_ctrl.get_speed(2) if motor_ctrl else 0,
                            motor_ctrl.get_servo_angle(1) if motor_ctrl else 90,
                            motor_ctrl.get_servo_angle(2) if motor_ctrl else 90,
                            int(power_data.get('efficiency', 0)),
                            0, mosfet_bits)

                    elif pkt_type == PKT_STATUS:
                        es_score_val = es_monitor.get_score()
                        es_sig = es_monitor.get_signature()
                        if es_monitor.is_anomaly():
                            es_cls = ES_FAULT
                        elif es_score_val > 0.3:
                            es_cls = ES_PREFAULT
                        elif es_score_val > 0.1:
                            es_cls = ES_DRIFT
                        else:
                            es_cls = ES_HEALTHY
                        fault_stats = fault_mgr.get_stats()
                        shed_lvl = len(fault_stats.get('shed_loads', []))
                        reroute = 1 if "reroute" in actions else 0
                        pkt = pack_status(
                            _STATE_MAP.get(state, 0), fault_src,
                            int(imu_data.get('rms', 0) * 1000),
                            _IMU_MAP.get(imu_status, 0),
                            int(es_score_val * 100), es_cls,
                            int(es_sig.mean_current), int(es_sig.std_current),
                            shed_lvl, mode,
                            time.ticks_diff(now, boot_ms) // 1000,
                            fault_stats.get('faults_today', 0), reroute)

                    elif pkt_type == PKT_PRODUCTION:
                        sort_stats = sorter_inst.get_stats() if sorter_inst else {}
                        pkt = pack_production(
                            sort_stats.get('total_items', 0),
                            sort_stats.get('passed', 0),
                            sort_stats.get('rejected', 0),
                            int(sort_stats.get('reject_rate', 0)),
                            0,  # last_weight_mg
                            _RESULT_MAP.get(sort_stats.get('last_weight_class', 'NONE'), 0),
                            motor_ctrl.get_speed(2) if motor_ctrl else 0,
                            int(config.WEIGHT_THRESHOLD_LIGHT * 1000),
                            int(config.WEIGHT_THRESHOLD_HEAVY * 1000),
                            0,  # station_active
                            1 if led_stations.is_active() else 0)

                    elif pkt_type == PKT_HEARTBEAT:
                        uptime = time.ticks_diff(now, boot_ms) // 1000
                        pkt = pack_heartbeat(now, uptime)

                # Determine criticality: ALERT=3x, COMMAND=2x, others=1x
                is_alert = ("alert" in actions)
                send_packet(hw['nrf'], pkt, critical=is_alert)

                if wireless_stats['consecutive_fail'] >= 10:
                    print("[MASTER] WIRELESS DEGRADED — 10 consecutive send failures")

            # === 10. Print serial JSON for web dashboard ===
            if time.ticks_diff(now, last_serial_ms) >= config.SERIAL_PRINT_MS:
                last_serial_ms = now

                mc_state = motor_ctrl.get_state() if motor_ctrl else {}
                sort_stats = sorter_inst.get_stats() if sorter_inst else {}
                fault_stats = fault_mgr.get_stats()

                serial_data = {
                    'bus_v': power_data.get('bus_v', 0),
                    'm1_mA': power_data.get('m1_mA', 0),
                    'm2_mA': power_data.get('m2_mA', 0),
                    'm1_W': power_data.get('m1_W', 0),
                    'm2_W': power_data.get('m2_W', 0),
                    'total_W': power_data.get('total_W', 0),
                    'efficiency': power_data.get('efficiency', 0),
                    'state': fault_stats.get('state', 'UNKNOWN'),
                    'imu_rms': imu_data.get('rms', 0),
                    'imu_status': imu_status,
                    'es_score': es_monitor.get_score(),
                    'm1_speed': mc_state.get('m1_speed', 0),
                    'm2_speed': mc_state.get('m2_speed', 0),
                    'mode': mode,
                    'total_items': sort_stats.get('total_items', 0),
                    'passed': sort_stats.get('passed', 0),
                    'rejected': sort_stats.get('rejected', 0),
                    'reject_rate': sort_stats.get('reject_rate', 0),
                    'faults_today': fault_stats.get('faults_today', 0),
                    'comparison_done': comparison['done'],
                    'dumb_avg_W': comparison['dumb_avg_W'],
                    'smart_avg_W': comparison['smart_avg_W'],
                    'savings_pct': comparison['savings_pct'],
                    'wireless_sent': wireless_stats['sent'],
                    'wireless_failed': wireless_stats['failed'],
                }
                print(json.dumps(serial_data))

            # === Loop timing ===
            elapsed = time.ticks_diff(time.ticks_ms(), now)
            sleep_ms = config.MAIN_LOOP_MS - elapsed
            if sleep_ms > 0:
                time.sleep_ms(sleep_ms)

    except KeyboardInterrupt:
        print("\n[MASTER] Shutting down...")
        if imu_reader:
            imu_reader.stop()
        if motor_ctrl:
            motor_ctrl.emergency_stop_all()
        if hw['nrf']:
            hw['nrf'].stop_listening()
        hw['led_red'].value(0)
        hw['led_green'].value(0)
        print("[MASTER] Shutdown complete")


if __name__ == "__main__":
    main()
