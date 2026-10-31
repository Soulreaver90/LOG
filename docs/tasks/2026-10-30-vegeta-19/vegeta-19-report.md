# Vegeta 19 reveal trial: report (2026-10-30)

This report covers the trial module that makes Vegeta go Super Saiyan after his line to Android 19.

Labels: **C** = CONFIRMED (bytes, listing or test quoted), **L** = LIKELY, **S** = SPECULATIVE. Scripts and listings: `scripts\one-time\2026-10-30-vegeta-19\`. Trial files: `builds\mockups\2026-10-30-vegeta-19\`.

---

## SHIPPED

| Ask (my words and the brief) | Where | Label |
|---|---|---|
| "Let's have him transform after the dialogue (no permanent ki)" | `scripts\permanent\patches\vegeta_19_reveal.py`, list `scripts\permanent\build_list_trial_vegeta19.txt` | C (tests), L (in game) |
| "Prove the form state at the fight start is the normal pool Super Saiyan" | Form proof below; `FormTests` in `scripts\permanent\tests\test_vegeta_19_reveal.py` | C (interpreter) |
| "does not touch any record another trial module changes ... builds after all of them in one list" | Clash check below; `s9_combined.txt` | C |
| "Tests green, full suite once at the end. `--list` must still give r39" | 27 new tests; full suite 914 OK; r39 `aa51dc16...` | C |
| "Build ... `log2_poc_r39_vegeta19.gba` with a save placed just before the 19 scene" | Build and save below; `s10_build.txt` | C (bytes), L (plays) |
| "Diff runs r39 to the trial; all inside declared sites" | 52 bytes in 2 runs, 0 outside | C |
| "Bible rows (tag V19) as `## Section N` table blocks" | `scripts\one-time\2026-10-30-vegeta-19\bible_rows.md` (sections 6, 7, 8, 11, 13) | C |

## PENDING

| Item | Why |
|---|---|
| My play test of the look | Pose, flash and HUD timing are not checked in an emulator (S). Play steps at the end |
| Merge of `bible_rows.md` into `docs\RE-BIBLE.md` | I own the bible. Add `V19` = this report to the source list |
| My question 9 (space scene) | Left as is, as the brief says. The space scene still shows his first Super Saiyan earlier (flag 77) |
| Approval | Approval = move the last line of `build_list_trial_vegeta19.txt` into `build_list.txt` |
| 19 death scene with gold Vegeta | The death table `rom:0x3D4834` seq 1 drives the player with `ext 134 (0, 20, n)` several times, then walks him. With a full pool he will almost always still be Super Saiyan there. `set:140` lacks anims 9, 14 and 17 (VSJ row). The bible has no row for ext 134 or its player state, so the anim it uses is not pinned. Vanilla reaches the same path when the player transforms in the fight, so the risk is low (L). Play step 5 checks it |
| Limit deviation | Three early read-only commands changed the working folder (`cd` twice in Bash, `Set-Location` once in PowerShell), which the brief forbids. No file was written outside the allowed folders; every write used an absolute path |

---

## The scene change

Table `rom:0x3D40C8` (map 7,15, named by `rom:0x3FD4F4`). Word 40 = seq 41, the line. Word 41 `rom:0x3D416C` = seq 42, the fight start (C, `s1_study.txt`).

| | Before (base and r39) | After (trial) |
|---|---|---|
| Word 41 `rom:0x3D416C` | `0x083D40B2` | `0x0890A308` (the copy) |
| Record | `rom:0x3D40B2`, 22 bytes | `rom:0x90A308`, 49 bytes; the old record stays, named by no word |
| Bytes | `2a0000 0001 0256 1d021804 0268 000c 0255 0000 0221 11` | `2a0000 020b 0002 0b 027e 0000 0b 04 130e 1d020046 0239 000a 022a 000a 022b` + the same 19 vanilla bytes |
| Ops | `push 1 ; ext 86 ; push 12,2 ; ext 104 ; push 12 ; ext 85 ; push 0 ; ext 33 ; end` | `ext 11 ; push 2 ; eq ; ext 126 ; push 0 ; eq ; and ; jz +14 ; push 0,35 ; ext 57 ; push 10 ; ext 42 ; push 10 ; ext 43 ;` then the vanilla ops |

What each part does:

