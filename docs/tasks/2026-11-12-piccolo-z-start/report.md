# Piccolo: Super Namek from the start, with the healing removed (phase 1)

Agent report, 2026-11-12. Written to disk by the controller because the harness refused the agent's
own `.md` write. The controller re-verified every load-bearing byte below against the base ROM
before saving it; the verified items are marked RE-CHECKED.

Trial ROM `builds\mockups\2026-11-12-piccolo-z-start\log2_piccolo_z_v1.gba`, SHA-1
`177c52cf181f83a1a1bd6272158006fd7752a30d` (RE-CHECKED on disk). Save `log2_piccolo_z_v1.sav`
seeded from `builds\log2_poc_r40.sav`, which is unchanged at SHA-1
`d2fa5e1a016ae40fe3b264eb21008b807d391a1f` (RE-CHECKED).

---

## 1. What gates the transform today. CONFIRMED

**No story flag gates it.** The brief assumed one did. None does.

| Step | Code | What it does |
|---|---|---|
| B fires an ability | `@0x08007EDA` | reads record `+9` (selected slot), indexes the four ability ids at `+0x18`, calls the ability table test (`+8`) and action (`+0xC`). Never reads `+0x14`, never reads a flag |
| Ability 11 test | `@0x080134F2` | reads the appearance entry flags (`+0` bit 1 blocks, bit 0 means transformed), the map combat word, the party cooldown, EP >= 10. No flag byte |
| Ability 11 action | `@0x080134C0` | reads entry `+0` bit 0 only: transformed sends player vtable `+0x28` with `0x24` (revert), else `0x25` (Namek transform) |
| L cycles the slot | `@0x08004284` | `lsl r1,r2,#0x19 ; lsr r1,r1,#0x1C` takes record `+0x14` bits 3-6 as a mask. **Slot k is bit 3 + k** |
| Piccolo's abilities | `rom:0x1D9564 +0x18` | `9, 8, 11, 2`. Ability 11 is **slot 2**, so it needs **bit 5** (RE-CHECKED: reads `[9, 8, 11, 2]`) |
| The default record | `rom:0x1D9578` | `0x40`: slot 3 alone. Slot 2 is shut (RE-CHECKED: reads `0x40`) |

So the player cannot **select** the transform. The grant is **`ext 82 (1)`** in the Kami fusion
record (table `rom:0x3E0DBC` index 48, map 10,16), shortly before the `SET 132`. Handler
`@0x0800AA58` ends:

```
0800aa74  ldr r1,[r0,#0x14]
0800aa76  orr r1,r2            ; r2 = 0x20
0800aa78  str r1,[r0,#0x14]
```

RE-CHECKED, the fusion tail from `rom:0x3E0D69`:

```
1d 02 02 04 02 53   ext 83 (1, 2)   sets bit 4, form slot 1
00 01 02 50         ext 80 (1)
00 01 02 52         ext 82 (1)      sets bit 5, slot 2, which is ability 11
...
00 84 02 1b         SET 132
```

Both ops fire at the fusion. **`ext 82` is the one that opens the transform**, because ability 11
lives in slot 2. An earlier controller note that pointed at `ext 83 (1,2)` was incomplete.

### Three search shapes, each with its blind spot stated

- **A**, the map-owned scene walk: four `ext 82` sites, `rom:0x3D1FD7` (char 2), `rom:0x3DF2B4` and
  `rom:0x3DF2DB` (char 3), `rom:0x3E0D75` (char 1). A floor: it cannot reach a table only code names.
- **B**, every byte string `scene_lib` itself encodes, over the whole ROM: `ext 82 (1)` = `00 01 02 52`
  gives **one** site, the same one. `ext 83 (1, 3)`, the other op that would set bit 5 (`4 << 3`),
  gives **none**. Control: `ext 83 (1, 2)` gives exactly the known fusion grant.
- **C**, Thumb that ORs `0x20` into a record `+0x14`: five sites at a 20-byte window, of which only
  `@0x0800AA68` (this handler) and `@0x08005C70` write a character record. The latter is inside the
  unreferenced `sub_08005B50` and sets bits 2-5 at once, which reads as debug.

> **Shape C failed its known-answer check at first.** At a 10-byte window it missed the `ext 82`
> handler itself. Widened to 20 and re-run. The narrow window read as 4 clean sites and was wrong.

