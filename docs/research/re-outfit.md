# LoG II outfit selection (USA, ALFE)

Date: 2026-10-16. ROM SHA-1 `18e0715dec419f3501c301511530d2edcd590f8b`. Addresses are GBA addresses. "rom:0x..." is a file offset (address minus 0x08000000).

Labels: **CONFIRMED** = proved here with quoted bytes or disassembly. **LIKELY** = strong evidence, not proved. **SPECULATIVE** = a guess.

I verify each CONFIRMED line before Task 5 starts (plan Task 3 Step 4).

## Result in one paragraph

Every playable path reads the sprite set id from appearance table byte +1 (`rom:0x1D967C + 20 * appearance + 1`) and resolves it through `get_set` at 0x08009324. Cutscenes do not use that path. They spawn and address Gohan with the literal set id 56, or they set the player sprite directly from the ext op 73 argument. So my rule can be met with data changes only. Task 5 changes entry 2 +1 (rom:0x1D96A5, 0x38) and entry 5 +1 (rom:0x1D96E1, 0x3B) to new set ids. It also repoints two literals: rom:0x42F0 (`7C 96 1D 08`) to an unchanged copy of the appearance table, and rom:0x959C (`90 4E 3B 08`) to an extended copy of the set table. The first literal, rom:0x42F0, prevents the hang: it is the only literal of the reverse lookup 0x080042BC (`080042be ldr r4,=0x081d967c`), so without the unchanged copy ext op 73 cannot find set 56 and the game hangs on an assert screen. The second literal, rom:0x959C, gives ids 157-159 their set table words. The 12-byte "item" after some record lists is the start of the next frame header or set header. The game never reads it, because each animation's frame count is in code. A clone does not need to copy it.

---

## 1. Appearance table fields

The table holds one 20-byte entry per character look. The character record byte +8 is the entry index.

Gohan's entries (bytes from `rom:0x1D967C`, CONFIRMED):

| Entry | Bytes +0..+5 | +0 | +1 set | +4 | +5 | Meaning |
|---|---|---|---|---|---|---|
| 0 | `00 35 38 08 00 00` | 0 | 53 | 0 | 0 | Demon Clothes |
| 1 | `00 37 3A 09 01 01` | 0 | 55 | 1 | 1 | Purple and white outfit |
| 2 | `00 38 3B 0A 05 05` | 0 | 56 | 5 | 5 | Battle armor: post-chamber and post-Cell |
| 3 | `00 39 3C 0B 02 02` | 0 | 57 | 2 | 2 | Casual green (default) |
| 4 | `03 3A 3D 0C 02 02` | 3 | 58 | 2 | 2 | Rage, Cell fight (ext 73 with 58 at 0x083EA369) |
| 5 | `01 3B 3E 0D 04 02` | 1 | 59 | 4 | 2 | Super Saiyan |

- **+4 = transform target, +5 = revert target. CONFIRMED.** Transform routine 0x08014D58: `08014d8c ldrb r0,[r5,#0x4]` (transform) or `08014d90 ldrb r0,[r5,#0x5]` (revert), then `08014d92 strb r0,[r6,#0x8]` (record +8). Load routine 0x08003ED4 reverts every transformed non-leader with +5 (`08003ef8 ldrb r3,[r3,#0x5] ; strb r3,[r2,#0x14]`).
- Entry 2 transforms to entry 5 (Super Saiyan, set 59). Entry 5 +4 = 4, which is the Rage entry (set 58). 0x08014D58 takes +4 whenever its argument is nonzero. Its callers are not traced. If play can reach +4 from Super Saiyan, playable Gohan shows set 58 (armor). Answered by `re-forms.md` section 2, last paragraph: entry 5 +4 = 4 is never read in play (CONFIRMED by three facts), so Super Saiyan always reverts and never reaches Rage.
- +2 and +3 are image ids passed to 0x0800BDCC (0x08026440 reads +2, 0x08003A8C reads +3). LIKELY portraits. They do not change the sprite.
- +0x10 is a pointer to a per-form object in IWRAM (0x030021E0, 0x030021E4, 0x030021EC). The code calls its vtable +0xC on leaving a form and +8 on entering it (0x08014D82, 0x0800A92E). CONFIRMED (calls). Purpose LIKELY form effects (Task 4).
- +6 is a frame count, +8 a frame bit mask, used by the state update at 0x080083C2 (section 7). CONFIRMED.
- The same routine also reads +7 (`0800850c ldrb r1,[r5,#0x7] ; cmp r0,r1`, a frame bound) and +0xC as a word (`0800843c ldr r2,[r5,#0xc]`, `08008448 ldr r1,[r5,#0xc]`, each followed by a `mul`). r5 is the appearance entry (`080083e6 add r5,r0,r1` after `ldr r1,=0x081d967c`) and is not reassigned before 0x0800850C. CONFIRMED (reads). Meaning of +0xC not traced. Forms (+0x10) are in `re-forms.md`.

