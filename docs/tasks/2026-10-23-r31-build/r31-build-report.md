# r31 build report: Piccolo and Gohan stay, fly off after the last line, no cut back; scouter; save slot 2

Brief: `docs\tasks\2026-10-23-r31-build\r31.md`, plus my two items sent during the work (scouter, save slot 2). Base: r30 `51d856e18fd607e8366d965f834c884537268651`. Built 2026-10-23 9:49 AM (build-log time). Labels: CONFIRMED (C), LIKELY (L), SPECULATIVE (S).

| SHIPPED | Where |
|---|---|
| Piccolo and Gohan stay through the walk-offs; only Trunks and Vegeta fly off | `log2_poc_r31.gba`, patch `piccolo_gi_scene` (edited in place) |
| After "You look great Gohan", Piccolo and gi Super Saiyan Gohan fly off screen downward (ext 54), then are removed | same |
| No cut back: no fade, Goku keeps his spot, the follow camera eases 40 px right from the scene camera | same |
| SET 158 once, "Journal Updated!", Goku leads, flags and later scenes as in r30 | same, tests |
| Super Perfect Cell scans: entry 19 +8 = 58, +0xC = 52 | patch `superperfect_cell` |
| Save slot 2 = before the Cell Games, slot 3 = the chamber exit test | `log2_poc_r31_chamber2.sav` |
| Saves, states and ROM pair copied to r31 names | `builds\` |
| Suite passes | 549 tests, 0 failures, 0 skipped |

| PENDING | Why |
|---|---|
| In-game check by me | Test plan, section 9 |
| The scouter cannot open in the requested saves | Header bit 2 is clear in every slot and state (section 5). I made an extra pair `log2_poc_r31_scouter.gba` / `.sav` with the bit set. Concern 1 |

---

## 1. Records changed (`piccolo_gi_scene`)

Every record and the scene table keep their r30 addresses. Records 31 and 44 are shorter, so each keeps its r30 slot (`R30_SLOTS`) and the tail stays 0xFF. So no later allocation moves: set 58, the idle hook and the table stay where r30 put them. C (diff proof, test `test_r31_keeps_every_r30_address`).

| Index | Address | r30 | r31 | Item |
|---|---|---|---|---|
| 31 (seq 32 copy) | `rom:0x89AF38`, slot 75 | 75 bytes: sound 26, Gohan flies and leaves, sound 26, group (Trunks, Vegeta), sound 26, Piccolo flies and leaves | 40 bytes, then 35 x `FF`: `23 00 00 00 1a 02 2e 02 3f 1d 03 82 08 8b 20 87 50 02 36 00 84 02 34 1d 03 82 12 8b 40 87 30 02 36 00 89 02 34 02 40 11` | 1 |
| 35 | `rom:0x89AF84` | `push 103,312,400 ; ext 51` and `push 59,496,400 ; ext 51` (spawn) | the same pushes with ext 62 (move): `+0x28` and `+0x38` `33` to `3E` | 1 |
| 44 | `rom:0x89B118`, slot 61 | fade out, remove, Goku to (744,352), camera jump, follow, wait, fade in, tail | 52 bytes, then 9 x `FF`: `20 00 00 00 1a 02 2e 02 3f 1d 03 81 4e 84 70 87 70 02 36 00 67 02 34 1d 03 82 3c 85 30 87 70 02 36 00 9e 02 34 02 40 00 00 02 21 00 9e 02 1b 00 3e 02 2e 11` | 2, 3, 4 |

Record 44 decoded: sound 26 ; group ( ext 54 (103, 312, 504) ; remove 103 ; ext 54 (158, 344, 504) ; remove 158 ) ; ext 33 (0) ; SET 158 ; sound 62 ; next index 32.

- **Record 31** is built by `relocate` with two drops (`SEQ32_DROPS`): the Gohan block (`sound 26 ; push 56,840,480 ; ext 54 ; push 56 ; ext 52`) and the Piccolo block. What is left equals the vanilla Trunks and Vegeta bytes (test). Its tail (camera to the player, SET 158, sound 62) still lives in record 44, as in r29. C.
- **Why ext 62, not ext 51:** both NPCs now exist when record 35 runs, so a second spawn would make two of each. ext 62 (set position) is an actor command that vanilla uses on NPCs (record `rom:0x3B8566` moves NPC Goku 60, Piccolo 103 and Gohan 53). It runs under black, between the fade out and the fade in. C.
- **Piccolo exists in every branch.** Seq 3 spawns him if he does not lead; seq 27 spawns the old leader as an NPC when Goku takes over. Vanilla seq 32 already flies him off with no branch. C (walk), L (branch values).
- Nothing else in the scene changed: lines, walk-ins, flash, portraits and the table words (diff proof, `test_code_records`, line tests).

## 2. The fly-off (item 2)

- **Direction: down (facing 0), the vanilla walk-off direction.** In vanilla seq 32 every flight goes down from its seq 3 spot: Gohan (0, +48), Trunks (+32, +56), Vegeta (+24, +32), Piccolo (-16, +56). Each ends 16-32 px below the view. C (decode, test).
- Piccolo flies from (312,400) to (312,504), Gohan from (344,400) to (344,504): straight down, 104 px at 2 px a frame, about 52 frames (0.9 s). They fly together in one command group, as vanilla flies Trunks and Vegeta. Sound 26 plays first, as before each vanilla flight. C (bytes), L (look).
- **Off screen before removal:** the scene camera is (232,320), so the view ends at y 480. Fly frames are drawn from y - 24, so at y 504 the sprite top is at the bottom edge. Vanilla Gohan's flight ends the same way (480 with a 456 view bottom). C (record dy from the ROM, test).
- **Gohan flies as gi Super Saiyan:** the flying actor is set 158 (spawned in record 40). Set 158 and set 103 have anim 12 (the flying pose) in all 4 dirs; dir 0 is a head-first dive (`scripts\one-time\2026-10-23-r31-build\set158_fly_d0.png`, `set103_fly_d0.png`). C.
- Goku does not turn. He faces left, toward where Gohan stood, as after his walk-in. Not asked; one `ext 55 (0, 0)` would make him face down.

## 3. The hand-back (item 3)

- After "You look great Gohan" there is no fade, no wait, no ext 31 and no command to Goku. Goku stays at (384,400). C (test).
- **Camera:** the scene camera stays at (232,320) from record 35. ext 33 (0) then starts the follow. Goku's 16x8 box gives the target (272,320). So the camera **eases 40 px right and 0 px down**. C (simulation from the listing constants).

| Frames after ext 33 | 0 | 1 | 15 | 30 | 60 | 78 |
|---|---|---|---|---|---|---|
| Gap left (px) | 40 | 38.1 | 19.5 | 9.5 | 2.2 | under 1 |

- **I will see it move:** a slow 40 px slide to the right over about 1 s, most of it in the first half second, likely while "Journal Updated!" is up. Goku moves from screen x 152 to 112 (the centre) and stays on screen throughout (test). L (seen in game).
- Option, not done: put the scene camera at (272,320) in record 35, then there is no ease at all. That shifts the whole scene framing 40 px right (Piccolo at screen x 40, not 80). The brief keeps the framing.

## 4. End state kept (item 4)

- SET 158 runs once, in record 44, then index 32 "Journal Updated!", then index 33 ext 86 (1). ext 70 (4) is still in seq 27, so Goku leads. Gohan's record ends at ext 73 (0, 158) (record 40). C (tests `FlagAndControlTests`).
- None of these lived in the removed blocks. The tail was already in record 44 and stays last in it, in r28 order (ext 33, SET 158, sound 62). The removed walk-off blocks held no flag, no ext 73 and no ext 70. C (test `test_seq32_copy_is_the_trunks_and_vegeta_walk_offs_then_the_new_scene`).
- Nothing of the scene stays on the map: Piccolo, set 59 and set 158 are all removed (test).

## 5. Scouter for Super Perfect Cell (my add)

**What the scouter shows (C, listings and data):**

| | Entry | Name | Portrait | HP | STR | POW | END |
|---|---|---|---|---|---|---|---|
| Cell before the self-destruct (`set:30`), r30 and r31 | 13 | Cell, "Perfect" | 40 | 5160 | 44 | 46 | 50 |
| Super Perfect Cell (`set:58`), r30 | none: skipped, no marker | | | | | | |
| Super Perfect Cell (`set:58`), r31 | 19 | Cell, "Perfect" | 52 (shows 40's face until I draw 52) | 8230 | 60 | 59 | 65 |

- The game has no numeric "power level". The info screen (`@0x08018A38`, text `@0x0801790E`) shows the name, the text, the portrait and, from the entry's +0x10 enemy type, HP, STR, POW and END (labels "HP: %d" and so on). The text of both entries ends "The effect on his power level is so drastic that it cannot be calculated." C.
- Entry 19's +0x10 is already enemy type 25, the Super Perfect Cell fight's own type (`rom:0x6D5904`), so its stats are his real stats. C.
- **Set 30 still scans as today:** `scouter_match` (`@0x08019102`) returns the first of 128 entries whose set header matches. Entries 13-18 still name set 30, so set 30 gets 13. No other set id 7-160 changes its match (test). C.
- The scan marker draws the entry's set (`@0x08018EFC`), so it shows the set 58 sprite. The database list skips a repeat of the previous name, so it still shows one 'Cell, "Perfect"' row. C.
- **Bytes:** `rom:0x6F8FC4` `1E` to `3A` (+8, set) and `rom:0x6F8FC8` `28` to `34` (+0xC, portrait). The patch checks entry 19 is vanilla, 13-18 name set 30 and no entry names 58, before any write.
- I set the portrait too (the study's design 7 lists both bytes). It keeps the scouter face equal to his dialog face, now and after I draw 52. To drop it, delete one line in `superperfect_cell.apply`.
- **The scouter needs save header bit 2.** Select opens it only while save +1 bit 2 is set (`@0x08004D68`). The story sets it with ext 113 (`@0x0800AEB8`) in the records that give the Scouter item (`rom:0x3CF49C`, `rom:0x3D0C48`). Every slot of `log2_poc_r31.sav` and `log2_poc_r31_chamber2.sav`, and all five states, have the item but not the bit. So no requested file can open the scouter. C. I made `log2_poc_r31_scouter.gba` (byte copy of r31) and `log2_poc_r31_scouter.sav` (the chamber2 save with slot 2 +1 = `07`, checksum redone) for the scouter step. Concern 1.

## 6. Save slot 2 (my add)

`log2_poc_r31_chamber2.sav` = `log2_poc_r30_chamber2.sav` with slot 2 replaced by slot 3 of `log2_poc_r30.sav`.

- A slot holds its own Adler-32 at +0x164 and no slot number: the load routine (`@0x08003F9C`) takes the offset 0x10 + n x 0x168 from its argument. So the whole 0x168-byte slot moves with **no field change**: no checksum, index or header edit was needed. Slot offsets and the slot size are multiples of 8, so the .sav block swap keeps a slot whole. C (listing, tests).
- Slot 1 (Gohan, Capsule Corp, after Cell), slot 3 (Vegeta, TV room, the chamber exit test) and every byte outside slot 2 equal the r30 chamber2 save. All three checksums are valid (game Adler-32 and `zlib`). C (tests).
- Slot 2: Goku leads, map 9,1 (the Lookout) at (768,832), flag 191 set, flag 195 clear, level 40 party, Hercule not in the party. C.

## 7. r31, copies and diff proof

**r31:** `builds\log2_poc_r31.gba`, SHA-1 **`b6ddbe93ce12c0f8d3e98d487f37a9b2b28f63f8`**. It equals the in-memory build of `build_list.txt`. The build added one line to `docs\build-log.md`.

Copies, exclusive create (`scripts\one-time\2026-10-23-r31-build\copy_files.py`, `make_scouter_save.py`). No ROM, `.sav` or state was overwritten.

| Source | Copy | SHA-1 |
|---|---|---|
| `log2_poc_r30.sav` | `log2_poc_r31.sav` | `159601a376596afbd9d4124845a3b1355b46a839` |
| `log2_poc_r30.ss1` | `log2_poc_r31.ss1` | `177e917c7fe67ac7c1ff9e011154cfb2f8945548` |
| `log2_poc_r30.ss2` | `log2_poc_r31.ss2` | `4487d1d348f206bf098d1d62a32c1767880e691a` |
| `log2_poc_r30.ss3` | `log2_poc_r31.ss3` | `e04c34dbbbf39c0196b0a3425022f6c55481dd32` |
| `log2_poc_r30.ss4` | `log2_poc_r31.ss4` | `570ba9bb945748fe0599761a4a26d9bb8113bb8e` |
| `log2_poc_r30.ss5` | `log2_poc_r31.ss5` | `8062e3d9b6248d2a6075898dfeb21ea688b8c3b7` |
| `log2_poc_r30_chamber2.sav` + slot 2 from `log2_poc_r30.sav` slot 3 | `log2_poc_r31_chamber2.sav` | `8b0b74f4896ba1a57666499305861f5f42c40a06` |
| `log2_poc_r31.gba` | `log2_poc_r31_chamber2.gba` | `b6ddbe93ce12c0f8d3e98d487f37a9b2b28f63f8` |
| `log2_poc_r31_chamber2.sav`, slot 2 +1 bit 2 | `log2_poc_r31_scouter.sav` (extra) | `43746ae5a8a7990b7ea5ca59dcbdaca76d59176e` |
| `log2_poc_r31.gba` | `log2_poc_r31_scouter.gba` (extra) | `b6ddbe93ce12c0f8d3e98d487f37a9b2b28f63f8` |

**States safe with r31:** all five copied states. No RAM word in `log2_poc_r31.ss1`-`.ss5` names a changed byte or any `piccolo_gi_scene` allocation (`rom:0x89ADB4`-`0x89B20B`). C (state scan). `log2_poc_r29_chamber2.ss2` and `.ss3` (not copied) hold the r29 table address and are not safe, as r30 said.

**Diff proof r30 to r31** (`scripts\one-time\2026-10-23-r31-build\diff_proof.py`, output `diff_proof.txt`): **127 bytes in 8 runs, 0 outside a named site.** C.

| Region | Bytes | Item |
|---|---|---|
| `rom:0x6F8FC4` scouter entry 19 +8 (`1E` to `3A`) | 1 | scouter |
| `rom:0x6F8FC8` scouter entry 19 +0xC (`28` to `34`) | 1 | scouter |
| `rom:0x89AF3F`-`0x89AF82` record 31 (walk-offs, then `FF` tail) | 68 | 1 |
| `rom:0x89AFAC`, `rom:0x89AFBC` record 35 op bytes (`33` to `3E`) | 2 | 1 |
| `rom:0x89B11C`-`0x89B154` record 44 (fly-off, hand-back, tail, then `FF`) | 55 | 2, 3, 4 |

The table, both type 5 words, records 2-30 and 36-43, set 58, the hook and every vtable word are unchanged.

## 8. Tests

Suite: `py -3 -P -m unittest discover -s ...\scripts\permanent\tests -t ...\scripts\permanent` ran **549 tests, OK, 0 skipped** after the build, the copies and the last test edit (`scripts\one-time\2026-10-23-r31-build\suite_final.txt`). Before the build: 542, OK, 4 skipped (the r31-file checks).

| Item | Tests |
|---|---|
| 1 stay | `StayTests`: record 31 = the vanilla Trunks and Vegeta bytes; Piccolo and set 59 are never removed before record 44 (except the gi swap in 40); they are spawned only in seq 3 or seq 27; record 35 moves them with ext 62 under black; vanilla moves NPCs with ext 62; old seq 32 is named only by the dead table. `test_seq32_copy_...` |
| 2 fly-off | `FlyOffTests`: record 44 follows the last line; one group: fly, remove, fly, remove; down like every vanilla flight; sprite top below the view at the end (record dy from the ROM); sets 103 and 158 have anim 12 in all dirs; the flyer is the live set 158. `test_walk_ins_use_ext_53_and_only_the_fly_off_flies` |
| 3 hand-back | `HandBackTests`: no ext 40, 41, 42, 43 or 31 after the last line, one ext 33; the last command to Goku is his walk-in; the follow starts from (232,320); eases 40 px right, 0 down, gap per frame; Goku on screen for 120 frames; follow constants from the listing; the player box from a state |
| 4 end state | `FlagAndControlTests` (SET 158 once in 44, then 32, 33; ext 70 (4); last ext 73 (0, 158)), `ActorTests` (nothing stays, one Gohan at a time) |
| 6 nothing else | `test_code_records`, line and portrait tests, `test_r31_keeps_every_r30_address`, `test_r30_to_r31_changes_only_records_31_35_44`, `test_r30_to_r31_outside_the_scene_is_the_scouter_only` |
| scouter | `ScouterTests`: set 30 matches 13 and set 58 matches 19 (r30: -1); no other set changes; what the scan screen shows for 13 and 19; only 2 scouter bytes change; one database row; the listings of match, info screen, marker and scan. `FailClosedTests` adds entry 19 and entry 15 |
| save | `test_r31_saves.py`: copies; slot 2 = r30 slot 3, slots 1 and 3 and the rest = the chamber save; checksums valid; the slot offset comes from the index; the scouter save differs in the bit and its checksum only; Select needs the bit and ext 113 sets it |

Rebased tests: `test_piccolo_gi_scene.py` (CODE 35 and 44; the camera hand-off tests replaced by `HandBackTests`; the r30-file test became r31; the r29 walk test counts the r31 op bytes), `test_superperfect_cell.py` (the scouter-unchanged test became stats-unchanged plus `ScouterTests`; the r30-file test became r31). Backups of the four files: `scripts\one-time\2026-10-23-r31-build\backup\`.

## 9. My test plan

**A. The Lookout.** ROM `builds\log2_poc_r31_chamber2.gba` with `log2_poc_r31_chamber2.sav` (same name, so mGBA pairs them). Load **slot 3**. Read every box.

| Beat | Expect |
|---|---|
| Load to "You are now playing as Goku." | As r30 |
| **Walk-offs** | Trunks and Vegeta fly off together. **Piccolo and Gohan stay** where they stand |
| Fade | Black, then the left edge: Piccolo faces right (he did not leave) |
| Gohan comes in | Gold armor Gohan walks in from the right, as r30 |
| Lines, flash, admire, Goku walks in | As r30. "You look great Gohan" |
| **Fly-off** | Right after the box closes, sound 26 (the vanilla walk-off sound); Piccolo and gi Gohan (gold hair, purple gi) dive down off the bottom of the screen together, in under 1 s |
| **Hand-back** | No fade and no jump. Goku stays where he stopped, facing left. The view slides about 40 px right over about 1 s, so Goku ends near the centre |
| Control | "Journal Updated!", then Goku gold and playable on that spot |

**B. Slot 2 and the file select.** Same ROM and save. At the file select:

| Slot | Expect (C for the data, L for the look) |
|---|---|
| 1 | As r30: Gohan leads, Capsule Corp, after Cell |
| 2 | **Goku highlighted as the leader** when the slot is selected; Gohan (gi base sprite, appearance entry 2), Piccolo, Vegeta, Trunks. Hercule (record +0x14 bit 1 clear), if drawn, gray and from the back (L). Continue: Goku on Dende's Lookout, before the Cell Games |
| 3 | As r30: Vegeta leads. Continue: the TV room, the chamber exit test above |

**C. The scouter.** ROM `log2_poc_r31_scouter.gba` with `log2_poc_r31_scouter.sav`. Load **slot 2** (the same game as B, with the scouter switch on). Play the Cell Games to the self-destruct.

| Beat | Expect |
|---|---|
| Press Select on the Lookout | The scouter opens (it would not in the chamber2 save) |
| Select in the fight before the self-destruct | Cell gets a marker. Info: 'Cell, "Perfect"', the Cell face, HP 5160, STR 44, POW 46, END 50 (as today) |
| Select after "He's back!!!!" | Super Perfect Cell gets a marker with his bolts sprite. Info: 'Cell, "Perfect"', the same face (id 52 shows 40's art for now), **HP 8230, STR 60, POW 59, END 65** |
| Scouter database | One 'Cell, "Perfect"' row |

Watch for: whether Select works during a fight at all (L: the button handler also tests a field state word); the fly-off timing against the text box.

## 10. Concerns

1. **The scouter is off in every requested save and state** (section 5). The coordinator asked for a scouter step; it needs header bit 2. I made the extra pair `log2_poc_r31_scouter.gba` / `.sav` rather than change `log2_poc_r31_chamber2.sav`, which was already written (no overwrite). A real save made after the story gives the Scouter has the bit. Say if I want the bit in the chamber2 file under a new name instead. C.
2. **The SAV row on header bit 2 is wrong:** it says the debug teleport sets it. ext 113 sets it where the Scouter is given (bible row, section 7). C.
3. **The 40 px ease is visible** (section 3). Removing it changes the scene framing. L (look).
4. **The scouter portrait is 52** (one byte more than the coordinator's note). Same face as 40 until I draw 52.
5. **Not seen in an emulator.** Everything above is proved by bytes, listings and tests.
6. One-time helper scripts (`scripts\one-time\2026-10-23-r31-build\edit_spc_tests.py`, `edit_save_tests.py`) edited test files by exact text replace; `edit_spc_tests.py` has three lines over 120 characters.
7. **Process deviation.** One shell call held a stray `cat` that waited on input. I stopped it and removed the empty file it made (`%TEMP%\x`). Nothing else outside my files was written.

## 11. Files

- Patches: `scripts\permanent\patches\piccolo_gi_scene.py`, `superperfect_cell.py` (edited). `build_list.txt` unchanged.
- Tests: `scripts\permanent\tests\test_piccolo_gi_scene.py` (edited), `test_superperfect_cell.py` (edited), `test_r31_saves.py` (new).
- Study and tools: `scripts\one-time\2026-10-23-r31-build\` (`study.py` and `.txt`, `set158` and `set103` exports and fly sheets, `copy_files.py`, `make_scouter_save.py`, `diff_proof.py` and `.txt`, `lint.py`, `suite_prebuild.txt`, `suite_final.txt`, `bible_rows.md`, `backup\`).
- Nothing under `data\` or `art\` was written. No `cd` in any shell call.
