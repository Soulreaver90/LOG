# Z Hack review report (2026-10-30)

This report maps every change of the former modder's LoG II hack ("Z Hack", beta IPS) for inspiration only. Nothing from the hack went into `art\`, a LOG module or a build.

Study folder: `scripts\one-time\2026-10-30-zhack-review\` (scripts, listings, `renders\`). All scripts read the sources as bytes with `py -3.14 -I`; nothing from the sources was run.

## SHIPPED

| Ask (brief) | Result |
|---|---|
| 1. Parse the IPS with our own reader, check the result | Done. 16,990 records (9,035 data, 7,955 RLE), no truncate. Applied in memory to the Europe ROM, SHA-1 `b9646491a947fb3f3a63c814f39e2d465698335d`, 9,239,056 bytes = the patched file. Every record with its region: `ips_regions.txt` |
| 2. Classify the changes | Done. Change map below: 3 code-area edits (7 bytes), the rest is data |
| 3. The three named features | Done, with one finding: this beta has no playable Goku vs Android 19 fight (see feature A) |
| 4. Anything else | Done: 18 new sprite sets, 18 new portraits, 5 new scouter entries, new prologue and epilogue scenes, NPC outfit swaps, one more Cell Jr round played as Super Saiyan Goku, Cooler's first form, title screen edit |
| 5. Overlap with LOG and ideas table | Done: 20 same-byte overlaps in USA terms, structural overlaps, 11 ideas |
| 6. Renders for study | Done, scratch only: `scripts\one-time\2026-10-30-zhack-review\renders\` |
| Bible rows (tag ZHK) | `scripts\one-time\2026-10-30-zhack-review\bible_rows.md` (sections 2, 4, 5a, 8, 9, 10a, 11, 14) |

## PENDING

| Item | Why |
|---|---|
| Full decode of the 479 small changed clusters in the EU script and text region (30,074 bytes) | I decoded the 23 scene tables the hack changes or adds (`scenes_hack_full.txt`, `scenes_diff.txt`). The rest are text edits and small record edits that I did not read one by one |
| USA offsets for EU-only bytes | The EU script and text region (`rom:0x6C9044`-`0x7D561C`) holds five languages per line; only 14.1 % of it (mostly bytecode) maps to USA bytes (`region_cover.txt`). The key scene tables have USA twins (section 2 table and `usa_tables.txt`); text edits have none |
| A playable Goku vs Android 19 fight | Not in this IPS by two independent shapes (feature A). My question 1 |
| Names of zone 3 maps (3,4, 3,6, 3,9) | Not looked up |
| Unit suite | Not run: this study changed no permanent code, and a run writes test ROMs outside the folders the brief allows |

---

## 1. Change map

The hack is a data hack. It changes 1,303,460 bytes in 609 clusters (gap 0x100); 850,448 of them are past 8 MB.

| EU region | IPS records | Bytes changed | What it is |
|---|---|---|---|
| Code `rom:0x0`-`0x2FFFF` | 4 | 7 | 1 instruction byte and 2 pointer words (table below) |
| Maps and objects `0x30000`-`0x53303` | 45 | 145 | NPC set swaps, NPC positions, the map 14,3 list repoint |
| Packed graphics `0x53304`-`0x2F2B07` | 13 | 2,494 | Sprite record lists that live there (sets 32, 33 and others) |
| Sprite sets `0x4B8A1C`-`0x68D14F` | 2,772 | 208,884 | Frames redrawn in place (raw), records rewritten, anim lists repointed |
| Tables, palette, portraits `0x68D150`-`0x6C9043` | 225 | 39,384 | Set table grown to 168 ids, portrait block grown to 133 ids, new set headers in reused space, the old title bitmap area reused for frames |
| Scripts and text `0x6C9044`-`0x7D7DFF` | 1,031 | 37,833 | Scene tables grown in place, new records, five-language text, scouter entries 128-132 |
| EU free tail `0x7D7E00`-`0x7FFFFF` | 1,639 | 164,550 | New data (title bitmap copy, relocated image, sets, records) |
| Expansion `0x800000`-`0x8CFA0F` | 11,261 | 850,163 written | New frames, portraits, scene records and text |

**Code-area edits (all of them)**

| EU site | USA analog | Change | Meaning | Label |
|---|---|---|---|---|
| `@0x08009212` | `@0x08019122` | `cmp r4,#0x80` to `#0x85` | Scouter **set** matcher scans 133 entries. The **type** matcher (`@0x080091E8`, USA `@0x080190F6`) keeps 128 | C (listings, `code_diff.txt`) |
| `rom:0xBAA8` (pool of `@0x0800B8DC`) | `@0x08000308`, `0x08029294` | `0x0869C570` to `0x087E0CAC` | Title screen bitmap (240x160 8bpp) points at an edited copy. 1,416 of 38,400 pixels differ, all on the subtitle line under the logo | C (bytes), L (subtitle) |
| `rom:0x2DB54` | none found | `0x086930C0` to `0x087DAB60` | Entry 2 of a four-image table. The copy decodes equal: it moved only because the set table grew over it | C (`bg_images.txt`) |

