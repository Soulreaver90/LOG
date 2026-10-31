# LoG II forms, transform input and HUD (USA, ALFE)

Date: 2026-10-16. ROM SHA-1 `18e0715dec419f3501c301511530d2edcd590f8b`. Addresses are GBA addresses. "rom:0x..." is a file offset (address minus 0x08000000).

Labels: **CONFIRMED** = proved here with quoted bytes or disassembly. **LIKELY** = strong evidence, not proved. **SPECULATIVE** = a guess.

I verify each CONFIRMED line before Task 6 starts (plan Task 4 Step 5).

## Result in one paragraph

Forms are data-driven, so the BLOCKED case does not apply. Each appearance entry (rom:0x1D967C, 20 bytes) has at +0x10 a pointer to a form object. The form object is one word: a pointer to a 4-method vtable (apply stats, per-frame tick, enter, leave). Super Saiyan adds +10 to STR, POW and END and drains 1 EP every 20 frames. Rage sets all three to a flat 100, drains nothing and regenerates HP. The Z button is the B button with the transform ability selected (L cycles abilities). The ability table at rom:0x1D9900 holds absolute pointers to each ability's icon, test and action, so Task 6 can hook it without a BL. The HUD "Z" is the transform ability's raw 32x16 8bpp icon. Recommended Task 6 shape: a relocated appearance table with a new entry 22 (Super Saiyan 2), entry 5 +4 set to 22, a new form object in ROM, a gate on the ability 12 action pointer (flag 195), and a 10-byte in-place HUD hook for the "Z2" icon.

---

## 1. Form table (a)

The form behavior lives in the form object at appearance +0x10. The player object keeps the current one at +0x180.

### Form objects and their methods (CONFIRMED)

Each IWRAM form object holds one word, its vtable (capture 02, IWRAM 0x030021E0-0x030021F0: `08024004 08024e4c 0802526c 08024c58 08024abc`). Vtable words are offsets from the vtable base (target = base + word).

| Object | Vtable | Entries | +0 apply | +4 tick | +8 enter | +0xC leave |
|---|---|---|---|---|---|---|
| 0x030021E0 base | 0x08024004 | all untransformed | 0x08016FD8 | 0x08017028 | 0x0802609C (`bx lr`) | 0x080263B8 (`bx lr`) |
| 0x030021E4 Rage | 0x08024E4C | 4 | 0x080170D8 | 0x0801710E | 0x08017158 (sound) | 0x08017174 (sound stop) |
| 0x030021E8 Super Vegeta / Super Trunks | 0x0802526C | 10 (set 139), 14 (set 130) | 0x0801718C | 0x080171E4 | 0x0801727C | 0x08017298 |
| 0x030021EC Super Saiyan | 0x08024C58 | 5, 11, 16, 17, 20 | 0x080172B0 | 0x08017306 | 0x08017376 | 0x08017392 |
| 0x030021F0 Super Namek | 0x08024ABC | 7 (set 104) | 0x080173AA | 0x08017400 | 0x0802609C | 0x080263B8 |

- Vtable +0x10 and +0x14 are not called by any site found (shapes in section 8). The +0x14 target 0x08026390 is a literal pool word (`24 50 02 08`), not code. CONFIRMED (no caller), so only 4 methods are live.
- **Apply** writes u8 effective stats to player +0x160 (STR), +0x161 (POW), +0x162 (END), 0x80 to +0x163 and +0x164, two floats through 0x080265C4 to +0x188 and +0x18C (stored as value x 256), and 0 to the drain accumulator +0x184.
- **Tick** runs every frame from the player update 0x08008766: `0800876a add r0,#0xff ; add r0,#0x81 ; ldr r0,[r0] ; ldr r1,[r0] ; ldr r2,[r1,#0x4]` then `bl 0x8021d2c`.
- Apply is called by 0x080086A2: `080086c0 ldr r0,[r0,#0x10] ; ... str r0,[r2,r1]` (player +0x180 = form object), then vtable +0.

### Per form values (CONFIRMED unless marked)

