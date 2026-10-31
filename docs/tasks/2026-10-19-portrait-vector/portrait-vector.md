# Portrait from anime art, full-size method: Goku Super Saiyan, id 65 (final, 2026-10-19 12:36 PM)

Personal GBA ROM hack (Legacy of Goku II, USA), not distributed. Read first: `docs\RE-BIBLE.md` section 5a (portrait format: 64x64 8bpp, OBJ palette `rom:0x1DA6C8`), `scripts\one-time\2026-10-19-portrait-from-anime\anime\a1_guide.py` (crop, frame mask), `a5_dump65.py` (id 65 colors), `a6_ramp.py` (ramps and step shares).

## What failed, and why (my diagnosis)

- A hand redraw at 64x64 by a task: my verdict "terrible ... looks like a preschool child drew it". Do not redraw by judgment.
- Shrink first, then map to LoG colors (`compare_goku_ssj_conv_C.png`, `_conv_D.png`): me: "taking the high quality original and downsizing it loses all the details ... the task not knowing what is what". Averaging blurs line, eye, skin and hair into the same in-between colors.
- My direction: "draw it based on the full image and then vector downscale it to keep the details."

## Method

Work at full size, where the parts are clear, and only draw at 64x64 at the end.

1. Crop the anime frame `art\portrait-sources\remaster\refs\r6_owner_anime_goku_ssj_front.png` with `a1_guide.CROP` (x0 339, y0 -16, scale 5.5: the box that maps to the 64x64 picture). Keep it at full resolution (about 352x352). Optionally upscale 2x before labeling if it helps the tracer.
2. Label every full-size pixel: line art, hair, hair shadow, skin, skin shadow, eye white, iris, mouth, gi, gi shadow, undershirt, sky. Anime cels are flat colors: use color clustering (k-means or similar, OpenCV or scikit-image) and then name each cluster. Write a label image and look at it before going on (`view_labels.png`, flat false colors).
3. Vectorize:
   - Line art: thin it to a 1-pixel centerline (scikit-image `skeletonize`), then trace the centerlines into strokes (polylines or curves). potracer or your own path tracing.
   - Color areas: trace each label region into a shape (potracer or OpenCV contours). The anime's own cel shadow shapes are regions of their own.
   - Save the vector result as an SVG for inspection (`goku_ssj_vector.svg`) and a full-size render of it next to the crop (`view_vector.png`).
4. Draw at 64x64 from the vectors, not from pixels:
   - Fill each region with its LoG ramp color from id 65 (`a6_ramp.RAMPS`): base color for the lit area, the darker step for the anime shadow shape, the lighter step for highlights. Sky takes the id 65 background row shade (as in a6). Frame from id 65 (`a1_guide.frame_mask`).
   - Draw each stroke as a clean 1-pixel line, no doubled pixels, no anti-aliasing. Line color: 113 on skin and gi, 23 inside hair (id 65's hair line).
   - Minimum feature sizes: an eye at least 3 px wide and 2 px tall, with white and iris (id 65 greens 57 and 149); the mouth at least 2 px. Place them where the vectors put them.
   - Only OBJ palette indices that id 65 already uses (`a5_dump65.py 65`).
5. If a few face pixels still read wrong, list them and the fix you made. Keep hand fixes to the face and to under 30 pixels. Report the count.

## Output

- `art\portrait-sources\remaster\anime\goku_ssj_vec.png` (indexed, OBJ palette, 64x64).
- `art\portrait-sources\remaster\anime\compare_goku_ssj_vec.png`, 4x on lime (191, 255, 7) plus a 1x row: OLD (ROM id 65) | anime crop at full size, scaled to the same box | conv_D (the failed shrink) | vec (new). Look at it yourself and rate it honestly against id 65.
- Scripts in `scripts\one-time\2026-10-19-portrait-from-anime\anime\` named `b1_label.py`, `b2_vector.py`, `b3_raster.py` (one per step, header block per file, per-character settings at the top), so the steps run again for Perfect Cell (id 40) and later for sprites.

## Tools

Installed for this (pip --user, Python 3.14): numpy, scipy, scikit-image, opencv-python, potracer, svgpathtools, Pillow. Run Python as `py -3 -P` (not `-I`: `-I` hides the user packages). If one more pip package would clearly help, you may install it with `py -3 -m pip install --user <name>` and list it in the report. Nothing that needs admin rights.

## Limits

- No ROM build, no patch, no change outside `art\portrait-sources\remaster\anime\` and `scripts\one-time\2026-10-19-portrait-from-anime\anime\`. Never write under `data\`. Keep the earlier files there (H1, H2, conv_A-D); do not delete them.
- The refs are references for this personal hack. Never run anything downloaded.
- Python: LF, no byte order mark, no em or en dashes. Never `cd`; use absolute paths. The Bash tool collapses backslashes: Write each file with Python.

## Parallel run

- Nothing else is running. I do not edit your two folders while you run.

## Report

Save it as `docs\tasks\2026-10-19-portrait-vector\portrait-vector-report.md`: the steps, the label list with colors, the vector counts (strokes, regions), the hand-fix count, the compare path, and your honest rating. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with the compare path and concerns only.

