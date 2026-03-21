cmake_minimum_required(VERSION 3.13)

# Set board to Pico 2 (RP2350)
set(PICO_BOARD pico2)

include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(neurosync_master C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable(neurosync_master
    main.c
    # Add driver files here as they're created:
    # bmi160.c
    # nrf24l01.c
    # pca9685.c
    # tremor_analysis.c
    # pid_controller.c
)

target_link_libraries(neurosync_master
    pico_stdlib
    hardware_i2c
    hardware_spi
    hardware_adc
    hardware_pwm
    hardware_timer
    pico_multicore
)

# Enable USB serial output (not UART)
pico_enable_stdio_usb(neurosync_master 1)
pico_enable_stdio_uart(neurosync_master 0)

pico_add_extra_outputs(neurosync_master)
