"""
GridBox — Demo Master (Pico A)
Runs the full demo sequence autonomously.

REAL: nRF wireless, BMI160 IMU, PCA9685 (motors/servos), recycle path LED
SIMULATED: ADC values (preset, responds to motor state)

Flash as main.py for standalone demo day operation.
Usage: mpremote run src/demo/demo_master.py
"""

from machine import Pin, SPI, I2C, ADC
import struct
import time
import math

# ============ PIN CONFIG ============
SPI_SCK = 2
SPI_MOSI = 3
SPI_MISO = 16
NRF_CE = 0
NRF_CSN = 1
I2C_SDA = 4
I2C_SCL = 5
RECYCLE_PIN = 13
LED_PIN = 25

# nRF settings
NRF_CHANNEL = 100
TX_ADDR = b'NSYNT'
RX_ADDR = b'NSYNR'

# I2C addresses
BMI160_ADDR = 0x68
PCA9685_ADDR = 0x40

# PCA9685 channels
SERVO_VALVE = 0
SERVO_GATE = 1
MOTOR1_CH = 2
MOTOR2_CH = 3

# ============ PACKET TYPES ============
PKT_POWER = 0x01
PKT_STATUS = 0x02
PKT_PRODUCTION = 0x03
PKT_HEARTBEAT = 0x04
PKT_ALERT = 0x05

# States
STATE_BOOT = 0
STATE_READY = 1
STATE_RUNNING = 2
STATE_FAULT = 3
STATE_RECOVERY = 4
STATE_RECYCLE = 5
STATE_DONE = 6

STATE_NAMES = ['BOOT', 'READY', 'RUN', 'FAULT', 'RECOVER', 'RECYCLE', 'DONE']

# ============ GLOBALS ============
seq = 0
state = STATE_BOOT
motor1_on = False
motor2_on = False
fault_active = False
items_produced = 0
items_passed = 0
items_rejected = 0
cycle_count = 0
start_time = 0
imu_rms = 0.0


# ============ nRF24L01+ MINIMAL DRIVER ============
class NRF:
    def __init__(self):
        self.spi = SPI(0, baudrate=10_000_000, polarity=0, phase=0,
                       sck=Pin(SPI_SCK), mosi=Pin(SPI_MOSI), miso=Pin(SPI_MISO))
        self.ce = Pin(NRF_CE, Pin.OUT, value=0)
        self.csn = Pin(NRF_CSN, Pin.OUT, value=1)
        self._init_radio()

    def _reg_write(self, reg, val):
        self.csn(0)
        self.spi.readinto(bytearray(1), 0x20 | reg)
        self.spi.readinto(bytearray(1), val)
        self.csn(1)

    def _reg_write_bytes(self, reg, data):
        self.csn(0)
        self.spi.readinto(bytearray(1), 0x20 | reg)
        self.spi.write(data)
        self.csn(1)

    def _reg_read(self, reg):
        self.csn(0)
        self.spi.readinto(bytearray(1), reg)
        result = bytearray(1)
        self.spi.readinto(result)
        self.csn(1)
        return result[0]

    def _flush_tx(self):
        self.csn(0)
        self.spi.readinto(bytearray(1), 0xE1)
        self.csn(1)

    def _init_radio(self):
        time.sleep_ms(100)
        self._reg_write(0x00, 0x0C)       # CONFIG: CRC enabled, 2-byte
        self._reg_write(0x01, 0x00)       # EN_AA: disable auto-ack
        self._reg_write(0x02, 0x03)       # EN_RXADDR: pipes 0+1
        self._reg_write(0x03, 0x03)       # SETUP_AW: 5-byte address
        self._reg_write(0x04, 0x00)       # SETUP_RETR: no retry
        self._reg_write(0x05, NRF_CHANNEL)
        self._reg_write(0x06, 0x26)       # RF_SETUP: 250kbps, 0dBm
        self._reg_write(0x11, 32)         # RX_PW_P0: 32 bytes
        self._reg_write(0x12, 32)         # RX_PW_P1: 32 bytes
        self._reg_write_bytes(0x10, TX_ADDR)   # TX_ADDR
        self._reg_write_bytes(0x0A, TX_ADDR)   # RX_ADDR_P0
        self._reg_write_bytes(0x0B, RX_ADDR)   # RX_ADDR_P1
        self._flush_tx()
        self._reg_write(0x07, 0x70)       # clear status flags
        status = self._reg_read(0x07)
        print(f"  nRF status: 0x{status:02X} {'OK' if status == 0x0E else 'CHECK'}")

    def send(self, data):
        """Send 32-byte packet."""
        assert len(data) == 32
        self.ce(0)
        self._reg_write(0x00, 0x0C)  # TX mode
        self._reg_write(0x00, 0x0E)  # PWR_UP
        time.sleep_ms(2)
        self._flush_tx()
        self.csn(0)
        self.spi.readinto(bytearray(1), 0xA0)  # W_TX_PAYLOAD
        self.spi.write(data)
        self.csn(1)
        self.ce(1)
        time.sleep_ms(1)
        self.ce(0)
        self._reg_write(0x07, 0x70)  # clear flags


