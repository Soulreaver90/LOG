# Super Perfect Cell portrait (id 52), take 2: one reference image from all 4 refs

Date: 2026-10-23. Brief: `docs\tasks\2026-10-23-superperfect-portrait2\superperfect-portrait2.md`, with my scope change of 9:01 PM.

## Scope change

I changed the goal while the work ran. This report follows the new goal.

- No in-game portrait. I did not run b1-b5, the vec4 stage, the bolt variants, `e0_owner_pack.py` or `inject.py check`.
- I made no pipeline or pack files before the change. The only earlier files are the measuring scripts and views listed under Scripts.
- New goal: one anime reference portrait, with the cyothelion image as the base. The other refs fill only what the base crops. The Disturbing Power bolts go around the body, off the face and eyes.
- Nothing under `data\`, no ROM build. No take 1 file changed: a recursive listing of the 50 take 1 files outside `take2\` shows the newest at 5:50 PM, before this run.

---

## My files

All are in `art\portrait-sources\remaster\superperfect\take2\`.

| File | What it is |
|---|---|
| `sp52_ref_full.png` | The full-size reference, 1191x947, at the base's resolution (14.77 base px per game px). |
| `sp52_ref_64.png` | The id 40 box of the full image, area-averaged to 64x64. RGB, not indexed, no hand edits. |
| `sp52_ref_64_framed.png` | The same picture (game px 3-60) inside id 40's grey frame. |
| `sp52_breakdown.png` | The full image with each source region tinted, a legend with each region's share, and the id 40 box in red. |
| `preview_4x.png` | Live id 40, take 1 (vec4, no bolts), the 64x64 and the framed 64x64 at 4x on lime, with a 1x row. |

---

## What each ref gave

| Ref | What it shows | Used for |
|---|---|---|
| r3 `perfect_cell_by_cyothelion...jpg` (base) | Pose, framing, the whole face (eyes, smirk, nose, cheeks, jaw piece), the lower crest, the lower dome with its lavender reflection, neck, chest and shoulder armor. Clean flat cels and lines. Cropped at the top (base row 0 is game row 12.7) and the bottom (game row 58.1). | Everything it shows: 44% of the canvas, every row from the crest's top edge to the chest. |
| r4 `wondering-what-yall-think...ssj2...webp` (manga) | The only ref with the full head top: tall symmetric horns and the dome with its white rim line. Also the chest plates under the white chest. | The horns, horn tips and dome outline above the base's top edge. Its yellow bolts are inpainted first, and its crest is recolored to the base's crest. Its rim line becomes the base's lavender. Its chest plates gave the shape idea for the bottom fill, but not its pixels (see Concerns). |
| r1 `Cell-Disturbing-Power.avif` (anime) | The electric bolts and the teal sky. | Bolts A and B, and the background color. |
| r2 `Dragon-Ball-Z-Perfect-Cell.avif` (anime) | The same drawing as the base, at a larger scale. It crops more: game rows 15.0 to 50.6 only (eye row 340, chin row 682). | Nothing. It shows no area that the base lacks. |

### Each ref by feature

| Feature | r1 Disturbing Power | r2 DBZ Perfect Cell | r3 cyothelion (base) | r4 manga SSJ2 |
|---|---|---|---|---|
| Pose and framing | Front, head higher, shoulders to the bottom edge | Front, head tilted down, cropped top and bottom | Front, head tilted down: **used**, it sets the framing | Full body, head small (about 5.5 px per game px) |
| Head shape and crest | Whole crest, but turned, and its right horn is under a bolt | Lower crest only | Crest from game row 12.7 down: **used** | Full symmetric horns and dome outline: **used above row 12.7** |
| Face and expression | Small smirk | Clear smirk, same drawing as the base | Clear smirk, eyes, nose, cheeks, jaw piece: **used** | Smirk, but tiny and in manga style |
| Line quality | Anime ink, soft | Anime ink | Clean even lines, flat cels: **used** | Manga ink with hatching |
| Color and shading | Bright anime greens, plain black dome | Bright greens, lavender dome reflection | Muted greens, charcoal and lavender dome reflection: **used, and the target for every recolor** | Light greens, black dome with a white rim and glint |
| Aura and sparks | White and cyan bolts, yellow plumes: **bolts used** | White and cyan bolts behind | None | Yellow bolts (inpainted out of the horns) |

---

## How the composite is built

Scripts are in `scripts\one-time\2026-10-22-superperfect-study\portrait2\`. Run order: `q3_compose.py`, `q4_bolts.py`, `q5_outputs.py`.

1. **Framing.** On the base: eye centre row 290, chin outline row 547, face centre x 586. These land at game row 32.3, row 49.7 and x 31.4, the same as id 40 and take 1. The canvas grows 188 px up and 88 px down so the whole 64x64 box fits (box x 122.2, y 0.9, size 945.3).
2. **Background.** r1's sky color, row by row. The base's white background is cut away with its own alpha. A 2 px edge ring is unmixed from white.
   - Checked on `composite_nobolts.png`, base rows 24-664 (outside both fade bands): 490593 base figure pixels. 0 pixels outside the edge ring differ by more than 2. 2224 of the 3219 ring pixels differ, as expected.
   - Base rows 0-23, dome columns: 0 non-ring pixels differ. On the crest in those rows, the base is blended with the r4 horns on purpose.
3. **Head top from r4.**
   - At r4 row 185, the horn and dome edges (324, 417, 652, 743) are mapped to the base's row 1 edges (235, 405, 797, 967). The x map is piecewise linear, and the y scale is 1.75.
   - The base fades in over its top 24 rows on the crest. In the dome columns, the base is used from row 0.
   - The dome is an ellipse fitted to r4's white rim line. Inside it is the base's dome dark (16, 16, 18). The rim is the base's lavender (145, 145, 171).
   - The base's dome reflection is cut by its top edge. Each cut run is closed with a half ellipse above the cut: the charcoal field at x 491-684, and the lavender pieces at x 528-533 and 624-649.
4. **Below the base.** The base's last rows show the tops of the black chest plates. Below them is plate color (42, 41, 47). The lit chest between the plates tapers to a V, 60 rows deep, like r4's chest. The side armor runs straight down.
5. **Bolts from r1** (`q4_bolts.py`).
   - Over the sky, each bolt is lifted with alpha from the blue channel against r1's sky color. The yellow plumes have low blue, so they drop out.
   - Over Cell's head, where take 1 inpainted bolt B, alpha comes from the white core. The glow is the core's blur in B's own glow color (55, 255, 254).
   - Masks: a 30 px polyline along A's trunk, and a polygon for B. The masks leave out r1's clouds, the plume centres and the armor highlight.
   - Placement: B crosses the dome's right side and the right horn as in r1 (r1 aligned on eyes and chin, scale 1.425). A runs down beside the left crest to the left shoulder (scale 1). A's lower half, mirrored, runs beside the right jaw and shoulder.
   - Face guard: 0 bolt pixels on the face polygon (eyes, cheeks, jaw piece and chin, grown 10 px).

## Checks

- `sp52_ref_64.png` and `sp52_ref_64_framed.png`: 64x64 RGB.
- Measured on `sp52_ref_64.png`: the pink irises are on rows 31-33 (x 22-25 and 37-39), and the jaw piece's lowest row is 48, so its outline is on row 49. This matches id 40.
- Bolt pixels on the face guard: 0.
- Scripts: LF, no byte order mark, ASCII only, no dashes.

---

## Concerns for me

- **Crest width:** the base's crest is wider than id 40's. It reaches the box edges beside the horns, so little background shows at the sides. This is the base's own form, so I kept it.
- **Horn seam:** across base rows 0-24 (game rows 12.7-14.3), the r4 horns blend into the base crest. Some spots are soft or doubled there. r4's spots are also lighter and softer than the base's.
- **Right horn edge:** just above the seam (about x 960-975, y 150-210 full size), the horn has no dark outline, and one light speck remains. r4's yellow bolt crossed the horn there and was inpainted.
- **Chest bottom:** the 88 rows under the base are drawn from the base's own colors, not copied from a ref. I tried r4's chest, but it is drawn from another angle and did not line up with the base's plate arcs. Only about 2 game rows of it show inside id 40's frame.
  - In the full-size image, a hairline crosses the lit chest at about canvas row 854, where the base fades out.
  - The side armor meets the plate fill along hard vertical edges at x 197 and x 956.
  - Both are at or below game row 58, so they barely reach the 64x64 version.
- **Background:** teal from r1, not the base's white. The r1 bolts are white and cyan, so they do not show on white.
- **Bolt placement:** I chose the placement. Only B keeps its r1 position. Over the right horn, B is partly see-through, and some crest shows through it.
- **r2 is not used:** it is the base's drawing and adds no area that the base lacks.

## Scripts

| Script | Purpose |
|---|---|
| `q0_refs.py` | PNG copies of the 4 refs, and an 8x grid view of live id 40 |
| `q1_measure.py` | measuring views with a labeled grid (`views\m_*.png`) |
| `q2_rowscan.py` | color runs along one row (edges of the crest, dome and chest) |
| `q3_compose.py` | canvas, background, r4 head top, dome fill, base, bottom fill; `work\composite_nobolts.png`, `regions.npy`, `box.npy` |
| `q4_bolts.py` | r1 bolts lifted and placed; `work\composite.png`, `bolts_rgba.png`, `views\bolts_check.png` |
| `q5_outputs.py` | my files in `take2\` |

`refs\r1_clean_take1.png` is a copy of take 1's inpainted r1. It is used to find where bolt B was over the head.
