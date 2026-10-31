# gi-rules-night report: shoes, shading, torso and step light from the goldens

Status: DONE, with concerns.

## SHIPPED

| Ask (brief) | Result |
|---|---|
| 1. Shoes, shading C, step lighting as rules | Done in `gi_art.py` (lines below). All 12 goldens are fixed points of the shoe, gap fold and shading rules below the sash (tested). |
| 2. Torso and straps as a rule where it generalises | Done. Each torso rule holds for a whole (anim, dir) or not at all, so nothing flickers within an animation. The skipped frames are listed below. |
| 3. Idle slots of gi_base and gi_ssj equal the goldens byte for byte | Done by an overlay, the same way `finish_v2.py` does it. The rules alone come within 0-7 px (table in concern 2). |
| 4. Tests | 7 new tests in `GoldenRuleTests`. `test_front_v_matches_golden` updated. 104 tests discovered (97 + 7). The 36 tests that do not build a ROM pass. |
| 5. `gi_art.py all` and the SSJ2 chain | All 7 scripts ran without errors, in the brief's order. The gi_ssj2_v2 idle slots are byte-identical to `golden_gi_ssj2_d0/d1/d2`. `bodyfix.py` applied nothing (concern 1). |
| 6. Strips at 6x on lime | 52 strips, one per anim per form: armor, gi before tonight, gi now. |
| 7. RE-BIBLE | `docs\RE-BIBLE.md` lines 333-335: the rule row, the golden list row and the test row. |

## PENDING and concerns (final, please look)

1. **CONFIRMED: `bodyfix.py --apply` now applies nothing.** Its golden gate prints `{0: 1, 1: 0, 2: 0, 3: 0}`. Its rule R2 (gi beside arm outline 23 becomes 211) would change `golden_gi_ssj2_d0` pixel (12, 19) from 89 to 211. That pixel is my new rounder chest (backup_0015 diff: `11:116>23 12:211>89`). The gate is correct, so I did not force it or edit it.
   - Effect: on the gi_ssj2_v2 frames, R1 and R2 would still change 130 px in 70 frames. Before tonight bodyfix applied them.
   - My gap fold rule covers R1 where the gap is under the sash. R2 (211 between the trouser and the arm outline) has no replacement.
   - Possible fix (final decisions): exempt the armpit row on the image-left side from R2. The gate then passes again.
2. **The torso rule does not reach the goldens on its own.** The golden overlay makes the idle slots exact. Without the overlay, the idle diffs (rows 17 and down) are:

   | Form | d0 | d1 | d2 |
   |---|---|---|---|
   | gi_base, rules only (golden torso off) | 7 px | 24 px | 18 px |
   | gi_base, with the golden torso rule | 1 px (row 21 x 14, band 72) | 0 | 7 px |
   | gi_ssj, rules only | 8 px | 34 px | 19 px |
   | gi_ssj, with the golden torso rule | 1 px | 0 | 7 px |
   | gi_ssj2, with the golden torso rule (body rows) | 4 px | 8 px | 3 px |

   - The rest is wristbands (converter 117 or 72, golden 195), the 7 px base sash and the base and SSJ side shoes.
   - The base and SSJ side goldens are my hand shoe (toe forward on the hem row, the bottom row 1 px forward). The SSJ2 side golden uses the plain rule. These two cannot both be one rule, so every non-idle side frame gets the plain rule shoe. LIKELY visible in the side walk cycle.
3. **The torso rules reach only a few animations.** I made both torso rules all-or-none per (anim, dir): a golden torso or a strap on some frames only would blink as the animation plays.
   - Golden torso: anim 0 only (frames 0 and 1, all dirs, all forms). No other whole animation keeps the idle armor torso.
   - Straps: gi_base anim 4 dir 0 and anim 9; gi_ssj and gi_ssj2 anim 9 only.
   - V lines: every front frame that has the V (42, 40 and 46 headers).
   - Many front and back frames had a strap match on some frames but not all (walk 1.x, anim 11, 21). They now get no strap. If I prefer straps there, the strap rule needs a pose-proof shoulder finder, or art.
4. **Judgment call: shoes on lying and flying frames.** The prototype `shoes2` reads "bottom 2 rows", which fails when the feet do not point down. On these frames I applied the rule along the legs: the sole points from the sash middle to the boot (sideways only when `|dx| > 1.5 |dy|`). Each line along that axis keeps its own 2 shoe pixels, since one boot part can hold both feet (20.1.0).
   - Frames: 3.0.1-3.0.3, 12.2.0-12.2.3 (and their mirrored dir 3), 20.0.0-20.1.3, in each form.
   - At 6-7x they read as small shoes. SPECULATIVE whether I want this.
