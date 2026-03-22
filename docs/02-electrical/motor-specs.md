# DC Motor Specification — 200RPM 3-6V High Torque Geared

> Technical specs, weight sensing capability, and design constraints for Billy's mechanical build.

---

## Motor Datasheet

| Parameter | Value |
|---|---|
| **Model** | 200RPM High Torque Turbo Geared DC Motor |
| **Voltage range** | 3V – 6V |
| **Rated voltage** | 6V |
| **No-load speed** | ~200 RPM (at 6V) |
| **No-load current** | ~70-100 mA |
| **Stall current** | ~800-1200 mA (at 6V) |
| **Stall torque** | ~1.5-2.5 kg·cm |
| **Gear ratio** | Internal gearbox (high reduction) |
| **Shaft diameter** | ~6mm (D-shape or round, check your unit) |
| **Weight** | ~100g |
| **Mounting** | 2x M3 screw holes on face plate |

---

## Weight Sensing via Current — How Much Can We Detect?

### The Physics

The motor draws more current when it has to work harder (more load on the shaft):

$$I_{motor} = \frac{V_{supply} - K_e \cdot \omega}{R_{winding}}$$

When weight is added to the turntable/conveyor, friction increases, motor torque increases, current increases:

$$\Delta I = \frac{\Delta T}{K_t} = \frac{\Delta m \cdot g \cdot \mu \cdot r}{K_t}$$

Where:
- $\Delta m$ = added mass (kg)
- $g$ = 9.81 m/s²
- $\mu$ = friction coefficient (~0.3 for plastic on plastic)
- $r$ = distance from shaft to where weight sits (m)
- $K_t$ = motor torque constant (Nm/A)

### Estimated Current Change per Gram

For this motor at 6V with a 10cm radius turntable:

| Weight Added | Extra Torque | Extra Current | ADC Change | Detectable? |
|---|---|---|---|---|
| 1g | 0.003 g·cm | ~0.2 mA | ~4 ADC counts | Barely — in noise floor |
| 5g | 0.015 g·cm | ~1 mA | ~20 counts | Marginal — need averaging |
| 10g | 0.03 g·cm | ~2 mA | ~40 counts | **Yes — reliably detectable** |
| 20g | 0.06 g·cm | ~4 mA | ~80 counts | **Yes — clear signal** |
| 50g | 0.15 g·cm | ~10 mA | ~200 counts | **Yes — very clear** |
| 100g | 0.3 g·cm | ~20 mA | ~400 counts | **Yes — strong signal** |
| 200g | 0.6 g·cm | ~40 mA | ~800 counts | **Yes — large change** |
| 500g | 1.5 g·cm | ~100 mA | ~2000 counts | **Yes — massive signal** |
| 1000g (stall risk) | 3.0 g·cm | ~200+ mA | ~4000 counts | Motor may stall |

### ADC Resolution Check

Our ADC setup:
- 1Ω sense resistor
- RP2350 ADC: 12-bit (4096 levels) but `read_u16()` scales to 16-bit (65536)
- 3.3V reference

$$\text{ADC sensitivity} = \frac{3.3V}{65536} = 0.05 \text{ mV per count}$$

$$\text{Current per count} = \frac{0.05 \text{ mV}}{1\Omega} = 0.05 \text{ mA per count}$$

So a 10g item causing ~2mA change = ~40 ADC counts. With 10-sample averaging, this is reliably detectable above noise (~±10 counts).

### Practical Detection Limits

| Detection Quality | Minimum Weight | Best Item Examples |
|---|---|---|
| **Reliable (recommended for demo)** | **20g+** | AA battery (23g), stack of 3 coins (21g), small bottle cap filled with putty |
| **Detectable with averaging** | 10-20g | Single coin (10g), large marble (15g) |
| **Not reliable** | <10g | Paper clip (1g), single button — too close to noise |
| **Maximum before stall risk** | ~500g at 6V | Small phone, heavy toy — motor struggles |

---

## What Billy Needs to Know for Mechatronics Design

### Motor Mounting

```
FRONT VIEW (shaft side):        SIDE VIEW:

    ┌─ M3 hole                    ┌──────────────┐
    │                             │              │
  ╔═╤═══════════╤═╗              │  GEARBOX     │──── shaft (6mm)
  ║ ○    ●      ○ ║              │              │
  ╚═╧═══════════╧═╝              │  MOTOR       │
    │                             │              │
    └─ M3 hole                    └──────┬───────┘
                                         │
                                    wires (2x)
                                   red (+) black (-)
```

| Dimension | Value | Billy Action |
|---|---|---|
| Shaft diameter | ~6mm | **Measure your motor** — 3D print coupling to match exactly |
| Shaft shape | D-shape or round | Check if flat side — affects coupling design |
| M3 mounting holes | 2 holes on front face | 3D print bracket with matching hole spacing — **measure the distance** |
| Motor body | ~25mm diameter × 60mm long (with gearbox) | **Measure yours** — geared motors vary |
| Wire length | ~15cm typically | Enough to reach breadboard — extend if needed |

### Turntable Disc Design

```
TOP VIEW:

         ┌── outer edge (items ride here)
         │
    ╭────┴────╮
   ╱    ╭──╮   ╲
  │     │●●│    │     ● = shaft hole (6mm + tight fit)
   ╲    ╰──╯   ╱     size to friction-fit on shaft
    ╰─────────╯
         │
         └── 15-20cm diameter
```

