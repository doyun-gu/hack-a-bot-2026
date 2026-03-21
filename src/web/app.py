"""
NeuroSync — Web Dashboard
Live monitoring of Pico sensor data via USB serial.

Reads serial data from master Pico, stores in SQLite, serves a web UI.

Usage:
    python app.py --port /dev/tty.usbmodem*

Then open http://localhost:5000
"""

import argparse
import json
import threading
import time
from datetime import datetime

from flask import Flask, render_template, jsonify

app = Flask(__name__)

# In-memory data buffer (last 1000 readings)
data_buffer = []
MAX_BUFFER = 1000
latest_data = {}


def serial_reader(port, baud=115200):
    """Read serial data from Pico in a background thread."""
    global latest_data
    import serial

    try:
        ser = serial.Serial(port, baud, timeout=1)
        print(f"[SERIAL] Connected to {port} at {baud} baud")

        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                # Try to parse JSON data from Pico
                if line.startswith('{'):
                    try:
                        data = json.loads(line)
                        data['timestamp'] = datetime.now().isoformat()
                        latest_data = data
                        data_buffer.append(data)
                        if len(data_buffer) > MAX_BUFFER:
                            data_buffer.pop(0)
                    except json.JSONDecodeError:
                        pass
                # Also print raw output for debugging
                print(f"[PICO] {line}")

    except Exception as e:
        print(f"[SERIAL] Error: {e}")
        print(f"[SERIAL] Make sure Pico is connected and port is correct")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/latest')
def api_latest():
    return jsonify(latest_data)


@app.route('/api/history')
def api_history():
    return jsonify(data_buffer[-100:])  # last 100 readings


@app.route('/api/status')
def api_status():
    if latest_data:
        age = (datetime.now() - datetime.fromisoformat(latest_data.get('timestamp', datetime.now().isoformat()))).total_seconds()
        return jsonify({
            'connected': age < 5,
            'age_seconds': round(age, 1),
            'readings': len(data_buffer)
        })
    return jsonify({'connected': False, 'readings': 0})


def main():
    parser = argparse.ArgumentParser(description='NeuroSync Web Dashboard')
    parser.add_argument('--port', default='/dev/tty.usbmodem*',
                        help='Serial port for Pico USB')
    parser.add_argument('--baud', type=int, default=115200,
                        help='Baud rate')
    parser.add_argument('--web-port', type=int, default=5000,
                        help='Web server port')
    parser.add_argument('--no-serial', action='store_true',
                        help='Run web server without serial connection (for testing)')
    args = parser.parse_args()

    if not args.no_serial:
        # Resolve glob pattern for port
        import glob
        ports = glob.glob(args.port)
        if ports:
            port = ports[0]
            print(f"[WEB] Starting serial reader on {port}")
            thread = threading.Thread(target=serial_reader, args=(port, args.baud), daemon=True)
            thread.start()
        else:
            print(f"[WEB] No serial port found matching '{args.port}'")
            print("[WEB] Running without serial — use --no-serial to suppress this warning")
    else:
        print("[WEB] Running without serial connection (test mode)")

    print(f"[WEB] Dashboard at http://localhost:{args.web_port}")
    app.run(host='0.0.0.0', port=args.web_port, debug=False)


if __name__ == '__main__':
    main()
