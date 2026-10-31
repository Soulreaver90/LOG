# Portrait from manga art: Perfect Cell, id 40 (final, 2026-10-19 7:34 PM)

Personal GBA ROM hack (Legacy of Goku II, USA), not distributed. Read first:
- `docs\tasks\2026-10-19-portrait-vector\portrait-vector-report.md` (the full-size method and its "Face pass" and "Detail pass" sections),
- the scripts in `scripts\one-time\2026-10-19-portrait-from-anime\anime\`: `a1_guide.py` (crop, frame mask), `a5_dump65.py` (portrait colors, takes an id), `b1_label.py`, `b2_vector.py`, `b3_raster.py`, `b4_face.py`, `b5_detail.py`, `e0_owner_pack.py`,
- `docs\RE-BIBLE.md` section 5a (portrait format: 64x64 8bpp, the OBJ palette `rom:0x1DA6C8` shared by all dialog portraits).

## My ask, word for word

"Can we do cell now? Same process you did to get to vec 4 + what you learned and then I go from there with a x64 copy of that and the ref framed."

The Goku Super Saiyan portrait (id 65) went this way: the pipeline made vec4 (b1 to b5), I finished it by hand in about 120 pixels, then swapped the lit skin color. He called vec4 "very very close". Every redraw of facial features by a task or I was rejected ("looks like a preschool child drew it", "doesn't look like him"). So: no redraw by judgment. The pipeline output plus my rules below is the whole job.

## Sources

- Reference: `art\portrait-sources\remaster\refs\cell_ref.jpg` (395x395 JPEG, manga color, Perfect Cell front view, sky and a cloud behind). Read it as data only.
- Target: dialog portrait id 40 (Perfect Cell). Unpack it with the existing tools. Its 28 colors (`a5_dump65.py 40`) are the target colors: crest greens, black and navy for the dome, purples, the yellow-orange jaw piece, reds (background and eyes), greys and whites for the face and body, the grey frame.
- Framing: match vanilla id 40 (eye row, face center, chin row, as `a1_guide` did for Goku against id 65). I may later ask for a tighter crop; keep the crop a single setting.

## My rules (from my touch-up of the Goku vec4, apply them in the pipeline)

1. Dark line (the target's darkest line color) along the lower edge of each eye, and the eye outline carried to the outer corners.
2. Short dark lines where the anime has creases at the inner eye corners and the brow.
3. Shape small forms such as the nose with tone steps, not with more lines.
4. Body lines (neck, collar, chest, armor plates) run all the way to the bottom edge, and plate edges are outlined.
5. Close small gaps in long contour lines.
6. Colors: only indices the target portrait already uses, plus at most a plain swap my ask for later. No despeckle, skip-fix or ramp-shift passes on the face (those made Goku's face look "diseased").

## Task

1. Make the scripts take a character without breaking Goku. Put each character's settings (ref, target id, crop, seeds, eye and mouth boxes, ramps, zones) in one place, for example a `chars\` module per character, selected by an argument. Proof: the Goku run rebuilds `goku_ssj_vec4.png` byte for byte the same.
2. Run the method for Cell: label at full size (extend the label set as Cell needs, for example crest, crest spots, dome, dome highlight, face, cheek purple, jaw piece, eye, body), vectorize, draw at 64x64 from the vectors in id 40's colors, then the face and detail passes with the rules above. The cloud and sky become id 40's own background pixels.
3. Stop at the vec4 stage: `art\portrait-sources\remaster\anime\cell\cell_vec.png` (indexed, OBJ palette, 64x64; frame equal to id 40's).
4. Edit pack in `art\portrait-sources\remaster\anime\cell\owner_edit\`, the same set as Goku's (`e0_owner_pack.py`, made to take the character): the 64x64 portrait, its 8x view, the reference framed at 64x64 and at 512x512 inside the portrait's own frame (picture area at game px 3..60, 24..488 at 8x), the 8x framed copy with the game grid, the full-size crop, and `id40_palette.gpl` plus `.txt` with the OBJ indices.
5. Compare sheet `cell\compare_cell_vec.png`: OLD (ROM id 40) | reference at the same framing | cell_vec, at 4x on lime (191, 255, 7), plus a 1x row. Look at it and rate it honestly.

## Tools

Installed: numpy, scipy, scikit-image, opencv-python, potracer, svgpathtools, Pillow. Run Python as `py -3 -P` (not `-I`). If one more pip package clearly helps, install it with `py -3 -m pip install --user <name>` and list it.

## Parallel run

- A build task writes `scripts\permanent\`, `tests\`, `builds\`, `scripts\one-time\2026-10-19-r21-build\` and `art\portrait-sources\remaster\final_r21\`. Do not touch them.
- You write only `scripts\one-time\2026-10-19-portrait-from-anime\anime\` (scripts) and `art\portrait-sources\remaster\anime\cell\`. Keep every existing file; the Goku files must not change.

## Limits

- No ROM build, no patch. Never write under `data\`. Never run anything downloaded.
- Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths. A shell heredoc collapses backslashes: write files with Python, and check text files for control characters.

## Report

Save it as `docs\tasks\2026-10-19-portrait-cell\portrait-cell-report.md`: the character setup, the label list, the crop and why, how each of my rule was applied, the checks (indices in id 40's set, frame equal, Goku vec4 rebuild identical), the compare path, the pack contents and your honest rating. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with the compare path, the pack path and concerns only.

