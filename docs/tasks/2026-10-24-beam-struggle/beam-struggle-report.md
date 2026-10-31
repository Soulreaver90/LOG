# Beam struggle study: a grander Kamehameha clash

Study only. No ROM, build list or patch was made. Addresses are the base ROM (SHA-1 `18e0715dec419f3501c301511530d2edcd590f8b`) unless a line says r39. Every struggle byte range was compared with `builds\log2_poc_r39.gba` and is equal (`r39_check.txt`). Scripts, listings and renders are in `scripts\one-time\2026-10-24-beam-struggle\`.

Labels: **C** = CONFIRMED (bytes or listing read), **L** = LIKELY, **S** = SPECULATIVE.

---

## SHIPPED and PENDING

| Ask (my words, short) | Status | Where |
|---|---|---|
| Find how the vanilla struggle is drawn | SHIPPED | "Vanilla LoG II struggle" below |
| Find how the Buu's Fury intro draws it | SHIPPED (frame 2); frame 1 not found | "Buu's Fury intro struggle" below |
| Options A, B, C with cost and risk | SHIPPED | "Options" below |
| One recommended trial patch module design | SHIPPED (design only, not built) | "Recommendation" below |
| Emulator steps for me | SHIPPED | "My emulator checks" below |
| Bible rows, tag BMS | SHIPPED | `scripts\one-time\2026-10-24-beam-struggle\bible_rows.md` |
| Build the trial module | PENDING (not asked; needs my go) | - |
| My dome art for stage 2 | PENDING (mine) | "My drawing list" below |
| How the BF sphere appears (frame 1 to frame 2) | PENDING (emulator check B1-B3) | - |

---

## Short answer

- **Vanilla (C):** the struggle is not a sprite effect. It is painted into the map. The scene loads a special arena map, 14,4, whose BG0 layer holds two thin beams (6 px body) and whose BG1 layer holds a grey starburst that the hardware adds to the ground at half strength. Gohan and Cell only hold a pose. That is why it looks small.
- **Buu's Fury (C):** the intro struggle is also a map, BF map 3, but it is one still 240x160 picture on BG3: the fighters, the beams, a sphere about 50 px across, about 13 orbs and a starburst painted into the ground.
- **The BF beams are not thicker (C).** Both games draw a 6 px beam body. The BF gain is the big sphere and the orbs.
- **Recommendation:** option C as a code-free trial, in two stages. Stage 1 ports the BF sphere, orbs and beams into map 14,4 BG0 (91 tiles, no art of mine). Stage 2 adds a hand-drawn dome of light on BG1 that grows during the 10-second wait at the start of the scene. No script change, no OBJ, no palette change.

---

## Vanilla LoG II struggle

### The scene (C)

The struggle runs in the final Cell death event table `rom:0x3EC758` (bible CGS row, type 25). Word i is seq i+1.

| Seq | Record | What it does | Label |
|---|---|---|---|
| 1 | `0x083EB80C` | `ext 46 (60)`, boss bar off (`ext 88`), HUD off (`ext 86 (0)`), flash (`ext 42 (30)`), **`ext 39 (14,4,1,493,392)` loads map 14,4** (handler `@0x08009A88` > `map_load` `@0x0800C584`), music 17, camera `ext 31 (320,312,20)`, faces, **`ext 121 (0,30)` and `ext 121 (30,30)`**, sound 43, `ext 43 (600)` | C |
| 2-19 | text and actor records | Goku, Cell, Vegeta lines; the other fighters attack Cell (seq 5, 9, 17) | C |
| 20 | base `0x083EBE1C`, r39 `0x0889AB4C` (relocated) | flash `ext 42 (1)`, **`ext 24 (0)` and `ext 24 (1)` turn BG0 and BG1 off**, both fighters to state 0, sound 43 off, `ext 43 (80)`, **`ext 137 (0,140)`** (the final Kamehameha), 12 hit loops on Cell, Cell removed, 500000 EXP | C |

Proof lines:
- `ext 121 (set, n)` `@0x0800A004` queues command vtable `0x08025ED4`. Its +4 `@0x0800DF60` calls the actor vtable +0x28 (set state) with n. (C)
- State 30 is object `0x03002268` in both state tables (`rom:0x3B52F0`, `rom:0x3ED294`). Ctor `@0x080234AC` gives it vtable `0x08025038`. Enter `@0x0801CB10` sets anim row set + 0x16C (anim 18). Tick `@0x0801CB24` shows frame 0 for 8 ticks, then frames 1 and 2 every 8. A pose, no spawn. (C)
- `ext 24 (n)` `@0x08009658` > `@0x08006274` clears DISPCNT bit 8+n. (C)
- Only seq 1 pushes (14,4, ...) for a map load: 3 hits of the push shape, 2 are `ext 94` moves (`rom:0x3DA5D3`, `0x3DA5EC`); 0 hits of the byte-push shape. Warp and region items were not searched. So "a 14,4 layout edit changes only this scene" is **L**.

### How it is drawn (C unless marked)

Map 14,4: entry `rom:0x40DAB8`, layout list `0x084091EC` (word `rom:0x4091EC`), layout `0x084E2E7C`.

| Part | Data | Size and timing | Label |
|---|---|---|---|
| Beams | BG0 record `0x084E0090` (also holds the crater rocks) | world x 387-493, y 383-393; body 6 px; 10 px orbs at the hands | C (data), L (block order) |
| Spark at the meeting point | BG0 animated group `0x084E2E64`: 12 tiles at BG tile 831 | 3 frames x 10 game frames | C |
| Starburst | BG1 record `0x084E0308`: grey burst, layer box 432-576 x 392-488 = world 368-512 x 328-424 | group `0x084E2BE0`: 53 tiles at 843, 2 frames x 10; tile 843 fills the layer (10,892 cells) with index 1 (black) | C |
| Glow | BLDCNT `0x1C42`, EVA 8, EVB 16 (layout +0, +2, +3; writer `@0x08005F1A` to `0x04000050`, `0x04000052`, `0x04000053`) | BG1 adds at half strength, which makes the tan glow | C |
| Fighters | Gohan and Cell in state 30, anim 18 | Cell anim 18 is 64x64; Gohan 32x32 side view | C |
| Palette | shared BG palette `rom:0x1DA4C8` | beams use BG 2, 67, 73, 74, 169 | C |

Render: `struggle14_4_composite_step0.png` to `step5.png` (3x, layers offset and blended as the hardware does). The BG layers of 14,3 and 14,4 differ only in BG0 and BG1; BG2 and BG3 are the same arena.

Engine facts the design depends on:
- **Tile budget (C).** Map BGxCNT = table `rom:0x1DA8EC` entry 0 plus layout bytes 01 01 03 03: 8bpp, char base 0, screen blocks 28-31. So a map has 896 BG tiles. Map 14,4 loads 596 tiles (index list +0x48, delta coded, `@0x080050C8`) and its groups use 831-895. **Tiles 596-830 (235) are free (C for the layout data, L for "no other writer").**
- **Layer offset (C).** Layer n scrolls with an offset of 64 n px (record +0xC = 0x10000 n, `@0x080055A4`). Layer pixel = world pixel + 64 n.
- **Animated groups (C).** Layout +0xC count, +0x10 list. Record `{u8 frames, u8 tiles, u16 first tile, frame words}`; frame `{u32 duration, bare codec stream}` (no `{type, size}` header; `@0x0800501E` decompresses frame + 4 with r3 = 0). The stack buffer is 0x1000 B, so **64 tiles a group at most**. Group k starts its first countdown at k+1 (`@0x08005096`). The countdown is 16 bits, so a last frame of 0xFFFF holds about 18 minutes. The frame index wraps to 0 at the end. The tick runs in `field_tick` `@0x08004EDC`, which the cutscene scene vtable `0x08023E88` also uses (+0x14), so the art animates during the scene (C). Whether it also runs while a text box waits for A is **L** (check A4).
- **The final blast is OBJ (C).** `ext 137 (0,140)` `@0x0800A3A2` builds the beam `@0x080143A8` (12 units of OBJ VRAM, three 256 B pieces: origin 16x16, tip 16x16, body strips 32x8, 16x8, 8x8, 6 px of colour), sets state 30 itself (`mov r1,#0x1e` `@0x0801D7D2`), fires at frame count 132 (`@0x08014478`) and ends at 0 (`@0x0801451C`). Records: blue `0x086E3458` + 96 dir, yellow `0x08704604` + 96 dir (`vanilla_beam_records.png`).
- **Seq 20 hides BG0 and BG1 (C).** Any art on BG0 or BG1 vanishes at the seq 20 flash, as the vanilla beams do. Art on BG2 or BG3 would stay.

