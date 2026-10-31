# Portrait from anime art, full-size method: Goku Super Saiyan (id 65): report

Task run 2026-10-19.

## Result

- Compare sheet: `art\portrait-sources\remaster\anime\compare_goku_ssj_vec.png` (OLD | anime crop at full size, scaled to the box | conv_D | vec, 4x on lime, plus a 1x row).
- Portrait: `art\portrait-sources\remaster\anime\goku_ssj_vec.png` (mode P, OBJ palette, 64x64).
- Hand fixes: **1 pixel** (limit 30).

## Steps

1. `b1_label.py` crops the anime frame with `a1_guide.CROP` (339, -16, 5.5) at full resolution (352x352). The 16 rows above the frame are padding, labeled `outside`. The crop is upscaled 2x (704x704, 11 label px per game px), smoothed with a bilateral filter, and clustered with k-means (K 20, Lab, fixed seed). Each cluster gets a name from its nearest seed color (`SEEDS`).
   - Lines: dark pixels, plus a black-hat filter that finds thin dark strokes on a lighter ground. Sky is never a line. Dark parts wider than 2.2 game px stay regions.
   - Antialias pixels (the `fringe` clusters) join the line where they touch it. Elsewhere they take the label of the nearest region.
   - Cleanup: slivers under 0.7 game px wide, parts under 0.35 game px in area, and small or thin parts ringed by another family are merged into their neighbors. One example is faded hair-line tails that cluster as skin.
   - Eyes and mouth use position: `EYE_BOXES` and `MOUTH_BOX` in game px. Iris means green leads red, inside an eye box. Eye white means a light part that lies at least 80% inside an eye box. `GI_TOP` (row 47) turns gi colors above the shoulders into dark skin shadow.
2. `b2_vector.py` thins line and mouth pixels with `skeletonize` and walks the pixel graph into polylines. Adjacent junction pixels count as one node, and pass-through nodes are joined. It drops spurs under 0.8 game px and crumbs under 0.9 game px, then simplifies with Douglas-Peucker at 0.25 game px. Each region gets an outer contour (OpenCV, 0.2 game px tolerance). Line pixels first take the nearest region label, so regions meet under the line centre. Regions are stored largest first, which is the paint order.
3. `b3_raster.py` paints the region polygons at 8x8 sub-samples per game pixel, largest first. Each game pixel takes the label that covers most of it, then that label's single ramp color. No brightness ranks are used.
   - Sky: id 65's own background pixel at that spot. Where id 65 shows hair there, it takes the nearest id 65 background pixel in the same row. This rule is different from a6, which took the column-4 shade. Column 4 of id 65 is hair (23, 43, 44, 128) on several rows, so a6's rule would paint hair colors into the sky.
   - Strokes: Bresenham between the cells the vertices fall in, with a pixel-perfect L-corner drop. The whole mask is then thinned again and any 2x2 block is broken. The mouth cells are restored after thinning, because the thinning merged the mouth into the nose tip and cut the mouth to 2 px. Line color is 23 when a hair pixel touches the line, else 113.
   - The eye opening (white and iris shapes) overrides the lid strokes drawn into it. This rule replaced **25 line pixels** with eye white or iris. The lower iris cell takes 149.
   - Minimum-size rules (eye 3x2 with iris, mouth 2 px) are checked. Neither fired, so 0 pixels were stamped.

## Labels (false colors in `view_labels.png`) and fills

