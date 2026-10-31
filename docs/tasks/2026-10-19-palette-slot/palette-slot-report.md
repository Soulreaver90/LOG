# Palette slot study: a free OBJ index for the portrait skin #F8E0D0

Brief: `docs\tasks\2026-10-19-palette-slot\palette-slot.md`. Build read: r21 (`archive\builds\log2_poc_r21.gba`, SHA-1 `a3e9963aee85aef98d0bd013981f7deddf733fb2`, checked). Scripts and outputs: `scratch\rom-copies\palslot\`.

Labels: **C** = CONFIRMED, **L** = LIKELY, **S** = SPECULATIVE.

---

## Result

| Item | Value |
|---|---|
| Recommended index | **`pal:172`**, now (32,208,168), becomes (248,224,208) = BGR555 `0x6B9F` |
| Runner-up | **`pal:86`**, now (128,32,248), a different color family |
| Test copy to play | `scratch\rom-copies\palslot\log2_poc_r21_pal172.gba`, SHA-1 `4cb9bf139ca0478d2d62e36d61577d594adba331` |
| Brief-verbatim copy | `scratch\rom-copies\palslot\log2_poc_r21_pal172_objonly.gba`, SHA-1 `adb20582d029bab895f1ad3c1f777b4da017c6c9` |
| Second finding | Five sprite state ticks apply 12 more remap tables (`rom:0x6D0FD0`-`0x6D1AD0`) to live sprites. They map set colors onto 19 of the 29 indices that look free by pixels alone, including the first pick 126 (C). |
| Main finding | The field does not show `rom:0x1DA6C8` directly. Every fade in rewrites all 512 palette RAM words from a second copy, the RGB table `rom:0x3ECBA4`. A new color needs both copies changed (C). |

> [!WARNING]
> The brief asks for a copy with only the `rom:0x1DA6C8` entry changed. That copy is built, but it is not a valid play test. In the field the first fade in (map change, menu close, Continue) writes the old color back. I deviated: the copy to play changes the RGB table entry too. See Q1 and Q5.

---

## Q1. How the OBJ palette reaches palette RAM

The game has two ROM sources for OBJ palette RAM. Which one is live depends on the screen.

**Writers, two shapes reconciled (C).** Shape A: code literal `0x05000200`, 7 pool words in 9 functions. Shape B: `mov rX,#5 ; lsl rX,rX,#24`, 14 functions (equals the SSM count). The union is 16 functions; 7 are in both. Extra shapes found nothing: 0 `swi 0x0B`/`0x0C`, 0 ARM immediates in the palette range, 0 DMA0-2 register literals, 0 shape-B pairs in the r21 expansion code (`p1_refs.txt`, `p2_shapes.txt`).

| Function | Source | Entries | When |
|---|---|---|---|
| `@0x080005A4` title_enter | `rom:0x1DA6C8` DMA | OBJ 256 | Title |
| `@0x08009BE4` ext 45 | `rom:0x1DA6C8` DMA | OBJ 256 | A script op |
| `@0x08010BCE` party screen (`@0x08011058`) | menu palette, then `rom:0x1DA6C8` | BG 256, OBJ 256 | Party screen |
| `@0x080174EA`, `@0x08019934` | `rom:0x1DA4C8`, then `rom:0x1DA6C8` | BG 256, OBJ 256 | Menu scenes (Select, R) |
| `@0x0800BE14` | **RGB table `rom:0x3ECBA4`**, blended to a target color | BG 256, OBJ 256 | Fade in, fade out, colored fade |
| `@0x0800DA96`, `@0x0800DB18` | Palette RAM snapshot (`@0x0800DA68`) | 512 | Fade to black, flash to white (ext 42) |
| `@0x08005F1A` | Zero fill | 512 | Blackout before a fade |

The other six are BG only: `@0x080002F8`, `@0x08000B3C`, `@0x0801A39C`, `@0x0801D3A4`, `@0x0801EDFA` (256 each) and `@0x0801F878` (16, assert screen).

**The RGB table (C).** `@0x0800BE14` loads `ldr r4,=0x083ecba4` (`@0x0800BE1C`), then for 0x200 entries writes `strh r3,[r2,#0x0]` from `0x05000000` upward (`@0x0800BE60`). Each word is built from three 8-bit table bytes: channel = (table x (256 - r3) + target x r3) >> 11. The table's OBJ half equals `rom:0x1DA6C8` for 255 of 256 entries; only index 0 differs (black, ROM magenta). Its BG half equals `rom:0x1DA4C8` 256 of 256 (`p0_rgbtable.py`).

