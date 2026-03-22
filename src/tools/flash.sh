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

flash_test_wireless_master() {
    echo "=== Wireless Test: MASTER (Pico A) — sends PING ==="
    echo ""

    echo "Stopping running code..."
    mpremote soft-reset 2>/dev/null || true
    sleep 2

    echo "Uploading modules..."
    upload "$SRC_DIR/shared/protocol.py" "protocol.py"
    upload "$SRC_DIR/master-pico/micropython/heartbeat.py" "heartbeat.py"
    upload "$SRC_DIR/master-pico/micropython/config.py" "config.py"
    upload "$SRC_DIR/master-pico/micropython/nrf24l01.py" "nrf24l01.py"

    echo ""
    echo "Running wireless test (MASTER = PING sender)..."
    echo "Plug in Pico B with test-wireless-slave to complete the test."
    echo ""
    mpremote run "$SRC_DIR/master-pico/tests/test_wireless.py"
}

flash_test_wireless_slave() {
    echo "=== Wireless Test: SLAVE (Pico B) — replies PONG ==="
    echo ""

    echo "Stopping running code..."
    mpremote soft-reset 2>/dev/null || true
    sleep 2

    echo "Uploading modules..."
    upload "$SRC_DIR/shared/protocol.py" "protocol.py"
    upload "$SRC_DIR/slave-pico/micropython/heartbeat.py" "heartbeat.py"
    upload "$SRC_DIR/slave-pico/micropython/config.py" "config.py"
    upload "$SRC_DIR/slave-pico/micropython/nrf24l01.py" "nrf24l01.py"

    echo ""
    echo "Running wireless test (SLAVE = PONG responder)..."
    echo "Plug in Pico A with test-wireless-master to complete the test."
    echo ""
    mpremote run "$SRC_DIR/slave-pico/tests/test_wireless.py"
}

# ---- Persistent flash: saves test as main.py (runs on boot without USB) ----

flash_persist_master() {
    echo "=== Persist: MASTER datagram test (runs on boot) ==="
    echo ""

    echo "Stopping running code..."
    mpremote soft-reset 2>/dev/null || true
    sleep 2

    echo "Uploading modules..."
    upload "$SRC_DIR/shared/protocol.py" "protocol.py"
    upload "$SRC_DIR/master-pico/micropython/heartbeat.py" "heartbeat.py"
    upload "$SRC_DIR/master-pico/micropython/config.py" "config.py"
    upload "$SRC_DIR/master-pico/micropython/nrf24l01.py" "nrf24l01.py"

    echo "Uploading test as main.py (will run on every boot)..."
    upload "$SRC_DIR/master-pico/tests/test_datagram_master.py" "main.py"

    echo ""
    echo "=== Running pre-flight nRF check... ==="
    mpremote run "$SRC_DIR/master-pico/tests/test_nrf_debug.py"
    echo ""
    echo "If nRF PASS above → safe to unplug and power from external 5V."
    echo "The datagram test will auto-start on boot."
    echo ""
    echo "=== Resetting to start test... ==="
    mpremote reset
}

flash_persist_slave() {
    echo "=== Persist: SLAVE datagram test (runs on boot) ==="
    echo ""

    echo "Stopping running code..."
    mpremote soft-reset 2>/dev/null || true
    sleep 2

    echo "Uploading modules..."
    upload "$SRC_DIR/shared/protocol.py" "protocol.py"
    upload "$SRC_DIR/slave-pico/micropython/heartbeat.py" "heartbeat.py"
    upload "$SRC_DIR/slave-pico/micropython/config.py" "config.py"
    upload "$SRC_DIR/slave-pico/micropython/nrf24l01.py" "nrf24l01.py"

    echo "Uploading test as main.py (will run on every boot)..."
    upload "$SRC_DIR/slave-pico/tests/test_datagram_slave.py" "main.py"

    echo ""
    echo "=== Running pre-flight nRF check... ==="
    # Same pinout on both Picos — master nRF debug test works for slave too
    mpremote run "$SRC_DIR/master-pico/tests/test_nrf_debug.py"
    echo ""
    echo "If nRF PASS above → safe to unplug and power from external 5V."
    echo "The datagram test will auto-start on boot."
    echo ""
    echo "=== Resetting to start test... ==="
    mpremote reset
}