| Form | STR / POW / END on player +0x160..+0x162 | +0x188 / +0x18C (L: walk / run speed) | Tick effect | Proof |
|---|---|---|---|---|
| Base | record >> 8 (no bonus) | 1.25 / 2.5 (`0x3FA00000`, `0x40200000`) | Every 0x6E-per-frame accumulator overflow (596 frames): leader EP += maxEP x 0x7AE >> 16 (3 %); every other character HP and EP += max x 0xCCD >> 16 (5 %). Also struct +0x08 -= 1 per frame (cooldown) | `08017034 sub r2,#0x1 ; str r2,[r0,#0x8]`, `08017040 add r0,#0x6e`, `0801705c ldr r3,=0x7ae`, `08017090 ldr r3,=0xccd` |
| Super Saiyan | record >> 8 **+10** each | 1.75 / 3.0 | Accumulator += 0xCCD per frame. On each overflow (every 20 frames): EP -= 1, floor 0. If EP is 0 and HP is not 0: message 0x24 (revert). Skipped while the player is already in state 0x24 | `080172ce add r2,#0xa`, `080172d6 add r2,#0xa`, `080172de add r1,#0xa`; `08017324 ldr r1,=0xccd`; `0801734e sub r2,#0x1`; `08017366 mov r1,#0x24` |
| Rage | flat **100 / 100 / 100** (record ignored) | 2.0 / 3.25 | Accumulator += 0xCCD; on overflow leader HP += maxHP x 0x290 >> 16 (1 %). **No EP code** | `080170e2 mov r1,#0x64 ; strb r1,[r0,#0x0] ; strb r1,[r0,#0x1] ; strb r1,[r0,#0x2]`; `08017134 mov r3,#0x29 ; lsl r3,r3,#4` |
| Super Vegeta / Super Trunks | +15 / +10 / +15 | 0.75 / 1.75 (slower than base) | Same as Super Saiyan with 0x667: 1 EP per 40 frames | `080171aa add r2,#0xf`, `080171b2 add r2,#0xa`, `080171ba add r1,#0xf`; `08017202 ldr r1,=0x667` |
| Super Namek | +6 / +6 / +6 | not read | not read | `080173c8 add r2,#0x6` (x3) |

- The status screen value 100 to 110 (mine) matches +10. The record stats (8.8, cap 100) never change in a form. The bonus exists only on the player object, so 100 + 20 = 120 fits the u8.
- Drain rate in seconds at 60 fps: Super Saiyan 3 EP/s. Twice that (Task 6 Super Saiyan 2) is accumulator 0x199A: 6 EP/s.

### Appearance fields used by forms (CONFIRMED)

| Field | Meaning | Readers |
|---|---|---|
| +0 bit 0 | Transformed. Ability shows "revert", drain forms leave at 0 EP | 0x080134C0, 0x080134F2, 0x0801353C, 0x08008370, 0x08003ED4 |
| +0 bit 1 | Ability locked (Rage: entry 4 +0 = 3) | 0x08013502 (`lsl r2,r0,#30 ; lsr r2,r2,#31 ; beq ; mov r0,#0x0`) |
| +4 | Transform target | **only** 0x08014D8C (`ldrb r0,[r5,#0x4]`) |
| +5 | Revert target | 0x08014D90, 0x08003EF8, 0x0800838A |
| +0x10 | Form object | 0x080018A8, 0x08008374, 0x0800872E, 0x080086C0, 0x080089D8, 0x08008A00, 0x0800A6A8, 0x0800A926, 0x0800A98A, 0x08014D7A |

- Gohan entry 5 (Super Saiyan) bytes at rom:0x1D96E0: `01 3b 3e 0d 04 02 06 00 14 00 00 00 00 01 00 00 ec 21 00 03`. Entry 4 (Rage) at rom:0x1D96CC: `03 3a 3d 0c 02 02 06 00 14 00 00 00 00 01 00 00 e4 21 00 03`.

## 2. Transform input (b)

The "Z button" is B, pressed while the transform ability is the selected one. CONFIRMED.

1. **Keys.** 0x0801EEFC reads KEYINPUT: `0801eefe ldr r1,=0x04000120 ; ldrh r4,[r0,#0x12] ; ldrh r1,[r1,#0x10] ; ... mvn r1,r1`, then `+0x14 = new & changed` (pressed this frame), `+0x16` released, `+0x12` held. Its callers pass r0 = `[0x087FBDAC+8]` and `[0x087FD0F8+8]`, both 0x0300229C. Capture 02 holds `+0x12 = 0xFC00` (no key down).
2. **Use ability on B.** Four player state updates (0x0800800E, 0x08008118, 0x08008270, 0x080082AC) read `[0x083B50E8] = 0x0300229C`, `+0x14`, bit 0 (A) to 0x08007DE8 and bit 1 (B) to 0x08007EDA (`08008006 lsl r0,r0,#30 ; lsr r0,r0,#31 ; beq ; ... bl 0x8007eda`).
3. **Select ability on L.** 0x08008B88 tests `+0x14` bit 9 (`08008b94 lsl r0,r0,#22 ; lsr r0,r0,#31`) and calls 0x08004284, which steps record +0x09 through the slots enabled in record +0x14 bits 3-6.
4. **Ability lookup.** 0x08007EDA: `ability = record[0x18 + record[0x9]]`, `entry = 0x081D9900 + ability * 16` (`08007eee ldrb r0,[r4,#0x9] ; ldr r1,=0x081d9900 ; add r0,r0,r4 ; ldrb r0,[r0,#0x18] ; lsl r0,r0,#4`). It calls `entry+8` (test) with the record; if nonzero it calls `entry+0xC` (action) with (record, player), else plays a refusal sound.
   - **Record +0x18..+0x1B = ability id per slot.** Defaults (rom:0x1D9548): Gohan `04 03 0c 02`, Piccolo `09 08 0b 02`, Vegeta `00 07 0c 02`, Trunks `01 0d 0c 02`, Goku `03 0a 0c 02`, Hercule `06 06 06 06`. Same in captures 01, 02, 03. This answers the SAV open field.
   - Slot 2 of Gohan, Vegeta, Trunks and Goku is ability 12 (Saiyan transform). Piccolo slot 2 is ability 11 (Namek transform). The slot is usable only when record +0x14 bit 5 is set (capture 01 Gohan +0x14 = 0x43: not yet; capture 02 = 0x7F).
