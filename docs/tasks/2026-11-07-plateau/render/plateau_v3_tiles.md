# Plateau v3: which tiles, and where they came from

No new pixel art. Every tile is already in the ROM, read through map 7,15's own tile index stream at
layout `+0x48` and its chunk table at `+0x4C`.

The border, the cliffs, the boulders, the camera pair, the collision rule and the layer plan are v2
and did not change. Only the interior changed.

## What each part uses

| Part of the map | Tiles | Taken from |
| --- | --- | --- |
| The open ground between the grass and the rock | `0x66`-`0x6E`, the 9 plain ground tiles | 405 aligned 3x3 blocks of map 7,15's clean ground, each kept with the phase vanilla gave it |
| Ground detail: pebbles, cracks, scuff | 208 distinct entries | every non-plain ground cell of 7,15, one cell at a time |
| The grass | `0x57`-`0x65` and `0x37E`, two rows of 8 | 7,15's grass motif, phase 2, sheared 4 tiles every 2 rows |
| Ground patches in the grass | whole rectangles of 7,15's ground | each patch copies a real piece of 7,15's ground, clipped to a grown outline |
| The lip round the plateau and round each hill | 42 inside masks, 27 outside masks | 7,15's own lip autotile, keyed on the 8 neighbour pattern |
| The border wall and the boulders | 12 donor rectangles, 18 to 63 cells each | 7,15's rock formations, copied whole |

## Read this before you judge the v1 and v2 renders again

Slot 2 of the grass motif is `0x037E`, and that is **correct vanilla data**. All 18 of its cells on
map 7,15 sit at that exact slot, and the map reads `0x5F 0x60 0x37E 0x61 0x62` in a straight line at
ty 46, tx 74 to 78.

Its tile index is 894. Our reader decodes 633 tiles from map 7,15's static stream, so it cannot draw
894 and leaves the cell empty. The tile comes from the map's **animated tile group** instead: layout
`+0x0C` holds a count of 1 and `+0x10` points at `rom:0x5A1320`. It is animated grass.

> The polka-dot lattice in the v1 and v2 renders was one false hole every 8 columns and 4 rows, put
> there by our renderer. **It would not appear in the game.** The v3 render substitutes a neighbouring
> grass tile for it. The map data still carries `0x037E`.

The owner's other two complaints about v2 stand on their own: the field had no larger ground spots
and no hills.

## The interior, measured against vanilla

Measurement file: `scripts\one-time\2026-11-07-plateau\19_patch_shapes.txt`. It covers maps 14,1 to
14,4, 7,15 and 4,50 to 4,59, with two independent shapes per map.

Vanilla detail comes in two families. **Single-cell scatter**: map 7,15 has 312 of 324 regions single,
14,1 has 636 of 642, 14,2 has 532 of 536. **Patches**: map 4,50 has 46 single against 36 of 5 to 20
cells, 4,55 has 13 against 83, 4,53 has 25 against 13 plus 19 over 20 cells. v2 copied map 7,15, which
is the scatter family. v3 follows the patch family, which is what "larger ground spots" asks for.

| Property | v3 | Vanilla patch family | Whole reference set |
| --- | --- | --- | --- |
| Region sizes | 41 single, 21 of 2-4, 51 of 5-20, 36 of 21+ | 4,55: 13, 22, 83, 16. 4,50: 46, 7, 36, 6 | - |
| Median region | 6 cells | 2 to 5 cells | 1 to 5 cells |
| Largest region | 354 cells | 1551 to 1725 cells | 119 to 3056 cells |
| Detail share | 28 percent | 4,50 19.7, 4,55 24.3, 4,53 26.6 | 2.1 to 59.2 percent |
| Clark-Evans R | 1.20 | 0.75 to 0.93 | 0.57 to 1.83 |
| Ground types over 1 percent | 9 | 9 to 12 | 3 to 17 |
| Hills inside the field | 4 | - | - |

Two honest gaps. R of 1.20 means the patches are slightly MORE even than random, not clustered; the
cluster centres sit on a jittered grid, which is dispersed by construction. The detail share of 28
percent is above the patch family's 20 to 27, so the field is a little busier than 4,50.

## Numbers

- Map is 1280 x 1280 px. 17693 cells walkable, 7907 cells of rock. These are v2's and did not change.
- 309 distinct tile entries. Commonest entry covers 5.8 percent. Vanilla floors run 4.5 to 6.0.
- The open fighting square is 768 x 768 px, at px 192 to 959. Every fight spot envelope is open.
- 660 blocked cells face open ground, every one draws rock, and the camera reaches all 660.
- Camera clamp for layout `+0x08`: (1041, 1121), so the view reaches the whole map.
