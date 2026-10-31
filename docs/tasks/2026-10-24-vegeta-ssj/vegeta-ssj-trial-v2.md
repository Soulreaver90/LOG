# Vegeta Super Saiyan trial v2: longer exchange (final, 2026-10-25 9:16 AM)

Read `LOG\README.md`, `docs\tasks\global.md`, the v1
brief and report in this folder (`vegeta-ssj-trial.md`, `vegeta-ssj-report.md`), and the bible rows tagged VSJ, CJ2,
SPA and CGS. The module is `scripts\permanent\patches\vegeta_ssj_scene.py`, built through
`scripts\permanent\build_list_trial_vegeta.txt`.

## My verdict on v1 (verbatim)

"I tested the vegeta thing, my recommendation is to extend things a bit. Have vegeta do a couple of quick ki blasts,
he does one and cell responds with 3, have him do 3 and when cell does his 3, it knocks vegeta down instead of him
remaining standing."

Keep the v1 Super Saiyan power-up and look.

## Changes

1. **Find the scene he means.** In vanilla, the exchange where Vegeta fires one ki blast and Cell answers with 3 is
   LIKELY attack 1 (self-destruct table `rom:0x3EB704`, seq 50, after "He will pay!!!!"). Confirm it from the record
   bytes. If attack 2 (seq 17) has the same shape, say so and apply the change to both.
2. **Vegeta fires 3 quick ki blasts** instead of one. Reuse the vanilla op that fires his one blast (`ext 96` or
   `ext 142`, state 5) three times, with the timing of a quick volley. Cell's reaction to each hit stays vanilla.
3. **Cell's 3 blasts knock Vegeta down.** Find the vanilla knock-down: a state or animation that scene actors use
   when a hit knocks them down (search other scenes for an actor that falls), and check that set 140 has it. If set
   140 lacks the down animation, say so with the anim rows and propose the smallest route (for example, swap back
   to set 137 for the fall, or reuse the anim of another set); do not draw art.
4. **What happens after the fall**: Vegeta stays down until the scene removes him (seq 52), unless a vanilla line
   needs him up. Say what you chose and why.

## Task

- Change the module, keep its tests green, add tests for the changes, run the full suite once at the end (today
  718 OK).
- `--list` must still give r39 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`, and `--list build_list_trial.txt` must
  still give `1826ca8f6b498844323f9c487cee1864025c3aa8`.
- Build `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v2.gba` (exclusive create; never overwrite the v1
  ROM or save). Copy the v1 save to `log2_poc_r39_vegeta_v2.sav` (exclusive create).
- List the diff runs v1 to v2 and r39 to v2.
- Bible rows (tag VS2) as `## Section N` blocks in `scripts\one-time\2026-10-24-vegeta-ssj\bible_rows_v2.md`.

## Report

`docs\tasks\2026-10-24-vegeta-ssj\vegeta-ssj-v2-report.md`: SHIPPED and PENDING tables, the vanilla precedent for
each change with its address, SHA-1s, diff runs, test counts, what to watch in play. Label claims CONFIRMED, LIKELY
or SPECULATIVE and quote the proving line or address. If a claim needs an emulator run, say so.

## Limits

- Never write under `data\`. Never overwrite a ROM, save or state. Python: LF, no em or en dashes, `py -3 -P`.
  Never `cd`, in any shell; absolute paths only. Scripts and outputs go in
  `scripts\one-time\2026-10-24-vegeta-ssj\`.
- Do not edit `celljr_fight.py`, its tests, `build_list.txt` or `build_list_trial.txt`.
- I am editing `art\base-audit\` and `scripts\one-time\2026-10-23-base-audit\`. Do not touch them.

