# Vegeta Z+ : a second Super Saiyan grade on top of Z

Study and build in one run. The design is decided. Do not re-open it.

## What the owner asked for

Vegeta gains a second transformation, reached FROM Super Saiyan, not instead of it. It uses the
ascended grade stats the game already carries, his new hand drawn portrait, and a `Z+` HUD icon.
Trunks gets the same later; his portrait does not exist yet, so he is OUT of scope.

## Facts I measured myself. Build on these, do not re-derive them.

Vanilla appearance table `rom:0x1D967C`, 20 byte entries, fields per bible B0700: `+0` form flag,
`+1` set id, `+2` dialog portrait, `+4` transform target, `+5` revert target, `+16` form object.

```
entry  8  flag 0x00  set 137  portrait 106  +4 = 11  +5 = 11  obj 0x030021E0   base Vegeta, post-Cell
entry  9  flag 0x00  set 138  portrait 106  +4 = 10  +5 = 10  obj 0x030021E0   base Vegeta, pre-Cell
entry 10  flag 0x01  set 139  portrait 107  +4 =  9  +5 =  9  obj 0x030021E8   ascended grade
entry 11  flag 0x01  set 140  portrait 107  +4 =  8  +5 =  8  obj 0x030021EC   regular Super Saiyan
```

- On a SUPER entry `+4` points back to base, so nothing chains today. Entry 5 (Gohan) is the one
  exception, and only because `ssj2_form` set it.
- `set:139` and `set:140` decode to the same tiles in all 64 rows (bible B0221). The two grades are
  visually identical in vanilla. That is expected and is not yours to fix.
- Form object `0x030021E8` is Super Vegeta / Super Trunks: **+15 STR, +10 POW, +15 END**, speed
  0.75 / 1.75, 1 EP per 40 frames (bible B0427).
- Portrait id **121 is the only free dialog id**. `npc_gi` grew the block to 0-121; 116, 118 and 120
  are status twins and 115, 117 and 119 are Gohan's. Confirmed against `art\tables\portraits.json`.

## Decisions already made. Follow them.

1. **Add a NEW appearance entry. Do not reuse entry 10.** Entry 9 transforms into 10 and 10 reverts
   to 9, so repointing 10's revert would break the pre-Cell chain. `ssj2_form.py` already relocates
   the table and appends entry 22; append the next free entry the same way.
2. **The new entry's fields:** flag `0x01`; set id `139`; portrait `121`; `+4` = its own index (it
   does not transform further); `+5` = `8`, so leaving Z+ returns to post-Cell base Vegeta; `+16` =
   the ascended form object, so the +15/+10/+15 stats come for free.
3. **Chain it:** entry 11 `+4` changes from `8` to the new entry. Leave entry 11 `+5` at `8`.
4. **No gate in this trial.** Z+ is available whenever Z is. The owner decides the unlock separately.
   Say so in the report; do not invent a flag.
5. **The icon reads `Z+`.** Follow the `ssj2_form` Z2 icon pair exactly: a usable and a dim image, the
   same raw 32x16 8bpp shape. Draw it from existing OBJ palette indices only.
6. **The portrait** is `art\portraits\remastered\pending_vegeta_grade2.png`. It is 64x64, 30 colours,
   zero strays, already verified by me. Wire it as id 121 through the normal
   `art\tables\portraits.json` route. Rename the file to `121_vegeta_grade2.png` in the same pass.

## Scope

A new module `scripts\permanent\patches\vegeta_zplus.py`, its tests, and a TRIAL build only.

- Do NOT touch `build_list.txt` or `build_list_core.txt`. Make
  `scripts\permanent\build_list_trial_vegeta_zplus.txt` that includes `build_list_dev.txt` plus your
  module.
- `art_inject` is in `build_list_core.txt`. Adding portrait 121 moves both masters' SHA-1s. That is
  why this is a trial. If `test_golden.py` fails on its pins because of your change, say so in the
  report and leave the pins alone.
- Build the trial ROM to `builds\mockups\2026-11-12-vegeta-zplus\`. The build script seeds a `.sav`
  beside it; confirm in the report which save it seeded from. A trial ROM with no save costs the
  owner his file.

## Files to read first. You should not need others.

- `scripts\permanent\patches\ssj2_form.py` : the precedent for every part of this
- `scripts\permanent\patches\art_inject.py` : how a portrait id is wired
- `scripts\permanent\art\art_tables.py` : `valid_id`, `MAX_ID`, `check_pixels`
- `scripts\permanent\tests\test_ssj2.py` : the test shape to copy
- `docs\tasks\global.md` : the global constraints, which all apply

## Done means

1. The full suite passes: `py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t
   <LOG>\scripts\permanent`, run with a real exit code and never piped into `head` or `tail`.
2. The trial ROM is built, its SHA-1 printed, and a line added to `docs\build-log.md`.
3. Your own tests prove, at minimum: entry 11 transforms to the new entry; the new entry reverts to
   8; the new entry carries the ascended form object; portrait 121 decodes to the owner's pixels.
4. Bible rows for anything you learn, as `## Section N` table blocks in a `rows.md` beside this brief.
5. A `report.md` beside this brief. Label every RE claim CONFIRMED, LIKELY or SPECULATIVE.

Report any place where my four measured entries above disagree with the ROM you read. Deviate and
flag it rather than forcing the design onto a table that does not match.

One report message, then stop. Do not add a byte order mark.
