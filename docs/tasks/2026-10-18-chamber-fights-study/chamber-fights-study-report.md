# Chamber sparring fights: feasibility study

Study for me ask of 2026-10-18 (6:55 PM, 7:02 PM, 8:18 PM correction): four Time Chamber sparring fights, two per pair. This is a study only. No ROM was built or patched.

- ROMs read: base LoG II USA, SHA-1 `18e0715dec419f3501c301511530d2edcd590f8b` (the Ghidra copy `scratch\ghidra\log2.gba` is the same file), r17 `archive\builds\log2_poc_r17.gba`, SHA-1 `eee5eb351e94e50910d6129a48eacecb6d85ab80`. Buu's Fury USA read-only.
- Labels: **C** = CONFIRMED (bytes, disassembly or Ghidra decompile quoted), **L** = LIKELY, **S** = SPECULATIVE.
- Working files: `scripts\one-time\2026-10-18-chamber-fights-study\` (decompiles `dec_*.txt`, `enemies.txt`, `enemies2.txt`, `music.txt`, sheets `*.png`, tools `contact.py`, `table.py`). Bible rows: `scripts\one-time\2026-10-18-chamber-fights-study\bible_rows.md`.

---

## 1. Verdicts

| Fight | Verdict | Main blockers |
|---|---|---|
| 1. Trunks (jacket) vs Vegeta | **Feasible with limits** | No chamber interior map exists, and every zone 9 map has combat off. A new arena map entry is needed. Everything else is data in proven mechanisms. |
| 2. Trunks (armor, Super grade) vs Vegeta | **Feasible with limits** | Same arena blocker. The level bump and the +15 grade are vanilla script ops (ext 98, ext 73). |
| 3. Gohan (Demon Clothes) vs Goku (gi) | **Feasible with limits** | Same arena blocker. Gohan entry 0 (`set:53`) has no transform, so no form work. |
| 4. Gohan (armor, Super Saiyan) vs Goku (armor) | **Feasible with limits, largest** | (a) No Goku armor sprite exists in LoG II or in the Buu's Fury sheets: new art (L) or my decision to use `set:60`/`set:61`. (b) In r17 armor Gohan is in no appearance entry: playable armor Gohan with Super Saiyan needs two new entries, a moved appearance table and a wider reverse lookup. |

The answer to me question: the base game gives a **level bump plus unlocks**, not a fixed stat bump. Both chamber exits run ext 98 (level + 1, with the normal random stat gains of the level-up routine), ext 83 (unlock an ability slot), ext 109 and ext 110 (refill HP and EP), and an outfit change by ext 73. Gohan also gets Super Saiyan by ext 82. No script op adds a fixed stat value. Evidence in section 3.4.

---

## 2. How a LoG II boss fight works end to end

LoG II already has a complete sparring system: the Capsule Corp training facility, map **6,70** ("SCIENTIST: If you feel like sparring with your friends... try out the training facility", `@0x083CCE94`). Yamcha, Krillin and Tien fight the player there, and a loss does not end the game. This is the model for the chamber fights. The Cell fights use the same parts.

### 2.1 Trigger and start (C)

1. Map 6,70 region items (`@0x083FB7D0`, `@0x083FB7E4`, `@0x083FB7F8`, factory `@0x0800D7E1`, walk-in test `@0x0800D765`) run scene tables by flag: `!212`, `212 & !213`, `213 & !214`.
2. The NPC partner stands on the map (spawn factory `@0x0800D6DE`, `set:156` Yamcha at 128,136, condition `!212`).
3. Yamcha's table `@0x083D2D3C`: seq 2 is a type 4 record (prompt), seq 3 is `push 156,3 ; ext 104 ; push 156 ; ext 85`.
4. **ext 104 (actor, n)** (`@0x0800AAC6`, decompiled): finds the actor by set, removes it, and builds spawn item n of the current map list +0x14 at the actor's position and facing (`@0x0800C75C`, the item condition is not tested). Spawn item 3 is the enemy record `@0x083FB724`.
5. **ext 85 (actor)** (`@0x0800AB1A`): makes the boss HP bar object (section 2.5).

Spawn record `@0x083FB724` (bytes `7f e7 00 08 01 00 00 00 6a 00 00 00 80 00 8c 00 9c 00 00 00 1c b7 3f 08 ...`):

| Offset | Value | Meaning |
|---|---|---|
| +0 | `0x0800E77F` | Enemy factory |
| +4 | 1 | Condition: not spawned at map load (L: the evaluator `@0x08003F06` was not re-read) |
| +8 | 0x6A = 106 | Enemy type (index into the enemy table) |
| +0xC | x 128, y 140 | Position |
| +0x10 | 0x9C = 156 | Sprite set id |
| +0x14 | `0x083FB71C` | Event struct `{0x080106B3, scene table 0x083D2DE4}` (the win scene) |

### 2.2 Arena and map lock (C, L)

- Map entry +8 = combat allowed. It is copied to map info `@0x03002080` +0xC at load. With 0, the A button talks instead of punching (`@0x08007DE8`), and the Super Saiyan gate fails (FRM). Map 6,70 has +8 = 1.
- There is no separate arena lock. The fight map is a closed room; the player leaves only through the scripted warp (L: 6,70 has one exit region).

### 2.3 Boss object and factory (C)

- Factory `@0x0800E77E` passes the spawn record and the enemy table entry `0x086D56AC + 24 * type` to the constructor `@0x0800E280` (object 0x1F0 bytes, vtable `@0x080252A4`).
- The sprite comes from spawn +0x10 through `get_set` (`@0x08009324`). **Any sprite set can be any enemy type.** The constructor reads no other sprite data.
- Enemy table entry, 24 bytes (`@0x0800F7CC`, `@0x0800E484`, `@0x0800E560`, `@0x0800E4D2`):

| Offset | Meaning | Reader |
|---|---|---|
| +0 u32 | EXP award (bosses 0) | `@0x0800E4D2` |
| +4 u32 | HP and max HP (enemy +0x188) | `@0x0800E484`, `@0x0800E560` |
| +8 u32 | AI behaviour id (table `@0x086D5194`, 8 bytes each) | `@0x0801AA98` |
| +0xC, +0xD, +0xE | STR, POW, END (enemy +0x160..+0x162) | `@0x0800F7CC` |
| +0xF, +0x10 | Melee and ki hit factors (+0x163, +0x164; 0x80 normal, 0x40 or 0x60 resistant) | `@0x0800F7CC`, `@0x0800E5B8` |
| +0x14 | Death descriptor: `0x086D2B6C` normal, `0x086FF3C4` boss, others | `@0x0800E484` |

- 109 types are readable. Types 95, 96 and 97 are boss-descriptor placeholders (HP 5, AI 8) that no spawn record uses (one shape: all 666 enemy spawns).

### 2.4 AI (C for the selection, L for the behaviour)

- The AI is data, chosen per enemy type (+8), not per sprite. Each id is `{node tree, transition table}`; the humanoid bosses share the same class code (`0x0801AEF3`, `0x0801AF2B`, a distance test that picks a near or far node) with different node data.
- Humanoid AIs in use: **21** (Yamcha `set:156`, Android 17 `set:9`, Android 18 `set:11`, Cell Jr `set:31`, `set:34`, `set:48`), **98** (Krillin `set:76`, Tien `set:121`, the sparring partners), 29 (Androids 19, 20), 80 (Imperfect Cell), 116 (Semi-Perfect Cell), 138 and 148 (Perfect Cell).
- **LoG II has no Vegeta, Goku, Trunks or Gohan enemy.** Shape A: the 666 enemy spawn records use no set in 53-61 or 128-140. Shape B: constant ext 104 actor ids are 29, 30, 34, 50, 111, 121, 156 (and Krillin by a variable). The brief's "Vegeta is a boss already" does not hold in the ROM. A Vegeta or Goku enemy is a new enemy type that reuses AI 98 or 21.
- Animations: the enemy sets use the playable row layout (anim 3 knockdown, 4 arms up, 12 head-only; compare `set:76`, `set:156`, `set:9` with `set:60` in `scripts\one-time\2026-10-18-chamber-fights-study\enemy_a12.png`). AI 21 drives sets with only anims {0, 1, 2, 5, 6, 7, 8} (`set:48`, `set:31`); AI 98 drives sets with {0-6, 12} (`set:76`). The playable sets 53, 56, 60, 128, 129, 137, 138 hold anims 0-9, 11-14, 16-18, 20. So both AIs fit (L: the behaviour nodes were not traced; they could still reference a projectile object with its own sprite).

### 2.5 HP bar and HUD (C)

- ext 85 (actor) builds a 0x1C-byte object (vtable `@0x08025748`, constructor `@0x080104C0`): two OBJ sprites, 0x200 bytes of OBJ VRAM, sliding in from the top. The fill is `enemy+0x188 * width / entry+4`, redrawn when it changes (`@0x0801055C`).
- Message 0xF (enemy death broadcast) clears its target. Message 0x10 slides it out; **ext 88** broadcasts message 0x10 (`@0x0800AC00`). The win scenes call ext 88 first.

### 2.6 Music (C usage, L meaning)

- A fight plays the map music (entry +0x24) or a script track (ext 49 n, table `@0x081D4B2C`). Map 6,70 uses track 29. Section 9 lists candidates.

### 2.7 Win (C)

1. Damage reaches 0 in `@0x0800E484`: HP 0, broadcast message 0xF, call the death descriptor +8.
2. Boss descriptor `0x086FF3C4` +8 = `@0x0801A82C`: EXP task (`@0x0800E4D2`, entry +0 = 0 for bosses, so none) and the event task (`@0x0800E39C`).
3. The event task (vtable `0x080238FC`, tick `@0x080109AC`) stores the death position and calls the spawn +0x14 event struct; `0x080106B3` runs its scene table (`@0x080106B2`).
4. Yamcha win table `@0x083D2DE4`: ext 88 (hide bar), "YAMCHA: Whoa... You sure showed me! Good fight!", ext 26 (6) (gives a +3 Power Capsule), fade, ext 38 to 6,3, SET `flag:212`.

### 2.8 Loss (C)

1. Player HP 0 (`@0x08008784`): state 0x21 and a 200-frame task (vtable `@0x08023A50`).
2. The task (`@0x080085FC`) runs the fixed scene table `@0x083B63B4` from index 0 (literal `rom:0x8870`, the only reference).
3. Record 0 tests **map 6,70 only**: there it jumps to index 4 (the sparring branch); anywhere else it shows "You have died!" and ext 97 (back to the title).
4. Index 4 picks Krillin's line (19) or Tien's (16) by flags, else Yamcha's (5); each warps to 6,3 with ext 38. No game over.
5. **Unused loss lines:** the table also holds Vegeta (index 8, "Did you really think you could beat me? Pathetic."), Piccolo (10), Gohan (12), Goku (14, "Good fight! Keep working and maybe you'll beat me next time.") and Trunks (22). No record branches to them (seq 1 pushes only 4; seq 5 pushes only 19 or 16), and the only table literal is `rom:0x8870` (`owner_of.py`, two shapes). The developers planned more sparring partners. Vegeta's line fits fights 1-2; Goku's line fits fights 3-4.

### 2.9 Flags and rewards (C)

- The sparring flags are 212, 213, 214 (set in each win scene). Cell Games flags 192-195 (SAV).
- Rewards are script ops in the win scene: ext 26 (item), ext 98 (level). Boss entries give 0 EXP. Normal enemies drop items through the death descriptor +0xC parameter (8 normal, 1 boss, 0x40); the drop roll was not traced.

---

## 3. Characters, outfits, forms and the time jump

### 3.1 Outfits per phase (C: appearance table bytes)

| Who | Phase | Appearance entry | Set | Transform | Exists |
|---|---|---|---|---|---|
| Trunks | Jacket, fight 1 | 12 (`00 80 62 13 11 11`) | `set:128` | entry 17, `set:134`, form `@0x030021EC` (Super Saiyan +10) | Yes |
| Trunks | Armor, fight 2 | 13 (`00 81 64 14 0e 0e`) | `set:129` | entry 14, `set:130`, form `@0x030021E8` (Super: +15 STR, +10 POW, +15 END, slower) | Yes |
| Trunks | Post-chamber NPC | none | `set:131` (jacket over armor, anims 0, 1, 4 only) | none | Cutscene only |
| Vegeta | Before | 8 | `set:137` | entry 11, `set:140`, +10 | Yes |
| Vegeta | After the chamber | 9 | `set:138` | entry 10, `set:139`, Super Vegeta +15 | Yes |
| Gohan | Before (Demon Clothes) | 0 | `set:53` | none (+4 = +5 = 0) | Yes |
| Gohan | Armor | none in r17 | `set:56` (`set:59` Super Saiyan) | r17 entries 2 and 5 are the gi (157, 158) | Sets yes, entries no |
| Goku | Before (gi) | 19 | `set:60` | entry 20, `set:61`, +10 | Yes |
| Goku | Armor | none | none | none | **No** (LoG II contact sheet `contact_all.png`; Buu's Fury folders Goku to Goku 6 are all orange gi) |

- Vanilla chamber entry: NPC Trunks is `set:128` (`@0x083DDD22`), Gohan waits as `set:53` (seq 18). Trunks gets entry 12 and Super Saiyan at `flag:129` (`@0x083DF28C`: `ext 82 (3) ; ext 73 (3,128) ; ext 98 (3,27)`).
- Vanilla Vegeta and Trunks exit (`@0x083DE620` seq 33): `ext 73 (3,129) ; ext 73 (2,138)`. Later the 12,6 scene (`flag:151`, `@0x083E7789`) moves them to `set:132` and `set:137` (regular +10 forms).
- r17 note: the live appearance table is `rom:0x88DC54` (entries 0-22; the bytes after entry 22 are other data, so there is no free slot). The reverse-lookup copy is `rom:0x800000`; it has no entry with +1 = 56, and its scan stops at 22 entries (`cmp r2,#0x16` at `@0x080042D6`). **ext 73 (0, 56) hangs in r17.** Raw portrait 59 is remapped to the gi portrait for entries 2, 5, 22 by the r14 hook; use portrait **121** (armor, `npc_gi`) for armor Gohan lines.

