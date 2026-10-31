# Cell Jr v7: report (2026-10-30)

My ask: the v6 play test (9:20 PM). Brief: `celljr-v7.md`.

Labels: **C** = CONFIRMED (bytes, tests or a state), **L** = LIKELY, **S** = SPECULATIVE. No emulator run, so every in-game claim is L or S. Scripts and outputs: `scripts\one-time\2026-10-30-celljr-rework\v7_*`.

---

## SHIPPED

| Ask (my words) | Where |
|---|---|
| "They should be centered" (Gohan and Cell at "You wretched child") | Record N: Cell back on his vanilla spot, both faced as in vanilla. Pair centre (118,80) on a 240 x 160 view (C, box model and test) |
| "The Jrs should surround Gohan ... a transition to the middle and have them come in" | K1 and F: short fade, Gohan to the arena middle (432,392), the view on him, fade in, Jrs walk in from the view edges and stop left of, right of and above him (C bytes, L in game) |
| Tests for the new positions and the camera, old tests updated, none weakened | `test_celljr_fight.py`: 73 tests, OK (66 in v6). The v7 tests fail 11 times on the v6 module (C, `v7_tests_on_v6.txt`) |
| v7 ROM, exclusive create | `builds\mockups\2026-10-24-celljr\log2_poc_r40_celljr_v7.gba`, SHA-1 `5c3145dda0a2e2c2ffb989a23b96abfe77a70d5d` (C) |
| `.sav` byte copy of the v6 save | `log2_poc_r40_celljr_v7.sav`, SHA-1 `aa8efb2adaa7aa87f4cff27ceb7244368bd02759` = v6 (C) |
| Diff v6 to v7: every run inside a celljr_fight site | 1764 bytes in 217 runs, 0 bytes outside a v6 or v7 site. r40 to v7: 0 outside, no idle site (C, `v7_make.txt`) |
| Keep the rest of v6 | Decoded by name in both ROMs: only K1, F, N and the spots of items 14-16 change. X, C, seq 31 copy, seq 58 copy, the 3 relay copies, items 13 and 17, the spawn list, the trial type and the trial AI are the same (C, `v7_make.txt`) |
| Full suite once | 973 tests, OK (C, `v7_suite.txt`) |
| Bible rows, tag CJ7 | `scripts\one-time\2026-10-30-celljr-rework\bible_rows_v7.md` |

## PENDING

| Item | Why |
|---|---|
| My play test | No emulator run (steps below) |
| F blast at 48 px (v6 played at 72 px) | The one known freeze risk, L safe. One-line fix in Deviations if it freezes |
| `docs\build-log.md` line for the v7 ROM | Brief limits edits. The exact line is in `v7_make.txt` |
| Me: merge the CJ7 rows | Rows file, with merge notes |
| Stale comments carried from v6 | `build_list_trial.txt` line 4 ("fights 4 at once"); `vegeta_ssj_scene.py` line 6. Outside the brief's files |

---

## Cause of the off-centre view

The brief's guess was wrong. Record N is not vanilla: it is this module's own record (table T word 29) since v1. F did not move the camera last.

| Layout at "You wretched child" | Camera | Gohan | Cell | Pair centre on screen |
|---|---|---|---|---|
| Vanilla | (432,336), seq 11 | (576,376), faces down | (512,472), faces right | (118,80) |
| v1-v6 N | (432,336) | (576,376), faces right | **(616,384)**, faces left | **(177,26)**: top right, Cell's head cut |
| v7 N | (432,336) | (576,376), faces down | (512,472), faces right | (118,80) |

- N kept the vanilla camera but moved Cell to (616,384). Cell then stood beside Gohan, both in the upper right of the view (C, box model `v7_spots.py`; L that this is the screenshot).
- (616,384) is the CJR study's misread of seq 19's `ext 99`/`ext 100`. v3 fixed the NPC Cell (item 17) but not N.
- Vanilla proof (C, `v7_camera_study.py` and test): seq 11 sets `ext 31 (432, 336, 2)`. Words 12-29 hold no camera op and place neither Gohan nor Cell. Cell stands at item 11's spot (512,472) facing right in the v1 ss2 state.
- My `log2_poc_r40_celljr_v6.ss1` is at the spawn scene, not at "You wretched child". So the cause is a model, not a state read.

## New positions

