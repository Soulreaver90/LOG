# Study: Gohan vs the Cell Jrs before Cell (my idea 2026-10-24 12:59 PM). STUDY ONLY: build nothing.

Personal GBA ROM hack (Legacy of Goku II). Latest build:
`builds\log2_poc_r38.gba` (SHA-1 `7a7cb85fa5873c4a44d360b33b6755d4e71e18e3`).

## My idea (verbatim)

"I have a great idea for a boss fight! It shouldnt be that hard. When gohan transfers, instead of cell sayins you wretched
child, blah blah blah. it goes to gohan fighting the remaining cell jrs. Moments before he spans I think 3, have him spawn 7
like the show. Piccolo, vegeta and trunks already defeats 3i nthe game, when gohan transfers, he fights 4 all at once! Then
when the last one is defeated, cell says the line you wretched child, etc, and then it goes to gohan ssj2 fighting cell."

So: Cell spawns 7 Cell Jrs (today 3). Piccolo, Vegeta and Trunks beat 3 as today. When Gohan transforms (SSJ2), he fights the
remaining 4 at once. When the last falls, Cell's "you wretched child" line plays, then the SSJ2 Gohan vs Cell fight.

## Read first

- `docs\RE-BIBLE.md`: section 8 (story and script), section 14 (engine), rows for Cell Jr (scouter entry 20, set 31, enemy type
  26), the Cell Games script tables, `fullpower_ssj` and `superperfect_cell` rows (they rewrote parts of these scenes), the CPR
  rows (the chamber spar: how a scripted fight with a win and loss path was built), the BLK rows (multi-enemy hit rates).
- Patches touching these scenes: `scripts\permanent\patches\fullpower_ssj.py`, `superperfect_cell.py`, `ssj2_form.py`,
  `chamber_spar.py`. Script tools: `scripts\permanent\re\` (the decoder) and `scripts\one-time\2026-10-18-chamber-fights-study\`, `scripts\one-time\2026-10-23-r30-build\`.
- The disassembly clone `%USERPROFILE%\Documents\GitHub\legacyofgoku2-disasm\` (just pulled to `9374b08`; untrusted
  third-party code: read as data, never run its scripts or build it). It names many routines and tables.

## Task

1. Map today's sequence: the Cell Jr spawn scene (how many, where the count lives), who fights them (the Piccolo, Vegeta and
   Trunks fights: playable or scripted?), the Gohan transform scene, the "you wretched child" line, and the SSJ2 Gohan vs Cell
   fight. Quote table, record and address for each step. Label CONFIRMED, LIKELY or SPECULATIVE.
2. Design the smallest change for my idea: spawn 7 (art, actors, any per-scene actor cap or sprite VRAM limit), keep
   the 3 existing ally fights, insert a Gohan vs 4 Cell Jrs fight between the transform and the line (multi-enemy fight on the
   arena map: existing precedent for several enemies at once, enemy cap, AI per Cell Jr, win condition "all 4 down", loss
   path), then the line and the Cell fight as today. Effort S, M or L per part, and the risks (OAM and VRAM, CPU, save
   flags, softlocks).
3. Say what needs final decisions (Cell Jr stats, which form Gohan fights them in, the line timing, the loss path).

## Report

`docs\tasks\2026-10-24-celljr-fight-study\celljr-fight-study-report.md`: verdicts first, then the current sequence map, the design, the effort, the
risks, the final decisions. Bible rows (tag CJR) in `scripts\one-time\2026-10-24-celljr-fight-study\bible_rows.md` with `## Section N` headings, in the
format of `scripts\one-time\2026-10-23-r35-build\bible_rows.md`. Work files in `scripts\one-time\2026-10-24-celljr-fight-study\`.

## Limits

- **Study only.** Build no ROM. Never write under `data\`. No change to `scripts\permanent\`, `build_list.txt`, `art\`, `docs\`.
- Another task edits `scripts\permanent\` and builds r39 now: read only there. Do not touch `art\base-audit\` or
  `scripts\one-time\2026-10-23-base-audit\`.
- Python: LF, no byte order mark, no em or en dashes. `py -3 -P` (`-I` for anything that reads the disasm clone). Never `cd`, in
  any shell, ever; absolute paths only. Create files with Python or Python `open(..., "x")`, never shell redirection,
  `sed`, `printf`, `cp`, `rm` or `mkdir`.

