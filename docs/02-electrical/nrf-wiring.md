# nRF24L01+ Wiring Guide

> Print this and follow it exactly. The nRF is the most fragile module — wrong voltage kills it instantly.

---

## Pin Layout

Looking at the module from the **top, antenna pointing up:**

```
            ANTENNA
              ↑
        ┌───────────┐
        │           │
        │ nRF24L01+ │
        │           │
        └──┬─┬─┬─┬──┘
           │ │ │ │
    ┌──────┴─┴─┴─┴──────┐
    │  1   3   5   7    │  ← bottom row
    │  2   4   6   8    │  ← top row
    └───────────────────┘

    Pin 1 = bottom-left (square pad / dot marking)
```

---

## Wiring Table

| Pin | Name | Pico GPIO | Description |
|---|---|---|---|
| **1** | GND | GND | Ground |
| **2** | VCC | **3V3** | Power — **3.3V ONLY, 5V KILLS IT** |
| **3** | CE | GP0 | Chip Enable (TX/RX activate) |
| **4** | CSN | GP1 | Chip Select (SPI) |
| **5** | SCK | GP2 | SPI Clock |
| **6** | MOSI | GP3 | SPI Data Out (Pico → nRF) |
| **7** | MISO | GP16 | SPI Data In (nRF → Pico) |
| **8** | IRQ | Not connected | Leave empty |

---

## Capacitor — REQUIRED

Add a **10µF capacitor** directly across pins 1 and 2 (as close to the module as possible):

```
3V3 ───┬─── Pin 2 (VCC)
       │
     [10µF]  ← capacitor (observe polarity if electrolytic: + to VCC)
       │
GND ───┴─── Pin 1 (GND)
```

**Without this capacitor, the wireless will be unreliable or not work at all.** The nRF draws current in short bursts that cause voltage dips.

---

## Safety Rules

| Rule | Consequence of Breaking |
|---|---|
| **VCC = 3.3V only** | 5V destroys the module permanently |
| **Add 10µF capacitor** | Without it: random packet loss, module resets, no connection |
| **Pin 8 (IRQ) leave empty** | Connecting it wrong can cause issues |
| **Same wiring on both Picos** | Both must use identical pin mapping |
| **Keep antenna clear** | Don't place metal objects near the antenna |

---

## How to Verify It's Working

After wiring, run:

```bash
mpremote run src/master-pico/tests/test_circuit_check.py
```

Look for: `[PASS] nRF24L01+ responds (status=0x0E)` — any status between 0x01 and 0x7F means it's alive.

If you see `status=0xFF` — module not responding. Check wiring.
If you see `status=0x00` — module in reset. Check 10µF capacitor and 3.3V power.

---

## Which Pin is Pin 1?

Three ways to identify:

1. **Square pad** — one pin has a square solder pad, others are round. That's pin 1 (GND)
2. **Dot marking** — small dot printed on the PCB near pin 1
3. **Multimeter** — pin 1 (GND) has continuity with the metal RF shielding on top of the module
