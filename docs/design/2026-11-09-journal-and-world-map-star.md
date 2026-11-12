# The journal entry and the Capsule Corp world map star

The owner, 2026-11-09: "Take the time machine back to the future, or something of that sort / With
capsule corp starred in the world map as with all other major quests".

Both were measured before any code was written. Neither is as cheap as the earlier pricing said.

---

## 1. The journal entry is NOT cheap. My earlier pricing was wrong.

`docs\tasks\2026-11-09-beam-tick-music\addendum.md` priced a 44th quest as one pool word, one bound
byte and a table relocation. That is true of the TABLE and false of the MENU.

### What the addendum missed: the menu object sizes both lists for exactly 43

`sub_080049FC` allocates `0x444` bytes (pool word `rom:0x4C64`) and parks two list headers in it.

| Piece | Offset | Built at | How |
| --- | --- | --- | --- |
| active list header | `+0x154` | `rom:0x4A48` | `add r2,#0x18` onto `+0x13C`, stored to `[sp,#0x60]` |
| done list header | `+0x2B0` | `rom:0x4A52` | `mov r0,#0x2b ; lsl r0,r0,#4`, stored to `[sp,#0x5c]` |
| next field | `+0x40C` | `rom:0x4A5C` | `add r0,#0xff ; add r0,#0x5d` onto `+0x2B0` |

`0x2B0 - 0x154` is `0x15C`, which is `4 + 43 * 8` to the byte. `0x40C - 0x2B0` is `0x15C` again.
**Both lists hold exactly 43 items and nothing more.**

The fill loop at `rom:0x4A86` runs the done script, and on a non-zero result appends to the done
list and skips the rest; otherwise it runs the active script and appends to the active list. So a
quest lands in exactly ONE list per pass. The bound is `cmp r6,#0x2b` at `rom:0x4AE2`.

**Failure mode:** 44 entries in the SAME list writes 8 bytes past it. 44 done quests is the likely
one, because a player who finishes everything puts all of them in the done list. It is silent, it
needs a late save to show, and no test that only assembles the ROM will catch it. This is the same
shape as the scouter menu, and it is the same mistake twice: I measured the table and not the object
that renders it.

### The option the agent's report did not price

The report says `0x2B8` "is not 16 times any 8 bit immediate", so each site needs an extra
instruction it has no room for. That is true of `lsl #4` only. **`0x2B8` is `0x57 << 3`**, so
`mov rX,#0x57 ; lsl rX,rX,#3` keeps the same two instruction shape, which is exactly the trick
`docs\design\2026-11-09-scouter-menu-grow.md` already uses for the scouter. The `+0x40C` site is
formed RELATIVE to it, so `add #0xff ; add #0x5d` becomes `add #0xff ; add #0x65` and also keeps its
shape. The allocation is a pool word.

So growing the object is plausibly five same-length edits plus the bound byte. **It is not a last
build change**, because the scouter census proved the real risk is the sites a `mov ; lsl` grep
cannot see. Every reader of `+0x154`, `+0x2B0` and `+0x40C` across the whole journal menu family has
to be enumerated first, by two independent search shapes, exactly as the scouter was.

### The three real options

| Option | Cost | Risk |
| --- | --- | --- |
| Grow the menu object | a site census, then about 6 byte-level edits | silent overrun if the census misses a reader |
| Replace a vanilla quest | one table entry, nothing structural | costs a real quest; all 43 are real, none is dead |
| Defer the entry | nothing | the ending ships with no journal update |

All 43 vanilla entries were dumped and read (`scripts\one-time\2026-11-09-worldmap-star\quests.py`).
**There is no spare, placeholder or duplicate slot.** Entry 0 is "Talk to Dende on the Lookout",
which is the quest immediately before the ending, so it is the least-bad replacement candidate.

---

## 2. Capsule Corp is ALREADY a world map place. The star is a small insert.

### The mechanism, read from the ROM

Bible B0641 named it and this confirms it end to end. Map 6,99's enter script `rom:0x3FB868` runs to
`rom:0x3FBB27` and draws **13 places**, each as one block:

```
<goal condition> ; jz(9) ; ext102(x,y) ; jmp(13) ; test_flag(unlock) ; jz(7) ; ext101(x,y)
```

`ext 102` is the goal icon, `ext 101` the normal one.

The landing side is separate: map 6,99 carries **27 regions**, alternating a landing and a label.
A landing item is 20 bytes `{factory, trigger, rect, script}` and **its script sits in the 12 bytes
immediately before the item**, so a listing must stop at the item address or it decodes the item as
code. 13 of the 27 regions carry a landing script.

### Capsule Corp's own row

| Piece | Value |
| --- | --- |
| map | **6,1, named "Capsule Corporation"** (bible B1136) |
| world map region | 19, cond `0x0001001E` = flag 30 |
| landing script | `rom:0x3FBD20`, `load_map_fade(6, 1, 1, 248, 232)` |
| marker | **(193,25)**, goal block at `rom:0x3FB916`, normal at `rom:0x3FB925` |
| current goal condition | `(not 157 and 151) or (item 45 count eq, and 158)` |

### What starring it would take

Insert the ending's own flag into that block's `or` chain, right before its `jz(9)`. The jz skips
the `ext102` and the `jmp`, so **its offset does not change**, and no other block's offsets move.
Flag 196 is the natural one: farewell record 87 sets it at `rom:0x3DCEF7` immediately before the
ending, and map 6,1's own enter script already keys its rain off the same flag (B1154).

The enter script is vanilla, so it has to be relocated with the extra ops and map 6,99's entry
`+0x30` repointed. That is the ordinary move several modules already make.

### Why it is NOT in this build

**The ending never shows the world map.** Vanilla ending word 0 `rom:0x3B7B08` is one cutscene
record: `load_map(6,23)` at `rom:0x3B7B17`, then `load_map(1,2)` at `rom:0x3B7B6D` (our build
repoints the second to 1,100). There is no world map load and no free roam between them.

So a star added now is correct and invisible. It becomes visible the moment the player gets control
at Capsule Corp, which is the interactive time machine work the owner deferred. **The star belongs
in that cycle, with the thing it serves.**

---

## Tools written for this

- `scripts\one-time\2026-11-09-worldmap-star\markers.py`, the enter script's 13 marker blocks
- `scripts\one-time\2026-11-09-worldmap-star\landings.py`, every landing and the map it loads
- `scripts\one-time\2026-11-09-worldmap-star\quests.py`, all 43 journal entries
