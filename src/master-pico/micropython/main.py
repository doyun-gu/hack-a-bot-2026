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
    from protocol import (pack_data, pack_heartbeat, unpack,
                          PKT_COMMAND, CMD_SET_MOTOR_SPEED, CMD_SET_THRESHOLD,
                          CMD_RESET_FAULT, CMD_SET_MODE, CMD_EMERGENCY_STOP,
                          MODE_NORMAL, MODE_DUMB, MODE_MANUAL, MODE_CALIBRATE,
                          MODE_IDLE, FLAG_CALIBRATED)
except ImportError:
    print("[MASTER] WARNING: protocol.py not found, wireless disabled")
    pack_data = None


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
    cmd_type = pkt.get('test_level', 0)

    if cmd_type == CMD_SET_MOTOR_SPEED:
        motor_id = pkt.get('joy_x', 1)
        speed = pkt.get('joy_y', 0)
        if motor_ctrl:
            motor_ctrl.set_speed(motor_id, speed)
    elif cmd_type == CMD_SET_THRESHOLD:
        value = pkt.get('joy_x', 50)
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


def main():
    """Main entry point."""
    print("=" * 40)
    print("  GridBox — Grid Controller")
    print("  Master Pico (Pico A)")
    print("=" * 40)

    # Init hardware
    hw = init_hardware()

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

    # Timing
    last_wireless_ms = 0
    last_heartbeat_ms = 0
    last_serial_ms = 0
    loop_count = 0

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

            # === 4. Run fault manager ===
            actions = fault_mgr.update(power_data, imu_status)

            # === 5. Run sorter ===
            weight_class = None
            if sorter_inst and mode == MODE_NORMAL:
                weight_class = sorter_inst.process()

            # === 6. Update LED stations ===
            if weight_class and not led_stations.is_active():
                led_stations.run_sequence(weight_class, blocking=False)

            # === 7. Execute fault manager actions ===
            if actions and motor_ctrl:
                fault_mgr.execute_actions(actions)

            # === 8. Status LEDs ===
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

            # === 9. Send telemetry via wireless ===
            if (hw['nrf'] and pack_data and
                    time.ticks_diff(now, last_wireless_ms) >= config.WIRELESS_SEND_MS):
                last_wireless_ms = now

                roll = imu_data.get('ax', 0.0)
                pitch = imu_data.get('ay', 0.0)
                gyro = imu_data.get('rms', 0.0)

                flags = 0
                if state in ("FAULT", "EMERGENCY"):
                    flags |= 0x01
                if calibrated:
                    flags |= FLAG_CALIBRATED

                m1_speed = motor_ctrl.get_speed(1) if motor_ctrl else 0
                m2_speed = motor_ctrl.get_speed(2) if motor_ctrl else 0

                pkt = pack_data(roll, pitch, gyro,
                                m1_speed, m2_speed,
                                mode, 0, flags, now)

                hw['nrf'].stop_listening()
                hw['nrf'].send(pkt)
                hw['nrf'].start_listening()

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