5. **Ability table** rom:0x1D9900, 14 entries of 16 bytes: `+0 icon (usable)`, `+4 icon (not usable)`, `+8 test(record)`, `+0xC action(record, player)`. Literals: 0x08008024 (use) and 0x08008E8C (HUD) only. rom:0x1D99E0 starts other data (`01 00 00 00 80 47 00 00`, three literal refs), so the table cannot grow in place.

| Id | rom | Bytes |
|---|---|---|
| 11 Namek | 0x1D99B0 | `7c ae 6d 08 7c b0 6d 08 f3 34 01 08 c1 34 01 08` |
| 12 Saiyan | 0x1D99C0 | `7c ae 6d 08 7c b0 6d 08 f3 34 01 08 3d 35 01 08` |

6. **Test 0x080134F2** (abilities 11 and 12): +0 bit 1 set: 0. Else +0 bit 0 set: 1 (revert always allowed, no EP check). Else 1 only if `[0x03002080+0xC] != 0` (S: transform allowed on this map) and struct +0x08 == 0 (cooldown) and EP >= 10 (`08013534 cmp r1,#0xa`).
7. **Action 0x0801353C** (ability 12): transformed: message 0x24 to the player, else message 0x23. Action 0x080134C0 (ability 11): 0x24 or 0x25. Messages go through player vtable 0x08025604 +0x28 = 0x080088BA, which sets the state to `[0x083B5278 + 4 * msg]`.

| Msg | State object | Vtable | Enter | Tick | +0x14 (end) |
|---|---|---|---|---|---|
| 0x23 Saiyan transform | 0x03002184 | 0x08025D9C | 0x080155A8 (sound, anim 9 = set +0xDC) | 0x080155E4: struct +0x08 += 8 per frame, then 0x08011D4A | 0x0801563C |
| 0x25 Namek transform | 0x03002188 | 0x08025CE0 | 0x08011D38 (anim 9) | 0x0801560E: struct +0x08 += 0x14 per frame for 0x40 frames | 0x0801563C |
| 0x24 revert | 0x03002180 | 0x080256AC | 0x0801579A (anim 21 = set +0x19C, via 0x08013578) | 0x0801358C | 0x080157AE |

- 0x08011D4A ends after 0xA0 frames and calls the state's vtable +0x14 (`08011d5a cmp r0,#0xa0 ; ... ldr r2,[r1,#0x14] ; ... bl 0x8021d2c`).
- 0x0801563C: `08015652 mov r1,#0x1 ; add r0,r4,#0 ; bl 0x8014d58`. 0x080157AE: `080157b2 mov r1,#0x0 ; bl 0x8014d58`. These are the only two BL callers of 0x08014D58.
8. **Transform routine 0x08014D58 (player, sel):** call old form vtable +0xC (leave); `record+8 = sel ? +4 : +5`; player +0x48 = `get_set(+1)`; message 0 (idle); 0x080086A2 (apply new form); new form vtable +8 (enter).
9. **Cooldown = struct +0x08** (u32 at 0x03000E98). The Saiyan transform adds 160 x 8 = 1280, the base form tick removes 1 per frame (21 s), and the test requires 0. The HUD draws `min(cooldown >> 8, 4)` cooldown pixels when record +0x14 bit 5 is set (`08008d32 ldr r0,[r0,#0xc] ; ldr r0,[r0,#0x8] ; ... asr r0,r0,#8`). Only the base form tick decrements it, so the value never falls while transformed. CONFIRMED for the sites quoted; other writers were not swept (LIKELY complete).

**Entry 5 +4 = 4 (Rage) is never read in play.** CONFIRMED by three facts: +4 has one reader (0x08014D8C, sel 1); sel 1 comes only from 0x0801563C, the end of states 0x23 and 0x25; those messages are sent only by 0x080134EA and 0x08013566, each on the branch where +0 bit 0 is clear. From Super Saiyan, B always reverts (0x24). A message id loaded from data or a register, or a script ext that sets a player state, would not appear in this search.

## 3. Rage in the Cell fight (c)

ext 73 (0, 58) at 0x083EA369 runs handler 0x0800A8EC. CONFIRMED order:

1. `0800a926 ldr r0,[r0,#0x10] ; ... ldr r2,[r1,#0xc] ; bl 0x8021d2a`: old form leave.
2. `0800a948 bl 0x80042bc`: record +8 = 4 (first entry with +1 = 58, from the rom:0x42F0 copy).
3. `0800a950 add r0,r6,#0 ; bl 0x8009324 ; str r0,[r4,#0x48]`: player sprite = raw set 58.
4. `0800a968 bl 0x80086a2`: apply the Rage form: STR, POW, END = 100 flat.
5. `0800a98a ldr r0,[r0,#0x10] ; ... ldr r2,[r1,#0x8] ; bl 0x8021d2a`: Rage enter (sound).

