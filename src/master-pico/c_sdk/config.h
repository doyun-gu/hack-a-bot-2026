/**
 * GridBox — Master Pico (Pico A) Configuration (C SDK)
 * All pin assignments, timing, and threshold constants.
 * Ported from MicroPython config.py — this is the C single source of truth.
 */

#ifndef CONFIG_H
#define CONFIG_H

/* ============ I2C BUS (BMI160 + PCA9685) ============ */
#define I2C_PORT       i2c0
#define I2C_SDA        4
#define I2C_SCL        5
#define I2C_FREQ       400000
#define BMI160_ADDR    0x68
#define PCA9685_ADDR   0x40

/* ============ SPI BUS (nRF24L01+) ============ */
#define SPI_PORT       spi0
#define SPI_SCK        2
#define SPI_MOSI       3
#define SPI_MISO       16       /* GP16 — NOT GP4 */
#define SPI_BAUD       10000000
#define NRF_CE         0
#define NRF_CSN        1

/* nRF24L01+ settings */
#define NRF_CHANNEL         100      /* 2.4GHz + 100 = 2.500GHz */
#define NRF_PAYLOAD_SIZE    32
#define NRF_DATA_RATE       250      /* kbps */
#define NRF_TX_ADDR_STR     "NSYNT"  /* 5-byte TX address */
#define NRF_RX_ADDR_STR     "NSYNR"  /* 5-byte RX address */

/* ============ MOSFET SWITCHES (GPIO) ============ */
#define MOSFET_M1      10       /* GP10 → Motor 1 (fan) */
#define MOSFET_M2      11       /* GP11 → Motor 2 (pump/conveyor) */
#define MOSFET_LED     12       /* GP12 → LED bank */
#define MOSFET_RECYCLE 13       /* GP13 → Recycle path */

/* ============ STATUS LEDs ============ */
#define LED_RED        14
#define LED_GREEN      15
#define LED_ONBOARD    25

/* ============ ADC (Power Sensing) ============ */
#define ADC_BUS_V      26       /* GP26 — bus voltage via divider */
#define ADC_M1_I       27       /* GP27 — Motor 1 current sense */
#define ADC_M2_I       28       /* GP28 — Motor 2 current sense */
#define ADC_VREF       3.3f
#define ADC_RESOLUTION 4095     /* 12-bit ADC on RP2350 */
#define VOLTAGE_DIVIDER 2.0f    /* 10kΩ+10kΩ divider */
#define SENSE_R        1.0f     /* 1Ω current sense resistor */
#define ADC_SAMPLES    10       /* samples to average per reading */

/* ============ TIMING ============ */
#define MAIN_LOOP_US        10000   /* 100Hz main loop */
#define WIRELESS_SEND_MS    50      /* telemetry every 50ms */
#define HEARTBEAT_MS        1000    /* heartbeat every 1s */
#define SERIAL_PRINT_MS     200     /* JSON for web dashboard */

/* ============ IMU THRESHOLDS ============ */
#define IMU_SAMPLE_RATE     100     /* Hz */
#define IMU_ACCEL_RANGE     4       /* ±4g */
#define IMU_GYRO_RANGE      500     /* ±500°/s */
#define IMU_WINDOW_SIZE     100     /* rolling RMS window */
#define IMU_HEALTHY_G       1.0f    /* below = healthy */
#define IMU_WARNING_G       2.0f    /* above = warning */
#define IMU_FAULT_G         2.0f    /* sustained = fault */
#define IMU_FAULT_DURATION_MS 3000  /* sustained vibration = fault */

/* ============ POWER THRESHOLDS ============ */
#define BUS_V_NOMINAL       5.0f    /* expected bus voltage */
#define BUS_V_LOW           4.2f    /* low voltage warning */
#define BUS_V_CRITICAL      3.8f    /* critical — shed loads */
#define MOTOR_I_MAX_MA      800.0f  /* stall/jam threshold */

/* ============ PCA9685 SERVO/MOTOR CHANNELS ============ */
#define SERVO_VALVE_CH      0
#define SERVO_GATE_CH       1
#define MOTOR1_PWM_CH       2
#define MOTOR2_PWM_CH       3
#define SERVO_MIN_US        500     /* min pulse width µs */
#define SERVO_MAX_US        2500    /* max pulse width µs */
#define SERVO_CENTRE_US     1500    /* centre position */
#define PCA9685_PWM_FREQ    50      /* Hz — standard servo freq */

/* ============ FACTORY / SORTING ============ */
#define BELT_LENGTH_CM          20
#define BELT_SPEED_CM_PER_S     5
#define WEIGHT_THRESH_MIN       0.03f   /* min current delta for detection */
#define WEIGHT_THRESH_LIGHT     0.05f   /* below = reject light */
#define WEIGHT_THRESH_HEAVY     0.15f   /* above = reject heavy */
#define WEIGHT_THRESH_JAM       0.30f   /* above = jam fault */

/* ============ LOAD PRIORITIES (for shedding) ============ */
/* P1=highest (keep), P4=lowest (shed first) */
#define LOAD_PRIO_MOTOR1    1       /* fan — critical cooling */
#define LOAD_PRIO_MOTOR2    2       /* conveyor — important */
#define LOAD_PRIO_LEDS      3       /* LED bank — shed early */
#define LOAD_PRIO_RECYCLE   4       /* recycle path — shed first */

#endif /* CONFIG_H */