### The text box in this scene

- Every text record in seq 2-19 opens the scene text box: an OBJ object of 224 contiguous units (bible CJR row). (C, prior row)
- r39 budget while a box is open: 492 - 224 - Cell 64 - Gohan 64 (r39 `set:58` header `rom:0x908D54` = 0x1000; base is 0x400) - five NPCs 80 = **60 units free** (40 if the HUD object stays after `ext 86 (0)`). (L: slot sums, no state measured)
- So an OBJ dome of 64x64 8bpp (64 units) cannot exist while dialog shows. BG art costs no OBJ VRAM and no OAM.
- The box covers part of the screen. The struggle sits about 106 px wide on the beam line; where the box falls against it depends on the camera, which is not measured (check A3).

---

## Buu's Fury intro struggle

| Fact | Data | Label |
|---|---|---|
| The struggle is BF map 3 (zone 0, area 4) | entry `rom:0x8E388`, layout list `0x080728DC` (word `rom:0x8E3B4`), layout `0x082B5E94` (word `rom:0x0728DC`) | C |
| One still screen on BG3 | record `0x082B5E5C`, factory `0x08008087` (the LoG II `0x080056A1` twin, DCR row), 1x1 block, frame `0x082B5B7C`; BG0-BG2 = the empty record `0x080707FC` | C |
| Tiles | 297 tiles, banks 184 (169) and 185 (125) of `0x08179764`, plus 3 singles | C |
| No blend, no animation | BLDCNT `0x1040` (no first target), layout +0xC = 0 | C |
| Palette | BF BG palette `rom:0x5632C` (copied to `0x05000000` at `0x0802C9C2`-`0x0802C9C8`) | C (code), L (intro uses it; render colours are right) |
| Content | Cell, SSJ2 Gohan, beams (6 px body), sphere about 50 px across (flood fill box 73-177 x 83-133 with the beams), about 13 orbs, starburst painted INTO the ground (ground pixels recoloured tan) | C (render, `bf_measure.txt`) |
| Frame 1 (no sphere) | not a map layout: no other of 426 BF layouts shares banks 184/185 in a struggle image; the zone 0 sheet shows only map 3 | S |
| How the sphere grows | not traced. Most likely a cut from a screen without the sphere to this still, or OBJ over it | S |

