# Bible rows earned by 2026-11-07 set table reader, tag RDR

Merge with:
`py -3.14 -I scripts\one-time\2026-10-16-first-probes\merge_bible_rows.py docs\tasks\2026-11-07-set-table-reader\rows.md RDR <report path>`

## Section 4

| Fact | Tags | Conf | Src |
|---|---|---|---|
| Three readers resolved a sprite set id through the BASE constant `rom:0x3B4E90` instead of the live table literal `rom:0x959C`: `webfoot_decompress.cmd_set`, `log2_sprites._main export` and `art\gi_aura._layout_rows`. On `log2_poc_r41_arena_v7.gba` that read one WRONG set, `set:58` (vanilla `@0x082AB508` against live `@0x08908D54`, the `superperfect_cell` repaint), and `set:157` raised `TypeError` because the word past the vanilla table is not a ROM address. The reader said nothing: it returned vanilla art and looked correct. Fixed by `webfoot_decompress.set_table(rom)` and `set_offset(rom, id)` | #sprite #tool set:58 set:157 | C (measured on the ROM before and after) | RDR |
| A forward walk of a build's live set table that stops at the first non-ROM word counts 155 entries, one more than the 154 words `gohan_gi` writes (ids 7-160). The extra word is the first word of the appearance table copy, which starts right after the set table, not a set. So id 161 does not exist | #sprite | C (`log2_poc_r41_arena_v7.gba`: table `rom:0x88D9EC` + 154 x 4 = `rom:0x88DC54`, the appearance copy named in the SPC row) | RDR |
| `gohan_gi.py` lines 97, 111 and 130 read `SET_TABLE` ON PURPOSE and must keep doing so: line 97 checks that the literal still names the vanilla table, line 111 lays the new sets out from vanilla `set:56`, `set:58` and `set:59`, and line 130 copies the vanilla table. So "every patch resolves through `rom:0x959C`" is not literally true | #sprite #decision | C (code) | RDR |

## Section 7

| Fact | Tags | Conf | Src |
|---|---|---|---|
| `log2_save.py` holds five table addresses, but its CODE reads only one from the ROM: `QUEST_TABLE @0x086D68DC` (line 336, the journal). The default character records `@0x081D9548`, the visited table `@0x086F6D8C`, the scouter table `@0x086F8E40` and the item table `@0x086ADE24` appear in COMMENTS only, so they document the save layout and no reader can go stale on them today | #save #tool | C (code) | RDR |
| None of the `log2_save.py` tables moves on a build. Literal sites in the base ROM, all still holding the same value in a dev master build and in `log2_poc_r41_arena_v7.gba`: `rom:0x1D9548` 1 site (`@0x08003EA0`), `rom:0x6F6D8C` 2 (`@0x08004158`, `@0x08004210`), `rom:0x6F8E40` 5 (`@0x08018E40`, `@0x08018F94`, `@0x08019130`, `@0x080195F8`, `@0x08019924`), `rom:0x6ADE24` 5, `rom:0x6D68DC` 1 (`@0x08004C80`). Pinned by `tests\test_rom_constants.py` against the base ROM and a dev master build. The counts come from an aligned-word search of the base 8 MB, so a reader that forms an address by arithmetic would not appear | #save #tool | C (measured on both ROMs) | RDR |

## Section 11

| Fact | Tags | Conf | Src |
|---|---|---|---|
| `webfoot_decompress.set_table(rom)` returns THIS ROM's set table file offset, read from the literal `rom:0x959C`, and `set_offset(rom, set_id)` returns one set header offset through it. On the base ROM both equal the old `SET_TABLE` expression for every id 7-156, so base behaviour is unchanged. `rom_sheet.live_set_offset` is a second copy of the same resolver and was left as it is | #tool #sprite | C (`tests\test_rom_constants.py`, 12 tests) | RDR |
| Correction to the T5 row on `log2_sprites.py export` ("resolves a set id through the base table constant `SET_TABLE`"): it resolves through the live literal `rom:0x959C` now, so `set:157` to `set:160` export from a build | #tool #sprite set:157 set:158 set:159 set:160 | C | RDR |
| `tests\test_rom_constants.py` builds the DEV MASTER in memory (about 3 seconds) rather than reading a ROM file from `builds\`. A file on disk never changes, so a test against one stays green when a later patch moves a table | #tool #decision | C | RDR |

## Section 13

| Fact | Tags | Conf | Src |
|---|---|---|---|
| `tests\test_tools.py::test_matches_set_table_on_poc_for_old_ids` compares `live_set_offset` against the DEAD vanilla table on a BUILD for ids 7, 56 and 156. It passes only because no module repaints those three. A patch that repaints one of them turns that test red for the wrong reason | #open #tool | C (code) | RDR |

## Section 14

| Fact | Tags | Conf | Src |
|---|---|---|---|
| The item table `rom:0x6ADE24` has 5 aligned literals in the base ROM (`@0x080045F8`, `@0x08009838`, `@0x0800F6C8`, `@0x0800FB68`, `@0x080119C4`) and the 260-entry UI string table `rom:0x0E2840` has 20. Both still hold those values in a dev master build and in `log2_poc_r41_arena_v7.gba`, so no module moves either table today, and `item_index.py` may keep them as constants | #item #text #tool | C (measured on both ROMs) | RDR |
