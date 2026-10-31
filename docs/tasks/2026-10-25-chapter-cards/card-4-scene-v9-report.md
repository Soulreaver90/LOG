# Card 4 scene v9: the row on open ground (2026-10-30)

Brief: `card-4-scene-v9.md`. Labels: CONFIRMED (C) = ROM bytes, render, collision or a test run; LIKELY (L) = strong evidence, no emulator run.

---

## SHIPPED

| Ask | Result |
|---|---|
| 1. Render 8,1 and pick a clear patch | Patch west of the central trees, y 84, x 24-144. Section "Patch" |
| 2. Row, player spot and camera moved, all three branches | One set of six spots for all branches; the player spot is open and not boxed in (flood fill). Section "Positions" |
| 3. Plan picture | `builds\mockups\2026-10-25-chapter-cards\v9_row_plan.png` (3x, row drawn under the BG1 trees as in game) |
| 4. Tests, ROM, save, diff, suite | `test_chapter_cards.py` 69 OK (one new test). `log2_poc_r40_chapters_v9.gba` and `.sav`. v8 to v9: 129 runs, 0 outside a site. Full suite 973 OK |
| Bible rows | `scripts\one-time\2026-10-25-chapter-cards\bible_rows_c4v.md`, tag C4V |

## PENDING

| Item | Why | My step |
|---|---|---|
| The scene in play | No emulator run | Play the v9 ROM with the v9 save, as in the v8 play steps; check each branch by eye |
| NPCs on the save point | Spots 2-4 (x 48, 72, 96) stand inside the save point rect (56,48)-(105,97), on a BG3 leaf ring that is likely its mark (L). Not checked: whether the save point object (factory `0x08010AC7`) draws an OBJ marker that the NPCs would overlap. The brief bans trees, bushes and rocks only. The player stands outside the rect, so A does not open the save menu after the scene | Say if they must move off it. No other six-wide row exists, so the fix would be a smaller pitch or two rows |
| Row and text box | Not checked: where the dialog box draws. The sprite tops are at screen y 56 | In play, check that the row stays visible while a text box shows |
| Build log line | `docs\build-log.md` is outside this task's files | Append the v9 line, or ask me to |

---

## Patch

Map 8,1 is small: 376x200 px (C: render and collision). Layout +8/+0xA = 137, 41 is likely the camera clamp: the same field on 9,1 holds 1297, 865, against the known clamp 1296, 864 (L, off by one). Camera (0,4) is inside it either way.

**Why the v8 row failed (the checker reproduces my words):** at y 128, Krillin (152), Tien (176) and Gohan (200) stand under BG1 tree canopies and on closed cells, Piccolo (224) is under a canopy edge, and the player at (272,128) has the rock at (272-287, 120-127) in his sprite. C (`c4v_patch.py` on the v8 spots).

**Check per actor:** box x - 8..x + 24, y - 28..y + 8 (wider than the 16x32 sprite at y - 24, so a 32-wide set fits). Clear = no BG1 pixel (drawn over actors), no BG2 pixel (rocks, pebbles, flowers), every collision cell open (trunks, bushes, rocks).

**Result:** over the whole map, the only clear row of six at pitch 24 is y 84, first x 24. The middle band (y 64-104) is cut by the two top trunks (x 192-207 and 304-319, down to y 71) and two pebble groups. The right side near the flight pad is about 104 px wide, too narrow for six. C (`c4v_patch.txt`).

## Positions

