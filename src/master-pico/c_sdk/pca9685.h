/**
 * GridBox — PCA9685 16-Channel PWM Driver (C SDK)
 * I2C driver for PCA9685 servo/motor controller.
 * Mirrors the MicroPython API in pca9685.py.
 */

#ifndef PCA9685_H
#define PCA9685_H

#include "hardware/i2c.h"
#include <stdbool.h>
#include <stdint.h>

/* PCA9685 register addresses */
#define PCA9685_MODE1        0x00
#define PCA9685_MODE2        0x01
#define PCA9685_PRE_SCALE    0xFE
#define PCA9685_LED0_ON_L    0x06
#define PCA9685_ALL_LED_ON_L 0xFA

/* MODE1 bits */
#define PCA9685_RESTART      0x80
#define PCA9685_SLEEP        0x10
#define PCA9685_AI           0x20
#define PCA9685_ALLCALL      0x01

/* Constants */
#define PCA9685_CLOCK_FREQ   25000000
#define PCA9685_RESOLUTION   4096
#define PCA9685_NUM_CHANNELS 16

/* Device handle */
typedef struct {
    i2c_inst_t *i2c;
    uint8_t addr;
} pca9685_t;

/**
 * Initialise PCA9685.
 * @param dev     Device handle to populate
 * @param i2c     I2C instance
 * @param addr    I2C address (default 0x40)
 * @param freq_hz PWM frequency in Hz (default 50 for servos)
 * @return true on success
 */
bool pca9685_init(pca9685_t *dev, i2c_inst_t *i2c, uint8_t addr, uint16_t freq_hz);

/** Set PWM frequency in Hz. Valid range: 24-1526. */
void pca9685_set_frequency(pca9685_t *dev, uint16_t freq_hz);

/** Set raw PWM on/off values for a channel (0-15). */
void pca9685_set_pwm(pca9685_t *dev, uint8_t channel, uint16_t on, uint16_t off);

/** Set duty cycle 0-100% for a channel. */
void pca9685_set_duty(pca9685_t *dev, uint8_t channel, uint8_t duty_percent);

/** Set servo position by angle (0-180 degrees). Assumes 50Hz PWM. */
void pca9685_set_servo_angle(pca9685_t *dev, uint8_t channel, uint16_t angle);

/** Set motor speed 0-100% via PWM duty cycle. */
void pca9685_set_motor_speed(pca9685_t *dev, uint8_t channel, uint8_t speed_percent);

/** Turn off a single channel. */
void pca9685_off(pca9685_t *dev, uint8_t channel);

/** Turn off all 16 channels. */
void pca9685_all_off(pca9685_t *dev);

#endif /* PCA9685_H */
