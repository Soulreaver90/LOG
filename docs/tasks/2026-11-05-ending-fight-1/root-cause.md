# Ending fight: what the evidence actually says

Written 2026-11-05. This is the THIRD version of this file. The first two each carried a
conclusion that did not survive checking, and both are recorded in the ledger rather than hidden.

## Read this first

I do not have a verified control state. Three of the four save states I have are the same broken
moment. One is different, and I do not know what it is. Every conclusion below is labelled with
what actually supports it.

| State | What it is |
|---|---|
| `ss1` | during the nightmare line, cutscene running |
| `ss2` | the reported fault |
| `pc1` | **the same fault moment again**, not a control, see below |
| `pc2` | the only state that differs. Nature UNVERIFIED |

`log2_poc_r41_endingfight_postcell.gba` has the SAME sha1 `34f045fb` as the fault build, so `pc1`
and `pc2` come from the same ROM. `pc1`'s objects 4 and 5 are identical to `ss2`'s, a 16x32 tile
728 at (112,112) and a 64x64 tile 600 at (88,16). That is the same stuck fight.

## The measurements

| Word | ss1 (line) | ss2 (fault) | pc1 (= fault) | pc2 (differs) |
|---|---|---|---|---|
| `Sprite_CurrentDirectory` `0x03001FA8` | `0x0202EBA4` | `0x00000000` | `0x00000000` | `0x00000000` |
| `Handler_Depth` `0x03000E24` | 2 | 1 | 1 | **0** |
| `0x03001FDC` | 1 | 1 | 1 | **0** |
| `Scene_Current` `0x03000FF4` | `0x030020C8` | `0x030020F4` | `0x030020F4` | `0x030020C0` |

| Register | ss1 | ss2 | pc1 | pc2 |
|---|---|---|---|---|
| `DISPCNT` | `0x1E40` | `0x1F40` | `0x1F40` | `0x1F40` |
| `BG0CNT` | `0x1C81` | `0x1C80` | `0x1C80` | `0x1C80` |
| `BLDCNT` | `0x1E41` | `0x1E41` | `0x1E41` | `0x1E41` |
| `BLDALPHA` | `0x0C09` | `0x1010` | `0x1010` | `0x1010` |

## What is ruled out, and on what grounds

1. **The blend is not the fault.** `pc2`, the state furthest from the fault, carries the identical
   `DISPCNT 0x1F40`, `BG0CNT 0x1C80`, `BLDCNT 0x1E41` and `BLDALPHA 0x1010`. Supported by `pc2`.

2. **A zero `Sprite_CurrentDirectory` is not the fault.** `pc2` holds it at zero with
   `Handler_Depth` 0. The disassembly agrees that a zero does not make a lookup fail:
   `Sprite_Directory_Lookup` `@0x08009324` falls through to `[base+0x20]`, reads a count byte and
   indexes the party roster via `Sprite_ObjectDirectory` `@0x0802645C`. Supported by `pc2` plus
   the disassembly. I had called this word a player pointer twice, from an agent and from a Grok
   review, before reading the handler.

## The leading theory, back after being wrongly retracted

**One level is still active at the fault.** `Handler_Depth` reads 1 and `0x03001FDC` reads 1 at
the fault, against 0 and 0 in `pc2`. I retracted this earlier on the strength of `pc1`, which was
the bug itself. The retraction was wrong and the theory stands.

What does NOT fit it: the ending table `rom:0x3B8140` is entered by two type 5 records,
`rom:0x3C4E90` (resume 30) and `rom:0x3DD03C` (resume 89), and both resume indices land on an END
word (`word 30` of table `0x3C4E98` and `word 89` of table `0x3DD044` are both `0x00000000`). On
that reading the outer scene should end too. Either a third level exists, or the live path is not
one of these two. Not resolved.

## Verified from the ROM, independent of any save state

- The type 5 record shape is `{u16 next, u8 type=5}` then the table pointer. It CALLS the inner
  table and resumes the outer one at `next`.
- `ext 86` is `sub_0800AB82` into `sub_080040AA`: it toggles bit 1 of a flag byte and on set
  creates a kind 18 object with `+0x20 = 1` and `+0x24 = -16`. That is the HUD.
- Record F in the built ROM carries exactly the ops it was written with.

## Open contradictions I have NOT resolved

1. **Object 4's y does not agree with `move_to`.** It sits at screen y 112. With `BG1VOFS` 48 or
   `BG2VOFS` 112 that is world y 160 or 224, not the 568 that `move_to(set=0, 248, 568)` names.
   The x agrees (screen 112 plus HOFS 136 = world 248). I noticed this, set it aside, and then
   wrote "move_to placed him" from the x alone. That was wrong and the y is still unexplained.

2. **An OAM entry does not prove a live actor.** Tile 728 belonged to an actor during the line,
   and record F's `ext 52` removes set 133. So "both fighters are on screen" is not established.

3. **What `pc2` is.** Free play, a menu, dialog or a fight. It has five small HUD objects and no
   character objects at all. This needs one question to the owner.

## What changed in v2

Only the defect the owner named: `ext 33 camera_follow(0)` is removed from record F, so the view
is not moved. Nothing above is fixed by it.
