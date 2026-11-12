# Where does the arena's exit come from? Measured 2026-11-06, controller

The owner confirmed by play test that leaving the arena **fades the screen and shows a new place
name**, so it is a real map load, not a walk to a far corner of one map.

## What I measured

I tested every word of the map entry and every word of the layout struct against one question, over
all 327 vanilla maps: is this field non zero exactly when the map has regions? Script:
`scratch\probe_find_warp_field.py`. Region count is an imperfect proxy for "has exits", because a
region can be a save point or a world map spot, but the ranking still finds any field that tracks it.

| field | non zero on the 179 WITH regions | non zero on the 148 WITHOUT | separation |
|---|---|---|---|
| **`entry +0x10`, the region list** | **179** | **0** | **1.000** |
| `layout +0x24` | 137 | 57 | 0.380 |
| `layout +0x28` | 137 | 57 | 0.380 |
| `layout +0x2c` | 137 | 57 | 0.380 |
| `entry +0x20`, markers | 20 | 0 | 0.112 |

**`entry +0x10` is the only perfect separator.** It is non zero on every single map that has regions
and zero on every single map that does not. So the region list really is THE carrier of exits, and the
bible row is right.

**The arena's `entry +0x10` is 0.** I read that from the built v2 ROM myself, along with region count
0, enter script 0, leave script 0, and the swap, pickup and marker lists all 0.

**No layout field separates.** The best is 0.380, and it is shared by three ADJACENT fields
(`+0x24`, `+0x28`, `+0x2c`), which is the signature of an art or tile group, not a door table. My
earlier guess of `layout +0x10` is dead: 110 of the 148 region-free maps carry it.

## What that leaves

The warp is **not** in the map entry and **not** inherited through the layout copy. So it comes from
somewhere neither place reaches. Candidates, none measured yet:

1. **The pause menu's travel or world map.** LIKELY. It is always available, it is not map data, and
   it would show exactly the fade plus place name the owner describes. It would also explain "to west
   city", which is a travel destination rather than a neighbouring room.
2. **The scene VM.** Record F ends at index 26 (END) and hands control over, but the ending scene's
   other records may still be reachable.
3. **A save point or world map region reached some other way.**

Candidate 1 changes the shape of the fix completely: it would not be a map-data edit at all, but
suppressing travel while the fight is live.

## The question that separates them

Whether the owner opened a menu, or walked into it. That is one question for him and I have not asked
it yet, because he is making save states.

## Why the earlier claim was wrong

I told him twice that region count 0 means no exits. The data above says the region list IS the exit
carrier and the arena has none, so the claim was right about the DATA and wrong about the WORLD: it
assumed map data is the only way to change maps. His play test proved otherwise, and a measurement
over 327 maps cannot see a mechanism that does not live in those maps.

---

# ANSWERED, same day: the warps live in the LAYOUT

Every candidate above was wrong, including the menu. The owner's three save states settled it and a
direct search found the record.

## The current map word

`0x03002080`, zone byte then area byte. Found by difference across his three states on arena v1, and
it is the ONLY byte pair in IWRAM or WRAM that holds (6,100) in state 3 and changes in the others.

| state | current map |
|---|---|
| 3, the start of the fight | 6,100, the arena |
| 4, outside the arena | **4,6** |
| 5, reentry | **6,1**, the real Capsule Corp, NOT the arena |

That is the whole breakage: he returns to 6,1, so the arena, the fight and Cell are all gone.

## The carrier

`layout +0x40` is the warp COUNT and `layout +0x44` is the warp LIST. Each word of the list names a
warp item whose first word is a factory, `0x0800C233` or `0x0800D9C3`, with `{dir, zone, area, var,
x, y}` inline at `+0x10`.

Found directly: 675 aligned words name a factory, 7 of those records name destination 4,6, and map
6,1 reaches one of them, `0x085F2048`, through `layout +0x44` -> `0x085F2090` word 0.

Verified over the population, not on one map:

```
layouts where EVERY word of the +0x44 list is a warp factory record : 283
layouts where it is not, or the count and list disagree             :   0
layouts with no warp list at all                                    :  44
283 + 44 = 327, the whole table
```

| map | +0x40 | destinations |
|---|---|---|
| 6,1 Capsule Corp | 3 | **4,6**, 6,21, **6,2** |
| 6,2 inside | 5 | 6,4, 6,1, 6,4, 6,3, 6,8 |
| 4,6 West City | 3 | **6,1**, 4,4, 4,5 |
| 14,3 Cell Games arena | **0** | none |
| 14,4 | **0** | none |

4,6 is West City and 6,2 is the inside of Capsule Corp, which are the two places the owner named. The
game's own arena carries zero warps, which is the pattern to copy.

## Why my survey missed it

I ranked fields by how well they separate maps WITH regions from maps without. Warps do not track
region count, so the right field scored no better than art. The proxy was wrong, not the method. The
fix was a direct search for the destination bytes, which needed no proxy at all.

## The fix

Zero `+0x40` and `+0x44` in the arena's layout copy. Nothing else changes: every tile, palette and art
pointer stays, and `+0x34` goes back to map 6,1's own collision frame so the whole area is walkable.
Bible rows merged under tag `WRP`.
