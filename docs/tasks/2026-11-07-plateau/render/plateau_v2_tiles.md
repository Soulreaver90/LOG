# Plateau v2: which tiles, and where they came from

No new pixel art. Every tile in v2 is already in the ROM.

## The donor map

All of it comes from **map 7,15**, the Vegeta against Android 19 field, through that map's own tile
index stream at layout `+0x48` and its chunk table at `+0x4C`. v2 keeps both, so a tile number means
on our map exactly what it means on 7,15.

## What each part uses

| Part of the map | Tiles | Taken from |
| --- | --- | --- |
| The open ground between the grass and the rock | `0x66`-`0x6E`, the 9 plain ground tiles | 405 aligned 3x3 blocks of 7,15's clean ground, each kept with the phase vanilla gave it |
| Ground detail: pebbles, cracks, scuff | 208 distinct entries | every non-plain ground cell of 7,15, one cell at a time |
| The grass the fight happens on | `0x57`-`0x65`, two rows of 8 | 7,15's grass motif, phase 2, sheared 4 tiles every 2 rows |
| The stone lip around the grass | 42 inside masks, 27 outside masks | 7,15's own lip autotile, keyed on the 8 neighbour pattern |
| Dirt specks in the grass | 10 distinct entries | measured: the entries 7,15 shows through its own holes, at its own rate of one in 21 |
| The border wall and the boulders | 12 donor rectangles, 18 to 63 cells each | 7,15's rock formations, copied whole |

## The border

The cliff and boulder ART is 7,15's. The continuous three-row band round the map is MY arrangement,
not a copy of any one vanilla border. Of the 57 vanilla maps at least 768 px on a side, 16 have a
fully closed border; 7,15 is one of them, and it was picked for its tiles, not its layout.
The LOOK reference for the band is map 14,3, the Cell Games arena.

## Numbers

- Map is 1280 x 1280 px. 17693 cells walkable, 7907 cells of rock.
- The player walks right up to the rock. 660 blocked cells face open ground, every one of them draws rock, and the camera can bring all 660 on screen.
- The grass plateau keeps its stone lip, so in v2 that lip is a step he walks over, not a stop.
- The open fighting square is 768 x 768 px, at px 192 to 959. Every fight spot sits inside it.
- 305 distinct tile entries over the two layers. v1 used 56.
- Commonest entry covers 5.6 percent. Vanilla floors run 4.5 to 6.0 percent.
- Camera clamp for layout `+0x08`: (1041, 1121), so the view reaches the whole map.
