# Super Perfect Cell portrait (id 52): pipeline draft and my edit pack (final, 2026-10-23)

Personal GBA ROM hack (Legacy of Goku II, USA). Current build: r34 (`builds\log2_poc_r34.gba`). The Super Perfect Cell dialog and scouter lines already use portrait id 52, which shows id 40's face until I inject a new 52.

## My ask

"I want to create a new super perfect cell portrait with this. Would you be able to use the images to create a portrait I can do a final edit of? Also with the electrical aura around him, maybe 2-3 of them."

Refs (my files): `art\portrait-sources\remaster\refs\superperfect\` (two .avif, one .webp, one .jpg). Convert them to PNG copies in your work folder; never change the originals.

## Read first

- My notes on this pipeline hold the method and the lessons. Follow them: full-size pipeline `scripts\one-time\2026-10-19-portrait-from-anime\anime\b1_label.py` to `b5_detail.py`, stop at the vec4 stage, apply its line rules, then the edit pack with `e0_owner_pack.py`. Do NOT hand-redraw eyes or features by judgment.
- The earlier Perfect Cell portrait work (id 40): `f4_cell_check.py`, `f7_cell_wip.py`, `f8_cell_final.py`, `art\portrait-sources\remaster\refs\cell_ref.jpg`, and the RE-BIBLE portrait rows (tags POR, CSP, SPC, R30). Match id 40's palette, framing, size (64x64) and style, so 52 reads as the same character.
- `scripts\permanent\art\inject.py` (`check` only; never `portrait`).

## Task

1. Pick the ref that best fits the 64x64 frame and id 40's framing (say which and why; the others serve as color and line reference). The front-facing smirk is the target expression.
2. Run the pipeline to vec4 in id 40's palette. Skin and body colors as id 40 uses them.
3. Electric aura: 2-3 thin SSJ2-style bolts around him (not over the face or eyes), in the colors the game's SSJ2 bolts use (see `scripts\permanent\art\gi_aura.py`). Make two variants: 2 bolts and 3 bolts, so I can pick.
4. Edit pack per variant (`e0_owner_pack.py`): 64x64 indexed portrait, 8x view, ref framed at 64 and 8x with grid, .gpl palette. Run `inject.py check` on each and fix any off-palette pixel.
5. Put my files in `art\portrait-sources\remaster\superperfect\` (pack, previews next to id 40 at 4x).

## Limits

- One task runs at a time; I am editing `art\base-audit\` and `scripts\one-time\2026-10-23-base-audit\`: do not touch them. Never write under `data\`. No ROM build. Never run `inject.py portrait`.
- Python: LF, no byte order mark, no em or en dashes. Never `cd` in any shell call; absolute paths only. Write and edit files with the Write and Edit tools. Work scripts in `scripts\one-time\2026-10-22-superperfect-study\portrait\`. Tools installed with pip --user load with `py -3 -P`; installs are pre-approved (an AVIF reader if Pillow lacks one).

## Report

Save it as `docs\tasks\2026-10-23-superperfect-portrait\superperfect-portrait-report.md`: the ref chosen, the stages, the variants, the check results and the paths. Then reply with the pack paths and concerns only.

