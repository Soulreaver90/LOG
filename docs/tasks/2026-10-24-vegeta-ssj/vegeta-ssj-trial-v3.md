# Vegeta Super Saiyan trial v3: the anime exchange (final, 2026-10-25 12:44 PM)

Read `LOG\README.md`, `docs\tasks\global.md`, the v1 and
v2 briefs and reports in this folder, and the bible rows tagged VSJ, VS2, CJ3, FPH, SPA and CGS. The module is
`scripts\permanent\patches\vegeta_ssj_scene.py`, built through `scripts\permanent\build_list_trial_vegeta.txt`.

## My verdict on v2 and the v3 ask (verbatim)

"Vegeta v2 is great!" Then: "Instead of 3, can Vegeta do 5 ki blasts in quicker succession, I think there have been
movements of that. If not keep the 3. And then instead of Cell returning 3, he quickly walks up to Vegeta, does a
single punch which knocks Vegeta back which knocks him out (leaving the same distance currently between Vegeta and
Cell). Gohan walks in just as Cell does a ki blast which hits Gohan instead (and he reacts with a standard hit
animation), then it continues with the dialogue. This mirrors the anime where [Cell] hits Vegeta with a 1-hit KO and
Gohan takes the ki blast hit that was meant to kill Vegeta."

Keep: the Super Saiyan power-up and look, attack 2 (seq 17) as is, the black hair on the fall (me: "keep black").

## Changes (attack 1, seq 50 copy)

1. **5 ki blasts, quicker.** Vegeta fires 5 `ext 96` blasts with a shorter hold than v2's 32 frames. Find whether the
   hold or fire frame can be shortened per call, or whether a vanilla op or actor state fires faster (a precedent of
   a rapid volley in any scene). If 5 quick blasts are not possible without engine code, keep 3 and say why. Cell
   keeps his vanilla reaction to each hit, or a shorter one if 5 reactions drag; say what you chose.
2. **Cell walks up and punches once.** Cell walks quickly to Vegeta (walk op with a fast speed, vanilla precedent),
   plays a single punch (find the melee or punch state or anim that scene actors use, and check set 58 has it), and
   Vegeta is knocked back (knock-back precedent) and down, landing so that the final Vegeta-to-Cell distance equals
   v2's. Vegeta's fall uses the v2 knock-down (`ext 57 (140, 3)`, hair turns black).
3. **Gohan takes the blast.** Cell fires a ki blast at the downed Vegeta; Gohan walks in between just in time and the
   blast hits Gohan, who plays the standard hit reaction (the same hurt op the scenes use). Then the vanilla dialogue
   continues. Gohan's position after this must not break seq 52, which places him at (432,472).
4. **Aura loop.** The fullpower-hud study found that the NPC Vegeta power-up copies start sound 55 (the Super Saiyan
   aura loop) with no stop (`rom:0x90A696` and `rom:0x90A77C` in the vegeta_v2_cj3 build). Check how vanilla NPC
   power-ups end the loop (Goku's NPC power-up `rom:0x3D35D4` and its scene) and stop the loop at the right point in
   both copies (attack 1 and attack 2), for example when Vegeta is knocked out and when attack 2 ends.

## Task

- Change the module, keep its tests green, add tests for the changes, run the full suite once at the end (today 771
  OK). `--list` must still give r39 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`, and `--list build_list_trial.txt` must
  still give `76e610fb3ca4febcf1cefd1199ef39fad10ccbf8`.
- Build `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v3.gba` and copy the v2_cj3 save to
  `log2_poc_r39_vegeta_v3.sav` (exclusive create for both; never overwrite).
- List the diff runs v2_cj3 to v3 and r39 to v3.
- Bible rows (tag VS3) as `## Section N` blocks in `scripts\one-time\2026-10-24-vegeta-ssj\bible_rows_v3.md`.

## Report

`docs\tasks\2026-10-24-vegeta-ssj\vegeta-ssj-v3-report.md`: SHIPPED and PENDING tables, the vanilla precedent for each
step with its address, the timing (frames per step), SHA-1s, diff runs, test counts, what to watch in play. Label
claims CONFIRMED, LIKELY or SPECULATIVE and quote the proving line or address. If a claim needs an emulator run, say
so.

## Limits

- Never write under `data\`. Never overwrite a ROM, save or state. Python: LF, no em or en dashes, `py -3 -P`.
  Never `cd`, in any shell; absolute paths only. Scripts and outputs go in
  `scripts\one-time\2026-10-24-vegeta-ssj\`.
- Do not edit `celljr_fight.py`, `relay_cooldown.py`, `fullpower_hud.py`, their tests, `build_list.txt` or any list but
  your own (no change to `build_list_trial_vegeta.txt` is expected).
- Another task is building `chapter_cards` (its own module, tests and list). I am editing
  `art\base-audit\`, `scripts\one-time\2026-10-23-base-audit\` and `docs\RE-BIBLE.md`. Do not touch them.