**Who calls it (C code, L names).** Fade in `@0x0800BE84` ends with r3 = 0, so palette RAM then equals the table exactly. Builders of these fade objects: the warp `@0x0800C1AC` (fade out `@0x0800C84C`, `map_load`, fade in), `@0x0800C88A`, `menu_buttons` (return from Start, Select, R), Continue `@0x0800180C`, `debug_level`, ext 38, `@0x080109EC`, `@0x0801915C`. Ext 135 (`@0x0801D348`) makes a colored fade from the same table.

**Runtime proof (C).** Every field capture holds OBJ palette RAM equal to the RGB table, 256 of 256, and differs from `rom:0x1DA6C8` at 0 and 168. That covers base ss1, ss2 and r18-r21 ss2, ss3. Title, file select and debug captures equal `rom:0x1DA6C8` (`p3_states.txt`). This also explains the bible's "entries 0 and 168 set at run time": `@0x0800BE14` writes black at 0 and drops bit 15 of 168.

**Partial rewrites (C for the two shapes).** No writer touches part of the OBJ palette. Nothing reloads sprite banks per actor or per map, and `map_load` writes no palette. Forms and auras use pixels, not palette writes. Fades and flashes rewrite all 512 words.

**Dialog open (C).** The dialog box `@0x0800B1E2` and the portrait upload (`@0x0800BAB4`, VRAM copy `@0x0800BB44`) write no palette: neither is in the 16-function union. A portrait shows in whatever OBJ palette RAM holds.

**Color effects are remaps, not palette writes (C).** Sprite tints change the pixel indices, not the palette. `obj_set_table` `@0x080076EE` sets obj+0x24 = T[set remap[i]], and `frame_upload` unpacks through it (`@0x0801F3BA`, its only caller). The tables T: dim, gray, and 12 tables at `rom:0x6D0FD0`-`0x6D1AD0` that five state ticks pick from word lists (Q3).

## Q2. Banks while a dialog portrait shows

Banks do not matter in this game. **Every OBJ is 8bpp (C):**
- All 14,412 records of the 154 live r21 sets have attr0 bit 13 set.
- The HUD OAM attr0 words are `0x6000`, `0x2000` and `0x6000` (`@0x08008BF8`-`@0x08008C3A`).
- The 29 captures show 0 4bpp OBJ.

So no bank is reloaded or kept as a unit. During a field dialog or a cutscene, all 256 OBJ entries are the RGB table copy from the last fade in. The exception is a script that ran ext 45: that writes the `rom:0x1DA6C8` values until the next fade (L, which scripts use ext 45 is not traced). I found no separate battle scene: combat runs in the field, and the boss HP bar is a field object made by ext 85 (L, bible s8 CFS row).

## Q3. Candidates

The e8 list has 73 indices that no vanilla dialog portrait uses. I re-ran the census on r21 through the live tables (`p4_census.txt`, `p6_remap.txt`).

| Step | Removes | Evidence |
|---|---|---|
| Dialog portraits, live block `rom:0x894EAC`, 93 ids incl. 63, 65, 106, 115, 117, 119, 121 | none (the remaster art adds none of the 73) | C |
| Index 0 (transparent) | 0 | C |
| 154 live sets, every record unpacked; remap applied for the 41 sets with word +8 | 4, 6, 47, 51, 54, 61, 85, 87, **88**, 101, 104, 109, 125, 134, 136, 150, 154, 166, 171, 176, 199, 202, 210, 214, 219, 222, 226, 227, 231, 234, 236-240, 251 | C |
| HUD frame `rom:0x6D7B54` (raw 0x300), bar colors, ability icons, Z2 icons `rom:0x88DE3C` | 60, 61, 62, 173, 177, 201 | C |
| Dim table on playable sets (file select, party screen) | 235 (239 to 235), 246 (107 to 246) | C |
| State tint tables (below), applied to the displayed index of every set | 53, 59, 82, 83, 93, 102, 108, **126**, 127, 145, 147, 148, 151, 157, 162, 164, 175, 179, 180 | C (tables, callers), L (which actors enter those states) |

**The state tint tables (C).** `obj_set_table` has 9 callers (`p10_tables.txt`). Four are menu callers: gray in the file select and the party screen, dim through the menu sprite. Five are state ticks that index a word list of remap tables:

| Tick | Word list | Tables | Reached from |
|---|---|---|---|
| `@0x08010104` | `rom:0x6D0DC4` | `rom:0x6D0FD0`, `0x6D10D0`, `0x6D11D0` | ROM word `rom:0xB2020` |
| `@0x080106F8` | `rom:0x6D75F8` | 9 words, tables `0x6D12D0`-`0x6D16D0` | vtable `0x08024BC8`, built by `@0x08008390` (L: player code) |
| `@0x08010730` | `rom:0x6D760C` | 4 words, tables `0x6D13D0`-`0x6D16D0` | vtable `0x08024A3C`, built by `hold_special_tick` and `@0x0801BC84`, `@0x0801BCAC` |
| `@0x08018FA4` | `rom:0x6FD4D8` | 8 words, tables `0x6D17D0`-`0x6D1AD0` | vtable `0x08024A28`, built by `@0x08018F4E` |
| `@0x0801A078` | `rom:0x6FDFBC` | 3 words, tables `0x6D13D0`-`0x6D16D0` | vtable `0x08024A14`, built by `@0x0801B8C0`, `@0x0801C5A8` |

These are LIKELY glow and tint cycles; `hold_special_tick` is one builder. Example: table `rom:0x6D13D0` maps 130 to 126, and `set:112` shows 130 (674 px). With 126 as skin, that tint would flash skin-pink. I applied every table to every set (conservative), so the filter is a superset of the real use.

**10 indices stay clean** (`p11_final.txt`): 3, 7, 86, 94, 103, 172, 174, 178, 216, 218.

> [!NOTE]
> `pal:88` is in the e8 list, but Piccolo and all four gi sets use it heavily. The e8 list is portrait-only. Do not take an index from it without the sprite check.

**Extra checks on the 10 (C):**
- None appears on screen in any of the 29 captures (`p3_states.txt`).
- None is a gray table output. Gray outputs are only 1, 2, 9-15, 43 and 211.
- The raw effect tiles that code DMAs by literal use none of them (`p8_dma.txt`). These are `rom:0x6AF644`, `0x6D87F0`, `0x6D883C`, `0x6F7914` and `0x701E58`.

**What the census cannot see (L):**
- An effect graphic that reaches OBJ VRAM only through an object field or an argument, not a literal. 40 OBJ VRAM users exist (`p7_objsrc.txt`). Most read their source from a field.
- The broad ROM scan of 13,174 frame headers (`p5_romscan.txt`) is noise for this question. The hits for these indices lie in map tile chunks (0x800, 0x2000, 0x4000 bytes), full-screen BG art (0x9600) or menu BG frames. All of these use BG palettes.

**Choice: `pal:172`.** All 10 indices pass every check, so the tie-break is the old color. `pal:172` (32,208,168) is the nearest of the 10 to #F8E0D0 (weighted distance 99,136). All 10 are far from skin, so a missed user would show plainly. Runner-up `pal:86` (128,32,248), distance 181,056. I skipped 174 and 178 although they are nearer: they are in the same 171-180 ramp as 172, so a missed user of that ramp would hit all three.

## Q4. The status page

`status_portrait` paint (r21 code `rom:0x89A4D0`) maps by index and copies the color by value from ROM (C):

```
lsl r0,r7,#1
ldr r2,=OBJ_PAL          ; r21 pool rom:0x89A554 = 0x081DA6C8
add r2,r2,r0
ldrh r0,[r2,#0x0]        ; dialog color: OBJ palette entry
...
strh r0,[r1,#0x0]        ; BG palette RAM 0x05000000 + 2 x slot (pool rom:0x89A558)
```

- A changed `rom:0x1DA6C8` entry reaches the status page with **no code change**. Paint never reads palette RAM or the RGB table, so the field fades do not affect it.
- The 64-slot pool is the only limit. The r21 remaster portraits use 18-35 distinct indices (63: 23, 65: 22, 106: 35, 115: 24, 117: 24, 119: 18, 121: 20). The vanilla maximum is id 27 with 64, and id 27 does not use 172. One more index fits.

## Q5. Fades

Two kinds of fade exist. They give different answers.

| Fade | Source | Changed `rom:0x1DA6C8` only | Both entries changed |
|---|---|---|---|
| `@0x0800BE14` (map change, menu close, Continue, ext 135) | RGB table `rom:0x3ECBA4` | **Wrong**: fades to the old color and stays there | Correct |
| `@0x0800DA96`, `@0x0800DB18` (ext 42 flash; snapshot users `@0x0801079C`, `@0x0802664C`) | Palette RAM snapshot | Correct if RAM held the new color | Correct |

(C, code; L, in game.)

---