- **Why no ki drain:** the Rage tick 0x0801710E has no EP code. It regenerates 1 % of max HP every 20 frames instead.
- **Why the player cannot leave or re-transform:** entry 4 +0 = 3 sets bit 1, so test 0x080134F2 returns 0 and the HUD shows the dim "Z".
- Rage ends at ext 73 (0, 56) at 0x083EBFFC (post-Cell). Message 0x21 enter 0x0800833E also reverts any form with bit 0 (Rage included) to +5 without animation: `08008374 ldr r0,[r0,#0x10] ; ... ldr r2,[r1,#0xc]` then `0800838a ldrb r0,[r0,#0x5] ; strb r0,[r4,#0x8]`. What message 0x21 means is not traced (S: knocked out).
- Set 58 has 19 animations and lacks anims 9, 11, 12, 20 and 21, which set 59 has. Anim 9 is the transform animation, anim 21 the revert animation. Rage never plays them because it can never use the ability. CONFIRMED by the set headers and the row offsets `+0xDC` (0x08011D44) and `+0x19C` (0x08013584).

## 4. HUD form icon (d)

The HUD icon belongs to the selected ability, not to the form. CONFIRMED.

- Draw routine 0x08008BEE builds 0x500 bytes of 8bpp OBJ tiles on the stack, then DMAs them to `0x06010000 + 32 * tile` (`08008e44 ldr r1,=0x06010000`, count 0x140 words).
  1. DMA 0x300 bytes of the HUD frame from 0x086D7B54.
  2. Pick the icon: `08008d1c ldr r1,[r6,#0x8] ; add r0,r5,#0 ; bl 0x8021d2a ; cmp r0,#0x0 ; beq ; ldr r1,[r6,#0x0] ; b ; ldr r1,[r6,#0x4]`. So it is usable ? entry +0 : entry +4.
  3. DMA the 0x200-byte icon to buffer +0x300. The icon pointer is the redraw key at HUD +0x1C (`08008d6e ldr r2,[r4,#0x1c] ; cmp r2,r1`).
  4. Set bar pixels from offset tables: HP 0x083B5358, EP 0x083B5658, EXP 0x083B5968, cooldown 0x083B5B90.
- **The draw runs every frame, and so does the icon pick.** CONFIRMED by this caller chain:
  1. Main loop 0x0801F294: `ldr r5,=0x03000e1c ; ... ldr r0,[r5,#0x0] ; ldr r1,[r0,#0x0] ; ldr r2,[r1,#0xc] ; ... bl 0x8021d2a`, then `bl 0x8020d40` (frame wait: `swi 0x2` until the IRQ flag, 0x08020D6E), then `bl 0x801eefc` (keys). It calls the current state's vtable +0xC once per frame.
  2. In the field (captures 01 and 02), `[0x03000E1C]` has vtable 0x08023884, whose +0xC is 0x08004EA8. It calls the `[0x03000FF4]` object's vtable +0 and its own +0x1C, then `08004ec6 ldr r0,=0x081d9cb0 ; ldr r0,[r0,#0x4] ; bl 0x8006ad8`. The ROM word at 0x081D9CB4 is 0x03001120, so this is the draw pass on the scene list 0x03001120.
  3. Draw pass 0x08006AD8 calls each object's vtable +0xC (visible?) and then +0x10 (draw) for every visible one: `08006bf8 ldr r1,[r0,#0x0] ; ldr r2,[r1,#0x10] ; add r2,r2,r1 ; mov r1,sp ; bl 0x8021d2c`.
  4. The HUD object has vtable 0x0802408C (stored by the constructor 0x08008B14 at 0x08008B3E). Its +0xC is 0x080264A8 (`mov r0,#0x1 ; bx lr`, always visible) and its +0x10 is 0x08008BEE. 0x080040C6 and 0x0800C630 build it and add it to 0x03001120 through 0x080068B8 (`080040d6 ldr r0,[r4,#0xc]` with r4 = 0x081D952C, and `0800c636 ldr r0,[r6,#0x4]` with r6 = 0x083ED1B8 from 0x0800C5B4; both ROM words are 0x03001120). Captures 01 and 02 hold it in that list.
  5. In 0x08008BEE, no branch leaves the routine before the icon pick at 0x08008D10. The pick runs on every draw, before the redraw-key compare `08008d6e ldr r2,[r4,#0x1c] ; cmp r2,r1`. A new icon pointer forces a redraw in that frame.
