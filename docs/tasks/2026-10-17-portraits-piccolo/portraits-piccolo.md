# gohan_portraits: Piccolo gi colors and the new base gi portrait (approved 3:47-3:48 PM)

Personal GBA ROM hack (Legacy of Goku II). Read the header of `scripts\permanent\patches\gohan_portraits.py` and `docs\research\re-portraits.md` (sections 5-7) first. Tests: `scripts\permanent\tests\test_portraits.py`.

## Final decisions (approved, do not redesign)

1. **Gi colors = Piccolo's portrait.** Piccolo's dialog portrait (id 94) draws his gi with OBJ index 97 (88,0,120) body, 233 (168,32,224) lit folds, 1 black outline. The game pairs 97 to status 232 and 233 to status 234. Index 96 has no game pair and falls to a dull mauve on the status screen.
2. **gi_ssj:** recolor dialog index 96 to 97. Nothing else.
3. **gi_ssj2 (final call "B"):** recolor dialog index 80 to 233 and 215 to 97.
4. **New base gi portrait for appearance entry 2:** I-approved drawing is `art\portrait-sources\src\gi_base_dialog_src.png` (64x64 indexed, OBJ palette, SHA-1 `2bcc68315e4919f872ca9e773e1c24bdeb201ce4`). It is source art: never regenerate or edit it. New ids 119 (dialog) and 120 (status). Entry 2 +2/+3 changes from 59/10 (`3B 0A`) to 119/120.

## Task

1. In `gohan_portraits.py`:
   - Add a per-form recolor map applied to the dialog indices after `convert`. The status version must come from the recolored dialog through the existing game-pair rule, so the status uses 232/234. Feeding `[obj[k] for k in dialog]` back into `convert` returns the same dialog indices (checked for all three forms); use that or an equivalent path.
   - Add form `gi_base`: source = the src PNG (dialog indices as drawn), entry 2, old (0x3B, 0x0A), new (119, 120). Put it last so the new ids stay in order 115-120.
   - Remove the "entry 2 keeps the armor" special case (`BASE_ENTRY`, `BASE_PORTRAITS`) and its `_expect`, since entry 2 is now a normal form. Keep the old-bytes check for entry 2 through the FORMS loop.
   - Update the header docstring (Method, Rules) and the review sheet rows.
2. Run `py -3 -I scripts\permanent\patches\gohan_portraits.py art`. Check the written PNGs: gi_ssj and gi_ssj2 dialog contain no index 96, 80 or 215 in the gi; status gi uses 232/234; `gi_base_dialog.png` is byte-identical in pixels to the src PNG.
3. Update `test_portraits.py`: replace `test_gi_base_keeps_armor_portraits` with a test that entry 2 points at 119/120; extend NEW; add a test that no gi portrait dialog uses 96 or 80 and every gi status uses 232 or 234 for the gi. Keep `test_pngs_reproduce_from_reference` meaningful for all three forms (the base reproduces from the src PNG). Run the whole suite: `python -m unittest discover -s scripts\permanent -p "test_*.py"` (82 tests pass now).
4. Build a review ROM to `archive\builds\log2_poc_r5.gba`, with the same patches and env as r4: set `LOG_GI_SSJ2=gi_ssj2_v2`, then `py -3 -I scripts\permanent\log2_build.py --out archive\builds\log2_poc_r5.gba gohan_gi ssj2_form gohan_portraits`. Append the build line to `docs\build-log.md` in the r4 style, with the env noted. Copy `archive\builds\log2_poc_r4.ss1` to `log2_poc_r5.ss1` if it exists.
5. Update `docs\research\re-portraits.md` sections 5 and 7 (entry 2 now 119/120; ids 119-120 and their offsets; Piccolo color rule; the drawn base art is approved source, not from 122601.png) and the RE-BIBLE rows that state entry 2 keeps the armor (search "gohan_portraits" and "59/10"). Describe the system as it is, with no history wording.
6. While in `scripts\permanent\patches\gohan_gi.py`: add one header doc line for the env var `LOG_GI_SSJ2` (overrides the art folder that set 159 reads; default `gi_ssj2`). Read the header first; the code already reads it.

## Limits

- Never write under `data\`. Never overwrite `builds\log2_poc.gba` or `log2_poc_r4.gba`. Never edit `art\portrait-sources\src\` or `art\golden\`.
- No palette is written. Install nothing. Python files: LF line ends, no byte order mark, no em or en dashes.
-

## Report

Save it as `docs\tasks\2026-10-17-portraits-piccolo\portraits-piccolo-report.md`: changes (file:line), new ROM offsets for ids 119/120, the r5 SHA-1, test count, and the path of the regenerated review sheet. Then reply with status and a 3-line summary only.

