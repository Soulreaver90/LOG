STATUS: Task 5 part 1, Steps 1-5, is done. I stopped at my art gate. I built no ROM, ran no git command and wrote nothing under data\.
REPORT FILE: The harness refused my write of the .md report. The full report is below, so this message runs past 15 lines. docs\tasks\2026-10-16-task-5-gi-art\task-5-report.md is an old draft. It is not the report.
SHEETS (under LOG\art\): gi_base_sheet.png, gi_ssj_sheet.png (with the set 61 brow crop), gi_ssj2_sheet.png, gi_overview.png, gi_ssj_9_2_test_cases.png, anim\compare_transform.png. Strips and GIFs are in anim\<form>\.
FRAMES: 162 base, 159 SSJ and 159 SSJ2. 0 checks fail. Each form has 1 recorded exception (3.0.1). IoU is 1.0 in every frame.
HAND WORK: 0 pixel edits. 13 keys have a reviewed part hint (35 key-form pairs). 13 frame headers are flagged for my look.
TESTS: 29 tests OK, 2 skipped (part 2). 2 mutation checks failed as expected, then passed after I restored the file.
CONCERN 1: 22 SSJ2 records are enlarged (8 at 32x32, 14 at 32x64). Direction k allows this. Ruling 18 says to keep w and h. Part 2 must allow for the sizes and VRAM.
CONCERN 2: 30 SSJ2 frames are stand-ins (set 59 body, set 58 head). The lying frames 12.2.x are the weakest.
CONCERN 3: The mouth exemption differs from the advisor's advice. It applies to y <= chin only, not to "inside the mask". An audit found 0 exempted pixels below the chin.
CONCERN 4: The Ruling 25 check counts skin pixels. It does not measure V depth. The fixed V shape sets the depth: 3 px, 2 rows.
DOCS: docs\RE-BIBLE.md has 16 new lines tagged T5. The Z2 files were not touched.
Report: below.

====================================================================
# Task 5 part 1 report: gi sprites and Z2 icon (Steps 1-5)

The art, the tool and this report all need my review at the art gate before any use.

## 1. Summary

| Item | Result |
|---|---|
| gi base (new set 157) | 162 frames. The pose and record come from set 56 |
| gi Super Saiyan (new set 158) | 159 frames. The pose and record come from set 59 |
| gi Super Saiyan 2 (new set 159) | 159 frames: 129 from set 58, plus 30 stand-ins (set 59 body, set 58 head) for keys that set 58 does not have |
| Per-frame checks failing | 0 in each form. 1 recorded exception per form (3.0.1, section 6) |
| Silhouette IoU against the same-form original | 1.0 in every frame. The body is repainted in place. For stand-ins, IoU is measured on the body only |
| Hand pixel edits (FIXES) | 0 |
| Part hints (PART_HINTS, a reviewed class override for a white part) | 13 keys, 35 key-form pairs |
| Frame headers flagged for my look | 13 (section 7) |
| Z2 HUD icon | Unchanged, as approved (direction p) |
| Test suite | 29 tests OK, 2 skipped (part 2 patch tests) |

## 2. Files (under )

| File | Contents |
|---|---|
| scripts\permanent\art\gi_art.py | The tool (v3). Commands: frames, sheets, anim, compare, all. z2 runs only on request |
| scripts\permanent\tests\test_gi.py | Art tests (updated for the new geometry and checks), Z2 tests and 2 skipped patch tests |
| art\gi_base\, gi_ssj\, gi_ssj2\ | One indexed PNG per frame header, plus manifest.json (geometry, source, view, V-neck, notes, checks, head pixels, keys with records) |
| art\gi_base_sheet.png, gi_ssj_sheet.png, gi_ssj2_sheet.png | A review sheet per form: the original and the gi frame on one anchor, with the per-frame checks. The SSJ sheet also has the Goku set 61 0.0.0 brow crop |
| art\gi_overview.png | Armor and gi in all three forms, idle, 4 dirs |
| art\gi_ssj_9_2_test_cases.png | SSJ 9.2.0-9.2.2 at 4x: original, old method (before) and gi (after) |
| art\anim\<form>\ | Per anim: a strip PNG (gi, original and onion skin, one anchor, 4x) and one GIF per dir |
| art\anim\compare_transform.png, art\anim\compare\ | Transform comparison sheet and 13 GIFs |
| art\hud_z2.png, hud_z2_usable.bin, hud_z2_dim.bin | Z2 icon. Not touched in this run |
| archive\2026-10-17-gi-art-rounds\art-work\gi_art_v1.py, gi_art_v2_headswap.py, gi_art_v3_*.py | Backups of earlier versions and checkpoints |
| art\work\gi_base_old_method\, gi_ssj_old_method\, gi_ssj2_old_method\ | Old-method frames, kept for the before and after sheet |
| archive\2026-10-17-gi-art-rounds\art-work\report_tables.py, report_compact.py | Throwaway scripts. They print the tables in sections 9 and 10 from the manifests |
| docs\RE-BIBLE.md | 16 new lines tagged T5 (sections 4, 5 and 11). T5 is added to the source list |

## 3. Method and palette mapping (directions h, k, l)

Each gi frame keeps the pose and the record (w, h, dx, dy, attr0, attr1) of the original frame of the same form. Only the armor body is repainted. The head, hair, eyes, aura, sparks and attack arcs keep their pixels.

| Armor part (source indices) | Gi result |
|---|---|
| Jumpsuit blue 77, 79, 80 | Gi purple 88, dark shade 89 |
| Jumpsuit outline 81, loose grey outline 13, 14 | Outline 211 on the sprite edge, else 89 |
| Chest plate whites 2, 9-12 and trim 16, 40-42, 46, 128, 131, 142 | Purple 88 (dark 89, edge 211) |
| Collar and shoulder bits next to the trim | Purple, with no collar. Front frames get a fixed V of 3 skin px (115, 116), 2 wide and 2 rows deep |
| Sleeves (suit pixels on the line from a glove to its shoulder) | Skin 114-117 with outline 23. An arm that touches the face also gets outline 23 |
| White glove | Skin fist (2 and 9 to 114, 10 to 115, others to 116, outline 23). A wristband at the cuff: 195 with outline 72 |
| White boot | The lowest 3 rows become brown (34, edge 35). The boot shaft above becomes trouser purple |
| Waist line | Red sash 26 with ends 27, as one run at the waist. It never goes on arms, hands or boots |
| SSJ2 sparks (small light parts near the head) | Light blue 191 with a white 2 core, in the same place (Ruling 19) |
| White or light grey left in the body | Repainted with the majority color of its neighbours (gi, skin or outline) |

White and light grey indices (Ruling 26), from the palette at rom:0x1DA6C8: 2 (248,248,248), 9 (216,216,216), 10 (192,192,192), 11 (168,168,168), 12 (144,144,144), 43 (248,248,240). These regions are exempt: eye whites, mouths (a light pixel between face skin, at or above the chin row, or next to an eye), hair shine (inside the hair or on its rim), motion arcs and streaks, and SSJ2 spark cores.

## 4. My direction and status

| Dir | Direction | Status |
|---|---|---|
| a | Base head and hair from set 56 (superseded by Ruling 27) | Done. Every base frame is set 56 itself |
| b | V-neck in all forms (superseded by Ruling 25) | Done under Ruling 25 |
| c | No set 53 ponytail or collar. Hair and collar check. A 4x review sheet per form. A per-frame table with hair, collar, V-neck, notes and eyebrows | Done. No set 53 pixels are used. The collar is repainted. Sheets exist, and the table is in section 9 |
| d | Animation review per form and per (anim, dir): strip, GIF and onion skin. Look, fix, look again | Done. All strips and GIFs were made again and viewed after the last fix. Table in section 10 |
| e | SSJ and SSJ2 brows in hair colors. Reference crop. Set ids and brow indices in the RE-BIBLE | Done. The SSJ and SSJ2 heads come from sets 59 and 58, which already use pal:20 and pal:21 above the eyes, like Goku set 61, Vegeta sets 139 and 140, and Trunks set 130. Base keeps black brows. Dark brow pixels remain only where the hair is black (knocked down 3.x.2-3, revert 21.x.2-3) and in SSJ 20.0.x (1-2 original pixels) |
| f | Ruling 25 torso skin. Purple must outnumber chest skin. Front V at most 2 px deep. Side at most 1 skin px. Back 0 | Done. The V shape is fixed at 3 px, 2 rows deep. The check counts skin pixels in the box under the chin: front at most 3, side at most 1, back 0, and gi must be more than 2 times the skin. The check does not measure depth. A test computes the count again from each PNG |
| g | Ruling 26: 0 white indices in the body from the neck down, with exceptions by region | Done. Each frame is checked, and a test computes it again from the PNG |
| h | Ruling 27: pose from the same form, IoU audit, and anims 9 and 21 reviewed first | Done. IoU is 1.0. Anims 9 and 21 were reviewed first |
| i | Transform comparison with Goku, Vegeta and Trunks | Done. Section 8 |
| j | Anim 20 fixes and an audit for hollow gloves and boots | Done. Anim 20 is fixed in all forms. "Lost" (original pixels left empty) is 0 in every frame |
| k | Geometry from the same form, the next legal size if needed, no lost pixel, no new hair on an edge, and the SSJ2 0.2.0 Rage stance | Done. 22 SSJ2 stand-in records are enlarged (section 6). SSJ2 0.2.0 keeps the set 58 record and stance |
| l | Conversion map, all checks, and a full strip and GIF review | Done. Section 3 |
| m | SSJ2 anim 4 sparks blue in place. RE-BIBLE spark anims. SSJ2 anim 5 wristbands | Done. Sparks are 191 with a 2 core. Frames 5.0.1, 5.0.2, 5.2.1, 5.2.2 and 5.3.1 have wristbands |
| n | SSJ 9.2.0-9.2.2 test cases at 4x, before and after | Done. art\gi_ssj_9_2_test_cases.png. The aura stays. The gloves are skin fists with wristbands |
| o | SSJ2 anim 11 arms and heads. Set 58 scan. RE-BIBLE note | Done. Set 58 has anims 0-8, 13, 16 and 18 and shares 0 headers with set 59. Every SSJ2 frame shows the SSJ2 head, except the revert frames 21.x.2-3, which show the base head. Arms in front of the hair stay |
| p | The Z2 icon is approved as is | Done. The files were not touched (timestamps unchanged) |

## 5. Frame counts and unmatched keys

| Form | Frame headers | Keys | From the same-form original | Stand-ins |
|---|---|---|---|---|
| gi base | 162 | 288 | 162 (set 56) | 0 |
| gi Super Saiyan | 159 | 276 | 159 (set 59) | 0 |
| gi Super Saiyan 2 | 159 | 276 | 129 (set 58) | 30 |

Unmatched keys (set 58 has no frame for them): anim 9 (9.0.0-9.0.3), anim 11 (11.0.0-11.0.1), anim 12 (12 headers: 12.0.x, 12.1.x and 12.2.x, which 12.3.x shares), anim 20 (20.0.x, 20.1.x) and anim 21 (21.0.x). These 30 headers use the set 59 body with one set 58 head per (anim, dir), placed by the eyes. The revert keeps the base head in 21.x.2-3 and dims the hair in 21.x.1.

## 6. Geometry and check exceptions

- 22 SSJ2 stand-in records are enlarged to keep the new hair 1 px from the edge: 8 to 32x32 (12.0.x, 12.1.x) and 14 to 32x64 (9.0.1-3, 11.0.0-1, 12.2.x, 20.1.x, 21.0.0). Each new box holds the original box, and a test checks this.
- Exception in all forms, 3.0.1: the box under the chin holds the hand on the ground, not the chest. I reviewed this at 4x.
- Chest check "n.a." (no gi and no skin in the box under the chin, because the frame is lying, flying, or has the head over the torso): 10 base frames, 9 SSJ frames and 9 SSJ2 frames. I looked at each one in the strips. None shows a bare torso.

## 7. Hand work and frames for my look

No pixel was edited by hand. 13 keys have a reviewed part hint (PART_HINTS in gi_art.py): 5.1.0, 6.1.0, 7.1.0, 6.1.3, 7.1.3, 13.1.1, 13.1.3, 13.2.1, 13.3.1, 14.0.3, 14.0.4, 16.2.4, 16.3.4.

Frame headers flagged for my look (13):
1. 7.2.3 in all three forms: the punch fist shows no wristband.
2. 16.2.3 in all three forms: the hands at the face show no wristband.
3. 18.0.2 in all three forms: the crossed-arm block frame reads busy.
4. SSJ2 12.2.0-12.2.3 (shared by 12.3.x, so 8 keys): an upright set 58 head on a lying set 59 body.

## 8. Transform comparison (direction i)

The sheet is art\anim\compare_transform.png (one anchor, 4x, all dirs). The GIFs are in art\anim\compare\. The set pairs come from the appearance table at rom:0x1D967C (entries whose +4 target is a transformed entry).

| Row | Set (entry) | Anim | Frames per dir | What I saw |
|---|---|---|---|---|
| Goku | set 60 (19, +4 = 20) | 9 | 4 | Power-up pose, flash hair (brown and gold), gold, gold. No aura |
| Goku SSJ | set 61 (20) | 21 | 4 | Gold, dim gold, brown, black |
| Vegeta | set 137 (8, +4 = 11) | 9 | 4 | The same sequence as Goku |
| Vegeta SSJ | set 140 (11) | 21 | 4 | The same as Goku |
| Trunks | set 129 (13, +4 = 14) | 9 | 4 | The same sequence |
| Trunks SSJ | set 130 (14) | 21 | 4 | The same |
| Gohan | set 56 | 9 | 4 | The same sequence |
| gi base | new set 157 | 9 | 4 | Matches set 56 frame for frame |
| Gohan SSJ | set 59 | 9 | 4 | SSJ to SSJ2 step: a gold aura ring in frames 1-3 |
| gi SSJ | new set 158 | 9 | 4 | Matches set 59. The aura stays. Skin fists with wristbands |
| Gohan SSJ revert | set 59 | 21 | 4 | Gold, dim gold, brown, black |
| gi SSJ revert | new set 158 | 21 | 4 | Matches |
| gi SSJ2 revert | new set 159 | 21 | 4 | SSJ2 head, dimmed SSJ2 head, base head, base head |

