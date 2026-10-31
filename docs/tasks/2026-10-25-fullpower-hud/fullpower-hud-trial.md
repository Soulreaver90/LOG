# Full-power Super Saiyan: yellow ki on the HUD and no aura sound loop (final, 2026-10-25 12:14 PM)

Read `LOG\README.md`, `docs\tasks\global.md` and the
bible rows tagged FRM, R27, R28, HKS, HKP, HKB, R39, FCD, RCD. Read the modules
`scripts\permanent\patches\cellgames_ssj.py`, `fullpower_ssj.py`, `scene_drain_pause.py`, `bf_hud.py` and
`bf_ki_pool.py` first.

## My report (verbatim)

"Since we have the new HUD, the semi permanent SSJ for Gohan/Goku during the Cell Games has no yellow SSJ ki, just
the base green. Also the constant SSJ sound effect does get annoying, not sure if we can remove that during the Cell
Games for Goku/Gohan until after. SSJ2 can keep the sound effect."

Context: `fullpower_ssj` (r28) keeps Goku and Gohan Super Saiyan from the Time Chamber until Cell is beaten, and
`cellgames_ssj` (r27) puts them in Super Saiyan through the Cell Games. HUD v2b (`bf_hud`, `bf_ki_pool`, r39) shows the
Super Saiyan ki pool in yellow over the EP row.

## Task

1. **Yellow ki.** Find how `bf_ki_pool` decides to draw the yellow pool (which form state, flag or field it reads,
   with addresses) and how the full-power Super Saiyan state differs from a normal transform (which fields it sets or
   skips). Name the root cause. Propose the smallest fix: the full-power state should show the yellow pool exactly as
   a normal Super Saiyan does. Say what the pool should hold while the full-power state skips the drain (full, frozen,
   or as vanilla), with evidence of how the drain and pool interact; if this is a design choice, give options for
   I.
2. **Aura sound loop.** Find the sound that repeats while a character is Super Saiyan (the loop, its trigger, the
   sound id and the call site, with addresses). Design a gate: no loop for Goku and Gohan in plain Super Saiyan while
   the full-power state holds (until Cell is beaten). Super Saiyan 2 keeps the loop. Every other character and every
   other time stays vanilla. Say how the gate tells SSJ from SSJ2 and how it reads the full-power state.
3. Build both as one trial patch module `scripts\permanent\patches\fullpower_hud.py` with tests
   `scripts\permanent\tests\test_fullpower_hud.py`, in the style of the existing modules (header, source checks before
   the first write, a second run raises). Tests decode new code with `scripts\permanent\rom\thumb_dis.py`.
4. New list `scripts\permanent\build_list_trial_fullpower.txt` = the lines of `build_list.txt` plus `fullpower_hud`. Do
   not edit any other list or any existing module. `--list` must still give r39
   `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`.
5. Build `builds\mockups\2026-10-25-fullpower-hud\log2_poc_r39_fullpower.gba` (exclusive create) with a save that
   reaches the full-power state quickly (copy an existing build save, exclusive create, `.sav` next to the ROM); give
   I the slot and the steps: what to look at on the HUD, when the loop should and should not play, and the
   SSJ2 check.
6. Full suite once at the end (today 744 OK, more if other tasks add tests). List the diff runs r39 to the new ROM.
7. Bible rows (tag FPH) as `## Section N` blocks in `scripts\one-time\2026-10-25-fullpower-hud\bible_rows.md`.

Label every claim CONFIRMED, LIKELY or SPECULATIVE and quote the proving line or address. If a claim needs an
emulator run, say so and give my check steps; do not guess.

## Report

`docs\tasks\2026-10-25-fullpower-hud\fullpower-hud-report.md`: SHIPPED and PENDING tables, the two root causes, the fix
with its bytes and decode, any choice of mine, SHA-1s, diff runs, test counts, my play steps.

## Limits

- Never write under `data\`. Never overwrite a ROM, save or state. Python: LF, no em or en dashes, `py -3 -P`.
  Never `cd`, in any shell; absolute paths only. Scripts and outputs go in
  `scripts\one-time\2026-10-25-fullpower-hud\`.
- Do not edit `cellgames_ssj.py`, `fullpower_ssj.py`, `bf_hud.py`, `bf_ki_pool.py` or any other existing module or list.
- Other work is changing `celljr_fight.py` and building `chapter_cards` (their modules, tests and lists), making
  beam mockups in `art\mockups\2026-10-25-beam-struggle\`, and reading the disasm clones. I am editing
  `art\base-audit\` and `scripts\one-time\2026-10-23-base-audit\`. Do not touch them.

