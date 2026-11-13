# The Z charge meter: it stops short of empty, and it empties at the wrong moment

**Play `builds\mockups\2026-11-12-ki-meter\log2_kimeter_v4.gba`**, SHA-1
`2d468d7a5f632a09b03b135c5fbc9c23c7741190`, save seeded from `builds\log2_poc_r40.sav`.

> **Do not play v1, v2 or v3.** v3 in particular is broken: it leaves the cooldown at 0 after every
> transform, so the triangle never empties and Z is instantly available again. See "The bug v3 carried".

---

## Report 1: which layer stops short

**It is not the ki bar. It is the small yellow triangle beside the ability icon, the Z charge meter.**

I measured both ki pool layers first, because that is what the brief points at.

| Layer | Measured | Result |
|---|---|---|
| The pool value | 820 frame drain at max EP 40, frame by frame | Reaches 0, sits at 0 for one drain period, then reverts |
| The drawn pool bar | `hud_draw` run at 15 pool values over 3 max EP values | Reaches fill 0 and paints 0 pixels |

At max EP 134 the bar is already empty at pool 2, and at max EP 500 it is empty from pool 10 down, because
`pool x 49 / max EP` truncates. **The ki bar empties early, never late.** Evidence:
`scripts\one-time\2026-11-12-ki-meter-drain\probe_drain.py`.

### Defect 1: the meter cannot reach empty

The charge meter is the yellow triangle in the ability icon: columns 22-28, rows 3-9 of the 32x16 icon.

- **Address:** the cooldown offset table `rom:0x3B5B90`. It holds `0x50` bytes, which is 20 offsets.
- **Op:** the vanilla draw `@0x08008DFA` to `@0x08008E10` paints index 1 at the FIRST `count` offsets of
  that table, where `count` is the count table `rom:0x3B5BE0` indexed by the level, highest entry 20.
- **Why 20 is short:** `bf_hud` steps 3 and 4 give LoG II the Buu's Fury meter. That meter is **28** pixels
  (Buu's Fury table `0x08072410`, 28 entries; its own count table `0x08071CA8` is 8 bytes,
  `0, 7, 13, 18, 22, 25, 28`). Our table cannot grow, because `rom:0x3B5B90 + 0x50` is the count table.

Steps 20-27, the corner wedge, are lit in all 27 icon images and no draw can reach them. Measured: 8 of 8
stranded, in 27 of 27 icons. Colours `#F8F800`, `#F8D040`, `#F8B028`, `#E0E878`: yellow.

### Defect 2: the meter empties at the wrong moment

This is the one you saw in Buu's Fury. **CONFIRMED, and the two games differ in one instruction.**

- **Buu's Fury** sets the whole cooldown in ONE store when the form lands: `@0x0801C34C`
  `str r0,[r1,#0x4]` writes `0x37FFF` to the leader record `+4`, inside `@0x0801C312`, the same routine
  that swaps the appearance entry and fills the ki pool. Its level is `record +4 >> 15`, so `0x37FFF` is
  level 6, the top of its 7 entry table, which erases all 28 pixels. Nothing touches the cooldown during
  the transformation, so the triangle sits full and then empties all at once.
- **LoG II** accumulates it: the state 35 tick `@0x080155EE` adds 8 every frame for 160 frames. The level
  crosses 1, 2, 3 and 4 at frames 32, 64, 96 and 128, so our triangle drained in steps through the
  transformation and was already empty 32 frames before the form landed.

---

## Report 2: does the Buu's Fury meter fill while transforming

**CONFIRMED. It stays full, then empties in one step when the form lands.**

Evidence, decoded from the Buu's Fury USA ROM in `data\roms\`:

