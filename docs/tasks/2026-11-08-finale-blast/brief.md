# Brief: the finale blast and Cell's death (rung 7)

You build the last beat of the future Trunks finale: Trunks fires a gold beam upward, Cell takes
three hits with explosions and screen rumble, then explodes.

Another agent owns the dialogue, the music picks and the transition cut. Do not touch their work.

## Read first, in this order

1. `docs\tasks\global.md` - the standing constraints. They all apply.
2. `docs\design\2026-11-08-finale-dialogue.md` - **your spec.** Section 5 and the two sections at
   the end, "The blast, settled" and "Build state". His words are quoted exactly; build them
   verbatim and never re-word them.
3. `docs\tasks\2026-11-08-finale-beam\rows.md` - 21 CONFIRMED rows measured for you already, with
   addresses. **Read these before you disassemble anything.** They answer most of what you need.
4. `scripts\permanent\patches\chapter_cards.py` - **your model for the new ext op.** It already
   solves the hard part: see the header notes about copying the LIVE 145-word ext table at
   `0x083B5D28` into a 146-word copy whose last word is the new op.

## What is already measured, so you do not redo it

All CONFIRMED, with evidence in the rows file:

- The beam object `@0x080143A8` picks its colour from **argument 6**: 0 is blue, non-zero is the
  gold set the owner chose. Both sets are byte identical in geometry.
- `ext 137`'s builder `sub_0801D84C` hardcodes that argument to 0 at `rom:0x1D870` (`mov r2,#0x0`).
  **You may not flip that byte globally**: `ext 137` has exactly two vanilla sites and one is
  Gohan's Cell Games Kamehameha, which must stay blue.
- The beam fires along **the actor's own facing**, read at `actor+0x10` by the tick `@0x0801D7DC`.
- **Direction 1 is UP**, proved from record geometry. So `face(trunks, 1)` before the beam op.
- `ext 137` forces the shooter into state 30, which is anim 18. **Both vanilla sites override it on
  the very next op** with `pose(set, state)`. Do the same.
- Set 130 anim 4 has 4 frames a direction. Set 28 has anim 18 (7 frames) and anim 2 (4 frames).

## Build it

### 1. The gold beam op

Add a new ext op that is `ext 137` with the colour argument set to 1. Follow `chapter_cards.py`'s
ext-table pattern. You will need copies in expansion of `sub_0801D84C` (0x3E bytes, with that one
byte set to `0x01`), of `sub_0801D788` (0x54 bytes, with its `bl` retargeted), of the `ext 137`
command vtable `0x0802521C`, and of the `ext 137` handler `@0x0800A3A2`.

**The vtable copy trap.** A command vtable stores offsets RELATIVE to its own address, with the
Thumb bit, not absolute pointers. A verbatim copy breaks every slot. Rebase each one:
`new_value = old_value + 0x0802521C - new_vtable_address`. Verify by resolving your copy's slots 1,
2 and 3 and checking they land on your copied start, the vanilla tick and the vanilla done.

Find the ext dispatch bound check and raise it, the same way `scouter_future.py` raises its
`cmp r0,#0x80`. **Check first whether `chapter_cards` is in this build list and already relocated
the table.** If it is, copy the LIVE table, not the base one, and say so in your report. Two
relocations must not collide.

### 2. The scene

Build the spec's section 5. Vanilla's own Perfect Cell death is your shape; it is decoded in the
spec. **Three hit loops, then the fifth explosion block**, per his ruling.

Staging: Cell ABOVE, Trunks BELOW, a vertical pair. Place them on his map 142 yourself and prove
both spots walkable and clear of the BG1 art that draws over the player. The spec's "Build state"
section has the current map numbers. Vanilla's own death record ends `music(37)`, which is worth
weighing against his line "back to the credits music that normally plays".

### 3. One thing to flag, not to decide alone

Anim 4 is a **cycling** idle of 4 frames, and his two picked frames are indices 2 and 3, the top of
the raise. Firing while it cycles will move his arms up and down during the beam. He said: "yeah
its the idle arms up and down but we can repurpose it to make it look like he is shooting up."

Measure what it actually looks like. If a frame hold is needed, the clean way is a one-frame clone
through `log2_sprites.build_set` with `counts=`. **Do not pick for him by taste.** Build the version
you can defend, then say in your report what you did, what the alternative looks like, and what you
recommend. He decides by eye.

