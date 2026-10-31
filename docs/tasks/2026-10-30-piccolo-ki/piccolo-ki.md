# Piccolo shows no yellow ki after he transforms (final, 2026-10-30 9:05 PM)

Read `scripts\permanent\patches\bf_ki_pool.py`
(its header: `pool_ref` takes only the Super Saiyan form object `0x030021EC` or ssj2_form's), `fullpower_hud.py`,
`relay_cooldown.py`, and the bible rows tagged HUD, KIP, R39, R40 for the ki pool. Read other files only when needed.

## My words

"Piccolo doesn't have the gold ki post transformation, doing Vegeta fight and he does. Is this an oversight?"
He is playing the Cell Jr relay (`builds\mockups\2026-10-24-celljr\log2_poc_r40_celljr_v6.gba`, on main r40). An
earlier note blamed old trial lists, but r40 includes main and the gap is still there, so that cause was wrong.

## Task

1. Find the cause with evidence: Piccolo's transform (which state, form object and vtable), why the pool does not take
   it, and whether it also fails outside the relay (plain r40, any map). Label CONFIRMED, LIKELY or SPECULATIVE.
2. If the cause is that the pool only knows the Saiyan form objects, fix `bf_ki_pool.py` so Piccolo's form gets the
   same pool (fill on transform, drain, spend, yellow HUD, empty on revert), with tests. Keep Goku, Gohan, Vegeta and
   Trunks byte-identical in behaviour. If the fix needs a design choice, stop and report the options instead.
3. If you fix it: build `builds\mockups\2026-10-30-piccolo-ki\log2_poc_r40_piccolo_ki.gba` from a new trial list
   `scripts\permanent\build_list_trial_piccolo_ki.txt` = `include build_list.txt` (the module change applies through
   main, so the list is main only; say so). Check absent first; exclusive create. Diff r40 to it: every run inside a
   bf_ki_pool site. Copy `builds\log2_poc_r40.sav` next to it. Run the full suite once.

## Report

Short: `docs\tasks\2026-10-30-piccolo-ki\piccolo-ki-report.md`. SHIPPED and PENDING tables, the cause, the fix,
SHA-1s, the play steps, the suite count. Bible rows (tag PKI, a few) as `## Section N` table blocks in
`scripts\one-time\2026-10-30-piccolo-ki\bible_rows.md`.

## Limits

- Edit only `bf_ki_pool.py`, its test file and the new trial list. Scripts go in `scripts\one-time\2026-10-30-piccolo-ki\`.
  Python: `py -3.14 -P`. Base ROM: `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba`.
- Never write under `data\`. Never overwrite a ROM, save or state. LF, no em or en dashes.
- Never `cd`, `Set-Location` or `Push-Location`. Use absolute paths in every command and in every script that opens a
  file. Do not touch `docs\RE-BIBLE.md`, `docs\ledger\`, `build_list.txt` or `LOG\zhack\`.
- Work lean: no full enumerations. ROM quality comes first.

