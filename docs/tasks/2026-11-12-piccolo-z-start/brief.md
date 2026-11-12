# Piccolo: Super Namek from the start, with the healing removed

Study and build in one run. Phase 1 of two. Stay inside the scope below.

## What the owner asked for

His words: "His Z transformation will be available at the start! But I want to balance it, remove the
healing." And: "Kami already happens in the game, its what unlocks his Z form, instead we make Z
available from the start and swap the Z unlock with Z+."

Phase 1 is the first half of that: Z from the start, no healing. Phase 2 adds the Z+ form and
repoints the Kami unlock at it. **Phase 2 is NOT yours.** Your job includes finding and documenting
the exact unlock site so phase 2 is cheap, but you do not change what it grants.

## Facts I measured or read myself. Build on these.

Appearance table `rom:0x1D967C`, 20 byte entries, fields per bible B0700.

```
entry  6  flag 0x00  set 103  portrait 90  +4 = 7  +5 = 7  obj 0x030021E0   Piccolo, cape, weighted
entry  7  flag 0x01  set 104  portrait 94  +4 = 6  +5 = 6  obj 0x030021F0   Super Namek
```

- Super Namek is +6 to each of STR, POW and END (bible B0428).
- On r40 the Super Namek tick word (vtable `0x08024ABC` `+4`, `rom:0x24AC0`) still names vanilla
  `0x08017401`. It drains 1 regular EP every 20 frames, **heals HP by max HP x 0x290 >> 16, about
  1 percent, at each step**, and enters state `0x24` at EP 0 when HP is not 0 (bible B0543).
- The Kami fusion ends by setting **flag 132** at `rom:0x3E0D89`, then loads world map 6,99
  (bible B0816). Flag 127 is the earlier post-Android-18 scene end (B0815). Confirm which flag
  actually gates the transform before you touch anything.

## Decisions already made. Follow them.

1. **The heal goes, by taking the Saiyan pool tick.** Bible B1691 parked an open question: which tick
   should Super Namek use? Option A was the Saiyan pool tick, which fits with no address moves and
   whose only drawback was losing the Super Namek HP heal. The owner now WANTS that loss. So take
   option A. Read `docs\tasks\2026-10-30-piccolo-ki\piccolo-ki-report.md` for its measurements.
2. **Z becomes available from the start.** Find what gates the transform today and open it. Do not
   guess the flag: read the gate, quote its address, and say what it tests.
3. **Do not change the stats.** Super Namek stays +6. Phase 2 gives Z+ the +10.
4. **Do not change the portrait.** Entry 7 keeps portrait 94. There is no free dialog portrait id;
   121 is being used by the Vegeta Z+ build running right now.

## Scope, and a hard boundary

A new module `scripts\permanent\patches\piccolo_z_start.py`, its tests, and a TRIAL build.

**Another agent is building `vegeta_zplus.py` at the same time.** To stay clear of it you must NOT:

- append or relocate an appearance table entry
- edit `art\tables\portraits.json`
- edit `scripts\permanent\patches\art_inject.py`
- edit `build_list.txt`, `build_list_core.txt` or any existing build list

Make `scripts\permanent\build_list_trial_piccolo.txt` that includes `build_list_dev.txt` plus your
module. Build to `builds\mockups\2026-11-12-piccolo-z-start\`. The build script seeds a `.sav` beside
the ROM; say in the report which save it seeded from. A trial ROM with no save costs the owner his
file.

If you find that phase 1 genuinely cannot be done without touching one of the files above, STOP and
say so in the report rather than editing it.

## Files to read first

- `docs\tasks\2026-10-30-piccolo-ki\piccolo-ki-report.md` : the tick options and their measurements
- `scripts\permanent\patches\ssj2_form.py` : how a form module is shaped here
- `scripts\permanent\scene\scene_lib.py` : how script records are read and patched
- `docs\tasks\global.md` : the global constraints, which all apply

## Done means

1. The full suite passes, run with a real exit code, never piped into `head` or `tail`.
2. The trial ROM is built, its SHA-1 printed, and a line added to `docs\build-log.md`.
3. Your tests prove: Piccolo can transform with the story flag CLEAR; the tick no longer heals; the
   EP drain still ends the form; old saves still load.
4. **A written answer to the phase 2 question:** exactly which site grants Super Namek today, its
   address, what it tests, and what phase 2 must change there to grant Z+ instead. Label it
   CONFIRMED, LIKELY or SPECULATIVE.
5. Bible rows in a `rows.md` beside this brief, as `## Section N` table blocks.
6. A `report.md` beside this brief.

Report any place where my facts above disagree with the ROM you read. Deviate and flag it rather than
forcing the design onto a table that does not match.

One report message, then stop. Do not add a byte order mark.
