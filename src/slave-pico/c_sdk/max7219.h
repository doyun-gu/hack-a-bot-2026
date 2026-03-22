/**
 * MAX7219 7-Segment Display Driver (C SDK)
 * SPI1: CLK=GP10, DIN=GP11, CS=GP13
 */

#ifndef MAX7219_H
#define MAX7219_H

#include "hardware/spi.h"
#include <stdbool.h>
#include <stdint.h>

typedef struct {
    spi_inst_t *spi;
    uint cs_pin;
} max7219_t;

bool max7219_init(max7219_t *dev, spi_inst_t *spi, uint cs_pin);
void max7219_brightness(max7219_t *dev, uint8_t level);
void max7219_clear(max7219_t *dev);
void max7219_show(max7219_t *dev, const char *text);
void max7219_show_left(max7219_t *dev, const char *text);
void max7219_flash(max7219_t *dev, const char *text, int times, int on_ms, int off_ms);

#endif /* MAX7219_H */
