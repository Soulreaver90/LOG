# Cell Jr trial v2: my play-test changes (final, 2026-10-24 8:45 PM)

Read `LOG\README.md`, `docs\tasks\global.md`, and the v1
brief and report in this folder (`celljr-trial.md`, `celljr-trial-report.md`). The module is
`scripts\permanent\patches\celljr_fight.py`, built through `scripts\permanent\build_list_trial.txt`.

## My verdict on v1

He played it: "The Jrs were tough but it was a fun challenge." Keep the difficulty, the 4 Jrs, the EXP and the flow.
No HP refill before the Cell fight (decided).

## Changes

1. **Cell faces Gohan during the Jr fight.** Today the NPC Cell placed by record X stands facing one fixed direction.
   He must turn to face the player while Gohan fights the Jrs (the way vanilla NPCs or scene actors track the
   player). Find a vanilla mechanism first (an NPC flag, a "face player" op or ext, an actor behaviour) and cite it.
   If none exists, say so and propose the smallest code route before you write code.
2. **The 4 Jrs fly in from the top of the screen at the fight start**, instead of appearing in place. My
   reason: appearing in place reads as Cell creating more; they come from the top because that is where they fought
   the allies. They fly down to their fight positions, then fight as today. Look for a vanilla precedent (scene
   actors moving with a move or fly op, enemies entering from off-screen, the seq 27 or 31 spawn, Cell Games
   arrivals) and reuse it. Say whether the Jrs fly in as scene actors that become enemies, or as enemies with a
   scripted entry, and why.

## Task

- Change the module, keep its own tests green, add tests for both changes, run the full suite once at the end
  (today 691 OK). The main `--list` build must still give r39 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`.
- Build `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr_v2.gba` (exclusive create; never overwrite the v1 ROM
  or save). Copy the v1 save to `log2_poc_r39_celljr_v2.sav` so the pair loads together.
- List the diff runs v1 to v2 and r39 to v2.
- Bible rows (tag CJ2) as `## Section N` blocks in `scripts\one-time\2026-10-24-celljr-trial\bible_rows_v2.md`.

## Report

`docs\tasks\2026-10-24-celljr-trial\celljr-trial-v2-report.md`: SHIPPED and PENDING tables, the vanilla precedent for
each change with its address, SHA-1s, diff runs, test counts, what to watch in play. Label claims CONFIRMED,
LIKELY or SPECULATIVE and quote the proving line or address.

## Limits

- Never write under `data\`. Never overwrite a ROM, save or state. Python: LF, no em or en dashes, `py -3 -P`.
  Never `cd`; absolute paths only.
- I am editing `art\base-audit\` and `scripts\one-time\2026-10-23-base-audit\`. Do not touch them.

