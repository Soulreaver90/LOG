# Arena v4: what was measured, and where each number came from

Every number in the v4 brief, with its source, so the brief can be checked rather than trusted. All of it is
read from the base ROM or from the owner's save states beside the v3 ROM. Nothing here is inferred.

## The assets in this folder

| File | What it is |
|---|---|
| `arena_markup.png` | map 6,1 art, 1:1, 512x800, grid in MAP PIXEL coordinates. Thin line every 32 px, heavy labelled line every 128 px. One collision cell is 8x8 px, so a thin square is 4x4 cells |
| `arena_collision.png` | the same with the red tint, which marks cells that are ALREADY closed |
| `ground_clean_floor.png` | 64x40 of real floor from (200,560), in case a partial tile ever needs hand art |
| `ground_clean_floor_6x.png` | the same at 6x, for drawing |

The owner marked `arena_markup.png` and returned it with two red boxes. Those marks located both shadows in
one round, after four of my own crop searches had missed them.

## Fix 1: the fighters must not move

**Source: the owner's states 2 and 3, read directly.**

Method: scan WRAM for consecutive u32 pairs that are both multiples of 256 and whose `>> 8` values land
inside the map. An anchor is `{u32 x<<8, u32 y<<8}` at obj+0x158.

| State | What it holds |
|---|---|
| 2, the conversation just ended | **(244,504)** at object `0x02035078` and **(248,568)** at `0x020351ec` |
| 3, the fight has started | neither of those. It holds **(248,680)**, our `TRUNKS_SPOT` |

So the fight does not MOVE the conversation's actors. It destroys them and builds new ones 112 px lower.
That drop is what the owner sees.

`ending_fight.py` line 136 already recorded `(244,504)` from an older state set, so two independent sources
agree.

**Collision check at the new spots**, using the engine's own indexing
(`collision_test @0x08005D6C`: byte `cy*32 + (cx>>3)`, bit `cx&7` LSB first, set = OPEN, 8 px cells):

| Spot | Cells tested | Closed |
|---|---|---|
| Cell at (244,504) | 36, including his 56 px head clearance | **0** |
| Trunks at (248,568) | 36 | **0** |
| Trunks at (248,680), the current spot | 36 | 4, at y 688 |

The new spots are clear and the current one is not, so this also removes a stand against a wall.

## Fix 2: the glass door

**Source: map 6,1's collision frame `0x085F164C`, plus the owner's states 4 and 5.**

| Region | Cells | Open |
|---|---|---|
| the doorway, px (224,88)-(273,105) | 21 | **21** |
| 0x20 px deeper, px (224,56)-(273,88) | 35 | 21 |

State 4 sits at (246,94), in front of the door. State 5 sits at (246,72), inside it.

The doorway was never solid. In vanilla the warp to map 6,2 fires before the player crosses it. v3 zeroed
`layout +0x40` and `+0x44`, which killed every transition but left the geometry open, so the player now walks
into the building instead of warping out of it.

## Fix 3: the two shadows

**Source: BG2 rendered from the base ROM and read per pixel, every tile entry decoded.**

The Capsule Corp save point and the map post are sprites the map spawns. Only their SHADOWS are painted into
BG2. A cloned map that spawns neither shows a shadow with nothing casting it. That is why searching the
ground art for the logo itself returned nothing.

Shadow palette index **73**, RGB (144,200,248). Pale floor index **72**, RGB (208,232,248).

| Shadow | Pixels | Box | Tiles | Entries | BG2 blocks |
|---|---|---|---|---|---|
| save point | 270 | (246,344)-(274,359) | 10, px (240,344)-(279,359) | 483 to 492, each its own tile | 2 and 3 |
| dome | 602 | (420,694)-(474,739) | 18, px (416,688)-(479,743) | 510 to 520, `0x0C9C`, 155, and 55 on 5 tiles | 5 |

BG2 is layout `+0x1C`: blocks of 256x256 px, 2 across by 4 down, each block a 32x32 map of u16 entries with
the tile index in bits 0-9, flip X `0x400` and flip Y `0x800`. Block index is `(y//256)*2 + (x//256)`.

**No shadow tile is shared with art we keep**, so the removal is a tilemap ENTRY swap and needs no hand art.
Entry 55 appearing on 5 tiles is the one to check: it is probably a mostly clean tile catching a few shadow
pixels at its edge.

The map post also has **no collision at all**: 49 cells of 49 at (408,568)-(457,617) are open, so the player
walks through it.

## Not in scope

Trunks starting in base form instead of Super Saiyan. Reported by the owner on v3, not investigated, and
deliberately kept out of the v4 brief so no cause is guessed at.