Gap found and fixed: frame 1 of the gi SSJ2 revert had a bright head. It is now dimmed one step, like set 59 21.x.1. Timing: anims 9 and 21 are not traced, so the GIFs use 167 ms per frame. Set 103 to set 104 is Piccolo, not Trunks.

## 9. Per-frame table

These columns have the same value in all 480 rows, so the table leaves them out: IoU 1.0, Lost 0, Edge hair 0, Light 0. IoU is measured against the same-form original, on the body only for stand-ins. Lost is the number of original pixels left empty. Edge hair is hair on the record edge that the original does not have. Light is the number of armor white pixels left in the body.

Columns:
- Key (keys): the first key, then the number of keys that share the header.
- Record: w x h. "enlarged" means a larger legal size. "(setNN k)" names the source when it is not the same key of the form's own set.
- Chest skin / gi: the pixel counts in the box under the chin. "n.a." means no torso is in the box.
- V: the V-neck. "yes" means front and drawn. "n.a." means a side or back view. "no (blocked)" means no gi under the chin, because an arm, the pose or an effect is in the way. A front frame with V "yes" and 0 chest skin has its V drawn, but the V touches arm or face skin, so the box count leaves it out. This is from the code, and I did not check each frame.
- Brow: black pixels that touch face skin in the head. Black brows are expected in base, and 0 is expected in the SSJ heads.
- Hint: a PART_HINTS override.
- Notes: hN, wbN = hands and wristbands found. The fragments of one glove count separately. Then come repaints, stand-in head sources, record changes, exceptions and review flags.

