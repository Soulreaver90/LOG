# Save slot 3 report: a real state just before the Cell Games

Date: 2026-10-18. Brief: `docs\tasks\2026-10-18-save-slot3\save-slot3.md`. ROM: USA base, SHA-1 `18e0715d...` (read through its copy `scratch\ghidra\log2.gba`, same SHA-1).

Labels: **CONFIRMED** = proved from ROM bytes, code or a test. **LIKELY** = strong evidence, my test pending. **SPECULATIVE** = a guess.

## Result

| Item | Value |
|---|---|
| New save | `test-data\saves\log2_lv40_cellgames_v2.sav`, 8192 bytes, SHA-1 **`159601a376596afbd9d4124845a3b1355b46a839`** (`log2_save.py build <base> <out> --set cellgames2`) |
| Slots 1 and 2 | Byte for byte the `c755acf0` file (tested). Only RAM bytes 0x3EB, 0x3EC and the slot 3 checksum 0x444-0x447 differ |
| Slot 3 change | Visited bits 294-296 (maps 14,1, 14,2, 14,3) now clear. Flags, party, outfits, items, leader and place are unchanged, because the evidence says they already are the flag 191 state |
| Tests | `test_save.py`: **30 OK** (19 old + **11 new**). Whole suite once at the end: **277 OK** |
| ROM, other saves | None written. No .sav or ROM overwritten |

## 0. Most likely reason I saw "all post-Cell": the save state, not the save

**CONFIRMED (bytes and code). That I loaded the state: SPECULATIVE, but it explains "all three slots" exactly.**

- The game reads the EEPROM once at boot into a RAM shadow at `0x0203E000` (pointer `0x03003898`). Slot load `0x08003F9C` copies a slot with `0x08021526`, a DMA from `[0x03003898]` plus the slot offset.
- The read-dword routine `0x08021ACC` has two callers. `0x080214AC` is in `0x08021454`, reached only from boot (`0x080001B4` > `0x0801F248` > `0x08021454`). `0x08021C80` sits inside the write routine `0x08021CB0` (a read-back, LIKELY). So nothing on the title, file select or Continue path refills the shadow from the chip. CONFIRMED (BL scan and pool words).
- So an mGBA save state taken after boot carries its own slot image. Load the state, choose Continue, and the game shows the slots in the state, not the .sav next to the ROM.
- `archive\builds\log2_poc_r12.ss1` through `log2_poc_r16.ss1` are one file (all five hashed: SHA-1 `47f898f3`). It is a title-screen state. Its shadow at `0x0203E000` equals `test-data\saves\log2_lv40_postcell.sav` (`1973041f`) in RAM bytes 0x000-0x447, all the bytes the game uses:

| Slot in the state | Leader | Map | Position | Flag 195 |
|---|---|---|---|---|
| 1 | Gohan | Capsule Corp 6,1 | 432,591 | set |
| 2 | Gohan | East District 439, 2,29 | 248,285 | set |
| 3 | Gohan | Capsule Corp post-Cell spawn 6,3 | 376,408 | set |

- That is the old post-Cell save: all three slots are after Cell. Slot 2 is East District 439, not Roshi's Island.
- Second, weaker lead (SPECULATIVE): the mGBA recent list (`%APPDATA%\mGBA\qt.ini`, read only) now reads r16, **r12**, r14. So r12 was opened after r14. `log2_poc_r12.sav` is the old post-Cell file (`1973041f`).
- mGBA config has no custom save folder (`config.ini` has no path key), so a cold boot reads the .sav next to the ROM.

## 1. State diff: "after Cell" against "flag 191 just set"

Search rule (CONFIRMED by the walk): a path is LATE when it assumes or has set any of flags 192-196, or it runs on map 14,2 or 14,3 (behind the 14,1 barrier). Flag 191 is not late.

