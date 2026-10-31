# Beam struggle option B v2: trial module report

The mockup v2 beam struggle is now a trial patch module. It draws the BF sphere, the orbs, the sway and the soft flash as BG0 tile art on map 14,4.

Labels: **C** = CONFIRMED (bytes, listing or test read), **L** = LIKELY, **S** = SPECULATIVE. Addresses are the base ROM unless a line says trial.

> [!WARNING]
> v1 (`log2_poc_r39_beam.gba`) is broken in game. Play v2 (`log2_poc_r39_beam_v2.gba`). The v2 fix section comes first; the v1 sections below it keep their v1 numbers.

---

## v2 fix (final, 2026-10-25 6:40 PM)

My two notes: "beam struggle is broken completely", and "a section of one of the balls is cropped out and remains in the center, it should be a clean cut of the center orb".

### SHIPPED and PENDING (v2)

| Ask (my words, short) | Status | Where |
|---|---|---|
| "beam struggle is broken completely": find the cause from the state | SHIPPED: root cause below, quoted from `log2_poc_r39_beam.ss2` | `scripts\one-time\2026-10-25-beam-trial\diag_ss2.txt`, `diag_ss2_tiles.txt`, `diag_index.txt` |
| Fix the module | SHIPPED | `patches\beam_struggle.py`: chunk table copy keeps words 0-167, static chunk at word 168 |
| "a clean cut of the center orb" | SHIPPED | `beam_struggle_art.py`: the two BF orbs that cross the disk edge are left out whole |
| A test that would have caught the fault | SHIPPED: 4 `LoadTests` + 2 `CleanCutTests` | `tests\test_beam_struggle.py`, 26 tests, all pass |
| v2 ROM and save (exclusive create; v1 and the `.ss2` kept) | SHIPPED | `builds\mockups\2026-10-25-beam-struggle\log2_poc_r39_beam_v2.gba`, `.sav` |
| Full suite once | SHIPPED with a note: 854 run, 852 pass, 2 `test_chapter_cards` failures from another task's edit during my run (below) | `suite_v2.txt` |
| Bible rows (BMT) with the root cause | SHIPPED | `bible_rows.md`, section "Section 9 (v2 fix ...)" |
| The emulator checks of v1 | PENDING (final, on v2) | "What to play" below |

### Root cause (C, from the state)

The ground tiles 441-595 of map 14,4 were replaced. The v1 module overwrote vanilla chunk 167 with its own 9-tile chunk.

- **The table has 168 words, not 167.** `0x084DF574` + 4 x 168 = `0x084DF814`, the frame header of BG0 block 0 (type word `0x00000001`). Word 167 is the vanilla chunk `0x084DE7C8`. I misread the table end as word 167 (the BMS row said "167 chunk frames, word 167 = 1").
- **The vanilla list uses chunk 167.** Entries 441-595 are `0xA700`-`0xA79A`. v1 copied words 0-166 and put the static chunk at word 167.
- **What the state shows** (`diag_ss2.txt`, `diag_index.txt`):
  - VRAM BG tiles 441-449 hold the 9 static tiles.
  - VRAM tiles 450-595 hold stale bytes of chunk 166. Tile 450 equals chunk `0xA6` tile 9, where the entry is `0xA709`. The loader copies byte 64 x k of the last decoded buffer and does not check k against the chunk size (`@0x08005156`-`@0x08005172`).
  - BG2 and BG3 (the ground) name tiles 0-595, so the ground showed white and cream blocks.
- **Ruled out, with values from the state:**
  - Registers are as designed: DISPCNT `0x1F40`, BG0CNT-BG3CNT `0x1C81`, `0x1D81`, `0x1E83`, `0x1F83`, all 8bpp, char base 0.
  - The blend is unchanged: BLDCNT `0x1C42`, BLDALPHA `0x1008`.
  - The group state is right: 4 groups at `0x03000FF8`, k2 frame 142, k3 frame 141.
  - VRAM 596-714 equal the intended static tiles and group frames. No layer names tiles 596-830 except the 124 BG0 footprint cells.
- **Why the tests missed it.** They checked the table copy against "the first 167 vanilla words" and the 596 list entries, never the tile bytes the game loads. The new `LoadTests` load VRAM the way the game does. On the v1 ROM they find 155 vanilla tiles changed (441-595) and 146 entries past their chunk. On v2 they find 0 and 0.
- **The pale sphere (L).** The sphere tiles in the state equal mockup frame 142 exactly. The pale look most likely came from the white broken ground behind it.