| Form | Key (keys) | Record | Chest skin / gi | V | Brow | Hint | Notes |
|---|---|---|---|---|---|---|---|
| base | 0.0.0 | 16x32 | 3 / 24 | yes | 27 |  | h2, wb2 |
| base | 0.0.1 | 16x32 | 3 / 24 | yes | 25 |  | h2, wb2 |
| base | 0.1.0 (2) | 16x32 | 0 / 20 | n.a. (back) | 6 |  | h2, wb2 |
| base | 0.2.0 (2) | 16x32 | 0 / 14 | n.a. (side) | 16 |  | h1, wb1 |
| base | 0.2.1 (2) | 16x32 | 0 / 14 | n.a. (side) | 14 |  | h1, wb1 |
| base | 1.0.0 | 16x32 | 3 / 15 | yes | 26 |  | h5, wb5 |
| base | 1.0.1 | 16x32 | 3 / 25 | yes | 27 |  | h2, wb2 |
| base | 1.0.2 | 16x32 | 0 / 16 | yes | 26 |  | h4, wb4 |
| base | 1.0.3 | 16x32 | 3 / 25 | yes | 27 |  | h2, wb2 |
| base | 1.1.0 | 16x32 | 0 / 19 | n.a. (back) | 6 |  | h2, wb2 |
| base | 1.1.1 | 16x32 | 0 / 20 | n.a. (back) | 6 |  | h2, wb2 |
| base | 1.1.2 | 16x32 | 0 / 19 | n.a. (back) | 6 |  | h2, wb2 |
| base | 1.1.3 | 16x32 | 0 / 20 | n.a. (back) | 6 |  | h2, wb2 |
| base | 1.2.0 (2) | 16x32 | 0 / 27 | n.a. (side) | 16 |  | h2, wb2 |
| base | 1.2.1 (2) | 16x32 | 0 / 14 | n.a. (side) | 18 |  | h1, wb1 |
| base | 1.2.2 (2) | 16x32 | 0 / 23 | n.a. (side) | 16 |  | h2, wb2 |
| base | 1.2.3 (2) | 16x32 | 0 / 15 | n.a. (side) | 16 |  | h1, wb1 |
| base | 2.0.0 | 16x32 | 3 / 23 | yes | 26 |  | h2, wb2 |
| base | 2.0.1 | 16x32 | 1 / 25 | yes | 15 |  | h2, wb2; 1 white repainted |
| base | 2.0.2 | 16x32 | 0 / 7 | yes | 27 |  | h1, wb1 |
| base | 2.0.3 | 16x32 | 0 / 10 | yes | 25 |  | h2, wb2 |
| base | 2.1.0 | 16x32 | 0 / 24 | n.a. (back) | 0 |  |  |
| base | 2.1.1 | 16x32 | 0 / 21 | n.a. (back) | 6 |  | h2, wb2 |
| base | 2.1.2 | 16x32 | 0 / 29 | n.a. (back) | 6 |  |  |
| base | 2.1.3 | 16x32 | 0 / 25 | n.a. (back) | 0 |  |  |
| base | 2.2.0 (2) | 16x32 | 0 / 13 | n.a. (side) | 14 |  | h3, wb3 |
| base | 2.2.1 (2) | 16x32 | 0 / 25 | n.a. (side) | 15 |  | h1, wb1; 2 white repainted |
| base | 2.2.2 (2) | 16x32 | 0 / 23 | n.a. (side) | 13 |  | h1, wb1 |
| base | 2.2.3 (2) | 16x32 | 0 / 24 | n.a. (side) | 13 |  | h1, wb1 |
| base | 3.0.0 (4) | 32x32 | 0 / 14 | yes | 14 |  | h2, wb2; 1 white repainted |
| base | 3.0.1 (4) | 32x32 | 3 / 2 | yes | 13 |  | h2, wb1; 4 chest skin covered; knocked down: the box under the chin holds the hand on the ground, not the chest (reviewed at 4x) |
| base | 3.0.2 (4) | 32x32 | 0 / 0 n.a. | no (blocked) | 14 |  | h1, wb0 |
| base | 3.0.3 (4) | 32x32 | 0 / 0 n.a. | no (blocked) | 14 |  | h1, wb0 |
| base | 4.0.0 | 16x32 | 3 / 24 | yes | 25 |  | h2, wb2 |
| base | 4.0.1 | 16x32 | 3 / 23 | yes | 20 |  | h7, wb6; 2 chest skin covered |
| base | 4.0.2 | 16x32 | 3 / 24 | yes | 25 |  | h2, wb2 |
| base | 4.0.3 | 16x32 | 3 / 23 | yes | 20 |  | h6, wb5; 2 chest skin covered |
| base | 4.1.0 | 16x32 | 0 / 20 | n.a. (back) | 6 |  | h2, wb2 |
| base | 4.1.1 | 16x32 | 0 / 24 | n.a. (back) | 12 |  | h4, wb0 |
| base | 4.1.2 | 16x32 | 0 / 20 | n.a. (back) | 6 |  | h2, wb2 |
| base | 4.1.3 | 16x32 | 0 / 24 | n.a. (back) | 11 |  | h2, wb0 |
| base | 4.2.0 (2) | 16x32 | 0 / 14 | n.a. (side) | 14 |  | h1, wb1 |
| base | 4.2.1 (2) | 16x32 | 0 / 20 | n.a. (side) | 17 |  | h1, wb1 |
| base | 4.2.2 (2) | 16x32 | 0 / 14 | n.a. (side) | 14 |  | h1, wb1 |
| base | 4.2.3 (2) | 16x32 | 0 / 20 | n.a. (side) | 14 |  | h1, wb1 |
| base | 5.0.0 | 16x32 | 3 / 9 | yes | 28 |  | h3, wb3; 1 chest skin covered |
| base | 5.0.1 | 16x32 | 3 / 14 | yes | 28 |  | h2, wb2 |
| base | 5.0.2 | 16x32 | 3 / 18 | yes | 28 |  | h2, wb2 |
| base | 5.1.0 | 16x32 | 0 / 31 | n.a. (back) | 1 | yes | h1, wb1 |
| base | 5.1.1 | 16x32 | 0 / 11 | n.a. (back) | 3 |  | h4, wb2 |
| base | 5.1.2 | 16x32 | 0 / 10 | n.a. (back) | 3 |  | h4, wb2 |
| base | 5.2.0 (2) | 32x32 | 0 / 24 | n.a. (side) | 17 |  | h5, wb5 |
| base | 5.2.1 (2) | 32x32 | 0 / 25 | n.a. (side) | 15 |  | h1, wb1; 3 white repainted |
| base | 5.2.2 (2) | 32x32 | 0 / 19 | n.a. (side) | 16 |  | h3, wb3; 1 white repainted |
| base | 6.0.0 | 32x32 | 3 / 8 | yes | 29 |  | h3, wb2; 2 chest skin covered |
| base | 6.0.1 | 32x32 | 0 / 16 | yes | 32 |  | h3, wb3 |
| base | 6.0.2 | 32x32 | 0 / 26 | yes | 25 |  | h1, wb1; 2 white repainted |
| base | 6.0.3 | 32x32 | 0 / 12 | no (blocked) | 25 |  | h2, wb2; 1 white repainted |
| base | 6.1.0 | 32x32 | 0 / 17 | n.a. (back) | 1 | yes | h3, wb3 |
| base | 6.1.1 | 32x32 | 0 / 19 | n.a. (back) | 5 |  | h5, wb3 |
| base | 6.1.2 | 32x32 | 0 / 11 | n.a. (back) | 5 |  | h3, wb2 |
| base | 6.1.3 | 32x32 | 0 / 5 | n.a. (back) | 3 | yes | h2, wb1 |
| base | 6.2.0 (2) | 32x32 | 0 / 24 | n.a. (side) | 16 |  | h3, wb3; 1 white repainted |
| base | 6.2.1 (2) | 32x32 | 0 / 23 | n.a. (side) | 16 |  | h3, wb3; 1 white repainted |
| base | 6.2.2 (2) | 32x32 | 0 / 19 | n.a. (side) | 16 |  | h2, wb2 |
| base | 6.2.3 (2) | 32x32 | 0 / 24 | n.a. (side) | 16 |  | h4, wb4 |
| base | 7.0.0 | 32x32 | 3 / 8 | yes | 29 |  | h3, wb2; 2 chest skin covered |
| base | 7.0.1 | 32x32 | 3 / 16 | yes | 32 |  | h3, wb3 |
| base | 7.0.2 | 32x32 | 3 / 26 | yes | 25 |  | h1, wb1; 2 white repainted |
| base | 7.0.3 | 32x32 | 0 / 12 | yes | 25 |  | h2, wb2; 1 white repainted |
| base | 7.1.0 | 32x32 | 0 / 17 | n.a. (back) | 1 | yes | h3, wb3 |
| base | 7.1.1 | 32x32 | 0 / 19 | n.a. (back) | 5 |  | h5, wb3 |
| base | 7.1.2 | 32x32 | 0 / 11 | n.a. (back) | 5 |  | h3, wb2 |
| base | 7.1.3 | 32x32 | 0 / 5 | n.a. (back) | 3 | yes | h2, wb1 |
| base | 7.2.0 (2) | 32x32 | 0 / 24 | n.a. (side) | 17 |  | h5, wb5 |
| base | 7.2.1 (2) | 32x32 | 0 / 21 | n.a. (side) | 16 |  | h1, wb1 |
| base | 7.2.2 (2) | 32x32 | 0 / 20 | n.a. (side) | 15 |  | h1, wb1; 3 white repainted |
| base | 7.2.3 (2) | 32x32 | 0 / 26 | n.a. (side) | 17 |  | h1, wb0; 3 white repainted; punch fist shows no wristband |
| base | 8.0.0 | 32x32 | 0 / 10 | yes | 29 |  | h3, wb2 |
| base | 8.0.1 | 32x32 | 3 / 20 | yes | 32 |  | h2, wb2 |
| base | 8.0.2 | 32x32 | 3 / 26 | yes | 25 |  | h1, wb1 |
| base | 8.0.3 | 32x32 | 3 / 26 | yes | 26 |  | h1, wb1; 1 chest skin covered |
| base | 8.1.0 | 32x32 | 0 / 25 | n.a. (back) | 1 |  | h1, wb1 |
| base | 8.1.1 | 32x32 | 0 / 11 | n.a. (back) | 6 |  | h6, wb6 |
| base | 8.1.2 | 32x32 | 0 / 16 | n.a. (back) | 8 |  | h2, wb1; 2 chest skin covered |
| base | 8.1.3 | 32x32 | 0 / 24 | n.a. (back) | 2 |  | h3, wb3 |
| base | 8.2.0 (2) | 32x32 | 0 / 27 | n.a. (side) | 17 |  | h4, wb4; 1 chest skin covered |
| base | 8.2.1 (2) | 32x32 | 0 / 20 | n.a. (side) | 17 |  | h4, wb4 |
| base | 8.2.2 (2) | 32x32 | 0 / 13 | n.a. (side) | 18 |  | h4, wb2; 2 white repainted |
| base | 8.2.3 (2) | 32x32 | 0 / 25 | n.a. (side) | 16 |  | h3, wb3 |
| base | 9.0.0 (4) | 32x32 | 3 / 24 | yes | 26 |  | h2, wb2 |
| base | 9.0.1 (4) | 32x32 | 0 / 22 | yes | 18 |  | h2, wb2 |
| base | 9.0.2 (4) | 32x32 | 0 / 21 | yes | 0 |  | h2, wb2; 3 chest skin covered |
| base | 9.0.3 (4) | 32x32 | 0 / 21 | yes | 0 |  | h2, wb2; 3 chest skin covered |
| base | 11.0.0 (4) | 16x32 | 3 / 24 | yes | 25 |  | h2, wb2 |
| base | 11.0.1 (4) | 16x32 | 3 / 23 | yes | 19 |  | h8, wb8; 2 chest skin covered |
| base | 12.0.0 | 16x32 | 0 / 0 n.a. | no (blocked) | 36 |  | h5, wb2 |
| base | 12.0.1 | 16x32 | 0 / 0 n.a. | no (blocked) | 36 |  | h5, wb2 |
| base | 12.0.2 | 16x32 | 0 / 0 n.a. | no (blocked) | 35 |  | h5, wb2 |
| base | 12.0.3 | 16x32 | 0 / 0 n.a. | no (blocked) | 36 |  | h5, wb2 |
| base | 12.1.0 | 16x32 | 0 / 22 | n.a. (back) | 14 |  | h2, wb2; 1 chest skin covered |
| base | 12.1.1 | 16x32 | 0 / 22 | n.a. (back) | 15 |  | h3, wb2; 1 chest skin covered |
| base | 12.1.2 | 16x32 | 0 / 22 | n.a. (back) | 13 |  | h2, wb2; 1 chest skin covered |
| base | 12.1.3 | 16x32 | 0 / 22 | n.a. (back) | 15 |  | h3, wb2; 1 chest skin covered |
| base | 12.2.0 (2) | 32x32 | 0 / 18 | n.a. (side) | 17 |  | h3, wb3 |
| base | 12.2.1 (2) | 32x32 | 0 / 18 | n.a. (side) | 17 |  | h3, wb3 |
| base | 12.2.2 (2) | 32x32 | 0 / 18 | n.a. (side) | 17 |  | h3, wb3 |
| base | 12.2.3 (2) | 32x32 | 0 / 18 | n.a. (side) | 17 |  | h3, wb3 |
| base | 13.0.0 | 16x32 | 0 / 12 | yes | 27 |  | h2, wb2 |
| base | 13.0.1 | 16x32 | 0 / 23 | yes | 26 |  | h3, wb2; 2 white repainted |
| base | 13.0.2 | 16x32 | 0 / 12 | yes | 27 |  | h2, wb2 |
| base | 13.0.3 | 16x32 | 1 / 23 | yes | 26 |  | h2, wb1; 1 white repainted |
| base | 13.1.0 | 16x32 | 0 / 1 | n.a. (back) | 6 |  | h2, wb2 |
| base | 13.1.1 | 16x32 | 0 / 28 | n.a. (back) | 5 | yes | h2, wb2 |
| base | 13.1.2 | 16x32 | 0 / 1 | n.a. (back) | 3 |  | h1, wb1 |
| base | 13.1.3 | 16x32 | 0 / 20 | n.a. (back) | 0 | yes | h2, wb2 |
| base | 13.2.0 (2) | 32x32 | 0 / 20 | n.a. (side) | 16 |  | h2, wb2; 2 white repainted |
| base | 13.2.1 (2) | 32x32 | 0 / 15 | n.a. (side) | 16 | yes | h2, wb2 |
| base | 13.2.2 (2) | 32x32 | 0 / 25 | n.a. (side) | 17 |  | h2, wb2 |
| base | 13.2.3 (2) | 32x32 | 0 / 10 | n.a. (side) | 17 |  | h3, wb3; 2 white repainted |
| base | 14.0.0 (4) | 16x32 | 3 / 23 | yes | 25 |  | h2, wb2 |
| base | 14.0.1 (4) | 16x32 | 3 / 22 | yes | 23 |  | h4, wb4 |
| base | 14.0.2 (4) | 16x32 | 3 / 18 | yes | 25 |  | h2, wb2 |
| base | 14.0.3 (4) | 16x32 | 3 / 23 | yes | 24 | yes | h2, wb2 |
| base | 14.0.4 (4) | 16x32 | 3 / 23 | yes | 27 | yes | h2, wb2 |
| base | 16.0.0 | 32x32 | 3 / 23 | yes | 25 |  | h2, wb2 |
| base | 16.0.1 | 32x32 | 0 / 25 | yes | 21 |  | h6, wb5; 2 white repainted |
| base | 16.0.2 | 32x32 | 3 / 23 | yes | 26 |  | h2, wb2; 2 white repainted |
| base | 16.0.3 | 32x32 | 3 / 22 | yes | 30 |  | h2, wb2 |
| base | 16.0.4 | 32x32 | 3 / 22 | yes | 29 |  | h2, wb2 |
| base | 16.0.5 (2) | 32x32 | 3 / 15 | yes | 36 |  | h5, wb5; 2 chest skin covered |
| base | 16.1.0 | 32x32 | 0 / 27 | n.a. (back) | 7 |  | h4, wb4; 1 white repainted |
| base | 16.1.1 | 32x32 | 0 / 20 | n.a. (back) | 16 |  | h5, wb4 |
| base | 16.1.2 | 32x32 | 0 / 12 | n.a. (back) | 6 |  | h2, wb0 |
| base | 16.1.3 | 32x32 | 0 / 22 | n.a. (back) | 8 |  | h2, wb2 |
| base | 16.1.4 | 32x32 | 0 / 10 | n.a. (back) | 8 |  | h3, wb2 |
| base | 16.1.5 (2) | 32x32 | 0 / 25 | n.a. (back) | 8 |  | h2, wb2 |
| base | 16.2.0 (2) | 32x32 | 0 / 23 | n.a. (side) | 16 |  | h2, wb2 |
| base | 16.2.1 (2) | 32x32 | 0 / 17 | n.a. (side) | 13 |  | h3, wb3 |
| base | 16.2.2 (2) | 32x32 | 0 / 20 | n.a. (side) | 13 |  | h3, wb3 |
| base | 16.2.3 (2) | 32x32 | 0 / 27 | n.a. (side) | 18 |  | h2, wb0; hands at the face show no wristband |
| base | 16.2.4 (2) | 32x32 | 0 / 15 | n.a. (side) | 32 | yes | h3, wb1 |
| base | 16.2.5 (4) | 32x32 | 0 / 17 | n.a. (side) | 16 |  | h4, wb2 |
| base | 17.0.0 (4) | 16x32 | 3 / 24 | yes | 27 |  | h4, wb4; 2 white repainted |
| base | 17.0.1 (4) | 16x32 | 3 / 24 | yes | 27 |  | h4, wb4; 2 white repainted |
| base | 18.0.0 | 16x32 | 0 / 8 | yes | 20 |  | h4, wb4 |
| base | 18.0.1 | 16x32 | 0 / 13 | yes | 20 |  | h1, wb1; 1 white repainted |
| base | 18.0.2 (5) | 16x32 | 3 / 27 | yes | 3 |  | h2, wb0; crossed-arm block frame reads busy |
| base | 18.1.0 | 16x32 | 0 / 20 | n.a. (back) | 1 |  | h3, wb3; 1 chest skin covered |
| base | 18.1.1 | 16x32 | 0 / 20 | n.a. (back) | 3 |  | h1, wb1 |
| base | 18.1.2 (5) | 16x32 | 0 / 13 | n.a. (back) | 7 |  | h2, wb1 |
| base | 18.2.0 (2) | 32x32 | 0 / 21 | n.a. (side) | 16 |  | h4, wb4 |
| base | 18.2.1 (2) | 32x32 | 0 / 26 | n.a. (side) | 16 |  | h2, wb2 |
| base | 18.2.2 (10) | 32x32 | 0 / 24 | n.a. (side) | 13 |  | h2, wb1 |
| base | 20.0.0 (2) | 32x32 | 0 / 0 n.a. | no (blocked) | 27 |  | h9, wb8 |
| base | 20.0.1 (2) | 32x32 | 0 / 0 n.a. | no (blocked) | 27 |  | h9, wb8 |
| base | 20.0.2 (2) | 32x32 | 0 / 0 n.a. | no (blocked) | 27 |  | h9, wb8 |
| base | 20.0.3 (2) | 32x32 | 0 / 0 n.a. | no (blocked) | 25 |  | h9, wb8 |
| base | 20.1.0 (2) | 32x32 | 0 / 7 | n.a. (back) | 7 |  | h1, wb1 |
| base | 20.1.1 (2) | 32x32 | 0 / 7 | n.a. (back) | 7 |  | h1, wb1 |
| base | 20.1.2 (2) | 32x32 | 0 / 7 | n.a. (back) | 7 |  | h1, wb1 |
| base | 20.1.3 (2) | 32x32 | 0 / 7 | n.a. (back) | 7 |  | h1, wb1 |
| ssj | 0.0.0 | 16x32 | 0 / 23 | yes | 0 |  | h2, wb2 |
| ssj | 0.0.1 | 16x32 | 0 / 23 | yes | 0 |  | h2, wb2 |
| ssj | 0.1.0 (2) | 16x32 | 0 / 28 | n.a. (back) | 0 |  | h2, wb2 |
| ssj | 0.2.0 (2) | 16x32 | 0 / 11 | n.a. (side) | 0 |  | h1, wb1 |
| ssj | 0.2.1 (2) | 16x32 | 0 / 11 | n.a. (side) | 0 |  | h1, wb1 |
| ssj | 1.0.0 | 16x32 | 0 / 13 | yes | 0 |  | h5, wb5 |
| ssj | 1.0.1 | 16x32 | 0 / 23 | yes | 0 |  | h2, wb2 |
| ssj | 1.0.2 | 16x32 | 0 / 12 | no (blocked) | 0 |  | h4, wb4; 4 chest skin covered |
| ssj | 1.0.3 | 16x32 | 0 / 23 | yes | 0 |  | h2, wb2 |
| ssj | 1.1.0 | 16x32 | 0 / 16 | n.a. (back) | 0 |  | h2, wb2 |
| ssj | 1.1.1 | 16x32 | 0 / 27 | n.a. (back) | 0 |  | h2, wb2 |
| ssj | 1.1.2 | 16x32 | 0 / 24 | n.a. (back) | 0 |  | h2, wb2 |
| ssj | 1.1.3 | 16x32 | 0 / 27 | n.a. (back) | 0 |  | h2, wb2 |
| ssj | 1.2.0 (2) | 16x32 | 0 / 22 | n.a. (side) | 0 |  | h2, wb2 |
| ssj | 1.2.1 (2) | 16x32 | 0 / 10 | n.a. (side) | 0 |  | h1, wb1 |
| ssj | 1.2.2 (2) | 16x32 | 0 / 23 | n.a. (side) | 0 |  | h2, wb2 |
| ssj | 1.2.3 (2) | 16x32 | 0 / 10 | n.a. (side) | 0 |  | h1, wb1 |
| ssj | 2.0.0 | 16x32 | 0 / 20 | yes | 0 |  | h2, wb2 |
| ssj | 2.0.1 | 16x32 | 3 / 25 | yes | 0 |  | h2, wb2 |
| ssj | 2.0.2 | 16x32 | 0 / 12 | yes | 0 |  | 1 chest skin covered |
| ssj | 2.0.3 | 16x32 | 0 / 13 | yes | 0 |  | h1, wb1 |
| ssj | 2.1.0 | 16x32 | 0 / 25 | n.a. (back) | 0 |  |  |
| ssj | 2.1.1 | 16x32 | 0 / 27 | n.a. (back) | 0 |  | h2, wb2; 1 white repainted; 1 chest skin covered |
| ssj | 2.1.2 | 16x32 | 0 / 26 | n.a. (back) | 0 |  | 1 white repainted |
| ssj | 2.1.3 | 16x32 | 0 / 27 | n.a. (back) | 0 |  | 1 white repainted |
| ssj | 2.2.0 (2) | 16x32 | 0 / 16 | n.a. (side) | 0 |  | h3, wb3; 3 chest skin covered |
| ssj | 2.2.1 (2) | 16x32 | 0 / 25 | n.a. (side) | 0 |  | h1, wb1; 2 white repainted |
| ssj | 2.2.2 (2) | 16x32 | 0 / 24 | n.a. (side) | 0 |  | h1, wb1; 1 white repainted |
| ssj | 2.2.3 (2) | 16x32 | 0 / 24 | n.a. (side) | 0 |  | h1, wb1 |
| ssj | 3.0.0 (4) | 32x32 | 0 / 16 | yes | 0 |  | h2, wb2; 2 white repainted |
| ssj | 3.0.1 (4) | 32x32 | 3 / 2 | yes | 0 |  | h2, wb1; 4 chest skin covered; knocked down: the box under the chin holds the hand on the ground, not the chest (reviewed at 4x) |
| ssj | 3.0.2 (4) | 32x32 | 0 / 0 n.a. | no (blocked) | 25 |  | h1, wb0; 1 white repainted |
| ssj | 3.0.3 (4) | 32x32 | 0 / 0 n.a. | no (blocked) | 32 |  | h1, wb1; 2 white repainted |
| ssj | 4.0.0 | 16x32 | 0 / 23 | yes | 0 |  | h2, wb2 |
| ssj | 4.0.1 | 16x32 | 3 / 23 | yes | 0 |  | h7, wb6; 2 chest skin covered |
| ssj | 4.0.2 | 16x32 | 0 / 23 | yes | 0 |  | h2, wb2 |
| ssj | 4.0.3 | 16x32 | 3 / 23 | yes | 0 |  | h6, wb5; 2 chest skin covered |
| ssj | 4.1.0 | 16x32 | 0 / 26 | n.a. (back) | 0 |  | h2, wb2 |
| ssj | 4.1.1 | 16x32 | 0 / 27 | n.a. (back) | 0 |  | h4, wb2 |
| ssj | 4.1.2 | 16x32 | 0 / 26 | n.a. (back) | 0 |  | h2, wb2 |
| ssj | 4.1.3 | 16x32 | 0 / 27 | n.a. (back) | 0 |  | h2, wb1 |
| ssj | 4.2.0 (2) | 16x32 | 0 / 11 | n.a. (side) | 0 |  | h1, wb1 |
| ssj | 4.2.1 (2) | 16x32 | 0 / 20 | n.a. (side) | 0 |  | h1, wb1 |
| ssj | 4.2.2 (2) | 16x32 | 0 / 11 | n.a. (side) | 0 |  | h1, wb1 |
| ssj | 4.2.3 (2) | 16x32 | 0 / 20 | n.a. (side) | 0 |  | h1, wb1 |
| ssj | 5.0.0 | 16x32 | 3 / 13 | yes | 0 |  | h3, wb3; 1 chest skin covered |
| ssj | 5.0.1 | 16x32 | 3 / 14 | yes | 0 |  | h2, wb2 |
| ssj | 5.0.2 | 16x32 | 3 / 16 | yes | 0 |  | h2, wb2 |
| ssj | 5.1.0 | 16x32 | 0 / 29 | n.a. (back) | 0 | yes | h2, wb2 |
| ssj | 5.1.1 | 16x32 | 0 / 24 | n.a. (back) | 0 |  | h3, wb2 |
| ssj | 5.1.2 | 16x32 | 0 / 26 | n.a. (back) | 0 |  | h3, wb2; 1 chest skin covered |
| ssj | 5.2.0 (2) | 32x32 | 0 / 22 | n.a. (side) | 0 |  | h5, wb5 |
| ssj | 5.2.1 (2) | 32x32 | 0 / 25 | n.a. (side) | 0 |  | h1, wb1; 1 white repainted |
| ssj | 5.2.2 (2) | 32x32 | 0 / 16 | n.a. (side) | 0 |  | h4, wb4 |
| ssj | 6.0.0 | 32x32 | 3 / 11 | yes | 0 |  | h3, wb2; 2 chest skin covered |
| ssj | 6.0.1 | 32x32 | 3 / 14 | yes | 0 |  | h3, wb3 |
| ssj | 6.0.2 | 32x32 | 3 / 27 | yes | 0 |  | h1, wb1 |
| ssj | 6.0.3 | 32x32 | 0 / 17 | no (blocked) | 0 |  | h2, wb2 |
| ssj | 6.1.0 | 32x32 | 0 / 20 | n.a. (back) | 0 | yes | h3, wb3; 1 white repainted |
| ssj | 6.1.1 | 32x32 | 0 / 26 | n.a. (back) | 0 |  | h3, wb2; 1 chest skin covered |
| ssj | 6.1.2 | 32x32 | 0 / 24 | n.a. (back) | 0 |  | h3, wb2; 1 chest skin covered |
| ssj | 6.1.3 | 32x32 | 0 / 21 | n.a. (back) | 0 | yes | h2, wb1 |
| ssj | 6.2.0 (2) | 32x32 | 0 / 20 | n.a. (side) | 0 |  | h4, wb4 |
| ssj | 6.2.1 (2) | 32x32 | 0 / 18 | n.a. (side) | 0 |  | h4, wb4 |
| ssj | 6.2.2 (2) | 32x32 | 0 / 19 | n.a. (side) | 0 |  | h2, wb2 |
| ssj | 6.2.3 (2) | 32x32 | 0 / 24 | n.a. (side) | 0 |  | h5, wb4; 1 chest skin covered |
| ssj | 7.0.0 | 32x32 | 3 / 11 | yes | 0 |  | h3, wb2; 2 chest skin covered |
| ssj | 7.0.1 | 32x32 | 3 / 14 | yes | 0 |  | h3, wb3 |
| ssj | 7.0.2 | 32x32 | 3 / 27 | yes | 0 |  | h1, wb1 |
| ssj | 7.0.3 | 32x32 | 0 / 17 | yes | 0 |  | h2, wb2 |
| ssj | 7.1.0 | 32x32 | 0 / 20 | n.a. (back) | 0 | yes | h3, wb3; 1 white repainted |
| ssj | 7.1.1 | 32x32 | 0 / 26 | n.a. (back) | 0 |  | h3, wb2; 1 chest skin covered |
| ssj | 7.1.2 | 32x32 | 0 / 24 | n.a. (back) | 0 |  | h3, wb2; 1 chest skin covered |
| ssj | 7.1.3 | 32x32 | 0 / 21 | n.a. (back) | 0 | yes | h2, wb1 |
| ssj | 7.2.0 (2) | 32x32 | 0 / 22 | n.a. (side) | 0 |  | h5, wb5 |
| ssj | 7.2.1 (2) | 32x32 | 0 / 21 | n.a. (side) | 0 |  | h1, wb1 |
| ssj | 7.2.2 (2) | 32x32 | 0 / 24 | n.a. (side) | 0 |  | h1, wb1; 1 white repainted |
| ssj | 7.2.3 (2) | 32x32 | 0 / 26 | n.a. (side) | 0 |  | h1, wb0; 1 white repainted; punch fist shows no wristband |
| ssj | 8.0.0 | 32x32 | 0 / 15 | yes | 0 |  | h3, wb2 |
| ssj | 8.0.1 | 32x32 | 3 / 18 | yes | 0 |  | h2, wb2 |
| ssj | 8.0.2 | 32x32 | 3 / 30 | yes | 0 |  | h1, wb1 |
| ssj | 8.0.3 | 32x32 | 3 / 23 | yes | 0 |  | h1, wb1 |
| ssj | 8.1.0 | 32x32 | 0 / 26 | n.a. (back) | 0 |  | h1, wb1; 1 white repainted |
| ssj | 8.1.1 | 32x32 | 0 / 22 | n.a. (back) | 0 |  | h6, wb5 |
| ssj | 8.1.2 | 32x32 | 0 / 16 | n.a. (back) | 0 |  | h2, wb2; 4 chest skin covered |
| ssj | 8.1.3 | 32x32 | 0 / 25 | n.a. (back) | 0 |  | h3, wb3 |
| ssj | 8.2.0 (2) | 32x32 | 0 / 27 | n.a. (side) | 0 |  | h4, wb4; 1 chest skin covered |
| ssj | 8.2.1 (2) | 32x32 | 0 / 19 | n.a. (side) | 0 |  | h5, wb3; 1 chest skin covered |
| ssj | 8.2.2 (2) | 32x32 | 0 / 16 | n.a. (side) | 0 |  | h4, wb3 |
| ssj | 8.2.3 (2) | 32x32 | 0 / 24 | n.a. (side) | 0 |  | h4, wb3; 1 chest skin covered |
| ssj | 9.0.0 (4) | 32x32 | 3 / 20 | yes | 0 |  | h2, wb2 |
| ssj | 9.0.1 (4) | 32x32 | 0 / 24 | yes | 0 |  | h2, wb2 |
| ssj | 9.0.2 (4) | 32x32 | 0 / 24 | yes | 0 |  | h2, wb2 |
| ssj | 9.0.3 (4) | 32x32 | 3 / 24 | yes | 0 |  | h2, wb2 |
| ssj | 11.0.0 (4) | 16x32 | 3 / 21 | yes | 0 |  | h2, wb2 |
| ssj | 11.0.1 (4) | 16x32 | 3 / 23 | yes | 0 |  | h8, wb8; 2 chest skin covered |
| ssj | 12.0.0 | 16x32 | 0 / 0 n.a. | no (blocked) | 0 |  | h5, wb2 |
| ssj | 12.0.1 | 16x32 | 0 / 0 n.a. | no (blocked) | 0 |  | h5, wb2 |
| ssj | 12.0.2 | 16x32 | 0 / 1 | no (blocked) | 0 |  | h5, wb2 |
| ssj | 12.0.3 | 16x32 | 0 / 0 n.a. | no (blocked) | 0 |  | h5, wb2 |
| ssj | 12.1.0 | 16x32 | 0 / 24 | n.a. (back) | 0 |  | h2, wb0 |
| ssj | 12.1.1 | 16x32 | 0 / 25 | n.a. (back) | 0 |  | h1, wb0 |
| ssj | 12.1.2 | 16x32 | 0 / 25 | n.a. (back) | 0 |  | h1, wb0 |
| ssj | 12.1.3 | 16x32 | 0 / 25 | n.a. (back) | 0 |  | h1, wb0 |
| ssj | 12.2.0 (2) | 32x32 | 0 / 17 | n.a. (side) | 0 |  | h3, wb3 |
| ssj | 12.2.1 (2) | 32x32 | 0 / 18 | n.a. (side) | 0 |  | h3, wb3 |
| ssj | 12.2.2 (2) | 32x32 | 0 / 18 | n.a. (side) | 0 |  | h3, wb3 |
| ssj | 12.2.3 (2) | 32x32 | 0 / 18 | n.a. (side) | 0 |  | h3, wb3 |
| ssj | 13.0.0 | 16x32 | 0 / 9 | yes | 0 |  | h3, wb2 |
| ssj | 13.0.1 | 16x32 | 0 / 22 | yes | 0 |  | h4, wb3; 1 chest skin covered |
| ssj | 13.0.2 | 16x32 | 0 / 9 | no (blocked) | 0 |  | h3, wb1 |
| ssj | 13.0.3 | 16x32 | 0 / 17 | yes | 0 |  | h2, wb1 |
| ssj | 13.1.0 | 16x32 | 0 / 26 | n.a. (back) | 0 |  | h1, wb1; 1 white repainted |
| ssj | 13.1.1 | 16x32 | 0 / 24 | n.a. (back) | 0 | yes | h2, wb2 |
| ssj | 13.1.2 | 16x32 | 0 / 26 | n.a. (back) | 0 |  | h1, wb1; 1 white repainted |
| ssj | 13.1.3 | 16x32 | 0 / 26 | n.a. (back) | 0 | yes | h2, wb2 |
| ssj | 13.2.0 (2) | 32x32 | 0 / 23 | n.a. (side) | 0 |  | h2, wb2 |
| ssj | 13.2.1 (2) | 32x32 | 0 / 14 | n.a. (side) | 0 | yes | h2, wb2 |
| ssj | 13.2.2 (2) | 32x32 | 0 / 29 | n.a. (side) | 0 |  | h2, wb2 |
| ssj | 13.2.3 (2) | 32x32 | 0 / 10 | n.a. (side) | 0 |  | h3, wb3; 1 white repainted |
| ssj | 16.0.0 | 32x32 | 3 / 20 | yes | 0 |  | h2, wb2 |
| ssj | 16.0.1 | 32x32 | 3 / 23 | yes | 0 |  | h7, wb5 |
| ssj | 16.0.2 | 32x32 | 3 / 20 | yes | 0 |  | h2, wb2; 1 white repainted |
| ssj | 16.0.3 | 32x32 | 3 / 19 | yes | 0 |  | h2, wb2 |
| ssj | 16.0.4 | 32x32 | 3 / 18 | yes | 0 |  | h2, wb2 |
| ssj | 16.0.5 (2) | 32x32 | 3 / 14 | yes | 0 |  | h5, wb5 |
| ssj | 16.1.0 | 32x32 | 0 / 25 | n.a. (back) | 0 |  | h5, wb5; 3 white repainted; 1 chest skin covered |
| ssj | 16.1.1 | 32x32 | 0 / 22 | n.a. (back) | 0 |  | h4, wb2; 1 white repainted; 1 chest skin covered |
| ssj | 16.1.2 | 32x32 | 0 / 18 | n.a. (back) | 0 |  | h1, wb0; 4 chest skin covered |
| ssj | 16.1.3 | 32x32 | 0 / 24 | n.a. (back) | 0 |  | h2, wb2 |
| ssj | 16.1.4 | 32x32 | 0 / 11 | n.a. (back) | 0 |  | h2, wb1 |
| ssj | 16.1.5 (2) | 32x32 | 0 / 28 | n.a. (back) | 0 |  | h2, wb2 |
| ssj | 16.2.0 (2) | 32x32 | 0 / 21 | n.a. (side) | 0 |  | h2, wb2 |
| ssj | 16.2.1 (2) | 32x32 | 0 / 17 | n.a. (side) | 0 |  | h3, wb3 |
| ssj | 16.2.2 (2) | 32x32 | 0 / 17 | n.a. (side) | 0 |  | h3, wb3 |
| ssj | 16.2.3 (2) | 32x32 | 0 / 24 | n.a. (side) | 0 |  | h3, wb0; 2 chest skin covered; hands at the face show no wristband |
| ssj | 16.2.4 (2) | 32x32 | 0 / 19 | n.a. (side) | 0 | yes | h3, wb1 |
| ssj | 16.2.5 (4) | 32x32 | 0 / 19 | n.a. (side) | 0 |  | h4, wb1; 2 chest skin covered |
| ssj | 18.0.0 | 16x32 | 0 / 6 | yes | 0 |  | h4, wb4 |
| ssj | 18.0.1 | 16x32 | 3 / 16 | yes | 0 |  | h1, wb1; 3 chest skin covered |
| ssj | 18.0.2 (5) | 16x32 | 0 / 28 | yes | 0 |  | crossed-arm block frame reads busy |
| ssj | 18.1.0 | 16x32 | 0 / 24 | n.a. (back) | 0 |  | h3, wb3; 1 white repainted |
| ssj | 18.1.1 | 16x32 | 0 / 23 | n.a. (back) | 0 |  | h1, wb1 |
| ssj | 18.1.2 (5) | 16x32 | 0 / 19 | n.a. (back) | 0 |  | h1, wb0; 2 chest skin covered |
| ssj | 18.2.0 (2) | 32x32 | 0 / 19 | n.a. (side) | 0 |  | h4, wb4 |
| ssj | 18.2.1 (2) | 32x32 | 0 / 26 | n.a. (side) | 0 |  | h2, wb2; 1 white repainted |
| ssj | 18.2.2 (10) | 32x32 | 0 / 29 | n.a. (side) | 0 |  | h1, wb1 |
| ssj | 20.0.0 (2) | 32x32 | 0 / 0 n.a. | no (blocked) | 1 |  | h10, wb8 |
| ssj | 20.0.1 (2) | 32x32 | 0 / 0 n.a. | no (blocked) | 1 |  | h10, wb8 |
| ssj | 20.0.2 (2) | 32x32 | 0 / 0 n.a. | no (blocked) | 1 |  | h10, wb8 |
| ssj | 20.0.3 (2) | 32x32 | 0 / 0 n.a. | no (blocked) | 2 |  | h10, wb8 |
| ssj | 20.1.0 (2) | 32x32 | 0 / 7 | n.a. (back) | 0 |  | h1, wb1 |
| ssj | 20.1.1 (2) | 32x32 | 0 / 7 | n.a. (back) | 0 |  | h1, wb1 |
| ssj | 20.1.2 (2) | 32x32 | 0 / 7 | n.a. (back) | 0 |  | h1, wb1 |
| ssj | 20.1.3 (2) | 32x32 | 0 / 7 | n.a. (back) | 0 |  | h1, wb1 |
| ssj | 21.0.0 (4) | 32x32 | 3 / 26 | yes | 0 |  | h2, wb2 |
| ssj | 21.0.1 (4) | 32x32 | 3 / 26 | yes | 0 |  | h2, wb2 |
| ssj | 21.0.2 (4) | 32x32 | 3 / 26 | yes | 22 |  | h2, wb2 |
| ssj | 21.0.3 (4) | 32x32 | 0 / 24 | yes | 33 |  | h2, wb2; 3 white repainted |
| ssj2 | 0.0.0 | 32x32 | 3 / 20 | yes | 0 |  | h2, wb2 |
| ssj2 | 0.0.1 | 32x32 | 3 / 24 | yes | 0 |  | h2, wb2 |
| ssj2 | 0.1.0 (2) | 32x32 | 0 / 31 | n.a. (back) | 0 |  | h2, wb2 |
| ssj2 | 0.2.0 (2) | 32x32 | 0 / 14 | n.a. (side) | 0 |  | h2, wb2 |
| ssj2 | 0.2.1 (2) | 32x32 | 0 / 14 | n.a. (side) | 0 |  | h2, wb2 |
| ssj2 | 1.0.0 | 16x32 | 3 / 15 | yes | 0 |  | h5, wb5 |
| ssj2 | 1.0.1 | 16x32 | 0 / 23 | yes | 0 |  | h2, wb2 |
| ssj2 | 1.0.2 | 16x32 | 0 / 16 | yes | 0 |  | h4, wb4 |
| ssj2 | 1.0.3 | 16x32 | 0 / 23 | yes | 0 |  | h2, wb2 |
| ssj2 | 1.1.0 | 16x32 | 0 / 23 | n.a. (back) | 0 |  | h2, wb2 |
| ssj2 | 1.1.1 | 16x32 | 0 / 26 | n.a. (back) | 0 |  | h2, wb2 |
| ssj2 | 1.1.2 | 16x32 | 0 / 25 | n.a. (back) | 0 |  | h2, wb2; 1 chest skin covered |
| ssj2 | 1.1.3 | 16x32 | 0 / 26 | n.a. (back) | 0 |  | h2, wb2 |
| ssj2 | 1.2.0 (2) | 16x32 | 0 / 22 | n.a. (side) | 0 |  | h2, wb2 |
| ssj2 | 1.2.1 (2) | 16x32 | 0 / 8 | n.a. (side) | 0 |  | h1, wb1 |
| ssj2 | 1.2.2 (2) | 16x32 | 0 / 25 | n.a. (side) | 0 |  | h2, wb2; 1 chest skin covered |
| ssj2 | 1.2.3 (2) | 16x32 | 0 / 8 | n.a. (side) | 0 |  | h1, wb1 |
| ssj2 | 2.0.0 | 16x32 | 3 / 19 | yes | 0 |  | h2, wb2 |
| ssj2 | 2.0.1 | 16x32 | 3 / 25 | yes | 0 |  | h2, wb2 |
| ssj2 | 2.0.2 | 16x32 | 3 / 15 | yes | 0 |  | 4 chest skin covered; 3 sparks blue |
| ssj2 | 2.0.3 | 16x32 | 0 / 13 | yes | 0 |  | h1, wb1 |
| ssj2 | 2.1.0 | 16x32 | 0 / 25 | n.a. (back) | 0 |  | 2 sparks blue |
| ssj2 | 2.1.1 | 16x32 | 0 / 25 | n.a. (back) | 0 |  | h2, wb2; 3 sparks blue |
| ssj2 | 2.1.2 | 16x32 | 0 / 18 | n.a. (back) | 0 |  | 3 sparks blue |
| ssj2 | 2.1.3 | 16x32 | 0 / 27 | n.a. (back) | 0 |  |  |
| ssj2 | 2.2.0 (2) | 16x32 | 0 / 16 | n.a. (side) | 0 |  | h3, wb3; 3 chest skin covered; 3 sparks blue |
| ssj2 | 2.2.1 (2) | 16x32 | 0 / 25 | n.a. (side) | 0 |  | h1, wb1; 2 white repainted; 1 sparks blue |
| ssj2 | 2.2.2 (2) | 16x32 | 0 / 23 | n.a. (side) | 0 |  | h1, wb1; 3 sparks blue |
| ssj2 | 2.2.3 (2) | 16x32 | 0 / 26 | n.a. (side) | 0 |  | h1, wb1 |
| ssj2 | 3.0.0 (4) | 32x32 | 0 / 16 | yes | 0 |  | h2, wb2 |
| ssj2 | 3.0.1 (4) | 32x32 | 3 / 2 | yes | 0 |  | h2, wb1; 4 chest skin covered; knocked down: the box under the chin holds the hand on the ground, not the chest (reviewed at 4x) |
| ssj2 | 3.0.2 (4) | 32x32 | 0 / 0 n.a. | no (blocked) | 25 |  | h1, wb0; 1 white repainted |
| ssj2 | 3.0.3 (4) | 32x32 | 0 / 0 n.a. | no (blocked) | 32 |  | h1, wb1; 2 white repainted |
| ssj2 | 4.0.0 | 32x32 | 3 / 20 | yes | 0 |  | h2, wb2; 6 sparks blue |
| ssj2 | 4.0.1 | 32x32 | 3 / 23 | yes | 0 |  | h2, wb2; 12 sparks blue |
| ssj2 | 4.0.2 | 32x32 | 3 / 22 | yes | 0 |  | h2, wb2; 6 sparks blue |
| ssj2 | 4.0.3 | 32x32 | 3 / 19 | yes | 0 |  | h2, wb2 |
| ssj2 | 4.1.0 | 32x32 | 0 / 31 | n.a. (back) | 0 |  | h2, wb2; 5 sparks blue |
| ssj2 | 4.1.1 | 32x32 | 0 / 28 | n.a. (back) | 0 |  | h2, wb2; 12 sparks blue |
| ssj2 | 4.1.2 | 32x32 | 0 / 33 | n.a. (back) | 0 |  | h2, wb2; 6 sparks blue |
| ssj2 | 4.1.3 | 32x32 | 0 / 29 | n.a. (back) | 0 |  | h2, wb2 |
| ssj2 | 4.2.0 (2) | 32x32 | 0 / 14 | n.a. (side) | 0 |  | h2, wb2; 2 sparks blue |
| ssj2 | 4.2.1 (2) | 32x32 | 0 / 18 | n.a. (side) | 0 |  | h3, wb3; 6 sparks blue |
| ssj2 | 4.2.2 (2) | 32x32 | 0 / 18 | n.a. (side) | 0 |  | h3, wb3; 3 sparks blue |
| ssj2 | 4.2.3 (2) | 32x32 | 0 / 18 | n.a. (side) | 0 |  | h3, wb3 |
| ssj2 | 5.0.0 | 16x32 | 3 / 13 | yes | 0 |  | h3, wb3; 1 chest skin covered |
| ssj2 | 5.0.1 | 16x32 | 3 / 17 | yes | 0 |  | h2, wb2 |
| ssj2 | 5.0.2 | 16x32 | 3 / 17 | yes | 0 |  | h2, wb2 |
| ssj2 | 5.1.0 | 16x32 | 0 / 29 | n.a. (back) | 0 | yes | h2, wb2 |
| ssj2 | 5.1.1 | 16x32 | 0 / 24 | n.a. (back) | 0 |  | h3, wb2 |
| ssj2 | 5.1.2 | 16x32 | 0 / 25 | n.a. (back) | 0 |  | h3, wb2 |
| ssj2 | 5.2.0 (2) | 32x32 | 0 / 22 | n.a. (side) | 0 |  | h5, wb5 |
| ssj2 | 5.2.1 (2) | 32x32 | 0 / 27 | n.a. (side) | 0 |  | h1, wb1; 1 white repainted |
| ssj2 | 5.2.2 (2) | 32x32 | 0 / 17 | n.a. (side) | 0 |  | h3, wb3; 1 white repainted |
| ssj2 | 6.0.0 | 32x32 | 3 / 8 | yes | 0 |  | h3, wb2; 2 chest skin covered |
| ssj2 | 6.0.1 | 32x32 | 3 / 20 | yes | 0 |  | h3, wb3 |
| ssj2 | 6.0.2 | 32x32 | 0 / 23 | yes | 0 |  | h1, wb1 |
| ssj2 | 6.0.3 | 32x32 | 0 / 15 | yes | 0 |  | h2, wb2 |
| ssj2 | 6.1.0 | 32x32 | 0 / 19 | n.a. (back) | 0 | yes | h3, wb3 |
| ssj2 | 6.1.1 | 32x32 | 0 / 22 | n.a. (back) | 0 |  | h3, wb3; 1 white repainted |
| ssj2 | 6.1.2 | 32x32 | 0 / 24 | n.a. (back) | 0 |  | h3, wb2; 2 chest skin covered |
| ssj2 | 6.1.3 | 32x32 | 0 / 16 | n.a. (back) | 0 | yes | h2, wb1 |
| ssj2 | 6.2.0 (2) | 32x32 | 0 / 21 | n.a. (side) | 0 |  | h4, wb4 |
| ssj2 | 6.2.1 (2) | 32x32 | 0 / 21 | n.a. (side) | 0 |  | h3, wb3; 1 white repainted; 1 sparks blue |
| ssj2 | 6.2.2 (2) | 32x32 | 0 / 19 | n.a. (side) | 0 |  | h2, wb2 |
| ssj2 | 6.2.3 (2) | 32x32 | 0 / 24 | n.a. (side) | 0 |  | h4, wb3; 1 white repainted; 1 chest skin covered; 3 sparks blue |
| ssj2 | 7.0.0 | 32x32 | 3 / 11 | yes | 0 |  | h3, wb2; 2 chest skin covered |
| ssj2 | 7.0.1 | 32x32 | 3 / 16 | yes | 0 |  | h3, wb3 |
| ssj2 | 7.0.2 | 32x32 | 0 / 23 | yes | 0 |  | h1, wb1 |
| ssj2 | 7.0.3 | 32x32 | 3 / 15 | yes | 0 |  | h2, wb2 |
| ssj2 | 7.1.0 | 32x32 | 0 / 22 | n.a. (back) | 0 | yes | h3, wb3 |
| ssj2 | 7.1.1 | 32x32 | 0 / 21 | n.a. (back) | 0 |  | h3, wb3 |
| ssj2 | 7.1.2 | 32x32 | 0 / 21 | n.a. (back) | 0 |  | h3, wb3; 1 chest skin covered |
| ssj2 | 7.1.3 | 32x32 | 0 / 16 | n.a. (back) | 0 | yes | h2, wb1 |
| ssj2 | 7.2.0 (2) | 32x32 | 0 / 22 | n.a. (side) | 0 |  | h5, wb5 |
| ssj2 | 7.2.1 (2) | 32x32 | 0 / 21 | n.a. (side) | 0 |  | h1, wb1 |
| ssj2 | 7.2.2 (2) | 32x32 | 0 / 24 | n.a. (side) | 0 |  | h1, wb1 |
| ssj2 | 7.2.3 (2) | 32x32 | 0 / 26 | n.a. (side) | 0 |  | h1, wb0; 1 white repainted; 1 sparks blue; punch fist shows no wristband |
| ssj2 | 8.0.0 | 32x32 | 0 / 10 | yes | 0 |  | h3, wb2 |
| ssj2 | 8.0.1 | 32x32 | 3 / 18 | yes | 0 |  | h2, wb2 |
| ssj2 | 8.0.2 | 32x32 | 3 / 28 | yes | 0 |  | h1, wb1 |
| ssj2 | 8.0.3 | 32x32 | 0 / 21 | yes | 0 |  | h2, wb2 |
| ssj2 | 8.1.0 | 32x32 | 0 / 28 | n.a. (back) | 0 |  | h1, wb1 |
| ssj2 | 8.1.1 | 32x32 | 0 / 22 | n.a. (back) | 0 |  | h6, wb6 |
| ssj2 | 8.1.2 | 32x32 | 0 / 17 | n.a. (back) | 0 |  | h2, wb1 |
| ssj2 | 8.1.3 | 32x32 | 0 / 22 | n.a. (back) | 0 |  | h3, wb3; 2 sparks blue |
| ssj2 | 8.2.0 (2) | 32x32 | 0 / 27 | n.a. (side) | 0 |  | h4, wb4; 1 chest skin covered |
| ssj2 | 8.2.1 (2) | 32x32 | 0 / 20 | n.a. (side) | 0 |  | h5, wb3; 1 chest skin covered; 1 sparks blue |
| ssj2 | 8.2.2 (2) | 32x32 | 0 / 16 | n.a. (side) | 0 |  | h4, wb3; 2 chest skin covered |
| ssj2 | 8.2.3 (2) | 32x32 | 0 / 24 | n.a. (side) | 0 |  | h4, wb3; 1 white repainted; 1 chest skin covered; 3 sparks blue |
| ssj2 | 9.0.0 (4) | 32x32 (set59 9.0.0) | 3 / 20 | yes | 0 |  | h2, wb2; set 58 has no 9.0.0: set 59 body with the set 58 head of 0.0.0 |
| ssj2 | 9.0.1 (4) | 32x64 enlarged (set59 9.0.1) | 0 / 24 | yes | 0 |  | h2, wb2; set 58 has no 9.0.1: set 59 body with the set 58 head of 0.0.0, aura ring 120 redrawn; record enlarged to 32x64 (dx -8, dy -56) to hold the head |
| ssj2 | 9.0.2 (4) | 32x64 enlarged (set59 9.0.2) | 0 / 24 | yes | 0 |  | h2, wb2; set 58 has no 9.0.2: set 59 body with the set 58 head of 0.0.0, aura ring 46 redrawn; record enlarged to 32x64 (dx -8, dy -56) to hold the head |
| ssj2 | 9.0.3 (4) | 32x64 enlarged (set59 9.0.3) | 3 / 27 | yes | 0 |  | h2, wb2; set 58 has no 9.0.3: set 59 body with the set 58 head of 0.0.0, aura ring 37 redrawn; 1 chest skin covered; record enlarged to 32x64 (dx -8, dy -56) to hold the head |
| ssj2 | 11.0.0 (4) | 32x64 enlarged (set59 11.0.0) | 3 / 21 | yes | 0 |  | h2, wb2; set 58 has no 11.0.0: set 59 body with the set 58 head of 0.0.0; record enlarged to 32x64 (dx -8, dy -56) to hold the head |
| ssj2 | 11.0.1 (4) | 32x64 enlarged (set59 11.0.1) | 3 / 24 | yes | 0 |  | h8, wb8; set 58 has no 11.0.1: set 59 body with the set 58 head of 0.0.0; 6 white repainted; 2 chest skin covered; record enlarged to 32x64 (dx -7, dy -56) to hold the head |
| ssj2 | 12.0.0 | 32x32 enlarged (set59 12.0.0) | 0 / 0 n.a. | no (blocked) | 0 |  | h5, wb2; set 58 has no 12.0.0: set 59 body with the set 58 head of 1.0.0; record enlarged to 32x32 (dx -8, dy -24) to hold the head |
| ssj2 | 12.0.1 | 32x32 enlarged (set59 12.0.1) | 0 / 0 n.a. | no (blocked) | 0 |  | h5, wb2; set 58 has no 12.0.1: set 59 body with the set 58 head of 1.0.0; 2 sparks blue; record enlarged to 32x32 (dx -8, dy -24) to hold the head |
| ssj2 | 12.0.2 | 32x32 enlarged (set59 12.0.2) | 0 / 1 | no (blocked) | 0 |  | h5, wb2; set 58 has no 12.0.2: set 59 body with the set 58 head of 1.0.0; record enlarged to 32x32 (dx -8, dy -24) to hold the head |
| ssj2 | 12.0.3 | 32x32 enlarged (set59 12.0.3) | 0 / 0 n.a. | no (blocked) | 0 |  | h5, wb2; set 58 has no 12.0.3: set 59 body with the set 58 head of 1.0.0; 2 sparks blue; record enlarged to 32x32 (dx -8, dy -24) to hold the head |
| ssj2 | 12.1.0 | 32x32 enlarged (set59 12.1.0) | 0 / 24 | n.a. (back) | 0 |  | h2, wb0; set 58 has no 12.1.0: set 59 body with the set 58 head of 1.1.0; record enlarged to 32x32 (dx -8, dy -24) to hold the head |
| ssj2 | 12.1.1 | 32x32 enlarged (set59 12.1.1) | 0 / 25 | n.a. (back) | 0 |  | h1, wb0; set 58 has no 12.1.1: set 59 body with the set 58 head of 1.1.0; 2 sparks blue; record enlarged to 32x32 (dx -8, dy -24) to hold the head |
| ssj2 | 12.1.2 | 32x32 enlarged (set59 12.1.2) | 0 / 25 | n.a. (back) | 0 |  | h1, wb0; set 58 has no 12.1.2: set 59 body with the set 58 head of 1.1.0; 2 sparks blue; record enlarged to 32x32 (dx -8, dy -24) to hold the head |
| ssj2 | 12.1.3 | 32x32 enlarged (set59 12.1.3) | 0 / 25 | n.a. (back) | 0 |  | h1, wb0; set 58 has no 12.1.3: set 59 body with the set 58 head of 1.1.0; 2 sparks blue; record enlarged to 32x32 (dx -8, dy -24) to hold the head |
| ssj2 | 12.2.0 (2) | 32x64 enlarged (set59 12.2.0) | 0 / 17 | n.a. (side) | 0 |  | h3, wb3; set 58 has no 12.2.0: set 59 body with the set 58 head of 5.2.1; 2 white repainted; record enlarged to 32x64 (dx -8, dy -56) to hold the head |
| ssj2 | 12.2.1 (2) | 32x64 enlarged (set59 12.2.1) | 0 / 15 | n.a. (side) | 0 |  | h3, wb3; set 58 has no 12.2.1: set 59 body with the set 58 head of 5.2.1; 2 white repainted; record enlarged to 32x64 (dx -8, dy -56) to hold the head |
| ssj2 | 12.2.2 (2) | 32x64 enlarged (set59 12.2.2) | 0 / 15 | n.a. (side) | 0 |  | h3, wb3; set 58 has no 12.2.2: set 59 body with the set 58 head of 5.2.1; 2 white repainted; record enlarged to 32x64 (dx -8, dy -56) to hold the head |
| ssj2 | 12.2.3 (2) | 32x64 enlarged (set59 12.2.3) | 0 / 15 | n.a. (side) | 0 |  | h3, wb3; set 58 has no 12.2.3: set 59 body with the set 58 head of 5.2.1; 2 white repainted; record enlarged to 32x64 (dx -8, dy -56) to hold the head |
| ssj2 | 13.0.0 | 16x32 | 0 / 9 | yes | 0 |  | h2, wb2 |
| ssj2 | 13.0.1 | 16x32 | 0 / 22 | yes | 0 |  | h3, wb2; 2 white repainted |
| ssj2 | 13.0.2 | 16x32 | 0 / 14 | yes | 0 |  | h2, wb2 |
| ssj2 | 13.0.3 | 16x32 | 3 / 16 | yes | 0 |  | h2, wb2; 1 white repainted |
| ssj2 | 13.1.0 | 16x32 | 0 / 26 | n.a. (back) | 0 |  | h1, wb1 |
| ssj2 | 13.1.1 | 16x32 | 0 / 27 | n.a. (back) | 0 | yes | h2, wb2 |
| ssj2 | 13.1.2 | 16x32 | 0 / 24 | n.a. (back) | 0 |  | h1, wb1 |
| ssj2 | 13.1.3 | 16x32 | 0 / 28 | n.a. (back) | 0 | yes | h2, wb2 |
| ssj2 | 13.2.0 (2) | 32x32 | 0 / 23 | n.a. (side) | 0 |  | h3, wb3; 1 white repainted |
| ssj2 | 13.2.1 (2) | 32x32 | 0 / 13 | n.a. (side) | 0 | yes | h2, wb2 |
| ssj2 | 13.2.2 (2) | 32x32 | 0 / 29 | n.a. (side) | 0 |  | h2, wb2 |
| ssj2 | 13.2.3 (2) | 32x32 | 0 / 10 | n.a. (side) | 0 |  | h3, wb3 |
| ssj2 | 16.0.0 | 32x32 | 3 / 20 | yes | 0 |  | h2, wb2 |
| ssj2 | 16.0.1 | 32x32 | 3 / 22 | yes | 0 |  | h4, wb4; 1 chest skin covered |
| ssj2 | 16.0.2 | 32x32 | 0 / 20 | yes | 0 |  | h2, wb2; 1 white repainted; 1 chest skin covered |
| ssj2 | 16.0.3 | 32x32 | 3 / 19 | yes | 0 |  | h2, wb2 |
| ssj2 | 16.0.4 | 32x32 | 0 / 19 | yes | 0 |  | h2, wb2 |
| ssj2 | 16.0.5 (2) | 32x32 | 3 / 14 | yes | 0 |  | h5, wb5 |
| ssj2 | 16.1.0 | 32x32 | 0 / 25 | n.a. (back) | 0 |  | h5, wb5; 2 white repainted; 1 chest skin covered |
| ssj2 | 16.1.1 | 32x32 | 0 / 22 | n.a. (back) | 0 |  | h4, wb2; 1 white repainted |
| ssj2 | 16.1.2 | 32x32 | 0 / 17 | n.a. (back) | 0 |  |  |
| ssj2 | 16.1.3 | 32x32 | 0 / 24 | n.a. (back) | 0 |  | h2, wb2; 1 sparks blue |
| ssj2 | 16.1.4 | 32x32 | 0 / 11 | n.a. (back) | 0 |  | h1, wb0 |
| ssj2 | 16.1.5 (2) | 32x32 | 0 / 28 | n.a. (back) | 0 |  | h2, wb2; 3 sparks blue |
| ssj2 | 16.2.0 (2) | 32x32 | 0 / 21 | n.a. (side) | 0 |  | h2, wb2 |
| ssj2 | 16.2.1 (2) | 32x32 | 0 / 15 | n.a. (side) | 0 |  | h3, wb3 |
| ssj2 | 16.2.2 (2) | 32x32 | 0 / 17 | n.a. (side) | 0 |  | h3, wb3 |
| ssj2 | 16.2.3 (2) | 32x32 | 0 / 24 | n.a. (side) | 0 |  | h2, wb0; hands at the face show no wristband |
| ssj2 | 16.2.4 (2) | 32x32 | 0 / 18 | n.a. (side) | 0 | yes | h3, wb1 |
| ssj2 | 16.2.5 (4) | 32x32 | 0 / 15 | n.a. (side) | 0 |  | h5, wb2 |
| ssj2 | 18.0.0 | 16x32 | 0 / 6 | yes | 0 |  | h4, wb4 |
| ssj2 | 18.0.1 | 16x32 | 0 / 13 | yes | 0 |  | h1, wb1 |
| ssj2 | 18.0.2 (5) | 16x32 | 3 / 29 | yes | 0 |  | 2 chest skin covered; crossed-arm block frame reads busy |
| ssj2 | 18.1.0 | 16x32 | 0 / 20 | n.a. (back) | 0 |  | h3, wb3 |
| ssj2 | 18.1.1 | 16x32 | 0 / 24 | n.a. (back) | 0 |  | h1, wb1 |
| ssj2 | 18.1.2 (5) | 16x32 | 0 / 19 | n.a. (back) | 0 |  | h1, wb0 |
| ssj2 | 18.2.0 (2) | 32x32 | 0 / 22 | n.a. (side) | 0 |  | h4, wb4; 2 chest skin covered |
| ssj2 | 18.2.1 (2) | 32x32 | 0 / 26 | n.a. (side) | 0 |  | h2, wb2 |
| ssj2 | 18.2.2 (10) | 32x32 | 0 / 29 | n.a. (side) | 0 |  | h1, wb1 |
| ssj2 | 20.0.0 (2) | 32x32 (set59 20.0.0) | 0 / 0 n.a. | no (blocked) | 0 |  | h10, wb8; set 58 has no 20.0.0: set 59 body with the set 58 head of 16.0.5; 1 white repainted |
| ssj2 | 20.0.1 (2) | 32x32 (set59 20.0.1) | 0 / 0 n.a. | no (blocked) | 0 |  | h10, wb8; set 58 has no 20.0.1: set 59 body with the set 58 head of 16.0.5; 1 white repainted |
| ssj2 | 20.0.2 (2) | 32x32 (set59 20.0.2) | 0 / 0 n.a. | no (blocked) | 0 |  | h10, wb8; set 58 has no 20.0.2: set 59 body with the set 58 head of 16.0.5; 1 white repainted |
| ssj2 | 20.0.3 (2) | 32x32 (set59 20.0.3) | 0 / 0 n.a. | no (blocked) | 0 |  | h10, wb8; set 58 has no 20.0.3: set 59 body with the set 58 head of 16.0.5; 1 white repainted |
| ssj2 | 20.1.0 (2) | 32x64 enlarged (set59 20.1.0) | 0 / 25 | n.a. (back) | 0 |  | h1, wb1; set 58 has no 20.1.0: set 59 body with the set 58 head of 13.1.2; record enlarged to 32x64 (dx -8, dy -56) to hold the head |
| ssj2 | 20.1.1 (2) | 32x64 enlarged (set59 20.1.1) | 0 / 25 | n.a. (back) | 0 |  | h1, wb1; set 58 has no 20.1.1: set 59 body with the set 58 head of 13.1.2; record enlarged to 32x64 (dx -8, dy -56) to hold the head |
| ssj2 | 20.1.2 (2) | 32x64 enlarged (set59 20.1.2) | 0 / 25 | n.a. (back) | 0 |  | h1, wb1; set 58 has no 20.1.2: set 59 body with the set 58 head of 13.1.2; record enlarged to 32x64 (dx -8, dy -56) to hold the head |
| ssj2 | 20.1.3 (2) | 32x64 enlarged (set59 20.1.3) | 0 / 25 | n.a. (back) | 0 |  | h1, wb1; set 58 has no 20.1.3: set 59 body with the set 58 head of 13.1.2; record enlarged to 32x64 (dx -8, dy -56) to hold the head |
| ssj2 | 21.0.0 (4) | 32x64 enlarged (set59 21.0.0) | 3 / 26 | yes | 0 |  | h2, wb2; set 58 has no 21.0.0: set 59 body with the set 58 head of 2.0.0; record enlarged to 32x64 (dx -8, dy -56) to hold the head |
| ssj2 | 21.0.1 (4) | 32x32 (set59 21.0.1) | 3 / 26 | yes | 0 |  | h2, wb2; set 58 has no 21.0.1: set 59 body with the set 58 head of 2.0.0, hair dimmed like set 59 21.x.1 |
| ssj2 | 21.0.2 (4) | 32x32 (set59 21.0.2) | 3 / 26 | yes | 22 |  | h2, wb2; set 58 has no 21.0.2: base head kept (the revert ends in base form) |
| ssj2 | 21.0.3 (4) | 32x32 (set59 21.0.3) | 0 / 24 | yes | 33 |  | h2, wb2; set 58 has no 21.0.3: base head kept (the revert ends in base form); 3 white repainted |

