# owner-0853-fixes report: one SSJ/SSJ2 gi body, golden torso per frame, pink strays, r11

Status: DONE, with concerns. Two points of the brief are not met as written: fix 1 point 5 (70 shared pairs differ in head pixels only, by the sash-minus-5 metric) and the stand-in rule for 9.x.3 and 11.x.1 (concern 1).

## SHIPPED

| Ask (brief) | Result |
|---|---|
| Fix 1: SSJ2 uses the gi SSJ body | Done in `gi_art.py`. 128 of 159 SSJ2 frames now carry the finished `gi_ssj` body with their own head and sparks on top. 31 frames keep their own body (list below). |
| Fix 1.3: R1/R2 on both or neither | Neither, on the shared frames. R1/R2 still run on the 31 own-body frames. Reason below. |
| Fix 1.4: SSJ2 golden idle slots | Byte for byte the goldens (test `test_golden_idle_slots_equal_goldens` passes). |
| Fix 2: golden torso per frame | Done for all forms. 157 a4 d1 i0 and i2 equal golden base d1 in the torso rows: 0 px differ, and identical by eye at 6x. |
| Fix 3: pink pixels | Done. No 239 or 240 in any of the 5 gi folders (test). |
| Tool: `rom_sheet.py --frames` | Done, with one deviation for dir 3 (concern 5). |
| Build r11 and export | `archive\builds\log2_poc_r11.gba` SHA-1 `77084b63dc815a53760c99ef0c10a090c9d8c754`. Tests 159 OK. Exports below. |

## PENDING and concerns (final, please look)

1. **CONFIRMED, deviation from the brief: two stand-in key groups keep their own body: 9.x.3 and 11.x.1.** The brief says that keys set 58 lacks take the gi SSJ body. On these two, the SSJ2 stand-in head sits 1 to 3 rows higher than the SSJ head. The SSJ body then showed a second V neck under the SSJ2 neck (11.0.1 at 10x: V, collar, then a second V). The existing chest check (Ruling 25) fails on the composite, so the rule keeps the own body there. The manifest note says "a second neck opening". All other stand-in keys (9.x.0-2, 11.x.0, 12.x, 20.x, 21.x) share the body.
2. **CONFIRMED: the r10 arm line leaves 128 SSJ2 frames.** R1/R2 change `golden_gi_ssj_d0` by 2 px ((22,12), (24,12)) and `d1` by 3 px ((20,11), (26,11), (22,12)). The base goldens change the same way. So R1/R2 may not run on the SSJ body, and the shared SSJ2 frames now show the SSJ body without the arm line that r10 added. R1/R2 now change 20 px in 11 own-body frames only (r10: 121 px in 67 frames): 1.1.1, 1.1.3, 2.0.1, 4.0.1, 4.0.2, 4.0.3, 4.1.3, 8.0.3, 13.0.1, 13.0.3, 9.x.3. They do not change 4.0.0 or 4.2.0, the two SSJ2 frames that took the golden torso.
3. **CONFIRMED: set 158 does not change.** For SSJ anim 4, frames 0 and 2 differ from the SSJ idle armor in the torso window by 2 px (d0), 24 px (d1) and 1 px (d2). The existing exact `torso_shift` test therefore gives them no golden torso. If I want a tolerance for d0 and d2, that is a rule change.
4. **LIKELY fine, please look: the golden torso now alternates in two animations.**
   - 157 front walk (1.0): frames 1 and 3 take the golden torso and its strap, frames 0 and 2 do not (the arms cross the chest there).
   - 159 ki charge front (4.0): frame 0 takes the golden torso; frames 1-3 take the strap rule. In the Rage set, frame 2 is not the frame 0 pose.