- So the icon follows EP, flag 195 and the form in the same frame they change. No redraw hook is needed.
- **Icon format:** raw (no codec), 0x200 bytes, 8 tiles of 8bpp in 1D order, 4 x 2 tiles = 32 x 16 pixels, shared OBJ palette. Render: `scripts\one-time\2026-10-16-task-4-forms-research\icons.png` (from `icons.py`).
- **The "Z":** abilities 11 and 12 both use 0x086DAE7C (usable, yellow Z) and 0x086DB07C (not usable, dim Z).
- **Bars draw over the icon.** The HP, EP and EXP offset tables reach into buffer 0x300-0x4FF: HP 24 pixels (0x310-0x327), EP 24 (0x338-0x33F, 0x400-0x40F), EXP 40 (0x428-0x4EA). A "Z2" icon must keep those pixels as in the "Z" icon. Change only the panel interior.
- These offsets are HUD buffer offsets. **Icon byte = buffer offset - 0x300.** For example, buffer 0x310 is icon byte 0x10.
- **Buu's Fury "Z3": not traced.** SPECULATIVE from me sheet: the "Z3" is the "Z" panel with a small separate "3" glyph. Tried: an exact search for the 8 LoG II "Z" tiles (no match), the LoG II ability lookup bytes `00 7e 00 01` (no match) and the ability-table shape (one hit, 0x087B6928, which is a jump table). The BF engine differs. Reference only; Task 6 does not depend on it.

## 5. RAM for my memory check (e)

| What | Address | Type | Label |
|---|---|---|---|
| Gohan record base | 0x03000E9C | 28 bytes | CONFIRMED (SAV) |
| Gohan current EP | 0x03000EA0 | u16 | CONFIRMED |
| Gohan max EP | 0x03000EA2 | u16 | CONFIRMED |
| Gohan appearance index (2 base, 5 Super Saiyan, 4 Rage, 22 Super Saiyan 2 after Task 6) | 0x03000EA4 | u8 | CONFIRMED |
| Gohan base STR, POW, END (do not change in a form) | 0x03000EA6, 0x03000EA8, 0x03000EAA | u16, 8.8 (value / 256) | CONFIRMED |
| Player object pointer | 0x03001FA8 | u32 | CONFIRMED |
| **Live STR, POW, END with the form bonus** | `[0x03001FA8]` + 0x160, +0x161, +0x162 | u8 each | CONFIRMED |
| Current form object | `[0x03001FA8]` + 0x180 | u32 (0x030021E0 base, 0x030021EC Super Saiyan, 0x030021E4 Rage) | CONFIRMED |
| Drain accumulator | `[0x03001FA8]` + 0x184 | u32, low 16 bits used | CONFIRMED |
| Transform cooldown | 0x03000E98 | u32 | CONFIRMED |
| Flag 195 | 0x03000F5C bit 3 (mask 0x08) | u8 | CONFIRMED (flag n = struct +0xB4 + n/8, bit n&7, SAV; test save `log2_lv40_postcell.sav` slots 1-3: struct +0xCC = 0x0F, bit 3 set, bit 4 (flag 196) clear) |

- The player object moves: 0x020319A8 in capture 01, 0x0202C8A4 in capture 02. Read the pointer first. Proof of +0x160: capture 01 Gohan 3/5/3 gives `03 05 03`; capture 02 leader Piccolo 64.6/56.2/64.2 gives `40 38 40`.
- Expected in Super Saiyan with STR 100: `[ptr]+0x160` = 110 (0x6E), EP at 0x03000EA0 falls by 1 every 20 frames.

## 6. Design for Task 6: how to add the Super Saiyan 2 entry

A new form needs a new appearance entry, because the sprite (+1), the form object (+0x10) and the revert target (+5) are all per entry.

| Option | What | Cost | Verdict |
|---|---|---|---|
| A. Relocate the appearance table, add entry 22 | Copy 22 entries (440 bytes, after Task 5 edits) plus entry 22 to the expansion area. Repoint 17 literal pools. Keep rom:0x42F0 on Task 5's copy | 17 words of data. No code for the table itself. Risk: a reader that computes the address another way (none found, section 8) | **Recommended** |
| B. Reuse an unused entry | None is free: all 22 are reached from default records (3, 6, 8, 18, 19, 21), ext 73 constant sets (53, 55, 56, 58, 128, 129, 132, 137, 138 = entries 0, 1, 2, 4, 12, 13, 15, 8, 9), the debug routine, or their +4/+5 chains. LIKELY complete (ext 73 calls with run-time arguments would not appear) | Breaks the scene that uses the entry (entry 0 is used by ext 73 (0, 53) at 0x083B8595, 0x083CCA4B, 0x083DF2C1) | Rejected |
| C. Make Rage (entry 4) act as Super Saiyan 2 after flag 195 | Entry 5 +4 already = 4. Make the Rage form object, the test and the sprite flag-conditional | Conditional code in apply, tick, test and sprite. Bit 1 must stop locking. Set 58 lacks the revert and transform animations (section 3). Touches Rage | Rejected: Rage must stay unchanged |
| D. "Point entry 5 +4 at a new entry only after flag 195" | +4 is ROM data and cannot depend on a flag. The flag test has to be in code, and the new entry still needs a table slot | Same as A plus a hook inside 0x08014D58, which has no pointer hook point | Not a separate option. A with the gate in the ability action |

