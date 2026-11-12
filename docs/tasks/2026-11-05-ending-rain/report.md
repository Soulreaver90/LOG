# Study: the rain and the filtered view in the ending

Agent study, 2026-11-05. Read only: no ROM built, no suite run, no patch written.

> [!NOTE]
> I transcribed this report, because the agent could not write it itself. Claims marked **[me: verified]**
> I checked against the base ROM myself with `scene_probe.py` or a byte read. Everything else is the
> agent's claim at the agent's own confidence label, and is NOT independently checked.

---

## Answer in one paragraph

One layer makes both effects. Map 6,1, "Capsule Corporation", carries a scrolling BG0 overlay of rain
streaks on a solid dark blue field. The field is 98 percent of the layer and the layer is fully opaque.
The map layout sets the GBA blend unit to alpha-blend BG0 over BG1, BG2, BG3 and the sprites, so that
dark blue adds to every pixel on screen. That addition is the washed out look. The map's own enter
script switches the layer off in ordinary play and leaves it on in the ending, gated on `flag:196`.
`ext 42` plays no part.

**The ending already loads map 6,1 for the Cell portion, and the look belongs to the map and the flag,
not to the cutscene. A playable fight placed there keeps the look for zero bytes.**

**[me: verified]** The ending table `rom:0x3B8140` calls `load_map(zone=6, area=1, var=1, x=136, y=432)`
at `rom:0x3B7E5E`, which sits just before the Cell dialogue in words 16 to 23.

---

## 1. What draws the rain

A background layer, not a sprite and not a scripted effect.

| Fact | Evidence |
|---|---|
| Map 6,1 entry `rom:0x40B320`, layout `0x085F209C`, BG0 record `0x085F02CC` | entry and layout words |
| BG0's first word is `0x08004FCD`, a layer factory different from the ordinary tilemap factory `0x080056A1` | record words |
| Width and height are 0, so it is a wrapping 256x256 pattern, not a map sized layer | record +4, +8 |
| The tilemap at `0x085F01E8` unpacks to 2048 bytes, a 32x32 screenblock | `render_rain.py` |
| The pattern is diagonal rain streaks on a solid field, fully opaque | rendered to `rain\rain_6_1_bg0.png` |

Scroll `dx` +0x500 and `dy` -0x2EAA read as +5.00 and -46.66 px a frame in 8.8 fixed point. The agent
labels the UNIT as LIKELY: it did not trace the tick that consumes the pair.

Palette of the layer: index 51 is the solid field at 98.04 percent, indices 49, 50 and 76 are the
streaks. All four are blue.

### Where it is turned on and off

The map enter script, entry +0x30, `rom:0x3F9B0A`, 21 bytes.

**[me: verified]** The bytes at `rom:0x3F9B0A` are exactly
`00 C4 02 14 13 04 00 00 02 18 00 C4 02 13 13 04 00 27 02 2E 11`.

```
push 196 ; test_flag_alt(196) ; jz +4 ; push 0  ; ext 24 (0)
push 196 ; test_flag(196)     ; jz +4 ; push 39 ; sound(39)
end
```

- `ext 19` is `flag_test`, at `@0x080095B4`.
- `ext 20` is `1 - flag_test`, at `@0x080095CA`. It is the INVERSE test. This was not in the bible and it
  is what makes the script readable.
- `ext 24 (n)` clears DISPCNT bit 8+n, switching BG layer n off.

So: **flag 196 clear, switch the rain off. Flag 196 set, leave it on and start sound 39.** Entry +0x34,
`rom:0x3F9B1F`, is the leave script: if flag 196, stop sound 39.

Of the 12 overlay rain maps in the game, map 6,1 is the ONLY one whose enter script switches BG0 off.
That is why Capsule Corp is dry in ordinary play and rains in the ending.

Sound 39 is the rain sound. The agent calls this CONFIRMED by correlation across 12 of 12 maps, and
notes that what it sounds like cannot be read from the ROM.

### The flag chain

**[me: verified]** `rom:0x3C4E8A` holds `00 C4 02 1B`, which is `push 196 ; set_flag`. The record
immediately after it, `rom:0x3C4E90`, is the type 5 jump into the ending table. I confirmed that jump
separately: it targets `rom:0x3B8140`.

The agent reports exactly two `push 196 ; set_flag` sites in the ROM, `rom:0x3C4E8A` and `rom:0x3DCEF7`,
the Lookout farewell, and no flag set anywhere inside the ending table. So flag 196 is already set
before the ending loads map 6,1.

---

## 2. What makes the view filtered

**Not `ext 42`.** The agent checked with two independent shapes: the full op listing of all 27 words
names no `palette_fx`, and a raw scan of `rom:0x3B7ADC` to `0x3B8160` for the byte pair `02 2A` returns
nothing. It also notes `ext 42` is a transient fade to white and could not hold a look.

The filter is the GBA blend unit, written from the map layout at map load. Map 6,1 layout word +0 is
`0x10101E41`:

