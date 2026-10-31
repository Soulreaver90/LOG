# Portrait from anime art: Goku Super Saiyan, id 65 (final, 2026-10-19 11:31 AM)

Personal GBA ROM hack (Legacy of Goku II, USA), not distributed. Read first: `docs\tasks\2026-10-19-portrait-soft\portrait-soft-report.md` (the "mid" method the approved), `scripts\one-time\2026-10-19-portrait-from-anime\k1_soft.py`, `docs\RE-BIBLE.md` section 5a (portrait format, OBJ palette `rom:0x1DA6C8`), `docs\research\re-portraits.md`.

## My ask, word for word

- "If I were to get a photo, is it possible to create a LOG style portrait?"
- "Maybe with the softer hair, a mid between the spiky and soft."
- "That is from the anime directly. I added another pose just for the correct color, but the color should already be in the game original portrait."
- Earlier verdicts that still hold: "mid is great!" (the mid shading of `art\portrait-sources\remaster\final_r20\*_mid_A.png`); shading, not "studio lighting"; OBJ palette for all portraits.

## Sources

- Drawing source: `art\portrait-sources\remaster\refs\r6_owner_anime_goku_ssj_front.png` (anime frame, front view, Cell saga Super Saiyan Goku).
- Color check only: `art\portrait-sources\remaster\refs\r7_owner_anime_goku_ssj_color.png`. Do not take its pose.
- Game original: dialog portrait id 65 (Goku Super Saiyan). Unpack it from the USA ROM with the existing tools (`scripts\permanent\patches\gohan_portraits.py`: `portrait()`, `palette()`, `OBJ_PAL`). Its colors are the target colors.
- Style target: the game's own portraits (id 65, 63, and our `final_r20\goku_mid_A.png`): 64x64, head and shoulders, the frame and background of id 65, 1 px dark outlines, flat cel areas with 2-3 shade steps.

## Task

1. Crop the front frame to head and shoulders at the framing of id 65 (compare the head size and position).
2. Build a new 64x64 drawing from the anime frame. Do not just shrink it: a straight downscale smears the eyes and mouth. Use the downscale as a guide, then set the outline, eyes (2-3 px), brows, nose, mouth and hair strands pixel by pixel by judgment.
3. Hair: two variants, so I can pick the middle. H1 is closer to the game's spiky id 65. H2 is closer to the anime's softer, rounder locks. Both keep clear strand lines, with highlights inside one strand along its direction, as in the Vegeta fix.
4. Colors: only OBJ palette indices that id 65 already uses, plus its frame and background indices. If a needed shade is missing, use the nearest OBJ palette index id 65 uses and list it. No new palette colors.
5. Shading at the "mid" strength of `goku_mid_A.png`.
6. Write the result as indexed PNGs (OBJ palette indices, `raw` type 0 ready, 64x64 8bpp row order): `art\portrait-sources\remaster\anime\goku_ssj_H1.png` and `goku_ssj_H2.png`. Check: every pixel index is one id 65 uses; size 64x64.
7. Compare sheet at 4x on lime (191, 255, 7): `art\portrait-sources\remaster\anime\compare_goku_ssj.png`: OLD (ROM id 65) | anime crop shrunk to 64x64 (plain, for reference) | H1 | H2 | our goku_mid_A (style reference). Also one 1x row, as seen in game. Look at it yourself and rate it honestly.
8. Note the scripts you wrote, so the same steps work for the next character (Perfect Cell, id 40, is a likely next test).

## Limits

- No ROM build, no patch, no change outside `art\portrait-sources\remaster\anime\` and `scripts\one-time\2026-10-19-portrait-from-anime\anime\` (create both). Never write under `data\`.
- The refs are references for this personal hack. Never copy pixels from other mods. Never run anything downloaded.
- Install nothing. Python: LF, no byte order mark, no em or en dashes. Never `cd`; use absolute paths. A shell heredoc collapses backslashes: write files with Python, and check text files for control characters. Run Python with `py -3 -I` when it reads the refs.

## Parallel run

- Nothing else is running. I do not edit your two folders while you run.

## Report

Save it as `docs\tasks\2026-10-19-portrait-from-anime\portrait-from-anime-report.md`: the method step by step, the palette indices used (and any substitutes), the hair strand map for H1 and H2, the checks, the compare path, your honest rating, and how long each step took. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with the compare path and concerns only.

