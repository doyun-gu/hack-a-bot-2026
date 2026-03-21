# Factory Options v2 — Specific, Detailed Proposals

> Each factory is evaluated against the same hardware kit and the same scoring rubric.
> The firmware/electronics are identical for all — only the physical layout, OLED labels, and narrative change.

---

## Hardware We Must Use (Non-Negotiable)

| Actuator | Physical Capability | Constraint |
|---|---|---|
| DC Motor 1 (via MOSFET) | Continuous rotation, variable speed via PWM | ~6-12V, moderate torque. Can spin a disc, roller, fan blade, drum |
| DC Motor 2 (via MOSFET) | Continuous rotation, variable speed via PWM | Same as above |
| Servo 1 (via PCA9685) | Precise 0-180° swing | MG90S — small, fast, audible click. Good for gates, pushers, flaps |
| Servo 2 (via PCA9685) | Precise 0-180° swing | Same as above |

| Sensor | What It Actually Measures | How We Use It |
|---|---|---|
| BMI160 IMU | Acceleration + gyro on 3 axes | Mounted on a motor → vibration = equipment health. Judge shakes it = fault injection |
| ADC × 3 | Voltage (0-3.3V analog) | Bus voltage + 2× motor current via sense resistors |
| Potentiometer | Rotary position (analog) | User setpoint: "production speed" or "demand level" |
| Joystick | X/Y analog + button | Manual override + fault reset |

| Output | What Judges See |
|---|---|
| OLED 128×64 | 4-screen SCADA dashboard (power, status, faults, savings) |
| 4× status LEDs | Tower: green/yellow/red/blue — visible from 3 metres |
| 4× load LEDs | Priority shedding: P1-P4 turn off in order when overloaded |

---

## What Makes a Good Factory for This Project

The factory is a **skin** over the real innovation (smart power management + fault detection). But it matters enormously for scoring:

| Scoring Category | What the Factory Choice Affects |
|---|---|
| **Problem Definition (30pts)** | Does this factory have a real-world energy waste problem? Can we cite stats? |
| **Live Demo (25pts)** | Can judges SEE things moving? Is there a dramatic fault moment? |
| **Innovation (15pts)** | Does the factory make the "£15 vs £162K" story believable? |
| **Technical (20pts)** | Does the factory use ALL components in meaningful roles? |

**The ideal factory:**
1. Every actuator has a **named, logical role** (not "Motor 2 is... a fan I guess")
2. There's a clear **production flow** — input → process → output
3. The **sustainability story writes itself** — obvious energy waste problem in that industry
4. **Physical items move** — judges remember things they can touch
5. **Fault injection is natural** — shaking a motor makes sense in context
6. **Build time ≤ 3 hours** — cardboard + hot glue + maybe 3D print one part

---

## Factory 1: Recycling Centre — Material Recovery Facility (MRF)

> Mixed waste arrives on a spinning turntable. The system identifies material type and sorts recyclables from landfill. A cooling fan prevents motor overheating during high-throughput shifts.

### The Real-World Problem
- UK sends **11 million tonnes** of recyclable waste to landfill every year
- Manual sorting costs **£80-120/tonne** and workers face injury from contaminated waste
- Automated MRFs cost **£2-5 million** to build — councils can't afford them
- **Contamination rates** of 25-30% mean "recycled" waste often ends up in landfill anyway

### Component Mapping

| Component | Factory Role | Why It Makes Sense |
|---|---|---|
| DC Motor 1 | **Sorting turntable** — spins the disc where mixed waste sits | Real MRFs use rotating trommels and disc screens |
| DC Motor 2 | **Extraction fan** — removes dust/fumes from sorting area | Real MRFs have ventilation systems for worker safety |
| Servo 1 | **Recyclable diverter** — pushes recyclable items into green bin | Real MRFs use pneumatic pushers on belt lines |
| Servo 2 | **Landfill diverter** — pushes contaminated items into red bin | Same mechanism, different position on the line |
| BMI160 IMU | **Turntable bearing monitor** — detects jammed items or worn bearing | Real MRFs monitor conveyor bearings for predictive maintenance |
| Potentiometer | **Throughput dial** — sets processing speed (tonnes/hour) | Operators adjust line speed based on incoming volume |
| Joystick | **Emergency stop + reset** | Every MRF has an e-stop panel |
| OLED | **SCADA: items sorted, contamination rate, energy use, faults** | Real MRFs have control room dashboards |
| LEDs (status) | **Safety tower** — green/yellow/red like real industrial indicators | Standard in every factory |
| LEDs (load) | **Power zones** — sorting, ventilation, lighting, auxiliary | Shows load shedding priority |

