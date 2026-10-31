# Study: the form cooldown carries over to the next fighter

Study only. No ROM was built, no patch module was written, and no build list was changed.

Labels: **C** = CONFIRMED (bytes, listing or interpreter run quoted), **L** = LIKELY, **S** = SPECULATIVE.

---

## SHIPPED and PENDING

The study answers the four questions of the brief. Nothing goes into a build until I say yes.

**SHIPPED**

| Ask (my words) | Result |
|---|---|
| "Can you check the code, it's a bit odd" | Cause found. The transform cooldown is one counter for the whole party, not one per fighter. The swap code never clears it (C) |
| Where the cooldown lives | Save struct +8, u32 at `0x03000E98` (IWRAM), before the first character record (C) |
| Why it carries across fighters | Relay = script `ext 70` (`set_leader` + `appearance_revert`). Neither touches struct +8. A transformed fighter's tick does not lower the cooldown, so it is still about 0x500 when the next fighter takes control (C code, L in game) |
| Vanilla or ours | **Vanilla.** The same bytes in the base ROM, r38 and r39. HUD v2b keeps the vanilla rule on purpose (C) |
| Smallest fix | Trial module design `relay_cooldown`: one table word plus a 28-byte wrapper that clears the cooldown after `ext 70`. Interpreter proof on r39 and on the base ROM (C, not in game) |
| Bible rows | `scripts\one-time\2026-10-24-form-cooldown\bible_rows.md`, tag FCD, sections 6 and 13 |

**PENDING**

| Item | Who does the next step |
|---|---|
| Yes or no for the trial module `relay_cooldown` | Me |
| A trial slot: `build_list_trial.txt` holds `celljr_fight` as its one trial line, and another task owns that file | Me, after `celljr_fight` is decided |
| Menu swaps too? Switch Characters keeps the cooldown in vanilla. The proposed fix does not change that | Final decisions |
| Clear at every scripted leader change, or only when the leader really changes (variant B below) | Final decisions |
| In-game check of the cause and of the trial (steps below) | Me, or an emulator run |

---

## Root cause

The game keeps one transform cooldown for all six characters.

- **Where (C).** Save struct `0x03000E90` +8 = `0x03000E98`, a u32. Character records start at struct +0xC, 0x1C bytes each (base tick `@0x0801704C`-`@0x08017054`: `lsl r3,r1,#3 ; sub r1,r3,r1 ; lsl r1,r1,#2 ; add r1,r1,r0 ; add r1,#0xc`). No record holds a cooldown.
- **The gate (C).** Abilities 11 (Namek) and 12 (Saiyan) share the test `@0x080134F2`:

  ```
  08013514  ldr r0,=0x086db27c     ; table word +0xC = 0x03000E90
  08013522  ldr r2,[r0,#0xc]
  08013524  mov r0,#0x1
  08013526  ldr r2,[r2,#0x8]       ; cooldown
  08013528  cmp r2,#0x0
  0801352a  beq 0x8013530          ; 0: go on to the EP >= 10 check
  0801352c  mov r0,#0x0            ; else: refused
  ```

- **Who raises it (C).** Saiyan transform state 0x23 anim `@0x080155EA`-`@0x080155EE` (`add r3,#0x8 ; str r3,[r2,#0x8]`, every frame up to the frame 0xA0 callback: about 1280). Namek transform state 0x25 anim `@0x0801562E`-`@0x08015632` (`add r2,#0x14`, while its counter is below 0x40: about 1260).
- **Who lowers it (C).** Only the base form tick `@0x08017028`: `@0x08017034 sub r2,#0x1 ; str r2,[r0,#0x8]`, 1 a frame, down to 0. That is about 21 s at 60 fps.
- **The freeze (C).** The transformed ticks (Rage `@0x0801710E`, Super `@0x080171E4`, Super Saiyan `@0x08017306`, Namek `@0x08017400`) never call the base tick and never write struct +8. While the winner stays transformed, the cooldown stays at about 0x500.
- **The swap (C).** The relay records decode to `push 2 ; ext 70` with the call at `rom:0x3E9DFB` (to Vegeta) and `push 3 ; ext 70` at `rom:0x3E9E5B` (to Trunks), each after `ext 139 (50000)`. Piccolo gets the first Jr with `push 1 ; ext 70` at `rom:0x3E9D1A`. ext 70 `@0x0800A784`:

  ```
  0800a784  push {r3,lr}
  0800a786  bl 0x800a680           ; set_leader
  0800a78a  ldr r0,=0x083b5c78
  0800a78c  ldr r0,[r0,#0x20]
  0800a78e  bl 0x8003ed4           ; appearance_revert
  0800a792  pop {r3,pc}
  ```

  Neither callee reads or writes struct +8 (cooldown sweep below). So Vegeta and Trunks inherit the last fighter's cooldown.