## 2. How a set id becomes a sprite set (CONFIRMED)

`get_set(id)` at 0x08009324 has three paths:

```
08009324  push {r3,lr} ; ldr r1,=0x083b5c78 ; cmp r0,#0 ; bne 0x800934c
0800932c  ldr r0,=0x03001fa8 ; ldr r0,[r0] ; cmp r0,#0 ; beq 0x8009338
08009334  ldr r0,[r0,#0x48]              ; id 0 with a player object: the player's current set
08009338  ldr r0,[r1,#0x20] ; ldrb r1,[r0] ; ... add r0,#0xc ; bl 0x0802645c   ; id 0, no player: leader's appearance
0800934c  cmp r0,#7 ; bge 0x8009364
08009350  sub r0,#1 ; (r0*28) + [r1+0x20] + 0xC ; bl 0x0802645c   ; ids 1-6: record (id-1), appearance +1
08009364  ldr r1,=0x083b4e90 ; lsl r0,#2 ; add ; sub #0x40 ; ldr r0,[r0,#0x24]  ; id >= 7: table entry id-7
```

- `[0x083B5C78 + 0x20]` is the word at rom:0x3B5C98 = `0x03000E90`, the game state struct. So ids 1-6 are the six character records, not run-time sprite slots. This replaces the earlier LIKELY "party slots" reading.
- 0x0802645C: `ldrb r0,[r0,#0x8] ; ldr r1,=0x081d967c ; ... ldrb r0,[r0,#0x1] ; bl 0x08009324`. It reads record +8, then appearance +1, then calls `get_set` again.

### Paths that give the player or a party sprite its set

Every path reads appearance +1. None reads a hard-coded Gohan set.

| Address | What | Reads |
|---|---|---|
| 0x0800C584 (load at 0x0800C5C4) | Map load: makes the player object with `get_set(appearance[leader].+1)` | +1, CONFIRMED (`0800c5ce ldrb r0,[r0,#0x1] ; bl 0x8009324`) |
| 0x080085FC | Player object refresh: `player+0x48 = get_set(appearance[leader].+1)` | +1, CONFIRMED |
| 0x0800A680 | ext 115 and ext 70 (set leader): `player+0x48 = 0x0802645C(record)` | +1, CONFIRMED (`0800a6ce bl 0x802645c ; str r0,[r4,#0x48]`) |
| 0x08011172 | Save point "Switch Characters": `player+0x48 = get_set(appearance.+1)` | +1, CONFIRMED (`080111e4 ldrb r0,[r0,#0x1] ; bl 0x8009324 ; str r0,[r7,#0x48]`) |
| 0x08014D58 | Transform and revert: new appearance from +4 or +5, then `player+0x48 = get_set(+1)` | +1, CONFIRMED (`08014d9c ldrb r0,[r0,#0x1] ; bl 0x8009324 ; str r0,[r4,#0x48]`) |
| 0x08010BCE | Switch Characters menu: one sprite per party member | +1, CONFIRMED (decompiled) |
| 0x08001AB8 | File screen character sprites | +1, CONFIRMED (decompiled) |
| 0x08009350 | Script and map ids 1-6 | +1 through 0x0802645C, CONFIRMED |
| 0x08018EFC | Scouter database sprite: entry 36 "Gohan" at 0x086F8E40 uses id 1 | +1 through ids 1-6, CONFIRMED (entry bytes `23 b6 6f 08 29 b6 6f 08 01 00 00 00`) |

The search shapes were: every literal pool word 0x081D967C (18 pools, 24 `ldr` sites), and every BL to 0x08009324 (17), 0x0802645C (3), 0x080042BC (3) and 0x08003ED4 (4). Every site is in the table above or in section 3, or reads only +0, +2, +3, +4, +5, +6, +7, +8, +0xC or +0x10. A site that computes the table address another way would not appear.

