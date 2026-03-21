/**
 * GridBox — BMI160 IMU Driver (C SDK)
 * I2C driver for BMI160 6-axis IMU (accelerometer + gyroscope).
 * Mirrors the MicroPython API in bmi160.py.
 */

#ifndef BMI160_H
#define BMI160_H

#include "hardware/i2c.h"
#include <stdbool.h>
#include <stdint.h>

/* BMI160 register addresses */
#define BMI160_CHIP_ID_REG   0x00
#define BMI160_CHIP_ID_VAL   0xD1
#define BMI160_ERR_REG       0x02
#define BMI160_PMU_STATUS    0x03
#define BMI160_DATA_GYR      0x0C
#define BMI160_DATA_ACC      0x12
#define BMI160_ACC_CONF      0x40
#define BMI160_ACC_RANGE_REG 0x41
#define BMI160_GYR_CONF      0x42
#define BMI160_GYR_RANGE_REG 0x43
#define BMI160_CMD_REG       0x7E

/* CMD values */
#define BMI160_CMD_SOFT_RESET 0xB6
#define BMI160_CMD_ACC_NORMAL 0x11
#define BMI160_CMD_GYR_NORMAL 0x15

/* Accelerometer range values */
#define BMI160_ACC_RANGE_2G  0x03
#define BMI160_ACC_RANGE_4G  0x05
#define BMI160_ACC_RANGE_8G  0x08
#define BMI160_ACC_RANGE_16G 0x0C

/* Gyroscope range values */
#define BMI160_GYR_RANGE_2000 0x00
#define BMI160_GYR_RANGE_1000 0x01
#define BMI160_GYR_RANGE_500  0x02
#define BMI160_GYR_RANGE_250  0x03
#define BMI160_GYR_RANGE_125  0x04

/* 3-axis reading */
typedef struct {
    float x;
    float y;
    float z;
} bmi160_vec3_t;

/* Full 6-axis reading */
typedef struct {
    float ax, ay, az;  /* accelerometer (g) */
    float gx, gy, gz;  /* gyroscope (deg/s) */
} bmi160_data_t;

/* Device handle */
typedef struct {
    i2c_inst_t *i2c;
    uint8_t addr;
    float acc_scale;
    float gyr_scale;
} bmi160_t;

/**
 * Initialise BMI160.
 * @param dev         Device handle to populate
 * @param i2c         I2C instance (i2c0 or i2c1)
 * @param addr        I2C address (0x68 or 0x69)
 * @param accel_range BMI160_ACC_RANGE_* constant
 * @param gyro_range  BMI160_GYR_RANGE_* constant
 * @param sample_rate Desired sample rate in Hz
 * @return true if chip ID matches 0xD1
 */
bool bmi160_init(bmi160_t *dev, i2c_inst_t *i2c, uint8_t addr,
                 uint8_t accel_range, uint8_t gyro_range, uint16_t sample_rate);

/** Read chip ID register. Should return 0xD1. */
uint8_t bmi160_who_am_i(bmi160_t *dev);

/** Read accelerometer. Returns (ax, ay, az) in g. */
bmi160_vec3_t bmi160_read_accel(bmi160_t *dev);

/** Read gyroscope. Returns (gx, gy, gz) in deg/s. */
bmi160_vec3_t bmi160_read_gyro(bmi160_t *dev);

/** Read all 6 axes in one burst. */
bmi160_data_t bmi160_read_all(bmi160_t *dev);

/** Return RMS acceleration magnitude: sqrt(ax^2 + ay^2 + az^2). */
float bmi160_accel_rms(bmi160_t *dev);

/** Read temperature in degrees C. */
float bmi160_read_temperature(bmi160_t *dev);

#endif /* BMI160_H */
