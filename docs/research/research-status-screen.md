# Research 2: status screen bonus bars and stat points

This page answers the five questions in `docs\tasks\2026-10-17-status-screen-research\research-2-status-screen.md` (design 6.3, slice 2). Sections 1 to 4 are research on the vanilla ROMs. Section 8 describes the `status_bonus` patch that builds tasks 2 to 5.

Labels: **C** = CONFIRMED (address plus bytes or disassembly), **L** = LIKELY, **S** = SPECULATIVE. Addresses are LoG II USA unless tagged EU. Scope (Ruling 34): no Buu's Fury code was read. Buu's Fury facts come from images and data scans only.

> [!IMPORTANT]
> **The premise is wrong.** The Europe ROM draws no gold bonus segment. Its status page is the USA page with one fix: it finds the player during the menu, so the number and the bar length include the form bonus. The bar still stops at 100. A gold segment is new work in slice 2, not a port.

> [!NOTE]
> **Short answer.**
> - USA shows only base stats on the status page because the menu clears the player pointer before the page draws (C for the code path, L at runtime until my check 1).
> - Europe looks the player up in the suspended object list instead, so it shows base + bonus as one number and one bar (C).
> - A gold segment needs no new palette entry: the menu palette already has gold colors (C). It needs one 75x8 image (600 bytes) and about 1 KB of relocated code (L).
> - The bar is full at 100. With base 100 the bonus cannot show unless the bar scale changes. This is my call.
> - Stat points can live in 6 padding bytes of the save slot without a format change (L).

---

## 1. USA status page `0x0800379C`

This section maps what the page draws and where each value comes from.

The page draws into an 8bpp bitmap canvas, then copies it to BG VRAM. It does not draw with sprites, so the shared OBJ palette is not involved.

