#!/bin/bash
cd "$(dirname "$0")"

tmux kill-session -t c-complete 2>/dev/null

tmux new-session -d -s c-complete \
    "cd $(pwd) && claude \
    --dangerously-skip-permissions \
    --max-turns 200 \
    -p 'Pull latest main. Port ALL remaining MicroPython modules to C SDK.

EXISTING C FILES (do NOT rewrite):
Master: config.h, bmi160.c/.h, pca9685.c/.h, nrf24l01.c/.h, power_manager.c/.h, main.c
Slave: config.h, ssd1306.c/.h, nrf24l01.c/.h, main.c

MASTER — Create these missing C files in src/master-pico/c_sdk/:

1. motor_control.c/.h — Port from motor_control.py
   Functions: motor_control_init(), set_speed(motor_id, pct), set_servo_angle(ch, angle), emergency_stop_all(), enable_motor(), disable_motor(), ramp_speed()
   Uses pca9685 for PWM + GPIO for MOSFET switching

2. imu_reader.c/.h — Port from imu_reader.py
   Runs on Core 1 via multicore. Continuously reads BMI160 at 100Hz.
   Functions: imu_reader_start(), imu_reader_get_rms(), imu_reader_get_status(), imu_reader_stop()
   Uses volatile globals for thread-safe data sharing (already in main.c pattern)

3. fault_manager.c/.h — Port from fault_manager.py
   State machine: NORMAL→DRIFT→WARNING→FAULT→EMERGENCY
   Functions: fault_init(), fault_update(power_data, imu_status), fault_get_state(), fault_get_actions(), fault_reset(), fault_execute_actions()
   Load shedding logic: shed by priority P4→P3→P2→P1

4. energy_signature.c/.h — Port from energy_signature.py
   Functions: es_init(), es_learn_baseline(duration_s), es_compute_signature(), es_divergence_score(), es_get_score(), es_is_anomaly()
   500Hz ADC sampling in 1-second windows. Zero-crossing counter. 4-metric divergence.

5. sorter.c/.h — Port from sorter.py
   Functions: sorter_init(), sorter_detect_item(), sorter_classify_weight(), sorter_schedule_sort(), sorter_get_stats()
   Timer-based servo trigger using hardware timer callbacks

6. led_stations.c/.h — Port from led_stations.py
   Functions: led_stations_init(), led_set_station(id, on), led_run_sequence(weight_class)
   4 GPIO pins for station LEDs

7. packet_tracker.c/.h — Port from packet_tracker.py
   Functions: tracker_init(), tracker_track(seq), tracker_reliability(), tracker_get_stats()

8. calibration.c/.h — Port from calibration.py
   Functions: cal_init(), cal_calibrate_empty(), cal_calibrate_reference(weight_g), cal_save(), cal_load(), cal_get_baseline()
   Note: Save to flash using Pico SDK flash_range_program() or just hardcode defaults

9. Update main.c to integrate ALL new modules. The existing main.c already has the framework. Add:
   - fault_manager calls in the main loop
   - motor_control for speed changes
   - sorter for weight detection
   - led_stations for production sequence
   - energy_signature on Core 1 (interleaved with IMU)
   - packet_tracker for wireless reliability

10. Update CMakeLists.txt to include all new .c files

SLAVE — Create these missing C files in src/slave-pico/c_sdk/:

11. dashboard.c/.h — Port from dashboard.py
   Functions: dashboard_init(), dashboard_render(view, data), dashboard_next_view(), dashboard_prev_view(), dashboard_render_link_lost()
   5 OLED views using ssd1306 driver. Draw text, bars, dividers.
   Yellow zone (y=0-15) header, blue zone (y=16-63) content.

12. operator.c/.h — Port from operator.py
   Functions: operator_init(), operator_read_joystick(x,y,btn), operator_read_pot(), operator_get_direction(), operator_is_long_press()
   ADC reading with deadzone, button debounce 50ms, long press 3s detection

13. commander.c/.h — Port from commander.py
   Functions: commander_init(), commander_send_override(motor_id, speed), commander_send_threshold(value), commander_send_reset(), commander_send_emergency_stop()
   Pack command packets and send via nrf24l01

14. packet_tracker.c/.h — Same as master version, copy to slave directory

15. Update slave main.c to integrate dashboard, operator, commander, packet_tracker
   Main loop: receive packet → update telemetry → read joystick → update dashboard → send commands

16. Update slave CMakeLists.txt

RULES:
- Use the same function signatures and logic as the MicroPython versions
- Use Pico SDK APIs (hardware_i2c, hardware_spi, hardware_adc, hardware_timer, pico_multicore)
- Include guards on all .h files
- Commit and push after every 2-3 files completed
- Keep code clean with comments matching the MicroPython docstrings'; \
    echo 'Done.'; read"

echo "C complete worker: tmux attach -t c-complete"
echo "Progress: git log --oneline -10"
