# Addendum 2: the owner caught us cutting the WRONG transition

He said: "I wonder if the transition youve been fixing is the transition TO capsule corp and not the
one to the plateau?" and then, flatly:

> "the 3 year transition is NOT the transition, thats the city to capsule corp. The issue is the
> capsule corp to the final battle plateue transition"

**He is right.** Verified by decoding the shipped `finale_blast_wip3.gba` ending table `rom:0x3B8140`.

## The two transitions, and which one was cut

| Transition | Record | State |
| --- | --- | --- |
| 3 year skip, city to Capsule Corp | `ending_fight.arrive()`, ending word 13 `rom:0x94064C` | ALREADY cut to 90 frames. Leave it alone. |
| **Capsule Corp to the plateau** | **`plateau.split()`** | **never touched. THIS is his complaint.** |

Ending word 13 loads map 6,100 and hands on to word 24, the "Three years later..." caption, then word
25, then word 14 "Come out Cell!". That whole stretch is Capsule Corp. The plateau, map 7,100, is
loaded by `plateau.split()` when round 1's Cell reaches HP 0.

## Job 7: cut the Capsule Corp to plateau transition

In `plateau.split()` the black runs:

```
fade_out(SPLIT_FADE=30) + load_map_at(7,100,...) + wait(LOAD_SETTLE=120)
  + the staging ops + ext 31 camera park (speed 40) + fade_in(SPLIT_FADE=30)
```

**`LOAD_SETTLE = 120` is the target.** It is the SAME 120 the previous agent already cut to 20 on
record 13, for a reason it proved and shipped: the FADE covers the map load, so the wait that follows
runs under black that nothing draws into. That reasoning transfers here unchanged. Keep a margin, do
not go to zero: a load does not finish inside its own op.

**The owner counted about 6 seconds of black. The scripted ops account for about 3.1 seconds. Find
the missing 3 seconds before you declare this fixed.** Two candidates worth reading first:

1. **`ext 57 (CELL_SET, DOWN_STATE)` in the `stage` block BLOCKS** until the state reports done. If
   DOWN_STATE's anim is long, or never ends, that is dead black time. Compare with `ext 121`, which
   sets a state and does not wait (bible B0750). Note `split()`'s own step 5b already uses `ext 121`
   for Cell standing, and gives the reason.
2. The map load itself. 7,100 is his composed map; time it rather than assume it is instant.

Do not guess a duration. Read the ops, and say in your report which op accounts for which frames.

## Jobs 4 and 5 still stand, and job 5 is now CONFIRMED

Jobs 4 and 5 in `addendum.md` are about the Capsule Corp arrival and are still real. The decode
CONFIRMS job 5 and names the op:

- ending word 13 `rom:0x94067D` runs `header_bit1(value=0)`, the HUD off;
- ending word 25 `rom:0x9406BA` runs **`header_bit1(value=1)`, the HUD back ON**;
- word 25 hands on to word 14, "Come out Cell!", which is the START of the dialogue.

So the HUD is turned on one record BEFORE the dialogue begins, which is exactly what he reported. His
expectation: the HUD appears when the dialogue ENDS. The dialogue ends at word 23, which already runs
`header_bit1(value=1)` at `rom:0x94683F` as part of the standard battle start. So the fix is likely
to drop the early one, not to add a new one. Check that word 23 is reached on every path first.

For job 4, the same word 13 runs `move_to(set=0, x=248, y=664)` at `rom:0x940686` and parks the view
with `camera(x=136, y=456, speed=40)` at `rom:0x940679`. The camera park is a PAN at speed 40, not an
instant jump, so the caption can open while the camera is still travelling. That is consistent with
the controller's LIKELY cause and is worth reading before you choose a fix.

## The owner is supplying save states

He offered states 1 (before the transition), 2 (during it) and 3 (right after). If they are on disk
when you reach job 7, use them to measure the real black duration rather than trusting arithmetic.
Ask the controller if you need them and they are not there.

One report message, then stop. Do not add a byte order mark.

---

## Job 8: did OUR transition cut cause the HUD and the sprite defects?

He asked: "I wonder if your changes to the 3 year transition is what caused the issues with the hud
and the trunsk being visible at the bottom".

**Treat this as the leading hypothesis, and TEST it. Do not argue it from reasoning.**

What the controller can confirm now, from the decode:

- Ending words 13 and 25 are BOTH at expansion addresses (`rom:0x94064C` and `rom:0x9406AC`), so both
  records are OURS, written by `ending_fight.arrive()`. Vanilla record 13 is preserved untouched at
  `rom:0x3B7E4A`. So whatever these two records do, we wrote it.
