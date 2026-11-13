# XFM-9: Piccolo's ki bar. Green through Super Namek, yellow for Z+

## The owner's decision, 2026-11-13

Plain green for base AND for Super Namek, with no ki pool. Only Z+ gets a pool, and it ramps to
yellow and stays yellow.

Reported symptom: "It shows the orange ramp and then stays yellow."

## Where this lives

NOT in either master. `ki_ramp`, `piccolo_z_start`, `piccolo_zplus`, `piccolo_powerup_art` and
`powerup_fx` all ship only in trial lists (`piccolo_fx` and friends). Only `bf_ki_pool` is in
golden and dev. Folding XFM-9 into the golden master means promoting that whole line, which is a
separate owner decision (XFM-6 is still PLAY).

## Why the two halves disagree today

**Super Namek (entry 7) and Z+ (entry 24) SHARE form object `0x030021F0`.** The bar picks its
colour by form object, so it cannot tell them apart. Measured from the appearance table.

`pool_ref` ends with a fixed-size splice from `piccolo_z_start`, sized by `fit_probe.py`:

    ldr r5,=SSJ_OBJ
    sub r0,r0,r5
    lsr r0,r0,#3     ; 0: Super Saiyan (diff 0), 4: Namek 0x030021F0 (diff 4, 4>>3 = 0)
    bne ref_none

One compare accepts BOTH objects, with no spare bytes. That is the elegance and the trap.

`ki_ramp` picks its colour by a different rule: bit 0 of the appearance entry the leader is
LEAVING. Leaving entry 7 has bit 0 set, so it ramps ORANGE. The bar then paints yellow. `ki_ramp`
note 3b already works around this by repainting Z+ orange over itself, and the ledger records that
workaround as CONTRADICTED IN GAME.

## The structural fix, recommended

**Make the ramp take its colour from what `pool_ref` would paint, not from the leaving entry's
flags.** Then the ramp and the bar agree by construction and this whole class of mismatch cannot
come back. The leaving-entry rule is a Saiyan heuristic that does not describe Piccolo, who will
have exactly ONE pool form under this decision.

Two changes follow:

1. **`pool_ref` must accept the Namek object for entry 24 only.** `r3` still holds the entry at
   the compare, so an entry test is possible, but the splice is fixed-size and full. Expect to
   need space: check whether `piccolo_zplus` can carry the test instead, since it owns entry 24.
2. **Delete `ki_ramp`'s 3b orange repaint.** With Z+ yellow and Super Namek pool-less, it has
   nothing left to do, and it is the one piece we know does not work in game.

## Do not do this

Entry 7's flags bit 0 must STAY set. It is also what makes `appearance_revert` send Piccolo back on
a leader change (bible B0554). Clearing it to fix a colour would move story behaviour silently.

## Proof this needs

A colour decision is a drawn pixel, so a green suite is not evidence. Build the trial ROM, hand it
to the owner with a save, and let him see: base green, Super Namek green, Z+ ramping yellow and
staying yellow.
