/**
 * GridBox — BMI160 IMU Driver (C SDK)
 * Full I2C register-level implementation for BMI160 6-axis IMU.
 * Ported from MicroPython bmi160.py.
 */

#include "bmi160.h"
#include <stdio.h>
#include <math.h>
#include "pico/stdlib.h"

/* Temperature register */
#define BMI160_TEMPERATURE 0x20

/* ---- Low-level I2C helpers ---- */

static int bmi160_write_reg(bmi160_t *dev, uint8_t reg, uint8_t val) {
    uint8_t buf[2] = {reg, val};
    int ret = i2c_write_blocking(dev->i2c, dev->addr, buf, 2, false);
    return ret;
}

static uint8_t bmi160_read_reg(bmi160_t *dev, uint8_t reg) {
    uint8_t val = 0;
    i2c_write_blocking(dev->i2c, dev->addr, &reg, 1, true);
    i2c_read_blocking(dev->i2c, dev->addr, &val, 1, false);
    return val;
}

static int bmi160_read_burst(bmi160_t *dev, uint8_t reg, uint8_t *buf, uint8_t len) {
    i2c_write_blocking(dev->i2c, dev->addr, &reg, 1, true);
    return i2c_read_blocking(dev->i2c, dev->addr, buf, len, false);
}

/* ---- Scale factor lookup ---- */

static float acc_range_to_scale(uint8_t range) {
    /* Returns LSB/g value for the given range register setting */
    switch (range) {
        case BMI160_ACC_RANGE_2G:  return 16384.0f;  /* 32768 / 2 */
        case BMI160_ACC_RANGE_4G:  return 8192.0f;   /* 32768 / 4 */
        case BMI160_ACC_RANGE_8G:  return 4096.0f;   /* 32768 / 8 */
        case BMI160_ACC_RANGE_16G: return 2048.0f;   /* 32768 / 16 */
        default:                   return 8192.0f;
    }
}

static float gyr_range_to_scale(uint8_t range) {
    /* Returns LSB/(deg/s) value for the given range register setting */
    switch (range) {
        case BMI160_GYR_RANGE_2000: return 16.4f;    /* 32768 / 2000 */
        case BMI160_GYR_RANGE_1000: return 32.8f;    /* 32768 / 1000 */
        case BMI160_GYR_RANGE_500:  return 65.6f;    /* 32768 / 500 */
        case BMI160_GYR_RANGE_250:  return 131.2f;   /* 32768 / 250 */
        case BMI160_GYR_RANGE_125:  return 262.4f;   /* 32768 / 125 */
        default:                    return 65.6f;
    }
}

/* ODR value for sample rate (ACC_CONF / GYR_CONF bits [3:0]) */
static uint8_t rate_to_odr(uint16_t sample_rate) {
    if (sample_rate >= 1600) return 0x0C;  /* 1600 Hz */
    if (sample_rate >= 800)  return 0x0B;  /* 800 Hz */
    if (sample_rate >= 400)  return 0x0A;  /* 400 Hz */
    if (sample_rate >= 200)  return 0x09;  /* 200 Hz */
    if (sample_rate >= 100)  return 0x08;  /* 100 Hz */
    if (sample_rate >= 50)   return 0x07;  /* 50 Hz */
    return 0x06;                           /* 25 Hz */
}

/* ---- Public API ---- */

bool bmi160_init(bmi160_t *dev, i2c_inst_t *i2c, uint8_t addr,
                 uint8_t accel_range, uint8_t gyro_range, uint16_t sample_rate) {
    dev->i2c = i2c;
    dev->addr = addr;
    dev->acc_scale = acc_range_to_scale(accel_range);
    dev->gyr_scale = gyr_range_to_scale(gyro_range);

    /* Soft reset */
    bmi160_write_reg(dev, BMI160_CMD_REG, BMI160_CMD_SOFT_RESET);
    sleep_ms(100);

    /* Verify chip ID */
    uint8_t id = bmi160_who_am_i(dev);
    if (id != BMI160_CHIP_ID_VAL) {
        printf("[BMI160] ERROR: chip ID 0x%02X (expected 0x%02X)\n", id, BMI160_CHIP_ID_VAL);
        return false;
    }
    printf("[BMI160] Chip ID OK: 0x%02X\n", id);

    /* Power on accelerometer (normal mode) */
    bmi160_write_reg(dev, BMI160_CMD_REG, BMI160_CMD_ACC_NORMAL);
    sleep_ms(50);

    /* Power on gyroscope (normal mode) */
    bmi160_write_reg(dev, BMI160_CMD_REG, BMI160_CMD_GYR_NORMAL);
    sleep_ms(100);

    /* Configure accelerometer: ODR + bandwidth normal (bwp=0x2 = normal) */
    uint8_t odr = rate_to_odr(sample_rate);
    bmi160_write_reg(dev, BMI160_ACC_CONF, (0x02 << 4) | odr);
    bmi160_write_reg(dev, BMI160_ACC_RANGE_REG, accel_range);

    /* Configure gyroscope: ODR + bandwidth normal */
    bmi160_write_reg(dev, BMI160_GYR_CONF, (0x02 << 4) | odr);
    bmi160_write_reg(dev, BMI160_GYR_RANGE_REG, gyro_range);

    /* Verify PMU status — both accel and gyro should be in normal mode */
    uint8_t pmu = bmi160_read_reg(dev, BMI160_PMU_STATUS);
    printf("[BMI160] PMU status: 0x%02X (acc=%d, gyr=%d)\n",
           pmu, (pmu >> 4) & 0x03, (pmu >> 2) & 0x03);

    return true;
}

