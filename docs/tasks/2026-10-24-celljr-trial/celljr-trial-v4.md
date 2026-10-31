# Cell Jr trial v4: the 2 moved Jrs go to my circles (final, 2026-10-25 2:39 PM)

Read `LOG\README.md`, `docs\tasks\global.md`, the v3 brief
and report in this folder, and the bible rows tagged CJR, CJT, CJ2, CJ3. The module is
`scripts\permanent\patches\celljr_fight.py`, built through `scripts\permanent\build_list_trial.txt`.

## My verdict on v3 (verbatim)

"For the Jrs, it looks better if they spawn in the yellow circle and not awkwardly outside to the side."

My screenshot: `docs\tasks\2026-10-24-celljr-trial\owner-jr-spots-2026-10-25.png` (view it). It shows the spawn scene
after v3: the 2 Jrs that v3 moved to (536,384) and (544,416) stand at the right edge. He drew two yellow circles: one
above the left group of Jrs (top left) and one between the middle Jrs and Cell, toward the top.

My estimate from the screenshot (4 screen px per game px; Jr (536,384) at about (745,232) px and Jr (544,416) at about
(778,360) px, feet): left circle about world (390,364), middle circle about world (476,368). Re-derive it yourself
from the image and the known positions; trust your derivation over mine and say where they differ.

## Change

Move seq 31 copy Jrs 3 and 4 (v3: (536,384) and (544,416)) to the centres of the two circles. Check: each spot is on
screen in the spawn scene view, its collision cells are open, it overlaps no other actor (the other Jrs, Gohan, Cell,
the allies), and it does not land in front of Gohan and Cell (the v2 complaint). Keep everything else from v3.

## Task

- Change the module, keep its tests green, add or update tests for the new spots, run the full suite once at the end
  (today 805 OK). `--list` must still give r39 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`.
- `build_list_trial_vegeta.txt` includes `celljr_fight`, so its build changes. Keep `test_vegeta_ssj_scene` green
  without editing it; if a pinned SHA-1 or address moves, stop and report.
- Build `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr_v4.gba` with a copy of the v3 save as
  `log2_poc_r39_celljr_v4.sav`, and the Vegeta list as `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v3_cj4.gba`
  with a copy of the Vegeta v3 save as `log2_poc_r39_vegeta_v3_cj4.sav`. Exclusive create for every file.
- Render the spawn scene positions over a screenshot-sized view (PNG), before and after, so I can compare
  with his circles.
- List the diff runs v3 to v4.
- Bible rows (tag CJ4) as `## Section N` blocks in `scripts\one-time\2026-10-24-celljr-trial\bible_rows_v4.md`.

## Report

`docs\tasks\2026-10-24-celljr-trial\celljr-trial-v4-report.md`: SHIPPED and PENDING tables, the screen-to-world mapping,
the new positions and checks, SHA-1s, diff runs, test counts. Label claims CONFIRMED, LIKELY or SPECULATIVE.

## Limits

- Never write under `data\`. Never overwrite a ROM, save or state. Python: LF, no em or en dashes, `py -3 -P`.
  Never `cd`, in any shell; absolute paths only.
- Do not edit `vegeta_ssj_scene.py`, `relay_cooldown.py`, `fullpower_hud.py`, `chapter_cards.py`, their tests, or any
  list. Another task is writing a new `beam_struggle` module, its tests and its own list; another studies Cell Jr
  hitboxes (read only). I am editing `art\base-audit\`, `scripts\one-time\2026-10-23-base-audit\` and
  `docs\RE-BIBLE.md`. Do not touch them.

