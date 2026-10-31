# Save slots report: slot 2 on Master Roshi's Island, slot 3 before the Cell Games

Date: 2026-10-18. Brief: `docs\tasks\2026-10-18-save-slots\save-slots.md`. ROM: USA base, SHA-1 `18e0715d...`.

Labels: **CONFIRMED** = proved from ROM bytes or code. **LIKELY** = strong evidence, my test pending. **SPECULATIVE** = a guess.

## Result

| Item | Value |
|---|---|
| New save | `test-data\saves\log2_lv40_cellgames.sav`, 8192 bytes, SHA-1 `c755acf074bc3eefb14023935142bbbc10ad26b1` |
| Copy next to a ROM | Not done by me. At the final check, `archive\builds\log2_poc_r13.gba` existed and `log2_poc_r13.sav` was already there (16:39, written by another task). Its SHA-1 is `c755acf0...`, the same file, so r13 already loads this save |
| Tests | 19 new save tests in `scripts\permanent\tests\test_save.py`, all OK. Whole suite: 195 OK (was 176) |
| Old build | `build --set postcell` writes SHA-1 `3ecf1e40...` byte for byte (tested) |

## 1. Slots

| Slot | Story | Map (zone, area, var) | x, y | Leader | Source bytes | Label |
|---|---|---|---|---|---|---|
| 1 | After Cell | Capsule Corporation save point (6, 1, 1) | 432, 591 | Gohan | Byte for byte the slot 1 I loaded (`log2_lv40_postcell.sav` = `log2_poc_r12.sav`) | LIKELY (position inside save rect (408,568)-(457,617)) |
| 2 | After Cell | Master Roshi's Island (11, 1, 1) | 416, 160 | Gohan | World map landing script `0x083FBC84`: `1d 05 16 02 02 86 40 82 40 02 26 11` = `push 11,1,1,416,160 ; ext 38 ; end` | CONFIRMED |
| 3 | Flag 191, before the Cell Games | Dende's Lookout (9, 1, 1) | 768, 832 | Goku | World map landing script `0x083FBBFC`: `1d 05 12 02 02 8c 00 8d 00 02 26 11` = `push 9,1,1,768,832 ; ext 38 ; end` | CONFIRMED (game-used position) |

**Slot 2 uses area 1, not areas 2-6 (deviation from the brief).** CONFIRMED.
- Area 1 is the island itself: its name script `0x08405C82` gives text 217 "Master Roshi's Island" while flag 196 is clear.
- Area 1 holds the zone's only world-map exit: region item `0x08405F34`, rect (393,121)-(440,176), condition always, script `0x08405F20` `00 2b 02 31 1d 05 0c 81 46 02 b1 10 a0 70 02 26 11` = music 43, world map at (3144,2104).
- Areas 2-3 are "Master Roshi's Home" (door warp at 11,1 rect (672,360)-(681,385)). Areas 4-6 have no world-map exit (`exits.py 11`).
- The exit needs no story flag. Flying back in needs flag 68 (world map region 13/14), which the post-Cell set has.
- Island save point, the fallback place: item `0x08406038`, rect (544,136)-(593,185), always.

**Spawns inside exit rectangles.** CONFIRMED. Slots 2 and 3 spawn inside the A-press exit rectangle, as the game does after a landing. Trigger type `0x0800D838` reads `[0x083ED2A4]` = input `0x0300229C`, +0x14 bit 0 (new A press). So loading there does not fly the player out. Pressing A does.

**Slot 3 place.** The Dende record that sets flag 191 (`0x083DD2F0`) loads no map, so the game leaves the player on the Lookout. The Lookout arrival (768,832) is the game's own placement on that map. Fallback: Lookout save point, item `0x08404040`, rect (736,600)-(793,649).

## 2. Slot 3 flag diff from the post-Cell set

Slot 3 = post-Cell flags minus 192, 193, 194, 195. 151 flags. Ranges end with 185-191.

| Removed flag | Only SET site | Scene evidence | Meaning | Label |
|---|---|---|---|---|
| 193 | `0x083E8D92` | after "#Let's do this!" | Cell Games entered; quest "Enter the Cell Games" done | C (site), L (meaning) |
| 192 | `0x083E93E0` | after "Okay. I'll do it." and "Wonderful. Let's get started!"; ext 70 (0) at `0x083E93A8` | Gohan agrees to fight Cell and becomes the player | C, L |
| 194 | `0x083E9BBB` | fight scenes near "Does anyone else want to be a martyr?" | A fight step before Rage (`0x083EA369`) | C, L |
| 195 | `0x083EC6A2` | after Cell's defeat | Cell beaten | C |

- Story order is 191, 193, 192, 194, 195.
- Kept: flag 191 (only SET `0x083DD32B`, Dende record `0x083DD2F0`). Flags 189 (`0x08408A68`, Snowy Highlands map script) and 190 (`0x083E7F67`, a +5 Strength capsule pickup) are not Cell Games scripts.
- No other flag is set or cleared in the Cell Games scenes (`0x083E8000`-`0x083ED000`) or the arena maps (`0x08408B00`-`0x08409368`). None of the post-Cell "cleared later" flags has a CLR site there.
- Search shape: `flagscan2.py` (literal pushes, ops 0, 1 and 29, before ext 27 or 28). A SETFLAG with a computed number would not appear.

