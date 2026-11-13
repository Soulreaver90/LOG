# Piccolo: the Super Namek power-up

Approved 2026-11-12. Goes on `set:104` anim 9, the Super Namek set, which is empty in vanilla and is
the null row that crashes a power-up on that set. `set:103` anim 9 is his turban and cape drop, which
is his vanilla Z transformation, and it is not touched.

| Frame | File | Pose |
| --- | --- | --- |
| 1 | `01_arms_down.png` | stands, arms at his sides |
| 2 | `02_arms_out.png` | crouched, arms out, fists clenched |
| 3 | `03_antennae_a.png` | lower, arms wide, mouth open, antennae one way |
| 4 | `04_antennae_b.png` | the same pose, antennae the other way |

**Frames 3 and 4 repeat on a loop, the same as Vegeta's hair sway.** They are the held beat of the
animation.

## The sway

Piccolo's antennae sway inside a fixed outline, because the ridges move but the head silhouette does
not. All 22 changed pixels are the three greens rearranging: `#107800`, `#30A800` and `#50D000`.
The pixel count of each green is identical in both frames, 38, 24 and 16, so nothing is added or
lost. Over rows 6 to 11 the lit pixels move 0.75 px one way and the dark 0.42 px the other, which is
the ridge pattern travelling across the antennae.

That is the right shape for Piccolo. Vegeta's hair swings the whole silhouette because hair hangs
free; antennae are attached, so they read by the light moving along them.

Watch `sequence.gif`, which plays 1, 2, 3, 4, 3, 4.