So no new code exists, by two shapes: (1) 0 BL instructions in the code area or the new space reach new space (`new_space_refs.txt` section 3); (2) of the 8 changed odd words that name new space, 0 point at a `push {..,lr}`, and every map object list still uses only the 3 vanilla factory words (`code_check.txt`). A routine reached through a pointer built at run time would not show. CONFIRMED.

**How the hack makes room (technique, for study).** It grows each table in place and moves the one item that sat after it. The set table grows from 150 to 168 words over a packed image (moved, decoded equal). The portrait block grows from 115 to 133 ids over the id 8 frame (moved, same pixels). The scouter table grows from 128 to 133 entries over the Alligator strings of entry 0 (moved). The epilogue scene table grows from 26 to 61 words over five-language strings that followed it. It also reuses freed vanilla space: the old title bitmap area (`rom:0x69BA78`-`0x69FF40`, 17,253 bytes) now holds raw frames of sets 32 and 33.

**The shared OBJ palette is unchanged** (EU `rom:0x6A87F8` equals USA `rom:0x1DA6C8`). All new art uses existing palette indices. CONFIRMED.

---

## 2. The three named features

### A. Goku vs Android 19

My words: "Goku vs Android 19 instead of the quick cutscene."

- Vanilla: EU scene table `rom:0x76F80C` (USA twin `rom:0x3D40C8`, 3 votes) on map 7,15 (event struct word EU `rom:0x42D0C`). Seq 1 (`0x0876D3E0`) is a scripted bout: NPC Super Saiyan Goku (`set:61`) and Android 19 (`set:12`), with state 6, 7 and 16 swings on 61 and hurt sets (ext 60, 112, 95, 57) on 12. Goku reverts at seq 21, Vegeta walks in, and the player fights 19 at seq 42 (`push 12,2 ; ext 104 ; push 12 ; ext 85`). CONFIRMED (EU script).
- The hack keeps seq 1 byte for byte. It changes small beats: seq 6, 8, 14 and 19 give Goku hurt reactions (`push 61,2 ; ext 57`) where vanilla only turned him, Tien gets the new portrait 131, and seq 42-48 add a Super Saiyan Vegeta transform with new lines ("And my heart is pure ... pure hatred!") before the same fight against 19. To fit 6 more words, the table now starts 24 bytes earlier at `rom:0x76F7F4` (word `rom:0x42D0C` repointed) and the old seq 42 record moved to `0x08690E44`. CONFIRMED (`scenes_diff.txt`).
- Goku himself looks different through the scene, because sets 60 and 61 are redrawn (feature C).
- **No playable Goku vs 19 fight exists in this IPS**, by two independent shapes:
  1. Byte shapes over the whole ROM: one `fight(12,n)` site (the Vegeta fight above), three new `setleader 4` sites (Cell Games, chamber exit, Cell Jr; none near map 7,15), and no new type 5 enemy spawn on any map (`byte_shapes.txt`, `maps_eu.txt`).
  2. Event structs: every `{0x08008A4F, table}` struct whose table is new or changed (4 tables, with their type 5 jumps) holds no actor 12 and no Goku leader near 7,15 (`event_tables.txt`).
  A fight built at run time, or a table named only from code, would not show. LIKELY. I may have seen a later release (question 1).

### B. Future Gohan vs the Androids

