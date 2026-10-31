# Super Perfect Cell study: aura, sprite set, portrait (2026-10-22)

Brief: `docs\tasks\2026-10-22-superperfect-study\superperfect-study.md`. Read only. Bases: r27 `log2_poc_r27.gba` (SHA-1 `5c4befd8...`, checked) and, after the parallel r28 build landed, r28 `log2_poc_r28.gba` (SHA-1 `eef01cf6aa37f660bbe0f07b87694d058252499c`, checked). Every address below is r28; r27 differs only where a row says so. My files are in `scripts\one-time\2026-10-22-superperfect-study\` only.

Labels: **CONFIRMED** = proved here by bytes, a code listing or a two-shape sweep. **LIKELY** = strong evidence, not proved in game. **SPECULATIVE** = a guess.

---

## 1. SHIPPED and PENDING

**SHIPPED (this study)**

| Ask | Answer | Where |
|---|---|---|
| "When perfect cell comes back after exploding, he should be in his super perfect cell form" | The stretch is 2 scene tables, 1 fight and 1 map: 68 script bytes, 2 map bytes, 1 enemy record. Design in section 6 | Section 2 |
| "the same sprite but with the same electrical aura that ssj2 gohan has" | Gohan's aura is baked into his frames. Cell gets a baked copy of set 30 with bolts, plus the existing idle hook for flicker | Section 3 |
| "just maybe bumped up in size" | Cell frames are already 64x64, the GBA maximum for one OBJ. Bigger bolts fit inside that frame beside and above him (up to 17-22 px each side, 6 px on top). An aura larger than 64x64 needs new multi-OBJ code | Section 3 |
| "Do we have room to add a whole new portrait?" | Yes. Fastest: id 52 is an unused vanilla portrait slot with Cell's frame ring. `inject.py portrait 52 <png>` works today with no code. A truly new id (122 or more) needs a block move and tool changes (1 extra task session) | Section 4 |
| Cell's stats (report only) | Type 25 (after the return): HP 8230, STR 60, POW 59, END 65 | Section 5 |

**PENDING (mine)**

| Item | Why |
|---|---|
| The Super Perfect Cell portrait PNG (64x64, OBJ palette, ring equal to id 40's) | Section 7 |
| Pick the bolt scale from preview GIFs (session 1 makes them) | Section 3 |
| Which anims get bolts (idle and walk only, as Gohan; or every anim) | Section 3 |
| Portrait id: 52 (recommended) or a new id 122 | Section 4 |
| Stronger stats or not | Section 5 |
| Scouter shows Super Perfect Cell (2 bytes) or not | Section 6 |

---

## 2. The stretch: where Cell shows after the self-destruct (CONFIRMED bytes, LIKELY triggers)

Cell before the self-destruct is `set:30` (Perfect). He spits out 18 and turns `set:29` (Semi-Perfect), swells to `set:27`, and Goku takes him away. He comes back as `set:30` again.

| # | Where | What Cell is | How the set is chosen |
|---|---|---|---|
| 1 | Table `rom:0x3EB704` (Cell type 24 death event, map 14,3) seq 40 "He's back!!!!" | NPC: `push 30,428,328 ; ext 51` | Raw set id in the script. Every later command finds him by set pointer (`find_actor_by_set` `@0x08009370`) |
| 2 | Same table seq 41-52 | Same NPC (hits Trunks, fights Vegeta) | Script actor 30 |
| 3 | Seq 52 | NPC removed (`push 30 ; ext 52`), then `push 12 ; ext 84` builds spawn item 12 of map 14,3 = enemy type 25 at its record position | Spawn record `rom:0x4090F8`, set word `rom:0x409108` = 30 |
| 4 | Seq 53-65, then the last fight | The type 25 enemy. Seq 65 `ext 90 (30, 20, 100)` shows its HP bar | Enemy ctor `sub_0800E280` takes the set from spawn +0x10 |
| 5 | Table `rom:0x3EC758` (type 25 death event) seq 1 | Loads map 14,4 | - |
| 6 | Seq 1-20 on 14,4 (Kamehameha struggle) | NPC from the 14,4 map record `rom:0x4091F8` (cond always), set word `rom:0x409204` = 30. Seq 20 removes him: Cell is beaten | Map record +0xC |

- **ext 84 (n)** = `sub_0800AAAE` > `sub_0800C73A`: builds spawn item n of the current map. Spawns with cond word 1 never build at map load (`condition_eval` returns 0), so all late Cell phases start by ext 84 (items 5, 8, 11, 12). CONFIRMED (listings).
- **Map 14,4** is loaded only by seq 1 of `rom:0x3EC758`: the only 5-value `push 14,4,...` in the ROM (`rom:0x3EB81D`). A warp record into 14,4 was not searched. LIKELY.
- **Records in r28:** `fullpower_ssj` moved seq 20 of `rom:0x3EC758` to `rom:0x89AB4C` (table word `rom:0x3EC7A4`). The r16 copy `rom:0x89516C` and the vanilla `rom:0x3EBE1C` are dead.

### 2a. Actor sites (two shapes, reconciled; `sites30_r28.txt`, `shapeb30_r28.txt`)

| Shape | Sites | Note |
|---|---|---|
| A: walk each record of the two tables by index (seq 40-65 and 1-55), model the stack (`ext 17` in place, binary ops and `neg` pop) and class each 30 by the op's set-arg slots (`sites.POS`) | 68 actor sites: 13 op 0 (`00 1E`), 55 op 29 list (`3C`); 8 more 30s are params | Exact list with byte offsets in `sites30_r28.txt` |
| B: `sites.shape_b` ('02 N' pairs decoded back) over the same byte ranges and both expansion copies | 118 | 54 equal to A. 64 B-only: 32 in the dead vanilla seq 20 (`0x3EBE1C`), 32 in the dead r16 copy (`0x89516C`). 14 A-only: behind `ext 17 ; add` or `neg`, which `sites.calls` does not model |

Records that hold actor sites: `0x3EACD0` (seq 40), `0x3EB134` (50), `0x3EB21C` (52), `0x3EB6E8` (65) in `rom:0x3EB704`; `0x3EB80C` (1), `0x3EBA4C` (7), `0x3EBC7E` (11), `0x3EBD7C` (17), `0x89AB4C` (20) in `rom:0x3EC758`.

> [!WARNING]
> `rom:0x3EB86A` is `push 30,30 ; ext 121`: the first 30 is Cell, the second is a param. Edit only the value byte `rom:0x3EB86C`. Also leave `push 0,30 ; ext 121` (`rom:0x3EB864`) and the `ext 134` third args alone.

---

## 3. The aura

### 3a. How Gohan's SSJ2 aura works today (CONFIRMED)

- **Baked into frames.** `scripts\permanent\art\gi_aura.py` draws 2-3 branched bolts from the transparent ring around the body: white core `pal:2` every third trunk pixel, glow `pal:191`, never on the face box (`face_box`: iris `pal:64`/`pal:65` grown 3 px). It bakes them into anims 0, 1, 4, 13 of `set:159` and `set:160`.
- **Idle flicker by code.** The idle row has 6 records per dir (index = body x 3 + shape). The `ssj2_idle` hook `rom:0x894E24` (vtable +4 of states 0 and 38) picks the shape every 8 ticks for sets 159 and 160 only (pool words `0x08869C7C`, `0x0888D870`).
- **No effect object.** Rage and SSJ2 make no aura object (T6, AUR). So "reuse the effect object" has nothing to reuse.
- **Size:** bolts reach a median 2-3 px and at most 8 px past Gohan's body (`measure_set159.txt`, `measure_set160.txt`).

### 3b. Cell's frames (CONFIRMED, `sets_r27.txt`, `measure_set30.txt`, `colors_set30.txt`)

- `set:30`: header `rom:0x242DBC`, slot 0x1000, 99 distinct frames, **every frame 64x64** at dx -20, dy -56. Rows 0 (2 per dir), 1, 2, 3, 5, 6, 7, 8, 12, 18. Dir 3 reuses dir 2 (H-flip).
- Free room inside the frame: idle left 18-22, right 17-22, top 6, bottom 0 px. Attacks and knockdown reach the frame edge.
- Cell is about 29 x 58 px against Gohan's 20 x 32, so about 1.8 times bigger.
- Colors: no `pal:191`, no iris 64/65, 1,246 px of white `pal:2` (his plates).

### 3c. GBA limits (CONFIRMED)

- One OBJ is at most 64x64. Cell already uses it, and the OAM build `@0x08007784` writes one OAM entry per object. So a baked aura can never pass the 64x64 box.
- OBJ VRAM: the slot comes from the set header u16 (0x1000). A baked copy keeps 0x1000, so VRAM use equals vanilla Cell. OAM count is unchanged.
- An aura larger than the frame needs a second object that follows Cell (new Thumb class, 2-4 more 64x64 OBJs at 4 KB each against 32 KB of OBJ VRAM in crowded scenes). High cost and risk.

### 3d. Options

| # | Method | Cost | Risk | Label |
|---|---|---|---|---|
| **A (chosen)** | Bake bolts into a copy of `set:30` with a Cell version of `gi_aura` (same outline family, bolts scaled about 2x: longer trunks and branches, 3-4 bolts, optional 2 px core). Idle row 6 records per dir; add Cell's set to the `ssj2_idle` hook for the flicker | 1 art session + 1 patch session | Low: same VRAM, no new object code. Art review by eye | CONFIRMED (fit), LIKELY (look) |
| B | Same, but draw the bolts at half size and scale them 2x (2 px blocky lines: "Gohan's aura magnified") | Same as A | Blocky next to Cell's 1 px detail | SPECULATIVE (look) |
| C | Separate aura object(s) attached to Cell, larger than 64x64 | New object class, OAM and VRAM work, 2-3 sessions | High: VRAM allocator returns -1 when full; z-order; scene and fight both | LIKELY (cost) |
| D | Recolor only (palette) | No | No: the OBJ palette is shared, so every user of those indices would change | CONFIRMED |

Design points for A:
- **Face rule:** `face_box` finds nothing on Cell. Session 1 must define a Cell face box (for example the bbox of his face skin `pal:209` in the head rows, grown 3 px) and check it by eye. SPECULATIVE which index is the face.
- **White core on white plates:** the bake rule already turns white over a bright pixel into 191. Bolts sit outside the body, so this matters only where they cross him.
- **Which anims:** Gohan has bolts on idle, walk, ki charge, run. Cell has no 4 or 13. Default: 0 and 1. My option: all rows (the fight shows attacks 5-8, 12, 18 and hurt 2, 3).
- **Idle flicker (CONFIRMED path, LIKELY in fight):** `npc_factory` `@0x0800D6DE` and the enemy ctor both build the object in state `0x03001F34` (state 38, vtable `0x08024BA0`), whose tick is the `ssj2_idle` hook. A chained hook (new code: compare Cell's new header, else jump to the old hook) and 2 repointed vtable words give Cell the same 3-shape flicker. Without the hook, keep 2 idle records per dir (one fixed pattern each). Whether the fight AI returns to state 38 when Cell stands is not traced.
- **Frame storage:** raw type 0 (4 KB each, about 110 frames, about 450 KB) or `pack(kind=1)` from the TRV compressor. Both unpack on the tint-table path (`@0x0801F3BA` does not unpack type 2).

---

## 4. A new portrait

### 4a. Ids today (CONFIRMED, `census_r27.txt`)

- Live block `rom:0x894EAC` (word 0 = `0x03000E90`, then ids 0-121). Its literal is `rom:0xBE10`; the `cutscene_portraits` hook pool holds it too.
- Users by shape: A text-valid record sweep (2,222), B records named by an aligned word (2,030 live), C appearance +2/+3, D scouter +0xC (read by the scouter screens `sub_08018C72` and `sub_08019320`), E the hook map (59 to 119, 62 to 115, 61 to 117).
- **No user at all:** ids 10, 13 (vanilla status twins of entries 2 and 5) and **52** (an unused vanilla dialog drawing, a green face in a white hood, `scripts\one-time\2026-10-22-superperfect-study\ids\id052.png`). The 16 raw byte shapes for 52 have no text and no pointer.
- Status ids 8-25 and twins 116, 118, 120 have no reader since `status_portrait`, but the tool refuses them (BG palette rule).
- **Status twin for Super Perfect Cell:** none needed. Cell has no appearance entry, as id 40 has none (R22).

### 4b. Plan

| Option | What | Code | Label |
|---|---|---|---|
| **P1 (recommended)** | Reuse id 52. Ring of 52 = ring of 40 (0 of 732 px differ, `rings.py`). I run `inject.py portrait 52 <png>`. The patch sets record +3 from `28` to `34` at 10 records | none for the portrait | CONFIRMED (tool rules), LIKELY (52 never shown) |
| P2 | New id 122: copy the block to a 124-word allocation in a new patch, repoint `rom:0xBE10` and the hook pool word, then change `art_inject._live_block` (it requires `rom:0xBE10` = the `npc_gi` block), `art_tables.MAX_ID` and the ring reference for an id with no vanilla frame, and the `inject.py` verify rules | 1 more task session | CONFIRMED (sites), LIKELY (cost) |

> [!WARNING]
> P2 has an order conflict: `art_inject` runs early in `build_list.txt` and checks the `npc_gi` block. A block grown by an appended patch does not exist when `art_inject` runs. Moving the block earlier moves every later allocation.

### 4c. Records to switch (two shapes 10 = 10: table walk and `records.py` sweep)

`+3` byte `28` to the new id (`34` for id 52):

| Table | Seq | Record | Byte |
|---|---|---|---|
| `rom:0x3EB704` | 41, 44, 51, 53, 55 | `0x3EAD70`, `0x3EADF8`, `0x3EB1C6`, `0x3EB264`, `0x3EB3D0` | record + 3 |
| `rom:0x3EC758` | 4, 6, 10, 16, 18 | `0x3EB89E`, `0x3EBA2A`, `0x3EBC58`, `0x3EBD68`, `0x3EBDF0` | record + 3 |

The self-destruct lines (seq 2, 5, 7) use 39 (Semi-Perfect) and stay.

---

## 5. Stats (report only, CONFIRMED)

Enemy table `@0x086D56AC`. One spawn record per type (aligned factory scan of the whole ROM).

| Type | Fight | HP | STR | POW | END | AI | EXP |
|---|---|---|---|---|---|---|---|
| 21-24 | Goku's fights, Gohan's first fight, the fight before the self-destruct | 6500 | 50 | 55 | 60 | 138 | 0 |
| **25** | **After the return (Super Perfect)** | **8230** | **60** | **59** | **65** | 138 | 0 |
| 26 | Cell Jr (x3) | 4990 | 46 | 50 | 46 | 21 | 0 |

Melee and ki factors are 128 for all. Type 25 entry: `rom:0x6D5904` (HP u32 +4, STR +0xC, POW +0xD, END +0xE). Only spawn `rom:0x4090F8` uses type 25, so a change there touches only this fight.

---

## 6. Design: patch `superperfect_cell` (appended after `fullpower_ssj`)

### 6a. Sprite set id

| Choice | How | Script edits | Label |
|---|---|---|---|
| **Id 58 (recommended)** | Sets 58 and 59 are dead in r28 by five shapes (`dead58_r28.txt`; control: the same shapes find every known set 30 site). Point the live table word `rom:0x88DAB8` at the new set. 58 encodes in one byte (op 0 `3A`, zigzag `74`) | All in place: `00 1E` to `00 3A` (13), `3C` to `74` (55). No record moves | CONFIRMED (shapes), LIKELY (no run-time id 58) |
| Id 161 | Relocate the 154-word set table (it touches the appearance table at `rom:0x88DC54`) and repoint `rom:0x959C`. 161 needs 2 bytes in a list (`82 42`) | 13 in place; 9 records grow (55 bytes) and move | CONFIRMED (sizes) |

### 6b. Changes

| # | Change | Bytes | Label |
|---|---|---|---|
| 1 | New set: copy of `set:30` layout with baked bolts (`log2_sprites.build_set`, `counts={0: 6}` when the hook is used), slot 0x1000 | new data | CONFIRMED (tool exists) |
| 2 | Set table word 58 (`rom:0x88DAB8`) to the new header | 3 bytes | CONFIRMED |
| 3 | 68 actor pushes (section 2a list) | 68 bytes in place | CONFIRMED |
| 4 | Enemy type 25 set word `rom:0x409108` and 14,4 NPC set word `rom:0x409204`: `1E` to `3A` | 2 bytes | CONFIRMED |
| 5 | 10 portrait bytes (section 4c) | 10 bytes | CONFIRMED |
| 6 | Chained idle hook: compare the new header, else `bx` to `rom:0x894E25`; repoint vtable words `rom:0x24BA4` and `rom:0x25A88` | about 0x30 bytes + 8 | LIKELY |
| 7 | Option: scouter entry 19 (`rom:0x6F8FBC`) +8 = 58, +0xC = 52. Entries 14-19 duplicate entry 13 and are never matched (first match wins), so this costs no other scan. Without it, `scouter_match` returns -1 and the scouter skips him | 2 bytes | CONFIRMED (code) |
| 8 | Option: type 25 stats | my values | - |

Read the seq 20 address from the notes chain (`npc_gi`, then `fullpower_ssj` `rom:0x89AB4C`), never hard-coded. Walk tables by index (r16, r27 and r28 tool traps).

### 6c. Tests

1. Every in-place byte: old and new; the patch raises on any mismatch, and on a second run.
2. Set 58 word names the new header; the new set decodes every record to w*h; rows equal set 30's rows; anim 0 has 6 records per dir with the hook (2 without).
3. Bolts: only `pal:2` and `pal:191` added, never on the Cell face box, body pixels unchanged; dir 3 flips dir 2.
4. Scene groups: in `rom:0x3EB704` seq 40-65 and all of `rom:0x3EC758`, every actor reference is 58 and each remove has a spawn, ext 84 or map record of 58; seq 1-39 still name 30; params unchanged (`rom:0x3EB864`, `0x3EB86D`, ext 134 args).
5. Interpreter: the chained hook gives sets 159 and 160 exactly the old sequence, set 58 the formula, every other set vanilla (512 ticks, 4 seeds).
6. Portraits: the 10 records read 52; records seq 2, 5, 7 read 39; no other record changed.
7. Dead-id guard: no ext 73, map field, appearance +1 or scouter names 58 except the new sites (fails if a later patch starts using 58).
8. Diff proof r28 to r29: only the listed bytes and the new data.
9. Whole suite. `test_idle.py:240` and `test_portraits.py:179` pin the set 58 table word ("armor Rage kept"); give them their own list or update them.

### 6d. My tests

Use `log2_poc_r28.sav` slot 3 (Goku leads at the Lookout, before the Cell Games). Play to the self-destruct. After "He's back!!!!" Cell shows bolts; his lines show the new portrait; the last fight and the 14,4 beam struggle show bolts; before the self-destruct he has none.

### 6e. Effort (LIKELY)

| Session | Who | Work |
|---|---|---|
| 1 | Me | Cell aura art: export set 30, face rule, scaled outline bolts (2-3 scale variants), preview GIFs for me |
| 2 | Me | Patch, hook, tests, r29 build, diff proof, bible rows |
| (3) | Me | Only for P2 (new portrait id 122) or option C (aura object) |

Total: **2 sessions** plus my art pick and portrait.

---

## 7. What I must make

1. **Portrait:** 64x64 PNG, OBJ palette colors that vanilla dialog portraits use (or `palette.json` entries), at most 64 colors, the outer 3 px ring equal to vanilla id 40 (the same as id 52). Start from `art\tables\portraits\040_cell_40.png`. Run `py -3 -P scripts\permanent\art\inject.py check <png> 52` first.
2. **Aura pick:** choose a bolt scale from the session 1 GIFs, and the anims.
3. **No sprite drawing is needed**: the body is set 30.

---

## 8. Concerns

1. Not tested in game. The proof is bytes, listings and two-shape sweeps.
2. A run-time set id 58 (ext 73 with run-time args) cannot be excluded statically. ext 73 (0, 58) already hangs today (no appearance entry), so no working script can pass it.
3. The fight AI's standing state is not traced, so the idle flicker in the fight is LIKELY.
4. The face index for Cell (`pal:209`) is SPECULATIVE; session 1 checks it by eye.
5. Brief deviation: one read-only Bash call started with `cd` (a failed, harmless search). All other calls used absolute paths.
6. The study ran on r27 first. r28 landed during the study; I re-ran the sweeps on r28. Only post-Cell seq 20 moved (`rom:0x89AB4C`).

## 9. Files

`scripts\one-time\2026-10-22-superperfect-study\`: `q.py`, `wordscan.py`, `sets.py`, `measure.py`, `colors.py`, `census.py`, `rings.py`, `render_ids.py`, `sites30.py`, `shapeb30.py`, `dead58.py`; outputs `scenes_r27.txt`, `scenes_r28.txt`, `sets_r27.txt`, `measure_set30.txt`, `measure_set159.txt`, `measure_set160.txt`, `colors_set30.txt`, `census_r27.txt`, `scouter_r27.txt`, `sites30_r27.txt`, `sites30_r28.txt`, `shapeb30_r27.txt`, `shapeb30_r28.txt`, `dead58_r28.txt`, `p40_sweep_r28.txt`, `ids\`; `bible_rows.md` (sections 4, 5a, 8, 14; tag `SPC`).
