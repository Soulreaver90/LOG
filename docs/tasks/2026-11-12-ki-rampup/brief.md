# The ki bar ramps up during the transformation

## What the owner described (2026-11-12, his words, condensed)

Buu's Fury layers bars. The green bar is the base. During a transformation the **yellow bar ramps up
over the green bar** until it is full. It does this whatever the green bar holds: full, empty or half
full, the yellow still ramps to full over it. **If the transformation is interrupted, the yellow bar
disappears.** The second transformation does the same thing again: the **orange bar ramps over the
yellow bar**.

So it is a stack of overlays, not a value. Green under, yellow over it, orange over that.

## What ours does now

The bar snaps to full on the landing frame, because the game fills the ki pool in one store when the
form lands. There is no ramp and nothing to interrupt.

## Why this is cheaper than it looks

The pieces are already in the tree:

| Piece | Where | What it gives |
|---|---|---|
| A per frame hook during the transform | `tick_xform`, state 35 vtable `0x08025D9C +0x04` | somewhere to drive a ramp from, frame by frame |
| An overlay fill cache | `bf_ki_pool` RAM `0x03003A00 +0xC` | the drawn fill, separate from the pool value |
| A bar colour byte | the same RAM `+0xE` | which overlay is drawn, yellow or orange |
| Two bar images | the yellow image and the orange one `ORANGE_AT` past it | the two overlays, already built |

The transform animation runs about 160 frames: the charge level crosses 1, 2, 3 and 4 at frames 32,
64, 96 and 128.

## What the work has to decide

1. The ramp drives the **drawn overlay**, not the ki pool. The pool still arrives at the landing
   frame. (Owner's description settles this: the bar goes over the green bar, so it is a draw.)
2. The ramp always ends full, whatever the base bar holds.
3. An interrupted transformation clears the overlay. Find what "interrupted" is in code: the state
   leaving 35 without reaching the landing store.
4. The orange overlay ramps over the yellow one on a second transformation, the same way.

## Open, needs measuring, do not assume

- How many steps the Buu's Fury ramp uses, and over how many frames. The earlier study found the
  DRAW has a gradation table of 7 entries but could not establish the schedule. That is a
  measurement, not a guess: read the Buu's Fury transform tick, do not infer it from the table.
- Whether Buu's Fury clears the overlay on interrupt or lets it fall back down.

## Rules for this work

- Never interpret a RAM word or an op from a label. Open the handler.
- `bf_ki_pool` is the owning module. The triangle work (`tick_xform`, `fill_end`, `cd_tail`) must
  keep working: it is pinned by `_check_charge_meter` and by the tests in `test_bf_ki_pool.py`.