### Recommended approach (A with a stepped transform)

1. Relocated table with entry 22 = Super Saiyan 2. Set entry 5 +4 = 22 unconditionally (safe: section 2, last paragraph).
2. B from Super Saiyan steps to Super Saiyan 2 only when flag 195 is set. Otherwise B reverts, as now. B from Super Saiyan 2 reverts to entry 2.
3. The gate replaces the ability 12 action pointer. It tests the data, not Gohan's id: `+0 bit 0 set and +4 != +5`. Today only entry 5 meets that (all 22 entries checked). Entry 22 gets +4 = +5 = 2, so it always reverts.
4. Super Saiyan 2 form object: one ROM word pointing at a new 24-byte vtable. New apply (+20) and tick (0x199A). Enter and leave reuse the Super Saiyan sound methods.
5. HUD: an in-place 10-byte hook plus one literal. With ability 12 selected, it returns the "Z2" icon pair when the leader's appearance is 22 or when B would step up (the gate's own predicate). The icon shows what B does next.

> [!WARNING]
> Super Saiyan 2 must use a set with set 59's animation layout (22 anims, anim 9 and 21 present). Set 58 or a plain clone of it breaks the step animation (anim 9, row set +0xDC) and the revert animation (anim 21, row set +0x19C). Both rows are null or past the end in set 58.

## 7. Patch sites for Task 6 (f)

All original bytes are from the base ROM. "X" is an address Task 6 allocates in rom:0x800000-0xFFFFFF.

### Data

| # | rom | Original | New | Why |
|---|---|---|---|---|
| 1 | 0x1954, 0x1B3C, 0x3B30, 0x414C, 0x854C, 0x886C, 0x8B04, 0xA77C, 0xAA04, 0xB050, 0xC804, 0x10F18, 0x112BC, 0x13574, 0x14FF4, 0x26458, 0x26474 | `7C 96 1D 08` each | GBA address of the relocated table | All literal pools of the table except rom:0x42F0 |
| 2 | 0x42F0 | `7C 96 1D 08` (Task 5 changes it) | Leave on Task 5's unchanged 22-entry copy | ext 73 reverse lookup; keeps `cmp r2,#0x16` (0x080042D6). No ext 73 names the Super Saiyan 2 set |
| 3 | relocated entry 5 +4 (original rom:0x1D96E4) | `04` | `16` (22) | Step target |
| 4 | relocated entry 22 (new, after entry 21) | none | `01 SS 3E 0D 02 02 06 00 14 00 00 00 00 01 00 00` + form object address (LE) | SS = Super Saiyan 2 set id (a set 59 layout). +2/+3 copy entry 5 (or entry 4 `3D 0C`, my choice). +4 = +5 = 2. +6..+0xF as entry 5 |
| 5 | rom:0x1D99CC (ability 12 action) | `3D 35 01 08` | step gate address, bit 0 set | Shared by Gohan, Vegeta, Trunks, Goku: the gate passes through for them |
| 6 | rom:0x8E8C (HUD literal, loaded only by `ldr r1` at 0x08008D12) | `00 99 1D 08` | HUD icon routine address, bit 0 set | HUD hook entry |

- Do not patch rom:0x8024 (the use-ability literal) or rom:0x1D99C8 (the shared test `F3 34 01 08`). The vanilla test already returns 1 in any transformed form.
- Task 5's edits at rom:0x1D96A5 and rom:0x1D96E1 must be carried into the relocated copy (build order: copy after Task 5, or patch the copy).

### Code

| # | rom | Original | New | Disassembly after the patch |
|---|---|---|---|---|
| 7 | 0x8D14-0x8D1D | `40 19 00 7E 00 01 46 18 B1 68` | `28 1C 19 F0 08 F8 01 1C 07 E0` | `add r0,r5,#0 ; bl 0x8021d2a ; add r1,r0,#0 ; b 0x8008d2e` (checked with thumb.py on a patched copy) |

- With item 6, 0x08008D12 loads the hook address into r1 and `bl 0x8021d2a` (`bx r1`) enters it with r0 = record. The hook returns the icon pointer in r0. 0x08008D10 (`ldrb r0,[r5,#0x9]`) stays and is harmless. Bytes 0x8D1E-0x8D2D become dead.
- The hook must keep r4, r5, r7 (used after 0x08008D2E). r6 is dead: it is set again at 0x08008DA0 before any read, and the early exit 0x08008E5E does not read it.
- Full original HUD bytes rom:0x8D10-0x8D2D: `68 7A 5E 49 40 19 00 7E 00 01 46 18 B1 68 28 1C 19 F0 03 F8 00 28 01 D0 31 68 00 E0 71 68`.

### New code and data in the expansion area

