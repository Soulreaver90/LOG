# Chapter card fades: why ours step and BF's are smooth (study report, 2026-10-30)

Study only: no module, build list or ROM changed.

2026-10-30 3:30 PM: "There is an issue with the cards, the fades are very jaggy. In Buu's Fury the fade in and
out are smooth, but the fade in the game seems like it's in steps, not smooth."

| SHIPPED | Result |
|---|---|
| "How Buu's Fury fades the card in and out" | Palette RAM fade, all 512 colours rewritten every frame, 32 levels per colour channel. The picture changes on 97 of 100 frames (in) and 94 of 100 (out), never more than 1 level at a time |
| "The same for our card fades" | Blend register fade (BLDALPHA EVA), 17 levels in all. The picture changes on 16 of 100 frames, 2 levels at a time, every colour on the same frame. Card 4's outer 60-frame fades are palette fades and are smooth |
| "Why ours steps" | The hardware gives EVA only 17 levels (0-16). v2 stretched the v1 16-frame EVA fade to 100 frames, so each level holds for 6 or 7 frames: a visible staircase at about 10 steps per second |
| "Fix options, recommend one" | Recommended: option B, a BF-style palette fade in our card tick (BG palette only). Options A and B and four rejected ideas below |

| PENDING | Why |
|---|---|
| The fix build | Needs your pick of an option. No module change in this study |
| Emulator frame-step check | Needs a build. Test plan under "Option B test plan" |

---

## Summary

Buu's Fury does not use the blend registers for its card fades. It rewrites the colour palette every frame. Each
colour channel has 32 levels, and different colours step on different frames, so the eye sees a smooth ramp.

Our card uses the blend register BLDALPHA. That register has 17 levels, and every colour steps together. Over 100
frames that is one jump every 6 or 7 frames. This is the staircase you see.

The fix is to fade our card the BF way: scale the card palette each frame. Buu's Fury's fade code is the same code
as LoG II's own ext 40 and ext 41 fades, so the method is native to our engine.

---

## 1. How Buu's Fury fades the card

Each fade is a scene object that `scene_push` (`@0x0803D8A0`) runs once per frame through vtable slot +0x2C.

| Step | Code | Label |
|---|---|---|
| Fade in: ext 121 (`@0x08002438`) allocates 12 bytes {vtable `0x0804C588`, frame 0, n = 100} | `bf_card_ext_ops.txt` | C |
| Tick (vtable +0x2C = `@0x08017806`): frame + 1, then L = (frame << 8) / n through `@0x08046E58` | `fade_compare.txt` | C |
| `@0x080070CC` sets the target to black with r3 = 256 - L and branches to `@0x08007074` | `fade_compare.txt` | C |
| `@0x08007074` writes all 512 palette words (BG and OBJ) from the RGB888 table `rom:0x701B0`: channel = (table x L) >> 11 | `fade_compare.txt`, `fade_frames.txt` | C |
| The table `rom:0x701B0` is BF's palette `rom:0x5632C` (512 of 512 entries equal after >> 3); 46 entries keep 8-bit precision (entry 2 = 255,255,255) | `fade_frames.py` check | C |
| The tick returns 1 (scene end) when frame >= n: 100 ticks | interpreter run | C |
| Fade out: ext 120 (`@0x08002404`) calls `@0x08050714`, which allocates 0x40C bytes, takes a palette snapshot (`@0x080176AC`: palette RAM into +4 to +0x403) and sets vtable `0x0804BBA4`, frame +0x404 = 0, n +0x408 | `fade_bf_probe.txt` | C |
| Tick (vtable +0x2C = `@0x080177D2`): L = 256 - (frame << 8) / n, then `@0x080176D6` writes all 512 words = snapshot channel x L >> 8 | `fade_compare.txt`, `fade_frames.txt` | C |
| The divide `@0x08046E58` returns r1 / r0. Its first 8 ARM words equal LoG `@0x08021F30`, which the VS5 ext 43 bible row reads as (frame << 8) / n | `fade_compare.txt` | C (bytes), L (semantics from the twin) |
| The update runs once per scene frame. `scene_push` runs the top scene's tick once per frame (bible CH2 row: 100 + 250 + 100 = 450 frames, matched in play) | bible CH2 | L |

Hardware: palette RAM only. No BLDCNT, BLDALPHA or BLDY write in either path (C, listings). Channel resolution: 32
levels (5 bits). Update rate: every frame.

