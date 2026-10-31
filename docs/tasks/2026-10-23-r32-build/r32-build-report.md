# r32 build report: the "Goku is playable" lines move to after the Lookout scene

Brief: `docs\tasks\2026-10-23-r32-build\r32.md`. Base: r31 `b6ddbe93ce12c0f8d3e98d487f37a9b2b28f63f8` (checked: the r31 list built in memory gave the r31 file before my edit; suite 549 OK). Built 2026-10-23 12:39 PM (build-log time). Labels: CONFIRMED (C), LIKELY (L), SPECULATIVE (S).

| SHIPPED | Where |
|---|---|
| The two lines show after Piccolo and Gohan fly off, as the last box before "Journal Updated!" | `log2_poc_r32.gba`, patch `piccolo_gi_scene` (edited in place) |
| Their chime (sound 28) moves with them; the Journal chime (sound 62) stays right before "Journal Updated!" | same |
| Party change and Goku's lead stay before the scene; SET 158 once; control as Goku where he stands | same, tests |
| No address moves: 24 bytes differ from r31, all in the scene table copy and two record slots | diff proof |
| Saves, states and ROM pairs copied to r32 names | `builds\` |
| Suite passes | 559 tests, 0 failures, 0 skipped |

| PENDING | Why |
|---|---|
| In-game check by me | Test plan, section 7 |

---

## 1. The two lines (item 1)

**C (walk decode of r31, base bytes).** They are one vanilla record with two boxes, not ours:

| Index (seq) | Address | Record | Writer |
|---|---|---|---|
| 29 (seq 30) | `rom:0x3DBD10` | `1e 00 00 00 1c 02 2e 11`: sound 28, next 30 | vanilla |
| 30 (seq 31) | `rom:0x3DBD18` | type 2, no portrait, next 31: "@^Goku is now an available character!" `0B` "You are now playing as Goku." | vanilla |

- Both are equal to the base ROM in r31. No patch writes them. Our patch only routed around them: in r29-r31 the walk was 28, 29, 30, then 31 (our walk-offs copy) and the new scene. C.
- **Sound 28 goes with the lines.** It is the vanilla system-message chime: 29 of the 30 base records that hold only `ext 46 (28)` are followed by a "^", "@" or "@^" box (`scripts\one-time\2026-10-23-r32-build\chime_sweep.txt`). C.
- **Sound 62 goes with "Journal Updated!".** All 48 vanilla "@^Journal Updated!" records have `ext 46 (62)` in the 24 bytes before them. C.
- **The party change is not with the lines.** Seq 27 (`rom:0x3DBBD4`, index 26) holds ext 79, 80, 82, 83, 98 on Goku's record and ext 70 (4). It must run before the scene, because record 42 walks the player (Goku) in. It stays. C.

## 2. Records changed

The vanilla next indexes are fixed (28 to 29, 29 to 30, 30 to 31), and a new allocation would move set 58 and everything after it. So the patch re-points two words of its own table copy and uses free 0xFF bytes. C.

| Site | Address | r31 | r32 | Item |
|---|---|---|---|---|
| Table word 29 | `rom:0x89B1CC` | `10 BD 3D 08` (chime record) | `38 AF 89 08` (walk-offs copy) | index 28 skips the lines |
| Table word 31 | `rom:0x89B1D4` | `38 AF 89 08` (walk-offs copy) | `60 AF 89 08` (tail record) | after the lines: tail, Journal |
| Tail record (new) | `rom:0x89AF60`, 12 bytes | 0xFF (free end of the 75-byte r30 record 31 slot) | `20 00 00 00 9e 02 1b 00 3e 02 2e 11`: SET 158 ; sound 62 ; next 32 | Journal chime and flag after the lines |
| Record 44 | `rom:0x89B118`, 48 of 61 bytes | 52 bytes: ... ext 33 (0) ; SET 158 ; sound 62 ; next 32 | `1e 00 00 00 1a 02 2e 02 3f 1d 03 81 4e 84 70 87 70 02 36 00 67 02 34 1d 03 82 3c 85 30 87 70 02 36 00 9e 02 34 02 40 00 00 02 21 00 1c 02 2e 11`, then 13 x `FF`: ... ext 33 (0) ; sound 28 ; next 30 | chime, then the lines |

- Record 44 decoded: sound 26 ; group ( ext 54 (103, 312, 504) ; remove 103 ; ext 54 (158, 344, 504) ; remove 158 ) ; ext 33 (0) ; sound 28 ; next 30.
- The walk-offs copy (`rom:0x89AF38`, 40 bytes) is unchanged; only its table index moved from 31 to 29. Its slot is now 40 bytes and the tail takes the next 35, so record 35 stays at `rom:0x89AF84`. C.
- The vanilla chime record `rom:0x3DBD10` is no longer named by the live table (only by the dead old table). Its op now lives in record 44. C.
- The patch checks both vanilla records before any write (`CHIME_RECORD`, `LINES_HEAD`) and still refuses a second run.
- No record in the table computes its next index from the stack. Branches in seq 3 and seq 27 jump inside the record (`scripts\one-time\2026-10-23-r32-build\next_scan.txt`). C for the walk; L for ops 6, 7, 12, 13, which the scan does not model.

## 3. The new order (items 2 and 3)

| Step | Index | What runs |
|---|---|---|
| ... Dende lines, "Okay, here goes...", white flash, Goku joins and leads (no message) | 0-26 | as r31 |
| "That should do it!", "Already? Wow ... bring them back here." | 27, 28 | as r31 |
| Trunks and Vegeta fly off | 29 (walk-offs copy) | as r31, no chime and no lines before it |
| The gi scene, "You look great Gohan" | 35-43 | as r31 |
| Fly-off, camera follow starts, sound 28 | 44 | |
| "Goku is now an available character!" / "You are now playing as Goku." | 30 | vanilla record |
| SET 158, sound 62 | 31 (tail) | |
| "Journal Updated!", HUD on, END | 32, 33 | as r31: Goku has control where he stands |

- The game's own order is chime, lines, then (later) SET 158, sound 62, Journal. The new order keeps that order. C.
- SET 158 runs once, now in the tail, right before the Journal chime, as in vanilla seq 32. Goku's lead (ext 70 (4)), the party bits and Gohan's last record write ext 73 (0, 158) are unchanged. C (tests).
- **Camera:** ext 33 (0) stays right after the fly-off, as r31. So the 40 px ease to Goku now runs while the lines are up, not under "Journal Updated!". L (look).

## 4. r32, copies and states

**r32:** `builds\log2_poc_r32.gba`, SHA-1 **`185dcc766e9a563270a74d5926426e98e412c02b`**. It equals the in-memory build of `build_list.txt`. The build added one line to `docs\build-log.md`.

Copies by exclusive create (`scripts\one-time\2026-10-23-r32-build\copy_files.py`). Each source was first checked against the SHA-1 in the r31 report. No ROM, `.sav` or state was overwritten.

| Source | Copy | SHA-1 |
|---|---|---|
| `log2_poc_r31.sav` | `log2_poc_r32.sav` | `159601a376596afbd9d4124845a3b1355b46a839` |
| `log2_poc_r31.ss1` | `log2_poc_r32.ss1` | `177e917c7fe67ac7c1ff9e011154cfb2f8945548` |
| `log2_poc_r31.ss2` | `log2_poc_r32.ss2` | `4487d1d348f206bf098d1d62a32c1767880e691a` |
| `log2_poc_r31.ss3` | `log2_poc_r32.ss3` | `e04c34dbbbf39c0196b0a3425022f6c55481dd32` |
| `log2_poc_r31.ss4` | `log2_poc_r32.ss4` | `570ba9bb945748fe0599761a4a26d9bb8113bb8e` |
| `log2_poc_r31.ss5` | `log2_poc_r32.ss5` | `8062e3d9b6248d2a6075898dfeb21ea688b8c3b7` |
| `log2_poc_r31_chamber2.sav` | `log2_poc_r32_chamber2.sav` | `8b0b74f4896ba1a57666499305861f5f42c40a06` |
| `log2_poc_r31_scouter.sav` | `log2_poc_r32_scouter.sav` | `43746ae5a8a7990b7ea5ca59dcbdaca76d59176e` |
| `log2_poc_r32.gba` | `log2_poc_r32_chamber2.gba` | `185dcc766e9a563270a74d5926426e98e412c02b` |
| `log2_poc_r32.gba` | `log2_poc_r32_scouter.gba` | `185dcc766e9a563270a74d5926426e98e412c02b` |

**States safe with r32:** all five copied states. No RAM word in `log2_poc_r32.ss1`-`.ss5` names a changed byte or a scene allocation (`rom:0x89ADB4`-`0x89B20B`). C (state scan). The `.sav` files hold no ROM pointers.

**Not copied (made after r31 shipped, 12:09-12:17 PM, likely by me):** `log2_poc_r31_chamber2.ss1` holds the scene table address `0x0889B158` at IWRAM `0x03007D50`, so it is paused in the chamber exit scene. The word after it is 2, likely the scene index (seq 3). An index of 28 or less plays the r32 order on r32. L. `log2_poc_r31_chamber2.ss2` and `.ss3` name nothing that changed. C. Use them with the r31 ROM.

## 5. Diff proof r31 to r32

`scripts\one-time\2026-10-23-r32-build\diff_proof.py`, output `diff_proof.txt`: **24 bytes in 6 runs, 0 outside a named site.** C.

| Region | Bytes | Item |
|---|---|---|
| `rom:0x89AF60`-`0x89AF6B` tail record (0xFF to the record) | 12 | 2, 3 |
| `rom:0x89B118`, `0x89B144`, `0x89B146`-`0x89B14B` record 44 (next 32 to 30; SET 158, sound 62 out; sound 28 in; tail to 0xFF) | 8 | 2, 3 |
| `rom:0x89B1CC`-`0x89B1CE` table word 29 | 3 | 2 |
| `rom:0x89B1D4` table word 31 | 1 | 2, 3 |

The type 5 words, records 2-28 and 35-43, the vanilla lines and chime records, the Journal word (32), set 58, the idle hook and the scouter bytes are unchanged.

## 6. Tests

Suite: `py -3 -P -m unittest discover -s ...\scripts\permanent\tests -t ...\scripts\permanent` ran **559 tests, OK, 0 skipped** after the build and the copies (`scripts\one-time\2026-10-23-r32-build\suite_final.txt`). Before my edits: 549 OK (`suite_before.txt`).

| Item | Tests (`test_piccolo_gi_scene.py`) |
|---|---|
| 1 the lines | `PlayableLinesTests`: the lines are the vanilla record at word 30, two boxes, next 31; vanilla showed them (after sound 28) before the walk-offs; the vanilla chime record is left unused and unchanged |
| 2 the move | lines show once, after the last fly-off and before the Journal; the last 10 events are fly-off, ext 33, sound 28, the lines, SET 158, sound 62, "Journal Updated!", ext 86 (1), then END; each chime sits right before its box in vanilla and r32; vanilla plays 62 before all 48 Journal boxes; `test_walk_order` (new walk) |
| 3 flags and end state | `test_the_party_change_and_lead_stay_before_the_scene` (all Goku party ops and ext 70 (4) in seq 27, before index 35); `FlagAndControlTests` (SET 158 once, in the tail; order 44, 30, 31, 32, 33; ext 70 (4); Gohan ends at (0, 158)); `test_seq32_copy_...` (the r28 tail split, each op once, in order) |
| 4 nothing else | `test_code_records` (CODE 31 and 44 added or changed), `test_r32_keeps_every_r30_address`, `test_r31_to_r32_changes_only_two_words_and_two_slots`, `test_new_table_keeps_every_other_word`, fail-closed on the two vanilla records |
| copies | `CopyTests.test_r32_saves_states_and_rom_pairs_are_copies` |

Rebased: `test_piccolo_gi_scene.py` (walk order, CODE 44, walk-offs at word 29, r31-file checks became r32, the slot test), `test_superperfect_cell.py` (`test_r31_file_equals_the_build` became r32). Backups: `scripts\one-time\2026-10-23-r32-build\backup\`.

## 7. My test plan

ROM `builds\log2_poc_r32_chamber2.gba` with `log2_poc_r32_chamber2.sav` (same name, so mGBA pairs them). Load **slot 3**. Read every box.

| Beat | Expect |
|---|---|
| Load | Vegeta in the Capsule Corp TV room; the TV scene starts (if not, step off the spot and back) |
| TV, chamber exit, Lookout, Dende lines | As r31 |
| "Okay, here goes..." | White flash; you now are Goku, on NPC Goku's spot (as r31). **No message** |
| "That should do it!", "Already? Wow ... bring them back here." | As r31 |
| **Next** | **No chime and no "Goku is now an available character!"**. Trunks and Vegeta fly off at once |
| Gi scene | As r31, through "You look great Gohan" |
| Fly-off | Piccolo and gi Gohan dive off the bottom, as r31 |
| **Lines** | The system chime, then "Goku is now an available character!", then "You are now playing as Goku." (two boxes). Behind the box the view slides about 40 px right |
| Journal | The Journal chime, then "Journal Updated!" |
| Control | Goku gold and playable on the spot where he stopped |

Watch for: whether the 40 px slide happens under the lines box or only after it closes. The follow is proved to run during waits and fades, not during a text box (L).

Optional: `log2_poc_r32_scouter.gba` with `log2_poc_r32_scouter.sav` slot 2 for the r31 scouter check (unchanged).

## 8. Concerns

1. **Index 31 is no longer the walk-offs.** Table words 29 and 31 of the copy do not match seq numbers any more (bible tool trap row). C.
2. **The camera ease moved under the lines box** (section 3). Moving ext 33 into the tail would put it back under "Journal Updated!"; I kept it right after the fly-off, as r31. L (look).
3. **State `log2_poc_r31_chamber2.ss1`** (made after r31 shipped, likely by me) is paused in this scene (section 4). Not copied. L (index).
4. **Not seen in an emulator.** Everything above is proved by bytes, walks and tests.

## 9. Files

- Patch: `scripts\permanent\patches\piccolo_gi_scene.py` (edited). `build_list.txt` unchanged.
- Tests: `scripts\permanent\tests\test_piccolo_gi_scene.py`, `test_superperfect_cell.py` (edited).
- Study and tools: `scripts\one-time\2026-10-23-r32-build\` (`study.py`, `study.txt` (r31 walk), `study_r32.txt` (r32 walk), `next_scan.py` and `.txt`, `chime_sweep.py` and `.txt`, `copy_files.py`, `diff_proof.py` and `.txt`, `lint.py`, `suite_before.txt`, `suite_final.txt`, `bible_rows.md`, `backup\`).
- Nothing under `data\` or `art\` was written. `inject.py` was not run. No `cd` in any shell call.