| Fact | Address | Op | Confidence |
|---|---|---|---|
| The character record is `[0x0871DD38 +8] + 0x68 * index + 0x4F8` | `0x0801C33C`-`0x0801C348` | `mul r1,r3 ; add r0,r1,r0 ; mov r1,#0x9f ; lsl r1,r1,#3 ; add r1,r0,r1` | CONFIRMED |
| The whole cooldown is set in ONE store when the form lands | `0x0801C34C` | `ldr r0,=0x00037fff ; str r0,[r1,#0x4]` | CONFIRMED |
| The same routine fills the ki pool | `0x0801C312` | the caller of both | CONFIRMED |
| Its charge meter draw erases `count_table[level]` pixels | `0x0800BC94`-`0x0800BCAC` | `ldrb r0,[r3,#0x5] ; ldsb r0,[r1,r0] ; strb r2,[r5,r3]` in a loop | CONFIRMED |
| Its level is a cached byte in the HUD buffer, not a live read | `0x0800BC94` | `ldrb r0,[r3,#0x5]`, `r3 = sp + 0x500` | CONFIRMED |

Shapes used: every aligned ROM word naming each meter table (1 of 1 each), and every pc-relative load of
those two literals (4 of 4). **A table reached through a register base, or a second copy of the literal,
would not appear in either shape.**

Only one store writes the record `+4` in `0x0801C000`-`0x0801C400`, so during the transformation the
cooldown does not move and the triangle holds full. On the landing frame one store takes it to its
maximum, so the triangle goes from full to empty between two frames. That is exactly what you described.

### What happens when the form ENDS: I could not establish it. SPECULATIVE.

I withdraw the claim my earlier draft made here. It cited `@0x0801C0D4` as a decrement
`sub r0,r0,#0x1 ; str r0,[r1,#0x4]`. **That address does not decode to those ops.** It decodes to
`lsl r0,r0,#2 ; add r6,r0,r1`. The "about 64 minutes" figure was arithmetic on that bad reading, and an
hour long wait was itself a sign the reading was wrong. Both are withdrawn.

What I then searched for, and did not find:

- Every `str rX,[rY,#0x4]` in the whole code area with a `sub` within 4 instructions before it:
  **0 sites.** A decrement written as `add rX,#-1`, through a computed offset, or as `strh`/`strb`,
  would not appear in this shape.
- Every `str rX,[rY,#0x4]` in `0x0801C000`-`0x0801C400`: 3 sites, and only `0x0801C34C` is the record.

So **I cannot say how, or how fast, Buu's Fury lowers its cooldown again.** Its 7 entry count table
proves the gradation exists in the DRAW, but the draw is not the refill schedule, and a 7 entry table is
a correlate, not the thing. Settling it needs the level byte traced back to its writer, which is a
separate study.

### What ours now does

Our side IS fully read, from the prior cooldown study `docs\tasks\2026-10-24-form-cooldown\`, which
cites the disassembly:

- **Raised** by the state 35 anim `@0x080155EA`-`@0x080155EE`, `add r3,#0x8 ; str r3,[r2,#0x8]`, every
  frame to frame 0xA0, reaching about 0x500.
- **Lowered** only by the base form tick `@0x08017034`, `sub r2,#0x1 ; str r2,[r0,#0x8]`, 1 a frame.
  **The base tick does not run while transformed**, so the cooldown holds at 0x500 for the whole form.

| Moment | Before | Now |
|---|---|---|
| Press Z | Triangle drains in 4 steps over 160 frames | Triangle stays full |
| Form lands | Triangle already empty, 32 frames early, 8 pixels still lit | Triangle empties, all 28 pixels, in one frame |
| Form runs | Triangle empty, 8 pixels still lit | Triangle empty, all 28 pixels off |
| Form ends | Refills in 4 steps, 8 pixels never erased | Refills in 4 steps, all 28 pixels |

The refill is `28 -> 18 -> 13 -> 7 -> 0` over 1280 frames, about 21 seconds, with the level changing at
cooldown `0x400`, `0x300`, `0x200` and `0x100`. Measured from `COUNTS` and `CD_TAIL`, not assumed.

### The refill still does not match Buu's Fury. Your decision.