# ============ IMU MINIMAL DRIVER ============
class IMU:
    def __init__(self, i2c):
        self.i2c = i2c
        self.ok = False
        try:
            chip_id = i2c.readfrom_mem(BMI160_ADDR, 0x00, 1)[0]
            if chip_id == 0xD1:
                i2c.writeto_mem(BMI160_ADDR, 0x7E, bytes([0x11]))  # accel normal
                time.sleep_ms(50)
                i2c.writeto_mem(BMI160_ADDR, 0x7E, bytes([0x15]))  # gyro normal
                time.sleep_ms(80)
                self.ok = True
                print(f"  BMI160: OK (chip 0x{chip_id:02X})")
            else:
                print(f"  BMI160: unexpected chip 0x{chip_id:02X}")
        except OSError as e:
            print(f"  BMI160: not found ({e})")

    def read_rms(self):
        if not self.ok:
            return 1.0
        try:
            data = self.i2c.readfrom_mem(BMI160_ADDR, 0x12, 6)
            ax = (data[1] << 8 | data[0])
            ay = (data[3] << 8 | data[2])
            az = (data[5] << 8 | data[4])
            if ax > 32767: ax -= 65536
            if ay > 32767: ay -= 65536
            if az > 32767: az -= 65536
            s = 4.0 / 32768.0
            return math.sqrt((ax*s)**2 + (ay*s)**2 + (az*s)**2)
        except:
            return 1.0


# ============ PCA9685 MINIMAL DRIVER ============
class PWMDriver:
    def __init__(self, i2c):
        self.i2c = i2c
        self.ok = False
        try:
            i2c.writeto_mem(PCA9685_ADDR, 0x00, bytes([0x00]))  # reset
            time.sleep_ms(10)
            # Set 50Hz PWM frequency (prescale = 121)
            i2c.writeto_mem(PCA9685_ADDR, 0x00, bytes([0x10]))  # sleep
            time.sleep_ms(5)
            i2c.writeto_mem(PCA9685_ADDR, 0xFE, bytes([121]))   # prescale
            i2c.writeto_mem(PCA9685_ADDR, 0x00, bytes([0x00]))  # wake
            time.sleep_ms(5)
            self.ok = True
            print("  PCA9685: OK (50Hz)")
        except OSError as e:
            print(f"  PCA9685: not found ({e})")

    def set_pwm(self, ch, on, off):
        if not self.ok:
            return
        reg = 0x06 + 4 * ch
        self.i2c.writeto_mem(PCA9685_ADDR, reg, bytes([
            on & 0xFF, (on >> 8) & 0xFF,
            off & 0xFF, (off >> 8) & 0xFF
        ]))

    def set_duty(self, ch, duty_pct):
        """Set channel duty cycle 0-100%."""
        val = int(duty_pct * 4095 / 100)
        self.set_pwm(ch, 0, max(1, min(val, 4095)))

    def servo_angle(self, ch, angle):
        """Set servo angle 0-180 degrees."""
        # 50Hz: 1ms=205, 2ms=410, range 205 counts for 180 degrees
        pulse = int(205 + (angle / 180) * 205)
        self.set_pwm(ch, 0, pulse)

    def off(self, ch):
        self.set_pwm(ch, 0, 0)

    def all_off(self):
        for ch in range(4):
            self.off(ch)


# ============ SIMULATED ADC VALUES ============
def get_sim_power():
    """Return simulated power values based on motor state."""
    bus_v = 5.02
    m1_ma = 0
    m2_ma = 0
    if motor1_on:
        m1_ma = 380 + int(time.ticks_ms() % 40) - 20  # 360-400mA with noise
    if motor2_on:
        m2_ma = 280 + int(time.ticks_ms() % 30) - 15  # 265-295mA with noise
    if fault_active:
        bus_v = 4.35  # voltage dip during fault
        m1_ma = 0
        m2_ma = 0
    total_mw = int(bus_v * (m1_ma + m2_ma))
    efficiency = 82 if (motor1_on or motor2_on) else 0
    return bus_v, m1_ma, m2_ma, total_mw, efficiency


