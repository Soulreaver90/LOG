# Cell Jr rework: build (final, 2026-10-30 7:40 PM: "Work on cell jr")

The plan is `docs\tasks\2026-10-30-celljr-rework-plan\plan-report.md`,
Part 1 (Q1-Q7). Read that, `scripts\permanent\patches\celljr_fight.py`, `tests\test_celljr_fight.py`, and
`scripts\permanent\build_list_trial.txt` (it includes main r40). Read other files only when the build needs them.

## Final decisions (final, they override the plan where they differ)

- Relay Jrs (Piccolo, Vegeta, Trunks): type 26 with the boss descriptor. The bar stops at 1/4 (`ext 90 (31,25,100)`),
  then sound 60 and the white flash, then the fade. The beaten Jr **vanishes during the fade: no stand-in** (drop the
  plan's stand-in spawns in R8 and R9).
- 1 v 1 Jr: type 26, full HP 4990, the standard AI, a bar. It explodes (the existing kill) and stays scannable.
- 1 v 3 Jrs: the trial type, **HP 1550**, the v5 AI, no bar. They explode.
- Scripted finish: 3 new Jrs **walk down from above** (no Jr fly row). Gohan punches one, blasts one, and flies at the
  third. Gohan's fly row (set 160 row 12 from set 159) goes in as planned.
- EXP 12,500 for each Gohan Jr (50,000 in all). No new scouter entry.
- Only two things are new: the relay non-death and the scripted finish. Everything else stays as v5.

## Task

1. Change `celljr_fight.py` and its tests to the plan with the decisions above. Use the plan's tests, minus the
   stand-in test; the "fly" tests become "walk" where the Jrs are concerned.
2. Build `builds\mockups\2026-10-24-celljr\log2_poc_r40_celljr_v6.gba` from `build_list_trial.txt` (check that it is
   absent first; exclusive create). Diff r40 to v6: every run inside a celljr_fight site.
3. Make a test save next to it (same name, `.sav`) that starts just before the relay, with `log2_save.py` and the
   Cell Games presets. Say which slot is where.
4. Full suite once at the end.

## Report

Short: `docs\tasks\2026-10-30-celljr-rework\celljr-rework-report.md`. SHIPPED and PENDING tables, the sites, the SHA-1s,
the save slots, the play steps (the plan's my checks, updated), the suite count. Bible rows (tag CJ6, a few) as
`## Section N` table blocks in `scripts\one-time\2026-10-30-celljr-rework\bible_rows.md`. Label claims CONFIRMED,
LIKELY or SPECULATIVE.

## Limits

- Edit only `celljr_fight.py` and `tests\test_celljr_fight.py` (and the VS5 fly test named in the plan, if the shared
  row needs it). Scripts go in `scripts\one-time\2026-10-30-celljr-rework\`. Python: `py -3.14 -P`. LoG II base ROM:
  `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba`.
- Never write under `data\`. Never overwrite a ROM, save or state. LF, no em or en dashes.
- Never `cd`, `Set-Location` or `Push-Location`. Use absolute paths in every command and in every script that opens a
  file.
- Do not touch `docs\RE-BIBLE.md`, `docs\ledger\`, `build_list.txt` or `LOG\zhack\`.
- Work lean: no full enumerations, no long tables. ROM quality comes first.