**Proof that the sweep is complete enough (C for the shapes, L for completeness).** `cd_sweep.py` tracks constants through every Thumb function of the codemap, with two join rules. All 27 ROM tables that hold `0x03000E90` resolve. Both shapes find the same 8 accesses in base, r38 and r39: 3 writers (above), and readers in those writers, the test `@0x08013526` and the HUD `@0x08008D34`. Control: the known test reader appears. Not covered: ARM code, a struct pointer passed in as an argument, the 0x164-byte slot load copy, and patch blobs (read by source instead).

**Bible correction.** The R28 row says the cooldown has one reader. It has two: the test and the HUD draw (cooldown pixels).

**Interpreter proof of the symptom (C, not in game).** `fix_proof.py` runs each ROM's own ability 12 test word for Vegeta after the swap (record 2, entry 9, EP 120, map combat word 1, `flag:149` set):

| Cooldown at the test | Base ROM | r39 |
|---|---|---|
| 0x500 (the winner transformed) | 0 (refused) | 0 (refused) |
| 1 | 0 | 0 |
| 0 | 1 (allowed) | 1 |

---

## Vanilla or ours

The carry-over is vanilla LoG II behavior. The fix I am a new trial module, not `bf_ki_pool` or `bf_hud`.

- **Bytes (C).** The test, the three writers, `set_leader` and ext 70 are byte equal in base, r38 and r39. The ext 70 table word `rom:0x3B5E40` is `0x0800A785` in all three. No patch module names that word.
- **HUD v2b keeps the rule (C).** The r39 pool tick saves the cooldown, runs the base tick for EP regeneration, then stores the old value back:

  ```
  0890a07e  ldr r4,[r4,#0x8]       ; cooldown
  0890a080  ldr r3,=0x08017029     ; base tick
  0890a082  bl 0x890a1e0
  0890a088  ldr r0,[r0,#0x4]
  0890a08a  str r4,[r0,#0x8]       ; cooldown kept
  ```

  The net effect equals the vanilla freeze. Also, Vegeta and Trunks at the Cell Games use the Super form (`0x030021E8`), which is not a pool form, so the pool code does not run for them.
- **bf_hud (C).** It changes only the cooldown pixel counts table `rom:0x3B5BE0`, from 0, 8, 14, 18, 20 to 0, 7, 13, 18, 20. That is a look change.
- **S:** the v2b HUD may make the cooldown easier to see, which could be why it reads as new.

---

## Proposed fix: trial module `relay_cooldown`

The fix clears the cooldown each time a script hands control to a fighter with `ext 70`. It uses one pointer-level hook, so no vanilla code byte changes.

**Bytes (C, assembled with `patches.ssj2_form.assemble`, decoded with `thumb_dis`).**

- New wrapper, 28 bytes, at an allocator address (the proof used the sample `rom:0xF783C0`, the first word after the last used byte of r39). The bytes do not depend on the address (relative BL, own pool):

  ```
  10b5044b00f005f80349496800228a6010bd184785a70008507e6f08
  ```

  ```
  push {r4,lr}
  ldr r3,=0x0800a785     ; vanilla ext 70
  bl via_r3              ; set_leader, appearance_revert (r0 = its result)
  ldr r1,=0x086f7e50
  ldr r1,[r1,#0x4]       ; save struct 0x03000E90
  mov r2,#0x0
  str r2,[r1,#0x8]       ; cooldown 0
  pop {r4,pc}
  via_r3: bx r3
  .word 0x0800a785, 0x086f7e50
  ```

- Hook: ext op table word `rom:0x3B5E40` (table `0x083B5D28` + 4 x 70), from `85 A7 00 08` to (wrapper address + 1), little endian.
- Why the table word is a safe hook (C). The script VM reads the handler straight from the ROM table each time. There is no RAM copy and no bound check. Six dispatch variants load the same pool literal (`rom:0x921C`, and `rom:0x92DC` for `@0x08009224`):

  ```
  08009226  ldr r2,[r1,#0x0]       ; script pc
  0800922a  ldrb r0,[r2,#0x0]      ; ext op number
  08009230  lsl r5,r0,#2
  08009232  ldr r0,=0x083b5d28     ; ext op table (ROM)
  08009234  ldr r1,[r0,r5]         ; handler word
  08009236  add r0,r4,#0           ; r0 = script context
  08009238  bl 0x8021d2a           ; call_via_r1
  0800923c  ldr r0,[r4,#0x0]       ; handler result not used here
  ```

  The second table `0x083B5F70` (+0x248) is called after the handler with the same op number. The hook does not change it.
- Interpreter run on r39 and on base (C): with the wrapper run first, the cooldown is 0 at the test and the test returns 1. The handler result in r0 is kept (stub value 0x1234 comes back).

**Module rules (from the existing patch modules).**

