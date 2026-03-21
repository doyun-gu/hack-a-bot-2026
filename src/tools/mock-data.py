"""
GridBox — Mock Data Generator
Generates fake sensor data and feeds it to the web dashboard.
Use this to test/demo the dashboard without a real Pico.

Usage:
    # Terminal 1: Start dashboard
    python src/web/app.py --no-serial

    # Terminal 2: Feed mock data
    python src/tools/mock-data.py

    # Open http://localhost:8080 — live data appears!

Modes:
    python src/tools/mock-data.py                  # normal operation
    python src/tools/mock-data.py --fault           # simulate faults
    python src/tools/mock-data.py --demo            # full demo sequence (3 min)
"""

import json
import time
import math
import random
import argparse
import urllib.request

DASHBOARD_URL = "http://localhost:8080/api/latest"
INJECT_URL = "http://localhost:8080/api/inject"


def inject_data(data):
    """Send mock data to dashboard via a direct function call approach.
    Since we can't POST easily, we'll write to a shared file that app.py reads."""
    # Write to a mock data file that app.py can pick up
    with open("src/web/mock_latest.json", "w") as f:
        json.dump(data, f)
    # Also print as if it were serial output
    print(json.dumps(data))


def generate_normal(t):
    """Generate normal operation data."""
    # Simulate slight variations
    noise = random.gauss(0, 0.02)
    return {
        "bus_v": 4.9 + random.gauss(0, 0.05),
        "m1_mA": 350 + random.gauss(0, 15) + 50 * math.sin(t * 0.1),
        "m2_mA": 280 + random.gauss(0, 10) + 30 * math.sin(t * 0.15),
        "m1_W": 0,  # calculated below
        "m2_W": 0,
        "total_W": 0,
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


def generate_fault_vibration(t, base_data):
    """Simulate vibration fault — IMU spikes."""
    data = base_data.copy()
    data["imu_rms"] = 2.5 + random.gauss(0, 0.3)
    data["imu_status"] = "FAULT"
    data["state"] = "FAULT"
    data["m1_speed"] = 0  # motor stopped
    data["m1_mA"] = 5 + random.gauss(0, 2)  # near zero
    data["faults_today"] = 1
    return data


def generate_fault_stall(t, base_data):
    """Simulate motor stall — current spikes then drops."""
    data = base_data.copy()
    data["m1_mA"] = 800 + random.gauss(0, 50)  # stall current
    data["state"] = "FAULT"
    data["imu_rms"] = 0.1  # motor not vibrating (stalled)
    data["faults_today"] = 1
    return data


def generate_power_sag(t, base_data):
    """Simulate power sag — bus voltage drops."""
    data = base_data.copy()
    data["bus_v"] = 3.5 + random.gauss(0, 0.1)
    data["state"] = "WARNING"
    data["m1_speed"] = 40  # reduced
    data["m2_speed"] = 20  # reduced more
    data["efficiency"] = 45 + random.gauss(0, 5)
    return data


def generate_load_shedding(t, base_data):
    """Simulate load shedding — non-essential loads off."""
    data = base_data.copy()
    data["bus_v"] = 3.8 + random.gauss(0, 0.05)
    data["state"] = "WARNING"
    data["m2_speed"] = 0  # motor 2 shed
    data["m2_mA"] = 0
    data["efficiency"] = 60 + random.gauss(0, 3)
    return data


def generate_dumb_mode(t):
    """Generate dumb mode data — everything at 100%."""
    return {
        "bus_v": 4.8 + random.gauss(0, 0.05),
        "m1_mA": 600 + random.gauss(0, 20),
        "m2_mA": 550 + random.gauss(0, 20),
        "m1_W": 0,
        "m2_W": 0,
        "total_W": 0,
        "efficiency": 100,
        "state": "NORMAL",
        "imu_rms": 0.4 + random.gauss(0, 0.05),
        "imu_status": "HEALTHY",
        "es_score": 0.03,
        "m1_speed": 100,
        "m2_speed": 100,
        "mode": 2,  # DUMB
        "total_items": 0,
        "passed": 0,
        "rejected": 0,
        "reject_rate": 0,
        "faults_today": 0,
    }


def calculate_power(data):
    """Calculate power fields from voltage and current."""
    bus_v = data.get("bus_v", 5.0)
    data["m1_W"] = round(bus_v * data["m1_mA"] / 1000, 2)
    data["m2_W"] = round(bus_v * data["m2_mA"] / 1000, 2)
    data["total_W"] = round(data["m1_W"] + data["m2_W"] + 0.5, 2)  # +0.5 for logic
    return data


def run_normal(duration=60):
    """Run normal operation for N seconds."""
    print(f"[MOCK] Normal operation for {duration}s")
    print("[MOCK] Paste this in another terminal to see it:")
    print("  python src/web/app.py --no-serial")
    print("  Then open http://localhost:8080")
    print()

    start = time.time()
    while time.time() - start < duration:
        t = time.time() - start
        data = generate_normal(t)
        data = calculate_power(data)
        data["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        inject_data(data)
        time.sleep(0.2)  # 5Hz


def run_fault_demo(duration=30):
    """Run with random faults injected."""
    print(f"[MOCK] Fault demo for {duration}s")
    start = time.time()
    fault_type = None
    fault_start = 0

    while time.time() - start < duration:
        t = time.time() - start
        base = generate_normal(t)

        # Random fault injection
        if fault_type is None and random.random() < 0.02:
            fault_type = random.choice(["vibration", "stall", "sag", "shed"])
            fault_start = t
            print(f"[MOCK] Fault injected: {fault_type}")

        if fault_type and t - fault_start < 5:  # fault lasts 5 seconds
            if fault_type == "vibration":
                base = generate_fault_vibration(t, base)
            elif fault_type == "stall":
                base = generate_fault_stall(t, base)
            elif fault_type == "sag":
                base = generate_power_sag(t, base)
            elif fault_type == "shed":
                base = generate_load_shedding(t, base)
        elif fault_type and t - fault_start >= 5:
            fault_type = None
            print("[MOCK] Fault cleared — recovering")

        base = calculate_power(base)
        base["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        inject_data(base)
        time.sleep(0.2)


def run_full_demo():
    """Full 3-minute demo sequence matching the demo script."""
    print("[MOCK] Full demo sequence (3 minutes)")
    print("[MOCK] Open http://localhost:8080 to watch")
    print()

    phases = [
        ("STARTUP — System powering on", 10, "startup"),
        ("NORMAL — All systems running", 20, "normal"),
        ("SPEED CHANGE — Potentiometer adjusted", 15, "speed_change"),
        ("SORTING — Items being processed", 20, "sorting"),
        ("FAULT — Motor vibration detected", 10, "fault_vibration"),
        ("RECOVERY — System self-healing", 10, "recovery"),
        ("DUMB MODE — Everything at 100%", 15, "dumb"),
        ("SMART MODE — Intelligent control", 15, "smart"),
        ("COMPARISON — Showing energy savings", 10, "comparison"),
        ("POWER SAG — Load shedding active", 10, "power_sag"),
        ("RECOVERY — Loads restored", 10, "recovery2"),
        ("FINAL — System stable", 15, "final"),
    ]

    item_count = 0
    passed_count = 0
    rejected_count = 0

    for phase_name, duration, phase_type in phases:
        print(f"[DEMO] {phase_name} ({duration}s)")
        start = time.time()

        while time.time() - start < duration:
            t = time.time() - start

            if phase_type == "startup":
                data = generate_normal(t)
                data["state"] = "NORMAL"
                data["m1_speed"] = min(int(t * 10), 65)  # ramp up
                data["m2_speed"] = min(int(t * 7), 45)
                data["m1_mA"] = data["m1_speed"] * 5

            elif phase_type == "normal":
                data = generate_normal(t)

            elif phase_type == "speed_change":
                data = generate_normal(t)
                speed_mult = 0.5 + 0.5 * math.sin(t * 0.5)
                data["m1_speed"] = int(30 + 50 * speed_mult)
                data["m2_speed"] = int(20 + 40 * speed_mult)
                data["m1_mA"] = data["m1_speed"] * 5 + random.gauss(0, 10)

            elif phase_type == "sorting":
                data = generate_normal(t)
                if random.random() < 0.3:  # item every ~0.6s
                    item_count += 1
                    if random.random() < 0.85:
                        passed_count += 1
                    else:
                        rejected_count += 1
                data["total_items"] = item_count
                data["passed"] = passed_count
                data["rejected"] = rejected_count
                data["reject_rate"] = round(rejected_count / max(item_count, 1) * 100, 1)

            elif phase_type == "fault_vibration":
                data = generate_normal(t)
                data = generate_fault_vibration(t, data)
                data["total_items"] = item_count
                data["passed"] = passed_count
                data["rejected"] = rejected_count

            elif phase_type in ("recovery", "recovery2"):
                data = generate_normal(t)
                data["m1_speed"] = min(int(t * 10), 65)
                data["total_items"] = item_count
                data["passed"] = passed_count
                data["rejected"] = rejected_count

            elif phase_type == "dumb":
                data = generate_dumb_mode(t)

            elif phase_type == "smart":
                data = generate_normal(t)
                data["efficiency"] = 82 + random.gauss(0, 2)

            elif phase_type == "comparison":
                data = generate_normal(t)
                data["efficiency"] = 69
                data["state"] = "NORMAL"

            elif phase_type == "power_sag":
                data = generate_normal(t)
                data = generate_power_sag(t, data)

            elif phase_type == "final":
                data = generate_normal(t)
                data["total_items"] = item_count
                data["passed"] = passed_count
                data["rejected"] = rejected_count

            else:
                data = generate_normal(t)

            data = calculate_power(data)
            data["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            inject_data(data)
            time.sleep(0.2)

    print("\n[DEMO] Demo sequence complete!")
    print(f"[DEMO] Items sorted: {item_count} (pass: {passed_count}, reject: {rejected_count})")


def main():
    parser = argparse.ArgumentParser(description="GridBox Mock Data Generator")
    parser.add_argument("--fault", action="store_true", help="Inject random faults")
    parser.add_argument("--demo", action="store_true", help="Run full 3-min demo sequence")
    parser.add_argument("--duration", type=int, default=60, help="Duration in seconds (default: 60)")
    args = parser.parse_args()

    if args.demo:
        run_full_demo()
    elif args.fault:
        run_fault_demo(args.duration)
    else:
        run_normal(args.duration)


if __name__ == "__main__":
    main()
