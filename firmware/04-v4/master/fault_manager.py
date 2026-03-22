"""
GridBox — Fault Manager
State machine: NORMAL → DRIFT → WARNING → FAULT → EMERGENCY.
Decides load shedding, rerouting, and motor speed adjustments.
"""

import time
import config

# States
STATE_NORMAL = "NORMAL"
STATE_DRIFT = "DRIFT"
STATE_WARNING = "WARNING"
STATE_FAULT = "FAULT"
STATE_EMERGENCY = "EMERGENCY"

# Actions
ACTION_NONE = "none"
ACTION_SHED_P4 = "shed_p4"      # shed priority 4 loads (recycle)
ACTION_SHED_P3 = "shed_p3"      # shed priority 3 loads (LEDs)
ACTION_SHED_P2 = "shed_p2"      # shed priority 2 loads (motor 2)
ACTION_STOP_MOTOR = "stop_motor"
ACTION_REROUTE = "reroute"
ACTION_ALERT = "alert"
ACTION_EMERGENCY_STOP = "emergency_stop"


class FaultManager:
    """Fault state machine with load shedding and rerouting."""

    def __init__(self, motor_control=None):
        self.motor_control = motor_control
        self.state = STATE_NORMAL
        self.prev_state = STATE_NORMAL
        self.actions = []

        # Timing
        self._drift_start_ms = 0
        self._warning_start_ms = 0

        # Thresholds (from config)
        self._drift_timeout_ms = 5000     # 5s in drift → warning
        self._warning_timeout_ms = 3000   # 3s in warning → fault

        # Stats
        self.faults_today = 0
        self.rerouted_mWs = 0.0
        self._shed_loads = set()

    def update(self, power_data, imu_status):
        """Update state machine. Called every main loop iteration.

        Args:
            power_data: dict from PowerManager.read_all()
            imu_status: string from IMUReader.get_status() (HEALTHY/WARNING/FAULT)

        Returns:
            list of action strings to execute
        """
        self.actions = []
        self.prev_state = self.state
        now = time.ticks_ms()

        bus_v = power_data.get('bus_v', 5.0)
        m1_mA = power_data.get('m1_mA', 0)
        m2_mA = power_data.get('m2_mA', 0)

        # === Check for emergency conditions ===
        if imu_status == "FAULT" or bus_v < config.BUS_VOLTAGE_CRITICAL:
            self._transition_to(STATE_EMERGENCY)
            self.actions.append(ACTION_EMERGENCY_STOP)
            self.actions.append(ACTION_ALERT)
            self.faults_today += 1
            return self.actions

        # === Check for motor overcurrent (jam) ===
        if m1_mA > config.MOTOR_CURRENT_MAX_MA or m2_mA > config.MOTOR_CURRENT_MAX_MA:
            self._transition_to(STATE_FAULT)
            if m1_mA > config.MOTOR_CURRENT_MAX_MA:
                self.actions.append(ACTION_STOP_MOTOR + ":1")
            if m2_mA > config.MOTOR_CURRENT_MAX_MA:
                self.actions.append(ACTION_STOP_MOTOR + ":2")
            self.actions.append(ACTION_ALERT)
            self.faults_today += 1
            return self.actions

        # === State transitions based on voltage ===
        if bus_v < config.BUS_VOLTAGE_LOW:
            # Low voltage — escalate through states
            if self.state == STATE_NORMAL:
                self._transition_to(STATE_DRIFT)
                self._drift_start_ms = now
            elif self.state == STATE_DRIFT:
                if time.ticks_diff(now, self._drift_start_ms) > self._drift_timeout_ms:
                    self._transition_to(STATE_WARNING)
                    self._warning_start_ms = now
                    self.actions.append(ACTION_SHED_P4)
            elif self.state == STATE_WARNING:
                if time.ticks_diff(now, self._warning_start_ms) > self._warning_timeout_ms:
                    self._transition_to(STATE_FAULT)
                    self.actions.append(ACTION_SHED_P3)
                    self.actions.append(ACTION_SHED_P2)
                    self.actions.append(ACTION_ALERT)
                    self.faults_today += 1
                else:
                    self.actions.append(ACTION_SHED_P4)
                    self.actions.append(ACTION_SHED_P3)
        elif imu_status == "WARNING":
            # Vibration warning — drift state
            if self.state == STATE_NORMAL:
                self._transition_to(STATE_DRIFT)
                self._drift_start_ms = now
            elif self.state == STATE_DRIFT:
                if time.ticks_diff(now, self._drift_start_ms) > self._drift_timeout_ms:
                    self._transition_to(STATE_WARNING)
                    self.actions.append(ACTION_ALERT)
        else:
            # Everything nominal — recover
            if self.state != STATE_NORMAL and self.state not in (STATE_FAULT, STATE_EMERGENCY):
                self._transition_to(STATE_NORMAL)
                self._drift_start_ms = 0
                self._warning_start_ms = 0

        # === Rerouting: if a motor stopped, try to use excess power ===
        if power_data.get('excess_W', 0) > 0.5:
            self.actions.append(ACTION_REROUTE)

        return self.actions

    def _transition_to(self, new_state):
        """Transition to a new state."""
        if new_state != self.state:
            self.state = new_state

    def get_state(self):
        """Return current state string."""
        return self.state

    def get_actions(self):
        """Return list of pending actions."""
        return self.actions

    def execute_actions(self, actions=None):
        """Execute actions via motor_control (if available).

        Args:
            actions: list of action strings, or None to use self.actions
        """
        if self.motor_control is None:
            return

        mc = self.motor_control
        for action in (actions or self.actions):
            if action == ACTION_EMERGENCY_STOP:
                mc.emergency_stop_all()
            elif action.startswith(ACTION_STOP_MOTOR):
                motor_id = int(action.split(":")[1])
                mc.emergency_stop(motor_id)
            elif action == ACTION_SHED_P4:
                mc.set_recycle(False)
                self._shed_loads.add('recycle')
            elif action == ACTION_SHED_P3:
                mc.set_led_bank(False)
                self._shed_loads.add('leds')
            elif action == ACTION_SHED_P2:
                mc.emergency_stop(2)
                self._shed_loads.add('motor2')
            elif action == ACTION_REROUTE:
                # If motor 1 stopped, boost motor 2 (or vice versa)
                if mc.get_speed(1) == 0 and mc.get_speed(2) > 0:
                    current = mc.get_speed(2)
                    mc.set_speed(2, min(100, current + 10))
                elif mc.get_speed(2) == 0 and mc.get_speed(1) > 0:
                    current = mc.get_speed(1)
                    mc.set_speed(1, min(100, current + 10))
                # Also enable LED bank with excess power
                if 'leds' not in self._shed_loads:
                    mc.set_led_bank(True)

    def reset(self):
        """Manual reset from FAULT/EMERGENCY back to NORMAL."""
        self.state = STATE_NORMAL
        self._drift_start_ms = 0
        self._warning_start_ms = 0
        self._shed_loads.clear()
        self.actions = []

    def get_stats(self):
        """Return fault statistics."""
        return {
            'state': self.state,
            'faults_today': self.faults_today,
            'rerouted_mWs': round(self.rerouted_mWs, 1),
            'shed_loads': list(self._shed_loads),
        }


