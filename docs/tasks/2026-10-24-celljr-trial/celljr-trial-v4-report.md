# Cell Jr trial v4: the 2 moved Jrs go to my circles (2026-10-25)

The v4 trial ROM and an all-trials Vegeta ROM are built. The 2 Jrs that v3 put at the right edge now stand in my two yellow circles. The main build is still r39.

Labels: **C** = CONFIRMED (bytes, state, image pixels or test), **L** = LIKELY, **S** = SPECULATIVE. Addresses are in the v4 ROM unless a line says otherwise. The state is my `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v2_cj3.ss1` (2:38 PM, spawn scene after seq 27), dumped read only to `scratch\review-renders\2026-10-25-celljr-v4\cj3_ss1\`.

---

## SHIPPED

| Ask | Result |
|---|---|
| "it looks better if they spawn in the yellow circle and not awkwardly outside to the side" | The 3rd and 4th extra Jrs of the seq 31 copy move from (536,384) and (544,416) to **(388,366)** (left circle) and **(476,370)** (right circle). Each Jr's sprite box centre is within 1 px of its circle centre (C bytes and test, L in game) |
| Re-derive the spots from the image | Done from the pixels, not by eye: 7 of 7 Jrs fit one mapping (C). Your estimates (390,364) and (476,368) differ by 2 px at most. See "Screen to world" |
| On screen, open cells, no overlap, not in front | All 4 checks pass (C). See "Checks" |
| Keep everything else from v3 | Only 8 bytes changed, all inside the 2 push operands. Every allocation equals v3 and v2 (C, `make_trial_v4.txt`) |
| Tests | `test_celljr_fight` 39 OK: 2 new, 1 replaced, 1 updated (C) |
| `--list` still gives r39 | CLI `--list` SHA-1 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`, bytes equal to `builds\log2_poc_r39.gba` (C) |
| `test_vegeta_ssj_scene` green without edits | 33 OK. No pinned SHA-1 or address moved, because no allocation moved (C) |
| v4 ROM and save, exclusive create | `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr_v4.gba` and `.sav` (C) |
| Vegeta ROM and save, exclusive create | `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v3_cj4.gba` and `.sav` (C) |
| Before and after renders | 3 PNGs at your screenshot's size. See "Renders" |
| Diff runs v3 to v4 | 2 runs, 8 bytes. See "Diff runs" |
| Bible rows, tag CJ4 | `scripts\one-time\2026-10-24-celljr-trial\bible_rows_v4.md` (sections 4, 8, 9, 11, 12, 13) |

## PENDING

| Item | Why |
|---|---|
| Full suite: 8 errors in `test_chapter_cards` | Another task was editing `patches\chapter_cards.py` during my run (file time 5:10 PM; `NameError: MUSIC_TABLE`). Its list `build_list_trial_chapters.txt` does not hold `celljr_fight`. A re-run of that file alone at 5:11 PM still fails (3 failures, 1 error), so the task that owns it must finish first. Not mine to touch |
| Me: emulator play test | No emulator run in this task. Every in-game claim is L |
| Me: the right circle is snug | Its inside is 22 px tall, and a Jr is 23 px tall. The Jr fills it edge to edge, and in the render your pen line crosses its feet (C arithmetic) |
| Carried from v3, not built | A frame with no Cell at the swap; Cell cut to head and shoulders by record X's view; fight Jr item 14 at (528,408) just above Cell's head; Cell turns from right to up at the swap. v4 does not touch these |
| Me: merge the CJ4 rows | See the rows file's merge notes |
| Approval | As before: move the `celljr_fight` line to `build_list.txt` and update the 3 tests the v1 report names |

---

## Screen to world (C)

**The camera, from the state.** The spawn scene view is (328,312), the target of seq 24 `ext 31 (328, 312, 2)`. Three actors in the cj3 ss1 OAM prove it:

