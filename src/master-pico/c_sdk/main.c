/**
 * GridBox — Master Pico (Pico A) — C SDK Production Firmware
 * Dual-core control loop: Core 0 = main + telemetry, Core 1 = IMU + fault detection.
 * Ported from MicroPython master firmware.
 */

#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/multicore.h"
#include "hardware/i2c.h"
#include "hardware/spi.h"
#include "hardware/adc.h"
#include "hardware/timer.h"
#include "hardware/gpio.h"

#include "config.h"
#include "bmi160.h"
#include "pca9685.h"
#include "nrf24l01.h"
#include "power_manager.h"

/* ============ Shared state (Core 0 ↔ Core 1) ============ */

typedef enum {
    FAULT_NONE = 0,
    FAULT_WARNING,      /* vibration elevated */
    FAULT_CRITICAL,     /* sustained high vibration */
    FAULT_SENSOR_FAIL   /* IMU not responding */
} fault_level_t;

static volatile fault_level_t g_fault_level = FAULT_NONE;
static volatile float g_accel_rms = 0.0f;
static volatile float g_temperature = 0.0f;

/* ============ Device handles ============ */

static bmi160_t imu;
static pca9685_t pwm;
static nrf24l01_t radio;
static power_manager_t pm;

/* ============ MOSFET switch control ============ */

static const uint mosfet_pins[] = {MOSFET_M1, MOSFET_M2, MOSFET_LED, MOSFET_RECYCLE};
#define NUM_MOSFETS 4

static bool mosfet_state[NUM_MOSFETS] = {false, false, false, false};

static void mosfets_init(void) {
    for (int i = 0; i < NUM_MOSFETS; i++) {
        gpio_init(mosfet_pins[i]);
        gpio_set_dir(mosfet_pins[i], GPIO_OUT);
        gpio_put(mosfet_pins[i], 0);
    }
}

static void mosfet_set(uint8_t index, bool on) {
    if (index >= NUM_MOSFETS) return;
    gpio_put(mosfet_pins[index], on);
    mosfet_state[index] = on;
}

/* ============ Status LEDs ============ */

static void leds_init(void) {
    gpio_init(LED_RED);
    gpio_set_dir(LED_RED, GPIO_OUT);
    gpio_init(LED_GREEN);
    gpio_set_dir(LED_GREEN, GPIO_OUT);
    gpio_init(LED_ONBOARD);
    gpio_set_dir(LED_ONBOARD, GPIO_OUT);
}

static void led_set_status(fault_level_t level) {
    switch (level) {
        case FAULT_NONE:
            gpio_put(LED_GREEN, 1);
            gpio_put(LED_RED, 0);
            break;
        case FAULT_WARNING:
            gpio_put(LED_GREEN, 1);
            gpio_put(LED_RED, 1);
            break;
        case FAULT_CRITICAL:
        case FAULT_SENSOR_FAIL:
            gpio_put(LED_GREEN, 0);
            gpio_put(LED_RED, 1);
            break;
    }
}

/* ============ Load shedding ============ */

static void shed_loads(float bus_v) {
    if (bus_v < BUS_V_CRITICAL) {
        /* Critical: shed P4 and P3 */
        mosfet_set(3, false);  /* recycle off */
        mosfet_set(2, false);  /* LEDs off */
        pca9685_set_motor_speed(&pwm, MOTOR2_PWM_CH, 50);  /* conveyor half speed */
    } else if (bus_v < BUS_V_LOW) {
        /* Low: shed P4 only */
        mosfet_set(3, false);  /* recycle off */
    } else {
        /* Normal: all on */
        mosfet_set(2, true);
        mosfet_set(3, true);
    }
}

/* ============ Wireless telemetry packet ============ */