### The clean cut (C)

- Two 13 px BF orbs cross the radius-25 disk edge: BF centre (150, 91) at the upper right, and (103.5, 126) at the lower left.
  - v1 kept their inside slices on the sphere: the wedge at the upper right, and a pale-blue sliver at the lower left. Their outside parts were never drawn.
  - Sources: `sphere_cut_view.png` and `.txt`.
- v2 leaves out every cut pixel within 7 px of either centre (44 pixels). So no part of either orb remains.
  - `sphere_v2_view.png` shows v1 on the left and v2 on the right.
  - The generator checks that both orbs still cross the edge, so a stale list raises.
- The frames still equal the mockup: `bridge.py` gives mockup_v2 the same cut, and the frames SHA-1 is `86ee47d69c03b591bb0142772b6f693cf0e061f7` in both, cell for cell. Tiles and groups do not change: 9 static tiles, 64 + 46 group tiles, 54 + 8 streams, tiles 596-714.

### Builds (v2)

| Build | SHA-1 |
|---|---|
| `log2_poc_r39_beam_v2.gba` (new, exclusive create) | `d7eed3c3b90a789edb935544dc261d01e6b69217` (same under two hash seeds) |
| `log2_poc_r39_beam_v2.sav` (byte copy of the same vegeta v3 save as v1) | `aa8efb2adaa7aa87f4cff27ceb7244368bd02759` |
| `--list` main | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` (r39) |
| r40 order scratch, in memory (all six apply now) | `3066f9bc2958c173e0a27e87e5f669be2043fdc2` |

- **Diff r39 to v2:** 41,067 bytes in 81 runs. Base 8 MB: only `rom:0x4091EC`-`0x4091EE`. Expansion: 80 runs from `rom:0x90A308` to `rom:0x9143BF`, all inside the 41,144 B beam block. Every run is listed in `diff_runs_v2.txt`.
- **r40 order with v2:** all six modules apply. `chapter_cards` changed at 8:14 PM (source SHA-1 `19aa4b1b...`, its "v3 fix" accepts packed data words). `beam_struggle` shares 0 bytes with each other module (`r40_order.txt`; the v1 run is in `r40_order_v1.txt`).
- **Full suite (once):** 854 tests: 852 pass, and 2 `test_chapter_cards` tests fail (`test_a_changed_source_byte_refuses_before_writing`, `test_enter_draws_the_card_and_starts_the_ported_song`).
  - `chapter_cards.py` and `test_chapter_cards.py` changed at 8:14 PM, while my run was going.
  - Run alone afterwards, `test_chapter_cards` passes 41 of 41. So I read the 2 failures as a mid-edit race, not a beam fault (L).
  - The beam tests in the same run: 26 of 26 pass.

### What to play (v2)

Load `log2_poc_r39_beam_v2.gba` with `log2_poc_r39_beam_v2.sav`. Use the same steps as below: slot 3, then the Cell Games, then win the Super Perfect Cell fight.

- Your v1 `.ss2` will not show the fix: a state holds VRAM and tiles that are already loaded. Load the save, not the state.
- The ground around the struggle must look like vanilla.
- The sphere edge has no orb wedge at the upper right and no sliver at the lower left.

---

## SHIPPED and PENDING (v1)

| Ask (my words, short) | Status | Where |
|---|---|---|
| "Go with the map tiles": build mockup v2 in the game | SHIPPED (trial) | `scripts\permanent\patches\beam_struggle.py` |
| Art made by a committed generator, never hand-copied | SHIPPED | `scripts\permanent\art\beam_struggle_art.py` (reads the BF ROM) |
| Tests that decode every record and compare with the mockup | SHIPPED: 20 tests, all pass | `scripts\permanent\tests\test_beam_struggle.py` |
| New list `build_list_trial_beam.txt` | SHIPPED | main list plus `beam_struggle`; `--list` still gives r39 |
| r40 order check | SHIPPED: no byte overlap; **`chapter_cards` refuses** in that order | "r40 order check" below |
| Trial ROM and save | SHIPPED | `builds\mockups\2026-10-25-beam-struggle\log2_poc_r39_beam.gba`, `.sav` |
| Full suite | SHIPPED: 832 tests, OK | `scripts\one-time\2026-10-25-beam-trial\suite.txt` |
| Bible rows, tag BMT | SHIPPED | `scripts\one-time\2026-10-25-beam-trial\bible_rows.md` |
| Emulator checks (timing, flash, seq 20 hide, text box) | PENDING (mine) | "What to play" below |
| Fix for the `chapter_cards` refusal | PENDING (my decision) | "r40 order check" below |

---

## What the module does

The module changes one base ROM word and adds one data block in the expansion area. It has no code, no script change and no palette change.

- **Base ROM:** `rom:0x4091EC`, the map 14,4 layout word, from `0x084E2E7C` to the layout copy. (C, diff)
- **Art source:** `beam_struggle_art.build()` renders BF map 3 BG3 from the BF ROM (SHA-1 checked) and runs the mockup v2 steps. The output equals the mockup frames. (C, `bridge.txt`)
  - BF screen: 0 of 38,400 pixels differ from the study render `bf_map3_bg3.png`.
  - Frames: 0 of 144 world-pixel frames differ from `mockup_v2.frame_art`.
  - Cells: 0 of 124 x 144 cell tiles differ from the `mockup_v2.count` cell rule.
- **Timing:** 144 frames of 5 ticks (12 s a loop), the same as the mockup. (C, records)

### Tiles

| Part | Cells | BG tiles | How it loads |
|---|---|---|---|
| Static (beam ends) | 14 | 596-604 (9, flip-folded) | 9 new index list entries, chunk 167 (C) |
| Group A, k2 (sphere, pulse, sway, flash, inner orbs) | 64 | 605-668 | animated group, 144 frame words, 54 streams (C) |
| Group B, k3 (outer orbs) | 46 | 669-714 | animated group, 144 frame words, 8 streams (C) |
| **Total** | **124** | **119 of the free 596-830** | 116 tiles stay free (C) |

- Group A is the 64 cells nearest the clash centre, world (443, 388). The k3 group changes 1 tick after k2 (init `@0x08005096` gives countdown k + 1). So the 1-tick seam falls only on outer orbs, never on the sphere. A test proves that group B holds only the 8-frame orb cycle. (C)
- Both groups stay within 64 tiles: 64 and 46. The load buffer is 0x1000 B (`add sp,#-0x1004` `@0x08005020`). Vanilla already runs 8 groups of 64 tiles. (C)
- Four groups fit the IWRAM state array: 16 fit (`0x03000FF8` to `0x0300107C`), and vanilla maps use up to 8. (C)
- The vanilla spark (k1) and starburst (k0) groups still run. No BG0 cell shows a spark tile now. (C, test)
- No vanilla cell on any 14,4 layer names a tile in 596-830, so the new art cannot show through a stray vanilla cell. BG0 names 0-595 and 831-842, BG1 0-595 and 843+, BG2 and BG3 0-595 only. (C, `tile_refs.txt`)