5. **CONFIRMED: the dir 3 premise of the tool brief is not true for every anim.** In sets 56, 59 and 157-159, anim 20 dir 3 has its own frame headers (no flip). In anims 9, 11 and 21 (and 14, 17 in sets 56 and 157), dir 3 is dir 2 again with no flip. `--frames` skips only a dir 3 record that reuses the dir 2 frame header, so it writes the anim 20 dir 3 frames. The header and RE-BIBLE row 354 say so. Frame PNGs are RGBA with color 0 transparent, at the record's own size.
6. **CONFIRMED: the pair metric reaches into the head.** "Rows from 5 above the sash down" includes face and hair pixels in crouched, attack and lying poses. After the fix, 70 shared pairs differ only in head pixels (details below). I did not get my 14 for "before": my count is 13 (method below; 3 sash variants and 2 folder pairs tried).
7. **LIKELY fine: shared frames take the SSJ effects.** Swoosh arcs and dust come with the SSJ body (set 59). Only the SSJ2 head mask and the blue sparks stay SSJ2's. For example, the 6.1.1 arc now crosses the hair top a little differently.
8. **CONFIRMED, no effect: the transplant reports a new offset for 4 flagged frames** (12.2.0-12.2.3 and their d3). Flagged frames get no head swap, so no pixel changes from this. All status counts are the same as r10: ok 93, ok+grow 38, ok+shift1 10, flag 7, ok+shift2 5, ok+shift1+grow 4, ok+shift3+grow 1, ok+shift2+grow 1.
9. **RE-BIBLE edited** (rule: every fact the same session): source `O853` added (line 27), rows 343-345, a new row 348 (one body, pinks), row 352 (`--frames`) and row 354 (dir 3 exceptions). Row 344 was stale since r10 (it said that `body_rules` applies nothing); it now gives the gate counts.

## Changes (file:line)

| File | Lines | What |
|---|---|---|
| `scripts\permanent\art\gi_art.py` | 16-17, 46-53 | Header: API lines and Method text for the shared body, the per-frame torso and the pinks |
| | 77 | `SHARE = {"gi_ssj2": "gi_ssj"}` |
| | 1003-1014 | `strap_groups(staged, torsos)`: a group is strapped when every upright frame without the golden torso fits; `torso_groups` removed |
| | 1243-1304 | New section: `armor_body_diff`, `shared_body`, `object_mask`, `PINK`, `stray_pinks` |
| | 1344-1353, 1362, 1368 | `chest()` split out of `frame_checks` (the shared-body gate and the checks use the same test) |
| | 1458 | `bodies = by_key(gi_ssj)` (make_frames writes gi_ssj first) |
| | 1460 | `whole = torso_groups(...)` removed |
| | 1496 | `parts["sparks"]` kept for the composite |
| | 1498, 1502 | `strap_groups(staged, torsos)`; `gi_rules` gets the torso for every frame |
| | 1503-1519 | Shared body: armor compare, composite, chest gate, checks read the same composite of the armor (set 59 body, set 58 head), `v_neck` from gi_ssj; `stray_pinks` on the frame and on the check source |
| | 1545-1546 | Sleeve check uses the gi_ssj arms on a shared frame. The old line had a broken join (13 spaces before `+`); it is now two lines. |
| | 1557-1558 | Manifest field `body`: `gi_ssj` or `own` (gi_ssj2 only) |
| `scripts\permanent\art\gi_post.py` | 16-18, 221-222 | Header and rule comment: why shared frames get no R1/R2 |
| | 260-263 | `body_rules` skips frames whose manifest `body` is not `own` |
| `scripts\permanent\rom\rom_sheet.py` | 5-8, 13, 20-23 | Header: `--frames` usage, API, the dir 3 rule |
| | 45-46 | `FRAME_SCALE = 3`, `MIRROR_DIR, SOURCE_DIR = 3, 2` |
| | 155-179 | `write_frames(rom, set_ids, out_dir, anims)` |
| | 187-208 | CLI: `--frames <out_dir>`; `out.png` is optional with `--frames` |
| `scripts\permanent\tests\test_gi.py` | 424-486 | `OneBodyTests`: shared frames are the gi_ssj body; own-body keys; no pink in any gi folder; pink rule (outside, inside, tie); golden torso per frame (157 a4) and straps on 157 4.0.1, 4.0.3 |
| `scripts\permanent\tests\test_gi_post.py` | 77-101 | R1/R2 change the SSJ goldens {0: 2, 1: 3}; `body_rules` leaves every shared frame alone and still changes own frames |
| `scripts\permanent\tests\test_tools.py` | 17-18, 54-74 | `FrameExportTests`: names, sizes, 3x, transparency, d3 skip for a0 and d3 kept for a20 |
| `docs\RE-BIBLE.md` | 27, 343-354 | See concern 9 |
| `docs\build-log.md` | last 2 lines | Builder line, then the annotated r11 line |

Python files: LF, no byte order mark, no em or en dashes (checked with Python).

## Head boundary rule (CONFIRMED)

