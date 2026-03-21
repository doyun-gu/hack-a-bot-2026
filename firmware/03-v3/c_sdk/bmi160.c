/**
 * GridBox — BMI160 IMU Driver (C SDK)
 * Stub implementation — prints function calls for testing.
 */

#include "bmi160.h"
#include <stdio.h>
#include <math.h>

bool bmi160_init(bmi160_t *dev, i2c_inst_t *i2c, uint8_t addr,
                 uint8_t accel_range, uint8_t gyro_range, uint16_t sample_rate) {
    printf("[STUB] bmi160_init(addr=0x%02X, accel=%d, gyro=%d, rate=%d)\n",
           addr, accel_range, gyro_range, sample_rate);

    dev->i2c = i2c;
    dev->addr = addr;

    /* TODO: Set acc_scale based on accel_range */
    /* TODO: Set gyr_scale based on gyro_range */
    /* TODO: Write CMD_ACC_NORMAL and CMD_GYR_NORMAL via I2C */
    /* TODO: Configure ACC_CONF, ACC_RANGE, GYR_CONF, GYR_RANGE registers */
    /* TODO: Verify chip ID == 0xD1 */

    dev->acc_scale = 8192.0f;   /* 4G default */
    dev->gyr_scale = 65.6f;     /* 500 deg/s default */

    return true;
}

uint8_t bmi160_who_am_i(bmi160_t *dev) {
    printf("[STUB] bmi160_who_am_i()\n");
    /* TODO: Read CHIP_ID register (0x00) via I2C */
    return BMI160_CHIP_ID_VAL;
}

bmi160_vec3_t bmi160_read_accel(bmi160_t *dev) {
    printf("[STUB] bmi160_read_accel()\n");
    /* TODO: Read 6 bytes from DATA_ACC (0x12) via I2C */
    /* TODO: Unpack as 3x int16_t little-endian, divide by acc_scale */
    bmi160_vec3_t v = {0.0f, 0.0f, 1.0f};
    return v;
}

bmi160_vec3_t bmi160_read_gyro(bmi160_t *dev) {
    printf("[STUB] bmi160_read_gyro()\n");
    /* TODO: Read 6 bytes from DATA_GYR (0x0C) via I2C */
    /* TODO: Unpack as 3x int16_t little-endian, divide by gyr_scale */
    bmi160_vec3_t v = {0.0f, 0.0f, 0.0f};
    return v;
}

bmi160_data_t bmi160_read_all(bmi160_t *dev) {
    printf("[STUB] bmi160_read_all()\n");
    /* TODO: Burst read 12 bytes from DATA_GYR (0x0C) — gyro + accel */
    bmi160_data_t d = {0.0f, 0.0f, 1.0f, 0.0f, 0.0f, 0.0f};
    return d;
}

float bmi160_accel_rms(bmi160_t *dev) {
    printf("[STUB] bmi160_accel_rms()\n");
    /* TODO: Read accel, compute sqrt(ax^2 + ay^2 + az^2) */
    bmi160_vec3_t a = bmi160_read_accel(dev);
    return sqrtf(a.x * a.x + a.y * a.y + a.z * a.z);
}

float bmi160_read_temperature(bmi160_t *dev) {
    printf("[STUB] bmi160_read_temperature()\n");
    /* TODO: Read 2 bytes from TEMPERATURE (0x20) */
    /* TODO: Convert: 23.0 + raw / 512.0 */
    return 23.0f;
}