5. **Judgment calls on the rules.**
   - Shading parity uses the object (screen) row, so the folds hold still when an animation changes dy. "Left" is the image left, so d3 (the mirror of d2) shows the light mirrored, the same as golden d3.
   - The gap fold fires for a gap of any width. The base goldens have a 1 px gap. The SSJ2 goldens open a 3 px gap, where bodyfix R1 drew the same 211 pixels. On 9.0.1-9.0.3 the fold gives a 3 px dark crotch (`211 211 211`) under the existing crotch outline. LIKELY acceptable, please look.
   - Step light "next to" means left or right in the row (the rule C runs are horizontal), not up or down.
   - The arm-outline part of the strap rule changes only the image-left side in front views. All three golden fronts changed only that side. Back views change both sides.
   - The strap needs both shoulders: an arm across the chest (7.0.2) took a one-sided strap and broke the V.
   - Upright shoes stay row-wise, as in the prototype. A per-column variant also kept the goldens unchanged, but it left the hem out of 1-5 columns in nearly every converted frame.
6. **One flat foot loses its brown.** 8.0.2 (all forms): the far foot is one boot row over the dust effect, so that row becomes the hem.
7. **Pre-existing ugliness made a little darker.** In gi_ssj2 1.0.0 and 1.0.2 (front walk, leg toward the camera) the converter draws the lower leg mostly 211. The hem adds one dark row above a 2-row shoe.
8. **The overlay also covers 0.1.1.** The back idle header (`frame_2902A8` in gi_base, `frame_2AB8B0` in gi_ssj) carries keys 0.1.0 and 0.1.1. It is the same drawing, so the golden is correct for both. The front header carries only 0.0.0. The side header carries 0.2.0 and its flip 0.3.0, and golden d3 equals the flipped d2 (checked pixel by pixel).
9. **Side effect, CONFIRMED.** At 12:21 AM my first probe imported `work_r3\shade\rules.py`. That module imports `shade_c_mock.py`, which runs its mock at import time. It rewrote `work_r3\shade\shadeC_*.png` and `shade_c_mock.png` from the current goldens. No golden changed: the golden SHA-256 values match the values from before my runs.
10. **ROM-building tests were not run.** The limits say never touch `builds`. I must run `py -3 -I -m unittest discover -s scripts\permanent -p "test_*.py"` (expected: 104 tests).
    - I verified slot geometry only: no record changed size, and `make_gi_set` raises on a slot overflow.
    - The ROM space, decode and set table checks in `GiPatchTests`, `test_ssj2` and `test_portraits` are not verified.
    - The new index 87 is in the shared OBJ palette. The patch has no index filter.
11. **gi_ssj2 idle frames are not overlaid.** `transplant.py` finds every SSJ2 head by matching the converter's idle heads, so the golden must not go there. `finish_v2.py` places the SSJ2 goldens in gi_ssj2_v2. The golden torso rule still covers rows 17-23 of the gi_ssj2 idle frames.

## Rule changes (`scripts\permanent\art\gi_art.py`)