| State | After Cell | Flag 191 just set | Evidence | Label |
|---|---|---|---|---|
| Flag 192 | set | clear | Only SET `0x083E93E2`, map 14,3 scene `0x083E93E8` | C |
| Flag 193 | set | clear | Only SET `0x083E8D94`, map 14,2 scene | C |
| Flag 194 | set | clear | Only SET `0x083E9BBD`, map 14,3 | C |
| Flag 195 | set | clear | Only SET `0x083EC6A4`, map 14,3 `0x083EC758` | C |
| Flag 196 | clear (set only at the farewell) | clear | Only SET `0x083DCEF9`, Lookout object `0x08403F60` (needs 195) | C |
| Flags 0-191 | as listed in `POSTCELL_FLAGS` | the same | No other flag has a LATE-only SET or CLR site; no flag is set only between 191 and 192 | C (walk, limits below) |
| Flag 29 | set | set | All 14 "CLR 29" byte hits are `NN 00 00 1D 02 1C 06` (record header, then push 14,3), not code | C |
| Gohan outfit | entry 2 (ext 73 (0, 58) Rage `0x083EA369`, then (0, 56) `0x083EBFFC`) | entry 2 (chamber exit `0x083DB62B`) | Both ext 73 after 191 are LATE-only | C |
| Vegeta, Trunks outfits | 137, 132 | 137, 132 | No ext 73 for them after the 12,6 scene (flag 151) | C (walk), L (order before 158) |
| Hercule | joins at level 40 only with trophies 302, 303, 305, 306 (5 sites) | ROM default record, not in party | All ext 79/80/98 (5) are LATE-only and need 195 | C |
| Goku | leaves the party, ext 91 (4) `0x083EC737` | in the party, leads | LATE-only. The post-Cell test slots keep him on purpose | C |
| Leader | Piccolo after Cell (ext 70 (1) `0x083EC00F`) | Goku (chamber exit ext 70 (4)) | Slot 3 keeps Goku: the 14,1 barrier needs leader 4 | C |
| Party bits, levels | as chamber exit (all ext 79-82, 98 run with no assumed flag above 158) | the same | `scripts\one-time\2026-10-18-save-slots\slot3\extops.txt` | C (walk), L (order before 158) |
| Items | Dragon Radar, Scouter | the same | Item ops above flag 158: side quests (206-221) and Dende's ball removal at 191 | C |
| Place | Capsule Corp 6,3 (376,408) after the fight | Dende's Lookout (the 191 record loads no map) | Record `0x083DD2F0` | C |
| Visited maps | arena 14,1-14,3 visited | not visited | Bits 294-296 (table `0x086F6D8C`); the arena landing needs 191 (world map region 25) | C (bits), L (no other path into zone 14) |
| Scouter entries | 0 in both test saves | 0 | Not story-driven; not changed | L |
| Opened chests, map objects | chest flags 241+ clear in both | clear | Map conditions have no test-and-clear mode; chests use their own flags | C |
| Quest table | "Talk to Dende" active | "Enter the Cell Games" active | `log2_save.py journal` | C |
| World map goal marker | Lookout (ext 102) | Cell Games Arena (ext 102) | Enter script `0x083FB868`, run with each slot's flags | C (script), L (102 = goal look) |
| Music | 1,2 2,1 3,3 4,1 4,76 6,1 6,22 8,32 8,47 9,1 11,1 test 196; 6,2 plays 37 while 151 and not 195 | pre-Cell tracks | Map music scripts | C |
| Gohan Super Saiyan 2 (hack) | available | not available | `ssj2_form` `step_ok` tests flag 195 | C |

**Search shapes and what each cannot find.**

| Shape | What | Result | Cannot find |
|---|---|---|---|
| A | Path walk (`story.py`) of every map-owned script and scene table: map lists +0x10, +0x14, +0x18, +0x1C, layout regions, name, variation, enter and leave scripts, and the `{0x080106B3, table}` sub-structs of `0x0800E77F` records. Flags are symbols, jz forks | LATE-only SET: 192-196 only. No LATE-only CLR | A scene started only from Thumb code or a computed pointer. Two walks hit their caps: the chamber exit table `0x083DBDD4` and the world map enter script (run concretely instead) |
| B | Literal `push N ; ext 27/28` byte scan | 43 hits the walk did not reach: byte overlaps (14 "CLR 29", 301) or early and side content (14-16, 78-84, 114-116, 156, 167-180, 304). No test of flags 191-196 within 0x300 bytes before each, except Bulma's table head `0x083CF3AB`, where 156 is set on the not-195 path | Flag numbers built at run time |
| C | ext 27/28 without a literal push | 34 byte pairs: type 2 text headers `NN 00 02 1B/1C`, push-list bytes, `push 2 ; op 27`, packed text | A computed SET whose bytes also look like a literal push |
| D | Thumb BL to the flag setter `0x08003E5E` and clearer `0x08003E74` | Only the ext 27/28 handlers | A write through a register-based struct pointer |
| E | Pool words in the flag bytes `0x03000F44`-`0x03000F75` | None | Same as D |

