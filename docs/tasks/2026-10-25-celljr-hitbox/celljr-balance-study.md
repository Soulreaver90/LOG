# Cell Jr group fight balance: study (final, 2026-10-25 4:38 PM)

Read `LOG\README.md`, `docs\tasks\global.md`, the hitbox
study brief and report in this folder (`celljr-hitbox-study.md`, `celljr-hitbox-report.md`) and the bible rows tagged
CJH, CJR, CJT, CJ2, CJ3, FRM, T6 and any damage or stat rows the source list names.

## My report (verbatim)

"The other issue with the Jrs is that when you get them in a group and attack, the Jrs behind the one in the front
punch and hit, so it's hard to get close and fight them all at once. That and their stats do make it harder. The ki
blast is a headache too but that isn't the entire issue. Maybe reduced stats? Not sure."

Earlier: "The Jrs were tough but it was a fun challenge." So the target is still a hard fight, not an easy one.

## Task (study only: no patch, no build-list change)

1. **Crowding.** Explain why Jrs behind the front Jr can punch Gohan: how enemies pick their spot, whether enemies keep
   any spacing from each other or overlap freely, and how the punch guard `@0x0801BEB8` decides. Measure, with the
   CJH box model, how many of 4 stacked Jrs can land a punch on Gohan at once from the positions the AI drives them
   to. Find any vanilla spacing or "wait your turn" behaviour (an AI node, a cap on attackers, a separation push) in
   other group fights, with addresses.
2. **Stats.** Give type 26 HP, attack (the stat used in its damage to Gohan), defence and EXP, and the damage numbers
   both ways at Gohan's level and stats in the trial save (slot 3: read the save) with his SSJ2 form bonus. Compare
   with the vanilla relay Jr fights (Piccolo, Vegeta, Trunks at their levels) and with one other 4-enemy group fight
   if one exists. How many Gohan hits kill one Jr, and how many Jr hits take Gohan from full to 0.
3. **Options** that change only the trial Jrs (a new type entry in the expansion area, as CJH option 1b; never type
   26 itself, which the relay fights use): lower HP, lower attack, a lower blast roll (an AI 21 copy), a punch-only AI,
   a spacing behaviour, fewer Jrs attacking at once. For each: bytes and data it adds, effect on the numbers in step
   2, risk. Recommend one combination that keeps the fight hard but fair, with the numbers.
4. Emulator steps for me if a fact needs a run.
5. Bible rows (tag CJB) as `## Section N` blocks in `scripts\one-time\2026-10-25-celljr-balance\bible_rows.md`.

Label every claim CONFIRMED, LIKELY or SPECULATIVE and quote the proving line or address.

## Report

`docs\tasks\2026-10-25-celljr-hitbox\celljr-balance-report.md`: SHIPPED and PENDING tables, crowding, the stat and damage
table, the options and the recommendation. Renders welcome in `scripts\one-time\2026-10-25-celljr-balance\`.

## Limits

- Read only, except your report, rows file, scripts and renders (in `scripts\one-time\2026-10-25-celljr-balance\`).
- Never write under `data\`. Python: LF, no em or en dashes, `py -3 -P`. Never `cd` or `Push-Location`, in any shell;
  absolute paths only.
- Other work is changing `celljr_fight.py` (v4) and writing `beam_struggle` and `chapter_cards`. I
  edits `art\base-audit\`, `scripts\one-time\2026-10-23-base-audit\` and `docs\RE-BIBLE.md`. Do not touch them.