## 10. Animation table

I made and reviewed one strip and one GIF for each (form, anim, dir): 72 for base, 68 for SSJ and 68 for SSJ2. Each verdict cell covers dirs 0-3 of that form. The "seen" and "fixed" notes apply to all forms unless they name a form.

| Anim | Frames per dir | Seen in the strips | Fixed | base | ssj | ssj2 |
|---|---|---|---|---|---|---|
| 0 | 2 | idle; SSJ2 0.2.0 keeps the Rage stance (arm out, fist forward) and the set 58 32x32 record | none needed after the new method | d0-3 ok | d0-3 ok | d0-3 ok |
| 1 | 4 | run; wide sash on run frames follows the wide torso; SSJ hair shine showed purple dots | shine blobs ringed by hair join the head (no purple in hair) | d0-3 ok | d0-3 ok | d0-3 ok |
| 2 | 4 | hit; SSJ hair shine showed purple dots | shine blob rule | d0-3 ok | d0-3 ok | d0-3 ok |
| 3 | 4 | knocked down; legs had turned skin, 3.0.1 chest box holds the hand | lying rule puts boots at the far end; 3.0.1 exception | d0-3 ok | d0-3 ok | d0-3 ok |
| 4 | 4 | SSJ2 sparks; one spark on the hair rim was skin; base and SSJ fine | small light parts with an open side next to hair are sparks; all sparks blue 191 with white 2 core | d0-3 ok | d0-3 ok | d0-3 ok |
| 5 | 3 | guard; 5.x.2 glove white dots read as an arc (hollow fist); back 5.1.0 knee and collar | short arcs need an open rim; PART_HINTS 5.1.0; SSJ2 5.0.1, 5.0.2, 5.2.1, 5.2.2, 5.3.1 have wristbands | d0-3 ok | d0-3 ok | d0-3 ok |
| 6 | 4 | attack arcs had turned skin or brown; back 6.1.0 and 6.1.3 torso skin | long, edged and open arcs stay white; PART_HINTS 6.1.0, 6.1.3 | d0-3 ok | d0-3 ok | d0-3 ok |
| 7 | 4 | as anim 6; 7.2.1 streak through the arm | arc rules keep the 15 px streak white; PART_HINTS 7.1.0, 7.1.3 | d0-3 ok | d0-3 ok | d0-3 ok |
| 8 | 4 | ground arcs had turned brown, 8.1.2 and 8.2.2 arcs skin | arc rules | d0-3 ok | d0-3 ok | d0-3 ok |
| 9 | 4 | transform; SSJ aura frames had purple hands and grey boot edges (aura enclosed the body); SSJ2 stand-in heads | head mask no longer swallows armor inside the aura; SSJ2 head placed by the eyes, aura ring redrawn | d0-3 ok | d0-3 ok | d0-3 ok, stand-in head |
| 11 | 2 | arms up; skin arms merged with the face; SSJ2 stand-in | arm pixels next to face skin get the 23 outline | d0-3 ok | d0-3 ok | d0-3 ok, stand-in head |
| 12 | 4 | lying; feet and hands sorted by the lying rule; SSJ2 stand-in head is an upright set 58 head | lying rule | d0-3 ok | d0-3 ok | d0-3 ok, stand-in head (my look) |
| 13 | 4 | walk; back 13.1.1 and 13.1.3 far hand read as boot; side 13.2.1 and 13.3.1 collar read as hand | PART_HINTS 13.1.1, 13.1.3, 13.2.1, 13.3.1 | d0-3 ok | d0-3 ok | d0-3 ok |
| 14 | 5 | sit (base only); hands on the knees read as boots | PART_HINTS 14.0.3, 14.0.4 | d0-3 ok | none | none |
| 16 | 7 | jump and kick; kick boot read as hand (skin leg); arcs 16.0.2 and 16.1.4 had turned brown or skin | PART_HINTS 16.2.4, 16.3.4; arc rules | d0-3 ok | d0-3 ok | d0-3 ok |
| 17 | 2 | dead with halo (base only) | none | d0-3 ok | none | none |
| 18 | 7 | 18.0.2 crossed-arm frame had purple in the face | face trim pixels join the head | d0-3 ok | d0-3 ok | d0-3 ok |
| 20 | 4 | flying; raised fist was a hollow grey hook and the arm purple; dir 1 and 3 red pixels | flying rules: boots by the feet, raised arm skin to the shoulder, cuff wristband, sash only at the waist | d0-3 ok | d0-3 ok | d0-3 ok, stand-in head |
| 21 | 4 | revert; SSJ2 frame 1 showed a bright head where set 59 dims the hair; frames 2-3 keep the base head | 21.x.1 hair dimmed one step like set 59 | none | d0-3 ok | d0-3 ok, stand-in head |

