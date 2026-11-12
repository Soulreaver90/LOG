# Bible rows: the music continuity closed in code, tag ARN3B

The agent proved the LOADER side and labelled the result LIKELY. These rows close the other half, the
SCRIPT side, which is what decides whether naming song 38 actually matches.

## Section 14

| Fact | Tags | Evidence | Source |
|---|---|---|---|
| **`loc_08020A4C` is the music starter**, and the disasm repo misnames it `Table_InitRing`. It does `STR r1,[r0,#0xC]`, storing the song record pointer, and ends on `STRB r5,[r4,#0x5]` with r5 = 1. **So every path through it leaves exactly the two fields the map loader tests**, player `+5` = 1 and player `+0xC` = the record. Its callers are `Scene_NewMaster.s`, `Table_InitRing.s`, `code_08000158.s`, `code_08009c8a.s`, `code_0800c390.s` and `code_0800f72c.s` | #sound #object | C (body read, callers enumerated over the whole disasm tree) | ARN3B |
| **`sub_08009C8A` is the script `music` op.** It pops the id off the script stack, forms `id * 20` with the same `LSL #2 / ADD / LSL #2` shape as the map loader, loads its table base from `pool_08009df0` index 11, which is `0x081D4B2C`, applies the SAME skip test (`+5` == 1 and `+0xC` == the record) and calls the SAME `loc_08020A4C`. The pool word was resolved by hand: the `LDR r2,[pc,#0x17C]` at `0x08009C9E` reads `(PC & ~3) + 0x17C` = `0x08009E1C`, which is 44 bytes into a pool starting at `0x08009DF0`. **This closes the music continuity from LIKELY to CONFIRMED in code**: a script that plays song N and a map entry whose `+0x24` is N compute an identical record pointer, so the compare is equal and the track is never restarted. Only the audible check in an emulator remains | #sound #script #map | C (handler read, pool word resolved) | ARN3B |
