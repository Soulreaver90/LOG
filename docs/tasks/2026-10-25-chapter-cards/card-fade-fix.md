# Chapter cards v7: smooth fades by palette scaling (option B) (final, 2026-10-30 5:21 PM)

Read `LOG\README.md`, `docs\tasks\global.md`,
`docs\tasks\2026-10-25-chapter-cards\card-fade-report.md` (the whole report, option B and its test plan),
`chapter-cards-v6-report.md`, `scripts\permanent\patches\chapter_cards.py`, `tests\test_chapter_cards.py`, the bible
rows tagged CHC, CH5, CH6, CH7, R40, and the proposed rows in `scripts\one-time\2026-10-25-chapter-cards\bible_rows_fade.md`.

## My words

"The fades are very jaggy. In Buu's Fury the fade in and out are smooth." Then: "did we look into fixing the chapter fade".

## Task

1. Change `chapter_cards.py` to option B of the fade report: `card_enter` writes a black BG palette and sets BLDCNT 0.
   `card_tick` scales the card's BG palette every frame with L = (frame << 8) / FADE_IN on the fade in and
   L = 256 - ((frame - (FADE_IN + WAIT)) << 8) / FADE_OUT on the fade out, as BF ext 121 and ext 120 do (channel x L >> 8,
   or the B8 variant if it is cheap and exact). Keep the 100 / 250 / 100 timing, the song, the leave path and every
   exit path. Do not touch the OBJ palette or the HUD. Card 4's in-field fades (ext 40 and ext 41) stay as they are.
2. Prove the frames: run the tick in our interpreter over all frames and compare each frame's BG palette with BF's
   formula on the same source colours. Give the per-frame step count (target: a change on about 97 of 100 frames, no
   change bigger than 1 level). Prove frame 0 of the fade in is black (no full-colour flash).
3. Update the tests the report names (`test_tick_has_bf_timing`, `test_enter_draws_the_card_and_starts_the_ported_song`,
   `test_leave_restores_file_select_registers_and_frees_the_object`) to the new behaviour, and add the first-frame test
   and a step-count test. No test may be weakened to pass: if one fails for a real reason, stop and report.
4. Build on r40 (the trial list is `scripts\permanent\build_list_trial_chapters.txt`, which includes main):
   `builds\mockups\2026-10-25-chapter-cards\log2_poc_r40_chapters_v7.gba`, exclusive create, plus `_v7_pre_a.gba` and
   `_v7_pre_b2.gba` as copies, and `.sav` byte copies of the matching v6 r40 saves. Diff v6 r40 to v7: every run inside
   a chapter_cards site. Give SHA-1s.
5. Full suite once at the end.

## Report

`docs\tasks\2026-10-25-chapter-cards\card-fade-fix-report.md`: SHIPPED and PENDING tables, the code change, the frame
proof table, the tests changed (old to new), SHA-1s, diff runs, suite count. Label claims CONFIRMED, LIKELY or
SPECULATIVE. Bible rows (tag CHF2) as `## Section N` table blocks in `scripts\one-time\2026-10-25-chapter-cards\bible_rows_fade_fix.md`.

## Limits

- Edit only `chapter_cards.py` and `tests\test_chapter_cards.py`. Scripts go in
  `scripts\one-time\2026-10-25-chapter-cards\` with names starting `fadefix_`. Python: `py -3.14 -P`. LoG II base ROM:
  `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba`; BF: `data\roms\Dragon Ball Z - Buu's Fury (USA).gba`.
- Never write under `data\`. Never overwrite a ROM, save or state: check absence first and use exclusive create. LF, no
  em or en dashes. Never `cd`, `Set-Location` or `Push-Location`: absolute paths in every command, including scripts
  that open files.
- Other tasks: a card 4 study (read only, `c4_` files) and a Krillin study. Do not touch their files,
  `docs\RE-BIBLE.md`, `docs\ledger\` or `LOG\zhack\`.