- Where: the future prologue, EU tables `rom:0x6EEC70` and `rom:0x6EF6B0` (USA twin of the second: `rom:0x3B7ADC`, 4 votes; the first has no USA vote) (Trunks and Future Gohan train, the Androids attack, Gohan goes alone).
- Vanilla: Future Gohan is `set:54` (Super Saiyan, orange gi). EU seq 1 (`0x086EEF18`) is already a scripted beat-down: Androids 18 (`set:11`) and 17 (`set:9`) hit set 54 with `ext 96` 6 times. CONFIRMED. This corrects the bible row that guessed set 54 is Goku.
- The hack's technique:
  1. `set:54` is redrawn as **base** Future Gohan (black hair), with a new anim 9 power-up: 4 records per dir, 32x32, a gold aura burst drawn into the frames (`renders\set54_0-1-9-12.png`). CONFIRMED (records), L (look by eye).
  2. New `set:157` = Super Saiyan Future Gohan (header copied from 54, 100 records, 68 frames shared with 54, 22 new raw frames). CONFIRMED.
  3. Seq 14 (new record `0x086A9CBA`): `ext 57 (54, 9)` power-up, `ext 52` remove 54, `ext 51` spawn 157 at (176,440). So the transform is a set swap after the power-up anim. CONFIRMED.
  4. Seq 1 is a new record in the free tail, `0x087DB8E0`: remove 54, spawn 157, spawn 18 and 17, then 8 `ext 96` hits from 11 and 9 on 157 with hurt states, 4 `ext 94` knockback moves with `ext 58`, music 22, `ext 57 (157, 3)` knocked down, remove 157. CONFIRMED.
- Enemy types: none. The Androids are NPC sets 9 and 11 moved by script, not enemy types. It is a cutscene, not a fight. CONFIRMED.

### C. Larger hair ("the larger hair seen in Buu's Fury")

- **Frame size and slot**: no frame exceeds the set's slot. Goku `set:60` turns all 316 keys into 32x32 at dx -8, dy -24 (vanilla: 142 keys were 16x32 at dx 0). 32 x 32 x 1 byte = 1024 bytes = the 0x400 slot, so the bible row on the 1024-byte player slot holds. CONFIRMED (`sets_keys_changed.txt`).
- **Where the hair grows**: sideways, not up. Set 60 median opaque width goes from 19 to 25 px. The top stays at y -24 (one key at -25), because the frame top is fixed at dy -24 (`hair_metrics.txt`, `renders\set60_0-1-4.png`). CONFIRMED.
- **Code change**: none. The record w, h, dx bytes change and frames are raw type 0 (no compressor needed). CONFIRMED.
- **Other characters done the same way** (keys with new pixels): Gohan `set:56` 288 of 288, `set:58` 204 of 204, `set:59` 276 of 276, Goku Super Saiyan `set:61` 56 of 304, Vegeta Super Saiyan `set:139` 169 of 245, Trunks Super Saiyan `set:130` 168 of 248, plus 13-19 keys in sets 128, 129, 132, 134, 135, 137, 138. Gohan's sets keep their sizes (they were already mostly 32x32); their hair gets 1 px taller on 123 keys of set 56. CONFIRMED (counts), L (hair as the reason, by eye).
- **Not a defect**: `sets_keys.txt` shows 64x64 records in set 58 dir 3. They are Cell frames that the reader reaches past the end of a moved list; the game reads only the code's frame count (bible OUT row). LIKELY.

---

## 3. Other changes

**New sprite sets 157-174** (`new_sets.txt`, `renders\new_sets_*.png`, `zoom_*.png`). Names are by eye and by script use (L). Many new sets fill missing anim rows with Vegeta `set:137` frames.