/* 32-byte telemetry packet structure:
 * [0]     packet type (0x01 = DATA, 0x02 = HEARTBEAT, 0x03 = ALERT)
 * [1]     fault level
 * [2-3]   bus voltage * 100 (uint16)
 * [4-5]   motor1 current mA (uint16)
 * [6-7]   motor2 current mA (uint16)
 * [8-9]   motor1 power * 100 (uint16)
 * [10-11] motor2 power * 100 (uint16)
 * [12-13] total power * 100 (uint16)
 * [14-15] accel RMS * 1000 (uint16)
 * [16-17] temperature * 10 (int16)
 * [18]    mosfet states (4 bits)
 * [19]    efficiency % (uint8)
 * [20-31] reserved
 */

static void build_telemetry_packet(uint8_t *pkt, uint8_t type,
                                   power_reading_t *pr) {
    memset(pkt, 0, NRF_PAYLOAD_SIZE);
    pkt[0] = type;
    pkt[1] = (uint8_t)g_fault_level;

    uint16_t v = (uint16_t)(pr->bus_v * 100.0f);
    pkt[2] = v & 0xFF; pkt[3] = v >> 8;

    uint16_t m1i = (uint16_t)pr->m1_mA;
    pkt[4] = m1i & 0xFF; pkt[5] = m1i >> 8;

    uint16_t m2i = (uint16_t)pr->m2_mA;
    pkt[6] = m2i & 0xFF; pkt[7] = m2i >> 8;

    uint16_t m1w = (uint16_t)(pr->m1_W * 100.0f);
    pkt[8] = m1w & 0xFF; pkt[9] = m1w >> 8;

    uint16_t m2w = (uint16_t)(pr->m2_W * 100.0f);
    pkt[10] = m2w & 0xFF; pkt[11] = m2w >> 8;

    uint16_t tw = (uint16_t)(pr->total_W * 100.0f);
    pkt[12] = tw & 0xFF; pkt[13] = tw >> 8;

    uint16_t arms = (uint16_t)(g_accel_rms * 1000.0f);
    pkt[14] = arms & 0xFF; pkt[15] = arms >> 8;

    int16_t temp = (int16_t)(g_temperature * 10.0f);
    pkt[16] = temp & 0xFF; pkt[17] = (temp >> 8) & 0xFF;

    pkt[18] = (mosfet_state[0] << 0) | (mosfet_state[1] << 1) |
              (mosfet_state[2] << 2) | (mosfet_state[3] << 3);

    pkt[19] = (uint8_t)pr->efficiency;
}

/* ============ Serial JSON output (for web dashboard) ============ */

static void print_json(power_reading_t *pr) {
    printf("{\"bus_v\":%.2f,\"m1_mA\":%.0f,\"m2_mA\":%.0f,"
           "\"m1_W\":%.2f,\"m2_W\":%.2f,\"total_W\":%.2f,"
           "\"accel_rms\":%.3f,\"temp\":%.1f,"
           "\"fault\":%d,\"efficiency\":%.0f,"
           "\"sw\":[%d,%d,%d,%d]}\n",
           pr->bus_v, pr->m1_mA, pr->m2_mA,
           pr->m1_W, pr->m2_W, pr->total_W,
           g_accel_rms, g_temperature,
           (int)g_fault_level, pr->efficiency,
           mosfet_state[0], mosfet_state[1],
           mosfet_state[2], mosfet_state[3]);
}

/* ============ Process incoming wireless commands ============ */

