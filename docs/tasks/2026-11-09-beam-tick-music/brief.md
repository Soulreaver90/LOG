# Brief: the beam fires from the WRONG code path, and the music restarts twice

Two defects, both root-caused from the handlers by the controller. **The owner said: "please lets not
waste an entire rebuild until we confirm its 100% fixed!"** So you PROVE both fixes with tests that
fail today and pass after, and you build ONCE at the end.

Base build: `builds\mockups\future\beam_start_wip1.gba`, sha1 `3a40c211`. The poses and the dialogue
in it are correct and the owner approved them. Do not touch either.

Read first: `docs\tasks\global.md`, then this brief.

---

## Defect 1: `BEAM_RISE` is in the function that does not position the fired beam

**The number 29 is right. The code path is wrong.** Do not re-derive 29.

There are TWO position calculations:

1. `gb_start` (our clone) computes a spawn point when the object is created. `BEAM_RISE` is applied
   there already, at `sub r0,#0x1d`, `rom:0x94DA78`. **Keep it.** It positions the charge.
2. **The tick `@0x0801D7DC` recomputes the position AGAIN at the moment the beam fires**, and hands
   that pair to the fire call. It ignores everything the start stored.

The tick, disassembled from the ROM:

```
bl   0x8007a26        ; spawn point recomputed FROM THE ACTOR
ldrb r0,[r5,#0x10]    ; the actor's facing
ldr  r1,=0x08701dec
add  r1,#0x4          ; the VANILLA muzzle offset table 0x08701DF0
lsl  r0,r0,#3
add  r0,r0,r1         ; &muzzle[facing]
ldr  r1,[sp,#0xc]     ; x
ldr  r2,[r0,#0x0]     ; muzzle dx
add  r1,r1,r2
ldr  r2,[sp,#0x10]    ; y
ldr  r0,[r0,#0x4]     ; muzzle dy
add  r0,r2,r0         ; <-- THE FIRE Y IS FORMED HERE
str  r0,[sp,#0x8]
str  r0,[sp,#0x18]    ; the pair handed to the fire call
bl   0x8014478        ; FIRE
```

**Slot 2 of the gold vtable still points at `0x0801D7DD`, the VANILLA tick.** That is why the beam
did not move.

### The arithmetic, already measured, so you do not repeat it

- Bible B1964: `sub_08007A26` for facing **1** returns the actor's hurtbox **centre**.
- Trunks' direction 1 hurtbox is `(-2, -26)` to `(+17, +10)`, so centre y is his point **-8**.
- Vanilla muzzle entry for direction 1 is `(0, 0)`, so the fire y is his point **-8**.
- The gold dir 1 beam run reaches `+16` from the fire point, so the beam's bottom is his point **+8**.
- His 16x32 firing frame is drawn at `dy -24`, so its bottom row is his point **+7**.

The beam has been starting at his feet to the pixel, which is exactly his screenshot. His raised
hands are at his point **-21**, so the fire y must become his point **-37**: a lift of **29**.

### What to build

**Clone the tick** the same way `gb_start` and `gb_build` were cloned, and point vtable slot 2 at the
clone. Apply the lift to the fire y inside the clone.

Either shape is fine, your judgement, but say which you chose and why:

- insert the lift after the fire y is formed, or
- clone the muzzle offset table, set direction 1's dy to the lift, and aim the clone's pool literal
  at your copy.

**The vanilla tick `0x0801D7DC`, the vanilla muzzle table `0x08701DF0` and the vanilla builder must
all stay byte identical**, because Gohan's Cell Games Kamehameha shares every one of them. The same
trampoline and `ssj2_form.assemble` machinery the existing clones use applies: pool literals sit
outside the body and a Thumb `bl` cannot reach the base ROM from expansion.

Keep ONE named constant for the lift, used by BOTH the start and the tick, so he can nudge it once.

### Prove it before you build

`test_ssj2`'s instruction interpreter already runs cloned code and compares registers; the gold
builder was proved that way. **Run the cloned tick on it and assert the fire y equals the actor's
point minus 37, where today it is minus 8.** That test must FAIL against the current tree and PASS
after your change. Say both results in your report.

---

## Defect 2: the music restarts TWICE between Capsule Corp and the plateau

His words: "the music transitions to a different track between capsule corp and the arena, that
should not be the case".

**Root cause, from the bible, not guessed.** B1191 and B2176: `ext 38` and `ext 39` read the new
map's `+0x24` music word and restart the music **unless the new map names the song ALREADY PLAYING**.
There is no "leave the music alone" value, and `0` is song 0, not silence.

What he hears today:

| Step | Track |
| --- | --- |
| the Capsule Corp fight, `ROUND1_MUSIC` | 28 |
| `plateau.split()`'s `ext 39` load of map 7,100, whose `+0x24` is `ARENA_MUSIC` | **38** |
| round 2's battle start, `ROUND2_MUSIC` | **35** |

### The fix, which is B1191's own stated rule

**Name the song that is playing.** Set the plateau map 7,100's `+0x24` to **28**, and make round 2's
music op **28**. B2028 confirms a script `music(n)` and a map `+0x24 = n` compute an identical record
pointer, so the compare is equal and the track is never restarted. Track 28 then carries unbroken.

This supersedes his earlier "track 35 instead of 15". If the controller tells you he wants 35
instead, carry **35** across BOTH halves rather than 28; the mechanism is the same either way.

**Check, do not assume:** map 6,100 also carries `+0x24 = 38` and reaches 28 only through a script
op. Read the whole chain from the Capsule Corp fight start to round 2's battle start and confirm 28
is genuinely the track playing at the moment of the load. If it is not, name whatever is, and say so.

### Prove it before you build

A test that reads the built map entry's `+0x24` and both modules' music ops, and asserts all three
name the same song. It must fail today.

---

## Build and verify

- Build ONCE, at the end, from `scripts\permanent\build_list_trial_plateau.txt` to
  `builds\mockups\future\beam_tick_wip1.gba`. Never overwrite an existing ROM. Never touch
  `build_list.txt` or `build_list_dev.txt`.
- Run the full suite ONCE, redirected to a file, never piped into head or tail.
  `test_battle_start.test_form_survives_the_leader_change` is a known red that predates this work.
- Bank bible rows in `docs\tasks\2026-11-09-beam-tick-music\rows.md` as `## Section N` table blocks,
  tag `BTM`. **Check that tag is free first**: `grep '| BTM |' docs\RE-BIBLE.md`. On 2026-11-09 a
  reused tag read as "already merged" and nearly lost 13 rows. Do not edit `RE-BIBLE.md`.

## Hard rules

- Absolute paths only. Never `cd`, `Set-Location` or `Push-Location`.
- Python is `py -3.14 -P`. Never `py -3`.
- Never write under `data\`. Never overwrite a ROM, save or state: check absence, then create.
- Never put a Windows path inside a Python string literal in `python -c` or a heredoc.
- No em dashes or en dashes in any output.
- Do not re-word his dialogue. Do not touch the poses. Both are approved.
- Do not read or write inside `art\Owner Build - Trunks Tank\`. That is his live art.

One report message, then stop. Do not add a byte order mark.