Renders: `bf_intro_struggle_3x.png` (the screen), `bf_cutout_log2pal_3x.png` (the light parts cut out and mapped to LoG II BG colours), `bf_sheet_zone0.png` (all zone 0 BF maps).

I did not trace the BF intro driver or the BF text encoding. The bible CFS row already records that BF dialog is not ASCII; the caption text was not found as UTF-16 or under a constant byte shift.

---

## Options

| | A. Port BF art | B. I draw bigger beams and a new clash | C. BF light parts plus a growing dome (recommended) |
|---|---|---|---|
| What changes | BF sphere, orbs and beams (light colours only) placed on 14,4 BG0 at the meeting point; vanilla BG1 starburst kept | New thick beams (12-16 px) on BG0, new animated clash on BG0, new burst on BG1 | Stage 1 = A. Stage 2: my dome of light on BG1, growing over the first 600 frames, then held |
| The whole BF screen instead | Fails: fighters baked in, 297 tiles (235 free), 26 colours missing from the LoG II BG palette, and the in-world camera moves in seq 5-17 would break | - | - |
| BG tiles (of 235 free) | 91 (C, `design_numbers.txt`) | about 10 for beams (a repeating strip) plus up to 64 a clash group | 91 + dome slots: 12x12 cells = 144, or 72 with a left-right mirror (H-flip map entries) |
| OBJ VRAM / OAM | 0 / 0 | 0 / 0 | 0 / 0 |
| Palette | none: 26 light colours map to existing BG indices, worst distance 17.9, mean 1.4 | I use existing BG indices | same |
| Script | none | none | none |
| Effort | S (data tool only) | M (my art, data tool) | S for stage 1, M for stage 2 (my art) |
| Risk | Low: one base word changes (`rom:0x4091EC`) | Low, same site | Low; group drift: k+1 start, trim durations |
| I draw | nothing (optional edge touch-up) | beams, clash frames, burst | dome frames only |