1. **Guard** (C listing, interpreter): run the transform only when Vegeta leads (ext 11 = 2) and is not transformed (ext 126 = 0). ext 126 `@0x0800AF72` pushes bit 0 of the leader's appearance entry. Why: entry 11 +4 = 8, so state 35 on a Super Saiyan Vegeta would drop him to base (C, `test_without_the_guard_a_super_saiyan_vegeta_would_drop_to_base`). Both vanilla Cell scenes guard their state 35 the same way (`rom:0x3E65E2`, `rom:0x3E6F04`, C).
2. **Transform** (C bytes): `push 0,35 ; ext 57`, the same 6 bytes as the space scene `rom:0x3D1FDF` and both Cell scenes. State 35 starts sound 55 (the aura) and the power-up pose. At frame 0xA0 it plays sound 23 and runs the r39 `fill_end`: vanilla `transform(player, 1)`, then a full pool. ext 57 waits until the state ends (C, T6 row).
3. **Flash** (C bytes, L look): `ext 42 (10)` then `ext 43 (10)`, a white flash and the fade back. Source: the r27 Goku transform and `celljr_fight` use this pair. `vegeta_ssj_scene` has no flash (its report: "a remove and a spawn, with no flash").
4. **Fight start**: the vanilla ops, unchanged. The HUD stays off through the transform and comes on with `ext 86 (1)`, as in both Cell scenes (C, `s5_state35_sites.txt`). Neither `transform` nor `@0x080086A2` reads the HUD object (C listing).

> [!NOTE]
> Placement. The plan put the head before the vanilla ops. The other choice was after `ext 86 (1)`, with the HUD on, as in the space scene. The vanilla sweep settled it: 2 of the 3 player transforms run with the HUD off, right before the fight op, as here.

---

## Form proof

The tests run the ROM's own code in `test_bf_ki_pool`'s interpreter, on the trial ROM. Sound and the form object methods are stubs. Expected values are restated, not imported (C, all 9 `FormTests` pass).

| Step | Result |
|---|---|
| ext 11 and ext 126 handlers, Vegeta leading | entry 8 (base): leader 2, form bit 0, so the guard passes. Entry 11: form bit 1, so it skips |
| State 35 vtable `0x08025D9C` +0x14 | names `fill_end` in r39 and in the trial |
| `fill_end` from leader 2, entry 8, EP 40, cooldown 0x500 | entry 11; player +0x180 = `0x030021EC` (Super Saiyan form object); player +0x48 = the `set:140` lookup; state 0; base form left, Super Saiyan entered; pool = 138 (max EP), tag `0x820B`; regular EP 40 and cooldown 0x500 not written |
| `pool_ref`, entry 11, flag 149 set | a pool form (no full-power rule for Vegeta) |
| Pool tick (Super Saiyan vtable +4) | 138 to 136 in 40 frames (1 every 20); no drain with the scene gate on |
| Pool tick at pool 0 | message 0x24: the form drops when ki runs out |
| Ability 12 test and action, entry 11, cooldown 0x500 | test 1, action message 0x24: B on the form icon drops the form at any time |
| Ops in the copy | no flag, party, leader, appearance, level, HP, EP or bonus op; one state op, (0, 35) |

So the fight starts in the normal Super Saiyan form with a full pool. Nothing is permanent and nothing locks the ki (C for the code paths, L in game). Vegeta's form slot comes from the space scene, `ext 83 (2, 1)` at `rom:0x3D1FD9` (C), which runs before 19 on the route below (L).

---

## Clash check (brief task 2)

Two shapes in `s9_combined.txt` (C). Source SHA-1s at the run: `chapter_cards.py` `ced2d3545a932f3ffdd199d493574df3c32a70e8` (another task edits it), `celljr_fight.py` `adc42087...`, `vegeta_ssj_scene.py` `e576c1da...`, `beam_struggle.py` `84e5a571...`, `relay_cooldown.py` `bd888a7a...`, `fullpower_hud.py` `926f572c...`, `vegeta_19_reveal.py` `87b3bfc1...`.

| Shape | Result |
|---|---|
| A: each module alone on r39 | No module lists or changes word 40, word 41, seq 41, seq 42, the 19 table, the space transform bytes or the 7,15 region item |
| B: r39 + `celljr_fight` + `vegeta_ssj_scene` + `beam_struggle` + `relay_cooldown` + `fullpower_hud` + `chapter_cards` + `vegeta_19_reveal` | Builds. Combined SHA-1 `28079de0cb828a3d88418db5b6f46d8502b307b2` (memory only). 197206 bytes differ from r39, 0 outside a declared site. The only shared bytes are the known `relay_cooldown` and `chapter_cards` ext table word. `vegeta_19_reveal`'s sites overlap no other module; its copy is byte-equal to the trial's |

## SHA-1s