| Item | Spec |
|---|---|
| Form object | 4 bytes: address of the new vtable. ROM is safe: no method stores through r0. SS apply starts `080172b0 ldr r0,=0x086f7e50`, tick `08017306 ... add r0,r1,#0`, enter/leave `ldr r0,=0x086f7e50`. Every +0x10 user only reads it |
| Vtable (24 bytes) | Each word = target - vtable base: +0 apply\|1, +4 tick\|1, +8 0x08017377, +0xC 0x08017393, +0x10 0x080271E1, +0x14 0x08026391 (last two copied, not called) |
| Apply | **Re-encoding** (not a byte copy) of the logic of 0x080172B0-0x08017305, with +20 (`#0x14`) in place of the three `add #0xa` at 0x080172CE, 0x080172D6, 0x080172DE. A byte copy crashes from 0x088xxxxx: the original loads pools 0x0801748C, 0x08017498, 0x0801749C pc-relative and BLs 0x080265C4 twice (0x080172EC, 0x080172F8). The new routine has its own literal pool (0x086F7E50, 0x3FE00000, 0x40400000 or my speeds, 0x080265C5) |
| Tick | **Re-encoding** of the logic of 0x08017306-0x08017375 with accumulator step 0x199A. The original loads pools 0x080174A0 and 0x0801748C and BLs 0x08021D2C twice (0x08017314, 0x08017368). It keeps the 0x24 skip test and the EP 0 to message 0x24 revert. **0x199A lives in the new routine's own pool. Never patch 0x080174A0 in place:** that pool belongs to the shared Super Saiyan tick, used by entries 5, 11, 16, 17 and 20 (Gohan, Vegeta, Trunks, Goku) |
| Calls in new code | Every BL in a re-encoded routine becomes `ldr rN,=target` (bit 0 set) plus a local BL to a local `bx rN` stub inside the expansion area |
| Step predicate `step_ok` (r0 = record, result in r2) | `e = table[record+8]`. r2 = 1 if `e+0 bit 0` and `e+4 != e+5` and `[0x03000F5C] & 0x08` and `(s16)[record+4] >= 10`, else 0. Leaf: keeps r0 and r1, uses r3, returns with `bx lr`. **Do not test the cooldown**: it is about 1280 right after Super Saiyan and does not fall while transformed |
| Step gate (ability 12 action, r0 = record, r1 = player) | `push {lr} ; bl step_ok ; pop {r3} ; mov lr,r3`. If r2 = 1: send message 0x23 to the player (`ldr r2,[r1] ; ldr r3,[r2,#0x28] ; add r3,r2`, r0 = player, r1 = 0x23, bx). Else jump to 0x0801353D with r0, r1 unchanged. Both exits leave lr and sp as at entry |
| HUD icon (r0 = record, returns r0) | `id = record[0x18 + record[9]]`; `e = 0x081D9900 + 16 * id`; `ok = e.test(record)`; `icon = ok ? e[0] : e[4]`; if `id == 12` and (`record[8] == 22` or `step_ok(record)`): `icon = ok ? Z2 : Z2dim`. Push and pop r4-r7. The gate and the HUD call the same `step_ok`, so the icon cannot disagree with B |
| Z2 icon pair | 2 x 0x200 bytes, raw 8bpp, 32 x 16, made from 0x086DAE7C and 0x086DB07C. Existing palette indices only. Keep every pixel in the HP, EP and EXP offset tables (section 4) |

> [!IMPORTANT]
> Thumb BL reaches only +/-4 MB. The game code is below 0x08030000, so neither direction reaches 0x08800000. Enter the expansion area only through absolute pointers (items 5 and 6, the vtable). Inside the expansion area, call base code with `ldr rN,=target|1` and a local `bx rN` stub. The base bx stubs are 0x08021D28 (r0), 0x08021D2A (r1), 0x08021D2C (r2), 0x08021D2E (r3). No assembler is installed: hand-encode and check each routine by disassembly (thumb.py), or use Ghidra's assembler from a script.

### Task 6 requirements (my Rulings 15 and 16)

- **END cap.** Add a test that 100 + END bonus <= 127. The damage formula computes `0x80 - END` (`0800f94a ldrb r0,[r6,#0x2] ; mov r1,#0x80 ; sub r0,r1,r0`). With END 120, Super Saiyan 2 takes about 44 % of Super Saiyan damage (8/128 against 18/128).
- **Attacker overflow** at 0x0800F974 (`mul r0,r5`): LIKELY safe only. The review sampled one descriptor family.
- **Gate keeps lr.** The step gate must return correctly on both exits: the fall-through to 0x0801353D and the tail call through player vtable +0x28. ARMv4T Thumb cannot `pop {lr}`: pop into a low register, then `mov lr,rN`.
- **Gate uses the relocated table.** Read the appearance entry through the relocated address, never 0x081D967C. Index 22 at the old base lands on the EXP table (rom:0x1D9834).
- **Step EP cost >= 9.** The Super Saiyan tick keeps running during the 160-frame step state (it skips only state 0x24), so it drains 8 EP. With less than 9 EP the drain reaches 0 and sends message 0x24 mid-step.
- **Map word (Ruling 16, decision).** The gate does not test the map-allowed word `[[0x086DB284]+0xC]` (= `[0x03002080+0xC]`). Vanilla skips it too while transformed (test 0x080134F2 returns 1 on +0 bit 0 before that check).

