/**
 * MAX7219 7-Segment Display Driver (C SDK)
 * SPI1: CLK=GP10, DIN=GP11, CS=GP13
 */

#include "max7219.h"
#include "hardware/gpio.h"
#include "pico/stdlib.h"
#include <string.h>

/* MAX7219 registers */
#define REG_NOOP        0x00
#define REG_DIGIT0      0x01
#define REG_DECODE      0x09
#define REG_INTENSITY   0x0A
#define REG_SCAN_LIMIT  0x0B
#define REG_SHUTDOWN    0x0C
#define REG_TEST        0x0F

/*
 * Segment encoding: dp g f e d c b a
 *
 *    --a--
 *   |     |
 *   f     b
 *   |     |
 *    --g--
 *   |     |
 *   e     c
 *   |     |
 *    --d--   .dp
 */
static const uint8_t char_map[128] = {
    ['0'] = 0x7E, ['1'] = 0x30, ['2'] = 0x6D, ['3'] = 0x79, ['4'] = 0x33,
    ['5'] = 0x5B, ['6'] = 0x5F, ['7'] = 0x70, ['8'] = 0x7F, ['9'] = 0x7B,
    ['A'] = 0x77, ['b'] = 0x1F, ['C'] = 0x4E, ['d'] = 0x3D, ['E'] = 0x4F,
    ['F'] = 0x47, ['H'] = 0x37, ['L'] = 0x0E, ['n'] = 0x15, ['o'] = 0x1D,
    ['P'] = 0x67, ['r'] = 0x05, ['t'] = 0x0F, ['U'] = 0x3E, ['S'] = 0x5B,
    ['-'] = 0x01, ['_'] = 0x08, [' '] = 0x00,
    ['i'] = 0x10, ['c'] = 0x0D, ['J'] = 0x38, ['G'] = 0x5E, ['y'] = 0x3B,
};

static void write_reg(max7219_t *dev, uint8_t addr, uint8_t data) {
    uint8_t buf[2] = {addr, data};
    gpio_put(dev->cs_pin, 0);
    spi_write_blocking(dev->spi, buf, 2);
    gpio_put(dev->cs_pin, 1);
}

bool max7219_init(max7219_t *dev, spi_inst_t *spi, uint cs_pin) {
    dev->spi = spi;
    dev->cs_pin = cs_pin;

    /* Init CS pin */
    gpio_init(cs_pin);
    gpio_set_dir(cs_pin, GPIO_OUT);
    gpio_put(cs_pin, 1);

    /* Init SPI1 */
    spi_init(spi, 10000000);
    gpio_set_function(10, GPIO_FUNC_SPI);  /* SCK */
    gpio_set_function(11, GPIO_FUNC_SPI);  /* MOSI */

    /* Configure MAX7219 */
    write_reg(dev, REG_TEST, 0x00);       /* display test off */
    write_reg(dev, REG_SHUTDOWN, 0x01);   /* normal operation */
    write_reg(dev, REG_SCAN_LIMIT, 0x07); /* all 8 digits */
    write_reg(dev, REG_DECODE, 0x00);     /* raw segment mode */
    write_reg(dev, REG_INTENSITY, 0x08);  /* medium brightness */

    max7219_clear(dev);
    return true;
}

void max7219_brightness(max7219_t *dev, uint8_t level) {
    write_reg(dev, REG_INTENSITY, level & 0x0F);
}

void max7219_clear(max7219_t *dev) {
    for (int d = 1; d <= 8; d++) {
        write_reg(dev, d, 0x00);
    }
}

void max7219_show(max7219_t *dev, const char *text) {
    int len = strlen(text);
    if (len > 8) len = 8;

    /* Right-aligned: pad with spaces on left */
    int pad = 8 - len;

    for (int i = 0; i < 8; i++) {
        uint8_t seg = 0x00;
        if (i >= pad) {
            char ch = text[i - pad];
            if (ch >= 0 && ch < 128) {
                seg = char_map[(unsigned char)ch];
            }
        }
        /* Digit 8 = leftmost, digit 1 = rightmost */
        write_reg(dev, 8 - i, seg);
    }
}

void max7219_show_left(max7219_t *dev, const char *text) {
    int len = strlen(text);
    if (len > 8) len = 8;

    for (int i = 0; i < 8; i++) {
        uint8_t seg = 0x00;
        if (i < len) {
            char ch = text[i];
            if (ch >= 0 && ch < 128) {
                seg = char_map[(unsigned char)ch];
            }
        }
        write_reg(dev, 8 - i, seg);
    }
}

void max7219_flash(max7219_t *dev, const char *text, int times, int on_ms, int off_ms) {
    for (int i = 0; i < times; i++) {
        max7219_show(dev, text);
        sleep_ms(on_ms);
        max7219_clear(dev);
        sleep_ms(off_ms);
    }
    max7219_show(dev, text);
}
