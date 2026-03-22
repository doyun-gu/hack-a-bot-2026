"""
Test: Datagram Protocol over Wireless — SLAVE (Pico B)
Listens for all packet types, unpacks and displays them.
Sends COMMAND replies to test B->A direction.

Flash as main.py for standalone operation (external power, no USB).
Or run via: mpremote run test_datagram_slave.py

Pair with: src/master-pico/tests/test_datagram_master.py on Pico A
"""

from machine import Pin, SPI
import time
import config
from nrf24l01 import NRF24L01
import protocol

print("=" * 50)
print("  Datagram Protocol Test — SLAVE (Pico B)")
print("  Listens for all 6 packet types from Pico A")
print("  Sends COMMAND replies every 10 packets")
print("=" * 50)

# Init SPI + nRF
spi = SPI(config.SPI_ID, baudrate=config.SPI_BAUD, polarity=0, phase=0,
          sck=Pin(config.SPI_SCK), mosi=Pin(config.SPI_MOSI),
          miso=Pin(config.SPI_MISO))

nrf = NRF24L01(spi, Pin(config.NRF_CSN), Pin(config.NRF_CE),
               channel=config.NRF_CHANNEL,
               payload_size=config.NRF_PAYLOAD_SIZE,
               data_rate=config.NRF_DATA_RATE,
               tx_addr=config.NRF_TX_ADDR,
               rx_addr=config.NRF_RX_ADDR)

led = Pin(config.LED_ONBOARD, Pin.OUT)
led_green = Pin(config.LED_GREEN, Pin.OUT)
led_red = Pin(config.LED_RED, Pin.OUT)

print(f"TX: {config.NRF_TX_ADDR}  RX: {config.NRF_RX_ADDR}  CH: {config.NRF_CHANNEL}")
print("Listening...\n")

# Packet counters by type
PKT_NAMES = {
    protocol.PKT_POWER: "POWER",
    protocol.PKT_STATUS: "STATUS",
    protocol.PKT_PRODUCTION: "PRODUCTION",
    protocol.PKT_HEARTBEAT: "HEARTBEAT",
    protocol.PKT_ALERT: "ALERT",
    protocol.PKT_COMMAND: "COMMAND",
}

counts = {t: 0 for t in PKT_NAMES}
total_rx = 0
bad_rx = 0
cmds_sent = 0

nrf.start_listening()

while True:
    data = nrf.recv()
    if data and len(data) == 32:
        total_rx += 1
        led.toggle()

        # Try to unpack
        parsed = protocol.unpack(data)
        if parsed is None:
            bad_rx += 1
            print(f"[{total_rx:4d}] BAD PACKET (type=0x{data[0]:02X}, could not unpack)")
            led_red.value(1)
            continue

        pkt_type = parsed['type']
        name = PKT_NAMES.get(pkt_type, f"0x{pkt_type:02X}")
        counts[pkt_type] = counts.get(pkt_type, 0) + 1

        led_green.value(1)
        led_red.value(0)

        # Display key fields based on type
        if pkt_type == protocol.PKT_POWER:
            print(f"[{total_rx:4d}] POWER      seq={parsed['seq']:3d}  "
                  f"bus={parsed['bus_voltage_mv']}mV  "
                  f"M1={parsed['motor1_current_ma']}mA  "
                  f"M2={parsed['motor2_current_ma']}mA  "
                  f"total={parsed['total_power_mw']}mW  "
                  f"eff={parsed['efficiency_pct']}%")

        elif pkt_type == protocol.PKT_STATUS:
            states = ["NORMAL", "DRIFT", "WARNING", "FAULT", "EMERGENCY"]
            modes = ["IDLE", "NORMAL", "DUMB", "MANUAL", "CALIBRATE", "LEARNING", "EMERGENCY"]
            st = states[parsed['system_state']] if parsed['system_state'] < len(states) else "?"
            md = modes[parsed['mode']] if parsed['mode'] < len(modes) else "?"
            print(f"[{total_rx:4d}] STATUS     seq={parsed['seq']:3d}  "
                  f"state={st}  mode={md}  "
                  f"IMU={parsed['imu_rms_mg']}mg  "
                  f"uptime={parsed['uptime_s']}s  "
                  f"faults={parsed['faults_today']}")

        elif pkt_type == protocol.PKT_PRODUCTION:
            print(f"[{total_rx:4d}] PRODUCTION seq={parsed['seq']:3d}  "
                  f"items={parsed['total_items']}  "
                  f"pass={parsed['passed_items']}  "
                  f"reject={parsed['rejected_items']} ({parsed['reject_rate_pct']}%)  "
                  f"belt={parsed['belt_speed_pct']}%")

        elif pkt_type == protocol.PKT_HEARTBEAT:
            print(f"[{total_rx:4d}] HEARTBEAT  seq={parsed['seq']:3d}  "
                  f"uptime={parsed['uptime_s']}s  "
                  f"core0={parsed['core0_load_pct']}%  "
                  f"core1={parsed['core1_load_pct']}%  "
                  f"wl={parsed['wireless_sent']}/{parsed['wireless_sent']+parsed['wireless_failed']} "
                  f"({parsed['wireless_reliability_pct']}%)")

        elif pkt_type == protocol.PKT_ALERT:
            levels = ["INFO", "WARNING", "FAULT", "EMERGENCY"]
            sources = ["NONE", "VIBRATION", "OVERCURRENT", "UNDERVOLTAGE", "INTERMITTENT", "JAM"]
            lv = levels[parsed['alert_level']] if parsed['alert_level'] < len(levels) else "?"
            src = sources[parsed['alert_source']] if parsed['alert_source'] < len(sources) else "?"
            print(f"[{total_rx:4d}] !! ALERT   seq={parsed['seq']:3d}  "
                  f"level={lv}  source={src}  "
                  f"IMU={parsed['imu_rms_mg']}mg  "
                  f"motor={parsed['motor_current_ma']}mA  "
                  f"bus={parsed['bus_voltage_mv']}mV")

        else:
            print(f"[{total_rx:4d}] {name:10s} seq={parsed['seq']:3d}  (raw: {parsed})")

        # Send a COMMAND reply every 10 packets to test B->A
        if total_rx % 10 == 0:
            nrf.stop_listening()
            cmd = protocol.pack_command(
                cmd_type=protocol.CMD_SET_SPEED,
                target=1, value=75 + (cmds_sent % 25), mode=0)
            ok = nrf.send(cmd)
            cmds_sent += 1
            if ok:
                print(f"  << COMMAND sent (speed={75 + ((cmds_sent-1) % 25)}, ACK=yes, total: {cmds_sent})")
            else:
                print(f"  << COMMAND sent (ACK=no, total: {cmds_sent})")
            nrf.start_listening()

        # Summary every 50 packets
        if total_rx % 50 == 0:
            print(f"\n--- Stats after {total_rx} packets (bad: {bad_rx}) ---")
            for t, n in sorted(counts.items()):
                if n > 0:
                    print(f"  {PKT_NAMES.get(t, '?'):12s}: {n}")
            print(f"  Commands sent: {cmds_sent}")
            print()

    time.sleep_ms(5)