### BF code is LoG II's ext 40 and ext 41 code

`fade_compare.py` lists each pair, maps the call targets and pool words, and diffs the text.

| BF | LoG II | Result |
|---|---|---|
| ext 120 tick `@0x080177D2` | ext 40 tick `@0x0800DBAE` | 26 of 26 instructions equal |
| ext 121 tick `@0x08017806` | ext 41 tick `@0x0800DBE2` | 19 of 19 equal |
| `@0x080070CC` (to black) | `@0x0800BE6C` | 7 of 7 equal |
| `@0x08007074` (table blend) | `@0x0800BE14` | 44 of 44 equal; table `0x080701B0` against `0x083ECBA4` |
| `@0x080176D6` (snapshot scale) | `@0x0800DA96` | The loop is equal; BF copies back with `@0x08049144`, LoG with DMA3 |
| `@0x080176AC` (snapshot take) | `@0x0800DA68` | Same job; BF copies with `@0x08049144`, LoG with DMA3 |
| divide `@0x08046E58` | divide `@0x08021F30` | First 8 words equal |

All C. In `fade_compare.txt` the two snapshot rows show low "equal" counts (35 of 60, 0 of 22). Their windows are
a fixed length and run past the function end, and the copy method (BF `bl 0x08049144`, LoG DMA3 register writes)
shifts every line after the loop. The scale arithmetic in the loop is equal; only the stack buffer offset and one
scratch register differ. So LoG II has BF's exact fade, but its ext 41 fades in toward the LoG field palette (`rom:0x3ECBA4`, literal
at `rom:0xBF04`), not toward the card palette.

## 2. How our card fades

| Fade | Code | Hardware | Update | Label |
|---|---|---|---|---|
| Card in, frames 1-100 | `card_tick` (`chapter_cards.py` CODE section 5): EVA = frame x 41 >> 8 | BLDCNT 0x2048 (BG3 first target, alpha blend, backdrop second target), BLDALPHA low byte = EVA, EVB 0 | Written every frame, value changes every 6 or 7 frames | C (code, `test_tick_has_bf_timing`) |
| Hold, frames 101-350 | EVA 16 | BLDALPHA | none | C |
| Card out, frames 351-449 | EVA = (450 - frame) x 41 >> 8; 0 at frame 450, scene end | BLDALPHA | as fade in | C |
| Card 4 outer fade out | `ext 40 (60)` before the card op | palette snapshot scale (= BF ext 120 code) | every frame | C (bible CH5 row, `fade_compare.txt`) |
| Card 4 outer fade in | `ext 41 (60)` after the map reload | palette table blend (= BF ext 121 code) | every frame | C |
| Cards 2, 3, 5-8 | the vanilla `ext 40` fade out before, the map load fade in after | palette | every frame | C (bible CH5 row) |

The shown colour for EVA is min(31, c x EVA >> 4) per channel (GBATEK alpha blend, EVB 0). Label L: the formula
is from the hardware documentation, not from a capture.

History (C, `chapter-cards-report.md`): v1 used a 16-frame fade, EVA 1-16, one level per frame (line 142). The v2
change "Card length should match BF" (final, 2026-10-25 4:25 PM) kept the EVA method and stretched it to 100
frames (line 272). Nobody chose 6-frame steps. They are a result of the stretch.

## 3. Why ours steps

Cause (C for the code, L for the hardware formula): the blend register has 17 levels. Over 100 frames each level
holds for 6 or 7 frames, and every colour on the screen jumps on the same frame by up to 2 of 31 levels.

| Fade | Frames | Frames with a change | Largest channel jump | Distinct pictures | White levels |
|---|---|---|---|---|---|
| BF in (ext 121) | 100 | 97 | 1 | 98 | 32 |
| BF out (ext 120) | 100 | 94 | 1 | 95 | 32 |
| Ours in | 100 | 16 | 2 | 17 | 17 |
| Ours out | 100 | 16 | 2 | 17 | 17 |
| Card 4 field in (ext 41, 60) | 60 | 57 | 1 | 58 | 32 |
| Card 4 field out (ext 40, 60) | 60 | 58 | 1 | 59 | 32 |

