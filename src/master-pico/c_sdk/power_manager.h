/**
 * GridBox — Power Manager (C SDK)
 * ADC-based power monitoring: bus voltage, motor currents, power calculations.
 * Mirrors the MicroPython API in power_manager.py.
 */

#ifndef POWER_MANAGER_H
#define POWER_MANAGER_H

#include <stdbool.h>
#include <stdint.h>

/* ADC input channels on RP2350 */
#define PM_ADC_BUS_VOLTAGE    0   /* GP26 = ADC0 */
#define PM_ADC_MOTOR1_CURRENT 1   /* GP27 = ADC1 */
#define PM_ADC_MOTOR2_CURRENT 2   /* GP28 = ADC2 */

/* Default constants (from config.py) */
#define PM_ADC_VREF              3.3f
#define PM_ADC_RESOLUTION        65535
#define PM_VOLTAGE_DIVIDER_RATIO 2.0f
#define PM_CURRENT_SENSE_R       1.0f
#define PM_ADC_SAMPLES_AVG       10
#define PM_BUS_VOLTAGE_NOMINAL   5.0f
#define PM_BUS_VOLTAGE_LOW       4.2f
#define PM_BUS_VOLTAGE_CRITICAL  3.8f
#define PM_MOTOR_CURRENT_MAX_MA  800.0f

/* Power reading result */
typedef struct {
    float bus_v;       /* bus voltage (V) */
    float m1_mA;       /* motor 1 current (mA) */
    float m2_mA;       /* motor 2 current (mA) */
    float m1_W;        /* motor 1 power (W) */
    float m2_W;        /* motor 2 power (W) */
    float total_W;     /* total power draw (W) */
    float excess_W;    /* available excess power (W) */
    float efficiency;  /* useful/total percentage */
} power_reading_t;

/* Device handle */
typedef struct {
    float r_sense;
    float divider_ratio;
    uint8_t n_samples;
} power_manager_t;

/**
 * Initialise power manager and ADC pins.
 * @param pm            Device handle to populate
 * @param r_sense       Current sense resistor value in ohms
 * @param divider_ratio Voltage divider ratio
 * @param n_samples     Number of ADC samples to average
 */
void power_manager_init(power_manager_t *pm, float r_sense,
                        float divider_ratio, uint8_t n_samples);

/** Read bus voltage in V (with divider correction). */
float power_manager_read_bus_voltage(power_manager_t *pm);

/**
 * Read motor current in mA.
 * @param motor_id 1 or 2
 */
float power_manager_read_motor_current(power_manager_t *pm, uint8_t motor_id);

/** Read all channels and compute power metrics. */
power_reading_t power_manager_read_all(power_manager_t *pm);

/** Return power efficiency percentage. */
float power_manager_get_efficiency(power_manager_t *pm);

/** Return true if bus voltage is below critical threshold. */
bool power_manager_is_overloaded(power_manager_t *pm);

/** Return true if bus voltage is below warning threshold. */
bool power_manager_is_low_voltage(power_manager_t *pm);

/** Return watts available for rerouting. */
float power_manager_get_excess_power(power_manager_t *pm);

#endif /* POWER_MANAGER_H */
