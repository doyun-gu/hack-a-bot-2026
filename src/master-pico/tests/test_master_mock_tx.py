"""
GridBox — Master: Send Mock Telemetry via nRF
No sensors needed — generates realistic fake data and transmits wirelessly.
Slave (test_slave_rx_display.py) receives and shows on MAX7219 + USB serial.

Upload: mpremote cp src/master-pico/tests/test_master_mock_tx.py :main.py && mpremote reset
"""

from machine import Pin, SPI
import struct
import time

# ── Pins ──
LED = Pin(25, Pin.OUT)
ce = Pin(0, Pin.OUT, value=0)
csn = Pin(1, Pin.OUT, value=1)
spi = SPI(0, baudrate=4_000_000, sck=Pin(2), mosi=Pin(3), miso=Pin(16))

CHANNEL = 100
TX_ADDR = b'GRIDM'

# ── nRF24 minimal driver ──
def nrf_write(reg, val):
    csn.value(0)
    if isinstance(val, int):
        spi.write(bytes([0x20 | reg, val]))
    else:
        spi.write(bytes([0x20 | reg]) + val)
    csn.value(1)

def nrf_read(reg, n=1):
    csn.value(0)
    spi.write(bytes([reg & 0x1F]))
    data = spi.read(n)
    csn.value(1)
    return data[0] if n == 1 else data

def nrf_send(payload):
    ce.value(0)
    csn.value(0); spi.write(b'\xE1'); csn.value(1)
    csn.value(0); spi.write(b'\xA0' + payload); csn.value(1)
    ce.value(1); time.sleep_us(15); ce.value(0)
    for _ in range(100):
        status = nrf_read(0x07)
        if status & 0x20:
            nrf_write(0x07, 0x70)
            return True
        if status & 0x10:
            nrf_write(0x07, 0x70)
            csn.value(0); spi.write(b'\xE1'); csn.value(1)
            return False
        time.sleep_us(100)
    return False

def nrf_init_tx():
    ce.value(0)
    nrf_write(0x00, 0x0E)
    nrf_write(0x01, 0x01)
    nrf_write(0x02, 0x01)
    nrf_write(0x03, 0x03)
    nrf_write(0x04, 0x4A)
    nrf_write(0x05, CHANNEL)
    nrf_write(0x06, 0x26)
    nrf_write(0x11, 32)
    csn.value(0); spi.write(b'\x30' + TX_ADDR); csn.value(1)
    csn.value(0); spi.write(b'\x2A' + TX_ADDR); csn.value(1)
    nrf_write(0x07, 0x70)
    time.sleep_ms(5)

# ── Simple pseudo-random (no urandom on some Picos) ──
_seed = time.ticks_us()
def rng():
    global _seed
    _seed = (_seed * 1103515245 + 12345) & 0x7FFFFFFF
    return _seed

def rand_float(low, high):
    return low + (rng() % 1000) / 1000.0 * (high - low)

# ══════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════
print("=" * 50)
print("  MASTER MOCK TX — Fake telemetry via nRF")
print("  No sensors needed — just nRF wired")
print("=" * 50)

nrf_init_tx()
print("nRF TX ready, channel", CHANNEL)
print()

seq = 0
sent = 0
failed = 0
t_start = time.ticks_ms()

# Simulated state
motor_speed = 0
motor_dir = 5
servo_pos = 0
servo_angles = [0, 90, 180]
t_servo = time.ticks_ms()
fault_active = False
fault_countdown = 0
items = 0
passed = 0
rejected = 0

while True:
    now = time.ticks_ms()

    # Ramp motor speed up and down
    motor_speed += motor_dir
    if motor_speed >= 100:
        motor_dir = -5
    elif motor_speed <= 0:
        motor_dir = 5
    motor_speed = max(0, min(100, motor_speed))

    # Cycle servo every 3 seconds
    if time.ticks_diff(now, t_servo) > 3000:
        servo_pos = (servo_pos + 1) % 3
        t_servo = now

    # Simulate occasional faults (every ~30 seconds for 5 seconds)
    if not fault_active and rng() % 150 == 0:
        fault_active = True
        fault_countdown = 25  # 25 * 200ms = 5 seconds
    if fault_active:
        fault_countdown -= 1
        if fault_countdown <= 0:
            fault_active = False

    # Simulate production items
    if not fault_active and rng() % 10 == 0:
        items += 1
        if rng() % 7 == 0:
            rejected += 1
        else:
            passed += 1

    # Generate mock sensor values
    bus_v = rand_float(4.7, 5.1)
    m1_mA = motor_speed * 4 + rand_float(-10, 10)
    m2_mA = rand_float(200, 320)
    imu_rms = rand_float(3.0, 5.0) if fault_active else rand_float(0.2, 0.5)
    total_W = bus_v * (m1_mA + m2_mA) / 1000
    efficiency = rand_float(60, 85)
    servo_deg = servo_angles[servo_pos]

    # Determine state
    if fault_active:
        state = 3  # FAULT
    elif bus_v < 4.5:
        state = 2  # WARNING
    else:
        state = 1  # NORMAL

    # Pack 32-byte packet
    # type(1) seq(1) state(1) servo(1) motor%(1) bus_mV(2) m1_mA(2) m2_mA(2)
    # imu_rms_x100(2) total_W_x100(2) eff(1) items(2) passed(2) rejected(2) pad(10)
    payload = struct.pack('<BBBBBHHHHHBHHh8s',
        0x01,                    # type: telemetry
        seq & 0xFF,              # sequence
        state,                   # 1=normal, 2=warning, 3=fault
        servo_deg,               # servo angle 0/90/180
        motor_speed,             # motor %
        int(bus_v * 1000),       # bus mV
        int(max(0, m1_mA)),      # motor 1 mA
        int(max(0, m2_mA)),      # motor 2 mA
        int(imu_rms * 100),      # IMU RMS * 100
        int(total_W * 100),      # total watts * 100
        int(efficiency),         # efficiency %
        items,                   # total items
        passed,                  # passed items
        rejected,                # rejected items
        b'\x00' * 8              # padding
    )

    ok = nrf_send(payload)
    LED.toggle()

    if ok:
        sent += 1
    else:
        failed += 1

    elapsed = time.ticks_diff(now, t_start) // 1000
    state_str = ["?", "NORMAL", "WARNING", "FAULT"][state]
    ack_str = "ACK" if ok else "FAIL"

    print(f"[{seq:4d}] {state_str:7s} servo={servo_deg:3d}° motor={motor_speed:3d}% "
          f"bus={bus_v:.1f}V m1={m1_mA:.0f}mA imu={imu_rms:.2f}g "
          f"items={items} → {ack_str}  (sent:{sent} fail:{failed} {elapsed}s)")

    seq += 1
    time.sleep_ms(200)