Method (`fade_frames.txt`, C): the BF rows run BF's own tick code in the test interpreter. Every frame was checked
against the closed form on all 512 palette words. "Shown" = the 103 palette entries the map 29 backdrop uses plus
the 2 text entries (105). The card 4 rows use the 512 LoG fade table colours. At full level the BF and our shown
colours are equal.

Two effects add up:
1. **Few steps.** 17 pictures against 98.
2. **All colours step together.** On a change frame ours moves 85-103 of 105 entries at once. BF moves 7-89 entries
   per frame after frame 3, a different set each frame, so no single frame shows a jump.

The first visible change of our fade in comes at frame 7 (EVA 1). The first 6 frames are black.

### Per-frame tables (fade in)

Cell = level / white text channel (0-31). BF level L is 0-256; our level is EVA 0-16.

BF fade in (ext 121):

| frames | +1 | +2 | +3 | +4 | +5 | +6 | +7 | +8 | +9 | +10 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1-10 | 2/0 | 5/0 | 7/0 | 10/1 | 12/1 | 15/1 | 17/2 | 20/2 | 23/2 | 25/3 |
| 11-20 | 28/3 | 30/3 | 33/4 | 35/4 | 38/4 | 40/4 | 43/5 | 46/5 | 48/5 | 51/6 |
| 21-30 | 53/6 | 56/6 | 58/7 | 61/7 | 64/7 | 66/8 | 69/8 | 71/8 | 74/9 | 76/9 |
| 31-40 | 79/9 | 81/10 | 84/10 | 87/10 | 89/11 | 92/11 | 94/11 | 97/12 | 99/12 | 102/12 |
| 41-50 | 104/12 | 107/13 | 110/13 | 112/13 | 115/14 | 117/14 | 120/14 | 122/15 | 125/15 | 128/15 |
| 51-60 | 130/16 | 133/16 | 135/16 | 138/17 | 140/17 | 143/17 | 145/18 | 148/18 | 151/18 | 153/19 |
| 61-70 | 156/19 | 158/19 | 161/20 | 163/20 | 166/20 | 168/20 | 171/21 | 174/21 | 176/21 | 179/22 |
| 71-80 | 181/22 | 184/22 | 186/23 | 189/23 | 192/23 | 194/24 | 197/24 | 199/24 | 202/25 | 204/25 |
| 81-90 | 207/25 | 209/26 | 212/26 | 215/26 | 217/27 | 220/27 | 222/27 | 225/28 | 227/28 | 230/28 |
| 91-100 | 232/28 | 235/29 | 238/29 | 240/29 | 243/30 | 245/30 | 248/30 | 250/31 | 253/31 | 256/31 |

Ours fade in:

| frames | +1 | +2 | +3 | +4 | +5 | +6 | +7 | +8 | +9 | +10 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1-10 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 1/1 | 1/1 | 1/1 | 1/1 |
| 11-20 | 1/1 | 1/1 | 2/3 | 2/3 | 2/3 | 2/3 | 2/3 | 2/3 | 3/5 | 3/5 |
| 21-30 | 3/5 | 3/5 | 3/5 | 3/5 | 4/7 | 4/7 | 4/7 | 4/7 | 4/7 | 4/7 |
| 31-40 | 4/7 | 5/9 | 5/9 | 5/9 | 5/9 | 5/9 | 5/9 | 6/11 | 6/11 | 6/11 |
| 41-50 | 6/11 | 6/11 | 6/11 | 7/13 | 7/13 | 7/13 | 7/13 | 7/13 | 7/13 | 8/15 |
| 51-60 | 8/15 | 8/15 | 8/15 | 8/15 | 8/15 | 8/15 | 9/17 | 9/17 | 9/17 | 9/17 |
| 61-70 | 9/17 | 9/17 | 10/19 | 10/19 | 10/19 | 10/19 | 10/19 | 10/19 | 11/21 | 11/21 |
| 71-80 | 11/21 | 11/21 | 11/21 | 11/21 | 12/23 | 12/23 | 12/23 | 12/23 | 12/23 | 12/23 |
| 81-90 | 12/23 | 13/25 | 13/25 | 13/25 | 13/25 | 13/25 | 13/25 | 14/27 | 14/27 | 14/27 |
| 91-100 | 14/27 | 14/27 | 14/27 | 15/29 | 15/29 | 15/29 | 15/29 | 15/29 | 15/29 | 16/31 |

Shown entries that change on each frame of the fade in (of 105):

