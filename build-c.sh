#!/bin/bash
# Build C SDK firmware for Pico 1 (RP2040) or Pico 2 (RP2350)
# Usage: ./build-c.sh pico1       (build for RP2040)
#        ./build-c.sh pico2       (build for RP2350)
#        ./build-c.sh pico1 flash (build + flash to connected Pico)

cd "$(dirname "$0")"
export PICO_SDK_PATH="$HOME/Developer/pico-sdk"

if [ ! -d "$PICO_SDK_PATH" ]; then
    echo "ERROR: Pico SDK not found at $PICO_SDK_PATH"
    echo "Install: cd ~/Developer && git clone --branch 2.1.0 https://github.com/raspberrypi/pico-sdk.git"
    exit 1
fi

case "$1" in
    pico1)
        BOARD="pico"
        echo "=== Building for Pico 1 (RP2040) ==="
        ;;
    pico2)
        BOARD="pico2"
        echo "=== Building for Pico 2 (RP2350) ==="
        ;;
    *)
        echo "Usage: ./build-c.sh [pico1|pico2] [flash]"
        echo ""
        echo "  pico1       Build for Raspberry Pi Pico (RP2040)"
        echo "  pico2       Build for Raspberry Pi Pico 2 (RP2350)"
        echo "  flash       Also flash to connected Pico (hold BOOTSEL + plug in first)"
        exit 1
        ;;
esac

# Build test blink
BUILD_DIR="src/master-pico/c_sdk/build_${BOARD}"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

echo "Configuring for $BOARD..."
cp ../CMakeLists_test.txt ../CMakeLists.txt.bak 2>/dev/null
cmake -DPICO_BOARD="$BOARD" -DCMAKE_BUILD_TYPE=Release .. -G "Unix Makefiles" 2>&1 | tail -5

echo "Compiling..."
make -j$(sysctl -n hw.ncpu) 2>&1 | tail -10

if [ -f "gridbox_test.uf2" ]; then
    SIZE=$(ls -la gridbox_test.uf2 | awk '{print $5}')
    echo ""
    echo "=== BUILD SUCCESS ==="
    echo "  Binary: $BUILD_DIR/gridbox_test.uf2"
    echo "  Size:   $SIZE bytes"
    echo "  Board:  $BOARD"

    if [ "$2" = "flash" ]; then
        echo ""
        echo "Flashing..."
        if [ -d "/Volumes/RPI-RP2" ]; then
            cp gridbox_test.uf2 /Volumes/RPI-RP2/
            echo "Flashed to Pico 1 (RPI-RP2)"
        elif [ -d "/Volumes/RP2350" ]; then
            cp gridbox_test.uf2 /Volumes/RP2350/
            echo "Flashed to Pico 2 (RP2350)"
        else
            echo "ERROR: No Pico in BOOTSEL mode found"
            echo "Hold BOOTSEL, plug USB, release, then run again with 'flash'"
        fi
    else
        echo ""
        echo "To flash: hold BOOTSEL + plug in Pico, then:"
        echo "  ./build-c.sh $1 flash"
    fi
else
    echo ""
    echo "=== BUILD FAILED ==="
    echo "Check errors above"
fi
