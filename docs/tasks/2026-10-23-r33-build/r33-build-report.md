# r33 build report: scouter name "Super Perfect" for Super Perfect Cell, and the database trace

Brief: `docs\tasks\2026-10-23-r33-build\r33.md`. Base: r32 `185dcc766e9a563270a74d5926426e98e412c02b`. Built 2026-10-23 2:08 PM (build-log time). Labels: CONFIRMED (C), LIKELY (L), SPECULATIVE (S).

| SHIPPED | Where |
|---|---|
| Scouter entry 19 reads `Cell, "Super Perfect"` (entry 13's format, "Super Perfect" in place of "Perfect") | `log2_poc_r33.gba`, patch `superperfect_cell` step 6 |
| Database trace: entries 14-19 can show; one row pages through several stats; the new name gives Super Perfect Cell his own row | Section 2 |
| Saves, states and ROM pairs copied to r33 names | `builds\` |
| Suite passes | 569 tests, 0 failures, 0 skipped |

| PENDING | Why |
|---|---|
| **my choice: the name does not fit the info screen** | 106 px in a 94 px field: the C sits on the left panel border and the closing quote is under the portrait. The list row fits. Options in section 1 |
| In-game check by me | Test plan, section 7 |

---

## 1. The name (item 1)

**Bytes (C):** a new 22-byte string at `rom:0x908EEC`: `43 65 6C 6C 2C 20 22 53 75 70 65 72 20 50 65 72 66 65 63 74 22 00` = `Cell, "Super Perfect"` + 00. Entry 13's string `rom:0x6FA859` is `Cell, "Perfect"` + 00 (ASCII, straight quotes), so the new one follows its format. Entry 19 +0 (`rom:0x6F8FBC`) goes from `0x086FA859` to `0x08908EEC`. The +4 text pointer stays.

- Entries 13-18 keep the shared string. The old string bytes do not change. C (tests).
- The string sits right after the r32 hook code (the last allocation of the last patch), so every r32 address stays. C (diff proof).

**Fit (C from listings and frame bytes; L for the look):** both info screens (the scan screen and the database panel) draw the name through `@0x0801790E`, centred on x 120, y 16. The background frame has the left panel border at x 72 and a field border at x 167. The 64x64 portrait is an OBJ at (168, 8). So the field holds 94 px of ink (x 73-166).

| Name | Width | Info ink x | Info screen | List row (160 px) |
|---|---|---|---|---|
| `Cell, "Perfect"` (entry 13, vanilla) | 74 | 83-156 | fits | fits |
| `Cell, "Nonperfect"` (widest vanilla name with a portrait) | 92 | 74-165 | fits | fits |
| **`Cell, "Super Perfect"` (built)** | **106** | **67-172** | **12 px over: C on the left border, closing quote under the portrait** | fits (27-132) |
| `Cell,"Super Perfect"` (no space) | 103 | 68-170 | 9 px over | fits |
| `Cell, "Superperfect"` (one word, like "Nonperfect") | 103 | 68-170 | 9 px over | fits |
| `Super Perfect Cell` (not entry 13's format) | 95 | 72-166 | 1 column on the left border | fits |
| `Cell, "S. Perfect"` | 85 | 77-161 | fits | fits |

- Mocks (3x, the database frame with the portrait): `scripts\one-time\2026-10-23-r33-build\fit_3_info.png` (built), `fit_1_info.png` (Nonperfect), `fit_4`, `fit_5`, `fit_6`, `fit_7`; list rows `fit_N_list.png`. Numbers: `scripts\one-time\2026-10-23-r33-build\name_fit.txt`.
- Not options: a 0x0A line break (`text_draw` supports it, but the list rows are 9 px apart and the line step is 8, so it hits the next row); moving the centre x (a code change, out of scope).
- Vanilla `Saber-Toothed Tiger` (101 px) and `Warlord's Henchman` (98 px) are wider, but they have no portrait, so nothing covers them.
- A swap to any option is one string in `superperfect_cell.SUPER_NAME` and the width pin in one test.

## 2. Database trace (item 2)

**Answer: entries 14-19 can show. C from listings and data; L until seen in game.** The bible row "14-19 are never matched" is right only for actors that scan by set. Enemies scan by enemy type.

| Step | Code | What it does |
|---|---|---|
| Scan an enemy | enemy vtable `0x080252A4` +0x24 = `@0x0800E5B8`, message 0x14 | Calls `@0x080190D4` with obj +0x180. The constructor `@0x0800E280` sets +0x180 to the type entry that `enemy_factory` `@0x0800E77E` passes (`0x086D56AC` + 24 x spawn +8). `@0x080190D4` returns the first scouter entry whose +0x10 type gives that entry. No fall back to the set |
| Scan anything else | vt_mover, vt_combatant, vt_npc +0x24 = `@0x08007B08` | `scouter_match` by set: set 30 gives 13, set 58 gives 19 |
| Set a database bit | `@0x08018A38` (scan info screen, from `@0x0801871C`) | Sets slot +0x11A bit n for the scanned entry n |
| Set a bit from a script | ext 141 `@0x0800B00C` | Pops a set id and sets the bit of its set match. Constant calls: sets 74 and 48 (King Cold, Frieza) in record `0x083BD6F0`. None names set 30 or 58 |
| Open the database | factory `@0x080191CA` (vtable `0x0802517C`, scene `@0x0801915C`) | A map object: the only word naming the factory is `rom:0x3FA360`, item 3 of the region list `rom:0x3FA370` of **map 6,6** (zone 6, Capsule Corp, entry 150, condition 0). The Select button opens the scan screen (`@0x08018540`), not the database. C (refs), L (which object the player touches) |
| Build the list | `@0x08019204` | Takes the entries with a set bit, in table order. A run of consecutive entries with an **equal name pointer** becomes one row `{first, last}` |
| Draw | `@0x08019320` | Up to 6 rows; a row shows its first entry's name. The panel shows the current entry: name, stats, portrait, the entry's set sprite |
| Page | `@0x08019844`, `@0x0801970A` | Left and Right step through the row's entries and wrap. Arrows show when the row has more than one entry. Up and Down change the row. A opens the text page |

**Cell entries (C, spawn scan and tests):**

| Entry | Enemy type | Spawn | Where | Scan stats (HP, STR, POW, END) |
|---|---|---|---|---|
| 13 | 78 | `rom:0x406FF0` | map 12,6 | 5160, 44, 46, 50 |
| 14 | 79 | `rom:0x406F78` | map 12,6 | 5500, 44, 46, 50 |
| 15-18 | 21-24 | `rom:0x408E4C` (14,2), `0x408F18`, `0x408FC8`, `0x4090C8` (14,3) | Cell Games | 6500, 50, 55, 60 each |
| 19 | 25 | `rom:0x4090F8` | Cell Games, after the self-destruct | 8230, 60, 59, 65 |

- **"Skips a repeat of the previous name"** = the row grouping above. It compares name pointers, not text, and only between neighbours in table order. C.
- **"Multiple stats for one character"** = one row with several scanned entries. Left and Right page through them; the name stays, the stats change. In vanilla the `Cell, "Perfect"` row can hold up to seven stat sets (13-19). C (listings), L (seen).
- **What the new name changes:** entry 19 now has its own name pointer, so it is no longer in the Perfect run. When his bit is set, the database shows a separate `Cell, "Super Perfect"` row right below `Cell, "Perfect"` (and above `Cell Junior`), with no arrows. The Perfect row pages through 13-18 only. C (simulation, test `test_the_database_gives_super_perfect_its_own_row`).
- **What sets the bits:** only a scan that opens the info screen, or ext 141. Found by three shapes (`scripts\one-time\2026-10-23-r33-build\db_bit_sweep.txt`); a computed offset or a bulk copy would not show. C for the two found, S for "no other writer".
- **The database opens empty in our saves:** every slot of `log2_poc_r33.sav`, `_chamber2.sav` and `_scouter.sav` has all 128 bits clear. C.

## 3. Corrections to earlier reports

1. **r31 test plan C, row 2 is wrong (C from listings).** A Cell Games fight is an enemy of type 21-24, so the scan shows entry 15-18: `Cell, "Perfect"`, HP 6500, STR 50, POW 55, END 60, not entry 13's 5160/44/46/50. Entry 13 is what a set 30 non-enemy actor or the map 12,6 type 78 enemy shows.
2. **r30/r31 "Super Perfect Cell in r30: no marker" is likely wrong.** He is a type 25 enemy, so r30 already matched entry 19 by type. The r31 set byte changed his sprite on the scan screens (set 58), not whether he scans. L (not seen in r30).
3. Bible rows 823 and 828 hold for the set path only. Corrections are in `scripts\one-time\2026-10-23-r33-build\bible_rows.md`.

## 4. r33, copies and diff proof

**r33:** `builds\log2_poc_r33.gba`, SHA-1 **`3ce2bb1763f9c472c5b37d3c4cb70ed417576b97`**. It equals the in-memory build of `build_list.txt` (default art folders, no `LOG_GI_*` variables). The build added one line to `docs\build-log.md`.

Copies, exclusive create (`scripts\one-time\2026-10-23-r33-build\copy_files.py`, output `copy_files.txt`). No ROM, `.sav` or state was overwritten.

| Source | Copy | SHA-1 |
|---|---|---|
| `log2_poc_r32.sav` | `log2_poc_r33.sav` | `159601a376596afbd9d4124845a3b1355b46a839` |
| `log2_poc_r32_chamber2.sav` | `log2_poc_r33_chamber2.sav` | `8b0b74f4896ba1a57666499305861f5f42c40a06` |
| `log2_poc_r32_scouter.sav` | `log2_poc_r33_scouter.sav` | `43746ae5a8a7990b7ea5ca59dcbdaca76d59176e` |
| `log2_poc_r32.ss1` | `log2_poc_r33.ss1` | `177e917c7fe67ac7c1ff9e011154cfb2f8945548` |
| `log2_poc_r32.ss2` | `log2_poc_r33.ss2` | `4487d1d348f206bf098d1d62a32c1767880e691a` |
| `log2_poc_r32.ss3` | `log2_poc_r33.ss3` | `e04c34dbbbf39c0196b0a3425022f6c55481dd32` |
| `log2_poc_r32.ss4` | `log2_poc_r33.ss4` | `570ba9bb945748fe0599761a4a26d9bb8113bb8e` |
| `log2_poc_r32.ss5` | `log2_poc_r33.ss5` | `8062e3d9b6248d2a6075898dfeb21ea688b8c3b7` |
| `log2_poc_r33.gba` | `log2_poc_r33_chamber2.gba` | `3ce2bb1763f9c472c5b37d3c4cb70ed417576b97` |
| `log2_poc_r33.gba` | `log2_poc_r33_scouter.gba` | `3ce2bb1763f9c472c5b37d3c4cb70ed417576b97` |

**Diff proof r32 to r33** (`scripts\one-time\2026-10-23-r33-build\diff_proof.py`, output `diff_proof.txt`): **25 bytes in 2 runs, 0 outside a named site.** C.

| Region | Bytes | Item |
|---|---|---|
| `rom:0x6F8FBC`-`0x6F8FBE`, scouter entry 19 +0 (`59 A8 6F` to `EC 8E 90`) | 3 | 1 |
| `rom:0x908EEC`-`0x908F01`, the new string (was `FF`) | 22 | 1 |

**States safe with r33:** no RAM word in `log2_poc_r33.ss1`-`.ss5` names a changed byte, the new string or the shared Perfect string. C (state scan).

## 5. Tests

Suite: `py -3 -P -m unittest discover -s ...\scripts\permanent\tests -t ...\scripts\permanent` ran **569 tests, OK, 0 skipped** after the build and the copies (`scripts\one-time\2026-10-23-r33-build\suite_final.txt`). Before the build, `test_superperfect_cell.py` alone: 39 tests, OK, 3 skipped (the r33-file checks).

| Check | Test (`test_superperfect_cell.py`) |
|---|---|
| The name decodes to `Cell, "Super Perfect"` 00, lives in the expansion area, and only entry 19 +0 names it | `test_the_name_is_a_new_string_and_13_18_keep_theirs` |
| Entries 13-18 keep pointer `0x086FA859`; its bytes are unchanged | same |
| Every entry except 19 is byte-identical; in 19 only +0, +8 and +0xC differ from vanilla; +4 text kept | `test_only_entry_19_name_word_and_two_bytes_change` |
| Scan screens: 13 and 15-18 read Perfect with their stats; 19 reads Super Perfect, 8230/60/59/65 | `test_what_the_scan_screen_shows` |
| Enemies match by type: the seven Cell spawns give 13-19; no type 0-127 changes its match | `test_cell_enemies_match_13_to_19_by_type`, `test_enemy_scan_listings` |
| Database: bits 12-20 give Nonperfect, Perfect (13-18), Super Perfect (19), Cell Junior; in the patch-free list, one Perfect row 13-19 | `test_the_database_gives_super_perfect_its_own_row`, `test_database_listings` |
| Fit: 106 px; fits the list; info ink x 67-172 against the 73-166 field (pinned so a rename re-checks it) | `test_name_fits_the_list_and_overflows_the_info_field_by_12` |
| Only named sites change; r32 to r33 is the name word and the string; r33 file = build; copies | `DiffTests`, `CopyTests` |
| Fail closed: a changed entry 19 name word or Perfect string refuses | `FailClosedTests` |

The old test `test_the_database_shows_one_perfect_row` became the two-row test; `test_only_two_scouter_bytes_change` became the entry 19 test. Backup: `scripts\one-time\2026-10-23-r33-build\backup\test_superperfect_cell.py`.

## 6. Nothing else changed (item 3)

- Patch `superperfect_cell.py`: step 6 (the string, the pointer, a check of the Perfect string, note `name_19`) and header lines. The comment "14-19 never match today" became "13-18 name set 30; enemies match 14-19 by type". `build_list.txt` unchanged.
- No stat, set, portrait, text or other entry changed (diff proof, tests).

## 7. My test plan

ROM `builds\log2_poc_r33_scouter.gba` with `log2_poc_r33_scouter.sav` (same name, so mGBA pairs them). Load **slot 2** (Goku on the Lookout before the Cell Games, scouter switch on). The database starts empty. Select opens the scan screen; the database is a separate screen on **map 6,6 in Capsule Corp** (L: the object's spot in the room is not traced; look for a computer or terminal). After Cell is beaten, the story moves you to Capsule Corp (zone 6, area 3).

| Beat | Expect |
|---|---|
| Select in a Cell Games fight before the self-destruct, open Cell's marker | `Cell, "Perfect"`, the Cell face, **HP 6500, STR 50, POW 55, END 60** (types 21-24, entries 15-18; not 5160 as r31 said) |
| Select after "He's back!!!!", open his marker | Bolts sprite. Name **`Cell, "Super Perfect"`**, face 52 (40's art for now), **HP 8230, STR 60, POW 59, END 65**. Look at the name: the C touches the left panel's right border and the closing quote is hidden under the portrait (section 1) |
| Database (map 6,6) after the Cell Games | A `Cell, "Perfect"` row. If you scanned Cell in two different fights, Left/Right arrows show and page through those entries (the same stats, since 21-24 are equal). Then a separate **`Cell, "Super Perfect"`** row with no arrows. Its panel shows the same name overflow as the scan screen |

Then pick a name from section 1: keep it, or one of the options.

Watch for: whether Select works during a fight at all (L, from r31); whether the portrait really covers the quote (L: OBJ over BG priority not traced).

## 8. Concerns

1. **The requested name does not fit the info screens** (section 1). I built the literal name and did not pick a variant for me. C (measure), L (look).
2. **The r31 test plan and two bible rows are wrong for enemies** (section 3). The fight stats I see differ from what r31 promised. C (listings).
3. The database writer sweep cannot see a computed offset or a bulk copy. S for "only two writers".
4. Where the database object sits on map 6,6 is not traced (L). A second constructor of the same object (`@0x08019134`) has no reference that the tool finds.
5. Not seen in an emulator. Everything above is proved by bytes, listings, a mock render and tests.

## 9. Files

- Patch: `scripts\permanent\patches\superperfect_cell.py` (edited). Tests: `scripts\permanent\tests\test_superperfect_cell.py` (edited).
- Study and tools: `scripts\one-time\2026-10-23-r33-build\` (`listings\`, `db_bit_sweep.py` and `.txt`, `name_fit.py`, `.txt` and `fit_*.png`, `copy_files.py` and `.txt`, `diff_proof.py` and `.txt`, `suite_final.txt`, `lint.py`, `bible_rows.md`, `backup\`). `backup\` holds the test file only: I edited the patch before I took a backup. Its r33 edits are the ones listed in section 6.
- Nothing under `data\` or `art\` was written. `inject.py` was not run. No `cd` in any shell call.