- Compare: for each key, `gi_art.head_mask` on the set 58 and the set 59 armor frame, then `chin_of` (the lowest face skin or outline 23 pixel of that mask). The body is every row strictly under the lower of the two chin rows, at screen position (record dx, dy, h-flip). Strict equality: 1 pixel of difference keeps the own body. A key set 58 lacks counts as equal (its body is set 59).
- Composite: gi_ssj pixels outside gi_ssj's head mask; then gi_ssj2 pixels on gi_ssj's head mask (no SSJ hair is left behind); then gi_ssj2's head mask and its blue sparks on top of all. The transplant then runs as before on this frame.
- Gate: the composite must pass the existing chest check, else the frame keeps its own body (concern 1).

Why the chin row: with the head mask alone as the boundary, 30 more keys differ, all by arcs, dust or 1-2 effect pixels above the chin (6.1.1, 7.2.2 and others; seen at 8x in `owner-0853-work\av1.png`).

## Keys that keep their own SSJ2 body (31 frames, 48 keys with d3; 228 keys share)

| Cause | Keys (armor pixels that differ under the chin) |
|---|---|
| Power-pose idle | 0.0.0 (117), 0.0.1 (108), 0.1.0 and 0.1.1 (116), 0.2.0 and 0.2.1 (127, d3 too) |
| Ki charge | every 4.d.i (103 to 144) |
| Walk pose differs | 1.1.1 (113), 1.1.3 (113), 1.2.1 and 1.2.3 (85, 76), 1.2.2 (1: (6,-5) 23 against 10) |
| Neck or collar pixels | 2.0.1 (1), 2.0.2 (2: 81 against 23), 8.0.1 (1: 21 against 23), 8.0.3 (5: 13 against 23), 18.2.0 (2: 113 against 23) |
| Pose differs | 13.0.1 (92), 13.0.3 (87) |
| Second neck opening (chest check) | 9.0.3, 9.1.3, 9.2.3, 9.3.3; 11.0.1, 11.1.1, 11.2.1, 11.3.1 |

## SSJ/SSJ2 body pairs (158 against 159)

Method (`owner-0853-work\pairs.py`): per set 159 frame header, the first key, gi_ssj_v2 against gi_ssj2_v2 by screen position. Sash row = the row with the most 26/27 pixels. Window = rows from 5 above the lower sash row down. 150 pairs have a sash in both.

| | Identical | Differ |
|---|---|---|
| Before (r10 folders) | 13 of 150 | 137 |
| After (r11 folders) | 49 of 150 | 101 |

- After, by cause (`pairclass.py`): 31 are the own-body list above; 70 are shared pairs whose every differing pixel is a head pixel (gi_ssj2 or gi_ssj head mask, a pixel the transplant or the SSJ step changed, or a spark). Outside both head masks, 0 shared pairs have a body pixel that differs. CONFIRMED.
- **Point 5 is not met as written.** By the brief's metric, 70 shared pairs still differ, and they are not on the point 2 list. They differ in head pixels only: the sash-minus-5 window reaches the face in crouched, attack and lying poses.
- Qualification: where gi_ssj drew its head and gi_ssj2 did not, the composite keeps gi_ssj2's own pixels (the SSJ body under the SSJ head is not drawn anywhere). In some shared frames those pixels are body colors (`fillcheck.py`): 20.0.x and 20.2.x 30 px each (the large SSJ head hides much of the upper torso there, so that part stays SSJ2's own conversion), 12.2.x 4 px of gi, 8.2.1 2 px, 6.0.0, 7.0.0, 7.1.2, 8.0.0, 8.1.2, 18.1.1-18.1.6 and 21.x 1 px each (wristbands or outline by the head).
- Pixel test: `test_shared_frames_are_the_gi_ssj_body` checks every shared key over the whole frame, outside both head masks and the sparks.

## Frames each fix changes, per form (folder frames against the copy from before this run)

| Folder | Fix 1 (shared body) | Fix 2 (torso or strap) | Fix 3 (pink) |
|---|---|---|---|
| gi_base (157) | 0 | 8: 1.0.1, 1.0.3, 4.0.0, 4.0.2, 4.1.0, 4.1.2, 4.2.0, 4.2.2 (golden torso) | 0 |
| gi_ssj / gi_ssj_v2 (158) | 0 | 0 (concern 3) | 0 |
| gi_ssj2 (pre-transplant) | 80 | 5: 4.0.0, 4.2.0 (golden torso); 4.0.1-4.0.3 (strap) | 4: 1.2.1, 1.2.3, 4.2.1, 4.2.2 |
| gi_ssj2_v2 (159) | 103 (includes R1/R2 no longer on shared frames) | the same 5 | the same 4 |

