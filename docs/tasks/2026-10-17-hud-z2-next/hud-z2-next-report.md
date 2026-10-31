# ssj2_form: the Z2 icon shows what B does next (report)

Date: 2026-10-17. Brief: `docs\tasks\2026-10-17-hud-z2-next\hud-z2-next.md`.

Labels: **CONFIRMED** = proved here with quoted code, data or a test. **LIKELY** = strong evidence, not proved. **SPECULATIVE** = a guess.

## Status

Done. Tests: **93 OK** (83 before, 10 new). Check ROM: `archive\builds\log2_poc_r6_hud.gba`, SHA-1 `588173e8da0f1b86a6cd59defe2e4071f555fa7e`.

| Ask | Result |
|---|---|
| 1. HUD shows Z2 in entry 22 or when the gate would send 0x23, one shared predicate | Done. `step_ok` is called by `gate` and `hud` |
| 2. WHEN the HUD hook runs | Every frame. CONFIRMED. No lag, no redraw hook needed |
| 3. Tests | 10 new behavior tests through a Thumb interpreter, 93 OK |
| 4. Check ROM and build log | Built, r5-style line appended |
| 5. re-forms.md and RE-BIBLE | Updated |

---

## 1. Changes (file:line)

`scripts\permanent\patches\ssj2_form.py`
- 12-16: header Method items 3 and 4 describe `step_ok` and the new HUD rule.
- 154-180: new `step_ok` predicate (listing below).
- 181-196: `gate` calls `step_ok`: `push {lr} ; bl step_ok ; pop {r3} ; mov lr,r3`, then the same two bx tail jumps.
- 197-235: `hud` keeps the vanilla pick and adds: ability 12 and (record +8 = 22, or `step_ok`) gives the Z2 pair. Bright or dim stays on the ability test result.
- 313-316: the assembler encodes `mov lr,rN` (format 5, `0x4686 | rN << 3`) and `bx lr` (`0x4770`). Both checked by thumb_dis.
- 415: `step_no` is left out of `alloc.notes`. `step_ok` is exported.

`scripts\permanent\tests\test_ssj2.py`
- 12-14: docstring names the interpreter.
- 141-153: `gate_parts` follows the gate's `bl` and reads TABLE, flag, bit and EP from `step_ok`. The vanilla exit literal still comes from the gate.
- 183-195: `EXPECTED` gains `step_ok`. `gate` and `hud` are updated. 204: `normalized` names `STEP_OK`.
- 214-372: new interpreter `Cpu` (runs thumb_dis text, never the encoder) plus `cpu_state`, `run_gate`, `run_hud`, `vanilla_icon`.
- 422-435: `test_gate_keeps_lr` now runs both exits and checks lr, sp, r0, r1 and r4-r7 at the exit. `test_gate_does_not_test_map_word` also reads the predicate.
- 437-513: new tests (see section 4).

Docs
- `docs\research\re-forms.md` 118-125: section 4, "The draw runs every frame, and so does the icon pick", with the caller chain. 167: section 6 item 5 (HUD rule). 209-211: section 7 table rows for `step_ok`, the gate and the HUD icon. 245-246: section 9 question 2 answered, with the LIKELY mid-step side effect.
- `docs\RE-BIBLE.md`: `HZ2` source added (line 27). New rows 219 (HUD runs every frame), 230 (Z2 rule, `step_ok`, r6 offsets), 231 (mid-step side effect, L). Row 229 points to the rule row and states what `log2_poc.gba` holds. New decision row (2026-10-17). Open question row on Z2 amended.
- `docs\build-log.md`: the builder's own line plus the r5-style annotated line.

