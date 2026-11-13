# The Z transform leaves the ki meter short of empty, and the orange bar pops in late

Study and build in one run. Two owner reports, one play-test, one pass.

## What the owner saw

1. "When you use the Z transformation, the yellow meter that charges the Z is supposed to go empty,
   but it stops shortly before." He believes this bug is old, not new to the red bar work.
2. "I am trying to remember if in Buu's Fury the yellow/orange meter fills while transforming. If
   interrupted, it goes away, if not, it starts full. Right now the yellow/orange bar just appears
   after the transformation appears."

Report 1 is a defect. Report 2 is a question first: answer it from the Buu's Fury ROM before you
change anything.

## Facts I read myself. Build on these.

`scripts\permanent\patches\bf_ki_pool.py`, RAM `0x03003A00`: `+0` u16 pool, `+2` u16 tag, `+8` u32
drain accumulator, `+0xC` u8 HUD fill cache, `+0xD` u8 swap guard, `+0xE` u8 bar colour.

In the `hud_key` block the fill is `pool x 0x31 / max EP`, clamped to `0x31` (49). The draw loop
`hud_step` then runs `r7` from 0 up to that fill, one `EP_TABLE` row per step. **`EP_TABLE` is built
by a `for j in range(41)` loop.** 49 is larger than 41. Say in the report what rows 41 to 48 read,
and whether a full pool can reach them. That may be a second defect; prove it before you call it one.

Integer division means the fill reaches 0 only when `pool x 49 < max EP`. Check whether the bar can
show 0 at all, and whether the pool itself reaches 0, before you decide which layer is short.

## What to decide, and how

**Separate the two layers.** The pool value and the drawn bar are not the same thing. Say which one
stops short. Quote the address and the op.

- `data\roms` holds the Buu's Fury ROM. Read its own transform state machine for report 2, not only
  its HUD draw. Buu's Fury HUD images: `BF_HP=0x08071CB0`, `BF_KI=0x08071F40`, `BF_EXP=0x080721D0`,
  `BF_CD=0x08072410`.
- Open each handler. Never name a RAM word or an op from a label.

## Scope

Fix report 1 in `scripts\permanent\patches\bf_ki_pool.py` and its tests. For report 2, decide and say
whether the fill-during-transform is cheap here; build it only if it is, and only inside this module.

- Do NOT touch `build_list.txt` or `build_list_core.txt`. Use an existing trial list, or make
  `scripts\permanent\build_list_trial_kimeter.txt` that includes `build_list_dev.txt` plus what you need.
- Do NOT touch anything under `art\`. I am editing sprite frames there in the same tree.
- `bf_ki_pool.py`, `fullpower_hud.py`, `test_bf_hud.py` and `test_bf_ki_pool.py` already carry
  uncommitted red-bar work. Build on it. Do not revert it.
- About 17 golden pins already fail from that red-bar work. Leave them alone. Say which of your own
  failures are new.
- Build the trial ROM to `builds\mockups\2026-11-12-ki-meter\`. Say which `.sav` the build seeded from.

## Files to read first

- `scripts\permanent\patches\bf_ki_pool.py` : the module, its header block holds the measured map
- `scripts\permanent\patches\fullpower_hud.py` : the HUD key pin and the overlay route
- `docs\RE-BIBLE.md` : search it for `pool`, `EP` and `HUD` BEFORE you read the ROM
- `docs\tasks\global.md` : the global constraints, which all apply

## Done means

1. The full suite runs with a real exit code. Never pipe it into `head` or `tail`.
2. The trial ROM is built, its SHA-1 printed, and a line added to `docs\build-log.md`.
3. A written answer to report 1: which layer stops short, the address, and the one line fix.
4. A written answer to report 2: what Buu's Fury does during the transform, CONFIRMED, LIKELY or
   SPECULATIVE, and what it would cost us.
5. Bible rows in `rows.md` beside this brief, as `## Section N` table blocks.
6. A `report.md` beside this brief.

Report any place where my facts above disagree with the code you read. Deviate and flag it.

One report message, then stop. Do not add a byte order mark.
