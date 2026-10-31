# Disasm update check: 9374b08 to 075b23c (final, 2026-10-25 9:40 AM)

Read `LOG\README.md`, `docs\tasks\global.md` and the
bible source list (tag DSA covers the earlier disasm reads).

I asked to pull the latest disasm. The clone is
`%USERPROFILE%\Documents\GitHub\legacyofgoku2-disasm` (read only), now at `075b23c`. The 8 new commits since
`9374b08` add: transform slot descriptor records (`tools\records\TRANSFORM_SLOTS.md`, `transform_slots.py`), the
state table and quest records, script opcode rows (`tools\records\opcode_rows.py`, `instruction.csv`), text storage
records (`tools\text\`: font, objective, roster), function bounds (`tools\code\FUNCTION_BOUNDS.csv`), runtime labels
(`tools\recomp\RUNTIME_LABELS.csv`), address runs (`tools\addr\`), IWRAM copy callers and a recarved container
census. Read `CHANGELOG.md` for the full list.

## Task (study only)

1. **Conflicts first.** Compare the new disasm facts with the bible. List every bible row the disasm contradicts or
   corrects, with both sides quoted and which side the ROM bytes support (check the bytes yourself in
   `builds\log2_poc_r39.gba` or the base ROM).
2. **Facts that touch live work:** forms and the party cooldown (rows FRM, FCD; the `relay_cooldown` trial is being
   built now), script ext ops used by `celljr_fight`, `vegeta_ssj_scene` and the beam struggle design (CJT, CJ2, VSJ,
   BMS), and text storage (the BF survey picks `chapter_cards` and `named_supplies`, rows BFP). Say what each new fact
   confirms, raises from LIKELY or SPECULATIVE to CONFIRMED, or puts at risk.
3. **New names:** list disasm labels for addresses the bible names only by number, as a short table. Do not rename
   anything in the bible; give the rows.
4. **Tools worth reusing** in `scripts\permanent\` (for example the opcode rows or text rows readers): say what each
   does and what our tool it would replace. Do not copy code.
5. Bible rows (tag DS8) as `## Section N` blocks in `scripts\one-time\2026-10-25-disasm-check\bible_rows.md`, with merge
   notes for rows that must be relabelled.

Label every claim CONFIRMED, LIKELY or SPECULATIVE and quote the proving line, file or address.

## Report

`docs\tasks\2026-10-25-disasm-check\disasm-check-report.md`: SHIPPED and PENDING tables, conflicts, live-work impact,
new names, tools.

## Limits

- Read only, except your report, rows file and scripts (in `scripts\one-time\2026-10-25-disasm-check\`). Never write in
  the disasm clone or run its `rebuild.cmd`. Never write under `data\`.
- Python: LF, no em or en dashes, `py -3 -P`. Never `cd`, in any shell; absolute paths only.
- Other work is changing `vegeta_ssj_scene.py` and `relay_cooldown.py` with their tests and lists. I
  edits `art\base-audit\` and `scripts\one-time\2026-10-23-base-audit\`. Do not touch them.

