# Piccolo Z+: its own icon and its own portrait id

The owner played `log2_piccolo_zplus_v1.gba` and found both gaps:

> "PIccolo is missing the Z+ icon (it just shows Z) and the new portrait for his z+ form."

Both were named as deviations in the power-up effects report. Close them.

## 1. The Z+ icon on ability 11

`vegeta_zplus.py` already does this for ability 12. Copy the mechanism, do not invent one.

- Art: `art\hud_zplus_usable.bin` and `art\hud_zplus_dim.bin`, the same pair Vegeta uses.
- `vegeta_zplus` pastes the Z+ picture into the **live** ability icon, so the icon keeps whatever HUD
  look the build has. `bf_look` refuses if `bf_hud`'s icon layout `(3, 2, 18, 9)` ever moves. Keep
  that guard.
- Its HUD hook shows the Z+ pair for ability 12 in entry 23, and in entry 11 while B steps up, and
  otherwise tail-calls `ssj2_form`'s hook. **Piccolo needs the same for ability 11**, in the Z+ entry
  and in the Super Namek entry while B steps up.
- The gate and the HUD must share one test, as Vegeta's share `zplus_ok`, so the icon can never
  disagree with what the button does.

## 2. Its own dialog portrait id

Today Piccolo Z+ reuses Super Namek's ids 94 and 18. Give it its own id, the way `vegeta_zplus`
gives Vegeta id 122.

- The block grows by one word for the new id. `npc_gi.py` proves the move: the block cannot grow in
  place, so it relocates, and `rom:0xBE10` plus the hook's pool word follow it. `vegeta_zplus`
  already grew it once to 122, so read **its** notes for the live block rather than the old numbers.
- **The owner draws every portrait. Do NOT draw one, and do not generate a candidate.** Wire the new
  id to a copy of Super Namek's existing portrait art as the placeholder, so his PNG is a drop-in
  later, exactly as `art\tables\portraits\122_vegeta_grade2.png` drops in for Vegeta.
- Say in the report which id you took and the exact PNG path and filename his art must use.

## 3. The kit so he can draw it

Use `portrait_export.py` and `portrait_blanks.py` (see `docs\tool-index.md`). Give him, in
`art\kits\2026-11-13-piccolo-zplus-portrait\`: the frame and background layers to sandwich his art
between, Super Namek's own portrait as the reference to draw against, and the palette swatch of the
colours a status page portrait may use. Nothing else.

## 4. The ki bar ramps up during the transformation

The owner, 2026-11-13: "also the yellow/orange bar ramp is not done either."

The full spec is already written at `docs\tasks\2026-11-12-ki-rampup\brief.md`. Read it. In short,
in his own words: the **yellow bar ramps up over the green bar** until full, whatever the green bar
holds, full, empty or half full. **If the transformation is interrupted the yellow bar disappears.**
The **orange bar does the same over the yellow** on the second transformation.

It is a draw, not a value: the ki pool still arrives in one store on the landing frame, so nothing
about gameplay changes. Four of the pieces already exist in `bf_ki_pool`: the per frame hook during
the transform (`tick_xform`, state 35 vtable `0x08025D9C +0x04`), the overlay fill cache at RAM
`0x03003A00 +0xC`, the bar colour byte at `+0xE`, and both bar images.

Two things in that brief are NOT measured and must not be assumed: how many steps Buu's Fury ramps
over and across how many frames, and whether it clears the overlay on interrupt or lets it fall
back. An earlier study found a 7 entry gradation table in the draw, but **a table is not a
schedule**. Read the Buu's Fury transform tick.

Note `powerup_fx.py` now also hooks state 35's tick and chains `tick_xform` first. Do not break that
chain, and do not fight it for the same frames.

## Deliver

Rebuild both trial ROMs, `build_list_trial_vegeta_fx.txt` and `build_list_trial_piccolo_fx.txt`, so
he has one pair to play. Report both paths and SHA-1s.

## Rules

- Search `docs\RE-BIBLE.md` first. B2410-B2423 are last night's rows for this work. Read the handler
  before you trust a label; `GitHub\legacyofgoku2-disasm\build\code` is the byte exact tree.
- Never write under `data\`. Absolute paths only. Never `cd`.
- Trial lists only. Do not touch `build_list.txt`, `build_list_dev.txt` or `build_list_core.txt`.
- Run the full suite ONCE at the end, to completion, never piped into `tail`. Compare the failure
  ids against `scratch\2026-11-12-ship\fails_base.txt`, which holds the 34 id baseline. Any id not
  in that file is yours.
- One report message, then stop. Do not add a byte order mark.