# ---- Datagram protocol test (run via mpremote, needs USB) ----

flash_test_datagram_master() {
    echo "=== Datagram Test: MASTER (Pico A) — sends all 6 types ==="
    echo ""

    echo "Stopping running code..."
    mpremote soft-reset 2>/dev/null || true
    sleep 2

    echo "Uploading modules..."
    upload "$SRC_DIR/shared/protocol.py" "protocol.py"
    upload "$SRC_DIR/master-pico/micropython/heartbeat.py" "heartbeat.py"
    upload "$SRC_DIR/master-pico/micropython/config.py" "config.py"
    upload "$SRC_DIR/master-pico/micropython/nrf24l01.py" "nrf24l01.py"

    echo ""
    echo "Running datagram test (MASTER = sends all packet types)..."
    echo "Pair with: test-datagram-slave on Pico B"
    echo ""
    mpremote run "$SRC_DIR/master-pico/tests/test_datagram_master.py"
}

flash_test_datagram_slave() {
    echo "=== Datagram Test: SLAVE (Pico B) — receives + displays ==="
    echo ""

    echo "Stopping running code..."
    mpremote soft-reset 2>/dev/null || true
    sleep 2

    echo "Uploading modules..."
    upload "$SRC_DIR/shared/protocol.py" "protocol.py"
    upload "$SRC_DIR/slave-pico/micropython/heartbeat.py" "heartbeat.py"
    upload "$SRC_DIR/slave-pico/micropython/config.py" "config.py"
    upload "$SRC_DIR/slave-pico/micropython/nrf24l01.py" "nrf24l01.py"

    echo ""
    echo "Running datagram test (SLAVE = receive + display all types)..."
    echo "Pair with: test-datagram-master on Pico A"
    echo ""
    mpremote run "$SRC_DIR/slave-pico/tests/test_datagram_slave.py"
}

flash_test_nrf_display() {
    echo "=== Quick Test: nRF + MAX7219 Display ==="
    echo ""

    # Stop any running code first
    echo "Stopping running code..."
    mpremote soft-reset 2>/dev/null || true
    sleep 2

    echo "Uploading modules..."
    upload "$SRC_DIR/slave-pico/micropython/heartbeat.py" "heartbeat.py"
    upload "$SRC_DIR/slave-pico/micropython/seg_display.py" "seg_display.py"

    echo ""
    echo "Running nRF test with display..."
    echo "(Display: BOOT → tESt → LINK On/OFF → PASS/FAIL)"
    echo ""
    mpremote run "$SRC_DIR/slave-pico/tests/test_nrf_with_display.py"
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
    test-nrf-display)
        flash_test_nrf_display
        ;;
    test-wireless-master)
        flash_test_wireless_master
        ;;
    test-wireless-slave)
        flash_test_wireless_slave
        ;;
    persist-master)
        flash_persist_master
        ;;
    persist-slave)
        flash_persist_slave
        ;;
    test-datagram-master)
        flash_test_datagram_master
        ;;
    test-datagram-slave)
        flash_test_datagram_slave
        ;;
    *)
        echo "Usage: ./flash.sh <command>"
        echo ""
        echo "  Flash firmware:"
        echo "    master                — Flash all master pico firmware"
        echo "    slave                 — Flash all slave pico firmware"
        echo ""
        echo "  Single-Pico tests:"
        echo "    test                  — nRF SPI debug (master pinout)"
        echo "    test-display          — MAX7219 display test"
        echo "    test-nrf-display      — nRF + display combined test"
        echo ""
        echo "  Two-Pico wireless tests (both need USB):"
        echo "    test-wireless-master  — PING sender (Pico A)"
        echo "    test-wireless-slave   — PONG responder (Pico B)"
        echo ""
        echo "  Datagram protocol tests (both need USB):"
        echo "    test-datagram-master  — Send all 6 packet types (Pico A)"
        echo "    test-datagram-slave   — Receive + display + send COMMAND (Pico B)"
        echo ""
        echo "  Persist mode (saves as main.py — runs on boot WITHOUT USB):"
        echo "    persist-master        — Flash master datagram test + pre-flight check"
        echo "    persist-slave         — Flash slave datagram test + pre-flight check"
        exit 1
        ;;
esac
