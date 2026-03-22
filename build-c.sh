#!/bin/bash
# Build C SDK firmware for GridBox
#
# Usage: ./build-c.sh test_hw          (build nRF + MAX7219 + LED test)
#        ./build-c.sh slave            (build production slave firmware)
#        ./build-c.sh test_hw flash    (build + flash to Pico in BOOTSEL)
#        ./build-c.sh test_hw clean    (clean rebuild from scratch)

set -e

cd "$(dirname "$0")"
PROJECT_ROOT="$(pwd)"

# ============ Environment ============
export PICO_SDK_PATH="$HOME/Developer/pico-sdk"
export PATH="/Applications/ArmGNUToolchain/13.3.rel1/arm-none-eabi/bin:$PATH"

if [ ! -d "$PICO_SDK_PATH" ]; then
    echo "ERROR: Pico SDK not found at $PICO_SDK_PATH"
    echo "Install: cd ~/Developer && git clone --branch 2.1.0 https://github.com/raspberrypi/pico-sdk.git"
    exit 1
fi

if ! command -v arm-none-eabi-gcc &>/dev/null; then
    echo "ERROR: ARM toolchain not found"
    echo "Expected at: /Applications/ArmGNUToolchain/13.3.rel1/arm-none-eabi/bin/"
    exit 1
fi

# ============ Parse args ============
TARGET="$1"
ACTION="$2"

SRC_DIR="$PROJECT_ROOT/src/slave-pico/c_sdk"
BUILD_DIR="$SRC_DIR/build"

case "$TARGET" in
    test_hw)
        UF2_NAME="test_hw.uf2"
        MAKE_TARGET="test_hw"
        echo "=== Building: test_hw (nRF + MAX7219 + Heartbeat LED) ==="
        ;;
    slave|gridbox_slave)
        UF2_NAME="gridbox_slave.uf2"
        MAKE_TARGET="gridbox_slave"
        echo "=== Building: gridbox_slave (production firmware) ==="
        ;;
    *)
        echo "Usage: ./build-c.sh <target> [clean|flash]"
        echo ""
        echo "  Targets:"
        echo "    test_hw          — nRF + MAX7219 + heartbeat LED test"
        echo "    slave            — Production slave firmware"
        echo ""
        echo "  Options:"
        echo "    clean            — Delete build/ and rebuild from scratch"
        echo "    flash            — Build + copy .uf2 to Pico in BOOTSEL mode"
        echo ""
        echo "  Examples:"
        echo "    ./build-c.sh test_hw              # just build"
        echo "    ./build-c.sh test_hw clean        # fresh rebuild"
        echo "    ./build-c.sh test_hw flash        # build + flash"
        echo "    ./build-c.sh slave clean flash    # fresh + flash"
        exit 1
        ;;
esac

# ============ Clean if requested ============
DO_FLASH=false
for arg in "$@"; do
    if [ "$arg" = "clean" ]; then
        echo "Cleaning build directory..."
        rm -rf "$BUILD_DIR"
    fi
    if [ "$arg" = "flash" ]; then
        DO_FLASH=true
    fi
done

# ============ Build ============
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

echo "Configuring (Pico 2 / RP2350)..."
cmake .. 2>&1 | tail -3

CORES=$(sysctl -n hw.ncpu 2>/dev/null || echo 4)
echo "Compiling ($CORES cores)..."
make -j"$CORES" "$MAKE_TARGET" 2>&1 | tail -15

if [ -f "$UF2_NAME" ]; then
    SIZE=$(stat -f%z "$UF2_NAME" 2>/dev/null || stat -c%s "$UF2_NAME" 2>/dev/null)
    echo ""
    echo "=== BUILD SUCCESS ==="
    echo "  Binary: src/slave-pico/c_sdk/build/$UF2_NAME"
    echo "  Size:   $SIZE bytes"

    if $DO_FLASH; then
        echo ""
        if [ -d "/Volumes/RP2350" ]; then
            echo "Flashing to Pico 2..."
            cp "$UF2_NAME" /Volumes/RP2350/
            echo "Done! Pico will reboot and run $MAKE_TARGET."
        elif [ -d "/Volumes/RPI-RP2" ]; then
            echo "Flashing to Pico (RP2040)..."
            cp "$UF2_NAME" /Volumes/RPI-RP2/
            echo "Done! Pico will reboot and run $MAKE_TARGET."
        else
            echo "ERROR: No Pico in BOOTSEL mode found."
            echo "Hold BOOTSEL, plug USB, then run: ./build-c.sh $TARGET flash"
        fi
    else
        echo ""
        echo "To flash: hold BOOTSEL + plug in Pico, then:"
        echo "  ./build-c.sh $TARGET flash"
        echo "Or manually: cp $BUILD_DIR/$UF2_NAME /Volumes/RP2350/"
    fi
else
    echo ""
    echo "=== BUILD FAILED ==="
    echo "Check errors above."
    exit 1
fi
