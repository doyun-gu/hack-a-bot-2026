cmake_minimum_required(VERSION 3.13)

# Set board to Pico 2 (RP2350)
set(PICO_BOARD pico2)

include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(gridbox_master C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable(gridbox_master
    main.c
    bmi160.c
    pca9685.c
    nrf24l01.c
    power_manager.c
)

target_link_libraries(gridbox_master
    pico_stdlib
    hardware_i2c
    hardware_spi
    hardware_adc
    hardware_pwm
    hardware_timer
    pico_multicore
)

# Enable USB serial output (not UART)
pico_enable_stdio_usb(gridbox_master 1)
pico_enable_stdio_uart(gridbox_master 0)

pico_add_extra_outputs(gridbox_master)
