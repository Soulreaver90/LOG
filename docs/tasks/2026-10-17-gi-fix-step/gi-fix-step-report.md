# gi-fix-step report: chin and sash in the transform step, base sash vs SSJ

Status: DONE, with concerns.

## SHIPPED

| Ask (my words) | Result |
|---|---|
| "the chest/chin section is messed up completely in frame 3/4" (157 9.0.2, 9.0.3) | Fixed by rule. Row 18 is skin again (`116 116 116` under the chin), the same as 9.0.1. |
| "same belt issue, it's likely one pixel down" (step frames) | Fixed by rule. The sash is now on one screen row in all 4 frames of anim 9 in every folder (table below). |
| 10:56 PM "base gohan red belt is actually still too low, it should be one pixel higher, to match ssj" | Fixed by rule. No gi_base frame has its sash below the gi_ssj sash of the same pose (0 of 99 same-body keys, was 29). The idle sash is on image row 22 in all 4 dirs, the same row as the goldens. |
| Tests | 4 new tests in `TransformStepTests`. All 4 fail on the old frames and pass on the new frames. |
| SSJ2 chain re-run | All 6 scripts ran without errors. The golden idle slots are byte-identical to `golden_gi_ssj2_d0/d1/d2`. |

## PENDING and concerns

| Item | Why it is open |
|---|---|
| ROM-building tests not run | The limits say never touch `builds`. `test_build`, `test_portraits`, `test_ssj2` and `test_gi.GiPatchTests` build ROMs under `scratch\test-roms`. I ran the other 29 of 97. I must run `py -3 -I -m unittest discover -s scripts\permanent -p "test_*.py"` (expected: 97 tests). |
| `test_front_v_matches_golden` now fails (1 of 29) | It did not fail because of my change. `golden_gi_base_d0.png` changed at 11:20:05 PM (not by me; see `golden\owner\base_gi\owner_base_d0_2317.txt`). The golden V rows now have 89 at the V ends and the converter draws 88. This test passed against the earlier golden with my output. |
| `art\vanilla-sets\set56\frame_292A58.png` (set 56 5.0.1) was overwritten at 11:18 PM, not by me | It is now 32x16, and the manifest record is 16x32. Its bytes do not match the ROM frame. A converter run on it enlarges gi_base 5.0.1 to 32x32. I did not touch the sprite. I restored `art\gi_base` from my 11:01 PM run, which used the intact sprite (it equals the current code's output on every other frame). Re-export set 56 before the next `gi_art.py` run, or 5.0.1 comes out wrong. |
| Base 7.0.1 arm top (my check) | The sash moved up one row, so the "fist hung below the sash" sleeve rule no longer fires in base 7.0.1. Cause: `gi_art.py` line 517 fires only when `min(y for _, y in comp) == waist_y + 1`, and its `cols` set is also keyed on `waist_y + 1`. The fist top is now at `waist_y + 2`. Not fixed in this run, because a regeneration now would read the overwritten set 56 sprite. Rows -5 and -4 of the hanging arm are now gi and outline (`88 89 89 89` / `211 211 211 89`), where before they were skin. gi_ssj 7.0.1 has the same sash row and shows `88 211 211 89` / `211 115 116 211` there. This change makes base 7.0.1 look more like SSJ, but its arm is 1 px shorter than SSJ's. |
| Base sash ends at the arms | Some base frames now show the sash over the arm row, for example 6.0.1 and 8.0.1, the same way gi_ssj does. Idle 0.0.0: the base sash is 5 px wide (`117 27 26 26 26 27 117`) and the golden sash is 7 px wide. Arm detection still differs between base and SSJ, because the base chin can include the collar outline row (see Residual 1). |
| `transform_review.py`, `transform_gif.py` not re-run | The brief did not name them. `anim\ssj_to_ssj2_step.png` and `.gif` are from 10:24 PM and 10:27 PM. The gi_ssj_v2 step frames did not change (see below), so they are still current. |
| RE-BIBLE | Not updated. These are converter rules, not ROM facts. The `gi_art` row at line 332 still describes the tool correctly. |

## Root cause (`scripts\permanent\art\gi_art.py`, line numbers before the fix)

The head zone is counted from the hair top, so taller hair cuts the neck out of the head:

- Line 183: `zone = top + HEAD_ROWS + 2`
- Line 201: `mask |= {p for p, v in px.items() if v in SKIN | {23} and p[1] < zone} | ...`

Measured on set 56 anim 9 dir 0:

| Frame | Hair top | Zone | Chin (`chin_of`) | Chest max | Waist |
|---|---|---|---|---|---|
| 9.0.0 (black hair) | -21 | -3 | -5 (collar outline row is in) | -2 | 0 |
| 9.0.1 (flash hair) | -23 | -5 | -6 | -3 | -1 |
| 9.0.2, 9.0.3 (gold hair, 1 px taller) | -24 | -6 | -7 (neck row y -6 cut out) | -3 | -2 |

- Defect 1: neck row y -6 (frame row 18) falls outside the head mask. `finish` then calls `chest_skin` (line 740 old, now 780). That function treats the cut neck as bare chest and paints it 88.
- Defect 2: the sash row follows the chin through lines 436-438 (old): `waist_y = max(y for _, y in chest) + 1 ...` and `waist_y = max(waist_y, chin_y + 5)`. Every hair height therefore moves the belt. The same rule lifts set 59 9.0.3 (hair top -22, zone -4, collar row in, chin -5) to waist 0, one row under its frames 0-2. The same rule puts the base sash one row under the SSJ sash wherever short black hair keeps the collar outline row in the zone.

## The rule change

1. **Neck rule** (`_neck`, line 231, called at line 207; `NECK_SEED = 2` at line 78). Skin joined to the face below the zone is neck, whatever the hair height. The flood starts 2 rows above the zone edge. A skin piece that the zone cuts is therefore not taken (base 8.0.3: a skin column at x 11 under the collar outline).
2. **Sash anchor** (lines 474-475). `body_rows` (line 381) gives (neck bottom, boot top, feet) rows. An upright frame whose rows equal frame 0 of its (anim, dir) takes frame 0's sash row. `make_gi_set` records the anchor for every index-0 key of a header group.
3. **Base sash cap** (lines 476-477, `SASH_MATCH` line 62, `sash_rows` line 1103). A gi_base sash never sits below the gi_ssj sash of the same key when the leg rows match. The key is the same drawing in both sets, so the legs are enough.
4. `_armor_pass` (line 1086) holds the old armor step of `make_gi_set` (the lit-frame branch included), so `sash_rows` and `make_gi_set` share it.
5. No FIXES entry. Header text updated (Method, API).

The 13.0.2 and 1.1.2 anchors and the cap also move the sash in other anims (lists below).

## Step sash rows (screen row = frame row + dy), before and after

| Folder | Before 9.0.0 / .1 / .2 / .3 | After |
|---|---|---|
| gi_base (157) | 0 / -1 / -2 / -2 | -1 / -1 / -1 / -1 |
| gi_ssj | -1 / -1 / -1 / 0 | -1 / -1 / -1 / -1 |
| gi_ssj2 | -1 / -1 / -1 / 0 | -1 / -1 / -1 / -1 |
| gi_ssj_v2 (158, transform158 output, dy -25 on 1-3) | -1 / -1 / -1 / -1 | -1 / -1 / -1 / -1 |
| gi_ssj2_v2 | -1 / -1 / -1 / 0 | -1 / -1 / -1 / -1 |

- The brief's figures for set 158 (9.0.0 on row 22, 9.0.1-9.0.3 on row 23) do not match the files. In gi_ssj, only 9.0.3 was low (frame row 24). gi_ssj_v2 was already level, because `transform158.py` copies rows 23-25 of index 2 into index 3.
- `transform158.py` is not changed. Its copy is now redundant for the sash (rows 23 and 24 already match). It still overwrites 3 pixels on source row 22 of 9.0.3 (`117 211 88` becomes `89 89 89`), so gi_ssj_v2 9.0.3 did not change.
- Base 9.0.1 (the "good" frame) keeps its sash on row 23. The 10:56 PM rule raised 9.0.0 to row 23, and the anchor then holds all 4 frames there.
- Still different (not covered by the rule): in frames 1-3 the armor plate ends one row higher, so the gi above the sash has a different shading split.

## Sweeps (two search shapes each; script `gi-fix-step-work\sweep.py`)

- Chin A (rule side): the source has face-joined skin below the `head_mask` chin.
- Chin B (output side): gi purple on source skin in the 2 lowest rows of the face blob, within 3 columns of its middle. It does not use `head_mask`.
- Belt A (rule side): the converter's sash row differs from index 0 while `body_rows` match.
- Belt B (output side): the output 26/27 row differs from index 0 while the source feet row and the top row of the lowest white part match. The neck row is reported as well.

| Form | Chin A before / after | Chin B before / after | Belt A before / after | Belt B (neck row equal) before / after |
|---|---|---|---|---|
| gi_base | 2 / 0 | 2 / 0 | 3 / 0 | 3 / 0 (10 / 4 with any neck row) |
| gi_ssj | 5 / 0 | 4 / 0 | 4 / 0 | 2 / 0 (7 / 5) |
| gi_ssj2 | 4 / 0 | 13 / 8 | 3 / 0 | 1 / 0 (13 / 12) |

How the shapes reconcile:

- Chin, before.
  - Both shapes: base 9.0.2, 9.0.3; SSJ 1.0.2, 2.0.2, 2.2.0, 12.0.2; SSJ2 2.0.2, 2.2.0, 12.0.2.
  - A only: SSJ 18.0.1 and SSJ2 18.0.2. The neck is shaded 113 and the opening covered it, so the output showed no purple.
  - B only: SSJ2 16.0.1 (a 1 px chin point). Shape A seeds from chin-2, `_neck` seeds from zone-2. Also SSJ2 12.2.0-3 and 20.0.0-3, see below.
  - A site that is not a 4-joined skin run (a neck drawn only in outline 23) would not appear in either shape.
- Chin B after: the 8 left are SSJ2 12.2.0-3 and 20.0.0-3. These are stand-in heads ("set 58 has no ...", set 59 body with a set 58 head). The source skin positions belong to the replaced head, so they are false alarms. Not changed.
- Belt, before.
  - Both shapes: base 9.0.1-9.0.3, SSJ 1.1.2 and 13.0.2, SSJ2 0.0.1.
  - A only: SSJ and SSJ2 9.0.3. Shape B reads the aura ring under the boots as the feet row (5 in frame 0, 6 in frames 1-3).
  - A only: SSJ and SSJ2 12.0.2. This is a crouch, and its neck row differs from frame 0, so there is no anchor. It changed only through the neck rule.
- Belt B after: every remaining case has a different neck row from frame 0. The torso moves (5.0.2, 8.2.2, 8.2.3, 16.2.5, 21.0.3, SSJ2 4.x), so the rule correctly leaves them.

## Frames changed per form (headers; twins in brackets)

**Neck rule**
- gi_base: 9.0.2, 9.0.3 (+ dirs 1-3)
- gi_ssj: 1.0.2, 2.0.2, 2.2.0 (+2.3.0), 12.0.2, 18.0.1, 18.0.2 (+18.0.3-6)
- gi_ssj2: 2.0.2, 2.2.0 (+2.3.0), 12.0.2, 16.0.1 (the stray wristbands by the shoulders become skin), 18.0.2 (+18.0.3-6)

**Sash anchor**
- gi_ssj: 1.1.2, 9.0.3 (+ dirs 1-3), 13.0.2
- gi_ssj2: 0.0.1 (idle frame 1, now level with 0.0.0), 9.0.3 (+ dirs 1-3)

**Base cap (10:56 PM rule, counted separately): 42 gi_base headers**
- 0.0.0, 0.0.1, 0.2.0 (+0.3.0), 0.2.1 (+0.3.1)
- 1.0.0-1.0.3, 1.2.0, 1.2.1, 1.2.3 (+1.3.x)
- 2.0.0, 2.2.2, 2.2.3
- 4.0.0, 4.0.2, 4.2.0, 4.2.2
- 5.2.0, 5.2.2
- 6.0.1, 6.2.1, 6.2.2, 6.2.3
- 7.0.1, 7.2.0
- 8.0.1, 8.0.3, 8.2.1, 8.2.2, 8.2.3
- 9.0.0 (+ dirs 1-3)
- 11.0.0
- 13.2.0, 13.2.1, 13.2.3
- 16.0.0, 16.0.4, 16.0.5, 16.2.0, 16.2.5
- 18.2.0

In each one the sash moves up 1 row and the trouser top fills the row under it. Leg and boot rows are unchanged.

**Totals:** gi_base 44 headers, gi_ssj 9, gi_ssj2 7. No changes outside these lists (`diffsets.py`).

**Chain outputs**
- gi_ssj2_v2: 7 frames changed (0.0.1, 2.0.2, 2.2.0, 9.0.3, 12.0.2, 16.0.1, 18.0.2).
- gi_ssj_v2: 8 frames changed (1.0.2, 1.1.2, 2.0.2, 2.2.0, 12.0.2, 13.0.2, 18.0.1, 18.0.2).
- transplant status counts: identical before and after.
- `bodyfix` golden check: 0 changes.
- Golden idle slots 2A15DC, 2A1878, 2A19AC: `cmp`-identical to `golden_gi_ssj2_d0`, `d1` and `d2`.
- SHA-256 of `golden\*.png`: unchanged by my runs. The only change is `golden_gi_base_d0`, edited by someone else at 11:20 PM.

**Idle sash vs goldens:** image row 22 in gi_base, gi_ssj and gi_ssj2, dirs 0-3, the same as every golden.

**Byte-for-byte golden check, form by form**
- gi_ssj2_v2: `finish_v2.py` copies the goldens into the idle slots. After the run they are byte-identical, as listed above.
- gi_base and gi_ssj: no code copies a golden into these slots. A read-only grep of `scripts\permanent` (including `patches\gohan_gi.py`, which reads `gi_base` and `gi_ssj` directly) and `work_r3` found none.
  - Their idle frames are converter output and were never byte-identical to the goldens. Pixel diffs against the current goldens:

    | Form | d0 | d1 | d2 and d3 |
    |---|---|---|---|
    | gi_base before | 48 px | 16 px | 9 px |
    | gi_base after | 40 px (rows 17-27; this golden was redrawn at 11:20 PM) | 16 px (rows 19-21) | 3 px (rows 19, 20, 22) |
    | gi_ssj before and after | 3 px (row 21) | 11 px | 2 px |

  - The sash row matches the golden in every dir.

**Coverage of the 6x review:** I viewed every changed frame at 6x, in `ba_base_1.png` to `ba_base_5.png`, `ba_ssj.png`, `ba_ssj2.png`, `ba_ssj2_v2.png` and `ba_step_6x.png`.
- gi_ssj_v2 frames are gi_ssj copies except the 3 step frames, so `ba_ssj.png` covers them.
- In gi_ssj2_v2, a pixel diff shows that only image rows 18-23 changed (neck and sash), for 2.0.2, 2.2.0, 16.0.1 and 18.0.2.

## Tests

- New in `scripts\permanent\tests\test_gi.py` (`TransformStepTests`, line 268):
  - `test_step_chin_stays_skin`
  - `test_step_sash_keeps_frame_0_row` (all three forms)
  - `test_base_sash_not_below_ssj` (all 99 same-body keys)
  - `test_idle_sash_row_matches_golden`
- Red check: all 4 fail on the old frames.
- Run: `py -3 -I archive\2026-10-17-gi-art-rounds\gi-fix-step-work\run_tests.py`. It discovers 97 (93 + 4), runs 29, and leaves out 68 ROM builders.
- Result: 28 passed. The one failure is `test_front_v_matches_golden`, caused by the 11:20 PM golden edit (see PENDING).
- `gi_art.py all`: 0 failing checks in all three forms.

## Review sheets (6x, armored source | before | after, placed by dx/dy)

- Step: `archive\2026-10-17-gi-art-rounds\gi-fix-step-work\ba_step_6x.png`
- All changed base frames: `...\gi-fix-step-work\ba_base_1.png` to `ba_base_5.png`
- SSJ: `...\gi-fix-step-work\ba_ssj.png`
- SSJ2 and v2: `...\gi-fix-step-work\ba_ssj2.png` and `ba_ssj2_v2.png`
- Regenerated by the chain: `art\anim\base_to_ssj_step.png` and its GIFs, `art\gi_ssj2_v2\review\`

## Residuals (not fixed, for a later task)

1. The head zone still decides whether the collar outline row (23) belongs to the chin. Base and SSJ share 99 armored bodies, and 59 of them still differ somewhere in the gi body (71 before), mostly in arms and openings. Counting the collar row in every frame would make the chin independent of the hair. A trial of that change altered 55 gi_ssj and 65 gi_ssj2 headers, including the approved idle frames, so I did not apply it.
2. 18 base keys have the sash above SSJ, mostly back views. The 10:56 PM rule only raises base sashes that are too low.

## Files

- Changed:
  - `scripts\permanent\art\gi_art.py`
  - `scripts\permanent\tests\test_gi.py`
  - Both are LF with no byte order mark and no en or em dashes.
- Backups and tools: `archive\2026-10-17-gi-art-rounds\gi-fix-step-work\`
  - `before\` holds the old frames, the v2 folders, the step sheets, `gi_art.py.orig` and `test_gi.py.orig`.
  - Tools: `sweep.py`, `diffsets.py`, `pixdiff.py`, `sheet.py`, `basevsssj.py`, `run_tests.py`.
