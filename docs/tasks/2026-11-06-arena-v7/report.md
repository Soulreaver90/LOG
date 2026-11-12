# Arena v7: build report

Agent build, 2026-11-06. The agent could not write this file itself, so its report is saved below.
Everything under "My verification" is mine. Treat the agent's text as unverified except where I say so.

## Deliverable

| Item | Value |
|---|---|
| Trial ROM | `builds\mockups\2026-11-05-ending-arena\log2_poc_r41_arena_v7.gba` |
| SHA-1 | `f0403027f74ba42829fb24723374b9e11d064d67` |
| Save | `log2_poc_r41_arena_v7.sav`, seeded from `log2_poc_r40.sav` |
| Build list | `build_list_trial_ending.txt` |
| Golden / dev | `acf1b15f...` / `ffbd2bfc...`, both rebuilt and unchanged |

Suite, read from the file and never piped:

```
Ran 1383 tests in 345.533s
FAILED (failures=1, skipped=3)
```

The one failure is the expected RED `test_form_survives_the_leader_change`, one finding:

```
record rom:0x89A9C0 (table rom:0x3DE6F4 word 32, map 9,3 region, fullpower_ssj) runs
appearance(character=4, set=61), entry 20, before leader(2), so appearance_revert undoes it
```

`fullpower_ssj` is untouched by this work and declares no exception.

## Part 3, settled CONFIRMED by the agent

**`ext 104` carries the death event table, because it builds the item with the ITEM's own factory.**

`Sprite_ReplaceWithEntry @0x0800AAC6` calls `Object_SpawnFromEntry @0x0800C75C`. That reads the map entry
at `+4`, bounds the index against the entry's **item count** byte `+4`, and calls the item's own `+0`
factory through `Thunk_BranchR1 @0x08021D2A`, a bare `BX r1`. It then overwrites only position and facing.
**The item's condition is never tested on this path.** For an enemy item the factory `@0x0800E77E` reaches
`@0x0800E280`, which runs `LDR r2,[r6,#0x14] ; STR r2,[r5,#0x4]`, copying the item's own event struct word.

