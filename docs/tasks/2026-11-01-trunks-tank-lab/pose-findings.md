# Side walk: what the sprite itself states about the pose

Measured 2026-11-01 from the tank frames. Pixel measurements only. No skeleton was used to produce any
number here, so none of it can be an echo of my own joint placements.

## The lit boot pixel names the same leg across frames

Palette index `25` is the boot's lit top. It appears on exactly one boot per frame.

| frame | left boot | right boot | lit at columns | lit foot |
|-------|-----------|------------|----------------|-----------|
| idle  | one merged cluster, x6.7 | | 8 | x8 |
| walk0 | x2.7, 14 px | x12.2, 14 px | 12, 13 | screen RIGHT |
| walk1 | x5.2, 9 px | x10.8, 14 px | 10, 11 | screen RIGHT |
| walk2 | x2.0, 15 px | x11.6, 10 px | 1, 2, 3 | screen LEFT |
| walk3 | one merged cluster, x9.3 | | 9 | about x9, inferred |

**Two independent cues agree.** The lit boot and the larger boot cluster pick the same foot in walk1
(right, 14 px against 9 px) and in walk2 (left, 15 px against 10 px). Cluster size is a separate
measurement from the highlight, so this is not one cue counted twice.

**The lit foot therefore swaps sides between walk1 and walk2.** That is the sprite stating "one leg after
the other". I had missed it because I read foot POSITIONS and never looked for a per-frame identity tag.

**Cycle order 0, 1, 2, 3 is confirmed by RE-BIBLE TNK2, not by the lit foot.** The lit foot runs 12.2, 10.8, 2.0, 9.3. The jump from 10.8 to 2.0
is the swing. The run 2.0, 9.3, 12.2 is the planted foot drifting back under the body.

**Check on the idle.** The idle's lit boot is at x8, which is its screen-right leg. That leg also has the
lower sole, y30 against y28. The two cues agree on a frame nobody was arguing about.

## The torso centre moves

Span and midpoint of the non-background pixels, rows 17 to 19. The span includes the arms, so only the
midpoint is worth reading.

| frame | y17 mid | y18 mid | y19 mid |
|-------|---------|---------|---------|
| idle  | 7.5 | 7.5 | 7.5 |
| walk0 | 9.0 | 9.0 | 8.5 |
| walk1 | 7.0 | 7.5 | 7.5 |
| walk2 | 8.0 | 8.0 | 7.5 |
| walk3 | 7.0 | 7.0 | 7.5 |

The body centre swings about 2 px, from 7.0 to 9.0, and the two extremes are walk3 and walk0.

## The lit pixel is NOT a depth tag

It is on the FAR leg in walk0 and on the NEAR leg in the idle. Proof for walk0: his forward hand is on the
screen left, from the shoulder at x5-6 y19 down to x0-4 y20-23. The forward foot, x3.8, is his orange leg
from `hip_r`. Forward arm and forward leg are on opposite sides, which is a normal contralateral gait, and
only his crossing produces it. The idle's near side is the screen right, so the orange leg is near and the
lit foot at x12.5 is far.

So the lit pixel means **the same leg**, and nothing about depth. That is enough to alternate the cycle and
not enough to colour it by depth.

## Open, and NOT resolved here

The near leg's hip is on the screen LEFT in his walk 0 drawing, but on the screen RIGHT in his idle. A
real body cannot swap which hip owns the near leg. Either one of the two is mis-assigned, or the artist
does not keep a consistent hip to leg mapping in a cheated view and the hips are decorative. Do not pick
one and build on it.
