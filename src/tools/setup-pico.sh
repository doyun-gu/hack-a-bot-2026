#!/bin/bash
# Setup a Raspberry Pi Pico 2 with MicroPython + GridBox firmware
# Usage: ./setup-pico.sh master    (setup master Pico A)
#        ./setup-pico.sh slave     (setup slave Pico B)
#        ./setup-pico.sh install   (just install MicroPython firmware)

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$(dirname "$SCRIPT_DIR")"
UF2_URL="https://micropython.org/resources/firmware/RPI_PICO2-20241025-v1.24.0.uf2"
UF2_FILE="/tmp/micropython-pico2.uf2"

case "$1" in
    install)
        echo "=== Install MicroPython on Pico 2 ==="
        echo ""
        echo "STEP 1: Hold BOOTSEL button on the Pico"
        echo "STEP 2: Plug USB cable in (while holding BOOTSEL)"
        echo "STEP 3: Release BOOTSEL — Pico appears as USB drive"
        echo ""
        read -p "Press Enter when RPI-RP2 drive appears..."

        # Check if drive mounted
        if [ -d "/Volumes/RPI-RP2" ]; then
            echo "Found RPI-RP2 drive!"
        else
            echo "ERROR: /Volumes/RPI-RP2 not found."
            echo "Make sure you held BOOTSEL while plugging in."
            exit 1
        fi

        # Download firmware if not cached
        if [ ! -f "$UF2_FILE" ]; then
            echo "Downloading MicroPython for Pico 2..."
            curl -L -o "$UF2_FILE" "$UF2_URL"
        else
            echo "Using cached firmware: $UF2_FILE"
        fi

        # Copy to Pico
        echo "Flashing MicroPython..."
        cp "$UF2_FILE" /Volumes/RPI-RP2/
        echo "Done! Pico will reboot with MicroPython."
        echo "Wait 5 seconds for reboot..."
        sleep 5

        # Verify
        if mpremote version 2>/dev/null; then
            echo "Verifying connection..."
            mpremote exec "import sys; print('MicroPython', sys.version)"
            echo "=== MicroPython installed successfully! ==="
        else
            echo "mpremote not responding yet. Unplug and replug USB, then try:"
            echo "  mpremote repl"
        fi
        ;;

    master)
        echo "=== Uploading GridBox Master Firmware (Pico A) ==="

        # Check mpremote
        if ! command -v mpremote &> /dev/null; then
            echo "ERROR: mpremote not installed. Run: pip install mpremote"
            exit 1
        fi

        echo "Uploading shared protocol..."
        mpremote cp "$SRC_DIR/shared/protocol.py" :protocol.py

        echo "Uploading config..."
        mpremote cp "$SRC_DIR/master-pico/micropython/config.py" :config.py

        echo "Uploading drivers and modules..."
        for f in "$SRC_DIR/master-pico/micropython/"*.py; do
            fname=$(basename "$f")
            if [ "$fname" != "main.py" ] && [ "$fname" != "config.py" ]; then
                echo "  $fname"
                mpremote cp "$f" ":$fname"
            fi
        done

        echo "Uploading main.py (last — triggers auto-run on boot)..."
        mpremote cp "$SRC_DIR/master-pico/micropython/main.py" :main.py

        echo "Resetting Pico..."
        mpremote reset

        echo "=== Master Pico A ready! ==="
        echo "To see output: mpremote repl"
        ;;

    slave)
        echo "=== Uploading GridBox Slave Firmware (Pico B) ==="

        if ! command -v mpremote &> /dev/null; then
            echo "ERROR: mpremote not installed. Run: pip install mpremote"
            exit 1
        fi

        echo "Uploading shared protocol..."
        mpremote cp "$SRC_DIR/shared/protocol.py" :protocol.py

        echo "Uploading config..."
        mpremote cp "$SRC_DIR/slave-pico/micropython/config.py" :config.py

        echo "Uploading drivers and modules..."
        for f in "$SRC_DIR/slave-pico/micropython/"*.py; do
            fname=$(basename "$f")
            if [ "$fname" != "main.py" ] && [ "$fname" != "config.py" ]; then
                echo "  $fname"
                mpremote cp "$f" ":$fname"
            fi
        done

        echo "Uploading main.py..."
        mpremote cp "$SRC_DIR/slave-pico/micropython/main.py" :main.py

        echo "Resetting Pico..."
        mpremote reset

        echo "=== Slave Pico B ready! ==="
        echo "To see output: mpremote repl"
        ;;

    test)
        echo "=== Run a test on connected Pico ==="
        if [ -z "$2" ]; then
            echo "Usage: ./setup-pico.sh test <test_file>"
            echo ""
            echo "Available tests:"
            ls "$SRC_DIR/master-pico/tests/"*.py 2>/dev/null | while read f; do
                echo "  master: $(basename $f)"
            done
            ls "$SRC_DIR/slave-pico/tests/"*.py 2>/dev/null | while read f; do
                echo "  slave:  $(basename $f)"
            done
            exit 1
        fi

        # Find the test file
        TEST_FILE=""
        if [ -f "$SRC_DIR/master-pico/tests/$2" ]; then
            TEST_FILE="$SRC_DIR/master-pico/tests/$2"
        elif [ -f "$SRC_DIR/slave-pico/tests/$2" ]; then
            TEST_FILE="$SRC_DIR/slave-pico/tests/$2"
        elif [ -f "$2" ]; then
            TEST_FILE="$2"
        else
            echo "ERROR: Test file '$2' not found"
            exit 1
        fi

        echo "Running: $TEST_FILE"
        echo "Press Ctrl+C to stop"
        echo "---"
        mpremote run "$TEST_FILE"
        ;;

    repl)
        echo "=== Opening REPL on connected Pico ==="
        echo "Type Python directly. Press Ctrl+] to exit."
        echo "---"
        mpremote repl
        ;;

    *)
        echo "GridBox Pico Setup Tool"
        echo ""
        echo "Usage: ./setup-pico.sh <command>"
        echo ""
        echo "Commands:"
        echo "  install        Install MicroPython on a new Pico 2 (hold BOOTSEL + plug in first)"
        echo "  master         Upload GridBox master firmware (Pico A — grid controller)"
        echo "  slave          Upload GridBox slave firmware (Pico B — SCADA station)"
        echo "  test <file>    Run a test file on connected Pico"
        echo "  repl           Open interactive Python on connected Pico"
        echo ""
        echo "First time setup:"
        echo "  1. ./setup-pico.sh install     (hold BOOTSEL + plug in)"
        echo "  2. ./setup-pico.sh master      (upload firmware)"
        echo "  3. ./setup-pico.sh repl        (verify it works)"
        echo ""
        echo "Repeat for second Pico with 'slave' instead of 'master'"
        ;;
esac
