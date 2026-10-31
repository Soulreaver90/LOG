# r37 report: chamber fight prototype, Gohan vs Goku in the training room

Brief: `docs\tasks\2026-10-24-chamber-proto\chamber-proto.md`. Base: r36 `eb4a1b4155eca4fa408bafe8c47949c67f85aa3d` (the in-memory r36 list equalled the r36 file before any edit). Built 2026-10-24 3:06 AM (build-log time). Labels: CONFIRMED (C), LIKELY (L), SPECULATIVE (S). Work files: `scripts\one-time\2026-10-24-chamber-proto\`.

| SHIPPED | Where |
|---|---|
| Re-check of the study's prototype plan on r36: all addresses still valid, one correction (types 96, 97 are not free) | Section 1, `verify_r36.txt` |
| Gohan (Demon Clothes) vs Goku (`set:60`) as an enemy with AI 98, in room 6,70, with a scene, a win path and a loss path | `builds\log2_poc_r37.gba`, patch `chamber_spar` |
| Proof: SHA-1, a diff with every run named, suite 604 OK (578 + 26 new), enemy frame sheet | Section 3 |
| Test save by exclusive create, with my steps | Section 4 |
| Plan (not built) for the chamber arena and Trunks vs Vegeta, with final decisions | Sections 5 and 6 |

| PENDING | Why |
|---|---|
| In-game look and feel | Not run in an emulator. Proved by bytes, decode and tests only |
| The four dialogue lines | Placeholders, for me to write (section 2) |

---

## 1. Re-check of the study plan on r36

Tool: `verify_r36.py` (output `verify_r36.txt`, 39 OK lines). Every item below is CONFIRMED on r36 unless it says otherwise.

| Item (study section 2 and 11) | r36 |
|---|---|
| Map table `rom:0x409368`, literals `rom:0x5ADC`, `0x5D5C`, `0xEBD8`; map 6,70 = entry 175 `rom:0x40B9B0`, combat +8 = 1, music 29 | Still valid |
| 6,70 region list `rom:0x3FB80C` (count 4) with walk-in items `rom:0x3FB7D0`, `0x3FB7E4`, `0x3FB7F8` (factory `0x0800D7E1`, trigger `0x0800D765`), tables `rom:0x3D2D3C`, `0x3D2E38`, `0x3D2F44` | Still valid. **Shape note:** the list is 8-byte `{condition, item}` pairs, not plain pointers |
| 6,70 spawn list `rom:0x3FB7A4` (count 6): Yamcha NPC `set:156` at 128,136; enemy record `rom:0x3FB724` (bytes as the study) | Still valid. NPC items are 0x18 bytes and enemy items 0x20 bytes (2 more fields than the study lists) |
| Event struct `rom:0x3FB71C` = `{0x080106B3, 0x083D2DE4}`; Yamcha seq 3 `push 156,3 ; ext 104 ; push 156 ; ext 85` | Still valid |
| Ext handlers 38, 49, 70, 73, 82, 83, 84, 85, 88, 98, 104, 109, 110 | Still valid (table `rom:0x3B5D28`) |
| Enemy table `0x086D56AC` (3 literal pools), death descriptor `0x086FF3C4` (+8 = `0x0801A82D`) | Still valid |
| Free enemy type 95 (`rom:0x6D5F94`, HP 5, AI 8) | Still free: no spawn, no pointer, no scouter entry (three shapes). Equals the base ROM |
| Free types 96, 97 | **Not free (correction):** scouter entries 107 and 111 name them at +0x10. Not used |
| Game-over table `rom:0x3B63B4`, only literal `rom:0x8870`, no other word into it; Goku line at word 14 (portrait 63) | Still valid. **Gap in the study's step 4:** word 15 after the Goku line is END, with no warp. The loss path needs a warp record (built, section 2) |
| `ext 73 (0, 53)` and `ext 73 (0, 157)` | Valid: the reverse lookup copy (`rom:0x800000`) has entry 0 = 53 and entry 2 = 157 |
| No enemy spawn uses sets 53 or 60 | Still valid |

No address moved, so the build went ahead.

## 2. What was built (r37, patch `chamber_spar`)

Files: `scripts\permanent\patches\chamber_spar.py`, `scripts\permanent\tests\test_chamber_spar.py`, one line appended to `scripts\permanent\build_list.txt`.

**Design: a fourth sparring partner in the vanilla room, cloned from Tien's three items (C for the bytes, L in game).**

1. **Enemy:** type 95 becomes Goku: HP 3500, AI 98 (Krillin's and Tien's sparring AI), STR/POW/END 34/36/34, EXP 0, boss death descriptor. These are the study's chamber-time numbers (S).
2. **Map 6,70:** new copies of the spawn list (8 items: the 6 vanilla + NPC Goku + enemy Goku) and the region list (5 pairs: the 4 vanilla + one walk-in region). The old lists stay as they are.
3. **Gate:** the NPC Goku and the region need `flag:214` (Tien beaten) and `flag:195` (Cell beaten). With those flags the vanilla partners are all off, so only Goku is in the room.
4. **Scene** (walk into the room): sound 50, fade out, `ext 73 (0, 53)` (Demon Clothes), `ext 70 (0)` (Gohan leads), fade in, two lines, `ext 104 (60, 7)` (Goku becomes the enemy where he stands), `ext 85 (60)` (HP bar).
5. **Win** (Goku's death event): Goku raises his arms, the HP bar slides out, two lines, fade, HP and EP refill, `ext 73 (0, 157)` (gi back), warp to 6,3 (Tien's spot). No flag is set, so the fight repeats on each visit.
6. **Loss:** game-over word 4 points at a copy of the partner picker with one test first: flags 214 and 195 go to the vanilla unused line "GOKU: Good fight!  Keep working and maybe you'll beat me next time.". Word 15 (END after that line) points at a copy of the vanilla loss warp with `ext 73 (0, 157)` after the fade. The Yamcha, Krillin and Tien picks give the same index as vanilla for all 16 flag combinations (test).

**Placeholder dialogue (I will write).** All four lines are placeholders. They live in `chamber_spar.LINES`.

| When | Speaker, portrait | Placeholder |
|---|---|---|
| Before | Goku, 63 | "GOKU: Gohan! Show me how strong you've gotten!" |
| Before | Gohan, 56 (pre-chamber face) | "GOHAN: Okay, Dad! I won't hold back!" |
| After a win | Goku, 63 | "GOKU: Wow, Gohan! You're getting really strong!" |
| After a win | Gohan, 56 | "GOHAN: Thanks, Dad! That was fun!" |
| After a loss | Goku, 63 | Vanilla line (not a placeholder) |

**Known limits.**
- Gohan stays the leader after the fight. The scene cannot read the old leader without a new variable (C for the design).
- The gi restore hard-codes `set:157` (entry 2). This is right after Cell, which the gate requires (C for the gate).
- On a loss, `ext 73` runs on the dead player under the black fade. It makes the same player call (`+0x28`, 0) that the vanilla `ext 38` makes on that player one op later. LIKELY safe; my test covers it.
- AI 98's projectiles were not traced. If they use the enemy set, Goku's ki blasts come from `set:60` (L).

## 3. Proof

- **r37:** `builds\log2_poc_r37.gba`, SHA-1 **`3877033c65d724a299a364f66a4c3d75a4df4566`**. It equals the in-memory build of `build_list.txt`. The build added one line to `docs\build-log.md`.
- **Diff r36 to r37** (`diff_proof.py`, `diff_proof.txt`): **590 bytes in 16 runs, 0 outside a named site. Same size.** C.

| Region | Runs | Item |
|---|---|---|
| `rom:0x3B63C4` (3 bytes) | 1 | Game-over word 4 to the picker copy |
| `rom:0x3B63F0` (4 bytes) | 1 | Game-over word 15 to the Goku loss warp |
| `rom:0x40B9B3` (2 bytes) | 1 | Map 6,70 counts 4, 6 to 5, 8 |
| `rom:0x40B9C0`, `rom:0x40B9C4` (3 + 3 bytes) | 2 | Map 6,70 list words to the copies |
| `rom:0x6D5F98`, `0x6D5F9C`, `0x6D5FA0` (2 + 1 + 3 bytes) | 3 | Type 95 HP, AI, STR/POW/END |
| `rom:0x909078`-`0x9092BF` (569 bytes, was `FF`) | 8 | New data right after r36's last allocation: condition, scene table and records, win table and records, event struct, picker copy, loss warp, NPC, enemy, region, two lists |

- **Decode of the new tables from the r37 file:** `decode_new.txt` (`decode_new.py`, the study's decoder).
- **Suite:** 604 tests, OK, 0 skipped (`suite_final.txt`). Before any edit: 578 OK (`suite_before.txt`).
- **New tests (26, `test_chamber_spar.py`):** base = r36; type 95 before and after, used by the new spawn only (three shapes), types 96 and 97 not free; list copies keep the vanilla items, only entry 175 names the lists; the new items equal Tien's with only set, type, condition and table changed; the condition is `flag 214 and flag 195`; the scene, win and loss decode as designed; no new record sets a flag; every path that puts on the Demon Clothes puts the gi back; the picker equals vanilla for every other flag mix; placement after r36; diff in named sites only; r37 file equals the build; 28 fail-closed sites; the save and ROM pair.
- **Changed tests (same count):** `test_superperfect_cell.py` builds its "rom" from the list up to `superperfect_cell` (so its r36 pins stay true); one test renamed to `test_build_list_has_superperfect_cell_after_piccolo_gi_scene`; its r35 check builds the r36 list. `test_art_inject.py`: the pinned list adds `chamber_spar`. Backups: `scripts\one-time\2026-10-24-chamber-proto\backup\`.
- **Enemy frames:** `scripts\one-time\2026-10-24-chamber-proto\goku_set60_enemy_rows.png`, set 60 from r37, anims 0-6 and 12 (the AI 98 rows), 4 dirs each, 2-4 frames per row. Every row is there (C by sheet).

## 4. My tests

Files (all by exclusive create, `make_files.txt`):

| File | What |
|---|---|
| `builds\log2_poc_r37_spar.gba` | Byte copy of r37 |
| `builds\log2_poc_r37_spar.sav` | `log2_poc_r36.sav` with slot 1 changed: flags 212, 213, 214 set, map 6,3 at (272,336). SHA-1 `4ca6f109e12693512b579262cb11711d2bc68d06` |
| `builds\log2_poc_r37.sav` | Byte copy of `log2_poc_r36.sav` (the plain r37 pair) |

The r36 states (`.ss1`-`.ss5`) were not copied or checked for r37.

**Steps:**

1. Open `log2_poc_r37_spar.gba` in mGBA. Load **slot 1**. You are Gohan (gi), Level 40, on map 6,3, just below the door of the training room.
2. Walk up one step into the door.
3. **Expect:** the room loads and Goku stands at the top. The screen fades, Gohan is in his purple Demon Clothes, and two lines show (Goku, then Gohan).
4. Goku fights you with the HP bar at the top. **Pass:** he moves, punches and is knocked down like Tien does, and no frame looks wrong.
5. **Win:** Goku raises his arms, two lines, fade, you are on 6,3 below the door in the gi, HP and EP full. Walk in again: the fight repeats.
6. **Loss:** the Goku line "Good fight! Keep working..." shows, fade, you are on 6,3 in the gi. **Pass:** no "You have died!" and no title screen.
7. **Extra checks:**
   - Enter the room as Super Saiyan Gohan. **Expect:** the Demon Clothes and normal form after the fade.
   - Watch Goku's ki attacks, if he uses any. **Expect:** normal blasts, no garbage tiles.
   - Scan Goku with the Scouter during the fight. **Expect:** no scan result and no crash (type 95 has no scouter entry; the game handles that case, C by listing).

> [!WARNING]
> At Level 40 (STR 70) this Goku (STR 34) will be easy. The numbers are the study's guess for the chamber point of the story. I set the final stats (section 6).

---

## 5. Plan, not built: move the fight into a chamber arena and hook it into the chamber scenes

Addresses re-checked on r37 (`verify_plan.py`, `verify_plan.txt`), C unless marked.

**(a) Arena map 9,8**

1. **Map table:** 327 entries end at `rom:0x40DAF0`, and the next bytes are other data, so a new entry needs a moved table. Copy the 327 entries to the expansion area, add entry 327 = zone 9 area 8, repoint the 3 literals (`rom:0x5ADC`, `0x5D5C`, `0xEBD8`) and change the count at `@0x0800E0AC` (`ff 20 48 30`: 0x147 to 0x148, for example `add r0,#0x49`). The visited-map table `rom:0x6F6D8C` and its bit count (297) are not traced for a new map (risk: the area map screen).
2. **Entry 9,8:** copy entry 9,3 (layout and tiles of the antechamber) or 9,4, then set +8 = 1 (combat), music by +0x24 (final call), and new lists: one exit region, the fight region, the NPC and enemy items (the r37 items with their conditions removed or set to the scene flag).
3. **Fight items:** the r37 shapes move as they are: walk-in region, NPC item, enemy item with the death event. The table changes are new tables, not edits.
4. **Loss:** extend the game-over picker. Record 0 (`rom:0x3B6104`) tests map 6,70 only. A copy must also test map 9,8 and jump to the picker, which then picks Goku (14) or Vegeta (8, "Did you really think you could beat me? Pathetic.") by a story flag. Each line needs a warp record after it (as r37 word 15). The warp goes back into the story (see 4 below), not to 6,3.
5. **Hooks into the story** (each a table word in the vanilla scene, through a type 5 record or a copy):

