"""
Simple MAX7219 test — lights up all segments then counts.
DIN=GP17, CS=GP18, CLK=GP19, VCC=5V, GND=GND

Usage: mpremote run src/master-pico/tests/test_7seg_simple.py
"""

from machine import Pin
import time

DIN = Pin(17, Pin.OUT)
CS = Pin(18, Pin.OUT, value=1)
CLK = Pin(19, Pin.OUT)

def sb(d):
    for i in range(8):
        CLK.value(0)
        DIN.value((d >> (7 - i)) & 1)
        CLK.value(1)

def sc(r, d):
    CS.value(0)
    sb(r)
    sb(d)
    CS.value(1)

print("Init MAX7219...")
sc(0x0C, 1)    # normal mode
sc(0x0B, 7)    # scan all 8 digits
sc(0x09, 0xFF) # BCD decode
sc(0x0A, 8)    # brightness medium

print("Display test — all segments ON...")
sc(0x0F, 1)    # test mode ON
time.sleep(2)
sc(0x0F, 0)    # test mode OFF

print("Counting...")
for n in range(100):
    d1 = n % 10
    d2 = (n // 10) % 10
    sc(1, d1)
    sc(2, d2)
    for i in range(3, 9):
        sc(i, 0x0F)  # blank other digits
    time.sleep_ms(100)

print("Done!")
sc(0x0C, 0)  # shutdown
