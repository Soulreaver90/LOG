# r29 build report: Piccolo gives Super Saiyan Gohan the gi on Dende's Lookout

Brief: `docs\tasks\2026-10-22-piccolo-gi-scene\piccolo-gi-scene.md`. Base: r28 `eef01cf6aa37f660bbe0f07b87694d058252499c`. Built 2026-10-22 9:11 PM (build-log time). Labels: CONFIRMED (C), LIKELY (L), SPECULATIVE (S).

| SHIPPED | Where |
|---|---|
| New scene on the Lookout, the storyboard lines as written ("it's" with the apostrophe) | `log2_poc_r29.gba`, patch `piccolo_gi_scene` |
| Gohan in armor Super Saiyan (set 59, portrait 62) before the flash, gi Super Saiyan (set 158, portrait 115) after | same |
| Fade in, Gohan walks in, Piccolo raises his arm, blue flash, Gohan in the gi, Goku walks in, fade out | same |
| The scene ends as r28: flag 158, "Journal Updated!", Goku playable | same, tests |
| Saves, states and the chamber test save copied to r29 names, ROM pair `log2_poc_r29_chamber2.gba` | `builds\` |
| Suite passes | 485 tests, 0 failures, 0 skipped |

| PENDING | Why |
|---|---|
| In-game check by me | Test plan, section 9 |
| Exact look of the left edge, the camera frame and the flash | Not seen in an emulator (section 8) |

---

## 1. Study: the chamber exit scene

The scene is one table, `rom:0x3DBDD4`: 34 records and an END word (index 34 = 0, resume 0). Each record's u16 at +0 is the next index. C.

**Who starts it (two shapes, C):** an any-offset byte search for `0x083DBDD4` finds only the type 5 words `rom:0x3CF7E4` (Bulma list) and `rom:0x3D1530` (Cell's TV scene). No aligned word points into the table body. Each record the patch replaces has one reference, its own table word.

**The Lookout part (map 9,1), r28:**

| Seq | What happens | Ops |
|---|---|---|
| 3 | Fade out 10, load 9,1 (player at 760,440), HUD off, camera to (648,296) speed 10, spawn NPC Goku `set:61` (744,352) and Gohan `set:56` (840,432), Piccolo `set:103` (816,416) if the leader is not Piccolo, Trunks 132, Vegeta 137; Gohan's record ext 73 (0, 158); fade in 180; level and unlocks | ext 40, 39, 55, 86, 31, 51, 55, 73, 41 |
| 6-26 | Dende dialog. Piccolo speaks as id 3 (his record: entry 6 +2 = 90). Gohan's lines seq 16, 21 use raw 121 (armor base) | type 1/2 |
| 27 | White fade 180 (ext 42), the player takes NPC Goku's spot (ext 62 (0, 744, 352)), NPC Goku removed, Goku joins and leads (ext 70 (4)), faces down | ext 42, 62, 52, 79-83, 98, 70, 55 |
| 31 | "Goku is now an available character! You are now playing as Goku." | type 2 |
| 32 | Gohan, Trunks, Vegeta, Piccolo walk off and are removed; camera follows the player (ext 33 (0)); SET 158; sound 62 | ext 54, 52, 63, 64, 33, 27, 46 |
| 33, 34 | "Journal Updated!", HUD on (ext 86 (1)), END: Goku has control | |

**Ops used, read from their handlers (C unless marked):**

| Op | Meaning | Proof |
|---|---|---|
| ext 40 (n) | Fade to black over n frames; stays black | `@0x08009B1C` > `@0x0802664C`, tick `@0x0800DBAE` |
| ext 41 (n) | Fade in from black to the RGB table | vtable `0x0802542C`, tick `@0x0800DBE2` > `@0x0800BE14` |
| ext 42 (n) | Snapshot fade to white (the seq 27 "flash") | tick `@0x0800DC08` > `@0x0800DB18` |
| ext 135 (set, R, G, B, n) | Colour pulse to (R, G, B) and back over n frames, queued on the actor | `@0x0800A2C2`, tick `@0x0801D348` |
| ext 31 (x, y, speed) | Camera moves to (x, y) and stays; (x, y) is the top-left of the view | `ext31_move`; top-left: the follow camera aims at actor centre minus (120, 84) |
| ext 33 (set) | Camera follows the actor, eased: each frame it closes 3/64 of the x gap and 9/128 of the y gap | `@0x08009814` sets `[@0x030020C0 +4]` and makes it current; update `@0x0800D9F8` (vtable `0x08025A6C`) |
| ext 51 (set, x, y) | Spawn, immediate | `npc_factory`, `world_add` |
| ext 52 (set) / 54 (set, x, y) / 55 (set, dir) / 57 (set, state) / 62 (set, x, y) | Remove / walk / face / state / set position: actor commands | `actor_queue` callers |
| ext 63 / ext 64 | Open / close a command group (parallel across actors) | `@0x0800E032`, `@0x0800E038` |
| ext 43 (n) | Wait n frames | vtable `0x0802545C` |
| SET (ext 27) | Story flag | bible s8 |

- Walks ignore collision: the mover adds a fixed velocity for a counted number of frames, then snaps to the target (`@0x0800D28C`). So a scripted walk always ends. C.
- Facing: 0 down, 1 up, 2 left, 3 right; a walk faces the way it moves. C.
- Ext handlers pop their arguments and push nothing; one value left at a code record's end would replace the next index. C.
- Map 9,1 regions: left edge (257,385)-(304,424), right edge (1217,385)-(1264,424), world exit (745,793)-(792,848), save point (736,600)-(793,649). C.

**Lists called complete, with their shapes:**
- ext 135 calls: 16 by both shapes (scene-table walk and `02 87` byte pairs); 2 B-only hits have no constant arguments. Colours: red, violet, black. No blue. C (`scripts\one-time\2026-10-22-piccolo-gi-scene\ext135_42_r28.txt`).
- ext 57 states (360 calls by both shapes, 387 by B): Piccolo gets states 0, 3, 4 only. C (`ext57_r28.txt`).

## 2. Design

The patch copies the table to the expansion area, appends records 35-44 and repoints the two type 5 words. Nothing in the old scene changes, so a state paused in the old scene runs the old scene to its end.

| New table index | Record | Content |
|---|---|---|
| 2 | copy of seq 3 | NPC Gohan `set:56` to `set:59`; ext 73 (0, 158) to ext 73 (0, 53) (entry 0) |
| 15, 20 | copies of seq 16, 21 | raw portrait 121 to 62 |
| 31 | copy of seq 32, walk-offs only | Gohan `set:59`; next index 35 |
| 35 | new code | fade out 30; Goku to (520,400) facing left; camera to (232,320); Piccolo (312,400) facing right; Gohan `set:59` (496,400) facing left; fade in 30; Gohan walks to (344,400) |
| 36-39 | new text | Gohan / Piccolo / Gohan / Piccolo |
| 40 | new code | group: Piccolo state 11, three blue pulses; Gohan 59 out, 158 in at (344,400) facing left; Piccolo faces right; ext 73 (0, 158); Gohan state 4 |
| 41 | new text | Gohan "Thank you, it's awesome!" |
| 42 | new code | Goku (the player) walks to (384,400); Gohan faces right |
| 43 | new text | Goku "You look great Gohan" |
| 44 | new code | fade out 30; Piccolo and Gohan removed; Goku to (744,352) facing down; camera follows Goku; wait 10; fade in 30; SET 158; sound 62; next index 32 |

Walk order: 0-31, 35-44, 32 ("Journal Updated!"), 33, END. C (tests).

Why Gohan's record is entry 0 until the flash: the cutscene hook maps raw 62 to 115 while his record is entry 2, 5 or 22. With entry 0 the line shows the vanilla armor Super Saiyan frame (id 62). Record 40 then writes entry 5 (gi Super Saiyan), as r28 has it after the scene. This needs no new portrait id and no block move. C (hook runs in the tests).

Text: type 1 records, no `0A` or `0B`: the game wraps each box at the last space, as its own boxes do. No name prefix: every speaker already said a "NAME:" line earlier in this scene, and the brief adds no words. The font has the apostrophe (vanilla "Here's", "That's"; the line breaker measures "it's" as one line). C.

Portraits per line: Gohan 62 before the flash, 115 after; Piccolo 3 (his record, entry 6 +2 = id 90, as every Piccolo line in this scene); Goku 65.

## 3. Substitutions

| Storyboard | Used | What it looks like | Label |
|---|---|---|---|
| "Piccolo raises his hands at Gohan" | ext 57 (103, 11): state 11, anim 11 of `set:103`, 96 frames | Piccolo turns to the front, then holds his right arm straight up (2 frames, front-facing in all directions). Anim 18 (both arms forward, glowing) is closer, but its state 30 never ends, so a script would wait forever | C (frames, code), L (look) |
| "There is a bright blue flash" | ext 135 (59, 72, 160, 248, 32) three times, on Gohan's queue, while Piccolo's arm is up | The game's own colour-pulse op with a blue the game never uses with it: the whole screen goes to bright blue (72,160,248) and back, three times in 96 frames. No vanilla blue flash exists (vanilla pulses: red, violet, black). Gohan changes to the gi right after the third pulse, in place | C (op), L (look) |
| "Gohan is in the new gi, admiring it" | ext 57 (158, 4): state 4, anim 4 of `set:158`, 64 frames | Gohan raises a fist with a sparkle and looks it over, then stands. Vanilla uses state 4 on NPCs 10 times for Piccolo alone | C (frames, code), L (look) |
| The transition | ext 40 (30) / ext 41 (30), the fade the scene already uses | Black for the set-up, then fade in on the left edge | C |
| The cut back | ext 40 / ext 41 again, then the r28 tail | Fade to Goku on his r28 spot (744,352), then "Journal Updated!" | C |

## 4. Records inserted (bytes)

Table copy `rom:0x89B14C` (45 words). Type 5 words `rom:0x3CF7E4` and `rom:0x3D1530`: `D4 BD 3D 08` to `4C B1 89 08`.

| Index | Address | Bytes | Data |
|---|---|---|---|
| 2 | `rom:0x89ADB4` | 204 | seq 3 copy; changed bytes: `1d 03 76 8d 10 86 60` (spawn 59), `1d 02 76 02` (face 59), `00 00 00 35 02 49` (ext 73 (0, 53)) |
| 15 | `rom:0x89AE80` | 100 | `10 00 02 3e` + the seq 16 stream unchanged |
| 20 | `rom:0x89AEE4` | 84 | `15 00 02 3e` + the seq 21 stream unchanged |
| 31 | `rom:0x89AF38` | 75 | `23 00 00 00 1a 02 2e 1d 03 76 8d 10 87 40 02 36 00 3b 02 34 00 1a 02 2e 02 3f 1d 03 82 08 8b 20 87 50 02 36 00 84 02 34 1d 03 82 12 8b 40 87 30 02 36 00 89 02 34 02 40 00 1a 02 2e 1d 03 81 4e 8c 40 87 30 02 36 00 67 02 34 11` |
| 35 | `rom:0x89AF84` | 77 | `24 00 00 00 1e 02 28 1d 03 00 88 10 86 20 02 3e 1d 02 00 04 02 37 1d 03 83 50 85 00 50 02 1f 1d 03 81 4e 84 70 86 20 02 33 1d 02 81 4e 06 02 37 1d 03 76 87 60 86 20 02 33 1d 02 76 04 02 37 00 1e 02 29 1d 03 76 85 30 86 20 02 36 11` |
| 36 | `rom:0x89AFD4` | 54 | `25 00 01 3e` "Piccolo, can I have a new outfit just like yours?" `00` |
| 37 | `rom:0x89B00C` | 8 | `26 00 01 03` "..." `00` |
| 38 | `rom:0x89B014` | 30 | `27 00 01 3e` "You were my first teacher" `00` |
| 39 | `rom:0x89B034` | 50 | `28 00 01 03` "Yeah kid, it will make you look really sharp." `00` |
| 40 | `rom:0x89B068` | 93 | `29 00 00 02 3f 1d 02 81 4e 16 02 39` + 3 x `1d 05 76 81 10 82 40 83 70 40 02 87` + `02 40 00 3b 02 34 1d 03 82 3c 85 30 86 20 02 33 1d 02 82 3c 04 02 37 1d 02 81 4e 06 02 37 1d 02 00 82 3c 02 49 1d 02 82 3c 08 02 39 11` |
| 41 | `rom:0x89B0C8` | 29 | `2a 00 01 73` "Thank you, it's awesome!" `00` |
| 42 | `rom:0x89B0E8` | 20 | `2b 00 00 1d 03 00 86 00 86 20 02 36 1d 02 82 3c 06 02 37 11` |
| 43 | `rom:0x89B0FC` | 25 | `2c 00 01 41` "You look great Gohan" `00` |
| 44 | `rom:0x89B118` | 51 | `20 00 00 00 1e 02 28 00 67 02 34 00 9e 02 34 1d 03 00 8b 50 85 40 02 3e 1d 02 00 00 02 37 00 00 02 21 00 0a 02 2b 00 1e 02 29 00 9e 02 1b 00 3e 02 2e 11` |

## 5. r29 SHA-1

`builds\log2_poc_r29.gba`: `7366217278fb7a158ca82fe1cc3d469330f78030`. It equals the in-memory build of `build_list.txt`. The build added one line to `docs\build-log.md`.

## 6. Files

Patch `scripts\permanent\patches\piccolo_gi_scene.py`, appended as the last line of `build_list.txt`. Test `scripts\permanent\tests\test_piccolo_gi_scene.py`. Study tools and outputs in `scripts\one-time\2026-10-22-piccolo-gi-scene\` (`extcalls.py`, `sheet.py`, `diff_proof.py` and `.txt`, `suite_after.txt`, sprite sheets, `bible_rows.md`).

Copied by exclusive create, byte-equal (tested). No ROM, `.sav` or state was overwritten.

| Source | Copy | SHA-1 |
|---|---|---|
| `log2_poc_r28.sav` | `log2_poc_r29.sav` | `159601a376596afbd9d4124845a3b1355b46a839` |
| `log2_poc_r28.ss1` | `log2_poc_r29.ss1` | `177e917c7fe67ac7c1ff9e011154cfb2f8945548` |
| `log2_poc_r28.ss2` | `log2_poc_r29.ss2` | `4487d1d348f206bf098d1d62a32c1767880e691a` |
| `log2_poc_r28.ss3` | `log2_poc_r29.ss3` | `e04c34dbbbf39c0196b0a3425022f6c55481dd32` |
| `log2_poc_r28.ss4` | `log2_poc_r29.ss4` | `570ba9bb945748fe0599761a4a26d9bb8113bb8e` |
| `log2_poc_r28.ss5` | `log2_poc_r29.ss5` | `8062e3d9b6248d2a6075898dfeb21ea688b8c3b7` |
| `log2_poc_r28_chamber2.sav` | `log2_poc_r29_chamber2.sav` | `11f295fe23528482bb33e8f4c1e6e3cd8ddfc3a9` |
| `log2_poc_r29.gba` | `log2_poc_r29_chamber2.gba` | `7366217278fb7a158ca82fe1cc3d469330f78030` |

`log2_poc_r28_chamber2.ss1` was not copied (not in the brief). It is paused in the old scene's narration, so in r29 it would play the r28 scene.

## 7. Diff proof

Script `scripts\one-time\2026-10-22-piccolo-gi-scene\diff_proof.py`, output `diff_proof.txt`. C.

- The in-memory list up to `fullpower_ssj` equals the r28 file; with `piccolo_gi_scene` it equals the r29 file.
- 1084 bytes differ in 14 runs. Every byte is in a named site: the two type 5 words (3 bytes each) and the new allocations `rom:0x89ADB4`-`0x89B1FF` (records and the table). Bytes outside: 0. Named sites with no change: none.
- The old table and the four source records are equal in r28 and r29. Every new allocation starts after r28's last one, so no earlier byte moved.
- States: no RAM word in the five r29 states names the old table, a replaced record or a type 5 record.

## 8. Tests

`test_piccolo_gi_scene.py`, 30 tests. The scene is walked by next index from the type 5 words; lines run through the game's line breaker; portraits run through `portrait()` and the cutscene hook.

| Brief item | Tests |
|---|---|
| Records decode to the storyboard | the six lines in order with portraits 62, 3, 62, 3, 115, 65; "it's" has a glyph; no control bytes; each line is one box and fits 0x90 px |
| Portraits and sets | Gohan's record is entry 0 at lines 16, 21, 36, 38 and entry 5 at 41; 62 shows the vanilla armor Super Saiyan frame at entry 0; 115, 65, Piccolo 90; NPC Gohan is 59 at his first two lines and 158 at the third; set 59 is the vanilla armor Super Saiyan header; anims 11 (Piccolo), 4 (set 158) exist |
| The scene list word | both type 5 words name the new table, nothing names the old one; the copy keeps every other word; old table and records unchanged |
| Flag 158 and Goku control | walk order; SET 158 once, in record 44; then "Journal Updated!" and ext 86 (1); ext 70 (4) still in seq 27; Gohan's last record write is (0, 158) as in r28 |
| Script safety | ext sequences of records 35, 40, 42, 44; each code record ends with an empty stack; every commanded actor exists; at most one Gohan at a time; no new actor stays |
| Diff and fail closed | only named sites change; earlier allocations unchanged; r29 file equals the build; a changed type 5 word, table, source record, tail or reverse lookup byte refuses with no write; a second run refuses |
| Copies | r29 saves, states and the ROM pair are byte copies |

Suite: `py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent` ran 485 tests, OK, 0 skipped (`scripts\one-time\2026-10-22-piccolo-gi-scene\suite_after.txt`).

Changed outside my own files (deviation, needed for a green suite, as r28 did): `test_fullpower_ssj.py` now builds its "rom" with `fullpower_ssj` only, and its list test checks the order around `fullpower_ssj`; `test_art_inject.py` `LIST` gets `piccolo_gi_scene`. Neither file is on the sprite task's list.

Lint: no BOM, CR, dashes, non-ASCII or lines over 120 in the new and changed files.

Not proved in code (LIKELY):
- The floor at (312-520, 400) is open Lookout floor next to the left-edge region. Walks ignore collision, so a wall cannot hang the scene, but a tree or rail there would overlap the sprites.
- State 11 on an NPC: vanilla never sends it, but its enter, tick and end follow state 4's shape, which vanilla sends to NPCs.

## 9. My test plan

ROM `builds\log2_poc_r29_chamber2.gba` with `log2_poc_r29_chamber2.sav` (same name, so mGBA pairs them). Load **slot 3**. Read every box; do not skip.

| Beat | Expect |
|---|---|
| Load | Vegeta in the Capsule Corp TV room. The TV scene starts at once (if not, step off the spot and back) |
| Exit scene, Lookout | NPC Goku gold, **NPC Gohan gold in the armor** (r28: base armor) |
| Gohan's two Dende lines | **Armor Super Saiyan portrait** (r28: armor base) |
| Seq 27-31 | As r28: white fade, Goku joins, "You are now playing as Goku." |
| Walk-offs | Gohan (gold, armor), Trunks, Vegeta, Piccolo walk off |
| Fade | Screen goes black, then fades in on the left edge of the Lookout: Piccolo stands facing right |
| Gohan walks in | Gold armor Gohan walks in from the right and stops facing Piccolo |
| Lines | Gohan "Piccolo, can I have a new outfit just like yours?" (armor gold portrait), Piccolo "...", Gohan "You were my first teacher", Piccolo "Yeah kid, it will make you look really sharp." |
| Flash | Piccolo turns to the front and raises his arm; the screen pulses bright blue three times; Gohan is in the purple gi, gold hair |
| Admire | Gohan raises a fist with a sparkle; "Thank you, it's awesome!" with the gi Super Saiyan portrait |
| Goku | Gohan turns right; gold Goku walks in from the right and stops beside him; "You look great Gohan" (portrait 65) |
| Cut back | Fade out, fade in on Goku at his r28 spot near the palace, then "Journal Updated!". The camera slides right during and after the fade-in (concern 5) |
| Control | Goku gold and playable. Later Gohan appearances as r28 (gi Super Saiyan) |

Watch for: the left-edge frame (sky, trees or rails around Piccolo), the blue tone, and whether the arm pose reads as "raises his hands". Each is one constant in the patch (`PICCOLO_AT`, `CAMERA`, `BLUE`, `RAISE`).

## 10. Concerns

1. **Scope beyond the new scene.** The storyboard says Gohan is already Super Saiyan in armor before Goku takes control. So the whole exit scene shows NPC Gohan as `set:59` and his two Dende lines with portrait 62. This settles r28 open point 2a my way. C (bytes), L (my intent).
2. **Gohan's record is entry 0 (Demon Clothes) from seq 3 to the flash.** No player control exists in that span and no line names his record, so nothing shows it. After the scene it is entry 5, as in r28. C.
3. **Process deviation.** Two existing test files changed (section 8). One shell call started a stray `cat` that waited on input; I stopped it and removed its empty `/tmp/x`. Nothing under `data\` or the sprite task's paths was written.
4. **Dead data.** The old table `rom:0x3DBDD4` and old seq 3, 16, 21, 32 are now unreferenced. Bible tool trap: the type 5 words point into the expansion area.
5. **The cut back pans.** Found after the build, from the follow camera code (C). Record 44 calls ext 33 (0) with the camera still at (232,320) and Goku at (744,352). The follow camera eases (3/64 of the x gap per frame), so after the 10-frame wait about 60 percent of the 390 px gap remains. I see the camera slide right across the Lookout during the fade-in. In r28 the same op starts from (648,296), close to Goku. It cannot hang the scene. Fix for r30 (not applied, because r29 must not be overwritten): in record 44, under black, add ext 31 (648, 296, high speed) before ext 33 (0). Then the hand-off matches r28.
6. **Other look items, not seen in an emulator (L):** at the pulse peak the whole screen is solid blue, not only Gohan; the gi swap shows right after the third pulse; anim 11 is front-facing with one arm raised, not two hands; Goku is put back at (744,352).
7. **`log2_poc_r28_chamber2.ss1` was not copied.** It is paused in the old scene, so in r29 it plays the r28 scene, not the new one. The brief's "every r28 .ss*" may include it. The parent decides.