| Item | SHA-1 | Label |
|---|---|---|
| r39 (`--list`) | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` | C |
| Trial ROM `log2_poc_r39_vegeta19.gba` | `05779b1fb41017e41b2327210571b9c041460a95` | C |
| Trial save `log2_poc_r39_vegeta19.sav` | `16e33a11e67fbdf07053f9fcea3189d5c57ae00f` | C |
| Combined list (memory only) | `28079de0cb828a3d88418db5b6f46d8502b307b2` | C |
| Base save `log2_poc_r39_chapters_v5_pre_a.sav` | `0a04aa03ad560f8b1373c572e67cfae73c0f2a40` | C |

Both trial files were written with exclusive create. One line was appended to `docs\build-log.md`.

## Diff runs (r39 to the trial)

| Run | Bytes | Site |
|---|---|---|
| `rom:0x3D416C`-`0x3D416E` | 3 (of the 4-byte word) | Android 19 table word 41 |
| `rom:0x90A308`-`0x90A338` | 49 | seq 42 copy |

52 bytes in 2 runs, 0 outside the declared sites (C, `s9_combined.txt`, `test_r39_to_trial_diff_is_the_word_and_the_copy`).

## Tests

| Suite | Count | Result |
|---|---|---|
| `test_vegeta_19_reveal.py` | 27 (list 2, fail-closed 6, record 10, form 9) | OK |
| Full suite, once at the end | 914 | OK, 0 skipped (`full_suite.txt`) |

---

## The save

Base: `log2_poc_r39_chapters_v5_pre_a.sav` slot 3 (the card 4 point: 7,18, flags to 85, Vegeta leads). It is after 19, so the build moves it back (C bytes, `s10_build.txt`).

| Field | Value | Why | Label |
|---|---|---|---|
| Map, spot | 7,12,1 at (244,40), below the top exit | 7,12 region 0 (flag 85 clear) warps rect (224,0)-(265,17) to 7,15. 7,15 region 0 covers the whole map and starts the 19 table on arrival. The 8 px box is open at the spot and every 4 px up to the warp | C (bytes, collision) |
| Leader | 2 (Vegeta) | Forced by `rom:0x3CCA2E` | C |
| Flags | 85 cleared; 75, 76, 77 and 78-84 kept | 85's one SET is the 19 death table `rom:0x3D4820`. 78-84 are the seven 7,10 enemies on the way | C (sites), L (route order) |
| Gohan, Piccolo +0x14 | `0x5F` to `0x4D` | bit 1 off (ext 81 at `rom:0x3CCA57`, `0x3CCA5B`; back on at the 19 death). Bit 4 off (its only constant sites are chamber exits) | C (sites) |
| Vegeta +0x14 | `0x7F` to `0x6F` | bit 4 off as above; keeps party, selectable, ext 83 (2,1) and ext 82 (2) from the space scene | C (sites) |
| Cooldown | 0 | struct +8 | C |
| Slots 2, 3 | empty | | C |

> [!WARNING]
> Levels (40), stats, items and visited bits stay as in the base slot, which came from a post-chamber save. Vegeta is much stronger than at a real 19 fight (about level 18 after the space scene). This does not change the scene. The fight will be short.

---

## Play steps

1. Open `builds\mockups\2026-10-30-vegeta-19\log2_poc_r39_vegeta19.gba` in mGBA. The `.sav` with the same name sits next to it.
2. Pick Continue, slot 1. Vegeta stands in map 7,12 just below the top exit.
3. Walk up into the exit. Map 7,15 loads and the 19 scene starts: Goku vs 19, the heart virus, Vegeta arrives.
4. After "So, does a machine like yourself ever experience fear?", look for: the power-up pose with the aura sound for about 2.7 s, gold hair, the sound, a white flash, then the HUD with a full yellow pool and 19's boss bar.
5. In the fight: the yellow pool drains; L to the form icon, then B, drops the form; at pool 0 he drops it by himself. Win once while still Super Saiyan and watch the finish scene (Vegeta's beatdown of 19, then "Silly robot"): look for a missing or broken frame on gold Vegeta.
6. Optional guard check: reload, press L to the form icon and B to transform in 7,12, then walk up. He enters the scene as a Super Saiyan. At the line there is no second transform and no flash, and the fight starts in his form.

Tell me if the flash comes too late or too early, or if the pose looks wrong with the HUD off.

---

## Files

| File | What |
|---|---|
| `scripts\permanent\patches\vegeta_19_reveal.py` | The module |
| `scripts\permanent\tests\test_vegeta_19_reveal.py` | 27 tests |
| `scripts\permanent\build_list_trial_vegeta19.txt` | Main list + the trial line |
| `s1_study.txt` | The 19 table and its namers, the force table, base equals r39 |
| `s2_state35.txt`, `s4_ability12.txt` | State 35, transform, HUD toggle, ability 12 listings |
| `s3_form_test.txt` | ext 126, ext 11, appearance entries 8-11 |
| `s5_state35_sites.txt` | Every scripted player transform, HUD state |
| `s6_route.txt`, `s6b_flag78.txt`, `s6c_into_7_15.txt`, `s6d_load_7_15.txt`, `s7_route_maps.txt` | The route from space to 7,15 |
| `s8_record.txt` | The record before and after |
| `s9_combined.txt` | Clash check, combined SHA-1, diff runs |
| `s10_build.txt` | Trial ROM and save SHA-1s, save proof |
| `full_suite.txt` | Full suite run |
| `bible_rows.md` | V19 rows |