## 3. Party and appearance choices (slot 3)

| Field | Value | Evidence | Label |
|---|---|---|---|
| Leader | 4 (Goku) | Map 14,1 barrier "Only Goku is allowed to pass through this barrier." (cond `0x08408DB0`: leader not 4 and flag 195 clear). Its break object (`0x08408DFC`) needs leader 4 and `level(4) > 39` (`0x08408DD4`; ext 22 = `0x08004214`, 1-based). Goku's EXP 2,727,775 gives level 40 | C (script), L (mechanism) |
| Gohan to Goku | Capture 02 level 40 records, +0x14 = 0x7F | Last party op before 191: `0x083DBC38` (flag 158): ext 79 (4), ext 80 (4), ext 80 (0), ext 82 (4); Goku joins at level 35 (ext 98 (4, 35) `0x083DBC4C`) | L (order by flags) |
| Hercule | ROM default record (`0x081D9548` + 5 * 28): HP 50, EP 20, level 1, +0x14 = 0x40 (not in party) | He joins only at seq 51 `0x083EC6C6` (ext 79 (5), ext 98 (5, 40), ext 80 (5)), reached only when trophies 302, 303, 305, 306 are all set. The four other join sites also test flag 195 first | C |
| Outfits | Gohan entry 2 (set 56), Vegeta entry 8 (set 137), Trunks entry 15 (set 132), others default | All literal ext 73 calls, ordered by the flag next to each: flag 129 Trunks 128, Gohan 53; flag 149 Trunks 129, Vegeta 138; flag 151 Trunks 132, Vegeta 137 (`0x083E7789`); flag 154 Gohan 56 (`0x083DB62B`); then only Rage 58 and post-Cell 56 inside the Cell Games | L (order by flags, not ROM address) |
| Items | Dragon Radar 45 = 1, Scouter 22 = 1, Dragon Balls 29-35 = 0 | Record `0x083DD2F0` runs ext 76 on items 29-35. Ext 76 lowers the count by 1 (`0x080096CA`: `ldrb`, `add #0xFF`, `strb`) | C |
| Journal | "Enter the Cell Games" active, "Return the Dragon Balls" finished, "Talk to Dende" hidden | `log2_save.py journal` on the quest table (below) | C (evaluation), my check pending |

**My facts checked.**
- "Enter the Cell Games": active flag 191, done flag 193. CONFIRMED.
- Flag sites 191 `0x083DD32B`, 192 `0x083E93E0`, 193 `0x083E8D92`, 194 `0x083E9BBB`, 195 `0x083EC6A2`. CONFIRMED.
- "Hercule joins at Cell's defeat (`ext_29` with 5 at `0x083EC67B`)": **wrong in part**. Ext 29 (5) at `0x083EC69C` is a message 4 broadcast (`0x08009740`). The party add is ext 79 (5) at `0x083EC6C9`, and it runs only with all four trophies.
- Gohan after the chamber: ext 73 (0, 56) at `0x083DB62B`. CONFIRMED.

## 4. East District 439 finding

**Cause: a character barrier, not the anti-piracy point and not a missing flag.** CONFIRMED (map data), LIKELY (that the barrier stops the walk).
- The old slot 2 map, 2,29, lies in the cluster of maps 2,26-2,52. A graph of every warp and map-load script in zone 2 shows no world-map exit in that cluster.
- The only link out is the warp at 2,26 rect (384,320)-(465,337), to map 2,7 at (112,52) (data `00 02 07 00 70 00 34 00`).
- (112,52) is inside the barrier scene `0x083EE640`, rect (89,49)-(136,72): "Only Vegeta is allowed to pass through this barrier.", condition "leader is not 2 and flag 274 is clear".
- Flag 274 has one SET site, `0x083EE682`. It runs from a break object whose condition is "leader 2 and Vegeta level 30 or more" (`0x083EE688`). The break script clears rect (104,24)-(136,56) with ext 71 and ext 117.
- The old slot 2 had Gohan leading and flag 274 clear. Workaround in the old save: at the 2,29 save point, Switch Characters to Vegeta.

**Anti-piracy point, found on the way.** CONFIRMED (script).
- The only East District world-map exits run scene table `0x083B8EEC`: map 2,5 rect (105,121)-(160,176), always; map 2,6 rect (249,201)-(296,256), while flag 27 is clear.
- Record `0x083B8E84`: music 43, ext 129 (pushes the SRAM probe byte `0x03001FC0`, handler `0x0800AFC2`). Zero: world map at (2944,1912). Non-zero: "This game will not run on the hardware found." (`0x083B8EAE`) and ext 97.
- So it fires only when SRAM at `0x0E000000` is writable. Ext 34-37 use `0x03001FC4` (map push and return), not the probe byte. The overview's "Readers: ext 34, 35, 36, 37, 129" is wrong for 34-37.
- Search shapes: region scripts of all 327 maps, and a byte scan for ext 129 followed by a test. An NPC talk scene that calls ext 129 would not appear in the first shape.

