# Brief: restore the Trunks transformation animation, future androids v4

Agent: small build. Read `docs\tasks\global.md` first. Absolute paths only. Never `cd`.
The owner play-tested v3 this morning: "the fights themselves work perfectly". **One defect only.**

## His words

"The only issue is trunks transforms in an instant, the transformation animation is missing, that is
literally it."

## Why it is missing, already diagnosed. Do not re-derive this.

`future_androids.py` rewrites ending word 4. Vanilla's word 4 at `rom:0x3B7C1C` is the NPC transform:

```
wait(40) ; face(132,0) ; sound(55) ; pose(132,9) ; remove(132) ; spawn(133,496,504) ; sound(23)
```

The v3 build kept the wait, both sounds and the face, and replaced the remove-and-spawn with a single
`ext 73 (3,133)`. It deliberately DROPPED `pose(132,9)`, with this reasoning in its own report: "`ext57_set_state
@0x08009FC4` does not block, and vanilla destroyed the posed NPC one op later, so the pose never played."

That reasoning is right for an NPC and **wrong for a live player**. Bible row `B0605`: player state 9
(power up, object `@0x03002174`, vtable `@0x08025B80`) enter `@0x08011D38` sets **anim 9**, tick
`@0x08011D4A` runs **0xA0 = 160 frames**, then plays sound 23 and the state ends. So on the player the
state is the animation, and dropping it is what removed the transformation.

## The shape to copy. It is already shipped and the owner already approved it.

`scripts\permanent\patches\cellgames_ssj.py`, `GOKU_TRANSFORM`:

```
push 55    ; ext 46     aura sound on
push 0,9   ; ext 57     PLAYER state 9, power up
push 10    ; ext 42     white flash
push 55    ; ext 47     aura sound off
push 4,61  ; ext 73     appearance swap
push 10    ; ext 43     wait
```

Retarget the appearance op to Trunks: `push 3 ; push 133 ; ext 73`. Keep everything else's role.

## The one judgement call that is yours

`cellgames_ssj` waits 10 frames after the swap. The player's state 9 runs 160. Decide how long word 4
should hold so the power-up READS before word 5's line "TRUNKS: The name's Trunks..." begins, and say in
your report what you chose and why. Consider that the appearance swap lands mid-animation in the shipped
Goku version and that this is apparently acceptable to the owner, so matching it is defensible; a longer
hold is also defensible. Do not exceed what the scene can carry without feeling slow.

Do not add sound 23 by hand if state 9 already plays it at its end. Check before you add a duplicate.

## Scope

- Change `scripts\permanent\patches\future_androids.py` word 4 only. Change nothing else.
- Build **v4** into the SAME folder, `builds\mockups\2026-11-07-future-androids\`. Move v3 to
  `superseded\` beside v1 and v2, per the one-folder-per-mockup-type rule. Keep every `.sav` and never
  overwrite one.
- `build_list.txt` and `build_list_core.txt` stay untouched. Golden must still rebuild to `acf1b15f` and
  dev to `ffbd2bfc`.
- Read the changed record BACK OUT of the built ROM and decode it op by op in your report.
- Run `test_future_androids`, `test_cellgames_ssj`, `test_build` and `test_golden`. Not the full suite.

## Rules

- `py -3.14 -P`. Never put a Windows path inside a Python string literal in a heredoc.
- Never write under `data\`. Never overwrite a ROM, save or state: check absence, then create exclusively.
- Never pipe a test run into `tail` or `head`.
- Cite bible facts by TAG and address, never by a line number.
- Rows as `rows.md` beside this brief only if you earn new facts, tag `FUT2`.

Report: the op by op decode read back from the ROM, the wait you chose and why, the v4 SHA-1, your test
counts with real exit codes, and anything you could not prove.

One report message, then stop. Do not add a byte order mark.