- The 17 BLs to 0x08009324 include 0x08009380 (in 0x08009370) and 0x0802646C (in 0x0802645C). Re-counted 2026-10-16 with four shapes: Thumb BL pairs at any byte alignment (17), ARM B/BL (0), pointer words 0x08009324 or 0x08009325 (0) and Thumb B (0). Sites: 0x08001ADC, 0x08008626, 0x08009380, 0x0800A952, 0x0800AF1C, 0x0800B01A, 0x0800B718, 0x0800C5D0, 0x0800D6E4, 0x0800E2A2, 0x08010C50, 0x080111E6, 0x08014D9E, 0x08018F24, 0x0801902C, 0x08019114, 0x0802646C. CONFIRMED. (Ruling 9 asked for 18; that count did not reproduce.)

## 3. ext op 73 and the reverse lookup (CONFIRMED)

ext op 73 (handler 0x0800A8EC, ext table 0x083B5D28) takes `(character, set id)`.

```
0800a944  add r0,#0xc ; add r1,r6,#0 ; bl 0x80042bc      ; record +8 = first entry whose +1 == set id
0800a94c  cmp r4,#0 ; beq 0x800a96c                      ; r4 = player object only if character == leader
0800a950  add r0,r6,#0 ; bl 0x8009324 ; str r0,[r4,#0x48] ; player sprite = get_set(raw set id)
```

- 0x080042BC scans entries 0-21 for `+1 == set id` (`080042ca ldrb r3,[r3,#0x1] ; cmp r3,r1`, `080042d6 cmp r2,#0x16`). Its table base comes from the literal at rom:0x42F0 (`7C 96 1D 08`), loaded only by `080042be ldr r4,=0x081d967c`.
- **No match hangs the game.** `080042e4 bl 0x801f878` with "K:\Source\CharacterData.cpp" and "Unable to find sprite index in character display data" (rom:0x4300). 0x0801F878 draws the text and ends in `0801f972 b 0x801f972`.
- Callers of 0x080042BC: ext 73 (0x0800A948) and the debug routine (0x08005CB2 with 53, 0x08005CBC with 128).
- ext 73 sets the **player** sprite from the raw argument, not from the appearance table. This is why cutscenes show armor even after the appearance resolves to the gi.

## 4. How scripts find an actor (CONFIRMED)

Scripts name an actor by a set id. 0x08009370 calls `get_set(id)` and then sends message 5 with that set pointer to every object (0x08006E0A). The sprite base handler answers:

```
0800786c  cmp r1,#0x5 ; beq 0x8007894
08007894  ldr r1,[r0,#0x48] ; cmp r1,r2 ; beq <return self> ; mov r0,#0   ; match = same set pointer
```

So the match is by set pointer. After the patch, id 56 finds only an actor whose set is the armor set, and id 1 or 0 finds the actor that wears the patched set. Section 5 shows which script references exist.

## 5. Users of sets 55 and 56

### Scripts

Search shape: every `02 N` (call ext N) for the 34 ext ops that pass an argument to 0x08009370 or 0x08009324, plus ext 73, decoded back to its constant pushes (`scripts\one-time\2026-10-16-task-3-outfit-research\extscan.py`, `setargs.py`). A set id computed at run time (a variable) would not appear.

| Script | Op and args | Leader at that point | Class |
|---|---|---|---|
| 0x083B8DD5, 0x083C32B9 | ext 73 (0, 55) | before the chamber | cutscene, appearance 1 |
| 0x083B84F9, 0x083C30BB-0x083C3169 | ext 51/53/54/52/55 on 55 | before the chamber | cutscene NPC |
| 0x083DB5D0-0x083DB62B | ext 39 load map 9,1; ext 51 spawn 60 (Goku) and 56 (Gohan) as NPCs; Piccolo, Trunks, Vegeta spawned only when not leader; then **ext 73 (0, 56)** | not Gohan (LIKELY: Gohan and Goku are spawned unconditionally) | cutscene: chamber exit. Sets appearance 2 only |
| 0x083DBD63-0x083DBD6E | ext 54 (56, 840, 480), ext 52 (56) | Goku (ext 70 with 4 at 0x083DBC62) | cutscene NPC walks off |
| 0x083E866C-0x083E939C | ext 51 spawn 56 at the Cell Games; ext 55/56 on 56; ext 52 (56) removes him | not Gohan | cutscene NPC |
| 0x083E93A8 | ext 70 (0): Gohan becomes the player in the Cell Games | Gohan | **playable**, sprite from appearance 2 |
| 0x083EA369 | ext 73 (0, 58): Rage | Gohan | Cell fight, set 58 direct (unchanged) |
| 0x083EBFF8 | **ext 73 (0, 56)**, then ext 62/55 on actor 0, then ext 70 (1) at 0x083EC00F | Gohan, then Piccolo | cutscene: player sprite set to armor directly |
| 0x083EC021-0x083EC2D6 | ext 51 spawn 56 and moves | Piccolo | cutscene NPC |
| 0x083EC690 | ext 35 load Capsule Corporation | Piccolo | then playable through Switch Characters |