## 5. Other findings

- **Quest table base** is `0x086D68DC`, 43 entries `{category, done, active, text}` (loop `0x08004A86`-`0x08004AE4`). The save doc had `0x6D68E0`, which read each category from the next entry. Fixed in section 5.
- **Goku after Cell**: ext 91 (4) at `0x083EC735` removes him. This answers open question 3 of the save doc. The post-Cell slots keep him, as I asked before.
- **Slot 1 mismatch.** `test-data\saves\log2_lv40_postcell.sav` and `log2_poc_r12.sav` are both SHA-1 `1973041f...` with slot 1 at (432,591). The bible's `3ecf1e40...` is the build output, with slot 1 at (432,613). The edit is not recorded anywhere I searched (build log, bible, slice1 reports). The new set uses 591, the value I loaded. The `postcell` set keeps 613, so the old build stays byte for byte.
- **Region items**: `{factory, trigger type, rect, data}`. Warps `0x0800C233` and `0x0800D9C3` carry `{dir, zone, area, var, x, y}`. A scan of all region items finds 17 that load the world map (15 script regions, 2 East District scene regions). All 17 use the A-press trigger `0x0800D838`; 16 play music 43 first, map 5,1 (`0x083F9690`) does not. Story scenes that load the world map are not in this count.

## 6. Code and doc changes

| File | Change |
|---|---|
| `scripts\permanent\rom\log2_save.py` | `PRESET_SETS` (`postcell`, `cellgames`) with a story field per slot; `build ... [--set]`, default `cellgames`; `journal <sav> <rom>` with a quest-script evaluator (raises on unknown ops; counts held items only); `write` refuses to overwrite a file |
| `scripts\permanent\tests\test_save.py` | New, 19 tests. The tool had no tests before |
| `docs\research\re-save-format.md` | Sections 5, 6, 7 (7a new save, 7b old save), open question 3, files table |
| `docs\RE-BIBLE.md` | 12 rows appended to section 8, 4 rows to section 11. No other line changed |
| `scripts\one-time\2026-10-18-save-slots\regions.py`, `exits.py`, `scene.py` | New scratch RE tools |

All written files: LF, no byte order mark, no en or em dashes.

## 7. My test plan

Before you start: turn off the cheat `0202b32d:02`. Cold boot; do not load a state.

1. **Install.** On r13, nothing to do: `archive\builds\log2_poc_r13.sav` is already this file. For another ROM, back up its .sav, then copy `test-data\saves\log2_lv40_cellgames.sav` to the ROM's base name with `.sav`.
2. **Slot 2, Master Roshi's Island.** Continue, slot 2. Expected: Gohan stands near the island's take-off spot. Press A there. Expected: the world map. Fly back onto the island marker. Expected: the island again.
3. **Slot 3, the Lookout.** Continue, slot 3. Expected: Goku leads on Dende's Lookout. Open the Journal. Expected: "Enter the Cell Games" is active.
4. **Reach the Cell Games.** Press A at the Lookout take-off spot. Fly to "The Cell Games Arena" marker. Expected: map 14,1. Walk north with Goku. Expected: the barrier opens (sound), and the warp north starts "GOKU: I'll fight Cell first." If walking north does nothing, face the barrier and press A. How the break object triggers was not traced.
5. **See Rage.** Play the Cell Games. Expected: Gohan becomes the player ("Okay. I'll do it."), then the Android 16 scene and the Rage transform (set 58, drawn as the gi in the hack).
6. **If something fails.**
   - Barrier stays closed: check that Goku leads. Switch Characters at the Lookout save point.
   - Slot 3 position is stuck: `log2_save.py set <in> <out> 3 pos=764,645` puts Goku at the Lookout save point.
   - Old slot 2 (East District): Switch Characters to Vegeta at the save point, then walk north through 2,26 to 2,7. If the barrier does not open, face it and press A.

## 8. Concerns

- Party bits and outfits at flag 191 are ordered by the flag number next to each script op. That order fits the quest chain, but it is not a traced run. LIKELY.
- The barrier mechanism (collision and break object) is read from data and scripts, not seen in game. LIKELY.
- The post-Cell slots still have Hercule in the party and Goku in the party. The story gives neither without the trophies, and it removes Goku. Unchanged on purpose ("as now").
- The flag scans see literal pushes only.
- The trigger of the two barrier break objects (factory `0x0800F9A3`) was not traced: walk into the barrier or press A at it.
- `test_save.py` pins slot 1 by its checksum `0x31C65A32` and compares it with `test-data\saves\log2_lv40_postcell.sav` only when that file exists.
- `build` now defaults to the `cellgames` set. Anyone who wants the old file must pass `--set postcell`.
