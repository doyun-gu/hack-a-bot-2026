# Conveyor Belt Calculations — Background Worker Task

> Calculate all mechanical dimensions for Billy's conveyor belt design. Write results to docs/03-factory/conveyor-calculations.md. Commit and push.

---

## Context

- Motor: 200RPM DC geared motor, 3-6V, ~2 kg·cm stall torque
- Read docs/02-electrical/motor-specs.md for full motor specs
- Read docs/03-factory/factory-design/factory-layout.md for factory dimensions
- Items to sort: 3D printed blocks 15g-80g
- Belt must carry items from detection point to servo sorting gate

## What to Calculate and Document

Create `docs/03-factory/conveyor-calculations.md` with proper LaTeX equations, Mermaid diagrams, and tables.

### Section 1: Belt Length and Roller Sizing

Calculate:
- Minimum belt length based on factory layout (detection point to sorting gate)
- Roller diameter options (2cm, 3cm, 4cm) — how each affects belt speed
- Belt circumference = 2 × distance between rollers + π × roller diameter
- Belt wrap angle on each roller for grip

Use equations:
$$L_{belt} = 2 \times D_{between\_rollers} + \pi \times d_{roller}$$
$$v_{belt} = \pi \times d_{roller} \times \frac{RPM}{60}$$

### Section 2: Belt Speed at Different PWM Settings

Table showing belt speed for each roller diameter at 25%, 50%, 75%, 100% PWM:
- Account for PWM reducing effective RPM linearly
- Speed in cm/s
- Time for an item to travel full belt length at each speed
- Recommended speed for demo (items visible but not flying off)

### Section 3: Belt Tension and Friction

Calculate:
- Minimum tension to prevent belt slipping on roller
- T_tight / T_slack ratio (capstan equation): $$\frac{T_1}{T_2} = e^{\mu \theta}$$
- Where μ = friction coefficient between belt and roller
- θ = wrap angle in radians
- Different belt materials: rubber band (μ≈0.8), fabric (μ≈0.4), string (μ≈0.3)
- Minimum weight/spring needed to keep belt taut

### Section 4: Maximum Load Capacity

Calculate:
- Motor torque at operating voltage (not stall — use 50% of stall for safety)
- Available torque at roller surface: $$F_{pull} = \frac{T_{motor}}{r_{roller}}$$
- Maximum weight the belt can move: $$m_{max} = \frac{F_{pull}}{\mu_{belt-item} \times g}$$
- Safety margin — recommend max load at 60% of calculated max

### Section 5: Sorting Gate Timing

Calculate:
- Time from detection (current spike on ADC) to item reaching servo gate
- $$t_{travel} = \frac{D_{detection\_to\_gate}}{v_{belt}}$$
- Servo response time (~100ms for MG90S)
- Total delay budget: detection (10ms) + ADC processing (10ms) + wireless (2ms) + servo response (100ms)
- At what belt speed does the item pass the gate before servo can react?
- Maximum belt speed for reliable sorting

### Section 6: Power Consumption

Calculate:
- Motor current at no-load vs loaded belt
- Power consumption: $$P = V \times I$$
- Expected current change per gram of load (for weight sensing)
- ADC resolution for weight detection at each belt speed

### Section 7: Recommended Design Specifications

Final recommendation table for Billy:
- Optimal roller diameter
- Optimal belt length
- Optimal belt material
- Optimal belt speed for demo
- Maximum item weight
- Minimum item weight for detection
- Servo gate distance from detection point
- Required belt tension

### Section 8: 3D Print Specifications for Billy

Exact dimensions Billy needs to print:
- Drive roller (fits motor shaft — measure 6mm D-shaft)
- Idler roller (free-spinning on a bearing or screw)
- Roller support frame (holds both rollers at correct distance)
- Belt guides (prevent belt from tracking sideways)
- Servo mount bracket at sorting gate position

Include:
- All dimensions in mm
- Wall thickness recommendations for PLA
- Infill percentage
- Orientation on print bed
- Estimated print time per part

Use Mermaid diagrams for:
- Side view of belt system with dimensions labelled
- Top view showing item path from detection to gate
- Roller cross-section with shaft hole

Commit: `"Add conveyor belt calculations with equations and specs for Billy"`
