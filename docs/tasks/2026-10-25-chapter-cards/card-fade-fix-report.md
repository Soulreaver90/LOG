# Chapter cards v7: smooth fades by palette scaling (report, 2026-10-30)

Brief: `card-fade-fix.md` in this folder. Labels: CONFIRMED (C) = read from ROM bytes or code, or proved by a test or an interpreter run. LIKELY (L) = strong evidence, no emulator run. SPECULATIVE (S) = a guess. Addresses are r40 + `chapter_cards` v7 unless the text says base or BF.

2026-10-30: "The fades are very jaggy. In Buu's Fury the fade in and out are smooth." Then: "did we look into fixing the chapter fade".

---

## SHIPPED

| Ask (brief) | Result | Label and proof |
|---|---|---|
| 1. Option B: `card_enter` writes a black BG palette and sets BLDCNT 0; `card_tick` scales the BG palette every frame with BF's L | Done, with variant B8 for the fade in (it was cheap and it is exact). Timing 100 / 250 / 100, the song, the leave path and every exit path are unchanged. OBJ palette and HUD are not touched. Card 4's ext 40 and ext 41 are unchanged | C: code below, `test_tick_has_bf_timing` |
| 2. Prove the frames, step count, black first frame | Fade in: a change on **97 of 100** frames, largest change **1 level**. Fade out: 94 of 100, 1 level. Both equal Buu's Fury exactly. Frame 0 and frame 1 are black | C: `fadefix_frames.txt`, frame proof below |
| 3. Update the three named tests, add a first-frame test and a step-count test | Done. No test weakened. 62 tests in `test_chapter_cards.py` (v6: 60) | C: test run |
| 4. Build v7 on r40, two ROM copies, three `.sav` copies, diff v6 to v7, SHA-1s | Built. v6 to v7: 42 runs, all inside a v7 `chapter_cards` site. r40 to v7: 924 runs, all inside | C: `fadefix_build.txt` |
| 5. Full suite once at the end | 925 tests in 196.5 s, OK | C: `full_suite_fadefix.txt` |

## PENDING

| Ask | Why pending | My step |
|---|---|---|
| The fades in play | No emulator run | Play steps below |
| Bible rows into `docs\RE-BIBLE.md` | The brief forbids that file | Rows (tag CHF2) are in `scripts\one-time\2026-10-25-chapter-cards\bible_rows_fade_fix.md` |

---

## Short answer

1. **The card now fades the way Buu's Fury fades.** The tick rewrites the card's BG palette on every fade frame with BF's own formulas, so the picture changes on almost every frame by at most 1 of 31 levels (C).
2. **The 6-frame staircase is gone.** v6 changed the picture on 16 of 100 frames, 2 levels at a time (CHF report). v7 changes it on 97 (in) and 94 (out) of 100 frames, 1 level at a time (C).
3. **No flash.** Enter makes the BG palette black before it turns BG3 on. The first 3 fade frames stay black, as in BF (C).
4. **The hold palette is byte for byte the v6 palette.** Frame 100 copies the stored BACKDROP bytes, so the card in the hold looks as it did in v6 (C).

---

## The code change (`scripts\permanent\patches\chapter_cards.py`)