Backups of the five edited files before the change: `archive\2026-10-17-review-snapshots\2026-10-17_hud-z2-next\`.

## 2. Predicate routine listing (thumb_dis, r6 build)

```
0886965e step_ok: ldrb r2,[r0,#0x8]
                  lsl r3,r2,#2
                  add r2,r3,r2
                  lsl r2,r2,#2
                  ldr r3,=0x08868fac      ; relocated appearance table
                  add r2,r2,r3            ; r2 = entry
                  ldrb r3,[r2,#0x0]
                  lsl r3,r3,#31
                  beq step_no             ; not transformed
                  ldrb r3,[r2,#0x4]
                  ldrb r2,[r2,#0x5]
                  cmp r2,r3
                  beq step_no             ; +4 == +5: no step target
                  ldr r2,=0x03000f5c
                  ldrb r2,[r2,#0x0]
                  lsl r2,r2,#28
                  bpl step_no             ; flag 195 clear
                  mov r3,#0x4
                  ldsh r2,[r0,r3]
                  cmp r2,#0xa
                  blt step_no             ; (s16) EP < 10
                  mov r2,#0x1
                  bx lr
0886968c step_no: mov r2,#0x0
                  bx lr
```

Contract: r0 = record in, r2 = result. Keeps r0 and r1, uses r3, no stack, returns with `bx lr`.

```
08869690 gate:    push {lr} ; bl step_ok ; pop {r3} ; mov lr,r3 ; cmp r2,#0x0 ; beq gate_vanilla
                  ldr r2,[r1,#0x0] ; ldr r3,[r2,#0x28] ; add r3,r3,r2 ; add r0,r1,#0 ; mov r1,#0x23 ; bx r3
         gate_vanilla: ldr r2,=0x0801353d ; bx r2
088696ae hud:     ... bl stub_r1 (r0 = test) ; cmp r5,#0xc ; bne hud_vanilla ; ldrb r1,[r4,#0x8] ; cmp r1,#0x16
                  beq hud_z2 ; add r5,r0,#0 ; add r0,r4,#0 ; bl step_ok ; add r0,r5,#0 ; cmp r2,#0x0 ; beq hud_vanilla
         hud_z2:  ldr r1,=Z2 ; cmp r0,#0x0 ; bne hud_done ; ldr r1,=Z2_DIM ; b hud_done
```

## 3. WHEN the HUD hook runs: every frame (CONFIRMED)

1. **Main loop** 0x0801F294 (called from 0x080001F8). One iteration per frame assumes IRQ mirror bit 0 is VBlank, the GBA convention, not traced here: `ldr r5,=0x03000e1c ; ... ldr r0,[r5,#0x0] ; ldr r1,[r0,#0x0] ; ldr r2,[r1,#0xc] ; add r1,r2,r1 ; bl 0x8021d2a`, then `bl 0x8020bd8`, `bl 0x8020d40` (frame wait: `08020d6e swi 0x2` until the IRQ flag), `bl 0x801eefc` (keys), then state +0x14 and loop. The current state's vtable +0xC runs once per frame.
2. **Field state.** In captures 01 and 02 (`scripts\one-time\2026-10-16-first-probes\captures\01-gohan-base`, `02-gohan-gi`), `[0x03000E1C]` has vtable 0x08023884, and its +0xC is 0x08004EA8. That routine ends with `08004ec6 ldr r0,=0x081d9cb0 ; ldr r0,[r0,#0x4] ; bl 0x8006ad8`. The ROM word at 0x081D9CB4 is 0x03001120.
3. **Draw pass** 0x08006AD8 on list 0x03001120: it calls each object's vtable +0xC (`08006afa ldr r2,[r1,#0xc]`), sorts the visible ones, then calls +0x10: `08006bf8 ldr r1,[r0,#0x0] ; ldr r2,[r1,#0x10] ; add r2,r2,r1 ; mov r1,sp ; bl 0x8021d2c`.
4. **HUD object.** Constructor 0x08008B14 stores vtable 0x0802408C (`08008b3e ldr r0,=0x0802408c ; ... str r0,[r4,#0x0]`). 0x080040C6 and 0x0800C630 call it and add the object to 0x03001120 through 0x080068B8: `080040d6 ldr r0,[r4,#0xc]` with r4 = 0x081D952C, and `0800c636 ldr r0,[r6,#0x4]` with r6 = 0x083ED1B8 (loaded at 0x0800C5B4, no other write to r6 before 0x0800C636). Both ROM words are 0x03001120. Vtable words (base-relative): +0xC = 0x080264A8 (`mov r0,#0x1 ; bx lr`, always visible), +0x10 = 0x08008BEE (the HUD draw). Captures 01 and 02 hold the HUD object in list 0x03001120 (index 2 and 14).
5. **Icon pick on every draw.** From 0x08008BEE to 0x08008D10, every branch is forward and stays inside the routine. The pick at 0x08008D10 (the hook) runs before the redraw-key compare `08008d6e ldr r2,[r4,#0x1c] ; cmp r2,r1`. A new icon pointer fails the compare and forces a redraw in the same frame.

Result: the icon follows EP, flag 195 and the form in the frame they change. **No redraw hook was added.**

Search shapes used: Thumb BL scan, absolute pointer words, and base-relative vtable words (`base + word`, slots 0-15) over the whole ROM. 0x08008BEE has no BL caller and no absolute pointer. It has one base-relative vtable word (rom:0x2409C, slot +0x10 of 0x0802408C). A call through a computed address would not appear. The capture evidence covers that gap for the field state.

## 4. Tests

New tests in `test_ssj2.py` run the built ROM's code through `Cpu`, a small interpreter of thumb_dis text. Ability tests are stubbed with a scripted result. The flag byte is 0xFF or 0xF7, so only bit 3 can matter.

| Test | Checks |
|---|---|
| `test_hud_z2_in_ssj_when_b_steps_up` | Entry 5, flag set, EP 10, 11, 100: Z2 (test 1), Z2 dim (test 0) |
| `test_hud_z_in_ssj_when_flag_clear` | Entry 5, flag clear: vanilla Z, bright or dim |
| `test_hud_z_in_ssj_when_ep_under_step_cost` | Entry 5, flag set, EP 9, 0, -1: vanilla Z |
| `test_hud_z2_in_ssj2` | Entry 22 with or without flag and EP: Z2 pair |
| `test_hud_vanilla_for_other_forms_and_abilities` | Every other entry 0-21 (other characters' forms, base, Rage) with ability 12; every other ability in entries 5, 22, 2 |
| `test_hud_matches_vanilla_pick_on_the_base_rom` | The interpreter runs the original pick at 0x08008D10 on the base ROM and gets the table icons |
| `test_hud_keeps_r4_to_r7_and_sp` | Caller registers and sp after return |
| `test_hud_icon_never_disagrees_with_b` | 23 entries x flag x EP {-1, 0, 9, 10, 100}: Z2 exactly when the gate sends 0x23 or the entry is 22 |
| `test_gate_steps_only_with_flag_and_ep` | Gate exits for EP 9/10/0x7FFF/-1, flag clear, entries 22, 2, 4 |
| `test_gate_and_hud_share_one_predicate` | The gate's `bl` target is `step_ok`, and the HUD calls the same address |

- Rewritten: `test_gate_keeps_lr` (runs both exits: lr and sp equal entry values, r0 and r1 as the exit needs, r4-r7 kept), `test_gate_does_not_test_map_word` (gate and predicate), `test_new_routines_disassemble_as_expected` (EXPECTED).
- Mutation check (ad hoc, not kept): HUD that ignores `step_ok`, `step_ok` with EP 11, and a HUD with no dim icon each fail at least one new test.
- Whole suite: `py -3 -I -m unittest discover -s scripts\permanent -p "test_*.py"`: **Ran 93 tests, OK**.

## 5. Check ROM

- `LOG_GI_SSJ2=gi_ssj2_v2`, `py -3 -I scripts\permanent\log2_build.py --out archive\builds\log2_poc_r6_hud.gba gohan_gi ssj2_form gohan_portraits`.
- SHA-1 `588173e8da0f1b86a6cd59defe2e4071f555fa7e`. An in-memory build of the same patches equals the file. CONFIRMED.
- Interpreter spot check on the file: entry 5, flag, EP 10: Z2 and gate "message". EP 9: Z and "vanilla". Flag clear: Z. Entry 22: Z2. Entry 2: Z.
- `log2_poc.gba` (345ae98c), `log2_poc_r4.gba` (0fb2a56d) and `log2_poc_r5.gba` (53f6c51a) are unchanged. CONFIRMED by SHA-1.

## 6. Findings for me

1. **Expansion layout shifts by 0x24 bytes.** CONFIRMED. The code block grows from 0x16C to 0x190 bytes. Against r5: gate 0x0886965F to 0x08869691, HUD 0x08869699 to 0x088696AF, portrait block literal (rom:0xBE10) 0x08869700 to 0x08869724. Table, form object, vtable and Z2 icons do not move. No test or script hard-codes these offsets (search: hex literals 0x863-0x867 in `scripts\`; a computed offset would not appear).
2. **Mid-step icon change.** LIKELY. The step state lasts 160 frames, and the record stays in entry 5 until it ends. The Super Saiyan tick drains 8 EP in that time (re-forms.md section 7, Ruling 15). A step that starts with EP 10-17 drops under 10 mid-step. The icon then shows Z for the rest of the step and Z2 again in entry 22. Not seen in play. Not changed: it is my call.
3. **The flag and EP checks now run every frame from the HUD.** CONFIRMED (section 3). Cost: `step_ok` runs once per frame while ability 12 is selected and the record is not in entry 22 (9 to 25 Thumb instructions). Other abilities stop at the id compare.
4. `archive\2026-10-17-review-snapshots\2026-10-17_hud-z2-next\` holds the pre-change copies of the five edited files.
