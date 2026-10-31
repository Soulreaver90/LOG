# Session 1: Super Perfect Cell aura art and previews (final, 2026-10-22 8:50 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Base: the latest main-line build in `builds\` (r29 if the Piccolo scene build has landed, else r28 `eef01cf6`). Read first: `docs\tasks\2026-10-22-superperfect-study\superperfect-study-report.md` (the design: bake bolts about 2x Gohan's into a copy of set 30, reuse set id 58, idle hook flicker, the 64x64 box limits, the face concern), `scripts\permanent\art\gi_aura.py` (how Gohan's bolts are baked), `patches\ssj2_idle.py` (the bolt flicker hook), `scripts\permanent\rom\log2_sprites.py`, and `docs\RE-BIBLE.md` rows tagged SPC.

## My ask

"Work on the Super Perfect Cell aura sprite so he has it when he comes back after self destruct." He wants Cell's own sprite with the electric aura Gohan has in Super Saiyan 2, bumped up in size for the bigger sprite.

## Task (art and previews only; the patch is session 2)

1. Export set 30 (Cell) frames. Write `scripts\one-time\2026-10-22-superperfect-study\cell_aura.py`: bake bolts in Gohan's style (same colors and shapes family as `gi_aura.py`), scaled about 2x, into a copy of every frame of the anims Cell uses in the stretch (scenes and the last fight; list them from the study). Stay inside each frame's box and the 64x64 limit. Bolts never cover his face: define a Cell face rule from his real eye and face pixels (check the study's SPECULATIVE index 209 against the frames, by eye on a zoomed sheet).
2. Make three bolt scales (about 1.5x, 2x, 2.5x) so I can pick, each with the three-shape flicker cycle Gohan's idle uses.
3. Output to `art\cell_aura\scale_15\`, `scale_20\`, `scale_25\` (PNGs plus manifest in the `log2_sprites` format, so session 2 can build set 58 from the chosen folder), and previews for me in `archive\2026-10-18-art-review-renders\cell_aura\`: per scale, an animated GIF of idle (with flicker), walk and one attack, at 4x on a dark and a light background, plus a side-by-side sheet of plain Cell vs the three scales.
4. Do not build a ROM and do not change `scripts\permanent\`.

## Limits

- One task runs at a time; nothing else is running when you start. Never write under `data\`. Never overwrite a ROM, .sav or state. Read-only on every ROM.
- Python: LF, no byte order mark, no em or en dashes. Code style: a header block, short functions, precise names, 1-2 line comments for the non-obvious why only. Never `cd` in any shell call; absolute paths only. Write each file with Python. Tools installed with pip --user load with `py -3 -P`.
- Art is judged by my eye: show, do not decide. Label technical findings CONFIRMED, LIKELY or SPECULATIVE.

## Report

Save it as `docs\tasks\2026-10-22-superperfect-aura\superperfect-aura-report.md`: the anims covered, the face rule, the three scales, where the previews are, and what session 2 needs. Then reply with the preview paths, the face rule and concerns only.

