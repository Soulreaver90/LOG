# Full-power Super Saiyan: yellow ki and no aura loop (trial report, 2026-10-25)

This report answers my 12:14 PM note on the full-power Super Saiyan HUD and aura sound.

---

## SHIPPED and PENDING

| Ask (my words) | State |
|---|---|
| "the semi permanent SSJ for Gohan/Goku during the Cell Games has no yellow SSJ ki, just the base green" | SHIPPED as a trial: yellow row in the full-power state (mirror of the regular EP) |
| "the constant SSJ sound effect does get annoying ... remove that during the Cell Games for Goku/Gohan until after" | SHIPPED as a trial: no aura loop for Goku and Gohan in plain Super Saiyan from the chamber until Cell is beaten |
| "SSJ2 can keep the sound effect" | SHIPPED: Super Saiyan 2 and Rage keep the loop (their vtables are not changed) |

| Pending | Me |
|---|---|
| Play test of the trial ROM (steps below). The interpreter tests do not run sound or the frame loop | Me |
| Pool choice: mirror (built), real pool with no drain, or a pool refilled every frame (see "my choice") | Me |
| Approval: move the `fullpower_hud` line from `build_list_trial_fullpower.txt` into `build_list.txt` | Me |
| Merge `scripts\one-time\2026-10-25-fullpower-hud\bible_rows.md` (tag FPH) into `docs\RE-BIBLE.md` | Me |
| The Vegeta trial (`builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v2_cj3.gba`) adds two script starts of sound 55 with no ext 47 after them: `rom:0x90A696` and `rom:0x90A77C` (its NPC Vegeta transform copies in the final Cell scene). This gate covers only the form enter, so it does not silence them if that trial is approved. LIKELY: what ends an unpaired script loop in vanilla is not traced (only ext 48 calls stop-all; a later form leave stops one matching channel). Read-only sweep; no Vegeta file was edited | Me, Vegeta trial |
| Process note: one Bash call (the single-file test run) began with `cd` into the LOG root, against the brief's "never cd". It changed no file | Disclosure |

---

## Root cause 1: no yellow ki

The full-power state is excluded from the pool on purpose in r39, so the HUD never paints yellow.

- **CONFIRMED.** `pool_ref` (`@0x08909FE4`) accepts form object `0x030021EC` (every Super Saiyan) only when `stretch_on` returns 0. With the stretch on and leader 0 (Gohan) or 4 (Goku) it returns 0: `@0x0890A01E` `lsr r2,r4,#8 ; cmp r2,#0x0 ; beq ref_none ; cmp r2,#0x4 ; beq ref_none`.
- **CONFIRMED.** The HUD draw (`@0x0890A0EE`) runs `bl pool_ref ; cmp r0,#0x0 ; beq hud_key` (`@0x0890A0F6`) with r6 = 0, so it paints no yellow step. The test `test_stretch_gohan_shows_yellow_at_the_ep_fill` runs the r39 draw on the same state and gets index 1 everywhere.
- **CONFIRMED.** The r28 fields are not the cause. `fullpower_ssj` skips only the drain, the revert at 0 EP, the ability 12 test and the revert of entries 5 and 20. The entry (5 or 20) and its form object `0x030021EC` are the same as in a normal transform.

### How the drain and the pool interact in the full-power state

- **CONFIRMED (listing).** The pool tick (`@0x0890A074`) first runs the base tick (`@0x0890A080` `ldr r3,=0x08017029 ; bl`), so the leader EP regenerates (3 % about every 596 frames). Then `bl pool_ref ; beq tick_done` (`@0x0890A08C`-`@0x0890A092`) ends the tick: no drain, no revert.
- **CONFIRMED (listing).** The spend stubs also see `pool_ref` = 0, so the ki moves spend the regular EP.
- **LIKELY (in game).** So in r39 the full-power state plays exactly as r28 with a green row.

## Root cause 2: the aura sound loop

The Super Saiyan enter method starts a looping sound, and nothing in the full-power state stops it.