### Physical Build

```
┌─────────────────────────────────────┐
│          RECYCLING CENTRE           │
│                                     │
│   [Mixed waste]                     │
│       ↓                             │
│   ┌───────────┐     ┌──────────┐   │
│   │ TURNTABLE │────→│ GREEN BIN│   │
│   │ (Motor 1) │     │ Recycle  │   │
│   │   ◉ disc  │     └──────────┘   │
│   │           │     ┌──────────┐   │
│   │  servo1→──│────→│ RED BIN  │   │
│   │  servo2→──│     │ Landfill │   │
│   └───────────┘     └──────────┘   │
│                                     │
│   [Fan - Motor 2]    [IMU on M1]   │
│   [LED tower]        [Pico A]      │
│                                     │
│ ─ ─ ─ wireless ─ ─ ─ ─ ─ ─ ─ ─ ─ │
│                                     │
│   CONTROL ROOM: [OLED] [Joystick]  │
│                  [Pot]  [Pico B]   │
└─────────────────────────────────────┘
```

**Materials:** Cardboard disc (15cm) hot-glued to motor shaft, two small cups/boxes as bins, cardboard ramps to guide items, servo horns as push arms, labels.

**Items to sort:** Coloured bottle caps (green caps = recyclable, red caps = landfill). Or small blocks with stickers.

### Demo Script (30 seconds)

| Step | Action | Judge Sees | Judge Hears You Say |
|---|---|---|---|
| 1 | Power on | System boots, LEDs light up, OLED shows dashboard | "This is a recycling centre powered by recovered energy" |
| 2 | Drop mixed waste | Place 5 bottle caps on turntable | "Mixed waste arrives — plastics, metals, contaminated" |
| 3 | Auto-sort | Turntable spins, servos push caps into correct bins | "The system identifies and sorts autonomously — no human needed" |
| 4 | Turn dial | Potentiometer → turntable speeds up, servos fire faster | "Shift change — demand goes up, system adapts" |
| 5 | Shake motor | IMU triggers fault, turntable stops, power reroutes | "Bearing failure detected. Motor isolated. Power redirected to fan" |
| 6 | Reset | Joystick press → system recovers | "Self-healing. OLED shows: 52% energy saved vs legacy system" |

### Sustainability Narrative (for 30-point Problem Definition)
- "The UK wastes 11M tonnes of recyclable material. Manual sorting costs £80/tonne. Automated MRFs cost millions. GridBox brings smart sorting to small councils for £15."
- Energy recycling angle: "When the turntable is running slow (low demand), excess power goes to the ventilation fan. No wasted watts."
- Affinity Laws: "Running the turntable at 80% speed uses 49% less power. Smart mode vs dumb mode."

### Score Prediction: 94/100

| Category | Score | Reasoning |
|---|---|---|
| Problem Definition | 28/30 | Recycling is universally understood. Real stats. Real UK problem. |
| Live Demo | 24/25 | Items physically moving into bins. Dramatic fault. Interactive. |
| Technical | 20/20 | All components used meaningfully. Dual-core, wireless, sensing. |
| Innovation | 13/15 | Good but "sorting" is a common hackathon concept |
| Docs | 9/10 | Strong with diagrams and equations |

---

## Factory 2: Pharmaceutical Tablet Inspection Line

> Tablets travel on a spinning inspection disc. The system monitors vibration signatures to detect cracked/malformed tablets and diverts them to quarantine. A ventilation fan maintains clean-room airflow.

### The Real-World Problem
- **1 in 10** medicines in low-income countries are **substandard or falsified** (WHO, 2017)
- Manual visual inspection catches only **60-70%** of defects
- Automated pharma inspection systems cost **£200K-500K** per line
- UK MHRA requires **100% batch traceability** — every reject must be logged
- Small generic drug manufacturers in developing countries have **zero QC automation**

### Component Mapping

