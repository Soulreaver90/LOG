# Which vanilla records use which scene op

Source: `Dragon Ball Z - The Legacy of Goku II (USA).gba`. The walk reached **302** map-owned scene tables and
**5304** ext op sites across **102** distinct ops.

> This walks tables a MAP owns. A table named only by code, by another table's next index, or
> by a script region's script is NOT reached, so every count here is a FLOOR. Say "the walk
> found N", never "there are N".

| ext | name | sites | example calls |
| --- | --- | --- | --- |
| 0 | ext0 | **3** | `rom:0x3C5718` (101); `rom:0x3C6F0E` (82); `rom:0x3C71B2` (82) |
| 4 | ext4 | **9** | `rom:0x3C0CCC` (); `rom:0x3CAEAC` (); `rom:0x3CAEB6` () |
| 8 | ext8 | **2** | `rom:0x3B60A7` (); `rom:0x3B60C7` () |
| 9 | ext9 | **2** | `rom:0x3B60AC` (); `rom:0x3B60CC` () |
| 11 | ext11 | **78** | `rom:0x3B85D5` (); `rom:0x3B880E` (); `rom:0x3B8B37` () |
| 14 | ext14 | **2** | `rom:0x3E6E21` (); `rom:0x3EA355` () |
| 16 | ext16 | **2** | `rom:0x3E6E25` (); `rom:0x3EA351` () |
| 17 | ext17 | **57** | `rom:0x3B77C5` (54, 34, 3); `rom:0x3B77E9` (54, 34, 3); `rom:0x3B780D` (54, 34, 3) |
| 19 | test_flag | **155** | `rom:0x3B603E` (287); `rom:0x3B6EF5` (0); `rom:0x3B6F3B` (1) |
| 20 | test_flag_alt | **27** | `rom:0x3C1EE1` (221); `rom:0x3C25D3` (206); `rom:0x3C2E79` (33) |
| 21 | item_count | **32** | `rom:0x3C2435` (42); `rom:0x3C25D7` (17); `rom:0x3C517D` (26) |
| 22 | ext22 | **5** | `rom:0x3B859B` (0, 0); `rom:0x3B85A6` (1, 1); `rom:0x3DDF47` (2, 2) |
| 24 | ext24 | **12** | `rom:0x3B831D` (2); `rom:0x3CA62D` (0); `rom:0x3DBF54` (0) |
| 25 | ext25 | **4** | `rom:0x3D8786` (1); `rom:0x3DC36F` (1); `rom:0x3DC385` (0) |
| 26 | ext26 | **37** | `rom:0x3B6015` (0); `rom:0x3BBEF8` (32); `rom:0x3C259D` (17) |
| 27 | set_flag | **177** | `rom:0x3B60C5` (289); `rom:0x3B60E5` (288); `rom:0x3B8573` (68) |
| 28 | clear_flag | **15** | `rom:0x3B9037` (27); `rom:0x3B903B` (25); `rom:0x3B903F` (24) |
| 29 | party_add | **41** | `rom:0x3B7924` (0); `rom:0x3B87FB` (2); `rom:0x3B8DA9` (0) |
| 30 | party_remove | **38** | `rom:0x3B85BE` (2); `rom:0x3B8DAD` (1); `rom:0x3B8E95` (0) |
| 31 | camera | **92** | `rom:0x3B779E` (104, 288, 3); `rom:0x3B7AB2` (448, 336, 2); `rom:0x3B8605` (496, 464, 10) |
| 33 | camera_follow | **74** | `rom:0x3B792C` (0); `rom:0x3B8844` (0); `rom:0x3B939B` (60) |
| 34 | ext34 | **7** | `rom:0x3BFBFD` (); `rom:0x3CA617` (); `rom:0x3D31E7` () |
| 35 | load_map | **13** | `rom:0x3B7A30` (2, 1, 1, 448, 464); `rom:0x3B8284` (1, 3, 1, 120, 104); `rom:0x3BD818` (3, 5, 1, 8, 16) |
| 37 | ext37 | **7** | `rom:0x3BFC55` (); `rom:0x3CA633` (); `rom:0x3D37AF` () |
| 38 | load_map_fade | **29** | `rom:0x3B7AD1` (2, 22, 1, 112, 136); `rom:0x3B8EAA` (6, 99, 1, 2944, 1912); `rom:0x3B904F` (6, 99, 1, 2944, 1912) |
| 39 | load_map_at | **29** | `rom:0x3B71C0` (1, 5, 1, 224, 128); `rom:0x3B79EE` (1, 6, 1, 120, 80); `rom:0x3B8336` (1, 1, 1, 200, 664) |
| 40 | fade_out | **47** | `rom:0x3B71B5` (120); `rom:0x3B828C` (240); `rom:0x3B856F` (240) |
| 41 | fade_in | **30** | `rom:0x3B71D4` (120); `rom:0x3B8609` (240); `rom:0x3B9764` (120) |
| 42 | palette_fx | **28** | `rom:0x3B8321` (120); `rom:0x3B9519` (120); `rom:0x3BDD85` (10) |
| 43 | flash_wait | **26** | `rom:0x3B833A` (120); `rom:0x3B9525` (30); `rom:0x3BDD9A` (10) |
| 44 | ext44 | **20** | `rom:0x3B7115` (10); `rom:0x3B7912` (10); `rom:0x3B9529` (40) |
| 45 | ext45 | **6** | `rom:0x3B7A00` (); `rom:0x3B828E` (); `rom:0x3B8E9B` () |
| 46 | sound | **390** | `rom:0x3B710B` (34); `rom:0x3B71A9` (26); `rom:0x3B7715` (28) |
| 47 | sound_stop | **13** | `rom:0x3B79F6` (55); `rom:0x3B79FA` (39); `rom:0x3BE5E9` (55) |
| 49 | music | **64** | `rom:0x3B7916` (22); `rom:0x3B7A04` (10); `rom:0x3B8292` (23) |
| 50 | ext50 | **1** | `rom:0x3C39FD` () |
| 51 | spawn | **96** | `rom:0x3B77A7` (11, 176, 272); `rom:0x3B77B0` (9, 248, 272); `rom:0x3B8FAE` (60, 144, 272) |
| 52 | remove | **166** | `rom:0x3B60C0` (155); `rom:0x3B60E0` (155); `rom:0x3B7920` (54) |
| 53 | walk | **293** | `rom:0x3B60BC` (155, 264, 592); `rom:0x3B60DC` (155, 120, 184); `rom:0x3B6EC0` (54, 144, 568) |
| 54 | fly | **143** | `rom:0x3B71B1` (54, 160, 0); `rom:0x3B8808` (60, 608, 648); `rom:0x3B8821` (103, 576, 648) |
| 55 | face | **647** | `rom:0x3B6C73` (0, 2); `rom:0x3B6D33` (54, 3); `rom:0x3B6DFB` (0, 0) |
| 56 | face_alt | **163** | `rom:0x3B8FC6` (60, 0); `rom:0x3B8FCC` (0, 60); `rom:0x3B9271` (60, 0) |
| 57 | pose | **344** | `rom:0x3B7111` (54, 10); `rom:0x3B7121` (0, 3); `rom:0x3B71CC` (0, 3) |
| 58 | ext58 | **8** | `rom:0x3B78D5` (54, 2); `rom:0x3B78E5` (54, 2); `rom:0x3B78F2` (54, 2) |
| 60 | ext60 | **50** | `rom:0x3B77BE` (54); `rom:0x3B77E2` (54); `rom:0x3B7806` (54) |
| 62 | move_to | **45** | `rom:0x3B85CD` (60, 616, 544); `rom:0x3B85E4` (103, 616, 600); `rom:0x3B85F6` (53, 616, 600) |
| 63 | block_begin | **175** | `rom:0x3B77B2` (); `rom:0x3B77D6` (); `rom:0x3B77FA` () |
| 64 | block_end | **175** | `rom:0x3B77D4` (); `rom:0x3B77F8` (); `rom:0x3B781C` () |
| 65 | ext65 | **14** | `rom:0x3B6FDC` (25, 80); `rom:0x3B790E` (20, 10); `rom:0x3BD700` (30, 120) |
| 69 | wait | **471** | `rom:0x3B6C6D` (60); `rom:0x3B6DFF` (120); `rom:0x3B709F` (180) |
| 70 | leader | **17** | `rom:0x3B7AC6` (0); `rom:0x3B832B` (3); `rom:0x3CCA4F` (2) |
| 71 | ext71 | **8** | `rom:0x3B8DE7` (224, 120, 280, 144); `rom:0x3BBEF0` (136, 40, 168, 80); `rom:0x3C9D85` (240, 352, 272, 384) |
| 72 | ext72 | **17** | `rom:0x3C001A` (600, 408, 656, 520); `rom:0x3D0129` (192, 272, 224, 304); `rom:0x3D5428` (352, 160, 368, 168) |
| 73 | appearance | **12** | `rom:0x3B8595` (0, 53); `rom:0x3B8DD5` (0, 55); `rom:0x3C32B9` (0, 55) |
| 74 | ext74 | **38** | `rom:0x3B8DDB` (); `rom:0x3B923B` (); `rom:0x3B9F7B` () |
| 76 | item_dec | **20** | `rom:0x3BB6AB` (37); `rom:0x3C25A1` (42); `rom:0x3C39D2` (19) |
| 77 | item_sub | **2** | `rom:0x3CF0D3` (17, 25); `rom:0x3DEABF` (43, 3) |
| 78 | ext78 | **2** | `rom:0x3E4290` (0, 3); `rom:0x3E42D4` (0, 1) |
| 79 | party_join | **9** | `rom:0x3B6C69` (3); `rom:0x3B7ABE` (0); `rom:0x3C32B3` (1) |
| 80 | bit1_set | **12** | `rom:0x3B7AC2` (0); `rom:0x3C32BD` (1); `rom:0x3CCA53` (2) |
| 81 | bit1_clear | **8** | `rom:0x3CCA57` (1); `rom:0x3CCA5B` (0); `rom:0x3D9885` (0) |
| 82 | bit5_set | **4** | `rom:0x3D1FD7` (2); `rom:0x3DF2B4` (3); `rom:0x3DF2DB` (3) |
| 83 | ext83 | **14** | `rom:0x3B8637` (0, 1); `rom:0x3B868F` (1, 1); `rom:0x3CE4CB` (0, 0) |
| 84 | ext84 | **17** | `rom:0x3B9521` (1); `rom:0x3D010E` (1); `rom:0x3D8B51` (0) |
| 85 | bar_show | **17** | `rom:0x3B9595` (48); `rom:0x3BC421` (50); `rom:0x3BC90D` (50) |
| 86 | header_bit1 | **126** | `rom:0x3B6EC4` (1); `rom:0x3B6F83` (0); `rom:0x3B7259` (1) |
| 88 | ext88 | **27** | `rom:0x3B973B` (); `rom:0x3BBEDF` (); `rom:0x3C9A6B` () |
| 89 | ext89 | **4** | `rom:0x3CABB1` (51, 0, 0, 0); `rom:0x3CAC81` (52, 0, 0, 0); `rom:0x3CB11D` (22, 0, 0, 0) |
| 90 | bar_set | **18** | `rom:0x3C9A32` (127, 25, 100); `rom:0x3D5E4C` (14, 75, 100); `rom:0x3D62EB` (14, 50, 75) |
| 91 | party_leave | **2** | `rom:0x3B7ABA` (3); `rom:0x3EC737` (4) |
| 94 | ext94 | **99** | `rom:0x3B78CF` (54, 16, 8); `rom:0x3B78DF` (); `rom:0x3B78EC` (54, 12, 0) |
| 95 | face_target | **76** | `rom:0x3B77CC` (54); `rom:0x3B77F0` (54); `rom:0x3B7814` (54) |
| 96 | attack | **29** | `rom:0x3B77BA` (11, 54, 120); `rom:0x3B77DE` (9, 54, 120); `rom:0x3B7802` (9, 54, 120) |
| 97 | ext97 | **1** | `rom:0x3B8EE9` () |
| 98 | ext98 | **10** | `rom:0x3B8327` (3, 6); `rom:0x3B85A0` (); `rom:0x3B85AB` () |
| 99 | ext99 | **31** | `rom:0x3CC756` (13, 180, 142, 100); `rom:0x3D4556` (0, 458, 144, 100); `rom:0x3DB19E` (0, 136, 144, 100) |
| 100 | ext100 | **32** | `rom:0x3CC75F` (13, 180, 142); `rom:0x3D455F` (0, 458, 144); `rom:0x3DB1A7` (0, 136, 144) |
| 104 | ext104 | **27** | `rom:0x3BC41D` (50, 1); `rom:0x3BC909` (50, 1); `rom:0x3BCD1F` (50, 1) |
| 109 | ext109 | **14** | `rom:0x3B857A` (0, 500); `rom:0x3B8588` (1, 500); `rom:0x3D90C9` (2, 5000) |
| 110 | ext110 | **14** | `rom:0x3B8581` (0, 500); `rom:0x3B858F` (1, 500); `rom:0x3D90C2` (2, 5000) |
| 112 | hit | **130** | `rom:0x3B77C8` (); `rom:0x3B77EC` (); `rom:0x3B7810` () |
| 113 | ext113 | **2** | `rom:0x3CF49F` (); `rom:0x3D0C53` () |
| 114 | ext114 | **2** | `rom:0x3CF4A1` (); `rom:0x3CF5A9` () |
| 115 | leader_alt | **1** | `rom:0x3D457E` (1) |
| 116 | ext116 | **1** | `rom:0x3D482C` () |
| 117 | ext117 | **1** | `rom:0x3C9D91` (240, 352, 272, 384) |
| 119 | ext119 | **3** | `rom:0x3E9ADF` (); `rom:0x3EB227` (); `rom:0x3EBDC9` () |
| 121 | fly_pose | **16** | `rom:0x3D0098` (111, 22); `rom:0x3E149F` (0, 2); `rom:0x3E14BD` (0, 22) |
| 123 | ext123 | **4** | `rom:0x3D8337` (); `rom:0x3D8431` (); `rom:0x3D84AB` () |
| 125 | ext125 | **2** | `rom:0x3C4E88` (); `rom:0x3DD037` () |
| 126 | ext126 | **3** | `rom:0x3D8C9A` (); `rom:0x3E65E5` (); `rom:0x3E6F07` () |
| 129 | ext129 | **1** | `rom:0x3B8E8B` () |
| 134 | ext134 | **22** | `rom:0x3B95F6` (0, 20, 30); `rom:0x3B9635` (0, 20, 30); `rom:0x3B967A` (0, 20, 40) |
| 135 | flash | **16** | `rom:0x3BE357` (49, 255, 0, 0, 10); `rom:0x3BE5BD` (74, 255, 0, 0, 10); `rom:0x3E52DA` (28, 255, 0, 0, 20) |
| 136 | walk_fast | **1** | `rom:0x3E8C18` (72, 448, 850, 1000) |
| 137 | ext137 | **2** | `rom:0x3E147E` (28, 140); `rom:0x3EBE6D` (0, 140) |
| 139 | ext139 | **16** | `rom:0x3B973F` (20); `rom:0x3BBEE5` (50000); `rom:0x3C9A77` (1500) |
| 140 | ext140 | **1** | `rom:0x3E6C21` (11, 41) |
| 141 | ext141 | **2** | `rom:0x3BD81C` (74); `rom:0x3BD820` (48) |
| 142 | ext142 | **1** | `rom:0x3EBDB6` (137, 30, 100) |
| 143 | ext143 | **3** | `rom:0x3C56D9` (101); `rom:0x3C6EED` (82); `rom:0x3C7191` (82) |
| 144 | ext144 | **3** | `rom:0x3C571A` (); `rom:0x3C6F10` (); `rom:0x3C71B4` () |

## Ops the handler table defines but this walk never saw

An op with no site here is not unused: it may live in a table the walk cannot reach.

ext 1, ext 2, ext 3, ext 5, ext 6, ext 7, ext 10, ext 12, ext 13, ext 15, ext 18, ext 23, ext 32, ext 36, ext 48, ext 59, ext 61, ext 66, ext 67, ext 68, ext 75, ext 87, ext 92, ext 93, ext 101, ext 102, ext 103, ext 105, ext 106, ext 107, ext 108, ext 111, ext 118, ext 120, ext 122, ext 124, ext 127, ext 128, ext 130, ext 131, ext 132, ext 133, ext 138

## Records the decoder could not read (1)

- `rom:0x-8000000` table: not a readable ROM offset