A grant that pushed a run-time character id, or lived in a table only code names, appears in none of
the three.

**Live proof from the owner's saves:** all three slots of `builds\log2_poc_r40.sav` and of
`test-data\saves\log2_lv40_postcell.sav` carry Piccolo `+0x14` = `0x7F` and story flag 132 = 1.

**Every reader of bit 5 is a form or HUD reader, never a story branch:** slot cycling, the HUD
cooldown bar (`@0x08008BEE`), and `fullpower_ssj`'s `appearance_revert`, which reads it for Gohan
only. `ext 84` (`@0x0800AAAE`, 17 sites) pops one value, calls `@0x0800C73A` with the map info and
reads no record. So opening the bit early cannot skip or flip a scene. One visible side effect:
Piccolo's HUD cooldown bar now draws its full 20-offset range.

### How phase 1 opens it

One byte: `rom:0x1D9578`, `0x40` to `0x60`. `save_defaults` `@0x08003C24` DMAs that six-record
template into the save struct on a new game.

> **Limitation, traced not assumed.** Continue `@0x0800180C` never runs `save_defaults` on a loaded
> slot: `bl @0x080019F6` tests the slot, `beq @0x080018CE` takes the empty-slot new game path (which
> does run it), and the loaded path goes straight to the 0x164-byte copy `bl @0x08021EA8` then
> `appearance_revert`. **So this reaches a new game only.** A save made before the fusion still waits
> for the fusion. The other `save_defaults` callers (`slot_write`, `save_game`, `debug_level`) were
> not traced. A load-time grant is possible, was out of scope, and is logged as an open row.

---

## 2. The deviation: option A is three runs, not one

The brief said take option A, "Namek `+4` to `tick_ssj`". **That one word on its own breaks the form.**

`tick_ssj` opens with `bl pool_ref`, then `cmp r0,#0x0 ; beq tick_done`. `pool_ref` accepts only
`0x030021EC` (Super Saiyan) and `ssj2_form`'s object; Super Namek's entry 7 holds `0x030021F0`. So
`pool_ref` returns 0, `tick_done` skips the drain **and the revert**, and Piccolo would stay Super
Namek for ever with free ki.

Option A in the PKI report is three runs together. All three shipped, from the new module, **without
editing `bf_ki_pool.py`**:

| Run | Site | From | To |
|---|---|---|---|
| The accept | `rom:0x909FFC`, 22 bytes inside `pool_ref` | Super Saiyan only | Super Saiyan and Namek |
| The tick | `rom:0x24AC0`, Namek vtable `0x08024ABC` `+4` | `0x08017401` | `tick_ssj` |
| The transform end | `rom:0x25CF4`, state 0x25 vtable `0x08025CE0` `+0x14` | `0x0801563D` | `fill_end` |

The third is needed because `ext 70` reverts entry 7 to 6 in seq 27 with no `empty_end`, so a stale
tag would block the refill.

Because `bf_ki_pool.py`'s source is untouched and the module is only in a trial list, none of the 16
pins B1467 lists breaks, and both master SHA-1s are unchanged.

### The heal was real, and it is gone

The vanilla Super Namek tick `@0x08017400` (0x90 bytes) is the vanilla Super Saiyan tick
`@0x08017306` (0x70 bytes) with one 0x20-byte block inserted: leader HP += max HP x `0x290` >> 16,
capped at max HP. Every other instruction is the same code in the same order. Two interpreter tests
run both ticks on the same setup: the vanilla tick raises HP 500 to 503 on one overflow; `tick_ssj`
leaves HP at 500 over eight overflows while the pool falls 50 to 42.

### What Super Namek now costs, and the cheaper alternative

He spends the **yellow ki pool**, not regular EP. The pool fills to max EP at the transform end,
drains 1 every 20 frames (his vanilla rate), regular EP regenerates underneath through the vanilla
base tick, the r27 scene pause applies, HP is never written, and the form still ends with state 0x24
at pool 0 when HP is not 0.

> That is a ki pool Piccolo never had (B0542). It is what option A means, and it closes open row
> B1691. **This is a larger change than "remove the heal" and it is the owner's call.** The
> alternative: point `rom:0x24AC0` at the vanilla Super Saiyan tick `0x08017306`. One word, identical
> drain, identical revert, no pool, no `pool_ref` edit.