| Component | Factory Role | Why It Makes Sense |
|---|---|---|
| DC Motor 1 | **Inspection turntable** — tablets sit on disc, rotate past inspection point | Real pharma lines use rotary inspection tables |
| DC Motor 2 | **Clean-room ventilation fan** — maintains positive air pressure | Pharma manufacturing requires ISO Class 7+ cleanrooms |
| Servo 1 | **PASS gate** — pushes good tablets toward packaging | Real lines use air jets or mechanical pushers |
| Servo 2 | **QUARANTINE diverter** — pushes failed tablets into quarantine bin | Defective tablets must be physically separated and logged |
| BMI160 IMU | **Vibration QC sensor** — mounted on turntable, detects abnormal vibration from cracked/chipped tablets | Real lines use vibration + vision. We simulate the vibration aspect |
| Potentiometer | **Production rate dial** — tablets per minute target | Operators set line speed based on batch schedule |
| Joystick | **Batch reset + manual quarantine override** | Pharmacists can manually flag suspicious tablets |
| OLED | **SCADA: batch count, pass/fail rate, contamination %, energy** | Real pharma SCADA shows OEE (Overall Equipment Effectiveness) |
| Status LEDs | **GMP compliance tower** — green=GMP OK, yellow=deviation, red=batch hold | Standard in pharma manufacturing |
| Load LEDs | **Facility zones** — inspection, HVAC, lighting, auxiliary | Load shedding shows energy management |

### Physical Build

```
┌──────────────────────────────────────┐
│     PHARMACEUTICAL INSPECTION LINE   │
│     "GridPharma QC Station"          │
│                                      │
│   [Tablet hopper]                    │
│       ↓                              │
│   ┌────────────┐    ┌───────────┐   │
│   │ INSPECTION │───→│ PASS      │   │
│   │  TURNTABLE │    │ (package) │   │
│   │  (Motor 1) │    └───────────┘   │
│   │    ◉       │    ┌───────────┐   │
│   │ servo1 →───│───→│ QUARANTINE│   │
│   │ servo2 →───│    │ (logged)  │   │
│   └────────────┘    └───────────┘   │
│                                      │
│   [Cleanroom Fan]   [IMU on M1]     │
│   (Motor 2)         [LED tower]     │
│                                      │
│ ─ ─ ─ ─ wireless ─ ─ ─ ─ ─ ─ ─ ─  │
│                                      │
│   QC LAB: [OLED] [Joystick] [Pot]   │
└──────────────────────────────────────┘
```

**Materials:** Same turntable as recycling, but labelled "INSPECTION DISC." Bins labelled "PASS → PACKAGING" and "QUARANTINE." White cardboard enclosure to look clinical.

**Items:** Small round mints, Smarties, or 3D-printed tablet shapes. Or just small white discs cut from foam.

### Demo Script

| Step | Action | Judge Sees | You Say |
|---|---|---|---|
| 1 | Power on | Clean startup, fan spins, OLED: "BATCH 001 READY" | "This is a tablet inspection line. Every pill you take was checked by a system like this." |
| 2 | Load tablets | Place mints/discs on turntable | "Batch of 500mg paracetamol tablets entering QC" |
| 3 | Auto-inspect | Disc spins, servos push: most to PASS, some to QUARANTINE | "Good tablets pass. The system caught 3 defects — cracked, wrong weight, contaminated" |
| 4 | Turn dial | Speed up production rate | "Rush order came in. Line speeds up. System adapts energy automatically" |
| 5 | Shake motor | IMU triggers → "BATCH HOLD" → turntable stops | "Vibration anomaly. Could be a cracked bearing contaminating tablets. Line halted." |
| 6 | Reset | Joystick → resume, OLED: "47% energy saved" | "Maintenance cleared it. System self-heals. And we saved 47% energy vs running at full speed 24/7" |

### Sustainability Narrative
- "Pharma factories run 24/7 at full power even when demand is low. Our system scales energy to match production rate — Affinity Laws mean 20% slower = 49% less power."
- "In developing countries, there's no QC automation at all. Substandard medicines kill 250,000 children annually (WHO). £15 could change that."
- Cleanroom HVAC is **40-60% of pharma factory energy costs** — smart fan control directly addresses this.

### Score Prediction: 95/100

| Category | Score | Reasoning |
|---|---|---|
| Problem Definition | 29/30 | Life-or-death problem. WHO stats. Developing world angle. |
| Live Demo | 24/25 | Same turntable mechanics, but "quarantine" framing adds drama |
| Technical | 20/20 | Identical circuit, all components justified |
| Innovation | 13/15 | Pharma angle is unusual for hackathons — stands out |
| Docs | 9/10 | GMP terminology impresses if judges are engineers |

