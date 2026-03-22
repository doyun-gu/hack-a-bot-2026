"""
Test: Send real sensor data to web dashboard via USB serial.
Pico reads actual ADC values and prints JSON that the Flask dashboard reads.

Setup:
  Terminal 1: python3 src/web/app.py --port /dev/tty.usbmodem*
  Terminal 2: mpremote run src/master-pico/tests/test_live_dashboard.py

Then open http://localhost:8080 — real Pico data appears!
"""

from machine import Pin, ADC
import time
import json

led = Pin(25, Pin.OUT)

# ADC channels (works even without full wiring — reads noise/voltage)
adc26 = ADC(Pin(26))
adc27 = ADC(Pin(27))

print("[LIVE] Starting real sensor output to dashboard")
print("[LIVE] Ctrl+C to stop")

tick = 0
try:
    while True:
        # Read real ADC values
        raw26 = adc26.read_u16()
        raw27 = adc27.read_u16()

        # Convert to real voltage/current
        bus_v = raw26 * 3.3 / 65535 * 2  # voltage divider
        m1_mA = raw27 * 3.3 / 65535 / 1.0 * 1000  # sense resistor

        # Build JSON matching dashboard format
        data = {
            "bus_v": round(bus_v, 2),
            "m1_mA": round(m1_mA, 0),
            "m2_mA": 0,
            "m1_W": round(bus_v * m1_mA / 1000, 2),
            "m2_W": 0,
            "total_W": round(bus_v * m1_mA / 1000, 2),
            "efficiency": 82,
            "state": "NORMAL",
            "imu_rms": 0.0,
            "imu_status": "NO_IMU",
            "es_score": 0.0,
            "m1_speed": 0,
            "m2_speed": 0,
            "mode": 1,
            "total_items": 0,
            "passed": 0,
            "rejected": 0,
            "reject_rate": 0,
            "faults_today": 0,
        }

        # Print JSON — Flask reads this via USB serial
        print(json.dumps(data))

        # LED heartbeat
        led.toggle()
        tick += 1
        time.sleep_ms(200)  # 5Hz

except KeyboardInterrupt:
    led.value(0)
    print("[LIVE] Stopped")
