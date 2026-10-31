# Block mockup v3: use the LoG II hurt frame as the block pose, tested with Goku (final, 2026-10-24 7:53 AM)

Personal GBA ROM hack (Legacy of Goku II merged with Buu's
Fury). The block mockup v2 is `builds\mockups\2026-10-24-block\log2_poc_r37_block2.gba` (SHA-1 `c5c654fb070a449f781626b9108f6b4123ebc4e6`),
built by `scripts\one-time\2026-10-24-block\build_mock.py` from r37 (`builds\log2_poc_r37.gba`, SHA-1
`3877033c65d724a299a364f66a4c3d75a4df4566`). Read `docs\tasks\2026-10-24-block\block-study-report.md` first (design, hooks, tests).

## My ask (verbatim)

"Block is missing the block animation frame, which already exists in LOG2 when the person is hit somewhat. We can test with
just goku"

v2 holds the stand frame (`BLOCK_ANIM, BLOCK_FRAME = 0, 0` in `build_mock.py`). I say LoG II already has a guard-like
frame inside the hit (hurt) animation. The study says the hurt state uses anim 2.

## Task

1. Render every frame of anim 2 (all dirs and indices) for Goku's player sets (set 60 and the other Goku sets in
   `scripts\permanent\rom\log2_save.py` `APPEARANCE_SET`), enlarged, into `scripts\one-time\2026-10-24-block\pose\`. Also render anim 2 for set 56
   (armor Gohan) and set 157 (gi Gohan) so I see the same frame on Gohan. Find the frame that reads as a guard pose
   (arms raised or crossed in front). If anim 2 has none, check the other short reaction anims and say which one you used.
   Label the choice CONFIRMED (frame data read) and say in words what the pose shows.
2. Check how the hurt state shows anim 2 per dir (flips, dx and dy) and make the BLOCK state show the chosen frame the same way
   in all four dirs. Prove from the code that the BLOCK enter uses the same anim row layout (`BLOCK_ROW = 0x4C + 16 x anim`) for
   every set, and that the chosen anim and frame exist in every player set (a set with fewer frames must not read past its
   table). If one does not, say which and fall back to the stand frame for that case only if it can be done by reading.
3. Build v3 as a new file: copy `build_mock.py` to `build_mock3.py` (Write tool), change only the pose constants and the
   output name to `mockups\log2_poc_r37_block3.gba`, and keep v2 and its files untouched. Exclusive create. Update a copy of
   the tests (`test_block3.py`) and the diff proof (`diff_proof3.txt`): every run named, 0 bytes outside named regions.
4. Make a Goku test pair by exclusive create: `log2_poc_r37_block3_goku.gba` (copy) and `.sav` where slot 1 has leader Goku
   (`log2_save.py set ... leader=4`) standing near enemies on a combat map where the block works (the v2 R mask allows it
   only on combat maps). Prove the slot with `log2_save.py info`. Give my steps: where to walk, which enemy, what a pass
   looks like (pose shows while R is held, small damage, short push, pose ends when R is released).

## Report

`docs\tasks\2026-10-24-block\block-pose-report.md`: the chosen frame with the rendered image paths, the per-set check, SHA-1 of every
new file, the diff proof, test results, my steps. Bible rows (tag BLP) in `scripts\one-time\2026-10-24-block\pose\bible_rows.md`, in the
format of `scripts\one-time\2026-10-24-block\bible_rows.md`.

## Limits

- Never write under `data\`. Never overwrite any ROM, save or state. No change to `scripts\permanent\`, `build_list.txt`,
  `art\` or `docs\`. Do not touch `art\base-audit\` or `scripts\one-time\2026-10-23-base-audit\` (I am editing them).
- Python: LF, no byte order mark, no em or en dashes. `py -3 -P`. Never `cd`, in any shell, ever; absolute paths only. Create
  and edit files with the Write and Edit tools or Python `open(..., "x")`, never shell redirection, `sed`, `printf`, `cp`,
  `rm` or `mkdir`. Label findings CONFIRMED, LIKELY or SPECULATIVE.