| Id | Look | Used by |
|---|---|---|
| 157 | Super Saiyan Future Gohan | Prologue (feature B) |
| 158 | Super Saiyan Goku in the Yardrat outfit (corrected 2026-10-30 from the export sheets, an earlier draft said Future Trunks). Dir 1 and anim 1 reuse base Yardrat frames. Dir 3 of anim 0 holds stray frames | Goku meets Trunks scene (`rom:0x713224` seq 45: NPC Goku in the Yardrat outfit, `set:62`, powers up and becomes 158) |
| 159, 160, 161, 162 | Vegeta in the pink shirt, Bulma, Yamcha, Tien in casual clothes | Talk NPCs on maps 3,4, 3,6, 3,9 (were 137, 23, 156, 121) and the Goku arrival scenes |
| 163, 164, 166 | Future Bulma and partial sets | Epilogue |
| 165, 167 | Super Saiyan and base Future Trunks | Epilogue fights |
| 168 | Imperfect Cell copy (header from `set:28`, slot 0x1000) | Epilogue |
| 169 | Bulma in the orange outfit with the Capsule Corp cap | Map 10,8 talk NPC (was 23) |
| 170 | Android 18, new art | Maps 9,7, 11,4, 11,5, 11,6 NPC (was 11); scouter entry 132 |
| 171 | Super Saiyan Gohan in the purple gi and white cape (the Cell Games outfit) | Map 14,1 arena NPC (was armor 56); scouter entry 130 |
| 172 | Super Saiyan 2 teen Gohan copy (41 frames shared with `set:58`) | NPC in the beam struggle (post-Cell table seq 20) |
| 173 | Tien, new art | Map 9,7 and 14,1 NPC (was 121); scouter entry 129 |
| 174 | Cooler first form | Map 6,61 NPC (was `set:34`), Cooler scene |

**Scouter** (`scouter_types.txt`): new entries 128 Goku (`set:61`), 129 Tien (173), 130 Gohan (171), 131 Bulma (169), 132 Android 18 (170, type 3), each with five-language names and texts. Entry 100 Tien gets portrait 131. Enemy types: the hack changes none (EU type table `rom:0x3244C`). CONFIRMED.

**Portraits** (`portraits.txt`, `renders\portraits_changed.png`): 18 new ids 115-132 (Future Gohan, Future Trunks base and Super Saiyan, Yamcha, pink-shirt Vegeta, kid Gohan, Future Bulma, Bulma in two looks, Android 18, Super Saiyan Vegeta, Tien, Cooler and others) and 20 redrawn vanilla ids. CONFIRMED (table), L (names).

**Scenes** (`scenes_hack_full.txt`):
- Goku meets Future Trunks (`rom:0x70CADC`, `0x713224`): the casual-outfit cast (159-162), and Goku arrives in the Yardrat outfit (`set:62`, redrawn with bigger hair and a new anim 9 power-up) and turns Super Saiyan (158) for Trunks.
- Chamber exit (EU `rom:0x78F9EC` = USA `rom:0x3DBDD4`): seq 3 spawns NPC Goku as 61 (was 60) and NPC Gohan as 171 (was 56); their portraits go from 63 to 65 and 59 to 62. Seq 27 no longer removes Goku; seq 32 is a new record (`0x0889B348`) where Goku reverts (state 21), the others walk off, and then the vanilla handoff runs (level 35, `ext 83` unlocks, `ext 70 (4)`, `flag:158`). CONFIRMED (`scenes_diff.txt`).
- Cell Games, self-destruct and post-Cell (EU `rom:0x7CD790`, `0x7D25B8`, `0x7D553C` = USA `rom:0x3EA400`, `0x3EB704`, `0x3EC758`): NPC Goku is Super Saiyan (`set:61`), NPC Gohan wears the cape outfit (171). In the beam struggle record (EU `0x087D34A4`, seq 20 of EU `rom:0x7D553C`) the hack spawns NPC set 172 (Super Saiyan 2 Gohan, 41 frames shared with `set:58`) at (496,392), where vanilla moves the player there (`push 0,496,392 ; ext 62`). CONFIRMED (records).
- **One more Cell Jr round, played as Super Saiyan Goku**: vanilla map 14,3 has three Cell Jr items in a row (items 8-10: type 26, `set:31`, at (432,376), each with its own scene table). The hack moves the list to `rom:0x89D24C` (13 to 14 items, `map14_3.txt`) and inserts a fourth Jr item as item 10, whose new scene (`rom:0x8A09CC`, record `0x088A0960`) ends the previous boss bar, runs `ext 139 (50000)`, removes NPC Goku, makes Goku the leader (`ext 70 (4)`), sets him Super Saiyan (`ext 73 (4, 61)`) and puts the boss bar on actor 31. The vanilla rounds shift down one (old item 10 is item 11, Cell items 11-12 are 12-13). CONFIRMED (list, record), L (round order in play). NPC Gohan on 14,3 (item 3) is also set 171.
- Cooler (`rom:0x769B7C`): NPC 174 plays state 25 (a transform), then the vanilla final form `set:34` spawns and the fight starts. CONFIRMED.
- Epilogue (`rom:0x6F0A14`, 26 to 61 words): Trunks visits his mother, a radio report, the vanilla Android 17 and 18 beat-down, "Three years later...", Imperfect Cell in the future, a flight to another place, the final fight, then "The End". CONFIRMED.
- Vegeta's start (`rom:0x7670A0`): the same records in a new order (the Super Saiyan unlock comes earlier). CONFIRMED (order), S (intent).