- No script addresses Gohan as actor id 1 by a constant push. A run-time variable id would not appear in this search. The three constant hits (0x083E3C65, 0x083E3E83, 0x083F3B8B) are text records and a pointer table, not script code. CONFIRMED by the bytes (`0a 00 01 02 21 "GOHAN: DADDY!!!"`).
- Between ext 73 at 0x083EBFFC and ext 70 at 0x083EC00F, the script addresses Gohan only as actor 0 (`push 0,472,480 ; ext_62`, `push 0,1 ; ext_55`). Actor 0 returns the player's own set, so the lookup matches. CONFIRMED.
- ext 141 (Scouter scan) is never called with 55 or 56.
- False positive dismissed: `ext_112 at 0x84011cb ... stack [0, 56, 104]` (extset.txt). The bytes are a map record for factory 0x0800D00E, not script code: rom:0x4011C0 = `0F D0 00 08 4C 00 00 00 38 00 68 02 70 00 90 02`. The "02 70" is the high byte of 616 and the low byte of 112. Its halfwords 56, 616, 112, 656 are LIKELY a rectangle. CONFIRMED (bytes).

### Map objects

Search shape: every map object record in the 327 map entries (`conds.py` lists, 1984 records), any u32 equal to 55 or 56 in the first 0x20 bytes, then checked against the factory code.

| Map entry | Map | Record | Factory, field | Condition | Class |
|---|---|---|---|---|---|
| 7 | 2,1 East District 439 | 0x083EDACC | 0x0800D6DE, +0xC = 55 | flag 66, not flag 68, leader 1 | NPC before the chamber |
| 323 | 14,1 Cell Games Arena | 0x08408C90 | 0x0800B710, +0x10 = 56 | leader is not Gohan and flag 195 clear | **NPC in armor while another character leads** |
| 325 | 14,3 | 0x08408F80 | 0x0800D6DE, +0xC = 56 | flag 192 clear | NPC (the Cell Games script removes it with ext 52 (56)) |

- False positives removed: in factory 0x0800E77E records, +8 is an enemy type (`0800e780 ldr r1,[r0,#0x8]`, times 24, table 0x086D56AC). No enemy entry uses sets 53 to 59. Factory 0x0800FFE6 (map entries 65, 79, 204, 235) reads only record +0x14, a script pointer (`08010004 ldr r1,[r0,#0x14] ; bl 0x800b4ae`), then runs that script (`bl 0x800b4fc`). It calls no NPC factory and no `get_set`, so its 56 values are not set ids. CONFIRMED (code). That they are trigger coordinates is LIKELY (neighbors 0xE8, 0xD0, 0x118, 0x120).

### Summary

- **Playable** (goes through appearance +1): map load, player refresh, set leader (ext 70, ext 115), Switch Characters, transform, the two menus, the Scouter database entry, ids 1-6.
- **Cutscene or NPC** (literal set id): every ext 51/52/53/54/55/56/62 on 55 or 56, the map objects above, and the player sprite set by ext 73.

## 6. Patch site for Task 5

The rule from the brief holds: cutscenes use set ids directly, playable Gohan uses appearance 2. So the conflict case (BLOCKED) does not apply.