# ============ PACKET BUILDERS ============
def build_packet(pkt_type, payload_dict):
    global seq
    seq = (seq + 1) % 256

    buf = bytearray(32)
    buf[0] = pkt_type
    buf[1] = seq

    if pkt_type == PKT_POWER:
        bus_v, m1, m2, total, eff = get_sim_power()
        struct.pack_into('<HHHH', buf, 2,
                         int(bus_v * 100), int(m1), int(m2), total)
        buf[10] = eff
        buf[11] = state

    elif pkt_type == PKT_STATUS:
        buf[2] = state
        buf[3] = 1 if fault_active else 0  # fault source
        struct.pack_into('<H', buf, 4, int(imu_rms * 100))
        buf[6] = 1 if motor1_on else 0  # mode
        struct.pack_into('<I', buf, 8, time.ticks_ms() - start_time)

    elif pkt_type == PKT_PRODUCTION:
        struct.pack_into('<HHH', buf, 2,
                         items_produced, items_passed, items_rejected)
        buf[8] = cycle_count % 256

    elif pkt_type == PKT_HEARTBEAT:
        struct.pack_into('<I', buf, 2, time.ticks_ms())
        buf[6] = seq  # CPU load proxy

    elif pkt_type == PKT_ALERT:
        buf[2] = 1  # fault code: vibration
        buf[3] = 2  # severity: FAULT
        struct.pack_into('<H', buf, 4, int(imu_rms * 100))
        buf[6] = state

    return bytes(buf)


