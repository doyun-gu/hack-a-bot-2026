/**
 * GridBox — Power Manager (C SDK)
 * ADC-based power monitoring: bus voltage, motor currents, power calculations.
 * Ported from MicroPython power_manager.py.
 */

#include "power_manager.h"
#include "hardware/adc.h"
#include <stdio.h>

/* ---- Internal helpers ---- */

static float read_adc_avg(power_manager_t *pm, uint8_t adc_input) {
    adc_select_input(adc_input);
    uint32_t total = 0;
    for (int i = 0; i < pm->n_samples; i++) {
        total += adc_read();
    }
    return (float)total / (float)pm->n_samples;
}

static float adc_to_voltage(float raw) {
    /* RP2350 ADC: 12-bit (0-4095), VREF = 3.3V */
    return raw * PM_ADC_VREF / 4095.0f;
}

/* ---- Public API ---- */

void power_manager_init(power_manager_t *pm, float r_sense,
                        float divider_ratio, uint8_t n_samples) {
    pm->r_sense = r_sense;
    pm->divider_ratio = divider_ratio;
    pm->n_samples = n_samples;

    /* Init ADC hardware */
    adc_init();
    adc_gpio_init(26);  /* GP26 = ADC0 = bus voltage */
    adc_gpio_init(27);  /* GP27 = ADC1 = motor 1 current */
    adc_gpio_init(28);  /* GP28 = ADC2 = motor 2 current */

    printf("[POWER] Init OK: Rsense=%.1fΩ, divider=%.1f, samples=%d\n",
           r_sense, divider_ratio, n_samples);
}

float power_manager_read_bus_voltage(power_manager_t *pm) {
    float raw = read_adc_avg(pm, PM_ADC_BUS_VOLTAGE);
    return adc_to_voltage(raw) * pm->divider_ratio;
}

float power_manager_read_motor_current(power_manager_t *pm, uint8_t motor_id) {
    uint8_t input = (motor_id == 1) ? PM_ADC_MOTOR1_CURRENT : PM_ADC_MOTOR2_CURRENT;
    float raw = read_adc_avg(pm, input);
    float v_sense = adc_to_voltage(raw);
    return (v_sense / pm->r_sense) * 1000.0f;  /* convert to mA */
}

power_reading_t power_manager_read_all(power_manager_t *pm) {
    power_reading_t r;

    r.bus_v = power_manager_read_bus_voltage(pm);
    r.m1_mA = power_manager_read_motor_current(pm, 1);
    r.m2_mA = power_manager_read_motor_current(pm, 2);

    /* Power = V * I */
    r.m1_W = r.bus_v * r.m1_mA / 1000.0f;
    r.m2_W = r.bus_v * r.m2_mA / 1000.0f;
    r.total_W = r.m1_W + r.m2_W;

    /* Nominal max power (both motors at max rated current) */
    float nominal_W = r.bus_v * PM_MOTOR_CURRENT_MAX_MA / 1000.0f * 2.0f;
    r.excess_W = (nominal_W > r.total_W) ? (nominal_W - r.total_W) : 0.0f;
    r.efficiency = (nominal_W > 0.0f) ? (r.total_W / nominal_W * 100.0f) : 0.0f;

    return r;
}

float power_manager_get_efficiency(power_manager_t *pm) {
    power_reading_t r = power_manager_read_all(pm);
    return r.efficiency;
}

bool power_manager_is_overloaded(power_manager_t *pm) {
    return power_manager_read_bus_voltage(pm) < PM_BUS_VOLTAGE_CRITICAL;
}

bool power_manager_is_low_voltage(power_manager_t *pm) {
    return power_manager_read_bus_voltage(pm) < PM_BUS_VOLTAGE_LOW;
}

float power_manager_get_excess_power(power_manager_t *pm) {
    power_reading_t r = power_manager_read_all(pm);
    return r.excess_W;
}
