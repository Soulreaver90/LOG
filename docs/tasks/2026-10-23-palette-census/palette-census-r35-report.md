# OBJ palette census on r35: which of the 256 indices are never drawn

Brief: `docs\tasks\2026-10-23-palette-census\palette-census-r35.md`. Build read: r35 (`builds\log2_poc_r35.gba`, SHA-1 `736c778a1d576a86143d052e8af7847fd10bbf50`, asserted by every script). Scripts and outputs: `scripts\one-time\2026-10-23-palette-census\`. Read-only on every ROM, save and state.

Labels: **C** = CONFIRMED, **L** = LIKELY, **S** = SPECULATIVE.

---

## Result

| Index | Color now | Verdict on r35 | Note |
|---|---|---|---|
| `pal:174` | (32,232,120) green | **NEVER DRAWN**: C on the enumerated paths, L overall (7 open paths) | Free. Same ramp as 172 |
| `pal:178` | (32,248,120) green | **NEVER DRAWN**: C on the enumerated paths, L overall (7 open paths) | Free. Margin users: status twins (BG) and item menu art (BG) |
| `pal:218` | (32,32,248) blue | **NEVER DRAWN**: C on the enumerated paths, L overall (7 open paths) | Free |
| `pal:239` | (248,32,224) magenta | **NEVER DRAWN**: C on the enumerated paths, L overall (7 open paths) | New since r30. Free only while set 58 stays Super Perfect Cell |
| `pal:172` | (248,200,192) skin | **NEVER DRAWN today, but RESERVED** | `art\tables\palette.json` already sets it to the portrait skin. No live portrait uses it yet. Do not take it |

Every other index 1-255 (250 of them) is USED by at least one path. The full matrix, one row per index 1-255 with the first evidence per path, is `scripts\one-time\2026-10-23-palette-census\c7_final.txt`.

> [!IMPORTANT]
> "Never drawn" here means: no path that I could enumerate puts the index on the OBJ layer, and every save state agrees. Seven residual paths stay open (section "Residual risk"). They are the same kind of gap that the r21 work left open. None of them is closed by this study, so the honest label for the list as a whole is **C on the enumerated paths, L overall**. The one test that closes them is in "What would close it".

> [!WARNING]
> **Correction to the r21 starting list.** The brief's r21 candidates were 7, 103, 174, 178, 218. The EFX trace had already shown 7 and 103 used (area map frames, arrival marker text) on r21, so the true r21 list was 174, 178, 218. EFX tested each effect graphic for 172 and 86 only. This study tests all 256 indices on every graphic, and it finds more users for the old "clean 10": 3 (item 43 icon, orb, area map, props, arrival text), 103 (blast body record run `0x086E4560`, area map), 216 (item 43 icon, props). See the table below.

---

## Candidate table (each path, on r35)

Columns are the paths of the brief. "-" = no pixel of that index on that path. Counts are distinct graphics.

| Index | 1 Sets (154 live, remap) | 2 Dialog portraits (93 ids) | 3 HUD, icons, effects | 4 Tables (14) | 5 Props | 6 Text on OBJ | 7 States (21 distinct) | Verdict |
|---|---|---|---|---|---|---|---|---|
| 3 | - | - | item 43 icon, orb `rom:0x6F7914`, area map x3 | - | 9 prop entries | arrival marker color | not seen | USED (C) |
| 7 | - | - | area map records 36, 58 | - | - | arrival marker color | not seen | USED (C) |
| 86 | - | - | script icon `rom:0x6FF4D4` (ext 130) | - | layouts `0x08526BCC`, `0x086A1998` | - | not seen | USED (C) |
| 94 | - | - | - | - | 13 entries of layout `0x085C0814` (map 176.1) | - | OBJ VRAM in 10 states | USED (C) |
| 103 | - | - | blast body run `0x086E4560` (28), area map x2 | - | - | - | not seen | USED (C) |
| 172 | - | - | - | - (closure only) | - | - | not seen | NEVER DRAWN, reserved |
| 174 | - | - | - | - | - | - | not seen | **NEVER DRAWN** |
| 177 | - | - | ability icons 0 and 10 | - | - | - | not seen | USED (C) |
| 178 | - | - | - | - | - | - | not seen | **NEVER DRAWN** |
| 216 | - | - | item 43 icon | - | 10 prop entries | - | not seen | USED (C) |
| 218 | - | - | - | - | - | - | not seen | **NEVER DRAWN** |
| 239 | - (vanilla set 58 only, dead) | - | - | - | - | - | not seen | **NEVER DRAWN** |
| 240 | - (vanilla set 58 only, dead) | - | item 33 icon, orb, run `0x08703158`, raw `rom:0x701E58` | - | 1 prop entry | - | not seen | USED (C) |

Evidence files: `c1_sets.txt`, `c2_tables.txt`, `c3_portraits.txt`, `c4_effects.txt` (with `c4_effects.json` for every graphic tag), `c6_states.txt`, `c7_final.txt`.

**Margin hits for the free four** (no OBJ reader found; listed so the gap is visible):

| Index | Margin source | Why it is not an OBJ use | Label |
|---|---|---|---|
| 178 | Status twin portraits 8-10, 12, 13, 15, 19-25 | Twins use the BG palette; no reader passes a twin id (below) | C (shapes), S (run-time id) |
| 178 | Item menu art +0x28/+0x2C of items 5-7, 27, 37, 40, 41, 43, 45 | All three readers SSM names unpack it to a canvas and blit it with `@0x080211C8`: `@0x080044C6` (+0x2C) and `@0x08004546` (+0x28) in `@0x080043F6`, and `@0x0800480E` (+0x2C) in `@0x08004788` (vtable `0x08023DDC`), whose canvas goes to BG VRAM `0x0600B0C0`. The character menu runs with DISPCNT `0x0E00` (OBJ off, SSM) | L |
| 239 | Vanilla armor Rage set 58 (header `rom:0x2AB508`, 129 frames) | Named only by the dead vanilla table word `rom:0x3B4F5C`; 0 aligned words equal `0x083B4E90`; no state RAM holds `0x082AB508` | C |
| 239 | Status twins 19, 20; item menu art of items 8-10, 19, 23 | As for 178 | C / L |
| 172, 174, 218 | BG palette DMAs and BG unpacks found by the p8 tracker | Destinations are BG VRAM or palette RAM (for example `@0x0801D3A4` and `@0x0801D496` blit to `0x06000080` and `0x06008080`) | C |

---

## Path 1. Sprite sets (C)

Three shapes, reconciled (`c1_sets.py`, `c1b_setids.py`):

| Shape | Count | Reconciliation |
|---|---|---|
| A: live set table (word `rom:0x959C` = `0x0888D9EC`), ids 7-160 | 154 sets, 14,384 records, 6,521 distinct frames, all decoded (fail closed; type 0 sizes checked) | Every record is 8bpp; every frame size equals w x h |
| B: every aligned 12-byte record shape in the whole 16 MB | 6,650 distinct frames | 6,521 = all of A. The 129 extra frames are all the vanilla armor Rage set 58 (`rom:0x2AB508`) |
| C: aligned words that point at a set-header shape | 155 headers | 154 = A, plus `rom:0x2AB508` named only by `rom:0x3B4F5C` (vanilla table, dead: no word equals `0x083B4E90`) |

- **Readers by id (C):** script set args (shape A 85 ids, shape B 95 ids, rom `0x3B5000-0x420000` and `0x880000-0x910000`), 1,108 map object fields, appearance +1 (live `rom:0x88DC54` and copy `rom:0x800000`), scouter +8. Every id is 0-160. Shape B also returns 168, 192, 200, 208, 224: all in map data bytes (`rom:0x3ED857`-`0x405083`), and each resolves to a non-ROM word, so they cannot draw a set.
- **Remap (C):** 41 sets have word +8 (41 distinct tables). Displayed index = remap[byte].
- **r30 set 58 (C):** Super Perfect Cell, header `rom:0x908D54`, 176 records, 28 indices. It replaced the armor Rage set, so `pal:239` and `pal:240` lost their set user (240 keeps effect users).
- Result: 187 displayed indices.

## Path 2. Dialog portraits (C), status portraits out of scope (C)

- Live block `rom:0x894EAC` (word `rom:0xBE10`): 122 words, ids 0-121; word 122 is not a ROM address. 93 dialog ids decoded, each 4096 bytes (`c3_portraits.py`).
- Word 52 = word 40 = slot `rom:0xF28140` (the r30 alias). The `art_inject` slots 40, 52, 63, 65, 106, 115, 117, 119 decode to full size.
- Readers: 1,636 named, text-valid cutscene records (93 ids), appearance +2, scouter +0xC, hook outputs 115, 117, 119. No reader names an id above 121. Every dialog id 26-121 is decoded anyway (superset).
- The SPC row counts 2,030 live records with another walk. The difference does not hide a twin id: the check also ran over the 299 named records that fail the text test, and their twin ids (8, 25) are map-data words, listed in `c3_portraits.txt`.
- **Status twins (ids 8-25, 116, 118, 120) are BG, not OBJ (C):** no text-valid record, no appearance +2 and no scouter +0xC names one. Appearance +3 has no reader in the patched ROM (SGR row). The status page draws into a canvas copied to BG VRAM `0x06006940` (RSS row), and `status_portrait` paints dialog-id pixels into BG palette slots (pool word `rom:0x89A558` = `0x05000000`, unchanged). The page indices are therefore a subset of the dialog indices. The only twin-id hits are map-data words (`0x08010099` read as "seq 153, type 1, portrait 8") and the noisy byte shape B.
- Dead frames (vanilla 52 hooded face `rom:0x6BAF30`, vanilla 40, vanilla 65) hold no index outside the dialog set.
- Result: 183 indices. The free four and 172 are not among them.

## Path 3. HUD, icons, effects, OBJ VRAM writers (C, with the EFX limits)

- Graphics re-read on r35 (`c4_effects.py`): HUD frame `rom:0x6D7B54`, EXP blink colors, bar fill, the ability icon words (14 x 2), Z2 icons (pool `rom:0x88E3C4`, `0x88E3C8`), 50 items (+0x14, +0x24: 97 of 100 decode; the other 3 are null words, item 28 both and item 45 +0x14; a non-null word that is not a frame stops the run), 7 record lists, the orb span, 22 record-run bases (264 records), 16 area map OBJ frames, 16 raw tiles, 4 literal frames, 4 dialog box frames, area map arrows, and the p8 register tracker re-run on r35 (65 events, 9 to OBJ). Result: 218 indices.
- **No new writer in r22-r35 (C), two shapes** (`c5_writers.txt`, `c0_diff.txt`):
  - Byte diff r21 to r35 in the code region: 22 bytes, all at `@0x08003ED4` (appearance_revert hook) and 4 vtable words (`rom:0x24BA4`, `0x24C5C`, `0x254D8`, `0x25A88`). None is inside an OBJ writer. Code shapes on r35: A' 53, B 0, C 0, D 0, E 47 (29 E-only), the same as r21.
  - Expansion and art region: 4 VRAM/palette words, all r21 status-page words (BG VRAM `0x0600E000`, `0x06006940`, `0x0600B0C0`, BG palette `0x05000000`); 0 `mov #5/#6/#7 ; lsl #24`, 0 `mov #0xC0 ; lsl #19`, 0 `swi 0x0B/0x0C`; 0 long-call words to `obj_set_table`, `frame_upload`, `frame_unpack_remap`, `obj_vram_alloc`. New long-call words: `0x0800185D` (a compared return address), `0x0800833F` and `0x080134F3` (vanilla tails), and `0x0800021D` inside script record bytes (`rom:0x89ADA8`, post-Cell record copy).
  - Disassembly of every new code block (`rom:0x89A788`, `0x89A81C`, `0x89A8B0`, `0x908ED0`): no BL to base code, only `bx` to known ticks; the only ROM data word is the set 58 header for a compare.