### Suggested Task 6 tests

- `test_ssj2_gate_reads_flag_195`: the gate routine bytes load 0x03000F5C and test 0x08.
- `test_rage_entry_unchanged`: relocated entry 4 equals rom:0x1D96CC (20 bytes), and the reverse-lookup copy still finds 58 at index 4.
- `test_all_17_pools_repointed`: every word in item 1 equals the new table address, and rom:0x42F0 equals Task 5's copy.
- `test_entry5_plus4_is_22` and `test_entry22_revert_is_2`.
- `test_z2_icon_keeps_bar_pixels`: for every HP, EP and EXP table offset o with 0x300 <= o < 0x500, Z2[o - 0x300] equals Z[o - 0x300] (both icons of the pair).
- `test_ssj2_set_has_anim_9_and_21`.

## 8. Search shapes and limits

- **Appearance table readers.** (1) Aligned words equal to 0x081D967C: 18 pools. (2) Aligned words inside 0x081D967D-0x081D9833: none. (3) Neighbor literals 0x081D9400-0x081D99FF: 0x081D9638 is a compressed block header (`01 00 00 00 80 47 00 00`), not an offset into the table. (4) For each of the 24 ldr sites, the next 48 instructions for +4, +5 and `cmp #0x16`. A site that builds the address from another base with an added constant would not appear.
- **Form object users.** Shape A: +0x10 reads after each table ldr (10 sites, all read only, 0x0800A9AE is a false positive on another table). Shape B: `add #0xff ; add #0x81/#0x85` (player +0x180/+0x184) in 0x08000000-0x0802FFFF: 2 player sites (0x08008704 store, 0x0800876A tick) plus form methods. The rest (0x0800B63E, 0x0800E3B6-0x0800E56E, 0x080105B6, 0x0801D31C) use +0x180 as a struct with fields +4, +8, +0xD (LIKELY another object class).
- **Messages 0x23, 0x24, 0x25.** `mov r1,#imm` followed by a bx stub call, 0x08000000-0x0803FFFF: 10 sites, all in sections 1 and 2. Code above 0x08040000, a message id from data or a register, and script ext ops that set a player state would not appear.
- **Callers of 0x08014D58:** Thumb BL scan: 2. No pointer words hold it.

## 9. Open questions

1. **Me:** from Super Saiyan with flag 195, should B go up to Super Saiyan 2 (recommended) or revert? Should base go straight to Super Saiyan 2 instead?
2. Answered (final, 2026-10-17): the icon shows what B does next. "Z2" shows in Super Saiyan 2, and in Super Saiyan when B would step up (flag 195 set, EP >= 10). Otherwise "Z". Bright or dim follows the ability test.
   - LIKELY side effect: the step state lasts 160 frames and the record stays in entry 5 until it ends. The Super Saiyan tick drains 8 EP in that time. A step that starts with EP 10-17 drops under 10 mid-step, so the icon shows "Z" for the rest of the step and "Z2" again in entry 22. Not seen in play.
3. **Me:** Super Saiyan 2 speed (+0x188/+0x18C). Default: same as Super Saiyan (1.75 / 3.0).
4. **Me:** EP needed for the step (default 10, like Super Saiyan; never below 9, section 7). The step adds another 1280 to the cooldown, so after Super Saiyan 2 the wait is about 43 s.
5. Which set Super Saiyan 2 shows: needs a set 59 layout (spiky hair art from set 58 on set 59 animations, or Task 5's gi Super Saiyan clone). Mine and Task 6.
6. Portrait ids +2/+3 for entry 22: Super Saiyan (`3E 0D`) or Rage (`3D 0C`). Task 7.
7. Can the game save while transformed? A save in Super Saiyan 2 stores record +8 = 22, which only the patched ROM can load. 0x08003ED4 reverts transformed non-leaders on load. Not traced for the leader.
8. `[0x03002080+0xC]` (map allows transform): meaning SPECULATIVE.
9. Message 0x21 (revert without animation, 0x0800833E): trigger not traced.
10. Europe status screen form bonus: not traced.

## Files

| File | Purpose |
|---|---|
| `scripts\one-time\2026-10-16-task-4-forms-research\vtfind.py` | Find vtables whose base-relative entries point at a function |
| `scripts\one-time\2026-10-16-task-4-forms-research\formuse.py` | Readers of appearance +0x10 and player +0x180/+0x184 |
| `scripts\one-time\2026-10-16-task-4-forms-research\appsweep.py` | Every way to reach the appearance table; +4/+5 readers |
| `scripts\one-time\2026-10-16-task-4-forms-research\icons.py`, `icons.png`, `hud_base.png` | Render the ability icons and the HUD frame |
| `scripts\one-time\2026-10-16-task-4-forms-research\bf_hud_crop.png`, `log2_hud_crop.png` | Zoomed crops of my HUD sheets |