- **CONFIRMED.** Super Saiyan vtable `0x08024C58` +8 = enter `@0x08017376`: `sound_start(manager, 0x080E15B0 + 0xA5 x 4)` = sound entry 55 (0x294 = 55 x 12), volume 0x40. Leave `@0x08017392` stops entry 55.
- **CONFIRMED.** Entry 55 (`0x080E1844`) has flags 1. The channel setup copies entry +4 to channel +0x11 (`@0x0801FA30`), and the mixer loops a channel whose +0x11 bit 0 is set (`@0x0801FA80`-`@0x0801FA84`). Otherwise it ends the channel (`@0x0801FBE0`).
- **CONFIRMED (two shapes, 8 = 8).** Code starts sound 55 in four enter methods and stops it in the matching leaves: Rage `@0x08017158`, Super `@0x0801727C`, Super Saiyan and Super Saiyan 2 `@0x08017376` (shared), transform state 35 `@0x080155A8`. No aligned word names `0x080E1844`.
- **CONFIRMED (byte shapes).** Of 9 script starts (ext 46 (55)), 6 are followed by ext 47 (55). The 3 without a stop are Trunks NPC transforms and the virus attack scene, all before the chamber (**LIKELY** for the virus scene, which the r28 sweep calls OPEN). So the form enter is the only loop source in the full-power state.
- **CONFIRMED (shape).** Every enter caller picks the form from the leader byte at the call: Continue `@0x080018B0`, menu return `@0x08008A08`, `set_leader` `@0x0800A706` (after the leader store `@0x0800A6B6`), ext 73 `@0x0800A992` (leader only), transform `@0x08014DD8`. **LIKELY:** that list is complete; a caller that reaches the form another way would not show.

---

## The fix: trial module `fullpower_hud`

One new code block and two vtable words. No vanilla code byte, no pool code byte and no RAM layout changes.

### What it does

1. **Yellow ki (HUD vtable `0x0802408C` +0x10).** In the full-power state (stretch on, leader 0 or 4, entry form object `0x030021EC`), `hud_fp` computes fill = EP x 49 / max EP, as the vanilla EP row does. It then enters bf_ki_pool's `hud_draw` at `hud_key` (`0x0890A11C`) with the same stack frame (r4 = HUD, r5 = OAM cursor, r6 = fill). Every other case tail-calls `hud_draw` unchanged.
2. **Aura gate (Super Saiyan vtable `0x08024C58` +8).** `enter_fp` returns at once in the stretch with leader 0 or 4. Every other case tail-calls the vanilla enter `0x08017377`.

### How the gate tells Super Saiyan from Super Saiyan 2

- Only the Super Saiyan vtable word changes. ssj2_form's vtable `0x0888DE24` has its own +8 word, which still names `0x08017377`. Rage (`0x08024E4C` +8 = `0x08017159`) and the transform state 35 are not touched.
- The stretch test is fullpower_ssj's own `stretch_on` (`0x0889A8B0`): flag 149 set and flag 195 clear. Super Saiyan 2 needs flag 195, so it never runs in the stretch.

> [!NOTE]
> The gate reads the leader byte `0x03000E90`, the same key that fullpower_ssj's tick and bf_ki_pool's `pool_ref` use. Vegeta, Trunks and every time outside the stretch get the vanilla enter.

### Bytes

| Site | r39 | Trial |
|---|---|---|
| `rom:0x24C60` (SSJ vtable +8) | `1f27ffff` (`0x08017377`) | `79578e00` (`0x0890A3D1`, `enter_fp`) |
| `rom:0x2409C` (HUD vtable +0x10) | `6360 8e00` (`0x0890A0EF`) | `6763 8e00` (`0x0890A3F3`, `hud_fp`) |
| `rom:0x90A3D0`, 0xC8 bytes | 0xFF | the code below |

```
00b5294b00f04ff808bc9e46002a06d0264b1b78002b01d0042b00d17047244a1047f0b5041c0d1c00f00cf8312802dc061c204b1847201c291cf0bc08bc9e461d4b1847f0b5184b00f02df8002a28d016480278002a01d0042a22d1d100891a890009180c310b7a9800c0188000134bc0180069124b984213d10423cc5e0623c85e00280bdd002c09dd31235c43211c0c4b00f008f8312804dd312002e0002000e0ff20f0bd1847b1a88908900e0003777301081da19008efa0900854dc8808ec210003311f0208
```

<details>
<summary><b>Decode (thumb_dis)</b></summary>