---

## Factory 3: Coffee Roasting & QC Facility

> Green coffee beans enter a rotating roasting drum. After roasting, beans pass a vibration-based quality check. Good beans go to packaging; burnt/underweight beans are rejected. A cooling fan prevents over-roasting.

### The Real-World Problem
- Specialty coffee is a **£80 billion** global industry
- Small-batch roasters lose **15-25%** of beans to over-roasting, under-roasting, or defects
- Professional roasting monitoring systems (Cropster, Artisan + probes) cost **£5K-15K**
- Energy waste: most small roasters run exhaust fans and drum motors at **100% all day** regardless of batch size
- Coffee roasting produces **CO₂ and chaff** — ventilation is critical for safety and quality

### Component Mapping

| Component | Factory Role | Why It Makes Sense |
|---|---|---|
| DC Motor 1 | **Roasting drum** — rotates to ensure even roasting | Every drum roaster has a rotating drum driven by a motor |
| DC Motor 2 | **Cooling tray fan** — cools beans immediately after roasting to stop the cook | Real roasters dump beans onto a cooling tray with a fan underneath |
| Servo 1 | **Drum release gate** — opens to dump roasted beans onto cooling tray | Real roasters have a manual or automated dump door |
| Servo 2 | **QC diverter** — pushes cooled beans to PASS or REJECT | After cooling, beans pass a colour/density check |
| BMI160 IMU | **Drum bearing monitor** — detects imbalanced load or worn bearing | Roasting drums spin at 40-60 RPM; vibration indicates uneven bean distribution or mechanical wear |
| Potentiometer | **Roast level dial** — light / medium / dark roast (controls drum speed + time) | Roasters constantly adjust based on bean origin and desired profile |
| Joystick | **Emergency dump + manual roast override** | Sometimes you need to dump early if beans are burning |
| OLED | **SCADA: roast time, drum temp (simulated), bean count, energy, faults** | Professional roasters watch temperature curves in real-time |
| Status LEDs | **Roast stage: green=heating, yellow=first crack, red=second crack/danger** | Colour-coded roast progression is intuitive |
| Load LEDs | **Facility zones: drum motor, fan, lighting, chaff collector** | Load shedding priority |

### Physical Build

```
┌──────────────────────────────────────────┐
│        COFFEE ROASTING FACILITY          │
│        "GridRoast QC Line"               │
│                                          │
│   [Green beans in]                       │
│       ↓                                  │
│   ┌──────────┐    ┌──────────────────┐  │
│   │ ROASTING │    │ COOLING TRAY     │  │
│   │  DRUM    │───→│ (Fan = Motor 2)  │  │
│   │(Motor 1) │    │                  │  │
│   │ ◉ rotate │    │ servo1 = dump    │  │
│   └──────────┘    │ servo2 = QC sort │  │
│                    │   ↙        ↘     │  │
│                    │ PASS    REJECT   │  │
│                    └──────────────────┘  │
│                                          │
│   [IMU on drum]  [LED tower]  [Pico A]  │
│                                          │
│ ─ ─ ─ ─ ─ wireless ─ ─ ─ ─ ─ ─ ─ ─ ─  │
│                                          │
│   ROAST LAB: [OLED] [Joystick] [Pot]    │
└──────────────────────────────────────────┘
```

**Materials:** Small cardboard cylinder (toilet roll tube) on motor shaft = roasting drum. Open cardboard tray with fan underneath = cooling station. Two cups = PASS + REJECT.

**Items:** Dried beans, small beads, or brown-painted pebbles. Anything that looks like coffee beans from a distance.

### Demo Script

| Step | Action | You Say |
|---|---|---|
| 1 | Power on | "This is a smart coffee roastery. Drum, cooler, QC — all powered by recovered energy." |
| 2 | Load beans, drum spins | "Green beans enter the roasting drum. Motor speed controls roast evenness." |
| 3 | Servo 1 dumps beans | "First crack reached. Beans dump to cooling tray. Fan kicks up to stop the cook." |
| 4 | Servo 2 sorts | "QC check — good beans to packaging, rejects removed. Consistent quality." |
| 5 | Turn potentiometer | "Dark roast order — drum slows, roast time extends. Energy adjusts automatically." |
| 6 | Shake drum motor | "Bearing failure! Drum stops. Beans could burn. Fan maxes out to emergency-cool." |
| 7 | Reset + savings | "System recovered. OLED: 48% energy saved vs running everything at full blast all day." |

