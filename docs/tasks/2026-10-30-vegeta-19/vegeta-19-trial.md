# Vegeta 19 reveal trial: Vegeta goes Super Saiyan after his line (final, 2026-10-30)

Read `LOG\README.md`, `docs\tasks\global.md`,
`docs\tasks\2026-10-30-celljr-rework-plan\plan-report.md` item 11, the Vegeta SSJ trial reports
(`docs\tasks\2026-10-24-vegeta-ssj\`, the transform model in `scripts\permanent\patches\vegeta_ssj_scene.py`), and the bible
rows tagged CJP, VSJ, VS2-VS5, CGS and FRM. Look at how existing trial modules are built and tested (for example
`relay_cooldown.py` and its test and `build_list_trial_cooldown.txt`).

## My words

"For Vegeta against Android 19, he says 'So, does a machine like yourself ever experience fear?' and the fight starts,
he can transform. In the anime, this is the SSJ reveal. Let's have him transform after the dialogue (no permanent ki)."

The plan (item 11): the line is seq 41 `0x083D4076` in the 19 table `rom:0x3D40C8`; Vegeta is already forced for the
fight (record `0x083CCA2E`); copy seq 42 with a transform head and repoint the table word `rom:0x3D416C`. The space
scene `rom:0x21F0` table (flag 77) already shows his first Super Saiyan; leave it as is (my question 9 open).

## Task

1. New trial module `scripts\permanent\patches\vegeta_19_reveal.py` and test file, built through a new list
   `scripts\permanent\build_list_trial_vegeta19.txt` (the main list lines, then this module). Right after the line,
   Vegeta transforms to Super Saiyan in the scene (the same visual transform as `vegeta_ssj_scene`: pose, flash, aura,
   sound), then the fight starts with Vegeta in his normal Super Saiyan form: the player can drop it and it drains ki
   as usual. No permanent form, no ki lock. Prove the form state at the fight start is the normal pool Super Saiyan.
2. Check that the module does not touch any record another trial module changes (`celljr_fight`, `vegeta_ssj_scene`,
   `beam_struggle`, `relay_cooldown`, `fullpower_hud`, `chapter_cards`), and that it builds after all of them in one
   list (give the combined SHA-1, in memory only).
3. Tests green, full suite once at the end. `--list` must still give r39 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`.
4. Build `builds\mockups\2026-10-30-vegeta-19\log2_poc_r39_vegeta19.gba` with a save placed just before the 19 scene
   (base it on `builds\mockups\2026-10-25-chapter-cards\log2_poc_r39_chapters_v5_pre_a.sav` slot 3 or the presave tools in
   `scripts\one-time\2026-10-25-chapter-cards\presave_*`; set flags as the game would), exclusive create for both. Give
   play steps.
5. Diff runs r39 to the trial; all inside declared sites. Bible rows (tag V19) as `## Section N` table blocks in
   `scripts\one-time\2026-10-30-vegeta-19\bible_rows.md`.

## Report

`docs\tasks\2026-10-30-vegeta-19\vegeta-19-report.md`: SHIPPED and PENDING tables, the scene change (records before and
after), the form proof, SHA-1s, diff runs, test counts, play steps. Label claims CONFIRMED, LIKELY or SPECULATIVE.

## Limits

- Python: `py -3.14 -P`. LoG II base ROM: `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba`.
- Never write under `data\`. Never overwrite a ROM, save or state: exclusive create. LF, no em or en dashes. Never `cd`
  or `Push-Location`; absolute paths only. Scripts go in `scripts\one-time\2026-10-30-vegeta-19\`.
- Do not edit any other module, its tests or any other list. Another task edits `chapter_cards.py` and its test now.
  A study task works in `LOG\zhack\`. I am editing `docs\RE-BIBLE.md` and `docs\ledger\`.

