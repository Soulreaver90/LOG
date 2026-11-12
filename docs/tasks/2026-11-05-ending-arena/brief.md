# Brief: a battle arena map for the ending fight

## Why

The ending fight works except for its context. The owner's v5 play test: Trunks spawns with a body
and can MOVE, but cannot attack or transform, the Capsule Corp map-name banner appears, vanilla
NPCs are present, the world map is reachable and every exit works.

Cause: record F re-enters map 6,1, which is an ordinary non-combat town map.

His decision, 2026-11-05: "Maybe this should be a unique map, a new one, no npcs, no exits or save
point, just a battle arena. So a clone." And on where new data goes: "The same thing was done with
the kai rom hack, they did not have their extra data in the same area but in new tables."

So: a NEW map, built in NEW tables in the expansion area. Do not repurpose a vanilla entry.

## Confirmed facts. Do NOT re-derive any of these

All CONFIRMED, from `docs\RE-BIBLE.md` and the disassembly.

| Fact | Value |
|---|---|
| Map table | `rom:0x409368`, 56-byte entries, 327 entries, ends `rom:0x40DAF0` |
| Table pointer literals, ALL of them | `rom:0x5ADC`, `rom:0x5D5C`, `rom:0xEBD8` (3 only, verified by a full word-aligned ROM scan) |
| Entry count getter | `sub_0800E0AC` is 3 instructions: `MOV r0,#0xFF ; ADD r0,#0x48 ; BX lr`, bytes `ff 20 48 30 70 47`. 0xFF+0x48 = 327 |
| To get 328 | patch the single byte at `rom:0xE0AE` from `0x48` to `0x49` |
| Why a new entry needs a moved table | the bytes after entry 326 at `rom:0x40DAF0` are IWRAM pointers, not padding |
| **Combat flag** | entry **`+0x08`**, 1 = combat allowed, 0 = not. Map 6,1 has 0. Map 7,1 has 1. 248 of 327 maps have 1 |
| `+0x04` bytes are LIST COUNTS, not flags | byte `+0x03`/`+0x04`/`+0x05`/`+0x06`/`+0x07` is zero exactly when word `+0x10`/`+0x14`/`+0x18`/`+0x1C`/`+0x20` is zero, in all 327 |
| Map 6,1 | entry 145, `rom:0x40B320`. regions `+0x10` = `0x083F9CF8`, items `+0x14` = `0x083F9C40` (7), layout `+0x2C` = `0x083F9B2C`, `+0x0C` = 0xBE, combat `+0x08` = 0 |
| Zone 6 areas in use | 1..99. Area 100 is free. `(byte+0, byte+1)` is unique per entry in all 327 |
| Player body constructor | `sub_080086D4`. Allocates 0x1A0, registers itself with `STR r4,[0x03001FA8]`, builds the body FROM THE PARTY ROSTER. Reachable ONLY from `ext 35`, `ext 38`, `ext 39` |
| So | `ext 70 leader(3)` must run BEFORE the map op, never after |
| `ext 39 load_map_at` | same 5 args as `ext 35` (zone, area, var, x, y), handler `sub_08009A88`, has NO fade path. `ext 35` `sub_08009852` opens with `MOV r1,#0x40` into `@0x0802664C` |
| A map op does not finish inside the op | vanilla word 13 `rom:0x3B7E4A` runs `wait(frames=120)` between its `load_map` and its first `walk`. Skipping the wait got Cell ERASED |
| A map op sets player position AND camera origin to the same x,y | so load at an origin, then place the player with `ext 62`, which places with no walk |
| `ext 104` | requires a live NPC, reads its position and facing, DESTROYS it, then spawns the item. Pair it with an `ext 51` immediately before, as `celljr_fight` does |

## What to build

A new patch module `scripts\permanent\patches\battle_arena.py`.

1. Copy all 327 map entries into a NEW 328-entry table in the expansion area via `alloc.alloc()`.
2. Append entry 327, the arena:
   - `+0x00`: zone 6, area 100, var 1, and region count byte `+0x03` = 0
   - `+0x04`: item count = however many items the arena list holds; every other count byte 0
   - `+0x08`: **1**, combat ON
   - `+0x0C`: copy 6,1's `0xBE`
   - `+0x10`: **0**, no regions. That removes exits, the save point and the world map
   - `+0x14`: a NEW item list, allocated, holding ONLY the Imperfect Cell enemy item
   - `+0x18`, `+0x1C`, `+0x20`, `+0x24`, `+0x28`, `+0x30`, `+0x34`: **0**, no NPCs, no markers, no variation, enter or leave script
   - `+0x2C`: copy 6,1's layout `0x083F9B2C`, so it still looks like Capsule Corp
3. Patch the 3 literals to the new table base.
4. Patch the count byte at `rom:0xE0AE` to `0x49`.
5. Verify every source byte before the first write, and raise on a second run, the way the other
   patches in that folder do.

Then rework `scripts\permanent\patches\ending_fight.py` record F to:

```
ext 70 leader(3)
ext 39 load_map_at(6, 100, 1, <origin>)
ext 69 wait(120)
ext 62 move_to(player, <spot>)
ext 55 face(player, up)
ext 51 spawn(28, <cell spot>)      only if the arena item list does not already place Cell
ext 104 (28, 7)                    same condition
ext 86 header_bit1(1)
ext 85 bar_show(28)
next = 26 (END)
```

Prefer letting the ARENA ITEM LIST spawn Cell at map load, which removes the `ext 51` + `ext 104`
pair entirely. That is the owner's stated preference, "just load into a controllable trunks and a
boss cell". Only keep the pair if the item list route does not work, and say so in the report.

Pick the origin and the spot so both fighters are framed: vanilla uses origin `136,432` with
actors at `248,568` and `244,504`, giving screen (112,136) and (108,72).

## Files

- NEW `scripts\permanent\patches\battle_arena.py`
- EDIT `scripts\permanent\patches\ending_fight.py` (record F only; leave the death record alone)
- NEW `scripts\permanent\tests\test_battle_arena.py`
- EDIT `scripts\permanent\tests\test_ending_fight.py` (record F's op list and ordering tests)
- EDIT `scripts\permanent\build_list_trial_ending.txt` (battle_arena BEFORE ending_fight)

## Rules

- `docs\tasks\global.md` applies in full. Absolute paths only, never `cd`.
- Python is `py -3.14 -P`. No em or en dashes anywhere. No byte order mark.
- Build: `py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_ending.txt --out builds\mockups\2026-11-05-ending-arena\log2_poc_r41_arena_v1.gba --log <same folder>\build.log`
- Never overwrite an existing ROM or save: check absence, then create.
- Full suite must pass: `py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent`. Capture unittest's OWN exit code. NEVER pipe the run into `tail`, the pipe reports tail's exit code.
- Report: what you built, the ROM SHA-1, the suite result, every RE claim labelled CONFIRMED or
  LIKELY with its address, and proposed RE-BIBLE rows as `## Section N` table blocks.

One report message, then stop. Do not add a byte order mark.
