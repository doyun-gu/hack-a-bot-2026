#!/bin/bash
# GridBox — One-command demo launcher
# Usage:
#   ./demo.sh          → live mock data (runs forever)
#   ./demo.sh full     → scripted 3-min demo sequence (startup → faults → recovery → comparison)
#   ./demo.sh fault    → random fault injection mode

set -e

cd "$(dirname "$0")/src/web"

MODE="${1:-live}"

cleanup() {
    echo ""
    echo "[DEMO] Shutting down..."
    kill $FLASK_PID 2>/dev/null
    exit 0
}
trap cleanup INT TERM

# Start Flask dashboard with mock data
if [ "$MODE" = "full" ] || [ "$MODE" = "fault" ]; then
    # For full/fault demo: start server without mock, use external mock-data.py
    python3 app.py --no-serial --web-port 8080 &
    FLASK_PID=$!
    sleep 1

    echo "============================================"
    echo "  GridBox Dashboard: http://localhost:8080"
    echo "  Mode: $MODE"
    echo "============================================"
    echo ""

    cd "$(dirname "$0")/../../src/tools" 2>/dev/null || cd ../tools

    if [ "$MODE" = "full" ]; then
        python3 ../../src/tools/mock-data.py --demo
    else
        python3 ../../src/tools/mock-data.py --fault --duration 300
    fi

    # Keep server running after demo ends
    echo ""
    echo "[DEMO] Demo sequence finished. Dashboard still live. Ctrl+C to stop."
    wait $FLASK_PID
else
    # Live mode: built-in mock generator runs forever
    echo "============================================"
    echo "  GridBox Dashboard: http://localhost:8080"
    echo "  Mode: live (mock data at 5Hz)"
    echo "  Ctrl+C to stop"
    echo "============================================"
    echo ""
    python3 app.py --no-serial --mock --web-port 8080
fi
