# gi_art.py fix: chin and belt in the base to Super Saiyan step frames (final, 2026-10-17 10:38 PM)

Personal GBA ROM hack (Legacy of Goku II). `scripts\permanent\art\gi_art.py` converts teen Gohan's armored sprite sets (56 base, 59 Super Saiyan, 58 Super Saiyan 2) into purple gi frames: `py -3 -I scripts\permanent\art\gi_art.py all` writes `art\gi_base\`, `gi_ssj\`, `gi_ssj2\`. Read its header and `docs\RE-BIBLE.md` (search "gi_art") first. Use superpowers-style systematic debugging: find the root cause before you change code.

## Defect (me: "the chest/chin section is messed up completely in frame 3/4")

Set 157 (gi base, from set 56) anim 9 dir 0 (the base to Super Saiyan step; all 4 dirs share these frames). Index 2 and 3 differ from index 1 in the chin and belt area, but the armored source frames are identical there (set 56 9.0.1 and 9.0.3 match row for row in rows 17-25):

| Row | gi 9.0.1 (good) | gi 9.0.2 and 9.0.3 (bad) |
|---|---|---|
| 18 | `e3xe444ex3e` (skin under the chin) | `e3xepppex3e` (chin turned to gi purple 88) |
| 22-23 | row 22 `xPpppPx`, row 23 belt `RrrrrrR` | belt jumps up to row 22, row 23 `xpppppx` |

Index 1 has brown flash hair, indices 2-3 have gold hair, so a hair-color or head-bottom rule is a likely suspect. Prove it; do not assume.

**Second defect (10:38 PM, "same belt issue, it's likely one pixel down").** In both transformation steps, the belt must stay on the same screen row (frame row + dy) in all 4 frames of anim 9. Today it drops by 1 row after frame 0:
- Set 158 (gi_ssj, the Super Saiyan to Super Saiyan 2 step): 9.0.0 belt row 22, 9.0.1-9.0.3 belt row 23, same dy. The armored source (set 59) has a torso 1 px longer in frames 1-3, so the converter places the belt there. Required: belt on frame 0's screen row in every frame, and the gi top of the trousers fills the row under it. Keep the leg and boot rows where they are.
- Set 157 (gi_base, the base to Super Saiyan step): check 9.0.0 against 9.0.1-9.0.3 the same way and apply the same rule.
- Implement it as a rule (for example, belt row per anim and dir anchored to the first frame of that anim when the armored sources only stretch the torso), not as per-frame pixel edits. Note: `transform158.py` copies its body rows from gi_ssj and also copies rows 23-25 from index 2 into index 3; after your fix, check its output frames 1-3 have the belt on frame 0's screen row (its frames use dy - 1, so the belt row there is one more). Adjust `transform158.py` only if needed, and say so.

## Task

1. Find the root cause in gi_art.py. Quote the code line(s).
2. Fix the rule, not the frames. A FIXES entry only if a rule cannot express it, with the reason.
3. Sweep all three forms for the same failure: frames where gi purple sits directly under the mouth or chin, and frames in one anim and dir whose belt row differs while the armored sources keep the same body rows. Use two search shapes and report counts for each. List every frame the fix changes per form.
4. Tests in `scripts\permanent\tests\test_gi.py`: 9.0.2 and 9.0.3 of gi_base keep chin skin at row 18 and the belt on the same row as 9.0.1. Run the whole suite: `py -3 -I -m unittest discover -s scripts\permanent -p "test_*.py"` (93 tests pass now).
5. Run `gi_art.py all`. View the changed frames at 6x against the armored originals before you report. Judge by eye, not only by counts.
6. Re-run the SSJ2 frame chain so the review folders carry the fix, in this order: `py -3 -I art\golden\work_r3\transplant.py`, `finish_v2.py`, `bodyfix.py --apply`, `strips.py`, then `transform158.py` and `base_step.py`. Read each script's header first. Report any script that fails or changes approved frames (the golden idle slots must stay byte-identical to `art\golden\golden_gi_*`).

## Limits

- Never edit anything under `art\golden\` except running the work_r3 scripts named above. Nothing under `data\`.
- Do not build a ROM. Never touch `builds\`.
- Python files: LF line ends, no byte order mark, no em or en dashes. Install nothing.

## Report

Save it as `docs\tasks\2026-10-17-gi-fix-step\gi-fix-step-report.md`: root cause (file:line, quoted), the rule change, sweep counts per search shape, frames changed per form, test count, and a 6x before/after sheet path. Then reply with status and a 3-line summary only.