GIF paths: art\anim\<form>\<form>_aNN_dD.gif for each anim and dir above. There are 72 base, 68 SSJ and 68 SSJ2 GIFs. art\anim\compare\ has 13 GIFs: compare_gi_base_a09_d0, compare_gi_ssj_a09_d0, compare_gi_ssj_a21_d0, compare_gi_ssj2_a21_d0, compare_set56_a09_d0, compare_set59_a09_d0, compare_set59_a21_d0, compare_set60_a09_d0, compare_set61_a21_d0, compare_set129_a09_d0, compare_set130_a21_d0, compare_set137_a09_d0, compare_set140_a21_d0 (all .gif).

## 11. TDD evidence

- I updated the art tests after I wrote the v3 code, not before it. Two mutations on a copy of gi base 0.0.0 show that the new tests can fail:
  - One white pixel (index 2) in the legs made test_no_armor_white_below_the_chin fail ("gi_base set56 0.0.0: [(8, 2)]").
  - A 3x2 skin patch on the chest made test_torso_skin_recomputed_from_png fail ("8 > 3").
  - I restored the frame, and the suite passed again.
- Final run: py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v. Result: 29 tests OK, 2 skipped (part 2 patch tests).
- New or changed tests:
  - test_gi_frames_keep_record_geometry: the same-form record, or a larger legal size that holds the original box.
  - test_gi_covers_every_key: the keys of sets 56 and 59, with counts 162, 159 and 159.
  - test_manifest_checks_pass_or_have_a_reason.
  - test_torso_skin_recomputed_from_png.
  - test_no_armor_white_below_the_chin.
  - The allowed indices now include 191 (spark blue).

