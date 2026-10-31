# HUD mockup v2b: wrap Vegeta's hold move (state 46) in the ki pool (final, 2026-10-24 11:11 AM)

Read `docs\tasks\2026-10-24-hud-ki\hud-ki-proto-report.md` first (the v2
build, its hooks, the state 46 gap, its tools `scripts\one-time\2026-10-24-hud-ki\proto\build_proto.py`, `test_proto.py`, `proof_proto.py`).

## My ask (verbatim)

"For the flags, vegeta should be fixed but let me review the drain"

The v2 report: state 46 (ability 0, Vegeta hold) spends EP and is not wrapped; the fix is one word, vtable `0x080258B4` +8 to a
swap_state stub. The drain rates stay as built (I review them).

## Task

1. Prove the fix by reading: what state 46 spends, where (addresses), and that the stub pattern the other wrapped states use
   applies to it unchanged. Label CONFIRMED, LIKELY or SPECULATIVE.
2. Build v2b by a copy of the v2 builder (`build_proto_b.py`, Write tool), changing only what the fix needs, to
   `builds\mockups\2026-10-24-hud-ki\log2_poc_r38_bfhud2b.gba` plus `_spar` and `_scouter` pairs (copies of the v2 pair saves), all by
   exclusive create. v2 and its files stay untouched.
3. Prove: byte diff v2 to v2b (every byte named), diff r38 to v2b with 0 bytes outside named regions, tests (`test_proto_b.py`:
   the v2 tests plus state 46 tests), SHA-1 of every new file.
4. My steps: how to test Vegeta's hold move with the pool (which save file and slot, how to switch to Vegeta, transform,
   use ability 0) and what a pass looks like.

## Report

`docs\tasks\2026-10-24-hud-ki\hud-ki-proto-b-report.md`. Bible rows (tag HKB) in `scripts\one-time\2026-10-24-hud-ki\proto\bible_rows_b.md`.

## Limits

- Never write under `data\`. Never overwrite any ROM, save or state. No change to `scripts\permanent\`, `build_list.txt`, `art\`,
  `docs\`. Work only in `scripts\one-time\2026-10-24-hud-ki\`. Other work is running in `scripts\one-time\2026-10-24-computer-save\`.
- Python: LF, no byte order mark, no em or en dashes. `py -3 -P`. Never `cd`, in any shell, ever; absolute paths only. Create
  files with Python or Python `open(..., "x")`, never shell redirection, `sed`, `printf`, `cp`, `rm` or `mkdir`. Do not.