Notes for all options:
- A dome on BG0 or BG1 vanishes at seq 20 with the vanilla art. That matches the story: the flash, then Gohan's final blast.
- A dome on BG1 is additive (EVA 8/16): it reads as light on the ground, as in the anime. A dome on BG0 is opaque, like the BF sphere.
- Growth is counted from the map load in seq 1, not from a script line. The fixed `ext 43 (600)` wait gives a dependable 10-second window. Growth timed to "SAY GOODBYE" (seq 16) needs a script change and is a later option.
- An animated footprint needs one tile slot per map cell. The 91-tile count is for the static stage 1 art only.

---

## Recommendation: trial module `beam_struggle` (design only, not built)

Option C, staged. Stage 1 needs no art of mine and can be the first mockup. Stage 2 adds the dome when I draw it.

**Build list:** a separate trial list, `scripts\permanent\build_list_beam.txt` = the main list plus `beam_struggle`. Not created. `build_list_trial.txt` belongs to the celljr work. Output `builds\mockups\2026-10-24-beam-struggle\`.

**Base ROM sites changed:** one word. `rom:0x4091EC` (layout list of map 14,4) from `0x084E2E7C` to the layout copy. Nothing else in the base 8 MB changes. The relocated seq 20 record is not touched.

**New data in the expansion area (stage 1):**

| Item | Content | Bytes |
|---|---|---|
| Layout copy | `0x084E2E7C` 0x50 B; +0x14 = new BG0 record, +0x48 = new index list, +0x4C = new chunk table | 80 |
| Chunk table copy | words 0-166 of `0x084DF574` plus word 167 = new chunk | 672 |
| New chunk frame | type 0 raw, 91 tiles x 64 B (BF light cut, BF indices remapped to LoG II BG indices) | 5,832 |
| Index list | type 0 raw, delta coded, 596 vanilla entries unchanged plus 91 entries (chunk 167, tiles 0-90) = BG tiles 596-686 | 1,382 |
| BG0 record copy | 0x58 B; block (1,1) word to the new block | 88 |
| BG0 block (1,1) | the vanilla block decoded, cells in world x 381-489, y 339-423 set to tiles 596-686 (8-aligned offset (312,280) from BF screen to world: BF clash centre to world 440, 388); all other cells (rocks) kept | 2,056 |
| **Stage 1 total** | | **about 10.1 KB** |

**Stage 2 (dome, my art):**

| Item | Content | Bytes |
|---|---|---|
| Group list copy | count 2 to 4: the two vanilla records plus 2 dome groups | 16 |
| Dome group 1 and 2 | records `{frames, 64 / 8 tiles, first 687 / 751, frame words}`; frames `{u32 duration, packed stream}` from `pack(payload, kind=1)` with its 8-byte header removed | about 2 KB a frame (S); 7 frames x 2 groups about 28 KB |
| BG1 record copy and blocks | BG1 layer pixel = world + 64, so the dome at world 392-488 x 336-432 is layer 456-552 x 400-496: blocks (1,1) and (2,1) | 88 + 4,112 |

**Timing (stage 2):** 6 growth frames x 90 = 540 game frames, last frame 0xFFFF (held). Trim group 2 durations by 1 (k+1 start) so both groups switch on the same frame.

**Tests the module needs:**
1. The index list decodes to 687 entries; the first 596 equal vanilla.
2. Every map entry in the new blocks names a tile below 896; new tiles sit in 596-830; no new slot is in 831-895.
3. The new chunk frame decodes to 91 x 64 B.
4. Each dome frame stream (bare, r3 = 0 model) decodes to tiles x 64 B with `webfoot_decompress.decompress`.
5. The base ROM differs from the main build only at `rom:0x4091EC` (diff proof).
6. The BG0 block keeps every vanilla cell outside the beam box.

---

## My drawing list

Stage 1 needs no drawing. Optional: touch up the edges of `bf_cutout_log2pal_3x.png`, where the cut dropped mixed ground pixels.

Stage 2, the dome (on BG1, additive):

| Item | Canvas | Frames | Palette |
|---|---|---|---|
| Dome of light | 96x96 px (12x12 cells, 8-aligned), centred on world (440, 384), the beam meeting point | 6 growth steps (about 16, 32, 48, 64, 80, 96 px), the last one held | greys only (BG 1 = no light, 2, 9, 10, 11, 12, 13, 14): on an additive layer, brightness is light. Same ramp as the vanilla burst |
| Mirror rule | draw it left-right symmetric if you can: it halves the tile slots (72, not 144) | - | - |
| Reference | the vanilla burst `map14_4_bg1_burst_step0.png` and the composite `struggle14_4_composite_step1.png` | - | - |

If you prefer an opaque white-blue dome (like BF), draw it for BG0 with the stage 1 swatch instead. Swatch of the BG indices the BF light parts map to: `swatch_light_cut_log2_bg.png` (BG 2, 9, 10, 11, 12, 45, 52, 66, 72, 73, 74, 143, 148, 149, 153, 154, 159, 164, 169, 181, 184, 187, 193, 198, 214). No new colour is needed.

---

## My emulator checks

LoG II (latest build, mGBA):
- **A1.** Play to the final Cell fight and beat Cell. When the flash ends and both fighters hold the beam pose, make a state (seq 1, during the 10-second wait). Name it `log2_poc_r39_struggle.ss1` in `builds\`.
- **A2.** In that state, open Tools > Tile viewer (BG, 256 colours). Expected: tiles 596-830 are empty. Tell me if any are not.
- **A3.** Press A until the first text box ("GOKU: Dig deeper Gohan!") shows. Take a screenshot. I need the box rectangle against the beams.
- **A4.** In the same box, watch the spark at the meeting point. Expected: it keeps flickering while the box waits for A.
- **A5.** With the box open, Tools > I/O viewer: note BLDCNT (`0x04000050`) and BLDALPHA (`0x04000052`). Expected `0x1C42` and `0x1008`.

Buu's Fury (`data\roms\Dragon Ball Z - Buu's Fury (USA).gba`):
- **B1.** Start a new game and pause on the beam struggle screen before the sphere shows (your frame 1). Make a state.
- **B2.** Tools > Map viewer: which BG layer shows the beams, and is the sphere there. Tools > Sprite viewer: is any sphere or orb an OBJ.
- **B3.** Make a second state on frame 2 ("Goku's son, Gohan was able ..."). Send me both states; I will diff BG VRAM, OAM and palette.

---

## Limits kept and notes

- Read only, except this report, `bible_rows.md` and the study scripts and renders in `scripts\one-time\2026-10-24-beam-struggle\`. Nothing under `data\`. `celljr_fight.py`, its tests, `build_list_trial.txt` and `art\base-audit\` were not touched.
- Two Bash calls used `cd`, which the brief forbids: `cd /c` before a listing command early in the run, and `cd <LOG root>` at the start of the final file check. Neither changed a file; every path in both calls was absolute.
- All new files were normalised to LF and checked by Python: no CR, no byte order mark, no em or en dash, ASCII only.
- A mask bug in my first composites (PIL `point` on a palette image) made them look dim. Fixed in `render_map.mask_of`; the renders named above are the fixed ones. The bible rows record the trap.
- The vanilla BG block order (row-major) is assumed; it is supported by the beam ends meeting Cell's and Gohan's hands at their scene positions.