## 12. Concerns

1. **Part 2 geometry.** The gi SSJ2 set follows the set 59 key layout but uses set 58 records where they exist. It also has 22 enlarged records (32x32 or 32x64). This conflicts with the Ruling 18 wording "keep w and h equal to the record it replaces". Direction k allows the next legal size. Part 2 needs those record sizes, 159 new frame headers and a VRAM check.
2. **Stand-in heads.** 30 SSJ2 frames have a set 58 head on a set 59 body. The lying anim 12 frames look the weakest (section 7).
3. **SSJ2 anim 9** is probably not played, because the SSJ to SSJ2 step plays anim 9 on the SSJ set. I made it anyway, with the SSJ2 head and the aura.
4. **Small fists** often get a 1 px wristband (only the 72 outline), because the glove is only 2-3 px.
5. **Mouth exemption.** This differs from the advisor's advice. A light pixel between face skin on its row passes the Ruling 26 check only at or above the chin row. The advisor asked for "inside the head mask" as well. I did not add that condition, because some mouth pixels are outside the mask. An audit found 0 exempted pixels below the chin.
6. **Ruling 25 check.** The check counts skin pixels in the box under the chin. It does not measure V depth. The depth comes from the fixed V shape (3 px, 2 rows). In some front frames, the V touches arm or face skin, so the count leaves it out (V "yes" with 0 chest skin).
7. **RE-BIBLE decision row.** Ruling 27 supersedes the row "Gi base hair: the shorter armor hair on the Demon Clothes body (set 53)". I did not edit the final decisions table.
8. **Animation timing** is not traced for anims other than 0, 1 and 16. The GIFs use 167 ms per frame.
9. **Report location.** The harness blocked report .md files from this task, so this report exists only in this message. docs\tasks\2026-10-16-task-5-gi-art\task-5-report.md is an old draft that shows directions as "In progress". The coordinator should replace it or delete it.