## 2. Visible "post-Cell" signs, ranked

| Rank | Sign | In the current slot 3? | Label |
|---|---|---|---|
| 1 | All three slots post-Cell, slot 2 at East District 439 | Not in the .sav. It is the old image inside the r12-r16 `.ss1` state (section 0) | C (bytes), S (that I used the state) |
| 2 | The same, from opening r12 (old .sav) | Not in the .sav (mGBA recent list) | S |
| 3 | Arena maps marked as visited | Yes. The readers found (by the table literal) are the R area map, which needs header +1 bit 2 (debug teleport only), and ext 23, which no script calls. Fixed in v2 | C (bits), L (not visible in normal play) |
| 4 | Everyone at level 40, Gohan in the gi, Gohan Super Saiyan | Yes, by design (test save; my gi rule 6:29 PM; Super Saiyan comes from the chamber) | O |
| 5 | Any flag-driven line, object, marker, music or Journal entry | No. Every one checked reads "before the Cell Games" (section 4) | C |

## 3. The new slot 3

- Built from the "flag 191 just set" state: the old slot 3 plus visited bits 294-296 clear.
- Leader Goku, Dende's Lookout 9,1,1 at 768,832 (world map landing `0x083FBBFC`). The Dende record that sets 191 loads no map, so the game leaves the player on the Lookout.
- `log2_save.py`: new story `cellgames2`, `UNVISITED`, `ARENA_VISITED`, preset sets `cellgames2` and `cellgames2_arena`. The old presets and the default (`cellgames`) are unchanged.

## 4. Proof per sign (v2 slot 3, `visible.py` and the journal)

| Sign | Condition | v2 slot 3 reads | Label |
|---|---|---|---|
| Dende, map 9,1 object `0x08403F3C`, table `0x083DD380` | entry 0: `push 191 ; flag ; jz ; push 9 ; end` (bytes `00 BF 02 13 13 03 00 09 11` at `0x083DD1AF`); entry 9 = `0x083DD34C` | "DENDE: Good luck in the Cell Games, Goku!" | C (test) |
| Mr. Popo, `0x08403F08` | 156, 157 and not 195 | "MR. POPO: Hello there, Goku!" | C |
| Post-Cell Lookout crowd, `0x08403F60` | flag 195 | hidden | C |
| World map | arena ext 102 while 191 and not 195 | arena = goal, Lookout plain (post-Cell: the reverse) | C |
| Arena 14,1 crowd | not 195 (and leader tests) | Android 16, Yamcha, Tien, Piccolo, Hercule, Gohan, Vegeta, Trunks, Krillin stand there | C |
| Capsule Corp 6,14 Chi-Chi | 151 and not 195 | "If Cell wants a tournament, then it will have to have rules..." | C |
| Capsule Corp 6,5 Bulma | Bulma table: 195 goes to entry 19 | "Dr. Gero put bombs into all of his Androids ... I wonder if Cell has one too..." | C |
| Capsule Corp 6,3 Roshi | 151 and not 195 | "Back in my heyday, I would have joined in this tournament!" | C |
| Gohan's house 2,1 Chi-Chi "How can he be gone again?" | 195 and not 196 | hidden | C |
| Roshi's Island 11,1 post-Cell trio | 195 | hidden | C |
| Super Saiyan 2 | `step_ok`: flag 195 | not offered | C |
| Journal | quest table | below | C |

