# r34 build report: scouter name `Cell, "S. Perfect"`

Brief: `docs\tasks\2026-10-23-r34-build\r34.md`. Base: r33 `3ce2bb1763f9c472c5b37d3c4cb70ed417576b97`.

| SHIPPED | Where |
|---|---|
| Entry 19 name is `Cell, "S. Perfect"` (entry 13's format, ASCII, straight quotes, 19 bytes with the 00) | `builds\log2_poc_r34.gba`, SHA-1 `b5d3279a2af469321e272ebc6089d1c3697f390d` |
| Fit mock-up: 85 px, info ink x 77-161 in the 73-166 field, 0 px under the portrait, list ink x 37-121 | `scripts\one-time\2026-10-23-r34-build\fit_info.png`, `fit_list.png`, `fit.txt` |
| Saves, states, ROM pairs at r34 names | `builds\` (exclusive create, `scripts\one-time\2026-10-23-r34-build\copy_files.txt`) |
| Diff proof r33 to r34 | `scripts\one-time\2026-10-23-r34-build\diff_proof.txt` |
| Suite | 571 tests, OK, 0 skipped |

| PENDING | Why |
|---|---|
| In-game look by me | Not seen in an emulator. The fit is proved by the mock-up and a width test |

## Change

- `scripts\permanent\patches\superperfect_cell.py`: `SUPER_NAME` and the step 6 header line. Nothing else. `build_list.txt` unchanged.
- The string stays at `rom:0x908EEC`. The pointer word in entry 19 +0 is the same as r33, so only string bytes differ.

## Diff proof r33 to r34 (C)

13 bytes changed, all inside `rom:0x908EEC`-`0x908F01` (the name string). The ROM size is equal. r33 there: `Cell, "Super Perfect"` 00. r34 there: `Cell, "S. Perfect"` 00 FF FF FF (the tail is free space again). The file equals the in-memory build of `build_list.txt`.

## Copies

Same table as r33: `.sav`, `_chamber2.sav`, `_scouter.sav` and `.ss1`-`.ss5` are r33 byte copies. `log2_poc_r34_chamber2.gba` and `log2_poc_r34_scouter.gba` are r34 byte copies. No ROM, save or state was overwritten.

## Tests (`test_superperfect_cell.py`)

- `SUPER` is now `Cell, "S. Perfect"`. The name-string test reads 19 bytes.
- `test_name_fits_the_list_and_overflows_the_info_field_by_12` became `test_name_fits_the_list_and_the_info_field`: width 85, ink x 77-161, inside 73-166.
- `test_r33_file_equals_the_build` became `test_r34_file_equals_the_build`.
- New `test_r33_to_r34_is_the_name_string_only` and `test_r34_saves_states_and_rom_pairs_are_copies`. The r32 to r33 and r33 copy tests stay.
- Backup of the two edited files before the change: `scripts\one-time\2026-10-23-r34-build\backup\`.

## Build log

One line added by the build to `docs\build-log.md` (2026-10-23 14:29, r34, the SHA-1 above).

## Concerns

1. Not seen in an emulator (L for the look, C for the width and ink columns). The OBJ over BG priority is still not traced, but no ink is near the portrait (portrait opaque from x 168, name ink ends at x 161).
2. Nothing under `data\` or `art\` was written. `inject.py` was not run. No `cd` in any shell call (one harmless failed `cd /dev/null` in a mkdir call, no effect).
