# portraits-piccolo report

Status: DONE. All 83 tests pass. r5 built.

## Changes

- `scripts\permanent\patches\gohan_portraits.py`
  - Header docstring (Method, Rules, Input, API): lines 1-35.
  - `BASE_SRC`, `RECOLOR_SSJ`, `RECOLOR_SSJ2`, new `FORMS` tuple `(source, entry, old, new, recolor)`: lines 56-70. `gi_base` is last (119/120).
  - `BASE_ENTRY`, `BASE_PORTRAITS` and their `_expect` removed. The FORMS loop in `apply` checks old bytes for entries 2, 5 and 22.
  - `_use`, `_status_of`, `_report`, `convert(..., recolor)`, `drawn`, `form_art`: lines 105-180. Status comes from the recolored dialog through the game-pair rule. No round-trip through `convert` is used (the drawn base has no RGB source, so the status is computed straight from dialog indices).
  - `make_art` and the review sheet rows use `form_art`. Base row: new art, armor id 59/10, drawn art. Manifest gets a `recolor` key.
- `scripts\permanent\tests\test_portraits.py`: `NEW` has `gi_base`; `test_gi_base_entry_points_at_119_120` replaces the armor test; `test_pngs_reproduce_from_sources` (all three forms, base equals src PNG pixels and SHA-1); `test_gi_uses_piccolo_colors` (no 96/80/215, 232/234 present, every 97 pixel pairs to 232 and every 233 to 234); `test_other_entries_unchanged` expects [2, 5, 22]; free-space span covers 6 new ids.
- `scripts\permanent\patches\gohan_gi.py`: header line 6 documents `LOG_GI_SSJ2`.
- `docs\research\re-portraits.md`: sections 5, 6 (one line) and 7 and the tools row. `docs\RE-BIBLE.md`: rows at lines 164 and 166. `docs\build-log.md`: r5 line (auto) plus the env review line (manual).

## Art checks (`gohan_portraits.py art`)

- gi_ssj dialog: 0 pixels of 96, 80, 215; 108 of 97, 13 of 233. Status: 108 of 232, 13 of 234.
- gi_ssj2 dialog: 0 of 96, 80, 215; 30 of 97, 469 of 233. Status: 30 of 232, 469 of 234.
- gi_base dialog: 180 of 97, 58 of 233. Status: 232 and 234 the same counts.
- `gi_base_dialog.png` pixels are identical to `gi_base_dialog_src.png`. The src SHA-1 is `2bcc68315e4919f872ca9e773e1c24bdeb201ce4` (unchanged).

## ROM r5

- File: `archive\builds\log2_poc_r5.gba`, SHA-1 `53f6c51a9082786773f68f1cc10d0f85c9aa028f` (`LOG_GI_SSJ2=gi_ssj2_v2`). `log2_poc.gba` and `log2_poc_r4.gba` hashes verified unchanged. `log2_poc_r5.ss1` copied from r4.
- Block rom:0x869700. Relocated appearance table rom:0x868FAC (entry 2 +2/+3 reads `77 78`).
- New ids: 115 rom:0x8698E8, 116 rom:0x86A8F0, 117 rom:0x86B8F8, 118 rom:0x86C900, **119 rom:0x86D908, 120 rom:0x86E910**.

## Tests

- 83 OK (`py -3 -I -m unittest discover -s scripts\permanent -p "test_*.py"`). Was 82. One test replaced, one added.

## Files

- Review sheet: `art\portraits_review.png`
- PNGs and manifest: `art\portrait-sources\` (`gi_base_dialog.png`, `gi_base_status.png` are new).

## Notes

- Python files have LF line ends, no BOM, no em or en dashes (checked).
- Doc offsets are those of r5. The old `log2_poc.gba` offsets in the docs were replaced because block placement moves with the earlier patches' data size.
- Not verified in game. The gi status color result is derived from the game pairing, not viewed on the status screen.
