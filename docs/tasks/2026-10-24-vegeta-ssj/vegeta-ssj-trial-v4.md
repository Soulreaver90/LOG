# Vegeta Super Saiyan trial v4: Gohan blocks the blast in flight (final, 2026-10-25 4:38 PM)

Read `LOG\README.md`, `docs\tasks\global.md`, the v1-v3
briefs and reports in this folder, and the bible rows tagged VSJ, VS2, VS3, CJ4, SPA and CGS. The module is
`scripts\permanent\patches\vegeta_ssj_scene.py`, built through `scripts\permanent\build_list_trial_vegeta.txt`.

## My verdict on v3 (verbatim)

"Right now Cell shoots the ki AFTER Gohan is in front of Vegeta. In the anime Gohan steps in front to block the ki,
so Gohan walks in front of Cell after he shoots the ki? Also I did say to keep the distance the same but that also
means the ki barely travels, so not sure if we should have Vegeta go farther and recenter Vegeta to the far right and
Cell in the center and Gohan running to the front of Vegeta to take the ki blast?"

## Changes (attack 1, seq 50 copy)

1. **Layout.** After the punch, Vegeta is knocked back farther and lands near the far right edge of the screen; Cell
   stands near the screen centre. Read the camera for this scene and give screen positions. v3 ends with Vegeta at
   x 352, left of Cell at x 404 in world space; if that shows on the left of the screen, change the approach so the
   my layout holds (Vegeta right, Cell centre), and say what you changed. The knock-back distance must give the
   blast a visible flight (say how many frames it flies before the hit).
2. **Order.** Cell fires the ki blast at Vegeta first. While it flies, Gohan runs in (fast move, `ext 136` as in v3)
   and reaches the line between Cell and Vegeta just before the blast does; the blast hits Gohan, who plays the
   standard hit reaction. Then the dialogue. Find how a move and a projectile can run at the same time (one actor
   group, `ext 63` ... `ext 64`), and how the hit wait binds to Gohan when the blast is aimed at Vegeta. v3 aimed it
   at Gohan to avoid a wait that never ends; if aiming at Vegeta is unsafe, aim at Gohan but start the blast before
   Gohan arrives, so it reads as aimed at Vegeta. Say which you chose and why, with evidence.
3. Keep: 3 blasts (the fixed 32-frame hold), the power-up, the punch, the black hair on the fall, the aura stops,
   attack 2, and seq 52 placing Gohan at (432,472) afterwards.

## Task

- Change the module, keep its tests green, add tests for the changes, run the full suite once at the end. Another
  task is editing `chapter_cards.py`; if only `test_chapter_cards` fails, say so and give the counts.
- `--list` must still give r39 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`; `--list build_list_trial.txt` must still give
  `abbe5004f7d645329e8a141fadf70096ef6960c5`.
- Build `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v4.gba` with a copy of the v3_cj4 save as
  `log2_poc_r39_vegeta_v4.sav` (exclusive create for both).
- Render the scene layout (screen view with Cell, Vegeta, Gohan and the blast path, before and after) as PNG.
- List the diff runs v3_cj4 to v4.
- Bible rows (tag VS4) as `## Section N` blocks in `scripts\one-time\2026-10-24-vegeta-ssj\bible_rows_v4.md`.

## Report

`docs\tasks\2026-10-24-vegeta-ssj\vegeta-ssj-v4-report.md`: SHIPPED and PENDING tables, the screen layout, the timing
(frames per step, blast flight), SHA-1s, diff runs, test counts, what to watch in play. Label claims CONFIRMED,
LIKELY or SPECULATIVE and quote the proving line or address.

## Limits

- Never write under `data\`. Never overwrite a ROM, save or state. Python: LF, no em or en dashes, `py -3 -P`.
  Never `cd` or `Push-Location`, in any shell; absolute paths only. Scripts and outputs go
  in `scripts\one-time\2026-10-24-vegeta-ssj\`.
- Do not edit `celljr_fight.py`, `relay_cooldown.py`, `fullpower_hud.py`, `chapter_cards.py`, `beam_struggle.py`, their
  tests, or any list.
- Other tasks are writing `beam_struggle` and `chapter_cards` and studying Cell Jr balance (read only). The main
  session edits `art\base-audit\`, `scripts\one-time\2026-10-23-base-audit\` and `docs\RE-BIBLE.md`.

