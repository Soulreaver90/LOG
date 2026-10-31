# Task 6 review: usable Super Saiyan 2

Read only. Date: 2026-10-17.

## Spec Compliance

**Code: pass. My test plan: one defect (Important 1).** Every code and data requirement in the brief, the dispatch and re-forms.md section 7 is met in the built ROM. I checked each named risk with its own check, on bytes and on independent disassembly.

| # | Risk | Check I ran | Result |
|---|---|---|---|
| 1 | Routines: registers, stack, lr, Thumb bits, pools | Compared each new routine line by line against the vanilla code it re-encodes (0x080172B0, 0x08017306) and the callers (0x080086A2, 0x0800876A, 0x08007F0A, 0x08008D12). Read the pool words and the vtable from the ROM | Pass. apply `push {r4,lr}` / `pop {r4,pc}`. tick `push {r3,r4,r5,lr}`, both exits reach `pop {r3,r4,r5,pc}` at 0x08863E5C. hud `push {r4,r5,r6,lr}` / `pop {r4,r5,r6,pc}`, r7 untouched. The gate has no push, pop or bl, so lr stays 0x08007F11 on both `bx` exits (Ruling 15 met by never touching lr). Odd pointers: vtable 0x08863D95, 0x08863DEF; rom:0x1D99CC = 0x08863E5F; rom:0x8E8C = 0x08863E99; pool 0x080265C5, 0x0801353D. The pool at 0x08863ED4 is 4-aligned. The farthest load (0x08863D98) uses offset 0x4E words. 0x080265C4 reads only r0 and r1, so `bx r2` as the call register is safe |
| 2 | Flag 195 gate | Read 0x08003E42 in the base ROM and rom:0x6F7E54 = `90 0E 00 03`. Read the gate in Ghidra and by hand | Pass. It loads 0x03000F5C, and `lsl r2,r2,#28 ; bpl` tests bit 3. The table literal is 0x088637AC (relocated), never 0x081D967C. No map-word read. Every failing path reaches `ldr r2,=0x0801353d ; bx r2` with r0 and r1 unchanged. Only entry 5 has +0 bit 0 set and +4 != +5 (all 23 relocated entries dumped), so base (entry 2) and SSJ2 (entry 22, +4 = +5 = 2) take the vanilla path |
| 3 | Form object | Disassembled apply and tick, resolved the vtable, read the save with `log2_save.py info` | Pass. Three `add #0x14`. Speeds 0x3FE00000 / 0x40400000, as Super Saiyan. Step 0x199A = 2 x 0xCCD. The tick matches 0x08017306-0x08017374 instruction for instruction, except the pool value and the local bx stubs, so the EP 0 path sends message 0x24 exactly as Super Saiyan does. Test save END 71 + 20 = 91, and the ceiling 100 + 20 = 120 <= 127. rom:0x17000-0x174FF equals the base, so 0x080174A0 is untouched |
| 4 | HUD hook | Byte diff of rom:0x8D14-0x8D1D, Ghidra listing of 0x08008D10, base disassembly of 0x08008D2E-0x08008E6A. Scan of rom:0x0-0x3FFFF for pc-relative `ldr` that reach 0x08008E8C, for `b`, `bcc` and `bl` targets in 0x08008D14-0x08008D2D, and of the 8 MB for aligned words in that window | Pass. Bytes are `28 1C 19 F0 08 F8 01 1C 07 E0` (re-forms.md item 7). The only loader of rom:0x8E8C is 0x08008D12. No branch from outside 0x08008D10-0x08008D2D lands in the rewritten window, and no aligned word points into it. Z2 shows only when the ability id is 12 and record +8 is 22. Otherwise it returns `[r6]` or `[r6+4]`, as vanilla. The caller reloads r0, r2 and r3 at 0x08008D2E and first writes r6 at 0x08008DA0, so no live register is lost. Z2 pointers 0x08863994 and 0x08863B94 are 4-aligned and equal the approved .bin files. A jump into the window through a computed address would not appear in these scans |
| 5 | Base 8 MB diff, poc against gi | Full byte diff of rom:0x0-0x7FFFFF. Aligned words equal to 0x081D9900 | Pass. 20 changed runs: the 17 literals (each `7C 96 1D` to `AC 37 86`), rom:0x8D14-0x8D1D, rom:0x8E8C and rom:0x1D99CC. rom:0x42F0 is unchanged (0x08800000, the gohan_gi copy). The ability table has only two literal words, rom:0x8024 (unchanged) and rom:0x8E8C. The expansion writes lie in rom:0x8637AC-0x863EFF, which was all 0xFF in the gi build |
| 6 | Rage unchanged | Relocated entry 4 against base rom:0x1D96CC; set table word for set 58 (index 58 - 7); Rage vtable and methods; the 0x42F0 copy | Pass. Entry 4 `03 3a 3d 0c 02 02 ... e4 21 00 03` is identical. The set 58 word is 0x082AB508 in both. rom:0x24E4C-0x24E63 and rom:0x170D8-0x1719F are identical. The 0x42F0 copy equals the base table, so ext 73 (0, 58) still finds entry 4 |
| 7 | Test independence | Compared all 166 lines of `scripts\one-time\2026-10-16-task-6-ssj2\ghidra_t6.txt` with the build bytes by script (0 mismatches). Read Ghidra's text and the test's expected text side by side (not a scripted compare; Ghidra spells some mnemonics differently, for example `ldrsh`). Decoded 6 instructions by hand | Pass for this build. Ghidra's instruction list agrees with `thumb_dis.py` on every routine I read. Hand decodes: 0x08863E7C `12 07` = `lsl r2,r2,#28`; 0x08863E7E `09 D5` = `bpl 0x08863E94`; 0x08863E92 `18 47` = `bx r3`; 0x08863E78 `1C 4A` = pool 0x08863EEC = 0x03000F5C; 0x08863DD2 `00 F0 7E F8` = `bl 0x08863ED2` (`bx r2`); 0x08008D16 `19 F0 08 F8` = `bl 0x08021D2A`. A shared encoder and decoder bug is unlikely to pass all three checks |
| 8 | Report concerns 5 and 6 | Base disassembly of test 0x080134F2, action 0x0801353C, state 0x23 (0x080155A8, 0x0801563C) and 0x08014D58 | Matches vanilla and the dispatch. See Minor 4 for reader-facing effects, and Important 1 for the cooldown effect on me test plan |