| | Steps | Pixel counts |
|---|---|---|
| Buu's Fury count table `0x08071CA8` | 6 | 28, 25, 22, 18, 13, 7, 0 |
| Ours | 4 | 28, 18, 13, 7, 0 |

Ours jumps 28 to 18 in one step, where Buu's Fury takes three. **I did not change this**, because you
asked for the emptying moment and this is the refill. Matching it needs two more levels, and both of
the things that cap us are hard:

- The clamp `@0x08D3E` caps the level at 4, which is a vanilla code byte change.
- The count table `rom:0x3B5BE0` sits immediately after the offset table, so neither can grow in place.

Rough cost: a second wrapper on the draw that computes the level itself and runs its own 7 entry table
from free space, leaving both vanilla tables alone. Comparable to `cd_tail`, so roughly a day with
tests. Say the word and I will do it as its own task.

### The cost of what I DID change

**1 new vtable hook word and one new code block.** `tick_xform` wraps the state 35 tick `@0x080155E5`
through vtable `0x08025D9C +0x04`, saves the cooldown, calls the vanilla tick, and restores it under a
guard. `fill_end` gained one store and one literal. **No vanilla code byte changes.**

Holding the triangle full needed **no change in `hud_draw` and no new redraw key**, because the anim's
`+8` is a pure side effect: `powerup_tick @0x08011D4A` counts its own u16 at actor `+0x12` and never
reads the cooldown.

## The bug v3 carried: a re-entrancy trap

v1, v2 and v3 are all wrong. **v3 is the dangerous one**, because it looks right in the test suite.

`tick_xform` saved the cooldown, called the vanilla anim, and restored the saved value blindly. On the
landing frame, at count `0xA0`, `powerup_tick @0x08011D70` runs:

```
ldr r1,[r5,#0x0]
ldr r2,[r1,#0x14]
bl call_via_r2        ; state 35's +0x14, which is fill_end
```

So `fill_end` writes the whole cooldown **from inside the anim call**. The blind restore then put the
old value, 0, straight back over it. In `log2_kimeter_v3.gba` the cooldown sits at 0 after every
transform, so the triangle never empties and Z is available again at once: the opposite of the request.

The first three tests could not see it, because the stubbed anim never reaches `fill_end`.

**The fix** is a guard that restores only when the anim alone moved the word:

```
ldr r0,[r4,#0x8]
sub r0,#0x8
cmp r0,r5
bne xform_done        ; fill_end ran inside the anim: leave its value alone
str r5,[r4,#0x8]
```

Two end to end tests now run the real path with no anim stub, at frames `0x9F` and `0x9E`. Removing the
guard makes them fail with `AssertionError: 64 != 1280 : 0x9f`, so they are not vacuous.

### A second change the guard forced: SET, not ADD

`fill_end` now writes `CD_SET = 0x500` with `str`, the whole cooldown in one store, the way Buu's Fury
does. The vanilla behaviour was `+8` a frame, which ADDS. That matters for Super Saiyan to Super
Saiyan 2, which runs state 35 a second time: adding would stack a second wait on top of the first.
`test_a_second_step_sets_the_cooldown_rather_than_adding` pins it.

`0x500` is `0xA0` frames times 8, the exact value the vanilla animation used to reach, so the wait after
a transform is unchanged.

---

## What changed in the tree

| File | Change |
|---|---|
| `scripts\permanent\patches\bf_ki_pool.py` | `cd_tail` draws the 8 stranded pixels; `tick_xform` holds the meter full; `fill_end` sets the whole cooldown; `_check_charge_meter` pins all of it |
| `scripts\permanent\patches\fullpower_hud.py` | `HUD_KEY` re-pinned to the grown `hud_key` block |
| `scripts\permanent\tests\test_bf_ki_pool.py` | +10 tests, 43 to 53 |
| `scripts\permanent\tests\test_fullpower_hud.py` | +3 tests, the `hud_fp` entry path |
| `scripts\permanent\tests\test_bf_hud.py` | the new hook word registered in `HOOKS` |
| `scripts\permanent\build_list_trial_kimeter.txt` | new trial list, `include build_list_dev.txt` only |