static void process_command(uint8_t *pkt) {
    /* Packet type 0x05 = COMMAND from SCADA */
    if (pkt[0] != 0x05) return;

    uint8_t cmd = pkt[1];
    uint8_t param = pkt[2];

    switch (cmd) {
        case 0x01:  /* Set motor 1 speed */
            pca9685_set_motor_speed(&pwm, MOTOR1_PWM_CH, param);
            break;
        case 0x02:  /* Set motor 2 speed */
            pca9685_set_motor_speed(&pwm, MOTOR2_PWM_CH, param);
            break;
        case 0x03:  /* Set valve servo angle */
            pca9685_set_servo_angle(&pwm, SERVO_VALVE_CH, param);
            break;
        case 0x04:  /* Set gate servo angle */
            pca9685_set_servo_angle(&pwm, SERVO_GATE_CH, param);
            break;
        case 0x05:  /* MOSFET switch control */
            mosfet_set(param >> 4, param & 0x01);
            break;
        case 0xFF:  /* Emergency stop */
            pca9685_all_off(&pwm);
            for (int i = 0; i < NUM_MOSFETS; i++) mosfet_set(i, false);
            printf("[MASTER] EMERGENCY STOP\n");
            break;
    }
}

/* ============ CORE 1: IMU fault detection ============ */

static void core1_entry(void) {
    printf("[CORE1] Fault detection started\n");

    uint32_t fault_start_ms = 0;
    bool fault_timing = false;

    while (true) {
        /* Read IMU at ~100Hz */
        float rms = bmi160_accel_rms(&imu);
        float temp = bmi160_read_temperature(&imu);

        /* Update shared state */
        g_accel_rms = rms;
        g_temperature = temp;

        /* Vibration classification (ISO 10816 simplified) */
        if (rms < IMU_HEALTHY_G) {
            g_fault_level = FAULT_NONE;
            fault_timing = false;
        } else if (rms < IMU_WARNING_G) {
            g_fault_level = FAULT_WARNING;
            fault_timing = false;
        } else {
            /* Sustained high vibration check */
            if (!fault_timing) {
                fault_start_ms = to_ms_since_boot(get_absolute_time());
                fault_timing = true;
            } else {
                uint32_t elapsed = to_ms_since_boot(get_absolute_time()) - fault_start_ms;
                if (elapsed >= IMU_FAULT_DURATION_MS) {
                    g_fault_level = FAULT_CRITICAL;
                }
            }
        }

        sleep_ms(10);  /* ~100Hz */
    }
}

/* ============ Hardware init ============ */

static bool init_all_hardware(void) {
    stdio_init_all();
    sleep_ms(1000);  /* wait for USB serial */

    printf("================================\n");
    printf("  GridBox Master (C SDK)\n");
    printf("  Production Firmware\n");
    printf("================================\n");

    /* Status LEDs */
    leds_init();
    gpio_put(LED_RED, 1);  /* red during init */

    /* MOSFET switches */
    mosfets_init();

    /* I2C bus */
    i2c_init(I2C_PORT, I2C_FREQ);
    gpio_set_function(I2C_SDA, GPIO_FUNC_I2C);
    gpio_set_function(I2C_SCL, GPIO_FUNC_I2C);
    gpio_pull_up(I2C_SDA);
    gpio_pull_up(I2C_SCL);
    printf("[INIT] I2C OK\n");

    /* SPI bus */
    spi_init(SPI_PORT, SPI_BAUD);
    gpio_set_function(SPI_SCK, GPIO_FUNC_SPI);
    gpio_set_function(SPI_MOSI, GPIO_FUNC_SPI);
    gpio_set_function(SPI_MISO, GPIO_FUNC_SPI);
    printf("[INIT] SPI OK\n");

    /* BMI160 IMU */
    bool imu_ok = bmi160_init(&imu, I2C_PORT, BMI160_ADDR,
                               BMI160_ACC_RANGE_4G, BMI160_GYR_RANGE_500,
                               IMU_SAMPLE_RATE);
    if (!imu_ok) {
        printf("[INIT] WARNING: BMI160 init failed\n");
        g_fault_level = FAULT_SENSOR_FAIL;
    }

    /* PCA9685 PWM */
    pca9685_init(&pwm, I2C_PORT, PCA9685_ADDR, PCA9685_PWM_FREQ);

    /* Power manager ADC */
    power_manager_init(&pm, SENSE_R, VOLTAGE_DIVIDER, ADC_SAMPLES);

    /* nRF24L01+ wireless */
    const uint8_t tx_addr[] = NRF_TX_ADDR_STR;
    const uint8_t rx_addr[] = NRF_RX_ADDR_STR;
    nrf24l01_init(&radio, SPI_PORT, NRF_CSN, NRF_CE,
                  NRF_CHANNEL, NRF_PAYLOAD_SIZE, NRF_DATA_RATE,
                  tx_addr, rx_addr);

    /* All good — green LED */
    gpio_put(LED_RED, 0);
    gpio_put(LED_GREEN, 1);
    printf("[INIT] All hardware initialised\n");

    return imu_ok;
}