### 3.2 Forms and unlock (C)

- Super Saiyan needs record +0x14 bit 5 (FRM). **ext 82 (char)** sets it (`@0x0800AA58`: `orr #0x20`). **ext 83 (char, k)** sets bit 2 + k (`@0x0800AA7C`: `4 << k`): k 0 = hold special, 1 = slot 0, 2 = slot 1.
- The higher grade is an appearance change, not a flag: entry 13 (+4 = 14) and entry 9 (+4 = 10) point at the Super form object `@0x030021E8`. **A script unlocks it mid-scene with ext 73 (3, 129)**, as the vanilla exit does.
- Gohan's Super Saiyan in vanilla: `ext 82 (0)` in the chamber exit seq 3 (`@0x083DB59C`), then "Gohan now has Super Saiyan form! Gohan can now use the Kamehameha!" (ext 83 (0, 2) opens slot 1).

### 3.3 Player switch (C)

- **ext 70 (n)** (`@0x0800A784`) and **ext 115** (`@0x0800A680`): run the old form's leave, write struct +0 = n, rebuild the player sprite from the leader's appearance, enter the form. ext 70 also reverts every other transformed character (`@0x08003ED4`). No party test.
- Vanilla uses it around the chamber: entry scene ext 70 (1) (Piccolo leads), exit scene ext 70 (2) (Vegeta), chamber exit ext 70 (4) (Goku). Record +0x14 bit 1 is cleared and set around them by ext 81 and ext 80 (meaning of bit 1 not traced; FS shows it grays the file select sprite).
- Fights 1-2: `ext 80 (3) ; ext 70 (3)` before, restore with `ext 81 (3) ; ext 70 (1)` after. Fights 3-4: `ext 70 (0)` before, the vanilla scene's own ext 70 after.

