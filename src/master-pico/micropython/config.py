"""
Pin assignments and constants for Master Pico.
Change these when wiring changes — all other files import from here.
"""

# ============ I2C BUS ============
I2C_ID = 0
I2C_SDA = 4
I2C_SCL = 5
I2C_FREQ = 400_000

# Known I2C addresses
BMI160_ADDR = 0x68    # or 0x69 if SDO is high
PCA9685_ADDR = 0x40   # default
SSD1306_ADDR = 0x3C   # if OLED is on master

# ============ SPI BUS (nRF24L01+) ============
SPI_ID = 0
SPI_SCK = 2
SPI_MOSI = 3
SPI_MISO = 4
SPI_BAUD = 10_000_000
NRF_CSN = 1
NRF_CE = 0

# nRF24L01+ settings
NRF_CHANNEL = 100         # 2.4GHz + 100 = 2.500GHz
NRF_PAYLOAD_SIZE = 32     # bytes per packet
NRF_DATA_RATE = 250       # kbps (250, 1000, or 2000)
NRF_TX_ADDR = b'NSYNT'    # 5-byte TX address
NRF_RX_ADDR = b'NSYNR'    # 5-byte RX address

# ============ ADC (JOYSTICK) ============
JOY_X_PIN = 26
JOY_Y_PIN = 27
JOY_BTN_PIN = 22
JOY_CENTRE = 32768       # midpoint of 16-bit ADC
JOY_DEADZONE = 3000      # ignore values within this range of centre

# ============ GPIO (LEDs) ============
LED_GREEN = 15
LED_RED = 14
LED_ONBOARD = 25         # Pico onboard LED

# ============ SERVO CHANNELS (PCA9685) ============
SERVO_ROLL_CH = 0         # PCA9685 channel for roll servo
SERVO_PITCH_CH = 1        # PCA9685 channel for pitch servo
SERVO_POINTER_CH = 2      # PCA9685 channel for pointer arm (if used)
SERVO_MIN_US = 500        # min pulse width microseconds
SERVO_MAX_US = 2500       # max pulse width microseconds
SERVO_CENTRE_US = 1500    # centre position

# ============ IMU SETTINGS ============
IMU_SAMPLE_RATE = 100     # Hz
IMU_FILTER_ALPHA = 0.98   # complementary filter coefficient

# ============ TIMING ============
MAIN_LOOP_MS = 10         # 100Hz main loop
WIRELESS_SEND_MS = 10     # send data every 10ms
DISPLAY_UPDATE_MS = 100   # update OLED every 100ms
HEARTBEAT_MS = 1000       # send heartbeat every 1s
