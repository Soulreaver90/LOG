# Cell Jr trial v3: my play-test fixes (me, 2026-10-25 9:24 AM and 9:47 AM)

Read `LOG\README.md`, `docs\tasks\global.md`, the v1 and
v2 briefs and reports in this folder, and the bible rows tagged CJR, CJT, CJ2. The module is
`scripts\permanent\patches\celljr_fight.py`, built through `scripts\permanent\build_list_trial.txt`.

## My verdict on v2 (verbatim)

1. "Right before the Cell Jrs, your adjustment has Cell just awkwardly teleport to the right, why not just have him
   stay where he is? The next scene is a fade anyway so his reposition there is unnoticed."
2. "The 4 extra that spawn, 2 spawn directly in front, too close to Gohan and Cell, maybe have them spawn in the
   back. Apart from that it's fine."

Keep everything else from v2: Cell faces Gohan, the Jrs walk in from the top, Gohan faces Super Perfect Cell in the
seq 58 talk, no HP refill, difficulty, EXP and flow.

## Changes

1. **Cell stays where he stands.** v2 item 17 (NPC Cell with the face-the-player step) spawns at (616,384). Find where
   Cell stands just before record X runs (the actor that item 17 replaces: its position and facing) and spawn item 17
   at that exact spot, so the swap shows no jump. The later reposition behind the fade stays as it is. If the swap
   itself is visible (one frame of no Cell), say so and propose the smallest fix.
2. **The 2 Jrs that land in front go to the back.** Identify which Jrs I mean: LIKELY the 4 that appear
   after "My children!" in the seq 31 copy, 2 of which spawn in front of Gohan and Cell. Confirm from the spawn
   coordinates against Gohan's and Cell's positions, and say which records and coordinates you change. Move those 2
   behind Cell (away from Gohan, on the far side), clear of the other Jrs and of the walls.

## Task

- Change the module, keep its tests green, add tests for both changes, run the full suite once at the end (today 744
  OK). `--list` must still give r39 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`.
- `build_list_trial_vegeta.txt` includes `celljr_fight`, so its build changes too. Keep `test_vegeta_ssj_scene` and
  `test_relay_cooldown` green without editing those modules; if a test there pins a SHA or address that your change
  moves, stop and report it.
- Build `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr_v3.gba` and copy the v2 save to `log2_poc_r39_celljr_v3.sav`.
  Also build the Vegeta list to `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v2_cj3.gba` with a copy of
  the Vegeta v2 save as `log2_poc_r39_vegeta_v2_cj3.sav`, so I can play all trial changes in one ROM. Exclusive
  create for every file; never overwrite.
- List the diff runs v2 to v3 and r39 to v3.
- Bible rows (tag CJ3) as `## Section N` blocks in `scripts\one-time\2026-10-24-celljr-trial\bible_rows_v3.md`.

## Report

`docs\tasks\2026-10-24-celljr-trial\celljr-trial-v3-report.md`: SHIPPED and PENDING tables, the positions before and after
with their addresses, SHA-1s, diff runs, test counts, what to watch in play. Label claims CONFIRMED, LIKELY or
SPECULATIVE and quote the proving line or address.

## Limits

- Never write under `data\`. Never overwrite a ROM, save or state. Python: LF, no em or en dashes, `py -3 -P`.
  Never `cd`, in any shell; absolute paths only.
- Do not edit `vegeta_ssj_scene.py`, `relay_cooldown.py`, their tests or lists, `build_list.txt`, or any list but
  `build_list_trial.txt` (no change there is expected either).
- Other tasks are building `chapter_cards` (its own module, tests and list) and beam mockups in
  `art\mockups\2026-10-25-beam-struggle\`, and reading the disasm clones. I am editing `art\base-audit\` and
  `scripts\one-time\2026-10-23-base-audit\`. Do not touch them.

