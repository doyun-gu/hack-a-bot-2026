"""
Generate presentation charts as PNG images.
Usage: python3 docs/03-factory/generate_charts.py
Output: docs/03-factory/charts/*.png
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

out_dir = os.path.join(os.path.dirname(__file__), "charts")
os.makedirs(out_dir, exist_ok=True)

# Style
plt.rcParams['figure.facecolor'] = '#1a1a2e'
plt.rcParams['axes.facecolor'] = '#16213e'
plt.rcParams['text.color'] = 'white'
plt.rcParams['axes.labelcolor'] = 'white'
plt.rcParams['xtick.color'] = 'white'
plt.rcParams['ytick.color'] = 'white'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 12


# ============================================================
# 1. Cost Comparison Bar Chart
# ============================================================
fig, ax = plt.subplots(figsize=(10, 6))

categories = ['SCADA\nSystem', 'Power\nMeters', 'Vibration\nAnalyser', 'Motor\nDrives', 'BMS\nSoftware', 'GridBox\n(Ours)']
costs = [80000, 15000, 18000, 35000, 14000, 15]
colors = ['#e94560', '#e94560', '#e94560', '#e94560', '#e94560', '#2d6a4f']

bars = ax.bar(categories, costs, color=colors, edgecolor='white', linewidth=0.5)
ax.set_ylabel('Cost (£)', fontsize=14)
ax.set_title('Cost Comparison: Industrial vs GridBox', fontsize=18, fontweight='bold', color='#ff6b35')
ax.set_yscale('log')
ax.set_ylim(1, 200000)

# Add value labels
for bar, cost in zip(bars, costs):
    label = f'£{cost:,}' if cost > 100 else f'£{cost}'
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() * 1.3,
            label, ha='center', va='bottom', fontweight='bold',
            fontsize=12, color='white')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#444')
ax.spines['bottom'].set_color('#444')
plt.tight_layout()
plt.savefig(os.path.join(out_dir, '01-cost-comparison.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  [1/8] Cost comparison chart")


# ============================================================
# 2. Affinity Laws Power Curve
# ============================================================
fig, ax = plt.subplots(figsize=(10, 6))

speed = np.linspace(0, 100, 100)
power_cubic = (speed / 100) ** 3 * 100
power_linear = speed

ax.plot(speed, power_linear, '--', color='#e94560', linewidth=2, label='Linear (naive assumption)')
ax.plot(speed, power_cubic, '-', color='#2d6a4f', linewidth=3, label='Cubic — Affinity Laws (P ∝ n³)')
ax.fill_between(speed, power_cubic, power_linear, alpha=0.2, color='#2d6a4f')

# Annotation
ax.annotate('49% saving\nat 80% speed', xy=(80, 51.2), xytext=(55, 70),
            fontsize=14, fontweight='bold', color='#ff6b35',
            arrowprops=dict(arrowstyle='->', color='#ff6b35', lw=2))

ax.axvline(x=80, color='#ff6b35', linestyle=':', alpha=0.5)
ax.axhline(y=51.2, color='#ff6b35', linestyle=':', alpha=0.5)

ax.set_xlabel('Motor Speed (%)', fontsize=14)
ax.set_ylabel('Power Consumption (%)', fontsize=14)
ax.set_title('Affinity Laws: P ∝ n³ — Why Slowing Down Saves Energy', fontsize=16, fontweight='bold', color='#ff6b35')
ax.legend(fontsize=12, loc='upper left', facecolor='#16213e', edgecolor='#444')
ax.set_xlim(0, 100)
ax.set_ylim(0, 105)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#444')
ax.spines['bottom'].set_color('#444')
plt.tight_layout()
plt.savefig(os.path.join(out_dir, '02-affinity-laws.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  [2/8] Affinity Laws chart")


# ============================================================
# 3. Packet Protocol Diagram
# ============================================================
fig, ax = plt.subplots(figsize=(12, 5))
ax.set_xlim(0, 12)
ax.set_ylim(0, 8)
ax.axis('off')
ax.set_title('32-Byte Datagram Protocol — 6 Packet Types', fontsize=18, fontweight='bold', color='#ff6b35', pad=20)

# Packet structure
packet_y = 6.5
fields = [
    ('Type', 1, '#e94560'),
    ('Seq', 1, '#533483'),
    ('Timestamp', 2, '#0f3460'),
    ('Payload (24 bytes)', 6, '#2d6a4f'),
    ('CRC', 2, '#e94560'),
]

x = 0
for name, width, color in fields:
    rect = mpatches.FancyBboxPatch((x, packet_y - 0.4), width, 0.8,
                                     boxstyle="round,pad=0.05",
                                     facecolor=color, edgecolor='white', linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x + width/2, packet_y, name, ha='center', va='center',
            fontsize=11, fontweight='bold', color='white')
    ax.text(x + width/2, packet_y - 0.7, f'{width}B' if width < 6 else '24B',
            ha='center', va='center', fontsize=9, color='#aaa')
    x += width

ax.text(6, packet_y + 0.7, '← 32 bytes total →', ha='center', fontsize=12, color='#aaa')

# 6 packet types
types = [
    ('POWER', '#e94560', 'Bus V, motor I,\ntotal W, efficiency'),
    ('STATUS', '#0f3460', 'State, fault,\nIMU, mode, uptime'),
    ('PRODUCTION', '#533483', 'Items, pass/reject,\nbelt speed'),
    ('HEARTBEAT', '#1a1a2e', 'Timestamp, CPU,\nwireless stats'),
    ('ALERT', '#e94560', 'Fault code,\nseverity, subsystem'),
    ('COMMAND', '#2d6a4f', 'Motor speed, servo,\nmode, e-stop'),
]

for i, (name, color, desc) in enumerate(types):
    x = (i % 3) * 4 + 0.3
    y = 3.5 if i < 3 else 1.2
    rect = mpatches.FancyBboxPatch((x, y - 0.5), 3.4, 1.3,
                                     boxstyle="round,pad=0.1",
                                     facecolor=color, edgecolor='white', linewidth=1)
    ax.add_patch(rect)
    direction = 'A → B' if name != 'COMMAND' else 'B → A'
    ax.text(x + 1.7, y + 0.5, f'{name}', ha='center', va='center',
            fontsize=12, fontweight='bold', color='white')
    ax.text(x + 1.7, y - 0.05, f'{desc}\n({direction})', ha='center', va='center',
            fontsize=9, color='#ddd')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '03-packet-protocol.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  [3/8] Packet protocol diagram")


# ============================================================
# 4. System Architecture
# ============================================================
fig, ax = plt.subplots(figsize=(14, 7))
ax.set_xlim(0, 14)
ax.set_ylim(0, 8)
ax.axis('off')
ax.set_title('Two-Pico Wireless Architecture', fontsize=20, fontweight='bold', color='#ff6b35', pad=20)

# Pico A box
rect_a = mpatches.FancyBboxPatch((0.5, 1), 5, 6, boxstyle="round,pad=0.2",
                                   facecolor='#1a1a2e', edgecolor='#e94560', linewidth=2)
ax.add_patch(rect_a)
ax.text(3, 6.5, 'PICO A — MASTER', ha='center', fontsize=16, fontweight='bold', color='#e94560')
ax.text(3, 6.0, 'Grid Controller', ha='center', fontsize=12, color='#aaa')

pico_a_items = [
    ('SPI0: nRF24L01+', '#0f3460'),
    ('I2C: BMI160 IMU (0x68)', '#533483'),
    ('I2C: PCA9685 PWM (0x40)', '#533483'),
    ('ADC: Voltage + Current', '#2d6a4f'),
    ('GPIO: Recycle (2N2222)', '#e94560'),
    ('Motor Driver: 2x DC', '#0f3460'),
    ('PCA9685: 2x Servo', '#533483'),
]

for i, (text, color) in enumerate(pico_a_items):
    y = 5.2 - i * 0.6
    rect = mpatches.FancyBboxPatch((1, y - 0.2), 4, 0.45, boxstyle="round,pad=0.05",
                                     facecolor=color, edgecolor='white', linewidth=0.5)
    ax.add_patch(rect)
    ax.text(3, y, text, ha='center', va='center', fontsize=10, color='white')

# Pico B box
rect_b = mpatches.FancyBboxPatch((8.5, 1), 5, 6, boxstyle="round,pad=0.2",
                                   facecolor='#16213e', edgecolor='#2d6a4f', linewidth=2)
ax.add_patch(rect_b)
ax.text(11, 6.5, 'PICO B — SLAVE', ha='center', fontsize=16, fontweight='bold', color='#2d6a4f')
ax.text(11, 6.0, 'SCADA Station', ha='center', fontsize=12, color='#aaa')

pico_b_items = [
    ('SPI0: nRF24L01+', '#0f3460'),
    ('SPI1: MAX7219 7-Seg', '#533483'),
    ('I2C: SSD1306 OLED', '#533483'),
    ('Onboard LED: Heartbeat', '#2d6a4f'),
]

for i, (text, color) in enumerate(pico_b_items):
    y = 5.2 - i * 0.6
    rect = mpatches.FancyBboxPatch((9, y - 0.2), 4, 0.45, boxstyle="round,pad=0.05",
                                     facecolor=color, edgecolor='white', linewidth=0.5)
    ax.add_patch(rect)
    ax.text(11, y, text, ha='center', va='center', fontsize=10, color='white')

# Wireless link
ax.annotate('', xy=(8.3, 4.5), xytext=(5.7, 4.5),
            arrowprops=dict(arrowstyle='<->', color='#ff6b35', lw=3))
ax.text(7, 5.0, 'nRF24L01+\n2.4GHz Wireless\n250kbps', ha='center', fontsize=11,
        fontweight='bold', color='#ff6b35')
ax.text(7, 3.8, '6 packet types\n32 bytes each\n0% error rate', ha='center', fontsize=9, color='#aaa')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '04-architecture.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  [4/8] System architecture diagram")


# ============================================================
# 5. Scoring Radar Chart
# ============================================================
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
fig.patch.set_facecolor('#1a1a2e')
ax.set_facecolor('#16213e')

categories_radar = ['Problem Fit\n(30)', 'Live Demo\n(25)', 'Technical\n(20)',
                    'Innovation\n(15)', 'Documentation\n(10)']
values = [28, 22, 18, 14, 9]  # our estimated scores
max_values = [30, 25, 20, 15, 10]

angles = np.linspace(0, 2 * np.pi, len(categories_radar), endpoint=False).tolist()
values += values[:1]
max_values += max_values[:1]
angles += angles[:1]

ax.plot(angles, max_values, 'o--', color='#444', linewidth=1, label='Maximum')
ax.fill(angles, max_values, alpha=0.1, color='#444')
ax.plot(angles, values, 'o-', color='#2d6a4f', linewidth=2.5, label=f'GridBox ({sum(values[:-1])}/100)')
ax.fill(angles, values, alpha=0.25, color='#2d6a4f')

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories_radar, fontsize=12, fontweight='bold')
ax.set_ylim(0, 35)
ax.set_yticks([10, 20, 30])
ax.set_yticklabels(['10', '20', '30'], fontsize=9, color='#666')
ax.grid(color='#333', linewidth=0.5)
ax.spines['polar'].set_color('#444')

ax.set_title('Scoring Target: 91/100', fontsize=18, fontweight='bold',
             color='#ff6b35', pad=30)
ax.legend(loc='lower right', fontsize=11, facecolor='#16213e', edgecolor='#444')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '05-scoring-radar.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  [5/8] Scoring radar chart")


# ============================================================
# 6. Closed Loop Control Flow
# ============================================================
fig, ax = plt.subplots(figsize=(14, 4))
ax.set_xlim(0, 14)
ax.set_ylim(0, 4)
ax.axis('off')
ax.set_title('Closed-Loop Control — Every 10ms', fontsize=18, fontweight='bold', color='#ff6b35', pad=15)

steps = [
    ('SENSE\n(ADC)', '#e94560', 'Read voltage\n& current'),
    ('CALCULATE\n(KCL/KVL)', '#533483', 'Energy\nbalance'),
    ('DECIDE\n(Firmware)', '#0f3460', 'Optimal\nrouting'),
    ('ROUTE\n(GPIO/PWM)', '#2d6a4f', 'Switch\nMOSFETs'),
    ('VERIFY\n(ADC)', '#e94560', 'Confirm\nresult'),
]

for i, (title, color, desc) in enumerate(steps):
    x = i * 2.7 + 0.5
    rect = mpatches.FancyBboxPatch((x, 1.2), 2.2, 2, boxstyle="round,pad=0.15",
                                     facecolor=color, edgecolor='white', linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x + 1.1, 2.7, title, ha='center', va='center',
            fontsize=13, fontweight='bold', color='white')
    ax.text(x + 1.1, 1.6, desc, ha='center', va='center',
            fontsize=10, color='#ddd')

    if i < len(steps) - 1:
        ax.annotate('', xy=(x + 2.5, 2.2), xytext=(x + 2.2, 2.2),
                    arrowprops=dict(arrowstyle='->', color='#ff6b35', lw=2.5))

# Loop arrow back
ax.annotate('', xy=(0.5, 0.8), xytext=(13.2, 0.8),
            arrowprops=dict(arrowstyle='->', color='#ff6b35', lw=2,
                          connectionstyle='arc3,rad=-0.3'))
ax.text(7, 0.3, '← Loop back (100Hz) →', ha='center', fontsize=12, color='#ff6b35', fontstyle='italic')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '06-control-loop.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  [6/8] Control loop diagram")


# ============================================================
# 7. Fault State Machine
# ============================================================
fig, ax = plt.subplots(figsize=(12, 5))
ax.set_xlim(0, 12)
ax.set_ylim(0, 5)
ax.axis('off')
ax.set_title('Fault Detection State Machine', fontsize=18, fontweight='bold', color='#ff6b35', pad=15)

states = [
    ('NORMAL', 1.5, 3.5, '#2d6a4f'),
    ('DRIFT', 4, 3.5, '#0f3460'),
    ('WARNING', 6.5, 3.5, '#533483'),
    ('FAULT', 9, 3.5, '#e94560'),
    ('EMERGENCY', 10.5, 1.5, '#e94560'),
]

for name, x, y, color in states:
    circle = mpatches.FancyBboxPatch((x - 0.8, y - 0.4), 1.6, 0.8,
                                      boxstyle="round,pad=0.1",
                                      facecolor=color, edgecolor='white', linewidth=1.5)
    ax.add_patch(circle)
    ax.text(x, y, name, ha='center', va='center', fontsize=11, fontweight='bold', color='white')

# Transitions
transitions = [
    (1.5, 4, 'vibration\nincreasing'),
    (4, 6.5, 'RMS > 1g'),
    (6.5, 9, 'RMS > 2g\nsustained'),
    (9, 10.5, 'V < 3.8V'),
]

for x1, x2, label in transitions:
    ax.annotate('', xy=(x2 - 0.9, 3.5), xytext=(x1 + 0.9, 3.5),
                arrowprops=dict(arrowstyle='->', color='#ff6b35', lw=2))
    mid = (x1 + x2) / 2
    ax.text(mid, 4.2, label, ha='center', fontsize=9, color='#aaa')

# Recovery arrow
ax.annotate('', xy=(1.5, 2.8), xytext=(9, 2.8),
            arrowprops=dict(arrowstyle='->', color='#2d6a4f', lw=2,
                          connectionstyle='arc3,rad=0.4'))
ax.text(5.2, 1.8, 'AUTO RECOVERY\n(if vibration subsides)', ha='center',
        fontsize=11, fontweight='bold', color='#2d6a4f')

# Emergency transition
ax.annotate('', xy=(10.5, 2.3), xytext=(9.5, 3.1),
            arrowprops=dict(arrowstyle='->', color='#e94560', lw=2))

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '07-fault-state-machine.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  [7/8] Fault state machine")


# ============================================================
# 8. Wiring Progress
# ============================================================
fig, ax = plt.subplots(figsize=(10, 5))

categories_prog = ['Done', 'TODO', 'Cancelled']
wires = [48, 13, 18]
colors_prog = ['#2d6a4f', '#0f3460', '#e94560']

bars = ax.barh(categories_prog, wires, color=colors_prog, edgecolor='white', linewidth=0.5, height=0.6)

for bar, count in zip(bars, wires):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2.,
            f'{count} wires', va='center', fontsize=14, fontweight='bold', color='white')

ax.set_xlabel('Number of Wires', fontsize=14)
ax.set_title('Wiring Progress: 77% Complete', fontsize=18, fontweight='bold', color='#ff6b35')
ax.set_xlim(0, 60)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#444')
ax.spines['bottom'].set_color('#444')
plt.tight_layout()
plt.savefig(os.path.join(out_dir, '08-wiring-progress.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  [8/8] Wiring progress chart")


print(f"\nAll charts saved to: {out_dir}/")
print("Files:")
for f in sorted(os.listdir(out_dir)):
    if f.endswith('.png'):
        size_kb = os.path.getsize(os.path.join(out_dir, f)) // 1024
        print(f"  {f} ({size_kb}KB)")
