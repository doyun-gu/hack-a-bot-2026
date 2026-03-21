/**
 * GridBox — PCA9685 16-Channel PWM Driver (C SDK)
 * Full I2C register-level implementation for servo and motor control.
 * Ported from MicroPython pca9685.py.
 */

#include "pca9685.h"
#include <stdio.h>
#include "pico/stdlib.h"

/* ---- Low-level I2C helpers ---- */

static int pca9685_write_reg(pca9685_t *dev, uint8_t reg, uint8_t val) {
    uint8_t buf[2] = {reg, val};
    return i2c_write_blocking(dev->i2c, dev->addr, buf, 2, false);
}

static uint8_t pca9685_read_reg(pca9685_t *dev, uint8_t reg) {
    uint8_t val = 0;
    i2c_write_blocking(dev->i2c, dev->addr, &reg, 1, true);
    i2c_read_blocking(dev->i2c, dev->addr, &val, 1, false);
    return val;
}

/* ---- Public API ---- */

bool pca9685_init(pca9685_t *dev, i2c_inst_t *i2c, uint8_t addr, uint16_t freq_hz) {
    dev->i2c = i2c;
    dev->addr = addr;

    /* Reset: write RESTART bit to MODE1 */
    pca9685_write_reg(dev, PCA9685_MODE1, PCA9685_RESTART);
    sleep_ms(10);

    /* Set auto-increment + allcall */
    pca9685_write_reg(dev, PCA9685_MODE1, PCA9685_AI | PCA9685_ALLCALL);

    /* Set PWM frequency */
    pca9685_set_frequency(dev, freq_hz);

    /* Turn off all channels initially */
    pca9685_all_off(dev);

    printf("[PCA9685] Init OK at 0x%02X, freq=%dHz\n", addr, freq_hz);
    return true;
}

void pca9685_set_frequency(pca9685_t *dev, uint16_t freq_hz) {
    /* Prescale = round(25MHz / (4096 * freq)) - 1 */
    /* Clamp to valid range: 24-1526 Hz */
    if (freq_hz < 24) freq_hz = 24;
    if (freq_hz > 1526) freq_hz = 1526;

    uint8_t prescale = (uint8_t)((PCA9685_CLOCK_FREQ / (PCA9685_RESOLUTION * (uint32_t)freq_hz)) - 1);

    /* Must enter sleep mode to change prescaler */
    uint8_t old_mode = pca9685_read_reg(dev, PCA9685_MODE1);
    uint8_t sleep_mode = (old_mode & ~PCA9685_RESTART) | PCA9685_SLEEP;

    pca9685_write_reg(dev, PCA9685_MODE1, sleep_mode);
    pca9685_write_reg(dev, PCA9685_PRE_SCALE, prescale);
    pca9685_write_reg(dev, PCA9685_MODE1, old_mode);
    sleep_us(500);

    /* Set RESTART bit to re-enable PWM */
    pca9685_write_reg(dev, PCA9685_MODE1, old_mode | PCA9685_RESTART);

    printf("[PCA9685] Frequency set to %dHz (prescale=%d)\n", freq_hz, prescale);
}

void pca9685_set_pwm(pca9685_t *dev, uint8_t channel, uint16_t on, uint16_t off) {
    if (channel >= PCA9685_NUM_CHANNELS) return;

    uint8_t reg = PCA9685_LED0_ON_L + (channel * 4);
    uint8_t buf[5] = {
        reg,
        (uint8_t)(on & 0xFF),
        (uint8_t)(on >> 8),
        (uint8_t)(off & 0xFF),
        (uint8_t)(off >> 8)
    };
    i2c_write_blocking(dev->i2c, dev->addr, buf, 5, false);
}

void pca9685_set_duty(pca9685_t *dev, uint8_t channel, uint8_t duty_percent) {
    if (duty_percent == 0) {
        /* Full OFF: set bit 12 of OFF register */
        pca9685_set_pwm(dev, channel, 0, PCA9685_RESOLUTION);
    } else if (duty_percent >= 100) {
        /* Full ON: set bit 12 of ON register */
        pca9685_set_pwm(dev, channel, PCA9685_RESOLUTION, 0);
    } else {
        uint16_t off = (uint16_t)((uint32_t)duty_percent * PCA9685_RESOLUTION / 100);
        pca9685_set_pwm(dev, channel, 0, off);
    }
}

void pca9685_set_servo_angle(pca9685_t *dev, uint8_t channel, uint16_t angle) {
    /* Clamp angle to 0-180 */
    if (angle > 180) angle = 180;

    /* Map angle to pulse width: 500µs (0°) to 2500µs (180°) */
    float pulse_us = 500.0f + ((float)angle / 180.0f) * 2000.0f;

    /* Convert pulse width to 12-bit count at current frequency (assume 50Hz = 20ms period) */
    /* count = pulse_us / 20000us * 4096 */
    uint16_t off = (uint16_t)(pulse_us / 20000.0f * PCA9685_RESOLUTION);
    pca9685_set_pwm(dev, channel, 0, off);
}

void pca9685_set_motor_speed(pca9685_t *dev, uint8_t channel, uint8_t speed_percent) {
    uint8_t clamped = speed_percent > 100 ? 100 : speed_percent;
    pca9685_set_duty(dev, channel, clamped);
}

void pca9685_off(pca9685_t *dev, uint8_t channel) {
    /* Full OFF */
    pca9685_set_pwm(dev, channel, 0, PCA9685_RESOLUTION);
}

void pca9685_all_off(pca9685_t *dev) {
    /* Write to ALL_LED registers: ON=0, OFF bit 12 set (full off) */
    uint8_t buf[5] = {
        PCA9685_ALL_LED_ON_L,
        0x00, 0x00,             /* ON_L, ON_H = 0 */
        0x00, 0x10              /* OFF_L = 0, OFF_H = bit 4 set (= bit 12 of 12-bit value) */
    };
    i2c_write_blocking(dev->i2c, dev->addr, buf, 5, false);
}
