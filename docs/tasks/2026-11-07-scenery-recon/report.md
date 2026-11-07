# Scenery recon for plateau v6: the two reference areas, the breakable rocks, the rounded
# ground autotile and the rock vocabulary

Date 2026-11-07. Base ROM only, read-only. No map was rendered to a PNG, `map_view` was never run,
and the suite was not run. Scripts and their output: `scripts\one-time\2026-11-07-scenery-recon\`.

Every finding is labelled CONFIRMED, LIKELY or SPECULATIVE with the address or the file:line that
proves it.

---

## 1. Which maps are "East District 439"? CONFIRMED

**The brief's premise is half wrong, and the bible already held the answer.** Map entry `+0x0C` is
not a name POINTER, so the check that found no pointer there was right. It is a name INDEX into a
POINTER table at `rom:0xE2840`: word `+4i` points at the NUL-terminated name. Bible `B1136` and
`B1160` state this, and `scene_probe` already prints the field as "banner"
(`scripts\permanent\scene\scene_probe.py:62`, `BANNER_POOL = 0xE2840`).

`+0x0C` takes two forms, as `+0x24` music does: 313 maps hold a literal index and 14 hold a SCRIPT
that picks the index on a flag.

**Validation against the answers already known** (`name_maps.txt`), all five exact:

| Map | Wanted | Read |
| --- | --- | --- |
| 2,22 | Goku's Home | Goku's Home |
| 6,1 | Capsule Corporation | Capsule Corporation |
| 14,1 | The Cell Games Arena | The Cell Games Arena |
| 8,1 | Northern Mountains | Northern Mountains |
| 2,29 | East District 439 | East District 439 |

Maps 10,17 to 10,20 read "Gingertown" and 10,1 to 10,16, 10,22, 10,30 to 10,33 read "Outside
Gingertown", which is bible `B1137` exactly.

### East District 439: 36 maps, all in zone 2

35 by a literal index 203:

`2,2  2,3  2,4  2,5  2,6  2,7  2,8  2,9  2,26  2,27  2,28  2,29  2,30  2,31  2,32  2,33  2,34
2,35  2,36  2,37  2,38  2,39  2,40  2,41  2,42  2,43  2,44  2,45  2,46  2,47  2,48  2,49  2,50
2,51  2,52`

Plus **map 2,1** by the banner script `rom:0x3ED91E`: `test_flag(196) ; jz(3) ; push 221 ; return`
then `push 203 ; return`. The `jz` skips the 221 arm, so with flag 196 CLEAR the map is named
"East District 439" and with flag 196 SET it is named `***` (index 221, the blank banner `0xDD`).
Treat 2,1 as East District 439.

### Ginger Town: 25 maps, all in zone 10

- **Gingertown**, 4 maps: `10,17  10,18  10,19  10,20`
- **Outside Gingertown**, 21 maps: `10,1  10,2  10,3  10,4  10,5  10,6  10,7  10,8  10,9  10,10
  10,11  10,12  10,13  10,14  10,15  10,16  10,22  10,30  10,31  10,32  10,33`

Zone 10 also holds 10,21 and 10,23 to 10,29, which carry other names. See `name_maps.txt` for every
map in the game with its name.

---

## 2. The breakable rocks that hold powerups: a PROP plus an entry `+0x18` record. CONFIRMED

They are **neither BG tiles nor items in the `+0x14` item list**. One rock is two separate pieces of
map data, and both must be written to place one:

| Piece | Where | What it gives the rock |
| --- | --- | --- |
| A layout **PROP** | layout `+0x24` count, `+0x28` list, `+0x2C` sheet | the position, the 32x32 size and the pixels |
| A **break record** | map entry `+0x05` count, `+0x18` list | the break behaviour and the drop |

### The mechanism, read out of the handlers

1. `Map_Load` `sub_0800C390` walks the `+0x18` list at `loc_0800C47C`
   (`legacyofgoku2-disasm\build\code\code_0800c390.s`). For each pointer it runs the record's `+0x00`
   condition through `loc_08003F06`, and on a non-zero result calls `loc_0800F034`.
2. `sub_0800F034` (`code_0800f034.s`) calls
   `List_FirstMatch(list, kind = 6, arg = record[+0x04])`, then `sub_0800EEA8(0, record, match)`.
3. `List_FirstMatch @0x08006E0A` searches the LIVE object list for the first object whose `+0x24`
   method matches `(6, arg)`. So **record `+0x04` names an object already spawned**, and the match
   supplies the body.
4. `sub_0800EEA8` (`code_0800eea8.s`) stores the record at object `+0x24` and the match at `+0x28`,
   copies record `+0x05` and `+0x06` to object `+0x0C` and `+0x0D`, then reads the match's `+0x14`
   rect and its `+0x0E` tile to build the bounding box and the bitmap.

**The match is the layout prop. LIKELY, from a 348 of 348 correlation, not from a read of the
object's own `+0x24` method.** Measured over all 327 maps (`breakables.py`): **348 break records in
111 maps, and every single record's `+0x04` is a valid index into its own layout's prop list.** Zero
exceptions, and every prop a record names is 32x32 px at priority 40. To make this CONFIRMED, read
the `+0x24` query method of the prop object class.

### The record, 16 bytes

| Offset | Meaning |
| --- | --- |
| `+0x00` | condition script, or 0 for always |
| `+0x04` | the prop index this rock wears |
| `+0x05` | the DROP TIER, 1, 2 or 3 |
| `+0x06` | always 3 in all 348 records |
| `+0x08` | factory `@0x0800F9A3` (347 records) or `@0x0800F9C7` (1 record, map 1,1) |
| `+0x0C` | the break script |

### What it drops

The break script is a random draw that ends in `ext 92`. `ext 87` and `ext 92` share one handler
`@0x0800ABA4` (bible `B1028`); it pops the item id, checks a live count against 1024, and spawns a
dropped-item object. So `ext 92 N` = drop item N on the ground here.

Four distinct scripts, by tier:

| Script | Objects | Tier `+0x05` | Items it can drop |
| --- | --- | --- | --- |
| `rom:0x3ED894` | 102 | 1 | 11, 14 |
| `rom:0x3ED6CC` | 96 | 2 | 11, 12, 14, 15 |
| `rom:0x3EE6A8` | 104 | 3 | 11, 12, 13, 14, 15, 16 |
| `rom:0x3F27E4` | 8 | 1 | 11, 14 |

Items 11 to 16 are `HealthBonusSmall` to `EnergyBonusLarge` (bible `B1883`). Bible `B1883` also says
items 11 to 16 appear in no map pickup list; this is where they come from.

**No flag is set, so a broken rock comes back every time the map loads. LIKELY.** `rom:0x3ED894`
and `rom:0x3EE6A8` were decoded op by op and hold no `set_flag` (`ext 27`, the byte pair `02 1B`);
`rom:0x3ED6CC` and `rom:0x3F27E4` were read by the same byte scan, not op by op. 344 of the 348
records carry condition 0. The four records with a
condition are story barriers, not powerup rocks: map 2,7 `rom:0x3EE688` is the Vegeta barrier break
object of bible `B0625`, and maps 2,2, 2,32 and 3,7 carry the same shape.

### Collision

The static collision frame does NOT close the rock's cells. Measured on map 2,28: prop 0 at
(72,256)-(104,288) is 16 of 16 cells open and prop 2 at (120,248)-(152,280) is 13 of 16 open, while
plain grass at (300,300) is 6 of 16 open. **LIKELY**: the rock blocks at run time, from the bounding
box `sub_0800EEA8` builds, not from the frame.

### Map 7,15, the plateau's OWN source map, already carries 6 of these rocks

`breakables.txt`, records `rom:0x3FD500` to `rom:0x3FD550`: map 7,15 has 6 break objects wearing its
own 6 props, three at tier 2 (`rom:0x3ED6CC`, items 11, 12, 14, 15) and three at tier 3
(`rom:0x3EE6A8`, items 11 to 16), at (792,520), (112,360), (344,152), (112,520) and two more. Prop
tiles 0x00 and 0x20, priority 40, 32x32 px.

`patches\plateau.py` zeroes the layout `+0x24` prop count and `+0x28` prop list (lines 605 and 606)
but leaves `+0x2C` naming map 7,15's own prop SHEET `rom:0x504A2C`. **So the plateau already owns
the rock art.** Putting breakable rocks on the plateau is a prop list plus an entry `+0x18` list and
their two counts. It needs no new pixels and it spends none of the 261 BG tile slots, because a prop
is an OBJ sprite from the prop sheet, not a BG tile.

### The ruling the brief asked for

**The map editor may NOT place a breakable rock.** Its design is scenery only and it does not touch
the prop list, and a rock needs a prop AND a map entry `+0x18` record, neither of which is scenery.
A rock is also invisible to the editor's collision view, so an editor that only reads the collision
frame would place walkable ground where a rock stands. Breakable rocks belong to a patch module.


---

## 3. The rounded ground autotile. CONFIRMED

> **East District 439 has TWO ground tilesets, one per map VARIATION, and flag 68 picks between
> them** (bible `B0598`). Variation 1 is green grass with tan dirt. Variation 2 swaps the whole
> ground to an OLIVE tileset: map 2,1 var 2 bg3 is 9,776 of 16,384 cells olive, map 2,6 var 2 is
> 4,273 of 4,891, map 2,7 var 2 is 4,457 of 4,891, and variation 1 of all three is 0
> (`var2.txt`). **The owner's screenshot is the OLIVE one**: its dominant colour (156,156,0) is
> palette index 35, which no variation 1 ground tile holds. Both autotiles are below. **Use the
> variation 1 one**, and section 3's seam proof says why.

**Source: map 2,1 bg3, East District 439, variation 1.** Its ground layer is 160x160 tiles and draws 6,856 grass
cells, 489 dirt cells and 519 rim cells, the largest clean sample in either reference area
(`ground_survey.txt`). Maps 2,6, 2,7 and 2,26 to 2,33 carry the same vocabulary.

### How the two materials separate

On this tileset green dominance is an exact separator: every grass colour has `g >= r` and every
dirt colour has `r > g`. A tile with only grass colours is GRASS, with only dirt colours is DIRT,
and with both is RIM. No threshold tuning is needed.

| Role | Tiles on map 2,1 | Colours |
| --- | --- | --- |
| grass weave | 73 to 87, plus the animated group 893 to 895 | 81 (123,148,0), 80 (140,181,41), 34 (189,189,0), 219 (206,255,66) |
| dirt body | 90 to 95, 97, 98, 99 | 92 (206,132,82), 91 (222,165,132), 93 (189,107,41), 94 (140,82,41) |
| the rim | 88, 89, 96, 239 | both families |

### The mask table

The mask is the 8 neighbour membership of the blob (dirt body plus rim), bit order
`(-1,-1) (0,-1) (1,-1) (-1,0) (1,0) (-1,1) (0,1) (1,1)`, which is `patches\plateau.py NEIGHBOURS`.
A set bit means that neighbour is dirt.

**The whole autotile is FOUR tiles plus the tilemap flip bits.**

| Mask group | Which side | Tile and flip |
| --- | --- | --- |
| `0xF8` (north three clear) | top edge | 89, and 89 flip H; 88 is the variant |
| `0x1F` (south three clear) | bottom edge | 89 flip V, 88 flip V |
| `0xD6` (west three clear) | left edge | 96, 96 flip V |
| `0x6B` (east three clear) | right edge | 96 flip H, 96 flip HV |
| `0xD0`, `0xF4`, `0xF0` | top left corner | 239 |
| `0x68`, `0x69`, `0xE8`, `0xE9` | top right corner | 239 flip H |
| `0x16`, `0x17`, `0x96`, `0x97` | bottom left corner | 239 flip V |
| `0x0B`, `0x0F`, `0x2B`, `0x2F` | bottom right corner | 239 flip HV |
| `0xFF` | interior | the dirt body weave, 90 to 99 |

The full table with cell counts is in `autotile.txt`. Vanilla also draws tiles 203 to 239 on this
layer, each about 23 times; those are a repeated decal, not part of the autotile.

### What the tiles are, as stream pairs

The `(chunk, tile)` pair is what a new layout's `+0x48` stream would name.

| Tile | Pair | Role |
| --- | --- | --- |
| 88 | (1, 85) | horizontal edge, variant A |
| 89 | (1, 92) | horizontal edge, variant B |
| 96 | (1, 104) | vertical edge |
| 239 | (4, 194) | corner, all four flips |
| 90 to 99 | (1, 96) to (1, 108) | the dirt body weave |

Map 2,1's layout names the shared chunk table `rom:0x4DF574`, the same table map 7,15 names, so no
chunk table change is needed.

### THE TILE COST: 4 NEW TILES

Measured against map 7,15, the plateau's tile source, by PIXELS with all four flips, because a BG
tilemap entry carries the flip bits `0x400` and `0x800` (`map_view.layer`). Script `cost.py`.

| | |
| --- | --- |
| Map 7,15 loads | 633 static stream tiles plus 1 animated group of 2 tiles = 635 slots |
| The loader's budget | 896 slots (`scene_probe.TILE_BUDGET`, the 0x700 byte decode buffer) |
| Headroom | **261 slots** |
| The dirt body, tiles 90 to 99 | **already in 7,15, free.** The plateau owns this dirt already |
| The rim, tiles 88, 89, 96, 239 | **4 NEW slots** |

**Pulling the rounded ground autotile in costs 4 tiles of the 261 spare**, about 1.5 per cent of the
headroom.

### No colour seam. CONFIRMED

A rim tile bakes its grass half into its own pixels, so a borrowed rim only works when that grass
half is the grass it will sit next to. Measured (`seam.py`):

| | Palette indices |
| --- | --- |
| Map 7,15 grass (slots 0x57 to 0x65 and 894) | 81 (123,148,0), 80 (140,181,41), 34 (189,189,0), 219 (206,255,66) |
| Map 7,15 plain ground (slots 0x66 to 0x6E) | 91 (222,165,132), 92 (206,132,82), 22, 210, 93, 23, 99 |
| Rim tiles 88, 89, 96, 239, grass half | 81, 80, 34, 219 |
| Rim tiles 88, 89, 96, 239, dirt half | 92, 91, 93, 94, 210 |

**The rim's grass half is map 7,15's grass palette exactly, and its dirt half is map 7,15's own
ground palette.** The autotile drops into the plateau with no colour step on either side.

### The OLIVE autotile, for comparison. CONFIRMED

Variation 2's rim is the same shape and the same mask table, in chunk 10 (`autotile_olive.txt`):

| Role | Chunk pair | On map 2,6 var 2 | On map 2,1 var 2 |
| --- | --- | --- | --- |
| corner, all four flips | (10, 131) | tile 230 | tile 845 |
| horizontal edge | (10, 132) | tile 231 | tile 846 |
| vertical edge | (10, 135) | tile 233 | tile 849 |
| variants | (10, 128) (10, 129) (10, 130) (10, 134) (10, 105) | 227, 228, 229, 232, 206 | 842, 843, 844, 848, 819 |

Its rim is 8 new tiles, all new, **and it would seam.** Tile 230's grass half is indices 35
(156,156,0) and 236 (231,189,66), neither of which map 7,15 holds. Taking the olive look means
taking its grass weave and its dirt body as well, which is a far larger bill than 8 tiles, and the
plateau would then need all its grass replaced. That is a design decision for the owner, not a
finishing touch.

---

## 4. The loose boulders and the rock outcrops

Method (`formations.py`, `rocks.py`): on each layer the few entries that cover 88 per cent of the
drawn cells are the FIELD; everything else is a DECAL. Decal cells are flood filled 8 ways, each
blob is cut out as an entry grid, and identical grids are grouped, so a boulder drawn 13 times
counts once. Cost is against map 7,15 by pixels with flips, as above. 105 rock or wood formations
came out of 13 maps; the vocabulary below is the part worth copying.

### Loose boulders, the thing that breaks up plain grass with no hard edge

| Formation | Source | Size | Cells | Tiles | NEW | Uses in vanilla |
| --- | --- | --- | --- | --- | --- | --- |
| **loose boulder, small** | 2,32 bg3 (69,50) | 2x2 tiles, 16x16 px | 3 | 299, 308, 309 (chunk 23) | 3 | 13 |
| **loose boulder, tan** | 2,32 bg1 (18,2) | 2x2 tiles, 16x16 px | 3 | 335, 336, 345 (chunk 24) | 3 | 6 |
| **boulder, upright** | 2,50 bg1 (2,10) | 2x3 tiles, 16x24 px | 4 | 50, 69, 81, 82 (chunks 24, 25) | 4 | 4 |
| **boulder, upright mirrored** | 2,50 bg1 (46,10) | 2x3 tiles, 16x24 px | 4 | 49, 76, 85, 86 (chunks 24, 25) | 4 | 3 |
| **rock shelf, low** | 10,1 bg3 (40,50) | 9x1 tiles, 72x8 px | 9 | 376, 377, 378 (chunk 40) | 3 | 2 |

The two 2x2 boulders are the cheapest scenery in the game, 3 tiles each, and vanilla scatters the
first one 13 times across one map. **CONFIRMED.**

### Rock outcrops

| Formation | Source | Size | Cells | Distinct tiles | NEW |
| --- | --- | --- | --- | --- | --- |
| **tall outcrop, the owner's reference shape** | 2,32 bg3 (94,38) | 13x18 tiles, 104x144 px | 136 | 13 (61 to 69, 250 to 253; chunks 1, 10) | **4** |
| **diagonal ridge** | 2,28 bg3 (19,26) | 13x13 tiles, 104x104 px | 54 | 15 (1 to 9, 161 to 164, 894, 895; chunks 1, 10) | 6 |
| **round outcrop** | 10,31 bg3 (10,23) | 8x8 tiles, 64x64 px | 43 | 13 (19 to 30, 166; chunks 1, 4) | 4 |
| **long ridge** | 10,1 bg3 (78,65) | 9x14 tiles, 72x112 px | 78 | 26 (chunks 0, 8) | 12 |
| **rock band, wide** | 2,1 bg3 (130,47) | 22x9 tiles, 176x72 px | 75 | 15 (88 to 99, 239, 241, 243, 894; chunks 1, 4) | 7 |

The **tall outcrop at 2,32 bg3 (94,38)** matches the brief's words for the second reference,
"a tall brown rock outcrop running vertically through grass". **I did not see that image, so
this is a match to the TEXT, not to a picture.** It is a narrow vertical ridge that widens and
runs down and to the right, 104 px wide and 144 px tall, and it costs **4 new tiles**, because
9 of its 13 tiles are chunk 1 tiles map 7,15 already loads. Its occupancy, cell by cell:

```
##...........
###..........
.####........
.####........
.####........
..####.......
..#####......
..#####......
..######.###.
#############
#############
#############
######.##.##.
#########.###
..###########
...##########
....########.
.....######..
```

### Trees and bushes

| Formation | Source | Size | Cells | Tiles | NEW | Uses |
| --- | --- | --- | --- | --- | --- | --- |
| **tree trunk, bare** | 2,27 bg3 (57,65) | 2x4 tiles, 16x32 px | 8 | 270, 271, 274, 275, 359, 360 (chunk 23) | 6 | 2 |
| **tree, large canopy** | 2,1 bg1 (96,68) | 9x14 tiles, 72x112 px | 72 | 72 | 72 | 5 |
| **tree, medium** | 2,7 bg1 (33,11) | 8x5 tiles, 64x40 px | 12 | 12 | 12 | 3 |
| **bush row** | 2,1 bg1 (39,33) | 8x2 tiles, 64x16 px | 9 | 9 | 9 | 17 |
| **bush, dark** | 2,1 bg1 (118,23) | 7x2 tiles, 56x16 px | 8 | 8 | 8 | 21 |

**Trees are the expensive end.** A tree lives on BG1, an overlay layer, and none of its tiles are in
map 7,15. The large canopy alone is 72 new tiles, 28 per cent of the whole headroom. The trunk is
cheap at 6 tiles, but a trunk with no canopy only reads at the frame edge, which is where the
owner's reference puts them.

### A budget that fits

| Take | NEW tiles |
| --- | --- |
| the rounded ground autotile | 4 |
| the tall outcrop, 2,32 | 4 |
| the round outcrop, 10,31 | 4 |
| loose boulder small, scattered as often as wanted | 3 |
| loose boulder tan | 3 |
| boulder upright, both mirrors | 8 |
| rock shelf low | 3 |
| tree trunk, bare | 6 |
| **total** | **35 of the 261 spare** |

The union is a little smaller than the sum where two formations share a tile, so 35 is a safe upper
bound. A scattered boulder costs nothing extra per copy: one tile set, any number of placements.

---

## What I could NOT prove

1. **The owner's screenshot is narrowed to East District 439 variation 2, not pinned to one map.
   LIKELY.** Its dominant colour (156,156,0) is palette index 35, the olive grass, and variation 2
   of maps 2,1, 2,5, 2,6 and 2,7 is the only East District ground that draws it. The best positional
   placement over every zone 2, zone 8 and zone 10 variation is **145 of 378 blocks on map 2,6
   variation 2** (`locate_all.txt`, `locate8.txt`), ahead of 124 on 2,32 var 1 and 118 on 8,41. 320
   of the 378 blocks are tiles some map loads, but tile-set membership cannot locate a shot, because
   the 168 chunk frames are a global pool. The residual miss is probably the animated grass group,
   whose frame my reader does not pick. Say the word and I will walk every group frame.
   Two notes on that shot for anyone who reads it again: the emulator converts 5 bit colour as
   `(i << 3) | (i >> 2)`, not `i << 3`, and the crop is 5x with one column of the first native pixel
   missing.
2. **Only ONE owner reference image is on disk**, `docs\tasks\2026-11-07-plateau\owner-refs\ref-rounded-ground-and-boulder.png`,
   plus the markup `owner-markup-plateau-top.png`. The spec names `owner-ref-rounded-ground.png` and
   the brief describes a second "rocks" screenshot; neither file is anywhere under the docs tree. So
   everything I say about the second reference comes from the brief's words, not from a picture.
   Drop that image in and I will match it the same way.
3. **Whether a breakable rock blocks the player. LIKELY, not CONFIRMED.** The static collision frame
   leaves the rock cells open, and `sub_0800EEA8` builds a bounding box, so any block is a run time
   one. Proving it needs a play test or a state dump, not a ROM read.
4. **Which prop sheet frame holds which rock size.** The prop `+0x0E` tile is 0x00, 0x20 or 0x40 in
   the ordinary zone 2 maps and tracks the drop tier, but map 2,1 uses 0xE8 for all six of its
   rocks. I did not decode the prop sheet itself.
5. **The formation inventory is shape-scoped.** It finds a formation only where that formation's
   tiles fall outside the 88 per cent field of its own layer. A rock drawn entirely in field tiles,
   or one split across two layers, would not appear. So: 105 formations reachable by this shape, not
   "all the formations".
6. **No picture was made.** Every shape here is read from entries and pixels, never from a render,
   because the brief forbids rendering while `map_view` is mid-fix.