| Part | v6 | v7 | Label |
|---|---|---|---|
| `card_enter` | BLDCNT 0x2048, BLDALPHA 0, copies the BACKDROP palette to BG palette RAM | BLDCNT 0, BLDALPHA 0, `scale(0)` makes the 256 BG words 0. The base tiles are loaded from BACKDROP + 0x200 by an explicit `ldr`, `add` (v6 relied on r1 left by the palette copy) | C |
| `card_tick` frames 1-99 | BLDALPHA = frame x 41 >> 8 | `rise(L)`, L = (frame << 8) / 100: each channel = BF fade table row x L >> 11 (BF ext 121's rule, `@0x08007074`) | C |
| Frame 100 and hold 101-350 | BLDALPHA 16 | Frame 100: L = 256 copies the stored BACKDROP bytes (bit 15 kept). Hold: no write | C |
| Frames 351-450 | BLDALPHA = (450 - frame) x 41 >> 8 | `scale(L)`, L = 256 - ((frame - 350) << 8) / 100: each 5-bit channel x L >> 8 (BF ext 120's rule, `@0x080176D6`). Frame 450: L = 0 (black), returns 1 | C |
| `card_leave` | unchanged | unchanged (music stop, BG palette black, four registers back, free) | C |
| Divide | none | No ARM call. `level_rule(n)` finds an exact multiply: (k << 8) / 100 = k x 5243 >> 11 for every k in 0-100. The module raises at build time if no exact rule exists for FADE_IN or FADE_OUT | C (exhaustive check) |
| New data | none | A 0x300-byte data chunk: BF table `rom:0x701B0` rows 0-255, rows 247 and 248 from OBJ rows 257 and 258 (the text colours, as `backdrop()` does for the palette). The module checks every row >> 3 against the stored BG palette, and the BF literal `rom:0x7164` = `0x080701B0` (added to `BF_SOURCE_WORDS`) | C |
| Constants | `EVA_STEP`, `BLEND_CNT`, `END` in `SYMS` | Removed (a search of `scripts\` found `EVA_STEP` and `BLEND_CNT` only in this module; the full suite passes without all three). Added `FADE_OUT`, `FADE_TABLE`, and `IN_MUL`/`IN_SHIFT`/`OUT_MUL`/`OUT_SHIFT` (set in `_layout`) | C |

Why B8 and not plain B: plain B (5-bit channel x L >> 8 for the fade in too) was my first build. It changed on 92 of 100 fade-in frames and differed from BF by 1 level on 1065 entry-frames (C, an earlier run of `fadefix_frames.py` on the plain-B module, before B8; that listing was overwritten and not kept). B8 cost about 27 Thumb instructions (the `rise` routine) and 0x300 bytes, and it makes the fade in equal to BF's own code on every entry-frame (C, check C below).

Two layout facts from the first tries (C):
- The fade table first sat inside the code chunk. The 0x630-byte chunk found no free spot on the padded base ("no free chunk of 0x630 bytes in 8 tries", 4 test errors). The table is now its own data chunk, allocated after the v6 chunks.
- `ssj2_form.assemble` has no `orr`, `and` or `asr`. The loops pack the 5-bit fields with `lsl` and a 3-register `add`. The fields do not overlap, so `add` equals `orr` here.

Cost per fade frame: about 4,600 Thumb instructions (in) and 5,600 (out), about the size of the vanilla ext 40 loop over 512 words (C: instruction count). `scene_push` runs the tick right after the VBlank wait (bible CHC row). So the palette write likely ends inside VBlank and shows no tear line (L; the cycle count is an S estimate, not measured).

---

## Frame proof (`scripts\one-time\2026-10-25-chapter-cards\fadefix_frames.py`, `fadefix_frames.txt`)

Method (C): the r40 + v7 build in memory; `card_enter`, then `card_tick` until it returns 1, all as ROM code in the test interpreter. BG palette RAM is read after every call.

| Check | Result | Label |
|---|---|---|
| Scene end | The tick returns 1 first on frame 450; every earlier frame returns 0 | C |
| Frame 0 (after enter) | BG palette all 0. OBJ half untouched (0x5A fill kept after enter and after frame 450). BLDCNT 0, BLDALPHA 0, DISPCNT 0x0800 | C |
| A. Closed form, all 256 BG words, frames 1-450 | 450 of 450 frames equal: in = table x L >> 11, out = channel x L >> 8, frame 100 and the hold = the stored bytes | C |
| B. BF's own ext 120 code (`@0x080176AC` snapshot, `@0x080177D2` tick) on our palette | Our frame 350 + k equals BF's frame k on 100 of 100 frames, all 256 words | C |
| C. BF's own ext 121 code (`@0x08017806`, BF's table) against our fade in, 105 shown entries | 0 entry-frames differ (plain B: 1065, 1 level, from an earlier run of `fadefix_frames.py` on the plain-B module, before B8; that listing was overwritten and not kept) | C |
| First black frames | Frames 1-3 are black (BF's are too: CHF table "0 0 0") | C |
| First full-colour frame | Frame 100. Frames 1-99 are below full on every lit channel | C |
| Hold writes | 0 palette changes on frames 101-350 | C |

| Fade | Entries | Frames | Frames with a change | Largest channel jump | Distinct pictures |
|---|---|---|---|---|---|
| v7 in (frames 1-100) | 105 shown | 100 | 97 | 1 | 98 |
| v7 in | 256 all | 100 | 97 | 1 | 98 |
| v7 out (frames 351-450) | 105 shown | 100 | 94 | 1 | 95 |
| v7 out | 256 all | 100 | 94 | 1 | 95 |
| BF in, ext 121 (CHF report) | 105 shown | 100 | 97 | 1 | 98 |
| BF out, ext 120 (CHF report) | 105 shown | 100 | 94 | 1 | 95 |
| v6 in or out (CHF report) | 105 shown | 100 | 16 | 2 | 17 |

"Shown" = the 103 palette entries the map 29 backdrop uses plus the two text entries 247 and 248, as in the CHF report.

v7 fade in, L / white text channel (entry 248, red). It equals the BF row of the CHF report cell for cell:

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

The fade out table (frames 351-450, L 254 down to 0) is in `fadefix_frames.txt`.

---

## Tests changed (`scripts\permanent\tests\test_chapter_cards.py`)

| Test | Old (v6) | New (v7) |
|---|---|---|
| `test_tick_has_bf_timing` | BLDALPHA after each tick = frame x 41 >> 8 in, 16 in the hold, (450 - frame) x 41 >> 8 out; 450 frames | BG palette after each tick: frames 1-99 = BF table row x L >> 11, frames 100-350 = the card palette bytes, frames 351-450 = channel x L >> 8, frame 450 all 0; 450 frames; the fade in never steps back; OBJ half untouched. Expected values come from the BF ROM and the report rules, never from the module |
| `test_enter_draws_the_card_and_starts_the_ported_song` | Registers 0x0800, 0x1F83, 0x2048, 0; palette and text checked right after enter | Registers 0x0800, 0x1F83, **0**, 0; BG palette all 0 and OBJ half untouched after enter; picture unchanged; `check_palette_and_text` (unchanged) after 100 ticks |
| `test_leave_restores_file_select_registers_and_frees_the_object` | Starts from BLDCNT 0x2048, BLDALPHA 16 | Starts from the v7 card registers BLDCNT 0, BLDALPHA 0. Same assertions, including "OBJ palette not touched" |
| `test_no_button_skips_the_card` | 4 key masks, 450 frames each | Unchanged assertions; `ticks()` now runs the real palette fades (step limit 20000 per call) |
| New `test_first_card_frame_is_black_and_full_colour_waits_for_the_last_fade_in_frame` | none | Frame 1 all 0; the first frame equal to the full palette is frame 100; frames 1-99 below full on every channel |
| New `test_fades_step_on_bf_frames_by_one_level` | none | On the 105 shown entries: fade in (97 frames, jump 1), fade out (94, 1), the BF numbers of the CHF report table |

Helpers added: `card_palette`, `channels`, `fade_rows`, `steps`, and a decode cache in the test `Gba.run` (speed only: the same `thumb_dis` text per address; the old `Cpu.run` logic is kept line for line). One v7 tick run is shared by the three fade tests. `test_chapter_cards.py`: 62 tests in 24.2 s, OK (C).

No test failed for a real reason. `check_palette_and_text` was not changed: frame 100 copies the stored bytes, so entry 248 keeps 0xFFFF (C).

---

## Build (`scripts\one-time\2026-10-25-chapter-cards\fadefix_build.py`, `fadefix_build.txt`)

| File in `builds\mockups\2026-10-25-chapter-cards\` | Content | SHA-1 | Label |
|---|---|---|---|
| (list before `chapter_cards`, in memory) | r40 | `14d6b8314f5f418f80021fe60ef8d052b5dcf2be` | C |
| `log2_poc_r40_chapters_v6.gba` (source, read only) | v6 on r40 | `1cef4d6cc064eeec2e124c98b4ebbb4e96357e62` | C |
| `log2_poc_r40_chapters_v7.gba` | r40 + `chapter_cards` v7 | `57896c9fba8cc144c1ded4306de6625710c2be82` | C |
| `log2_poc_r40_chapters_v7_pre_a.gba` | copy of v7 | `57896c9fba8cc144c1ded4306de6625710c2be82` | C |
| `log2_poc_r40_chapters_v7_pre_b2.gba` | copy of v7 | `57896c9fba8cc144c1ded4306de6625710c2be82` | C |
| `log2_poc_r40_chapters_v7.sav` | byte copy of `log2_poc_r40_chapters_v6.sav` | `8b0b74f4896ba1a57666499305861f5f42c40a06` | C |
| `log2_poc_r40_chapters_v7_pre_a.sav` | byte copy of `log2_poc_r40_chapters_v6_pre_a.sav` | `0a04aa03ad560f8b1373c572e67cfae73c0f2a40` | C |
| `log2_poc_r40_chapters_v7_pre_b2.sav` | byte copy of `log2_poc_r40_chapters_v6_pre_b2.sav` | `8bd87bfcda7cb96edaef74dc7defb447db6953fe` | C |

All six targets were checked absent, then written with `open(path, "xb")`. Each was read back equal. Source SHA-1s were checked before any write. One line was appended to `docs\build-log.md`. States (`.ss1`, `.ss2`) were not copied: a state holds the old code (C).

### Diff runs

- **r40 to v7:** 924 runs, 0 outside a v7 site (C).
- **v6 to v7:** 42 runs, 1546 bytes, 0 outside a v7 site (C). The v6 sites came from `fadefix_v6_sites.json`, a snapshot of the v6 notes taken before the module changed (its in-memory build equals the v6 file, C).

| Class | Runs |
|---|---|
| v7 code block, `rom:0x93A254` +0x334 (v6: `rom:0x939F54` +0x2AC) | 27 |
| v7 fade table, `rom:0x939F54` +0x300 (new bytes over the old v6 code area) | 12 |
| A run across the fade table end and the code block start | 1 |
| Hook word `rom:0x23B38` (code moved) | 1 |
| Ext table copy word 145 (code moved) | 1 |
| Total | 42 |

The cards, the song, the backdrop, the ext table copy (except word 145) and the seven story records keep their v6 addresses and bytes (C: the same site list). No "reverted" bytes: the fade table covers the whole old code area.

---

## Play steps (mGBA)

1. Put `log2_poc_r40_chapters_v7.gba` and `log2_poc_r40_chapters_v7.sav` in one folder. Open the ROM. Do not load a state.
2. Continue a slot. Step the card fade in with frame advance. Expect a change on almost every frame, no 6-frame plateaus, and no colour on the first card frame (C: interpreter; L: in play).
3. In the palette viewer during the hold, expect BF's palette with 247 black and 248 white, steady (no writes) (C: interpreter; L: in play).
4. Step the fade out. Expect a smooth fall to black over 100 frames, then the map load (L).
5. With `_v7_pre_b2.sav` (slot 1, Chapter 4), play to card 5 at the end of Kami's scene. Expect a clean map 2,20 and its music (L).
6. Card 4 (`_v7_pre_a` slot 3 or a save before flag 86): expect the field fade out, the card with its new fades, then the map with the HUD and the right colours (L).

---

## Process note

I ran `cd` at the start of three Bash calls: the first line count of the reading list, a bible `grep`, and a `sed` edit of my own `fadefix_frames.py` (the `sed` used an absolute path). The brief forbids `cd`. No file other than my own script changed in those calls. Every other command used absolute paths.

## Files

- `scripts\permanent\patches\chapter_cards.py` (v7), `scripts\permanent\tests\test_chapter_cards.py` (v7)
- `builds\mockups\2026-10-25-chapter-cards\log2_poc_r40_chapters_v7.gba`, `_v7_pre_a.gba`, `_v7_pre_b2.gba` and the three `.sav` files
- `scripts\one-time\2026-10-25-chapter-cards\`: `fadefix_v6_sites.py` with `.json` and `.txt`, `fadefix_table_probe.py` and `.txt`, `fadefix_frames.py` and `.txt`, `fadefix_build.py` and `.txt`, `full_suite_fadefix.txt`, `bible_rows_fade_fix.md`