uint8_t bmi160_who_am_i(bmi160_t *dev) {
    return bmi160_read_reg(dev, BMI160_CHIP_ID_REG);
}

bmi160_vec3_t bmi160_read_accel(bmi160_t *dev) {
    uint8_t buf[6];
    bmi160_read_burst(dev, BMI160_DATA_ACC, buf, 6);

    /* Unpack little-endian int16 */
    int16_t raw_x = (int16_t)(buf[0] | (buf[1] << 8));
    int16_t raw_y = (int16_t)(buf[2] | (buf[3] << 8));
    int16_t raw_z = (int16_t)(buf[4] | (buf[5] << 8));

    bmi160_vec3_t v;
    v.x = (float)raw_x / dev->acc_scale;
    v.y = (float)raw_y / dev->acc_scale;
    v.z = (float)raw_z / dev->acc_scale;
    return v;
}

bmi160_vec3_t bmi160_read_gyro(bmi160_t *dev) {
    uint8_t buf[6];
    bmi160_read_burst(dev, BMI160_DATA_GYR, buf, 6);

    int16_t raw_x = (int16_t)(buf[0] | (buf[1] << 8));
    int16_t raw_y = (int16_t)(buf[2] | (buf[3] << 8));
    int16_t raw_z = (int16_t)(buf[4] | (buf[5] << 8));

    bmi160_vec3_t v;
    v.x = (float)raw_x / dev->gyr_scale;
    v.y = (float)raw_y / dev->gyr_scale;
    v.z = (float)raw_z / dev->gyr_scale;
    return v;
}

bmi160_data_t bmi160_read_all(bmi160_t *dev) {
    /* Burst read 12 bytes: gyro (0x0C-0x11) then accel (0x12-0x17) */
    uint8_t buf[12];
    bmi160_read_burst(dev, BMI160_DATA_GYR, buf, 12);

    /* Gyro: bytes 0-5 */
    int16_t gx = (int16_t)(buf[0] | (buf[1] << 8));
    int16_t gy = (int16_t)(buf[2] | (buf[3] << 8));
    int16_t gz = (int16_t)(buf[4] | (buf[5] << 8));

    /* Accel: bytes 6-11 */
    int16_t ax = (int16_t)(buf[6] | (buf[7] << 8));
    int16_t ay = (int16_t)(buf[8] | (buf[9] << 8));
    int16_t az = (int16_t)(buf[10] | (buf[11] << 8));

    bmi160_data_t d;
    d.gx = (float)gx / dev->gyr_scale;
    d.gy = (float)gy / dev->gyr_scale;
    d.gz = (float)gz / dev->gyr_scale;
    d.ax = (float)ax / dev->acc_scale;
    d.ay = (float)ay / dev->acc_scale;
    d.az = (float)az / dev->acc_scale;
    return d;
}

float bmi160_accel_rms(bmi160_t *dev) {
    bmi160_vec3_t a = bmi160_read_accel(dev);
    return sqrtf(a.x * a.x + a.y * a.y + a.z * a.z);
}

float bmi160_read_temperature(bmi160_t *dev) {
    uint8_t buf[2];
    bmi160_read_burst(dev, BMI160_TEMPERATURE, buf, 2);
    int16_t raw = (int16_t)(buf[0] | (buf[1] << 8));
    /* BMI160 temp formula: 23°C + raw / 512 */
    return 23.0f + (float)raw / 512.0f;
}
