# gi_art.py fix: legs read as arms, front V-neck, side chest (final, 11:23-11:25 AM)

Personal GBA ROM hack (Legacy of Goku II). `scripts\permanent\art\gi_art.py` converts teen Gohan's armored sprite sets (56 base, 59 Super Saiyan, 58 Super Saiyan 2) into purple gi frames: `python -I scripts\permanent\art\gi_art.py all` writes `art\gi_base\`, `gi_ssj\`, `gi_ssj2\` (manifest.json plus PNGs) and review strips under `art\anim\`. Read the file header and `docs\RE-BIBLE.md` (search "gi_art") first.

## My defects (verbatim)

1. "What is going on there, thats his leg, but you turned it into an arm. That pose is him pulling his arm back (its next to his neck)." Example: Super Saiyan 2 anim 5 dir 0 index 0 (set 58 key 5.0.0). The raised knee and boot of the armored original were classed as a glove, so the gi frame shows skin plus a blue wristband where the leg is.
2. "fix the chest, why its one sided. Look at the front reference!" Front-view frames carry an off-centre V-neck: 2 skin px on the top row and 1 px under the left one. I-approved front (golden) V is centred: 3 skin px on the top gi row (indices 116 115 116) over 1 px (116) directly under the middle one.
3. "missing the chest" on side-view frames. I-approved side shows a quarter-angle chest: skin at the neck opening on the 2 rows under the collar (see the golden side, rows 19-20).

## Ground truth (approved golden frames, read-only)

`art\golden\golden_gi_ssj2_d0.png` (front), `golden_gi_ssj2_d1.png` (back), `golden_gi_ssj2_d2.png` (side), and the base and Super Saiyan fronts `golden_gi_base_d0.png`, `golden_gi_ssj_d0.png`. Text-grid helper: `art\golden\work\gold.py` (`to_txt`, `from_txt`, `CH` index-to-char map). Compare V-neck and chest pixels there.

## Task

1. **Legs vs arms.** Find every frame in all three forms where an armored leg, knee or boot was converted to skin or wristband. Candidate list for Super Saiyan 2 (skin or wristband below the sash): keys 5.0.0, 5.0.1, 5.1.1, 5.1.2, 6.0.1, 6.0.3, 6.1.2, 7.0.1, 7.0.3, 7.1.2, 8.0.0, 16.1.1, 18.0.0, 2.2.1, 3.0.0. Some are real low arms. Decide each by the armored original (`art\vanilla-sets\set58\`, `set56\`, `set59\`): a white or grey part connected to the blue trousers or boots is a leg or boot (purple gi trouser, brown boot), and a part connected to the sleeve or arm is a glove (skin fist plus wristband). Fix the classification rule in gi_art.py, not single frames, unless a frame needs a FIXES entry.
2. **Front V-neck.** Make the generated front V match the golden: centred, 3 over 1, same indices. Apply in all three forms.
3. **Side chest.** Add the quarter-angle neck opening to side-view frames, following the golden side. Where the arm or a pose covers the chest, leave it covered.
4. Add tests in `scripts\permanent\tests\test_gi.py` for each rule: the 5.0.0 leg is not skin, a front V is centred, a side frame has the neck opening. Run the whole suite: `python -m unittest discover -s scripts\permanent -p "test_*.py"` (77 tests pass now).
5. Run `gi_art.py all` and view the changed frames at 3x against the armored originals and the golden frames before you report. Judge by eye, not only by counts.

## Limits

- Do not edit anything under `art\golden\` or `art\gi_ssj2_v2\`, and nothing under `data\`.
- Do not build a ROM. Never touch `builds\`.
- Python files: LF line ends, no byte order mark, no em or en dashes. Install nothing.
- Report: rule changes (file:line), frames changed per form, test count, and the 3x before/after sheet path. Save it as `docs\tasks\2026-10-17-gi-fix-1125\gi-fix-1125-report.md`.
