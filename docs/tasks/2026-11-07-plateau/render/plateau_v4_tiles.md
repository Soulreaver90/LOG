# Plateau v4: the plateau top, its tiles, and how much room it gives

No new pixel art. Every tile is already in the ROM, read out of map 7,15 at build time through that
map's own tile index stream at layout `+0x48`, its chunk table at `+0x4C` and its animated tile group
at `+0x0C`/`+0x10`.

The render and the ROM come from the SAME code: `scripts\permanent\patches\plateau.py`. The render
script calls `generate()` and draws it; the patch calls `generate()` and writes it. They cannot drift.

## The concept

The arena is the TOP of a plateau. Its boundary is a drop, not a wall. The player sees grass, then a
stone lip, then lower ground far below. Beyond the drop: a cliff line under the rim, cliff groups in
the side areas, a rock cavern in the south east, and eight further plateau tops.

Nothing beyond the drop is walkable, so nothing out there can be a gameplay mistake.

## Is it big enough to fight in?

Measured on the vanilla maps where a boss fight actually happens
(`plateau_v4_arena_size.txt`, largest connected open region per map):

| Map | Open cells | Box | Largest open square |
| --- | --- | --- | --- |
| **Our plateau top** | **8613** | **904 x 848 px** | - |
| 14,3 Cell Games, Gohan against Cell | 4810 | 696 x 632 px | 264 px |
| 14,4 Cell Games, beam struggle | 4810 | 696 x 632 px | 264 px |
| 7,15 Vegeta against Android 19 | 2759 | 752 x 424 px | 128 px |
| 11,4 Android 17 | 1981 | 536 x 360 px | 200 px |
| 12,4 Perfect Cell | 1443 | 504 x 400 px | 128 px |
| 14,1 Cell Games ring | 1156 | 320 x 376 px | 144 px |
| 12,6 Perfect Cell | 1132 | 336 x 320 px | 192 px |
| 11,6 Android 17 rematch | 1171 | 544 x 296 px | 128 px |

**Verdict: ours is larger.** 1.8 times the open area of the biggest vanilla boss arena, and its box
is 208 px wider and 216 px taller.

## What each part uses

| Part of the map | Taken from map 7,15 |
| --- | --- |
| The grass on the top | the motif `0x57`-`0x65` and `0x37E`, phase 2, sheared 4 tiles every 2 rows |
| The lip at the drop, inside and out | 28 inside and 21 outside masks of 7,15's own lip autotile |
| The lower ground | 405 aligned 3x3 blocks of 7,15's clean ground, each with the phase vanilla gave it |
| Ground detail on the lower land | 208 distinct entries, one cell at a time |
| Ground patches on the top | whole rectangles of 7,15's ground, clipped to a grown and rounded outline |
| Cliffs, boulders, the cavern | 26 rock formations copied whole |

## The animated grass tile

Slot 2 of the grass motif is `0x037E`, and that is correct vanilla data. Its tile index is 894, past
the 633 tiles the static stream decodes, because map 7,15 carries one ANIMATED tile group. The clone
keeps that group, so the tile draws in game.

> Our tile reader decodes only the static stream, so the RENDER substitutes a neighbouring grass tile
> for `0x037E`. The ROM keeps `0x037E`. A render that did not substitute would show a false hole
> every 8 columns and 4 rows, which is what the v1 and v2 renders showed.

## The interior, measured

| Property | v4 | Vanilla patch family (4,50, 4,53, 4,55) |
| --- | --- | --- |
| Ground patch share of the top | 19.9 percent | 19.7 to 26.6 percent |
| Patch regions | 25 single, 13 of 2-4, 43 of 5-20, 34 of 21+ | 4,55: 13, 22, 83, 16 |
| Patch outlines | grown, then rounded by three majority passes | - |

## The three checks, re-run on v4

- Walkable cells touching the map border: **0**
- Closed cells facing open ground that draw nothing: **0**
- The drop face he can stop against: **100 percent of 334 cells** reachable by the camera
- The land beyond the drop: **48.0 percent of 6741 drawn cells** reachable
- Further plateau tops: **25.0 percent of 2096 cells** reachable
- Every fight spot envelope open: **True**

The camera model is the follow rule, actor box centre minus (120, 84), clamped by layout `+0x08`
(1041, 1121). Detail at the map edge is deliberately sparse, because he can never bring it on screen.