| Actor | World | OBJ | Frame offset | Camera |
|---|---|---|---|---|
| Gohan | (400,440) | obj 4 (72,104) 16x32 | dx 0, dy -24 | (328,312) |
| Jr | (408,392) | obj 7 (80,56) 16x32 | dx 0, dy -24 | (328,312) |
| Cell | (500,440) | obj 5 (152,72) 64x64 | dx -20, dy -56 | (328,312) |

**The screenshot, from its pixels** (`screen_map_v4.py`, listing in `study_v4.txt`).
- It is an mGBA screen at 4x nearest scale. Colour edges fall on x = 1 (mod 4) and y = 3 (mod 4).
- Jr pixels (blue >= red) form 7 Jr-shaped blobs. One camera fits all 7 with no residual on the left, top and bottom edges. Cell's cape forms an eighth blob, which the shape filter rejects.
- **Formula:** screenshot px (sx, sy) = world (357 + floor((sx - 1) / 4), 333 + floor((sy - 3) / 4)).
- So the image is a crop of the (328,312) view. 29 game px are cut on the left (the "State ... loaded" text is cut there too), 21 on top and 7 at the bottom. The dark band from sx 845 starts at world x 568, the view's right edge.

**The circles.** The inside of each pen loop is the set of pixels that cannot reach the image edge without crossing yellow.

| Circle | Inside, world | Centroid | Inside box centre | Spot (Jr box centre on the centroid) | Your estimate |
|---|---|---|---|---|---|
| Left (above the left group) | x 383-408, y 347-374 | (396.2,361.5) | (395.5,360.5) | **(388,366)** | (390,364) |
| Right (between the middle Jrs and Cell) | x 472-495, y 355-376 | (484.1,366.1) | (483.5,365.5) | **(476,370)** | (476,368) |

- A Jr at (x, y) draws its opaque box at x+1..x+15, y-15..y+7 (CJ3 row), so its centre is (x+8, y-4). The spot is the centroid minus that offset, rounded.
- **Where we differ:** 2 px left and 2 px down on the left Jr, 2 px down on the right Jr. I put the sprite's centre on the circle's centre; you may have used the feet.
- The blue pixels span x+1..x+13, not x+15 (the last 2 columns hold other colours). Centring on them would move both spots 1 px right. I used the full opaque box.

## The new positions and their bytes (C)

The seq 31 copy is at `rom:0x90A308`, named by spawn table word 30 (`rom:0x3E9DC4`).

| Group | Push | x, y bytes | v3 | v4 |
|---|---|---|---|---|
| 1 | `rom:0x90A30F` | `rom:0x90A312`-`0x90A315` | (384,408) | (384,408) |
| 2 | `rom:0x90A324` | `rom:0x90A327`-`0x90A32A` | (480,408) | (480,408) |
| 3 | `rom:0x90A339` | `rom:0x90A33C`-`0x90A33F` | (536,384) `1d033e883086000233` | **(388,366)** `1d033e8608855c0233` |
| 4 | `rom:0x90A34E` | `rom:0x90A351`-`0x90A354` | (544,416) `1d033e884086400233` | **(476,370)** `1d033e873885640233` |

- Every new value is a 2-byte zigzag push, as before. So the record keeps its length, and no later allocation moves.
- Module: `EXTRA_SPAWNS` in `scripts\permanent\patches\celljr_fight.py`, with its comment and the Method text updated.

## Checks (C unless marked)

| Check | Left (388,366), box x 389-403, y 351-373 | Right (476,370), box x 477-491, y 355-377 |
|---|---|---|
| On screen in the seq 24 view (x 328-567, y 312-471) | yes | yes |
| Inside your screenshot crop too (x 357-567, y 333-464) | yes | yes |
| Collision cells open (cj3 ss1 bitmap `@0x0203BFF8`; every cell in the view is open) | open | open |
| Nearest Jr | (408,392): 5 px right, 3 px down, no overlap | (456,392): 5 px left, no overlap; (480,408): 15 px below |
| Gohan (box x 400-415, y 416-447) | 42 px above his box top | 38 px above, 61 px to his right |
| Cell (box x 498-526, y 390-447) | far | 6 px left of his box, 12 px above it |
| Allies (cj3 ss1: (296,104), (256,112), (520,104), (448,112), (552,96)) | about 200 px above the view | same |
| Not in front of Gohan and Cell | box bottom y 373, above both box tops (416, 390) | box bottom y 377, above both |