if __name__ == "__main__":
    print("=" * 40)
    print("  Fault Manager Test (simulated)")
    print("=" * 40)

    fm = FaultManager()

    # Simulate normal operation
    print("\n--- Normal operation ---")
    power = {'bus_v': 5.0, 'm1_mA': 200, 'm2_mA': 150, 'excess_W': 0.2}
    actions = fm.update(power, "HEALTHY")
    print(f"State: {fm.get_state()}, Actions: {actions}")

    # Simulate voltage drop
    print("\n--- Voltage dropping ---")
    power['bus_v'] = 4.0
    actions = fm.update(power, "HEALTHY")
    print(f"State: {fm.get_state()}, Actions: {actions}")

    # Simulate sustained low voltage
    print("\n--- Sustained low voltage (simulate 6s) ---")
    fm._drift_start_ms = time.ticks_ms() - 6000
    actions = fm.update(power, "HEALTHY")
    print(f"State: {fm.get_state()}, Actions: {actions}")

    # Simulate overcurrent
    print("\n--- Motor 1 overcurrent (jam) ---")
    fm.reset()
    power['bus_v'] = 5.0
    power['m1_mA'] = 900
    actions = fm.update(power, "HEALTHY")
    print(f"State: {fm.get_state()}, Actions: {actions}")

    # Simulate IMU fault
    print("\n--- IMU fault ---")
    fm.reset()
    power['m1_mA'] = 200
    actions = fm.update(power, "FAULT")
    print(f"State: {fm.get_state()}, Actions: {actions}")

    # Reset
    print("\n--- Manual reset ---")
    fm.reset()
    print(f"State: {fm.get_state()}")
    print(f"Stats: {fm.get_stats()}")
