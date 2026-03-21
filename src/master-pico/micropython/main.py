"""
NeuroSync — Master Pico (Pico A)
Handles: sensors, input, processing, wireless TX

Role: The primary sensing and processing unit.
Connects to: IMU, joystick, servos (via PCA9685), nRF24L01+ TX, LEDs

This file will be populated once the project idea is finalised.
Currently scaffolded for rapid development start.
"""

from machine import Pin, I2C, SPI, ADC, PWM, Timer
import time
import _thread

# ============ PIN CONFIGURATION ============
# I2C Bus (shared: IMU + PCA9685)
I2C_SDA = 4
I2C_SCL = 5
I2C_FREQ = 400_000

# SPI Bus (nRF24L01+)
SPI_MOSI = 3
SPI_MISO = 4  # Adjust based on final wiring
SPI_SCK = 2
NRF_CSN = 1
NRF_CE = 0

# ADC (Joystick)
JOY_X = 26
JOY_Y = 27
JOY_BTN = 22  # Digital button

# LEDs
LED_GREEN = 15
LED_RED = 14

# ============ INITIALISATION ============
def init_hardware():
    """Initialise all hardware peripherals."""
    print("[MASTER] Initialising hardware...")

    # I2C
    i2c = I2C(0, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=I2C_FREQ)
    devices = i2c.scan()
    print(f"[MASTER] I2C devices found: {[hex(d) for d in devices]}")

    # SPI
    spi = SPI(0, baudrate=10_000_000, polarity=0, phase=0,
              sck=Pin(SPI_SCK), mosi=Pin(SPI_MOSI), miso=Pin(SPI_MISO))

    # ADC
    joy_x = ADC(Pin(JOY_X))
    joy_y = ADC(Pin(JOY_Y))
    joy_btn = Pin(JOY_BTN, Pin.IN, Pin.PULL_UP)

    # LEDs
    led_green = Pin(LED_GREEN, Pin.OUT)
    led_red = Pin(LED_RED, Pin.OUT)

    print("[MASTER] Hardware initialised OK")
    return i2c, spi, joy_x, joy_y, joy_btn, led_green, led_red


def main():
    """Main entry point."""
    print("=" * 40)
    print("  NeuroSync — Master Pico")
    print("  Waiting for project config...")
    print("=" * 40)

    i2c, spi, joy_x, joy_y, joy_btn, led_g, led_r = init_hardware()

    # Blink green LED to show we're alive
    while True:
        led_g.toggle()
        # Print joystick values for testing
        print(f"[MASTER] Joy X={joy_x.read_u16()}, Y={joy_y.read_u16()}, Btn={joy_btn.value()}")
        time.sleep(0.5)


if __name__ == "__main__":
    main()