**Balance and menus**: no enemy type, AI row or stat byte changed. No menu code changed. CONFIRMED (type table compare). The title screen subtitle line is redrawn (L).

---

## 4. Overlap with LOG

**Same USA bytes (mechanical)**: `overlap.py` maps 256,140 hack bytes to USA (196,872 have no USA twin) and intersects them with the 128 clusters that r39 changes in the base 8 MB. There are 20 hits, all in story scripts (`overlap.txt`):

| USA site | LOG patch (bible row) | Both change |
|---|---|---|
| `rom:0x3DB5C3`, `0x3DB5CC`, `0x3DBBED` | `fullpower_ssj` (NPC Goku 60 to 61, chamber exit) | Chamber exit seq 3 and 27 |
| `rom:0x3DB627` | `npc_gi` (ext 73 (0, 157)) | Chamber exit seq 3 |
| `rom:0x3E8C2B`, `0x3E8D1D`, `0x3E8D40`, `0x3E939B` | `npc_gi` and `cellgames_ssj` (NPC Gohan set) | Cell Games NPC Gohan |
| `rom:0x3E946B`, `0x3EA9CA` | `cellgames_ssj` (NPC Goku 60 to 61) | Cell Games NPC Goku |
| `rom:0x3EA365` | `gohan_gi` (Rage push 58 to 160) | Rage `ext 73` |
| `rom:0x3E9438`, `0x3E9807`, `0x3E982C`, `0x3EA679`-`0x3EA6D0`, `0x3EA7ED`, `0x3EA891`, `0x3EB14A`, `0x3EBDB3` | Not named in the bible by address. L: the Cell Games, self-destruct and post-Cell copies of `cellgames_ssj`, `superperfect_cell` or `fullpower_ssj` | Cell Games scenes |

**Same feature (structural)**:
- Both make Goku Super Saiyan through the Cell Games and change Cell Games NPC Gohan (LOG: gi 157 and 158; hack: cape outfit 171).
- Both work on the Cell Jr rounds of map 14,3 (LOG: `celljr_fight` trial; hack: a fourth Jr round as Super Saiyan Goku, inserted as item 10 at the vanilla Jr spot (432,376)).
- Both give Vegeta Super Saiyan in a scene (LOG: `vegeta_ssj_scene` trial in the Cell fight; hack: before Android 19).
- Set id meanings collide: LOG uses 157-160 for gi Gohan and table word 58 for Super Perfect Cell; the hack uses 157-174 for its own sets and redraws 58 as armor Super Saiyan 2 Gohan. Portrait ids 115-120 also collide (LOG gi portraits, hack new faces). This matters only for reading: we port nothing.
- Scouter: LOG edits entry 19; the hack edits 0 and 100 and adds 128-132.

---

## 5. Ideas we could build our own way

Sizes: a raw 32x32 frame is 0x408 bytes, a raw 64x64 portrait 0x1008 bytes; LOG has 16 MB with new data at `rom:0x800000` on.