**Arena middle (432,392).** It is the clear spot nearest the map centre (432,408). Map 14,3 is 864 x 816 px. The view is (320,312): Gohan's follow target, so K1's closing `ext 33 (0)` should not ease the camera (L: the 16 x 8 footprint comes from the Goku hand-off row, not from Gohan's Super Saiyan 2 form). Every path lies on 2 bands with 0 closed pixels in the ss2 collision bitmap, clear of Cell at (512,472) (C, `v7_spots.txt`).

| Record | Jr | Starts (out of view) | Stops | Then |
|---|---|---|---|---|
| K1 | item 14 | (296,392), left edge | (392,392), left of Gohan | enemy |
| K1 | item 15 | (568,392), right edge | (472,392), right of Gohan | enemy |
| K1 | item 16 | (432,288), top edge | (432,344), above Gohan | enemy |
| F | C | (456,288), top edge | (456,336), above right | Gohan flies to (432,336), punch, knock to (488,336) |
| F | B | (296,392), left edge | (384,392), left | blast, knock to (352,392) |
| F | A | (568,392), right edge | (456,392), right | punch, knock to (520,392) |

K1 and F share the set-up `ext 40 (30)`, `ext 62 (0, 432, 392)`, `ext 55`, `ext 31 (320, 312, 255)`, `ext 41 (30)`. This is v6 F's shape. I reached "You wretched child", so F ran to its end in v6 (L). X (the 1 v 1 walk-in) is unchanged: it is not a group walk-in.

## Deviations

| Brief or v6 | v7 | Why |
|---|---|---|
| "record N is vanilla" | N is ours; its Cell spot was the bug | See the cause |
| N: Gohan faces right, Cell faces left | Gohan down, Cell right | Vanilla (seq 24 `ext 55 (0, 0)`; ss2 state). Facing right would look away from Cell below him |
| "camera centres on him" | View = his follow target (x - 112, y - 80) | No ease when K1 hands back to the follow (L). His sprite centre sits 8 px above the view centre (C, box model and test) |
| v6 F blast: B 72 px left of Gohan | B 48 px left | A surround, not a far spot. The scene blast aims at B's hurtbox centre at 3 px a frame (n 100) with a 16 x 16 box, and the hit test runs every frame while `ext 60 (31)` polls (VS4 rows), so a nearer target cannot be skipped (L). A freeze right after the blast would mean it missed; the fix is B at (360,392), knock to (328,392), both inside the bands and the view |
| v6 F: C at (+64, -56) from Gohan; he flies up and right | C at (+24, -56); he flies straight up 56 px to (432,336) | C stands above him. The punch range stays 24 px, as in v6 |
| v6 F: `ext 31 (456, 288, 2)` under the fade | `ext 31 (320, 312, 255)` | A 1-2 frame cut under black, as piccolo_gi_scene r30 |
| K1 facing | Gohan faces down until the fight | S, check by eye |

## Tests: changed v6 assertions (old to new)

| Test | v6 | v7 |
|---|---|---|
| `test_fight_positions_are_distinct_and_clear_of_cell_and_gohan` | 4 distinct; not on (616,384), (512,472), (576,376) | Same, plus not on (432,392); no Jr box on Cell's box; no group box on Gohan's box at the middle |
| `test_n_fades_and_brings_cell_back` | `ext 62 (30, 616, 384)` | `ext 62 (30, 512, 472)` |
| `test_each_jr_walks_down_from_above_the_view_to_its_item_spot` | X and K1: straight down, from above X's view | Split. X: the same checks (`test_the_1v1_jr_walks_down_...`). K1 (`test_the_group_walks_in_from_the_view_edges_...`): its own view = (320,312); start box fully out of view; end box fully in view; one axis; swept box on the open bands; one Jr each left, right, above, within 64 px |
| `test_gohan_is_placed_behind_a_fade_before_the_jrs` | Gohan at (576,376) | Gohan at (432,392) |
| `test_jrs_walk_down_c_b_a_...` to `test_jrs_walk_in_c_b_a_...` | Order; spawn y above X's view | Same order; F's single view asserted; start box fully out of it; one axis; swept box on the open bands |
| `test_finish_spots_fit_the_view_and_clear_cell_and_gohan` | X's view; Gohan at (576,376) | F's own view (asserted); Gohan at (432,392); spots, knock sweeps and Gohan's flight on the open bands; flight clear of Cell |
| ARITY | no ext 30 | `30: 1` (seq 11 `push 0 ; ext 30`) |

New: `test_k1_puts_gohan_in_the_middle_...`, `test_the_middle_view_is_the_follow_target_inside_the_map`, `test_n_puts_the_pair_in_the_vanilla_wretched_child_layout`, `test_the_wretched_child_pair_is_centred_in_the_view`, `test_the_centring_check_rejects_the_v6_cell_spot`, `test_the_jrs_surround_gohan_above_left_and_right`.

## Play steps (my checks)

1. Load `log2_poc_r40_celljr_v7.gba` (mGBA pairs the `.sav` by name), slot 3. Old `.ss*` states belong to their own ROMs (v7 moved the relay copies and items), so make a new state at the 7 Jrs. Play to the 1 v 1 Jr.
2. After its explosion: a short fade. Gohan stands in the middle. 3 Jrs walk in from the left, right and top edges and stop around him. Then the flash and the 1 v 3.
3. Finish: a short fade, Gohan in the middle facing right. Jrs come from the top, left and right. Punch right, blast left, fly up to the third. A freeze right after the blast means the 48 px shot missed (fix in Deviations).
4. "You wretched child": Gohan upper right, Cell lower left, the pair centred, as in vanilla.
5. Report a Jr that sticks on a walk, a bad spot, or Cell cut at the bottom of the middle view (his box reaches y 479; the view ends at y 471).

## Housekeeping

- Edits only in `celljr_fight.py` and `tests\test_celljr_fight.py`. v6 copies in `scripts\one-time\2026-10-30-celljr-rework\v6_backup\` (revert path).
- No `cd`. Read-only state dump of the v6 `.ss1` in `scratch\review-renders\2026-10-30-celljr-v7\v6ss1\`.
- Nothing written under `data\`, `docs\RE-BIBLE.md`, `docs\ledger\`, `build_list.txt`, `zhack\` or the `bf_ki_pool` files. No ROM, save or state overwritten.
