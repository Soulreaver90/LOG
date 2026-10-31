# gi-fix-1125 report: legs read as arms, front V, side chest, side walk back arm

Status: DONE, with concerns.

## SHIPPED

| My ask | Result |
|---|---|
| "thats his leg, but you turned it into an arm" (5.0.0), and the 11:43 AM marks (5.1.1, 6.1.1, 7.0.1, 7.1.2) | Fixed by rule in all three forms. A white part on the ground shadow is a raised knee or boot. Each leg box is now gi trouser plus a brown boot, with no skin and no band. Each arm box is skin with a band. |
| "fix the chest, why its one sided. Look at the front reference!" | Fixed. The front V is centred, 3 over 1 (116 115 116 over 116). It matches the golden fronts pixel for pixel in all three forms. |
| "missing the chest" (side views) | Added. The quarter-angle neck opening (116 116, with 116 under the front one) matches the golden side. Where an arm or the pose covers the chest, it stays covered. |
| Side walk "look at the back" (11:26 AM), index 0 | Fixed by rule plus a hint. 1.2.0 now shows the back arm as skin, with a blue band and a fist. Before, it was trouser and boot. |
| Side walk, index 2 | Fixed with a FIXES entry. 1.2.2 back arm: the armor draws it 1 px wide, so the gi showed a thin dark line. It is now a 2 px skin arm with an outline, a band beside the fist, and the fist. |

Dir 3 reuses the dir 2 frame headers with an H-flip. Every dir 2 fix therefore covers dir 3 too, for example 1.3.0 and 1.3.2.

## PENDING

