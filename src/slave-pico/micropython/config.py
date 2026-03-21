"""
GridBox — Slave Pico (Pico B) Configuration
Pin assignments and constants for the SCADA Station.
Change these when wiring changes — all other files import from here.
"""

# ============ I2C BUS (OLED) ============
I2C_ID = 0
I2C_SDA = 4
I2C_SCL = 5
I2C_FREQ = 400_000

# I2C addresses
SSD1306_ADDR = 0x3C      # OLED display

# ============ SPI BUS (nRF24L01+) ============
SPI_ID = 0
SPI_SCK = 2
SPI_MOSI = 3
SPI_MISO = 16            # GP16
SPI_BAUD = 10_000_000
NRF_CE = 0               # GP0
NRF_CSN = 1              # GP1

# nRF24L01+ settings (must match master)
NRF_CHANNEL = 100
NRF_PAYLOAD_SIZE = 32
NRF_DATA_RATE = 250
NRF_TX_ADDR = b'NSYNR'   # reversed — slave TX = master RX
NRF_RX_ADDR = b'NSYNT'   # reversed — slave RX = master TX

# ============ ADC (JOYSTICK + POTENTIOMETER) ============
JOY_X_PIN = 26           # GP26 — Joystick X axis
JOY_Y_PIN = 27           # GP27 — Joystick Y axis
JOY_BTN_PIN = 22         # GP22 — Joystick button (pull-up)
POT_PIN = 28             # GP28 — Potentiometer

JOY_CENTRE = 32768       # midpoint of 16-bit ADC
JOY_DEADZONE = 3000      # ignore values within this range of centre

# ============ STATUS LEDs ============
LED_RED = 14             # GP14
LED_GREEN = 15           # GP15
LED_ONBOARD = 25         # Pico onboard LED

# ============ OLED SETTINGS ============
OLED_WIDTH = 128
OLED_HEIGHT = 64

# ============ OPERATOR INPUT ============
DEBOUNCE_MS = 50         # button debounce time
LONG_PRESS_MS = 3000     # long press for mode change
POT_MIN_THRESHOLD = 20   # potentiometer mapped range min (grams)
POT_MAX_THRESHOLD = 200  # potentiometer mapped range max (grams)

# ============ TIMING ============
MAIN_LOOP_MS = 10              # 100Hz main loop
DISPLAY_UPDATE_MS = 100        # update OLED every 100ms
HEARTBEAT_TIMEOUT_MS = 3000    # alert if no packet for 3s
COMMAND_SEND_MS = 50           # send commands every 50ms

# ============ DASHBOARD ============
NUM_VIEWS = 6                  # total dashboard views
VIEW_STATUS = 0
VIEW_POWER = 1
VIEW_FAULTS = 2
VIEW_PRODUCTION = 3
VIEW_MANUAL = 4
VIEW_COMPARISON = 5
