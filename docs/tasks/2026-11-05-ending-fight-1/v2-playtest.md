# Ending fight v2: what to play test

ROM: `builds\mockups\2026-11-05-ending-fight-1\log2_poc_r41_endingfight_v2.gba`
SHA-1 `737f85cbc03643d1ec9d2634b048fadcb7995367`. Its `.sav` is byte identical to v1's, so your
progress carries over.

## What changed from v1

One thing. `ext 33 camera_follow(0)` is gone from record F, so the fight starts in the cutscene's
own framing instead of snapping the view to the player. That is the only defect I could confirm,
so it is the only thing I changed. **I have not fixed the fight.**

## Fastest way in

Load save state 1 from v1 (the one just before the nightmare line) against this ROM. The record is
read from the ROM when it runs, so the new record F will execute. If mGBA refuses the state
because the ROM checksum moved, play in from the `.sav` instead.

## What to look for

1. **Does the view stay put** after "THE NIGHTMARE IS OVER CELL!!!!!"?
2. **Does anything respond to the pad?**
3. **Does Cell do anything, and does the boss bar move if you connect?**

A plain "no" to 2 and 3 is a useful answer and I expect it is the likely one. The camera change
does not address whatever froze it.

## One question I need answered

**What is `log2_poc_r41_endingfight_postcell` save state 2?** Free play, a menu, dialog, or a
fight? I used it as my control and I never verified what it is. It is the single state that
behaves differently from the fault, so what it represents decides which theory survives.

## Where the diagnosis actually stands

The leading theory is that **one scene or handler level is still active**, so control never
returns. `Handler_Depth` and `0x03001FDC` both read 1 at the fault and 0 in that one differing
state.

What argues against it: the ending table is entered by a type 5 record that resumes its outer
table at an index whose word is END, so on paper the outer scene should end too. Either there is a
third level or the live path is not the one I traced. Unresolved.

Two things I earlier reported as settled and should not have:

- I said both fighters were provably on screen. An OAM entry cannot tell a live actor from a
  sprite nobody cleared, and record F removes set 133, so that is not established.
- I said `move_to` placed the player. The x agrees, the y does not, and I do not yet know why.

## The untested risk

`ext 70 leader(3)` makes Trunks the party leader. If Trunks is not in your party at that point in
the save, that call has nothing to select. You reached this from the Cell Games save, which is not
where the ending normally begins. If nothing responds to the pad, this is my first suspect and I
will read the `ext 70` handler and the save's party roster before building again.
