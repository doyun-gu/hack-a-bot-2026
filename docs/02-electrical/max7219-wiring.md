# MAX7219 8-Digit 7-Segment Display Wiring Guide

> Connects to **Pico B (SCADA)** using SPI1 — completely separate from the nRF24L01+ on SPI0.

---

## Pin Layout

### Reference Pinouts

<p>
<img src="../images/pico2_pinout_reference.png" alt="Pico 2 Pinout" width="500"/>
</p>

The MAX7219 module has 5 pins on a header:

```
┌─────────────────────────────┐
│  MAX7219  8-Digit  Display  │
│  ╔═══╗╔═══╗╔═══╗╔═══╗╔═══╗ │
│  ║ 8 ║║ 8 ║║ 8 ║║ 8 ║║ 8 ║ │
│  ╚═══╝╚═══╝╚═══╝╚═══╝╚═══╝ │
│  ╔═══╗╔═══╗╔═══╗            │
│  ║ 8 ║║ 8 ║║ 8 ║            │
│  ╚═══╝╚═══╝╚═══╝            │
└─────────┬───────────────────┘
          │
    VCC GND DIN CS CLK
```

---

## Wiring Table

| MAX7219 Pin | Pico B GPIO | Physical Pin | Description |
|---|---|---|---|
| **VCC** | **3V3** | Pin 36 | Power — 3.3V from Pico |
| **GND** | **GND** | Pin 38 | Ground |
| **DIN** | **GP11** | Pin 15 | SPI1 MOSI — data from Pico to display |
| **CLK** | **GP10** | Pin 14 | SPI1 SCK — clock signal |
| **CS** | **GP13** | Pin 17 | Chip Select — active LOW |

### Why These Pins?

- **SPI1** is used (not SPI0) because SPI0 is already taken by the nRF24L01+ (GP0-3, GP16)
- GP10, GP11, GP13 are the hardware SPI1 pins on Pico 2 — no bit-banging needed
- GP10-13 are free on Pico B (they're only used for MOSFETs on Pico A)

---

## SPI Bus Summary — Pico B

| Bus | Device | SCK | MOSI | MISO | CS |
|---|---|---|---|---|---|
| **SPI0** | nRF24L01+ | GP2 | GP3 | GP16 | GP1 |
| **SPI1** | MAX7219 | GP10 | GP11 | — | GP13 |

No pin conflicts. Both buses operate independently.

---

## Voltage Notes

| Supply | LED Brightness | Logic Compatibility | Recommendation |
|---|---|---|---|
| **3.3V** (3V3 pin) | Dimmer but visible | Perfect — same as Pico GPIO | **Use this** |
| **5V** (VBUS pin) | Full brightness | Marginal — MAX7219 VIH=3.5V, Pico outputs 3.3V | Risk of unreliable data |

**For the hackathon, use 3.3V.** The LEDs will still be clearly visible and you avoid logic-level issues.

---

## Quick Physical Pin Reference

Looking at the Pico B with USB port at the top:

```
                    ┌─────────┐
                    │  USB-C  │
              ┌─────┴─────────┴─────┐
    GP0  [1]  │●                   ●│ [40] VBUS
    GP1  [2]  │●                   ●│ [39] VSYS
    GND  [3]  │●                   ●│ [38] GND ◄── MAX7219 GND
    GP2  [4]  │●                   ●│ [37] 3V3_EN
    GP3  [5]  │●                   ●│ [36] 3V3 ◄── MAX7219 VCC
    GP4  [6]  │●                   ●│ [35] ADC_VREF
    GP5  [7]  │●                   ●│ [34] GP28
    GND  [8]  │●                   ●│ [33] GND
    GP6  [9]  │●                   ●│ [32] GP27
    GP7  [10] │●                   ●│ [31] GP26
    GP8  [11] │●                   ●│ [30] RUN
    GP9  [12] │●                   ●│ [29] GP22
    GND  [13] │●                   ●│ [28] GND
    GP10 [14] │● ◄── CLK          ●│ [27] GP21
    GP11 [15] │● ◄── DIN          ●│ [26] GP20
    GP12 [16] │●                   ●│ [25] GP19
    GP13 [17] │● ◄── CS           ●│ [24] GP18
    GND  [18] │●                   ●│ [23] GND
    GP14 [19] │●                   ●│ [22] GP17
    GP15 [20] │●                   ●│ [21] GP16
              └─────────────────────┘
```

**3 data wires** (CLK, DIN, CS) are on physical pins 14, 15, 17 — all on the left side.
**Power** (VCC, GND) from pins 36 and 38 on the right side.

---

## How to Test

After wiring, run:

```bash
cd ~/Developer/hack-a-bot-2026
./src/tools/flash.sh test-display
```

Or manually via mpremote:

```python
from machine import Pin, SPI
import time

# Init SPI1
spi = SPI(1, baudrate=10_000_000, polarity=0, phase=0,
          sck=Pin(10), mosi=Pin(11))
cs = Pin(13, Pin.OUT, value=1)

def write_reg(addr, data):
    cs.value(0)
    spi.write(bytes([addr, data]))
    cs.value(1)

# Wake up MAX7219
write_reg(0x0C, 1)    # shutdown register → normal operation
write_reg(0x0B, 7)    # scan limit → all 8 digits
write_reg(0x09, 0xFF) # decode mode → BCD for all digits
write_reg(0x0A, 8)    # intensity → medium (0-15)

# Display "12345678"
for digit in range(1, 9):
    write_reg(digit, digit)

print("Display should show: 1 2 3 4 5 6 7 8")
```

If the display lights up with "12345678", the wiring is correct.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Nothing displays | VCC/GND wrong or CS not toggling | Check power + CS wire to GP13 |
| Garbled digits | DIN or CLK swapped | Swap GP10 and GP11 wires |
| Very dim | Running at 3.3V (normal) | Increase intensity: `write_reg(0x0A, 15)` |
| Only some digits work | Bad connection on module chain | Re-seat the module, check solder joints |
| Display flickers | Power supply noise | Add 10µF cap across VCC-GND (same as nRF fix) |
