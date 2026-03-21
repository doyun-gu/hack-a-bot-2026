#!/bin/bash
# Flash MicroPython files to Pico via mpremote
# Usage: ./flash.sh master   (flash master pico)
#        ./flash.sh slave    (flash slave pico)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$(dirname "$SCRIPT_DIR")"

if [ "$1" = "master" ]; then
    echo "=== Flashing Master Pico ==="
    echo "Uploading shared protocol..."
    mpremote cp "$SRC_DIR/shared/protocol.py" :protocol.py
    echo "Uploading config..."
    mpremote cp "$SRC_DIR/master-pico/micropython/config.py" :config.py
    echo "Uploading main..."
    mpremote cp "$SRC_DIR/master-pico/micropython/main.py" :main.py
    echo "Uploading drivers..."
    for f in "$SRC_DIR/master-pico/micropython/"*.py; do
        fname=$(basename "$f")
        if [ "$fname" != "main.py" ] && [ "$fname" != "config.py" ]; then
            echo "  $fname"
            mpremote cp "$f" ":$fname"
        fi
    done
    echo "=== Master Pico flashed. Resetting... ==="
    mpremote reset

elif [ "$1" = "slave" ]; then
    echo "=== Flashing Slave Pico ==="
    echo "Uploading shared protocol..."
    mpremote cp "$SRC_DIR/shared/protocol.py" :protocol.py
    echo "Uploading config..."
    mpremote cp "$SRC_DIR/slave-pico/micropython/config.py" :config.py
    echo "Uploading main..."
    mpremote cp "$SRC_DIR/slave-pico/micropython/main.py" :main.py
    echo "Uploading drivers..."
    for f in "$SRC_DIR/slave-pico/micropython/"*.py; do
        fname=$(basename "$f")
        if [ "$fname" != "main.py" ] && [ "$fname" != "config.py" ]; then
            echo "  $fname"
            mpremote cp "$f" ":$fname"
        fi
    done
    echo "=== Slave Pico flashed. Resetting... ==="
    mpremote reset

else
    echo "Usage: ./flash.sh [master|slave]"
    echo ""
    echo "  master  — Flash master pico (sensors + processing)"
    echo "  slave   — Flash slave pico (display + base station)"
    exit 1
fi