| frames | BF | Ours |
|---|---|---|
| 1-10 | 0 0 0 57 29 34 37 52 39 54 | 0 0 0 0 0 0 85 0 0 0 |
| 11-20 | 37 22 38 49 47 30 67 28 11 55 | 0 0 100 0 0 0 0 0 99 0 |
| 21-30 | 50 28 43 36 59 10 54 14 58 38 | 0 0 0 0 100 0 0 0 0 0 |
| 31-40 | 36 19 64 50 19 57 28 26 30 57 | 0 98 0 0 0 0 0 101 0 0 |
| 41-50 | 44 38 64 15 43 41 51 27 54 67 | 0 0 0 99 0 0 0 0 0 101 |
| 51-60 | 10 39 37 48 12 48 36 46 57 14 | 0 0 0 0 0 0 96 0 0 0 |
| 61-70 | 54 35 44 7 65 27 58 49 29 25 | 0 0 101 0 0 0 0 0 100 0 |
| 71-80 | 19 64 36 38 77 11 52 33 43 8 | 0 0 0 0 101 0 0 0 0 0 |
| 81-90 | 71 31 36 57 37 46 29 52 31 41 | 0 97 0 0 0 0 0 101 0 0 |
| 91-100 | 57 31 53 55 18 29 62 16 11 89 | 0 0 0 98 0 0 0 0 0 103 |

The fade out tables are the mirror (full tables in `fade_frames.txt`). Ours holds EVA 15 for frames 351-356 and
steps every 6 or 7 frames to EVA 0 at frame 444, black for the last 7 frames.

---

## 4. Fix options

### Rejected

| Idea | Why not | Label |
|---|---|---|
| BLDY brightness (BLDCNT effect 3, EVY 0-16) | Also 17 levels, all colours on the same frame. The same staircase | L (GBATEK) |
| BLDALPHA on another schedule | 17 levels is the ceiling. At best 16 changes in 100 frames | C (count) |
| Temporal dither (EVA n and n + 1 on alternate frames) | Flicker at 30 Hz on the LCD, and BF does not look like that | S (look) |
| Call vanilla ext 41 for the card fade in | `@0x0800BE14` always fades toward the LoG field table `rom:0x3ECBA4`. The card would fade in to LoG colours. Changing that table changes every fade in the game | C |

### Option A: reuse LoG's snapshot fade from `card_tick`

| Item | Detail |
|---|---|
| What changes | `card_enter` copies the card palette as now, allocates a 0x40C-byte buffer, calls `@0x0800DA68` (snapshot take; it writes vtable `0x080240B4` into word 0 of the buffer) and then `@0x0800DA96(buffer, 0)` before DISPCNT turns BG3 on. `card_tick` calls `@0x0800DA96(buffer, L)` in and `(buffer, 256 - L)` out, L = (frame << 8) / 100 through the divide `@0x08021F30`. `card_leave` frees the buffer. BLDCNT 0 or BLDALPHA 16 |
| Code | About 30 new Thumb instructions, no new data |
| BF look | Exact for the fade out (the same code as BF ext 120). Fade in: scale of the 5-bit palette, within 1 level of BF's 8-bit table form (below) |
| Risk | A second heap block of 0x40C bytes during the Continue path (heap room at file select not checked: S). It scales the OBJ half too. Every exit refills OBJ: Continue's map load fade in (`@0x0800180C` builds a fade in from the table, bible PSL row: L), story cards 2, 3, 5-8 (a map load, then an ext 41 table fade in: C), card 4 (`@0x08005F1A` zeroes both halves, then ext 41: C). `test_leave_restores_file_select_registers_and_frees_the_object` asserts "OBJ palette not touched". It still passes (it runs no tick), but the claim no longer holds for the whole card |

### Option B (recommended): a BF-style palette fade of the BG palette in `card_tick`