| Line | What |
|---|---|
| 14-15, 39-46 | Header: API line for `gi_rules`, Method paragraph for the golden rules |
| 806-820 | Section comment and constants: `GOLDEN`, `SHOE_ROWS`, `SOLE_TILT`, `STEP_FRAMES`, `STEP_LIGHT`, `TORSO_MARGIN`, `LOOSE`, `IDLE_GOLDEN`, `GOLDEN_CHECKS`, `GOLDEN_EXCEPTION` |
| 839 | `shoes`: 2 rows nearest the sole, 211 hem under trouser, toe stays shoe, trouser above |
| 871 | `hip_of`: the sole axis for lying and flying frames |
| 880 | `gap_folds`: gi under the sash above a gap between the legs becomes 211 |
| 895 | `shade`: rule C per horizontal run |
| 913 | `v_lines`: 211 beside and under the front V tip |
| 924 | `straps`: strap top, strap edge, strap 89, arm outline 23 under the strap, both shoulders required |
| 968 | `golden_torso`: golden pixels, idle armor and torso window per form and dir |
| 985 | `torso_shift`: the frame's armor equals the idle armor in the window (suit shades as one, shift up to 2 px) |
| 996 | `torso_groups`: (anim, dir) groups where every frame takes the golden torso |
| 1006 | `strap_groups`: (anim, dir) groups where the strap fits every frame |
| 1018 | `gi_rules`: shoes, gap folds, shading, then the golden torso or the V lines and straps, then the step light. Each rule writes a manifest note `rule <name>: N px`. |
| 1390, 1426-1427 | `make_gi_set` stages every converted frame, picks the torso and strap groups, then runs `gi_rules` |
| 1447-1453 | Golden idle overlay for gi_base and gi_ssj |
| 1469-1471 | `check_exception` for golden frames that fail only `sleeve` or `lost` (my torso is wider than the converter's arms) |

Each rule function has a one-line `# Why:` comment above it.

## Frames changed per form per rule (headers)

| Rule | gi_base | gi_ssj | gi_ssj2 |
|---|---|---|---|
| shoes (upright) | 146 | 143 | 143 |
| shoes along the legs | 15 | 15 | 15 |
| gap folds | 6: 5.1.2, 9.0.1-9.0.3, 18.0.1, 18.0.2 | 3: 5.1.2, 18.0.1, 18.0.2 | 12: 0.0.0, 0.0.1, 0.1.0, 4.0.0, 4.0.3, 4.1.0-4.1.3, 5.1.2, 18.0.1, 18.0.2 |
| shading | 156 | 159 | 159 |
| golden torso | 5: 0.0.0, 0.0.1, 0.1.0, 0.2.0, 0.2.1 | 5, the same | 5, the same |
| golden idle overlay | 3: 0.0.0, 0.1.0, 0.2.0 | 3, the same | none (chain) |
| v lines | 42 | 40 | 46 |
| straps | 8: 4.0.0-4.0.3, 9.0.0-9.0.3 | 4: 9.0.0-9.0.3 | 4: 9.0.0-9.0.3 |
| step light | 3: 9.0.1-9.0.3 | 3 | 3 |

- Full lists: `gi-rules-night-work\tally.txt`. Pixel transitions per form: `transitions.txt`.
- Chain outputs: all 159 frames of gi_ssj2_v2 and gi_ssj_v2 changed. The transplant status counts equal the counts from before tonight. No frame changed status, direction or offset.
- The anim 9 headers serve all 4 dirs, so the step light and the straps show in every dir of the transform.

## Poses the torso rule skips

- Golden torso: every frame outside anim 0.
- Straps: every frame outside the strap groups above.
- Frames with neither (the V lines and the leg rules still apply):

  | Form | Front | Back | Side |
  |---|---|---|---|
  | gi_base | 57 | 48 | 44 |
  | gi_ssj | 58 | 48 | 44 |
  | gi_ssj2 | 58 | 48 | 44 |

- Lists: `gi-rules-night-work\skipped.txt`.
- I drew no new art for attacks, lying or flying torsos.

## Tests (`scripts\permanent\tests\test_gi.py`)

- `EXTRA` adds 87 (the step light).
- `test_front_v_matches_golden` checks idle frames 0 and 1. Frame 1 gets its torso from the golden torso rule, not from the overlay.
- `GoldenRuleTests`:
  - `test_shoe_rows`: a synthetic boot, plus every ruled frame being a fixed point (lying and flying frames along the legs).
  - `test_hem`: a toe that sticks out stays shoe, plus the 12 goldens.
  - `test_shading_runs`: n = 1..6 on even and odd rows, mirrored, plus the golden legs.
  - `test_gap_fold`: 1 px gap, 3 px gap, no fold at an arm or at the sash, plus the goldens.
  - `test_step_light_only_on_anim_9_frames_1_3`
  - `test_v_lines_and_straps`: converter pixels to golden base front rows 17-20.
  - `test_idle_slots_equal_goldens`
- Run without the ROM builds: `py -3 -I archive\2026-10-17-gi-art-rounds\gi-rules-night-work\run_tests.py`. Result: discovered 104, ran 36, OK. 68 left out (test_build, test_portraits, test_ssj2, GiPatchTests).

## Review

- Strip folder: `archive\2026-10-17-gi-art-rounds\gi-rules-night-work\strip_<form>_a<anim>.png` (52 files at 6x on lime).
- What I viewed, and how big it showed:
  - Whole strips, downscaled for display to about 3-4.6x: gi_base anims 0, 1, 7, 9, 12, 16 (about 2.6x), 20; gi_ssj anims 0, 21; gi_ssj2 anims 0, 4, 9.
  - Zooms at 6-10x: base 1.0.0, 1.0.2, 1.1.0, 3.0.1, 3.0.2, 4.0.1, 5.1.0, 7.1.0, 9.0.0-9.0.2, 12.2.0, 14.0.2, 16.0.1, 16.1.5, 18.0.2, 20.0.0, 20.1.0, 20.3.0; SSJ2 1.0.0, 1.0.2, 3.0.2, 11.0.1, 12.2.0, 16.0.4, 20.0.0, 20.1.0.
  - I did not view the other 40 strips. I should page through them.
- Automated sweeps (against the before copies and the armor):
  - 0 new gi pixels on armor skin.
  - 0 sash moves outside golden frames.
  - 0 silhouette changes outside golden frames.
  - 0 new isolated pixels.
  - 0 mixed torso treatments within an (anim, dir) (`groups.py`).
  - 1 foot with no shoe left (8.0.2, concern 6) (`feet.py`).
- Before copies of the code, the docs and the 5 output folders: `gi-rules-night-work\before\`.
- Golden SHA-256 values: unchanged (`golden_sha_before.txt`).