```
enter_fp:
0890A3D0  push {lr}
0890A3D2  ldr r3,=0x0889a8b1        ; stretch_on
0890A3D4  bl 0x890a476              ; via_r3
0890A3D8  pop {r3}
0890A3DA  mov lr,r3
0890A3DC  cmp r2,#0x0
0890A3DE  beq 0x890a3ee
0890A3E0  ldr r3,=0x03000e90
0890A3E2  ldrb r3,[r3,#0x0]         ; leader
0890A3E4  cmp r3,#0x0
0890A3E6  beq 0x890a3ec
0890A3E8  cmp r3,#0x4
0890A3EA  bne 0x890a3ee
0890A3EC  bx lr                     ; no sound 55 loop
0890A3EE  ldr r2,=0x08017377
0890A3F0  bx r2                     ; vanilla enter
hud_fp:
0890A3F2  push {r4,r5,r6,r7,lr}
0890A3F4  add r4,r0,#0
0890A3F6  add r5,r1,#0
0890A3F8  bl 0x890a414              ; ep_fill
0890A3FC  cmp r0,#0x31
0890A3FE  bgt 0x890a406
0890A400  add r6,r0,#0
0890A402  ldr r3,=0x0890a11d        ; bf_ki_pool hud_key
0890A404  bx r3
0890A406  add r0,r4,#0
0890A408  add r1,r5,#0
0890A40A  pop {r4,r5,r6,r7}
0890A40C  pop {r3}
0890A40E  mov lr,r3
0890A410  ldr r3,=0x0890a0ef        ; bf_ki_pool hud_draw
0890A412  bx r3
ep_fill:
0890A414  push {r4,r5,r6,r7,lr}
0890A416  ldr r3,=0x0889a8b1
0890A418  bl 0x890a476
0890A41C  cmp r2,#0x0
0890A41E  beq 0x890a472
0890A420  ldr r0,=0x03000e90
0890A422  ldrb r2,[r0,#0x0]
0890A424  cmp r2,#0x0
0890A426  beq 0x890a42c
0890A428  cmp r2,#0x4
0890A42A  bne 0x890a472
0890A42C  lsl r1,r2,#3
0890A42E  sub r1,r1,r2
0890A430  lsl r1,r1,#2
0890A432  add r1,r1,r0
0890A434  add r1,#0xc               ; leader record
0890A436  ldrb r3,[r1,#0x8]         ; entry
0890A438  lsl r0,r3,#2
0890A43A  add r0,r0,r3
0890A43C  lsl r0,r0,#2
0890A43E  ldr r3,=0x0888dc54        ; appearance table
0890A440  add r0,r0,r3
0890A442  ldr r0,[r0,#0x10]         ; form object
0890A444  ldr r3,=0x030021ec
0890A446  cmp r0,r3
0890A448  bne 0x890a472
0890A44A  mov r3,#0x4
0890A44C  ldsh r4,[r1,r3]           ; EP
0890A44E  mov r3,#0x6
0890A450  ldsh r0,[r1,r3]           ; max EP
0890A452  cmp r0,#0x0
0890A454  ble 0x890a46e
0890A456  cmp r4,#0x0
0890A458  ble 0x890a46e
0890A45A  mov r3,#0x31
0890A45C  mul r4,r3
0890A45E  add r1,r4,#0
0890A460  ldr r3,=0x08021f31        ; ARM divide r0 = r1 / r0
0890A462  bl 0x890a476
0890A466  cmp r0,#0x31
0890A468  ble 0x890a474
0890A46A  mov r0,#0x31
0890A46C  b 0x890a474
0890A46E  mov r0,#0x0
0890A470  b 0x890a474
0890A472  mov r0,#0xff              ; not the full-power state
0890A474  pop {r4,r5,r6,r7,pc}
0890A476  bx r3
pool: 0x0889A8B1 0x03000E90 0x08017377 0x0890A11D 0x0890A0EF 0x0888DC54 0x030021EC 0x08021F31
```

</details>

### Safety checks in the module

- Before the first write it checks both vtable words, the vanilla enter bytes, the divide entry, the `stretch_on` bytes and the form objects of entries 5 and 20.
- It re-assembles bf_ki_pool at its window and compares the bytes. It pins the 0x4A bytes from `hud_key` to `put_px` by SHA-1, so a change to the HUD draw stops the build.
- The new space must be 0xFF and named by no ROM word. The first chunk (`rom:0x90A308`) was named by the hold46 word `rom:0x258BC`, so the module skipped it.
- A second run raises.

---

## My choice: what the yellow row holds

The full-power state skips the drain, so the yellow row cannot work exactly like a normal transform. Each option below changes the behavior.

| Option | Yellow row | Ki moves | Risk |
|---|---|---|---|
| **1. Mirror (built)** | Equals the regular EP | Spend the regular EP, which regenerates (as r28 and r39) | Looks different from a normal transform: a normal one starts full yellow whatever the EP; mirror shows yellow only up to the current EP and never green past it |
| 2. Real pool, no drain | Full at the start, falls with moves | Spend the pool | Only a new tag refills it. A swap away and back gives the same tag, so a spent pool stays spent. At pool 0 the moves are refused and no revert happens |
| 3. Pool refilled every frame | Always full | Free | Ki moves cost nothing in the Cell Games |

