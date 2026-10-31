# Cell Jr hitboxes: study (final, 2026-10-25 2:44 PM)

Read `LOG\README.md`, `docs\tasks\global.md` and the
bible rows on combat, hit tests, enemy types and the Cell Jr trial (tags CJR, CJT, CJ2, CJ3, BLK, EFX and any combat
or collision tags the source list names).

## My report (verbatim)

"The hitbox for the Cell Jrs' attacks seem pretty big, it's hard to hit them but they hit far, can a task check it?"

Context: in the `celljr_fight` trial (`scripts\permanent\patches\celljr_fight.py`, ROM
`builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr_v3.gba`) Super Saiyan 2 Gohan fights 4 Cell Jrs at once (enemy
type 26, `set:31`). In vanilla, Piccolo, Vegeta and Trunks each fight one Jr in the Cell Games relay.

## Task (study only: no patch, no build-list change)

1. **How hits are tested.** Find the code that tests a melee hit and a projectile hit between the player and an enemy:
   where each side's box comes from (a per-type table, the sprite frame, a per-anim box, a fixed size), and the box
   values. Quote addresses.
2. **Cell Jr numbers.** Give the Jr's hurtbox (where Gohan must hit) and the reach of each Jr attack (melee box or
   range, projectile size), next to the same numbers for: Gohan's own attacks, a vanilla Jr in the relay fight, and
   two ordinary enemies of similar size. Render the boxes over the sprite frames (PNG) so I can see them.
3. **Vanilla or ours?** Say whether the big reach and the small hurtbox are vanilla Jr data or come from the trial (for
   example type 26 data, set 31 frames, the NPC-to-enemy swap, spawn items 13-16, Gohan's SSJ2 form). Check the r39
   bytes and the trial bytes.
4. **Fix options** (do not build): for example a smaller attack box, a larger hurtbox, or a per-type value, each with the
   bytes it would touch, whether it changes the vanilla relay Jr fights too, and the risk. Recommend one.
5. If a fact needs an emulator run (for example a box read from RAM in a fight), list the exact states and steps.
6. Bible rows (tag CJH) as `## Section N` blocks in `scripts\one-time\2026-10-25-celljr-hitbox\bible_rows.md`.

Label every claim CONFIRMED, LIKELY or SPECULATIVE and quote the proving line or address.

## Report

`docs\tasks\2026-10-25-celljr-hitbox\celljr-hitbox-report.md`: SHIPPED and PENDING tables, the hit test, the numbers
table, vanilla or ours, the options and the recommendation. Renders in `scripts\one-time\2026-10-25-celljr-hitbox\`.

## Limits

- Read only, except your report, rows file, scripts and renders (in `scripts\one-time\2026-10-25-celljr-hitbox\`).
- Never write under `data\`. Python: LF, no em or en dashes, `py -3 -P`. Never `cd`, in any shell; absolute paths
  only.
- Other work is changing `vegeta_ssj_scene.py` and building `chapter_cards` and beam mockups. I am editing
  `art\base-audit\`, `scripts\one-time\2026-10-23-base-audit\` and `docs\RE-BIBLE.md`. Do not touch them.

