"""
GridBox — Slave Pico (Pico B) Main
SCADA display and control loop.

Receives telemetry from Pico A, displays on OLED dashboard,
reads operator input, sends commands back to Pico A.
"""

from machine import Pin, I2C, SPI, ADC
import time

import config
from nrf24l01 import NRF24L01
from ssd1306 import SSD1306
from dashboard import Dashboard
from operator import OperatorInput
from commander import Commander

# Import protocol (copied to micropython dir from src/shared/)
try:
    from protocol import (unpack, PKT_POWER, PKT_STATUS, PKT_PRODUCTION,
                          PKT_HEARTBEAT, PKT_ALERT,
                          MODE_NORMAL, MODE_MANUAL, MODE_IDLE)
except ImportError:
    print("[SLAVE] WARNING: protocol.py not found")
    unpack = None
    PKT_POWER = 0x01
    PKT_STATUS = 0x02
    PKT_PRODUCTION = 0x03
    PKT_HEARTBEAT = 0x04
    PKT_ALERT = 0x05

# Enum -> string mappings for display
_STATE_NAMES = {0: "NORMAL", 1: "DRIFT", 2: "WARNING", 3: "FAULT", 4: "EMERGENCY"}
_IMU_NAMES = {0: "HEALTHY", 1: "WARNING", 2: "FAULT"}
_RESULT_NAMES = {0: "PASS", 1: "REJECT_HEAVY", 2: "REJECT_LIGHT", 3: "JAM"}


def init_hardware():
    """Initialise all hardware peripherals."""
    print("[SLAVE] Initialising hardware...")
    hw = {}

    # I2C bus (OLED)
    try:
        hw['i2c'] = I2C(config.I2C_ID, sda=Pin(config.I2C_SDA),
                        scl=Pin(config.I2C_SCL), freq=config.I2C_FREQ)
        devices = hw['i2c'].scan()
        print(f"[SLAVE] I2C devices: {[hex(d) for d in devices]}")
    except Exception as e:
        print(f"[SLAVE] I2C error: {e}")
        hw['i2c'] = None

    # SPI bus (nRF24L01+)
    try:
        hw['spi'] = SPI(config.SPI_ID, baudrate=config.SPI_BAUD, polarity=0, phase=0,
                        sck=Pin(config.SPI_SCK), mosi=Pin(config.SPI_MOSI),
                        miso=Pin(config.SPI_MISO))
    except Exception as e:
        print(f"[SLAVE] SPI error: {e}")
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
            print("[SLAVE] nRF24L01+ OK")
        except Exception as e:
            print(f"[SLAVE] nRF error: {e}")

    # OLED display
    hw['oled'] = None
    if hw['i2c']:
        try:
            hw['oled'] = SSD1306(hw['i2c'], config.OLED_WIDTH,
                                 config.OLED_HEIGHT, config.SSD1306_ADDR)
            print("[SLAVE] OLED OK")
        except Exception as e:
            print(f"[SLAVE] OLED error: {e}")

    print("[SLAVE] Hardware init complete")
    return hw


