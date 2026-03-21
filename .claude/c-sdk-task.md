# C SDK Production Firmware — Worker Task

> Port the MicroPython firmware to C/C++ using the Pico SDK for production demo.
> C gives deterministic timing, instant boot, and impresses judges.

## Context

- Read CLAUDE.md for project context
- Read src/firmware-dev-plan.md for architecture
- The MicroPython versions are in src/master-pico/micropython/ and src/slave-pico/micropython/
- C SDK scaffolding exists in src/master-pico/c_sdk/ and src/slave-pico/c_sdk/
- Header stubs already exist: bmi160.h, pca9685.h, nrf24l01.h, power_manager.h
- CMakeLists.txt is ready
- Target board: Pico 2 (RP2350, set PICO_BOARD=pico2)

## Rules

1. Pull latest main first
2. Write real implementations (not stubs) for the C files
3. Port the logic from the MicroPython versions — same algorithms, same pin mapping
4. Use config.py values but as C #defines in a config.h
5. USB serial output for debugging (pico_enable_stdio_usb)
6. Dual-core: core0 = main loop, core1 = IMU + fault detection
7. Commit and push after each completed driver
8. Don't modify MicroPython files or docs

## Pin Mapping (from config.py — use these in config.h)

```c
// I2C
#define I2C_PORT i2c0
#define I2C_SDA 4
#define I2C_SCL 5
#define I2C_FREQ 400000
#define BMI160_ADDR 0x68
#define PCA9685_ADDR 0x40

// SPI (nRF24L01+)
#define SPI_PORT spi0
#define SPI_SCK 2
#define SPI_MOSI 3
#define SPI_MISO 16
#define NRF_CE 0
#define NRF_CSN 1
#define NRF_CHANNEL 100

// MOSFET switches
#define MOSFET_M1 10
#define MOSFET_M2 11
#define MOSFET_LED 12
#define MOSFET_RECYCLE 13

// Status LEDs
#define LED_RED 14
#define LED_GREEN 15

// ADC
#define ADC_BUS_V 26
#define ADC_M1_I 27
#define ADC_M2_I 28
#define ADC_VREF 3.3f
#define VOLTAGE_DIVIDER 2.0f
#define SENSE_R 1.0f
```

## Task List

### Task 1: config.h

Create `src/master-pico/c_sdk/config.h`:
- All pin defines from above
- Timing constants (MAIN_LOOP_US = 10000 for 100Hz)
- Threshold constants (IMU healthy < 1.0g, warning < 2.0g, fault >= 2.0g)
- PCA9685 servo constants (min/max pulse, channels)
- Include guards

Commit: `"Add C SDK config.h with all pin and threshold defines"`

### Task 2: bmi160.c/.h — IMU driver

Implement the full BMI160 I2C driver:

```c
// bmi160.h
bool bmi160_init(i2c_inst_t *i2c, uint8_t addr);
uint8_t bmi160_who_am_i(void);
void bmi160_read_accel(float *ax, float *ay, float *az);
void bmi160_read_gyro(float *gx, float *gy, float *gz);
float bmi160_accel_rms(void);
```

Register-level implementation:
- CMD register 0x7E: write 0x11 (accel normal), 0x15 (gyro normal)
- ACC_CONF 0x40: set ODR, range
- GYR_CONF 0x42: set ODR, range
- DATA registers 0x0C-0x17: read 12 bytes, convert to float
- Accel: raw * range / 32768.0
- Gyro: raw * range / 32768.0

Commit: `"Add C SDK BMI160 IMU driver — full I2C implementation"`

### Task 3: pca9685.c/.h — PWM driver

```c
bool pca9685_init(i2c_inst_t *i2c, uint8_t addr, uint16_t freq_hz);
void pca9685_set_pwm(uint8_t channel, uint16_t on, uint16_t off);
void pca9685_set_duty(uint8_t channel, float duty_percent);
void pca9685_set_servo(uint8_t channel, float angle_deg);
void pca9685_set_motor(uint8_t channel, float speed_percent);
void pca9685_off(uint8_t channel);
void pca9685_all_off(void);
```

