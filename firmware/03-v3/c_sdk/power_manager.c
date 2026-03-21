/**
 * GridBox — Power Manager (C SDK)
 * Stub implementation — prints function calls for testing.
 */

#include "power_manager.h"
#include "hardware/adc.h"
#include <stdio.h>

void power_manager_init(power_manager_t *pm, float r_sense,
                        float divider_ratio, uint8_t n_samples) {
    printf("[STUB] power_manager_init(r_sense=%.1f, divider=%.1f, samples=%d)\n",
           r_sense, divider_ratio, n_samples);

    pm->r_sense = r_sense;
    pm->divider_ratio = divider_ratio;
    pm->n_samples = n_samples;

    /* TODO: adc_init() */
    /* TODO: adc_gpio_init(26), adc_gpio_init(27), adc_gpio_init(28) */
}

static float _read_adc_avg(power_manager_t *pm, uint8_t adc_input) {
    /* TODO: Select ADC input, read n_samples, return average */
    /* adc_select_input(adc_input); */
    /* uint32_t total = 0; */
    /* for (int i = 0; i < pm->n_samples; i++) total += adc_read(); */
    /* return (float)total / pm->n_samples; */
    return 32768.0f;  /* stub: mid-range */
}

static float _adc_to_voltage(float raw) {
    return raw * PM_ADC_VREF / PM_ADC_RESOLUTION;
}

float power_manager_read_bus_voltage(power_manager_t *pm) {
    printf("[STUB] power_manager_read_bus_voltage()\n");
    /* TODO: Read ADC0, convert with divider correction */
    float raw = _read_adc_avg(pm, PM_ADC_BUS_VOLTAGE);
    return _adc_to_voltage(raw) * pm->divider_ratio;
}

float power_manager_read_motor_current(power_manager_t *pm, uint8_t motor_id) {
    printf("[STUB] power_manager_read_motor_current(motor=%d)\n", motor_id);
    /* TODO: Read ADC1 or ADC2, convert via sense resistor */
    uint8_t input = (motor_id == 1) ? PM_ADC_MOTOR1_CURRENT : PM_ADC_MOTOR2_CURRENT;
    float raw = _read_adc_avg(pm, input);
    float v_sense = _adc_to_voltage(raw);
    return (v_sense / pm->r_sense) * 1000.0f;  /* mA */
}

power_reading_t power_manager_read_all(power_manager_t *pm) {
    printf("[STUB] power_manager_read_all()\n");
    /* TODO: Read all channels, compute power metrics */

    power_reading_t r;
    r.bus_v = power_manager_read_bus_voltage(pm);
    r.m1_mA = power_manager_read_motor_current(pm, 1);
    r.m2_mA = power_manager_read_motor_current(pm, 2);
    r.m1_W = r.bus_v * r.m1_mA / 1000.0f;
    r.m2_W = r.bus_v * r.m2_mA / 1000.0f;
    r.total_W = r.m1_W + r.m2_W;

    float nominal_W = r.bus_v * PM_MOTOR_CURRENT_MAX_MA / 1000.0f * 2.0f;
    r.excess_W = (nominal_W > r.total_W) ? (nominal_W - r.total_W) : 0.0f;
    r.efficiency = (nominal_W > 0.0f) ? (r.total_W / nominal_W * 100.0f) : 0.0f;

    return r;
}

float power_manager_get_efficiency(power_manager_t *pm) {
    printf("[STUB] power_manager_get_efficiency()\n");
    power_reading_t r = power_manager_read_all(pm);
    return r.efficiency;
}

bool power_manager_is_overloaded(power_manager_t *pm) {
    printf("[STUB] power_manager_is_overloaded()\n");
    return power_manager_read_bus_voltage(pm) < PM_BUS_VOLTAGE_CRITICAL;
}

bool power_manager_is_low_voltage(power_manager_t *pm) {
    printf("[STUB] power_manager_is_low_voltage()\n");
    return power_manager_read_bus_voltage(pm) < PM_BUS_VOLTAGE_LOW;
}

float power_manager_get_excess_power(power_manager_t *pm) {
    printf("[STUB] power_manager_get_excess_power()\n");
    power_reading_t r = power_manager_read_all(pm);
    return r.excess_W;
}
