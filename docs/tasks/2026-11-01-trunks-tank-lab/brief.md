# Brief: Trunks tank, side walk, in the sprite lab

Date: 2026-11-01. One Opus agent. Build and capture in one run.

## Goal

Make a trial ROM that shows **base Trunks wearing the tank top** walking sideways, and capture it in the
sprite lab. I need to watch the walk cycle move. Stills have already passed my eye.

## What is already done, do not redo it

`art\trunks_tank\` holds 7 drawn base frames and a `manifest.json`. The manifest was generated from the ROM,
not typed, so every `headers` entry is proved. Read it first.

Two facts in it that matter:

- A PNG can map to **several headers**. Set 128 stores the stand pose and the idle variant (anim 4) as
  separate copies of the same picture. Patch **every** header listed, or the jacket returns in anim 4.
- Dir 3 reuses dir 2's header with the OBJ h-flip bit, so patching dir 2 covers dir 3. Do not patch dir 3.

Frames: front idle, back idle, side idle, and side walk 0-3 (anim 1 dir 2). Base form only. The Super Saiyan
set (134) is **out of scope**.

## Build it

1. New patch module `scripts\permanent\patches\trunks_tank.py`. Follow `patches\gohan_gi.py` for the
   `build_set` / `clone_set` pattern and its header docstring style.
2. New trial list `scripts\permanent\build_list_trial_trunkstank.txt`:
   `include build_list_trial_spritelab.txt` then `trunks_tank`.
3. Build with `log2_build.py --list ... --out ... --log ...` into `builds\`.

**Never build `build_list.txt` or `build_list_dev.txt`.** Report their SHA-1s unchanged as proof you did not.

## The open design question, decide it and say why

The sprite lab shows the **player**, which is set 157 (Gohan). Trunks is set 128. You must decide how to get
set 128 on screen in the lab. Two routes I can see, and there may be better:

- Point the lab player's appearance at set 128.
- Add Trunks as a second actor in the lab.

The ledger (2026-10-31 3:55 AM) records these lab limits, carry them:
the map enter script never fires on a Continue load; save slot 1 has no enemies, slot 2 has eight;
the camera stays still only while walking **down or right**, and tracks past 20 px up or 52 px left.

Walking **left** is what I need to see, and that is exactly the direction the camera tracks. Solve it or say
plainly that it is not solvable in this pass, and capture what you can.

## Capture it

Follow `scripts\one-time\2026-10-31-lab-verify\` for the capture job shape. Capture all four side walk frames
plus the side idle. Save the sheet under `scripts\one-time\2026-11-01-trunks-tank-lab\`.

## Verify, and report honestly

- Full suite once: `py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent`.
  There are 10 known failing tests from r41 with stale SHA pins. Name any failure that is **not** one of those.
- Confirm in the built ROM that every header in the manifest now holds the new pixels. Read the bytes back.
- State what you verified yourself and what you assumed.

## Rules

Absolute paths only, never `cd`. Python is `py -3.14 -P`. Never write under `data\`. Never overwrite a ROM
or save. Pair every built ROM with a `.sav`, which `log2_build.py` does for you.
Read `docs\sprite-guide.md` before you touch any pixel. Do not redraw my art.
No em dashes or en dashes anywhere.

One report message, then stop. Do not add a byte order mark.
