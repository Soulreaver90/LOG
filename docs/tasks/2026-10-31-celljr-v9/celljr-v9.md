# Cell Jr v9: drop the flying sound effect

2026-10-31, after I play tested v8: "Cell jr is good, we just need that flying sprite we do not
yet have. So either we do that or we drop the flying sound effect and just leave them walking in. I think
walking in is the easiest option, just need to drop the flying sound effect."

Decision: keep the walk-in. Remove the flying sound. We have no flying sprite, so the sound does not match
what the player sees.

## Files you may edit

1. `scripts\permanent\patches\celljr_fight.py`
2. `scripts\permanent\tests\test_celljr_fight.py`

Edit nothing else. Another task is working in `chapter_cards.py` and `build_list_trial_chapters.txt`.
Never open those two files.

## The change

`FLY_SOUND` is sound 26, declared at line 171. It plays at three moments, from two call sites:

| Site | Line | Who hears it |
|---|---|---|
| `_arrive_and_swap` | 247 | the single Jr at `fight_start`, and the 3-Jr group at `one_v_one_end` |
| `finish` | 300 | the 3 Jrs that walk in for the final fight |

Remove the sound at both sites. All three moments use a walk animation, so all three mismatch.

Then clean up what the removal leaves behind:

- Line 171 is `FLY_FROM_Y, FLY_SOUND = 248, 26`. `FLY_FROM_Y` is still used. Split the assignment and delete
  the `FLY_SOUND` name and the part of its comment that describes it. Do not leave an unused constant.
- Fix any docstring that still promises a sound. Line 244 and line 296 are the two to read.

## Gate: prove the change is exactly this and nothing more

1. Build v9: `py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial.txt
   --out <LOG>\builds\log2_poc_r40_celljr_v9.gba --log <the matching log>`. The file must not exist first.
   Check absence, then create.
2. Rebuild the main list and confirm its SHA-1 is still `14d6b831`. The main list has no celljr module, so
   main must not move.
3. Run the full suite once: `py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t
   <LOG>\scripts\permanent`. Report the count and the exit code.
4. **The real proof.** Disassemble or dump the three changed scene blocks from the v8 ROM and from the v9
   ROM, and compare them op by op. Report the diff. The only difference must be three removed `46 26` ops
   and the length and offset shifts that follow from them. If any other op moved, changed or vanished, stop
   and report that instead of carrying on. Use `scripts\permanent\scene\scene_lib.py` and `scene_probe.py` for the
   op names. The v8 ROM is in `builds\`.

A screen capture cannot prove a sound is gone, so the byte diff in step 4 is the gate. Do not run the
emulator for this task.

## Report

In the report give: the v9 SHA-1, the main SHA-1, the suite count and exit code, the op diff from step 4,
and the exact lines you changed.