| Idea | How the hack did it | How LOG would do it (own art, own code) | Size |
|---|---|---|---|
| Bigger Buu's Fury-style hair on base characters (my preference) | 16x32 records widened to 32x32 at dx -8; raw frames; slot stays 0x400; no code | I draw the hair on 32x32 cells; `build_set` writes each record's own geometry (as for sets 157-160); raw frames in the expansion. Gohan's sets are mostly 32x32 already | Goku `set:60` 316 keys, about 324 KB raw; no code |
| Future prologue with a base-to-Super Saiyan Gohan power-up | Redrew 54 as base with anim 9, added set 157, new seq 14 and seq 1 records with `ext 96` choreography | Our own Future Gohan sets cloned from set 54's layout; new scene records in the expansion, table words repointed | 2 sets (about 100 KB raw), 2 records |
| Casual outfits for the Capsule Corp cast | Talk object +0x10 set swaps on maps 3,4, 3,6, 3,9 | Same item field, our own sets | 4 sets; 12 bytes of map data |
| Cell Games Gohan in the purple gi and cape | NPC set swap to 171 at 14,1 | Already close to LOG's gi work; a cape variant would be a new hand-drawn set | 1 set |
| A Cell Jr round played as Super Saiyan Goku | One more Jr item in a relocated 14,3 list; its scene sets leader 4 and `ext 73 (4, 61)` | Compare with our `celljr_fight` trial; take only the idea of Goku as the player for that round | Script only |
| Vegeta goes Super Saiyan before Android 19 | 6 new records and a table grown 24 bytes backward | Our own scene records; `vegeta_ssj_scene` has the transform parts | Script only |
| Goku vs 19 with visible strain | Turn beats replaced by hurt states on Goku | A few `ext 57 (61, 2)` edits in our own copy of the table | Bytes |
| Cooler's first form before the final form | NPC 174, state 25, spawn 34 | Hand-drawn first form set; same three-op swap | 1 set |
| Future epilogue with Trunks vs 17, 18 and Imperfect Cell | Table grown in place from 26 to 61 words | A Buu's Fury-merge chapter card before the epilogue; our own records in the expansion | Script plus 2-3 sets |
| New dialog portraits | Portrait block grown in place over id 8 | LOG already relocates the block (`gohan_portraits`); add ids there | 0x1008 per portrait |
| Scouter entries for new characters | Table grown over entry 0's strings; set-matcher bound 0x80 to 0x85 | Reuse duplicate entries 14-18 (bible SPC row) instead of growing past 128, because of the save risk below | 1 byte of code if grown |

---

## 6. My questions

1. **Goku vs Android 19**: this beta keeps the vanilla scripted bout (with more hurt beats) and the player fight is still Vegeta's. Did you see a playable Goku vs 19 in a later release? If you have that file, I can map it the same way.
2. **Scouter save risk in the hack**: the hack's set matcher can return entries 128-132, and the USA bit setter has no upper bound (ext 141 `@0x0800B00C`), so a scan would write bits into save byte slot + 0x11A + 16 (`+0x12A`), past the 16-byte database field. CONFIRMED for USA code; SPECULATIVE for the EU save layout. LOG keeps the save format, so we would not grow the scouter past 128. Do you agree?
3. **Bigger hair**: do you want base Goku first (all 316 keys, sideways growth like the hack), or Gohan's base sets first?
4. **Future prologue**: is a base-to-Super Saiyan Future Gohan power-up in scope for the merge, or does the prologue stay vanilla?

---

## Files

- Report: `docs\tasks\2026-10-30-zhack-review\zhack-review-report.md`
- Bible rows: `scripts\one-time\2026-10-30-zhack-review\bible_rows.md`
- Listings: `ips_records.txt`, `ips_regions.txt`, `change_map.txt`, `code_diff.txt`, `new_space_refs.txt`, `sets_eu.txt`, `sets_keys.txt`, `sets_keys_changed.txt`, `new_sets.txt`, `hair_metrics.txt`, `scouter_types.txt`, `portraits.txt`, `maps_eu.txt`, `rec_dump.txt`, `scenes_tables.txt`, `scenes_diff.txt`, `scenes_hack_full.txt`, `byte_shapes.txt`, `event_tables.txt`, `code_check.txt`, `usa_tables.txt`, `region_cover.txt`, `rec_at.txt`, `map14_3.txt`, `owner_of.txt`, `bg_images.txt`, `overlap.txt`
- Renders (study only): `renders\new_sets_*.png`, `zoom_*.png`, `set54_*.png`, `set56_*.png`, `set59_*.png`, `set60_*.png`, `portraits_changed.png`, `bg_*.png`

Writes: only `scripts\one-time\2026-10-30-zhack-review\` (scripts, listings, `eu_us_map.json` cache, `renders\`) and this report. The study's own `__pycache__` was removed. No `.pyc` was written in `scripts\permanent\` or `2026-10-18-npc-gi\` by this study (no file there is newer than the first study script). Nothing under `data\` or the sources folder was written.