/* ============ CORE 0: Main control loop ============ */

int main(void) {
    init_all_hardware();

    /* Launch fault detection on Core 1 */
    multicore_launch_core1(core1_entry);

    /* Enable all MOSFET switches for normal operation */
    for (int i = 0; i < NUM_MOSFETS; i++) {
        mosfet_set(i, true);
    }

    /* Start motors at default speed */
    pca9685_set_motor_speed(&pwm, MOTOR1_PWM_CH, 60);  /* fan 60% */
    pca9685_set_motor_speed(&pwm, MOTOR2_PWM_CH, 40);  /* conveyor 40% */

    /* Servos to centre */
    pca9685_set_servo_angle(&pwm, SERVO_VALVE_CH, 90);
    pca9685_set_servo_angle(&pwm, SERVO_GATE_CH, 90);

    printf("[MASTER] Control loop running at 100Hz\n");

    /* Timing counters */
    uint32_t last_wireless_ms = 0;
    uint32_t last_heartbeat_ms = 0;
    uint32_t last_serial_ms = 0;

    /* Main 100Hz control loop */
    while (true) {
        uint32_t loop_start = time_us_32();
        uint32_t now_ms = to_ms_since_boot(get_absolute_time());

        /* 1. Read power */
        power_reading_t pr = power_manager_read_all(&pm);

        /* 2. Load shedding based on voltage */
        shed_loads(pr.bus_v);

        /* 3. Update status LEDs */
        led_set_status(g_fault_level);
        gpio_put(LED_ONBOARD, !gpio_get(LED_ONBOARD));  /* heartbeat blink */

        /* 4. Check for incoming wireless commands */
        uint8_t rx_buf[NRF_PAYLOAD_SIZE];
        nrf24l01_start_listening(&radio);
        sleep_us(300);  /* brief listen window */
        if (nrf24l01_available(&radio)) {
            if (nrf24l01_recv(&radio, rx_buf)) {
                process_command(rx_buf);
            }
        }
        nrf24l01_stop_listening(&radio);

        /* 5. Send telemetry wirelessly */
        if (now_ms - last_wireless_ms >= WIRELESS_SEND_MS) {
            last_wireless_ms = now_ms;
            uint8_t pkt[NRF_PAYLOAD_SIZE];
            build_telemetry_packet(pkt, 0x01, &pr);  /* DATA packet */
            nrf24l01_send(&radio, pkt);
        }

        /* 6. Send heartbeat */
        if (now_ms - last_heartbeat_ms >= HEARTBEAT_MS) {
            last_heartbeat_ms = now_ms;
            uint8_t pkt[NRF_PAYLOAD_SIZE];
            build_telemetry_packet(pkt, 0x02, &pr);  /* HEARTBEAT packet */
            nrf24l01_send(&radio, pkt);
        }

        /* 7. Print JSON to USB serial (for web dashboard) */
        if (now_ms - last_serial_ms >= SERIAL_PRINT_MS) {
            last_serial_ms = now_ms;
            print_json(&pr);
        }

        /* 8. Maintain 100Hz loop timing */
        uint32_t elapsed_us = time_us_32() - loop_start;
        if (elapsed_us < MAIN_LOOP_US) {
            sleep_us(MAIN_LOOP_US - elapsed_us);
        }
    }

    return 0;
}