Vanilla carries the exact pairing on map 11,4: item 0 is an NPC, condition 0, set 9; item 1 is an enemy,
**condition 1**, set 9, same point. Its word 6 `rom:0x3E47DC` is the four-op record. So the arena now lists
an NPC Cell (condition 0, (288,392), map 6,1 item 6's own bytes) plus the enemy Cell (condition 1).

"Is a map-built enemy idle during a scene" is moot for this build and was not read. It stays LIKELY from
vanilla precedent, bible row 818.

## Parts 1, 2, 4, 5, 6 as built

- **Part 1.** The arena load moved to record A, ending word 13. It reuses vanilla's own `wait(60)` and
  `fade_out(180)` bytes, then `appearance(3,133)`, `leader(3)`, `load_map_at(6,100,1,248,624)`,
  `wait(120)`, `camera(136,456,2)`, `fade_in(180)`, `walk(0,248,568)`, `wait(100)`.
- **Part 2.** Record F is now `ext104(28,1) ; bar_show(28) ; header_bit1(1) ; camera_follow(0)`. No fade,
  no load, 19 bytes.
- **Part 4.** `INSIDE_BAND = (28, 9, 35, 11)`. `DOOR_MOUTH_ROW` is gone.
- **Part 5.** The arena has its own 3 entry prop list, props 0, 3 and 4. The agent rendered all five first
  to name them: 0 is the glass door, 1 the map post, 2 the save disc, 3 and 4 the two pillars. The map
  post stood on exactly one closed cell, (32,28), so the module opens it. Cutting the prop without that
  would have left an invisible 8 px block. The save point's 72 cells were already open.
- **Part 6.** `battle_start()` is now the four-op default. The old emitter is
  `battle_start_that_opens_a_scene()`. Rule 6 is in `DEFAULT_SHAPE_RULES`, and a census test pins the
  vanilla bar records.

Built-ROM readback: 2 items, 0 warps, 3 props, collision differing from map 6,1 at 25 cells (24 closed,
1 opened), and the whole 834-byte span `rom:0x3B7B08` to `rom:0x3B7E4A` byte-for-byte base.

## One deviation from the brief

The agent used `ext 85 bar_show(28)`, not the brief's sketched `bar_set(28, lo, hi)`. Its reading: `ext 90`'s
extra two values are a display **segment** for one round of a multi-round boss, for example Android 17 at
75/100 then 25/50. Cell here is one round, so the segment form would be wrong.

## A defect the agent found in its own evidence, and fixed

Its one-time probe read a record's kind at `+3` and its ops at `+5`. **Both are wrong: the kind is the byte
at `+2` and the ops start at `+3`.** The wrong filter kept only records whose first op byte happened to be
0, a biased subset, and reported 415 type 0 records against the true 875.

It fixed the probe to use `scene_probe.show_record` and `S.TYPE_CODE`, re-ran, and corrected the three
places the biased numbers had reached: the bible fade row, the `REVEAL` comment in `ending_fight.py`, and
an `ArriveTests` docstring. `scene_harness.run_record` reads `kind = rom[at + 2]` correctly, so the
permanent harness was not affected.

Corrected: of the 28 records carrying both fade ops, 26 run the same number in each. Of the 4 whose
`fade_out` is 180 and which also fade in, 3 fade in at 180. The corrected census also found exactly 3 base
records that open a fade at a bar, all set 31, at tables `0x3E9D4C` word 30, `0x3E9E24` and `0x3E9E84`,
which are precisely the three `celljr_fight` relays already declared as exceptions.

## Exceptions declared beyond the brief's expected one

Four scene openings, not one: `cellgames_ssj.records.fight_cell_seq21`, and three in `celljr_fight`
(`seq31` and the two relays). A dotted notes-path key form was added so the offsets cannot go stale.

## Stale rows marked

Six bible rows asserted the design v7 reverses, marked in place: **1052, 1063, 1239, 1241, 1681**, plus a
clause on **1261** where the music conclusion still holds but the load moved off record F. A search for
`AR5`, `DOOR_MOUTH`, `RETURN_LANDING` and the collision bands found no further rows.

The **ARN4 shadow row is flagged OPEN**. The earlier relabel of the two shadow boxes rested on tile
columns, a correlate. The geometry agrees with the relabel (a flat 40x16 oval suits the post, a round
64x56 disc suits the 64x64 save disc), but each box sits about 130 px **below** its prop's rect, which no
handler explains. The claim is removed from the module comment. It changes no bytes: the arena cuts both
props and paints out both boxes either way.

## Files changed

| File | Change |
|---|---|
| `scene\scene_lib.py` | `battle_start()` is the four-op default; old body renamed `battle_start_that_opens_a_scene()` |
| `patches\battle_arena.py` | Two-item pair, own prop list, band `(28,9,35,11)`, opens `(32,28)`, shadow comment rewritten |
| `patches\ending_fight.py` | New `arrive()` at word 13, `fight_start()` uses the default, two base sites, `REVEAL` rationale corrected |
| `patches\cellgames_ssj.py`, `patches\celljr_fight.py` | `BATTLE_START_EXCEPTIONS` |
| `tests\test_battle_start.py` | Rule 6, census test, note-path resolver, new `DefaultEmitterTests` |
| `tests\test_battle_arena.py` | 61 tests, new `PropTests` |
| `tests\test_ending_fight.py` | 48 tests, new `ArriveTests` |
| `scene\map_view.py`, `scene\scene_probe.py`, `make_tool_index.py` | `TOOL_INDEX_NOTE`, so the generator carries the note |
| `docs\RE-BIBLE.md` | 15 AR7 rows, 3 corrected after merge, 6 marked superseded, 1 flagged OPEN |
| `docs\build-log.md` | One NOTE naming the 5 verification rebuilds |
| `scripts\one-time\2026-11-06-arena-v7\` | Probes, outputs, renders |

## Open, for the owner to watch or decide

1. **A loss is untested.** If the game-over path reloads the current map, only the NPC Cell (condition 0)
   is rebuilt. Map 6,100 has no regions and no warps, so the player would have no fight and no exit.
2. **A stray actor during words 14 to 22.** Record A now runs `ext 39` from whichever map is live before
   the talk, not from map 6,1. Bible rows 1096 and 1776 still hold "what clears the actor list on the
   `ext 39` path" as OPEN, and the v6 play test proved the clear from map 6,1 only.
3. The HUD behaviour across records 14 to 22 is unread.
4. At the reveal the player may clip about 9 px with `VIEW=(136,456)`, against vanilla's `(136,432)`.
5. `fade_in(180)` is three seconds. It is vanilla's own pairing, but he may want it shorter.
6. Cell stands under the CAPSULE CORPORATION banner.
7. **Tooling gap:** `log2_build.py` logs every build, including one aimed at a temporary folder, so
   verification rebuilds accumulate in `build-log.md`. It has no `is_throwaway()` test on the `--out` path.

## My verification

See the night-survey report and the checks recorded below this line after the build was handed back.
