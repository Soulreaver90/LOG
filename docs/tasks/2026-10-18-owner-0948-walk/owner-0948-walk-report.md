# My 0948 walk pass: report

Base: r11 `77084b63`. Result: `archive\builds\log2_poc_r12.gba`, SHA-1 `50a9f95d8a60351bbda822bb0fb5fa1f219d795b`. The suite has 176 tests, and all pass on the final tree. Before this pass the count was 159.

---

## 1. SHIPPED and PENDING

This section lists each ask and its state.

**SHIPPED**

| Ask (my words, short) | State | Evidence |
|---|---|---|
| Task 1: my 4 frames into gi_base 1.0.0-1.0.3, byte for byte | Done | `golden_gi_base_a1_d0_i0..3.png`. In r12, set 157 1.0.0-1.0.3 tile bytes equal the PNGs (CONFIRMED, 4 of 4). |
| Extend the golden set, `frame_lock.py lock --golden --replace` | Done | `GOLDEN_WALK` and `GOLDEN_FILES` (16 names), `scripts\permanent\art\frame_lock.py:44-45`. The old lock moved to `locks\golden_20261018-1016`. `check --golden` exits 0. The 12 idle SHA-256 values equal `golden_sha_before.txt` (12 of 12). |
| Task 2: converter rules from my changes | Done | Section 3 |
| Task 3: sweep with 2 shapes per defect, per form | Done | Section 4 |
| Task 4: regenerate, before and after sheets on lime, at 4x or more | Done | `gi_art.py all`, `gi_post.py all`, `gi_review.py all`. Sheets: `archive\2026-10-18-art-review-renders\walkfix_157.png`, `walkfix_158.png`, `walkfix_159.png`. I viewed all 23 bands (every changed frame, 296 headers) at 4x. I found no frame that got worse. |
| Task 5: suite, new tests, r12, ss1, build log, exports | Done | 176 tests OK. `log2_poc_r12.ss1` is a copy of r11.ss1. One line was added to `docs\build-log.md`. Exports are in `archive\2026-10-18-art-review-renders\full_r12\` and `frames_r12\`, plus the change sheets `r12_changes_157.png`, `r12_changes_158.png`, `r12_changes_159.png`. |
| 9:52 AM: split arm from torso by shape, proven on my 4 frames | Done | `torso_split`, `gi_art.py:418`. Test `test_torso_split_on_the_owner_frames`. |
| 9:55 AM: a1 d1 back keeps golden d1 width and strap; only the arm is skin | Done | `back_columns`, `gi_art.py:1746`. Sweep D5: 4 to 0 in each form. |
| 10:30 AM (69.png, 70.png): back shoe, swoosh boot, legs in any direction | Done (acknowledged) | Boot sweep shape A: 8/8/8 to 0/0/0. `boot_in_arc` `gi_art.py:459`. The 8.0.2 boot by the swoosh is a shoe. |
| 10:52 AM: 5.0.1, 6.0.1, 7.0.1 forearms skin; 8.0.1 sash on the waist span only; 16.0.4 effect white stays white | Done (acknowledged) | Section 5 table: each fails on r11 and passes on r12 in every form, except ssj2_v2 16.0.4 (1 px, shared body). |
| 10:55 AM: `check_parts` in the suite and the manifest | Done (acknowledged) | `part_map` `gi_art.py:1613`, `check_parts` `gi_art.py:1638`, manifest `checks["parts"]` `gi_art.py:1913`, `failing()` `gi_art.py:1937`. All 16 truth frames pass. |
| 11:03 AM item 1: the golden torso never covers an arm or glove | Done (acknowledged) | Limb guard `gi_art.py:1281`. Test `test_golden_torso_never_covers_an_arm`. Read section 6.1: 73.png is 8.0.3, not 4.2.0. |
| 11:03 AM item 2: base 16.0.2 sash | Done | `SASH_NUDGE` `gi_art.py:96`. The base sash is one row up, 7 px, the full waist. |
| 11:03 AM item 3: find the 72.png spot | Done | Gi base 8.0.1, object box x -2..7, y -4..0. The match has 0 mismatches. Fix: `_leg_above` `gi_art.py:534`. |
| Carry-over 3: 159 4.0 by eye | Done | `walkfix_159_b1.png` (4.0.1-4.0.3). The charge pose reads in r12. |
| Carry-over 4: dir 3 is not always a flip | Done | No new rule reads dir 2 for a dir 3 frame (section 6.4). |
| RE-BIBLE rows | Done | `docs\RE-BIBLE.md`: 3 rows in section 4 (Sprites), 2 rows in section 12 (Final decisions). |

**PENDING (for me or a next pass)**

| Ask | State | Why |
|---|---|---|
| Carry-over 1: retire R2 | Not retired | `gi_post.py all` still changes 14 px (R1 and R2 together) on SSJ2 own-body frames. I did not measure R1 and R2 apart. |
| Carry-over 2: SSJ a4 0/2 torso miss by a named rule | Pixels found, rule not shipped | Section 6.2. My named rule `not_torso` changed 16 more frames, and it caused `lost` failures on ssj2 4.0.1/4.0.3. I reverted it. |
| 9:56 AM: a2 d1 sash on the band rows | Not changed (conflict) | Golden d1 puts the sash 1-2 rows under the band. 2.1.2/2.1.3 already match the idle d1 sash. Final decisions needed. |
| 9:56 AM: a2 d2 poses that do not read | Listed | 2.2.0, 2.2.2 and 2.2.3 in all three forms. Sheets: `owner0948_a2d2_157.png`, `owner0948_a2d2_158.png`, `owner0948_a2d2_159.png`. |
| 10:30 vs 11:03 AM on base 8.0.3 | Conflict, arm kept | Section 6.1 |
| Frames that the check or a sweep still flags | Listed | 10 (base), 17 (ssj) and 52 (ssj2, mostly shared bodies) frames. Each set is the union of the check_parts failures, `PARTS_REVIEW`, the r12 sweep hits D1A, D1B, D2A and D3A, and boot B 6.2.1. Sheets: `owner0948_flagged_157.png`, `owner0948_flagged_158.png`, `owner0948_flagged_159.png`. |

---

## 2. What I changed (per pixel group)

The truth harness compares each converter rule with my 4 walk frames and the 12 goldens, per pixel group. All findings are CONFIRMED by script output.

| Pixel group | My change | r11 (below shoulders, S/T/B mismatches) | r12 rules |
|---|---|---|---|
| Crossing arm over the torso | The torso stays gi. The arm is skin with its own 23 outline. A 211 line sits on the gi side under and beside the arm. | i0 13, i1 2, i2 12, i3 2 | 0 on each frame |
| Sash | The sash runs to the torso edge only. | in the 13/12 above | 0 |
| Leg centre | A 211 line between the walking legs | 4 px on i1/i3 | 0 |
| Front-foot shoe | A taller shoe from where the foot widens, a hem over it, and 1 row on a raised back foot | 3 px on each frame | i0/i2 3 each (diagonal hem), i1/i3 0 |

- All 7 of my frames put 211 directly under skin (3-4 px each). Directly under skin they have 0 px of gi fill. So the rim rule under an arm matches I (CONFIRMED by count).
- Where the change does not generalise:
  - Before the overlay, the pixel distance to me frames is i0 22, i1 23, i2 16 and i3 23 (r11: 22, 23, 20 and 23).
  - The golden torso causes most of the distance on i1/i3. My walk shoulders (23, 117, 211) differ from the idle golden strap, and I draw dark 2 px sash ends.
  - The overlay makes 1.0.0-1.0.3 exact. Other walk frames keep the idle strap.
  - Question for me: should the walk strap follow my frames?

---

## 3. Rules (file:line in `scripts\permanent\art\gi_art.py`)

Each rule leaves every golden unchanged. Evidence: `check --golden` exits 0, the idle overlay holds, the truth harness passes 16 of 16, and the shoes golden test passes.

| Rule | Where | What it does |
|---|---|---|
| Torso by shape | `torso_split` :418, called in `armor_to_gi` | The torso columns come from the chest plate whites, joined by trim rows. Belly suit rows widen them, never toward a glove or boot. Suit outside the torso that reaches a glove is arm. |
| Arm line | :827 | A torso pixel beside an arm becomes 211. The arm keeps its 23 outline. |
| Back width (9:55) | `back_columns` :1746 | A back view in a walk frame takes golden d1's columns, moved with the head. |
| Leg line (9:48) | :802 | In front and back views, armor 81 between suit under the sash becomes 211. |
| Feet | `feet` :504, `_stacked` :486, `shoe_top` :546, `raised_feet` :558 | Feet split by fill blobs, and stacked blobs join. A shoe starts where the foot widens. A raised back foot gets 1 row. |
| Hem only under a leg (72.png) | `_leg_above` :534 | A kicking leg's shaft stays gi. Before, it was a 211 hem. |
| Shoes across feet | `shoes` :1080 | Upright parts split into feet. Pixels are painted by row across all feet. |
| Swoosh boot (10:30) | `boot_in_arc` :459 | A boot inside the swoosh arc is a boot, not an effect. |
| Effect white (10:52) | `loose_white` :586 | White that touches only white, grey or empty is effect and stays. |
| Sash span (10:52) | :831 | The sash covers only the torso columns. |
| Forearm check | `purple_forearms` :1561 | A step onto the torso does not count. |
| Limb guard (11:03) | :1281 | The golden torso skips arm and glove pixels under the strap rows, unless the golden pixel there is an arm color. |
| Sash nudge (11:03) | `SASH_NUDGE` :96, applied :685 | Reviewed: base 16.0.2 only, -1 row. |
| my walk frames | `OWNER_FRAMES` :1059 | my frames win over every rule. |
| Part check (10:55) | `part_map` :1613, `check_parts` :1638, `PART_COLORS` :1608 | Arm and glove map to skin, 23 or wristband. Torso and leg map to gi. Boot maps to gi or shoe. Effect and shadow stay the same. Red is allowed on the waist rows within the torso columns. Each upright foot needs a shoe pixel. |
| Parts left for me | `PARTS_REVIEW` :2325 | These frames go to the review sheets. Test `test_parts_review_frames_fail_only_parts` proves that a listed frame fails no other check. |
| Reviewed hints | `PART_HINTS` :2296 | 5.0.1 and 6.0.1 fists. I removed the 8.0.3 "boot" hint (section 6.1). |

**Does not generalise (CONFIRMED):**
- Glove and boot fill sizes overlap, so the fists on boots (5.0.1, 6.0.1, 7.0.1) need reviewed hints.
- Side views get no torso split.
- Base 16.0.2's sash row is a reviewed nudge, not a rule.

**check_parts tolerances, each needed for a golden to pass (CONFIRMED on the 16 truth frames):**
- A border pixel may take a neighbour part's color, but torso and leg never take skin fill.
- Strap rows (chin+1, chin+2) allow gi, 23 and empty. A torso pixel there must not be skin.
- The front V box allows skin.
- Leg pixels allow empty and shadow.
- In a side view, a grey cuff (13/14) allows arm colors.
- A sole moved 1 px allows a shoe/shadow swap.
- Hair and skin left out of the head mask are allowed when unchanged.
- In a side view, the sash may run behind the arm.

**Proof that the check catches the 11:03 defect:** `test_check_parts_catches_an_arm_painted_gi` paints the arm and glove of 5.0.1 gi. Then `check_parts` reports more than 0 misfits.

---

## 4. Sweeps (Task 3)

Each sweep runs on the shipped folders (`gi_base`, `gi_ssj_v2`, `gi_ssj2_v2`). It counts frames on r11 (`before\`) and r12. Scripts: `owner-0948-work\sweep_all.py` and `sweep_boot.py`. Output: `sweep_all_final.txt`.

| Defect | Shape | base r11 to r12 | ssj r11 to r12 | ssj2 r11 to r12 |
|---|---|---|---|---|
| D1 torso turned skin | A: torso_split pixel painted skin | 29 to 5 | 35 to 6 | 33 to 9 |
| | B: plate white or trim painted skin | 0 to 0 | 2 to 0 | 1 to 1 |
| D2 sash off the waist | A: red outside the torso columns | 14 to 0 | 18 to 0 | 20 to 8 |
| | B: red on glove, boot or empty | 0 to 0 | 0 to 0 | 0 to 0 |
| D3 legs not apart | A: armor leg gap not 211 | 21 to 0 | 14 to 0 | 15 to 3 |
| | B: gi-only middle run under the sash | 22 to 19 | 27 to 23 | 26 to 20 |
| Boot without shoe (69.png) | A: white on the shadow, no shoe | 8 to 0 | 8 to 0 | 8 to 0 |
| | B: converter foot, no shoe | 16 to 1 | 16 to 1 | 11 to 1 |
| D5 a1 d1 back width | golden d1 columns | 4 to 0 (1.1.0-1.1.3) | 4 to 0 | 4 to 0 |

**Reconciliation**
- **D1:** shape B is much smaller than A. The r11 defect was mostly torso suit painted skin, not plate or trim. That is a finding, not a gap.
  - Base r12 A leftovers: 2.1.0 and 2.1.2 (reviewed `ARM_SEEDS`), 6.0.1 and 7.0.1 (the reviewed straight arm across the sash), and 16.1.1. The reviewed seeds win over the split on purpose. LIKELY intended.
- **D2:** shape B never fires. The 8.0.1 defect was red on leg suit, which B does not test, so B cannot see it. Shape A gets the 10:52 defect to 0 in base and ssj.
  - The 8 ssj2 r12 leftovers are shared bodies. The set 58 part map does not fit the gi_ssj body there. The gi_ssj frames of the same keys pass. LIKELY a harness limit.
- **D3:** shape B stays high in both versions. It flags poses whose legs touch in the armor, so it is over-inclusive. Shape A is the defect, and it is 0 in base and ssj. The ssj2 leftovers 5.0.2, 6.0.2 and 7.0.2 are shared bodies. LIKELY a harness limit.
- **Boot B:** 6.2.1 is a 4 px shaft piece in a side view. Its foot has a shoe. LIKELY a false alarm.

---

## 5. check_parts fail counts and I-reported frames

**Shipped folders (same check, same part map, r11 and r12, rerun on the final tree):**

| Folder | r11 failing frames | r12 failing frames |
|---|---|---|
| gi_base (157) | 74 | 4 (7.2.3, 8.0.3, 9.0.0, 16.2.2) |
| gi_ssj_v2 (158) | 77 | 10 |
| gi_ssj2_v2 (159) | 86 | 45. Own-body frames only: 17 to 9. The rest are shared bodies, which are checked on their gi_ssj frame. |

**Manifest:** `gi_art.py all` reports 0 failing frames per form. 13 frames pass only because they are in `PARTS_REVIEW` (1-3 px each), so they are listed, not passed:
- base: 7.2.3, 16.2.2
- ssj: 1.0.2, 2.0.2, 2.0.3, 4.1.1, 4.1.3, 7.0.3, 7.2.3, 16.2.1
- ssj2: 2.0.2, 9.0.3, 11.0.1

Shared-body frames skip the own-part checks (`gi_art.py:1909`).

**Me-reported frames (full table: `owner-0948-work\owner_table.txt`):**
- **gi_base:** every reported frame fails on r11 and passes on r12. There are two exceptions:
  - 2.2.2 and 2.2.3 pass on both.
  - 8.0.3 fails on both (torso 2 px: the arm's right outline is skin highlight 117 at the torso column edge).
- **gi_ssj_v2:** all pass on r12, except 1.0.2 (1 px, listed).
- **gi_ssj2_v2:** all pass on r12, except these:
  - 2.1.2 (arm 5 px, the same as r11);
  - 2.2.1, 2.2.2 and 2.2.3 (1-3 px, shared bodies);
  - 16.0.4 (torso 1 px, shared body);
  - 4.2.2 (1 px, the same as r11).
- Frames listed for me: base 8.0.3, ssj 1.0.2, and ssj2 2.1.2, 2.2.x, 4.2.2 and 16.0.4.

---

## 6. Findings, conflicts and questions

### 6.1 The 11:03 AM notes came from intermediate output (CONFIRMED)

- **73.png is gi base 8.0.3, not 4.2.0.**
  - The top version equals r11. In set 157, r10 and r11 bytes for 8.0.3 are equal.
  - The bottom version (purple arm) equals the `art\gi_base` folder after my `cd` slip. That slip ran `gi_art.py all` with intermediate code (the 8.0.3 "boot" hint).
- **r11 4.2.0/4.2.2 keep the skin arm.** Evidence: `owner-0948-work\v\r10_r11_420.png` and `v\sheet_420.png`. The r10 to r11 change there is 1-2 px.
- I kept the limb guard anyway, because the rule stands. Only 1 px per frame changed: (11,-3) 211 to 23 in base 0.2.1, 0.3.1, 4.2.0, 4.2.2, 4.3.0 and 4.3.2.
- **72.png is base 8.0.1.** It matches the intermediate output and the r12 code before the hem fix with 0 mismatches. On r11 the best match has 7 mismatches.
  - The spot is the kicking leg's shaft (x -2..-1, y -1), which was painted as a 211 hem. It is now gi 89/88.
  - The 211 under the forearm at (3..4, -1) stays, because it follows my own pattern (section 2).
- **Conflict on 8.0.3:**
  - At 10:30 I read the chest-height white as a raised knee. At 11:03 I say "the arm is gone".
  - By shape, it is a fist. Suit runs from the shoulder pad to it, and both boots stand on the ground.
  - I removed the hint and kept the arm. Please confirm.
  - The arm and glove pixels of r12 equal r11 (pixel diff, CONFIRMED). These 10 px differ:
    - (6,-1) is now the 211 torso edge.
    - The sash starts 1 px right, on the torso columns: (5,0) 27 to 89, (6,0) 26 to 27.
    - Two shading pixels changed.
    - The second foot got its shoe: (11,3) and (12,3) 211 to 35, with the hem at (10,2) and (11,2).

### 6.2 SSJ anim 4 frames 0/2 torso miss (carry-over 2)

| Dir | Pixels that differ from idle (window coords) | What they are |
|---|---|---|
| d0 | (2,-7) idle suit 79, frame empty; (7,-7) idle 114, frame 23 | shoulder edge; neck or chin pixel |
| d1 | 24 px of plate whites and trim (40-42, 2, 9-13) moved | a different back-plate drawing: real torso |
| d2 | (11,-3) idle empty, frame 81 | the arm's outline in the margin column |

A named rule (`not_torso`: skin or 23, or a suit/empty swap in the margin) fit d0 and d2. It also changed SSJ 1.0.1, 1.0.3 and 21.x.3, and ssj2 4.0.1/4.0.3 (lost-pixel failures). I reverted it. Pending.

### 6.3 Other items

- **16.0.2:** base sash is one row up, 7 px. SSJ and SSJ2 16.0.2 already sat on the full-width row (r11), so they did not change.
- **7.0.1 vs 16.0.2 by eye:**
  - 7.0.1: the arm hangs down the left side across the sash. It is skin with a wristband.
  - 16.0.2: the forearm crosses the chest. It is skin, and the gi shows under it.
  - Both read as arms in r12.
- **a2 d1 sash:** golden d1 puts the sash 1 row (front) or 2 rows (back) under the band bottom. 2.1.2 and 2.1.3 sit like idle d1 (sash = chin + 6). Moving the sash to the band would contradict golden d1. Final decisions.
- **a2 d2:** 2.2.0 (crouch), 2.2.2 and 2.2.3 (arm across the hips) still do not read. Please draw them. 2.2.1 reads.
  - check_parts passes base 2.2.2 and 2.2.3 on r11 and r12. The check cannot see this defect, because side views get no torso split.

### 6.4 Dir 3 mirror check (CONFIRMED by 2 shapes)

- Shape 1: grep of `HFLIP`. Every use reads the record's own flip bit (`gi_art.py:159, 171, 1257, 1522, 1720, 1728, 1855`).
- Shape 2: grep of `dir 3`, `[1] == 3` and `mirror`.
- No new rule takes dir 2 pixels for a dir 3 frame. Golden d3 is read as shown.
- A rule that assumes the mirror without either string would not appear in these searches.

### 6.5 Tests loosened (each named, with its reason)

1. `test_shoe_rows`: on side views a re-run may turn a back-foot toe 35 into 211. On the gi output the toe touches the near shoe, and only the armor split tells them apart (69.png).
2. `test_no_armor_white_below_the_chin`: loose effect white is exempt, by `gi_art.loose_white` (10:52 AM, 16.0.4).
3. `test_golden_torso_per_frame`: a window pixel that is arm-colored where the golden is not (the limb guard) is exempt (11:03 AM).

New tests (17, `scripts\permanent\tests\test_owner_walk.py`):
- 16 golden names;
- My frames are byte-equal;
- torso_split on me frames;
- check_parts passes 16 truth frames;
- check_parts catches an arm painted gi;
- PARTS_REVIEW frames fail only parts;
- one test per rule: back width, leg line, stacked feet, front and back shoes, swoosh boot, loose white, sash span, kick shaft, limb guard, 8.0.3 arm, 16.0.2 sash.

### 6.6 Process slips (I report these myself)

- **`cd` slip 1 (before compaction):** `cd ... && py gi_art.py all` wrote intermediate frames to `art`. I reviewed that output at 11:03 (section 6.1).
- **`cd` slips 2 and 3 (after the resume):** one suite run started with `cd .../owner-0948-work`, and one command started with `cd /c`. Both had no effect on the output, because the scripts use `__file__` paths.
- `scripts\permanent` differs from `before\scripts` only in my files: `gi_art.py`, `frame_lock.py`, `tests\test_gi.py` and the new `tests\test_owner_walk.py`.
- No other task edits were found. `patches\` is outside the before copy.

---

## 7. r12 build facts

- **Command:** `py -3 -I scripts\permanent\log2_build.py --out archive\builds\log2_poc_r12.gba gohan_gi ssj2_form gohan_portraits status_bonus`. It uses no env vars.
- **SHA-1:** `50a9f95d8a60351bbda822bb0fb5fa1f219d795b`. r11 `77084b63` is unchanged.
- **Diff from r11:**
  - 3959 bytes in rom:0x800B4B-0x867F27.
  - Frames changed: set 157 in 167 keys, set 158 in 150 keys, set 159 in 141 keys.
  - No geometry changed.
  - Of the 154 sets compared, only 157, 158 and 159 changed (CONFIRMED).
- **Exports:**
  - `archive\2026-10-18-art-review-renders\full_r12\`;
  - `archive\2026-10-18-art-review-renders\frames_r12\` (armor_56, gi_base_157, armor_59, gi_ssj_158, armor_58, gi_ssj2_159);
  - `r12_changes_157.png`, `r12_changes_158.png` and `r12_changes_159.png` (r11 over r12).
- **Review sheets (lime, in `archive\2026-10-18-art-review-renders\`):**
  - `walkfix_157.png`, `walkfix_158.png` and `walkfix_159.png`;
  - `owner0948_flagged_157.png`, `owner0948_flagged_158.png` and `owner0948_flagged_159.png` (10, 17 and 52 frames);
  - `owner0948_a2d2_157.png`, `owner0948_a2d2_158.png` and `owner0948_a2d2_159.png`.

Labels: CONFIRMED means proven by script output or a byte compare in this session. LIKELY means inferred from a sheet or harness, with a stated limit. I made no SPECULATIVE claims.
