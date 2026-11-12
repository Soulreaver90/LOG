# Arena v4 report

Written after the build, from my own reads of the shipped bytes. Numbers an agent gave me are marked as its
claim where mine disagree. Measurement method and the per-tile evidence are in `measurements.md` beside this.

## The ROM

```
builds\mockups\2026-11-06-arena-v4\log2_poc_r41_arena_v4.gba
sha1 09877ad0cf250ff38b59f51fde316507be4445f6
```

A `.sav` is paired. Built from `scripts\permanent\build_list_trial_ending.txt`. Suite 1321, exit 0.

**Read this before trusting any earlier note.** I first verified `c7950cc5` and reported results from it. That
ROM is the WITHDRAWN band, now `superseded\log2_poc_r41_arena_v4_band11to12.gba`. Every number below comes
from a re-read of `09877ad0`. The 12:08 build in `superseded\` is byte identical to the ship.

## What the owner asked for, and what the ROM does

He play-tested arena v3 and reported three defects. Each one below is checked against the built bytes, not
against the patch source.

| His words | State in `09877ad0` |
|---|---|
| "the start still transitions both cell and trunks to different points on the map" | Cell item at **(244,504)**, `TRUNKS_SPOT` **(248,568)**. Both are the spots the conversation itself leaves them on, so the fight spawns nobody anywhere new |
| "there is no collision for the glass door in the capsule corp" | **16 cells closed**, cx 28-35, cy 9-10, px (224,72)-(287,87). **0 cells opened.** His state 5 spot (246,72), inside the door, now reads CLOSED. State 4 (246,94) in front of it, and the map 6,2 return landing (248,100), both still OPEN |
| "remove the item and collision" for the save panel and the map post, and draw out their shadows | Shadows gone: **0** palette index 73 pixels in both boxes, against 270 and 602 in source map 6,1. **The objects themselves still spawn with collision** |

## The one open defect

The save panel and the map post are still there. My earlier claim that they were "drawn in, not spawned" was
too broad: their SHADOWS are painted into BG2, which is what v4 fixed, but the objects are spawned and carry
their own collision. The owner proved this by loading the ROM. Which layout field spawns them is not known.

Five probe ROMs are waiting for him in `builds\mockups\2026-11-06-arena-probe\`, each zeroing one candidate
word, made with `scripts\permanent\rom\poke_rom.py` so no rebuild was needed.

## The trade this build makes, which the owner has not ruled on

Holding Cell at the conversation's own spot satisfies "no movement at all at fight start" and costs cover.
Bible row 1207 already named (244,504) as "the single worst cell on the map for this".

| Spot | BG1 pixels over Cell's sprite box, my count | Movement at fight start |
|---|---|---|
| (244,504), shipped | **1894**, the CAPSULE CORPORATION arch across his lower body | none |
| (244,616), the v3 spot | **0** | he jumps on the first frame |

There is no middle spot. BG1 is clear only from y 552 down and his box reaches 56 px above his feet, so the
nearest banner-free row is y 608. Trunks at (248,568) is clear either way, 0 pixels by my count.

The agent reported 2423 px for Cell and 642 for Trunks. My envelope clipping differs, so the Cell figures are
the same finding measured two ways; **my Trunks count of 0 contradicts its 642** and the render agrees with me.

Sheet I viewed: `scripts\one-time\2026-11-06-arena-v4\sheet_spots.png`.

## Not in scope, deliberately

- **Trunks starts in base form, not Super Saiyan.** Reported in the same message and never investigated. Its
  own task.
- **The glass panels** at px (224-287, 200-223), 72 px south of the arch, are still open floor. If those are
  what he meant by "the glass door" rather than the dome entrance, fix 2 aimed at the wrong opening.
- **A third drawn-in shadow**, the gate's own, px (200,272)-(207,327), 376 pixels. The brief never covered it
  and both fighters stand beside it.

## Bible rows

Six rows merged under tag `ARN4`, three in section 9 and three in section 11, from `rows.md` beside this.
The collision indexing (rows 1095 and 1721), `obj+0x48` as a set pointer (row 105) and the warp carrier
(row 708) were all already in the bible before this task and are not repeated.
