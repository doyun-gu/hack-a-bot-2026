"""
Benchmark: Measure MicroPython speed on your Pico.
Shows how fast ADC, GPIO, math operations run.
Compare these numbers to C SDK expectations.

Usage: mpremote run src/master-pico/tests/test_benchmark.py
"""

from machine import Pin, ADC
import time

led = Pin(25, Pin.OUT)

print("=" * 40)
print("  MicroPython Speed Benchmark")
print("=" * 40)

# Test 1: GPIO toggle speed
print("\n1. GPIO Toggle Speed")
start = time.ticks_us()
for _ in range(10000):
    led.value(1)
    led.value(0)
elapsed = time.ticks_diff(time.ticks_us(), start)
toggles_per_sec = 10000 / (elapsed / 1_000_000)
print(f"   10,000 toggles in {elapsed}us")
print(f"   = {toggles_per_sec:,.0f} toggles/sec")
print(f"   C SDK expected: ~10,000,000 toggles/sec ({10_000_000/toggles_per_sec:.0f}x faster)")

# Test 2: ADC read speed
print("\n2. ADC Read Speed")
adc = ADC(Pin(26))
start = time.ticks_us()
for _ in range(1000):
    adc.read_u16()
elapsed = time.ticks_diff(time.ticks_us(), start)
reads_per_sec = 1000 / (elapsed / 1_000_000)
print(f"   1,000 reads in {elapsed}us")
print(f"   = {reads_per_sec:,.0f} reads/sec")
print(f"   C SDK expected: ~500,000 reads/sec ({500_000/reads_per_sec:.0f}x faster)")

# Test 3: Math operations (float)
print("\n3. Float Math Speed")
start = time.ticks_us()
x = 1.0
for i in range(10000):
    x = x * 1.001 + 0.1
    y = (x * x) ** 0.5
elapsed = time.ticks_diff(time.ticks_us(), start)
ops_per_sec = 10000 / (elapsed / 1_000_000)
print(f"   10,000 float ops in {elapsed}us")
print(f"   = {ops_per_sec:,.0f} ops/sec")
print(f"   C SDK expected: ~5,000,000 ops/sec ({5_000_000/ops_per_sec:.0f}x faster)")

# Test 4: Loop overhead
print("\n4. Empty Loop Overhead")
start = time.ticks_us()
for _ in range(100000):
    pass
elapsed = time.ticks_diff(time.ticks_us(), start)
loops_per_sec = 100000 / (elapsed / 1_000_000)
print(f"   100,000 empty loops in {elapsed}us")
print(f"   = {loops_per_sec:,.0f} loops/sec")
print(f"   C SDK expected: ~100,000,000 loops/sec ({100_000_000/loops_per_sec:.0f}x faster)")

# Test 5: Simulated 100Hz control loop
print("\n5. Control Loop Timing")
adc26 = ADC(Pin(26))
adc27 = ADC(Pin(27))
times = []
for _ in range(100):
    start = time.ticks_us()
    # Simulate one control loop iteration:
    v1 = adc26.read_u16()  # read ADC
    v2 = adc27.read_u16()  # read ADC
    bus_v = v1 * 3.3 / 65535 * 2  # voltage calc
    current = v2 * 3.3 / 65535 / 1.0 * 1000  # current calc
    power = bus_v * current / 1000  # power calc
    led.toggle()  # GPIO
    elapsed = time.ticks_diff(time.ticks_us(), start)
    times.append(elapsed)

avg = sum(times) / len(times)
worst = max(times)
best = min(times)
print(f"   100 iterations measured")
print(f"   Average: {avg:.0f}us per loop")
print(f"   Best:    {best}us")
print(f"   Worst:   {worst}us")
print(f"   Max frequency: {1_000_000/avg:.0f} Hz")
print(f"   C SDK expected: <10us per loop = 100,000+ Hz")

# Summary
print("\n" + "=" * 40)
print("  SUMMARY")
print("=" * 40)
print(f"\n  MicroPython control loop: {avg:.0f}us ({1_000_000/avg:.0f} Hz)")
print(f"  C SDK control loop:      ~5us (200,000 Hz)")
print(f"  Speedup:                 ~{avg/5:.0f}x faster")
print(f"\n  For 100Hz target:")
print(f"    MicroPython: {'OK' if avg < 10000 else 'TOO SLOW'} ({avg:.0f}us < 10,000us budget)")
print(f"    C SDK:       OK (5us << 10,000us budget)")
print(f"\n  MicroPython works for 100Hz but C gives")
print(f"  {avg/5:.0f}x headroom for additional processing.")
