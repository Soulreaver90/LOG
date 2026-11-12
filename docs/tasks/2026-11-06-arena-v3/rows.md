# Bible rows for arena v3, tag ARN3

The warp carrier rows are NOT repeated here. They are already merged as `WRP`, and bible row 708 held the
field pair before this task.

## Section 9

| Fact | Tags | Evidence | Source |
|---|---|---|---|
| **Map entry `+0x24` is the map's MUSIC.** `sub_0800EB58(entry)` loads `[entry+0x24]`: when the value is under `0x10000` it RETURNS it as the song id, and when it is larger it runs the value as a script and returns the script's result. Map 6,1 uses the script form, `0x083F9AF0` | #map #sound | C (handler read) | ARN3 |
| **A map load restarts the music unless the new map names the song ALREADY PLAYING.** `loc_0800C4D6` in `code_0800c390.s` calls `sub_0800EB58`, and on `0xFF` writes player `+5` = 0, which STOPS the music. Otherwise it forms the record `0x081D4B2C + 20 * id` and calls `music_play` UNLESS player `+5` is 1 AND player `+0xC` equals that record: `LDRB r2,[r0,#0x5]` / `CMP r2,#1` / `BNE play` / `LDR r2,[r0,#0xC]` / `CMP r2,r1` / `BEQ skip`. **There is no "leave the music alone" value. `0` is song 0, not silence**, so a cloned map left at 0 starts song 0 on entry, which is the abrupt cut the owner heard on arena v1. To carry a track unbroken across a load, name the song that is playing | #map #sound #decision | C (handler read) | ARN3 |
| The ending table `rom:0x3B8140` record 0 runs `music(42)` then `music(38)`, and no record from 1 to 22 changes or stops the music. So **song 38 is playing when record F (word 23) runs**, and `+0x24` = 38 on the arena keeps it unbroken | #map #sound #story | C (every record 1 to 22 read) | ARN3 |

## Section 14

| Fact | Tags | Evidence | Source |
|---|---|---|---|
| Cleared dead ends, so nobody re-reads them: **`sub_0800D8AE` is a two instruction constant getter** and **`sub_0800D9C2` is an object constructor that allocates 0x18 bytes**. Neither is a region or warp trigger test, which is what both were guessed to be while hunting the arena's exits | #object #debug | C (both listings read) | ARN3 |
| Two addresses the stale gnu tree emits as functions, `0x08003AFE` and `0x080042EA`, are **data mis-decoded as code**: zero references anywhere in the disasm tree, and bodies that repeat `LSR rX, rY, #0x20` after an `LSL r0, r0, #0x0` pad. Measured 2026-11-06 while closing the gnu tree gap. The filename gap runs both ways, 103 `code_<addr>.s` only in gnu, but **101 of those 103 are in the disasm `CODE_INDEX.md` under a FUNCTION name**, so a missing `code_<addr>.s` is never proof a function is absent | #tool #debug | C (grep over the whole tree, both bodies read) | ARN3 |
