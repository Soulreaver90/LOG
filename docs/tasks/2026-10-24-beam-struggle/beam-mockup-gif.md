# Beam struggle stage 1 (pulsing sphere): GIF mockup before any build (final, 2026-10-25 9:52 AM)

Read `LOG\README.md`, `docs\tasks\global.md`, the study
brief and report in this folder (`beam-struggle-study.md`, `beam-struggle-report.md`) and the bible rows tagged BMS.
Reuse the study scripts in `scripts\one-time\2026-10-24-beam-struggle\` (`render_struggle.py`, `bf_cutout.py`,
`anim_tiles.py`, `render_vanilla.py`); copy into new scripts, do not edit them.

## Final decisions (verbatim)

"Go with B. Can you make a gif mockup before we port to build?"

Option B: the BF sphere, orbs and beams on map 14,4 BG0 at the meeting point, with **3 pulsing frames** made by
shifting the sphere's light ramp brighter and dimmer (a shimmer). I draw nothing. The vanilla BG1 starburst
keeps its 2-frame cycle and the fighters keep their anim 18 pose.

## Task (mockup only: no patch, no ROM, no build-list change)

1. Make the 3 sphere frames on the LoG II BG palette only (no new colours; the study remapped BF light colours to
   LoG II BG indices). Pulse order 0-1-2-1, 10 game frames each, unless the vanilla spark timing suggests better.
   Trim the stray grey bit at the left beam tip (Cell's fingers in the BF cutout).
2. Render GIFs at the game's real timing (60 fps game frames; a 10-frame step = 167 ms), screen size 240x160 around
   the meeting point, at 3x with nearest-neighbour scaling:
   - `mockup_vanilla.gif`: the vanilla struggle (BG layers with blend, spark 3 frames, starburst 2 frames).
   - `mockup_b.gif`: option B.
   - `mockup_side_by_side.gif`: both, left vanilla, right B.
   Put Gohan and Cell in their anim 18 pose frames (state 30 timing from the report: frame 0 for 8 ticks, then 1 and 2
   every 8) if the sprite renders are reachable; otherwise leave the fighters out and say so.
3. Apply the BG1 starburst blend as the game does (BLDCNT `0x1C42`, EVA 8, EVB 16) so the colours match the screen.
4. Count the tiles the 3 frames need (one tile slot per map cell for an animated footprint; at most 64 tiles per
   animated group) and say whether they fit the free tiles 596-830 of 14,4.

## Output

GIFs and frame PNGs in `art\mockups\2026-10-25-beam-struggle\`. Scripts in `scripts\one-time\2026-10-25-beam-mockup\`.
Report `docs\tasks\2026-10-24-beam-struggle\beam-mockup-report.md`: what each GIF shows, the palette indices used, the
tile count and fit, anything that differs from the game (label CONFIRMED, LIKELY or SPECULATIVE).

## Limits

- Never write under `data\`. Python: LF, no em or en dashes, `py -3 -P`. Never `cd`, in any shell; absolute paths
  only.
- Other work is changing `vegeta_ssj_scene.py`, `relay_cooldown.py`, their tests and lists, and reading the disasm
  clone. I am editing `art\base-audit\` and `scripts\one-time\2026-10-23-base-audit\`. Do not touch them.

