# Vegeta goes Super Saiyan when he attacks Super Perfect Cell: trial module (final, 2026-10-24 9:05 PM)

Read `LOG\README.md`, `docs\tasks\global.md` and the
bible rows on the Cell Games scenes, set swaps and forms (tags CGS, SPA, CJR, CJT, CJ2, FRM, FCD). Read the modules
`scripts\permanent\patches\cellgames_ssj.py`, `fullpower_ssj.py`, `superperfect_cell.py` and `celljr_fight.py` first:
they already put Gohan and Goku in Super Saiyan through the Cell Games and edit the self-destruct table.

## My ask (verbatim)

"Also when Vegeta attacks S perfect cell, have him go super saiyan please!"

## Task

1. Find the scene (or fight) where Vegeta attacks Super Perfect Cell: script records, the actor or fighter that is
   Vegeta, his set and form. Say whether he is a scene actor, the controlled fighter, or both. Quote addresses.
2. Find how Vegeta's Super Saiyan look exists in the ROM (set, palette, form state). Reuse the vanilla or existing
   module mechanism (for example the way `cellgames_ssj` swaps Gohan and Goku). If Vegeta has no Super Saiyan set,
   say so and stop at a design with my art list. Do not draw art.
3. If he becomes the controlled fighter in that stretch: say how the form, the ki drain, the HUD v2b ki pool and the
   form cooldown (bible FCD) behave. Keep vanilla rules unless my ask needs a change, and name each change.
4. Write a new trial patch module `scripts\permanent\patches\vegeta_ssj_scene.py` with tests
   `scripts\permanent\tests\test_vegeta_ssj_scene.py`, in the style of the existing modules (header, source checks
   before the first write, a second run raises).
5. Make a new list `scripts\permanent\build_list_trial_vegeta.txt` = the lines of `build_list_trial.txt` (including
   `celljr_fight`) plus `vegeta_ssj_scene`, so I play all trial changes in one ROM. Do not edit
   `build_list.txt` or `build_list_trial.txt`. `--list` must still give r39 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`
   and `--list build_list_trial.txt` must still give `1826ca8f6b498844323f9c487cee1864025c3aa8`.
6. Build `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta.gba` (exclusive create). Give I a way to
   reach the scene: a save copied from `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr_v2.sav` (exclusive
   create, same folder, `.sav` next to the ROM), and say which slot and what to play.
7. Full suite once at the end (today 700 OK). List the diff runs r39 to the new ROM and v2 to the new ROM.
8. Bible rows (tag VSJ) as `## Section N` blocks in `scripts\one-time\2026-10-24-vegeta-ssj\bible_rows.md`.

Label every claim CONFIRMED, LIKELY or SPECULATIVE and quote the proving line or address. If a claim needs an
emulator run, say so and give my check steps; do not guess.

## Report

`docs\tasks\2026-10-24-vegeta-ssj\vegeta-ssj-report.md`: SHIPPED and PENDING tables, the scene and mechanism with
addresses, SHA-1s, diff runs, test counts, what to watch in play.

## Limits

- Never write under `data\`. Never overwrite a ROM, save or state. Python: LF, no em or en dashes, `py -3 -P`.
  Never `cd`, in any shell; absolute paths only. Scripts and outputs go in
  `scripts\one-time\2026-10-24-vegeta-ssj\`.
- Do not edit `celljr_fight.py`, its tests, `build_list.txt` or `build_list_trial.txt`. If `vegeta_ssj_scene` must
  touch a site that `celljr_fight` or `superperfect_cell` also writes, stop and report the conflict with addresses.
- Another task studies the beam struggle (read only). I am editing `art\base-audit\` and
  `scripts\one-time\2026-10-23-base-audit\`. Do not touch them.

