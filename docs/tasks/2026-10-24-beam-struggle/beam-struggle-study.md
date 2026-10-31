# A grander Kamehameha beam struggle: study (final, 2026-10-24 9:05 PM)

Read `LOG\README.md`, `docs\tasks\global.md` and the
bible rows on effects, OBJ VRAM, scenes and the Cell Games (tags EFX, CJR, CJT, CGS, SPA, BFS, HKS).

## My ask (verbatim)

"The kamehameha beam struggle at the end was always a bit lame with how tiny they are. Especially compared to the
manga/anime. Buu's Fury intro has a screen shot of a larger beam struggle. I wonder if we can draw and replace it
with something more grand?"

What he showed (described, the images are not on disk):
- **Buu's Fury intro, frame 1:** Cell and SSJ2 Gohan at the screen edges, each firing a thick glowing blue-white beam
  with a bright core; the beams meet in the middle in a large tan starburst burst.
- **Buu's Fury intro, frame 2 (text box "Goku's son, Gohan was able to tap into his deepest powers and finally
  destroy the monstrous Cell."):** a big white-blue glowing sphere at the meeting point, with smaller ki orbs around
  it and the starburst behind.
- **Anime and manga panels (inspiration only, never traced or copied):** the beams are thin lines feeding a huge
  dome of light that dwarfs both fighters; debris flies outward.

## Task (study only: no patch, no build-list change)

1. **Vanilla LoG II struggle:** find the scene (script records, the ext ops it calls), and how the beams and the
   clash are drawn (OBJ effect sets, BG layer, palette, sizes, frame counts, timing). Quote addresses.
2. **Buu's Fury intro struggle:** in the BF ROM (`data\roms\`, read only) and the BF disasm the bible names, find how
   the intro draws it: BG tiles or OBJ, tile and palette data, sizes, how the sphere grows. Quote addresses.
3. **Options**, each with effort, VRAM and OAM cost, risk and what I must draw:
   - A. Port the BF intro struggle art (BF is the official sibling game; its art is ours to reuse, as with the HUD).
   - B. Bigger beams and a new clash effect drawn by me (I draw the art, so the plan needs canvas sizes and palette slots).
   - C. A mix: BF beams plus a new growing dome.
   Include whether a BG layer can carry the dome (it is big) while OBJ carries beams and fighters, and what the text
   box in that scene needs.
4. Recommend one option as a trial patch module design (my rule: mockups are trial patch modules built through a
   second build list), with the bytes and data it would add. Do not build it.
5. If a frame-accurate check needs an emulator, list the exact states and steps for me.
6. Bible rows (tag BMS) as `## Section N` blocks in `scripts\one-time\2026-10-24-beam-struggle\bible_rows.md`.

Label every claim CONFIRMED, LIKELY or SPECULATIVE and quote the proving line or address.

## Report

`docs\tasks\2026-10-24-beam-struggle\beam-struggle-report.md`: SHIPPED and PENDING tables, the vanilla and BF findings,
the options table, the recommendation and my drawing list (if any).

## Limits

- Read only, except your report, rows file and study scripts and renders (in
  `scripts\one-time\2026-10-24-beam-struggle\`). Renders of found graphics are welcome there.
- Other work is changing `scripts\permanent\patches\celljr_fight.py`, its tests and `build_list_trial.txt`, and the
  I am editing `art\base-audit\`. Do not touch them.
- Never write under `data\`. Python: LF, no em or en dashes, `py -3 -P`. Never `cd`, in any shell; absolute paths only.

