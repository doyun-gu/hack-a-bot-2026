"""
GridBox — SCADA Dashboard
5 OLED views, joystick Y-axis scrolls between them.
Each view renders live telemetry data from Pico A.
"""

import config


class Dashboard:
    """OLED dashboard with 5 switchable views."""

    def __init__(self, oled):
        self.oled = oled
        self.current_view = config.VIEW_STATUS
        self._views = [
            self._render_status,
            self._render_power,
            self._render_faults,
            self._render_production,
            self._render_manual,
            self._render_comparison,
        ]
        self._view_names = [
            "System Status",
            "Power Flow",
            "Fault Monitor",
            "Production",
            "Manual Override",
            "Dumb vs Smart",
        ]

    def next_view(self):
        """Switch to next view."""
        self.current_view = (self.current_view + 1) % config.NUM_VIEWS

    def prev_view(self):
        """Switch to previous view."""
        self.current_view = (self.current_view - 1) % config.NUM_VIEWS

    def set_view(self, view_id):
        """Set current view directly."""
        if 0 <= view_id < config.NUM_VIEWS:
            self.current_view = view_id

    def render(self, data):
        """Render current view with data.

        Args:
            data: dict with telemetry from Pico A
        """
        self.oled.fill(0)
        self._render_header(data)
        self._views[self.current_view](data)
        self.oled.show()

    def _render_header(self, data):
        """Draw common header bar."""
        name = self._view_names[self.current_view]
        self.oled.text(name, 0, 0, 1)
        # View indicator dots
        for i in range(config.NUM_VIEWS):
            x = 128 - (config.NUM_VIEWS - i) * 6
            if i == self.current_view:
                self.oled.fill_rect(x, 1, 4, 4, 1)
            else:
                self.oled.rect(x, 1, 4, 4, 1)
        self.oled.hline(0, 8, 128, 1)

    def _render_status(self, data):
        """View 1: System Status — motors, servos, bus, state."""
        m1_spd = data.get('m1_speed', 0)
        m1_mA = data.get('m1_mA', 0)
        m2_spd = data.get('m2_speed', 0)
        m2_mA = data.get('m2_mA', 0)
        s1 = data.get('servo1_angle', 90)
        s2 = data.get('servo2_angle', 90)
        bus_v = data.get('bus_v', 0)
        state = data.get('state', 'UNKNOWN')

        self.oled.text(f"M1:{m1_spd:3d}% {m1_mA:4.0f}mA", 0, 12, 1)
        self.oled.text(f"M2:{m2_spd:3d}% {m2_mA:4.0f}mA", 0, 22, 1)
        self.oled.text(f"S1:{s1:3d}  S2:{s2:3d}", 0, 32, 1)
        self.oled.text(f"Bus: {bus_v:.1f}V", 0, 44, 1)
        self.oled.text(f"[{state}]", 0, 54, 1)

    def _render_power(self, data):
        """View 2: Power Flow — per-branch bars, totals."""
        m1_W = data.get('m1_W', 0)
        m2_W = data.get('m2_W', 0)
        total_W = data.get('total_W', 0)
        excess_W = data.get('excess_W', 0)
        eff = data.get('efficiency', 0)

        # Motor 1 bar
        self.oled.text("M1", 0, 12, 1)
        bar1 = min(int(m1_W / 5.0 * 80), 80)  # scale to 5W max
        self.oled.rect(20, 12, 82, 8, 1)
        if bar1 > 0:
            self.oled.fill_rect(21, 13, bar1, 6, 1)
        self.oled.text(f"{m1_W:.1f}W", 104, 12, 1)

        # Motor 2 bar
        self.oled.text("M2", 0, 24, 1)
        bar2 = min(int(m2_W / 5.0 * 80), 80)
        self.oled.rect(20, 24, 82, 8, 1)
        if bar2 > 0:
            self.oled.fill_rect(21, 25, bar2, 6, 1)
        self.oled.text(f"{m2_W:.1f}W", 104, 24, 1)

        # Totals
        self.oled.text(f"Total: {total_W:.2f}W", 0, 38, 1)
        self.oled.text(f"Excess: {excess_W:.2f}W", 0, 48, 1)
        self.oled.text(f"Eff: {eff:.0f}%", 0, 56, 1)

    def _render_faults(self, data):
        """View 3: Fault Monitor — waste targets, fault count."""
        state = data.get('state', 'NORMAL')
        faults = data.get('faults_today', 0)
        rerouted = data.get('rerouted_mWs', 0)
        imu_status = data.get('imu_status', 'HEALTHY')
        es_score = data.get('es_score', 0)

        # Waste target status indicators
        targets = ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8']
        y = 12
        for i in range(0, 8, 4):
            line = ""
            for j in range(4):
                idx = i + j
                if idx < len(targets):
                    # Simulate status from state
                    if state == "EMERGENCY":
                        status = "!"
                    elif state in ("FAULT", "WARNING") and idx < 2:
                        status = "?"
                    else:
                        status = "+"
                    line += f"{targets[idx]}:{status} "
            self.oled.text(line, 0, y, 1)
            y += 10

        self.oled.text(f"IMU: {imu_status}", 0, 34, 1)
        self.oled.text(f"ES: {es_score:.2f}", 0, 44, 1)
        self.oled.text(f"Faults:{faults} R:{rerouted:.0f}mWs", 0, 54, 1)

    def _render_production(self, data):
        """View 4: Production — sort stats, belt speed, threshold."""
        total = data.get('total_items', 0)
        passed = data.get('passed', 0)
        rejected = data.get('rejected', 0)
        rate = data.get('reject_rate', 0)
        last_class = data.get('last_weight_class', 'NONE')
        belt_speed = data.get('belt_speed', 0)
        threshold = data.get('threshold', 0)

        self.oled.text(f"Items: {total}", 0, 12, 1)
        self.oled.text(f"Pass:{passed} Rej:{rejected}", 0, 22, 1)
        self.oled.text(f"Reject: {rate:.1f}%", 0, 32, 1)
        self.oled.text(f"Last: {last_class}", 0, 42, 1)
        self.oled.text(f"Belt:{belt_speed}cm/s", 0, 52, 1)
        self.oled.text(f"Thr:{threshold}", 80, 52, 1)

    def _render_manual(self, data):
        """View 5: Manual Override — joystick control display."""
        joy_x = data.get('joy_x', 50)
        joy_y = data.get('joy_y', 50)
        btn = data.get('button', False)
        pot = data.get('pot_value', 0)

        self.oled.text("Joy X->M1  Y->M2", 0, 12, 1)

        # Joystick crosshair
        cx = 32
        cy = 40
        size = 20
        self.oled.rect(cx - size, cy - size, size * 2, size * 2, 1)
        # Map joy 0-100 to crosshair position
        jx = cx - size + int(joy_x / 100 * size * 2)
        jy = cy - size + int(joy_y / 100 * size * 2)
        self.oled.fill_rect(jx - 2, jy - 2, 4, 4, 1)

        # Values
        self.oled.text(f"M1:{joy_x:3d}%", 72, 22, 1)
        self.oled.text(f"M2:{joy_y:3d}%", 72, 32, 1)

        btn_txt = "BTN:ON" if btn else "BTN:--"
        self.oled.text(btn_txt, 72, 42, 1)
        self.oled.text(f"Pot:{pot:3d}%", 72, 52, 1)

    def _render_comparison(self, data):
        """View 6: Dumb vs Smart — A/B comparison results."""
        dumb_w = data.get('dumb_avg_W', 0)
        smart_w = data.get('smart_avg_W', 0)
        savings = data.get('savings_pct', 0)

        if dumb_w == 0 and smart_w == 0:
            self.oled.text("No comparison", 0, 14, 1)
            self.oled.text("data yet.", 0, 26, 1)
            self.oled.text("Long-press to", 0, 42, 1)
            self.oled.text("start A/B test", 0, 52, 1)
        else:
            self.oled.text("DUMB (100% PWM)", 0, 12, 1)
            self.oled.text(f"  {dumb_w:.2f} W", 0, 22, 1)
            self.oled.text("SMART (optimised)", 0, 34, 1)
            self.oled.text(f"  {smart_w:.2f} W", 0, 44, 1)
            self.oled.text(f"Saved: {savings:.1f}%", 0, 56, 1)

            # Draw savings bar
            bar_w = min(int(savings), 100)
            self.oled.rect(80, 54, 48, 8, 1)
            if bar_w > 0:
                fill = min(int(bar_w / 100 * 46), 46)
                self.oled.fill_rect(81, 55, fill, 6, 1)

    def render_link_lost(self):
        """Special screen: no wireless link."""
        self.oled.fill(0)
        self.oled.rect(0, 0, 128, 64, 1)
        self.oled.text("LINK LOST", 24, 20, 1)
        self.oled.text("No signal", 28, 36, 1)
        self.oled.text("from Pico A", 20, 48, 1)
        self.oled.show()