### Sustainability Narrative
- "Coffee roasting consumes 2-5 kWh per kg of beans. Small roasters waste energy running equipment at 100% between batches."
- "Our system idles the drum between batches and scales the cooling fan to match batch size. Affinity Laws: 20% slower fan = 49% less power."
- "The global coffee industry produces 16 million tonnes per year. Even 10% energy savings = massive impact."

### Why It's Interesting
- **Everyone drinks coffee** — instant emotional connection for judges
- **Multi-stage production flow** — roast → cool → sort, not just "spin and push"
- The drum is a **different visual** from a flat turntable — more industrial looking
- **Roast level dial** gives the potentiometer a very natural, intuitive role
- Emergency dump is a **dramatic demo moment** — "the beans are burning!"

### Score Prediction: 93/100

| Category | Score | Reasoning |
|---|---|---|
| Problem Definition | 27/30 | Good sustainability angle but "coffee roasting" is less critical than pharma/recycling |
| Live Demo | 25/25 | Multi-stage flow, dramatic "burning beans" fault, very tactile |
| Technical | 20/20 | All components used well |
| Innovation | 13/15 | Unusual factory choice — memorable |
| Docs | 8/10 | Good but less "serious" than infrastructure |

---

## Factory 4: E-Waste Battery Sorting & Recovery Plant

> Used batteries arrive on a spinning sorting disc. The system checks vibration signatures (loose internals = damaged), sorts good batteries for reconditioning and damaged ones for safe disposal. A ventilation fan extracts toxic fumes.

### The Real-World Problem
- **78 million** lithium-ion batteries reach end-of-life **every year** in the UK
- Only **5%** of lithium batteries are currently recycled (Royal Society of Chemistry)
- Improper disposal causes **fires** in waste facilities — 700+ fire incidents in UK recycling centres (2019-2022)
- Battery sorting is done **manually** — workers handle potentially hazardous cells by hand
- Automated battery sorting systems cost **£500K+** — most councils don't have them
- **EU Battery Regulation 2023** mandates 70% collection rate by 2030 — infrastructure doesn't exist yet

### Component Mapping

| Component | Factory Role | Why It Makes Sense |
|---|---|---|
| DC Motor 1 | **Sorting disc** — batteries placed on spinning platform, pass inspection points | Real battery MRFs use conveyor + robotic sorting |
| DC Motor 2 | **Fume extraction fan** — removes off-gassing from damaged lithium cells | Critical safety system in real battery facilities — thermal runaway produces toxic HF gas |
| Servo 1 | **RECONDITION diverter** — pushes healthy batteries toward second-life testing | Batteries with >80% capacity can be reused in grid storage |
| Servo 2 | **HAZMAT diverter** — pushes damaged/swollen batteries into sealed containment | Damaged lithium cells must be isolated — fire/explosion risk |
| BMI160 IMU | **Cell integrity sensor** — vibration signature of a battery with loose internals differs from a healthy cell | Real facilities use X-ray and impedance testing. We simulate with vibration |
| Potentiometer | **Throughput control** — processing rate (cells/minute) | Operators adjust based on incoming volume and staffing |
| Joystick | **Emergency shutdown + thermal event override** | Battery fires require immediate line shutdown |
| OLED | **SCADA: cells processed, pass/fail rate, thermal alerts, energy use** | Real battery facilities have intensive monitoring |
| Status LEDs | **Safety: green=normal, yellow=elevated temp, red=thermal event** | Thermal runaway is the #1 fear in battery processing |
| Load LEDs | **Facility zones: sorting, extraction, containment cooling, lighting** | Load shedding: extraction fan is NEVER shed (safety critical) |

### Physical Build

```
┌───────────────────────────────────────────┐
│     E-WASTE BATTERY RECOVERY PLANT        │
│     "GridCell Sorting Facility"            │
│                                           │
│   [Mixed batteries in]                    │
│       ↓                                   │
│   ┌────────────┐    ┌────────────────┐   │
│   │  SORTING   │───→│ RECONDITION    │   │
│   │   DISC     │    │ (second life)  │   │
│   │ (Motor 1)  │    └────────────────┘   │
│   │    ◉       │    ┌────────────────┐   │
│   │ servo1→────│───→│ HAZMAT         │   │
│   │ servo2→────│    │ (safe dispose) │   │
│   └────────────┘    └────────────────┘   │
│                                           │
│   [EXTRACTION FAN]  [IMU on disc]        │
│   (Motor 2)         [LED tower]          │
│   ⚠ NEVER SHEDS     [Pico A]            │
│                                           │
│ ─ ─ ─ ─ wireless ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │
│                                           │
│   CONTROL ROOM: [OLED] [Joystick] [Pot]  │
└───────────────────────────────────────────┘
```

