# Portrait from manga art, full-size method: Perfect Cell (id 40): report

Task run 2026-10-19.

## Result

- Compare sheet: `art\portrait-sources\remaster\anime\cell\compare_cell_vec.png`. Columns: OLD (ROM id 40), the reference at the same framing inside id 40's frame, and cell_vec. Each is at 4x on lime (191, 255, 7), with a 1x row below.
- Portrait (vec4 stage): `art\portrait-sources\remaster\anime\cell\cell_vec.png`. It is mode P with the OBJ palette, 64x64.
- Edit pack: `art\portrait-sources\remaster\anime\cell\owner_edit\`.
- Hand fixes: **0**. No feature was redrawn by judgment.

## Character setup (task 1)

Each script now reads its per-character values from one module, `scripts\one-time\2026-10-19-portrait-from-anime\anime\chars\<name>.py`.

- **Selection:** add `--char <name>` to any script. The default is `goku_ssj`, so old commands still work.
- **Proof runs:** `--out <dir>` sends every output, and every read of an earlier stage, to `<dir>`. The Goku proof ran this way, so it touched no Goku file.
- **Chain:** run `py -3 -P -B <script> --char cell` for b1_label, b2_vector, b3_raster, b4_face, b5_detail, b6_final and e0_owner_pack, in that order.

New files:

| File | Purpose |
|---|---|
| `chars\__init__.py` | Reads `--char` and `--out`. Exports `C`, `ART`, `VIEW`, `ARGS` and `FLAGS` (FLAGS passes the choice on to the c1 subprocess). |
| `chars\goku_ssj.py` | Every Goku value, copied without change from the old script headers. |
| `chars\cell.py` | Every Cell value. Boxes, rows and points are in reference px and convert through `CROP`. |
| `b6_final.py` | Copies `cell40_vec4.png` to `cell_vec.png`, runs the checks and draws the 3-column compare sheet. |

Changed scripts: `a1_guide.py`, `b1_label.py`, `b2_vector.py`, `b3_raster.py`, `b4_face.py`, `b5_detail.py`, `c1_face_zoom.py` and `e0_owner_pack.py`. Each "per character" block now reads from `C`. The Goku-only literals became settings:

- the line test exclusions
- the iris test (a function per character)
- the eye-white source clusters
- the gi row rule (now `REMAP`)
- the line color map (`LINE_BY`, first match wins)
- the lock labels and lock fills (Goku: hair)
- the skin ramp names
- the face-zoom window, the pack names and the palette id

Settings that are new and off for Goku:

- b1: `SKY_FILL`, `HATCH` and `THICK_LABELS`
- b2: `GAP_CLOSE` and `TO_BOTTOM`
- b4: `TONE_CLASSES` and `SHADOW_CRUMBS`
- b5: `EYE_LINE`, `LOWER_LID_LINE`, `OUTER_CORNERS`, `CREASE_BOXES` and `EYE_GROUNDS`

`join_strokes` and its helpers moved from b4 to b2, so b2 can close gaps. b4 now uses them from b2.

**File names.** Cell's stage files use the stem `cell40` (`cell40_labels.png` through `cell40_vec4.png`). This keeps them clear of the required names `cell_vec.png` and `compare_cell_vec.png`. Cell's working views go to `cell\views\`, so no Goku view in the scripts folder is written.

## Crop and why

- `CROP = (14.0, 44.0, 5.75)`. A game pixel covers 5.75 reference pixels, and the window starts at reference (14, 44).
- **Measured in the reference.** The red eye centroids are at (149.9, 228.6) and (239.5, 230.7), so the eye row is y 229.6 and the face centre is x 194.7. The chin outline under the jaw piece is at y 328-334, centre 330.
- **Targets in id 40.** Eye row 32.0 (rows 31-32), chin outline row 49.5 (row 49), face centre x 31.5.
- **Fit.** s comes from the eye-to-chin distance: 100.4 / 17.5 = 5.74, rounded to 5.75. With y0 = 44 the eye row lands at 32.3, the chin at 49.7 and the centre at x 31.4. The picture area (rows 3-60) also stays inside the 395-px reference, so no "outside" padding reaches the body. Only the frame rows 61-63 lie past the bottom edge.
- **A single setting.** Every box in `chars\cell.py` (eye, mouth, nose, zone, dome row, armor row, neck row, face view) is written in reference px. The functions `gx()`, `gy()` and `gbox()` convert it through `CROP`, so a tighter crop needs only a new `CROP`. The hatch polygons and sky points are in reference px as well.
- CONFIRMED: the eyes in the reference sit wider apart than in vanilla. The eye distance is 15.6 game px, against id 40's 11. One scale cannot match both eye spacing and the eye-to-chin distance. The brief's anchors (eye row, face centre, chin row) win.

## Labels (false colors in `cell\views\view_labels.png`) and fills

The counts are from the final b1 run, in game pixels.

| Label | Game px | id 40 fill | How it is found |
|---|---|---|---|
| sky | 1083 | id 40 background (25, 252, 31, 30) | seed blues. The cloud joins it through `SKY_FILL`. |
| crest | 522 | 129 | seed green |
| crest_shadow | 106 | 132 | darker green cluster (mostly on the right crest) |
| crest_spot | 90 | 167 | seed dark green |
| dome | 398 | 1 | thick black above game row 40.2 (`THICK_LABELS`) |
| dome_tone | 135 | 211 | dome screentone (`HATCH`), plus grey above the dome row |
| dome_hi | 23 | 212 | white above the dome row (game row 25.9), plus the screentone's light core |
| face | 627 | 2 | seed white. This family covers the body white too. |
| face_shadow | 108 | 10 | seed light grey, plus the mid band of the neck hatching |
| face_dark | 57 | 12 | seed grey, plus the dark band of the neck hatching |
| cheek | 69 | 229 | seed purple |
| jaw | 102 | 120 | seed yellow (the jaw piece and the side pieces) |
| jaw_shadow | 24 | 118 | seed orange-brown |
| eye_white | 8 | 43 | light part 80% inside an eye box |
| iris | 10 | 25 (top), 31 (lower) | red leads green by 70 and blue by 60, inside an eye box |
| mouth | 5 | stroke, 15 | line inside `MOUTH_BOX` |
| body_dark | 59 | 14 | thick black below game row 40.2 (the armor at the lower right) |
| line | 481 | stroke, by neighbor: dome 1, crest_spot 167, crest 211, jaw 23, else 15 | ink |

Special rules in b1, all of them settings in `chars\cell.py`:

- **Cloud.** The non-ink area joined to 3 points in the cloud becomes sky. A closing of 0.6 game px then removes the cloud's own grey outline, which has sky on both sides. CONFIRMED in the labels view: the cloud and its outline are gone.
- **Hatching.** There are 2 polygons: the dome screentone and the neck hatching under the jaw. Inside them there are no lines. A label comes from the lightness, blurred by 0.5 game px.
- **Ink test.** `LINE_L` is 35, not 70. The crest spots and the cheek purple are darker than 70, so they are excluded from the line test.

## How each of my rule was applied

1. **Darkest line at the lower eye edge, carried to the outer corners.** `EYE_LINE = 1` (0, 0, 0), id 40's darkest color.
   - b5 puts 1 under every eye column and recolors any 15 line cell that is already there: 15 px.
   - Upper-lid cells that were 15 also become 1.
   - The outer-corner rule placed 2 px at the left eye: (21, 31) changed from 15 to 1, and (21, 32) changed from 2 to 1. Rows 29-30 of that column are the locked crest edge.
   - CONFIRMED (traced): the right eye's outer column (x 44, rows 30-32) is the side piece's 23 outline. That outline already closes the corner, and the rule does not repaint it.
2. **Short dark lines at inner-corner creases and the brow.** Not applied. `CREASE_BOXES` is empty.
   - LIKELY: the manga has no crease strokes at Cell's inner eye corners.
   - The crest's lower edge is the brow. It is locked, so b3 draws it as the crest outline (211).
3. **Small forms by tone steps, not lines.** The nose stroke class is in `TONE_CLASSES`, so b4 draws no nose line cells. b5 draws the nose as a 1-px tone stroke (10 or 12 on white).
4. **Body lines to the bottom edge, plate edges outlined.**
   - b2 `TO_BOTTOM` runs 8 stroke ends on to the bottom edge. A stroke must be at least 5 game px long, end below reference y 340 and head down.
   - CONFIRMED in the final image: row 60 (x 3-60) of `cell_vec.png` holds 13 line px (15, 23 or 1), against 5 in id 40.
   - The plate edges keep their manga ink outlines. In b4 they are contour strokes, or "other" strokes of 9.5 px or longer.
5. **Close small gaps in long contours.**
   - b2 `GAP_CLOSE` made 12 joins: strokes of 4+ game px across gaps up to 1.5 px, bend up to 35 degrees.
   - b4 then added 5 bridges inside the zone.
6. **Only id 40's indices. No despeckle, skip-fix or ramp-shift on the face.**
   - b4's 64x64 shadow-crumb merge (`SHADOW_CRUMBS`) is off for Cell.
   - b4's full-size shadow smoothing stays on. It shapes the vector regions before rasterization and is part of the vec4 method I accepted. It is not a pixel pass.
   - No e3/e4-style pass exists in this chain.

## Pipeline counts

- b2: **432** strokes (430 line, 2 mouth), 905 game px in total. **110** regions.
- b3: 587 line px and 0 2x2 line blocks in the line mask. The eye opening replaced 13 line px. The eyes are drawn 6x4 and 9x4, each with an iris. The minimum-size rules stamped 0 px.
- b4:
  - Zone: game px (3, 25)-(61, 64). The crest and dome are locked, together with their lines.
  - Face strokes: 248, which became 154 after 94 junction joins.
  - vec2 keeps 44 strokes (11 eye, 19 contour, 14 other). The mouth is 4 px at row 41 (x 30-33) and the lip shadow is 1 px at (31, 43).
  - Diff outside the zone: 0.
- b5 on vec2:
  - 28 px "anime shadow cel" and 78 px "anime dark cel" shade steps.
  - 64 px of tone strokes.
  - 15 px of lower-lid line and 2 px of outer corner.
  - 137 px changed in the zone and 0 outside it.

## Checks

- CONFIRMED: **the Goku vec4 rebuild is byte for byte identical.**
  - The whole Goku chain ran with `--out` into the scratchpad, after the last script edit.
  - These files match the originals by SHA-256: `goku_ssj_labels.png`, `goku_ssj_vector.json`, `goku_ssj_vector.svg`, `goku_ssj_vec.png`, `goku_ssj_vec2.png`, `goku_ssj_vec3.png`, `goku_ssj_vec4.png`, `compare_goku_ssj_vec2.png` and `compare_goku_ssj_vec4.png`.
  - The Goku pack also matches: e0 rebuilt all 12 `owner_edit` files identical.
  - `compare_goku_ssj_vec.png` matches once `goku_ssj_conv_D.png` is present in the out folder. b3 skips that column when the file is absent.
- CONFIRMED: **no Goku file changed.**
  - 131 files under `anime\` (art) and `scripts\one-time\2026-10-19-portrait-from-anime\anime\` were hashed before the work and again after it.
  - Only the 8 scripts I edited differ. None is missing.
  - A `__pycache__` my compile check created was deleted.
- CONFIRMED (independent script, not the pipeline's code): `cell_vec.png` is mode P, 64x64, and its palette is the OBJ palette.
  - All 732 frame pixels equal id 40's.
  - It uses 23 indices, all in id 40's 28-index set. id 40 indices it leaves unused: 22, 36, 42, 97 and 107.
- CONFIRMED: `cell_vec.png`, `cell40_vec4.png` and `owner_edit\cell_vec_64.png` have the same SHA-256.
- CONFIRMED: there are 0 2x2 blocks of line colors inside the zone. Outside the zone, indices 1, 167 and 211 are also dome and spot fills, so a picture-wide count would mean nothing there. b3 reports 0 blocks in its line mask.
- CONFIRMED: the new and changed scripts are LF, ASCII only, with no byte order mark and no control characters. All compile.

## Edit pack (`cell\owner_edit\`), the same set as Goku's

| File | Content |
|---|---|
| `cell_vec_64.png` | the portrait to edit: 64x64, indexed, OBJ palette |
| `cell_vec_8x.png` | the same at 8x |
| `ref_manga_crop_full.png` | the reference cropped to the exact portrait box (368x368). The last 17 rows are past the image and black. They fall on frame rows 61-63. |
| `ref_manga_8x.png`, `ref_manga_8x_grid.png` | that crop at 512x512, without and with the game grid |
| `ref_manga_8x_framed.png`, `ref_manga_8x_framed_grid.png` | 512x512 inside the portrait's own frame, picture at game px 3..60 (24..488 at 8x), without and with the grid |
| `ref_manga_64_framed.png` | 64x64 with the frame, the reference shrunk into the 58x58 picture (true color) |
| `ref_manga_face_full.png` | the face (game px x 14-50, y 21-55) at full size |
| `ref_manga_face_grid.png` | the face with the game grid, numbered every 4. e0 draws it now, in place of the Goku-only copy. |
| `id40_palette.gpl`, `id40_palette.txt` | id 40's 28 colors, darkest first, with OBJ indices |

## Honest rating against id 40

- LIKELY: about **6/10**, against id 40 at 8/10.
- **What works.**
  - At 1x it reads as Perfect Cell. The crest has its spots and the black dome has a screentone sheen.
  - The purple cheeks and the yellow jaw frame match the manga's shape and pose.
  - The face is the manga's plain white with a tone nose, a 4-px mouth and a lip mark.
  - The body lines are much calmer after rule 4 was limited to long strokes.
- **Eyes.** They are the weakest part. Each is 2-3 red px under the crest edge, with a black lower lid. The outer white wedges of the manga are mostly lost to the cheek and line cells. id 40's pink eyes (107) read more clearly at 1x. LIKELY: my hand pass will go here first, as with Goku.
- **Crest.** It is busier than id 40. The manga's scratch strokes on the crest show as 211 squiggles (for example x 34-40, rows 22-26). The large spots merge at the left crest edge.
- **Face tone.** White (2) is 71% of the face tones, against 49% in id 40. id 40 also uses 9 and 11, which the 3-step ramp (2/10/12) never paints. SPECULATIVE: a face_shadow fill of 9 in place of 10 would come closer to id 40's soft look. That is a one-value change to `FILL`.

## Concerns

- **Color choices are settings.** I may want different values. Each is one value in `chars\cell.py`.
  - eyes: 25 top and 31 lower, which are background reds
  - dome screentone: 211
  - dome highlights: 212
  - spot ink: 167
- **Hand-set geometry, like the Goku eye boxes:** the hatch polygons, the cloud points, the eye and mouth boxes, and the dome and armor rows. They are in reference px, so they follow a new `CROP`. A crop change still needs a check of `cell\views\view_labels.png` before b2.
- **Rule 2 was not applied** (see the rules section). If I want crease lines, set `CREASE_BOXES` in `chars\cell.py`.
- **The crest and dome are locked** in b4 and b5, as the hair was for Goku. They get only the b3 drawing.
- **Lines and fills share indices.** `b3.LINES` now holds 1, 167 and 211, which are also fills. b5's "no new 2x2 line block" test can therefore refuse a lid cell next to the crest outline or the dome. SPECULATIVE: this did not change the outer corners (both were traced), but it may have refused other lid cells.
- **Late b5 change.** After the first Cell run, the outer-corner rule was allowed to recolor a 15 line cell. Goku does not run this rule. CONFIRMED: Goku b5 rebuilt `goku_ssj_vec4.png` identical after this change.
- **Unread working views.** The zoom views in `cell\views\` are working files and I did not check every one. The face zoom labels its third column "vec" for every stage, as before.
- No pip package was installed. Nothing was written under `data\`, `scripts\permanent\`, `tests\`, `builds\`, `scripts\one-time\2026-10-19-r21-build\` or `final_r21\`. Scratch helpers and the Goku proof outputs are in a scratch folder outside the project, not in the project.