### 3.4 Time jump bumps (C)

| Op | Handler | Effect |
|---|---|---|
| ext 98 (char, level) | `@0x0800AC10` | Cap 50. If below, runs level-up `@0x08003CA0(struct, char, cur, target)` and sets EXP to the target threshold |
| Level-up `@0x08003CA0` | | Per level: max HP x (1 + (0xE14 + rand 0x51F) / 65536), max EP + 2-4, both refilled; STR, POW, END += `lo*n + rand((hi-lo+1)*n)` (8.8) from `rom:0x1D95F0` (12 bytes per character), cap 100 (`@0x08003C6E`) |
| ext 109 / 110 (char, n) | `@0x0800ADF2`, `@0x0800AE32` | Set HP / EP to min(n, max); 5000 = refill |
| ext 82, 83, 73 | above | Unlocks and outfit |

- Vanilla bumps: Gohan exit `level(0)+1` capped at 50, ext 82 (0), ext 83 (0,2), refill (`@0x083DB59C`). Vegeta and Trunks exit: ext 83 (3,2), ext 83 (2,2), refills, `level+1` each (`@0x083DDE68` seq 1).
- Trunks' gain per level: STR 0x11F-0x1E7 (1.12-1.90), POW 0xAC-0x174, END 0xB6-0x17E. A larger bump is ext 98 with `level + n`. A fixed bump has no op (a new ext op or code would be needed).

