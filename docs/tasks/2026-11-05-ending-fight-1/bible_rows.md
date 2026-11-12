# Bible rows from 2026-11-05-ending-fight-1

Merge these into `docs\RE-BIBLE.md`. Tag: `EF1`.
Source listings: `scripts\one-time\2026-11-05-ending-fight-1\01_probe.txt`, `02_ext_table.py`,
`03_slices.txt`, `04_conds.txt`.

## Section 8

| Fact | Tags | Label | Tag |
|---|---|---|---|
| Ext op handler table `rom:0x3B5D28`, 4 bytes an entry, found by voting 12 handler addresses the bible already names (`02_ext_table.py`). It sits 0x128 after the base op table `rom:0x3B5C00`. Slots read: ext 31 `@0x0800977A`, ext 33 `@0x08009814`, ext 96 `@0x0800A158`, ext 104 `@0x0800AAC6`, ext 119 `@0x08009840` | #script | C (12 known slots agree) | EF1 |
| The live camera object pointer is `0x03000FF4`. ext 33 (who) `@0x08009814` finds the actor, writes it into `[0x083B5C78 + 0x18] + 4` and stores that follow object in `0x03000FF4`. ext 119 `@0x08009840` stores `[0x083B5C78 + 0x1C]` there instead, the default camera. ext 31 (x, y, speed) `@0x0800977A` calls `@0x0800DF1C(0, args)`, which stores the fixed camera `0x030020C8` in `0x03000FF4` (`@0x0800DF46`). **So ext 31 ENDS an ext 33 follow**, and ext 33 (0) or ext 119 starts one again | #script #combat | C (disassembly) | EF1 |
| ext 31's x and y are the view TOP LEFT, not its centre: ending record 0 `rom:0x3B7B8F` runs `ext 31 (384, 368, 2)` for the pair at (472,408) and (520,408) with Trunks at (496,504) | #script | C (bytes), L (the offset) | EF1 |
| Ending record 23 `rom:0x3B8016` is 255 bytes, SHA-1 `96d07a4392ea2f35f876503e45cf0f28df20a8ec`, and splits in three: two attack groups, the third attack group `rom:0x3B80AC` (43 bytes, `ext 63` to `ext 64`, which ends with `ext 52 (28)`), and the tail `rom:0x3B80D7` (61 bytes, wait 80 to `ext 45`). The attacker push of the third group is at `rom:0x3B80AE` (`1d03820a388148` = push 133, 28, 100) | #story #script set:28 set:133 | C (bytes, `03_slices.txt`) | EF1 |
| The ending tail names set 132 and set 133 in four ops only: `ext 57 (133, 21)` `rom:0x3B80E6`, `ext 52 (133)` `rom:0x3B80ED`, `ext 51 (132, 248, 568)` `rom:0x3B80F1` and `ext 52 (132)` `rom:0x3B810E`. Its other ops are `ext 55 (133, 0)` `rom:0x3B80DF`, waits, music 15, sound stops 55 and 39, fade 300, `ext 119` and `ext 45` | #story #script | C (bytes) | EF1 |
| `ending_fight` (trial, not in `build_list.txt`): 3 base sites change. Ending table word 23 `rom:0x3B819C` names record F; map 6,1 count `rom:0x40B324` goes 7 to 8; its item list word `rom:0x40B334` names an 8 word copy. Record F = `ext 52 (133)`, `ext 70 (3)`, `ext 62 (0, 248, 568)`, `ext 55 (0, 1)`, `ext 104 (28, 7)`, `ext 86 (1)`, `ext 85 (28)`, `ext 33 (0)`, next 26 (END). New item 7 is the vanilla Cell item with cond 1, spot (244,504) and its own 27 word event table D (word 0 = the death record, word 24 = `0x083B8116`, word 25 = `0x083B813A`). No type entry is written, so Imperfect Cell keeps HP 5210 and AI 80 | #story #combat #map set:28 | C (build, 28 tests) | EF1 |

## Section 9

| Fact | Tags | Label | Tag |
|---|---|---|---|
| Map 6,1 is map entry 145, `rom:0x40B320`: count byte `rom:0x40B324` = 7, item list word `rom:0x40B334` = `0x083F9C40`, region list `rom:0x40B330` = `0x083F9CF8` with 6 regions. Item 5 `rom:0x3F9C08` is NPC `set:133` at (248,624) and item 6 `rom:0x3F9C28` is NPC `set:28` at (288,392), both cond `0x000100C4` (flag 196 set). The ending walks them to (248,568) and (244,504) | #map #story set:28 set:133 flag:196 | C (bytes, `01_probe.txt`) | EF1 |
| Map 6,1 item 0 cond `rom:0x3F9B30` = `push 58 ; ext 20 ; push 60 ; ext 20 ; and ; end`, so the Goku talk object at (232,568) is gated on flags 58 and 60 through ext 20. Region 5 cond `rom:0x3F9BD0` = `push 75 ; ext 19 ; push 211 ; ext 20 ; and ; end`. Region 1 script `rom:0x3F9C6C` plays music 43 and runs `ext 38` to the world map. Region 4 script `rom:0x3F9CC4` runs `ext 30 (0)` then `ext 46 (11)` | #map #script | C (bytes, `04_conds.txt`), L (ext 20 = flag clear) | EF1 |
| The vanilla Imperfect Cell enemy item is `rom:0x4058A4`: factory `0x0800E77F`, cond `0x00020088`, type 60, (264,128), `set:28`, event `rom:0x40589C` = {`0x080106B3`, `rom:0x3E24A0`}, tail `rom:0x405894` = {`0x0800CB0F`, `0x00007D00`}. Enemy type 60 `rom:0x6D5C4C` is 24 bytes: HP 5210, AI 80, descriptor `0x086FF3C4` (boss) at +0x14 | #map #combat set:28 | C (bytes) | EF1 |

## Section 7

| Fact | Tags | Label | Tag |
|---|---|---|---|
| In the r40 seed save `builds\log2_poc_r40.sav` Trunks is level 40 at HP 1181/1181 with appearance entry 15 (`set:132`, the base Saiyan armor). Slots 1 and 2 have flag 195 set and flag 196 clear, so `ext 70 (3)` in the ending gives a full health base-armor Trunks, not a Super Saiyan one | #save #form char:trunks | C (`log2_save.py info --flags`) | EF1 |