`build_list.txt` and `build_list_core.txt` were NOT touched. Nothing under `art\` was touched.

### Pins that moved

| Pin | Value |
|---|---|
| `fullpower_hud.HUD_KEY` | `0x54`, `e3aeee87b5d3d5a34e9f11dbe963d9a8e15b92ec` |
| Golden master `build_list.txt` | `c9daab4609ef72cfe0245a59f40aa5d5cd04aaac` |
| Dev master `build_list_dev.txt` | `2d468d7a5f632a09b03b135c5fbc9c23c7741190` |
| Trial `log2_kimeter_v4.gba` | `2d468d7a5f632a09b03b135c5fbc9c23c7741190` |

The trial ROM is byte identical to the dev master, because the fix lives in `bf_ki_pool`, which
`build_list_core.txt` already carries. The trial list exists only to give the ROM its own name.

The save beside it seeded from **`builds\log2_poc_r40.sav`**, the highest numbered one present. Verified
by SHA-1, not by the log: `log2_kimeter_v4.sav` and `log2_poc_r40.sav` are both
`d2fa5e1a016ae40fe3b264eb21008b807d391a1f`. There is no `log2_poc_r41.sav`.

### The suite

Full output: `scripts\one-time\2026-11-12-ki-meter-drain\suite_after.txt`, 46590 bytes, summary at
line 518 and the exit status at line 636. Failing test IDs: `fails_after.txt`, 35 lines.

```
Ran 2037 tests in 451.972s
FAILED (failures=31, errors=4, skipped=10, expected failures=1)
EXIT=1
```

Red before my work: 34. Red after: 35. **Exactly one failure is new, and it is not mine:**

`tests.test_piccolo_powerup_art.PiccoloPowerUpArtTests.test_the_base_8mb_differs_only_at_super_nameks_own_row`

That is the other agent's file. It was edited at 19:31, DURING this suite run, which on its own
invalidates the result. Its diff names offsets `0x31D550` to `0x31D55F`, Super Namek's sprite row, not
my hook word at `0x25DA0`. And `test_bf_hud.LayoutTests.test_only_named_bytes_change` is GREEN, which
proves `bf_ki_pool` writes only its own window and its own hook words.

The other 34 have the **same test IDs** as the pre-work baseline in `fails_before.txt`, which is what
`compare_suites.py` measured. I did not trace which change left them red.

---

## The alternative I did not take

One line in `bf_hud.plan` could blank the 8 stranded pixels in the 27 icon images, and the meter would
then reach empty with no new code. **I did not do it, because you draw the art.** The 8 pixels are part
of the yellow triangle you see when the meter is full. Blanking them would shorten the triangle.

---

## Two documentation defects, now fixed

- **B0514** said the cooldown offset table holds the Buu's Fury meter. It did not say the table is 20
  slots against the meter's 28 pixels, which is the whole defect. The row now says both.
- `bf_ki_pool.py`'s header cited `docs\tasks\2026-11-12-red-ki-bar\report.md`, which does not exist. It
  now cites that task's `rows.md` and this task's `report.md`.

## Where the facts disagree

**Your two reports both matched the code exactly.** Report 1's "it stops shortly before" is the 8 pixel
corner wedge. Report 2's "the triangle remains full while the ki builds up" is `@0x0801C34C`.

Three disagreements are with MY earlier statements and with the brief, not with you:

| Claim | Correction |
|---|---|
| My first draft: the cooldown "jumps to 0x500 at press" | It accumulates `+8` a frame over 160 frames. The jump is what the fix now creates, not what vanilla did |
| My first draft: the Buu's Fury meter refills in 7 steps through `@0x0801C0D4` | That address does not decode to a decrement. The refill is unestablished, and my draft's 7 steps also miscounted a 7 entry table as 7 steps rather than 6 |
| The brief: about 17 golden pins were already red | I measured 34 red before any edit of mine, in `fails_before.txt` |