| Fact | Evidence | Label |
|---|---|---|
| Routine `0x0800379C`-`0x08003AFC`, literal pool to `0x08003B43` (0x3A8 bytes). Only caller: page dispatcher `0x08003B44` (BL at `0x08003B5E`, page 0). The dispatcher is reached through base-relative vtable entries at `0x08023B9C` and `0x0802492C` | Disassembly in `scripts\one-time\2026-10-17-status-screen-research\status_usa_379c.txt`; BL scan; vtable word scan | C |
| Three canvases: 208x88 main page (`sp+0x9C`), 64x64 portrait (`sp+0x64`), 64x8 level line (`sp+0x2C`), made by `0x08020E5C(canvas, w, h)` | `080037c2 mov r1,#0xd0` with `r2 = 0x58`; `0x40, 0x40`; `0x40, 0x8` | C |
| Canvas layout: +0x24 pixel buffer, +0x2C stride; one byte per pixel | Fill `0x0802130A` and blit `0x08021188` read `[r0,#0x24]` and `[r0,#0x2c]`, store with `strb` | C |
| Page background: frame `0x081D9638` (208x88, indices 1, 146, 149) unpacked into the main canvas | `08003802 ldr r0,=0x081d9638 ; bl 0x801f394` with r1 = `[sp+0xc0]` (canvas +0x24) | C |
| Record: `r4 = struct + 0xC + 28 * char`; `char` comes from `[this + 0x158 + 4 * page + 4]` | `080037a6`-`080037c0` | C |
| HP: text "HP" at (59, 15); "%d/%d" (HP, max) at (136, 23); filled rect x 62 to 62 + HP * 74 / max, y 8 to 15, color index 5 (248,0,0) | `0x08003844`-`0x08003898`; fill routine `0x0802130A` writes one color byte per pixel | C |
| EP: same shape, y 24 to 31, color index 4 (0,248,0) | `0x0800389C`-`0x080038EC` | C |
| STR, POW, END base values: record +0x0A, +0x0C, +0x0E, 8.8 fixed point, shifted right 8 into `[sp+0x14]`, r6, r7 | `08003902 ldrh r0,[r4,#0xa] ; lsr r1,r0,#8 ; str r1,[sp,#0x14]` | C |
| Live override: if the shown character is the leader AND the word at `0x03001FA8` (player pointer) is not 0, the three values are replaced by player +0x160, +0x161, +0x162 | `0800391a cmp r0,r1 ; bne` then `0800391e ldr r0,=0x03001fa8 ; ldr r0,[r0] ; cmp r0,#0 ; beq` then `08003926 add r0,#0xff ; add r0,#0x61 ; ldrb r1,[r0]` | C |
| Stat text: "STR", "POW", "END" at (59, 47 / 63 / 79); value "%d/100" at (136, 55 / 71 / 87) | strings at `0x080E2840` +0x70, +0x74, +0x78; format `0x08003B24` | C |
| Stat bar width: `w = 75` if value > 100, else `(value >> 2) * 3`. One bar segment = 4 points | `08003960 mov r0,#0x4b ; cmp r1,#0x64 ; bgt ; asr r0,r1,#2 ; lsl r3,r0,#1 ; add r0,r3,r0` | C |
| Stat bar draw: `0x08021188(canvas, src, rect, stride 75)` copies the bar image into rect x 62 to 62 + w, y 40 to 47 (POW 56 to 63, END 72 to 79). Source index 0 is transparent | blit body: `ldrb r3,[r1] ; cmp r3,#0 ; beq skip ; strb r3,[r0]` | C |
| Bar image: frame `0x086F869C`, 75x8, 25 segments of 2 color px + 1 black px, red to yellow to green (indices 47 to 40, 8, 89 to 85, 112) | rendered `scripts\one-time\2026-10-17-status-screen-research\usa_bar.png` | C |
| EXP value "%d" (record +0x10) at (208, 79); "NEXT" value (`0x08004230`) at (208, 87) unless level is 50; labels "EXP", "NEXT" at (144, 79 / 87) | `0x08003A22`-`0x08003A7C` | C |
| Level line: "Level: %d" (`0x08004214` = level) drawn on the 64x8 canvas, which is cleared to index 0x95 and copied to `0x0600B0C0` | `08003834 bl 0x8021f18` with `r1 = 0x95`; `08003ade` | C |
| Portrait: appearance +3, unpacked to the 64x64 canvas, blitted into the main canvas at rect {144, 4, 208, 68} (table `0x081D94E4`) | `08003a8c ldrb r0,[r0,#0x3]`; `08003a9e add r2,#0x14 ; bl 0x80211c8`; words at `rom:0x1D94E4` | C (call), L (rect order x0, y0, x1, y1) |
| Main canvas copied to BG VRAM `0x06006940`; tile map written to `0x0600E000` | `08003ad0`-`08003ad4`; `0x0801F508` calls | C (addresses), L (map meaning) |
| Text color: canvas +0x20 is a font object; +0x28 = 1 and +0x29 = 2 for most text, +0x29 = 0x29 for "Level", "EXP" and "NEXT"; index 0x29 (41) is gold (248,184,24) | `080037ee strb r0,[r1,#0x9]` (r1 = canvas + 0x20); `08003a52` | C (stores), L (+0x29 = text color, +0x28 = shadow) |
| Menu BG palette: `rom:0x1D4F50`, all 256 entries, DMA'd to `0x05000000` at menu init (`0x08011046`, also `0x08000BC4`); one generated color ramp, index 0 and 1 both black | DMA count `0x100` halfwords; `scripts\one-time\2026-10-17-status-screen-research\menu_palette_1D4F50.png` | C |

---

## 2. Europe status page and the bonus

This section finds the Europe page, diffs it against USA, and lists what slice 2 needs.

### 2.1 The Europe page

| Fact | Evidence | Label |
|---|---|---|
| EU status page `0x0800E3CC`, dispatcher `0x0800E7E8` (same page 0 to 3 switch) | Byte search: `ff30 6130 0178 0591 4678` at USA `0x08003926` and EU `0x0800E588` only; dispatcher bytes `08b5 002a 09d0 012a 0ad0 022a 0bd0` at USA `0x08003B44`, EU `0x0800E7E8` | C |
| Same canvases, same coordinates, same bar formula (`cmp #0x64 ; bgt ; (v >> 2) * 3`), same 75 px clamp | `0800e5d0`-`0800e5de`; full side by side in `scripts\one-time\2026-10-17-status-screen-research\status_eu_e3cc.txt` | C |
| Same blit (EU `0x08021638`, byte for byte the USA `0x08021188` body), same bar image (EU `0x086A0ED0`, same SHA-1 `21e2a4056876` as USA `0x086F869C`), same background (EU `0x086A32A8`), same palette bytes (EU `0x086A85F8` = USA `rom:0x1D4F50`) | `scripts\one-time\2026-10-17-status-screen-research\render.py` output: "palette equal True, bar equal True, bg equal True" | C |
| EU differences: (1) strings come from per-language tables (`[0x0802B288] + 3` = language); (2) the player lookup | Diff of the two listings | C |
| EU player lookup: `list = [[0x0802B288 + 8] + 0xBC0 + 0x38]`, then `0x0801E61A(list, 7, 0)`; if the result is not 0, read +0x160..+0x162 as USA does | `0800e570 ldr r0,=0x0802b288 ; mov r1,#0x2f ; ldr r0,[r0,#0x8] ; lsl r1,r1,#6 ; add r0,r0,r1 ; mov r2,#0 ; mov r1,#7 ; ldr r0,[r0,#0x38] ; bl 0x801e61a ; cmp r0,#0 ; beq` | C |
| `0x0801E61A` (EU) = USA `0x08006E0A`: send message r1 to each object in both lists, return the first non-zero answer | Same bytes `f8b5 4468 071c 161c 0d1c 013c` in both ROMs | C |
| The player answers message 7 with its own pointer | USA player method `0x08008944` (vtable `0x08025604` and `0x08025F28` +0x24): `0800894e cmp r1,#0x7 ; beq 0x8008a1a` and `08008a1c add r0,r4,#0` | C |