**Materials:** Same turntable disc. Bins labelled "SECOND LIFE" (green) and "HAZMAT DISPOSAL" (red with ⚠ symbol). Yellow hazard tape on the build adds drama.

**Items:** AA/AAA batteries (actual dead batteries are perfect props), or small cylinders.

### Demo Script

| Step | Action | You Say |
|---|---|---|
| 1 | Power on, fan starts | "This is a battery recovery plant. That fan is extracting toxic fumes — it never turns off." |
| 2 | Drop batteries on disc | "Mixed e-waste batteries. Some are good for second-life storage. Some are swollen and dangerous." |
| 3 | Auto-sort | "Healthy cells to reconditioning. Damaged cells to hazmat containment. Autonomous." |
| 4 | Turn dial up | "Shipment surge — processing rate increases. Energy scales to match." |
| 5 | Shake motor | "Jammed cell! Sorting disc halted. Fan STAYS ON — safety critical. Power rerouted from disc to fan." |
| 6 | Reset + savings | "OLED: 89 cells processed, 12 hazmat. 51% energy saved. Zero thermal events." |

### Sustainability Narrative
- "78 million lithium batteries hit end-of-life in the UK every year. Only 5% are recycled."
- "The EU Battery Regulation mandates 70% collection by 2030. The infrastructure doesn't exist."
- "Our system sorts batteries safely for £15. A real automated line costs £500K+."
- **Unique angle:** The extraction fan being safety-critical means it's **never load-shed**. This demonstrates intelligent priority-based power management — not everything is equal. Judges can see P1 (fan) LED stays on even when other loads are shed.

### Why It's Strong
- **Topical** — e-waste, lithium battery fires, and EU regulations are in the news constantly
- **Safety narrative is powerful** — "that fan never turns off because lithium fires produce hydrogen fluoride gas" is a sentence that wakes judges up
- **Load shedding priority is visible** — fan LED (P1) NEVER goes off, even during overload. Other loads shed around it. This demonstrates the intelligence better than any other factory
- **Real dead batteries as props** — judges can pick them up and drop them on the turntable. Tactile and real

### Score Prediction: 96/100

| Category | Score | Reasoning |
|---|---|---|
| Problem Definition | 29/30 | EU regulation, fire risk, developing crisis. Urgent and specific |
| Live Demo | 25/25 | Batteries as props are real. Fan staying on during fault is dramatic |
| Technical | 20/20 | Safety-critical load priority adds genuine technical depth |
| Innovation | 13/15 | E-waste angle is unusual and timely |
| Docs | 9/10 | Regulatory citations strengthen documentation score |

---

## Factory 5: Precision Seed Sorting for Vertical Farms

> Seeds are loaded onto a spinning grading disc. Viable seeds are diverted to planting trays, non-viable seeds (cracked, undersized) are rejected. An airflow fan maintains optimal germination temperature.

### The Real-World Problem
- Vertical farming market growing at **25% CAGR** — expected to reach $20B by 2028
- Seed viability rates vary **60-95%** — planting non-viable seeds wastes space, water, nutrients
- Industrial seed sorters (optical + air jet) cost **£50K-200K**
- A vertical farm planting non-viable seeds wastes **water, energy, and growing space** for 2-4 weeks before discovering the seed failed
- UK food strategy calls for increased **domestic food production** — vertical farms are key

### Component Mapping

| Component | Factory Role | Why It Makes Sense |
|---|---|---|
| DC Motor 1 | **Grading disc** — seeds rotate past inspection points | Real seed graders use vibrating tables and rotating discs |
| DC Motor 2 | **Climate fan** — maintains airflow over germination trays | Real vertical farms control temperature/humidity precisely |
| Servo 1 | **VIABLE chute gate** — directs good seeds to planting tray | Automated seeders have mechanical gates |
| Servo 2 | **REJECT chute gate** — diverts bad seeds to compost | Non-viable seeds are composted, not wasted |
| BMI160 IMU | **Vibration grading** — on the disc, vibration pattern changes with seed density/integrity | Real graders use vibration and density sorting |
| Potentiometer | **Viability threshold** — how strict is the QC? (adjustable sensitivity) | Farmers adjust based on crop value |
| Joystick | **Manual override + seed type selector** | Different crops need different thresholds |
| OLED | **SCADA: seeds/min, viability %, planting queue, energy, climate** | Vertical farm control systems show this data |

