#!/bin/bash
# Flash MicroPython files to Pico via mpremote
# Handles the timer-interrupt timeout issue by soft-resetting first.
#
# Usage: ./flash.sh master   (flash master pico)
#        ./flash.sh slave    (flash slave pico)
#        ./flash.sh test     (upload heartbeat + run nRF debug test)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$(dirname "$SCRIPT_DIR")"

# Upload a single file with retry logic
upload() {
    local src="$1"
    local dst="$2"
    local fname=$(basename "$src")
    echo "  $fname"

    # Try up to 3 times
    for attempt in 1 2 3; do
        if mpremote cp "$src" ":$dst" 2>/dev/null; then
            return 0
        fi
        echo "    retry $attempt..."
        # Soft reset and wait for USB to reconnect
        mpremote soft-reset 2>/dev/null || true
        sleep 2
    done

    echo "  FAILED to upload $fname after 3 attempts"
    return 1
}

flash_master() {
    echo "=== Flashing Master Pico ==="
    echo ""

    # Stop any running code first
    echo "Stopping running code..."
    mpremote soft-reset 2>/dev/null || true
    sleep 2

    echo "Uploading shared protocol..."
    upload "$SRC_DIR/shared/protocol.py" "protocol.py"

    echo "Uploading config..."
    upload "$SRC_DIR/master-pico/micropython/config.py" "config.py"

    echo "Uploading boot..."
    upload "$SRC_DIR/master-pico/micropython/boot.py" "boot.py"

    echo "Uploading drivers..."
    for f in "$SRC_DIR/master-pico/micropython/"*.py; do
        fname=$(basename "$f")
        if [ "$fname" != "main.py" ] && [ "$fname" != "config.py" ] && [ "$fname" != "boot.py" ]; then
            upload "$f" "$fname"
        fi
    done

    # Upload main.py LAST (so boot.py + drivers are ready)
    echo "Uploading main..."
    upload "$SRC_DIR/master-pico/micropython/main.py" "main.py"

    echo ""
    echo "=== Master Pico flashed. Resetting... ==="
    mpremote reset
    echo "Done. LED should start blinking (boot mode)."
}

flash_slave() {
    echo "=== Flashing Slave Pico ==="
    echo ""

    # Stop any running code first
    echo "Stopping running code..."
    mpremote soft-reset 2>/dev/null || true
    sleep 2

    echo "Uploading shared protocol..."
    upload "$SRC_DIR/shared/protocol.py" "protocol.py"

    echo "Uploading config..."
    upload "$SRC_DIR/slave-pico/micropython/config.py" "config.py"

    echo "Uploading boot..."
    upload "$SRC_DIR/slave-pico/micropython/boot.py" "boot.py"

    echo "Uploading drivers..."
    for f in "$SRC_DIR/slave-pico/micropython/"*.py; do
        fname=$(basename "$f")
        if [ "$fname" != "main.py" ] && [ "$fname" != "config.py" ] && [ "$fname" != "boot.py" ]; then
            upload "$f" "$fname"
        fi
    done

    # Upload main.py LAST
    echo "Uploading main..."
    upload "$SRC_DIR/slave-pico/micropython/main.py" "main.py"

    echo ""
    echo "=== Slave Pico flashed. Resetting... ==="
    mpremote reset
    echo "Done. LED should start blinking (boot mode)."
}

flash_test() {
    echo "=== Quick Test: heartbeat + nRF debug ==="
    echo ""

    # Stop any running code first
    echo "Stopping running code..."
    mpremote soft-reset 2>/dev/null || true
    sleep 2

    echo "Uploading heartbeat module..."
    upload "$SRC_DIR/master-pico/micropython/heartbeat.py" "heartbeat.py"

    echo ""
    echo "Running nRF debug test..."
    echo "(LED: fast=testing, slow=PASS, rapid=FAIL)"
    echo ""
    mpremote run "$SRC_DIR/master-pico/tests/test_nrf_debug.py"
}

flash_test_display() {
    echo "=== Quick Test: MAX7219 7-Segment Display ==="
    echo ""

    # Stop any running code first
    echo "Stopping running code..."
    mpremote soft-reset 2>/dev/null || true
    sleep 2

    echo "Uploading heartbeat module..."
    upload "$SRC_DIR/slave-pico/micropython/heartbeat.py" "heartbeat.py"

    echo ""
    echo "Running MAX7219 display test..."
    echo "(Should show 12345678, countdown, brightness sweep)"
    echo ""
    mpremote run "$SRC_DIR/slave-pico/tests/test_max7219.py"
}

case "$1" in
    master)
        flash_master
        ;;
    slave)
        flash_slave
        ;;
    test)
        flash_test
        ;;
    test-display)
        flash_test_display
        ;;
    *)
        echo "Usage: ./flash.sh [master|slave|test|test-display]"
        echo ""
        echo "  master       — Flash all master pico firmware"
        echo "  slave        — Flash all slave pico firmware"
        echo "  test         — Upload heartbeat + run nRF debug test"
        echo "  test-display — Upload heartbeat + run MAX7219 display test"
        exit 1
        ;;
esac