## Test copies and diff proof

`p9_testcopy.py` checks the r21 SHA-1 and the old bytes, writes only into `scratch\rom-copies\palslot\`, and refuses to overwrite. `cmp -l` against r21 agrees (`p9_testcopy.txt`).

| Copy | SHA-1 | Differing bytes |
|---|---|---|
| `log2_poc_r21_pal172.gba` (play this) | `4cb9bf139ca0478d2d62e36d61577d594adba331` | `rom:0x1DA820` `44 57` to `9F 6B`; `rom:0x3ED0A8` `20 D0 A8` to `F8 E0 D0` (5 bytes) |
| `log2_poc_r21_pal172_objonly.gba` (brief verbatim) | `adb20582d029bab895f1ad3c1f777b4da017c6c9` | `rom:0x1DA820` `44 57` to `9F 6B` (2 bytes) |

The header checksum covers `0xA0`-`0xBC` only, so no fix is needed. The first pick 126 had copies too. I deleted them after the tint table check removed 126.

**What to check in mGBA:**
1. Load `log2_poc_r21_pal172.gba`, continue into the field, and change maps once (any exit).
2. Open Tools > Palette view. OBJ entry 172 must read (248,224,208).
3. With the objonly copy, the same entry reads (32,208,168) after the map change. That proves the second write is needed.
4. No graphic uses index 172 today, so nothing on screen may change. Use a hold special and a few attacks too: the tint states are the nearest risk. Any visible change means the census missed a user. Report it.

## Proposed patch (not written to `scripts\permanent\`)

`patches\portrait_skin.py`, `apply(rom, alloc)`:
- Expect `rom:0x1DA820` = `44 57` and `rom:0x3ED0A8` = `20 D0 A8`. Raise on any other bytes.
- Write `9F 6B` and `F8 E0 D0`. Assert that each RGB888 channel >> 3 equals the BGR555 channel.
- No allocation, so its build position does not move other patches. List it **before** `portrait_remaster`. That patch checks each PNG color against `rom:0x1DA6C8`, so it must see the new value.
- In `portrait_remaster`, allow 172 as the one index outside the vanilla dialog set. Today it refuses any index no vanilla dialog portrait uses.
- Test: no live set frame (set remap applied) shows 172; no dim, gray or state tint table maps a displayed set index to 172; no HUD frame, icon or non-remaster dialog portrait uses 172; both entries are written. `p11_final.py` is the model for the guard.

## Risks

- **Effects through object fields (L).** About 40 OBJ VRAM users take their graphic from a field. A missed effect that uses 172 would turn skin-pink. The mGBA check in step 4 above is the cheapest catch.
- **Remap tables reached another way (L).** I found the tint tables through the 9 callers of `obj_set_table`. A table stored to obj+0x24 by other code would not be seen.
- **Future sprite use (C).** `dim[172]` = 169 (32,184,120), green. If a gi sprite later uses 172, the file select would dim it to green. Then change `rom:0x6D0F7C` too (dim table entry 172). The tint tables would also need a check for 172 as an input.
- **Ext 45 screens (L).** Scripts that run ext 45 load `rom:0x1DA6C8`. With both entries changed, both sources agree, so this is safe.
- **The objonly copy (C).** It must not be the play test. It shows the new color only on the title, file select and menu scenes.
- **The bible rows (C).** The bible says "entries 0 and 168 set at run time" (s5) and "the ROM value is the displayed color" (SSM, s5). Both are explained, not wrong: the field color comes from the RGB table. The new rows say so.

## Files

- `scripts\one-time\2026-10-19-palette-slot\p0_rgbtable.py`: RGB table vs palettes.
- `p1_refs.py` and `.txt`: shape A, literal census.
- `p2_shapes.py` and `.txt`: shapes B, C, D.
- `p3_states.py` and `.txt`: 29 captures.
- `p4_census.py` and `.txt`: sets, portraits, dim and gray tables, HUD.
- `p5_romscan.py` and `.txt`: broad header scan (noise, see Q3).
- `p6_remap.py` and `.txt`: remap sets, dim and gray on playable sets.
- `p7_objsrc.py` and `.txt`: OBJ VRAM users.
- `p8_dma.py` and `.txt`: DMA and unpack source tracker.
- `p9_testcopy.py` and `.txt`: the test copies.
- `p10_tables.py` and `.txt`: the state tint tables.
- `p11_final.py` and `.txt`: the final filter and ranking.
- `bible_rows.md`: rows for sections 5, 5a, 5b and 14, tag `PSL`.
