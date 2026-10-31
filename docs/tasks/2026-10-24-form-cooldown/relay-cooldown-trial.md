# Relay cooldown fix: trial module (final, 2026-10-25 9:32 AM)

Read `LOG\README.md`, `docs\tasks\global.md`, the study
brief and report in this folder (`form-cooldown-study.md`, `form-cooldown-report.md`) and the bible rows tagged FCD.

## Final decisions (verbatim)

"Agreed, menu unchanged, just plain."

So: build the plain design from the study report. At every scripted `ext 70` (relay and other leader swaps) the party
form cooldown (save struct +8, `0x03000E98`) is set to 0. The Switch Characters menu keeps vanilla behaviour.
Variant B is not wanted.

## Task

1. Write the trial patch module `scripts\permanent\patches\relay_cooldown.py` and its tests
   `scripts\permanent\tests\test_relay_cooldown.py`, in the style of the existing modules (header, source checks before
   the first write, a second run raises). Design from the report: repoint ext table word `rom:0x3B5E40` (today
   `0x0800A785`) to a 28-byte wrapper in free space that calls the vanilla ext 70 and then clears the cooldown
   (report bytes `10b5044b00f005f80349496800228a6010bd184785a70008507e6f08`). Re-derive every byte and pool word; do
   not trust the report. Check the free space with the project's allocator and that no r39 module or trial module
   (`celljr_fight`, `vegeta_ssj_scene`) writes the same bytes.
2. Tests must decode the wrapper with `scripts\permanent\rom\thumb_dis.py` (not with the encoder) and prove: the table word,
   the call to the vanilla ext 70, the store of 0 to the cooldown word, the return, and that the menu swap path is
   byte-equal to r39.
3. Make a new list `scripts\permanent\build_list_trial_cooldown.txt` = the lines of `build_list.txt` plus
   `relay_cooldown`. Do not edit `build_list.txt`, `build_list_trial.txt` or `build_list_trial_vegeta.txt`. `--list`
   must still give r39 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`.
4. Build `builds\mockups\2026-10-25-relay-cooldown\log2_poc_r39_cooldown.gba` (exclusive create). Give I a save
   that reaches a relay quickly (copy an existing Cell Games save, exclusive create, `.sav` next to the ROM) and the
   steps: which slot, transform, win, check the next fighter can transform at once.
5. Full suite once at the end. List the diff runs r39 to the new ROM.
6. Bible rows (tag RCD) as `## Section N` blocks in `scripts\one-time\2026-10-25-relay-cooldown\bible_rows.md`.

## Report

`docs\tasks\2026-10-24-form-cooldown\relay-cooldown-report.md`: SHIPPED and PENDING tables, the bytes and their decode,
SHA-1s, diff runs, test counts, my play steps. Label claims CONFIRMED, LIKELY or SPECULATIVE and quote the
proving line or address.

## Limits

- Never write under `data\`. Never overwrite a ROM, save or state. Python: LF, no em or en dashes, `py -3 -P`.
  Never `cd`, in any shell; absolute paths only. Scripts and outputs go in
  `scripts\one-time\2026-10-25-relay-cooldown\`.
- Other work is changing `vegeta_ssj_scene.py`, its tests and its list. Do not touch them, `celljr_fight.py` or its
  tests. I am editing `art\base-audit\` and `scripts\one-time\2026-10-23-base-audit\`. Do not touch them.

