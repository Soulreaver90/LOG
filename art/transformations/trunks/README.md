# Trunks: not drawn yet

The owner draws these next week. This folder holds what was measured so the drawing can start cold.

## Where it goes

`set:133` and `set:134` are the Super Trunks sets and **neither has an anim 9**, so a second
transformation drops into a free row, exactly as Vegeta's and Piccolo's do. The base sets `set:128`
and `set:132` each DO have one, and neither is touched.

| Set | anim 9 | Frame files |
| --- | --- | --- |
| 128 base | 4 frames, 32x32, same four in all 4 directions | `356324, 35643C, 356590, 3566E8` |
| 132 base | 4 frames, 32x32, same four in all 4 directions | `362D64, 362E70, 362FAC, 3630F4` |
| 133 super | none | |
| 134 super | none | |

Which of 133 and 134 the Z+ step plays from is NOT measured yet. It depends on which set the
appearance entry carries, and that is read at build time, not guessed here.

## What to draw

Four frames, 32x32, front view only. One front view covers all four directions.

The vanilla beat is in `vanilla-reference\`. `set132_powerup_strip.png` shows it: purple hair, a
purple and gold flash, then two gold frames that alternate. For a SECOND transformation the first
two frames start already gold, the way Vegeta's do, because he is Super Saiyan before it plays.

The last two frames carry the motion. Vegeta's swing 3 px at the apex and 0 at the brow, pivoting at
the scalp. Piccolo, who has no hair, pulses the shading instead.

## Export from Piskel

Piskel writes a magenta key `#F800F8` rather than an alpha channel, so the conversion needs
`--key F800F8`. Just say "Piskel" when sending frames.
