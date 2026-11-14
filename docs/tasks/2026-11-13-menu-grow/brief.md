# Brief: grow the scouter database menu, and price the journal menu

Two halves. The first is approved and buildable. The second is a study that ends in a recommendation.

## Read first, in this order

1. `docs\tasks\2026-11-13-journal-menu\census.md`. The measurements. It corrects the design below.
2. `docs\design\2026-11-09-scouter-menu-grow.md`. The approved design, now carrying my correction.
3. `docs\design\2026-11-09-journal-and-world-map-star.md`, section 1 only.
4. Bible rows B2444 to B2451, B2268 to B2271. Find them with
   `py -3.14 -P scripts\permanent\rom\whatis.py B2444`.

---

# HALF 1: the scouter menu. Build this.

## What the owner gets

Entries 128 `Future 17`, 129 `Future 18` and 130 `Future Cell` already exist and already scan in
battle. They do NOT appear in the scouter database list, because the list menu object is sized for
exactly 128 and `scouter_future` deliberately left its bound alone. After this, they appear.

## The object

`sub_08019204` allocates `0x6B0` bytes. List 1 holds 4 bytes per scanned entry from `+0x80` and ends
exactly on `+0x280`, which is list 2's own count word. List 2 holds 8 bytes per distinct name from
`+0x284` and ends at `+0x684`, inside the live block at `+0x680`. Neither list has one spare byte.

## The edits, from the corrected design

- `0x6B0` object size becomes `0x6E0`, at `rom:0x1920A`
- list 2's base `0x280` becomes `0x290`, at `rom:0x193AE` and `rom:0x19848`
- the live block `0x680` becomes `0x6B0`, at **FIVE** sites: `rom:0x192A8`, **`rom:0x192DE`**,
  `rom:0x1966E`, `rom:0x19726`, `rom:0x19866`
- the list bound at `rom:0x19260` goes from `0x80` to `0x83`

**`rom:0x192DE` is the site the original design missed.** It is in `sub_080192D6`, which the first
census never named. Moving four and leaving the fifth is the silent overrun this work exists to
prevent. Verify all five yourself before you write any of them.

Every replacement keeps its instruction LENGTH. These sit inside vanilla functions that are not
relocated.

## Before you write anything

The design's own warning, which the census proved true twice: **a `mov ; lsl` scan finds only its
own shape.** Re-run all four shapes yourself over the scouter family:

- `scripts\one-time\2026-11-13-journal-menu\imagewide.py`, image wide `mov ; lsl`
- `scripts\one-time\2026-11-13-journal-menu\poolrefs.py`, image wide pc relative loads
- an aligned word scan for each value
- read every `add rX,#imm` in the family by eye, since no image wide shape covers add chains

Report what each shape returns. If a shape finds a site this brief does not name, STOP and report it.

## Where it goes

Extend `scripts\permanent\patches\scouter_future.py`. It already owns the table move and the one
bound byte, and it already ships only in trial lists, so neither master moves. Do NOT make a new
module and do NOT touch any build list.

## The test the design asks for

> A test must prove the new bases and the new size agree with each other arithmetically, not merely
> that the ROM assembled.

Write that test. `0x80 + 4 * 131` must be at or below the new list 2 count word. `0x284 + 8 * 131`
must be at or below the new live block. The new block plus its own length must be at or below the
new object size. Derive each number, never type it twice.

---

# HALF 2: the journal menu. Study only. Do NOT edit it.

The owner has not chosen between growing the object and replacing a vanilla quest, and the census
changed the price he was quoted. Your job is to give him the real number.

## What the census already settled, so you do not redo it

- The grow is EIGHT same length edits, listed in census.md section 3, not the six the design said.
- `+0x400` is a third tail field the design never saw, at `rom:0x4B86`.
- `rom:0x4DA0` is NOT a field reader. It allocates a separate 0x40C byte object.
- The eleven other `0x40C` readers are in `List_RemoveValue` and friends. 57 callers exist and none
  is in the journal menu range, so the journal never calls it. The grow option stands.

## What is left to answer

1. **Run the same four shapes over the journal family** and confirm the eight sites. The `0x154`
   count is a floor, because add chains have no image wide shape. Say what you find, with its shape.
2. **What is the 44th quest?** The design quotes the owner: "Take the time machine back to the
   future, or something of that sort". All 43 vanilla entries are real, so nothing is free to take.
3. **Recommend one option** and say what it costs if you are wrong.

Write the result to `docs\tasks\2026-11-13-menu-grow\journal-price.md`.

---

## Rules for both halves

- Python is `py -3.14 -P`. Absolute paths. Never `cd`.
- Never write under `data\`. Write NO ROM, no save and no state. Build in memory only.
- Do not commit. Do not touch `build_list.txt`, `build_list_dev.txt` or `build_list_core.txt`.
- Both master SHA-1s must not move: golden `778ccff59eddf7d34f432ece7e9a929595b2425f`,
  dev `49cdfd3c172d734956d74ecb6c6419d1a301da6e`. Build both in memory and prove it.
- Run the full suite ONCE at the end. The baseline is
  `docs\tasks\2026-11-13-xfm9\baseline-failures.md`, plus whatever I tell you has landed since.
  Name any failure not on it.
- Never interpret a RAM word, an op or a symptom from a label. Open the handler.
- Write in ASD-STE100. No em dashes, no en dashes.

One report message, then stop. Do not add a byte order mark.

---

## UPDATE, late on 2026-11-13. Read this before you start.

Four things changed after this brief was written. None of them changes your job.

1. **The build lists MOVED.** They are in `scripts\permanent\build-lists\` now, not
   `scripts\permanent\`. Reach them through `log_paths.BUILD_LISTS` and never a literal path.
2. **The suite baseline is different.** It is now **2152 tests with 4 failures and 0 errors**. All
   four are in `test_bf_hud.py` and another agent owns them. Any OTHER failure is yours. Do not use
   `docs\tasks\2026-11-13-xfm9\baseline-failures.md`: it is the old 21 row list and it is stale.
3. **A new trial list exists**, `build_list_trial_rough.txt`. It is the dev master plus the whole
   future Trunks line and the whole Piccolo and Vegeta Z+ line, and it carries `scouter_future`.
   **Build it as well as the fx trials when you check your work**, because it is the ROM the owner
   plays. Its SHA-1 before your change is `abdc640f947a06e3e3c49d03099ac4578c6accaf`.
4. **XFM-9 landed.** `piccolo_z_start` no longer splices `pool_ref`, and `piccolo_zplus` now carries
   a four byte splice and a `pool_gate` leaf. Neither touches the scouter or the journal, but the
   bible rows B2458 to B2468 describe the new shape if you meet it.

### One more thing I measured myself, which the half 2 notes already carry

I decoded every `bl` in the image whose target is `List_RemoveValue` at `0x080068CA`. There are 57
callers and not one is inside the journal menu range. That is why the grow option stands. If your own
work finds a caller I missed, say so loudly: it would remove the grow option entirely.