| Item | v8 | v9 |
|---|---|---|
| NPC row (left to right) | x 152-248, y 128 | x 24, 48, 72, 96, 120, y 84 |
| Player (first landing, `ext 39`) | (272,128) | (144,84), farthest right |
| Camera `ext 31` | (92,44,255), clamped to y 41 | (0,4,255), inside the clamp |
| Spawn y (`ext 51`) | 300 | 260 (about v8's fly distance; sprite top 236 is below the view bottom 164) |
| Fly-off y (`ext 54`) | -40 | -40 |
| Later landings (`ext 38`) | (272,128) | (272,128), vanilla, unchanged |

Branch orders are unchanged: Gohan leads: Krillin, Tien, Trunks, Vegeta, Piccolo. Piccolo leads: Krillin, Trunks, Vegeta, Gohan, Tien. Vegeta leads: Krillin, Tien, Gohan, Piccolo, Trunks (Trunks stays next to the player).

**Player after the scene:** the foot box at (144,84) is open. A flood fill from it reaches 2554 positions, the flight pad and the west and north map edges. C (`c4v_row_plan.txt`, and the new test).

**Camera hand-back (L):** `ext 33 (0)` makes the follow camera aim at about (32,4) (offset 112,80, bible R31 row), so the view eases about 32 px right when control returns. The row sits left in the view because the camera cannot go below x 0.

---

## Build and diff

| Item | Value |
|---|---|
| r40 (list before `chapter_cards`) | SHA-1 `14d6b8314f5f418f80021fe60ef8d052b5dcf2be` |
| **v9 ROM** | `log2_poc_r40_chapters_v9.gba` SHA-1 `fc84155519296ac415537d89e6ea897939537ad6` |
| **v9 save** | `log2_poc_r40_chapters_v9.sav` SHA-1 `d5a44ccc83b741f0265024fc1848dd0b134a9765` (byte copy of v8) |
| Landing chunk | `rom:0x93A148` +0x6C5 (v8 +0x6DA: shorter varints for the small x values) |
| Code block | `rom:0x93A810` +0x314 (v8 `0x93A824`: it follows the landing chunk), 0 skipped |
| r40 to v9 | 921 runs, 0 outside a v9 site |
| v8 to v9 | 129 runs (2252 bytes), 0 outside: each byte is in a v9 site or reverted to r40 inside a v8 site |

Listing: `scripts\one-time\2026-10-25-chapter-cards\c4v_build.txt`. Suite: `c4v_full_suite.txt`.

---

## Changes

- `chapter_cards.py`: new `ARRIVE = (8,1,1,144,84)` for the first-landing `ext 39` and the row x; `ROW_Y` 84, `FROM_Y` 260, `CAMERA` (0,4,255). `LAND` stays the vanilla spot for the plain `ext 38`.
- `test_chapter_cards.py`: record 0 bytes (`push 8,1,1,144,84`), the row, spawn, fly and camera values restated; new test `test_row_stands_on_open_ground_and_the_player_can_walk_off` reads the 8,1 collision frame from the ROM, checks every actor box is open, the view holds every sprite, the spawn and fly-off rows are off it, and the player can reach the flight pad.

## Notes

- The plan picture's black 8x8 squares are tile ids past the layout tile list (L: animated grass slots). In game they show grass.
- BG1 canopy and BG2 rocks are checked in `c4v_patch.py` only; the unit test checks collision (PIL stays out of the tests).
- Process: two Bash calls started with `cd`, which the brief forbids: `cd /c/` before a folder listing, and `cd` into the one-time folder to make 3x crops. Neither wrote a file outside the scratchpad.

## Files

- Module and tests: `scripts\permanent\patches\chapter_cards.py`, `scripts\permanent\tests\test_chapter_cards.py`.
- One-time: `c4v_probe.py` and `.txt`, `c4v_81_ground.png`, `c4v_81_over.png`, `c4v_81_full.png`, `c4v_patch.py` and `.txt`, `c4v_row_plan.py` and `.txt`, `c4v_build.py` and `.txt`, `c4v_full_suite.txt`, `bible_rows_c4v.md`.
- Builds: `builds\mockups\2026-10-25-chapter-cards\v9_row_plan.png`, `log2_poc_r40_chapters_v9.gba`, `log2_poc_r40_chapters_v9.sav`.