**No gold anywhere in the EU page.** Search shapes used, all agree:

| Shape | Result | Label |
|---|---|---|
| BL callers of the EU blit `0x08021638` | 3 (`0x0800E5EE`, `0x0800E648`, `0x0800E6A4`), one per stat, as in USA | C |
| BL callers of the EU fill `0x080217BA` | 2 (HP, EP), as in USA | C |
| Literal users of the EU bar image `0x086A0ED0` | 2 (`0x0800E542`, `0x0800E54E`: size read and unpack), as in USA | C |
| Other 0x258-byte (75x8) frames | EU `0x081CFC6C` = USA `0x0858AED8`, same SHA-1 `6705002a9f69`, not referenced by either status page | C |
| A second draw per stat in the EU page | None: each stat row has one label, one value, one blit | C |

A gold drawing done in another routine or a different screen would not appear in these shapes. Nothing in the EU page calls such a routine.

### 2.2 Why USA hides the bonus

| Step | Evidence | Label |
|---|---|---|
| Opening the status menu calls `0x08006F4A(world)` | `08004e2e ldr r0,[r7,#0xc] ; 08004e30 bl 0x8006f4a`, then the menu object (vtable `0x080248CC`, whose page dispatcher is `0x08003B44`) is made at `0x08004E46`. Another menu path does the same at `0x08004D9A` (vtable `0x080253CC`) | C |
| `0x08006F4A` sends message 8 to every object, copies the object lists (0xE00 bytes) to a heap buffer, stores it at world +0xBC0 +0x38, and empties the live lists | `08006f50 mov r1,#0x8 ; bl 0x8006da6`; `08006f84 bl 0x8021ea8` with `r2 = 0xE00`; `08006f90 str r5,[r6,#0x38]` (r6 = world + 0xBC0) | C |
| `0x08006DA6` delivers the message through each object's vtable +0x24 | `08006dc8 ldr r2,[r1,#0x24] ; add r3,r2,r1 ; ... bl 0x8021d2e` | C |
| Player message 8: run the current form's leave method, then store 0 to `0x03001FA8`. Message 9: run enter, then store the player back | `080089e0 bl 0x8021d2a ; mov r0,#0 ; str r0,[r6]` (r6 = `0x03001FA8`); `08008a0c str r4,[r6]` | C |
| The leave methods do not touch the live stats: Rage `0x08017174`, Super Saiyan `0x08017392`, Super Vegeta / Trunks `0x08017298` only stop sound entry 55 (`mov r1,#0xa5 ; lsl r1,#2 ; ... bl 0x801fc22 ; pop`); base and Namek leave are `bx lr` (`0x0802609C`). So player +0x160..+0x162 keep the bonus during the menu, and the Europe lookup reads base + bonus | C |
| So during the menu the USA page sees pointer 0 and prints the record base stats. A form bonus never shows | Combination of the rows above | C (code path), L (runtime; see my check 1) |
| The USA world object is `0x03001120` (ROM tables `0x086F7E50` +0x10 and `0x081D952C` +0xC). The level-up code broadcasts to it: `08003db0 ldr r6,=0x081d9548 ; sub r6,#0x1c` (r6 = `0x081D952C`), `08003de8 ldr r0,[r6,#0xc] ; bl 0x8006da6`. In capture 01 its list holds 3 objects, the player `0x020319A8` among them | Code above; `scripts\one-time\2026-10-17-status-screen-research\states\ss1\iwram.bin` | C |

