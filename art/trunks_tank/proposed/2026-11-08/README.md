# Staged tank frames, 2026-11-08: no strap, no gear reveals, plus the front run

These PNGs are the live `art\trunks_tank\` frames with the sword strap taken off, the gear reveals of
an earlier pass taken back out, and the armour review's Findings A and E applied. `run\` holds pass one
of the anim 13 front row, which is new art. **The live frames are untouched.** Nothing here reaches a
ROM until someone copies it up.

Rebuild this folder from the live frames by running the three scripts in order:

```
py -3.14 -P art\trunks_tank\hand-fixes\2026-11-08_drop_strap_and_reveals.py
py -3.14 -P art\trunks_tank\hand-fixes\2026-11-08_armour_head_fixes.py
py -3.14 -P art\trunks_tank\hand-fixes\2026-11-08_run_front_pass1.py
```

Each one prints a line per frame and stops if a frame has moved on.

## Why this is staged and not shipped

`scripts\permanent\tests\test_trunks_tank.py` pins what the live frames may hold. Two of its tests
fail the moment these frames go live, and the task that made them was told not to edit a test.

| Test | Why it fails |
|---|---|
| `test_every_super_saiyan_pixel_comes_from_vanilla_134_or_the_base_tank_png` | It allows a Super Saiyan pixel to be vanilla 134's, the base tank PNG's, or a `COLLAR_FILL` of the base PNG's. Findings A and E take pixels from set 130, a third source. It also asserts 16x32 and splits head from body at `16 * 16`, which a 32x32 run row would fail twice |
| `test_the_manifest_covers_the_frames_the_briefs_name` | It pins the view list and the counts 32, 37 and 53, so no run row may enter the manifest |

Promotion is therefore two steps, and the second one is the owner's or the main loop's:

1. Copy these PNGs over the live ones, and add the run rows to `manifest.json`.
2. Update `test_trunks_tank.py`: allow set 130 as a third source, make the head and body split
   per frame rather than a constant, and move the pinned counts.

## What changed

| Change | Pixels | Note |
|---|---|---|
| Sword strap removed | 48 in the manifest, 51 with `ssj_front` | 62 of the 110 strap-index pixels stay, because they are BELT. The owner has to settle that |
| Scabbard and sword reveals removed | 40 orange and 6 grey in the manifest | the reveals an earlier pass added over vanilla jacket |
| Leftover jacket `4E` removed | 18 | 10 at (4,17) cut or filled with skin, 8 at (5,20) turned into set 134's own `4D` |
| Finding A, the sword in the Super Saiyan back head | 20 in the back idle | 11 lifted from set 130, 9 cut. The 4 back walk frames wait on a measurement |
| Finding E, the Super Saiyan hair tip | 2 px in each of 3 frames | lifted from set 130 |
| The front run, anim 13 dir 0 | 8 new drawings | pass one, in `run\` |

**The belt stays.** Index `4D` is the strap AND the belt's highlight, and `47` is the strap AND the
belt's shadow. `docs\tasks\2026-11-08-trunks-tank-run\report.md` sections 2 and 11 give the four
measurements and the question.

## Sheets

| Sheet | What it shows |
|---|---|
| `sheets\01_whole_front_base.png`, `02_whole_side_base.png` | the whole figure, live beside staged |
| `sheets\03_run_front_base.png`, `04_run_front_ssj.png` | the run, vanilla beside mine, both forms |
| `sheets\05_run_front_both_1x.png` | all 8 run frames at 12x, 3x and game size |
| `sheets\06_findingA_back.png` | Finding A: live, staged, and set 130 |
| `sheets\07a_belt_question_front.png`, `07b_belt_question_side.png` | the belt question, four panels each |
| `sheets\cmp_*.png` | 12 frames, each as vanilla, live and staged |
