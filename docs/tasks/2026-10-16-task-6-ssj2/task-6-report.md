# Task 6 report: usable Super Saiyan 2

Date: 2026-10-17.

## Status

**DONE_WITH_CONCERNS.** The build, the code and 57 tests pass. In-game behavior is not yet seen: my test plan below covers it.

| Item | Value |
|---|---|
| Build | `builds\log2_poc.gba` (gohan_gi, ssj2_form) |
| SHA-1 | `86ae697b9b061480bbe3ffebab6e2b63b8e0a524` (logged in `docs\build-log.md`) |
| gohan_gi stage | still `40d66d64dfda1179365b094194083ff828f1b6dd` |
| Tests | 59 OK after the review fix round (35 earlier, 24 new in `tests\test_ssj2.py`). RED run saved in `task-6-red.txt` (ImportError: no `ssj2_form`) |

## Files

| File | What |
|---|---|
| `scripts\permanent\patches\ssj2_form.py` | New. `apply(rom, alloc)`, a small two-pass Thumb assembler and the Thumb source of the 4 routines |
| `scripts\permanent\rom\thumb_dis.py` | New. Thumb decoder over a ROM buffer. It is separate from the encoder, so the tests check the code with independent code. It matches `scripts\one-time\2026-10-18-save-slots\thumb.py` on 900 base instructions |
| `scripts\permanent\tests\test_ssj2.py` | New. 22 tests |
| `docs\RE-BIBLE.md` | 10 new lines (source `T6`), 2 open questions updated |
| `docs\build-log.md` | Build line and a Task 6 section |
| `scripts\one-time\2026-10-16-task-6-ssj2\` | `gh6.sh` (Ghidra import of the build), `ghidra_t6.txt` (its listing), `bible_t6.py` and `fix_t6.py` (BIBLE and report edits), a BIBLE backup |

## What the patch does

1. **Table.** Copies the live appearance table (with gohan_gi's 157 and 158) to rom:0x8637AC. Adds entry 22: `01 9F 3D 0C 02 02 06 00 14 00 00 00 00 01 00 00 78 39 86 08`. Sets entry 5 +4 = 22. Repoints the 17 literals. rom:0x42F0 stays on gohan_gi's unchanged copy at rom:0x800000.
2. **Form.** ROM form object rom:0x863978 points at vtable rom:0x86397C. The words are base-relative and give apply 0x08863D95, tick 0x08863DEF, enter 0x08017377, leave 0x08017393, then 0x080271E1 and 0x08026391 (copied, never called).
   - Apply re-encodes 0x080172B0 with `add #0x14` (+20) on STR, POW and END. Speeds are 1.75 and 3.0, as Super Saiyan. Its own pool, and each BL goes through a local `bx r2` stub.
   - Tick re-encodes 0x08017306 with a step of 0x199A (twice 0xCCD: 1 EP every 10 frames, 6 EP/s). It keeps the state 0x24 skip and the EP 0 revert. The shared pool 0x080174A0 is untouched.
3. **Gate.** rom:0x1D99CC (ability 12 action) = 0x08863E5F. The gate is a leaf (r2 and r3 only, no push, lr untouched). It steps only if all of these hold, then tail-calls player message 0x23: entry +0 bit 0 is set, +4 != +5 (only entry 5), flag 195 is set (0x03000F5C bit 3), and EP >= 10. Otherwise it jumps to 0x0801353D with r0 and r1 unchanged. It reads the relocated table and skips the map word (Ruling 16).
4. **HUD.** rom:0x8E8C = 0x08863E99 and rom:0x8D14 = `28 1C 19 F0 08 F8 01 1C 07 E0`. The hook returns the vanilla icon, or the approved Z2 pair (rom:0x863994 usable, rom:0x863B94 dim) when the ability is 12 and record +8 is 22.

## Confirmed facts (new in Task 6)