| Label | False color | Game px | LoG fill (id 65 index) |
|---|---|---|---|
| sky | (60,140,255) | 774 | id 65 background (233, 92, 225, 91) |
| hair | (255,240,60) | 1210 | 44 |
| hair_shadow | (190,140,0) | 126 | 128 |
| skin | (255,190,190) | 460 | 114 |
| skin_shadow | (220,110,110) | 403 | 115 |
| skin_dark | (150,50,60) | 57 | 116 (extra label: the anime's deepest skin cel, under the jaw and on the neck) |
| eye_white | (255,255,255) | 14 | 2 |
| iris | (0,220,120) | 6 | 57 top, 149 below |
| mouth | (255,0,255) | 5 | stroke, 113 |
| gi | (255,120,0) | 74 | 32 |
| gi_shadow | (140,60,0) | 129 | 33 |
| undershirt | (40,40,160) | 0 | 215 (none in this crop: the navy shirt starts below the box) |
| line | (20,20,20) | 652 | stroke, 113 or 23 |

## Vector counts

- Strokes: **222** (218 line, 4 mouth), 792 game px total length, 562 points.
- Regions: **64** (hair 3, hair_shadow 5, skin 5, skin_shadow 15, skin_dark 21, eye_white 2, iris 2, gi 1, gi_shadow 5, sky 5).

## Checks on `goku_ssj_vec.png`

- CONFIRMED: there are 21 indices, all from id 65's used set. Frame pixels equal id 65's.
- CONFIRMED: 572 line pixels (113: 255, 23: 317) against id 65's 585. There are 0 2x2 blocks of line pixels.
- CONFIRMED: the eyes are at rows 34-37, left iris x 25-27 and right iris x 36-38. id 65 has them at rows 36-37, x 26-28 and 35-37. After the hand fix, the drawn eye extents are 8x3 (left) and 7x4 (right). Each eye has white (2) and iris (57 and 149).
- CONFIRMED: the mouth is 4 px (row 44, x 30-33), as wide as its vector stroke. The lower lip is at rows 46-47, x 31-33. The nose tip at (31, 43) touches the mouth.
- CONFIRMED: there are 2 places where a hair or skin fill touches the sky with no line between them. id 65 has 0. The effect is small.
- Hand fix (1): (35, 38) changed from 2 to 115. This was a stray eye-white cell under the right eye. The pixel now matches its left neighbor. `HAND_FIXES` is keyed by `NAME`, so a Perfect Cell run does not receive this fix.

## Honest rating against id 65

- CONFIRMED (by eye on the compare): the new picture is far better than conv_D. Lines are clean 1-px strokes, the face reads as a face, and the pose, hair silhouette and neck lines follow the anime.
- LIKELY: it is still below id 65 as a game sprite. My rating is about 6/10, against id 65 at 8/10.
  - **Flat hair.** The anime lit cel maps to one color (44, 1173 px), and 43 is unused. id 65 gets volume from 43 highlights and 128 shading beside each line. The brief's rule (lit cel to base) causes this. If I want id 65's look, the whitest anime cel could map to 43. That is a one-line change to `FILL` plus a seed split.
  - **Small eyes.** They are narrow glaring slits (iris 3 px per eye), as in the frame. id 65's eyes are larger and easier to read at 1x.
  - **Line crumbs.** Some short broken strokes on the neck and chest come from gaps in the anime lines.
- SPECULATIVE: at 1x in game the new face may read as more "anime" but less clear than id 65.

## Concerns

- The per-character settings must be set again for Perfect Cell (id 40):
  - In b1: `SEEDS`, `EYE_BOXES`, `MOUTH_BOX` and `GI_TOP`. I set the boxes by hand from a grid view of the anime, and the eye rule depends on them.
  - In b3: `FILL`, `BG`, `LINE` and `HAIR_LINE`, the iris and eye-white indices, and `HAND_FIXES`.
  - The CROP comes from `a1_guide.py`.
- k-means names come from seed colors. A new frame with other cel colors needs a `view_labels.png` check before step 2.

## Files

- Scripts: `scripts\one-time\2026-10-19-portrait-from-anime\anime\b1_label.py`, `b2_vector.py`, `b3_raster.py`. Run them in order with `py -3 -P -B`.
- Data: `art\portrait-sources\remaster\anime\goku_ssj_labels.png`, `goku_ssj_vector.json`, `goku_ssj_vector.svg`.
- Views: `scripts\one-time\2026-10-19-portrait-from-anime\anime\view_labels.png`, `view_vector.png`, `view_vec_grid.png`, `view_vec_big.png`, `view_vec_face.png`, and the exploration views `view_b0_*.png`.
- No pip package was installed. No earlier file was changed or deleted. Nothing was written under `data\`.

## Face pass

This pass follows my verdict of 2026-10-19 1:37 PM: "The hair is perfect, its the facial details that is still a mess." The script is `scripts\one-time\2026-10-19-portrait-from-anime\anime\b4_face.py`. Its per-character settings are at the top of the file.

### Results

- Compare sheet: `art\portrait-sources\remaster\anime\compare_goku_ssj_vec2.png` (OLD | vec | vec2 | vec3, 4x on lime, plus a 1x row).
- Portraits: `goku_ssj_vec2.png` (medium line density) and `goku_ssj_vec3.png` (fewer lines), both mode P, OBJ palette, 64x64.
- Face close-ups made by `c1_face_zoom.py`: `scripts\one-time\2026-10-19-portrait-from-anime\anime\view_face_zoom_vec.png`, `view_face_zoom_vec2.png`, `view_face_zoom_vec3.png`. The third column of each close-up is labeled "vec" because the script has a fixed label.

### Face line counts

A face line pixel is a 113 or 23 pixel inside ZONE that touches no hair fill (44, 43, 128). I used the same count for all four pictures.

| Picture | Face line px |
|---|---|
| id 65 | 137 |
| vec | 204 |
| vec2 | 132 |
| vec3 | 110 |

### Rules and values

- **Zone:** rows 30-63, cols 14-50. Hair-labeled pixels, 23 lines next to hair and the frame stay locked.
- **Junction chain:** strokes that meet at one junction join when the bend is 25 degrees or less. This turned 145 face strokes into 85.
- **Classes:**
  - Eye and brow: `EYE_KEEP` (20,32)-(30,39) and (34,32)-(42,39).
  - Jaw and chin: within 0.8 game px of `JAW_GUIDE` for 60% of the stroke. The guide points come from the vectors.
  - Nose: `NOSE_BOX` (29,40)-(35,44).
  - Contour: for 50% of the stroke, skin and sky, hair or gi lie within 0.7 game px.
  - Other: every stroke that is not in a class above.
- **Keep rule:** an "other" stroke stays only if it is at least `min_len` long. vec2 uses 9.5 game px (about 52 full-size px). vec3 uses 14 game px. A contour stroke must be at least `min_contour` long (vec2 1.5, vec3 4). Eye, jaw and nose strokes stay at 1 game px or more.
- **Bridge:** kept strokes join across gaps up to 2 game px, with a bend up to 40 degrees. vec2 has 10 bridges and vec3 has 8.
- **Clear box:** (30,36)-(34,39) gets no line cells. This removes the brow furrow between the eyes.
- **Shadow at full size:** the skin_dark and skin_shadow masks are opened and closed with a disk of 0.6 game px. Parts under 4 game px go to the next lighter step. Then the regions are traced again and painted by coverage.
- **Shadow at 64x64:** shadow parts under 4 px take the most common fill around them. This merged 17 px in vec2 and 16 px in vec3.
  - 116 parts in the zone rectangle: vec 27, vec2 4, vec3 4.
  - 115 parts in the zone rectangle: vec 19, vec2 14, vec3 11.
- **Nose:** cells of the nose stroke from its tip, with no cell next to the mouth line, at most 3 cells. The result is (32,41)-(32,42), 2 px.
- **Mouth:** 3 px at row 44, x 31-33. The lower lip strokes become one 116 pixel at (32,47).
- **Eyes:** eye white cut off from its iris becomes skin. Otherwise the eyes are drawn as in b3.

### Checks

- CONFIRMED: the hair lock holds. An independent diff against `goku_ssj_vec.png` gives 0 changed pixels outside rows 30-63 and cols 14-50, 0 changed hair-fill pixels (44, 43, 128) and 0 changed 23 pixels. The script also stops if any pixel outside its zone mask changes.
- CONFIRMED: vec2 changes 137 pixels and vec3 changes 155. All are inside the zone.
- CONFIRMED: there are no 2x2 line blocks and all indices are in id 65's used set. One seam pixel per variant was cleared where a new line met a locked line in a 2x2.
- **Hand fixes: 1 per variant.** (35, 38) changes from 2 to 115. This is the same stray eye-white cell as in vec.

### Honest rating

- LIKELY: vec2 is the best of the three:
  - The face now reads as eyes, a short nose, a 3 px mouth with one lip-shadow pixel, a continuous jaw V to the chin, and a few unbroken neck lines.
  - The shadows are fewer, larger shapes.
  - I rate vec2 about 7/10, against id 65 at 8/10.
- LIKELY: vec3 differs from vec2 mostly on the neck and chest, with fewer neck and collarbone lines. The face itself is almost the same as in vec2. I rate it about 6.5/10, because the neck looks bare next to id 65.
- LIKELY: id 65 still wins on the eyes. Its eyes are larger and cleaner. Ours are a white band with a 2-3 px iris, with lid lines only partly drawn below.

### Concerns

- `JAW_GUIDE`, `EYE_KEEP`, `NOSE_BOX` and `CLEAR_BOXES` are set by hand for this frame. Perfect Cell needs new values.
- Contour strokes make up most of the remaining face lines (19 kept in vec2). They are real outlines, but they are the next thing to thin if I want fewer lines.
- The nose lost its tip cell. The tip sits right above the mouth line, so keeping it would join the nose and mouth into one shape.
- The eye-white band under each iris is unchanged from vec.

## Detail pass

This pass follows my verdict of 2026-10-19 2:22 PM: "Vec 2 is better but still missing a lot of details in the face." The script is `scripts\one-time\2026-10-19-portrait-from-anime\anime\b5_detail.py`. It uses vec2 as the base and reuses the b4 zone and strokes. To make that possible, `b4_face.py` now has `prepare()` and `kept_strokes()`. After that refactor, vec2 and vec3 rebuild byte for byte the same (checked with `cmp`).

### Results

- Compare sheet: `art\portrait-sources\remaster\anime\compare_goku_ssj_vec4.png` (OLD | vec2 | vec4, 4x on lime, plus a 1x row).
- Portrait: `goku_ssj_vec4.png` (mode P, OBJ palette, 64x64).
- Face close-up: `scripts\one-time\2026-10-19-portrait-from-anime\anime\view_face_zoom_vec4.png`. The third column is labeled "vec" by `c1_face_zoom.py`.

### Tone counts

The counts cover rows 30-60 and cols 14-50.

| Picture | 113 | 114 | 115 | 116 | 117 | Shares 114 / 115 / 116 |
|---|---|---|---|---|---|---|
| id 65 | 155 | 412 | 305 | 47 | 2 | 0.538 / 0.398 / 0.061 |
| vec2 | 131 | 394 | 301 | 16 | 0 | 0.554 / 0.423 / 0.023 |
| vec4 | 133 | 330 | 323 | 54 | 0 | 0.467 / 0.457 / 0.076 |

All three shares in vec4 are within 25% of id 65's shares: 114 is 13% lower, 115 is 15% higher and 116 is 24.6% higher. 116 is at the edge of the 25% range.

### Rules and values

All rules act inside the b4 zone and change only skin pixels, unless a rule says otherwise.

- **Shade steps** use the original anime cels, before the b4 smoothing:
  - Where the anime has a shadow cel on lit skin, 114 becomes 115 (13 px).
  - Where the anime has a dark cel of at least `DARK_MIN` = 5 px, the pixel becomes one step darker: 115 to 116, or 114 to 115 (43 px).
- **Tone strokes:** every stroke the vec2 keep rule dropped, and the line cells the furrow box removed, return as 1-px tone (32 px). The darkness of each stroke is the median, along the stroke, of the darkest anime pixel near each point (Lab L, 0-255).
  - On lit skin: 116 if L is 95 or less (`FAINT_L`), else 115.
  - At row 50 and below (`NECK_ROW`): 115 on lit skin.
  - In shadow: 116 only if L is 25 or less (`SHADOW_LINE_L`). Otherwise the shadow stays as it is.
- **Eyes:**
  - Upper lid 2 px where the anime lid is at least 1.5 game px thick (`LID_THICK`): 2 px.
  - Upper lid on a column that had none: 3 px.
  - Brow cell above an existing lid: 1 px. A new line cell is never placed where it would complete a 2x2 line block.
  - Lower lid in 116 where the anime lower lid is at least 0.6 game px (`LOWER_LID`): 12 px.
  - The white is still 8x3 (left) and 7x4 (right), with iris 57 and 149.
- **Nose:** 116 beside each nose cell on the shadow side (`NOSE_SIDE` +1, to the right) and under the tip on that side: 3 px.
- **Mouth:** unchanged. 115 under the lip-shadow pixel, at (31-33, 48): 3 px.

### Checks

- CONFIRMED: the hair lock holds. Against `goku_ssj_vec.png`, 0 pixels changed outside rows 30-63 and cols 14-50, 0 hair-fill pixels changed and 0 hair-line (23) pixels changed. Against vec2, 0 pixels changed outside the b4 zone, and 112 changed inside it.
- CONFIRMED: all indices are in id 65's used set. There are 0 2x2 line blocks.
- **Hand fixes: 0.** The rules placed every change. The 40-pixel allowance is unused.

### Honest rating

- LIKELY: vec4 is the best face so far. My rating is about 7.5/10, against id 65 at 8/10 and vec2 at 7/10.
  - The cheek creases, the furrow, the nose side and the neck muscles now show as tone, as in id 65.
  - The lower lids and the nose shadow give the face the anime's angry look.
  - The face no longer reads as bare skin with a few lines.
- LIKELY: id 65 still wins on the eyes. Its white shows on both sides of a 3-color iris under a clean lid. Our whites are flat bars.

### Concerns

- The brow could not be drawn over most of each eye. The pixels above the eyes are hair or hair line, and the hair lock keeps them. The brow rule placed 1 cell. The existing hair line acts as the brow.
- The furrow returns as a 116 run at row 37, x 30-33. It sits on the same row as the bottom of the eye whites, so it may read as a band that joins the eyes.
- 116 is at the edge of the 25% range (+24.6%). One more 116 rule would push it over.
- `FAINT_L`, `SHADOW_LINE_L`, `NECK_ROW`, `DARK_MIN`, `LID_THICK`, `LOWER_LID`, `NOSE_SIDE` and `LIP_UNDER` are set per character. Perfect Cell needs its own values.
