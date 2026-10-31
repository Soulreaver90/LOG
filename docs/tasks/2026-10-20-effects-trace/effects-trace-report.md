# Effects trace: OBJ graphics that come through an object field

This study traces the 40 field-sourced OBJ VRAM users to their ROM graphics. It tests each graphic for `pal:172` and the runner-up `pal:86`. Build r21, `archive\builds\log2_poc_r21.gba`, SHA-1 `a3e9963aee85aef98d0bd013981f7deddf733fb2`. All work is read-only.

## Verdict

- **pal:172: LIKELY clean. No user blocks it.** No graphic that any of the 53 OBJ VRAM users can upload holds index 172. The label is C for 47 users and L for 6 users (see "What stays open", items 2 to 7). The brief forbids CONFIRMED while those paths stay untraced.
- **pal:86: used. It cannot be the runner-up.** Two independent sources show it (C for the pixels):
  - Map props: layout `0x08526BCC` (map 275 var 1, entry 1, 10 px) and layout `0x086A1998` (map 7 var 2, entry 10, 6 px), uploaded by `@0x080072C4`.
  - The script icon of ext op 130: frame `rom:0x6FF4D4`, four 16x16 frames with 4-5 px of index 86 each, uploaded by `@0x0801C4FA`.
- **The PSL "clean 10" list has other leaks** (C pixels): `pal:3`, `pal:7` and `pal:103` in area map frames; `pal:3` and `pal:7` in arrival marker text; `pal:3`, `pal:94` and `pal:216` in map props. I tested each graphic for 172 and 86 only. I did not test 174, 178 and 218 against every graphic.

## Method

1. I reconciled the user list. p7 lists 53 functions. 13 load their graphic by a ROM literal (p7 and p8 decoded them). 53 minus 13 gives the brief's 40. I decoded the 13 again as a check.
2. For each user I read the listing (`listings\<addr>.txt`) and named the field or argument that holds the source.
3. I found the writers of that field with two shapes:
   - Shape A: class-scoped store sweep (`e5_sweep.py`, functions of every vtable that holds the user, symbolic walk `esym.py`).
   - Shape B: base-relative vtable scan (`e10_vtscan.py`), pool-word loaders (`e11_poolrefs.py`), literal and constructor callers, and a global store census at the offset (`e6_global.py`).
4. I resolved each writer to ROM graphics and enumerated whole tables: layouts (`e3`, `e4`), items (`e7`), record lists and runs (`e8`, `e9`), the area map table (`e12`).
5. I decoded every graphic with the r21 bytes. Remap tables apply only on the `frame_upload` path (`frame_unpack_remap` has one caller), which the PSL census covers.
6. I checked the user list itself with five shapes in the code region and three in the r21 expansion area (`e14_usershapes.py`, `e13_expansion.py`).

## Counts per search shape