| Fact | Label | Evidence |
|---|---|---|
| Only entry 5 has +0 bit 0 set and +4 != +5 | CONFIRMED | All 22 entries read from rom:0x1D967C. Entry 5 `01 3b 3e 0d 04 02 ...`. Every other transformed entry has +4 = +5 (4: 2/2, 7: 6/6, 10: 9/9, 11: 8/8, 14: 13/13, 16: 15/15, 17: 12/12, 20: 19/19) |
| Ability action call shape | CONFIRMED | `08007f06 add r1,r7,#0 ; add r0,r4,#0 ; ldr r2,[r5,#0xc] ; bl 0x8021d2c` (r0 = record, r1 = player, lr = 0x08007F11) |
| Struct 0x03000E90 is fixed | CONFIRMED | rom:0x6F7E54 = `90 0e 00 03` (table 0x086F7E50 +4). Script base `[0x083B5C78+0x20]` = `90 0e 00 03` too |
| Flag n = byte struct +0xB4 + n/8, bit n&7 | CONFIRMED | `08003e42 asr r2,r1,#3 ; add r0,r2,r0 ; lsl r2,r1,#29 ; add r0,#0xb0 ; ldrb r0,[r0,#0x4] ; lsr r2,r2,#29 ; mov r1,#0x1 ; lsl r1,r2 ; and r0,r1`. Flag 195 = 0x03000F5C bit 3 |
| Form objects are set by one init routine; nothing compares them to a constant | CONFIRMED (shape: aligned words) | `080232e4 ldr r1,=0x030021e0 ; ldr r0,=0x08024004 ; str r0,[r1,#0x0] ; ...` for the 5 vtables. Aligned ROM words equal to 0x030021D8-0x030021F8 or to the 5 vtables: only the pool 0x08023304-0x08023318 and the appearance table. A compare built from a computed address would not appear |
| SS and Rage enter start sound 55; leave stops it | CONFIRMED | `08017378 ldr r0,=0x086f7e50 ; mov r1,#0xa5 ; ldr r2,=0x080e15b0 ; lsl r1,r1,#2 ; add r1,r1,r2 ; ldr r4,=0x5c4 ; ... bl 0x801fc9c`. Rage `0801715a` is the same. 0x0801FC9C fills a free 0x40-byte channel. SAV doc: +0x5C4 is the sound object |
| Rage has no aura object attached to the player | CONFIRMED for the form methods, ext 73, state 9 and ext 46, 47, 49; LIKELY for ext 42 and ext 43 | Rage apply, tick, enter and leave make no object. ext 73 handler 0x0800A8EC: leave, reverse lookup, get_set, message 0, apply, enter only. Cell scene 0x083EA33D-0x083EA36F: `ext_49(20)` music, `ext_46(55)`, `ext_57(0,9)`, `ext_42(10)`, `ext_16`, `ext_46(23)`, `ext_46(20)`, `ext_47(55)`, `ext_73(0,58)`, `ext_43(10)`. ext 42 makes a screen-wide palette object (below). ext 43 makes a 12-byte scene task (vtable 0x0802545C, +8 = 10; `08009bac ldr r1,=0x0802545c ; str r1,[r0,#0x0] ; str r4,[r0,#0x8]`), not traced, LIKELY a wait |
| ext 46 / 47 = start / stop sound n; ext 49 = music n | CONFIRMED | `08009c0c ldr r1,=0x080e15b0 ; lsl r3,r0,#1 ; add r0,r3,r0 ; lsl r0,r0,#2 ; add r1,r0,r1 ; ... bl 0x801fc9c` (ext 46), same with `bl 0x801fc22` (ext 47); ext 49 indexes 0x081D4B2C by 20 and calls 0x08020A4C |
| ext 57 (actor, n) sends message n to the actor and waits | CONFIRMED | `08009fdc bl 0x8009370` (actor), 12-byte command with vtable 0x08025BAC, +8 = n. Command +4 = 0x0800DF60: `ldr r2,[r1,#0x28] ... ldr r1,[r3,#0x8] ; bl 0x8021d2c` |
| State 9 (power up) spawns nothing | CONFIRMED | State object 0x03002174, vtable 0x08025B80 (init `74 21 00 03 80 5b 02 08`). Enter `08011d42 ldr r0,[r1,#0x48] ; add r0,#0xdc ; str r0,[r1,#0x4c]`. Tick `08011d5a cmp r0,#0xa0` then sound 23 (`ldr r1,=0x080e16c4`) and the state end |
| ext 42 (n) copies the BG and OBJ palettes into a 0x40C object | CONFIRMED (code), LIKELY (screen flash) | `08009b6c ldr r0,=0x40c ; bl 0x801f08c`, vtable 0x08024FC4; `0800da84 ldr r5,=0x05000200` DMA |
| Super Namek tick drains EP like Super Saiyan and also regenerates HP | CONFIRMED | `0801741e ldr r1,=0x00000ccd ; add r0,r0,r1`, `0801742a mov r2,#0x29 ; lsl r2,r2,#4` (HP), `08017464 sub r2,#0x1` (EP), `0801740c mov r1,#0x24` |
| New routines disassemble as intended | CONFIRMED | `thumb_dis.py` in the tests and a Ghidra import of the build (`scripts\one-time\2026-10-16-task-6-ssj2\ghidra_t6.txt`). Example: `08863e78 1C4A ldr r2,[0x08863eec] [=03000F5C] ; 08863e7a 1278 ldrb r2,[r2,#0x0] ; 08863e7c 1207 lsl r2,r2,#0x1c ; 08863e7e 09D5 bpl 0x08863e94` and `08008d12 5E49 ldr r1,[0x08008e8c] [=08863E99] ; 08008d14 281C add r0,r5,#0x0 ; 08008d16 19F008F8 bl 0x08021d2a` |