# ============ DEMO SEQUENCE ============
def run_demo():
    global state, motor1_on, motor2_on, fault_active
    global items_produced, items_passed, items_rejected, cycle_count
    global imu_rms, start_time

    print()
    print("=" * 50)
    print("  GridBox Demo — Pico A (Master)")
    print("=" * 50)
    print()

    # Init hardware
    led = Pin(LED_PIN, Pin.OUT)
    recycle = Pin(RECYCLE_PIN, Pin.OUT)
    led.on()

    print("[INIT] Hardware...")
    nrf = NRF()

    i2c = I2C(0, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=400_000)
    devices = i2c.scan()
    print(f"  I2C devices: {['0x{:02X}'.format(d) for d in devices]}")

    imu = IMU(i2c)
    pwm = PWMDriver(i2c)

    start_time = time.ticks_ms()
    print()
    print("[DEMO] Starting sequence...")
    print()

    # === STAGE 1: BOOT (3s) ===
    state = STATE_BOOT
    print(f"[{STATE_NAMES[state]}] Booting — self test...")
    for i in range(6):
        led.toggle()
        pkt = build_packet(PKT_STATUS, {})
        nrf.send(pkt)
        time.sleep_ms(500)
    led.on()

    # === STAGE 2: READY (2s) ===
    state = STATE_READY
    print(f"[{STATE_NAMES[state]}] System ready — waiting...")
    for i in range(4):
        pkt = build_packet(PKT_POWER, {})
        nrf.send(pkt)
        time.sleep_ms(500)

    # === STAGE 3: MOTOR 1 ON (5s) ===
    state = STATE_RUNNING
    motor1_on = True
    pwm.set_duty(MOTOR1_CH, 65)  # 65% speed
    print(f"[{STATE_NAMES[state]}] Motor 1 ON (pump) — 65% PWM")

    # Open valve servo
    pwm.servo_angle(SERVO_VALVE, 90)
    print(f"[{STATE_NAMES[state]}] Valve OPEN (servo 90°)")

    for i in range(10):
        imu_rms = imu.read_rms()
        pkt_type = [PKT_POWER, PKT_STATUS][i % 2]
        pkt = build_packet(pkt_type, {})
        nrf.send(pkt)
        bus_v, m1, m2, total, eff = get_sim_power()
        print(f"  [{i+1}/10] M1={m1}mA Bus={bus_v}V IMU={imu_rms:.2f}g")
        time.sleep_ms(500)

    # === STAGE 4: MOTOR 2 ON (5s) ===
    motor2_on = True
    pwm.set_duty(MOTOR2_CH, 45)  # 45% speed
    print(f"[{STATE_NAMES[state]}] Motor 2 ON (conveyor) — 45% PWM")

    for i in range(10):
        imu_rms = imu.read_rms()
        # Simulate production
        if i % 3 == 0:
            items_produced += 1
            items_passed += 1
            cycle_count += 1

        pkt_type = [PKT_POWER, PKT_STATUS, PKT_PRODUCTION, PKT_POWER][i % 4]
        pkt = build_packet(pkt_type, {})
        nrf.send(pkt)
        bus_v, m1, m2, total, eff = get_sim_power()
        print(f"  [{i+1}/10] M1={m1}mA M2={m2}mA Total={total}mW Items={items_produced}")
        time.sleep_ms(500)

    # Close valve
    pwm.servo_angle(SERVO_VALVE, 0)
    print(f"[{STATE_NAMES[state]}] Valve CLOSED")

    # Sort gate
    pwm.servo_angle(SERVO_GATE, 45)
    time.sleep_ms(300)
    pwm.servo_angle(SERVO_GATE, 135)
    time.sleep_ms(300)
    pwm.servo_angle(SERVO_GATE, 90)
    print(f"[{STATE_NAMES[state]}] Sort gate demo — PASS/REJECT/CENTRE")

    # Send production update
    pkt = build_packet(PKT_PRODUCTION, {})
    nrf.send(pkt)

    # === STAGE 5: FAULT INJECTION (5s) ===
    print()
    print(f">>> SHAKE THE BOARD NOW! Waiting for vibration... <<<")
    print()

    fault_detected = False
    for i in range(50):  # wait up to 5 seconds for shake
        imu_rms = imu.read_rms()
        pkt = build_packet(PKT_STATUS, {})
        nrf.send(pkt)

        if imu_rms > 2.0 and not fault_detected:
            fault_detected = True
            fault_active = True
            state = STATE_FAULT
            print(f"[{STATE_NAMES[state]}] FAULT DETECTED! RMS={imu_rms:.2f}g")

            # Stop motors
            motor1_on = False
            motor2_on = False
            pwm.all_off()
            print(f"[{STATE_NAMES[state]}] Motors STOPPED — emergency")

            # Send alert
            pkt = build_packet(PKT_ALERT, {})
            nrf.send(pkt)

            # Blink LED fast
            for _ in range(6):
                led.toggle()
                time.sleep_ms(150)
            led.on()
            break

        if i % 5 == 0:
            print(f"  Waiting... IMU={imu_rms:.2f}g (shake > 2.0g to trigger)")
        time.sleep_ms(100)

    if not fault_detected:
        # Auto-trigger fault if no shake
        fault_active = True
        state = STATE_FAULT
        imu_rms = 3.5  # simulated
        print(f"[{STATE_NAMES[state]}] FAULT auto-triggered (no shake detected)")
        motor1_on = False
        motor2_on = False
        pwm.all_off()
        pkt = build_packet(PKT_ALERT, {})
        nrf.send(pkt)
        for _ in range(6):
            led.toggle()
            time.sleep_ms(150)
        led.on()

    time.sleep(2)

    # === STAGE 6: RECOVERY (3s) ===
    state = STATE_RECOVERY
    fault_active = False
    imu_rms = 0.8
    print(f"[{STATE_NAMES[state]}] Recovering — vibration subsided")

    # Restart motors in priority order
    time.sleep(1)
    motor1_on = True
    pwm.set_duty(MOTOR1_CH, 65)
    print(f"[{STATE_NAMES[state]}] Motor 1 RESTORED (priority 1)")
    pkt = build_packet(PKT_STATUS, {})
    nrf.send(pkt)

    time.sleep(1)
    motor2_on = True
    pwm.set_duty(MOTOR2_CH, 45)
    print(f"[{STATE_NAMES[state]}] Motor 2 RESTORED (priority 2)")
    pkt = build_packet(PKT_POWER, {})
    nrf.send(pkt)

    time.sleep(1)

    # === STAGE 7: ENERGY RECYCLE (4s) ===
    state = STATE_RECYCLE
    print(f"[{STATE_NAMES[state]}] Energy recycling demo...")

    for i in range(3):
        recycle.high()
        print(f"  [{i+1}] Charging capacitor...")
        pkt = build_packet(PKT_STATUS, {})
        nrf.send(pkt)
        time.sleep_ms(800)

        recycle.low()
        print(f"  [{i+1}] Released — LED fading (recycled energy)")
        pkt = build_packet(PKT_POWER, {})
        nrf.send(pkt)
        time.sleep_ms(1200)

    # === STAGE 8: SHUTDOWN (2s) ===
    state = STATE_DONE
    motor1_on = False
    motor2_on = False
    pwm.all_off()
    recycle.low()
    print()
    print(f"[{STATE_NAMES[state]}] Demo complete!")
    print(f"  Items produced: {items_produced}")
    print(f"  Passed: {items_passed}")
    print(f"  Rejected: {items_rejected}")
    print(f"  Cycles: {cycle_count}")
    elapsed = (time.ticks_ms() - start_time) // 1000
    print(f"  Duration: {elapsed}s")

    # Send final heartbeat
    pkt = build_packet(PKT_HEARTBEAT, {})
    nrf.send(pkt)

    # Heartbeat LED — slow blink = done
    while True:
        led.toggle()
        time.sleep(1)


# ============ MAIN ============
if __name__ == '__main__':
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\nDemo interrupted")
        Pin(LED_PIN, Pin.OUT).off()
    except Exception as e:
        print(f"\nDEMO ERROR: {e}")
        # Error blink
        led = Pin(LED_PIN, Pin.OUT)
        for _ in range(20):
            led.toggle()
            time.sleep_ms(100)