### Why the accept is safe

```
ldr r5,=0x030021EC
sub r0,r0,r5
lsr r0,r0,#3            ; 0: Super Saiyan, 4: Namek 0x030021F0
bne ref_none
```

It passes a form object within 7 of `0x030021EC`. Over the live appearance table that is
`0x030021EC` and `0x030021F0` only: base `0x030021E0`, Rage `0x030021E4` and Super `0x030021E8` sit
**below** it and give a large unsigned difference. A test runs `pool_ref` over entries 3, 4, 5, 6, 7,
8, 10, 11 and 22 and pins each answer. The accept is fixed size, so every label, the literal pool and
every later module address are unchanged.

---

## 3. What the module writes, and nothing else

`diff_probe.py` compares the built trial against the dev master rebuilt in memory:

```
4 differing run(s):
  rom:0x024AC0   4 bytes   dev 45 29 ff ff -> trial b3 55 8e 00
  rom:0x025CF4   4 bytes   dev 5d f9 fe ff -> trial 67 43 8e 00
  rom:0x1D9578   1 byte    dev 40 -> trial 60
  rom:0x909FFC  22 bytes   dev 98 00 c0 18 80 00 93 4d ... -> trial 14 20 58 43 93 4d 40 19 ...
```

The three PKI runs land where the PKI report predicted, to the byte count.

Pre-flight checks before the first write: the template literal `rom:0x3EA0` still names
`0x081D9548`; record 1 wears entry 6, carries ability 11 in slot 2 and `+0x14` = `0x40`; the Namek
tick word still resolves to `0x08017401`; the state 0x25 end word still resolves to `0x0801563D`;
live appearance entry 7 still holds `0x030021F0`; and the ki pool code in the ROM is byte for byte
what `bf_ki_pool`'s own source assembles to at its own address, with the same labels. That last check
makes rewriting another module's blob safe: a reordered list, a second run, or a changed
`bf_ki_pool` all fail loudly instead of corrupting the pool.

---

## 4. Phase 2: exactly what to change. CONFIRMED

**The grant site is `ext 82 (1)` at `rom:0x3E0D75`.** It sets record `+0x14` bit 5 = slot 2 =
ability 11. It tests nothing. The same record sets `flag:132` and then loads world map 6,99.

**The step-gate site is ability 11's ACTION word, `rom:0x1D99BC` (`0x080134C1`)**, the same shape
`ssj2_form` uses on ability 12's `rom:0x1D99CC`.

**Route A, recommended: leave `ext 82` alone and gate the Z+ step on `flag:132`.** Exactly
`ssj2_form`'s shape (B0454): a `step_ok` predicate shared by the action gate and the HUD icon hook,
reading `0x03000E90 + 0xB4 + 132/8` bit `132 & 7`. Z+ becomes a new appearance entry whose `+5`
returns to entry 6, and entry 7 `+4` points at it so B steps up from Super Namek. No scene byte
changes, and the owner's existing saves get Z+ at once because all six slots read already hold
flag 132. `op_usage --flag 132` reports set x1 and no clearer (a floor: a clearer in a code-named
table would not show), so it is a safe once-only gate.

**Route B: replace the `ext 82` op so the fusion grants Z+ directly.** Costs a script edit and
strands every save made before the fusion, because phase 1 only opens bit 5 for a new game. Not
recommended.

> **A cost phase 1 created, LIKELY:** the Namek accept spent `pool_ref`'s fixed-size slack. A Z+ form
> object of its own, which a stats change needs, is a **third** object for `pool_ref` and will not fit
> the same way. Phase 2 must either give Z+ the Namek form object `0x030021F0` (same stats, no
> `pool_ref` change) or rewrite `pool_ref`, which moves `bf_ki_pool`'s blob and renews the pins
> B1467 lists.

On portraits: the Vegeta Z+ build took id **122**, not 121; `npc_gi` had already given 121 the armor
frame. Phase 2 should re-read `art\tables\portraits.json` rather than trust either number. No
portrait was changed here.

---

## 5. Tests

`scripts\permanent\tests\test_piccolo_z_start.py`, **23 tests, all passing**. Every expected value is
a measured difference between the dev master and the trial, never a restatement of the module's
constants. Interpreter is `tests.test_ssj2.Cpu` through `tests.test_bf_ki_pool.Cpu2`, extended with
the two-operand ALU forms slot cycling needs.

