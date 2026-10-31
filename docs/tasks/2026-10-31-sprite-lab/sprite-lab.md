# Sprite lab: our own debugger for looking at frames (me, 2026-10-30 11:15-11:20 PM)

Read `docs\playbooks\capture-playbook.md` and
`scripts\permanent\emu\capture.py` (the capture loop, finished tonight), `scripts\permanent\scene\scene_lib.py` (named ext
ops, finished tonight), `scripts\permanent\patches\chapter_cards.py` **only for its BG palette writer**, and
`scripts\permanent\rom\log2_save.py`. Search `docs\RE-BIBLE.md` (tags CHF2, PSL, SSM, CAP) before you read the ROM.

## My words

"gingertown has a very white section of road not far to the left of the spawn point, you can perform actions and
capture frames. Can create a build and save just for testing this. Or a custom rom with a totally white background,
our own debugger." Then: "No enemies either and no action restriction."

## Why

We judge sprites from static PNGs decoded out of the ROM. That misses animation timing, the real palette, OBJ
layering and motion. This gives us the sprite in motion on a flat field, captured unattended.

## Task

1. **Trial module `scripts\permanent\patches\sprite_lab.py`**, on r40, with its own
   `scripts\permanent\build_list_trial_spritelab.txt` (a new file: `include build_list.txt` then `sprite_lab`).
   **Do not touch `build_list.txt` or any existing list.**
2. **Flat background.** Turn the BG layers off and set the backdrop, BG palette entry 0, to a chosen colour. The
   mechanism is proven in our own code: `chapter_cards` v7 writes the BG palette directly every frame.
   **Make the colour a module constant, not white only.** The gi carries white swoosh, light greys and highlights, so
   white hides exactly what we need to see. Provide at least lime, magenta, white and black, default lime, and say in
   the header how to change it.
3. **No enemies.** Pick a map that spawns none, or empty the spawn list for the lab map in the trial module only.
   Report which map you chose and how you proved it spawns nothing.
4. **No action restriction.** Every form must be reachable and must not end on its own:
   - Super Saiyan 2 is gated on `flag:195`. Set it in the lab save.
   - Forms drain ki, so a long capture would drop out of the form part way and quietly spoil the sheet. Set stats and
     ki in the save so no form can time out during a capture. Prefer fixing this in the save. Only if that is not
     enough, disable the drain on the lab map in the trial module, and say so.
5. **HUD off and a fixed camera**, so the bar is not in every frame and the background does not slide under the
   sprite between frames. `ext 86` and `ext 31`, the same ops the card 4 and Cell Jr scenes already use.
6. **A lab save**, through `log2_save.py`, placing the player on the lab map with the flags and stats above.
   Also add a preset row for the Ginger Town road I named, as a real-scenery comparison. Find it from the map
   data and report its zone, area, x and y. Never overwrite an existing save: check absence, then create.
7. **One capture job** under `scripts\one-time\2026-10-31-sprite-lab\` that walks Gohan through each direction and a
   few actions, and a contact sheet of the captured frames. **This is the gate: the sheet must show the sprite on the
   flat colour with no HUD and no background movement.**
8. **Tests** in `scripts\permanent\tests\test_sprite_lab.py`: the module's byte sites, the backdrop colour constant,
   the empty spawn list, and that main `build_list.txt` still rebuilds to `14d6b831`.

## Report

Short. `docs\tasks\2026-10-31-sprite-lab\sprite-lab-report.md`: SHIPPED and PENDING tables, the trial SHA-1, the map
you chose and the proof it spawns nothing, how you stopped the form draining, the contact sheet path, the test count.
Label every claim C, L or S. Bible rows (tag LAB) in `scripts\one-time\2026-10-31-sprite-lab\bible_rows.md` as
`## Section N` table blocks.

## Limits

- New files only, plus `log2_save.py`. **Do not touch `chapter_cards.py`, `test_chapter_cards.py` (another task
  holds them now), `celljr_fight.py`, any existing build list, `docs\RE-BIBLE.md`, `docs\ledger\`, `zhack\` or
  `data\`.**
- Never overwrite a ROM, save or state: check absence, then create. Python: `py -3.14 -P`.
- Never `cd`, `Set-Location` or `Push-Location`. Use absolute paths in every command and in every script that opens a
  file. Five tasks in a row have broken this. Do not be the sixth.
- Run `test_sprite_lab.py` only. Do not run the full suite.