### Data block (trial ROM, `rom:0x90A308`, 0xA398 B = 41,880 B)

| Piece | Address | Content |
|---|---|---|
| Layout copy | `0x0890A308` | 0x50 B; +0xC = 4 groups, +0x10, +0x14, +0x48, +0x4C changed |
| Group list | `0x0890A358` | `0x084E2BE0`, `0x084E2E64` (vanilla), then group A, group B |
| Group A record | `0x0890A368` | {144, 64, 605}, 144 frame words |
| Group B record | `0x0890A5AC` | {144, 46, 669}, 144 frame words |
| BG0 record copy | `0x0890A7F0` | 0x58 B; only block 5 (block (1,1)) changes |
| Chunk table copy | `0x0890A848` | 167 vanilla words, word 167 = the static chunk |
| Index list | `0x0890AAE8` | type 1, 605 entries (596 vanilla, then chunk 167 tiles 0-8) |
| Static chunk | `0x0890AC0C` | type 1, 9 tiles |
| BG0 block (1,1) | `0x0890AC9C` | type 1; the 124 footprint cells changed, every other cell vanilla |
| Group frames | `0x0890ADDC`-`0x08914690` | {u32 5, bare stream}; group A packed 512-772 B (mean 702), group B 188-232 B (mean 210) |

All frames use the packed type 1 form, like the vanilla ones. The packer is a copy of the proven TRV vendor file (`scripts\permanent\rom\webfoot_lz_pack.py`). Every stream starts with 8-bit literal mode, so the decoder's entry r3 does not matter. The module decodes every stream before it writes. (C)

---

## Builds and SHA-1s