- Both new Jrs stand behind the first extra row (y 408) and at about the vanilla row's depth (376-392).
- The allies are in the cj3 state, taken after Piccolo's seq 5-7 actions. No ally sprite shows in your screenshot either.
- Tests: `test_the_moved_pair_stands_in_the_owners_circles`, `test_the_moved_pair_stands_behind_gohan_cell_and_the_first_row`, and `test_every_jr_fits_the_view_and_clears_cell_gohan_and_the_others` (now with the allies).

## Renders (C model, mock-up)

Files are in `scratch\review-renders\2026-10-25-celljr-v4\`:
- `celljr_v4_before.png`: your screenshot, with white boxes on the 2 Jrs that move.
- `celljr_v4_after.png`: the same image, with those 2 Jrs covered by ground and drawn at the v4 spots. Your circles are drawn on top.
- `celljr_v4_compare.png`: both side by side.

How the "after" image is made (`render_v4.py`):
- The Jr is the ROM's set 31 frame with the state's OBJ palette. It matches a real Jr in your screenshot 3568 of 3568 px.
- The ground under the old spots is copied from 16 game px to the left. That is clean ground on the same 8 px tile grid. 0 Jr pixels remain.
- It is a mock-up, not an emulator capture. The label in the dark band says so.

## SHA-1s (C)

| File | SHA-1 |
|---|---|
| `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr_v4.gba` | `abbe5004f7d645329e8a141fadf70096ef6960c5` |
| `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr_v4.sav` (copy of the v3 save) | `aa8efb2adaa7aa87f4cff27ceb7244368bd02759` |
| `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v3_cj4.gba` | `b5e2019f579a8cbffceaf2588678242004cc0129` |
| `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v3_cj4.sav` (copy of the Vegeta v3 save) | `aa8efb2adaa7aa87f4cff27ceb7244368bd02759` |
| CLI `--list` (main) | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` = r39 |
| CLI `--list build_list_trial.txt`, `--list build_list_trial_vegeta.txt` | equal to the v4 and Vegeta cj4 ROMs |
| Sources checked: celljr v3, Vegeta v3 | `76e610fb...`, `6d80e874...` (both match their build-log lines) |

- Before the module edit, both trial lists were built in memory from the current tree. They reproduced `76e610fb...` and `6d80e874...`, so the Vegeta base had not drifted.
- Every target was checked before the first write and opened with `"xb"`. No ROM, save or state was overwritten.
- `docs\build-log.md` has one new line per ROM (4:56 PM).

## Diff runs (C, `make_trial_v4.txt`)

**v3 to v4: 8 bytes in 2 runs, 0 outside a site.**

| Run | Bytes | Site |
|---|---|---|
| `rom:0x90A33C`-`0x90A33F` | 4 | seq 31 copy, group 3 x and y ((536,384) to (388,366)) |
| `rom:0x90A351`-`0x90A354` | 4 | seq 31 copy, group 4 x and y ((544,416) to (476,370)) |

- **Vegeta v3 to Vegeta v3 cj4:** the same 2 runs and 8 bytes ("vegeta runs == celljr v3 -> v4 runs: True"). The `vegeta_ssj_scene` sites keep their addresses (`rom:0x90A67C`, `0x90A780` and its 3 base sites).
- **r39 to v4:** 882 bytes in 12 runs, 0 outside the 27 named sites, and no site without a change. These are the same runs as v3.

---

## Tests

| Run | Result |
|---|---|
| `test_celljr_fight` | 39 OK (v3: 38) |
| `test_vegeta_ssj_scene` | 33 OK, file not edited |
| Full suite, once at the end (`py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v`) | Ran 791: 785 OK, 8 errors, all in `test_chapter_cards` (PENDING row 1). `suite_v4.txt` |