**Cannot verify (static review only):**
- In-game behavior. My test in the report are the proof. The STR, POW and END numbers in the plan (90, 78, 91) match the save (70.56, 58.28, 71.39, each + 20).
- The aura sound count. State 0x23 enter (0x080155C2) starts sound 55 again while the Super Saiyan sound plays. Then SSJ leave stops it and SSJ2 enter starts it. Vanilla base to SSJ also starts sound 55 twice, so the step is no worse than vanilla. I can listen after a revert from Super Saiyan 2 to confirm that the hum stops.
- ext 42 and ext 43 in the Cell scene stay LIKELY, as the report says. I spot-checked the Rage methods (0x080170D8-0x0801718A) and state 9 (0x08011D38-0x08011D6C). They call only the speed helper and the sound routines, as claimed.

## Strengths

- The tick is a faithful re-encoding. Only the pool value and the call stubs differ from 0x08017306, so the revert path is the vanilla one.
- The gate is a leaf with two tail jumps. This removes the lr risk instead of managing it.
- Fail-closed checks run before any write: 17 literals, rom:0x42F0, rom:0x1D99CC, rom:0x8E8C, the full 30-byte HUD block, and the gohan_gi entries 2 and 5. The test proves that the ROM is unchanged on each failure.
- The test readers derive values from code (bonus from the `add` before each `strb`, drain from the tick pool), not from the patch module constants.
- A Ghidra import of the build backs the in-house decoder, and its bytes match the shipped ROM.
- Files are LF, with no byte order mark and no em or en dashes. The RE-BIBLE lines carry tags, labels and the T6 source.

## Issues

### Critical

None.

### Important