Facts used from Task 4 (re-forms.md) and rechecked on bytes here: the 18 words 0x081D967C (17 plus rom:0x42F0); the 2 words 0x081D9900 (rom:0x8024, rom:0x8E8C), each loaded by one `ldr` (0x08007EF0, 0x08008D12); rom:0x1D99CC = `3d 35 01 08` with no pc-relative loader; rom:0x8D10-0x8D2D as quoted; rom:0x174A0 = 0xCCD.

## Lightning (Rulings 19 and 31)

Rage has no aura object attached to the player (CONFIRMED above, with ext 42 and ext 43 LIKELY). Its lightning lives in the set 58 frames, and the set 159 frames already carry it in blue (Task 5). Task 6 adds no aura code, so Rage stays unchanged. Super Saiyan 2 does not copy the cutscene's screen-wide palette effect (ext 42): vanilla Super Saiyan has none, and it is not part of the form. I can ask for it as an option. If I want a visible aura around Super Saiyan 2 in every animation, that is new sprite work (an effect object or more spark pixels), not a recolor. It is not built.

## Tests (22 new)

- Brief: `test_ssj2_form_values` (+20 x3, drain 0x199A = 2 x 0xCCD), `test_ssj2_gate_reads_flag_195` (Super Saiyan steps only on flag 195; base and Super Saiyan 2 go vanilla), `test_rage_unchanged`.
- Rulings: the END ceiling over all 23 entries, the gate reading the relocated table with EP 10 (>= 9), the gate keeping lr (no push, pop or bl), no map word, only entry 5 steps.
- Data: entry 5 +4 = 22, entry 22 = set 159 with +4 = +5 = 2 and portraits `3D 0C`; set 159 has anims 9 and 21 and slot 0x400; the relocated table equals the live table except entry 5 +4; the reverse lookup still finds 58 at entry 4; the vtable resolves to the intended methods; the Super Saiyan code and pool rom:0x17000-0x174FF are unchanged.
- Fail closed: the 17 literals, rom:0x1D99CC, rom:0x8E8C and rom:0x8D14 held the old values before the write and the new values after. A corrupted literal, action word, HUD literal or HUD byte makes `apply` raise with the ROM unchanged. A missing gohan_gi note also raises.
- The base 8 MB differs from the gohan_gi build only inside the listed site ranges.
- Expected disassembly text for apply, tick, gate, HUD and both stubs, plus the HUD call site. The file build equals the memory build.

## My test plan (mGBA, no save state)

Use `builds\log2_poc.gba` with `test-data\saves\log2_lv40_postcell.sav`. In every slot, Gohan leads with 134 EP, appearance 2, and record +0x14 = 0x7F (transform slot on). Flag 195 is set. Turn off the debug cheat.

