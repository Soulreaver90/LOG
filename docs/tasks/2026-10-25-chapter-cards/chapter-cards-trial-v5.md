# Chapter cards trial v5: 8 my chapters, cards at their story points (final, 2026-10-29 6:28 PM)

Read `LOG\README.md`, `docs\tasks\global.md`, every
brief and report in this folder (above all `chapter-placement-report.md`), the module
`scripts\permanent\patches\chapter_cards.py` and its tests, and the bible rows tagged CHC, CH2, CH3 and CHP. The module
is built through `scripts\permanent\build_list_trial_chapters.txt`. v4 (`7f3024f4`) shows a card on Continue only.

## Final decisions (2026-10-29)

8 chapters, own titles, the placement study's story points ("Proceed with these titles"):

| # | Title | Story point (from `chapter-placement-report.md`) | Continue flag |
|---|---|---|---|
| 1 | The Mysterious Youth | New game | none |
| 2 | Preparation | Fade 120 `rom:0x3BFDBB`, the Trunks warning scene ends, before SET 26 | 26 (`rom:0x3BFDBF`) |
| 3 | The Androids Appear | "Three years later..." fade 240 `rom:0x3B856D` | 68 (`rom:0x3B8571`) |
| 4 | Into Gero's Lab | End of the post-Android 20 scene, after SET 86 `rom:0x3D542A` (no fade) | 86 |
| 5 | A New Horror | Fade 90 `rom:0x3D9867`, Piccolo flies to Kami after the Android 18 fight | 127 (`rom:0x3D986F`) |
| 6 | Perfection | Fade 180 `rom:0x3E5ED7`, Roshi's Island to the Lookout after Cell absorbs 17 | 148 (`rom:0x3E605A`) |
| 7 | The Cell Games | Chamber exit time skip, fade 240 `rom:0x3DB4BB` (SET 154 `rom:0x3DB4B3`) | 158 (`rom:0x3DBDAA`) |
| 8 | The Champion's Hour | Fade 240 `rom:0x3EC67F`, after Cell | 195 (`rom:0x3EC6A2`) |

Dropped: Nightmare Comes True (125), His Name is Cell (129), Room of Spirit and Time, the old Cell Games point (191).
I approved the look (BF backdrop, font, song 37 port, 100/250/100 timing) and the music.

## Task

1. **Titles and Continue.** Update `CHAPTERS` and the tests. Card 7 plays at the 154 time skip, but Continue reads 158
   (the study: 158 is the chamber exit table's end flag). Check that a save made between 154 and 158 cannot exist, or
   say what Continue shows there.
2. **Story-point cards.** Make each card 2-8 also play once in the story, at its point above, the way BF does it
   (the study's design B: a `push N ; ext X` at the point, X the module's card op). The card plays after the scene's
   fade out (or, for 4, at the scene end) and before the next map fades in; the script then continues as before. A
   new game plays card 1 before the first scene. Find how a scene script op can run the card and return (the BF
   ext 183 model: study `bf_card_ext_ops.txt`), how to insert bytes into a scene record (record lengths, `next`
   words, any table offsets that move), and prove the scene still runs: decode each changed record before and after.
3. **No clash with the other trials.** List the scene tables and records each trial module changes (`celljr_fight`,
   `vegeta_ssj_scene`, `beam_struggle`, `relay_cooldown`, `fullpower_hud`), and show that no story-point insert
   touches the same record or moves bytes they patch. All of them go into one ROM soon (r40).
4. Keep its tests green and add tests: the 8 rows, flags rising, each insert decoded, each record still ends where its
   `next` word says. Run the full suite once at the end.
5. `--list` must still give r39 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`. Do not touch the other lists.
6. Build `builds\mockups\2026-10-25-chapter-cards\log2_poc_r39_chapters_v5.gba` with a copy of the v4 save as
   `log2_poc_r39_chapters_v5.sav` (exclusive create for both). If a save near a story point exists in `builds\` (for
   example just before the Android 20 scene or the chamber exit), name it and the slot, and give emulator steps.
7. Render all 8 cards as one sheet (BF BG palette `rom:0x5632C`) and view it. List the diff runs v4 to v5; every run
   inside a declared site.
8. Bible rows (tag CH5) as `## Section N` blocks in `scripts\one-time\2026-10-25-chapter-cards\bible_rows_v5.md`.

## Report

`docs\tasks\2026-10-25-chapter-cards\chapter-cards-v5-report.md`: SHIPPED and PENDING tables, the 8 cards with their
inserts (address, bytes before and after), the clash check, SHA-1s, diff runs, test counts, and play steps for the
me. Label claims CONFIRMED, LIKELY or SPECULATIVE and quote the proving line or address.

## Limits

- Python: `py -3.14 -P`. The default `py -3` is 3.15, which has no Pillow. The LoG II base ROM is
  `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba` (not the Europe file).
- Never write under `data\`. Never overwrite a ROM, save or state. Python: LF, no em or en dashes. Never `cd` or
  `Push-Location`, in any shell; absolute paths only. Scripts and outputs go in
  `scripts\one-time\2026-10-25-chapter-cards\`.
- Do not edit `celljr_fight.py`, `vegeta_ssj_scene.py`, `relay_cooldown.py`, `fullpower_hud.py`, `beam_struggle.py`, their
  tests, or any build list. Other work is changing `celljr_fight.py` and the SHA-1 pins in the vegeta tests now. If
  only their tests fail in your full suite run, say so and give the counts.
- I am editing `docs\RE-BIBLE.md` and `docs\ledger\`. Do not touch them.