---

## Fix round 1 (2026-10-17)

This section answers docs\ledger\task-5-fix-r1.md. All 6 defects have a fix. Defect 1 has one item that I kept on evidence (the navy band).

> [!NOTE]
> Before and after crops at 10x: archive\2026-10-18-art-review-renders\fix_r1_before_after.png. The sheet has 36 pairs, one for each fixed frame header that changed, in all three forms. "Before" is the round 0 output (copies in archive\2026-10-17-gi-art-rounds\art-work\r0_gi_*).

### Status per defect

| # | Frames | Status | What changed |
|---|---|---|---|
| 1a | 18.0.2-18.0.6 navy band, all forms | Kept, with evidence | The band is the lit hair of the original, not sleeves. See below. |
| 1b | 18.0.2-18.0.6 lavender block, all forms | Fixed | Hands. The lit frames now take their parts from the unlit frame 18.0.1. The block is two skin fists at the belly with blue wristbands. No lavender is left. |
| 1c | 18.1.2-18.1.6 back waist, all forms | Fixed | Red sash at the waist, gi purple above it. The white part at the lower right is the far boot (raised). It is now a brown boot, not a hand. |
| 2 | 12.0.x, all forms | Fixed | Each fist has a dark outline (23) and a blue wristband below it (195 fill, 72 edge). In SSJ2 the right fist is behind the hair in the original, so only its band shows. |
| 3 | SSJ2 12.2.x (shared by 12.3.x) | Fixed | The set 58 head turns 90 degrees. The hair lies along the ground. The neck join has a dark outline. The record changes from 32x64 to 64x32 (dx -28, dy -24). |
| 4 | SSJ2 11.0.1 (and its dirs) | Fixed | The hair rows between the brow and the top are compressed, so the hair top is 1 px above the fists. The fists sit on the hair top with a dark rim. The face shows between the arms. |
| 5 | SSJ2 20.0.x and 20.2.x | Fixed | The head moves up 2 px. The raised arm and fist are drawn in front of the hair. A torso shows below the chin (skin neck, purple gi, navy rim). |
| 6 | 7.2.3 and 16.2.3, all forms | Fixed | 16.2.3: a band on both forearms. 7.2.3: the punch fist is hidden, so the band (195 over 72) sits at the forearm end, image pixels (6,19) and (6,20), through FIXES. The white speed line in front of it stays white. Round 0 had painted it skin. |

### Defect 1a: why the navy band stays

The band is index 211 in the original set 56 frame 18.0.2, rows 9-13 around the face. The evidence:

- In the unlit frame set 56 18.0.1, the same pixels are 1 (black hair).
- In set 59 and set 58 18.0.2, the same pixels are gold hair (20, 37, 46).
- So 211 there is the black hair, lit by the charge glow. The gi head keeps the original head, as Rulings 25-27 require.
- The gi output keeps these pixels the same as the original.

If I want the lit hair to read darker, the change is one map in gi_art.py (LIT_HEAD). I did not make that change without a ruling.

### Rule changes in gi_art.py

These are general rules, not per-frame edits. Only 7.2.3 uses FIXES.

1. **Lit frames (anim 18, index 2 and up).** `unlit_probe` reads the body parts from frame 1 of the same dir. Then the frame goes through the normal armor-to-gi pass. The lit head stays as it is.
2. **Hidden forearm band.** When no forearm touches a glove, the band crosses the end that faces the shoulder. The band is at most half the fist. Round 0 had no band there.
3. **Fist outline.** A fist drawn with index 12 on its rim (fists over the head) uses that rim as the outline (23).
4. **Head mask.** Pupils include black pixels next to face skin. A glove at the chin and a small fist row against the hair are no longer counted as head.
5. **Speed lines.** A straight white line of 3 px or more with an open rim stays white. This changes only 7.2.3 in all forms.
6. **Stand-in heads (SSJ2).** HEAD_TURN for lying frames, HEAD_NUDGE for flying frames, and the arms-up compression for anim 11. Fists outside the head are kept in front.
7. **PART_HINTS.** 3 new entries for the anim 18 back view (boot, chest).