| Fight | Hook (r37 state) | After the fight |
|---|---|---|
| Gohan vs Goku (before) | V/T exit seq 33. Its word `rom:0x3DE774` already points at the r28 copy `rom:0x89A9C0`. Edit that copy's table word, not the vanilla record | Win and loss tables end with a warp back to 9,3 and a type 5 jump to the rest of seq 33 (SET 149, ext 70 (2), load 9,1). Each tail must run once |
| Gohan vs Goku (after the time jump, armor) | Chamber exit seq 3. Both type 5 words (`rom:0x3CF7E4`, `0x3D1530`) point at the piccolo_gi_scene copy `rom:0x89B158` | The vanilla seq 3 bump (level + 1, ext 82 (0), ext 83 (0,2)) runs before the fight or once after, not twice |

6. **No new flag is needed** while the fight is inside a one-shot scene. A retry after a loss needs one flag; the free-flag list is still not traced (S).
7. **Effort:** M. Risk: the map table move (3 literals, 1 count, the visited table) and the scene tails.

**(b) Trunks vs Vegeta**

1. **Enemy:** a second free enemy type is needed. Type 95 is now Goku; 96 and 97 have scouter entries. Options: reuse a scouter-named placeholder (96 or 97) and accept the scan entry, or grow the enemy table (3 literal pool words: `rom:0xE79C`, `rom:0x17A38`, `rom:0x1912C`), or swap Goku's type per fight with a second copy of the HP and stats (S: not traced how the type is read after spawn, the enemy keeps a pointer at +0x180).
2. **Sets:** Vegeta `set:137` (before) or `set:138` (armor after the chamber); Trunks is the player: jacket entry 12 (`set:128`) for fight 1, armor entry 13 (`set:129`) with the +15 grade for fight 2.
3. **Scene:** chamber entry table `rom:0x3DDE0C` seq 21 (vanilla word `rom:0x3DDE5C` = `0x083DDD22`), after Vegeta and Trunks walk to the door and before SET 144. Before: `ext 80 (3) ; ext 70 (3)`. After: `ext 81 (3) ; ext 70 (1)`, as the study section 3.3.
4. **Fight 2:** V/T exit table `rom:0x3DE6F4` seq 1 (word `rom:0x3DE6F4` = `0x083DDE68`, vanilla). Add `ext 73 (3, 129)` and remove the vanilla level + 1 if the fight gives its own bump.
5. **Loss line:** the unused Vegeta line (index 8) and Trunks line (index 22) are in the game-over table; each needs a warp record after it, as in r37.
6. **Effort:** M for one fight with an existing AI. Risk: the second enemy type, and a Vegeta with AI 98 that fights like Tien.

