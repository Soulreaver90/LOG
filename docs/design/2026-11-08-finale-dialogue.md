# The finale dialogue and music, as the owner gave it

Given 2026-11-08. This supersedes the placeholder lines in `plateau.py` and is the spec for the
rung 6 and rung 7 work. **Lines are quoted EXACTLY as he wrote them, typos and all.** Do not
"correct" his wording. Ask before changing a single character.

Track numbers are music ids, matching `art\music\log2\track_NN.it`, which he picked by ear in
OpenMPT. The music table is `rom:0x1D4B2C`, 44 songs, ids 0 to 43.

---

## 1. After Trunks beats future 17

REPLACE the existing line `now theres just one more thing that needs to be done` with:

```
I wish I could say that it's all over, but there is one more thing that has to be done
```

then:

```
... Cell
```

His note: "Maybe make ... cell its own line". **Treat as his preference, confirm before building.**

## 2. NEW caption box, after 17 and after the fade out

A box that says:

```
Three years later...
```

- The user presses a button to dismiss it.
- **Track 42 plays when the box appears.**
- Then it fades to Trunks arriving at Capsule Corp, which is already built.

Note for whoever builds it: the caption `@^Three years later...` ALREADY EXISTS in the ROM at
`rom:0x3B8610` (bible row on the LoG II time skip), so the mechanism has a vanilla precedent and the
string may already be reusable. CHECK rather than assume.

## 3. At Capsule Corp

REPLACE Trunks' line `I dont think so` AND the line `the nightmare is over` with:

```
If you can get past me then you can to the past
```

```
But I wont let you!
```

**Track 28 plays when the battle starts.**

**CAUTION:** `THE NIGHTMARE IS OVER CELL!` is used AGAIN later, at the Kamehameha pose in section 5.
Only the EARLY one is replaced here. The ROM's own copy is at `rom:0x3B7FF6`.

## 4. The plateau arena talk

This replaces the two `[PLACEHOLDER ...]` records that `plateau.py` currently ships.

```
Cell gets up
Cell:   "Your energy will be refreshing. A nice treat to start of my journey in the time machine"
Trunks: "Enough!"
Trunks transforms to Super Saiyan if he is not already
Trunks: "You're overconfident Cell."
Cell:   "There's no reason not to be, I've come across thousands like you"
Trunks: "But count me as the last!"
```

**Track 35 starts as the fight starts.** (He first said 15, then changed it: "track 35 instead of 15".)

Note the transform sits BETWEEN two Trunks lines, so the form change is part of the exchange and not
a pre-roll.

## 5. When the fight ends

```
fade transition
Cell at the TOP, Trunks BELOW            <- a VERTICAL pair, not the left-right arrival pair
Cell does the kamehameha pose:  "Kamehame..."
Trunks with arms up
Trunks: "THE NIGHTMARE IS OVER CELL!"
a large blast, maybe Vegeta's Big Bang
kills Cell in an explosion, light flash
Trunks powers down to base
Trunks: "Now I can finally say that it's really over. Thanks to you father, and to you Gohan.
         And especially to you Goku"
back to the credits music that normally plays
```

### The sprite poses, as he named them

He picked these himself from the exported sheets. **These are his choices, not guesses.**

| Who | Pose | Set | Anim | Dir | Source |
| --- | --- | --- | --- | --- | --- |
| Cell | Kamehameha | 28 | 18 | 0 | his words: "Cell set28 a18 d0" |
| Cell | the hit he takes, looped | 28 | 2 | 0 | his words: "set28 a2 d0" |
| Trunks | arms rising | 130 | 4 | 1 | `frame_36AD44.png`, resolved through `log2_sprites.set_records` |
| Trunks | arms up, fires | 130 | 4 | 1 | `frame_36AE4C.png`, same resolve |

Notes that matter:

- Both Trunks frames are **set 130 anim 4 dir 1**, indices 2 and 3 of the same anim. **Not anim 11**,
  which an earlier draft of this document guessed. Anim 4 is the idle variant that raises and lowers
  the arms, so the raise he wants is already in it.
- **Dir 1 is the back view.** That agrees with his staging: Cell at the top, Trunks below, so Trunks
  faces away from the camera and fires upward.
