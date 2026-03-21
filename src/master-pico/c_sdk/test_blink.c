/**
 * GridBox C SDK Test — LED Blink + Temperature
 * Proves C SDK compiles and runs on your Pico.
 */

#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/adc.h"

int main(void) {
    stdio_init_all();
    sleep_ms(2000);  // wait for USB serial

    printf("================================\n");
    printf("  GridBox C SDK — Blink Test\n");
    printf("================================\n");

    // LED
    gpio_init(PICO_DEFAULT_LED_PIN);
    gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);

    // ADC for internal temp sensor
    adc_init();
    adc_set_temp_sensor_enabled(true);

    int count = 0;
    while (true) {
        // Blink LED
        gpio_put(PICO_DEFAULT_LED_PIN, 1);
        sleep_ms(250);
        gpio_put(PICO_DEFAULT_LED_PIN, 0);
        sleep_ms(250);

        // Read internal temperature
        adc_select_input(4);  // temp sensor channel
        uint16_t raw = adc_read();
        float voltage = raw * 3.3f / 4095.0f;
        float temp_c = 27.0f - (voltage - 0.706f) / 0.001721f;

        count++;
        printf("[C SDK] Blink #%d  Temp: %.1f C  ADC: %d\n", count, temp_c, raw);
    }

    return 0;
}
