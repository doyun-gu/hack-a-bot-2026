/**
 * GridBox — SSD1306 OLED Driver (C SDK)
 * I2C driver for 128x64 SSD1306 OLED display with framebuffer.
 * Ported from MicroPython ssd1306.py.
 */

#ifndef SSD1306_H
#define SSD1306_H

#include "hardware/i2c.h"
#include <stdbool.h>
#include <stdint.h>

/* Display dimensions */
#define SSD1306_WIDTH  128
#define SSD1306_HEIGHT 64
#define SSD1306_PAGES  (SSD1306_HEIGHT / 8)
#define SSD1306_BUF_SIZE (SSD1306_WIDTH * SSD1306_PAGES)

/* SSD1306 commands */
#define SSD1306_SET_CONTRAST       0x81
#define SSD1306_ENTIRE_DISPLAY_ON  0xA4
#define SSD1306_SET_NORM_INV       0xA6
#define SSD1306_DISPLAY_OFF        0xAE
#define SSD1306_DISPLAY_ON         0xAF
#define SSD1306_SET_MEM_ADDR_MODE  0x20
#define SSD1306_SET_COL_ADDR       0x21
#define SSD1306_SET_PAGE_ADDR      0x22
#define SSD1306_SET_START_LINE     0x40
#define SSD1306_SET_SEG_REMAP      0xA0
#define SSD1306_SET_MUX_RATIO      0xA8
#define SSD1306_SET_COM_OUT_DIR    0xC0
#define SSD1306_SET_DISPLAY_OFFSET 0xD3
#define SSD1306_SET_COM_PIN_CFG    0xDA
#define SSD1306_SET_CLK_DIV        0xD5
#define SSD1306_SET_PRECHARGE      0xD9
#define SSD1306_SET_VCOM_DESEL     0xDB
#define SSD1306_SET_CHARGE_PUMP    0x8D

/* Device handle */
typedef struct {
    i2c_inst_t *i2c;
    uint8_t addr;
    uint8_t width;
    uint8_t height;
    uint8_t buffer[SSD1306_BUF_SIZE];
} ssd1306_t;

/** Initialise SSD1306 display. */
bool ssd1306_init(ssd1306_t *dev, i2c_inst_t *i2c, uint8_t addr);

/** Push framebuffer to display. */
void ssd1306_show(ssd1306_t *dev);

/** Fill entire screen (0=black, 1=white). */
void ssd1306_fill(ssd1306_t *dev, uint8_t color);

/** Clear screen and update. */
void ssd1306_clear(ssd1306_t *dev);

/** Set a single pixel. */
void ssd1306_pixel(ssd1306_t *dev, int16_t x, int16_t y, uint8_t color);

/** Draw text at position using built-in 5x7 font. */
void ssd1306_text(ssd1306_t *dev, const char *str, int16_t x, int16_t y, uint8_t color);

/** Draw horizontal line. */
void ssd1306_hline(ssd1306_t *dev, int16_t x, int16_t y, int16_t w, uint8_t color);

/** Draw vertical line. */
void ssd1306_vline(ssd1306_t *dev, int16_t x, int16_t y, int16_t h, uint8_t color);

/** Draw rectangle outline. */
void ssd1306_rect(ssd1306_t *dev, int16_t x, int16_t y, int16_t w, int16_t h, uint8_t color);

/** Draw filled rectangle. */
void ssd1306_fill_rect(ssd1306_t *dev, int16_t x, int16_t y, int16_t w, int16_t h, uint8_t color);

/** Set display contrast (0-255). */
void ssd1306_contrast(ssd1306_t *dev, uint8_t value);

/** Invert display. */
void ssd1306_invert(ssd1306_t *dev, bool on);

#endif /* SSD1306_H */