> [!NOTE]
> My screenshot "100 to 110" (research notes, forms table) fits the Europe page. If it was taken on the USA ROM, this explanation is wrong. My check 1 settles it.

Europe also changed the reapply after stat items. EU `0x080159FC` uses the player pointer if set, else the message 7 query, then reapplies the form (EU `0x08015786`). The stat item routine calls it (EU `0x080117C2`, `0x08011822`, `0x08011882`). USA `0x0800F4AA` checks `0x03001FA8` before `0x0800F4B2 bl 0x80086a2` and skips the reapply in the menu (C). So in USA, a STR item used from the menu leaves the live STR one step behind until the next map load or transform (L).

### 2.3 What a USA build needs

This list covers both parts: the Europe fix (number and bar include the bonus) and the new gold segment.

| Need | Detail | Label |
|---|---|---|
| Player lookup | Replace the test at `0x0800391E`-`0x08003925` with: `list = [0x03001D18]` (world `0x03001120` + 0xBC0 + 0x38), `0x08006E0A(list, 7, 0)`. About 0x18 bytes plus a pool word, against 8 bytes in place. It does not fit in place | C (addresses), L (size) |
| Hook | A Thumb BL from the base ROM cannot reach the expansion area (RE-BIBLE, Task 6). Put a 16-byte long-jump veneer at `0x0800379C` (the only entry: one BL caller, no literal) and run a relocated copy of the page (0x3A8 bytes) at `rom:0x800000`+. Calls back into base code (`0x08021188`, `0x08006E0A` and about 15 others) need `bx` veneers or a long-call helper | C (one entry), L (method) |
| Base and live together | The copy keeps base (record >> 8) and live (player +0x160..0x162) in separate stack slots. Bonus = live - base, never below 0 | C (sources), L (layout) |
| Gold segment | Second blit per stat: source = gold image + base width, rect from base width to live width, stride 75. The blit takes any source pointer, so the segment pattern stays aligned | C (blit behavior) |
| Gold image | 75x8, 600 bytes, raw type 0 or plain bytes. Draft: `scripts\one-time\2026-10-17-status-screen-research\gold_bar_75x8.bin` (indices 82 and 69) | L |
| Palette | No new entry and no palette change. Gold colors already in `rom:0x1D4F50`: 82 (248,208,64), 69 (248,232,120), 37 (248,160,64), 36 (224,184,64), 41 (248,184,24, already used as text gold). The OBJ palette is not touched | C (colors), L (that no other menu page conflicts; we only read entries, so a conflict cannot arise) |
| Size | About 1 KB code and pool plus 600 bytes art, all in the expansion area | L |
| Tiles | No new VRAM tiles and no tile map change. The gold segment is drawn into the existing 208x88 canvas before the copy to `0x06006940` | C |
| Optional | Bonus text, for example "100+20", in text color 41 | S |

**Two design problems** (see `scripts\one-time\2026-10-17-status-screen-research\mock_gold_bars.png`, a mock, not game output):

- **Scale.** The bar is full at 100. The stat cap is 100 (`0x08003C6E` clamps at `0x6400`). A level 40 to 50 character near 100 would show no gold at all. The mock's lower half uses a 125 scale: one segment = 5 points, 100 = 20 segments, 125 = 25. This changes how a full base bar looks.
- **Contrast.** The bar's middle is already yellow (indices 8, 87 to 89). A gold segment there is hard to see. Options: a pale gold (69), a gold with a white top row, or a different color.

---

## 3. Stat points

This section maps the level-up code and says where a points counter can live.

### 3.1 Level-up code

