# Chapter cards: test saves before each story card (report, 2026-10-30)

Brief: `chapter-test-saves.md` in this folder. Labels: CONFIRMED (C) = read from ROM bytes, save bytes or code. LIKELY (L) = strong evidence, no emulator run. SPECULATIVE (S) = a guess. Addresses are the base ROM unless the text says v5.

---

## SHIPPED

| Ask (brief) | Result | Label and proof |
|---|---|---|
| 1. One slot just before the scene of each story card 2-8 | Cards 2-6: new slots. Card 7: v5 slot 3 (checked). Card 8: v5 slot 2 (checked). Card 1: an empty slot | C: `presave_proof.txt` |
| 2. Base each slot on the nearest real save; set flags, map, position, party, leader, outfit | Base = v5 save slot 3 (6,16, flags to 156), the nearest save in the census. Flags, party bits, outfits and items set per card | C: `presave_build.txt`, `presave_flags.txt`, `presave_party.txt` |
| 2. Say which flags you set or cleared and why, and what you could not match | Table "Flags" and section "Known gaps" | C (flag sites), L (story order) |
| 3. Prove the target scene starts: trigger, table, record, condition, slot meets it | Table "The route of each slot" | C (bytes, conditions evaluated on each slot), L (play) |
| 4. Two files, 3 slots each, resealed; a ROM copy next to each; exclusive create | `log2_poc_r39_chapters_v5_pre_a.sav`/`.gba` and `_pre_b2.sav`/`.gba` in `builds\mockups\2026-10-25-chapter-cards\`. **Use `_pre_b2`, not `_pre_b`** (see the warning below) | C: SHA-1s below |
| 5. Tests if the builder is permanent | The builder is one-time (`presave_build.py`), so no new test. Full suite once: 883 tests, OK | C: `presave_full_suite.txt` |

> [!WARNING]
> `_pre_b.sav` is superseded by `_pre_b2.sav`. My first run cleared story flag 29 in the card 5 and card 6 slots. Every "CLR 29" site in the flag list is a record header that reads as an op (the bible CHP trap row, `rom:0x3D4874`), so the game never clears 29. Exclusive create kept `_pre_b` on disk. `_pre_b2` differs from it only in flag 29 in slots 1 and 2 (C, `presave_proof.txt`: "data bytes that differ ['0xb7'], story flags that differ [29]").

## PENDING

| Ask | Why pending | My step |
|---|---|---|
| The transitions in play | No emulator run | Play steps below |
| Cards 4, 5 and 6 need boss fights first | The card plays in the boss's death scene. No save point exists after the fight and before the card (C: each card table is the death event of the boss) | Win the fight (all six records are level 40, so the fights are short) |
| Levels, EXP, visited maps | Kept from the base save (level 40, all maps visited but the arena) | Say if you want story levels |

---

## Short answer

1. **Five new slots, one empty slot, in `_pre_a` and `_pre_b2`.** `_pre_b` is superseded (flag 29). Cards 2, 4, 5 and 6 start with one A press. Card 3 starts after a walk of about 33 px (4 cells) down.
2. **Cards 4, 5 and 6 have a fight first.** Card 4: Android 20. Card 5: Android 18. Card 6: Android 17, three times. The card plays in the scene after the last fight.
3. **Continue shows the chapter before each card.** Slot for card N shows Chapter N-1 (C, `chapter_cards.chapter_for` on each slot).
4. **Cards 7 and 8 keep the v5 save.** Card 7: slot 3 (you confirmed it). Card 8: slot 2 needs the whole Cell Games.

---

## Files and SHA-1

| File | SHA-1 | Label |
|---|---|---|
| `log2_poc_r39_chapters_v5_pre_a.sav` (cards 2, 3, 4) | `0a04aa03ad560f8b1373c572e67cfae73c0f2a40` | C |
| `log2_poc_r39_chapters_v5_pre_b2.sav` (cards 5, 6, empty slot 3) | `8bd87bfcda7cb96edaef74dc7defb447db6953fe` | C |
| `log2_poc_r39_chapters_v5_pre_a.gba`, `_pre_b2.gba` | `80cf4ab9b32d0ad802858294c1cc375ad0d1a1dc`, equal to the v5 ROM | C |
| Superseded, kept: `_pre_b.sav` (`d0b60986ae159241c7a9e49a0b8947f4bb64b564`) and `_pre_b.gba` (v5 copy) | Flag 29 clear in slots 1 and 2. Do not use | C |
| Base save `log2_poc_r39_chapters_v5.sav` (not changed) | `8b0b74f4896ba1a57666499305861f5f42c40a06` | C |

Every file was written with `open(path, "xb")`. The options block (`04 06 04 00`) and every slot are resealed. The bytes outside the slots equal the v5 save (C, `presave_proof.txt`: "bytes outside the slots equal the v5 save: True").

---

## One row per card

| Card | File, slot | Map, position | Leader | What you do | Label |
|---|---|---|---|---|---|
| 1 The Mysterious Youth | `_pre_b2`, slot 3 | Empty slot | n/a | Pick Continue on slot 3. Card 1 plays, then the new game | C (slot empty), L (play) |
| 2 Preparation | `_pre_a`, slot 1 | 3,4,1 at (128,164) | Gohan | Press A. Gohan flies to 3,6, the Z fighters arrive. Walk to Trunks at (216,456) and talk. After "Yeah dad, let's head home." the fade plays, then card 2 | C (route), L (play) |
| 3 The Androids Appear | `_pre_a`, slot 2 | 2,1,1 at (360,424) | Gohan | Walk down about 33 px (4 cells) into the yard. Goku's scene plays, then the fade 240 and card 3 | C (route), L (walk-in fires on entry) |
| 4 Into Gero's Lab | `_pre_a`, slot 3 | 7,18,1 at (224,132) | Vegeta | Press A. You fly to 7,19 and the Android 20 fight starts. Win. The post-fight scene plays, then card 4 where the fly-offs meet | C (route), L (play) |
| 5 A New Horror | `_pre_b2`, slot 1 | 8,48,1 at (536,124) | Vegeta | Press A. You fly to 8,49, the Androids talk, the Android 18 fight starts. Win. Piccolo flies to Kami, fade 90, card 5 | C (route), L (play) |
| 6 Perfection | `_pre_b2`, slot 2 | 11,1,1 at (384,564) | Piccolo | Press A. You fly to 11,4: Android 17 fight 1. Win. On 11,5 press A again: fight 2, then fight 3 on 11,6. Cell absorbs 17, Goku teleports out, fade 180, card 6 | C (route), L (play) |
| 7 The Cell Games | v5 save, slot 3 | 6,16,1 at (200,236) | Vegeta | As you played it | C (your play) |
| 8 The Champion's Hour | v5 save, slot 2 | 9,1,1 at (768,832) | Goku | Fly to the arena and play the whole Cell Games | C (flags), L (route) |

---

## The route of each slot

Trigger types (bible SAV row 657): `0x0800D839` = plain A press inside the rect (C). `0x0800D765` = walk-in: its test `@0x0800D730` calls the region action with no input test, then removes the region (`bl 0x0800BF6E` at `@0x0800D758`) (C, listing). That the region tick calls it while the player overlaps the rect is L: the whole-map rects of 3,6 region 0 (-15,-7)-(768,768) and 7,15 region 0 can only fire that way.

| Card | Start region (map entry list, item) | Condition, and the slot | Chain to the card (C, `presave_maps.txt`) |
|---|---|---|---|
| 2 | 3,4 region 1, item `rom:0x3F1D30` (`c3 c2 00 08 39 d8 00 08 69 00 91 00 98 00 b8 00`: script region, A press, rect (105,145)-(152,184)) | `rom:0x3F1D04` `00 16 02 13 00 1a 02 14 04 11` = flag 22 and not 26. Slot: 22 set, 26 clear, position inside | Script `rom:0x3F1D0E`: fly, `push 3,6,1,792,472 ; ext 38`, fly to (416,456). 3,6 region 0 item `rom:0x3F1F20`, cond `0x00020017` (23 clear), walk-in over the whole map, table `rom:0x3C0020` (Z fighters arrive, SET 23 at `rom:0x3C000C`). Trunks = 3,6 spawn 6 item `rom:0x3F1E74` (factory `0x0800B711`, cond 0, (216,456), table `0x083BFDDC`). Word 87 `rom:0x3BFF38` = v5 `0x0892F8C0`: `... 78 02 28 00 02 02 91 00 1a 02 1b` (fade 120, card 2, SET 26) |
| 3 | 2,1 region 11, item `rom:0x3EDD54` (`e1 d7 00 08 65 d7 00 08 a1 00 c9 01 c0 01 68 02 a0 88 3b 08`: scene region, walk-in, rect (161,457)-(448,616), table `0x083B88A0`) | `rom:0x3EDD48` `00 42 02 13 00 44 02 14 04 11` = flag 66 and not 68. Slot: 66 set, 68 clear, (360,424) is 33 px above the rect; the 8 px steps to (360,488) are open cells | Table `rom:0x3B88A0` [0]-[6] (Goku: "Did you have a good time in West City?"), word 7 `rom:0x3B88BC` = v5 `0x0892F8EC`: `19 02 31 00 f0 02 28 00 03 02 91 00 44 02 1b` (music 25, fade 240, card 3, SET 68) |
| 4 | 7,18 region 0, item `rom:0x3FD758` (A press, rect (201,113)-(248,152)) | Cond `0x00020056` = 86 clear. Slot: 86 clear, inside | Script `rom:0x3FD734`: fly, `push 7,19,1,160,560 ; ext 38`, fly to (200,376). 7,19 region 1 item `rom:0x3FD80C` (cond 86 clear, walk-in, rect (145,345)-(248,424), (200,376) inside): `push 14,1 ; ext 104` builds spawn 1, item `rom:0x3FD7A8` (type 6, Android 20), event `rom:0x3FD7A0` = `{0x080106B3, 0x083D5524}`. Word 46 `rom:0x3D55DC` = v5 `0x0892F998`, card 4 ops at v5 `rom:0x92FA8A` (v5 report) |
| 5 | 8,48 region 0, item `rom:0x403218` (A press, rect (513,105)-(560,144)) | Cond `0x0002007F` = 127 clear. Slot: 127 clear, inside | Script `rom:0x4031F4`: fly, `push 8,49,1,208,792 ; ext 38`, fly to (208,712). 8,49 region 0 item `rom:0x4033C8` (cond 0, walk-in, rect (-15,577)-(416,760), (208,712) inside), table `rom:0x3D8B60`; its [23] `push 0 ; ext 84` builds spawn 0, item `rom:0x4033A4` (type 4, Android 18), event `rom:0x40339C` = `{0x080106B3, 0x083D98AC}`. Word 47 `rom:0x3D9968` = v5 `0x0892FAA4`: `5a 02 28 00 05 02 91 00 01 02 56 00 7f 02 1b` (fade 90, card 5, HUD, SET 127) |
| 6 | 11,1 region 4, item `rom:0x406024` (A press, rect (361,545)-(408,584)) | `rom:0x405F9C` `00 91 02 13 00 94 02 14 04 11` = flag 145 and not 148. Slot: 145 set, 148 clear, inside | Script `rom:0x405FA6`: actors 121 and 76 fly in, `push 11,4,1,520,-32 ; ext 38`, fly to (352,224). 11,4 region 0 item `rom:0x406504` (cond 0, walk-in, rect (233,169)-(464,344)), table `rom:0x3E47F8` [6] `push 9,1 ; ext 104` (spawn 1, death table `rom:0x3E49F0`). That table [5] loads 11,5 at (336,88), inside 11,5 region 0 (item `rom:0x406624`, cond 0, A press, rect (313,73)-(360,112)), SET 146. Its script `rom:0x4065E8`: 11,6, `push 9,0 ; ext 104` (spawn 0, death table `rom:0x3E4B50`), whose [5] `push 9,4 ; ext 104` (spawn 4, death table `rom:0x3E6078`). Word 85 `rom:0x3E61CC` = v5 `0x0892FAD8`: `b4 02 28 00 06 02 91` (fade 180, card 6) |
| 7 | 6,16 region 1, item `rom:0x3FACA4` (trigger `0x0801087F`, rect (169,193)-(232,248), table `0x083D1534`) | Flag 151 and not 157. v5 slot 3: true; (200,236) inside | Your play (C). The trigger type `0x0801087F` is not traced |
| 8 | 9,1 world map exit, region 0 | Flag 191 set, 192-195 clear (C, v5 census) | World map, arena 14,1 (Goku leads, level 40 passes the barrier, bible SAV row 654), then every Cell Games fight. Option: the arena door slot of `log2_save` preset `cellgames2_arena` (14,1 at (264,304)) skips the flight; not built here |

Each slot map's every region and spawn, with its condition evaluated on the slot's flags and leader, is in `presave_proof.txt` (C, model of `condition_eval` `@0x08003F06`, bible BLP row 892).

---

## Flags

Rule (C for each site, L for story order): start from the base flags, keep those up to the card's flag minus 1, and clear the flags a script clears before that point. Every SET and CLR site of flags 0-200 (shapes `00 NN 02 1B` and `00 NN 02 1C`) with the map that runs it is in `presave_flags.txt`. The main-story order is the Journal chain (quest table `rom:0x6D68DC`): each quest is active at one flag and done at the next, for example "Meet Krillin and the others in the Northern Wastelands" active at 11, done at 26 (C).

| Card | Flags set in the slot | Cleared from the base, and why |
|---|---|---|
| 2 | 0-9, 11-20, 22 | 23 (3,6 arrival, after the A press), 26 and later (the story after the card). 171, 176, 181, 189, 190: see below |
| 3 | 0-9, 11-20, 22-23, 26, 28-31, 33-67 | 68 and later. 24, 25, 27 are clear in the base and in the game: set at card 2 and in 2,20, cleared when you leave home (2,5 region 2 and 2,6 region 0, `rom:0x3B9035`-`0x3B903D`, `rom:0x3B92DF`-`0x3B92E7`), which also sets 29 |
| 4 | 0-9, 11-20, 22-23, 26, 28-31, 33-70, 73-85 | 86 and later. 71 and 72 are clear in the base and in the game (5,1 region 1 script `rom:0x3F9628` clears them and sets 74) |
| 5 | 0-9, 11-20, 22-23, 26, 28-31, 33-70, 73-100, 108-113, 117-126 | 127 and later. 114-116 are clear in the base and in the game (CLR `rom:0x3D82E8`-`0x3D830C` in the generator table, C). 101-107 are clear in the base: each 8,37 region script sets and clears its own flag, and I did not prove the state after the puzzle (L; nothing on the card 5 route reads them) |
| 6 | 0-9, 11-20, 22-23, 26, 28-31, 33-70, 73-100, 108-113, 117-132, 134, 136-145 | 146 and later. 133 is clear in the base and in the game (SET `rom:0x3E042F`, CLR `rom:0x3E0D85`, C) |

**Flag 29 stays set (C).** The 14 "CLR 29" matches in `placement_sites.txt` all sit at record +2: the header type byte `00`, then a record that opens `1D 02 1C ..` (`push 14,x`). Example: `rom:0x3D4874` = `01 00 00 | 1D 02 1C 06 02 39` = push (14,3) ; ext 57 (bible CHP trap row). `presave_flags.txt` marks all 14 "HEADER ALIAS". No other shape clears 29: the varint form `01 3A 02 1C` has no match, and the one list form `3A 02 1C` (`rom:0x3BF493`) is inside a type 2 text record. An op-boundary test over every SET and CLR site of flags 0-200 flagged only these 14 (sites that start a raw map script also show, and are real ops).

**Base flags cleared in every slot.**

- 171, 176, 181: set by the leave scripts of 2,42, 2,43, 2,44 (C). That is the East District 439 side dungeon behind the Vegeta barrier (bible SAV row 655). Optional, so I cleared them (L).
- 189, 190: two of the seven Dragon Ball flags. The quest "Collect the seven Dragon Balls" tests 162, 163, 164, 185 and more, and is active at 158 (C, quest table). So they are set after card 7.

**Flags not set that the base also lacks.** 162, 163, 164, 187 are single `push N ; SET ; END` records with no holder found by my walk (C). The quest table makes 162-164 Dragon Ball flags (C), so they come after 158. 187 is likely a Dragon Ball too (S). 196-199 are clear: 196 is the farewell, 197-199 are Capsule Corp talk flags (S: optional).

## Party, leader, outfit, items

Ops decoded from each record start, not from bytes inside a push list (C, `presave_party.txt`). Record +0x14: bit 0 = in party (ext 79 / 91), bit 1 = ext 80 / 81, bit 5 = ext 82 (bible SAV row 651). Bits 2, 3, 4 and 6 are kept from the base record (`0x5C`), meaning not known. A character who has not joined gets `0x40`, the ROM default record value (C, `rom:0x1D9548`).

| Card | Party (+0x14) | Leader | Outfit (+8 entry) | Proof |
|---|---|---|---|---|
| 2 | Gohan `0x5F`; others `0x40` | Gohan | Gohan 1 (set 55) | 1,2 table `rom:0x3B7ADC` [8]: leave 3, join 0, bit1 on 0, leader 0. 2,4 `rom:0x3B8DD5` ext 73 (0,55) before SET 8 |
| 3 | Gohan, Piccolo `0x5F` | Gohan | Gohan 1 | 4,3 talk `rom:0x3C3298`: join 1, ext 73 (0,55), bit1 on 1; set level (1,10) with SET 57 |
| 4, 5 | Gohan, Piccolo `0x5F`, Vegeta `0x7F` | Vegeta | Gohan 0 (set 53) | Card 3 record ext 73 (0,53) `rom:0x3B8595`. 5,3 `rom:0x3CCA2E`: join 2, join 1, ext 73 (0,53), leader 2, bit1 on 2, bit1 off 1 and 0. 6,50 `rom:0x3D1FD7` bit5 on 2. Android 19 death `rom:0x3D4826`: bit1 on 1 and 0, SET 85 |
| 6 | Gohan `0x5D`, Piccolo `0x7F`, Vegeta `0x7D`, Trunks `0x7D` | Piccolo | Gohan 0, Trunks 12 (set 128) | Post-18 `rom:0x3D9881`: leader 1, bit1 off 0 and 2. 9,6 `rom:0x3DF2A8`-`0x3DF2DB` (SET 129): join 3, 1, 2, ext 73 (3,128), leader 3, bit1 on 0 and 3. 10,16 `rom:0x3E0D71` bit1 on 1, bit5 on 1. 9,3 `rom:0x3DDDD6` (SET 144): bit1 off 3 and 0, leader 1 |

- Outfit entry = the index of ext 73's set id in the appearance table `rom:0x1D967C` (L: the bible SAV row 471 example, (0,56) gives entry 2, fits this rule).
- Items: the Dragon Radar (45) is cleared in every slot. It is given in `rom:0x3CF62B` (table `rom:0x3CF7E8`, after 151), and its quest is active at 158 (C). The Scouter (22) is kept for cards 3-6 and cleared for card 2. Its quest "See Bulma at Capsule Corporation" is active at flag 30, so it is optional and can be held from West City on (C: quest table, give site `rom:0x3D0C4B` in the 6,16 talk table).
- Journal on each slot (C, `presave_proof.txt`): the active main quest is the one the card ends. Card 2: "Meet Krillin and the others in the Northern Wastelands". Card 3: "Meet Goku in East District 439". Card 4: "Meet up with the others on the Southern Continent". Card 5: "Follow Androids 16, 17, and 18". Card 6: "Intercept the Androids on Master Roshi's Island".

---

## Known gaps

| Gap | Effect | Label |
|---|---|---|
| Levels and EXP stay at 40 (Hercule 1) | Fights are short. Story levels would be much lower (not measured). The card 3 scene raises Gohan and Piccolo one level (`ext 22`, `push 1 ; add`, `ext 98`), as in vanilla | C (kept), S (story levels) |
| Visited maps stay 294 of 297 | The area map shows maps you would not have seen | C |
| Record +0x14 bits 2, 3, 4, 6 | Kept from the base; meaning not known | S |
| Optional flags before each card (side quests, talk flags, the side dungeon) | Kept as in the base where the site comes before the card; I did not prove each one is on your path | L |
| Walk-in trigger on entry (card 3 only needs it from the player) | If the yard scene does not start on the walk in, walk out and back in | L |
| Card 7 trigger `0x0801087F` | Not traced; your play proves the slot | C (play) |

## Play steps (mGBA)

1. Each `.sav` has a `.gba` with the same base name next to it. Open `log2_poc_r39_chapters_v5_pre_a.gba` or `_pre_b2.gba`. Do not load a state.
2. On Continue, expect the chapter before the card (slot for card N shows Chapter N-1).
3. Follow "What you do" in the table above. Watch the fade before each card and the map after it.
4. Card 1: `_pre_b2`, Continue on slot 3 (empty).

## Proposed bible rows (I merge them)

Source key `CTS` = `docs\tasks\2026-10-25-chapter-cards\chapter-test-saves-report.md` (add it to the section 1 source list).

| Fact | Tags | Label | Source |
|---|---|---|---|
| Flag 29 has no clear site. All 14 shape-A "CLR 29" matches (`rom:0x3D4876` to `rom:0x3DA336`) are record +2: type byte `00`, then a record that opens `1D 02 1C` (push 14,x). Shapes V (`01 3A 02 1C`) and L (list ending 29, then `02 1C`) find no op. So 29 stays set after it is set on leaving home (2,5 or 2,6, cond 27) | #story #tool flag:29 | C (bytes, op-boundary test) | CTS |
| Walk-in region trigger `0x0800D764` returns object `0x03002094` (vtable `0x080238E4`, set at `@0x08023064`); its test `@0x0800D730` calls the region action with no input test and removes the region (`bl 0x0800BF6E`) when the map did not change | #map #input | C (listing), L (fires on overlap) | CTS |
| Story routes: card 2 = 3,4 region 1 A press (22 and not 26) to 3,6; card 3 = 2,1 region 11 walk-in (66 and not 68); card 4 = 7,18 region 0 A press (86 clear) to 7,19 region 1 (`ext 104 (14,1)`); card 5 = 8,48 region 0 A press (127 clear) to 8,49 region 0 (`ext 84 (0)`); card 6 = 11,1 region 4 A press (145 and not 148) to 11,4, 11,5 and 11,6 (three Android 17 fights, death tables `rom:0x3E49F0`, `rom:0x3E4B50`, `rom:0x3E6078`) | #story #map flag:26 flag:68 flag:86 flag:127 flag:148 | C | CTS |
| Journal quest chain (quest table `rom:0x6D68DC`) orders the main story flags: 11, 26, 29, 30, 57, 58/59/60, 62, 66, 68, 69, 77, 86, 126, 127, 129, 131, 132, 136, 140, 141, 143, 144, 148, 149, 151, 154, 156/157, 158, 191, 193, 195. Flags 162, 163, 164, 185 (and more) are Dragon Ball flags (quest 3) | #story | C | CTS |
| Test saves `builds\mockups\2026-10-25-chapter-cards\log2_poc_r39_chapters_v5_pre_a.sav` (`0a04aa03...`, cards 2-4) and `_pre_b2.sav` (`8bd87bfc...`, cards 5, 6, empty slot 3) with v5 ROM copies. `_pre_b.sav` (`d0b60986...`) is superseded: flag 29 wrongly clear | #tool #save | C | CTS |

## Process note

Several early Bash calls in this task ran `cd` into the study folder before `py`. The brief forbids `cd` in any shell. I stopped that and used absolute paths from then on. No file outside the scope changed.

## Files

- `scripts\one-time\2026-10-25-chapter-cards\`: `presave_lib.py`, `presave_holders.py` and `.txt`, `presave_maps.py` and `.txt`, `presave_flags.py` and `.txt`, `presave_party.py` and `.txt`, `presave_build.py` with `presave_build.txt` (run 1: `_pre_a`, `_pre_b`) and `presave_build_b2.txt` (run 2: `_pre_b2`), `presave_proof.py` and `.txt`, `presave_full_suite.txt`.
- `builds\mockups\2026-10-25-chapter-cards\log2_poc_r39_chapters_v5_pre_a.sav`, `.gba`, `_pre_b2.sav`, `.gba` (use these), `_pre_b.sav`, `.gba` (superseded).
