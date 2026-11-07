# Bible rows, tag FUT2

Input for `merge_bible_rows.py`. The file `rows.md` beside this one holds the FUT rows and is NOT
overwritten.

> WARNING, read before you merge `rows.md`. Its Section 8 row
> "**`ext57_set_state` `@0x08009FC4` does NOT block**" is WRONG and must be dropped or replaced by the
> first row below. The bible does not hold it yet (`grep ext57_set_state docs\RE-BIBLE.md` returns
> nothing), so nothing needs unpicking.

## Section 8

| Fact | Tags | Label | Src |
|---|---|---|---|
| **`ext 57` BLOCKS the script, and the call that proves it is one level down.** `sub_08009FC4` pops the state and the set, resolves the actor through `find_actor_by_set` `@0x08009370`, allocates a 0xC command with `@0x0801F08C`, writes 0 at `+0x4`, the state at `+0x8` and a vtable at `+0x0`, then ends in `BL Queue_Append @0x0800E04C`. `Queue_Append` appends the command to the actor's list at `+0x150` and then runs `LDR r0,[r0,#0x0] ; CMP r0,#0x0 ; BNE loc_0800E076 ; BL loc_0800DE20 ; BL loc_0801F2F4`. `[r0,#0]` is the ext 63 / ext 64 group flag, so OUTSIDE a group the flag is 0 and the script enters the frame loop `@0x0801F2F4`. Inside a group it does not, which is the same branch B1967 reads for the group wait. This CORRECTS the reading that `ext 57` is non-blocking because `@0x0801F2F4` is not named inside `@0x08009FC4`. B0604 ("waits until it leaves state n") was right, and B1677 records the same reading | #script #state | C (`code_08009fc4.s`, `Queue_Append.s`) | FUT2 |
| **The ending's vanilla `pose(132,9)` DID get its frames; the NPC was destroyed only after it left state 9.** Ending word 4 `rom:0x3B7C1C` is `wait(40) ; face(132,0) ; sound(55) ; pose(132,9) ; remove(132) ; spawn(133,496,504) ; sound(23)`, 44 bytes, next index 5. Because `ext 57` blocks, `remove(132)` runs only after NPC set 132 leaves state 9, not one op later, and set 132 carries anim 9. How long an NPC holds state 9 is NOT read: B0605 times the PLAYER object `@0x03002174`, vtable `@0x08025B80`, at 160 frames, and the NPC object's state 9 handler was not opened. So the vanilla beat is a played power up of unread length, and a copy that drops the pose removes the transformation animation, which is the defect the owner reported on v3 | #script #story #form | C (bytes, `Queue_Append.s`, set 132 anim 9), L (that the NPC beat is the same 160 frames) | FUT2 |
| **`cellgames_ssj.GOKU_TRANSFORM` reads as a blocking sequence, not a flash over a running animation.** `sound(55) ; pose(0,9) ; palette_fx(10) ; sound_stop(55) ; appearance(4,61) ; flash_wait(10)`: the pose blocks for the whole 160 frames of state 9 and the state plays sound 23 at its end (B0605), then `ext 42` fades to white over 10 frames, the body swap happens under the white, and `ext 43` fades back over 10 (B1978). The swap lands AFTER the animation, never during it. Total hold is about 180 frames | #script #form #sound | C (bytes, handlers), L (the on-screen look) | FUT2 |

## Section 4

| Fact | Tags | Label | Src |
|---|---|---|---|
| **A base form set carries anim 9 and its Super Saiyan twin does not, in BOTH pairs the transformation records use.** Walked through `set_offset` plus `read_set` on the base ROM, 4 directions each: Goku `set:60` `rom:0x2C1D90` has anims 0-9, 11-14, 16-20 and `set:61` `rom:0x2CEDD4` has 0-8, 10-13, 16, 18-21; Trunks `set:132` `rom:0x36813C` has 0-9, 11-14, 16-18, 20 and `set:133` `rom:0x373B30` has 0-8, 11-13, 16, 18, 20, 21. **Only the base set has anim 9.** So a transformation record must run `ext 57 (0,9)` BEFORE `ext 73`, never after and never during: the power up has no frames on the Super Saiyan set. This is the structural reason the shipped Goku record orders its ops the way it does. For contrast the NPC-only sets in the same scene are much smaller: `set:54` Future Gohan has 0-3, 5, 10, 12; `set:11` Android 18 has 0-8, 12; `set:9` Android 17 has 0-3, 5-8, 12 | #sprite #form | C (set walk, base ROM) | FUT2 |