- The area map has 16 OBJ frames, not 18 as the EFX bible row says (`e12_areamap.txt` on r21 also lists 16).

## Path 4. Remap and tint tables (C)

- Callers on r35: 9 BL to `obj_set_table` `@0x080076EE` (the r21 nine), 1 BL to `frame_unpack_remap` (`@0x080077F0`), 0 long-call words to either (`c2_tables.txt`).
- Tables: the 14 blocks at `rom:0x6D0DD0`-`0x6D1BCF` and the 14 tables the 5 word lists plus the dim and gray literals name are the same 14. Two stray words point into the block at non-table offsets (`rom:0x387E40`, `0x5D98B0`, graphics bytes).
- Rule `T[remap[i]]`, every table on every displayed set index (superset of the real states): 52 more indices become USED. None of 172, 174, 178, 218, 239 is an output.
- Closure margin (two table steps, not a game path): adds 92 and 172 only.

## Path 5. Map props (C pixels, L on screen)

336 layouts, 201 with props, 710 entries; displayed spans counted, whole sheets kept as a margin. Props show 3, 86, 94, 216, 240 among the old candidates. No sheet byte of 172, 174, 178, 218 or 239.

## Path 6. Text and fills on OBJ (C)

Dialog text table `rom:0x3EC9B0` = {2, 9-15, 1}; number popup {1, 4, 5, 39}; arrival markers (22 records) {2-7, 39} with shadow 1; menu label {1, 2}; `0x0800C8D8` {1, 2}; `0x080113A0` {39, 2}; gauges {4}. Glyphs are bits only.

