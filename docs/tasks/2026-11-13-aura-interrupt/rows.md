# Bible rows: the Z+ bar measured in game, and the aura an interrupt must take back

Merge with `merge_bible_rows.py rows.md AIN <the file that holds this agent's report>`.
Add `AIN` to the source list in section 1. The agent could not write a report file, so the controller
owns where the report text lands: this folder, the ledger or the queue. Name that file in the merge.

## Section 6

| Fact | Tags | Label | Src | Id |
|---|---|---|---|---|
| **The Z+ bar repaint WORKS in game, and the ROM the owner played was v2.** Measured on a headless BizHawk run of each ROM with the same inputs: on `log2_piccolo_zplus_v2.gba` the landed Z+ bar is YELLOW, which is his report word for word, and on v3 and v4 it is ORANGE. v2's `hud_ramp` holds `cmp r6,#0 ; beq` straight to the pop at `0x08941412`, so it paints nothing when no ramp is live. v2 and v3 differ in 229 bytes and every one of them is inside `ki_ramp`'s own code blob, so the repaint and its test were added between the two builds. This corrects B2430's CONTRADICTED IN GAME mark: the repaint was never on screen when he looked | #hud #form char:piccolo | C (two capture runs, the same job text, the HUD photographed at 8 points; the v2 blob disassembled) | AIN | |
| The landed Z+ frame, read on v4: leader record `+8` = `0x18`, pool tag `0x8118`, RAM `0x03003A00 +0xC` = `0x31` and `+0xE` = 0, and RAM `0x03003A14` = `00 00 31 01`. **`+0xC` and `+0xE` read the SAME in the yellow build and the orange one**, because `ki_ramp` puts the colour byte back on every draw, so neither byte can tell the two apart. The bytes that do are the OBJ VRAM bar pixels and the ROM itself | #hud #form | C (capture reads on v2, v3 and v4) | AIN | |
| **A transform ability test skips the Z charge cooldown when the fighter is already in a super form.** Ability 11's test `@0x080134F2` reads the appearance entry's `+0` byte: bit 1 set returns 0 (no transform), bit 0 set returns 1 AT ONCE, and only a plain entry falls through to the three field conditions, `[[0x086DB284]+0xC] != 0`, the save struct's transform cooldown `+8 == 0`, and record `+4` EP >= 10. So base to Super Namek waits for the Z meter and Super Namek to Z+ never does | #form #combat char:piccolo | C (listing read whole; both branches exercised in a capture run) | AIN | |
| The B button fires the selected ability through `@0x08007FF4`: `[[0x083B50E8]+0x14]` is the button word, bit 0 (A) runs `@0x08007DE8` and bit 1 (B) runs `@0x08007EDA`, which reads leader record `+9` for the slot, `+0x18 + slot` for the ability id and the ability table `rom:0x1D9900` stride 16 for its test `+8` and action `+0xC` | #combat #hud | C (listings, and a capture run that fired the transform after writing record `+9`) | AIN | |

## Section 9

| Fact | Tags | Label | Src | Id |
|---|---|---|---|---|
| **A capture job can photograph any form's HUD without playing to it**: write the leader record's appearance entry byte at save struct `+0xC + 28 x leader + 8` and the next frame draws that form's bar, because `pool_ref` keys on the entry alone and a changed tag refills the pool. Writing record `+9` picks the ability B fires. Both are IWRAM, which `capture.py` allows, and a run that uses them is an ASSISTED run | #tool #hud | C (four runs, 2026-11-13) | AIN | |
| `world_remove` is `@0x080068CA(r0 = the world list, r1 = the object)`, and the effect class's own tick calls it on itself at `@0x08013672` with the list from `[0x086DB34C]`. That literal and `[0x086DB358]`, which the vanilla spawn caller uses, both hold `0x03001120`, so the add and the remove name one list. An object the list does not hold is searched for in a second list at `+0x40C` and then dropped, so a call with a pointer that already left is harmless | #object | C (both listings; the two literals dumped from the base ROM) | AIN | |

## Section 11

| Fact | Tags | Label | Src | Id |
|---|---|---|---|---|
| `powerup_fx` (2026-11-13) takes state 35's LEAVE word, vtable `0x08025D9C +0xC`, vanilla `0x080155F7`, which stops the power-up sound and reads neither argument. The state switch `@0x0800763C` calls it with r0 = the old state and r1 = the actor. The spawn stores the aura object at RAM `0x03003A1C` with the stamp `0x5A03` at `+4`, and the leave removes the object when the stamp is ours, the object's `+0` is still the effect vtable `0x080245C0` and its records-left `+0x34` is not 0. The word is cleared on every leave, so a pointer cannot outlive its transformation. This is Buu's Fury's own shape at `BF 0x0801C552` | #object #state #form | C (built, read back, 8 tests in `test_powerup_fx`; **and CONFIRMED ON SCREEN by the owner on v4, 2026-11-13: "I tested the aura hit with no issue"**, which is the interrupt no capture could stage, because the test map holds no enemies) | AIN | |
| `test_ki_ramp` now carries an END TO END draw: `hud_ramp`, then `fullpower_hud`'s `hud_fp`, then `bf_ki_pool`'s `hud_draw` and its real `put_px`, with only the vanilla draw and the ARM divide stopped, and it reads the bar back out of OBJ VRAM against the orange image. Every other draw test stubs the chained draw, so none of them can see what colour the bar ENDS as. The v2 shape was put back in memory and the new check fires on it | #tool #hud | C (`test_the_landed_zplus_bar_is_the_orange_image_in_vram`, and `scratch\2026-11-13-zplus-bar\prove_test_fires.py`) | AIN | |
