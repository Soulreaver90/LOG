# Bible rows, tag BST

Input for `merge_bible_rows.py`. Only facts the bible does not already hold.
Deliberately omitted because the bible has them: the map table literals `rom:0x5ADC`, `rom:0x5D5C`,
`rom:0xEBD8` and the count getter `@0x0800E0AC` (rows 1095, 1203, 1204), the ext op table `0x083B5D28`
and its setter half `0x083B5F70` (rows 596, 857, 1894), `appearance_revert` skipping the current leader
(the `VBS` row), and the appearance table layout (the `VBS` row).

## Section 6

| Fact | Tags | Label | Src |
|---|---|---|---|
| **`appearance_revert` `@0x08003ED4` reverts ONLY a transformed entry.** After the leader skip it reads the record's entry index from record `+0x14`, loads `appearance_table + 20 * entry`, and tests flags bit 0 with `lsl r5,r5,#31 ; beq`. An entry whose bit 0 is CLEAR is left alone, so `ext 73 (c, set)` with an untransformed set survives a later `ext 70` even when c never becomes the leader. Record stride is 28 bytes (`lsl r2,r1,#3 ; sub r2,r2,r1 ; lsl r2,r2,#2`), the loop runs 6 records, and the write is `strb r3,[r2,#0x14]` with the `+5` revert target | #form #script | C (listing `@0x08003ED4`, whole function) | BST |
| Appearance table `0x081D967C` revert targets, all 22 entries: 0, 1, 18 and 21 revert to THEMSELVES, so reverting them is a no-op whatever the flags say. The rest pair up (2 and 5 both name 2, 6 and 7, 8 and 11, 9 and 10, 12 and 17, 13 and 14, 15 and 16, 19 and 20). Untransformed entries with a paired target (2, 8, 9, 12, 13, 15, 19) would revert UP into a transformed form if the revert were unconditional, which is the second reason the bit 0 test above has to be there. Flags bit 0 is set on entries 4 (`0x03`), 5, 7, 10, 11, 14, 16, 17 and 20 only | #form | C (table bytes, base and the dev build) | BST |

## Section 8

| Fact | Tags | Label | Src |
|---|---|---|---|
| **Base script ops 21-26 are six get-and-set variable ops, and they differ only in what they leave on the stack.** Each runs the ext op named by its operand byte as a getter, which pushes the variable, then writes `value +/- 1` through the setter `0x083B5F70 + 4n`. Op 21 `@0x08009130` adds 1 and POPS the pushed value; op 22 `@0x08009160` adds 1 and leaves the NEW value; op 23 `@0x08009190` adds 1 and leaves the OLD value; ops 24 `@0x080091BC`, 25 `@0x080091EC` and 26 `@0x08009224` are the same three with minus 1. Ops 21 and 24 do `sub r0,#1 ; str r0,[r4,#0]` on the stack count first and then read the slot they freed; 22 and 25 rewrite the top slot in place; 23 and 26 read the top slot and leave it. This refines row 1894, which said only that op 21 pushes nothing, and row 857, which read op 26 alone | #script | C (all six listings) | BST |
| Our own `celljr_fight` counter record uses op 21 as "var 1 += 1" and the vanilla record `rom:0x3BAFEA` uses op 22 as "++var 5" feeding an op 15 `lt`. These are the only two records in the r41 plus arena build that run a get-and-set op, so `scene_harness` modelling the six ops is what lets it read every record in the build | #script #tool | C (census over the build) | BST |
| **A scene table is NOT always reachable from the map table, and `table_end()` is a floor, not a length.** Walking the live build's own map table (328 entries, resolved from `rom:0xEBD8`) reaches 309 scene tables through region lists, item lists, talk objects and group sub-structs. The ending sequence `rom:0x3B8140` is named only by code and never appears, and `piccolo_gi_scene`'s copy of the chamber exit is reached only by the two type 5 records `rom:0x3CF7E0` and `rom:0x3D152C`. That copy also carries its appended records 35-44 PAST the END word at index 34, so `S.table_end()` reports 35 words and under-reads 10 records. Reading it at 35 words wrongly reports the scene as never handing the camera back, because the `camera_follow` sits in record 44 | #script #map #tool | C (census, both shapes) | BST |
| Boss bar census over the r41 plus arena build: 30 records run `bar_show` or `bar_set`, and 17 of them run `header_bit1(1)` in the SAME record. The other 13 do not, and not one of those 13 sits in a table that ever ran `header_bit1(0)`, so there was no HUD to put back. 12 are vanilla and 1 is `chamber_spar`'s `rom:0x909100`. Two records both load a map and show a bar: the live copy of the Cell Games template and the arena start | #script #combat | C (census; a bar drawn by code would not appear) | BST |
