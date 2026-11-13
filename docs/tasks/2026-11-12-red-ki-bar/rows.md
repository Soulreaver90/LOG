# Bible rows: the red ki bar

Merge with `merge_bible_rows.py rows.md RKB docs\tasks\2026-11-12-red-ki-bar\report.md`.
Add `RKB` = `docs\tasks\2026-11-12-red-ki-bar\report.md` to the source list in section 1.

## Section 5

| Fact | Tags | Label | Src | Id |
|---|---|---|---|---|
| Buu's Fury draws its second ki bar from a SECOND IMAGE at `0x08713FD8`, exactly `0x500` past the yellow one `0x08713AD8`. The two 0x500 buffers are byte equal everywhere except the 105 ki-row offsets, where the yellow ramp 26, 27, 28, 29, 30 becomes 107, 108, 4, 109, 110, five for five. On the BF OBJ palette `rom:0x5652C` that ramp is `#FF4200`, `#FF6300`, `#FF8400`, `#FFAD00`, `#FFD600`: ORANGE to amber, not red. It is therefore a second image, not a palette swap and not a second bar row | #palette #hud game:bf | C (`bf_second_bar.py`: 105 of 105 offsets differ, whole-block pair census) | RKB | |
| Three BF indices of the second bar ramp already map through `bf_hud.BF_TO_LOG2` (108 to `pal:32`, 109 to `pal:38`, 110 to `pal:37`, all used by the HUD frame); BF 4 and BF 107 have no entry, so `bf_hud.remap` would raise on the second image. A BF-faithful orange bar therefore needs two new `BF_TO_LOG2` entries | #palette #hud game:bf | C (table read, `bf_second_bar.py`) | RKB | |
| The LoG II OBJ palette `rom:0x1DA6C8` carries a red ramp that mirrors the HUD yellow five for five: `pal:41` `#989800`, `pal:40` `#C8C800`, `pal:46` `#F8F838`, `pal:131` `#E0E878`, `pal:123` `#E0F8C8` against `pal:25` `#D01028`, `pal:24` `#F81838`, `pal:31` `#F84848`, `pal:30` `#F87070`, `pal:29` `#F89090` (5 bit `v << 3`). All ten checked in a built ROM | #palette #hud | C (`check_ramp.py`) | RKB | |

## Section 6

| Fact | Tags | Label | Src | Id |
|---|---|---|---|---|
| From the red ki bar build `bf_ki_pool` accepts a THIRD form object, the ascended grade `@0x030021E8`, and hooks its vtable `0x0802526C` +4 (was the vanilla tick `@0x080171E5`) to `tick_ssj`. So appearance entries 10 (Super Vegeta `set:139`), 14 (Super Trunks `set:130`) and `vegeta_zplus`'s entry 23 (Z+) now drain the yellow pool at the Super Saiyan rate instead of the regular EP. Supersedes the KIR row "`@0x030021E8` (entries 10 and 14) is NOT a pool form" | #form #hud char:vegeta char:trunks | C (built trial ROM, vtable word and `pool_ref` listing; `test_bf_ki_pool.Ascended`) | RKB | |
| The pool bar colour is decided by the leader entry's FORM OBJECT, not by character. `pool_ref` writes RAM `0x03003A00` +0xE on every call: 1 (red) for `@0x030021E8` and ssj2_form's `@0x0888DE20`, 0 (yellow) for `@0x030021EC`, and 0 when there is no pool form, because `fullpower_hud`'s `hud_fp` enters `hud_draw` at `hud_key` without calling `pool_ref` and would otherwise inherit a stale red bar. `put_px` reads +0xE and adds `flag << 11` to the image base | #form #hud | C (listing, `test_bf_ki_pool.Ascended`, `RedHud`) | RKB | |
| **`@0x030021E8` is NOT unique to a second transformation.** In the r41 live table it is appearance entries 10 and 14, both reached in ONE step out of a BASE entry (9 `set:138` and 13 `set:129`, unlocked mid-scene by ext 73 (2, 138) and ext 73 (3, 129)), and in the Z+ trial also entry 23, reached out of entry 11, a Super Saiyan. No single entry field separates them: entries 10, 14 and 22 all carry +4 = +5, and entries 22 and 23 both revert straight to a base entry. The only exact rule is "some entry whose form object is not `@0x030021E0` transforms into me", which needs a table walk and a row count the table does not carry | #form #open char:vegeta char:trunks | C (live table walk of the Z+ trial ROM, `zplus_forms.py`) | RKB | |
| The red pool image is the yellow one with `pal:41, 40, 46, 131, 123` swapped for `pal:25, 24, 31, 30, 29`, written `0x800` past the yellow image in the same `bf_ki_pool` window. All 105 painted offsets differ between the two images, so a second transformation repaints every pool pixel | #hud #palette | C (`test_bf_ki_pool.RedHud.test_the_two_images_disagree_on_every_painted_pixel`) | RKB | |
| `bf_ki_pool`'s window grows from `0x824` to `0x1040` bytes with the red image (yellow `0x500`, pad to `0x800`, red `0x500`, code `0x338`, st46 blob `0x8`). The r39 `hud_key`-to-`put_px` pin in `fullpower_hud` moves from `f3cb6d1d5806eeea0f101eedfde389110f112f74` to `dbdff3fc1df989572fb3904e8edaf9809bc4402a`: the 37 instructions and every literal they resolve to are unchanged, and only 5 pc-relative `ldr` offsets differ, because the literal pool moved 8 bytes on | #hud #tool | C (`pin_probe.py`, instruction-for-instruction listing of both) | RKB | |
| Masters after the red ki bar: `build_list.txt` SHA-1 `bab496d8d56b0380aaef65c0fdf78933912ea0c0` (was `acf1b15f...`) and `build_list_dev.txt` `26e6ffc84dda6a0aa27d68d6635b987762d10e3a` (was `ffbd2bfc...`). Pins not updated | #tool #decision | C (`test_golden.py` run) | RKB | |

## Section 14

| Fact | Tags | Label | Src | Id |
|---|---|---|---|---|
| Buu's Fury HUD ki-row fill loops (`0x0800B99C`, decomp `slice_000158.s:24979`, `:25007`): `@0x0800BB98` paints steps 0 to b3-1 from the step table `0x08071F40` and the ORANGE image `0x08713FD8`; `@0x0800BBCC` paints b3 to b2-1 from the same step table and the YELLOW image `0x08713AD8`; `@0x0800BC02` paints b2 to b1-1 with the frame green (index 1) and `@0x0800BB74` clears the row first. b1 = ki `+0x1A`, b2 = pool `+0x1E`, b3 = pool `+0x20`, each x 41 / max ki, then b2 = max(b2, b3) at `@0x0800BB06` and b1 = max(b1, b2) at `@0x0800BB18`. So a Super Saiyan 3 bar is the whole row in orange and a Super Saiyan bar the whole row in yellow. Settles the HKS row "pixels below b3 from the orange image" with the two literals read from the ROM | #hud game:bf | C (`thumb_dis` listing of `0x0800BB8A`, both literals) | RKB | |