| Field | Value | Meaning |
|---|---|---|
| BLDCNT | `0x1E41` | first target BG0, mode 1 alpha, second target BG1, BG2, BG3 and OBJ |
| EVA | 16 | the top layer at full weight |
| EVB | 16 | the layers under it at full weight |

Both coefficients at 16 make the blend a saturating add, so every pixel gains the rain layer's colour,
about +15 of 31 on blue, with red and green untouched and nothing dimmed. Register values CONFIRMED,
the arithmetic LIKELY, following GBATEK.

Sprites are in the second target, so Trunks, Cell, the HUD and any boss bar all take the same cast.

### The other rain maps, measured not extrapolated

| Map(s) | Name | BLDCNT | EVA | EVB | Enter script |
|---|---|---|---|---|---|
| 6,1 | Capsule Corporation | `0x1E41` | 16 | 16 | flag 196 gate, `ext 24 (0)` plus sound 39 |
| 1,2 | Pepper Town | `0x1E41` | 11 | 12 | none, always rains |
| 1,5 | Outside Pepper Town | `0x1E41` | 16 | 12 | sound 39, unconditional |
| 8,15 | Northern Mountains | `0x1E41` | 11 | 14 | other work |
| 8,19 | Northern Mountains | `0x1A41` | 11 | 12 | sound 39, unconditional |
| 8,20 to 8,26 | Northern Mountains | `0x1E41` | 11 | 12 | sound 39, unconditional |

Map 6,1 is the only one with EVB 16, so it is the only one that tints without also dimming. That is why
the ending's Capsule Corp reads washed out rather than dark.

### A correction to the premise

Map 6,23 is ALSO named "Capsule Corporation". It is the map the ending opens on, with the time machine.
It is NOT rainy. The rainy Capsule Corp is map 6,1.

---

## 3. Does either survive a real fight

The agent's overall label is LIKELY, resting on a vanilla precedent.

**The precedent.** Map 14,3, the Cell Jr fight map, has a BG0 of the same layer class `0x08004FCD` and a
layout whose BLDCNT is also `0x1E41`, alpha-blending it over BG1, BG2, BG3 and OBJ. A playable boss
fight with a boss bar already runs under this exact arrangement in the shipped game.

Supporting points, at the agent's labels:

| Point | Label |
|---|---|
| The rain is a BG layer enabled through DISPCNT at map load, not a scene object | CONFIRMED |
| The only script path that disables a BG layer is `ext 24 (n)` | CONFIRMED as a script-path claim |
| The only `ext 24` touching map 6,1 runs only when flag 196 is CLEAR | CONFIRMED |
| No script op writes BLDCNT, EVA or EVB | CONFIRMED |
| The enter script exists in order to switch BG0 off for ordinary field play, and a playable fight is ordinary field play | LIKELY |

**Three things it could not answer without running the game.**

1. Whether the layer keeps scrolling while a fight scene holds the world.
2. **The Start menu.** The character menu stores a DISPCNT that switches BG0 off. Opening and closing the
   menu mid-fight is a real risk to both the rain and the wash.
3. Whether the HUD and a boss bar stay readable under a blue cast. Only the owner's eye can judge.

**A no-build way to settle all three.** Maps 8,19 to 8,26, Northern Mountains, rain with NO flag gate.
The owner can walk into one on the base ROM, fight something, open and close the menu, and watch. Their
EVA and EVB are 11 and 12 rather than 16 and 16, so the tint is slightly darker than the ending's.

---

## 4. The smallest change that keeps the look

**Zero bytes, if the fight is placed inside the ending on map 6,1.**

Three rules for the ending fight module:

1. A reload of map 6,1 is safe for the look while flag 196 is set. The enter script runs again and leaves
   BG0 on.
2. **Do not call `ext 24` inside the fight.** No script op was found that switches a BG layer back on, so
   a layer switched off in the fight cannot be restored from a script. The agent labels "no setter
   exists" as LIKELY, because its search covered the named ops and one function's callers.
3. Keep the fight after flag 196 is set. Anything inside the ending table already is.

`ext 42` white flashes remain free to use inside the fight.

---

## One disagreement with an existing bible row, for the owner to settle

The BMS row records map 14,3 as "EVA 12, EVB 9", and the same row defines layout +2 as EVA and +3 as
EVB. Map 14,3's layout word +0 is `0x0C091E41`, so byte +2 is `0x09` and byte +3 is `0x0C`. By the row's
own definition that is EVA 9, EVB 12, the reverse of what it states. Either the row's numbers are
swapped or its field definition is. The agent flagged it rather than guessing. It matters, because every
EVA and EVB figure above uses the row's stated field positions.

---

## Files

Listings and scripts are in `scripts\one-time\2026-11-05-ending-rain\`: `ending_table.txt`,
`overlay_maps.txt`, `bg0_census.txt`, `map61_probe.txt`, `disasm.txt`, the `rain\` renders, and the
probe scripts that produced them. Bible rows are in `bible_rows.md` beside this file, 18 rows, tag
`RAIN`, not yet merged.