if __name__ == "__main__":
    from machine import Pin, I2C
    import time
    from ssd1306 import SSD1306

    print("=" * 40)
    print("  SCADA Dashboard Test")
    print("=" * 40)

    i2c = I2C(config.I2C_ID, sda=Pin(config.I2C_SDA),
              scl=Pin(config.I2C_SCL), freq=config.I2C_FREQ)

    try:
        oled = SSD1306(i2c, config.OLED_WIDTH, config.OLED_HEIGHT, config.SSD1306_ADDR)
        dash = Dashboard(oled)

        # Mock telemetry data
        mock_data = {
            'm1_speed': 65, 'm1_mA': 280, 'm1_W': 1.4,
            'm2_speed': 40, 'm2_mA': 180, 'm2_W': 0.9,
            'servo1_angle': 90, 'servo2_angle': 45,
            'bus_v': 4.9, 'state': 'NORMAL',
            'total_W': 2.3, 'excess_W': 1.2, 'efficiency': 37,
            'faults_today': 2, 'rerouted_mWs': 150,
            'imu_status': 'HEALTHY', 'es_score': 0.12,
            'total_items': 47, 'passed': 42, 'rejected': 5,
            'reject_rate': 10.6, 'last_weight_class': 'PASS',
            'belt_speed': 5, 'threshold': 50,
            'dumb_avg_W': 3.45, 'smart_avg_W': 1.76, 'savings_pct': 49.0,
            'joy_x': 50, 'joy_y': 50, 'button': False, 'pot_value': 65,
        }

        # Cycle through all 5 views
        for v in range(config.NUM_VIEWS):
            dash.set_view(v)
            dash.render(mock_data)
            name = dash._view_names[v]
            print(f"View {v + 1}: {name}")
            time.sleep(2)

        # Show link lost
        dash.render_link_lost()
        print("Link Lost screen")
        time.sleep(2)

        oled.clear()
        print("\nDashboard test complete")

    except OSError as e:
        print(f"I2C error: {e}")
