"""
GridBox — Web Dashboard
Live monitoring + persistent SQLite storage.

Reads JSON serial from Pico, stores in SQLite, serves web UI.

Usage:
    python app.py --port /dev/tty.usbmodem*    (with Pico)
    python app.py --no-serial                  (test mode)
    python app.py --no-serial --mock           (auto mock data)

Then open http://localhost:8080
"""

import argparse
import json
import threading
import time
from datetime import datetime
from collections import deque

from flask import Flask, render_template, jsonify, request
from database import init_db, insert_reading, insert_fault, start_session, \
    end_session, get_recent_readings, get_recent_faults, get_sessions, get_stats

app = Flask(__name__)

# In-memory buffer for real-time display (last 1000 readings)
data_buffer = deque(maxlen=1000)
latest_data = {}
current_session_id = None
prev_state = 'UNKNOWN'
_mock_thread = None
_mock_running = False


def _ingest_data(data):
    """Store a data dict into the buffer and database."""
    global latest_data, prev_state
    if 'timestamp' not in data:
        data['timestamp'] = datetime.now().isoformat()
    latest_data = data
    data_buffer.append(data)
    insert_reading(data)

    state = data.get('state', 'UNKNOWN')
    if state in ('FAULT', 'EMERGENCY') and prev_state not in ('FAULT', 'EMERGENCY'):
        insert_fault(
            fault_type=state,
            source=data.get('imu_status', 'unknown'),
            imu_rms=data.get('imu_rms'),
            motor_current=data.get('m1_mA'),
            bus_voltage=data.get('bus_v'),
            action_taken='auto_logged'
        )
    prev_state = state


def _mock_generator():
    """Background thread that generates mock data at 5Hz."""
    import math
    import random
    global _mock_running
    t = 0.0
    while _mock_running:
        data = {
            "bus_v": 4.9 + random.gauss(0, 0.05),
            "m1_mA": 350 + random.gauss(0, 15) + 50 * math.sin(t * 0.1),
            "m2_mA": 280 + random.gauss(0, 10) + 30 * math.sin(t * 0.15),
            "m1_W": 0, "m2_W": 0, "total_W": 0,
            "efficiency": 82 + random.gauss(0, 3),
            "state": "NORMAL",
            "imu_rms": 0.3 + random.gauss(0, 0.05),
            "imu_status": "HEALTHY",
            "es_score": 0.05 + random.gauss(0, 0.02),
            "m1_speed": 65 + int(10 * math.sin(t * 0.1)),
            "m2_speed": 45 + int(5 * math.sin(t * 0.15)),
            "mode": 1,
            "total_items": int(t / 5),
            "passed": int(t / 5 * 0.87),
            "rejected": int(t / 5 * 0.13),
            "reject_rate": 13.0 + random.gauss(0, 2),
            "faults_today": 0,
        }
        bus_v = data["bus_v"]
        data["m1_W"] = round(bus_v * data["m1_mA"] / 1000, 2)
        data["m2_W"] = round(bus_v * data["m2_mA"] / 1000, 2)
        data["total_W"] = round(data["m1_W"] + data["m2_W"] + 0.5, 2)
        _ingest_data(data)
        t += 0.2
        time.sleep(0.2)


def _start_mock():
    """Start mock data generation in a background thread."""
    global _mock_thread, _mock_running
    if _mock_running:
        return False
    _mock_running = True
    _mock_thread = threading.Thread(target=_mock_generator, daemon=True)
    _mock_thread.start()
    return True


def _stop_mock():
    """Stop mock data generation."""
    global _mock_running
    if not _mock_running:
        return False
    _mock_running = False
    return True


def serial_reader(port, baud=115200):
    """Read serial data from Pico in a background thread."""
    global latest_data, prev_state
    import serial

    try:
        ser = serial.Serial(port, baud, timeout=1)
        print(f"[SERIAL] Connected to {port} at {baud} baud")

        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                if line.startswith('{'):
                    try:
                        data = json.loads(line)
                        _ingest_data(data)
                    except json.JSONDecodeError:
                        pass
                else:
                    print(f"[PICO] {line}")

    except Exception as e:
        print(f"[SERIAL] Error: {e}")
        print(f"[SERIAL] Make sure Pico is connected and port is correct")


# ============ PAGE ROUTES ============

@app.route('/')
def index():
    return render_template('index.html')