Register-level:
- MODE1 = 0x00, write 0x20 (auto-increment)
- PRE_SCALE = 0xFE, prescale = 25MHz / (4096 * freq) - 1
- LED0_ON_L = 0x06, each channel +4 offset, 4 bytes (ON_L, ON_H, OFF_L, OFF_H)
- Servo: angle → pulse width (500-2500us) → PWM count
- Motor: speed% → duty cycle → PWM count

Commit: `"Add C SDK PCA9685 PWM driver — servos and motors"`

### Task 4: nrf24l01.c/.h — Wireless driver

```c
bool nrf24l01_init(spi_inst_t *spi, uint csn, uint ce, uint8_t channel, const uint8_t *tx_addr, const uint8_t *rx_addr);
bool nrf24l01_send(const uint8_t *data, uint8_t len);
bool nrf24l01_available(void);
bool nrf24l01_recv(uint8_t *data, uint8_t len);
void nrf24l01_start_listening(void);
void nrf24l01_stop_listening(void);
```

Register-level:
- CONFIG = 0x00, EN_AA = 0x01, EN_RXADDR = 0x02
- SETUP_AW = 0x03 (5-byte address), RF_CH = 0x05 (channel)
- RF_SETUP = 0x06 (250kbps, max power)
- TX_ADDR = 0x10, RX_ADDR_P0 = 0x0A
- W_TX_PAYLOAD = 0xA0, R_RX_PAYLOAD = 0x61
- STATUS = 0x07, FIFO_STATUS = 0x17
- SPI: CSN low → send command → CSN high

Commit: `"Add C SDK nRF24L01+ wireless driver — full SPI implementation"`

### Task 5: power_manager.c/.h — ADC sensing

```c
void power_init(void);
float power_read_bus_voltage(void);
float power_read_motor_current(uint8_t motor_id);
float power_read_total_watts(void);
float power_read_efficiency(void);
bool power_is_overloaded(void);
```

Implementation:
- adc_init(), adc_gpio_init() for GP26, GP27, GP28
- adc_select_input() + adc_read() with 10-sample averaging
- Voltage: adc * 3.3 / 4095 * DIVIDER_RATIO
- Current: adc * 3.3 / 4095 / SENSE_R * 1000 (mA)
- Power: voltage * current

Commit: `"Add C SDK power manager — ADC sensing with averaging"`

### Task 6: main.c — Full integrated control loop

Rewrite `src/master-pico/c_sdk/main.c` with:

```c
// Core 0: Main control loop
void core0_main() {
    // Init all hardware
    // 100Hz loop:
    //   1. Read ADC (power)
    //   2. Check wireless for commands
    //   3. Run fault state machine
    //   4. Control motors/servos
    //   5. Send telemetry wireless
    //   6. Print JSON serial (for web dashboard)
}

// Core 1: Fault detection
void core1_entry() {
    // 100Hz IMU reading
    // Vibration classification
    // Fault detection (shared via multicore_fifo or global volatile)
}
```

Use `repeating_timer_callback` for precise 100Hz timing.
Use `multicore_launch_core1()` for dual-core.
Use `printf()` for USB serial JSON output.

Commit: `"Add C SDK main.c — dual-core control loop with all drivers integrated"`

### Task 7: Slave Pico C SDK

Create `src/slave-pico/c_sdk/`:
- `config.h` — Pico B pin defines
- `ssd1306.c/.h` — OLED driver (I2C, framebuffer)
- `main.c` — Receive wireless, display on OLED, read joystick, send commands

This is lower priority — do it if time permits. Minimum viable: just receive and print to serial.

Commit: `"Add C SDK slave Pico — OLED + wireless RX"`

### Task 8: Update CMakeLists.txt and test build

Make sure CMakeLists.txt includes all new files.
Try to build (if PICO_SDK_PATH is set):
```bash
cd src/master-pico/c_sdk && mkdir -p build && cd build && cmake .. && make
```

If PICO_SDK_PATH is not set, just verify the files compile conceptually (no syntax errors visible).

Commit: `"Update CMakeLists.txt and verify C SDK build structure"`
