# Super Perfect Cell portrait (id 52): pipeline draft and my edit packs

Date: 2026-10-23. Brief: `docs\tasks\2026-10-23-superperfect-portrait\superperfect-portrait.md`. No ROM build, no `inject.py portrait`, nothing under `data\`.

## My files

All in `art\portrait-sources\remaster\superperfect\`:

| File | What it is |
|---|---|
| `pack_2bolts\sp52_2bolts_64.png` | 64x64 indexed portrait with 2 bolts. Edit this one. |
| `pack_3bolts\sp52_3bolts_64.png` | The same portrait with 3 bolts (the 2-bolt layout plus one bolt). Edit this one. |
| `pack_*\sp52_*_8x.png` | The portrait at 8x, for viewing. |
| `pack_*\ref_anime_*.png` | The reference at the portrait framing: full crop, 8x, 8x with grid, framed 8x (with and without grid), framed 64x64, face crop, face grid. |
| `pack_*\id52_palette.gpl` / `.txt` | 22 colors: the live id 40 colors plus the bolt glow 191, with OBJ index names. |
| `sp52_vec4_nobolts.png` | The vec4 stage without bolts, if I want to place my own. |
| `preview_4x.png` | Live id 40, id 52 with 2 bolts, with 3 bolts, and with no bolts, at 4x on lime, plus a 1x row. |

The two packs hold the same reference files. Each pack is complete by itself.

---

## Reference chosen

I chose `Cell-Disturbing-Power.avif` (r1, 1200x700).

- It is the only reference where the crest, dome, face, chin, neck and shoulders all fit in id 40's framing at id 40's eye row and chin row.
- It is front-facing with the smirk, and it is Super Perfect Cell with sparks.
- `Dragon-Ball-Z-Perfect-Cell.avif` and the cyothelion `.jpg` are the same drawing. At id 40's eye and chin scale (about 14-15 ref px per game px), the crop starts 130-160 px above the image and ends below it. So the dome and crest top are missing, and so is the bottom of the chest.
- The manga `.webp` is full body. The face gets only about 4 ref px per game px, and the style is manga, not anime.
- Use the other three as color and line reference only.

---

## Stages

Work scripts are in `scripts\one-time\2026-10-22-superperfect-study\portrait\`. The pipeline stage files are in `superperfect\pipeline\`.

1. **`p0_refs.py`** writes PNG copies of the four references to `refs\`. Pillow 12.3 reads AVIF, so no install was needed. The originals are unchanged.
2. **`p4_clean.py`** writes `refs\r1_clean.png`, a working copy without the anime bolt over the dome and the right crest.
   - It masks the bolt band, keeps the crest greens, and fills the rest with two OpenCV inpaint passes.
   - Filled green pixels become the plain lit crest color.
   - It draws the crest's outer outline again where the bolt crossed it, 4 px. Without this line, the label step's sky fill ran into the right crest.
   - The pack references use the original r1, not this working copy.
3. **Pipeline b1 to b6** (`scripts\one-time\2026-10-19-portrait-from-anime\anime\`) runs with `--char superperfect`. The settings file is `scripts\one-time\2026-10-19-portrait-from-anime\anime\chars\superperfect.py`. It has to live in `chars\` for the import, so it is outside the work folder.
   - CROP is `(295.0, 54.5, 10.2)`. It puts the eye centre at row 32.3, the chin outline at row 49.7 and the face centre at x 31.4, the same as id 40 (`chars\cell.py`).
   - Colors follow the live id 40 (`040_cell_40_owner_v2.png`), not vanilla 40:

     | Part | Index |
     |---|---|
     | Crest, lit and shadow | 132 |
     | Crest spots | 167 |
     | Crest line | 211 |
     | Dome | 1 |
     | Dome rim tone | 15 |
     | Dome glint | 2 |
     | Skin (lit / shadow / dark) | 2 / 10 / 12 |
     | Cheek | 89 |
     | Jaw (lit / shadow) | 37 / 120 |
     | Jaw line | 23 |
     | Eye white | 43 |
     | Iris (dark / light) | 25 / 31 |
     | Armor | 1 |
     | Face line | 15 |
     | Eye line | 1 |
     | Background | id 40's own (25, 252, 31, 30) |

   - Crest shadow takes 132, so the crest reads mid green like id 40. With 167, the lower crest was one dark mass.
   - My rules 1-6 are on, as for Cell: the darkest line under the eyes and at the outer corners, crease lines at the inner eye corners (`CREASE_BOXES`), nose by tone, neck and chest lines run to the bottom edge, line gaps closed, and no face despeckle.
   - **Smirk:** b4 turns a `mouth` stroke into a flat 3-4 px dash on one row, and that flattened the smirk. So `MOUTH_BOX` is empty, and a `JAW_GUIDE` on the anime smirk keeps its own traced stroke. This is a settings change, not a hand redraw.
   - **Result:** the mouth line is on row 40 at x 28-34 and rises at (35,39) and (36,38). The lower lip is tone 12 on row 42.
   - b6 copies `sp52_vec4.png` to `sp_vec.png`. The result has 20 colors and a frame equal to id 40's. There are no hand fixes in any stage.
4. **`p6_aura.py`** adds the bolts. It uses the game's SSJ2 bolt from `gi_aura.py`:
   - `gi_aura.walk` trunk, white core 2 on every third trunk pixel, glow 191 elsewhere, and one glow branch.
   - White over a bright pixel turns 191.
   - The bolts are longer for 64 px: 11-16 px up or down and 2-5 px sideways.
   - Each bolt starts on the background ring next to the body, inside its own box. Its fixed seed is the first one that puts 18 or more pixels in the picture.
   - No bolt pixel goes on the face box (x 14-49, y 24-50), on the frame, or in a 2x2 block.
   - Bolt A: left, beside the jaw. Bolt B: right, beside the crest. Bolt C: right, over the shoulder.
   - 2 bolts (A, B): 45 px, 14 of them white. 3 bolts (A, B, C): 67 px, 15 of them white. 2x2 blocks: 0.
5. **`p7_pack.py`** runs `e0_owner_pack.py` once per variant, with its source, output folder and reference redirected. It swaps e0's vanilla `id40_palette` for `id52_palette` and writes the preview.

---

## Checks

| PNG | `inject.py check <png> 52` |
|---|---|
| `pack_2bolts\sp52_2bolts_64.png` | OK: 21 colors, frame equals id 52's frame |
| `pack_3bolts\sp52_3bolts_64.png` | OK: 21 colors, frame equals id 52's frame |
| `sp52_vec4_nobolts.png` | OK: 20 colors, frame equals id 52's frame |

- No off-palette pixel, so no fix was needed.
- The check wrote nothing: the newest build is still r34.
- The pipeline's "in used set: False" lines are expected. Indices 37, 89 and 191 are not in vanilla id 40, and the inject check accepts all three.
- b6 reports 28 "2x2 line-color blocks". I checked each one:
  - 27 are the crest-spot fill 167 at the crest's lower tip (x 27-34, rows 27-33).
  - 1 is the armor corner at (3,51).
  - None is a line block.

---

## Concerns for me

- **Dome:** it is plain black. r1 has only a thin rim highlight there, so id 40's large grey reflection and white glints are not in this reference.
- **Crest width:** the anime crest is drawn from a lower angle, so it fills more of the width than id 40's. The red background shows mainly beside the jaw and below the right horn.
- **Right horn:** the spots under the removed anime bolt are lost. About x 40-59, rows 3-14 are plain lit crest.
- **Smirk:** at 64x64 the smirk is a 2-px rise at the right end of the mouth line. I may want it stronger.
- **Bolts:** they are a first layout, from seeds and not chosen by eye. They are thin and light blue on the red background. White core pixels over the white chest became glow by the bright rule.

## Deviations from the brief

- I edited `p4_clean.py`, `p6_aura.py` and `chars\superperfect.py`, and created `p8_strokes.py`, through PowerShell `Set-Content`, not the Write and Edit tools. A byte scan of every script shows LF line endings, no byte order mark, ASCII only and no dashes.
- `chars\superperfect.py` is in the shared pipeline folder, outside the work folder, because the pipeline imports it from there.

## Scripts

| Script | Purpose |
|---|---|
| `p0_refs.py` | PNG copies of the references |
| `p1_palette.py` | live versus vanilla id 40 colors |
| `p2_refgrid.py`, `p3_sample.py` | measure reference positions and colors |
| `p4_clean.py` | the bolt-free working copy |
| `p5_view.py` | 8x and 16x working views |
| `p6_aura.py` | the bolts |
| `p7_pack.py` | the packs and the preview |
| `p8_strokes.py` | stroke debug |

Working views are in `views\`.