### Physical Build

**Materials:** Cardboard disc, two small trays (one with soil/green paper = "planting", one empty = "compost"). Actual seeds (sunflower, pumpkin) are great props — cheap, visible, relevant.

**Items:** Sunflower seeds — large enough to see, cheap, everyone recognises them.

### Sustainability Narrative
- "Every non-viable seed planted wastes 2 weeks of water, LED energy, and nutrients. Pre-sorting saves 20-30% of vertical farm operating costs."
- "The UK imports 40% of its food. Vertical farms can grow locally, year-round. But they need automation to be economically viable."
- Affinity Laws on the climate fan: "Running the fan at 80% saves 49% energy — perfect for off-peak growing cycles."

### Score Prediction: 91/100

| Category | Score | Reasoning |
|---|---|---|
| Problem Definition | 27/30 | Good sustainability angle, growing industry, but less urgent than waste/pharma |
| Live Demo | 23/25 | Seeds are small — less visually dramatic than batteries or bottle caps |
| Technical | 20/20 | All components used well |
| Innovation | 13/15 | Vertical farming is trendy and relevant |
| Docs | 8/10 | Solid |

---

## Factory 6: Precious Metal Recovery from Circuit Boards

> Shredded e-waste PCB fragments arrive on a separation disc. The system sorts metallic fragments (gold, copper, tin) from non-metallic waste (plastic, fibreglass). A fume extraction fan handles toxic dust.

### The Real-World Problem
- **1 tonne of circuit boards** contains more gold than **1 tonne of gold ore** (40-800x richer)
- Global e-waste reached **62 million tonnes** in 2022 — only **22%** was properly recycled
- Precious metal recovery from e-waste is worth **£48 billion/year** globally
- Small-scale e-waste recyclers in developing countries use **acid baths** and **open burning** — lethal to workers
- Automated separation costs **£1M+** — most facilities sort by hand

### Component Mapping

| Component | Factory Role | Why |
|---|---|---|
| DC Motor 1 | **Separation disc** — fragments spin past sorting stations | Real plants use eddy current separators and shaking tables |
| DC Motor 2 | **Fume extraction** — removes toxic PCB dust (lead, brominated flame retardants) | Safety-critical, similar to battery plant |
| Servo 1 | **Metal recovery gate** — pushes metallic fragments to smelting queue | Valuable output stream |
| Servo 2 | **Waste diverter** — pushes non-metallic waste to disposal | Low-value output |
| BMI160 IMU | **Shredder health monitor** — vibration on the disc detects jams or worn parts | Real shredders are monitored for bearing health |
| Potentiometer | **Feed rate** — how fast new material enters the separation disc | Operators control throughput |

### Sustainability Narrative
- "There's more gold in a tonne of phones than a tonne of gold ore. But we throw most of it in landfill."
- "Informal e-waste workers burn circuit boards in open air — poisoning themselves and their communities. Automation saves lives."
- Safety-critical fan angle works here too.

### Score Prediction: 93/100

| Category | Score | Reasoning |
|---|---|---|
| Problem Definition | 28/30 | Powerful stats, environmental justice angle |
| Live Demo | 23/25 | Hard to get convincing "PCB fragments" as props — less tactile |
| Technical | 20/20 | All components justified |
| Innovation | 13/15 | E-waste precious metal angle is unusual |
| Docs | 9/10 | Strong regulatory context (WEEE Directive) |

---

## Factory 7: Water Treatment — Desalination Pre-Treatment Plant

> Raw water enters a mixing chamber (Motor 1 stirs coagulant). After settling, Servo 1 opens the drain valve to release treated water. Motor 2 aerates the water. Servo 2 controls the sludge outlet. System monitors pump health via IMU.

### The Real-World Problem
- **2 billion people** lack access to safely managed drinking water (UN, 2023)
- Desalination pre-treatment is the **most energy-intensive** step — 30-50% of total plant energy
- Small community desal plants in coastal regions can't afford SCADA systems (£100K+)
- Pump failures cause **40% of plant downtime** — predictive maintenance could prevent most