| Fact | Evidence | Label |
|---|---|---|
| Level-up `0x08003CA0(struct, char, old_level, new_level)`: `L = new - old`; STR, POW, END each get `stat += L * min + rand((max - min + 1) * L)` through `0x08003C6E`, cap `0x6400` | `08003cd0 ldr r1,=0x081d9548 ; add r1,#0xa8` (range table `rom:0x1D95F0`, 12 bytes per character: 3 x {u16 min, u16 max}); `08003c92 mov r1,#0x19 ; lsl r1,r1,#10 ; cmp ; bls ; strh r1` | C |
| Per level: max HP += max HP x (0xE14 + rand(0x51F)) >> 16, HP = max; max EP += 2 + rand(3), EP = max | `0x08003D02`-`0x08003D2E` | C |
| Integer gains stored for the level-up text: STR to `0x03001FC1`, POW `0x03001FC2`, END `0x03001FC3` | `08003d38 ldr r1,=0x03001fc1 ; strb r0,[r1]` | C |
| Those bytes are read by three script VM handlers (`0x08009466`, `0x08009478`, `0x0800948A`) that push them as values | `ldr r1,=0x03001fc0 ; ldrb r2,[r1,#0x1]` (and #2, #3) then push | C (reads), L (they feed the level-up dialog) |
| Callers: EXP gain `0x08003D58` (BL `0x08003D92`), debug level 40 (`0x08005C98`), one more (`0x0800AC4E`) | BL scan | C (sites), L (`0x0800AC4E` is a script op) |
| After a level-up the game shows dialog script `0x083B6524`, plays a sound, and reapplies the form when the player exists (`0x080086A2`) | `0x08003DAA`, `0x08003DD8`-`0x08003DE0` | C |
| Stat items add 1, 3 or 5 points (as `n << 8`) to a record stat, cap `0x6400` (STR shown here) | `0800f470 ldrh r4,[r3,#0xa]`; `0800f48a lsl r0,r2,#8 ; add r0,r4,r0`; `0800f492 strh r0,[r3,#0xa]` | C |

**Removing the random gains needs no code.** Set every min and max in `rom:0x1D95F0` (72 bytes) to 0. The formula then adds `rand(L)` in 1/256 units, below one point over 49 levels (C, from the formula). The level-up text would then print "+0" for each stat. The dialog `0x083B6524` should change to a "stat points gained" line (L).

### 3.2 Where the counter can live

| Option | How | Cost | Label |
|---|---|---|---|
| **A. Save padding (recommended)** | Struct +0x05..+0x07 and +0x15D..+0x15F: 6 bytes, one u8 per character, inside the checksummed 0x164 bytes. The slot size, offsets and checksum do not change | Zero them in default init `0x08003C24` (it writes +0x00, +0x01, +0x08, the records, the flags and the items, not these bytes). Old saves read 0 points | L (see below) |
| B. No storage | `unspent = P * (level - 1) - sum(stat - start stat)`, start stats from the default table `rom:0x1D9548`, level from EXP | Breaks with stat items (they raise record stats directly) and with the 100 cap. Old saves with random gains give wrong counts | L |
| C. New save block | A new block after `0x448` in the 8 KB EEPROM, with its own checksum | Hooks in save `0x08004030` and load `0x08003F9C`; a new save region must pass the anti-piracy test | L |

Evidence that the padding bytes are unused, by search shape:

| Shape | Hits | Label |
|---|---|---|
| Absolute literals `0x03000E95`-`0x03000E97`, `0x03000FED`-`0x03000FEF` | 0 | C |
| `add rX,#0xff` then `add rX,#0x5e/0x5f/0x60` (offsets 0x15D..0x15F) in code `0x08000000`-`0x08030000` | 0 | C |
| Byte access at #5..#7 through a register loaded from a struct pointer source (`0x03000E90`, `0x081D94D0`, `0x086F7E50` +4) | 0 | C |
| Byte access at #5..#7 with any base in `0x08001000`-`0x08005FFF` | 40; the ones checked are other objects (menu fields, map bits at +0xE7, appearance +5); the rest are not resolved | L |

A function that gets the struct as an argument and touches +5..+7 would not appear in shapes 1 to 3. So option A is LIKELY, not CONFIRMED. The items array ends at +0x15C (item 49). An item id of 50 or more would write into +0x15D; the item count was not checked (S).

### 3.3 Not traced yet

- Where the player assigns points. The status page only draws; it has no input code. A cursor and A/B input need either a new menu page or input in the menu object (vtables `0x080248CC`, `0x08023B3C`). Not traced (S on effort).
- Points per level. I believe Buu's Fury gives 3. Ruling 34 forbids reading Buu's Fury code, so the ROM cannot confirm it here (my play test, or final decisions).

---

## 4. Buu's Fury look

This section describes the Buu's Fury art that exists in `data\` and what fits LoG II.

| Fact | Evidence | Label |
|---|---|---|
| The HUD sheet has no status screen. It holds: attack icons (with "Z" and a "3" glyph); a "STAT" badge with an up arrow, 4 frames of 16x16 (arrow bob); a HUD panel (name box, four short bars red, green, yellow, orange, a pointer, a thin blue bar); a scouter; a d-pad; a long red to yellow to green gradient bar and a red bar in frames | `scripts\one-time\2026-10-17-status-screen-research\bf_hud_x3.png`, `bf_panel_x8.png`, `bf_stat_x8.png`; badge frames at sheet x 0, 16, 32, 48, y 56 to 71 | C (what is drawn), S (what each bar means) |
| The "STAT" badge LIKELY marks unspent points on the HUD | my design and game memory; no BF code read | S |
| Two 240x160 Buu's Fury menu frames: `rom:0x7319E0` and `rom:0x732384` (frame codec type 1). Layout: a large grid panel top left with arrows under it, two small panels top right, one large panel bottom right, one wide panel bottom left | Data scan of all 0x9600 frames; `scripts\one-time\2026-10-17-status-screen-research\bf_menu_pair.png` (placeholder colors, the BF BG palette was not found) | C (frames and layout), S (that this is the status or stat screen) |
| No Buu's Fury text strings "STR", "POW", "Level: %d" in ASCII | String search; the BF text encoding is unknown | C (search), S (meaning) |
| BF frame `rom:0x1C90B8` (600 bytes) is not a stat bar: scattered pixels at widths 8 to 75 with the BF OBJ palette | `scripts\one-time\2026-10-17-status-screen-research\bf_1c90b8_w24.png` | L |

**What fits LoG II.**

- The STAT badge: a 16x16 OBJ beside the HUD. Its yellow, gold and black can map to LoG II OBJ palette entries (BFS shows 83 to 91 % exact matches for BF character colors). It must use existing OBJ indices. Fits (L).
- The gradient bar style: the LoG II stat bar is already red to yellow to green, as the BF bars are. Fits as is (C, both images).

**What does not fit.**

- The BF full-screen 5-panel menu. LoG II draws its status page as one 208x88 canvas inside its own menu frame, with a fixed portrait box at the right. A BF-style layout means a new menu screen (S on effort).
- BF art on the menu BG palette: BF art would need a remap to `rom:0x1D4F50` (L).

I should supply a Buu's Fury status and stat-assignment screenshot, or an mGBA state taken on it. Without BF code, that is the only way to read its exact layout.

---

## 5. Slice 2 outline

This section orders the status screen work. Each task is small enough to test alone.

| # | Task | Depends on | Risk | Status |
|---|---|---|---|---|
| 1 | My check: USA mGBA state with Super Saiyan active and the status page open | none | Settles section 2.2: the screen shows what USA prints, and WRAM shows player +0x160 through the suspended list `[0x03001D18]` | Open (my check) |
| 2 | Relocate the status page behind an entry veneer at `0x0800379C`; byte-identical behavior first (no visible change) | 1 | Long calls back into base code; a missed call hangs the menu | Built (section 8) |
| 3 | EU player lookup in the relocated page (number and bar show base + bonus) | 2 | Low: EU proves the method | Built (section 8) |
| 4 | Gold segment: base bar to base, gold from base to live, chosen scale | 3, final decisions 1 and 2 | Contrast; the bar scale changes the look of every stat | Built (section 8) |
| 5 | Reapply form stats after a stat item in the menu (EU `0x080159FC` pattern), so live never lags base | 3 | Low; without it, bonus = live - base can be wrong after an item | Built (section 8) |
| 6 | Remove random stat gains: zero the table `rom:0x1D95F0` (data only) | none | The level-up text prints "+0" until task 8 | Open |
| 7 | Points counter in struct +0x05..+0x07, +0x15D..+0x15F; level-up adds P per level; default init zeroes them | 6, final decisions 3 | The padding bytes are LIKELY unused, not proven; an in-game save and load test is required | Open |
| 8 | Level-up dialog: show points gained instead of stat gains | 7 | Script text edit; the dialog format is not traced | Open |
| 9 | Assignment UI: cursor on STR, POW, END in the status page, A adds a point, B undoes before leaving | 7, final decisions 4 | Largest unknown: menu input code is not traced | Open |
| 10 | Optional: STAT badge on the HUD while points are unspent | 7 | OBJ VRAM and palette indices; the HUD build is at `0x08008BEE` | Open |

Order: 1, 2, 3, 5, 4 (status display), then 6, 7, 8, 9 (points), then 10.

---

## 6. Final decisions

1. **Gold or not.** Decided (final, 2026-10-17): a gold segment after the base part. Built in section 8.
2. **Bar scale.** Decided (final, 2026-10-17): a 125 scale, 3 px a 5 points, `w = min(v, 125) / 5 * 3`. Built in section 8.
3. **Points per level and cap.** 3 per level (my memory of Buu's Fury)? Keep the 100 cap per stat?
4. **Where points are spent.** On the status page (LoG II style) or a new Buu's Fury style screen? Please supply a Buu's Fury screenshot or mGBA state of its stat screen.
5. **Check 1.** Was the "100 to 110" screenshot from the USA or the Europe ROM? One USA mGBA state with Super Saiyan active and the status page open settles section 2.2. Its screen shows what USA prints. Its WRAM shows the live stats through the suspended list at `0x03001D18`, which proves the bonus survives the menu.
6. **Number text with a bonus.** Open. The build draws "100+20" (`BONUS_TEXT = "split"`); the other option draws "120" (`"live"`). See section 8.

---

## 7. Files

All scripts only read the ROMs. They live in `scripts\one-time\2026-10-17-status-screen-research\`.

| File | Content |
|---|---|
| `status_usa_379c.txt`, `status_eu_e3cc.txt` | Full listings of both status pages (thumb_dis) |
| `find_eu.py`, `find2.py` | Byte pattern search in both ROMs |
| `lits.py`, `stores.py`, `blctx.py`, `ctx.py` | Literal users, stores through a literal, BL callers with context |
| `render.py`, `usa_bar.png`, `usa_bg.png`, `eu_bar.png`, `eu_bg.png` | Decoded status art in both ROMs |
| `pal_usage.py`, `menu_palette_1D4F50.png` | Menu palette colors and use by status art |
| `mock.py`, `mock_gold_bars.png`, `gold_bar_75x8.bin` | Mock of vanilla and gold bars (not game output), draft gold image |
| `mock_status.py`, `mock_status_gold.png` | Mock of the patched page: the built page code run in the test interpreter and painted with the ROM font, bar art and menu palette (not game output) |
| `r9_diff.py` | Proof of where `log2_poc_r9.gba` differs from `log2_poc_r8.gba` |
| `listing_check.py` | Proof of the page copy in `log2_poc_r9.gba` against `status_usa_379c.txt` |
| `padscan.py`, `padscan2.py`, `padscan3.py` | Search shapes for the padding bytes |
| `bf_scan.py`, `bf_full.py`, `bf\`, `bf_*.png` | Buu's Fury data scans and crops |
| `states\` | Memory regions of the four data\roms save states |

---

## 8. Built: the gold bonus patch `status_bonus`

This section describes `scripts\permanent\patches\status_bonus.py` (tasks 2 to 5). It runs after `ssj2_form`. Offsets are those of `archive\builds\log2_poc_r9.gba`, SHA-1 `f61fd3b7c978d12dc7e05b1ba5723c4bf238bcc7`. Labels: **C** from bytes and `tests\test_status.py`, **L** until I play it.

> [!NOTE]
> **What I see.** STR, POW and END bars use a 125 scale (3 px a 5 points, base 100 = 60 px). The form bonus is a gold segment after the base part. With a bonus the number is "100+20"; with no bonus it is "100/100". HP and EP use the vanilla bars and text.

### 8.1 Parts

| Part | Where | What it does | Label |
|---|---|---|---|
| Entry stub | `@0x0800379C`, 16 bytes | `push {r7} ; ldr r7,=copy+1 ; mov r12,r7 ; pop {r7} ; bx r12`. Keeps r0-r7, sp and lr, so the dispatcher's arguments reach the copy | C |
| Page copy | `rom:0x86F93C`, 0x3A8 bytes, 4-aligned | The vanilla page and its pool. Every `ldr =` and `add rX,pc` reads the copied pool. Outside the splice, the copy equals the page except BL offsets | C |
| Long-call stubs | 18 x 16 bytes, `rom:0x86FCE4`-`rom:0x86FE03` | One per base target: the 17 page targets and the query `@0x08006E0A`. Same shape as the entry stub | C |
| Splice | copy +0x166 to +0x280 (vanilla `@0x08003902`-`@0x08003A1B`, the stat rows) | `ldr r0,[sp,#0xd8] ; ldr r1,[r0] ; add r0,sp,#0x9c ; bl stats ; mov r6,#0x57 ; add r7,sp,#0x9c ; b copy+0x280`, then zero fill. No branch outside the rows lands inside them | C |
| `find_player` | `rom:0x870064`; base stub `@0x080037AC` | Player pointer `@0x03001FA8`; else, if `[@0x03001D18]` != 0, message 7 to the suspended list through `@0x08006E0A`. The Europe method (`@0x080159FC` EU) | C |
| `width` | `rom:0x870080` | `min(v, 125) / 5 * 3` by subtraction (no divide) | C |
| `stats` | `rom:0x870092` | Per stat: label, number, base blit from the vanilla image, gold blit from the base end to the live end. Bonus = live - base, never below 0. Live is read only for the leader, as vanilla | C |
| Gold image | `rom:0x86FE0C`, 600 bytes raw | 75x8, rows `pal` 58 (248,248,168), 69 x4 (248,232,120), 34 x3 (200,160,64); index 0 in every third column, as the vanilla bar | C |
| Bonus format | `rom:0x86FE04` | `"%d+%d"` (base, bonus). The constant `BONUS_TEXT = "live"` builds `"%d"` (live) instead | C |
| Stat items | `@0x0800F4AA` (STR), `@0x0800F512` (POW), `@0x0800F57A` (END) | Each check is `bl @0x080037AC ; cmp r0,#0 ; beq ; bl @0x080086A2`: find_player, then reapply the form. An item used in the menu reapplies the form | C |
| +3 portrait literal | `rom:0x86FCD0` (copy pool) | The game reads this word, which holds the relocated appearance table. No code reads `rom:0x3B30` | C |

### 8.2 Behavior

| Case | Number | Bar (px from x 62) | Label |
|---|---|---|---|
| Base 100, no bonus | `100/100` | base 0-60 | C (test run) |
| Super Saiyan, base 100, live 110 | `100+10` | base 0-60, gold 60-66 | C (test run) |
| Super Saiyan 2, base 100, live 120 | `100+20` | base 0-60, gold 60-72 | C (test run) |
| Rage on base 30 (flat 100) | `30+70` | base 0-18, gold 18-60 | C (test run) |
| Not the leader, or no player found | `%d/100` | base only | C (test run) |
| Live below base | `%d/100` with base | base only | C (test run) |

The number text is right-aligned at x 136. "100+20" is 28 px wide and "100/100" is 34 px, so no bonus text is wider than the vanilla box (all bases 0-100, all live values to 255) (C).

### 8.3 Gold choice

The draft gold 82 is CIE76 delta E 15.4 from bar color 40 (248,184,0); 69 is 31.3 from 89 (248,216,0). Rows 58/69/34 are at least 29.9 from every bar color (8, 40, 43-47, 85-89, 112; the minimum is 34 against 40), and the light top and bronze foot make the segment read as a different material next to yellow (C, computed from `rom:0x1D4F50`). Mock: `scripts\one-time\2026-10-17-status-screen-research\mock_status_gold.png` (not game output).

### 8.4 Checks

- `tests\test_status.py`: veneer bytes; the base 8 MB differs only at `@0x0800379C`-`@0x080037BB` and the 3 item sites; relocated page integrity (every BL target through its stub, every other instruction and the pool); the splice; stubs keep r0-r7, sp and lr; the whole page runs in the test interpreter with the same calls as the vanilla page except the bar widths; widths at 0, 4, 5, 99, 100, 120, 125, 126, 127; gold, text and item behavior; palette unchanged.
- `scripts\one-time\2026-10-17-status-screen-research\listing_check.py`: against `status_usa_379c.txt`, outside the splice, 33 BL targets (through their stubs), 18 `ldr =` values and 4 `add rX,pc` strings agree. The one difference is `@0x08003A82 ldr r1,=`: `0x081D967C` in the listing, the relocated appearance table `0x08868FAC` in the copy.
- `scripts\one-time\2026-10-17-status-screen-research\r9_diff.py`: r9 equals r8 except the veneer site, the 3 item sites and the new data `rom:0x86F93C`-`rom:0x87017B`, which is 0xFF in r8.

> [!WARNING]
> **Open (L).** The resume routine `@0x08006FA4` frees the suspended list but does not clear `[@0x03001D18]`. `find_player` reads the list only when `[@0x03001FA8]` is 0, which is the menu case. The page draws 44 more stack bytes deep than vanilla. Both are not tested in game.