`log2_save.py journal` on v2, slot 3 (main quests): **active "Enter the Cell Games"**; finished "Return the Dragon Balls to Dende on the Lookout", "Collect the seven Dragon Balls" and every earlier main quest; "Talk to Dende on the Lookout" hidden. Side quests "Train with Master Roshi", "Rescue the man kidnapped by the Warlord" and "Retrieve the Bait" stay active (unchanged from the old save).

## 5. Option: the Cell Games Arena door

- `log2_save.py build <base> <out> --set cellgames2_arena`: slot 3 at map 14,1,1, 264,304, the world map landing (`0x083FBDC4` = push 14,1,1,264,304 ; ext 38). Same story as v2.
- Goku leads, so the barrier scene (cond `0x08408DB0`: leader not 4 and not 195) does not start. Not built; the Lookout slot stays.

## 6. My test plan

1. **Rule out the state.** Close mGBA. Open the ROM with File > Load ROM. Do **not** load a state (no F1, no Load State). Turn off the cheat `0202b32d:02`.
2. At the title, choose Continue. Check slot 2. Expected: Master Roshi's Island. If it shows East District 439, the game is reading an old image: you loaded a state or the wrong ROM.
3. For r16 now: `log2_poc_r16.sav` is the `c755acf0` file (hashed at the end of this session). Its slot 3 has the same story as v2. For r17: I copy v2 to `log2_poc_r17.sav`.
4. **Slot 3.** Expected: Goku on Dende's Lookout. Talk to Dende: "Good luck in the Cell Games, Goku!". Mr. Popo: "Hello there, Goku!". No Android 17, 18 or Tien group on the Lookout.
5. Open the Journal. Expected: "Enter the Cell Games" active.
6. Press A at the take-off spot. On the world map the Cell Games Arena is the goal marker, not the Lookout.
7. Optional: land at Capsule Corp. Chi-Chi talks about tournament rules; Bulma wonders if Cell has a bomb.
8. Fly to the arena. Expected: the whole crowd, Krillin's "a bit of a snag" line, the barrier opens for Goku, then "GOKU: I'll fight Cell first."
9. If you test with save states, make a new one after a cold boot with the new .sav. The r12-r16 `.ss1` files hold the old post-Cell slots.
10. Tell I what made you read it as post-Cell, if anything still does.

## 7. Files

| File | Change |
|---|---|
| `test-data\saves\log2_lv40_cellgames_v2.sav` | new |
| `scripts\permanent\rom\log2_save.py` | `cellgames2` story, `ARENA_VISITED`, `UNVISITED`, preset sets `cellgames2` and `cellgames2_arena`, docstring |
| `scripts\permanent\tests\test_save.py` | `CellGames2SetTests` (11 tests), `_literal_sets` helper |
| `scripts\one-time\2026-10-18-save-slots\slot3\` | `story.py`, `classify.py`, `visible.py`, `shapes.py`, `owner_of.py`, outputs `classify.txt`, `extops.txt`, `shapes.txt`, `diff_s3_s1.txt`, `suite.txt` |
| `docs\RE-BIBLE.md` | source `SS3` in the list; 6 rows in section 8, 5 rows in section 11 |

All written files: LF, no byte order mark, no en or em dashes, no control characters (checked).

## 8. Concerns

1. **The brief's premise does not hold.** The old slot 3 already had the flag 191 story state. The only state change in v2 is three visited bits that normal play does not show. If I did not use a state or r12, the cause is still open: ask what he saw.
2. **Walk limits.** The chamber exit table and the world map enter script hit the walker's caps (both checked by other means). A scene started only from Thumb code is not covered. The visible-sign tool forks on unknown ext results, so it can list a branch the game never takes.
3. **Order before flag 158** of party, outfit and level ops comes from the assumed flags, not a traced run (LIKELY). Nothing changes between 158 and 192.
4. **The `.ss1` files** were not touched (not mine). Whether r17 should get a fresh state is my call.
5. **Brief deviation:** early in the session several read-only Bash commands used `cd` (surveys and one scratch-file patch inside my own `scripts\one-time\2026-10-18-save-slots\slot3\` folder). Nothing outside my files was written. I stopped once I noticed.
6. **Not tested in game.**
