"""
GridBox — Master Pico (Pico A) Configuration
Pin assignments and constants for the Grid Controller.
Change these when wiring changes — all other files import from here.
"""

# ============ I2C BUS (BMI160 + PCA9685) ============
I2C_ID = 0
I2C_SDA = 4
I2C_SCL = 5
I2C_FREQ = 400_000

# I2C addresses
BMI160_ADDR = 0x68       # IMU (0x69 if SDO high)
PCA9685_ADDR = 0x40      # PWM servo/motor driver

# ============ SPI BUS (nRF24L01+) ============
SPI_ID = 0
SPI_SCK = 2
SPI_MOSI = 3
SPI_MISO = 16            # GP16
SPI_BAUD = 10_000_000
NRF_CE = 0               # GP0
NRF_CSN = 1              # GP1

# nRF24L01+ settings
NRF_CHANNEL = 100        # 2.4GHz + 100 = 2.500GHz
NRF_PAYLOAD_SIZE = 32    # bytes per packet
NRF_DATA_RATE = 250      # kbps (250, 1000, or 2000)
NRF_TX_ADDR = b'NSYNT'   # 5-byte TX address
NRF_RX_ADDR = b'NSYNR'   # 5-byte RX address

# ============ MOSFET SWITCHES ============
# Motor MOSFETs now driven by PCA9685 PWM (CH2, CH3) — not GPIO
# GP10, GP11, GP12 are FREE (no longer used for MOSFET gates)
MOSFET_RECYCLE = 13      # GP13 → Recycle path (binary on/off, no PWM needed)

# ============ STATUS LEDs ============
LED_RED = 14             # GP14
LED_GREEN = 15           # GP15
LED_ONBOARD = 25         # Pico onboard LED

# ============ ADC (Power Sensing) ============
ADC_BUS_VOLTAGE = 26     # GP26 — bus voltage via 10kΩ+10kΩ divider
ADC_MOTOR1_CURRENT = 27  # GP27 — Motor 1 current via 1Ω sense R
ADC_MOTOR2_CURRENT = 28  # GP28 — Motor 2 current via 1Ω sense R

# ADC conversion constants
ADC_VREF = 3.3           # Pico ADC reference voltage
ADC_RESOLUTION = 65535   # 16-bit ADC
VOLTAGE_DIVIDER_RATIO = 2.0   # 10kΩ+10kΩ divider → multiply by 2
CURRENT_SENSE_R = 1.0    # 1Ω sense resistor

# ============ PCA9685 SERVO/MOTOR CHANNELS ============
SERVO_VALVE_CH = 0       # PCA9685 channel for valve servo
SERVO_GATE_CH = 1        # PCA9685 channel for sorting gate servo
MOTOR1_PWM_CH = 2        # PCA9685 channel for Motor 1 speed
MOTOR2_PWM_CH = 3        # PCA9685 channel for Motor 2 speed
SERVO_MIN_US = 500       # min pulse width microseconds
SERVO_MAX_US = 2500      # max pulse width microseconds
SERVO_CENTRE_US = 1500   # centre position

# ============ IMU SETTINGS ============
IMU_SAMPLE_RATE = 100    # Hz
IMU_ACCEL_RANGE = 4      # ±4g
IMU_GYRO_RANGE = 500     # ±500°/s
IMU_WINDOW_SIZE = 100    # rolling window for RMS
IMU_HEALTHY_THRESHOLD = 1.0   # g — below = healthy
IMU_WARNING_THRESHOLD = 2.0   # g — above = warning
IMU_FAULT_DURATION_MS = 3000  # sustained vibration = fault

# ============ POWER THRESHOLDS ============
BUS_VOLTAGE_NOMINAL = 5.0     # V — expected bus voltage
BUS_VOLTAGE_LOW = 4.2         # V — low voltage warning
BUS_VOLTAGE_CRITICAL = 3.8    # V — critical, shed loads
MOTOR_CURRENT_MAX_MA = 800    # mA — stall/jam threshold
ADC_SAMPLES_AVG = 10          # average N samples per reading

# ============ FACTORY / SORTING ============
BELT_LENGTH_CM = 20            # conveyor belt length
BELT_SPEED_CM_PER_S = 5        # belt speed at nominal PWM
WEIGHT_THRESHOLD_MIN = 0.03    # minimum current delta for "item detected"
WEIGHT_THRESHOLD_LIGHT = 0.05  # below = reject light
WEIGHT_THRESHOLD_HEAVY = 0.15  # above = reject heavy
WEIGHT_THRESHOLD_JAM = 0.30    # above = jam fault

# ============ LOAD PRIORITIES (for shedding) ============
# P1=highest priority (keep), P3=lowest (shed first)
# LED bank removed — replaced by MAX7219 display on Pico B
LOAD_PRIORITY = {
    'motor1': 1,    # fan — critical cooling
    'motor2': 2,    # conveyor — important
    'recycle': 3,   # recycle path — shed first
}

# ============ ENERGY SIGNATURE ============
ES_SAMPLE_RATE_HZ = 500       # ADC sampling rate for signatures
ES_WINDOW_SIZE = 500           # 1 second of data
ES_LEARNING_DURATION_S = 30    # baseline learning duration
ES_ANOMALY_THRESHOLD = 0.5    # divergence score above = anomaly
ES_WEIGHT_MEAN = 0.30
ES_WEIGHT_STD = 0.25
ES_WEIGHT_CROSSING = 0.25
ES_WEIGHT_MAXDEV = 0.20

# ============ TIMING ============
MAIN_LOOP_MS = 10              # 100Hz main loop
WIRELESS_SEND_MS = 50          # send telemetry every 50ms
HEARTBEAT_MS = 1000            # send heartbeat every 1s
SERIAL_PRINT_MS = 200          # print JSON for web dashboard

# ============ CALIBRATION ============
CALIBRATION_FILE = 'calibration.json'
CALIBRATION_SAMPLES = 100      # readings per calibration step