| Item | Why it is open |
|---|---|
| Full suite run (`python -m unittest discover -s scripts\permanent -p "test_*.py"`) | `GiPatchTests`, `test_build`, `test_portraits` and `test_ssj2` build ROMs under `scratch\test-roms\`, and the limits say never touch `builds`. I must run them. Expected count: 77 + 5 new = 82. |
| My check of 5.0.2 | The white on the shadow at the lower left is a raised knee and boot. The blue column above it now reads as body and trouser, so 5.0.2 has no visible left arm. Before, it was an arm plus a giant fist. |
| My check of the opening flicker in cycles | See "Animation cycles" below. |

## Rule changes (`scripts\permanent\art\gi_art.py`)

**Ground shadow rule**
- Line 71: `SHADOW = 1`.
- Lines 357-360: the new function `_grounded()`.
- Lines 431-434: after the outline join, a glove that is not hinted becomes a boot when its fill or outline has the ground shadow right under it, more than `CHEST_ROWS` rows below the chin. Lying and flying frames are skipped.
- The rule runs after the "boot top beside a boot" merge loop. The merge loop therefore cannot swallow the hip fists next to the new boots (6.0.0).
- It re-classes these frames in all forms: 5.0.0-5.0.2, 5.1.1, 5.1.2, 6.0.0, 6.0.1, 6.0.3, 6.1.1, 6.1.2, 7.0.0, 7.0.1, 7.0.3, 7.1.1, 7.1.2, 18.0.0.

**Splits and hints**
- Lines 382-387 and 1497-1500: `PART_SPLITS`. In 7.0.1 the fist and its boot are drawn as one white part. The split cuts that part below row 3 before the parts are sorted.
- Line 1496: `PART_HINTS["7.0.1"] = {(4, 2): "hand"}`.
- Line 1494: `PART_HINTS["1.2.0"] = {(13, 0): "hand"}`. The merge loop had joined the back fist to the back boot.
  - Why a hint and not a rule: I tested a guard that only merges a part stacked over the boot's columns.
  - That guard also rejected merges that are correct today: the chest plate bits in 2.0.2, and small boot-top bits in 8.0.3 and 16.0.2. Those frames would have regressed.

**Arm through the sash**
- Lines 476-484: when a fist's top row sits right under the sash, its sleeve runs straight up from it, in the fist's own columns, through the sash and the belly.
- My on 7.0.1: "the arm hangs down the left side across the sash".

**Seeded arms**
- Lines 449-458: `ARM_SEEDS` islands are now found before the glove loop.
- Lines 486-487: a seeded arm next to a glove that has no sleeve becomes that glove's sleeve, so the band faces the arm.
- Line 1510: new seeds `"6.1.1": [(13, -6)]` and `"7.1.1": [(2, -6)]`. They cover my red "small piece at the top right beside the head" in 6.1.1, and its mirror in 7.1.1.

**Hand fix for 1.2.2**
- Lines 1466-1469: `_WALK_BACK_ARM` (FIXES) for "1.2.2" in all three forms.
- I checked that the record is the same in sets 56, 58 and 59 (16x32, dx 0, dy -24, no flip). `FIX_GEOMETRY["1.2.2"]` holds that record.

**Openings**
- Lines 84-86:
  - `V_NECK = ((-1, 1, 116), (0, 1, 115), (1, 1, 116), (0, 2, 116))`.
  - New `SIDE_NECK = ((0, 1, 116), (1, 1, 116), (0, 2, 116))`.
  - `V_LIMIT["side"]` changes from 1 to 3.
- Lines 650-753: `neck_run`, `facing`, `_draw_spots`, `_collar_rows`, `add_v_neck` (rewritten) and `add_side_opening` (new). `finish` now also opens side views.
- Front V:
  - It is centred on the gi gap between the collar outlines, on the first gi row under the chin. An even gap leans left, as on the goldens.
  - It is never drawn at or below the sash, because flying frames show the legs under the head. 20.0.x had a V on the trousers until I added this guard.
  - The old anchor on the chin skin was 1 px off on SSJ 0.0.0.
- Side opening:
  - It starts at the front end of the neck skin, and draws only on gi purple.
  - The facing comes from the coloured eyes. The base head has black eyes, so for it dir 2 faces left.

**Header**
- The Method text in the header is updated (lines 19-24).

## Tests (`scripts\permanent\tests\test_gi.py`, class `OwnerReviewTests`, line 197)

| Test | What it checks |
|---|---|
| `test_owner_legs_are_trouser_and_boot` | My leg boxes in 5.0.0, 5.1.1, 6.1.1, 7.0.1 (also the foot under the arm), 7.1.2 and 1.2.0. In all three forms: no skin or band, and brown boot present. |
| `test_owner_arms_are_skin_with_a_band` | SSJ2 arm boxes in 5.0.0 (wind-up fist by the neck), 5.1.1, 6.1.1, 7.0.1, 7.1.2, 1.2.0 and 1.2.2 show skin and a band. The arm piece beside the head in 5.1.1 and 6.1.1 is skin in SSJ and SSJ2. |
| `test_front_v_matches_golden` | Rows 19-20 of 0.0.0 equal the golden fronts in all three forms. |
| `test_side_opening_matches_golden` | Rows 19-20 of SSJ2 0.2.0 equal the golden side. |
| `test_every_opening_has_its_shape` | Every frame with `v_neck` "yes" has the front or side pattern. |

All 5 new tests fail on the old output (`gi-fix-1125\before\`). I ran that check before I added 1.2.2 to the arm boxes.

**Run results**
- `GiArtTests`, `OwnerReviewTests`, `HudZ2Tests` and `test_sprites`: 25 tests, OK.
- `patches.gohan_gi` applied to an in-memory ROM copy, with nothing written: it accepted the new art. Sets 157-159 were allocated, with no slot overflow.
- `gi_art.py all`: 0 failing checks in all three forms (162, 159 and 159 frames).
- Frame geometry (`keys` and `geometry` in each manifest entry) is the same as before for every frame. No record was enlarged.

## Frames changed per form (by frame header)

| Form | Changed | Legs and arms (10+ px) | V, opening and 1.2.2 only |
|---|---|---|---|
| gi_base | 81 | 17 | 64 |
| gi_ssj | 83 | 17 | 66 |
| gi_ssj2 | 84 | 17 | 67 |

**Legs and arms:** the same 17 keys in every form: 1.2.0, 5.0.0, 5.0.1, 5.0.2, 5.1.1, 5.1.2, 6.0.0, 6.0.1, 6.0.3, 6.1.1, 6.1.2, 7.0.0, 7.0.1, 7.0.3, 7.1.1, 7.1.2 and 18.0.0.

**Candidates that did not change:**
- 16.1.1 was already hinted as a knee.
- 8.0.0 keeps its low arm, because no shadow sits under that white.
- In 2.2.1 and 3.0.0 only the V moved. Their low skin is a hand.

**Front V count:**

| Form | Now | Before |
|---|---|---|
| base | 44 | 44 |
| SSJ | 42 | 48 |
| SSJ2 | 48 | 49 |

- Lost: 7.0.3 and 8.0.0 in all forms, plus SSJ 1.0.0, 12.0.0, 12.0.1 and 12.0.3. In each, an arm leaves less than 3 px of gi under the collar, so the centred V cannot fit and the chest stays covered.
- Gained: base 9.0.2 and 9.0.3.

**Side openings:**
- Of the 46 side frames, base has 27, SSJ 25 and SSJ2 22.
- Base and SSJ 0.2.0 get none: the near arm covers the chest, the same as on their golden sides.

## Animation cycles (I should know)

**The opening blinks on and off where a swinging arm covers the chest.**
- Front V flicker existed before this work: 2.0, 3.0, 5.0, 6.0, 7.0, 13.0 and 18.0 already mixed V and no V.
- Changes in front flicker:
  - SSJ 1.0 walk went from YY-Y to -Y-Y, because 1.0.0 lost its V.
  - The new 8.0 (-YYY) comes from 8.0.0.
  - Base 9.0 went from YY-- to YYYY.

**New side flicker:**
- Side walk 1.2: base and SSJ show Y-Y-. Indices 1 and 3 have the front arm over the chest. SSJ2 shows no opening on any walk frame.
- The same pattern shows in the 4.2, 6.2, 7.2, 13.2 and 16.2 cycles.

**What I saw:** at sprite scale, the openings are 3 px and the gaps match the arm swing. I judge this correct, but I should hear it first.

## Downstream manifest use

- Side frames used to carry `v_neck` "n.a. (side)". They now carry "yes" or "no: ...". The field names and the geometry are unchanged.
- I checked the transplant scripts for which manifest fields they read: `work_r3\transplant.py`, `finish_v2.py` and `bodyfix.py`. They read `keys`, `png`, `w`, `h`, `dx`, `dy`, `head`, `iou` and `status`.
- None of them reads `v_neck` or `view`. The new values break nothing there.

## Review sheets (3x)

- `archive\2026-10-17-gi-art-rounds\gi-fix-1125\before_after_3x_focus.png`: my frames and the idle frames, for each form. Columns: armor | before | after | golden.
- `archive\2026-10-17-gi-art-rounds\gi-fix-1125\before_after_3x_gi_base.png`, `..._gi_ssj.png` and `..._gi_ssj2.png`: every changed frame. Columns: armor | before | after.
- Script: `archive\2026-10-17-gi-art-rounds\gi-fix-1125\sheet.py`.
- Pre-fix output and the `gi_art.py` backup: `archive\2026-10-17-gi-art-rounds\gi-fix-1125\before\`.

**What I inspected by eye:**
- All four sheets, each split into thirds. I saw no gross regression.
- At 8-18x, mostly SSJ2:
  - I-marked frames;
  - anim 5, 6, 7 and 18.0.0;
  - the walk cycles 1.0.x and 1.2.x in all forms;
  - 1.2.2 in all forms;
  - the front V crops for SSJ and SSJ2;
  - the side opening crops for base and SSJ2.

## Concerns

1. The 5.0.2 left arm call is in PENDING above.
2. Golden differences I left out of scope:
   - the wristband 72 vs 195 placement on the idle arms;
   - the arm outline 23 vs 211 on the base and SSJ sides (golden row 19 col 11);
   - golden-only hand tweaks;
   - the eyes and heads, which the head transplant replaces.
3. The base and SSJ lying frames 12.2.x get a side opening under the chin, on the horizontal body. No golden covers them.
4. Base 6.1.1 has its sash one row higher than SSJ and SSJ2. This was already so before this work, and I left it.
5. The 1.2.2 back arm is a hand edit (FIXES), not a rule. A future change to the 1.2.2 record makes `make_gi_set` refuse the build, by design.
