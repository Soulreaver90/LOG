# Form cooldown carries over to the next fighter: study (final, 2026-10-24 8:53 PM)

Read `LOG\README.md`, `docs\tasks\global.md` and the
`docs\RE-BIBLE.md` rows on forms, transform input, ki drain and the HUD v2b ki pool (tags FRM, HKS, HKP, HKB, R39).

## My report (verbatim)

"When Piccolo transforms and wins the battle, the transformation is on cool down when taking control of Vegeta.
Same if you go Super Saiyan and win, it's on cool down for Trunks. Can you check the code, it's a bit odd."
This is the Cell Games relay: one fighter wins, the next fighter takes over.

## Task (study only: no patch, no build-list change)

1. Find the cooldown: where the transform is refused or delayed, what timer or flag gates it, and where it lives
   (IWRAM, EWRAM, per-character struct, global). Quote the code addresses.
2. Find why it carries across fighters: is the timer global instead of per character, is it never cleared on the
   fighter swap, or does the swap copy state? Name the swap code.
3. **Vanilla or ours?** Check whether vanilla LoG II does this (r38 or the base ROM, before HUD v2b) and whether HUD
   v2b / `bf_ki_pool.py` / `bf_hud.py` (in r39) causes or changes it. The answer decides the fix mine.
4. Propose the smallest fix (for example, clear the timer on the fighter swap, or make it per character) as a trial
   patch module design (my rule: mockups are trial patch modules built through a second build list), with the
   bytes it would touch. Do not build it.
5. Bible rows (tag FCD) as `## Section N` blocks in `scripts\one-time\2026-10-24-form-cooldown\bible_rows.md`.

Tools: `scripts\permanent\disasm\`, the decomp and disasm clones the bible names, `scripts\permanent\rom\thumb_dis.py`,
save states under `builds\`. Label every claim CONFIRMED, LIKELY or SPECULATIVE and quote the proving line or
address. If a claim needs an emulator run, say so; do not guess.

## Report

`docs\tasks\2026-10-24-form-cooldown\form-cooldown-report.md`: SHIPPED and PENDING tables, the root cause, vanilla vs
ours, the proposed fix with its bytes and risks.

## Limits

- Read only, except your report, rows file and study scripts (in `scripts\one-time\2026-10-24-form-cooldown\`).
- Other work is changing `scripts\permanent\patches\celljr_fight.py`, its tests and `build_list_trial.txt`, and the
  I am editing `art\base-audit\`. Do not touch them.
- Never write under `data\`. Python: LF, no em or en dashes, `py -3 -P`. Never `cd`; absolute paths only.

