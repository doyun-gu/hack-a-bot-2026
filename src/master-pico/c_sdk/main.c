/**
 * NeuroSync — Master Pico (C/C++ SDK version)
 * Production firmware for demo day.
 *
 * This is the C port of the MicroPython master.
 * Will be populated once MicroPython version is tested and working.
 */

#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include "hardware/spi.h"
#include "hardware/adc.h"
#include "hardware/pwm.h"
#include "pico/multicore.h"

// Pin definitions (must match config.py)
#define I2C_SDA_PIN 4
#define I2C_SCL_PIN 5
#define SPI_SCK_PIN 2
#define SPI_MOSI_PIN 3
#define SPI_MISO_PIN 4
#define NRF_CSN_PIN 1
#define NRF_CE_PIN 0
#define JOY_X_PIN 26
#define JOY_Y_PIN 27
#define JOY_BTN_PIN 22
#define LED_GREEN_PIN 15
#define LED_RED_PIN 14

void init_hardware(void) {
    stdio_init_all();

    printf("================================\n");
    printf("  NeuroSync Master (C SDK)\n");
    printf("  Initialising hardware...\n");
    printf("================================\n");

    // I2C
    i2c_init(i2c0, 400000);
    gpio_set_function(I2C_SDA_PIN, GPIO_FUNC_I2C);
    gpio_set_function(I2C_SCL_PIN, GPIO_FUNC_I2C);
    gpio_pull_up(I2C_SDA_PIN);
    gpio_pull_up(I2C_SCL_PIN);

    // SPI
    spi_init(spi0, 10000000);
    gpio_set_function(SPI_SCK_PIN, GPIO_FUNC_SPI);
    gpio_set_function(SPI_MOSI_PIN, GPIO_FUNC_SPI);
    gpio_set_function(SPI_MISO_PIN, GPIO_FUNC_SPI);

    // nRF control pins
    gpio_init(NRF_CSN_PIN);
    gpio_set_dir(NRF_CSN_PIN, GPIO_OUT);
    gpio_put(NRF_CSN_PIN, 1);
    gpio_init(NRF_CE_PIN);
    gpio_set_dir(NRF_CE_PIN, GPIO_OUT);
    gpio_put(NRF_CE_PIN, 0);

    // ADC (joystick)
    adc_init();
    adc_gpio_init(JOY_X_PIN);
    adc_gpio_init(JOY_Y_PIN);

    // Joystick button
    gpio_init(JOY_BTN_PIN);
    gpio_set_dir(JOY_BTN_PIN, GPIO_IN);
    gpio_pull_up(JOY_BTN_PIN);

    // LEDs
    gpio_init(LED_GREEN_PIN);
    gpio_set_dir(LED_GREEN_PIN, GPIO_OUT);
    gpio_init(LED_RED_PIN);
    gpio_set_dir(LED_RED_PIN, GPIO_OUT);

    printf("[MASTER] Hardware initialised OK\n");
}

// Core 1: fall detection (runs independently)
void core1_entry(void) {
    while (true) {
        // TODO: Fall detection algorithm here
        sleep_ms(10);
    }
}

int main(void) {
    init_hardware();

    // Launch fall detection on Core 1
    multicore_launch_core1(core1_entry);

    // Main loop on Core 0
    while (true) {
        gpio_put(LED_GREEN_PIN, !gpio_get(LED_GREEN_PIN));

        // Read joystick
        adc_select_input(0); // GP26
        uint16_t joy_x = adc_read();
        adc_select_input(1); // GP27
        uint16_t joy_y = adc_read();

        printf("[MASTER] Joy X=%d, Y=%d, Btn=%d\n",
               joy_x, joy_y, !gpio_get(JOY_BTN_PIN));

        sleep_ms(500);
    }

    return 0;
}