| # | rom offset | Original bytes | New value | Why |
|---|---|---|---|---|
| 1 | `0x1D96A5` | `38` | gi base set id (first free id is 157, 0x9D) | appearance 2 +1: playable armor becomes the gi. Old saves keep appearance 2 |
| 2 | `0x1D96E1` | `3B` | gi Super Saiyan set id (for example 158, 0x9E) | appearance 5 +1: the transform target of entry 2 |
| 3 | `0x42F0` | `7C 96 1D 08` | GBA address of an unchanged copy of rom:0x1D967C-0x1D9833 (440 bytes) | only literal of 0x080042BC (ldr at 0x080042BE). ext 73 (0, 56) still finds entry 2, and (0, 58) still finds entry 4 |
| 4 | `0x959C` | `90 4E 3B 08` | GBA address of a copy of rom:0x3B4E90-0x3B50E7 (150 words) plus one word per new id | only literal of the set table (ldr at 0x08009364). Id N uses word N-7. rom:0x3B50E8 starts another table (literal refs 0x08008014, 0x080082B4, 0x080085F8), so the table cannot grow in place |

- Set ids are a u8 (`080042ca ldrb`, `08014d9c ldrb`). New ids must be 157 to 255.
- Sets 55, 56, 58 and 59, and their table words, stay unchanged. Word 49 (set 56) = 0x08299C48 and word 52 (set 59) = 0x082B69C8 in the copy too.
- The copy for item 3 must hold the **original** +1 values. Only +1 is compared, so later changes to other fields of the real table do not need the copy.
- Effects after the patch (LIKELY, from sections 2-5; test in game):
  - Chamber exit cutscene: Gohan is an NPC with set 56: armor.
  - Next time the player picks Gohan (Switch Characters, or ext 70 (0) at 0x083E93A8): gi.
  - Cell Games: the NPC Gohan is armor until 0x083E939C, then the player Gohan is the gi. Rage stays set 58. The post-Cell scene is armor (ext 73 sets the player sprite to 56 directly).
  - A save with appearance 2 loads with the gi. The file screen and Switch Characters menu show the gi.
- Suggested Task 5 test: `test_ext73_reverse_lookup_unchanged` reads the table at the rom:0x42F0 literal and asserts the first entry with +1 == 56 is 2, with 58 is 4, with 53 is 0.

> [!WARNING]
> Do not repoint entry 2 alone. Without item 3, the two `ext 73 (0, 56)` calls (0x083DB62B, 0x083EBFFC) hang the game on the CharacterData.cpp assert screen.

> [!NOTE]
> Task 6: 0x080042BC stops at 22 entries (`cmp r2,#0x16`), and rom:0x1D9834 (EXP table) follows the table. A new appearance entry needs a relocated table and the other 17 literals moved. rom:0x42F0 stays on the copy in item 3. Plan and patch sites: `re-forms.md` sections 6 and 7.

## 7. Animation end and the 12-byte item (Ruling 7)

The game never searches a record list for its end. Each state routine sets the animation row and computes the frame index itself.

**Record lookup.** 0x0800775A, CONFIRMED:

```
0800775a  ldrb r2,[r0,#0x10] ; ldr r1,[r0,#0x4c] ; lsl r2,#2 ; ldr r1,[r1,r2]   ; list = row[obj+0x10]
08007762  ldrh r2,[r0,#0x14] ; r2*12 ; add r1,r2 ; str r1,[r0,#0x3c] ; mov r0,#1 ; bx lr
```

- obj+0x4C is the animation **row** (`set + 12 + 16*dirs + anim*dirs*4`). obj+0x10 is the **direction**. This corrects SPR, which calls obj+0x10 the animation table index.
- There is no bound check and no terminator test. The upload at 0x08007772 multiplies w*h and DMAs that many bytes with no zero check (`080077d8 ldrb r1,[r0,#2] ; ldrb r2,[r0,#3] ; mul r1,r2`).

**Who advances obj+0x14.** Enter and tick routine pairs. Each pair sits in one vtable, and the vtable entries are offsets from the vtable base. CONFIRMED:

| Vtable | Enter | obj+0x4C | Anim | Tick | Frame index | Frames |
|---|---|---|---|---|---|---|
| 0x08024BA0 | 0x08007554 | set+0x4C | 0 | 0x08007570 | 1 if `(tick & 0xFF) > 0xF0`, else 0 | 2 |
| 0x08024A00 | 0x08007520 | set+0x5C | 1 | 0x08007532 | `(tick << 27) >> 30` | 4 (loops) |
| 0x08024B8C, 0x08025D0C | 0x08007520 | set+0x5C | 1 | 0x0801C120, 0x0801CF8C | `(tick << 27) >> 30`, `(tick << 28) >> 30` | 4 |
| 0x08025500 | 0x08010760 | set+0x14C | 16 | 0x08010774 | `tick >> 3` until tick reaches 0x38, then message 0 | 7 |
| 0x08025E20 | 0x08008390 (calls 0x08010760) | set+0x14C | 16 | 0x080083C2 | `tick >> 2` until it reaches appearance +6 (6), then message 0 | 6 |
| 0x08024824 | 0x0800E7A0 | set+0x10C | 12 | 0x0800E7B4 | `(tick << 27) >> 30` | 4 (enemy factory) |