| Question | Shape A | Shape B | Reconciliation |
|---|---|---|---|
| OBJ VRAM users | literal `0x06010000`-`0x0601FFFF` (OBJ plus mirror): 53 | `mov #6 ; lsl #24`: 0; `mov #0xC0 ; lsl #19`: 0; literal `0x06000000`: 0; BL `obj_vram_alloc`: 47 | 18 alloc callers are in A. Each of the other 29 is a ctor or realloc of a class whose upload is an A user, or allocation only (`@0x080068A6`). Agree. |
| IWRAM code image `rom:0x7FD6BC` (0xE7C B, `e15_iwram.py`) | words `0x06010000`-`0x0601FFFF`, `0x06000000`, DMA3: 0 | ARM immediates in VRAM or IO range: 1 (`irq_handler` `0x03000824`, IO base `0x04000000`, no VRAM write); Thumb `mov #6 ; lsl #24`: 0 | No IWRAM routine writes OBJ VRAM. The two blitters there take the destination as an argument. Agree. |
| r21 expansion area | OBJ VRAM words: 0 | `mov #6 ; lsl #24`: 0; DMA3 words: 0 | 2 long-call words (frame_unpack, blit_b) belong to the status page copy, which writes BG VRAM only. Agree. |
| Vtables that hold `@0x08013D40` | codemap: 13 | base-relative scan: 14 | **Disagree.** `0x080241B0` (ctor `@0x08013E48`) is real and missing from codemap. Its writers (ctor `@0x08013E48`, tick `@0x08014008`, `@0x08014160`) use `0x086DEB6C` and `0x086E0B90`. Both are in the run set. |
| Other vtable memberships (24 more users scanned) | codemap | scan | Agree for 22. Scan-only hits `0x08025A28` (`@0x08016586`) and `0x08024E60`, `0x08024E64` (`@0x0801E432`) are artifacts: no code loads them. |
| Prop layouts | 336 layouts from the map table walk | 336 aligned words that point at them | Agree. 201 have props, 131 distinct sheets. |
| Writers of obj+0x4C (frame_vram_copy row) | class sweep | global census: 80 stores | Every store is `[actor+0x48]` + const. Agree. |
| scene+0x80AC (area map) | class sweep: none | loaders of pool words `0x8080` and `0x80B0`: 7 functions, walked | Only `area_map_ctor` `@0x08017A50` writes it (`@0x08017A94`). Agree. |

## Per-user summary

The full table with fields, writers and indices is `scripts\one-time\2026-10-20-effects-trace\effects_trace.txt` (one row per user).

| User | Graphic source | 172 | 86 | Label |
|---|---|---|---|---|
| `@0x080072C4`, `@0x08012EA4` map props | 131 layout sheets | no | **yes** | C (L on screen) |
| `@0x0800784C` sprite sets | PSL census sets | no | no | L |
| `@0x0800B7E6`, `@0x0800BAB4` dialog | portrait, box frames `rom:0x3EC9BC`, text colors `rom:0x3EC9B0` | no | no | C |
| `@0x0800EEA8`, `@0x0800FE2E` | read OBJ VRAM, write none | n/a | n/a | C |
| `@0x0800FC84` item icons | item table, 50 entries | no | no | C |
| `@0x08010124` number popup | glyphs, colors {1,4,5,39} | no | no | C |
| `@0x08010304` arrival markers | 22 records, colors {2-7,39} | no | no | C |
| `@0x08012A68`, `@0x08012AFE` script tiles | `rom:0x3B5CA8`, `rom:0x3B5CE8` | no | no | C |
| `@0x08013750`, `@0x08013B12`, `@0x08013D40` effect records | 6 lists and 22 record runs | no | no | C (L run bound) |
| `@0x080143A8`-`@0x08014556` beam, `@0x080157E0`-`@0x0801594C` blast | record runs | no | no | C |
| `@0x08016586`, `@0x08026044` spark | `rom:0x6F784C`, `rom:0x6F788C` | no | no | C |
| `@0x08016B12` orb | `rom:0x6F7914` 320 B | no | no | C |
| `@0x08016C48`, `@0x08016CAA` sparkle | IWRAM copy of `rom:0x7FE2D8` | no | no | C (L no RAM write) |
| `@0x08016D40`, `@0x08016DA2` area map arrows | `rom:0x6F7A4C`, `rom:0x6F7C4C` | no | no | C |
| `@0x08017ACC` area map | 18 frames of `visited_table` | no | no | C |
| `@0x08018398` menu sprite | `rom:0x6FE194`, portrait canvas copies | no | no | C (L canvas) |
| `@0x080187F0`, `@0x08018870` stat bar | `rom:0x6F86F4` | no | no | C |
| `@0x08019CA2`, `@0x08019DC2` gauges | generated {0,4} | no | no | C |
| `@0x08019ECE` blink icon | `rom:0x6F8D40`, `0x6FDD2C`, `0x6FDE2C` | no | no | C |
| `@0x0801A62A` menu label (`@0x0801A568` dead) | glyphs, colors {1,2} | no | no | C (L dead) |
| `@0x0801C4FA` script icon | `rom:0x6FF4D4` | no | **yes** | C (L on screen) |
| `@0x0801E432` sweep effect | `rom:0x7032D0` 1536 B | no | no | C |
| 13 literal users (HUD, `0x0800C8D8`, `0x080113A0`, raw tiles) | p8 literals, decoded again | no | no | C |