# ============ REAL-TIME API ============

@app.route('/api/latest')
def api_latest():
    return jsonify(latest_data)


@app.route('/api/history')
def api_history():
    """Last 60 seconds from memory buffer (fast)."""
    return jsonify(list(data_buffer)[-300:])


@app.route('/api/status')
def api_status():
    if latest_data:
        ts = latest_data.get('timestamp', datetime.now().isoformat())
        age = (datetime.now() - datetime.fromisoformat(ts)).total_seconds()
        return jsonify({
            'connected': age < 5,
            'age_seconds': round(age, 1),
            'readings': len(data_buffer),
            'state': latest_data.get('state', 'UNKNOWN'),
            'session_id': current_session_id,
        })
    return jsonify({'connected': False, 'readings': 0, 'state': 'DISCONNECTED'})


# ============ MOCK DATA API ============

@app.route('/api/inject', methods=['POST'])
def api_inject():
    """Accept JSON data and store as latest reading."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'invalid JSON'}), 400
    _ingest_data(data)
    return jsonify({'ok': True})


@app.route('/api/mock/start', methods=['POST'])
def api_mock_start():
    """Start internal mock data generation."""
    started = _start_mock()
    if started:
        print("[MOCK] Mock data generation started")
        return jsonify({'ok': True, 'status': 'started'})
    return jsonify({'ok': False, 'status': 'already_running'})


@app.route('/api/mock/stop', methods=['POST'])
def api_mock_stop():
    """Stop internal mock data generation."""
    stopped = _stop_mock()
    if stopped:
        print("[MOCK] Mock data generation stopped")
        return jsonify({'ok': True, 'status': 'stopped'})
    return jsonify({'ok': False, 'status': 'not_running'})


# ============ DATABASE API ============

@app.route('/api/db/stats')
def api_db_stats():
    """Overall database statistics."""
    return jsonify(get_stats())


@app.route('/api/db/readings')
def api_db_readings():
    """Historical readings from database."""
    limit = request.args.get('limit', 300, type=int)
    return jsonify(get_recent_readings(min(limit, 5000)))


@app.route('/api/db/faults')
def api_db_faults():
    """Fault event log from database."""
    limit = request.args.get('limit', 50, type=int)
    return jsonify(get_recent_faults(min(limit, 200)))


@app.route('/api/db/sessions')
def api_db_sessions():
    """Session history with summaries."""
    limit = request.args.get('limit', 10, type=int)
    return jsonify(get_sessions(min(limit, 50)))


# ============ MAIN ============

def main():
    global current_session_id

    parser = argparse.ArgumentParser(description='GridBox Web Dashboard')
    parser.add_argument('--port', default='/dev/tty.usbmodem*',
                        help='Serial port for Pico USB')
    parser.add_argument('--baud', type=int, default=115200,
                        help='Baud rate')
    parser.add_argument('--web-port', type=int, default=8080,
                        help='Web server port')
    parser.add_argument('--no-serial', action='store_true',
                        help='Run web server without serial connection')
    parser.add_argument('--mock', action='store_true',
                        help='Auto-start mock data generation (use with --no-serial)')
    args = parser.parse_args()

    # Initialise database
    init_db()

    # Start session
    current_session_id = start_session()
    print(f"[DB] Session {current_session_id} started")

    if not args.no_serial:
        import glob
        ports = glob.glob(args.port)
        if ports:
            port = ports[0]
            print(f"[SERIAL] Starting serial reader on {port}")
            thread = threading.Thread(target=serial_reader, args=(port, args.baud), daemon=True)
            thread.start()
        else:
            print(f"[WEB] No serial port found matching '{args.port}'")
            print("[WEB] Running without serial — use --no-serial to suppress this")
    else:
        print("[WEB] Running without serial (test mode)")

    if args.mock:
        _start_mock()
        print("[MOCK] Auto-started mock data generation (5Hz)")

    print(f"[WEB] GridBox Dashboard at http://localhost:{args.web_port}")
    print(f"[WEB] Database API at http://localhost:{args.web_port}/api/db/stats")

    try:
        app.run(host='0.0.0.0', port=args.web_port, debug=False)
    finally:
        if current_session_id:
            end_session(current_session_id)
            print(f"[DB] Session {current_session_id} ended")


if __name__ == '__main__':
    main()
