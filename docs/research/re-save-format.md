# LoG II save format (USA, ALFE)

Date: 2026-10-16. ROM SHA-1 `18e0715dec419f3501c301511530d2edcd590f8b`. Addresses are GBA addresses. "ROM 0x..." is a file offset (address minus 0x08000000).

Labels: **CONFIRMED** = proved here with quoted evidence. **LIKELY** = strong evidence, not proved. **SPECULATIVE** = a guess.

I verify it and run the in-game test.

## Result in one paragraph

The game keeps the whole 8 KB EEPROM image in a RAM shadow and uses only the first 0x448 bytes: one options block at 0x000 and three save slots of 0x168 bytes from 0x010. Each slot is a 0x164-byte copy of the game state struct at IWRAM 0x03000E90, followed by a little-endian Adler-32 of those bytes. The options block adds 0x12345678 to its Adler-32. In the .sav file every 8-byte block is byte-reversed against RAM. My .sav holds no game data (the game never saved to it), so the checksum could not be proved on it. It is proved from the code instead. `scripts\permanent\rom\log2_save.py` reads, checks and writes the format. `test-data\saves\log2_lv40_postcell.sav` holds three post-Cell, level 40 slots. `test-data\saves\log2_lv40_cellgames.sav` (2026-10-18) holds two post-Cell slots (Capsule Corporation, Master Roshi's Island) and one slot on Dende's Lookout before the Cell Games.

## 1. Routines and checksum

| Address | What | Label |
|---|---|---|
| 0x080218E0 | `IdentifyEeprom(kbits)`: 4 selects type 0x087FD644 (512 B), 64 selects 0x087FD650 (8 KB). The game calls it with 0x40 at 0x08021458 | CONFIRMED |
| 0x08021ACC | `ReadEepromDword(addr, dst)` (Nintendo EEPROM_V122 library) | CONFIRMED |
| 0x08021CB0 | `ProgramEepromDword(addr, src)`, calls 0x08021B7C (program) and 0x08021C58 (verify) | CONFIRMED |
| 0x08021454 | Save init: identify, `malloc(0x2000)` (0x0801F08C) to the shadow pointer at 0x03003898, read all 1024 dwords into it. The captures show the shadow at 0x0203E000 | CONFIRMED |
| 0x080214C4 | `write(obj, offset, src, size)`: DMA3 src to shadow+offset, then program each dword of the range | CONFIRMED |
| 0x08021526 | `read(obj, dst, offset, size)`: DMA3 shadow+offset to dst | CONFIRMED |
| 0x0802153E | Checksum `(ptr, len)`: Adler-32. a = 1, b = 0, blocks of 0x15B0 (5552) bytes, then mod 65521 through 0x08027F1C | CONFIRMED |
| 0x08027F1C | ARM after a `bx pc` veneer: `ldr r3,=0x80078071 ; umull r1,r2,r3,r0 ; ldr r3,=0xFFFF000F ; mov r1,r2,lsr #15 ; mla r0,r3,r1,r0 ; bx lr`. That is r0 - (r0 / 65521) * 65521 | CONFIRMED (decoded by hand from bytes `e59f3010 e0821093 e59f300c e1a017a2 e0200193 e12fff1e`) |
| 0x08001E4A / 0x08001EC0 | Options load / save, 8 bytes at EEPROM 0x000 | CONFIRMED |
| 0x08003F9C | Slot load: read 0x168 bytes from 0x10 + n * 0x168, compare `adler32(0x164 bytes)` with the u32 at +0x164, copy on match, else default init 0x08003C24 | CONFIRMED |
| 0x08003FEC | Slot write (used by Delete Game at 0x08001B24) | CONFIRMED |
| 0x08004030 | Save game: copies map zone/area/variation into +2..+4, player x,y into +0x160/+0x162, sets +1 bit 0, checksums and writes the slot named by the byte at 0x03000E8C | CONFIRMED |
| 0x08001848 | Continue: copy the slot into 0x03000E90, then load map (zone +2, area +3) with variation +4 and position +0x160 through 0x0800C584 | CONFIRMED |

Key code (Thumb):

```
08003F90  mov r1,#0xff ; add r1,#0x65 ; bl 0x0802153E   ; checksum(slot, 0x164)
08003FB0  mul r2,r6 ; add r2,#0x10                      ; offset = 0x10 + slot * 0x168
08003FCE  ldr r1,[r1,r5] ; cmp r0,r1                    ; compare with u32 at +0x164
08001E64  bl 0x0802153E ; ldr r1,=0x12345678 ; add r0,r1  ; options check = adler32(4 bytes) + 0x12345678
08021B44..08021B6A  4 halfwords, 16 bits each MSB first, stored at dst+6, dst+4, dst+2, dst+0
```

**Byte order (CONFIRMED for the game side, LIKELY for mGBA).** ReadEepromDword stores the first 16 bits it receives at dst+6 and moves down. mGBA keeps the EEPROM bit stream MSB first in file order. So RAM byte j of a block equals file byte 7 - j. `swap_blocks()` in the tool does this in both directions. The captures cannot show it, because every byte in the real image is FF or 00.

**Proof on the real .sav: not possible.** `data\roms\...(USA).sav` is 0x200 bytes of FF then zeros, and the three state files embed the same image. The options block and all three slots fail their checks. The game shows them as empty. The test file therefore rests on the code reading above, and the tool checks its own Adler-32 against `zlib.adler32` on every slot.

## 2. EEPROM map

| EEPROM offset | Size | Content |
|---|---|---|
| 0x000 | 4 | Options. Values must be 8 or less, else the game uses 4, 6, 4, 0 (0x08001E98). Byte 1 goes to the sound object (+0x5C4), byte 2 to 0x08020AC8. Exact meaning of each byte: LIKELY text speed, sound volume, music volume, unused |
| 0x004 | 4 | `adler32(options) + 0x12345678` |
| 0x008 | 8 | Never written by the game |
| 0x010 | 0x168 | Slot 1 |
| 0x178 | 0x168 | Slot 2 |
| 0x2E0 | 0x168 | Slot 3 |
| 0x448 | to 0x2000 | Never written by the game |

## 3. Slot layout (RAM struct at 0x03000E90)

| Offset | Size | Field | Evidence | Label |
|---|---|---|---|---|
| +0x00 | u8 | Party leader index (0 Gohan ... 5 Hercule). Default 3 (Trunks, the intro) | 0x08003C2E; capture 01 = 0 (Gohan), capture 02 = 1 (Piccolo on screen) | CONFIRMED |
| +0x01 | u8 | Bit 0: slot in use (0x0800405E, tested at 0x080019FE). Bit 1: set by script op 86 (0x080040AA), set in normal play. Bit 2: set by the debug teleport only | captures 01, 02 | CONFIRMED (bit 0), LIKELY (bits 1, 2) |
| +0x02 | u8 | Map zone | 0x0800403A | CONFIRMED |
| +0x03 | u8 | Map area | 0x08004040 | CONFIRMED |
| +0x04 | u8 | Map variation (1-based) | 0x08004046, used at 0x0800187C | CONFIRMED |
| +0x05 | 3 | Not written, 0 | | LIKELY padding |
| +0x08 | u32 | Default 0, 0 in all captures. Use not found | 0x08003C2A | open |
| +0x0C | 6 x 28 | Character records, see below | default table ROM 0x1D9548 | CONFIRMED |
| +0xB4 | 50 | Story flags 0-399. Flag n = bit n&7 of byte 0xB4 + n/8. Script ops 19/20 (test), 27 (set), 28 (clear) | 0x08003E42, 0x08003E5E, 0x08003E74 | CONFIRMED |
| +0xE7 | 38 | Map visited bits 0-296, index from table 0x086F6D8C (zone, area, bit) | 0x080040EE; capture 01 bit 35 = map 2,22; capture 02 bit 294 = map 14,1 | CONFIRMED |
| +0x11A | 16 | Scouter database bits 0-127, table 0x086F8E40 (name, text, sprite set) | op 141 0x0800B00C, list 0x08019236 | CONFIRMED |
| +0x12B | 50 | Item counts, item n at +0x12B + n, table 0x086ADE24 (56 bytes, +4 name id, +6 text id, +3 max) | op 21 0x080095E4, give 0x0800F3F0, use 0x080046B0 | CONFIRMED |
| +0x15D | 3 | Not used | | LIKELY padding |
| +0x160 | s16, s16 | Player x, y in map pixels | written 0x08004050 from player +0x158/+0x15C >> 8 (0x0800791A), read by `ldsh` at 0x0800C58A | CONFIRMED |
| +0x164 | u32 | Adler-32 of +0x000..+0x163 (EEPROM copy only) | 0x08003FCE | CONFIRMED |

Character order (CONFIRMED by name strings at ROM 0xE2E15 and by sprite sets): 0 Gohan, 1 Piccolo, 2 Vegeta, 3 Trunks, 4 Goku, 5 Hercule. Gohan's default appearance points to set 57, the frame captured in capture 01. Piccolo's points to set 103, the probe in capture 02.

### Character record (28 bytes)

| Offset | Size | Field | Label |
|---|---|---|---|
| +0x00 | u16 | Current HP | CONFIRMED (0x08003D18) |
| +0x02 | u16 | Max HP | CONFIRMED (0x08003D16) |
| +0x04 | u16 | Current EP | CONFIRMED (0x08003D2A) |
| +0x06 | u16 | Max EP | CONFIRMED (0x08003D28) |
| +0x08 | u8 | Appearance entry, index into ROM 0x1D967C (22 entries of 20 bytes, +1 = sprite set id, +0 bit 0 = transformed form, +4 = form to transform into, +5 = base form) | CONFIRMED (0x080042BC, 0x08003ED4); meaning of +4 LIKELY |
| +0x09 | u8 | Selected attack slot 0-3 (cycled by 0x08004284) | CONFIRMED |
| +0x0A | u16 | STR, 8.8 fixed point, cap 0x6400 (100) | CONFIRMED (0x08003C6E) |
| +0x0C | u16 | POW, 8.8 | CONFIRMED |
| +0x0E | u16 | END, 8.8 | CONFIRMED |
| +0x10 | u32 | EXP | CONFIRMED (0x08004214) |
| +0x14 | u32 | Bit 0: in party (0x08003E00). Bit 1: counted at 0x08003E1E. Bit 2: special melee attack (0x080085D4). Bits 3-6: attack slots 0-3 (0x08004284). Default 0x40 | bits 0, 3-6 CONFIRMED; bits 1, 2 LIKELY |
| +0x18 | 4 | Per-character constant, never changed by level-up or debug | open |

### Level and stat rules (CONFIRMED)

- Level is not stored. Level = 1 + the highest i with `EXP >= table[i]`, table at ROM 0x1D9834, 50 entries, cap level 50 (0x08004214).
- **Level 40 needs EXP 2,727,775** (table[39]). Level 41 needs 3,335,510.
- Level-up routine 0x08003CA0 `(struct, char, old_level, new_level)`:
  - STR, POW, END: one draw for the whole gain: `stat += rand((max - min + 1) * L) + min * L`, L = levels gained, cap 100. Min and max per level (1/256 units) are at ROM 0x1D95F0. Gohan: STR 318-518, POW 302-502, END 256-456.
  - HP: for each level, `HP += HP * (0xE14 + rand(0x51F)) >> 16`, that is +5.5 % to +7.5 %.
  - EP: for each level, `EP += 2 + rand(3)`.
  - rand is the generator at 0x080213FC (state at 0x03003890).
- The stats are random, so no single "level 40 value" exists. The test save uses the records that the game's own routine produced (next section).

## 4. Debug menu and the level 40 records

- Routine 0x08005C0A resets the struct, sets record +0x14 bits 0-5 (Hercule only 0-1), calls 0x08003CA0 from the current level to **40** (`mov r3,#0x28` at 0x08005C92), sets EXP with 0x08004276, sets Gohan to appearance set 53 and Trunks to set 128 (0x080042BC), sets leader 1 and +1 bit 2, then teleports to the chosen zone and area. CONFIRMED (code).
- Capture 02 (the cheat `0202b32d:02` is in its extdata, map 14,1 = Cell Games Arena) matches every one of these effects: EXP 0x0029_9F5F on all six, +0x14 = 0x7F and Hercule 0x43, leader 1, +1 = 0x06. CONFIRMED that capture 02 holds output of 0x08005C0A. That it is the "Map test" item of the debug menu: LIKELY. The link from 0x0202B32D to this routine was not traced.
- All 18 stats in capture 02 are inside the min-max range of the rule above (checked by `log2_save.py info`). Max HP and max EP of all six are inside their ranges too. The tool compounds HP from the default base (85, 95, 105, 110, 100, 50) per level with truncation. Example: Gohan HP 906 in range 619-1314, EP 134 in range 98-176.

## 5. Story progress

There is no single progress variable. The story is the flag bitset at +0xB4.

- Quest table at ROM 0x6D68DC: 43 entries of 16 bytes, `{u32 category, done script, active script, text}`. The Journal loop at 0x08004A86-0x08004AE4 runs the done script first (true: Finished list), then the active script (true: active list under the category name from 0x081D9C80). CONFIRMED. Correction (2026-10-18): the first version of this doc put the base at 0x6D68E0, which read each category from the next entry. Done and active scripts were right. The main chain ends with:

| Quest | Active when | Done when |
|---|---|---|
| Collect the seven Dragon Balls | flag 158 | flags 162, 163, 164, 185, 186, 187, 188 |
| Return the Dragon Balls to Dende on the Lookout | the 7 Dragon Ball flags | flag 191 |
| Enter the Cell Games | flag 191 | flag 193 |
| Talk to Dende on the Lookout | flag 195 | never (the game ends) |

- **Flags 191-195 (CONFIRMED sites, meanings LIKELY from the dialog).** Story order is 191, 193, 192, 194, 195, not numeric order.

| Flag | Only SET site | Meaning |
|---|---|---|
| 191 | 0x083DD32B, record 0x083DD2F0 after "DENDE: You've found all the Dragon Balls!" | Dragon Balls returned to Dende. The same record runs ext 76 on items 29-35 (Dragon Balls 1-7). The player stays on the Lookout: no map load |
| 193 | 0x083E8D92, after "#Let's do this!" | Cell Games entered (quest "Enter the Cell Games" done) |
| 192 | 0x083E93E0, after "Okay. I'll do it." and "Wonderful. Let's get started!"; ext 70 (0) at 0x083E93A8 | Gohan agrees to fight Cell and becomes the player |
| 194 | 0x083E9BBB, in the fight scenes near "Does anyone else want to be a martyr?" | A Cell Games fight step, before the Rage scene (ext 73 (0, 58) at 0x083EA369) |
| 195 | 0x083EC6A2 | Cell beaten |

  Search shape: `flagscan2.py` (literal pushes, op 0, 1 and 29, before ext 27). A SETFLAG with a computed number would not appear.
- **Ext 76 lowers an item count by 1. CONFIRMED.** Handler 0x080096CA: `ldrb [struct+0x12B+n]`, `add #0xFF`, `strb`. Ext 77 (n, k) subtracts k (0x080096E8). The earlier note "ext 76 = count +1" is wrong. So the flag 191 record removes Dragon Balls 29-35.
- **Party ops. CONFIRMED (handlers):** ext 79 (n) sets record +0x14 bit 0 (in party, 0x0800A9B6), ext 91 (n) clears it (0x0800A9DA), ext 80 / 81 set / clear bit 1 (0x0800AA10, 0x0800AA34), ext 82 sets bit 5 (0x0800AA58). Ext 29 / 30 are message 4 broadcasts (0x08009740, 0x0800975E), not party ops.
- **Party at Cell's defeat. CONFIRMED (script).** Record 0x083EC678 (seq 50) loads Capsule Corp, broadcasts ext 29 (5), sets flag 195, then tests the four Hercule trophies 302, 303, 305, 306. All four: seq 51 at 0x083EC6C6 runs ext 79 (5), ext 98 (5, 40) and ext 80 (5), so Hercule joins at level 40. Else the scene skips to seq 53. Seq 54 (0x083EC726) runs ext 91 (4): Goku leaves the party. Four more Hercule join sites (0x083C9C8F, 0x083D2C67, 0x083D6733, 0x083E271D) each test flag 195 and the trophies first. So before flag 195, Hercule is never in the party.
- **Party at flag 191 (LIKELY: story order taken from the flag number next to each party op).** Last party op before 191: flag 158 site 0x083DBC38, ext 79 (4), ext 80 (4), ext 80 (0), ext 82 (4), with ext 98 (4, 35) at 0x083DBC4C. Result: Gohan, Piccolo, Vegeta, Trunks and Goku have bits 0 and 1 set; Hercule has the default record (ROM 0x1D9548 + 5 * 28, +0x14 = 0x40).
- **Outfits at flag 191 (LIKELY: ordered by flags).** Every ext 73 call with a literal (character, set): flag 129 Trunks 128 and Gohan 53 (0x083DF2BB), flag 149 Trunks 129 and Vegeta 138 (0x083DE6B9), flag 151 Trunks 132 and Vegeta 137 (0x083E7789), flag 154 Gohan 56 (chamber exit, 0x083DB62B), then Rage 58 and post-Cell 56 inside the Cell Games. So at flag 191: Gohan set 56, Vegeta set 137, Trunks set 132, the same as after Cell.
- **Slot 3 flag set (LIKELY):** the post-Cell set minus 192-195. Each has one SET site, inside a Cell Games scene (table above). The Cell Games scenes (0x083E8000-0x083ED000) and the arena maps (0x08408B00-0x08409368) hold no other SET or CLR site. Result: 151 flags, the post-Cell list with 185-191 in place of 185-195.

- **Flag 195 = Cell is beaten. CONFIRMED.** Script at 0x083EC67B, right after "PICCOLO: He did it! Cell's energy completely vanished!": `push 6,3,1,376,408 ; call ext_35` (load map zone 6, area 3, variation 1 at x 376, y 408: Capsule Corporation), `push 5 ; call ext_29` (Hercule joins), `push 195 ; call SETFLAG`, then the trophy check and "Hercule is now an available character! / Journal Updated!".
- **A playable state after Cell exists. CONFIRMED.** The game drops the player at Capsule Corporation with the quest "Talk to Dende on the Lookout". Flag 196 is set at the Lookout farewell (0x083DCEF7, "TIEN: Well it's about time I get going ... Goodbye Gohan!"), before the ending. So the latest playable point is: flag 195 set, flag 196 clear.
- Script VM used for this: interpreter 0x080092E4, 30 base ops at 0x083B5C00, 145 ext ops at 0x083B5D28. Scratch disassembler: `scripts\one-time\2026-10-18-save-slots\sdis.py`.

**Flag set used in the test save (LIKELY):** every flag 0-195 that has a script SETFLAG site which decodes as a clean script, minus the flags that a later script clears again. Those are scene or puzzle flags: 10, 21, 24, 25, 27, 71, 72, 101-107, 114-116, 133, 147, 159-161, 165-170, 172-175, 177-180, 182-184. Flags 32 and 135 have no SET site. Result, 155 flags: 0-9, 11-20, 22-23, 26, 28-31, 33-70, 73-100, 108-113, 117-132, 134, 136-146, 148-158, 162-164, 171, 176, 181, 185-195.

- Side content stays at default (clear): flags 196-306, which hold side quests (205-221), stat capsules (255-271), Missing Nameks (288-298) and the Hercule trophies (302-306).
- This is a superset of one real playthrough: optional story branches (for example 58, 59, 60) are all set. A real save may differ in flags that a single run never sets.
- **No one-shot map conditions.** Map object conditions go through evaluator 0x08003F06 (0 = always, high half 1 = flag, 2 = not flag, 3 = test and clear, else a script). Callers: 0x0800C332, 0x0800C376, 0x0800C486, 0x0800C4B2, 0x0800C526, 0x0800C6EC. A scan of all 1984 conditions in the map lists (+0x10 pairs, +0x14 at record +4, +0x18 and +0x1C at record +0) found no mode 3. CONFIRMED (`scripts\one-time\2026-10-18-save-slots\conds.txt`). So no map object consumes a flag on load, and the flag set needs no extra clears.
- **Journal check.** The quest table conditions were evaluated against the test flag set plus items 45 and 22. Every main and story quest shows Finished, except "Talk to Dende on the Lookout", which stays active as intended. Side quests 39, 40 and 42 show Outstanding, which a real run at this point can also show. CONFIRMED by evaluation of the ROM scripts, not checked in game.
- **Journal check, before the Cell Games.** `log2_save.py journal` runs the same scripts (ops push, flag, notflag, counter, and, or, compare, jz, jmp, end; anything else raises). On slot 3 of the new save, "Enter the Cell Games" is the only active main quest, "Return the Dragon Balls" is Finished and "Talk to Dende" is hidden. Ext 21 (counter) also adds a count of on-map pickups, which a save file cannot show; the tool counts held items only.

## 6. Position and save points

- Save points are trigger rectangles made by object factory 0x08010AC7 (vtable 0x08023BCC). Its activate method 0x080109EC offers Save / Switch Characters (menu 0x080112C0, strings 19 and 22) and calls the save routine. It is the only caller of 0x08004030. CONFIRMED.
- The factory pointer appears in 30 map object lists (map entry +0x10). Relevant ones (map table ROM 0x409368, 56-byte entries, 327 maps):

| Map entry | Zone, area | Name | Variations | Save rectangle (x1,y1)-(x2,y2) |
|---|---|---|---|---|
| 145 | 6, 1 | Capsule Corporation | 1 | (408,568)-(457,617) |
| 156 | 6, 12 | Capsule Corporation | 1 | (240,248)-(289,297) |
| 25 | 2, 29 | East District 439 | 1 | (224,240)-(273,289) |
| 47 | 2, 51 | East District 439 | 1 | (176,96)-(225,137) |
| 7 | 2, 1 | East District 439 (name script) | 2 (variation 2 when flag 68) | (520,248)-(569,297) |

- All 30 save point entries use condition 0 (always), so no story flag hides them. CONFIRMED (`conds.txt`).
- The saved x,y is the player position when Save is chosen, so it lies inside the rectangle. The test save uses the bottom middle of the rectangle. LIKELY: a solid sprite in the middle of the rectangle would block the centre, and the bottom edge avoids that. Not checked against the collision map.
- The map variation is stored, not recomputed on load. All three chosen maps have one variation, so +4 = 1. CONFIRMED.

**Region items, exits and arrivals (2026-10-18).** Scratch tools: `scripts\one-time\2026-10-18-save-slots\regions.py`, `exits.py`, `scene.py`.

- Map region items (`{cond, item}` at entry +0x10) and layout regions (layout +0x40 count, +0x44 list of item pointers, layout = entry +0x2C [variation - 1], read at 0x08006264) share one item shape: `{factory, trigger type, s16 rect x0 y0 x1 y1, data}`. CONFIRMED (0x0800C2F8, 0x0800BF42).
- Factories: 0x0800C233 and 0x0800D9C3 are warps, data `{u8 direction, zone, area, variation, s16 x, s16 y}` (variation 0 in many warps, LIKELY "use the variation script"); 0x0800C2C3 runs the script at data +0; 0x0800D7E1 runs a scene table at data +0; 0x08010AC7 is a save point; 0x0801A6B3 is a world-map place label (data +0 = text id). CONFIRMED (bytes), LIKELY (names of the last two).
- Trigger type 0x0800D839 fires on a new A press inside the rectangle: it reads `[0x083ED2A4]` = input 0x0300229C, +0x14 bit 0. Type 0x0800D87F (and +8, +0x10, +0x18) also needs the facing direction byte at player +0x10 to equal its parameter (0x0800D844). CONFIRMED. So a spawn inside an exit or save rectangle does not fire it.
- **World map exits.** A scan of all map region lists and layout regions finds 17 items whose script or scene loads map 6,99: 15 script regions (factory 0x0800C2C3) and the 2 East District scene regions (table 0x083B8EEC, below). All 17 use trigger type 0x0800D839 (A press). 16 play music 43 first; map 5,1 (item 0x083F9690) does not. Shape: region items only. Story scenes that load the world map from an NPC talk or a cutscene (for example flag 29 at 0x083B9045, after Cell at 0x083EC729) are not counted. World map (map 6,99, entry 176) landing places are a script region (`push zone,area,var,x,y ; ext 38`) and one or more label regions with the same rectangle. Their conditions can differ: the Lookout script region needs flag 127, its two labels need 127 and not 158, and 158.

| Place | Exit region (A press) | World map landing script | Needs |
|---|---|---|---|
| Master Roshi's Island, map 11,1 | item 0x08405F34, rect (393,121)-(440,176), always; script 0x08405F20 `00 2b 02 31 1d 05 0c 81 46 02 b1 10 a0 70 02 26 11` = music 43, world map at (3144,2104) | 0x083FBC84 `1d 05 16 02 02 86 40 82 40 02 26 11` = map 11,1,1 at (416,160) | flag 68 for the landing |
| Dende's Lookout, map 9,1 | item 0x08403FA4, rect (745,793)-(792,848), always; world map at (896,1480) | 0x083FBBFC `1d 05 12 02 02 8c 00 8d 00 02 26 11` = map 9,1,1 at (768,832) | flag 127 for the landing |
| Cell Games Arena, map 14,1 | rect (241,265)-(288,320), always; world map at (1832,1088) | region 25 script = map 14,1,1 at (264,304) | flag 191 for the landing |

- Map 11,1 is the island itself (name script 0x08405C82: "Master Roshi's Island" while flag 196 is clear). Areas 2-3 are "Master Roshi's Home" (door warp at 11,1 rect (672,360)-(681,385)), and areas 4-6 have no world-map exit. Save point 11,1 rect (544,136)-(593,185), always. CONFIRMED.
- **Cell Games start gate. CONFIRMED (script), LIKELY (mechanism).** Map 14,1 has the scene "Only Goku is allowed to pass through this barrier." (cond 0x08408DB0: leader not 4 and flag 195 clear). The barrier object (swap list item 0x08408DFC) runs its break script (sound 47, ext 71 on rect (248,56)-(280,88)) only when cond 0x08408DD4 holds: leader 4 and `level(4) > 39` (ext 22 = 0x08004214, 1-based level from EXP). The warp north (14,1 to 14,2) is behind it. Map 14,2 then starts the scene "GOKU: I'll fight Cell first." So Goku must lead at level 40 or more.
- **East District 439: why the old slot 2 could not leave. CONFIRMED (map data), LIKELY (that the barrier blocks the walk).** Map 2,29 lies in the cluster 2,26-2,52, which has no world-map exit. The only link out is the warp 2,26 rect (384,320)-(465,337) to map 2,7 at (112,52). That point is inside the barrier scene at 0x083EE640, rect (89,49)-(136,72): "Only Vegeta is allowed to pass through this barrier.", cond leader not 2 and flag 274 clear. Flag 274 is set only at 0x083EE682, by the break script (sound 47, ext 71 and ext 117 on rect (104,24)-(136,56)) of a swap item whose cond is leader 2 and Vegeta level 30 or more (0x083EE688). The test save had Gohan leading and flag 274 clear. Fix in the old save: Switch Characters to Vegeta at the 2,29 save point.
- **Anti-piracy point. CONFIRMED (script).** The only East District world-map exits are scene table 0x083B8EEC, used by map 2,5 (rect (105,121)-(160,176), always) and map 2,6 (rect (249,201)-(296,256), flag 27 clear). Record 0x083B8E84: music 43, ext 129 (push the SRAM probe byte 0x03001FC0, 0x0800AFC2); zero loads the world map at (2944,1912); non-zero waits, shows "This game will not run on the hardware found." (0x083B8EAE) and runs ext 97. So it fires only when SRAM at 0x0E000000 is writable. The old slot 2 never reached it. Search shapes: region scripts of all 327 maps, and a byte scan for ext 129 followed by a test; an NPC talk scene that calls ext 129 would not appear in the first.

## 7. The test save

### 7a. Second test save: post-Cell and before the Cell Games (2026-10-18)

File: `test-data\saves\log2_lv40_cellgames.sav`, 8192 bytes, SHA-1 `c755acf074bc3eefb14023935142bbbc10ad26b1`, built by `py -3 -I scripts\permanent\rom\log2_save.py build "data\roms\...(USA).sav" test-data\saves\log2_lv40_cellgames.sav` (the default set, `cellgames`). Base, options and untouched bytes as below.

| Slot | Story | Location | Zone, area, var | x, y | Leader | Position source | Label |
|---|---|---|---|---|---|---|---|
| 1 | After Cell | Capsule Corporation save point | 6, 1, 1 | 432, 591 | Gohan | The slot I loaded (`log2_lv40_postcell.sav`, byte for byte) | LIKELY |
| 2 | After Cell | Master Roshi's Island | 11, 1, 1 | 416, 160 | Gohan | World map landing script 0x083FBC84 | CONFIRMED |
| 3 | Before the Cell Games (flag 191) | Dende's Lookout | 9, 1, 1 | 768, 832 | Goku | World map landing script 0x083FBBFC | CONFIRMED |

- Slots 1 and 2: the post-Cell content of section 7, unchanged (Hercule 0x43, Goku in the party). Only the place differs. Both spawn points sit inside an A-press exit rectangle (section 6), so they do not fire on load.
- Slot 3 differs from post-Cell in: flags 192-195 clear (151 flags, section 5); Hercule = ROM default record, +0x14 = 0x40 (not in party, level 1); leader 4 (Goku), because the Cell Games barrier needs Goku leading at level 40 (section 6). Outfits: Gohan set 56, Vegeta 137, Trunks 132 (section 5). Items: Dragon Radar and Scouter, no Dragon Balls.
- The Dende scene does not load a map, so the game leaves the player on the Lookout at flag 191. The Lookout arrival point is the game's own placement on that map. LIKELY that it is walkable from there; the Lookout save point rect (736,600)-(793,649) is the fallback.
- `build --set postcell` still writes the first test save byte for byte (SHA-1 `3ecf1e40...`, test `test_postcell_set_is_byte_for_byte_the_first_build`). Note: `test-data\saves\log2_lv40_postcell.sav` on disk is SHA-1 `1973041f...`: its slot 1 sits at (432,591), not (432,613). That edit is not recorded. I loaded that file (as `log2_poc_r12.sav`).
- `write` now refuses to overwrite an existing file.

### 7b. First test save

File: `test-data\saves\log2_lv40_postcell.sav`, 8192 bytes, built by `py -3 -I scripts\permanent\rom\log2_save.py build "data\roms\...(USA).sav" test-data\saves\log2_lv40_postcell.sav --set postcell`. Bytes 0x008-0x00F and 0x448-0x1FFF are copied unchanged from my save. Options block: the game defaults 4, 6, 4, 0 with a valid check.

| Slot | Location | Zone, area, var | x, y | Position label |
|---|---|---|---|---|
| 1 | Capsule Corporation save point | 6, 1, 1 | 432, 613 | LIKELY |
| 2 | East District 439 save point | 2, 29, 1 | 248, 285 | LIKELY |
| 3 | Capsule Corporation, where the game itself puts you after Cell | 6, 3, 1 | 376, 408 | CONFIRMED (script 0x083EC687) |

Same content in all three slots:

| Field | Value | Label |
|---|---|---|
| Leader | 0 (Gohan) | LIKELY (Gohan leads in the post-Cell scenes) |
| Header +1 | 0x03 (in use, bit 1 as in normal play), +8 = 0 | CONFIRMED for bit 0, rest as capture 01 |
| Characters | Capture 02 records (game level-up to 40, EXP 2,727,775), current HP and EP full | CONFIRMED source |
| Record +0x14 | 0x7F for Gohan to Goku, 0x43 for Hercule (all six in the party, all attacks) | CONFIRMED as the debug routine's values |
| Appearance | Gohan set 56 (0x083EBFF8, after Cell), Vegeta set 137 and Trunks set 132 (0x083E7784), others default (Piccolo 103, Goku 60, Hercule 72) | LIKELY (last ext_73 call in ROM order) |
| Story flags | 155 flags listed in section 5 | LIKELY |
| Visited maps | all 297 bits set | LIKELY cosmetic: the only readers found are minimap scripts (ROM 0x086E0000-0x086FFFFF) |
| Scouter database | all clear | default |
| Items | Dragon Radar (item 45) = 1, Scouter (item 22) = 1, rest 0 | LIKELY: the story gives item 45 at 0x083CF62B and item 22 at 0x083CF4A3 and 0x083D0C4B, and quests 34 and 36 count as done only while they are held |

Level 40 values per character (from capture 02):

| Character | HP | EP | STR | POW | END |
|---|---|---|---|---|---|
| Gohan | 906 | 134 | 70.56 | 58.28 | 71.39 |
| Piccolo | 1052 | 138 | 64.61 | 56.24 | 64.19 |
| Vegeta | 1143 | 138 | 71.04 | 63.60 | 60.67 |
| Trunks | 1181 | 135 | 53.03 | 39.95 | 40.62 |
| Goku | 1026 | 139 | 47.33 | 50.07 | 65.99 |
| Hercule | 470 | 141 | 36.59 | 16.03 | 30.67 |

The status screen shows the integer part.

Verification done: the tool re-parses the file, every slot's stored checksum equals both its own Adler-32 and `zlib.adler32`, max HP, max EP and all stats are in range, and my .sav SHA-1 is unchanged (78ec1584...).

## 8. Open questions and the save that settles them

> [!WARNING]
> Disable the mGBA cheat file entry `0202b32d:02` before you load the test save. mGBA applies it every frame, and it may drive the debug routine that resets the struct and levels the party.
>
> Do not load an mGBA save state on top of the test save. The game reads slots from the RAM shadow at 0x0203E000, and a state restores that RAM with the old blank slots. LIKELY: it was not traced whether the load menu reads the EEPROM again. Cold boot instead.

**Install steps for me (the task may not write under `data\`):**

1. Back up `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).sav`.
2. Copy `test-data\saves\log2_lv40_postcell.sav` over it. Keep the exact base name of the ROM.
3. Disable the cheat entry `0202b32d:02` in the `.cheats` file.
4. Cold boot: load the ROM again, or reset it, with the new .sav in place. Do not load a state.
5. Choose Continue and pick slot 1, 2 or 3.

1. **One in-game save.** I cold boots with the cheat off, makes one Save at any save point to slot 1, then gives the .sav and an mGBA state taken right after. That pair confirms the byte-reversed blocks, both checksums, the +2..+4 and +0x160 fields, and the options bytes, all at once.
2. **Save point position.** If Gohan appears stuck in slot 1 or 2, use slot 3, or move the position with `log2_save.py set <in> <out> 1 pos=432,625`. That point is 8 pixels below the save rectangle on purpose: it is clear of the trigger and of any sprite on it, and Gohan can walk up into the rectangle. LIKELY, not checked against the collision map.
3. **Goku after Cell.** Answered 2026-10-18 (section 5): ext 91 (4) at 0x083EC735 takes Goku out of the party after Cell, and Hercule joins only with all four trophies. The post-Cell slots keep all six in the party as I asked, so they do not match the story there.
4. **Unknown fields:** +0x08 (u32), record +0x18 (4 bytes), header +1 bits 1 and 2, record +0x14 bits 1 and 2, the exact option byte meanings.
5. **Transformations.** The appearance entry +4 names the transformed form. Whether a story flag also gates Super Saiyan was not traced.
6. **What happens after flag 196.** The ending runs after the Lookout farewell. Whether the game saves after the credits was not traced.

## Files

| File | Purpose |
|---|---|
| `scripts\permanent\rom\log2_save.py` | info / journal / build / set for .sav files |
| `scripts\permanent\tests\test_save.py` | Tests for both build sets and the journal evaluator |
| `test-data\saves\log2_lv40_postcell.sav` | Test save, 3 slots, post-Cell |
| `test-data\saves\log2_lv40_cellgames.sav` | Test save, 3 slots, slot 3 before the Cell Games |
| `scripts\one-time\2026-10-18-save-slots\regions.py`, `exits.py`, `scene.py` | Region item dump, per-zone warps and exit scripts, cutscene record dump |
| `scripts\one-time\2026-10-18-save-slots\thumb.py` | Small Thumb disassembler used for this work |
| `scripts\one-time\2026-10-18-save-slots\sdis.py` | Script VM disassembler |
| `scripts\one-time\2026-10-18-save-slots\flagscan2.py`, `flags2.txt`, `clr_sites.txt` | Flag SET and CLR site scan and its check |
| `scripts\one-time\2026-10-18-save-slots\conds.py`, `conds.txt` | Map object condition scan (1984 conditions, no mode 3) |
| `scripts\one-time\2026-10-18-save-slots\maps.py`, `maps.txt` | Map table dump with names and variation scripts |
| `scripts\one-time\2026-10-18-save-slots\struct_sites.py`, `ops.txt`, `baseops.txt` | Code sites and VM op listings |
| `scripts\one-time\2026-10-16-first-probes\captures\03-ss3\` | Capture of state 3 (debug menu screen) |