- He listed `frame_36AE4C` first and said "second is his hands up, he shoots the blast", so the
  firing frame is the one he listed second, `frame_36AD44` = index 2. **Confirm this with him before
  wiring**, because the two frames are one frame apart and the order is easy to read either way.

### The death sequence, in his words

> "FOr the explosion, we can do something similar with how perfect cell dies, where he does a hit
> animation with explosions a few times, I think there is screen rumbling. So when cell gets hit with
> the blast, white flash, imperfect cell does the set28 a2 d0 animation, each loop with the smoke
> effect explosion and and screeenrumbling before he finally explodes, so 3 loops maybe, check how
> perfect cell dies against gohan after the kamehameha"

So the shape is: blast lands, white flash, then **3 loops** of (hit anim + smoke explosion + screen
rumble), then the final explosion.

### The blast itself

He asked: "In the anime, its a giant beam, but I dont think we have that in the game at all", then
"maybe we can use the spirit bomb sprite? full size?"

---

## Settled

1. **`... Cell` gets its own box.** He said "Maybe make ... cell its own line", and that is the
   reading taken. Flagged here so he can overrule it when he plays the build.
2. **The firing frame is `frame_36AD44`**, header `0x36AD44`, set 130 anim 4 dir 1 index 2. He
   listed `frame_36AE4C` first and said "second is his hands up, he shoots the blast", so the
   second one he named is the firing pose. Re-resolved through `log2_sprites.set_records` on
   2026-11-08 after an earlier note had the two the wrong way round. **Brief this frame by its
   filename and header address, never by index.**
3. **Three hit loops, not four.** His ruling: "lets do 3 loops isntead of 4 for future cell."
4. **He repurposes the idle.** "yeah its the idle arms up and down but we can repurpose it to make
   it look like he is shooting up."

## Open, and mine to measure before building

- Whether `@^Three years later...` at `rom:0x3B8610` can be reused as-is, including its dismiss
  behaviour, or whether a new caption record is needed.
- Whether the caption box's button dismiss is the same mechanism as the existing captions.
- Where the vertical Cell-above-Trunks pair lands on the owner's map 142, against the walkable box
  (px x 96 to 792, y 136 to 784), the sealed pocket at px (488,536) to (616,608), the 477 BG1 cells
  that draw OVER the player, and his new overhead cliff at px (416,768) to (520,776).
- Whether Vegeta's Big Bang animation can be driven for Trunks, and what it costs.

---

# The blast, settled 2026-11-08

## The game HAS a full beam

The engine draws a real screen-crossing beam, not only a sphere. The beam object `@0x080143A8`
builds an origin, a repeating 32x8 body, a tip and a burst, in all four directions. `ext 137 (set, n)`
already drives it: Gohan's Cell Games Kamehameha is `ext 137 (0, 140)`.

## The owner picked the yellow set

The beam object carries **two interchangeable record sets**, chosen by argument 6:

| argument 6 | records | measured colour |
| --- | --- | --- |
| 0 | `0x086E29B4` charge, `0x086E3458` beam | white core, cyan and blue |
| non-zero | `0x08703B60` charge, `0x08704604` beam | white core, yellow and gold, pink outline |

Both sets are byte identical in geometry, so this is a pure pixel swap. Rendered side by side in
`art\finale\beam-colours.png`, with an orange remap option in `art\finale\beam-orange-preview.png`.

**His ruling: "teh blast was yellow so just use the existing middle one."** So we use the gold set
as it ships. No drawing, no recolour, no new art. The orange remap stays on the shelf.

His anime reference frame shows a vertical white-gold beam firing upward and widening at the top.
That is the gold set's **direction 1** run, which matches the staging already chosen: Cell above,
Trunks below, firing up.

## What it costs to switch the colour on

`ext 137` hardcodes blue. `sub_0801D84C` sets argument 6 at `rom:0x1D870` with `mov r2,#0x0`, and
the immediate is the single byte at `rom:0x1D870`.

**We cannot flip that byte globally.** `ext 137` has exactly two vanilla sites, and one of them is
Gohan's Cell Games Kamehameha, which must stay blue.

