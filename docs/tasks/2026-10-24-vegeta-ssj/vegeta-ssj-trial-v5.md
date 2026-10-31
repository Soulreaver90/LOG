# Vegeta Super Saiyan trial v5: finish v4b, Gohan flies in (final, 2026-10-25 9:10 PM, resumed 2026-10-29)

Read `LOG\README.md`, `docs\tasks\global.md`, the
v1-v4 briefs and reports in this folder, `scripts\one-time\2026-10-24-vegeta-ssj\make_trial_vegeta_v4b.txt`, and the
bible rows tagged VSJ, VS2, VS3, CJ4, SPA and CGS. The module is `scripts\permanent\patches\vegeta_ssj_scene.py`, built
through `scripts\permanent\build_list_trial_vegeta.txt`.

## State

The v4 task stopped when the session restarted, during its final full-suite run. The module and tests on disk equal
v4b: the vegeta list rebuilds to `d3d0a89a`, 41 vegeta tests OK. v4b = v4 with the plain wait `ext 69` in place of
`ext 43` (a fade from white). The v4 report does not cover v4b, and the VS4 rows (`bible_rows_v4.md`) are not merged.

## My verdict on v4b (verbatim)

"For the new Vegeta, it's great. One minor thing, Gohan jumps in front of Vegeta, he should fly in maybe. It's a short
distance but looks less awkward."

## Task

1. Add a v4b section to `vegeta-ssj-v4-report.md`: the change from v4, why `ext 43` was replaced (read the v4b make
   file and the module), SHA-1 `d3d0a89a`.
2. v5: Gohan flies to his spot in front of Vegeta in place of the jump or run. Find how a scene actor flies with his fly
   pose (for example `ext 54`, or the pose and move pair other scenes use for a flying Gohan; quote the vanilla
   script that does it). Keep the timing: Gohan must reach the line between Cell and Vegeta just before the blast,
   and the blast must hit Gohan, who plays the standard hit reaction. Keep everything else in v4b.
3. Keep the module's tests green and add tests for the change. Run the full suite once at the end.
4. `--list` must still give r39 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`, and `--list build_list_trial.txt` must still give
   `abbe5004f7d645329e8a141fadf70096ef6960c5`.
5. Build `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v5.gba` with a copy of the v4b save as
   `log2_poc_r39_vegeta_v5.sav` (exclusive create for both).
6. Render the Gohan path (screen view: Cell, Vegeta, Gohan's flight and the blast path, with frame numbers) as PNG.
7. List the diff runs v4b to v5.
8. Bible rows (tag VS5) as `## Section N` blocks in `scripts\one-time\2026-10-24-vegeta-ssj\bible_rows_v5.md`. Leave
   `bible_rows_v4.md` as it is; I merge both.

## Report

`docs\tasks\2026-10-24-vegeta-ssj\vegeta-ssj-v5-report.md`: SHIPPED and PENDING tables, the fly-in (op, pose, frames,
start and end screen x), the timing against the blast, SHA-1s, diff runs, test counts, what to watch in play. Label
claims CONFIRMED, LIKELY or SPECULATIVE and quote the proving line or address.

## Limits

- Python: use `py -3.14 -P`. The default `py -3` is now 3.15, which has no Pillow.
- Never write under `data\`. Never overwrite a ROM, save or state. Python: LF, no em or en dashes. Never `cd` or
  `Push-Location`, in any shell; absolute paths only. Scripts and outputs go in
  `scripts\one-time\2026-10-24-vegeta-ssj\`.
- Do not edit `celljr_fight.py`, `relay_cooldown.py`, `fullpower_hud.py`, `chapter_cards.py`, `beam_struggle.py`, their
  tests, or any build list.
- I build chapter cards v4 at the same time (its own list and folder) and edits `docs\RE-BIBLE.md` and
  `docs\ledger\`. Do not touch them.