- **Count:** 791 ran + 15 tests not run (the `CodeTests` (8) and `RunTests` (7) classes, whose setUpClass failed) = 806 = your 805 + my net 1 (C).
  - Between the brief (4:23 PM) and my run (about 5:08 PM), the only test file that changed was mine (file times). `test_chapter_cards.py` was last changed at 3:18 PM then.
  - `test_beam_struggle.py` (5:17 PM) appeared after my run and is not in it.
- **New:** `test_the_moved_pair_stands_in_the_owners_circles` and `test_the_moved_pair_stands_behind_gohan_cell_and_the_first_row`. They replace `test_the_front_pair_moved_behind_cell`, which encoded the v3 rule.
- **Updated:** `test_every_jr_fits_the_view_and_clears_cell_gohan_and_the_others` now also checks the allies.
- **Kept:** `test_the_check_rejects_the_v2_front_pair`.
- The circle centres and the ally spots are restated as constants, with their source, and are not imported from the module.

## Files

| File | What |
|---|---|
| `scripts\permanent\patches\celljr_fight.py` | `EXTRA_SPAWNS` groups 3 and 4, the comment, the header and Method item 1 |
| `scripts\permanent\tests\test_celljr_fight.py` | 39 tests |
| `scripts\one-time\2026-10-24-celljr-trial\screen_map_v4.py` | Screenshot to world mapping and circle centres |
| `scripts\one-time\2026-10-24-celljr-trial\render_v4.py` | The before and after renders |
| `scripts\one-time\2026-10-24-celljr-trial\make_trial_v4.py`, `make_trial_v4.txt` | Both ROMs and saves by exclusive create, CLI proofs, positions, diffs |
| `scripts\one-time\2026-10-24-celljr-trial\study_v4.txt` | Listings: mapping, cj3 ss1 OAM and actors, collision, render checks |
| `scripts\one-time\2026-10-24-celljr-trial\suite_v4.txt` | Full suite output |
| `scripts\one-time\2026-10-24-celljr-trial\bible_rows_v4.md` | CJ4 rows |

- The CLI proofs went to `scratch\test-roms\celljr_v4_cli_main.gba`, `celljr_v4_cli_trial.gba` and `celljr_v4_cli_vegeta.gba` (log `celljr-v4-cli-log.md`).
- **Limit breach:** one read-only Bash call began with `cd /c` to run an in-memory build check. It wrote no file. Every other call used absolute paths only.
- **Not touched:** `vegeta_ssj_scene.py`, `relay_cooldown.py`, `fullpower_hud.py`, `chapter_cards.py` and their tests, every build list, `beam_struggle`, `art\base-audit\`, `scripts\one-time\2026-10-23-base-audit\` and `docs\RE-BIBLE.md`.

---

## What to watch in play

Load `log2_poc_r39_celljr_v4.gba`, or `log2_poc_r39_vegeta_v3_cj4.gba` for all trials, from slot 3 as before. Old `.ss*` states belong to their own ROMs: do not load them on v4.

1. After "My children! Give them pain!", 4 Jrs pop in with a flash:
   - the 1st is left of the group;
   - the 2nd is just left of Cell;
   - the 3rd is in your left circle, above the left group;
   - the 4th is in your right circle, between the middle Jrs and Cell, toward the top.
   Pass: no Jr at the right edge, none in front of Gohan or Cell, and every Jr fully on screen.
2. Everything else is v3: Cell stays put at the swap, the Jrs walk down from the top, and the fade comes before "You wretched child".

## Risks

| Risk | Status | Label |
|---|---|---|
| The spots miss your circles in game | The mapping fits 7 of 7 Jrs and the camera is exact in your state. The ROM frame matches your screenshot pixel for pixel | C (model), L (in game) |
| The left Jr crowds the vanilla Jr (408,392) | Boxes 5 px apart in x and 3 px in y, no overlap. Your circle puts it there | C (arithmetic) |
| Vegeta build drift | Same 8 bytes; no allocation moved; the Vegeta v3 base reproduced before the edit | C |
| `test_chapter_cards` errors | Another task's edit in progress, not on the celljr build path | C (traceback, list) |
