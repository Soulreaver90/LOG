# Sprite study: what Buu's Fury can and cannot give us (2026-10-31, me, no task)

Read with `bf-gohan-vs-ours.png` in this folder, which is every frame named below at 8x on magenta.
Labels: C = CONFIRMED by measurement, L = LIKELY, S = SPECULATIVE.

## The measurement that settles the source question

I measured the occupied column runs of every main-cast `stand.png` in
`data\sprites\Buu_Fury_Character_Sprites\characters\`:

| BF character | Frame pitch | Our match? |
|---|---|---|
| **Gohan** | **16 px** | **Yes. Our gi Gohan frames are 16x32** |
| Goku | 32 px | No |
| Piccolo | 32 px | No |
| Vegeta | 32 px | No |
| Trunks | 32 px | No |

(C, column-run measurement, `bf-gohan-vs-ours.png`.)

**This corrects what I told me earlier tonight.** I recommended BF Piccolo as the purple-gi body source,
because Piccolo wears the garment our gi copies. Piccolo is twice our width, so he cannot serve as a body at all.
**BF Gohan is the only scale-matched body in Buu's Fury**, and he is official Webfoot art I have cleared for
porting.

## What BF Gohan gives us, and what it does not

He wears a white shirt and brown trousers, not a gi. So this is a reference for **construction**, never a garment
transplant. Comparing our gi idle against his stand and walk frames at 8x:

| Our frame | BF Gohan | Label |
|---|---|---|
| Limbs are flat: the arm is one skin value against the torso | Each sleeve carries a light and a dark value, so the arm reads as a round volume beside the torso | C (by eye at 8x) |
| The shoe is a dark mass continuous with the leg | The shoe is a separate lighter value with a clear top edge, so the foot reads as a foot | C |
| Arm and torso share an edge, so the silhouette is one block | A visible gap, or a value change, separates arm from torso | C |
| Mostly two values per surface | Mostly three: light, mid, dark | L (not counted per surface yet) |

**What I will not claim.** I guessed earlier that our head is proportionally too large. Seen side by side, the head
and hair masses are comparable. That guess was wrong and is withdrawn.

**Caveat on the comparison.** Our tile is `157_a0_d0_i1`, the blink frame, because index 0 is unchanged in r40 and
has no approved PNG. Its face is unrepresentative. The body, which is the subject here, is the same.

## What this changes about the redraw

The earlier root cause stands: our gi changes 0.0 cells of silhouette against the vanilla armour, so we recoloured
rather than rebuilt. This study adds the missing half, which is **what to rebuild toward**. Not invention, and not
another mod's work. Three measurable properties of official art at our exact frame size:

1. Two values on every limb, so arms and legs read as volumes.
2. The shoe a separate, lighter value from the leg, with a hard top edge.
3. A real separation between arm and torso in the silhouette.

Those are checkable by script, not only by eye. A frame that fails all three has the old problem whatever its colours.

## The one-frame test, banked rather than built

I must judge this by eye, so there is no point drawing something I may reject.
The spec, ready to run:

1. Target: set 157 anim 0 dir 0 index 0, the main standing frame, 16x32, palette mode P.
2. Build the body on BF Gohan's stand construction, keeping our head and hair unchanged (my rule: the gi is body
   only, never the head or chin).
3. Apply my gi rules: sleeveless with skin arms, about 2 px blue wristband, one dark purple row over the top
   of the shoulder, red sash 2 px below the chest V point, one exposed chest skin pixel under the chin, the gi shoe
   shorter than the armour boot with the boot's upper part becoming trousers.
4. Every pixel an index in the OBJ palette at `rom:0x1DA6C8`. No palette entry changes.
5. Gate it on the three properties above before showing him anything.
6. Deliver it as a draft he edits, never as a finished frame. He edits sprites, he does not draw them from scratch.
7. Then one trial build, his frame beside the current one, judged in game.

**Kill criterion, unchanged:** if his edit of my draft is not clearly better than what is already in the
`gi_base_audit` trial, gi work stops and the time goes to scenes.

## Final decisions, 2026-10-31 morning: BF references are not the route

My words: "isnt BF gohan a teen and thus taller? its odd he would be a candidate. In any event, with our sprite
work, using BF references isnt going to cut it. When we make new sprites, we may have to reference official art."

The point about the character stands, and my measurement answered a narrower question than that objection.

**What I measured:** the drawn figure is 30 px tall in our frame and 32 px in BF Gohan, so only 2 px apart, and the
frame pitch is 16 px for both. That settles **scale**, which is what I had been testing.

**What his objection is about, and what I did not measure:** proportion. Buu-saga Gohan is a teenager. Cell-saga
Gohan is a child. Within the same 32 px a teen carries a smaller head ratio, a longer torso and longer legs. Building
our child Gohan on a teen body would make him read as the wrong character even at the right height. My earlier note
that the head masses "look comparable" was an eyeball reading of a blink frame, not a measurement, and it is not
evidence against his point.

**The route is now official art**, not another game's sprites. That also matches how he already works on portraits:
he draws from an anime reference. The clean-room rule is unchanged and unaffected, since it only ever barred the Z
Hack, never official material.

**What survives from this study:** the three measurable properties are about drawing quality, not about which body
was copied, so they still gate any new frame. Two values on every limb, the shoe a separate lighter value with a hard
top edge, and real arm-to-torso separation in the silhouette. Our current frames fail all three.