**RAM to watch** (from the Task 4 report, re-forms.md section 5):

| Address | Meaning | Expected |
|---|---|---|
| 0x03000E90 (u8) | Leader | 0 (Gohan) |
| 0x03000EA0 (u16) | Gohan EP | Falls 1 every 10 frames in Super Saiyan 2 |
| 0x03000EA4 (u8) | Gohan appearance | 2 base, 5 Super Saiyan, 22 Super Saiyan 2 |
| 0x03000EB0 (u8) | Record +0x14 | 0x7F (bit 5 set) |
| 0x03000E98 (u32) | Transform cooldown | 0 before the first press |
| 0x03000F5C (u8) | Flag byte | 0x0F (bit 3 = flag 195) |
| 0x03001FA8 (u32) | Player object pointer | Read it first, it moves |
| `[0x03001FA8]` + 0x160, +0x161, +0x162 | Live STR, POW, END | Super Saiyan 2: 90, 78, 91 (0x5A, 0x4E, 0x5B) for this save |
| `[0x03001FA8]` + 0x180 (u32) | Form object | 0x030021E0 base, 0x030021EC Super Saiyan, 0x08863978 Super Saiyan 2 |

**My test 3: ki runs out in Super Saiyan 2 (Review Focus 4)**

1. Load slot 2 (East District 439). A fresh load gives cooldown 0 and EP 134: check 0x03000E98 = 0 and 0x03000EA0 = 134. If the Z stays dim with both of those, the map forbids transforming: walk to a field map and try again.
2. Press L until the HUD shows the yellow "Z".
3. Press B. Expected: Gohan powers up to Super Saiyan in the gi. 0x03000EA4 = 5.
4. Press B again. Expected: the step animation plays, then Super Saiyan 2 (set 159, blue sparks). 0x03000EA4 = 22. The HUD shows "Z2". The form object is 0x08863978. STR, POW and END are 90, 78 and 91.
5. Wait without pressing B. Expected: EP falls about 6 a second, twice the Super Saiyan rate. To save time, set 0x03000EA0 to 20.
6. At EP 0, expected: the revert animation plays and Gohan is base again. 0x03000EA4 = 2. The HUD shows the "Z" (dim while the cooldown runs, about 43 s).
7. Optional: first set 0x03000E98 (cooldown) to 0 and 0x03000EA0 (EP) to 134. Why: step 6 left EP at 0 and the cooldown at about 2560 (43 s), and the base form test refuses B while the cooldown is above 0 or EP is under 10. Then repeat steps 3 and 4, and press B in Super Saiyan 2. Expected: a direct revert to base (2), never to 5.

**My test 4: no Super Saiyan 2 before Cell is beaten (Review Focus 3)**

1. Reset and load slot 2 again. This restores cooldown 0 and EP 134 (check 0x03000E98 = 0). In the memory viewer, set 0x03000F5C from 0x0F to 0x07. This clears flag 195 only.
2. Press B. Expected: Super Saiyan (5).
3. Press B. Expected: revert to base (2). Never 22, never "Z2".
4. Set 0x03000E98 (cooldown) to 0. Why: the transform in step 2 added 1280 to the cooldown, and only the base form lowers it, by 1 per frame. With the cooldown above 0, B plays the refusal sound for about 21 s, which looks like a gate failure. Setting it to 0 is faster and exact; waiting in base form until the Z is bright also works. Check that EP 0x03000EA0 is 10 or more. Then set 0x03000F5C back to 0x0F and press B twice. Expected: Super Saiyan, then Super Saiyan 2 (22) and "Z2".
5. Do not save the game after step 1. Reset without saving.

**Optional: the shared hooks for other characters**