> [!IMPORTANT]
> The choice is mine. Mirror keeps every r39 rule (regen, spend, no revert) and changes only the color.

---

## Builds and SHA-1s

| File | SHA-1 |
|---|---|
| r39 `builds\log2_poc_r39.gba` (main list, rebuilt in memory) | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` |
| Trial `builds\mockups\2026-10-25-fullpower-hud\log2_poc_r39_fullpower.gba` | `1278a8c07d0382ed68e40dc2ff0cb83b50d6eb7b` |
| Trial `.sav` (byte copy of `builds\log2_poc_r39.sav`) | `d2fa5e1a016ae40fe3b264eb21008b807d391a1f` |

Both files were written with exclusive create. The build log has one new line.

### Diff runs, r39 to the trial

205 bytes differ in 4 runs, all in the three named sites (`make_trial.txt`, `test_r39_to_new_diff_is_two_words_and_the_code`).

| Run | Bytes | Site |
|---|---|---|
| `rom:0x2409C`-`0x2409D` | 2 | HUD vtable +0x10 (the top two bytes do not change) |
| `rom:0x24C60`-`0x24C63` | 4 | Super Saiyan vtable +8 |
| `rom:0x90A3D0`-`0x90A471` | 162 | new code |
| `rom:0x90A473`-`0x90A497` | 37 | new code and pool (`rom:0x90A472` is 0xFF in both) |

## Tests

- `scripts\permanent\tests\test_fullpower_hud.py`: 22 tests, OK. They cover the list, the r39 pin, fail-closed checks, the diff, the decode, the `hud_key` entry contract, the enter gate (interpreter, 7 states) and the HUD draw (interpreter, 9 states against r39).
- Full suite: **771 tests, OK, no skips** (`scripts\one-time\2026-10-25-fullpower-hud\suite.txt`; 771 = 744 before + 22 here + 5 others, by subtraction).
- `log2_build.py --list` still gives r39 `aa51dc16...` (`build_list.txt` not edited; `test_before_is_r39`).

---

## My play steps

Load `log2_poc_r39_fullpower.gba` with its `.sav` from `builds\mockups\2026-10-25-fullpower-hud\` and start from Continue.

> [!WARNING]
> Do not load an older save state. A state saved while the loop played holds a live sound channel, and it keeps playing until the next form leave.

### Check 1: full-power state (slot 3)

Slot 3 is Goku at Dende's Lookout (9,1) with flag 149 set and flag 195 clear.

1. Continue slot 3. Expected: Goku is Super Saiyan, the EP row is yellow up to his EP (full row when EP is full), and the aura hum does **not** loop.
2. Open the menu and close it. Expected: still no loop.
3. Switch Characters to Gohan. Expected: gi Super Saiyan, yellow row, no loop.
4. Switch to Vegeta. Expected: base form, green row, no loop.
5. Fly from the Lookout exit to Master Roshi's Island (11,1). Ki moves and transforms do nothing at 9,1.
6. As Goku or Gohan, use ki moves. Expected: the yellow row falls with the EP, then slowly refills; no revert; B on the Z is refused.
7. As Vegeta, press B on the Z. Expected: the aura loop **plays**, the row is full yellow and drains. When he reverts, the loop stops.
8. Transform Vegeta again so the loop plays. Open the menu, switch to Goku and close the menu. Expected: the loop stops and does not come back while Goku leads. This checks the Switch Characters path, which the code sweep could only label LIKELY.

### Check 2: Super Saiyan 2 keeps the loop (slot 2)

Slot 2 is Gohan at Master Roshi's Island (11,1) with flag 195 set (after Cell).

1. Continue slot 2. Gohan is in base form.
2. Press B on the Z. Expected: Super Saiyan, the loop **plays**, full yellow row, drain.
3. Press B again. Expected: Super Saiyan 2, the loop **plays**, faster drain.
4. Revert. Expected: the loop stops.

### Check 3 (optional): the Cell Games

- Gohan versus Cell in Super Saiyan: yellow row, no loop.
- Rage keeps the loop and its green EP row (global rule: Rage is unchanged).

---

## Files

- Module: `scripts\permanent\patches\fullpower_hud.py`
- Tests: `scripts\permanent\tests\test_fullpower_hud.py`
- List: `scripts\permanent\build_list_trial_fullpower.txt`
- Study and proofs: `scripts\one-time\2026-10-25-fullpower-hud\` (`make_trial.py`/`.txt`, `sound55_sweep`, `script55_sweep`, `form_enter_callers`, `bl_callers`, `dis.py`, `suite.txt`, `bible_rows.md`)