Frames that differ from round 0: 211 frame headers (base 80, Super Saiyan 66, Super Saiyan 2 65). Most of the changes outside the 6 defects are new wristbands and leftover gray that is now outline or purple. I looked at before and after sheets of all of them at 4x. Three regressions came from the new band rule (6.1.2, 7.1.1 and 7.1.2 lost their fist to a full band). I fixed them with the half-fist cap.

### Checks

- `py -3 -I scripts\permanent\art\gi_art.py all`: base 162 frames, Super Saiyan 159, Super Saiyan 2 159, failing 0 in each. The only check exception is still 3.0.1 in all forms.
- Unit tests: 29 ran, OK, 2 skipped.
- Strips and GIFs under art\anim\ and the contact sheets are new (all made by the `all` run). I read the anim 12 and 18 strips again.
- hud_z2.png, hud_z2_usable.bin and hud_z2_dim.bin are unchanged (timestamp 22:22).
- No ROM build, no git, nothing written under data\. No em or en dashes and no byte order mark in the changed files.

### Concerns

1. **Wide rule changes.** The glove and mask rules changed 211 frames. I reviewed them at 4x, but not one by one at 10x.
2. **Turned head (SSJ2 12.2.x).** The turned set 58 head is a stand-in. The join is a plain dark outline. Part 2 must allow a 64x32 record for this frame.
3. **SSJ2 12.0.x right fist.** It stays behind the hair, as in the original set 58. Only its wristband shows.
4. **7.2.3** has only the band, because the original frame shows no fist.

## Purple-arm fix (my review 2026-10-17)

**Fault.** The gi is sleeveless, but many arms were purple. The old rule painted skin only in a 3 px corridor from the glove to a guessed shoulder. It missed arms that cross the torso (SSJ2 0.2.0, 0.2.1, 6.2.2), arms whose fist the classifier called chest, and arms with no glove in view.

**New rules in scripts\permanent\art\gi_art.py.**

1. Sleeve flood: from each glove, the suit joined to it within ARM_REACH (10) steps is arm. A torso-wide suit block (5x5 core plus 2 px) and the belly under the plate stay gi. In back views the arm stays beside the back plate.
2. One-pixel shine: a lone light pixel on the suit with no grey outline is a shine (chest). A shine beside a boot is the knee's (boot). An outlined lone pixel stays a fist.
3. The cuff faces the sleeve centroid when a sleeve exists.
4. ARM_SEEDS: suit islands that are arms with no glove in view (2.1.0, 2.1.2, 2.1.3, 13.1.0, 13.1.2, 16.1.3, 18.0.1-6, 18.1.1-6). An island over ARM_ISLAND_MAX (20 px) is never painted.
5. SHORT_REACH: the hunched poses 2.0.2, 2.0.3, 6.0.2 and 7.0.2 get a 3-step sleeve (forearm only). A full flood bared their small torso.
6. PART_HINTS added: 16.1.1 knee, 5.1.0 shoulder shine and far fist, 8.1.0 fist, 16.2.5 and 16.2.6 plate edge.
7. Outline: finish() paints each gi pixel beside bare arm skin dark outline 211, so a dark line parts the arm from the torso. chest_skin() ignores arm skin. The chest check counts 211 as gi.

**Checks.** New check `sleeve` = purple_forearms (the forearm pixels next to each wristband are not gi purple) + purple_arms (no arm pixel, shoulder to wristband, is gi purple). With the sleeve flood switched off it flagged 60 frames, among them my SSJ2 0.2.0, 0.2.1 and 6.2.2. Now: base 162, SSJ 159, SSJ2 159 frames, 0 failing on every check.

**By eye.** I looked at every changed frame of all three forms on original | before | after sheets (4x to 5x). I zoomed each doubtful frame to 8x-14x and checked the anim strips. Two more throwaway scans looked for misses the check cannot see: white parts classed as chest far from the neck, and detached purple suit islands above the waist. Their hits were reviewed one by one, and the arm cases became the seeds and hints above. I re-ran the island scan on the final art (87 hits) and viewed every hit again: all are belly, lower back, trouser or torso bits, none is an arm.

**Changed frames** (against the art before this round; the dark arm line touches almost every frame):

- Base (159): 0.0.0, 0.0.1, 0.1.0, 0.2.0, 0.2.1, 1.0.0, 1.0.1, 1.0.2, 1.0.3, 1.1.0, 1.1.1, 1.1.2, 1.1.3, 1.2.0, 1.2.1, 1.2.2, 1.2.3, 2.0.0, 2.0.1, 2.0.2, 2.0.3, 2.1.0, 2.1.1, 2.1.2, 2.1.3, 2.2.0, 2.2.1, 2.2.2, 2.2.3, 3.0.0, 3.0.1, 4.0.0, 4.0.1, 4.0.2, 4.0.3, 4.1.0, 4.1.1, 4.1.2, 4.1.3, 4.2.0, 4.2.1, 4.2.2, 4.2.3, 5.0.0, 5.0.1, 5.0.2, 5.1.0, 5.1.1, 5.1.2, 5.2.0, 5.2.1, 5.2.2, 6.0.0, 6.0.1, 6.0.2, 6.0.3, 6.1.0, 6.1.1, 6.1.2, 6.1.3, 6.2.0, 6.2.1, 6.2.2, 6.2.3, 7.0.0, 7.0.1, 7.0.2, 7.0.3, 7.1.0, 7.1.1, 7.1.2, 7.1.3, 7.2.0, 7.2.1, 7.2.2, 8.0.0, 8.0.1, 8.0.2, 8.0.3, 8.1.0, 8.1.1, 8.1.2, 8.1.3, 8.2.0, 8.2.1, 8.2.2, 8.2.3, 9.0.0, 9.0.1, 9.0.2, 9.0.3, 11.0.0, 11.0.1, 12.0.0, 12.0.1, 12.0.2, 12.0.3, 12.1.0, 12.1.1, 12.1.2, 12.1.3, 12.2.0, 12.2.1, 12.2.2, 12.2.3, 13.0.0, 13.0.1, 13.0.2, 13.0.3, 13.1.0, 13.1.1, 13.1.2, 13.1.3, 13.2.0, 13.2.1, 13.2.2, 13.2.3, 14.0.0, 14.0.1, 14.0.2, 14.0.3, 14.0.4, 16.0.0, 16.0.1, 16.0.2, 16.0.3, 16.0.4, 16.0.5, 16.1.0, 16.1.1, 16.1.2, 16.1.3, 16.1.4, 16.1.5, 16.2.0, 16.2.1, 16.2.2, 16.2.3, 16.2.4, 16.2.5, 17.0.0, 17.0.1, 18.0.0, 18.0.1, 18.0.2, 18.1.0, 18.1.1, 18.1.2, 18.2.0, 18.2.1, 18.2.2, 20.0.0, 20.0.1, 20.0.2, 20.0.3, 20.1.0, 20.1.1, 20.1.2, 20.1.3
- Super Saiyan (155): 0.0.0, 0.0.1, 0.1.0, 0.2.0, 0.2.1, 1.0.0, 1.0.1, 1.0.2, 1.0.3, 1.1.0, 1.1.1, 1.1.2, 1.1.3, 1.2.0, 1.2.1, 1.2.2, 1.2.3, 2.0.0, 2.0.1, 2.0.3, 2.1.0, 2.1.1, 2.1.2, 2.1.3, 2.2.0, 2.2.1, 2.2.2, 2.2.3, 3.0.0, 3.0.1, 4.0.0, 4.0.1, 4.0.2, 4.0.3, 4.1.0, 4.1.1, 4.1.2, 4.1.3, 4.2.0, 4.2.1, 4.2.2, 4.2.3, 5.0.0, 5.0.1, 5.0.2, 5.1.0, 5.1.1, 5.1.2, 5.2.0, 5.2.1, 5.2.2, 6.0.0, 6.0.1, 6.0.2, 6.0.3, 6.1.0, 6.1.1, 6.1.2, 6.1.3, 6.2.0, 6.2.1, 6.2.2, 6.2.3, 7.0.0, 7.0.1, 7.0.2, 7.0.3, 7.1.0, 7.1.1, 7.1.2, 7.1.3, 7.2.0, 7.2.1, 7.2.2, 8.0.0, 8.0.1, 8.0.2, 8.0.3, 8.1.0, 8.1.1, 8.1.2, 8.1.3, 8.2.0, 8.2.1, 8.2.2, 8.2.3, 9.0.0, 9.0.1, 9.0.2, 9.0.3, 11.0.0, 11.0.1, 12.0.0, 12.0.1, 12.0.2, 12.0.3, 12.1.0, 12.1.1, 12.1.2, 12.1.3, 12.2.0, 12.2.1, 12.2.2, 12.2.3, 13.0.0, 13.0.1, 13.0.2, 13.0.3, 13.1.0, 13.1.1, 13.1.2, 13.1.3, 13.2.0, 13.2.1, 13.2.2, 13.2.3, 16.0.0, 16.0.1, 16.0.2, 16.0.3, 16.0.4, 16.0.5, 16.1.0, 16.1.1, 16.1.2, 16.1.3, 16.1.4, 16.1.5, 16.2.0, 16.2.1, 16.2.2, 16.2.3, 16.2.4, 16.2.5, 18.0.0, 18.0.1, 18.0.2, 18.1.0, 18.1.1, 18.1.2, 18.2.0, 18.2.1, 18.2.2, 20.0.0, 20.0.1, 20.0.2, 20.0.3, 20.1.0, 20.1.1, 20.1.2, 20.1.3, 21.0.0, 21.0.1, 21.0.2, 21.0.3
- Super Saiyan 2 (154): 0.0.0, 0.0.1, 0.1.0, 0.2.0, 0.2.1, 1.0.0, 1.0.1, 1.0.2, 1.0.3, 1.1.0, 1.1.1, 1.1.2, 1.1.3, 1.2.0, 1.2.1, 1.2.2, 1.2.3, 2.0.0, 2.0.1, 2.0.3, 2.1.0, 2.1.1, 2.1.2, 2.1.3, 2.2.0, 2.2.1, 2.2.2, 2.2.3, 3.0.0, 3.0.1, 4.0.0, 4.0.1, 4.0.2, 4.0.3, 4.1.0, 4.1.1, 4.1.2, 4.1.3, 4.2.0, 4.2.1, 4.2.2, 4.2.3, 5.0.0, 5.0.1, 5.0.2, 5.1.0, 5.1.1, 5.1.2, 5.2.0, 5.2.1, 5.2.2, 6.0.0, 6.0.1, 6.0.2, 6.0.3, 6.1.0, 6.1.1, 6.1.2, 6.1.3, 6.2.0, 6.2.1, 6.2.2, 6.2.3, 7.0.0, 7.0.1, 7.0.2, 7.0.3, 7.1.0, 7.1.1, 7.1.2, 7.1.3, 7.2.0, 7.2.1, 7.2.2, 8.0.0, 8.0.1, 8.0.2, 8.0.3, 8.1.0, 8.1.1, 8.1.2, 8.1.3, 8.2.0, 8.2.1, 8.2.2, 8.2.3, 9.0.0, 9.0.1, 9.0.2, 9.0.3, 11.0.0, 11.0.1, 12.0.0, 12.0.1, 12.0.2, 12.0.3, 12.1.0, 12.1.1, 12.1.2, 12.1.3, 12.2.0, 12.2.1, 12.2.2, 12.2.3, 13.0.0, 13.0.1, 13.0.2, 13.0.3, 13.1.0, 13.1.1, 13.1.2, 13.1.3, 13.2.0, 13.2.1, 13.2.2, 13.2.3, 16.0.0, 16.0.1, 16.0.2, 16.0.3, 16.0.4, 16.0.5, 16.1.0, 16.1.1, 16.1.3, 16.1.4, 16.1.5, 16.2.0, 16.2.1, 16.2.2, 16.2.3, 16.2.4, 16.2.5, 18.0.0, 18.0.1, 18.0.2, 18.1.0, 18.1.1, 18.1.2, 18.2.0, 18.2.1, 18.2.2, 20.0.0, 20.0.1, 20.0.2, 20.0.3, 20.1.0, 20.1.1, 20.1.2, 20.1.3, 21.0.0, 21.0.1, 21.0.2, 21.0.3

Total 468 frames.

**Outputs.**

- Before and after sheet: archive\2026-10-18-art-review-renders\fix_arms_before_after.png (every changed frame, rA before | after, 3x).
- Build: archive\builds\log2_poc_r2.gba = gohan_gi + ssj2_form + gohan_portraits, SHA-1 `b7bee5347f77de8ad490e2bb365c6eca9c674d8b`, logged in docs\build-log.md. builds\log2_poc.gba is unchanged (SHA-1 `345ae98c1145f669d936cad62cad8635467f3824`).
- Tests: 77 OK. gi_art.py all: 0 failing. hud_z2 files unchanged (22:22).

**My review needed.**

1. Small back views with a short torso (1.1.x walk in all forms): the arm takes about 3 px of the back. It reads as a swung arm, but it is the widest change.
2. Hurt pose 2.0.2 and 2.0.3: the source does not show where the arms are, so only the forearm is skin. Base 2.0.2 keeps a skin patch on the belly where the fist sits (there before, now a little larger).
3. Arms that cross the torso horizontally (18.0.0, 18.2.1, 18.2.2 and the guard poses) now show as a wide skin band with a dark line around it. This is my rule, but the band is 3-4 px tall.
4. SSJ 4.2.1 and 4.2.3: three hair-white pixels beside the raised fist stay purple (as before this round).
5. SSJ2 2.2.3: a one-pixel fist with a grey outline keeps its wristband (as before this round).