So the module adds a gold entry point instead, all in expansion space:

1. Copy `sub_0801D84C` (0x3E bytes) with that one byte set to `0x01`.
2. Copy `sub_0801D788` (0x54 bytes) with its `bl` retargeted to the copy.
3. Copy the `ext 137` command vtable `0x0802521C`, slot 1 pointing at the new start.
4. Copy the `ext 137` handler `@0x0800A3A2` to load the new vtable.
5. Relocate the ext dispatch table and add one entry for the new op.

About 200 bytes of new code plus one table relocation, which is the same pattern the map table and
the scouter table already use. Every vanilla beam keeps its colour.

## The death loop, measured from vanilla

Perfect Cell's death is ending table `rom:0x3EC758` word 19, record `0x083EBE1C`. **Decoded through
the table walk, not a guessed length.** An earlier pass used `--len 0x163` and stopped one and a
half blocks early, so the "four blocks" first reported here was wrong.

After the Kamehameha it runs a 32-iteration hit loop, then **five** blocks. Four are hit loops:

```
block_begin
ext 134 (0, 20, n)          <- the camera op, n = 30, 30, 40, 20 across the four hit loops
hit(set 30, sound 31)
face_target(set 30)
pose(set 30, 2)
ext 94 ; hit(set 30, sound 20 or 21)    x3
block_end
wait(20)
```

The fifth block is the **final explosion**, and it is a different, bigger shape:

```
block_begin
ext 134 (0, 20, 80)         <- the largest camera value in the record
face_target(set 30) ; pose(set 30, 2) ; hit(set 30, 21)
ext 94 (30, 0, 0) ; ext 94 (30, 16, 16) ; three more ext 94 at offsets
remove(set 30)              <- Cell is destroyed here
block_end
wait(80)
ext 139 (500000)
music(id = 37)              <- vanilla's own post-Cell-death track
fade_out(120)
```

**Build three hit loops, then the fifth explosion block.** His ruling is three, and the explosion
block is a separate beat, not one of the three.

`ext 94 (actor, dx, dy)` builds an effect at the actor's centre (bible B0793). `ext 134 (actor, b, n)`
pushes its command onto the **camera chain head** at `0x03000FF4`; it is the only camera-touching op
in the record, which matches his memory of screen rumble. Its tick is empty, so it fires once.

`music(37)` is worth noting against his line "back to the credits music that normally plays": 37 is
what vanilla itself starts the moment Cell dies.

---

# Build state for `future_v3`, set by the controller 2026-11-08

## His map is already copied in

`art\plateau\map_142.json` now holds his live file byte for byte. Copied and audited BEFORE any
agent started, so no agent's input changes under it. **Do not copy it again.**

What the copy brought in, measured by diff against the previous repo copy:

| change | detail |
| --- | --- |
| One collision cell OPENED | collision byte 2090, `0xBF` to `0xFF`, bit 6. World cell (86,65) = px (688,520) |
| Cliff art moved up a layer | BG3 lost 20 cells, BG2 lost 8, BG1 gained 9, all in world px x328-527, y768-823 |
| Editor stamps | 215 to 218. Editor-only data, nothing reaches the ROM |

Re-audited after the copy: **validate CLEAN**, 4988 open cells (was 4987), 4849 reachable from the
centre (was 4848), **the wall still holds** with no border cell reachable, and the one sealed pocket
is unchanged at 139 cells at px (488,536) to (616,608).

## One test WILL go red, and it is not a defect

`test_plateau.test_no_over_layer_was_blanked_and_bg1_really_stands_over_him` asserts
`{"bg0": 0, "bg1": 477}`. That 477 was measured against the OLD map. His cliff move changes it.

The count cannot be computed without a build, because it reads the built ROM's own tiles. So:
**build first, read the real number, then update the constant and the docstring to the measured
value, and say the old and new numbers in the report.** Do not reach the number by trial.
`bg0` must stay 0: if BG0 ever draws over walkable ground, that IS a defect, so report it instead
of updating it.

The plateau docstring also carries 1100, 477, 4987, 4848 and 139. 1100 is now 1109 and the others
are above. Fix every one.