## Path 7. Save states (proves use only)

- 117 files (109 `builds`, 4 `builds\mockups\2026-10-21-rage-music`, 4 `data\roms`), **21 distinct states** after SHA-1 dedupe (7 groups of byte copies, for example r27-r35 `.ss4`/`.ss5`).
- Areas (map info `@0x03002080` zone, area): 0,0 (title, file select, debug) x4; 1,4 x3; 2,22 x1; 6,99 x1; 9,1 x1; 14,1 x2; 14,3 x9.
- On-screen OAM tiles hold 118 indices; whole OBJ VRAM 161. Every one of them is in the static USED union (`c7_final.txt`: 0 outside). None of the free four or 172 appears on screen or in OBJ VRAM.
- This cannot prove non-use: 21 states in 7 areas.

---

## Residual risk (not closed)

| # | Path | Effect on the free four | What would close it | Label |
|---|---|---|---|---|
| 1 | A set id built at run time (ext 73 or another op with a computed arg) | An id 161+ would read the appearance table bytes as a header | A trace of every ext op set arg in the interpreter | S |
| 2 | An OBJ VRAM address built without a literal, `mov` shape or `obj_vram_alloc` (EFX open 2) | Any graphic | An emulator write watch on `0x06010000-0x06017FFF` | S |
| 3 | A table stored to obj+0x24 by code other than `obj_set_table` | Any table output | A store census at +0x24 in the frame_upload classes | L |
| 4 | Record runs: an index that leaves its run (EFX open 4) | Run neighbors only | Range proofs per tick | L |
| 5 | Sparkle IWRAM copy and the portrait canvas (EFX open 5, 6) | Low | RAM write watch | L |
| 6 | Item menu art +0x28/+0x2C reaching OBJ outside the character menu | 178, 239 | A store census of item pointers into OBJ classes | L |
| 7 | IRQ handler RAM vectors (not traced) | Any | Trace of the vectors | S |

