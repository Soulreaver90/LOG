# Chapter card fades: why ours step and BF's are smooth (final, 2026-10-30 3:30 PM)

Read `LOG\README.md`, `docs\tasks\global.md`, the
chapter card reports in this folder (v3, v5, v6), `scripts\permanent\patches\chapter_cards.py` (its fade code and the
100 / 250 / 100 timing), `bf_card_ext_ops.txt` in `scripts\one-time\2026-10-25-chapter-cards\`, and the bible rows
tagged CHC, CH2, CH3, CH5, CH6, CH7.

## My words

"There is an issue with the cards, the fades are very jaggy. In Buu's Fury the fade in and out are smooth, but the
fade in the game seems like it's in steps, not smooth."

## Task (study only: no module, list or ROM change)

1. **BF.** How Buu's Fury fades the card in and out (ext 121 and ext 120, 100 frames each): the code, the hardware
   used (BLDY brightness with 17 levels, BLDALPHA, palette interpolation per channel with 32 levels, or another way),
   how often it updates (every frame or every n frames), and the resulting number of visible steps over 100 frames.
2. **Ours.** The same for our card fades (in, out, and the card 4 in-field fade): the code path, the hardware, the
   update rate and step count. Use our interpreter or a frame model to list the per-frame values for both games.
3. **Why ours steps.** Name the cause with evidence (for example BLDY with 16 levels updated every 6 frames, an integer
   rounding, a coarse palette step, or an update only on some frames).
4. **Fix options.** For each: what changes, bytes or code, whether it matches BF's look, risk (other scenes, the HUD,
   OBJ layers), and test plan. Recommend one.

## Report

`docs\tasks\2026-10-25-chapter-cards\card-fade-report.md`: SHIPPED and PENDING tables, the BF method, ours, the cause,
the options and the recommendation, with per-frame tables. Label claims CONFIRMED, LIKELY or SPECULATIVE with
addresses. Bible rows (tag CHF) as `## Section N` table blocks in `scripts\one-time\2026-10-25-chapter-cards\bible_rows_fade.md`.

## Limits

- Read only, except your report, rows file and scripts (in `scripts\one-time\2026-10-25-chapter-cards\`, names starting
  `fade_`). Python: `py -3.14 -P`. LoG II base ROM: `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba`; BF:
  `data\roms\Dragon Ball Z - Buu's Fury (USA).gba`. Never write under `data\`. LF, no em or en dashes. Never `cd` or
  `Push-Location`; absolute paths only.
- Another task is building r40 (it edits `log2_build.py`, the build lists and tests). Do not touch them,
  `chapter_cards.py`, `docs\RE-BIBLE.md` or `docs\ledger\`.