def main():
    """Main entry point."""
    print("=" * 40)
    print("  GridBox — SCADA Station")
    print("  Slave Pico (Pico B)")
    print("=" * 40)

    # Init hardware
    hw = init_hardware()

    # Init subsystems
    op_input = OperatorInput()
    print("[SLAVE] Operator input OK")

    dash = None
    if hw['oled']:
        dash = Dashboard(hw['oled'])
        print("[SLAVE] Dashboard OK")

    cmd = None
    if hw['nrf']:
        cmd = Commander(hw['nrf'])
        print("[SLAVE] Commander OK")

    # Start listening for telemetry
    if hw['nrf']:
        hw['nrf'].start_listening()

    # Telemetry data (updated from wireless packets)
    telemetry = {
        'm1_speed': 0, 'm1_mA': 0, 'm1_W': 0,
        'm2_speed': 0, 'm2_mA': 0, 'm2_W': 0,
        'servo1_angle': 90, 'servo2_angle': 90,
        'bus_v': 0, 'state': 'UNKNOWN',
        'total_W': 0, 'excess_W': 0, 'efficiency': 0,
        'faults_today': 0, 'rerouted_mWs': 0,
        'imu_status': 'UNKNOWN', 'es_score': 0,
        'total_items': 0, 'passed': 0, 'rejected': 0,
        'reject_rate': 0, 'last_weight_class': 'NONE',
        'belt_speed': 5, 'threshold': 50,
        'joy_x': 50, 'joy_y': 50, 'button': False, 'pot_value': 50,
        'mode': 0,
        # Comparison results (populated by PKT_STATUS when comparison runs)
        'dumb_avg_W': 0, 'smart_avg_W': 0, 'savings_pct': 0,
    }

    # Timing
    last_packet_ms = time.ticks_ms()
    last_display_ms = 0
    last_command_ms = 0
    link_alive = False
    prev_direction = "CENTRE"
    prev_pot = 50

    print("\n[SLAVE] Entering main loop")
    print("=" * 40)

    try:
        while True:
            now = time.ticks_ms()

            # === 1. Receive wireless packet from Pico A ===
            if hw['nrf']:
                data = hw['nrf'].recv()
                if data and unpack:
                    pkt = unpack(data)
                    if pkt:
                        last_packet_ms = now
                        link_alive = True
                        pkt_type = pkt['type']

                        if pkt_type == PKT_POWER:
                            telemetry['bus_v'] = pkt['bus_voltage_mv'] / 1000
                            telemetry['m1_mA'] = pkt['motor1_current_ma']
                            telemetry['m2_mA'] = pkt['motor2_current_ma']
                            telemetry['m1_W'] = pkt['motor1_power_mw'] / 1000
                            telemetry['m2_W'] = pkt['motor2_power_mw'] / 1000
                            telemetry['total_W'] = pkt['total_power_mw'] / 1000
                            telemetry['excess_W'] = pkt['excess_power_mw'] / 1000
                            telemetry['m1_speed'] = pkt['motor1_speed_pct']
                            telemetry['m2_speed'] = pkt['motor2_speed_pct']
                            telemetry['servo1_angle'] = pkt['servo1_angle']
                            telemetry['servo2_angle'] = pkt['servo2_angle']
                            telemetry['efficiency'] = pkt['efficiency_pct']

                        elif pkt_type == PKT_STATUS:
                            telemetry['state'] = _STATE_NAMES.get(pkt['system_state'], 'UNKNOWN')
                            telemetry['imu_status'] = _IMU_NAMES.get(pkt['imu_state'], 'UNKNOWN')
                            telemetry['es_score'] = pkt['es_score_x100'] / 100
                            telemetry['faults_today'] = pkt['faults_today']
                            telemetry['mode'] = pkt['mode']

                        elif pkt_type == PKT_PRODUCTION:
                            telemetry['total_items'] = pkt['total_items']
                            telemetry['passed'] = pkt['passed_items']
                            telemetry['rejected'] = pkt['rejected_items']
                            telemetry['reject_rate'] = pkt['reject_rate_pct']
                            telemetry['last_weight_class'] = _RESULT_NAMES.get(pkt['last_result'], 'NONE')
                            telemetry['belt_speed'] = pkt['belt_speed_pct']

                        elif pkt_type == PKT_HEARTBEAT:
                            pass  # link alive confirmed above

                        elif pkt_type == PKT_ALERT:
                            telemetry['state'] = 'EMERGENCY'

            # === 2. Check heartbeat timeout ===
            if time.ticks_diff(now, last_packet_ms) > config.HEARTBEAT_TIMEOUT_MS:
                link_alive = False

            # === 3. Read operator input ===
            joy_x, joy_y, btn = op_input.read_joystick()
            pot = op_input.read_potentiometer()
            direction = op_input.get_direction()
            long_press = op_input.is_long_press()

            telemetry['joy_x'] = joy_x
            telemetry['joy_y'] = joy_y
            telemetry['button'] = btn
            telemetry['pot_value'] = pot

            # === 4. Handle view switching (joystick up/down) ===
            if dash and direction != prev_direction:
                if direction == "UP":
                    dash.prev_view()
                elif direction == "DOWN":
                    dash.next_view()
            prev_direction = direction

            # === 5. Handle long press (emergency stop) ===
            if long_press and cmd:
                cmd.send_emergency_stop()
                telemetry['state'] = 'EMERGENCY'

            # === 6. Send commands if in manual mode or input changed ===
            if cmd and dash and dash.current_view == config.VIEW_MANUAL:
                if time.ticks_diff(now, last_command_ms) >= config.COMMAND_SEND_MS:
                    last_command_ms = now
                    # Send joystick as motor speed override
                    cmd.send_override(1, joy_x)
                    cmd.send_override(2, joy_y)

                    # Send potentiometer as threshold if changed
                    if abs(pot - prev_pot) > 3:
                        cmd.send_threshold(pot)
                        prev_pot = pot
                        telemetry['threshold'] = pot

                    # Button toggles servo (send mode toggle)
                    if btn:
                        cmd.send_reset()

            # === 7. Update dashboard ===
            if dash and time.ticks_diff(now, last_display_ms) >= config.DISPLAY_UPDATE_MS:
                last_display_ms = now

                if link_alive:
                    dash.render(telemetry)
                else:
                    dash.render_link_lost()

            # === 8. Status LEDs ===
            if link_alive:
                hw['led_green'].value(1)
                hw['led_red'].value(0)
            else:
                hw['led_green'].value(0)
                hw['led_red'].value(1)

            # === Loop timing ===
            elapsed = time.ticks_diff(time.ticks_ms(), now)
            sleep_ms = config.MAIN_LOOP_MS - elapsed
            if sleep_ms > 0:
                time.sleep_ms(sleep_ms)

    except KeyboardInterrupt:
        print("\n[SLAVE] Shutting down...")
        if hw['nrf']:
            hw['nrf'].stop_listening()
        if hw['oled']:
            hw['oled'].clear()
        hw['led_red'].value(0)
        hw['led_green'].value(0)
        print("[SLAVE] Shutdown complete")


if __name__ == "__main__":
    main()
