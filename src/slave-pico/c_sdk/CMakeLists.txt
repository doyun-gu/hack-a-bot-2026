cmake_minimum_required(VERSION 3.13)

# Set board to Pico 2 (RP2350)
set(PICO_BOARD pico2)

include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(gridbox_slave C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable(gridbox_slave
    main.c
    ssd1306.c
    nrf24l01.c
)

target_link_libraries(gridbox_slave
    pico_stdlib
    hardware_i2c
    hardware_spi
    hardware_adc
    hardware_timer
)

# Enable USB serial output (not UART)
pico_enable_stdio_usb(gridbox_slave 1)
pico_enable_stdio_uart(gridbox_slave 0)

pico_add_extra_outputs(gridbox_slave)

# ---- Test: nRF + MAX7219 + Heartbeat LED ----
add_executable(test_hw
    test_hw.c
    max7219.c
)

target_link_libraries(test_hw
    pico_stdlib
    hardware_spi
    hardware_gpio
    hardware_timer
)

pico_enable_stdio_usb(test_hw 1)
pico_enable_stdio_uart(test_hw 0)

pico_add_extra_outputs(test_hw)