## 6. Final decisions

| # | Decision | Needed for | Options (the task's lean in bold) |
|---|---|---|---|
| 1 | The four dialogue lines of the prototype, then the chamber scenes | All | my text from the show |
| 2 | Goku's stats (HP, STR, POW, END) | All Goku fights | **Study guess 3500, 34/36/34 for the chamber point**; higher for a post-game test |
| 3 | Keep the training-room fight in later builds, or remove it once the chamber arena exists | (a) | **Keep it as a repeatable post-game spar** or remove |
| 4 | Gohan's outfit per chamber phase | (a) | Demon Clothes before (as r37); armor after needs the two new appearance entries of study section 3.1 |
| 5 | Goku's look in the armor phase | (a) | **`set:60` gi** (exists); `set:61`; new armor art (L effort, no source art in LoG II or Buu's Fury) |
| 6 | AI per opponent | (a), (b) | **AI 98** (sparring, as r37); AI 21 (Yamcha, Androids 17 and 18); new AI data (not traced, L) |
| 7 | Win and loss story effect | (a), (b) | **Loss continues the story with the loss line (no retry, no flag)**; retry needs one free flag |
| 8 | Chamber arena look | (a) | **Reuse 9,3's layout** (no new tiles); a white chamber look needs new tiles or a Buu's Fury map port (L) |
| 9 | Fight music | (a), (b) | Map music via +0x24 or ext 49: tracks 29 (spar room), 33, 19, 40 (study section 9) |
| 10 | Trunks' outfit and grade per fight, Vegeta's set (137 or 138) | (b) | **Jacket `set:128` then armor `set:129` with the +15 grade; Vegeta 137 then 138** |
| 11 | Level and stat bump size at the time jump | (a), (b) | **Vanilla level + 1 (no double bump)**; a larger `level + n` |
| 12 | Second enemy type for Vegeta | (b) | **Reuse type 95** (the sprite comes from spawn +0x10, so Vegeta can use type 95 if he shares Goku's stats and AI); type 96 or 97 (its scouter entry shows); a grown enemy table |

## 7. Concerns

1. Not seen in an emulator. The scene timing, the fade around the outfit change and the AI 98 behaviour with `set:60` are LIKELY, not CONFIRMED.
2. Files edited outside the new patch and test: `test_superperfect_cell.py` (built up to its own patch; one test renamed) and `test_art_inject.py` (pinned list). Both were needed because the build list grew; no pin value changed except the list.
3. `docs\RE-BIBLE.md` not edited. Bible rows: `scripts\one-time\2026-10-24-chamber-proto\bible_rows.md` (tag CPR).
4. Nothing was written under `data\`, `scripts\one-time\2026-10-24-hud-ki\`, `art\base-audit\` or `scripts\one-time\2026-10-23-base-audit\`. No ROM, save or state was overwritten.
5. **I broke two brief rules.**
   - Never `cd`: about six Bash calls started with `cd` to the LOG root or `/tmp`. They include the r37 build and two test runs.
   - Write and Edit only: I appended the `build_list.txt` line with `printf >>`, edited two report lines with `sed -i`, and made the backups with `mkdir -p` and `cp`.
   - Some read-only tool runs used `py -3 -I` instead of `-P`.
   - Checked afterward: every edited or new file is LF, ASCII, no byte order mark, no en or em dash. The r37 file SHA-1 equals the in-memory build. I did not undo any of these steps.
6. **Shared tree.** `build_list.txt` now ends with `chamber_spar`, so the next build or inject by any task (sp-portrait2 included) contains this fight, and the name r37 is taken. `test_before_is_r36` pins the r36 SHA-1, and the r37 file tests pin the r37 file. The next art table change breaks these pins, as it broke the r36 pins.
7. The ext 14 field: it reads the leader's max HP, not POW (the name in `sdis.py` is wrong). The vanilla loss warp gives back half of max HP (L for what var 13 does).
