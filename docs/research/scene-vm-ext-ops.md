# Ext handler profile, 145 ops (ext 0 to 144)

Table rom:0x3B5D28 in the base ROM. `arity` is how many values the op REMOVES from
the VM stack. `pred` marks an op that instead replaces the top value with its result and
leaves the depth alone, which is what a test feeding base op 19 `jz` must do.

`pushes` marks an op that RETURNS a value: a getter, which takes no argument at all.

| ext | handler | disasm name | pops | pushes | pred | via | calls | RAM words |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | `0x08009392` | sub_08009392 | 0 | 1 |  | - | - | - |
| 1 | `0x080093A4` | sub_080093a4 | 0 | 1 |  | - | - | - |
| 2 | `0x080093B6` | sub_080093b6 | 0 | 1 |  | - | - | - |
| 3 | `0x080093C8` | sub_080093c8 | 0 | 1 |  | - | - | - |
| 4 | `0x080093DA` | Opcode_PushOperandOne | 0 | 1 |  | - | - | - |
| 5 | `0x080093EE` | Opcode_PushOperandTwo | 0 | 1 |  | - | - | - |
| 6 | `0x08009402` | Opcode_PushOperandThree | 0 | 1 |  | - | - | - |
| 7 | `0x08009416` | Opcode_PushOperandFour | 0 | 1 |  | - | - | - |
| 8 | `0x0800942A` | sub_0800942a | 0 | 1 |  | - | - | - |
| 9 | `0x0800943E` | sub_0800943e | 0 | 1 |  | - | - | - |
| 10 | `0x08009452` | sub_08009452 | 0 | 1 |  | - | - | - |
| 11 | `0x0800949C` | sub_0800949c | 0 | 1 |  | - | - | - |
| 12 | `0x080094B0` | sub_080094b0 | 0 | 1 |  | - | - | - |
| 13 | `0x080094E8` | sub_080094e8 | 0 | 1 |  | - | - | - |
| 14 | `0x08009508` | sub_08009508 | 0 | 1 |  | - | - | - |
| 15 | `0x08009528` | sub_08009528 | 0 | 1 |  | - | - | - |
| 16 | `0x08009548` | sub_08009548 | 0 | 1 |  | - | - | - |
| 17 | `0x08009568` | sub_08009568 | 0 |  | yes | - | Random_Scale | - |
| 18 | `0x0800957A` | sub_0800957a | 0 |  | yes | - | Random_Below | - |
| 19 | `0x080095B4` | Bitmap_LoadCell | 0 |  | yes | - | Bitmap_TestCell | - |
| 20 | `0x080095CA` | Bitmap_LoadCellInverted | 0 |  | yes | - | Bitmap_TestCell | - |
| 21 | `0x080095E4` | sub_080095e4 | 0 |  | yes | - | sub_08006e64 | - |
| 22 | `0x08009608` | sub_08009608 | 0 |  | yes | - | Character_GetLevel | - |
| 23 | `0x08009628` | sub_08009628 | 2 | 1 |  | - | sub_080041a6 | - |
| 24 | `0x08009658` | sub_08009658 | 1 |  |  | - | Display_ClearControlBit | - |
| 25 | `0x08009670` | sub_08009670 | 1 |  |  | - | Display_SetControlBit | - |
| 26 | `0x080096AA` | sub_080096aa | 1 |  |  | - | Thunk_BranchR1 | - |
| 27 | `0x08009710` | sub_08009710 | 1 |  |  | - | sub_08003e5e | - |
| 28 | `0x08009728` | sub_08009728 | 1 |  |  | - | sub_08003e74 | - |
| 29 | `0x08009740` | sub_08009740 | 1 |  |  | - | List_FirstMatch | - |
| 30 | `0x0800975E` | sub_0800975e | 1 |  |  | - | List_FirstMatch | - |
| 31 | `0x0800977A` | sub_0800977a | 3 |  |  | - | Scene_Publish, Handler_RunScoped | - |
| 32 | `0x080097B4` | sub_080097b4 | 2 |  |  | - | Sprite_Select, Rect_FromFields, Scene_Publish, Handler_RunScoped | - |
| 33 | `0x08009814` | sub_08009814 | 1 |  |  | - | Sprite_Select | - |
| 34 | `0x0800984A` | sub_0800984a | 0 |  |  | - | - | - |
| 35 | `0x08009852` | Map_LoadFromQueue | 5 |  |  | - | Palette_New, Handler_RunScoped, Scene_Install, Map_Load, Heap_Alloc, Handler_RunScoped | - |
| 36 | `0x080098F2` | sub_080098f2 | 5 |  |  | - | Palette_New, Handler_RunScoped, Scene_Install, Map_Load, Heap_Alloc, Handler_RunScoped | - |
| 37 | `0x08009992` | sub_08009992 | 0 |  |  | - | Palette_New, Handler_RunScoped, sub_0800c7c6, Heap_Alloc, Handler_RunScoped | - |
| 38 | `0x080099D2` | sub_080099d2 | 5 |  |  | - | Thunk_BranchR2, Palette_New, Handler_RunScoped, sub_0800c584, Thunk_BranchR2, Heap_Alloc | - |
| 39 | `0x08009A88` | sub_08009a88 | 5 |  |  | - | Thunk_BranchR2, sub_0800c584 | - |
| 40 | `0x08009B1C` | sub_08009b1c | 1 |  |  | - | Palette_New, Handler_RunScoped | - |
| 41 | `0x08009B36` | sub_08009b36 | 1 |  |  | - | Heap_Alloc, Handler_RunScoped | - |
| 42 | `0x08009B5E` | sub_08009b5e | 1 |  |  | - | Heap_Alloc, Palette_Save, Handler_RunScoped | - |
| 43 | `0x08009B94` | sub_08009b94 | 1 |  |  | - | Heap_Alloc, Handler_RunScoped | - |
| 44 | `0x08009BBC` | sub_08009bbc | 1 |  |  | - | Heap_Alloc, Handler_RunScoped | - |
| 45 | `0x08009BE4` | Palette_LoadObject | 0 |  |  | - | - | - |
| 46 | `0x08009BF8` | sub_08009bf8 | 1 |  |  | - | Slot_Claim | - |
| 47 | `0x08009C54` | sub_08009c54 | 1 |  |  | - | - | - |
| 48 | `0x08009C7A` | sub_08009c7a | 0 |  |  | - | sub_0801fc0c | - |
| 49 | `0x08009C8A` | sub_08009c8a | 1 |  |  | - | Table_InitRing | - |
| 50 | `0x08009CBA` | sub_08009cba | 0 |  |  | - | - | - |
| 51 | `0x08009CC4` | sub_08009cc4 | 3 |  |  | - | sub_0800d6de, List_Append | - |
| 52 | `0x08009D00` | Sprite_QueueObject | 1 |  |  | - | Sprite_Select, Sprite_Select, Heap_Alloc, Queue_Append | - |
| 53 | `0x08009D4A` | sub_08009d4a | 3 |  |  | - | Sprite_Select, Record_NewFromWords, Queue_Append | - |
| 54 | `0x08009E30` | sub_08009e30 | 3 |  |  | - | Sprite_Select, Heap_Alloc, Queue_Append | - |
| 55 | `0x08009EFC` | sub_08009efc | 2 |  |  | - | Sprite_Select, Heap_Alloc, Queue_Append | - |
| 56 | `0x08009F7C` | sub_08009f7c | 2 |  |  | - | Sprite_Select, Sprite_Select, Heap_Alloc, Queue_Append | - |
| 57 | `0x08009FC4` | sub_08009fc4 | 2 |  |  | - | Sprite_Select, Heap_Alloc, Queue_Append | - |
| 58 | `0x0800A044` | sub_0800a044 | 2 |  |  | - | Sprite_Select, Heap_Alloc, Queue_Append | - |
| 59 | `0x0800A084` | sub_0800a084 | 0 |  |  | - | sub_0801f878 | - |
| 60 | `0x0800A09A` | sub_0800a09a | 1 |  |  | - | Sprite_Select, Heap_Alloc, Queue_Append | - |
| 61 | `0x0800A438` | sub_0800a438 | 0 |  |  | - | sub_0801f878 | - |
| 62 | `0x0800A44E` | sub_0800a44e | 3 |  |  | - | Sprite_Select, Heap_Alloc, Queue_Append | - |
| 63 | `0x0800A5A6` | sub_0800a5a6 | 0 |  |  | - | sub_0800e032 | - |
| 64 | `0x0800A5B2` | sub_0800a5b2 | 0 |  |  | - | sub_0800e038 | - |
| 65 | `0x0800A5BE` | sub_0800a5be | 2 |  |  | - | Slot_Claim, sub_0800ded0, Handler_RunScoped | - |
| 66 | `0x0800A60C` | sub_0800a60c | 1 |  |  | - | sub_0801f878 | - |
| 67 | `0x0800A622` | sub_0800a622 | 0 |  |  | - | Heap_Alloc, Handler_RunScoped | - |
| 68 | `0x0800A638` | sub_0800a638 | 1 |  |  | - | Heap_Alloc, Handler_RunScoped | - |
| 69 | `0x0800A65C` | sub_0800a65c | 1 |  |  | - | Heap_Alloc, Handler_RunScoped | - |
| 70 | `0x0800A784` | sub_0800a784 | 1 |  |  | 0x0800A680 | Character_SetActiveIndex, sub_08003ed4 | - |
| 71 | `0x0800A7A0` | sub_0800a7a0 | 4 |  |  | - | Bitmap_FillCells, Bitmap_FillCells | - |
| 72 | `0x0800A7F8` | sub_0800a7f8 | 4 |  |  | - | Bitmap_FillCells, Bitmap_FillCells | - |
| 73 | `0x0800A8EC` | sub_0800a8ec | 2 |  |  | - | Thunk_BranchR1, sub_080042bc, Sprite_Directory_Lookup, Thunk_BranchR2, sub_080086a2, Thunk_BranchR1 | - |
| 74 | `0x0800A998` | sub_0800a998 | 0 |  |  | - | sub_0800c2f8 | - |
| 75 | `0x080094CC` | sub_080094cc | 0 | 1 |  | - | - | - |
| 76 | `0x080096CA` | sub_080096ca | 1 |  |  | - | - | - |
| 77 | `0x080096E8` | sub_080096e8 | 2 |  |  | - | - | - |
| 78 | `0x08009688` | sub_08009688 | 2 |  |  | - | sub_080062c0 | - |
| 79 | `0x0800A9B6` | sub_0800a9b6 | 1 |  |  | - | - | - |
| 80 | `0x0800AA10` | sub_0800aa10 | 1 |  |  | - | - | - |
| 81 | `0x0800AA34` | sub_0800aa34 | 1 |  |  | - | - | - |
| 82 | `0x0800AA58` | sub_0800aa58 | 1 |  |  | - | - | - |
| 83 | `0x0800AA7C` | sub_0800aa7c | 2 |  |  | - | - | - |
| 84 | `0x0800AAAE` | sub_0800aaae | 1 |  |  | - | sub_0800c73a | - |
| 85 | `0x0800AB1A` | sub_0800ab1a | 1 |  |  | - | Sprite_Select, Sprite_NewSpan, List_Append | - |
| 86 | `0x0800AB82` | Object_SetActiveFromQueue | 1 |  |  | - | Object_SetActive | - |
| 87 | `0x0800ABA4` | sub_0800aba4 | 1 |  |  | - | List_MaxScaled, Sprite_NewLayer, List_Append | - |
| 88 | `0x0800AC00` | sub_0800ac00 | 0 |  |  | - | - | - |
| 89 | `0x08009D94` | sub_08009d94 | 4 |  |  | - | Sprite_Select, Sprite_Select, sub_0801094c, Queue_Append | - |
| 90 | `0x0800AB44` | sub_0800ab44 | 3 |  |  | - | Sprite_Select, Sprite_NewSpan, List_Append | - |
| 91 | `0x0800A9DA` | sub_0800a9da | 1 |  |  | - | - | - |
| 92 | `0x0800ABA4` | sub_0800aba4 | 1 |  |  | - | List_MaxScaled, Sprite_NewLayer, List_Append | - |
| 93 | `0x0800A49A` | sub_0800a49a | 1 |  |  | - | Sprite_Select, Heap_Alloc, Queue_Append | - |
| 94 | `0x0800A526` | sub_0800a526 | 3 |  |  | - | Sprite_Select, Heap_Alloc, Queue_Append | - |
| 95 | `0x0800A572` | sub_0800a572 | 1 |  |  | - | Sprite_Select, Heap_Alloc, Queue_Append | - |
| 96 | `0x0800A158` | sub_0800a158 | 3 |  |  | - | Sprite_Select, Sprite_Select, Heap_Alloc, Queue_Append | - |
| 97 | `0x0800A3E8` | sub_0800a3e8 | 0 |  |  | - | sub_08006c24, Queue_Clear, sub_0801f346, Scene_NewMaster, Handler_Restore | - |
| 98 | `0x0800AC10` | Character_SetLevel | 2 |  |  | - | Character_GetLevel, Character_ApplyLevelUp, Character_SetXpForLevel | - |
| 99 | `0x0800A210` | sub_0800a210 | 4 |  |  | - | Sprite_Select, Heap_Alloc, Queue_Append | - |
| 100 | `0x0800A4DA` | sub_0800a4da | 3 |  |  | - | Sprite_Select, Heap_Alloc, Queue_Append | - |
| 101 | `0x0800AC5C` | sub_0800ac5c | 2 |  |  | - | sub_08012a68, List_Append | - |
| 102 | `0x0800ACAC` | sub_0800acac | 2 |  |  | - | sub_08012a68, List_Append | - |
| 103 | `0x0800ACEA` | sub_0800acea | 4 |  |  | - | sub_08012b38, List_Append | - |
| 104 | `0x0800AAC6` | Sprite_ReplaceWithEntry | 2 |  |  | - | Sprite_Select, Point_LoadScaled, List_RemoveValue, Object_SpawnFromEntry | - |
| 105 | `0x0800AD7A` | sub_0800ad7a | 0 |  | yes | - | - | - |
| 106 | `0x0800AD98` | sub_0800ad98 | 0 |  | yes | - | - | - |
| 107 | `0x0800ADB6` | sub_0800adb6 | 0 |  | yes | - | - | - |
| 108 | `0x0800ADD4` | sub_0800add4 | 0 |  | yes | - | - | - |
| 109 | `0x0800ADF2` | sub_0800adf2 | 2 |  |  | - | - | - |
| 110 | `0x0800AE32` | sub_0800ae32 | 2 |  |  | - | - | - |
| 111 | `0x08009C22` | sub_08009c22 | 2 |  |  | - | Slot_Claim | - |
| 112 | `0x0800AE76` | sub_0800ae76 | 2 |  |  | - | Sprite_Select, Heap_Alloc, Queue_Append | - |
| 113 | `0x0800AEB8` | sub_0800aeb8 | 0 |  |  | - | - | - |
| 114 | `0x0800AEC8` | sub_0800aec8 | 0 |  |  | - | - | - |
| 115 | `0x0800A680` | Character_SetActiveIndex | 1 |  |  | - | Thunk_BranchR1, Sprite_ObjectDirectory, Thunk_BranchR2, sub_080086a2, Thunk_BranchR1 | - |
| 116 | `0x0800A794` | sub_0800a794 | 0 |  |  | - | sub_08003ed4 | - |
| 117 | `0x0800A850` | sub_0800a850 | 4 |  |  | - | Bitmap_FillCells | - |
| 118 | `0x0800A89E` | sub_0800a89e | 4 |  |  | - | Bitmap_FillCells | - |
| 119 | `0x08009840` | sub_08009840 | 0 |  |  | - | - | - |
| 120 | `0x0800AD3E` | sub_0800ad3e | 2 |  |  | - | sub_08016ab4, List_Append | - |
| 121 | `0x0800A004` | sub_0800a004 | 2 |  |  | - | Sprite_Select, Heap_Alloc, Queue_Append | - |
| 122 | `0x0800AED8` | sub_0800aed8 | 0 |  |  | - | - | - |
| 123 | `0x0800AEE4` | sub_0800aee4 | 0 |  |  | - | - | - |
| 124 | `0x0800AEF0` | sub_0800aef0 | 3 |  |  | - | Sprite_Directory_Lookup, sub_08019f5c, List_Append | - |
| 125 | `0x0800AF44` | sub_0800af44 | 0 |  |  | - | Heap_Alloc, sub_08001f04, Handler_RunScoped, Dma3_WordFill | - |
| 126 | `0x0800AF72` | sub_0800af72 | 0 | 1 |  | - | - | - |
| 127 | `0x0800ABD6` | sub_0800abd6 | 1 |  |  | - | List_MaxScaled, sub_0800c718 | - |
| 128 | `0x0800AFA0` | sub_0800afa0 | 2 |  |  | - | sub_080040ee | - |
| 129 | `0x0800AFC2` | sub_0800afc2 | 0 | 1 |  | - | - | - |
| 130 | `0x0800AFD4` | sub_0800afd4 | 0 |  |  | - | sub_0801c4b0, List_Append | - |
| 131 | `0x08009466` | sub_08009466 | 0 | 1 |  | - | - | - |
| 132 | `0x08009478` | sub_08009478 | 0 | 1 |  | - | - | - |
| 133 | `0x0800948A` | sub_0800948a | 0 | 1 |  | - | - | - |
| 134 | `0x0800A276` | sub_0800a276 | 3 |  |  | - | Sprite_Select, Heap_Alloc, Queue_Append | - |
| 135 | `0x0800A2C2` | sub_0800a2c2 | 5 |  |  | - | Sprite_Select, Heap_Alloc, __16__rt_sdiv, Queue_Append | - |
| 136 | `0x0800A346` | sub_0800a346 | 4 |  |  | - | Sprite_Select, Heap_Alloc, Queue_Append | - |
| 137 | `0x0800A3A2` | sub_0800a3a2 | 2 |  |  | - | Sprite_Select, Heap_Alloc, Queue_Append | - |
| 138 | `0x0800AFE8` | sub_0800afe8 | 0 |  |  | 0x08021388 | Boot_StopUntilKey | - |
| 139 | `0x0800AFF0` | Character_AwardXpToActive | 1 |  |  | - | Character_AwardXp | - |
| 140 | `0x08009F3C` | sub_08009f3c | 2 |  |  | - | Sprite_Select, Heap_Alloc, Queue_Append | - |
| 141 | `0x0800B00C` | sub_0800b00c | 1 |  |  | - | Sprite_Directory_Lookup, Table_FindByDirectory | - |
| 142 | `0x0800A1B4` | sub_0800a1b4 | 3 |  |  | - | Sprite_Select, Sprite_Select, Heap_Alloc, Queue_Append | - |
| 143 | `0x08009E80` | sub_08009e80 | 1 | 1 |  | - | Sprite_Select, Point_LoadScaled | - |
| 144 | `0x08009EBA` | sub_08009eba | 2 |  |  | - | Sprite_Select, Record_NewFromWords, Queue_Append | - |