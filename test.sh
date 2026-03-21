#!/bin/bash
# GridBox Test Runner — one command for all tests
# Usage: ./test.sh [test_name]

cd "$(dirname "$0")"

case "$1" in
    led)
        echo "=== LED Blink Test ==="
        mpremote run src/master-pico/tests/test_led_blink.py
        ;;
    alive)
        echo "=== Alive Check (LED + temp + imports) ==="
        mpremote run src/master-pico/tests/test_basic_alive.py
        ;;
    i2c)
        echo "=== I2C Bus Scan ==="
        mpremote run src/master-pico/tests/test_i2c_scan.py
        ;;
    adc)
        echo "=== ADC Reading (GP26 + GP27) ==="
        mpremote run src/master-pico/tests/test_adc_partial.py
        ;;
    imu)
        echo "=== IMU Vibration Test ==="
        mpremote run src/master-pico/tests/test_imu.py
        ;;
    servo)
        echo "=== MG90D Servo Control (calibrated) ==="
        mpremote run src/master-pico/tests/test_servo_control.py
        ;;
    servo-find)
        echo "=== Find Servo Stop Point ==="
        mpremote run src/master-pico/tests/test_servo_findstop.py
        ;;
    servo-90)
        echo "=== Servo Single 90° Turn ==="
        mpremote run src/master-pico/tests/test_servo_single90.py
        ;;
    motor)
        echo "=== Motor Speed Test ==="
        mpremote run src/master-pico/tests/test_motor.py
        ;;
    oled)
        echo "=== OLED Display Test ==="
        mpremote cp src/slave-pico/micropython/ssd1306.py :ssd1306.py
        mpremote cp src/slave-pico/micropython/config.py :config.py
        mpremote run src/slave-pico/tests/test_oled.py
        ;;
    oled-live)
        echo "=== OLED Live Monitor (DIM + spinner) ==="
        mpremote cp src/slave-pico/micropython/ssd1306.py :ssd1306.py
        mpremote cp src/slave-pico/micropython/config.py :config.py
        mpremote run src/slave-pico/tests/test_oled_live.py
        ;;
    oled-modes)
        echo "=== OLED Display Modes (pick your favourite) ==="
        mpremote cp src/slave-pico/micropython/ssd1306.py :ssd1306.py
        mpremote cp src/slave-pico/micropython/config.py :config.py
        mpremote run src/slave-pico/tests/test_oled_modes.py
        ;;
    wireless)
        echo "=== Wireless Ping-Pong (master side) ==="
        mpremote cp src/master-pico/micropython/nrf24l01.py :nrf24l01.py
        mpremote cp src/master-pico/micropython/config.py :config.py
        mpremote run src/master-pico/tests/test_wireless.py
        ;;
    joystick)
        echo "=== Joystick Test ==="
        mpremote run src/master-pico/tests/test_joystick.py
        ;;
    dashboard)
        echo "=== Live Dashboard (Pico → Web) ==="
        mpremote run src/master-pico/tests/test_live_dashboard.py
        ;;
    web)
        echo "=== Start Web Dashboard (mock data) ==="
        pkill -f "app.py" 2>/dev/null
        sleep 1
        echo "Open http://localhost:8080"
        python3 src/web/app.py --no-serial --mock
        ;;
    web-live)
        echo "=== Start Web Dashboard (real Pico data) ==="
        pkill -f "app.py" 2>/dev/null
        sleep 1
        echo "Open http://localhost:8080"
        python3 src/web/app.py --port /dev/tty.usbmodem*
        ;;
    flash-master)
        echo "=== Flash Master Firmware (Pico A) ==="
        ./src/tools/flash.sh master
        ;;
    flash-slave)
        echo "=== Flash Slave Firmware (Pico B) ==="
        ./src/tools/flash.sh slave
        ;;
    install)
        echo "=== Install MicroPython on Pico 2 (RP2350) ==="
        ./src/tools/setup-pico.sh install
        ;;
    install1)
        echo "=== Install MicroPython on Pico 1 (RP2040) ==="
        ./src/tools/setup-pico1.sh
        ;;
    repl)
        echo "=== Open REPL on Pico ==="
        mpremote repl
        ;;
    status)
        echo "=== Device Status ==="
        mpremote devs
        ;;
    all)
        echo "=== Running ALL hardware tests ==="
        echo ""
        echo "--- LED ---" && mpremote run src/master-pico/tests/test_led_blink.py
        echo ""
        echo "--- I2C Scan ---" && mpremote run src/master-pico/tests/test_i2c_scan.py
        echo ""
        echo "--- ADC ---" && timeout 5 mpremote run src/master-pico/tests/test_adc_partial.py 2>/dev/null
        echo ""
        echo "=== All tests complete ==="
        ;;
    *)
        echo "GridBox Test Runner"
        echo ""
        echo "Usage: ./test.sh <test>"
        echo ""
        echo "Hardware tests (plug in Pico first):"
        echo "  led          LED blink (no wiring needed)"
        echo "  alive        System alive check"
        echo "  i2c          I2C bus scan (finds IMU, PCA, OLED)"
        echo "  adc          ADC voltage/current reading"
        echo "  imu          IMU vibration test"
        echo "  servo        MG90D servo control (calibrated)"
        echo "  servo-find   Find servo stop point"
        echo "  servo-90     Single 90° turn"
        echo "  motor        Motor speed test"
        echo "  joystick     Joystick reading"
        echo "  wireless     Wireless ping-pong"
        echo "  all          Run all basic tests"
        echo ""
        echo "OLED tests:"
        echo "  oled         Display test (boot + status)"
        echo "  oled-live    Live monitor (DIM + spinner)"
        echo "  oled-modes   Compare display modes"
        echo ""
        echo "Dashboard:"
        echo "  web          Start web dashboard (mock data)"
        echo "  web-live     Start web dashboard (real Pico)"
        echo "  dashboard    Pico sends live data to web"
        echo ""
        echo "Setup:"
        echo "  install      Install MicroPython (Pico 2)"
        echo "  install1     Install MicroPython (Pico 1)"
        echo "  flash-master Flash master firmware"
        echo "  flash-slave  Flash slave firmware"
        echo "  repl         Open Python REPL"
        echo "  status       Show connected devices"
        ;;
esac