| Design Parameter | Value | Notes |
|---|---|---|
| Disc diameter | **15-20cm** | Larger = more dramatic but needs more torque |
| Disc thickness | **3-5mm** | Thick enough to be rigid, thin enough to be light |
| Shaft hole | **6mm** (measure motor shaft!) | Tight press-fit or use set screw |
| Material | PLA (3D print) or cardboard + hot glue | PLA is better — more rigid, precise hole |
| Weight of disc | **Keep under 50g** | Heavier disc = less sensitivity to item weight |
| Surface | Slightly rough (not polished) | Items need friction to ride the disc, not slide off |
| Edge lip | **2-3mm raised rim** | Prevents items from flying off at speed |

### Maximum Load Calculation

The motor has ~2 kg·cm stall torque at 6V. We need to stay well below stall:

$$T_{max\_safe} = \frac{T_{stall}}{3} = \frac{2.0}{3} = 0.67 \text{ kg·cm}$$

At 10cm radius (edge of a 20cm disc):

$$m_{max} = \frac{T_{max\_safe}}{g \cdot \mu \cdot r} = \frac{0.67}{0.981 \times 0.3 \times 10} = 0.23 \text{ kg} = 230g$$

**Maximum total load on disc edge: ~230g** (including the disc weight itself).

If disc weighs 50g → maximum item weight: **~180g** at the edge.

If items are closer to the centre (5cm radius) → maximum doubles to **~360g**.

### RPM and Speed

At 200 RPM, the disc edge speed is:

$$v_{edge} = 2\pi r \times \frac{RPM}{60} = 2\pi \times 0.1 \times \frac{200}{60} = 2.1 \text{ m/s}$$

**Edge speed: ~2.1 m/s at full speed.** That's quite fast — items may fly off without a lip.

At 50% PWM (~100 RPM): edge speed ~1.0 m/s — more manageable.

**Recommended demo speed: 30-50% PWM (60-100 RPM)** — items stay on the disc, servos have time to sort.

### Items to 3D Print for Demo

Billy should 3D print test items of known weight:

| Item | Target Weight | Print Settings | Purpose |
|---|---|---|---|
| **Light test block** | ~15g | Small cube, 20% infill | Below threshold → REJECT (too light) |
| **Normal test block** | ~40g | Medium cube, 50% infill | Within threshold → PASS |
| **Heavy test block** | ~80g | Large cube, 80% infill | Above threshold → REJECT (too heavy) |
| **Reference calibration** | Exactly 50g | Adjust infill until scale reads 50g | For calibration routine |

**Label each with weight written on it** — judges can see what weight the system is sorting.

Approximate PLA weights for solid cubes:

| Cube Size | 20% Infill | 50% Infill | 80% Infill | 100% Infill |
|---|---|---|---|---|
| 2×2×2 cm | ~3g | ~5g | ~7g | ~10g |
| 3×3×3 cm | ~8g | ~16g | ~22g | ~33g |
| 4×4×4 cm | ~20g | ~40g | ~55g | ~78g |
| 5×5×5 cm | ~38g | ~75g | ~105g | ~152g |

**Recommended: 3cm and 4cm cubes** at different infills give the 15g/40g/80g range we need.

---

## Conveyor Belt Considerations

If using Motor 2 for a conveyor belt instead of a turntable:

| Parameter | Value |
|---|---|
| Belt speed at 200 RPM (6cm roller) | ~63 cm/s — **very fast** |
| Belt speed at 50% PWM | ~31 cm/s — better for demo |
| Belt speed at 20% PWM | ~13 cm/s — **ideal for demo** (items visible moving) |
| Maximum belt load | ~200g distributed across belt |
| Belt material | Rubber band, fabric strip, or timing belt |
| Roller diameter | 2-3cm (3D print) — larger = faster belt |
| Belt tension | Must be tight enough to not slip on roller |

**Key dimension for firmware:** Billy must measure and tell Doyun the **distance from the detection point (motor/roller) to the servo sorting gate** in centimetres. This goes into `config.py`:

```python
BELT_LENGTH_CM = XX     # Billy measures this
BELT_SPEED_CM_PER_S = XX  # calibrate at chosen PWM %
```

---

## Power Supply for Motors

| Voltage | Speed | Current (no load) | Recommended Use |
|---|---|---|---|
| 3V | ~100 RPM | ~50 mA | Too slow for demo |
| 4.5V | ~150 RPM | ~70 mA | Slow but visible |
| 6V | ~200 RPM | ~100 mA | Full speed — may be too fast |
| **5V (from buck converter)** | **~170 RPM** | **~80 mA** | **Best for demo — use existing 5V rail** |

Or use the 300W buck-boost converter set to 6V for the motor power rail (separate from logic 5V).

**Important:** Don't run motors directly from the Pico's 5V pin — use the buck converter or buck-boost with MOSFET switching as designed.

---

## Summary for Billy

| Question | Answer |
|---|---|
| How heavy can items be? | **Up to ~180g** on disc edge (20cm disc, 50g disc weight) |
| What's the minimum detectable weight? | **~20g reliably**, ~10g with averaging |
| What RPM for demo? | **60-100 RPM** (30-50% PWM) — items stay on disc |
| How big should the turntable be? | **15-20cm diameter** — bigger is more dramatic |
| How thick should the disc be? | **3-5mm** — rigid but light |
| What test items to print? | **3cm + 4cm cubes at 20%/50%/80% infill** → 15g/40g/80g |
| What dimensions must I tell Doyun? | Shaft diameter, mounting hole spacing, disc radius, belt length to servo |
