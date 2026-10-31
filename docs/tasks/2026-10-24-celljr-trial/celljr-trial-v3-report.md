# Cell Jr trial v3: my play-test fixes (2026-10-25)

The v3 trial ROM and an all-trials Vegeta ROM are built with both fixes. The main build is still r39.

Labels: **C** = CONFIRMED (bytes, listing, state or test), **L** = LIKELY, **S** = SPECULATIVE. Addresses are r39 (`builds\log2_poc_r39.gba`, SHA-1 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`, read and checked) unless a line names a trial ROM. RAM values come from my v1 states (`log2_poc_r39_celljr.ss1` at spawn table seq 2, `.ss2` at Gohan table seq 24), dumped read only. The v1 ROM runs the vanilla records in both stretches, so the states show vanilla positions.

---

## SHIPPED

| Ask | Result |
|---|---|
| 1. "Cell just awkwardly teleport to the right ... why not just have him stay where he is?" | Item 17 (the NPC Cell) now stands at (512,472), where the type 24 Cell stands when record X runs. v2 used (616,384). Record N still moves him behind the fade (C bytes and state, L in game) |
| 2. "2 spawn directly in front, too close to Gohan and Cell, maybe have them spawn in the back" | The 3rd and 4th extra Jrs of the seq 31 copy move from (408,424) and (456,424) to (536,384) and (544,416): behind Cell, on his far side from Gohan (C bytes, L in game) |
| Keep the rest of v2 | Records X, C, N, the seq 58 copy, table T and items 13-16 are byte equal to v2. Only 7 bytes changed (C, `make_trial_v3.txt`) |
| Tests for both changes | 5 new tests, 2 updated; `test_celljr_fight` 38 OK |
| Full suite once at the end | 771 OK (C, `scripts\one-time\2026-10-24-celljr-trial\suite_v3.txt`). The brief's 744 + my 5 = 749. The other 22 are `test_fullpower_hud` (22 tests), a file another task created at 1:08 PM today, during this task (C: file time; 771 - 22 = 749) |
| Main `--list` still gives r39 | CLI `--list` SHA-1 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`, bytes equal to `builds\log2_poc_r39.gba` (C) |
| v3 ROM, exclusive create | `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr_v3.gba`, SHA-1 `76e610fb3ca4febcf1cefd1199ef39fad10ccbf8`. The CLI trial build gives the same SHA-1 (C) |
| v3 save | `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr_v3.sav` = byte copy of the v2 save, SHA-1 `aa8efb2adaa7aa87f4cff27ceb7244368bd02759` (C) |
| All trial changes in one ROM | `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v2_cj3.gba`, SHA-1 `f94fd65807a7db0957fcbc34b65c0473282f6b09` (CLI gives the same). Save `log2_poc_r39_vegeta_v2_cj3.sav` = byte copy of the Vegeta v2 save, SHA-1 `aa8efb2a...` (C) |
| Vegeta tests green without edits | `test_vegeta_ssj_scene` 26 OK, `test_relay_cooldown` 18 OK. No test there pins a celljr SHA-1 or address that moved: no allocation moved (C) |
| Diff runs | Below, in full in `make_trial_v3.txt` |
| Bible rows, tag CJ3 | `scripts\one-time\2026-10-24-celljr-trial\bible_rows_v3.md` (sections 4, 8, 9, 11, 12, 13) |

## PENDING

| Item | Why |
|---|---|
| Me: a frame with no Cell at the swap? | LIKELY yes, one frame or more. See "The swap itself". Two fixes are proposed, neither is built |
| Me: Cell at the bottom edge in the Jr fight | X's camera `ext 31 (456,288,2)` shows y 288-447. Cell's sprite spans y 422-479 at (512,472), so only his head and shoulders show during the walk-in (C arithmetic, L on screen). Option: view top about 320 and `FLY_FROM_Y` 280 (two constants). Not built: the brief keeps the v2 walk-in |
| Me: a fight Jr lands just above Cell | With Cell now at (512,472), item 14's landing spot (528,408) puts that Jr's box (x 529-543, y 393-415) 6 px above Cell's head (box x 510-538, y 422-479). The boxes do not overlap, but this is the same "too close to Cell" look (C arithmetic, L on screen). Option: item 14 x 544 (one constant in `FIGHT_AT`). Not built: the brief keeps the v2 fight spots |
| Me: Cell turns at the swap | The enemy Cell faces right (ss2 facing byte 3). The NPC's face step turns him up at once, because Gohan (576,376) is 96 px up and 64 px right (L) |
| Emulator play test (checklist below) | No emulator run in this task. Every in-game claim is L or S |
| Me: merge the CJ3 rows | See the rows file's merge notes. One row supersedes the CJR study's (616,384) claim |
| Approval | As v2: move the `celljr_fight` line to `build_list.txt` and update the 3 tests the v1 report names |

---

## Change 1: Cell stays where he stands

**Where Cell stands when X runs (C, two shapes).**
- **State.** In v1 ss2 (Gohan table seq 24, "I just let you die!") the type 24 Cell (object `0x020359DC`, vtable `0x080252A4`) has +0x158 = `0x20000` and +0x15C = `0x1D800`. Positions are 8.8 fixed point, so he stands at **(512,472)**, facing byte +0x10 = 3 (right).
- **Bytes.** (512,472) is item 11's spot (`rom:0x4090C8` +0xC = `0002 d801`, s16 512, 472). Gohan's seq 1 (`0x0889A71C`) builds item 11 with `push 11 ; ext 84`, and `ext 84` builds an item at its own spot (SPC row).
- **Nothing moves him later.** Words 1-29 hold no position op on actor 30 (`ext 51`, 53, 54, 62). Seqs 25-30 touch only the player. Test `test_nothing_places_cell_between_his_build_and_x`.

**Why v2 used (616,384) (C state, S op meaning).** Seq 19 (`0x083EA222`) runs `ext 99 (30, 616, 384, 100)` and `ext 100 (30, 616, 384)` in a group. The CJR study read this as Cell moving there. The ss2 state, taken after seq 19, shows him at (512,472). Both ops only queue a command with the point: ext 99 `@0x0800A210` (vtable `0x08024A50`), ext 100 `@0x0800A4DA` (vtable `0x08025230`). The point is near Android 16's head, where Hercule left it (seq 12 `ext 53 (72, 616, 376)`).

**What v3 does (C, tests `test_item_17_stands_on_item_11s_spot`, `test_item_17_is_an_npc_cell_with_the_face_player_step`).**

| What | Address (v3 ROM) | v2 | v3 |
|---|---|---|---|
| Item 17 x | `rom:0x90A624`-`0x90A625` | 616 (`6802`) | 512 (`0002`) |
| Item 17 y | `rom:0x90A626`-`0x90A627` | 384 (`8001`) | 472 (`d801`) |

- `CELL_STANDS` is read from the `ITEM11_AT` source bytes, which `_check` verifies before the first write. So item 17 cannot drift from item 11.
- Record N still runs `ext 62 (30, 616, 384)` behind the fade, as the brief asks (test `test_n_fades_and_brings_cell_back`, unchanged).

### The swap itself (L: a frame with no Cell)

- An actor command outside a group blocks. `actor_queue` `@0x0800E04C` reads the group flag (`@0x0800E068 ldr r0,[r0,#0x0] ; cmp r0,#0x0 ; bne`). When it is 0, it calls `@0x0800DE20` and the blocking scene `@0x0801F2F4`, a nested frame loop (C, listing).
- So `ext 52 (30)` removes the enemy Cell and at least one frame runs. Only then does `ext 84 (17)` build the NPC Cell, which draws after its first tick. One frame or more with no Cell is LIKELY. It was not measured.

**Smallest fixes (not built; my call).**
1. **One actor group:** `ext 63 ; ext 52 (30) ; ext 84 (17) ; ext 64` (4 more bytes in X).
   - Inside a group, ext 52 queues without blocking. It binds the enemy Cell before the NPC exists (`bl 0x8009370` `@0x08009D24`, then `actor_queue` `@0x08009D44`), so the newest-actor rule cannot bind the NPC (C).
   - The NPC is built in the same script pass, so no frame shows without Cell (L).
   - Cost: two `set:30` slots for a frame or more (64 more OBJ units). In ss2 (seq 24, text box open) the OBJ free list holds one block of 124 units (`obj_pool_v3.py`), so 64 fits (L: X itself was not measured).
2. **A flash:** `ext 42 (5)` before the remove and `ext 43 (5)` after the build, as X already does for the Jr swap. No VRAM cost, but the flash is visible.

Option 1 is invisible if it works. X grows by 4 bytes, so every later allocation moves by 4, and the Vegeta allocations move too.

---

## Change 2: the 2 front Jrs go to the back

**Who stands where in the spawn scene (C, states, bytes).**
- Gohan: (400,440). Table `rom:0x3E9D4C` seq 1 reloads 14,3 at (400,440). ss1 player +0x158/+0x15C = `0x19000`/`0x1B800`.
- Cell (type 22, item 0 `rom:0x408F18`, +0xC = (500,440)): (500,440). ss1: `0x1F400`/`0x1B800`. Seq 22's 3 `ext 96 (30, 8, 100)` do not move him. The start `@0x08011AA0` only turns him (`bl 0x800df98`) and sets state 5. The tick `@0x08011AE2` stores only to the command and the stack (C listing; L that state 5 does not move him).
- The view for the spawns: seq 24 `ext 31 (328, 312, 2)`, so x 328-567 and y 312-471. `ext 31` takes the top-left corner, to within 1 px (C, both states' OAM: ss1 camera (327,304), ss2 (432,335)).

**Which Jrs I mean (C positions, L reading).** A larger y is lower on the screen, toward the viewer. Sprite boxes come from the frame records (`sprite_boxes_v3.py`).

| Jr | Spot | Lowest row on screen | Distance to Gohan (400,440) | Distance to Cell (500,440) | Box overlaps |
|---|---|---|---|---|---|
| vanilla 1-3 | (408,392), (432,376), (456,392) | no | 48 or more | 65 or more | none |
| extra 1 | (384,408) | no | 36 | | none |
| extra 2 | (480,408) | no | | 38 | none (2 px from Cell's box) |
| **extra 3** | **(408,424)** | **yes (y 424)** | **18** | | **Gohan's frame** |
| **extra 4** | **(456,424)** | **yes (y 424)** | 58 | 47 | none, but it stands between the two |

- I used my word "front": the y 424 pair is the front row, the lowest on screen and drawn over all other Jrs. Both stand between Gohan and Cell, who face each other.
- Extra 3 stands on Gohan, 18 px away, and its box overlaps his frame (`test_the_check_rejects_the_v2_front_pair`).
- By distance alone, extra 2 (38 px from Cell) is closer to Cell than extra 4 (47 px). It stands in the back row, so I left it.
- It is not the X group: in the fight the 4 Jrs walk in from the top, so none "spawns" in front.

**What v3 does (C, tests `test_the_front_pair_moved_behind_cell`, `test_every_jr_fits_the_view_and_clears_cell_gohan_and_the_others`).** The seq 31 copy (`rom:0x90A308`, named by spawn table word 30 `rom:0x3E9DC4`):

| Group | Push (v3 ROM) | x, y bytes | v2 | v3 |
|---|---|---|---|---|
| 1 | `rom:0x90A30F` | `rom:0x90A312`-`0x90A315` | (384,408) | (384,408) |
| 2 | `rom:0x90A324` | `rom:0x90A327`-`0x90A32A` | (480,408) | (480,408) |
| 3 | `rom:0x90A339` | `rom:0x90A33C`-`0x90A33F` | (408,424) `1d033e863086500233` | **(536,384)** `1d033e883086000233` |
| 4 | `rom:0x90A34E` | `rom:0x90A351`-`0x90A354` | (456,424) `1d033e871086500233` | **(544,416)** `1d033e884086400233` |

- **Behind Cell:** the boxes start at x 537 and 545. Cell's box ends at x 526, so 10 and 18 px of ground stay clear between them and Cell, on the side away from Gohan. Both stand at a smaller y than Cell's feet (440), so they are not in front.
- **Inside the view:** the boxes end at x 551 and 559 (the view ends at 567), and the y ranges are 369-391 and 401-423.
- **Clear of the others:** no box overlaps another Jr, Cell or Gohan (test). The nearest other Jr is extra 2 at (480,408).
- **Clear of the walls:** every 8x8 cell in the seq 24 view is open (ss1 collision bitmap `@0x0203BFF8`, `collision_v3.py`). The nearest closed cells are a rock at x 576-623, y 424-463, 16 px right of the new boxes.
- The spawn order stays the same: flash, Jr, wait, pause, 4 times.
- The 7 removes after the fade still bind every NPC Jr (test `test_spawned_jrs_equal_removed_jrs`).

---

## SHA-1s

| File | SHA-1 |
|---|---|
| `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr_v3.gba` | `76e610fb3ca4febcf1cefd1199ef39fad10ccbf8` |
| `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr_v3.sav` | `aa8efb2adaa7aa87f4cff27ceb7244368bd02759` |
| `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v2_cj3.gba` | `f94fd65807a7db0957fcbc34b65c0473282f6b09` |
| `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v2_cj3.sav` | `aa8efb2adaa7aa87f4cff27ceb7244368bd02759` |
| CLI `--list` (main) | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` = r39 |
| Sources checked: celljr v2 ROM, Vegeta v2 ROM | `1826ca8f...`, `11e443ad...` (both match their build-log lines) |

Every target was checked before the first write and opened with `"xb"`. No ROM, save or state was overwritten. `docs\build-log.md` has one new line per ROM.

## Diff runs (C, `make_trial_v3.txt`)

**v2 to v3: 7 bytes in 6 runs, 0 outside a v3 site.**

| Run | Bytes | Site |
|---|---|---|
| `rom:0x90A33C` | 1 | seq 31 copy, group 3 x (408 to 536) |
| `rom:0x90A33F` | 1 | seq 31 copy, group 3 y (424 to 384) |
| `rom:0x90A351`-`0x90A352` | 2 | seq 31 copy, group 4 x (456 to 544) |
| `rom:0x90A354` | 1 | seq 31 copy, group 4 y (424 to 416) |
| `rom:0x90A624` | 1 | item 17 x (616 to 512) |
| `rom:0x90A626` | 1 | item 17 y (384 to 472) |

**r39 to v3: 882 bytes in 12 runs, 0 outside the 27 named sites, no site without a change.** The runs are the same as v2's:
- Base data: `rom:0x3E9DC4`-`0x3E9DC6`, `0x3EA478`, `0x3EA47A`, `0x3EB7E9`-`0x3EB7EA`, `0x40DA84`, `0x40DA94`-`0x40DA96`.
- Expansion: `rom:0x90A308`-`0x90A3C5` (seq 31 copy), `0x90A3C8`-`0x90A460` (X), `0x90A464`-`0x90A47C` (C), `0x90A480`-`0x90A4C0` (N), `0x90A4C4`-`0x90A4CD` (seq 58 copy), `0x90A4D0`-`0x90A67B` (table T, items 13-17, the list).
- Every allocation equals v2 (`make_trial_v3.txt`: "allocations equal v2" for all 9).

**Vegeta v2 to Vegeta v2 cj3: the same 7 bytes in the same 6 runs** ("vegeta runs == celljr v2 -> v3 runs: True"). The `vegeta_ssj_scene` sites keep their addresses (`rom:0x90A67C`, `0x90A768` and its 3 base sites).

---

## Tests

| Run | Result |
|---|---|
| `test_celljr_fight` | 38 OK (v2 33, plus 5 new) |
| Full suite (`py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v`) | 771 OK, once, at the end |

- New for change 1: `test_item_17_stands_on_item_11s_spot`, `test_nothing_places_cell_between_his_build_and_x`.
- New for change 2: `test_the_front_pair_moved_behind_cell`, `test_every_jr_fits_the_view_and_clears_cell_gohan_and_the_others`, `test_the_check_rejects_the_v2_front_pair`.
- Updated: `test_item_17_is_an_npc_cell_with_the_face_player_step` (expects (512,472)), `test_fight_positions_are_distinct_and_clear_of_cell_and_gohan` (also not on (512,472)), and `test_a_changed_source_byte_refuses_before_writing` (also flips item 0's and item 11's spots).
- The box sizes in the tests come from `sprite_boxes_v3.py` and are restated as constants. The Gohan box is his 16x32 frame at dy -24 (ss1 OAM), not an opaque box.
- After the full suite, I changed one test constant (`GOHAN_BOX` dy -23 to -24, to match ss1). `test_celljr_fight` ran again: 38 OK. No other file changed after the suite.

## Files

| File | What |
|---|---|
| `scripts\permanent\patches\celljr_fight.py` | The module, v3: `EXTRA_SPAWNS` groups 3 and 4, `CELL_STANDS` (from `ITEM11_AT`), `ITEM0_AT` and `ITEM11_AT` in `_check`, comments |
| `scripts\permanent\tests\test_celljr_fight.py` | 38 tests |
| `scripts\one-time\2026-10-24-celljr-trial\make_trial_v3.py`, `make_trial_v3.txt` | Both ROMs and saves by exclusive create, CLI proofs, positions, diffs |
| `scripts\one-time\2026-10-24-celljr-trial\dump_gohan_v3.py`, `state_actors_v3.py`, `collision_v3.py`, `sprite_boxes_v3.py`, `obj_pool_v3.py`, `study_v3.txt` | Study tools and the listings they printed |
| `scripts\one-time\2026-10-24-celljr-trial\suite_v3.txt` | Full suite output |
| `scripts\one-time\2026-10-24-celljr-trial\bible_rows_v3.md` | CJ3 rows |

The CLI proofs went to `scratch\test-roms\celljr_v3_cli_main.gba`, `celljr_v3_cli_trial.gba`, `celljr_v3_cli_vegeta.gba` (log `celljr-v3-cli-log.md`). The state dumps are in `scratch\review-renders\2026-10-25-celljr-v3\`. Limit breach: one early Bash call began with `cd` into the LOG root (a read-only `cat` of the briefs). It wrote no file, and every later call used absolute paths only. Not touched: `vegeta_ssj_scene.py`, `relay_cooldown.py`, their tests, every build list, `art\base-audit\`, `chapter_cards`, the beam mockups.

---

## What to watch in play

Load `log2_poc_r39_celljr_v3.gba` (or `log2_poc_r39_vegeta_v2_cj3.gba` for all trials), slot 3, as before. The v1 `.ss1` and `.ss2` belong to the v1 ROM: do not load them on v3.

1. **The 4 extra Jrs (change 2).** After "My children! Give them pain!": the 1st Jr pops left of the group, the 2nd just left of Cell, the 3rd and 4th behind Cell on the right. Pass: no Jr pops on Gohan or between him and Cell, and every Jr is fully on screen.
2. **The swap (change 1).** After "Gohan has transformed into Super Saiyan 2!", Cell must not move. Pass: no jump. Watch for a one-frame blink with no Cell (see "The swap itself"). He turns from right to up at once.
3. **Camera.** The camera rises to frame the Jrs coming from the top. Cell stays at his spot, low on the screen, and may be cut to his head and shoulders. Say whether this reads well.
4. **The 2nd fight Jr.** It lands at (528,408), just above Cell's head. Say whether it is too close.
5. **Cell turns.** During the fight Cell turns to face Gohan, as in v2.
6. **After the 4th kill.** Fade, then Cell stands at (616,384) facing left for "You wretched child". The fade hides the move, as I said.
7. **v2 checks that still hold.** The Jrs walk down from the top, the flash at the Jr swap, the Super Perfect Cell talk with Gohan facing right, EXP per kill, a loss gives the normal game over.

## Risks

| Risk | Status | Label |
|---|---|---|
| A frame with no Cell at the swap | Blocking remove before the build (listing). Fix options above, not built | L |
| Cell cut off at the bottom in the Jr fight | X's view bottom is y 447 and Cell's box reaches y 479 | C (arithmetic), L (on screen) |
| The face step turns Cell up at the swap | Enemy facing 3 in ss2; Gohan is mostly above him | L |
| A new Jr spot near the screen edge | The 4th Jr's box ends at x 559, 8 px inside the view's right edge at 567 | C (arithmetic), L (the camera reached (328,312) by seq 31) |
| Seq 19 ops moved Cell after all | ss2 is a real game state after seq 19 with Cell at (512,472) | C |
| Vegeta build drift | Same 7 bytes changed; no allocation moved | C |
