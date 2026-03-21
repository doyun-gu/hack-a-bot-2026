#!/bin/bash
# Setup Raspberry Pi Pico 1 (RP2040) with MicroPython
# Usage: ./src/tools/setup-pico1.sh

cd "$(dirname "$0")"
UF2="/tmp/micropython-pico1.uf2"

echo "=== Install MicroPython on Pico 1 (RP2040) ==="
echo ""
echo "Hold BOOTSEL, plug USB, release BOOTSEL"
echo ""
read -p "Press Enter when RPI-RP2 drive appears..."

if [ ! -d "/Volumes/RPI-RP2" ]; then
    echo "ERROR: /Volumes/RPI-RP2 not found"
    exit 1
fi

echo "Found RPI-RP2!"

if [ ! -f "$UF2" ]; then
    echo "Downloading MicroPython for Pico 1..."
    curl -L -o "$UF2" "https://micropython.org/resources/firmware/RPI_PICO-20241025-v1.24.0.uf2"
fi

echo "Flashing..."
cp "$UF2" /Volumes/RPI-RP2/
echo "Done! Wait 5 seconds..."
sleep 5

echo "Testing connection..."
mpremote run ../../master-pico/tests/test_led_blink.py