The firing frame is `frame_36AD44`, header `0x36AD44`, set 130 anim 4 dir 1 index 2. **Refer to it
by filename and header address, never by index alone.**

## Traps

- **His map is already copied in and audited.** `art\plateau\map_142.json` is his live file. Do not
  copy it again and do not edit it.
- Your module is NEW. Add it to `scripts\permanent\build_list_trial_plateau.txt` and say where in
  the order it must run and why. Do not touch `build_list.txt` or `build_list_dev.txt`.
- Build to a SCRATCH name under `builds\mockups\future\`. **Do NOT name anything `future_v3`.**
- `test_battle_start.test_form_survives_the_leader_change` is ALREADY red and predates your work.
  Any OTHER failure is yours.
- Run the full suite ONCE, at the end. **Never pipe a test run into `head` or `tail`**: the pipe
  reports the pipe's exit code and a red suite reads as green. Redirect to a file.
- Verify every claim out of the BUILT ROM, not out of your plan. Decode each record you wrote and
  quote the ops.

## Rules that bite here

- Absolute paths only. Never `cd`, `Set-Location` or `Push-Location`.
- Python is `py -3.14 -P`.
- No em or en dashes in any file you write. No byte order mark.
- Never write under `data\`. Never overwrite a ROM, save or state: check absence, then create.
- The shared OBJ palette at `rom:0x1DA6C8` is not changed. The gold beam needs no new art.
- Label every claim CONFIRMED (address plus bytes or disassembly), LIKELY or SPECULATIVE. Build only
  on CONFIRMED.

## Deliverables

- The new module, the build list line, and the tests for both.
- `docs\tasks\2026-11-08-finale-blast\report.md` - what you built, the rebased vtable slots with
  their resolved addresses, the staging spots with their walkability proof, the frame-hold finding
  and your recommendation, and anything you could not do.
- `docs\tasks\2026-11-08-finale-blast\rows.md` - new bible rows, `## Section N` table blocks, tag
  `FBL`.

One report message, then stop. Do not add a byte order mark.

---

# Addendum, added by the controller after the dialogue agent landed

Read this with the brief above. Where they disagree, this wins.

## The tree moved under you. Start from what is there now.

The dialogue agent has finished and its work is SHIPPED in the tree. It changed
`patches\ending_fight.py`, `patches\plateau.py`, `tests\test_ending_fight.py` and
`tests\test_plateau.py`. The owner's dialogue, his music picks and the transition cut are all in.
Read those files as they are now. Do not undo any of it.

Its trial ROM is `builds\mockups\future\finale_dialogue_wip4.gba`, SHA-1
`d6c15081475a0c6c9f30943dd2dcf1cd61017674`. I rebuilt it from the same list and got the same SHA-1,
and I ran the full suite myself: **1856 tests, 1 failure**, the known
`test_battle_start.test_form_survives_the_leader_change`, which predates all of this.

## A collision to check FIRST

The dialogue agent also edited ONE file outside its own set:
`scripts\permanent\tests\test_battle_start.py`. It changed a single pin, the rule 5 census, from 16
to 17, with a comment naming the cause. **That file is shared with you.** Read its current state
before you touch it, and say in your report whether your work moves that census again.

## Corrections to the spec you must carry

The death record is FIVE blocks, not four. The design doc is already corrected, but an earlier
version said four, so trust the doc's current "The death loop, measured from vanilla" section. Build
THREE hit loops plus the fifth explosion block.

## Two things that make your job easier

1. **`scripts\permanent\art\` was invisible to the tool index until today.** It holds 12 tools,
   including `frame_lock.py` and `palette_export.py`. Re-read `docs\tool-index.md`: it now has a
   `scripts\permanent\art\` section. Search it before you write anything, especially for the frame
   hold question.
2. **The ext table pattern is proven in this repo.** `chapter_cards.py` copies the live 145 word ext
   table at `0x083B5D28` into a 146 word copy whose last word is its new op. Check whether
   `chapter_cards` is in `build_list_trial_plateau.txt`. If it is, you MUST copy the LIVE table, not
   the base one, and your module must run after it.

## Do not rebuild what I already verified

Do not re-run the full suite to "check the tree is clean" before you start. It is clean, and the
result is above. Run the suite ONCE, at the end, after your own edits.