## What stays open

1. **pal:86 on screen (LIKELY).** Props start hidden (obj+0x10 = 0). A script message 4 shows them. I did not find which scripts show the two props. Ext op 130 has 35 call sites of one shape by a byte scan of the base ROM scripts, not a script walk. Both affect only 86, not 172.
2. **OBJ address built another way (SPECULATIVE risk).** A writer that builds the OBJ VRAM address from a RAM pointer, with no literal, no `mov` shape and no `obj_vram_alloc` call, is not seen by the five shapes.
3. **Sprite sets (LIKELY).** `@0x0800784C` uploads `[actor+0x48]` set frames. I assume every obj+0x48 is one of the 154 census sets, as the PSL census states. I did not trace every obj+0x48 writer.
4. **Record runs (LIKELY).** For `@0x08013D40`, the index is a direction (0-3) or a tick counter. I decoded every valid record of each run as a superset. An index that leaves its run is not excluded by a range proof.
5. **Sparkle tiles (LIKELY).** `0x03000C1C` holds the crt0 copy of `rom:0x7FE2D8`. No code literal writes that range. A store through a computed IWRAM pointer is not excluded.
6. **Portrait canvas in `@0x08018398` (LIKELY).** The 64x64 canvas copy holds only the 4096-byte portrait. The `@0x08019320` canvas had text before, but the code resets it to 64x64 before the unpack.
7. **Dead code (LIKELY).** `@0x080072FC`, `@0x08007318` and `@0x0801A568` have no reference by either shape. If one runs, its graphic is still clean for 172.

Open count: 7 (1 affects only pal:86; items 2 to 7 keep pal:172 at LIKELY for the users they name).

## Concerns for the census I ran

- `p8_dma.py` marks a frame unpacked to a RAM buffer as "not OBJ". That is how `rom:0x6FF4D4` (pal:86) passed the PSL. A guard for a new index must decode buffer-staged frames too.
- The codemap vtable list misses `0x080241B0`. A sweep that trusts codemap vtables alone misses its writers.
- `p8` read only the first 64 B of `rom:0x6F7914`. `@0x08016B12` uses 320 B (frames 0-4). The extra frames are clean.

## Files

- `scripts\one-time\2026-10-20-effects-trace\effects_trace.txt`: one row per user, the 13 re-check rows, and the shape counts.
- `scripts\one-time\2026-10-20-effects-trace\symbols_proposed.txt`: 62 functions and 12 data names in the `symbols.py` format. Four names already in `symbols.py` are kept out.
- `scripts\one-time\2026-10-20-effects-trace\bible_rows.md`: rows for sections 5, 9 and 14, tag EFX.
- Tools: `e0_codediff.py`, `e1_listings.py`, `eq.py`, `esym.py`, `e3_layouts.py`-`e14_usershapes.py`, each with a header and its output beside it.

## Symbols proposed

Main names (full list in `symbols_proposed.txt`): `map_prop_upload` `0x080072C4`, `record_upload` `0x08013D40`, `anim_effect_ctor` `0x080135E0`, `area_map_upload` `0x08017ACC`, `menu_sprite_upload` `0x08018398`, `script_icon_ctor` `0x0801C4B0`, `script_icon_oam` `0x0801C4FA`, `canvas_new` `0x08020E5C`, `canvas_blit` `0x08021344`, `dma_copy` `0x0801F412`, `memset8` `0x08021F18`, `blit_a_arm` `0x03000480`, `blit_b_arm` `0x03000348`, `vt_record_extra` `0x080241B0`, `script_icon_frame` `0x086FF4D4`.

