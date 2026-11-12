# Study: Future Trunks vs Android 18, Android 17 and Cell as playable boss fights

Date 2026-11-05. Base ROM only, no build, no patch. Every listing is in
`scripts\one-time\2026-11-05-trunks-boss-fights\`.

> [!IMPORTANT]
> The brief's premise does not hold for the main story. All three of the `ext 139` bosses are ALREADY
> real player fights in vanilla, and Trunks already fights one of them himself. The place where the game
> plays a cutscene of Trunks beating 18, 17 and Cell is the ENDING, scene table `rom:0x3B8140`. That is
> where the owner's ask fits word for word, and that is what this report recommends building.

---

## Headline

| Ask | Answer |
|---|---|
| Is Android 18 a cutscene? | No. Real player fight, enemy type 4, 8000 EXP. CONFIRMED |
| Is Android 17 a cutscene? | No. Real player fight, 4 rounds, enemy type 3, 15000 EXP. CONFIRMED |
| Is Perfect Cell a cutscene? | No. Real player fight, 2 rounds, types 78 and 79, 40000 EXP. CONFIRMED |
| Does Trunks already fight one? | Yes. Perfect Cell. `ext 70 (3)` forces him. CONFIRMED |
| Where IS the cutscene the owner means? | The ending, table `rom:0x3B8140`, records 8, 11 and 23. CONFIRMED |

---

## Q1. Which of the three is a real fight, and who fought it in vanilla

All three are real fights. None is a cutscene.

| Boss | Enemy item | Type | HP | AI | Descriptor | Death event table | EXP record |
|---|---|---|---|---|---|---|---|
| Android 18 `set:11` | `rom:0x4033A4` (map 8,49 item 0) | 4 | 2910 | 21 | `0x086FF3C4` boss | `rom:0x3D98AC` | `rom:0x3D8BC4`, `ext 139 (8000)` at `rom:0x3D8BDA` |
| Android 17 `set:9` r1 | `rom:0x406494` (map 11,4 item 1) | 3 | 3550 | 21 | `0x086FF3C4` boss | `rom:0x3E49F0` | - |
| Android 17 r2 | `rom:0x40657C` (map 11,5 item 0) | 3 | 3550 | 21 | boss | none, +0x14 is `0x086D66BC` | - |
| Android 17 r3 | `rom:0x406654` (map 11,6 item 0) | 3 | 3550 | 21 | boss | `rom:0x3E4B50` | - |
| Android 17 r4 | `rom:0x4066E4` (map 11,6 item 4) | 3 | 3550 | 21 | boss | `rom:0x3E6078` | `rom:0x3E4B6C`, `ext 139 (15000)` at `rom:0x3E4B7F` |
| Perfect Cell `set:30` r1 | `rom:0x406FF0` (map 12,6 item 4) | 78 | 5160 | 148 | boss | `rom:0x3E7104` | - |
| Perfect Cell r2 | `rom:0x406F78` (map 12,6 item 1) | 79 | 5500 | 148 | boss | `rom:0x3E77B0` | `rom:0x3E7110`, `ext 139 (40000)` at `rom:0x3E7121` |

**Label: CONFIRMED.** Source `22_enemy_sweep.txt` (every aligned word equal to the enemy factory
`0x0800E77F`, 666 items, then the type row at `rom:0x6D56AC + 24 x type`), plus `06_a17_t1.txt`,
`07_pcell_t78.txt`, `08_pcell_t79.txt` and `10_control_sweep.txt`.

Two more vanilla fights the brief did not name, found by the same sweep:

- **Imperfect Cell `set:28`**: item `rom:0x4058A4`, map entry 287, type 60, HP 5210, AI 80, boss
  descriptor, condition "flag 136 clear", death table `rom:0x3E24A0`. CONFIRMED.
- **Semi-Perfect Cell `set:29`**: item `rom:0x406E10`, map 12,4 item 1, type 76, HP 4890, AI 116, boss
  descriptor, death table `rom:0x3E6F30`, `ext 139 (30000)` at `rom:0x3E666F`. CONFIRMED.

### Who fought each one

| Boss | Who fights it in vanilla |
|---|---|
| Android 18 | The current leader, which STARTS AS PICCOLO. `push 1 ; ext 115` at `rom:0x3D457E`, in record `rom:0x3D4548` of the post-Android-19 table `rom:0x3D4834`, makes Piccolo the leader with the map load to 7,16, and `ext 80 (1)` and `ext 80 (0)` at `rom:0x3D4824` and `rom:0x3D4828` enable Piccolo and Gohan. Nothing forces a leader again until `push 1 ; ext 70` at `rom:0x3D987F`, at the END of 18's own death table. Trunks is NOT in the party, so the player can only be Gohan, Piccolo or Vegeta. CONFIRMED |
| Android 17 | The current leader. No leader force runs between `push 3 ; ext 70` at `rom:0x3E2460` (the Gingertown Cell death table) and `rom:0x3E6E1D` (after the Semi-Perfect fight): CONFIRMED by a byte sweep of `ext 70` and `ext 115` in two push shapes, and by the round hand-offs at `rom:0x3E47E3`, `rom:0x406613` and `rom:0x3E4B41`, none of which touches the leader. That the leader is therefore still TRUNKS when the fight starts is LIKELY, not CONFIRMED: the 18 barrier objects force a switch at a door, and two of them (`rom:0x3DF938` at map entries 272 and 288, "Only Gohan") sit in the zones just before zone 11 |
| Perfect Cell | **Trunks**, forced. `push 3 ; ext 70` at `rom:0x3E6E1D`, record `rom:0x3E6DE4` (table `rom:0x3E6F30` index 22), three records before `ext 104 (30, 4)` at `rom:0x3E6F21` arms round 1. CONFIRMED |

> [!NOTE]
> The Android 17 scene still speaks Piccolo's lines (`rom:0x3E4904`, "PICCOLO: You're not perfect. I'll
> destroy you before that happens.", portrait 3), but the engine never forces him. A player who keeps
> Trunks after Gingertown fights Android 17 as Trunks today, with Piccolo's dialogue over it.

---

## Q2. Is Trunks the player at each story point

| Point | Trunks in the party? | Leader | Can the leader be forced? |
|---|---|---|---|
| Android 18 (map 8,49) | **No** | free, starts as Piccolo | `ext 70` works, but a leader who is not in the party is a new, untested state |
| Android 17 (maps 11,4-11,6) | Yes | free, LIKELY still Trunks | Not needed if the LIKELY holds. An `ext 70 (3)` would make it certain |
| Perfect Cell (map 12,6) | Yes | **Trunks, forced** | Already done in vanilla |
| The ending (`rom:0x3B8140`) | Yes | the post-Cell leader, free | `ext 70 (3)` is the proven op, the same shape as `rom:0x3E9E59` in the Cell Jr relay |

**Trunks' party window, CONFIRMED.** `ext 91 (3)` at `rom:0x3B7AB8` takes him out in the prologue on map
1,2. `ext 79 (3)` at `rom:0x3DF2A6` puts him back, in the record that SETs flag 129 (Cell reveal), with
`ext 80 (3)` enable at `rom:0x3DF2D5`. Shape A found 14 `ext 79` sites and 2 `ext 91` sites. Shape B
(varint push) found 1 and 0. Source `24_party_sites.txt`.

Android 18's fight ends by setting flag 127 (`ext 27 (127)` at `rom:0x3D9871`, record `rom:0x3D9864`,
death table index 47), and flag 127 comes before flag 129. So Trunks is out of the party for the whole
Android 18 stretch. CONFIRMED.

`celljr_fight` works because Gohan is the leader there. The equivalent is already true for Perfect Cell
and nearly true for Android 17.

---

## Q3. The exact table, record and seq of each cutscene

### The ending: table `rom:0x3B8140`, 27 words

Two type 5 records hand off to it. Each sits right after a record that SETs flag 196.

| Route | Type 5 record | Holder table | Holder item | Flag 196 SET |
|---|---|---|---|---|
| News interview, "now that you've saved the world, what's next?" | `rom:0x3C4E90`, seq 30, word `rom:0x3C4F0C` | `rom:0x3C4E98`, 31 words | map entry 67 region 9, step item `rom:0x3F3E7C`, rect (401,969)-(464,1008), cond always | `rom:0x3C4E8C` |
| Dende at the Lookout | `rom:0x3DD03C`, seq 89, word `rom:0x3DD1A4` | `rom:0x3DD044`, 90 words | map 9,1 talk item `rom:0x403F60`, `set:36` at (760,416), cond flag 195 set | `rom:0x3DCEF9` |

The three fights inside it are all cutscene: `ext 96` scripted blasts, then `ext 52` removes the target.

| Fight | Table word | Record | What it runs | What a copy does |
|---|---|---|---|---|
| vs Android 18 `set:11` | word 8, `rom:0x3B8160` | `rom:0x3B7C96`, seq 8, next 9 | 2 groups of `ext 96 (133, 11, 100)` at `rom:0x3B7CA2` and `rom:0x3B7CDE`, then `ext 52 (11)` at `rom:0x3B7D1B` | redirect word 8 to a copy that runs `ext 104 (11, N18)`, `ext 86 (1)`, `ext 85 (11)` and ends. The new item's death event carries the rest |
| vs Android 17 `set:9` | word 11, `rom:0x3B816C` | `rom:0x3B7D6E`, seq 11, next 12 | 2 groups of `ext 96 (133, 9, 100)` at `rom:0x3B7D80` and `rom:0x3B7DBC`, then `ext 52 (9)` at `rom:0x3B7DF9` | the same, with `ext 104 (9, N17)` |
| vs Imperfect Cell `set:28` | word 23, `rom:0x3B819C` | `rom:0x3B8016`, seq 23, next 24 | 3 groups of `ext 96 (133, 28, 100)` at `rom:0x3B8022`, `rom:0x3B805E` and `rom:0x3B80B5`, then `ext 52 (28)` at `rom:0x3B80D3`, the revert to `set:132` and the fade | the same, with `ext 104 (28, NCELL)`. The death event ends with the vanilla tail: `ext 52 (133)`, `ext 51 (132, 248, 568)`, `ext 47 (55)`, fade 300, `ext 119`, `ext 52 (132)`, `ext 45` |

The three opponents already stand on the map as NPC spawn items with cond "flag 196 set", so
`ext 104 (actor, n)` can turn each into an enemy at its own spot. That is the vanilla shape: Android 17's
own rounds use `ext 104 (9, 1)` at `rom:0x3E47E3` and `ext 104 (9, 4)` at `rom:0x3E4B41`.

| Map | Item | What it is | Spot | Cond |
|---|---|---|---|---|
| 1,2 entry `rom:0x4093A0`, count 4 | item 1 `rom:0x3ED774` | NPC `set:11` Android 18 | (472,408) | `0x000100C4` = flag 196 set |
| 1,2 | item 2 `rom:0x3ED794` | NPC `set:9` Android 17 | (520,408) | flag 196 set |
| 1,2 | item 3 `rom:0x3ED7B4` | NPC `set:132` Trunks | (496,648) | flag 196 set |
| 6,1 entry `rom:0x40B320`, count 7 | item 5 `rom:0x3F9C08` | NPC `set:133` Super Saiyan Trunks | (248,624) | flag 196 set |
| 6,1 | item 6 `rom:0x3F9C28` | NPC `set:28` Imperfect Cell | (288,392) | flag 196 set |
| 6,23 entry `rom:0x40B7F0`, count 1 | item 0 `rom:0x3FAEE4` | NPC `set:132` Trunks | (48,280) | always |

All CONFIRMED. Source `19_epi_maps.txt`, `20_items_detail.txt`, `04_epilogue_table.txt`.

### The main story, for completeness

| Boss | Fight start ops | In record | Table and word |
|---|---|---|---|
| Android 18 | `ext 84 (0)`, `ext 86 (1)`, `ext 90 (11, 50, 100)` at `rom:0x3D8B51` to `rom:0x3D8B5D` | `rom:0x3D8B38` seq 24 | approach table `rom:0x3D8B60`, word 23 |
| Android 17 r1 | `ext 104 (9, 1)`, `ext 90 (9, 75, 100)`, `ext 86 (1)` at `rom:0x3E47E3` to `rom:0x3E47F0` | `rom:0x3E47DC` seq 6 | 11,4 region table `rom:0x3E47F8`, word 6 |
| Perfect Cell r1 | `ext 104 (30, 4)`, `ext 86 (1)`, `ext 90 (30, 50, 100)` at `rom:0x3E6F21` to `rom:0x3E6F2D` | `rom:0x3E6F16` | 12,4 death table `rom:0x3E6F30`, word 25 |

---

## Q4. What blocks each one

### Blockers that kill the main-story reading of the ask

1. **Nothing to convert.** All three are already fights. Making them playable is a no-op. CONFIRMED.
2. **Android 18: Trunks is not in the party.** Forcing him needs `ext 79 (3)`, `ext 80 (3)` and a level
   (`ext 98`) 16 story flags early. It also puts a character with no items and no EXP history into every
   later leader branch of the 18 death table. Records 23, 25 and 27 (`rom:0x3D90BA`, `rom:0x3D9164`,
   `rom:0x3D91F0`) each read the leader with base op 11 and place a different NPC, and none of them has
   a Trunks arm. CONFIRMED for the branch records, LIKELY for the fallout.
3. **Android 17: already Trunks by default.** The only change worth making is the dialogue, which is
   Piccolo's. That is a text job, not a fight job. CONFIRMED.
4. **Perfect Cell: already Trunks.** CONFIRMED.

### Blockers for the ending fights, which is the build worth doing

| # | Blocker | Label | Detail |
|---|---|---|---|
| B1 | Map 1,2 carries an always-on step region that undoes the party | CONFIRMED | Region 0 of map 1,2 is scene item `rom:0x3ED7DC`: factory `0x0800D7E1`, step trigger `0x0800D765`, rect (-15,-7)-(360,584), cond 0, table `rom:0x3B7ADC`. That table is the prologue beating of `set:54`, and it ends with `ext 91 (3)` at `rom:0x3B7AB8`, which takes Trunks OUT of the party, then `ext 79 (0)`, `ext 80 (0)` and `ext 70 (0)` at `rom:0x3B7AC4`, which makes Gohan the leader. A free fight west of x 360 fires it |
| B2 | The player object is not Trunks | CONFIRMED | The ending record 0 loads 1,2 at (384,552) and record 13 loads 6,1 at (136,432). The leader stands there while Trunks acts as NPC `set:132` or `set:133`. A playable fight needs `ext 70 (3)` plus the NPC Trunks item suppressed. Otherwise find-by-set clashes: `@0x08006E0A` binds the NEWEST actor, so every `ext 53 (132, ...)` binds the wrong one |
| B3 | Both maps need a new spawn list | CONFIRMED | Map 1,2 holds 4 items and map 6,1 holds 7, none of them an enemy. `ext 104 (actor, n)` needs the enemy item to exist in the map +0x14 list. The `celljr_fight` method applies: copy the list into the expansion area with the new items, then repoint the map entry |
| B4 | No hand-back from a death event to the ending table | CONFIRMED | The event runner `@0x080106B2` starts every death event at word 0. A death event cannot resume the ending table at word 9. The `celljr_fight` answer is that the enemy event table IS the continuation: build a table whose word 0 is the death record and whose later words are copies of the ending records that follow |
| B5 | A loss throws the player back to the title | CONFIRMED | Game-over table `rom:0x3B63B4` word 0, record `rom:0x3B6104`: the died box, then `ext 97` at `rom:0x3B6159`. No save point sits between the Lookout farewell and the ending, so a death means replaying the whole farewell flight |
| B6 | EXP at the ending is thrown away | LIKELY | `ext 139` adds to the leader record, and the ending runs `ext 97` with no save point after. A bar is worth showing. An EXP award is cosmetic |
| B7 | No record in the ending turns the HUD on | CONFIRMED for the absence, LIKELY for the HUD state | No `ext 86` appears anywhere in table `rom:0x3B8140`. The fight records must add `ext 86 (1)` and the death records `ext 86 (0)` |
| B8 | Set 9 lacks anim 4 | CONFIRMED, not a blocker | `set:9` has anims 0-3, 5-8 and 12. `set:11` has 0-8 and 12. `set:28` has 0-3, 5-10, 12, 18 and 19. Both already run as vanilla enemies with these rows. Only `ext 57 (actor, 4)` would ask for anim 4, and no fight record needs it |
| B9 | Super Saiyan Trunks is a different art set from the NPC one | CONFIRMED, not a blocker | Appearance entry 15 is `set:132`, and +4 = 16 = `set:133`. `set:132` has exactly the anim rows of the playable sets 56 and 128 (0-9, 11-14, 16-18, 20, all four directions), so it drives the player object with no code change. `set:133` has 0-8, 11-13, 16, 18, 20 and 21, the same shape as the vanilla playable `set:134` |

| B10 | Map 6,1 carries its own regions, but none over the fight area | CONFIRMED | Region 0 `rom:0x3F9C5C` is the SAVE POINT (factory `0x08010AC7`, A press, rect (408,568)-(457,617)), so a free fight lets the player save inside the ending. Region 1 `rom:0x3F9C80` is an A-press script `rom:0x3F9C6C` that loads the world map. Regions 2 and 3 are the west-edge warps at rect (0,176)-(9,481), conds flag 77 clear and flag 77 set, so one arm is always live. Region 4 `rom:0x3F9CD0` is a script `rom:0x3F9CC4` at rect (209,65)-(288,112). Region 5 `rom:0x3F9CE4` is the only STEP region, rect (193,193)-(312,264), gated on flags 75 and 211. Cell stands at (288,392), 128 px south of that rect |
| B11 | The ending maps also carry present-day NPCs | CONFIRMED | Map 6,1 builds three `set:120` NPCs with cond always (items 1, 2 and 3 at (432,376), (416,136) and (40,104)) plus the Goku talk object `rom:0x3F9B4C` gated on `rom:0x3F9B30`. They share the field with any fight placed there |

### Checks the brief asked for, answered

- **Boss descriptors and HP.** Types 3, 4, 60, 76, 78 and 79 all carry the BOSS descriptor
  `0x086FF3C4`, which holds the actor at HP 0 with no AI so its death event runs. HP is 3550, 2910,
  5210, 4890, 5160 and 5500. No new type is needed for the ending: reuse type 4 with `set:11`, type 3
  with `set:9` and type 60 with `set:28`. The art set comes from the ITEM (+0x10), not the type, so no
  type copy is needed either. CONFIRMED.
- **Hurtbox rows.** `set:9` and `set:11` are (-2,-25,18,10) in all four facings, footprint 16x8.
  `set:28` is (-16,-42,36,10), (-7,-42,41,10), (-11,-43,46,10), (-22,-43,35,10), footprint 24x8.
  `set:132` is (-2,-23,18,10) in three facings and (-2,-24,17,10) facing up. `set:133` is about
  (-2,-26,18,10). All present and sane. CONFIRMED. Source `26_boxes_and_maps.txt`.
- **Is a loss scripted as part of the story?** No. None of the three ending records tests HP or the
  leader, and the vanilla ending has no loss arm. CONFIRMED.
- **Does a story flag gate progression on the cutscene finishing a certain way?** No. The ending table
  sets no flag. Flag 196 is set BEFORE it, in the two holder tables. Its last record `rom:0x3B813A`
  runs `ext 97` only. CONFIRMED.

### Two reading traps in the listings

- `10_control_sweep.txt` prints `ext 29` as PARTY_ADD and `ext 30` as PARTY_REMOVE. Those names carry
  label L in the bible: `ext 29` and `ext 30` broadcast message 4, and PARTY MEMBERSHIP is `ext 79` and
  `ext 91`. Read the `ext 29 (3)` at `rom:0x3D8CE2` as a broadcast, not as Trunks joining at 18's death.
- The map entry +4 word is not a reliable item count on every entry. `20_items_detail.txt` reads
  garbage past the real end of a list. Use `22_enemy_sweep.txt`, which scans for the enemy factory word.

### The input ROM

`celljr_fight` runs on the main build, not the base ROM, so the Q3 targets were checked against the
build list. No patch in `build_list.txt` or `build_list_core.txt` writes the ending table `rom:0x3B8140`,
its records `rom:0x3B7B08`-`rom:0x3B813A`, the map 1,2 or map 6,1 entries, their item lists, or the two
type 5 records. The only hits for those addresses in `scripts\permanent\patches\` are two comments in
`vegeta_ssj_scene.py` that cite `rom:0x3B80FD` and `rom:0x3B7C1C` as vanilla precedents. CONFIRMED,
source `31_build_check.txt`.

### One bonus the ending unlocks

The game-over table holds an unused Trunks loss line at index 22 (RE-BIBLE row, label C). A Trunks boss
fight is the first place in the hack that could use it.

---

## Q5. Recommended order

Build the ENDING, not the main story. Within it, this order:

1. **Imperfect Cell on map 6,1 first.** Cheapest by a clear margin.
   - One enemy item to add, and map 6,1 already carries 7 items with no enemy, so one list copy serves.
   - Its record `rom:0x3B8016` is the LAST fight in the ending, so its death event table only has to
     carry two more records, `rom:0x3B8116` and `rom:0x3B813A`, plus the vanilla tail that already sits
     inside record 23. Blocker B4 costs almost nothing here.
   - Map 6,1 has no always-on STEP region over the fight area, so B1 does not apply. Its only step
     region sits at rect (193,193)-(312,264) and is gated on flags 75 and 211, 128 px north of Cell.
     The save point and the world-map exit both need an A press, and the warps need the west edge.
     See blocker B10 for the full region list.
   - It is the climax, so one fight alone still reads as a payoff.
2. **Android 18 on map 1,2 second.** It needs B1 solved, either by changing the region condition or by
   fencing the arena east of x 360 plus the player footprint. Its death event chain must also carry
   records 9 and 10.
3. **Android 17 on map 1,2 last.** The same map, so B1 and B3 are already paid, but its chain is the
   longest: records 12 through 23 have to live in its death event table, or the 17 fight has to hand
   back through another enemy event.

Do not touch the main-story Android 18 and Android 17 fights. For Android 17 the only real gap is that
Piccolo's lines play while Trunks may be the one fighting. That is a dialogue decision for the owner,
not a fight to build.

---

## Evidence index

All files are in `scripts\one-time\2026-11-05-trunks-boss-fights\`.

| File | What it proves |
|---|---|
| `01_find_epilogue.txt` | The USA ending text `rom:0x3B8116`, named by `rom:0x3B81A0` |
| `03_words.py`, `03_words.txt` | The ending table start `rom:0x3B8140` and its two namers |
| `04_epilogue_table.txt` | The whole ending table, 27 words, every op |
| `05_a18_death.txt` to `09_maps.txt` | The three main-story boss tables and the maps that own them |
| `10_control_sweep.py`, `10_control_sweep.txt` | Leader, party, spawn, bar, EXP, flag and map ops of 11 tables |
| `11_leader_sites.py`, `11_leader_sites.txt` | Every `ext 70` and `ext 115` site, two push shapes |
| `13_table_3B8340.txt` | The opening table of the game, for contrast with the ending |
| `14_epi_namers.txt`, `15_find_table_start.txt`, `17_table_3C4E98.txt` | The two routes into the ending and their holders |
| `18_enemy_items.py`, `20_items_detail.txt`, `22_enemy_sweep.txt` | Every enemy item and type, and the items of all relevant maps |
| `21_set_rows.py`, `21_set_rows.txt` | Anim rows of sets 9, 11, 28, 29, 30, 53, 56, 128, 132, 133, 134 and 137 |
| `23_entry_records.txt` | The flag 196 SET sites and the game-over table |
| `24_party_sites.py`, `24_party_sites.txt` | The Trunks party window: ext 79, 91, 80, 81, 29 and 30 |
| `25_a17_entry.txt` | Piccolo's lines over the unforced Android 17 fight |
| `26_boxes_and_maps.txt` | Hurtboxes and footprints, plus the Gingertown and 11,5 items |
| `27_map12_region.txt` | The always-on step region on map 1,2 that undoes the party, blocker B1 |
| `28_gates.txt`, `29_gates.py`, `29_gates.txt` | The 18 barrier lines, the map entry that owns each, and the 11,5 round 2 hand-off |
| `30_61_scripts.txt` | The map 6,1 region scripts and the region 5 condition |
| `31_build_check.txt` | No patch in the build list writes the ending data |
| `32_adhoc_probes.py`, `32_adhoc_probes.txt` | The ad-hoc probes, saved so every CONFIRMED row can be regenerated |