1. **My test plan will report a false failure on Review Focus 3.** `docs\tasks\2026-10-16-task-6-ssj2\task-6-report.md`, my test 4 step 4 and my test 3 step 7.
   - What: my test 4 step 2 enters Super Saiyan, and the transform state adds 1280 to the cooldown (re-forms.md section 2 item 9). Step 3 reverts. Step 4 then says "press B twice" at once. The untransformed test needs cooldown 0: `08013514 ldr r0,=0x086db27c`, then `08013522 ldr r2,[r0,#0xc]` gets struct 0x03000E90 (rom:0x6DB288 holds it), and `08013526 ldr r2,[r2,#0x8] ; 08013528 cmp r2,#0x0` refuses while +8 is not 0. Only the base tick lowers it, by 1 per frame. So the first B press plays the refusal sound for about 21 s.
   - My test 3 step 7 has the same fault after Super Saiyan 2 (2560 frames, about 43 s). Its EP is also 0 after step 6, and the test needs EP >= 10.
   - Why it matters: the dispatch made this plan a deliverable. The refusal reads as "the gate is broken" on a Review Focus item, and it can send me after a bug that does not exist.
   - Fix: in my test 4 step 4, wait in base form until the "Z" is bright, or set 0x03000E98 to 0 first. In my test 3 step 7, set 0x03000E98 to 0 and 0x03000EA0 to 134 first. Plan text only. No code change.

### Minor

1. **The assembled size is not asserted.** `scripts\permanent\patches\ssj2_form.py:362-365`. The size comes from a first pass at 0x08000000. The second pass runs at the real address. Pool padding depends on the address mod 4. Today `alloc` aligns to 4, so the sizes match. If the alignment ever differs, `rom[code:code + size] = blob` with a different length resizes the bytearray and shifts every later byte. Fix: `if len(blob) != size: raise ValueError(...)`.
2. **No range checks for `ldr rN,=`, `b` and `bl`.** `ssj2_form.py:294-298` and `312-317`. The conditional branch checks its range, but these do not. A longer routine could silently encode a wrong pool offset or branch. Today the farthest pool load is 0x4E words and the tests decode every routine, so the current build is safe. Fix: raise when the pool word offset is outside 0-255, `b` is outside -1024 to 1023 halfwords, or `bl` is outside +/-4 MB.
3. **apply does not check set 159 directly.** `ssj2_form.py:340-341`. It checks that gohan_gi set entries 2 and 5 to 157 and 158. It does not check that the set table resolves id 159 (`alloc.notes["gohan_gi"]["set_159"]`). The test `test_entry22_set_is_gi_ssj2_with_anims_9_and_21` covers this at test time, so the risk is low. Fix: one `_expect` on the set table word at index 159 - 7.
4. **Reader-facing effects of the stepping rule (report concerns 5 and 6).** These match vanilla mechanics and Rulings 10 and 11. They are not defects, but I should hear them once. (a) After flag 195, with EP >= 10, B in Super Saiyan always steps up. A direct revert from Super Saiyan to base is possible only when EP is under 10. Otherwise the player leaves the form through Super Saiyan 2. (b) The step uses state 0x23 again. Its tick adds 8 per frame for 160 frames. Only the base tick removes cooldown, so the wait after any trip through Super Saiyan 2 is 2560 frames, about 43 s, against about 21 s for Super Saiyan alone. Fix: none required. Add (a) to me test notes so that it is a known choice.
5. **The decoder cross-check lives outside the suite.** The Ghidra comparison is a one-time artifact (`scripts\one-time\2026-10-16-task-6-ssj2\ghidra_t6.txt`). Future edits to CODE are checked only by `thumb_dis.py` and the expected text, both from the same author. Fix: none now. On any CODE change, re-run `scripts\one-time\2026-10-16-task-6-ssj2\gh6.sh` and compare.

## Assessment

**Task quality: Needs fixes (my test plan text only). The code and the ROM are approved.** The patch matches re-forms.md section 7 and Rulings 10-16 on every byte I checked, Rage and the shared Super Saiyan pool are untouched, and the new Thumb code is sound on register use, stack, lr and Thumb bits. Fix Important 1 in the report's my test plan before I run it. The Minors are hardening items and my notes.
