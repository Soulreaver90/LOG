# Bible rows, tag FUT3

Input for `merge_bible_rows.py`. The files `rows.md` and `rows-fut2.md` beside this one hold the FUT
and FUT2 rows and are NOT overwritten.

Every row below was read out of the built plateau v5 ROM, SHA-1 `48936bf4`. The positional reading of
an `ext 104` item index is NOT a new fact: B0645 already holds it ("builds spawn item n of the current
map list `+0x14`"), so no row restates it.

## Section 9

| Fact | Tags | Label | Src |
|---|---|---|---|
| **Only 14 of the ending table's 29 record pointers hold ops.** The live ending table `rom:0x3B8140` carries 27 words after `ending_fight` and `future_androids` run, and the two android death tables add 2 more word 0 pointers. Of those 29, word 26 is an END entry, 12 point at type 1 text records and 2 at type 2 streams, so only 14 carry an op stream. The kind byte is record `+0x02`, and a decoder that reads ops from every word raises on the first text record | #script #map | C (plateau v5 read back: words 1, 3, 5, 7, 9, 10, 12, 14, 16, 18, 22, 24 type 1; words 20, 21 type 2; word 26 END) | FUT3 |
| **`ext 104` runs three times in the whole ending after both trials, and the third reads a different map's item list.** A sweep of all 14 code records found `ext 104 (11, 2)` in word 8, `ext 104 (9, 3)` in word 11 and `ext 104 (28, 1)` in word 23. Word 23 is `ending_fight`'s Imperfect Cell fight, and the map it runs on is whatever word 13 last loaded, which in the plateau build is `ext 39 (7, 100, 1, 248, 624)`, the plateau clone map 7,100. Map 7,100 item 1 is the set 28 enemy, type 60. So an item index is only ever read against the loaded map, and an item shift on map 1,100 cannot reach word 23 | #map #item #script | C (plateau v5 read back, `06_gohan_out.py` sections 5 and 6) | FUT3 |
| **Nothing in the ending drives NPC Future Gohan, so removing him costs no scene.** No op in any of the 14 code records pushes 54. Two search shapes have now been run: a decode of the code records, re-run here on the built ROM, and an earlier raw byte scan of the base span `rom:0x3B7B08` to `rom:0x3B8140` for `push 54 ; ext N` and a zigzag 54 `push_list` head. Both are empty. His vanilla step struct `rom:0x3ED74C` only parks him, which is why he stood still while Android 18 fought. An op that COMPUTES 54 instead of pushing it, or a record outside these tables, would appear in neither shape | #story #map | C (two search shapes, both empty), L (that no such computed op exists) | FUT3 |