- In sets 53, 56, 58 and 59, `frames_of()` gives anim 0 = 2, anim 1 = 4 and anim 16 = 7 records in all 4 directions. That equals the code counts. CONFIRMED.
- The strh-to-+0x14 search found 117 sites in rom:0x0-0x30000. The sites in the 7 tick routines and 4 enter routines above were checked. The rest were not. For the other animations, the record count equals the `frames_of()` count: LIKELY. Reason: reading one record past a list end would take a frame header word as the record +8 pointer (for example 0x20001145), and the upload has no guard. The original game would show garbage or crash there.

**The 12-byte item.** CONFIRMED by `scripts\one-time\2026-10-16-task-3-outfit-research\tails2.py` over sets 53, 55, 56, 57, 58, 59:

- Each list that frames_of stops early ends on one of two things. In set 56: 40 lists end at the next list, 17 at a frame header that a record of a walked set uses, and 1 at the set's own header (anim 20 dir 3, `00 04 15 10 08 00 00 00 00 00 00 00` = set 56 header at rom:0x299C48).
- `01 00 00 00 00 02 00 00 45 11 00 20` is `u32 type = 1`, `u32 size = 0x200`, then the first stream word. The top byte 0x20 is the literal-mode code `001 0000 0` that starts every stream (SPR). It is not a pointer into RAM.

**Answer for the clone.** A cloned record list does **not** need the item. Copy exactly the records `frames_of()` returns. Record counts per animation: anim 0 = 2, anim 1 = 4, anim 16 = 7 are CONFIRMED. The rest are LIKELY exact (`scripts\one-time\2026-10-16-task-3-outfit-research\tails_all.txt`).

## 8. Open questions

1. **Answered by me (2026-10-16, design 6.6):** "once Gohan has the gi (from the first moment he is playable after the chamber), every later cutscene and NPC appearance uses the gi too. This includes the Cell Games Arena NPC and the post-Cell scene". Slice 1 leaves these in armor on purpose and changes them in the slice after my test slice 1. Changing it needs a script or map edit, not the appearance patch.
2. **Answered by me (2026-10-16, design 6.6):** same quote as question 1. The post-Cell scene uses the gi in a later slice. In slice 1 the sequence stays armor NPC, gi player (from 0x083E93A8), Rage (set 58), armor in the post-Cell scene.
3. Scouter: entry 36 "Gohan" uses id 1, so it shows the gi after the patch. Scanning an armored NPC Gohan no longer matches entry 36 (0x08019102 compares set pointers). Minor.
4. ext 29 / ext 30 (0x08009740, 0x0800975E) broadcast message 4 with `2n+1` / `2n` to every object. CONFIRMED (code). That this means "party add / remove" stays LIKELY.
5. Not checked in game: everything in section 6 "Effects".

## Files

| File | Purpose |
|---|---|
| `scripts\one-time\2026-10-16-task-3-outfit-research\extscan.py`, `setargs.py` | Find ext op calls and their constant set id arguments |
| `scripts\one-time\2026-10-16-task-3-outfit-research\extset.txt`, `ext73.txt`, `extleader.txt` | Scan output (ext ops with a set argument, ext 73, ext 70 and 115) |
| `scripts\one-time\2026-10-16-task-3-outfit-research\sweep.py`, `cell.txt` | Linear script disassembly with resync, Cell Games region |
| `scripts\one-time\2026-10-16-task-3-outfit-research\mapsets.py` | Map object records holding a set id |
| `scripts\one-time\2026-10-16-task-3-outfit-research\tails.py`, `tails2.py`, `tails_56_59.txt`, `tails_all.txt` | Record counts and what follows each record list |
| `scripts\one-time\2026-10-16-task-3-outfit-research\decomp1.txt`, `decomp2.txt`, `decomp2c.txt` | Ghidra decompiles of the appearance readers and the ext ops |