| Item | Detail |
|---|---|
| What changes | `card_enter` writes a black BG palette (0x200 zero bytes) in place of the BACKDROP palette, and still copies the base tiles from BACKDROP + 0x200. BLDCNT 0 (no blend effect); the save and restore of the four registers stay. `card_tick` computes L and writes 256 BG palette words: each channel of the BACKDROP palette word x L >> 8. Hold: no write (the palette is full after frame 100). `card_leave` is unchanged (BG palette black) |
| Level | Fade in L = (frame << 8) / 100. Fade out L = 256 - ((frame - 350) << 8) / 100, which is BF's form. The form ((450 - frame) << 8) / 100 is 1 level lower on 96 of 100 frames, because of the floor |
| Divide | `ldr r3,=0x08021F31 ; bl via_r3`, as ext 40 uses it (its first instruction `bx pc` enters ARM; the return goes back by `bx lr` with the Thumb bit). A `bl` cannot reach from the expansion code. The alternative L = frame x 656 >> 8 (clamp 256) differs from the divide on 14 of 100 frames, by 1 level |
| Code | About 35 new Thumb instructions in `card_tick` (the same loop shape as `@0x080176D6`: three 5-bit fields, three `mul`, three `asr #8`, `orr`). No new data. Cost per frame: 256 entries, about the size of the vanilla ext 40 loop over 512 |
| BF look | Fade out: exact (BF ext 120 scales the 5-bit palette RAM by the same rule). Fade in: 1023 of 10,300 entry-frames differ from BF by 1 level, never more, because BF's table keeps 8 bits for 46 entries. Variant B8 below makes it exact |
| Risk | Only the card scene runs this code. BG palette only, so the OBJ half and the HUD are not touched (OBJ is off in the card, DISPCNT 0x0800). BLDCNT and BLDALPHA are restored by `card_leave` as now. If the tick runs while the screen draws, one frame can show a 1-level tear line: not visible (S). Other scenes: none use the card vtable |

Variant B8 (exact BF fade in): store a 0x300-byte RGB888 copy of BF's table for BG entries 0-255 (`rom:0x701B0`,
with 247 and 248 from OBJ entries 1 and 2), and fade in with table x L >> 11 as `@0x08007074` does. The fade out
stays c x L >> 8. The gain is at most 1 level on 10% of entry-frames. I do not think the eye can see it.

### Option B test plan

Unit tests (`tests\test_chapter_cards.py`). These pin today's behaviour and must change:
- `test_tick_has_bf_timing`: keep the 450-frame end. Replace the BLDALPHA list with the BG palette after each tick,
  checked against c x L >> 8 for frames 1-100 and 351-450, and full for 101-350. The test `Gba` needs `asr`, `orr`
  and the divide stub (or the multiply rule). `fade_frames.py` has a `Gba` with `mul`, `asr`, `orr` and `ldmia`.
- `test_enter_draws_the_card_and_starts_the_ported_song`: after enter, BLDCNT 0 and the BG palette black. Move
  `check_palette_and_text` to after 100 ticks.
- `test_leave_restores_file_select_registers_and_frees_the_object`: unchanged in shape; the OBJ half stays
  untouched.
- New: no frame of the fade in shows a full-colour palette before frame 100 (no flash on the first frame).

Emulator (mGBA, frame advance):
1. Continue a save. Step the card fade in. Expect a change on almost every frame and no 6-frame plateaus.
2. Expect no full-colour flash on the first card frame.
3. In the palette viewer during the hold, expect the BF palette with 247 = black and 248 = white.
4. Play to card 3 (fade 240, then the card, then the "Three years later" map). Expect a clean map and its music.
5. Play to card 4. Expect the field fade out, the card, then the map with the HUD and the right colours.
6. During the card, check that no other code writes BG palette RAM on each frame (palette viewer is steady in the
   hold).

---

## Recommendation

Option B. It is BF's own method (palette scale, 32 levels, every frame) on the BG palette only. It needs no heap
block, does not touch OBJ or the HUD, and changes only the card's own code. Take variant B8 only if you see a
difference in play.

## Related note (not in scope)

The cut from file select to the card is still abrupt: `card_enter` sets DISPCNT 0 at once (C, CODE section 4).
`chapter-cards-report.md` line 227 lists it as a possible follow-up. BF fades out before its card.

## Files

- `scripts\one-time\2026-10-25-chapter-cards\fade_bf_probe.py` and `fade_bf_probe.txt`: BF listings by address.
- `scripts\one-time\2026-10-25-chapter-cards\fade_compare.py` and `fade_compare.txt`: BF against LoG fade code.
- `scripts\one-time\2026-10-25-chapter-cards\fade_frames.py` and `fade_frames.txt`: per-frame values and counts.
- `scripts\one-time\2026-10-25-chapter-cards\bible_rows_fade.md`: bible rows, tag CHF.
