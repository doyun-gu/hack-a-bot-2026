"""
Test: Datagram Protocol over Wireless — MASTER (Pico A)
Sends all 6 packet types in rotation, listens for COMMAND replies.
Blinks LED on every successful send. Shows packet stats.

Flash as main.py for standalone operation (external power, no USB).
Or run via: mpremote run test_datagram_master.py

Pair with: src/slave-pico/tests/test_datagram_slave.py on Pico B
"""

from machine import Pin, SPI
import time
import config
from nrf24l01 import NRF24L01
import protocol

print("=" * 50)
print("  Datagram Protocol Test — MASTER (Pico A)")
print("  Sends POWER/STATUS/PRODUCTION/HEARTBEAT/ALERT")
print("  Listens for COMMAND replies from Pico B")
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
print()

# Simulated sensor data (increments to show live values)
sim_uptime = 0
sim_items = 0
sent_ok = 0
sent_fail = 0
cmds_received = 0
start_ms = time.ticks_ms()

PKT_NAMES = {
    protocol.PKT_POWER: "POWER",
    protocol.PKT_STATUS: "STATUS",
    protocol.PKT_PRODUCTION: "PRODUCTION",
    protocol.PKT_HEARTBEAT: "HEARTBEAT",
    protocol.PKT_ALERT: "ALERT",
}

rotation_idx = 0

while True:
    sim_uptime = time.ticks_diff(time.ticks_ms(), start_ms) // 1000
    sim_items += 1

    # Pick next packet type from rotation
    pkt_type = protocol.ROTATION[rotation_idx % len(protocol.ROTATION)]
    rotation_idx += 1

    # Every 20th cycle, inject an ALERT to test that too
    if rotation_idx % 20 == 0:
        pkt_type = protocol.PKT_ALERT

    # Build packet with simulated data
    if pkt_type == protocol.PKT_POWER:
        pkt = protocol.pack_power(
            bus_mv=4900, m1_ma=350 + (sim_items % 50), m2_ma=200 + (sim_items % 30),
            m1_mw=1700, m2_mw=980, total_mw=2680, excess_mw=1320,
            m1_spd=65, m2_spd=40, s1_ang=90, s2_ang=45,
            eff=37, leds=0x0F, mosfets=0x03)

    elif pkt_type == protocol.PKT_STATUS:
        pkt = protocol.pack_status(
            sys_state=protocol.SYS_NORMAL, fault_src=protocol.FAULT_NONE,
            imu_rms_mg=800 + (sim_items % 200), imu_state=protocol.IMU_HEALTHY,
            es_score_x100=15, es_class=protocol.ES_HEALTHY,
            es_mean_ma=350, es_std_ma=20,
            shed_level=0, mode=protocol.MODE_NORMAL,
            uptime_s=sim_uptime, faults_today=0, reroute=0)

    elif pkt_type == protocol.PKT_PRODUCTION:
        pkt = protocol.pack_production(
            total=sim_items, passed=sim_items - 3, rejected=3,
            reject_pct=6, last_weight_mg=1500, last_result=0,
            belt_spd=60, thresh_min_mg=500, thresh_max_mg=5000,
            station_active=1, sorting_active=1)

    elif pkt_type == protocol.PKT_HEARTBEAT:
        pkt = protocol.pack_heartbeat(
            timestamp_ms=time.ticks_ms(), uptime_s=sim_uptime,
            core0_pct=45, core1_pct=80,
            wl_sent=sent_ok, wl_failed=sent_fail,
            wl_reliability=int(sent_ok * 100 / max(sent_ok + sent_fail, 1)))

    elif pkt_type == protocol.PKT_ALERT:
        pkt = protocol.pack_alert(
            level=protocol.ALERT_WARNING, source=protocol.FAULT_VIBRATION,
            timestamp_ms=time.ticks_ms(), imu_mg=2500, motor_ma=850,
            bus_mv=4100, action=protocol.ACT_MOTOR_STOPPED)

    else:
        continue

    # Send packet
    name = PKT_NAMES.get(pkt_type, "???")
    ok = nrf.send(pkt)

    if ok:
        sent_ok += 1
        led.toggle()
        led_green.value(1)
        led_red.value(0)
        rel = int(sent_ok * 100 / (sent_ok + sent_fail))
        print(f"[{sent_ok + sent_fail:4d}] TX {name:12s} OK  (reliability: {rel}%)")
    else:
        sent_fail += 1
        led_red.value(1)
        led_green.value(0)
        print(f"[{sent_ok + sent_fail:4d}] TX {name:12s} FAIL (no ACK)")

    # Listen briefly for COMMAND replies from Pico B
    nrf.start_listening()
    deadline = time.ticks_add(time.ticks_ms(), 100)
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        data = nrf.recv()
        if data and len(data) == 32 and data[0] == protocol.PKT_COMMAND:
            cmds_received += 1
            cmd = protocol.unpack_command(data)
            print(f"  >> COMMAND received! type={cmd['cmd_type']} target={cmd['target']} value={cmd['value']} (total: {cmds_received})")
            break
        time.sleep_us(500)
    nrf.stop_listening()

    # Stats every 50 packets
    if (sent_ok + sent_fail) % 50 == 0:
        total = sent_ok + sent_fail
        rel = int(sent_ok * 100 / max(total, 1))
        print(f"\n--- Stats: {sent_ok}/{total} OK ({rel}%), commands received: {cmds_received}, uptime: {sim_uptime}s ---\n")

    time.sleep_ms(200)