| Done means | Test |
|---|---|
| Transform with the story flag clear | `test_slot_cycling_reaches_the_transform_with_every_story_flag_clear` (runs `@0x08004284` with all 50 flag bytes zero, lands on slot 2 / ability 11); `test_without_the_patched_byte_slot_cycling_never_leaves_slot_3`; `test_the_ability_11_test_does_not_read_the_kami_flag`; `test_the_action_enters_the_namek_transform_state_with_the_kami_flag_clear`; `test_the_action_reverts_when_he_is_already_super_namek` |
| The tick no longer heals | `test_the_vanilla_namek_tick_really_did_heal` (HP 500 to 503); `test_the_pool_tick_drains_and_never_touches_hp`; `test_hp_is_unchanged_over_a_run_of_drain_steps` |
| The drain still ends the form | `test_the_drain_still_ends_the_form`; `test_a_knocked_out_piccolo_does_not_revert`; `test_the_transform_end_fills_the_pool` |
| Old saves still load | `test_the_patch_writes_four_runs_and_none_of_them_is_save_code`; `test_the_save_image_layout_is_untouched`; `test_a_stored_save_still_decodes_and_keeps_its_own_record_bits` |

Plus `PoolRefAccept`, four tests over nine appearance entries.

**Full suite, real exit code, never piped: 1985 tests, 2 failures.**

1. `test_art_inject.test_a_palette_entry_makes_its_index_usable`. Pre-existing, caused by the
   controller's 2026-11-11 widening of `art_tables.allowed_indices`. Not this task's.
2. `test_battle_start.test_form_survives_the_leader_change`. Argued not this task's:
   `test_battle_start` builds `build_list_trial_ending.txt`, which never names this module, and
   `fullpower_ssj.py` is unmodified. Reproduces alone. **Unresolved; owner informed.**

---

## 6. Ordering against the Vegeta Z+ module

No forbidden file touched. Both master SHA-1s unchanged.

`vegeta_zplus` repoints every ROM word naming the live appearance table, **including
`bf_ki_pool`'s literal pool word**. This module re-assembles `bf_ki_pool`'s blob from its own source
and compares it to the ROM.

- `piccolo_z_start` then `vegeta_zplus`: **fine.** This edit changes 22 bytes inside `pool_ref`'s
  body, never the literal pool, so Vegeta's repoint still lands.
- `vegeta_zplus` then `piccolo_z_start`: **raises**, loudly, not silently.

If they ever go into one list, put `piccolo_z_start` first.

---

## 7. Play steps

1. **To see the heal go:** load the seeded save, lead with Piccolo, press L to the Z icon, press B.
   The EP row should turn yellow and drain at his old rate, his HP should no longer creep up while
   transformed, and regular EP should regenerate underneath.
2. **To see the gate change:** start a **NEW GAME**. The seeded save is post-fusion and already
   carries bit 5, so it shows the tick change only. On a new game, lead with Piccolo at the first
   chance and press L once from the default slot; the Z icon should be there, long before the fusion.
3. Let the pool run to zero and check he drops out of the form.

---

## 8. Bible correction

**B0432** ("Super Saiyan is gated by record `+0x14` bit 5 ... C (test `@0x080134F2`)") attributes the
bit to the wrong function. The test reads none of `+0x14`. The bit is still the gate, but through
**selection**, not through the test. Correction row is in `rows.md`.

---

## Files

| File | What |
|---|---|
| `scripts\permanent\patches\piccolo_z_start.py` | the module |
| `scripts\permanent\tests\test_piccolo_z_start.py` | 23 tests |
| `scripts\permanent\build_list_trial_piccolo.txt` | `include build_list_dev.txt` plus the module |
| `builds\mockups\2026-11-12-piccolo-z-start\log2_piccolo_z_v1.gba` and `.sav` | the trial |
| `scripts\one-time\2026-11-12-piccolo-z-start\probe.py`, `probe2.py`, `probe3.py`, `diff_probe.py` and their outputs | the measurements behind sections 1, 2 and 3 |
| `docs\tasks\2026-11-12-piccolo-z-start\rows.md` | 12 bible rows, tag `PZS`, sections 6 and 13 |
