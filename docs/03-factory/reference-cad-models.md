# Reference CAD Models — Conveyor Belt & Sorting Systems

> Free 3D printable models we can use as reference or directly adapt for our GridCell factory.

---

## Quick Summary — Which Model For What

| # | Model | Best For | Difficulty | Link |
|---|-------|----------|-----------|------|
| 1 | Mini Conveyor Belt | Conveyor base with DC motor | Easy | [Printables](https://www.printables.com/model/492442-mini-conveyor-belt-3d-model) |
| 2 | Fully 3D Printed Chain Conveyor | No-hardware belt system | Easy | [MakerWorld](https://makerworld.com/en/models/192994-conveyor-belt-fully-3d-printed) |
| 3 | Automatic Color Sorting Conveyor | **BEST MATCH** — conveyor + servo sorting arms | Medium | [MakerWorld](https://makerworld.com/en/models/1953615-automatic-color-sorting-conveyor) |
| 4 | Turntable Color Sorter | Simple turntable + servo gate | Easy | [Printables](https://www.printables.com/model/31861-color-sorting-machine-arduino-controlled) |
| 5 | 4-Bin Ball Sorter | Multi-bin disc sorting | Medium | [Printables](https://www.printables.com/model/885602-colored-ball-sorter) |

---

## Model 1: Mini Conveyor Belt (Solomon Githu)

**Source:** [Printables](https://www.printables.com/model/492442-mini-conveyor-belt-3d-model) / [Thingiverse](https://www.thingiverse.com/thing:6050953)

![Reference: Mini Conveyor Belt](images/ref_conveyor_belt.png)

### What It Is
A small 3D-printed conveyor belt driven by an N20 DC motor. Two rollers connected by a rubber band or fabric belt. Items ride along the top surface.

### Specs
- **Dimensions:** ~18cm wide x 9cm high x 11cm long
- **Motor:** N20 DC 6V 200RPM (3mm shaft)
- **Belt:** Rubber band or fabric strip wrapped around 2 rollers

### Parts Needed
- 4x corner brackets (3D printed)
- 4x roller supports (3D printed)
- 2x rollers (3D printed cylinders)
- 1x motor support + cover (3D printed, has driver board slot)
- 20+ pairs M3 bolts and nuts
- 1x N20 motor

### How We Use It
- Replace the N20 motor with our DC Motor 1 (same concept — motor drives a roller)
- Mount servo sorting arms along the belt edges
- Items ride along the belt, servos push them into bins at each sorting station
- The belt surface is where weight detection happens (motor current changes with load)

---

## Model 2: Fully 3D Printed Chain Conveyor + Motor Drive

**Source:** [Conveyor](https://makerworld.com/en/models/192994-conveyor-belt-fully-3d-printed) / [Motor Drive](https://makerworld.com/en/models/1801234-motor-drive-for-conveyor-belt-fully-3d-printed)

![Reference: Chain Conveyor](images/ref_chain_conveyor.png)

### What It Is
A conveyor belt where EVERYTHING is 3D printed — including the belt itself. The belt is made of snap-fit chain links (like a tank tread). No screws, no glue, no rubber band.

### Specs
- **Dimensions:** 15cm x 5cm x 3.5cm (mini) or 30cm (standard)
- **Belt:** 84 chain links for 30cm version (all 3D printed, snap together)
- **Motor Drive:** Separate add-on model with DC motor + gear reduction
- **Wheels:** 2 or 4 wheels can be attached

### Parts Needed
- Chain links (3D printed — print as many as needed)
- Frame pieces (3D printed — snap fit)
- Wheels (3D printed)
- Motor drive add-on (3D printed + DC motor)
- Nothing else — fully self-contained

### How We Use It
- Best option if you have access to a 3D printer
- Print the 15cm version for our factory
- Add the motor drive kit — connect to our Motor 1
- Mount servo arms along the sides for sorting stations
- The chain link belt is more durable than a rubber band belt
- Can extend length by printing more chain links

---

## Model 3: Automatic Color Sorting Conveyor (BEST MATCH)

**Source:** [MakerWorld](https://makerworld.com/en/models/1953615-automatic-color-sorting-conveyor)

![Reference: Sorting Conveyor](images/ref_sorting_conveyor.png)

### What It Is
The closest match to our factory design. A full conveyor belt with servo-powered sorting arms that push items off the belt into bins. Uses rack and pinion mechanism — servo rotates a gear, which pushes a rack (straight arm) across the belt.

### Specs
- **Detection:** Adafruit TCS34725 RGB color sensor (we replace with ADC current sensing)
- **Sorting:** 2x high-torque servos with rack & pinion push arms
- **Conveyor:** DC motor-driven belt
- **Controller:** Arduino Uno (we use Pico A)
- **Bins:** Multiple collection bins below the belt

### How The Rack & Pinion Sorting Works
1. Item rides along conveyor belt
2. Sensor detects the item (color sensor in theirs, current sensing in ours)
3. Servo rotates, which turns a small gear (pinion)
4. The gear pushes a straight bar (rack) across the belt
5. The bar pushes the item off the belt into a bin
6. Servo reverses, rack retracts, ready for next item

### Why This Is Our Best Reference
- **Has both conveyor AND sorting** in one design
- **Rack & pinion arms** are more reliable than simple servo arm sweeps
- **Well documented** with step-by-step assembly
- **Easy to adapt** — swap color sensor for current sensing, Arduino for Pico
- **Scalable** — we add more servo stations along the belt for multi-stage sorting

### How We Adapt It
| Their Design | Our Adaptation |
|-------------|---------------|
| TCS34725 color sensor | ADC GP27 motor current sensing (weight) |
| Arduino Uno | Pico A (RP2350) |
| 2 sorting servos | 4x 180-degree servo arms (hazmat, heavy, light, output) |
| — | Add 5x 90-degree servo gates (intake, transfer, HVAC dampers, emergency) |
| — | Add HVAC fan system (Motor 2) |
| Single-stage sorting | Multi-stage: size gap → hazmat → weight → output routing |

---

## Model 4: Turntable Color Sorting Machine

**Source:** [Printables](https://www.printables.com/model/31861-color-sorting-machine-arduino-controlled)

![Reference: Turntable Sorter](images/ref_turntable_sorter.png)

### What It Is
A disc-based sorting machine. Items drop from a hopper into a slot on a rotating disc. The disc brings the item to a sensor, then a second servo rotates to align the correct bin underneath before the item is dropped.

### How It Works (Step by Step)
1. **Hopper** drops a colored object into a slot on the top disc
2. **Top servo** rotates the disc, carrying the item to the sensor position
3. **Color sensor** (TCS3200) reads the RGB values of the item
4. **Bottom servo** rotates to position the correct bin underneath
5. **Top servo** rotates again, item falls through a hole into the bin below
6. Repeat for next item

### Specs
- **Servos:** 2 (top disc rotation + bottom bin selector)
- **Sensor:** TCS3200 color sensor
- **Controller:** Arduino
- **Bins:** Multiple (arranged in a circle below)
- **Items:** Small colored balls, Skittles, M&Ms

### How We Could Use It
- Alternative to the conveyor approach — simpler to build
- Use DC Motor 1 for continuous disc rotation instead of a servo
- Add servo push arms around the disc instead of bottom-rotation sorting
- Less impressive visually than a conveyor line, but easier to build
- Good fallback if we don't have time to build a full conveyor

---

## Model 5: 4-Bin Ball Sorter with Raspberry Pi Camera

**Source:** [Printables](https://www.printables.com/model/885602-colored-ball-sorter) / [Blog](https://raghavmarwah.com/blog/colored-ball-sorter/)

![Reference: Ball Sorter](images/ref_ball_sorter.png)

### What It Is
A rotating disc with 4 ball slots. A camera (PiCam) looks down at each ball, OpenCV detects the color, and the disc rotates to drop the ball into the correct bin. A servo gate opens to release the ball.

### Specs
- **Ball Size:** 15mm diameter
- **Bins:** 4 (one per color)
- **Main Motor:** MG995 servo modified for continuous 360-degree rotation
- **Gate Servo:** SG90 (unmodified)
- **Camera:** Raspberry Pi PiCam
- **Software:** Python + OpenCV for color detection
- **Origin:** BCIT ELEX 4618 school project

### How It Works
1. Balls loaded into slots on the rotating disc (4 slots for speed)
2. Disc rotates — each slot passes under the camera
3. PiCam + OpenCV identifies the ball color
4. Disc continues rotating to the correct bin position
5. SG90 servo gate opens, ball drops into the matching bin
6. Gate closes, disc continues to next ball

### How We Adapt It
| Their Design | Our Adaptation |
|-------------|---------------|
| PiCam + OpenCV | ADC current sensing — no camera needed |
| MG995 continuous servo | DC Motor 1 — same continuous rotation |
| SG90 gate (drops ball) | MG90S push arms — more dramatic for judges |
| 4 color bins | Our bins: SMALL, HAZMAT, HEAVY, LIGHT |
| Color detection | Weight detection via motor current |

---

## My Recommendation

### For the Conveyor Belt:
**Use Model 1 (Mini Conveyor Belt)** as the base design. It's simple, uses a DC motor like ours, and is easy to modify. If you have a 3D printer, **Model 2 (Chain Conveyor)** is even better because nothing else is needed.

### For the Sorting Mechanism:
**Use Model 3 (Automatic Color Sorting Conveyor)** as the primary reference. It already combines conveyor + servo sorting in one design. The rack & pinion push arm mechanism is exactly what we need for our 180-degree servo sorting arms.

### Fallback Plan:
If building a full conveyor is too hard, **Model 4 (Turntable Sorter)** works as a simpler alternative — just a spinning disc with servo arms around it.
