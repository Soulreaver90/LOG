# Brief: the Trunks tank run (anim 13), plus the confirmed armour-review cleanups

Work on the Trunks tank outfit stopped at the running animation. You build it, and you apply the
cleanups the armour review already proved.

**You touch only `art\trunks_tank\**` and `scripts\one-time\2026-11-08-trunks-tank-run\`.** Two
other agents are building the ROM right now. Do not edit any module, any build list, any test, or
anything under `scripts\permanent\patches\`. **Do not run the test suite.** Do not build a ROM.

## Read first, in this order

1. `docs\sprite-guide.md` - **read this before any sprite work.** It holds the drawing rules, the
   outfit swap method, and the process rules that exist to stop you spending the owner's eye on
   catchable mistakes.
2. `art\trunks_tank\edit-kit\armour-review.md` - the 540-line review of the current frames against
   the Saiyan armour sets. Findings A to H. Section 0 says how far the armour can be trusted, and it
   names a trap the review itself fell into twice. Read section 0 before you use any finding.
3. `docs\tasks\global.md` - the standing constraints.

## The owner's three new rulings, which change the job

These came after the review was written. They override it where they disagree.

1. **No scabbard.** His words: "Im wondering if trunks tanks hould even have the scabbard, it adds
   complications and his armor sprite doesnte ven wear it, it only comes out for special attacks."
   So the tank wears no scabbard. The sword appears only for special attacks.
2. **The armour sets are the reference for anything the jacket hides.** His words: "yeah we dont
   have to guess the jaw line, etc. Whatever is obscured by the jacket, review the armor version and
   align it accordingly." Sets 129 and 130 are armoured Trunks. Use them, inside the limits section
   0 of the review sets out.
3. **The Super Saiyan hair was never a guess.** His words: "I also realized we didnt have to guess
   the super saiyna hair at all, the trunks sprite with the armor exposes the super saiyan hair from
   the back." Finding A is about that back head. Use set 130's own back hair.

## What to build

### 1. The run, anim 13

Base and Super Saiyan, every view the source set carries. `art\trunks_tank\edit-kit\run_anim13.png`
already exists from the earlier pass: start by looking at it and saying what state it is in.

Build the run with **no scabbard**, and use the armour sets for anything the jacket hides.

### 2. The cleanups the review already proved

Apply only findings the review labels CONFIRMED or MEASURED. In particular:

- The **44 scabbard reveal pixels** across 14 frames (Finding C's first table). With the scabbard
  gone these are pure waste. The review gives the exact coordinates.
- The **18 leftover jacket pixels** in the side frames (the new finding at the end of Finding C).
- Findings A, D, E, F, G and H, each to the extent the review states a confirmed fix.

Leave anything the review calls LIKELY or SPECULATIVE. Say what you left and why.

### 3. What you must NOT touch

**Do not touch the cyan baldric, palette `47` and `4D`.** That is 110 pixels across 32 frames and
the owner has not answered it yet. Sets 129 and 130 wear no strap, so the armour cannot decide it.
Leave every baldric pixel exactly as it is. If his answer arrives mid-task you will be told.

## Process rules that exist for a reason

- **Sprite fixes are made by eye, frame by frame.** Never run a rule pass over art. Ask when unsure.
- Hand fixes go in `art\trunks_tank\hand-fixes\` as dated scripts, the way the three already there
  are written.
- **Run `sprite_guard.py` with `--body-from` before the owner sees anything**, per the sprite guide's
  outfit-swap rule. Quote its output.
- The shared OBJ palette is not changed. New art uses existing palette indices only.
- **Never copy other modders' art.** The Z Hack is clean-room inspiration only: nothing from
  `zhack\` goes into `art\`, a module, or a build. Buu's Fury art is official and may be ported.

## Review sheets

The owner decides by eye, so build him sheets he can judge without reading code:

- The run, every frame, base and Super Saiyan, at 1x and at 12x.
- Each frame you changed, next to what it was and next to the vanilla frame at the same key.
- **Render head to foot and look at the whole frame before you measure anything.** A past pass
  measured a detail and missed a broken eye in plain sight.

## Rules that bite here

- Absolute paths only. Never `cd`, `Set-Location` or `Push-Location`.
- Python is `py -3.14 -P`.
- No em or en dashes in any file you write. No byte order mark.
- Never write under `data\`. Never overwrite a ROM, save or state: check absence, then create.
- Label every claim CONFIRMED (coordinates and counts), LIKELY or SPECULATIVE.

## Deliverables

- The run frames and the cleaned frames, in `art\trunks_tank\`.
- `docs\tasks\2026-11-08-trunks-tank-run\report.md` - what you built, what you cleaned with counts
  and coordinates, what you left and why, the `sprite_guard` output, and every sheet's path.
- `docs\tasks\2026-11-08-trunks-tank-run\rows.md` - bible rows, `## Section N` table blocks, tag
  `TKR`. The review's section 11 already drafted candidate rows: reuse them where they still hold.

One report message, then stop. Do not add a byte order mark.
