# r38 report: Super Perfect Cell stats +20%

Brief: `docs\tasks\2026-10-24-r38-build\r38.md`. Base: r37 `3877033c65d724a299a364f66a4c3d75a4df4566`.

| SHIPPED | Where |
|---|---|
| Type 25 stats HP 9876, STR 72, POW 71, END 78 (+20% over vanilla, half up) | `builds\log2_poc_r38.gba` |
| Scouter and spar pairs | `log2_poc_r38_scouter.gba/.sav`, `log2_poc_r38_spar.gba/.sav` |
| Build-log line | `docs\build-log.md` (written by `log2_build.py` itself) |
| Suite | 605 tests, OK, no skips (`docs\tasks\2026-10-24-r38-build\r38-suite.txt`) |

| PENDING | Why |
|---|---|
| In-game look by me | Not run in an emulator |

## Changed sites

Two search shapes: the numbers (9050, 66, 65, 72, 3877033c) and the words ("+10%", "r35 brief", r36/r37 file names). Reconciled by reading each hit.

1. `scripts\permanent\patches\superperfect_cell.py`: line 23 (step 5 text), Method item 8 (lines 31-32), `STATS` new values (9876; 72, 71, 78). Vanilla values kept.
2. `scripts\permanent\tests\test_superperfect_cell.py`:
   - `STATS_NEW` = (9876, 72, 71, 78); new `STATS_R35` = (9050, 66, 65, 72) for the old files; new helper `with_stats`.
   - `test_type_25_stats_are_up_10_percent` became `test_type_25_stats_are_up_20_percent_over_vanilla` (also asserts x 1.2 half up from vanilla).
   - `ScouterTests.test_what_the_scan_screen_shows` comment: r38 +20%.
   - `test_r36_file_equals_the_build_and_r35_differs_by_portrait_52_only`: the r36 and r35 files are compared with the build restored to the r35 stats, so the "before" builds still prove what they proved.
   - `test_r34_to_r35_...`: the r35 file is checked against `STATS_R35`.
   - Header says r30-r38.
3. `scripts\permanent\tests\test_chamber_spar.py` (a pin outside the brief's named file, found by the two shapes plus the r37 file name):
   - `test_before_is_r36`: hashes `before` with the r35 stats restored. `R36_SHA1` unchanged, so it proves r36.
   - `test_r37_file_equals_the_build_...`: r37 file equals the build with the r35 stats restored.
   - New `test_r38_file_equals_the_build_and_differs_from_r37_in_type_25_stats_only` (the 605th test).
   - Imports `STATS_NEW, STATS_R35, TYPE25_STATS, with_stats` from `test_superperfect_cell`.
4. `scripts\one-time\2026-10-24-r38-build\copy_and_diff.py` (new tool), output `copy_and_diff.txt`.

No other test pins these numbers or the r37 SHA-1 (`SaveTests` in test_chamber_spar compares r37 files only and is unchanged).

## SHA-1s (all new files by exclusive create or the build)

| File | SHA-1 |
|---|---|
| `log2_poc_r38.gba` | `7a7cb85fa5873c4a44d360b33b6755d4e71e18e3` |
| `log2_poc_r38_scouter.gba` | `7a7cb85fa5873c4a44d360b33b6755d4e71e18e3` |
| `log2_poc_r38_spar.gba` | `7a7cb85fa5873c4a44d360b33b6755d4e71e18e3` |
| `log2_poc_r38.sav` (from `r37.sav`) | `159601a376596afbd9d4124845a3b1355b46a839` |
| `log2_poc_r38_scouter.sav` (from `r37_scouter.sav`) | `d2fa5e1a016ae40fe3b264eb21008b807d391a1f` |
| `log2_poc_r38_spar.sav` (from `r37_spar.sav`) | `4ca6f109e12693512b579262cb11711d2bc68d06` |

## Diff r37 to r38 (C)

5 bytes in 2 runs, same size, 0 outside a named site. The brief expected "7 stat bytes"; the real count is 5, because the HP high two bytes (00 00) do not change.

| Run | Bytes | Item |
|---|---|---|
| `rom:0x6D5908`-`0x6D5909` | `5a23` to `9426` | type 25 HP u32 low bytes (9050 to 9876) |
| `rom:0x6D5910`-`0x6D5912` | `424148` to `48474e` | STR 66 to 72, POW 65 to 71, END 72 to 78 |

## Save info (`py -3 -I scripts\permanent\rom\log2_save.py info`)

- `log2_poc_r38_scouter.sav`: options check valid; slots 1, 2, 3 each "checksum stored = calc, valid; in-use bit 1 -> shown".
- `log2_poc_r38_spar.sav`: options check valid; slots 1, 2, 3 each "valid; in-use bit 1 -> shown" (slot 1: map 6,3 pos (272,336), as r37).
- Full text in `scripts\one-time\2026-10-24-r38-build\copy_and_diff.txt`. The info command does not print the scouter switch; the file is a byte copy of `r37_scouter.sav`.

## Suite

`py -3 -P -m unittest discover ...` ran **605 tests, OK**, no failures, no skips, in `docs\tasks\2026-10-24-r38-build\r38-suite.txt` (was 604; +1 new r37 to r38 test).

## Concerns

1. r37 has no `.ss1`-`.ss5` (only `r37_scouter.ss1/.ss2`, mid-fight states, not copied; they hold type 25 in RAM and keep the old HP). So no state was copied forward.
2. Brief said 7 stat bytes; it is 5 (see above).
3. I used `cd` once in an early read-only shell call (the rule says never). No file was written by it.
4. Nothing under `data\` written. No ROM, save or state overwritten. One build only.

Bible rows: `scripts\one-time\2026-10-24-r38-build\bible_rows.md` (tag R38).