- The cut shortened the reveal fade from vanilla's 180 frames to `REVEAL = 90`, and the opening pair
  from `wait(60) ; fade_out(180)` to `wait(10) ; fade_out(60)`. **A shorter fade makes the screen
  visible sooner, so staging that a long fade used to hide can now be seen.** That is a credible
  mechanism for "you see his sprite in the very bottom".
- The HUD is a separate matter: `header_bit1(value=1)` sits in word 25 at `rom:0x9406BA`, one record
  BEFORE the dialogue starts at word 14. That is a structural ordering fault in our own record and
  it would show at any fade length. The cut is unlikely to be its cause.

**The decisive test, and it is cheap.** Build one extra trial ROM with the cut reverted to the
vanilla values (`HEAD_WAIT` 60, `HEAD_FADE` 180, `REVEAL` 180, `REC13_SETTLE` 120) and nothing else
changed. Then:

- if the sprite still shows at the bottom, the cut is NOT the cause and the staging is wrong;
- if it stops showing, the cut IS the cause, and the fix is to re-order the staging so it is correct
  at ANY fade length, NOT to put the slow fade back. He asked for a shorter transition and he still
  wants one.

Say in your report which of the two it was, with the evidence. Name that extra ROM
`builds\mockups\future\revert_probe.gba` so it is obviously a probe and not a candidate.

If the owner's save states arrive, prefer them: state 2 is during the transition and settles the
camera position directly, which the controller could only reason about.

---

## Job 9 SUPERSEDES job 7's method: COPY VANILLA, do not invent numbers

The owner: "again, why are we reinvintng the wheel, the game has loads of transitions, find out o,
the length of time, etc, and thats what we use".

He is right, and the measurement ALREADY EXISTS in the bible. Do not re-derive it.

**Bible B1017, the fade census over the 875 type 0 records the map walk reaches:**

- `ext 40 fade_out`, 44 sites: **120 x17**, 180 x9, 240 x5, 60 x4, 300 x3, 90 x3
- `ext 41 fade_in`, 28 sites: **120 x12**, 90 x5, 240 x3, 180 x3, 60 x2
- Of the 28 records carrying BOTH, **26 use the SAME number in each**.

So the house value is **120 out and 120 in**.

**Bible B2170, a vanilla map-load transition decoded op for op** (`rom:0x3E9E8C`, the third Cell
Junior's death event, which also proves a death event survives a map load):

```
ext88 ; ext139(50000) ; header_bit1(0) ; fade_out(120) ; leader(0) ;
load_map_at(14,3,1,576,376) ; music(37) ; remove(30) ; ext24(0) ; face(0,0) ;
ext84(11) ; spawn(72,640,224) ; face(30,1) ; party_add(0) ; camera(504,152,30) ; fade_in(120)
```

**Read that shape carefully. There is NO settle wait between the load and the fade in.** The staging
ops occupy that space instead. This confirms B0748 and B0877 from a third record.

### What this means for `plateau.split()`

Our shape is wrong in BOTH directions against vanilla:

| | ours | vanilla |
| --- | --- | --- |
| `fade_out` | 30 | 120 |
| settle wait after the load | **120** | **none** |
| `fade_in` | 30 | 120 |

So rebuild `split()`'s hand-off to **B2170's shape**: `header_bit1(0)`, `fade_out(120)`, the load, all
the staging ops back to back, `camera(...)`, `fade_in(120)`. **Delete `LOAD_SETTLE` rather than
shrinking it**, and put the staging where the wait used to be, which is what vanilla does.

Apply the SAME shape to `ending_fight.arrive()`. Its `HEAD_FADE`, `REVEAL` and `REC13_SETTLE` were
all hand-picked numbers and none of them is a vanilla value. This is very likely the cause of job 8:
a 90 frame reveal is outside vanilla's own pairing rule, and staging that a 180 frame fade used to
cover is now visible.

### The one thing still to measure

Vanilla's shape costs 240 frames of fade, which is MORE scripted black than our current 180. The
owner counted about 6 seconds. So a blocking op is eating time that neither number explains. **Find
it.** `ext 57 (CELL_SET, DOWN_STATE)` in `split()`'s `stage` block is the first suspect: `ext 57`
blocks until the state reports done, while `ext 121` sets a state and does not wait (B0750). Vanilla's
B2170 staging uses no blocking op at all.

A continuous 4 second fade reads as deliberate. A 3 second hold on dead black reads as a hang. That
is why copying vanilla's shape can look FASTER while spending more frames.
