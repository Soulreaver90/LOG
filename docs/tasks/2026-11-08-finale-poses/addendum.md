# Addendum: the owner added the transition defects to this same rebuild

He said: "okay but fix the transition, fix the dialgoue, do it all in this rebuild". So jobs 4, 5 and
6 below join the three jobs in `brief.md`. **One build carries all six.**

The full measurements are in `docs\ledger\queue.md`, section
"2026-11-08 play test of `finale_dialogue_wip4.gba`", including the controller's later narrowing of
finding 3. Read that section before you touch these. All three live in `ending_fight.py` record A
(the Capsule Corp arrival, ending word 13).

---

## Job 4: his sprite shows at the very bottom during the "Three years later..." caption

His words: "when we transtion to trunks going to cpasule corp, you see his sprite in the very bottom,
not sure if in vanilla hes there or if he is supposed to aarrive off screen".

**Ruled OUT already: solid ground clamping.** `CAPTION_SPOT` (248,664) decodes as OPEN walkable
ground. That was checked through the real collision decoder, not a raw byte read.

**LIKELY cause, not confirmed:** the camera never holds at `VIEW` (136,456). Only one camera
behaviour puts the sprite in the bottom third of the screen, which is what he describes: the camera
still centred where the map loaded him, (248,624). So `ext 31`'s park either never takes effect or a
camera follow re-centres on the player.

**Confirm the camera's real position before you fix it.** The arithmetic matches but no running
frame was ever read. If you cannot confirm it, say so and take fix 1, which does not depend on the
camera at all:

1. **Remove the player for the caption with `ext 52`** rather than walking him off frame. He is
   respawned for the arrival anyway. No camera dependency, so it cannot regress later.
2. Turn camera follow off before `ext 31` parks.
3. Move the player FIRST, then park the camera.

## Job 5: the HUD is visible during the dialogue

His words: "also the hud for trunks is visible, when it shouldnt be, it should appear whent he
dialgue ends I think."

`ext 86 (n)` is the HUD toggle (bible B0471, `@0x0800AB82`). Record A already runs `ext 86 (0)`, so
on paper it is off. **Walk every HUD op from record A through to the fight start** and find what
turns it back on, or find that the talk records never had it off.

His expectation is explicit: the HUD appears when the dialogue ENDS.

**Jobs 4 and 5 are probably ONE cause, not two.** Both `ext 31` and `ext 86 (0)` sit in record A and
both appear to do nothing. Check that before you write two separate fixes.

## Job 6: Trunks reaches the Cell fight with drained ki

His words: "also trunks ssj ki is drained after the 3 year split, it should be refrsehed for the cell
fight".

Three years pass in the caption, so this is a story beat, not a balance change. Vanilla has a refill
op: `chamber_spar` uses one (bible B0715, "refill"). Find it and run it in the three year transition
so the fight starts fresh.

---

## Unchanged from the brief

Same build list, same trial ROM name, same suite rules, same hard rules. Bank bible rows for these in
the same `rows.md`, tag `FPS`. Never re-word his dialogue.

One report message, then stop. Do not add a byte order mark.