- Strap frames after: gi_base 4.0.1, 4.0.3, 9.0.0-9.0.3 (4.0.0 and 4.0.2 carry the golden strap); gi_ssj 9.0.x; gi_ssj2 4.0.1-4.0.3, 9.0.x. Per-frame lists: `tally.py` output.
- Pinks: all 5 set 58 strays (1.2.1 and 1.2.3 at image (2,13), 4.2.1 (11,14), 4.2.2 (11,15), 16.2.1 (9,13)) touch the transparent area flooded from the border, so the rule cleared them. 16.2.1 lost its pink through the shared body. In gi_ssj2_v2 the golden head now covers those spots. The rule for an enclosed pink (most common non-zero 4-neighbour, tie to the lower index) is tested on synthetic frames only: no real pink is enclosed.

## Tests

`py -3 -I -m unittest discover -s scripts\permanent -p "test_*.py"`: **159 tests, OK** (151 before plus 8 new). `frame_lock.py check --golden`: exit 0. The 12 golden SHA-256 values equal the values before this run.

## r11

- Command, no env vars: `py -3 -I scripts\permanent\log2_build.py --out archive\builds\log2_poc_r11.gba gohan_gi ssj2_form gohan_portraits status_bonus`. r11 did not exist before.
- **r11 SHA-1 `77084b63dc815a53760c99ef0c10a090c9d8c754`.** r10 unchanged: `ad9e0d1976f13da6e55698217f6c62e47a14d85e`.
- `log2_poc_r11.ss1` copied from r10 (SHA-1 `47f898f3...`, equal).

## r10 to r11 proof (CONFIRMED, `owner-0853-work\cmp_r10_r11.py`)

- 1034 differing bytes in 557 runs, all in rom:0x800EFC-0x8673E5.
- No set offset moved (ids 7-159). Sets 157, 158, 159: every record (anim, dir, index, dx, dy, w, h, attr0, attr1, header) is equal. Every frame header kind and size is equal.
- Every differing byte lies in the pixel bytes of a set 157 or 159 frame block (frames are raw: 8-byte header plus w x h bytes). 0 bytes outside, 0 bytes in a frame header.
- Set 157: 8 frames (10 records), 134 bytes. Set 159: 112 frames (187 records), 900 bytes. Set 158: 0 frames.

## Exports

- `archive\2026-10-18-art-review-renders\full_r11\`: 35 sheets, `a<NN>_base.png` (sets 56, 157; 18 anims) and `a<NN>_ssj_ssj2.png` (sets 59, 158, 159; 17 anims), all dirs, scale 4. No set lacked an anim of its group.
- `archive\2026-10-18-art-review-renders\frames_r11\`: `armor_56` 220 frames, `gi_base_157` 220, `armor_59` 211, `gi_ssj_158` 211, `armor_58` 153, `gi_ssj2_159` 211 (each at 1x and 3x).
- `archive\2026-10-18-art-review-renders\r11_changes_157.png` (8 columns) and `r11_changes_159.png` (146 columns in 13 bands), r10 row over r11 row, 4x, lime. No sheet for 158: no frame changed.
- `archive\2026-10-18-art-review-renders\r11_157_a4d1_torso_6x.png`: golden base d1, 157 4.1.0, 4.1.2, 4.1.1 at 6x, rows 16-23 boxed.
- What I viewed: the 157 sheet at 4x (whole); the 159 sheet in 14 crops at 4x (every column); 1.2.0, 6.0.0, 6.2.0, 9.0.0, 9.0.3, 11.0.0, 11.0.1, 12.2.0, 20.0.0, 21.0.0 at 6-10x against r10 and 158; the 157 walk d0 row. Nothing broken found besides the second V (concern 1, fixed by the chest gate).

## Work files

`archive\2026-10-17-gi-art-rounds\owner-0853-work\`: `before\` (art folders, scripts, RE-BIBLE before this run), `golden_sha_before.txt`, probe and proof scripts (`armor_cmp.py`, `pairs.py`, `pairclass.py`, `cmp_r10_r11.py`, `export_r11.py`, `tally.py`, `a4d1.py`), the zoom sheets `v1.png`-`v6.png`, `av1.png`, and the `c159_*.png` crops.

Limits kept: nothing written under `data\`, no ROM in `builds\` overwritten, no golden file edited, `work_r3\aura2\` untouched, no install.
