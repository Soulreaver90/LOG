# Cell Games Super Saiyan study: Gohan and Goku (2026-10-20)

Brief: `docs\tasks\2026-10-20-cellgames-ssj\cellgames-ssj.md` (with the 10:19 AM Goku addition). Base: r22 `archive\builds\log2_poc_r22.gba`, SHA-1 `9287672b53f1757d43a46dc01a852f1142f0e115` (checked). Read only: no ROM, save or `data\` file was written. My files are in `scripts\one-time\2026-10-20-cellgames-ssj\` only.

Labels: **CONFIRMED** = proved here by bytes, code listing or a two-shape sweep. **LIKELY** = strong evidence, not proved in game. **SPECULATIVE** = a guess.

---

## 1. SHIPPED and PENDING

**SHIPPED (this study)**

| Ask | State | Where |
|---|---|---|
| "Gohan super saiyan at the cell games in his NPC form" | Designed: NPC set 157 to 158 at 10 sites, NPC portrait 59 to 62 (shows 115) at 4 records | Sections 3, 7 |
| "start super saiyan when playable" | Designed: ext 73 (0, 158) before both ext 70 (0) calls, and one reverse-copy byte | Sections 4, 7 |
| "base (default) after cell is beaten" | Already true: post-Cell seq 20 ext 73 (0, 157), nothing to add | Section 5 |
| "goku ... transform ... ssj before fighting cell" | Designed: scripted transform in the 14,2 entry scene (state 9, ext 73 (4, 61)), NPC Goku 60 to 61 at 28 sites, NPC portrait 63 to 65 at 7 records | Sections 3, 4, 7 |
| Is Goku playable at the arena? | Yes: he leads from 14,1 until "Me? Fight Cell?" seq 21 | Section 4 |

**PENDING (mine)**

| Item | Why |
|---|---|
| Goku transform point | Seq 26 (before "Let's do this!", recommended) or seq 1 (on arrival). Section 8, point 1 |
| NPC Goku after he gives up | Super Saiyan to his teleport (anime, recommended) or base. Section 8, point 2 |
| 14,1 NPC Goku (shown only when someone else leads) | Keep base (recommended) or Super Saiyan. Section 8, point 3 |
| EP refill at the Cell fight re-transform | Section 8, point 4 |
| In-game check | All proof is bytes and code reading |

---

## 2. Question 1: the stretch (CONFIRMED bytes, LIKELY trigger meaning)

The stretch starts at the arena landing (map 14,1, world map needs `flag:191`) and ends when Cell is destroyed (post-Cell seq 20). `flag:195` is set later, at seq 50, after the map load to Capsule Corp. Fight steps are enemy records (factory `0x0800E77F`) whose `{0x080106B3, table}` struct runs a scene table when the enemy is beaten (`scripts\one-time\2026-10-20-cellgames-ssj\maps14.txt`).

| # | Map, trigger | Scene table | Gate | What happens | Leader |
|---|---|---|---|---|---|
| 1 | 14,1 objects | talk `rom:0x3E81D4` (Gohan), `rom:0x3E8530` (Goku) | Gohan NPC `@0x08408C90`: `02 0b 00 00 0c 00 c3 02 14 04 11` (leader != 0 and not 195); Goku NPC `@0x08408D44`: leader != 4 and not 195 | NPCs wait at the arena | any |
| 2 | 14,1 barrier | region `rom:0x3E8084`, break object `@0x08408DD4` | leader == 4, level(4) > 39, not 195 | Only Goku passes | Goku |
| 3 | 14,2 region 0 (always) | `rom:0x3E8D98` (28 words) | none; ends `push 193 ; SETFLAG` | Refill all, NPC Gohan and Piccolo arrive, Hercule, "Let's do this!", ext 104 (30, 1) | Goku |
| 4 | Cell type 21 (`@0x08408E4C`) | `rom:0x3E8F50` | | Ring grows, ext 39 to 14,3 | Goku |
| 5 | Cell type 22 (`@0x08408F18`) | `rom:0x3E93E8` (21) | ends `push 192 ; SETFLAG` | Goku gives up; seq 21 removes NPC Gohan, `push 0 ; ext 70`, spawns NPC Goku `set:60` | Goku, then Gohan |
| 6 | Cell type 23 (`@0x08408FC8`) | `rom:0x3E9D4C` (31) | seq 22 `push 194 ; SETFLAG` | Android 16, Cell Jr, seq 31 `push 1 ; ext 70` | Gohan, then Piccolo |
| 7 | Cell Jr type 26 (x3) | `rom:0x3E9E24`, `rom:0x3E9E84`, `rom:0x3EA400` | | ext 70 (2) Vegeta, ext 70 (3) Trunks, then `rom:0x3EA400` seq 1 `push 0 ; ext 70` | Vegeta, Trunks, Gohan |
| 8 | (in `rom:0x3EA400`) | seq 27 | | Rage: `push 0,9 ; ext 57`, flash, `push 0 ; push 160 ; ext 73`, "transformed into Super Saiyan 2" (seq 30) | Gohan |
| 9 | Cell type 24 (`@0x084090C8`) | `rom:0x3EB704` (65) | | Self-destruct; NPC Goku teleports (seq 23 removes `set:60`); Cell returns | Gohan (Rage) |
| 10 | Cell type 25 (`@0x084090F8`) | `rom:0x3EC758` (55) | seq 50 `push 195 ; SETFLAG` | Seq 20: Cell removed, `push 0 ; push 157 ; ext 73`, `push 1 ; ext 70`, NPC Gohan 157 | Gohan, then Piccolo |

Full dumps: `scenes_r22.txt` (all tables, repointed words followed). Every ext 70 runs `appearance_revert` (section 4a).

**Completeness, three shapes.** (1) The map walk above (`maps14.txt`). (2) The R22 id-40 sweep (`scripts\one-time\2026-10-20-r22-build\scenes40c.txt`) found 7 arena tables: `0x3E8D98`, `0x3E8F50`, `0x3E93E8`, `0x3E9D4C`, `0x3EA400`, `0x3EB704`, `0x3EC758`. My list is those 7 plus 5 tables with no Cell line: the talks `0x3E81D4` and `0x3E8530`, the barrier `0x3E8084`, and the Cell Jr events `0x3E9E24` and `0x3E9E84`. (3) The obj18 records of maps 14,2-14,4 run script `0x083EE6A8` (factory `0x0800F9A3`): it is a random `ext 92` loop with no text, no set id and no ext 57. It needs no change. A scene started only from Thumb code would not appear.

---

## 3. Question 2: NPC Gohan and NPC Goku

### 3a. How the NPC set is chosen (CONFIRMED)

- Scripts spawn and address NPCs by raw set id. `find_actor_by_set` `@0x08009370` sends message 5 with the set pointer, so every reference to one NPC in a scene must change together. Map objects pass +0x10 (`@0x0800B710`) or +0xC (`@0x0800D6DE`) to `get_set`. No appearance entry is involved.
- NPC Gohan is `set:157` (gi base, from `npc_gi`). NPC Goku is `set:60`.

### 3b. Sites (two shapes, 42 = 42, `setsites_r22.txt`; exact bytes in `design_sites_r22.txt`)

| Who | Site | Bytes now | Change |
|---|---|---|---|
| Gohan, 14,1 object | `rom:0x408CA0` | `9D` | `9E` |
| Gohan, 14,3 object (`flag:192` clear) | `rom:0x408F8C` | `9D` | `9E` |
| Gohan, entry scene seq 1 (npc_gi copy) | `rom:0x8950F5`, `rom:0x89510B` | `00 9D` | `00 9E` |
| Gohan, entry seq 22, 26 | `rom:0x3E8C2C`, `0x3E8D1E`, `0x3E8D41` | `00 9D` | `00 9E` |
| Gohan, "Me? Fight Cell?" seq 14, 21 | `rom:0x3E921C`, `0x3E9226`, `0x3E939B` | `00 9D` | `00 9E` |
| Goku, "Me? Fight Cell?" seq 21 spawn | `rom:0x3E93C1` | `78` (zigzag 60) | `7A` (61) |
| Goku, `rom:0x3E9D4C` seq 1, 14 | `rom:0x3E946B`, `0x3E9807`, `0x3E982C` | `78` | `7A` |
| Goku, `rom:0x3EB704` seq 8-20 (23 sites) | `0x3EA679`, `0x3EA698`, `0x3EA6D0`, `0x3EA793`, `0x3EA7ED`, `0x3EA7F3`, `0x3EA7FA`, `0x3EA801`, `0x3EA808`, `0x3EA80F`, `0x3EA816`, `0x3EA891`, `0x3EA89F`, `0x3EA8A5`, `0x3EA8AC`, `0x3EA8B3`, `0x3EA8BA`, `0x3EA8C1`, `0x3EA8C8`, `0x3EA8CD`, `0x3EA8D8`, `0x3EA8E2`, `0x3EA951` | `78` | `7A` |
| Goku, `rom:0x3EB704` seq 23 remove | `rom:0x3EA9CA` | `3C` (op 0) | `3D` |

- All edits are one byte in place. 158 fits op 0 (`00 9E`); 61 is zigzag `7A`, the same length as `78`. No NPC record needs to move.
- The post-Cell group (`rom:0x3EC758`, 157) stays: that is after Cell is beaten.
- Search limits: a set id computed at run time, or a script reached only from Thumb code, is in neither shape. Shape B also finds 120 set-60/61 sites outside the stretch (earlier story); none is in `rom:0x3E8000`-`0x3EC800`.

### 3c. Poses (CONFIRMED rows, LIKELY for the command states)

| Set | Has (all 4 directions) | Lacks vs the base set |
|---|---|---|
| 158 (gi SSJ, set 59 layout) | 0-9, 11-13, 16, 18, 20, 21 | **14, 17** (157 has them) |
| 61 (Goku SSJ) | 0-8, 10-13, 16, 18-21 | **9, 14, 17** (60 has them) |

- NPC Gohan in the stretch gets only spawn, place/walk (ext 53), face (ext 55), ext 56 and remove. NPC Goku gets spawn, walk (ext 54), place (ext 53), face, ext 56 and remove. No ext 57 (state) names 157 or 60 in the stretch (shape A).
- Anim 14 is selected only by state 14 (`@0x0800E870`, vtable `@0x080251F4`) and anim 17 only by state 17 (`@0x0801A2A4`). Two shapes: the state table `@0x083B5278` and a code scan for the row immediates. No stretch script sends state 14 or 17.
- **Missing poses: none for the scenes.** Anims 14 and 17 are absent, but nothing in the stretch asks for them. Vanilla playable Super Saiyan Gohan (set 59) has the same gaps.
- Set 61 has no anim 9 (power up). The Goku transform must play state 9 **before** ext 73 (4, 61), while he is still set 60. Section 4.
- Vanilla already runs `set:61` as an NPC with ext 53, 55 and 57 (Southern Continent, `@0x083D3600`-`@0x083D3FB6`).

---

## 4. Question 3: playable Gohan and Goku

### 4a. Mechanism (CONFIRMED by listing)

- **ext 73** `@0x0800A8EC` (char, set): for the leader it runs the old form's leave, writes the record entry through the reverse-lookup copy (`rom:0x42F0` = `rom:0x800000`), sets player +0x48 = `get_set(set)`, runs `form_reapply` and the new form's enter. For a non-leader it only writes the record.
- **ext 70** `@0x0800A784` = `set_leader` (old leave, sprite from `appearance_set`, `form_reapply`, new enter) and then `appearance_revert` `@0x08003ED4`:
  ```
  08003ef0  add r3,r3,r4      ; entry of character r1 (r1 != leader)
  08003ef2  ldrb r5,[r3,#0]   ; +0 bit 0 = transformed
  08003ef8  ldrb r3,[r3,#5]   ; +5 = revert entry
  08003efa  strb r3,[r2,#0x14]
  ```
  So ext 70 (0) moves Goku 20 to 19. ext 70 (1) moves Gohan 5 to 2 (and 4 to 2).
- **Live table** `rom:0x88DC54`: entry 5 = set 158, form `0x030021EC` (Super Saiyan), +4 = 22, +5 = 2; entry 20 = set 61, +5 = 19.
- **Reverse copy** `rom:0x800000`: entry 5 +1 = **59** at `rom:0x800065`. ext 73 (0, 158) hangs on the assert today. ext 73 (0, 59) would show the armor sprite (ext 73 sets the sprite from the raw id). So `rom:0x800065` must become 158 (`3B` to `9E`). No ext 73 names 59 anywhere (shapes A and B), so no script loses its entry.

### 4b. Gohan (CONFIRMED sites, LIKELY in game)

- He becomes the leader twice: `rom:0x3E93E8` seq 21 (`00 00 02 46` = `push 0 ; ext 70` at `rom:0x3E93A6`) and `rom:0x3EA400` seq 1 (at `rom:0x3E9E9F`). Today he starts in entry 2 (gi base) both times.
- **Insert `00 00 00 9E 02 49` (push 0 ; push 158 ; ext 73) just before each `push 0 ; ext 70`.** Gohan is not the leader yet, so ext 73 writes only his record (entry 5). Then `set_leader` builds the player from entry 5 (sprite 158, Super Saiyan form, its enter). `appearance_revert` skips the leader.
- The second insert is required: the Cell Jr ext 70 (1) reverts him 5 to 2.
- Ki drain is the vanilla Super Saiyan tick (1 EP per 20 frames, revert at 0). The B button reverts (`step_ok` needs `flag:195`, so no SSJ2 step before Rage).
- **Rage from Super Saiyan works** (CONFIRMED by code): seq 27 plays state 9 on set 158 (anim 9 present: the set 59 SSJ-to-SSJ2 frames), then ext 73 (0, 160) runs the Super Saiyan leave, entry 4, sprite 160, `rage_stats` apply and the Rage enter. The `rage_text` record is untouched.

### 4c. Goku (CONFIRMED playable)

- Goku is the player from the 14,1 barrier until `rom:0x3E93E8` seq 21. The entry scene and both fights address him as actor 0. r22 ss2 shows leader 4 in entry 20 with player +0x48 = `0x082CEDD4` (the `set:61` header).
- **Insert before the `11` (end) of `rom:0x3E8D98` seq 26 (record `rom:0x3E8D14`, end op at `rom:0x3E8D63`)**, the Rage pattern with Goku's ids, 28 bytes:
  `00 37 02 2E` (sound 55) `1D 02 00 12 02 39` (state 0, 9 on set 60) `00 0A 02 2A` (flash) `00 37 02 2F` (sound 55 off) `00 04 00 3D 02 49` (ext 73 (4, 61)) `00 0A 02 2B` (wait 10).
- Goku leads, so ext 73 changes his sprite and form at once. The next line, "Let's do this!" (speaker 1), then shows portrait 65.
- No refill is needed: seq 1 refills all records and the drain starts at the transform.

### 4d. Records that grow (CONFIRMED: one referencing word each, no jump ops)

| Record | Table word | Length | Insert |
|---|---|---|---|
| `rom:0x3E9384` ("Me? Fight Cell?" seq 21) | `rom:0x3E9438` | 0x61 | 6 bytes at `rom:0x3E93A6` |
| `rom:0x3E9E8C` (Cell fight seq 1) | `rom:0x3EA400` | 0x5E | 6 bytes (13 with the refill) at `rom:0x3E9E9F` |
| `rom:0x3E8D14` (entry seq 26) | `rom:0x3E8DFC` | 0x50 | 28 bytes at `rom:0x3E8D63` |

Copy each to the expansion area with `npc_gi.relocate()` and repoint the one word, as `npc_gi` and `rage_text` do. Apply the in-place set bytes first. `rom:0x3E9384` holds `0x3E939B` and `0x3E93C1`, and `rom:0x3E8D14` holds `0x3E8D1E` and `0x3E8D41`, so the copies must carry them.

---

## 5. Question 4: after Cell (CONFIRMED)

- **Gohan:** post-Cell seq 20 (relocated record `rom:0x89516C`, push at `rom:0x89534A`) runs `push 0 ; push 157 ; ext 73` after Cell is removed. That moves the leader from Rage (entry 4) to entry 2 (gi base), the sprite to 157 and the base form. `push 1 ; ext 70` follows. NPC Gohan is spawned as 157. His portrait is then 119 (entry 2). **Nothing to add.**
- **Goku:** playable Goku goes back to entry 19 at `rom:0x3E93E8` seq 21 through `appearance_revert`. NPC Goku is removed at `rom:0x3EB704` seq 23 (his teleport). Post-Cell seq 54 removes him from the party (ext 91 (4)). His Other World lines use portrait 64, which stays. **Nothing to add.**
- The Rage ext 73 always runs before the last two fights, so Gohan reaches post-Cell from entry 4, not 5.

---

## 6. Question 5: portraits (CONFIRMED, two shapes 19 = 19, `portraits_r22.txt`)

| Speaker | Records | Today shows | Design |
|---|---|---|---|
| NPC Gohan, raw 59 | `rom:0x3E8170`, `0x3E81A0` (14,1), `0x3E9230`, `0x3E934C` ("Me? Fight Cell?") | 119 (gi base, hook) | +3 byte `3B` to `3E` (62). The hook maps 62 to **115** while his record is entry 2 |
| Gohan as leader, speaker 1 | `rom:0x3E9D4C` seq 3; `rom:0x3EA400` seq 22, 24, 26 | 119 | **115** with no byte change (entry 5 +2) |
| Gohan in Rage, speaker 1 | `rom:0x3EA400` seq 28 on, `rom:0x3EB704` | 117 | unchanged |
| Goku as leader, speaker 1 | entry seq 2, 27; "Me? Fight Cell?" seq 2, 9, 11, 13, 18 | 63 (65 if I transformed) | **65** once transformed, no byte change (entry 20 +2). Seq 2 "I'll fight Cell first." stays 63 with the seq 26 transform |
| NPC Goku, raw 63 | `rom:0x3E9704`, `0x3E977C`, `0x3E9832`; `rom:0x3EA79C`, `0x3EA820`, `0x3EA8EC`, `0x3EA95C` | 63 | +3 byte `3F` to `41` (**65**) |
| Goku in Other World, raw 64 | 7 records in `rom:0x3EB704` and `rom:0x3EC758` | 64 | unchanged |
| 14,1 NPC Goku talk, type 3 raw 63 | `rom:0x3E850B` | 63 | option, with the 14,1 object |

Each record has exactly one table word (aligned scan). The status page follows the leader's entry (`status_portrait`), so it shows 115 or 65 with no change.

---

## 7. Patch design: `cellgames_ssj`

**Place:** append after the second `portrait_remaster` (the end of the r22 list). Any earlier position moves later allocations (R22 allocator rule). r23 list: `gohan_gi ssj2_form gohan_portraits status_bonus ssj2_idle cutscene_portraits npc_gi rage_text portrait_remaster status_portrait rage_stats portrait_remaster cellgames_ssj`.

**Inputs:** `alloc.notes["npc_gi"]["records"][0x3E8610]` for the relocated entry seq 1 copy (sites at copy + 0x5D and + 0x73; do not hard-code `0x8950F5`). Check `rom:0x42F0` = `0x08800000` (gohan_gi copy) and that `cutscene_portraits` notes exist (the 62 to 115 map).

| # | Change | Bytes | Label |
|---|---|---|---|
| 1 | Reverse copy entry 5 +1 | `rom:0x800065` `3B` to `9E` | CONFIRMED |
| 2 | NPC Gohan 157 to 158 | 8 script bytes + 2 map-object bytes (section 3b) | CONFIRMED |
| 3 | NPC Gohan portraits | `rom:0x3E8173`, `0x3E81A3`, `0x3E9233`, `0x3E934F`: `3B` to `3E` | CONFIRMED |
| 4 | Gohan SSJ at "Me? Fight Cell?" seq 21 | relocate `rom:0x3E9384`, insert `00 00 00 9E 02 49` before `00 00 02 46`; repoint `rom:0x3E9438` | CONFIRMED (code), LIKELY (in game) |
| 5 | Gohan SSJ again at Cell fight seq 1 | relocate `rom:0x3E9E8C`, same insert (option: `1D 02 00 CE 10 02 6E` = push 0,5000 ; ext 110 after it); repoint `rom:0x3EA400` | CONFIRMED (code), LIKELY (in game) |
| 6 | Goku transform at entry seq 26 | relocate `rom:0x3E8D14`, 28-byte insert before `11`; repoint `rom:0x3E8DFC` | CONFIRMED (pattern = vanilla Rage seq 27 bytes `rom:0x3EA33C`), LIKELY (look) |
| 7 | NPC Goku 60 to 61 | 28 script bytes (section 3b) | CONFIRMED |
| 8 | NPC Goku portraits | `rom:0x3E9707`, `0x3E977F`, `0x3E9835`, `0x3EA79F`, `0x3EA823`, `0x3EA8EF`, `0x3EA95F`: `3F` to `41` | CONFIRMED |
| 9 | Option: 14,1 NPC Goku | `rom:0x408D54` `3C` to `3D`, `rom:0x3E850B` `3F` to `41` | my choice |

Base 8 MB diff: 6 + 2 + 4 + 28 + 7 = 47 bytes, plus 3 table words (up to 9 bytes); row 9 adds 2. Expansion: the reverse-copy byte `rom:0x800065` and 2 bytes in the npc_gi copy. New data: three relocated records (0x67, 0x64 or 0x6B, 0x6C bytes) after the last r22 allocation (`rom:0x89C5D4`).

**Tests** (each site fails closed on its old bytes):
1. Every in-place byte: old and new; the patch raises on any mismatch.
2. Reverse lookup interpreter (`@0x080042BC` with the patched copy): 158 gives 5, 157 gives 2, 160 gives 4, 61 gives 20, 60 gives 19; 59 finds no entry.
3. ext 73 run in the Thumb interpreter: (0, 158) as leader gives record +8 = 5, player +0x48 = set 158 header, player +0x180 = `0x030021EC`; (0, 158) as non-leader writes only the record; (4, 61) gives entry 20; (0, 160) from entry 5 gives entry 4.
4. ext 70 (0) with Goku in 20 and Gohan in 5: Goku 19, Gohan 5, player set 158. ext 70 (1) with Gohan in 5: Gohan 2.
5. Each relocated record decodes op for op as the old one plus the insert; the table word points at the copy; the old record is unchanged; the insert sits before `push 0 ; ext 70` (Gohan) and the state 9 push sits before ext 73 (4, 61) (Goku).
6. Scene groups: in `rom:0x3E8D98` and `rom:0x3E93E8` every Gohan reference is 158 and a spawn or map object 158 exists; in `rom:0x3E93E8`, `rom:0x3E9D4C` and `rom:0x3EB704` every Goku NPC reference is 61 and each scene spawns 61; `rom:0x3EC758` stays 157; no stretch scene names 157 or 60 after the patch.
7. Portrait hook: raw 62 with entry 2 gives frame 115; entry 5 speaker 1 gives 115; entry 20 speaker 1 gives 65; raw 65 gives block word 65.
8. Anim rows: set 158 has 0, 1, 4, 6, 9; set 61 has 0, 1; set 60 has 9.
9. No ext 73 names 59 (shapes A and B on the patched ROM).
10. r22 to r23 diff proof: only the listed bytes and new data. A mutation check drops one site at a time.
11. The whole suite must still pass. Existing tests that pin Cell Games bytes (for example the npc_gi test that wants 157 in the Cell Games scenes) fail on purpose after this patch when they build the full list. Give those tests their own list (the list up to their patch).
12. Old states: run the RAM-word check of `scripts\one-time\2026-10-19-r20-build\states.py` for r23 against the 3 repointed table words and the changed records.

**Tool trap (as in NGI):** after the patch, table words `rom:0x3E9438`, `rom:0x3EA400` and `rom:0x3E8DFC` point into the expansion area. A tool that bounds table words to `rom:0x3B5000`-`0x420000` splits those tables.

---

## 8. Final decisions

1. **Goku transform point.** Seq 26 (recommended): he transforms after walking up to Cell, before "Let's do this!", and the fight starts right after. Seq 1 ("when he enters"): he transforms on arrival. But the Hercule part is long, the drain runs during scene commands, and 139 EP lasts about 46 s. He may drop to base before the fight.
2. **NPC Goku after he gives up.** Recommended: Super Saiyan until his teleport (anime), 28 bytes and 7 portraits. To keep him base there, drop rows 7 and 8.
3. **14,1 NPC Goku.** He shows only while someone else leads, before Goku enters. Recommended: keep base (he transforms on entering). Option row 9 makes him SSJ.
4. **EP refill at the Cell fight re-transform (row 5).** Without it, a Gohan with low EP after fight 1 reverts at once, with the revert animation, at the start of the Android 16 scene. Rage still works from base. With it, Gohan starts the Rage fights with full EP (a gameplay change). At "Me? Fight Cell?" he already has full EP (ss2: 134/134), so no refill is needed there.

---

## 9. Risks

| Risk | Cause | Prevention | Label |
|---|---|---|---|
| Gohan stuck in SSJ after the stretch | Record left in entry 5 | Rage ext 73 (0, 160) always runs before the last fights; post-Cell seq 20 ext 73 (0, 157) sets entry 2. No save point in zone 14 (no `0x08010AC7` record), so no mid-stretch save. Game over leads to "You have died!" and ext 97 | CONFIRMED (scripts, map dump), LIKELY (game over path) |
| Goku stuck in SSJ | Record left in entry 20 | ext 70 (0) at "Me? Fight Cell?" seq 21 runs `appearance_revert` (20 to 19) | CONFIRMED |
| Gohan base inside the stretch | Drain to 0, the B button, or ext 70 for the Cell Jr fights | Final decisions 1 accepts drain and B; the second insert re-applies SSJ after Cell Jr. Drain during the Android 16 scene can still drop him to base before Rage (cosmetic; Rage works from base) | LIKELY |
| ext 73 (0, 158) hang | Reverse copy entry 5 = 59 | Row 1 of the design; test 2 | CONFIRMED |
| NPC remove finds no actor | Script and map object disagree on 157 or 158 | Both map objects are in the change list; test 6 | CONFIRMED |
| Null animation row | Set 61 has no anim 9 | State 9 runs before ext 73 (4, 61); test 5 | CONFIRMED |
| Player and NPC share a set | Lookup returns the first object with that set pointer | NPC Gohan 158 is removed before Gohan leads; player Goku reverts before NPC Goku 61 spawns. A player who switches to Gohan at 14,3 before seq 21 meets the same overlap vanilla had (56 and 56) | CONFIRMED (order), LIKELY (switching) |
| Playable Gohan on 14,1 is base | He leads there only through Switch Characters | Not changed: a map-enter transform would leave him SSJ when he walks out. Open point | design choice |
| Old states | ss2 and ss3 were made before the patch | See section 10 | LIKELY |

---

## 10. Question 6: saves and the test slot (CONFIRMED, `save_r22.txt`, `states_r22.txt`)

| File | State | Use |
|---|---|---|
| `log2_poc_r22.sav` **slot 3** | Goku leads at the Lookout (9,1), Lv 40, `flag:191` set, 192-196 clear, arena maps 14,1-14,3 unvisited | **Primary test.** Fly to the Cell Games Arena and play the whole stretch |
| Slots 1, 2 | `flag:195` set (post-Cell) | Regression: Lookout portraits 119, Gohan base |
| `.ss2` | "Me? Fight Cell?" `rom:0x3E93E8` index 15; Goku leads in entry 20 (EP 19/139); Gohan entry 2 (EP 134/134) | Quick test of seq 16-21: "Okay. I'll do it." shows 115, Gohan leads in SSJ, Goku reverts, NPC Goku 61. The NPC Gohan already on screen is the old 157 object, but seq 21 reloads map 14,3 (ext 39) before its remove, so the remove of 158 finds the rebuilt object (LIKELY) |
| `.ss3` | Cell fight `rom:0x3EA400` index 22 (seq 1 already ran); Gohan leads in entry 2 | Tests NPC Goku 61 and portrait 65 in `rom:0x3EB704`, and Rage from base. It cannot test the SSJ start |
| `.ss1` | Title or debug (leader 3, flags clear) | Not for this test |

---

## 11. Open points

1. Whether the Super Saiyan tick runs while a text box waits for A is not traced. It runs during scene commands (form tick and state tick share `@0x08008766`).
2. Event triggers: whether each enemy event fires on defeat or at an HP threshold is LIKELY, not traced.
3. Playable Gohan on 14,1 (Switch Characters) stays base.
4. The command states behind ext 53-56 were not traced to their animations. The evidence that they use stand and walk only is LIKELY (vanilla runs set 61 NPCs with them).

---

## 12. Files

- New in `scripts\one-time\2026-10-20-cellgames-ssj\`: `maps14.py`/`.txt`, `scenes.py`, `scenes_r22.txt`, `tables.py`, `tables_r22.txt`, `states.py`, `states_r22.txt`, `save_r22.txt`, `anims.py`, `anims_r22.txt`, `setsites.py`, `setsites_r22.txt`, `design_sites.py`, `design_sites_r22.txt`, `portraits.py`, `portraits_r22.txt`, `bible_rows.md`.
- Not touched: every ROM, save and state, `data\`, `docs\`, `scripts\permanent\`, `tests\`, `builds\`, `scripts\one-time\2026-10-20-inject-tool\`.

## 13. Concerns

1. Not tested in game. The proof is bytes, listings and two-shape sweeps.
2. Brief deviation: one read-only Bash call started with `cd /dev/null`. It failed at once (not a directory) and changed nothing. All other calls used absolute paths.
3. The `npc_gi` copy offsets (`rom:0x8950F5`, `0x89510B`, `0x89516C`) are r22 values. The patch must read them from `alloc.notes`.
