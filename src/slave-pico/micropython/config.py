"""
Pin assignments and constants for Slave Pico (Base Station).
Change these when wiring changes — all other files import from here.
"""

# ============ I2C BUS ============
I2C_ID = 0
I2C_SDA = 4
I2C_SCL = 5
I2C_FREQ = 400_000

# Known I2C addresses
SSD1306_ADDR = 0x3C

# ============ SPI BUS (nRF24L01+) ============
SPI_ID = 0
SPI_SCK = 2
SPI_MOSI = 3
SPI_MISO = 4
SPI_BAUD = 10_000_000
NRF_CSN = 1
NRF_CE = 0

# nRF24L01+ settings (must match master)
NRF_CHANNEL = 100
NRF_PAYLOAD_SIZE = 32
NRF_DATA_RATE = 250
NRF_TX_ADDR = b'NSYNR'   # reversed — slave TX = master RX
NRF_RX_ADDR = b'NSYNT'   # reversed — slave RX = master TX

# ============ ADC (JOYSTICK) ============
JOY_X_PIN = 26
JOY_Y_PIN = 27
JOY_BTN_PIN = 22
JOY_CENTRE = 32768
JOY_DEADZONE = 3000

# ============ GPIO (LEDs) ============
LED_GREEN = 15
LED_RED = 14
LED_ONBOARD = 25

# ============ OLED SETTINGS ============
OLED_WIDTH = 128
OLED_HEIGHT = 64

# ============ TIMING ============
MAIN_LOOP_MS = 10
DISPLAY_UPDATE_MS = 100
HEARTBEAT_TIMEOUT_MS = 3000  # alert if no heartbeat for 3s