---

## 4. The chamber map

- **LoG II has no chamber interior map** (C by three shapes): no map name string holds "Time", "Chamber" or "Hyperbolic" (string table `@0x080E2840`; zone 9 names are "Kami's Lookout" 212 and "Dende's Lookout" 199); the map table holds zone 9 areas 1-7 only; constant script loads of 9,4-9,7 (ext 35-39) hit 9,4 (a side room where Kami talks, L), 9,5 (Korin's Tower) and 9,7 (the post-Cell Shenron scene). A map reached only by a computed load would not appear.
- The "waiting" scenes play on **map 9,3** (antechamber): region 0 rect (73,113)-(120,140) "You cannot enter the Hyperbolic Time Chamber."; region 1 runs the entry scene (`flag:143` and not 144, table `rom:0x3DDE0C`); region 2 runs the Vegeta and Trunks exit (`flag:148` and not 149, table `rom:0x3DE6F4`). Vegeta and Trunks walk to the door at 96,56 and are removed; nobody is shown inside.
- Zone 9 maps 9,1-9,7 all have entry +8 = 0 (no combat), music 31 on 9,2-9,7. Do not set 9,3 +8 = 1: the Lookout's A-press talk objects would stop working.
- Layout +8/+0xA values (9,3: 225, 121; 6,70: 41, 137) do not match the region coordinates (9,3 regions reach y 289), so the map size is not traced. By coordinates 9,3 is about 370 x 300 px.
- **Map growth (C, two shapes):** the map table `@0x08409368` has 3 literal words (`rom:0x5ADC` debug menu, `rom:0x5D5C` debug level, `rom:0xEBD8` lookup); the count is `@0x0800E0AC` (`mov r0,#0xff ; add r0,#0x48`, 2 callers). A new entry 9,8 = a relocated table plus one changed byte. A computed table address would not appear in these shapes. Visited-map bits (table `@0x086F6D8C`) for a new map are not traced.
- **Buu's Fury chamber: not traced.** Buu's Fury dialog is not ASCII, not a webfoot stream and not a constant-offset 8-bit code (three shapes, 0 hits for "Gohan", "Chamber", "Hyperbolic"). The BF map and layout formats are engine unknown 7. Reusing a BF chamber map is L effort and is not the prototype path. `Fralacticus/LOGExtractor` (map viewer) is the tool to find it.

---

## 5. Story placement

| Fight | Hook (vanilla scene) | Gate | Before | After |
|---|---|---|---|---|
| 1 | Chamber entry table `rom:0x3DDE0C`, seq 21 (`@0x083DDD22`), after Vegeta and Trunks walk to the door, before `SET 144` | `flag:143` and not 144 (region) | Warp to the arena, `ext 80 (3) ; ext 70 (3)`, Vegeta NPC, dialogue, ext 104 + ext 85 | Win scene: ext 88, dialogue, then fight 2 setup or return |
| 2 | Same chain after fight 1 (option A), or Vegeta and Trunks exit table `rom:0x3DE6F4` seq 1 as "Meanwhile, inside" (option B, matches the vanilla bump place) | `flag:148` and not 149 for B | Fade (ext 40), `ext 98 (3, level+1)`, `ext 73 (3,129)`, dialogue, fight | Remove the vanilla `level+1` in seq 1 so the bump is not doubled; continue the exit scene |
| 3 | Exit table seq 33 (`@0x083DE620`), after Goku and Gohan walk to the door, before `SET 149` | same scene | `ext 70 (0)`, Goku NPC `set:60`, fight | Win: return to seq 33 tail (its ext 70 (2) restores Vegeta) |
| 4 | Chamber exit table `rom:0x3DBDD4` seq 1 or 3 (`@0x083DB59C`, "Meanwhile...") | `flag:154` set in seq 1; table reached by type 5 hand-offs (`@0x083CF7E0`, `@0x083D152C`) | Armor Gohan entry (new), `ext 82 (0)`, `level+1`, fight vs Goku | The vanilla seq 3 `ext 73 (0,157)` puts the gi on afterwards, as my rule wants |

- **Mechanism (C):** a scene table word can point at a type 5 record (`@0x0800B494`: jump to the table at record +4, index 0). So each hook is one changed table word in the base script region plus new tables in the expansion area. r16 already moved scene records to the expansion area (NGI).
- The fight is asynchronous: the pre-fight table ends after ext 104; the win continues in the enemy's event table, which must jump back into the vanilla flow (type 5 to a copy of the remaining records, or the remaining records copied into the win table).
- **Loss:** record 0 of `@0x083B63B4` must also test the arena map (relocate the record, repoint table word `rom:0x3B63B4`). Recommended design: a loss shows the unused Vegeta or Goku line, refills HP and EP (ext 109, 110), and continues the story the same way as a win (no reward). This cannot softlock. A retry design needs a re-triggerable start (the arena enter script +0x30 or a region) and a flag.

---

## 6. Hooks and space

- Ext op table `@0x083B5D28` has 145 entries; the interpreter does not bound-check (not traced). No new ext op is needed for fights 1-3: every step is an existing op (C, sections 2-3).
- New data goes in `rom:0x800000`-`rom:0xFFFFFF` (decision, bible section 2). Scene tables, records, spawn and region lists, the enemy entries and a map entry are all absolute pointers.
- Map lists: a map entry holds counts (+3, +4) and list pointers (+0x10, +0x14), so an arena's lists are new data, not table growth.
- New flags: none needed for a fight inside a one-shot scene. A retry design needs one flag; the free flag list is not traced.

---

## 7. Dialogue

- **Storage (C):** cutscene records `{u8 seq, 0, u8 type, u8 portrait, payload}`. Type 1 = plain ASCII text ending in 0 (`@0x0800B438`); type 2 = webfoot stream (`@0x0800B304`); type 3 = format pointer + script (`%s` = leader name, e.g. `@0x083CCE94`); type 4 = script pointer + stream (prompts, e.g. the sparring offer).
- **New text needs no compressor:** type 1 records work for any length (vanilla lines up to 67 characters and longer, e.g. `@0x083B627E`). 0x0B starts a new box page; the speaker name is part of the text ("GOKU: ..."). A leading `!`, `#` or `@` selects a box style (L, not traced).
- **Portraits (C):** Goku 63, Vegeta 106 (107 Super), Trunks 98 (jacket), 99 or 100 (armor; the exit scene uses 99), kid Gohan 56 (pre-chamber), armor Gohan **121** in r17.
- **Expanded ROM:** yes, through table words (r16 precedent).
- **Size of an 8-line scene:** about 0.6 KB: 8 type 1 records (4 + about 55 + 1 bytes each, about 480 bytes), 2-3 type 0 code records (about 80 bytes), the table (4 bytes per entry, about 48). Vanilla check: the Yamcha win table, 5 records, is 152 bytes (`@0x083D2D4C`-`@0x083D2DE3`).

---

## 8. Stats

Enemy entries near this story point (C, `enemies2.txt`):

| Type | Who (set) | HP | STR/POW/END | AI | Story place |
|---|---|---|---|---|---|
| 106 | Yamcha (156), spar | 800 | 18/12/14 | 21 | Post-game |
| 64 | Krillin (76), spar | 1800 | 23/24/17 | 98 | Post-game |
| 98 | Tien (121), spar | 2110 | 35/29/27 | 98 | Post-game |
| 3 | Android 17 (9) | 3550 | 32/39/34 | 21 | Before the chamber |
| 4 | Android 18 (11) | 2910 | 29/34/27 | 21 | Before the chamber |
| 60 | Imperfect Cell (28) | 5210 | 32/32/37 | 80 | Before the entry |
| 76 | Semi-Perfect Cell (29) | 4890 | 39/41/46 | 116 | Between entry and exits |
| 78, 79 | Perfect Cell (30), 12,6 | 5160, 5500 | 44/46/50 | 148 | Before the Goku and Gohan exit |
| 21-24, 25 | Perfect Cell, Cell Games | 6500, 8230 | 50/55/60, 60/59/65 | 138 | After |
| 26 | Cell Jr (31) | 4990 | 46/50/46 | 21 | After |

- Scaling: hand-set per entry; no formula. Bosses give 0 EXP and rely on script rewards.
- Player levels: Trunks is set to at least 27 at `flag:129` (`ext 98 (3,27)`); Goku joins at 35. Gohan's and Vegeta's levels at the chamber are not traced (they depend on play). By the range table, Trunks at level 30 has STR about 50 (S).
- **Proposed numbers (S, to tune in play):** fight 1 Vegeta HP 4000, 36/34/38; fight 2 Super Vegeta HP 5000, 44/44/48; fight 3 Goku HP 3500, 34/36/34; fight 4 Goku HP 5500, 46/50/50. EXP 0, death descriptor `0x086FF3C4`, factors 0x80.

---

## 9. Music and sound engines

- **Pick (C):** map entry +0x24, or ext 49 n in a script. Music table `@0x081D4B2C` (44 entries of 20 bytes) has 3 literal users: `@0x08005906` (debug sound test, L), `@0x08009C9E` (ext 49), `@0x0800C4FA` (map load).
- **LoG II tracks to reuse (C usage, L meaning):** 29 (sparring room 6,70), 33 (Cell maps 12,6, 14,3, 14,4), 31 (Lookout 9,2-9,7, calm), 19 (Android 17 maps 11,4-11,6), 25 (Android 20 7,15), 35, 39, 40 (Vegeta's "QUIET!" in the exit scene `@0x083DE1D0`). Track names are not in the ROM; I should listen in the debug sound test.
- **Engines (C by shape):** Buu's Fury has a music table of the same 20-byte shape at `rom:0x3BB78C` (53 entries, shared instruments `0x0836D18C`, samples `0x0836D540`; LoG II `0x0814A8A4`, `0x0814AD60`). Entry 0 of both ends in length `0x682`. 17 of 19 16-byte chunks of the LoG II play routine `@0x08020A4C` occur in Buu's Fury at `rom:0x3F110`; the update routine `@0x08020BD8` matches only 5 of 32 chunks and init 0 of 27. So it is the same driver family with code differences.
- **Porting a BF track:** a data copy (song data, its instrument table and the samples it uses, plus one table entry and 3 repointed literals) if the song format matches; the update-routine differences are the risk. Size: song data a few KB (S); the BF instrument and sample banks, if copied whole, are up to about 1 MB (S, LoG II samples sit in `rom:0x30000`-`rom:0x14FFFF`). Effort M, risk medium. `ghxstboyy/webfootaudioengine` claims a cross-ROM song import.

---

## 10. Component list

| Component | Effort | What it needs |
|---|---|---|
| Arena map | M (L for a real chamber look) | New map entry (zone 9 area 8): relocated map table, count byte, entry +8 = 1, a reused LoG II layout (9,3 or 9,4), spawn and region lists, music. A white chamber look needs a new tileset or a BF port (L) |
| Boss object and AI | S | 4 enemy entries (or reuse unused types 95-97), AI 98 or 21, death descriptor `0x086FF3C4` |
| Sprites | S, L for Goku armor | Existing sets 128, 129, 137, 138, 139, 53, 60, 61. Goku armor: a new set of about 300 frames, or I accept the gi |
| Armor Gohan playable (fight 4) | M | Move the r17 appearance table again, add 2 entries (`set:56` +4 to a `set:59` entry), repoint the 17 literals, the status pool `rom:0x86FCD0` and the portrait hook pool, widen the reverse lookup (bound byte `@0x080042D6`, copy) |
| Script and trigger | M | 4 hook words (type 5), new tables, NPC spawns for ext 104, return paths |
| Flags | S | None for one-shot fights |
| Dialogue | S | Type 1 records, about 0.6 KB per scene, my text |
| Stats | S | Enemy entry fields |
| Music | S reuse, M port | ext 49 or map +0x24 |
| HUD | S | ext 85, ext 88 as is |
| Win and loss | S win, M loss | Event structs; relocated game-over record 0 with an arena test |
| Player switch and bumps | S | ext 70, 80, 81, 98, 73, 82, 83, 109, 110 |
| **Total** | **M for fights 1-3; L for all four with Goku armor art** | |

---

## 11. Smallest first prototype

Gohan (Demon Clothes) vs Goku (`set:60`) in the existing sparring room, so no map growth and no new code:

1. Reuse unused enemy type 95 in place: HP 3500, STR/POW/END 34/36/34, AI 98, death descriptor `0x086FF3C4` (24 bytes at `rom:0x6D5F94`).
2. Copy the 6,70 spawn and region lists to the expansion area with one more pair: an NPC Goku (`set:60`, factory `@0x0800D6DE`) and an enemy record (type 95, `set:60`, condition 1, event `{0x080106B3, new win table}`); repoint 6,70 entry +0x10/+0x14 and raise its counts.
3. New region scene (for example after `flag:214`): `ext 73 (0,53) ; ext 70 (0)`, two type 1 lines, then `push 60,<n> ; ext 104 ; push 60 ; ext 85`.
4. Win table: ext 88, "GOKU: ..." line, ext 109/110 refill, ext 38 to 6,3. Loss: change seq 5 of `@0x083B63B4` (copy) to reach the unused Goku line (index 14) and a warp record.
5. Test from the post-Cell save with the debug teleport or the atrium. Then move the same data to a 9,8 arena and hook it into the chamber scenes.

---

## 12. Risks

| Risk | Level | Note |
|---|---|---|
| AI quality | Medium | AI 98 is a sparring AI built for Krillin and Tien; it has no Super Saiyan, no beam and no special. A Vegeta that fights like Tien may feel weak. New behaviour data is untraced (L effort to author) |
| Missing enemy anims | Low | The playable sets hold every anim the two AIs use (L). Projectile objects of AI 98 were not traced and may carry their own sprites |
| Softlock | Medium | A fight ends a scene and resumes in another. Each return path must re-run the vanilla tail exactly once. A loss outside 6,70 goes to the title today. Use "loss continues the story" |
| Save state | Low | The arena has no save point, and the fights sit inside one-shot scenes. A save in a new appearance entry (armor Gohan, entry 23 or 24) loads only on the patched ROM (same open item as entry 22) |
| Double bumps | Low | Option B for fight 2 and fight 4 must remove the vanilla `level+1` or accept +2 |
| My premises | Note | No chamber interior map exists; Vegeta is not a LoG II boss; Goku has no armor sprite; `set:131` (the vanilla exit look for Trunks) is cutscene-only |
| Tool traps | Note | Scene tables that point into the expansion area break tools that bound words to `rom:0x3B5000`-`0x420000` (NGI). The Ghidra headless run needs addresses without `0x` |

---

## 13. Open items

- Buu's Fury chamber map and fight staging: not traced (text encoding and map format unknown).
- Meaning of record +0x14 bit 1 (ext 80, 81).
- Drop roll in the death event (+0xC parameter).
- AI node data format (`@0x086D5194` entries).
- Box style prefixes `!`, `#`, `@`.
- Free story flags.
- Gohan's and Vegeta's expected levels at the chamber (needs a save at that point).
