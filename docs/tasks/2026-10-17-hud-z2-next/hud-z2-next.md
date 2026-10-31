# ssj2_form: the Z2 icon shows what B does next (final, 2026-10-17 7:28 AM, confirmed 10:09 PM)

Personal GBA ROM hack (Legacy of Goku II). Read the header of `scripts\permanent\patches\ssj2_form.py`, `docs\research\re-forms.md` (sections on the step gate and the HUD hook) and `scripts\permanent\tests\test_ssj2.py` first.

## My rule

One transform slot (ability 12). The HUD icon shows what B does next:
- Base: Z (vanilla).
- Super Saiyan (record +8 == 5) when B would step up to Super Saiyan 2: **Z2**.
- Super Saiyan when B would revert (flag 195 clear, or EP under the step cost): Z (vanilla).
- Super Saiyan 2 (record +8 == 22): Z2 (as now).
- Bright or dim keeps the vanilla rule: dim when the ability test fails.

## Task

1. Change the `hud` routine in `ssj2_form.py`. Z2 shows when ability 12 is selected and either the record is in entry 22, or the step gate would send message 0x23. Use the gate's exact predicate (transformed bit, `e+4 != e+5`, flag 195 at `FLAG_ADDR`/`FLAG_SHIFT`, `(s16)[record+4] >= STEP_EP`). Share it with `gate` (one predicate routine both call) so the icon can never disagree with the action. Keep the register, stack and lr rules that the existing routines follow (see the comments and re-forms.md section 7). Keep Thumb.
2. Find out WHEN the HUD hook at rom:0x8D14 runs: every frame, or only on events (slot change, form change). Quote the caller chain. If it runs only on events, the icon can lag when EP crosses the step cost or flag 195 is set; report that with evidence, and do not add a redraw hook without telling I first.
3. Tests in `test_ssj2.py` (emulated or byte-level, following the existing style): Z2 in entry 5 with flag set and EP >= STEP_EP; Z in entry 5 with flag clear; Z in entry 5 with EP below STEP_EP; Z2 in entry 22; vanilla icon for other abilities and other characters; dim vs bright follows the ability test. Run the whole suite: `py -3 -I -m unittest discover -s scripts\permanent -p "test_*.py"` (83 tests pass now).
4. Build a check ROM: set `LOG_GI_SSJ2=gi_ssj2_v2`, then `py -3 -I scripts\permanent\log2_build.py --out archive\builds\log2_poc_r6_hud.gba gohan_gi ssj2_form gohan_portraits`. Append the build line to `docs\build-log.md` in the r5 style.
5. Update `docs\research\re-forms.md` (HUD hook section) and the RE-BIBLE row(s) for the Z2 icon. Describe the system as it is, with no history wording.

## Limits

- Never write under `data\`. Never overwrite `builds\log2_poc.gba`, `log2_poc_r4.gba` or `log2_poc_r5.gba`. Do not touch art under `art\`.
- Do not change the approved icon art (`art\hud_z2*.bin`). No palette is written. Install nothing.
- Python files: LF line ends, no byte order mark, no em or en dashes.

## Report

Save it as `docs\tasks\2026-10-17-hud-z2-next\hud-z2-next-report.md`: changes (file:line), the predicate routine listing, the WHEN finding with quoted evidence, test count, check ROM SHA-1. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with status and a 3-line summary only.

