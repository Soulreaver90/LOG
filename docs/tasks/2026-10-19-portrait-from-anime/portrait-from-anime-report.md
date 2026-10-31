# Portrait from anime art: Goku Super Saiyan, id 65 (2026-10-19)

Labels: **CONFIRMED** = proved here with data or a script check. **LIKELY** = strong evidence, not proved. **SPECULATIVE** = a guess.

Brief: `docs\tasks\2026-10-19-portrait-from-anime\portrait-from-anime.md`. No ROM build and no patch were made. I wrote files only in `art\portrait-sources\remaster\anime\` and `scripts\one-time\2026-10-19-portrait-from-anime\anime\`, plus this report.

---

## Result

| File | What |
|---|---|
| `art\portrait-sources\remaster\anime\goku_ssj_H1.png` | H1: spiky strands that taper to points (closer to id 65) |
| `art\portrait-sources\remaster\anime\goku_ssj_H2.png` | H2: the same strands, a little shorter, wider and more curved, with blunt round ends (closer to the anime) |
| `art\portrait-sources\remaster\anime\compare_goku_ssj.png` | **Compare sheet**, 4x on lime, plus a 1x row: OLD id 65, anime shrink, H1, H2, goku_mid_A |
| `art\portrait-sources\remaster\anime\goku_ssj_shrink.png` | The plain 64x64 box shrink of the anime crop, in the id 65 frame (reference only) |
| `art\portrait-sources\remaster\anime\old_65.png`, `old_63.png` | ROM portraits 65 and 63, unpacked (reference) |

Both PNGs are 64x64 indexed images with the OBJ palette, 4096 bytes in row order, so they are ready for a raw type 0 frame. **CONFIRMED** by an independent re-read (see Checks).

---

## Method, step by step

| Step | What I did | Time |
|---|---|---|
| 0. Read | The brief, `portrait-soft-report.md`, `k1_soft.py`, `k0_layers.py`, RE-BIBLE section 5a, `docs\research\re-portraits.md`, both refs | 11:31-11:36 AM, 5 min |
| 1. Unpack | `a0_unpack.py` unpacks id 65 (and 63) through `gohan_portraits.portrait()` and `palette()`, prints each index with its count and luma, and writes a 12x labelled grid view | 11:36-11:39 AM, 3 min |
| 2. Framing | Measured id 65: eye row 36, face centre x 32, chin row 51, eye spacing about 10 px. Measured the anime frame: eyes at y 182, nose x 515, chin y 264. Crop `CROP = (339, -16, 5.5)`: 5.5 anime px per game px. That puts the eye row at 36, the face centre at 32 and the chin at 51 (eye spacing 12.7 px, so the anime face is a little wider than id 65). Row 3 lands on anime y 0.5, so the hair top fills the picture | 11:39-11:45 AM, 6 min |
| 3. Guide | `a1_guide.py` makes the plain box shrink and prints a class map (hair, skin, line, gi, sky) per game pixel. `a1_gridview.py` draws the 64x64 grid over the anime crop, so I could read every line position in game pixels | 11:42-11:50 AM (with step 2) |
| 4. Face | Typed by hand in `a2_paint.py` as letter runs per row: jaw outline (1 px), ears, eyes, brows, nose, mouth, cheek lines, neck lines, collarbones, gi. Light from the upper left, as in the anime frame and id 65 | 11:50 AM-12:00 PM, 10 min |
| 5. Hair | Hand-placed strands (root, tip, root half-width, bend) over a back mass. Lines, shade and highlights follow from rules (below). 4 rounds of placement against the compare view | 11:55 AM-12:09 PM, 14 min |
| 6. Shading pass | Raised the skin shadow area toward mid strength (section "Shading") | 12:05-12:09 PM |
| 7. Compare and checks | `a3_compare.py`, an independent re-read of both PNGs, and this report | 12:09-12:20 PM, 11 min |

Times come from the file times and `date` calls. About 50 minutes in total.

### The face (shared by H1 and H2)

- **Eyes:** 3 rows tall with a sloped upper lid (the Super Saiyan glare). Iris 57, pupil 167, iris light 149, whites 2. Each iris is 3 px (2 rows). The left iris is at x 25-26, the right at x 38-39 (mirrored about x 32).
- **Brows:** hair colours (23 line, 44 and 128 fill). They slope down to the nose and touch the inner end of the upper lid, as in the anime.
- **Nose:** a 115 and 116 shade line on the right of the bridge (x 32, rows 40-42), then 116, 113, 116 at the tip (row 43).
- **Mouth:** 116, 113 x3, 116 at row 45. The lower lip shadow is 115 x3 at row 47.
- **Cheek lines under the eyes:** 115 on the lit side, 116 on the shadow side (row 40).
- **Ears, neck and gi:** both ears in 113 outline with 115 and 116 inside. The neck has 113 sternocleidomastoid lines, a 116 cast shadow under the jaw, and 117 at the deepest point (2 px). The collarbones are 113 near the shoulders and 116 toward the centre. The gi is 32 lit and 33 shade, with 113 edges.

### The hair rules (`a2_paint.py`, step 2-3)

1. Each strand is a curved centre line (a quadratic Bezier with a sideways bend) plus a width profile. H1: `w * (1 - t) ** 0.7` (straight taper to a point). H2: `w * (1 - t * t) ** 0.6` (stays wide, then a blunt round end). H2 is made from H1 by `soften()`: 0.88 of the length, 1.08 of the width, 1.6 of the bend.
2. A `CAP` polygon is the back hair mass. Later strands lie in front of earlier ones.
3. A strand pixel that touches (4-way) a strand behind it, the skin or the background is a line pixel (23). The frame crop never makes a line, as in id 65. L-corners are trimmed. A last pass (`thin_blocks`) breaks every 2x2 block of line pixels by turning one hair line pixel into shade 128 (H1: 17 px, H2: 16 px).
4. Shade 128: the far shadow side of a strand (more than 0.4 of its half-width), a 1 px rim where a line lies to the right or below, and the strand root (first 8 %).
5. Highlight 43: one stroke per strand, on the lit side at 0.45 of the half-width, from 20 % to 70 % of its length. Only the longest connected piece is kept. So every highlight lies inside one strand and runs along it.
6. Skin right under the hair steps 114 to 115 (cast shadow), 2 rows on the right half.

---

## Palette indices

**Used by H1 and H2 (both the same set, CONFIRMED):** 2, 9, 10, 11, 12, 13, 23, 32, 33, 43, 44, 57, 91, 92, 113, 114, 115, 116, 117, 128, 149, 167, 225, 233. All are id 65 indices. Never 0 or 168.

| Role | Index |
|---|---|
| Skin lit, mid, shadow, deep | 114, 115, 116, 117 |
| Skin and gi line | 113 |
| Hair line, base, highlight, shade | 23, 44, 43, 128 |
| Eyes | 2 white, 57 iris, 167 pupil, 149 iris light |
| Gi | 32 lit, 33 shade |
| Background (copied per pixel from id 65, else the nearest id 65 background pixel) | 233, 92, 225, 91 |
| Frame (copied from id 65) | 2, 9, 10, 11, 12, 13 |

Id 65 indices left unused: 95 (1 px of background), 211 and 215 (the navy undershirt; this crop shows none).

**Substitutes (goku_mid_A colours that id 65 does not have), CONFIRMED by nearest RGB:**

| Mid colour | Role in mid | Nearest id 65 index | Used |
|---|---|---|---|
| 16 (240,216,168) | skin lit | 114 (248,184,168) | 114 |
| 45 (248,248,120) | gold hair lit | 44 (248,248,184) | 44 |
| 36 (248,232,88) | gold hair base | 128 (200,184,120) | 44 as base, 128 as shade |
| 38 (248,176,40) | gold hair shadow | 32 (248,112,0), gi orange | **128, not 32**: a deviation. 32 is the gi orange and would make the hair read orange. 128 is id 65's own hair shade |

---

## Shading strength (CONFIRMED numbers, `a2_paint.py` output)

| Portrait | Lit / main shadow | Main gap | Weighted gap | Shadow share of skin | Skin range |
|---|---|---|---|---|---|
| goku_mid_A | 16 / 115 | 46.9 | 51.7 | 0.50 | 102.3 |
| H1 | 114 / 115 | 30.5 | 38.3 | 0.38 | 86.0 |
| H2 | 114 / 115 | 30.5 | 38.4 | 0.38 | 86.0 |

- With id 65's indices, the lit skin must be 114. The pair 114 / 115 gives only 30.5, the value I called "looks like the original". So I got the strength from area and steps instead: 115 for the cel shadow, 116 cores, 117 at 2 px.
- **The result is still softer than mid. CONFIRMED** (weighted gap 38 against 51.7, shadow share 0.38 against 0.50). A stronger look needs 116 as the main shadow (gap 55.4, the pink-tan pair the soft report dropped for hue) or the peach 16 that id 65 does not use.

---

## Hair strand map

Strand labels per pixel: `scripts\one-time\2026-10-19-portrait-from-anime\anime\a2_H1.txt` and `a2_H2.txt` (second block; 0 = back mass, 1-9 and A-G = the strands below). The first block of each file is the full letter map.

| Label | Strand | Root (x, y) | H1 tip | Root half-width H1 | Bend H1 |
|---|---|---|---|---|---|
| 1 | L0, low left, down-left | (19, 30) | (8, 44) | 5.0 | 0.04 |
| 2 | L1, down-left | (20, 26) | (1, 37) | 6.0 | -0.10 |
| 3 | L2, left | (21, 20) | (-2, 20) | 7.0 | -0.12 |
| 4 | L3, up-left | (23, 15) | (2, 1) | 7.5 | -0.08 |
| 5 | T4, up | (28, 13) | (16, -6) | 7.0 | -0.04 |
| 6 | T5, centre up | (33, 12) | (32, -6) | 7.5 | 0.0 |
| 7 | T6, up | (37, 13) | (48, -6) | 7.0 | 0.04 |
| 8 | R7, up-right | (41, 15) | (63, 0) | 7.5 | 0.08 |
| 9 | R8, right | (43, 20) | (66, 19) | 7.0 | 0.12 |
| A | R9, down-right | (43, 26) | (62, 35) | 6.0 | 0.10 |
| B | R10, low right | (44, 30) | (54, 43) | 5.0 | -0.04 |
| C | Fo-L, outer left lock | (25, 15) | (18, 32) | 4.5 | 0.12 |
| D | Fi-L, inner left lock | (29, 15) | (25, 30) | 3.5 | 0.10 |
| E | Fo-R, outer right lock | (39, 15) | (46, 31) | 4.5 | -0.12 |
| F | Fi-R, inner right lock | (35, 15) | (39, 30) | 3.5 | -0.10 |
| G | F-tuft, widow's peak | (32, 12) | (32, 19) | 2.5 | 0.0 |

- The side strands sag in the middle, so their tips rise (a flame shape). Top strands run past the frame, so the frame crops them, as in id 65.
- H2 uses the same roots. Its tips are at 0.88 of the length, half-widths x1.08 and bends x1.6.
- Highlight angle to its own strand axis: H1 at most 10.7 degrees, H2 at most 5.2 degrees. **CONFIRMED** (script output; the check limit is 30).

---

## Checks (CONFIRMED; the script stops on a failure, and a separate re-read agrees)

- Both PNGs: mode P, 64x64, 4096 bytes, palette equal to the OBJ palette `rom:0x1DA6C8`.
- Every index is one id 65 uses. None is 0 or 168.
- Every frame pixel (rows and columns 0-2 and 61-63) equals id 65.
- No `?` cell is left. No 2x2 block of line pixels is left (113 or 23).
- Every highlight pixel lies in one strand, as one connected stroke, within 30 degrees of the strand axis.
- Pixels that differ: H1 from id 65 2092, H2 from id 65 2077, H1 from H2 840.

---

## Honest rating (my judgment from the compare sheet at 4x and 1x, LIKELY)

| Point | H1 | H2 |
|---|---|---|
| Reads as Super Saiyan Goku at 1x | Yes | Yes |
| Eyes, brows, mouth read at 1x | Yes: the glare and green irises read. The mouth is faint | Same face |
| Hair | Spiky, but too regular: a fan of similar strips around the head. The strand tips are even, unlike the anime's mixed sizes | Softer and calmer. The round ends show on the side and front locks only |
| Against id 65 | **Weaker as a drawing.** Id 65's strands vary in size and curve. Mine look generated. Id 65's face is narrower and has more shape | Same |
| Against the anime | Closer than id 65 in proportion: the tall forehead, the front-facing glare, the locks that frame the forehead | Closer to the anime's lock shapes than H1 |

- **Overall: a working test, not ship-ready.** I rate H1 about 5 of 10 and H2 about 5.5 of 10 against id 65 as 8.
- **H1 and H2 look alike at 1x.** They differ in 840 px, mostly at strand tips and widths. I may not see much of a difference in game.
- The lit face is broad and flat, because the face shading is lighter than mid (see Shading).

---

## Concerns

1. **The hair looks generated** (even, radial strands). A real fix is hand edits per strand tip, or more strands of mixed sizes. The `PATCH` table in `a2_paint.py` is empty and ready for single pixel fixes. (LIKELY, by eye.)
2. **Shading is below mid strength. CONFIRMED** (weighted gap 38 against 51.7). With id 65's skin indices, only 116 as the main shadow (the pink-tan pair) gets closer. That needs my choice.
3. **Hair shade 128 is not the nearest-RGB substitute for mid's 38** (that is 32, the gi orange). I chose id 65's own hair shade. (CONFIRMED colours; the choice is mine.)
4. **The crop gives a wider face than id 65** (eye spacing 12.7 against 10 px), because it keeps the anime proportions. (CONFIRMED measure.)
5. **No in-game test.** Nothing was built or patched. The status twin was not made (not asked).
6. **The face is typed by hand in `a2_paint.py`, not traced.** The anime's line positions came from the grid view. The left and right eyes are mirrored about x 32, so the face is more symmetric than the anime frame. (CONFIRMED in the code.)

---

## Scripts for the next character (for example Perfect Cell, id 40)

All run with `py -3 -I -B` from any folder (they use absolute paths from their own location). Each new `.py` file is LF only, ASCII, with no byte order mark.

| Script | Use | Change for a new character |
|---|---|---|
| `scripts\one-time\2026-10-19-portrait-from-anime\anime\a0_unpack.py [pid ...]` | Unpacks ROM portraits, prints index counts and lumas, writes a 12x labelled view | Pass the id: `a0_unpack.py 40` |
| `scripts\one-time\2026-10-19-portrait-from-anime\anime\a1_guide.py` | Crop and shrink at the framing of a ROM portrait; prints the class map and line map | The `NAME`, `REF`, `FRAME_ID` and `CROP` block at the top. Set `CROP` so the eye row, face centre and chin match the ROM portrait. `klass()` holds the colour classes (Cell needs green and black classes in place of hair) |
| `scripts\one-time\2026-10-19-portrait-from-anime\anime\a1_gridview.py x0 y0 x1 y1` | The anime crop with the game grid over it, to read line positions in game pixels | Nothing (it reads `a1_guide`) |
| `scripts\one-time\2026-10-19-portrait-from-anime\anime\a2_paint.py` | The drawing: face letter runs, hair strands, rules, checks | The `INDEX` letter map (ROM portrait's indices), the face tables (`SPANS`, `EARS`, `FACE_*`, `NECK_*`, `BODY`), and the strands. Cell has no hair: his head crest could use the same strand rules |
| `scripts\one-time\2026-10-19-portrait-from-anime\anime\a3_compare.py` | The compare sheet | `STYLE` (the style reference) |

Working views (not deliverables): `scripts\one-time\2026-10-19-portrait-from-anime\anime\view_*.png`, `a0_unpack.txt`, `a1_guide.txt`, `a2_H1.txt`, `a2_H2.txt`.

---

## Bible rows (for me to add; I did not edit `docs\RE-BIBLE.md`)

| Topic | Fact | Label |
|---|---|---|
| Portrait id 65 (Goku Super Saiyan) indices | 27 OBJ indices: skin 114, 115, 116 (117 x2), line 113; hair 44, 43, 128, line 23; eyes 2, 57, 167, 149; gi 32, 33, navy 211, 215; background 92, 225, 91, 233, 95; frame 2, 9, 10, 11, 12, 13 | CONFIRMED |
| Portrait id 65 framing | Picture area x 3-60, y 3-60. Eye row 36, face centre x 32, chin row 51, iris centres about x 27 and x 37 | CONFIRMED |
