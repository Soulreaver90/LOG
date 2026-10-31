# Cell Jr fight: build the trial patch module (my ask 2026-10-24)

Personal GBA ROM hack, not a git repo. Read
`LOG\README.md` (folder map) and `docs\tasks\global.md` first. The folder layout changed today; trust `scripts\permanent\log_paths.py`.

## Source

The verified study: `docs\tasks\2026-10-24-celljr-fight-study\celljr-fight-study-report.md` (Design parts 1-4, Bytes
touched, Risks). Key facts it proves: seq 27 record `0x083E9C50`, its table `rom:0x3E9D4C`; seq 31 `0x083E9CF0`; Gohan
table word 30 at `rom:0x3EA478`; 14,3 spawn list `0x08409118`, count byte `rom:0x40DA84` (13), pointer `rom:0x40DA94`.
Re-read each address at its source before you write to it.

## Final decisions

1. The Jrs reuse enemy type 26 (Cell Junior).
2. All 7 Jrs appear in the spawn scene: 3 first, then 4 more after Cell's line "My children! Give them pain!".
   They are gone during the 1v1 ally fights, as in vanilla.
3. Gohan then fights 4 Jrs at once, spawned fresh for that fight.
4. No boss bar. A loss is the normal game over. 50,000 EXP total for the 4 (split evenly).
5. Right after the last Jr dies: a fade transition into the Gohan and Cell scene, the line "You wretched child", then
   the SSJ2 Gohan vs Cell fight as today.
6. The kill counter uses VM var 1 (study: var 0 is taken).

## Task

1. Build it as a **trial patch module** under `scripts\permanent\patches\` (my rule: mockups are patch modules from
   day one). A second build list (the main `build_list.txt` lines plus the trial line, for example
   `scripts\permanent\build_list_trial.txt`) builds the trial ROM. Approval later = move one line into `build_list.txt`.
   If `log2_build.py` needs a `--list <file>` option for this, add it with a test.
2. Write the module's own tests (addresses, bytes, counter logic, EXP split). Run only those while you work; run the
   full suite once at the end (baseline today: 666 OK).
3. Build `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr.gba` (exclusive create). Prove: the main `--list` build
   still gives the r39 SHA-1 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`; the trial ROM differs from r39 only inside the
   module's ranges (list the runs).
4. Make a test save next to it so I can play the fight: scouter on in every slot, a slot placed before the
   Cell Games sequence (the study says there is no save point there; pick the latest safe entry, say which). Use
   `scripts\permanent\rom\log2_save.py`. Never overwrite a ROM, save or state.
5. Add bible rows (tag CJT) for every new fact, as `## Section N` blocks in a rows file, for me to merge.

## Report

`docs\tasks\2026-10-24-celljr-trial\celljr-trial-report.md`: SHIPPED and PENDING tables, the module and list names, the
SHA-1s, diff runs, test counts, the save's slot and map, what the emulator check still needs, and each risk from the
study with its status. Label claims CONFIRMED, LIKELY or SPECULATIVE and quote the proving line or address.

## Limits

- Never write under `data\`. Read the BF ROM in `data\roms\` read only, if needed.
- Python: LF, no em or en dashes, `py -3 -P`. Never `cd`; absolute paths only.
- I am editing sprite files under `art\base-audit\` and `scripts\one-time\2026-10-23-base-audit\` at the same
  time. Do not touch them.