## The transition cut is approved

His words: "the transition from capsule corp tot he plateau arena is very very long." Measured at
9.8 seconds. Cut it to about 5.6 seconds with these four, all of which have a precedent:

| op | from | to | why it is safe |
| --- | --- | --- | --- |
| `camera` speed | 2 | 40 | speed 40 is already proven on the plateau in v6 |
| `fade_in` | 180 | 90 | vanilla precedent at `rom:0x3BB6A2` |
| `fade_out` | 180 | 90 | our own copy, not vanilla's |
| opening `wait` | 60 | 30 | |

**Do not touch `wait(120)`** (`REC13_SETTLE`). It was never measured and it is the map load settle.

---

## Section 7: his play-test ruling on wip3 (2026-11-08 evening). THIS SUPERSEDES SECTION 5.

He played `finale_blast_wip3.gba` and rejected the poses. His words:

> "For some reason, you are not using the sprite I told you to use. I was very clear which kamehameha
> sprite to use. And trunks is waving his hands around and doing slashes, what the heck. I was very
> clear of thw two sprites, his hands down, then his hands up, his hands up will be shooting the blast."

> "I just want the held pose of him charging the kamehameha, not shooting it. It should be a tense
> Kame.. hame.." / "then trunks interupts with the nightmare quote" / "cell never gets a chance to
> shoot the kamehameha" / "so split the cell dialgoue to two"

### Root cause, MEASURED, not guessed

**State 30 is not a held pose.** Bible B0149, from the tick `@0x0801CB24`: it shows frame 0 for 8
ticks, then ALTERNATES frames 1 and 2 every 8 ticks, for ever. Both defects come from this one fact:

| What he saw | Why |
| --- | --- |
| Cell not in the pose he picked | frame 0 of set 28 anim 18 dir 0 IS his charge pose, but it shows for 8 ticks only, then flickers frames 1 and 2, which are arms-spread release poses |
| Trunks "doing slashes" | `ext 137` forces state 30 on the shooter, and set 133 anim 18 dir 1 is Trunks' SWORD SPECIAL. Frame 2 is the slash arc |
| Trunks "waving his hands around" | the override `ext 121 (0, 4)` runs state 4 = anim 4, which cycles arms down, up, down, up over 64 ticks, then drops to standing |

Rendered from the build with `rom_sheet.py` and viewed by the controller:
`scratch\2026-11-08-finale-poses\`.

### The frame identity, settled by looking

The wip3 report said index 2 was "his firing frame". **That is wrong.** Set 133 anim 4 dir 1 renders
down, up, down, up:

| index | header | pose |
| --- | --- | --- |
| 0 | `0x36AB20` | arms down |
| 1 | `0x36AC30` | arms up |
| **2** | **`0x36AD44`** | **arms DOWN. This is "his hands down"** |
| **3** | **`0x36AE4C`** | **arms UP. This is "his hands up", the one that fires** |

### What the finale must do now

1. **Cell HOLDS the charge pose**, set 28 anim 18 dir 0 **frame 0**, with no flicker and no release.
   He never fires.
2. **Cell's line splits into two boxes:** `Kame..` then `hame..`. Tense, drawn out.
3. **Trunks interrupts** with `THE NIGHTMARE IS OVER CELL!` while Cell is still charging.
4. **Trunks shows exactly two held frames:** index 2 (hands down) first, then index 3 (hands up),
   and the hands-up frame is HELD for the whole beam. No anim 4 cycle. No anim 18 slash.

### The constraint the builder must solve

A held single frame needs a row whose frames are all the same picture, because every state that could
drive the pose animates. Cloning a row is the project's own method (`log2_sprites` clones a set with
replaced frames). **Two rows are NOT free to clone and must be left alone or worked around:**

- **set 28 anim 18** is Imperfect Cell's own vanilla Kamehameha, used at `rom:0x3E1484` (map 10,20).
- **set 133 anim 18** is Trunks' sword special, and he uses it in the future androids fight, which
  `future_androids` ships in this same build.

So the builder must prove, before cloning anything, which rows this build actually reaches, and must
not break either scene above. A finale-only clone SET is the safe fallback.