| Build | SHA-1 |
|---|---|
| `builds\mockups\2026-10-25-beam-struggle\log2_poc_r39_beam.gba` (new, exclusive create) | `05318b4ee086053dfa957e4ae0c625a42b47f55a` |
| `--list` main (in memory) | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` (r39, unchanged) |
| `log2_poc_r39_beam.sav` (byte copy of `log2_poc_r39_vegeta_v3.sav`) | `aa8efb2adaa7aa87f4cff27ceb7244368bd02759` |
| r40 order scratch ROM (in memory only, `chapter_cards` refused) | `7ae1b216c61103f80812fa2e0f92c211dc6b4f28` |

The build-log line was appended at 5:25 PM. The trial SHA-1 is the same under two hash seeds (C).

**Diff r39 to the trial ROM:** 41,792 bytes in 93 runs (C). Every run, with the piece it falls in, is in `scripts\one-time\2026-10-25-beam-trial\diff_runs.txt`.
- Base 8 MB: one run, `rom:0x4091EC`-`0x4091EE` (3 bytes; the high byte `0x08` is equal).
- Expansion: 92 runs from `rom:0x90A308` to `rom:0x91469F`, all inside the beam block. Bytes equal to 0xFF break the runs.

---

## Tests

`test_beam_struggle.py` has 20 tests. All pass. The expected values come from the base ROM, the bible rows and `bridge.txt`, not from the module.

| Class | Proves |
|---|---|
| ListTests (6) | the list is the main list plus the trial line; before = r39; the trial ROM SHA-1; a second run raises; 10 changed source bytes each refuse before any write; a module that lists the layout word refuses; two runs give equal bytes |
| SiteTests (2) | the base ROM changes only at `rom:0x4091EC`; expansion writes stay in the noted block, which was 0xFF |
| RecordTests (7) | the layout copy changes only 5 words; the vanilla groups come first and keep their bytes; each new group decodes to tiles x 64 B with duration 5; every stream starts with literal mode; the index list is 596 vanilla entries plus 9; the BG0 record changes only block 5; 124 block cells change, all to tiles 596-714 |
| TileTests (2) | only tiles 596-830 are used (596-714); no BG0 cell in any block names a spark tile or a beam-only tile |
| MockupTests (3) | the decoded screen cells equal the mockup frames cell for cell (SHA-1 `3348b7f5...`, 54 distinct frames); the 14 static cells and 9 unique static tiles; group B holds only the orb cycle |

**Full suite:** 832 tests, OK, 206 s (`suite.txt`). That is the 805 of the brief, plus my 20, plus 7 more tests from other tasks' files (count only, not traced).

---

## r40 order check

Order: `celljr_fight`, `beam_struggle`, `vegeta_ssj_scene`, `relay_cooldown`, `fullpower_hud`, `chapter_cards` on the main list (`r40_order.txt`).

| Module | Result | Bytes changed |
|---|---|---|
| `celljr_fight` (source SHA-1 `2683ae9e5b557e75864b6be6aae4f3ab95d7279e` at my run) | applied | 882 |
| `beam_struggle` | applied | 41,791 |
| `vegeta_ssj_scene` | applied (it repoints `rom:0x3EC798`, seq 17) | 420 |
| `relay_cooldown` | applied | 31 |
| `fullpower_hud` | applied | 206 |
| `chapter_cards` | **REFUSED**: "data chunk rom:0x9216C0 is named by patch words [9505940]: stop and report" | 0 |

- **No overlap with four modules in the r40 order (C).** `beam_struggle` shares 0 bytes with `celljr_fight`, `vegeta_ssj_scene`, `relay_cooldown` and `fullpower_hud` (byte diffs plus the noted sites).
- **No overlap with `chapter_cards` (C).** In the r40 order `chapter_cards` refused, so its write set there is empty and proves nothing. The proof comes from the order where all six apply (`celljr_fight`, `chapter_cards`, `beam_struggle`, `vegeta_ssj_scene`, `relay_cooldown`, `fullpower_hud`): `beam_struggle` (41,884 B) and `chapter_cards` (106,192 B) share 0 bytes, and so do the other four pairs.
- **Base ROM (C).** The only base byte range of `beam_struggle` is `rom:0x4091EC`-`0x4091EF`. No other module writes it, alone on r39 or in either order.
- **The refusal (C).** `chapter_cards` rejects any expansion word in 0x08000000-0x0A000000 that names its new data chunk. A beam codec word, `rom:0x910C94` = `0x08926D91` (group A frame 33 + 0x78 in this order), falls in that range. It is stream data, not a pointer. The refusal comes before any `chapter_cards` write, so the scratch ROM simply lacks `chapter_cards`.
- **Orders that apply (C):** `chapter_cards` before `beam_struggle` (`af7b6d192cc25cebe7c86eee467cbf40e96c30a9`), or `beam_struggle` last (`710898485799722a2dc884573c0a44545b72388b`). r39 + `chapter_cards` + `beam_struggle` also applies. r39 + `beam_struggle` + `chapter_cards` refuses the same way.

> [!WARNING]
> I did not change the beam data or `chapter_cards` to avoid the refusal. Choose one fix for r40: put `chapter_cards` before `beam_struggle` in the list, or let `chapter_cards` skip words inside another module's noted data block. The second is a `chapter_cards` change, which another task owns.

---

## What to play

Load `builds\mockups\2026-10-25-beam-struggle\log2_poc_r39_beam.gba` with the `.sav` next to it. The ROM is r39 plus `beam_struggle` only.

1. Pick **slot 3**: Cell Games Arena arrival, map 14,1, Goku leads. Flag 191 is set and flag 195 is clear (C, `log2_save.py info`).
2. Play the Cell Games through the Cell fight, the self-destruct and Super Perfect Cell's return.
3. Win the Super Perfect Cell fight. The struggle starts at once: map 14,4 loads in seq 1.
4. Make a state when both fighters hold the beam pose: `builds\mockups\2026-10-25-beam-struggle\log2_poc_r39_beam.ss1`. Then you can repeat the checks without the fights.

I found no closer save in `builds\` or `test-data\saves\` (C, `log2_save.py info` on the r39, vegeta v3 and test saves). I did not make a save at a later point, because the fights and the struggle play as one scene run (L). The state in step 4 is the fast way back.

Check these points. Each needs the emulator; I did not run one.

| Check | Expected | Label now |
|---|---|---|
| The picture | as `art\mockups\2026-10-25-beam-struggle\mockup_b2.gif`: sphere pulse, 8 orbs out of the edge, sway, beams joined to both hands | C (data equals the mockup), S (on screen) |
| Beam ends at the hands | both beam tips touch the hands. The mockup used base `set:30` and `set:58` (BMG row: L, r30 reused word 58). If a tip misses a hand, tell me which side and by how many px | L |
| Frame timing | pulse step 10 ticks; orb step 5 ticks; no stutter when the groups change every 5 ticks | L (packed frames are smaller than the vanilla starburst frames; vanilla runs 64-tile groups) |
| The 1-tick seam | an orb that crosses from group A to group B cells may split for 1 frame (17 ms); the sphere never splits | C (group split), L (not visible) |
| The flash | 3 soft flashes in 12 s (3.3 s, 3.8 s, 4.8 s apart), only the sphere area, no strobe | C (frames), S (on screen) |
| The text box | the art keeps moving while a box waits for A; note where the box sits against the sphere | L (field tick runs in the scene, BMS row) |
| The seq 20 hide | at the flash before the final Kamehameha, all new art vanishes with BG0 (`ext 24 (0)`) | C (code, BMS row), S (on screen) |
| Tile viewer (BG, 256 colours) | tiles 596-714 hold the art; 715-830 are empty | L |
| Map load | no garbage tiles during the seq 1 flash (frame 0 of every group loads with the map, `@0x08005196`) | C (listing) |

---

## Limits kept and notes

- Nothing under `data\` was written. No ROM, save or state was overwritten: the ROM and the `.sav` were made with exclusive create.
- No existing module, test or list was edited. New permanent files: `beam_struggle_art.py`, `webfoot_lz_pack.py`, `patches\beam_struggle.py`, `tests\test_beam_struggle.py`, `build_list_trial_beam.txt`.
- `webfoot_lz_pack.py` is the TRV vendor packer (MPL-2.0, Buu's Fury decomp) with a project header. The code below the header is byte for byte the vendor copy. It is a new permanent tool; the bible TRV row already records its round trip.
- `art\base-audit\`, `scripts\one-time\2026-10-23-base-audit\` and `docs\RE-BIBLE.md` were not touched.
- One Bash heredoc lost a backslash (the known trap): the first `build_list_trial_beam.txt` had a backspace byte in its header comment. I rewrote the file with Python before any build read it, and checked its bytes.
- Files in `scripts\one-time\2026-10-25-beam-trial\`: `bridge.py` and `.txt`, `pins.py` and `.txt`, `group_counts.py`, `group_sizes.py` and `.txt`, `tile_refs.py` and `.txt`, `bl_callers.py`, `peek.py`, `words_naming.py`, `r39_equal.py`, `r40_order.py` and `.txt`, `make_trial.py` and `.txt`, `diff_runs.py` and `.txt`, `make_pack_copy.py`, `suite.txt`, `bible_rows.md`.