1. Check before the first write: word `rom:0x3B5E40` = `0x0800A785` and ext 70 body `rom:0xA784` = `08b5fff77bff9d48006af9f7a1fb08bd`. Else refuse.
2. New space must be 0xFF and named by no ROM word. A second run raises.
3. Tests: the interpreter run of `fix_proof.py` (cooldown 0x500, wrapper, test returns 1), the r0 pass-through, and a byte pin of the hook word.
4. Build through a trial list line after the current trial is decided. Do not touch `build_list_trial.txt` while `celljr_fight` holds it.

**Variant B: clear only on a real leader change.** 40 bytes. It reads the leader byte (struct +0) before and after the vanilla handler and clears only when they differ. Interpreter runs on r39 and base, with a stub that writes the new leader (C): leader 1 to 2 clears 0x500 to 0; leader 0 to 0 keeps 0x500.

```
10b5074c64682478064b00f008f8044949680a78a24201d000228a6010bd1847507e6f0885a70008
```

**Why not one cooldown per character.** It needs a field per record, but the save format is frozen (no new save fields). It also needs new reads in the vanilla test and the HUD draw (`@0x08008D34` is inside vanilla code), so it needs code byte changes, not pointer hooks. Larger and riskier for the same visible result in the relay.

**Risks and blast radius.**

| Risk | Assessment |
|---|---|
| Every scripted `ext 70` clears the cooldown, not only the relay | 18 decoded base sites plus 6 r39 expansion copies (`ext_sites.txt`): chamber entry and exit, Vegeta and Trunks exit, Trunks Super Saiyan unlock, "Me? Fight Cell?", the Cell Jr relay, post-Cell, `chamber_spar`. Effect: the leader a story scene picks starts ready to transform. Harmless: revert ignores the cooldown (`@0x0801350C`: +0 bit 0 set returns 1 before the cooldown read), and the Super Saiyan 2 `step_ok` does not test it (C) |
| Same-leader `ext 70` (for example `ext 70 (0)` while Gohan leads) also clears it | Harmless as above. Variant B avoids it |
| ext 115 = `set_leader` with no revert (word `rom:0x3B5EF4`) is not hooked | Its one cleanly decoded site is `push 1 ; ext 115` at `rom:0x3D457E`, after a warp to map 7,16. No relay uses it (C for that site, S for the other byte pairs) |
| Switch Characters in the menu keeps the cooldown | `set_leader` has one BL caller (ext 70) and one table word (ext 115). Switch Characters `@0x08011172` does not call it (C). Menu behavior stays vanilla. Final decisions if it should change |
| HUD bar does not update | The HUD caches the cooldown index at HUD +0x15 and repaints when it differs (HKP row), so the bar clears on the next frame (C code, L in game) |
| Saves | The cooldown is inside the 0x164-byte slot copy, so it is saved today. The fix only writes a value. No format change (C) |
| Allocation | The fix needs 28 bytes (40 for variant B) of free expansion space. The allocator picks it; `0xF783C0` was only a sample (C) |

---

## In-game check (needs an emulator run)

The cause and the fix are proved in code and in the interpreter. They are not yet seen in play.

**Save states read (`states_cd.txt`, L).** No state covers Vegeta's or Trunks's first frame after a relay. `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr.ss2` (map 14,1,1, `flag:194` set, Gohan leads in entry 5) holds cooldown 0x461. So a nonzero cooldown is alive in Gohan's turn, as a global counter predicts. The same 0x461 is in the r27-r38 state copies with Gohan leading. Its origin is not traced: the cooldown is inside the saved 0x164 bytes, so it may come from the save lineage. Gohan is not blocked by it: in the r28 stretch his test returns 0 for entry 5 anyway, and the Super Saiyan 2 step does not test the cooldown.

1. Use a Cell Games save before the Jr fights (for example `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr.sav`, slot 3).
2. As Piccolo, transform to Super Namek and win the Jr fight while transformed.
3. On Vegeta's first controlled frame, read u32 `0x03000E98`. Expected: about 0x4EC to 0x500, minus the frames after `ext 70` in that scene. Pressing B with the transform slot plays the refusal sound. The cooldown code is byte equal in base, r38 and r39, so an r39 run is enough.
4. Repeat on the trial ROM. Expected: 0, and Vegeta can transform at once.

---

## Files

- `scripts\one-time\2026-10-24-form-cooldown\cd_sweep.py` and `cd_sweep.txt`: cooldown accesses in base, r38 and r39, two shapes.
- `scripts\one-time\2026-10-24-form-cooldown\ext_sites.py` and `ext_sites.txt`: ext 70 and ext 115 script sites in base and r39.
- `scripts\one-time\2026-10-24-form-cooldown\fix_proof.py`, `fix_proof.txt` (r39), `fix_proof_base.txt` (base): wrapper bytes, variant B bytes and the interpreter runs.
- `scripts\one-time\2026-10-24-form-cooldown\states_cd.py` and `states_cd.txt`: cooldown, leader, map and flags in the existing save states.
- `scripts\one-time\2026-10-24-form-cooldown\bible_rows.md`: FCD rows for sections 6 and 13.