**What would close it (proposal, not built here):** a scratch copy of r35 with 174, 178, 218, 239 set to a loud color (for example pure white) in both palette copies (`rom:0x1DA6C8` + 2i and `rom:0x3ECBA4` + 3 x (256 + i)), played through a fight with a hold special, a Super Saiyan transform, the item menu, the area map, the scouter, and a few prop maps. Any visible loud pixel names a missed path.

## Notes for the recolor

- Use `inject.py palette` (both copies). `art_tables` accepts a portrait color only if a vanilla dialog portrait uses it or the palette table sets it, so the new index must be in `art\tables\palette.json` first.
- 239 is free only because r30 replaced live set 58. If set 58 ever returns to the armor Rage art, 239 is used again.
- Dialog portraits never pass through a remap table, so the dim and tint tables do not affect a portrait-only color.

## Files

- `scripts\one-time\2026-10-23-palette-census\cc.py` (shared, fail-closed decode), `c0_diff.py` (r21 to r35 byte runs), `c1_sets.py`, `c1b_setids.py`, `c2_tables.py`, `c3_portraits.py`, `c4_effects.py`, `c5_writers.py`, `c6_states.py`, `c7_final.py`; each writes its `.txt` (and `.json` for the matrix).
- `scripts\one-time\2026-10-23-palette-census\bible_rows.md`: rows for section 5, tag PCN.
