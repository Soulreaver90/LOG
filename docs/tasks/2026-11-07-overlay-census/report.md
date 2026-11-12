# Overlay and parallax layer census, 2026-11-07

Mine, not an agent's. Measured on the base USA ROM while answering the owner's question about whether the
rain look can go on any map. It extends the `RAIN` study of 2026-11-05 rather than repeating it.

## Why it was run

The owner saw the arena rendered with its rain and asked "is it an overlay? can this be applied to any
map?", then read Cell Games' own layer as a wind gust effect. Both questions are about the population, and
the `RAIN` study answered them for the 12 rain maps only.

## The correction I had to make to myself

I first told him "30 of 327 maps carry a BG0 overlay" and treated them as one thing. **That was wrong, and
the bible already knew better.** Row `B1156` separates the records by width and height, and row `B1158`
calls map 14,3's layer "scrolling cloud, not rain" and records it as map sized.

Measured directly, BG0 slot, variation 1:

| map | record | w | h | shape |
|---|---|---|---|---|
| 6,1 | `0x085F02CC` | 0 | 0 | wrapping 256x256 overlay |
| 1,2 | `0x086A9800` | 0 | 0 | wrapping 256x256 overlay |
| 14,3 | `0x084E3178` | 0x400 | 0x400 | map-sized parallax layer |
| 7,21 | `0x08592638` | 0x400 | 0x400 | map-sized parallax layer |
| 13,1 | `0x084F1430` | 0x400 | 0x400 | map-sized parallax layer |
| 1,7 | `0x086A65CC` | 0x400 | 0x400 | map-sized parallax layer |

So one factory, `0x08004FCD`, serves two different layer shapes. The blend is the same for both. A
transplant must match the shape, not only copy the pattern.

## The catch: an open bible disagreement is now settled

Row `B1158` records a disagreement it could not close: the `BMS` row gives map 14,3 EVA 12 and EVB 9,
while the `RAIN` row reads byte +2 as 0x09 and byte +3 as 0x0C and so gives EVA 9 and EVB 12.

My census read those bytes independently, as part of a sweep of all 327 map entries rather than a look at
one map, and got **EVA 9, EVB 12**. That is a third reading, from a different script, agreeing with the
`RAIN` row. **The `BMS` row is the wrong one.**

## The velocity families

Scroll pair read as 8.8 fixed point, px per frame, over every map whose BG0 is class `0x08004FCD`:

| family | dx | dy | maps | dials |
|---|---|---|---|---|
| rain (overlay shape) | +5.00 | **-46.66** | 1,2 · 1,5 · 6,1 · 8,19 to 8,26 | various |
| rain, slower | +5.00 | -33.33 | 8,15 | 11 / 14 |
| **gust (parallax shape)** | **-25.00** | -2.00 | 7,21 to 7,26 · **14,3** | **9 / 12 on all seven** |
| cloud (parallax shape) | -2.33 | -14.66 | 13,1 to 13,10 | 16 / 16, blend OFF on 9 of 10 |

Map 14,3 is not merely similar to the 7,2x maps. It is identical in all four numbers and in both dials,
which is what makes the owner's "wind gust" reading a family claim rather than an impression of one map.

Map 13,8 is the single exception in the 13,x block: same pattern, same velocity, blend ON where its nine
neighbours have it off.

## Pattern pointers are shared between maps already

Row `B1156` says the patterns of 6,1, 1,2 and 8,22 "render identical", which is an image comparison. The
pointers tell a stronger story: some maps share the same pattern address outright.

- 8,19 and 8,22 both name `0x08574CB8`
- 8,24 and 8,25 both name `0x08570198`
- all ten of 13,1 to 13,10 name `0x084E8C60`

So reusing one pattern across maps is something vanilla already does, in three separate places. That
removes the "are overlay tilemaps tied to one map" question I had raised as unproven.

## Map 1,7 carries one

The map the game-over routine loads, `rom:0x3B6104` loads map 1,7 at (112,144), carries a parallax layer
with the blend switched off. Worth knowing before the custom game-over card is built on that map.

## What this does NOT establish

- I did not read the tick that consumes dx and dy, so "px per frame" stays the `RAIN` study's L reading of
  the 8.8 unit, not my own measurement.
- Naming the -25.00 family a "wind gust" is the owner's reading and remains L. What is C is that all seven
  maps share one velocity and one pair of dials.
- I swept the BG0 slot and variation 1 only. Row `B1156` counts 47 records of this class across every slot
  and variation, so a layer in another slot would not appear in my numbers.
- My borrowed-rain picture of Cell Games tiled a 256x256 pattern over a map whose real layer is map sized.
  It is a picture of an idea, not a preview of a build.

## Tool

`scripts\one-time\2026-11-07-arena-rain\render_with_rain.py` renders a map with its BG0 layer composited
and the real blend applied, in 5-bit, the GBA's own depth. `--pattern Z,A` borrows another map's layer and
dials. It is read only and never writes to a ROM.
