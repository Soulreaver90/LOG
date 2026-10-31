# Cell Jr trial v5: AI changes only (final, 2026-10-29 4:31 PM)

Read `LOG\README.md`, `docs\tasks\global.md`, the
v1-v4 briefs and reports in this folder, `docs\tasks\2026-10-25-celljr-hitbox\celljr-balance-report.md` and
`celljr-hitbox-report.md`, and the bible rows tagged CJH, CJB, CJR, CJT, CJ2, CJ3 and CJ4. The module is
`scripts\permanent\patches\celljr_fight.py`, built through `scripts\permanent\build_list_trial.txt`.

## Final decisions (verbatim)

"Let's try just the AI changes, not the stats."

## Change

1. The 4 trial Jrs use a new AI: a copy of AI 21 with a 30-frame wait after each punch (as the vanilla group AIs the
   balance report names) and a blast roll of 2.5 % (0x666 where AI 21 reads 0xCCC at `rom:0x6D23E4`; confirm the
   scale). Stats stay as type 26: HP 4990, POW 50, the rest unchanged.
2. Never change AI 21 or type 26 in place: the relay Jr fights use them. If the AI is chosen by the type entry, add a
   trial-only type entry (a copy of type 26 with the new AI) in the expansion area, as CJH option 1b. Find the type
   words through the spawn items and check that v4 moved nothing. Say which route you took and why, with evidence.
3. Keep everything else in v4: 7 Jrs spawn, 4 fight at once, Jrs 3-4 at (388,366) and (476,370).

## Task

- Change the module, keep its tests green, add tests for the change (AI 21 and type 26 bytes unchanged, the new
  wait and roll values, the trial Jrs point at the new entry). Run the full suite once at the end.
- `--list` must still give r39 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`. The trial list SHA-1 changes from `abbe5004`:
  update the tests that pin it, including the vegeta tests that pin `build_list_trial.txt` or the vegeta list, and
  say which pins you changed.
- Build `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr_v5.gba` with a copy of the v4 save as
  `log2_poc_r39_celljr_v5.sav` (exclusive create for both).
- List the diff runs v4 to v5. Every run must fall inside a declared site.
- Give the expected effect in numbers: punches per second from one Jr and from 4 crowded Jrs, before and after; blasts
  per minute before and after.
- Bible rows (tag CJ5) as `## Section N` blocks in `scripts\one-time\2026-10-24-celljr-trial\bible_rows_v5.md`.

## Report

`docs\tasks\2026-10-24-celljr-trial\celljr-trial-v5-report.md`: SHIPPED and PENDING tables, the AI change with
addresses, the numbers, SHA-1s, diff runs, test counts, the pins changed, and what to watch in play. Label claims
CONFIRMED, LIKELY or SPECULATIVE and quote the proving line or address.

## Limits

- Python: `py -3.14 -P`. The default `py -3` is 3.15, which has no Pillow.
- Never write under `data\`. Never overwrite a ROM, save or state. Python: LF, no em or en dashes. Never `cd` or
  `Push-Location`, in any shell; absolute paths only. Scripts and outputs go in
  `scripts\one-time\2026-10-24-celljr-trial\`.
- Do not edit `chapter_cards.py`, `relay_cooldown.py`, `fullpower_hud.py`, `beam_struggle.py`, `vegeta_ssj_scene.py` or
  their tests, except the SHA-1 pins named above. Do not edit any build list.
- A read-only study task works in `scripts\one-time\2026-10-25-chapter-cards\`. I am editing
  `docs\RE-BIBLE.md` and `docs\ledger\`. Do not touch them.