### Component Mapping

| Component | Factory Role | Why |
|---|---|---|
| DC Motor 1 | **Mixing impeller** — stirs raw water + coagulant chemical | Real pre-treatment plants have flash mixers |
| DC Motor 2 | **Aeration blower** — adds oxygen for biological treatment | Aeration is the #1 energy consumer in water treatment |
| Servo 1 | **Treated water outlet valve** — opens when water quality passes | Real plants have automated valve control |
| Servo 2 | **Sludge drain valve** — opens to remove settled contaminants | Sludge removal is timed and automated |
| BMI160 IMU | **Pump bearing monitor** — detects cavitation or wear | Pump failure = plant shutdown = no clean water |
| Potentiometer | **Flow rate setpoint** — litres per hour target | Operators adjust based on demand |

### Physical Build (NO ACTUAL WATER)
- Motor 1 spins a paddle in an **empty** container labelled "MIXING CHAMBER" — the concept is demonstrated without liquid
- Motor 2 has a small fan labelled "AERATOR"
- Servos open/close cardboard gates labelled "CLEAN WATER OUT" and "SLUDGE DRAIN"
- Blue LEDs inside the "tank" simulate water

### Sustainability Narrative
- "2 billion people lack clean water. Desalination can help, but pre-treatment wastes enormous energy."
- "Aeration alone is 50% of treatment plant energy. Running blowers at variable speed saves 40-60%."
- Pump predictive maintenance angle: "40% of plant downtime is pump failure. Our IMU detects it before it happens."

### Score Prediction: 92/100

| Category | Score | Reasoning |
|---|---|---|
| Problem Definition | 29/30 | Clean water access is a top-tier global problem |
| Live Demo | 22/25 | No actual water = less dramatic. Spinning paddles in empty containers |
| Technical | 20/20 | All components used |
| Innovation | 13/15 | Water treatment is a strong engineering angle |
| Docs | 8/10 | Good UN stats, SDG alignment |

---

## Final Comparison Matrix

| # | Factory | Problem Strength | Demo Visual | Build Ease | Props Available? | Component Fit | Sustainability | Predicted Score |
|---|---|---|---|---|---|---|---|---|
| 1 | **Recycling Centre (MRF)** | Strong — UK stats, landfill crisis | High — bottle caps sorted | Easy — 3h | Bottle caps (free) | All 4 natural | Obvious | 94 |
| 2 | **Pharma Tablet QC** | Very strong — WHO, lives at stake | High — mints/discs sorted | Easy — 3h | Mints/smarties | All 4 natural | Energy + access | 95 |
| 3 | **Coffee Roasting QC** | Medium — niche industry | Very high — multi-stage, drum visual | Medium — drum build | Dried beans/beads | All 4 natural | Energy waste | 93 |
| 4 | **Battery Recovery** | Very strong — EU regulation, fire risk | Very high — real batteries as props | Easy — 3h | Dead AA batteries (free) | All 4 + safety priority | Obvious + urgent | **96** |
| 5 | **Seed Sorting (Vertical Farm)** | Good — growing industry | Medium — seeds are small | Easy — 3h | Sunflower seeds | All 4 natural | Food + energy | 91 |
| 6 | **Precious Metal Recovery** | Strong — e-waste crisis | Medium — hard to get good props | Easy — 3h | Cut up old PCBs? | All 4 natural | Resource recovery | 93 |
| 7 | **Water Treatment** | Very strong — 2B people, SDGs | Low-medium — no actual water | Medium | No real props | Motor roles less obvious | Clean water | 92 |

---

## Top 3 Recommendation

### 1st: Battery Recovery Plant (Factory 4)
- Strongest narrative overlap with GridBox's core innovation (safety-critical load priority)
- Real batteries as props — no fakery
- EU Battery Regulation gives regulatory urgency
- Fan-never-sheds demonstrates intelligent power management better than anything else

### 2nd: Pharmaceutical Tablet QC (Factory 2)
- WHO stats are devastating — judges can't argue with "250,000 children die"
- Clinical white aesthetic stands out from typical hackathon cardboard brown
- "Every pill you've ever taken was checked by a system like this" hooks anyone

### 3rd: Recycling Centre MRF (Factory 1)
- Universally understood — zero explanation needed
- UK-specific stats (11M tonnes) for Manchester-based hackathon
- Safest choice — can't go wrong with recycling