1. With Gohan in base form, press L through all four slots. Expected: every ability icon draws as before (the HUD hook's vanilla path).
2. Switch to Goku or Vegeta. The cooldown at 0x03000E98 is one value for the whole party, so set it to 0 first (or wait until the Z is bright). Press B twice. Expected: Super Saiyan, then back to base, as in the vanilla game (the gate passes through).

**My notes: how the stepping behaves**

- With flag 195 set and EP 10 or more, B in Super Saiyan always steps up to Super Saiyan 2.
- B in Super Saiyan reverts to base only when EP is under 10. Otherwise the player leaves the form through Super Saiyan 2 (B again, or EP running out).
- The cooldown after any trip through Super Saiyan 2 is about 2560 frames, about 43 s, against about 21 s for Super Saiyan alone. Only the base form lowers it.

"The Cell fight still forces Rage" cannot be checked from a post-Cell save. The static tests cover it: the relocated entry 4 equals the base entry (`test_rage_unchanged`), and the rom:0x42F0 copy finds set 58 at entry 4 (`test_reverse_lookup_still_finds_rage`).

## Concerns

1. **In-game behavior is unverified.** Everything is checked on bytes and disassembly only. My test above are the proof.
2. **A save made in Super Saiyan 2 stores appearance 22.** Only the patched ROM can load it. An unpatched ROM reads entry 22 past the table, into the EXP table at rom:0x1D9834. Whether the game saves while transformed is still not traced (open question 7).
3. **END 120.** Super Saiyan 2 takes about 44 % of Super Saiyan damage (`0x80 - END`: 8/128 against 18/128). I may want a smaller END bonus. It is one constant (`add #0x14`).
4. **Attacker overflow.** STR and POW are now 120 in Super Saiyan 2. The attack product at 0x0800F974 (`mul r0,r5`) is LIKELY safe only (Ruling 15: the review sampled one descriptor family). Not rechecked in Task 6.
5. **Low EP in Super Saiyan.** With flag 195 set and EP under 10, B reverts to base instead of stepping, as vanilla does. This is a design choice under Ruling 11.
6. **Cooldown.** The step adds about 1280 more to the cooldown, so after Super Saiyan 2 the wait in base form is about 43 s (re-forms.md open question 4).
7. **Map word.** The gate skips the map-allowed word, as vanilla does while transformed (Ruling 16). If a map forbids transforming, Super Saiyan 2 is still reachable there from Super Saiyan.
8. **Process.** The tests were written first and failed on the missing module (`task-6-red.txt`). The expected disassembly text was written from the design before the code ran.

## Review fix round

Review: `task-6-review-report.md` (code and ROM approved, 1 Important, 5 Minor).

| Item | Fix | Proof |
|---|---|---|
| Important 1: my test plan cooldown and EP traps | My test 4 step 4 now sets 0x03000E98 to 0 before B (waiting until the Z is bright also works) and says why. My test 3 step 7 sets 0x03000E98 to 0 and 0x03000EA0 to 134 first. I re-read every step: my test 3 step 1 and my test 4 step 1 now start from a fresh load and check cooldown 0 and EP 134; the optional Goku or Vegeta step clears the shared cooldown first | Plan text only |
| Minor 1: assembled size | `apply` raises if the second pass size differs from the allocated size. All writes now come after that check, so a mismatch leaves the ROM unchanged | `test_code_size_mismatch_raises` (message: "code assembled to 0x16E bytes, allocated 0x16C") |
| Minor 2: range checks | `ldr =` pool word 0-255, `b` -1024 to 1023 halfwords, `bl` +/-4 MB, each raises `ValueError` | `test_assembler_range_checks` (both edges of each limit) |
| Minor 3: set 159 | `_expect` on the set table word for id 159 (through the rom:0x959C literal) against `alloc.notes["gohan_gi"]["set_159"]` | New case in `test_apply_fails_closed` (message: "rom:0x8637A8 is 00000000, expected 9c338608") |
| Minor 4: reader-facing stepping effects | "My notes: how the stepping behaves" in the plan | Plan text only |
| Minor 5: Ghidra check outside the suite | No change. On any change to CODE, re-run `scripts\one-time\2026-10-16-task-6-ssj2\gh6.sh` and compare | None |

- Rebuild: `builds\log2_poc.gba` SHA-1 `86ae697b9b061480bbe3ffebab6e2b63b8e0a524`, the same as before. No ROM byte changed.
- Suite: 59 tests OK (2 new).
