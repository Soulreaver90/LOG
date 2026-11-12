# Plateau v6: the fight enclosure

The owner approved this direction on 2026-11-07: "yes shrink it and fix the map. SHOW it to me
before building the next rom."

v5 carries the v4 arena unchanged, verified byte for byte: same art render hash, same collision
hash, 8,613 open cells. Only Gohan changed. So v6 is the first arena change since v4.

## What is wrong with v4

Measured, not impressions.

| Fault | Evidence |
| --- | --- |
| The enclosure is far too big | 8,613 open cells, largest clear square 584 px. Cell Games, vanilla's biggest boss floor, is 4,810 cells and 264 px. Ours is 2.2 times as wide. |
| The fight floor is littered with hard-edged rectangles | Ground patches are 19.9 percent of the top, placed as whole rectangles clipped to an outline, with stepped corners and no edge tiles. |
| The drop does not read as a drop | The lip is drawn, but grass meets a flat tan rocky band. Nothing says height, so the player walks at open-looking ground and stops. |

A fourth fault was in our RENDERER, not the map: 509 cells naming the animated grass slot drew as
dirt. That is being fixed separately before any v6 picture is shown.

## The owner's markup

`docs\tasks\2026-11-07-plateau\owner-markup-plateau-top.png`, in his words:

> The middle area is the constraint area, remove the blocking patches (colored green). The orange
> color is where the rock edges will be (collision) and the yellow is the clif edges. So cell and
> trunks will be boxed in on a hill, surrounded by other hills and a rocky cavern below.

Reading the three colours:

- **Green blobs** sit on the dirt patches of the fight floor. They mark what to delete.
- **Orange** is a closed loop around the central grass: the rock edge, and it blocks.
- **Yellow** sits outside the orange: the cliff edge, the drop itself.

So the boundary has two layers, inner rock then outer cliff, and the floor inside is clean.

## Copy vanilla, do not generate

The owner's ruling, 2026-11-07: "just reference easter district or ginger town please. Stop trying
to create garbage from scratch when vanilla has so many great references. The arena we made is
still great but the finishing touches we can add will turn it from passable to great."

Two consequences, and they outrank anything below that disagrees.

1. **No procedural scenery.** v4 placed patches by growing an outline and rounding it with majority
   passes. That is what produced the rectangles. Lift whole formations out of vanilla maps instead,
   tiles and arrangement together, the way v4 already did for its 26 rock formations.
2. **The arena is not torn down.** He calls it "still great" and wants finishing touches. Shrink the
   enclosure, which he approved, and dress it. Do not restart the design.

**The two reference areas, resolved in the ROM:**

| His name | The ROM's name | Where |
| --- | --- | --- |
| Easter district | **East District 439**, at `rom:0xE3CE0` | zone unresolved, find it |
| Ginger town | **Gingertown** `rom:0xE3D16`, **Outside Gingertown** `rom:0xE3E32` | zone 10. Maps 10,17 to 10,20 are Gingertown, and 10,1 to 10,16, 10,22, 10,30 to 10,33 are Outside Gingertown (bible `B1137`) |

Trap on the name lookup, bible `B1498`: the run of names at `rom:0xE2B78` is an ALPHABETICAL string
pool, not a per-map table. Indexing it directly returns names that look right and are wrong. Solve
the pool start against maps whose names are already known, such as map 2,22 Goku's Home.

Map entry `+0x0C` is NOT a name pointer. I checked: no entry in zones 1 to 15 holds a ROM address
there that resolves to one of these strings.

## The target

| Property | v4 | v6 target |
| --- | --- | --- |
| Open cells, largest connected region | 8,613 | 4,500 to 5,500 |
| Largest clear square | 584 px | 280 to 340 px |
| Ground patches on the fight floor | 19.9 percent | none |
| Boundary | one lip band | rock edge, then cliff edge |

Cell Games is the floor, not the ceiling: do not go below 4,500 cells. The owner has not fought
here yet and said "if its too tight, we can expand the size."

## Rules

1. **No new pixel art.** Every tile comes from the ROM, as v4 did.
2. **The fight floor gets ROUNDED ground, not rectangles.** The owner sent a reference screenshot
   on 2026-11-07 (`docs\tasks\2026-11-07-plateau\owner-ref-rounded-ground.png`): dirt winds through
   grass with soft curved edges, drawn with a proper autotile. v4's patches were hard rectangles
   with stepped corners and no edge tiles, which is the fault he keeps naming.
   His words: "there are these ground titles that are rounded".

   Note the machinery already exists in our own code. The v4 lip used "28 inside and 21 outside
   masks of 7,15's own lip autotile". The floor patches did not use it. Use an autotile for the
   floor too, or take the one from his reference map.

   No single-cell specks either way.
3. **Breakable rocks that hold powerups.** The owner asked for these by name: "rocks with
   powerups". Unresolved: whether they are tiles, layout props at `+0x24`, or map ITEMS like an
   NPC. That decides who places them and whether the map editor may ever touch them, since the
   editor's design is scenery only. Answer it before placing any.
4. **Rock outcrops and loose boulders.** Second reference, sent 2026-11-07, one word: "rocks". A
   forest map: a tall brown rock outcrop running vertically through grass, loose boulders of two
   or three sizes scattered on the grass around it, tree trunks at the frame edges, and a dropped
   item sprite beside the outcrop. Kid Gohan in the purple gi fights an orange enemy there.

   This is the scenery vocabulary for the surround, and the loose boulders are what break up plain
   grass without a single hard edge. Find that map, it is not 7,15.
3. **The rock edge blocks and looks like it blocks.** A player walking into it must see why.
4. **The cliff edge is outside the rock edge** and reads as a drop.
5. **Beyond the drop:** lower rocky ground, a cavern, further hills. None of it walkable.
6. **No walkable cell touches the map border.**
7. **No closed cell that faces open ground draws nothing.**
8. The recovered space goes to the surround, which the markup asks for and v4 had no room for.

## Proof before the owner sees it

A picture rendered from the module's `generate()` is NOT proof. That is intent, and the encode step
is where v4's faults became visible. Encode to a scratch ROM, render THAT with `map_view`, and show
the owner the ROM render plus the collision overlay.

The scratch ROM is for rendering only. Do not place a build in `builds\` until the owner approves
the picture.
