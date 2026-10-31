# Chapter title cards: trial module (final, 2026-10-25 10:42 AM)

Read `LOG\README.md`, `docs\tasks\global.md`, the BF
survey report `docs\tasks\2026-10-25-bf-feature-survey\bf-feature-survey-report.md` (pick 4, `chapter_cards`) and the
bible rows tagged BFP, BFS, DIS and the sound rows.

## Final decisions (verbatim)

"YES! I love chapter titles, it's one of my favorite parts of Buu's Fury. We can carry over the same backdrop and
music but custom titles."

## Task

1. **BF chapter card study.** In the BF ROM (`data\roms\`, read only) find the chapter card scene (`0x0803369E`, wait
   `0x0803377C`), its backdrop (BG layers, tiles, map, palette, addresses), its music (song id, the song data and
   the sample data it uses) and its text layout (font, lines, centring). Render the BF card to PNG.
2. **Port path for the backdrop and the music.** BF and LoG II share an engine family. Check whether the LoG II sound
   engine can play the BF song as is (song header format, voice group format, sample format, table indexing). Say
   what must be copied and repointed. If the song cannot play in LoG II without engine code changes, stop at a
   design for the music and build the card with a LoG II song I can swap later; say which song you picked.
3. **Chapter starts.** Map each placeholder chapter below to the LoG II story flag or event that starts it (quote
   the flag and the script record). Mark any you cannot place.
4. **Trial module** `scripts\permanent\patches\chapter_cards.py` with tests `scripts\permanent\tests\test_chapter_cards.py`,
   in the style of the existing modules (header, source checks before the first write, a second run raises).
   - Trial trigger: Continue from file select shows the card for the save's current chapter (from the flag table),
     as the survey designed. Story-point triggers come after approval: design them, do not build them.
   - The titles are one data table in the module, easy to edit: `CHAPTERS = [(number, title, start flag), ...]`.
   - Card: the BF backdrop, the BF music (or the stand-in song), two centred lines ("Chapter N" and the title),
     about 128 frames or until A or B, as in BF.
5. New list `scripts\permanent\build_list_trial_chapters.txt` = the lines of `build_list.txt` plus `chapter_cards`. Do
   not edit any other list. `--list` must still give r39 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`.
6. Build `builds\mockups\2026-10-25-chapter-cards\log2_poc_r39_chapters.gba` (exclusive create) with a save copied
   from an existing build save (exclusive create, `.sav` next to the ROM); say which slots show which chapter.
7. Full suite once at the end. List the diff runs r39 to the new ROM.
8. Bible rows (tag CHC) as `## Section N` blocks in `scripts\one-time\2026-10-25-chapter-cards\bible_rows.md`.

Placeholder titles (I will edit):

| # | Title | Starts at (to confirm) |
|---|---|---|
| 1 | A Warning from the Future | New game |
| 2 | Three Years to Prepare | Training years, Dragon Ball quest |
| 3 | The Androids Attack | Androids 19 and 20 arrive |
| 4 | Dr. Gero's Lab | Chase to the lab |
| 5 | Androids 17 and 18 | Gero wakes them |
| 6 | Terror in Ginger Town | Cell appears |
| 7 | The Namekians Reunite | Piccolo fuses with Kami |
| 8 | Super Vegeta | Vegeta returns from the Time Chamber |
| 9 | Perfection | Cell becomes Perfect Cell |
| 10 | One Day, One Year | Gohan and Goku in the Time Chamber |
| 11 | The Cell Games | Arrival at the Cell Games |
| 12 | Gohan's Fury | Gohan goes Super Saiyan 2 |

Label every claim CONFIRMED, LIKELY or SPECULATIVE and quote the proving line or address. If a claim needs an
emulator run, say so and give my check steps.

## Report

`docs\tasks\2026-10-25-chapter-cards\chapter-cards-report.md`: SHIPPED and PENDING tables, the BF card facts, the music
port result, the chapter flag table, SHA-1s, diff runs, test counts, what to watch in play. Renders in
`scripts\one-time\2026-10-25-chapter-cards\`.

## Limits

- Never write under `data\`. Never overwrite a ROM, save or state. Python: LF, no em or en dashes, `py -3 -P`, and
  `py -3 -I` for scripts that read downloaded files. Never `cd`, in any shell; absolute paths only.
- Other work is changing `vegeta_ssj_scene.py`, `relay_cooldown.py`, their tests and lists, making beam mockups in
  `art\mockups\2026-10-25-beam-struggle\`, and reading the disasm clone. I am editing `art\base-audit\` and
  `scripts\one-time\2026-10-23-base-audit\`. Do not touch them.

