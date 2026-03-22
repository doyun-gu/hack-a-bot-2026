"""
Find the exact STOP duty value for your MG90D.
Tries values from 4000 to 5000. Watch when the servo stops moving.

Usage: mpremote run src/master-pico/tests/test_servo_findstop.py
"""

from machine import Pin, PWM
import time

servo = PWM(Pin(0))
servo.freq(50)

print("Finding stop point...")
print("Watch servo — which value makes it STOP?\n")

for duty in range(4000, 5100, 100):
    servo.duty_u16(duty)
    print(f"  duty = {duty}  — is it stopped?")
    time.sleep(1)

servo.duty_u16(4500)
time.sleep(0.5)
servo.deinit()
print("\nDone. Which duty value stopped the servo?")
