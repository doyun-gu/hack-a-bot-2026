/**
 * GridBox — Slave Pico (Pico B) Configuration (C SDK)
 * Pin assignments for SCADA station.
 * Ported from MicroPython config.py.
 */

#ifndef CONFIG_H
#define CONFIG_H

/* ============ I2C BUS (OLED) ============ */
#define I2C_PORT       i2c0
#define I2C_SDA        4
#define I2C_SCL        5
#define I2C_FREQ       400000
#define SSD1306_ADDR   0x3C

/* ============ SPI BUS (nRF24L01+) ============ */
#define SPI_PORT       spi0
#define SPI_SCK        2
#define SPI_MOSI       3
#define SPI_MISO       16
#define SPI_BAUD       10000000
#define NRF_CE         0
#define NRF_CSN        1

/* nRF24L01+ settings (reversed from master) */
#define NRF_CHANNEL         100
#define NRF_PAYLOAD_SIZE    32
#define NRF_DATA_RATE       250
#define NRF_TX_ADDR_STR     "NSYNR"   /* slave TX = master RX */
#define NRF_RX_ADDR_STR     "NSYNT"   /* slave RX = master TX */

/* ============ ADC (Joystick + Potentiometer) ============ */
#define JOY_X_PIN      26       /* GP26 — Joystick X axis */
#define JOY_Y_PIN      27       /* GP27 — Joystick Y axis */
#define JOY_BTN_PIN    22       /* GP22 — Joystick button */
#define POT_PIN        28       /* GP28 — Potentiometer */

#define JOY_CENTRE     2048     /* midpoint of 12-bit ADC */
#define JOY_DEADZONE   200      /* ignore within this range */

/* ============ STATUS LEDs ============ */
#define LED_RED        14
#define LED_GREEN      15
#define LED_ONBOARD    25

/* ============ OLED SETTINGS ============ */
#define OLED_WIDTH     128
#define OLED_HEIGHT    64

/* ============ TIMING ============ */
#define MAIN_LOOP_MS         10       /* 100Hz */
#define DISPLAY_UPDATE_MS    100      /* OLED refresh */
#define HEARTBEAT_TIMEOUT_MS 3000     /* alert if no packet */
#define COMMAND_SEND_MS      50       /* send commands every 50ms */

/* ============ OPERATOR INPUT ============ */
#define DEBOUNCE_MS          50
#define LONG_PRESS_MS        3000

#endif /* CONFIG_H */
