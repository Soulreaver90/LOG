# Vegeta Super Saiyan trial v2: three blasts and a knock-down

This report covers the v2 change to the Vegeta trial module.

My verdict on v1 (2026-10-25 9:16 AM): "Have vegeta do a couple of quick ki blasts, he does one and cell responds with 3, have him do 3 and when cell does his 3, it knocks vegeta down instead of him remaining standing."

---

## Status

The v2 trial ROM is built. It needs one play test by me.

| Ask | Status | Where |
|---|---|---|
| Find the scene: Vegeta fires one, Cell answers with 3 | SHIPPED | Attack 1, seq 50 only (see "The scene") |
| Vegeta fires 3 quick ki blasts | SHIPPED | Seq 50 copy, first group |
| Cell's 3 blasts knock Vegeta down | SHIPPED | Seq 50 copy, `ext 57 (140, 3)` |
| After the fall, Vegeta stays down until seq 52 removes him | SHIPPED | No op on him after the fall |
| Keep the v1 power-up and look | SHIPPED | Transform and seq 17 unchanged |
| Tests, full suite, `--list` SHA-1s | SHIPPED | 26 module tests, 726 OK |
| v2 ROM and save (exclusive create) | SHIPPED | `builds\mockups\2026-10-24-vegeta-ssj\` |
| Diff runs v1 to v2 and r39 to v2 | SHIPPED | See "Proofs" |
| Bible rows (tag VS2) | SHIPPED | `scripts\one-time\2026-10-24-vegeta-ssj\bible_rows_v2.md` (not merged) |

| Pending | My action |
|---|---|
| Play test of attack 1 | Steps in "What to play" |
| Hair while he lies down | Say "keep black" (vanilla art, no change) or "keep gold" (needs 4 new lying frames in a cloned set, scene only; see the warning under "Change 2") |
| Approval | The last line of `build_list_trial_vegeta.txt` moves into the build list |

---

## The scene

Only attack 1 has the shape you describe. Attack 2 keeps its v1 change.

| | Attack 1 (seq 50) | Attack 2 (seq 17) |
|---|---|---|
| Vegeta's ki ops | 1 x `ext 96 (137, Cell, 100)` `rom:0x3EB157` | 1 x `ext 142 (137, Cell, 100)` `rom:0x3EBDB6` |
| Cell's answer | 3 x `ext 96 (Cell, 137, 120)` `rom:0x3EB172`, `0x3EB17B`, `0x3EB184` | none: `ext 95` (flash) and `ext 112 (137, 20)` (sound) only |
| v2 change | yes | no |

- CONFIRMED (bytes, base ROM, `s4_knockdown_base.txt` section 1). In the base ROM Cell is set 30; in r39 he is set 58 (superperfect_cell).
- Test: `test_vanilla_seq_50_is_one_blast_answered_by_three`, `test_seq_17_has_one_blast_and_no_answer`.

---

## Change 1: three quick blasts

Vegeta now fires the way Cell fires in the same record.

**Vanilla precedent (CONFIRMED, bytes).** Cell's volley in seq 50 is one group (`ext 63` `rom:0x3EB169` to `ext 64` `rom:0x3EB1C2`):
- 3 x `ext 96 (Cell, 137, 120)` on one actor.
- Then on the target, 3 x (`ext 60`, `ext 57 (137, 2)`, `ext 95`): wait for the hit, hurt, flash.

**The new first group** mirrors it with the roles swapped. It keeps Vegeta's own speed value 100 and Cell's own vanilla reaction:

```
ext 63
3 x ext 96 (140, 58, 100)
3 x (ext 60 (58) ; ext 57 (58, 2) ; ext 95 (58))
ext 64
```

**Timing (CONFIRMED, listings).** Each `ext 96` holds its actor for 32 frames and fires at frame 16:
- The command tick `@0x08011AE2` counts +8 down from 0x20 and fires at 0x10 (`cmp r0,#0x10` `@0x08011AEE`).
- The done check `@0x08011BA8` ends the command when +8 is 0.
- So the 3 blasts leave about every half second, the same rhythm as Cell's vanilla volley.
- Each blast restarts state 5 (ki pose, anim 5), which also runs 0x20 frames (`@0x0800E25A`).

> [!NOTE]
> The hit wait `ext 60` asks the world about the actor's spot (message 0x11, `@0x08011D0C`). I did not trace that message. Cell's own volley uses the same three-wait shape at speed 120, so the shape is proven in vanilla. Vegeta's blasts use speed 100 (LIKELY: +0x10 = n x 0x7AE is the speed). All 3 blasts share n, so they arrive 32 frames apart at any speed, and Cell's hurt also lasts 32 frames. If Cell misses a reaction or the scene freezes, first try n = 120, the exact mirror of Cell's vanilla volley. A freeze means world message 0x11 needs tracing.

---

## Change 2: the knock-down

Cell's third blast now knocks Vegeta down.

**Vanilla precedent (CONFIRMED, bytes).** In the same table, Cell knocks Trunks down in seq 40 (`0x083EACD0`):
- `ext 96 (Cell, 132, 120)` `rom:0x3EACE5`, `ext 60 (132)`, `ext 112 (132, 34)`, `ext 95 (132)`.
- `ext 57 (132, 2)` `rom:0x3EACFB` (hurt), then `ext 57 (132, 3)` `rom:0x3EAD02` (knocked down).
- 31 `ext 57 (x, 3)` sites by the table walk and 26 by byte pairs (26 in both). The 5 table-walk-only sites (`rom:0x3D487B`, `0x3D8BCB`, `0x3E4A13`, `0x3E4B73`, `0x3EA48B`) are each the first op of a record; the byte-pair shape decodes back from up to 24 bytes and starts inside the record header, so it misses them (LIKELY). The beam struggle uses the same state on sets 103, 121, 76 and 156 (seq 7 and 11).

**The new op.** After the third hurt and flash on Vegeta, the record runs `ext 57 (140, 3)`. It sits before Gohan's walk (`push 0,400,408 ; ext 53`), inside the same group. Gohan walks in parallel, as in vanilla.

**State 3 (CONFIRMED, listings `s4_knockdown_base.txt` section 3).**
- Enter `@0x0800E130` sets anim 3 (set + 0x7C).
- Tick `@0x0800E142` shows frame = count >> 4 and ends at 0x40 frames by `bl 0x08007688` (`@0x0800E154`). The fall takes 64 frames.
- `@0x08007688` leaves the state and enters the hold state `0x03001F3C`. Its enter `@0x080260C0` and tick `@0x08026094` are both `bx lr`. So the actor keeps the last frame (frame 3, lying down) and does not stand up.
- Hurt (state 2) and ki (state 5) end differently: they set state 0 (stand) after 0x20 frames.
- `ext 57` ends when the actor leaves state 3 (`@0x0800DF74`), so the group ends after the fall.
- LIKELY: scene NPCs use these state objects. The table `@0x083B5278` is the player's; Trunks in seq 40 is the NPC precedent.

**Set 140 has the anim (CONFIRMED, row pointers).** Set 140 has anim 3 in all 4 directions, 4 frames each (`s4_knockdown_base.txt` section 4).

> [!WARNING]
> **Vegeta's hair goes black when he falls.** Set 140 anim 3 frame 0 is gold, frame 1 brown, frames 2 and 3 black (`sets_137_140_anim2_3.png`). This is the vanilla Super Saiyan knock-down art: the sets of Super Saiyan Goku and Gohan do the same (bible T5 row). Set 139 has the same tiles, so no vanilla gold lying frame exists. He lies with black hair through Cell's line until seq 52 removes him. The only route to a gold Vegeta on the ground is art. Set 140 is also playable Super Saiyan Vegeta (appearance entry 11), so an edit to set 140 anim 3 also changes his knock-down in fights. A scene-only gold lying pose needs a cloned set with new lying frames. I drew nothing. Say "keep black" or "keep gold".

---

## After the fall

Vegeta stays down until seq 52 removes him. No vanilla line needs him up.

- **No op after the fall (CONFIRMED, bytes, test).** In the seq 50 copy, after `ext 57 (140, 3)` come only Gohan's walk, Gohan's face right and `ext 64`.
- **Seq 51 is text only (CONFIRMED).** Table word 50 (`0x083EB1C6`) is type 1: Cell's line "Why do you protect Vegeta? I'll never understand you Saiyans. You are stubborn." The line fits him lying behind Gohan.
- **Seq 52 removes him (CONFIRMED, v1 byte).** `push 140 ; ext 52` at `rom:0x3EB231`. No other op in seq 52 names 137 or 140.
- **Vanilla does the same with Trunks (CONFIRMED).** No op touches Trunks between his fall (seq 40) and his removal (seq 48 `rom:0x3EB02F`).
- **Nothing else stands him up (LIKELY).** `ext 51` spawns from a static item `0x03000C04` (`@0x08009CC4`). No literal in the code names `0x03000C04` except that handler, and none names `0x03000C14` (its step count and step pointer). A write through a nearby base or a block fill would not show in that search. If nothing writes them, the spawned Vegeta has no NPC steps that could reset his state.

Why I chose this: your words say he gets knocked down "instead of him remaining standing", and the vanilla Trunks scene shows the same pattern.

---

## The module change

The module changes only the seq 50 copy. The base sites are the v1 sites.

- `EDITS["seq50"]` no longer swaps the push at +0x1C, because the new first group replaces it.
- New table `SHAPE["seq50"]`:
  - +0x1A: the whole vanilla first group (`ext 63` to `ext 64`, 0x1B bytes) becomes the transform plus the 3-blast group.
  - +0x7F: `ext 57 (140, 3)` goes before Gohan's walk.
- The source checks are unchanged: the r39 record SHA-1, the table words, the seq 52 byte and the map 14,4 item, all before the first write.
- New guard: `record_edits` raises when one edit starts inside another. `npc_gi.relocate` would otherwise write a nested edit twice with no error.
- The seq 17 copy is the v1 copy byte for byte (a byte compare of the two ROMs: moved from `0x90A734` to `0x90A768`).
- Seq 50 copy: 0xB5 bytes in v1, 0xEA bytes in v2.

The v1 module and tests are backed up in `archive\2026-10-25-vegeta-ssj-v1\`.

---

## Proofs

**Builds** (`scripts\one-time\2026-10-24-vegeta-ssj\make_trial_vegeta_v2.txt`):

| Build | SHA-1 |
|---|---|
| `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v2.gba` (new, exclusive create) | `11e443ad586bb6e9f14846abb76a5dd648720f38` |
| CLI `--list build_list_trial_vegeta.txt` | `11e443ad586bb6e9f14846abb76a5dd648720f38` (equal) |
| CLI `--list` (main) | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` (r39, unchanged, bytes equal) |
| CLI `--list build_list_trial.txt` | `1826ca8f6b498844323f9c487cee1864025c3aa8` (celljr v2, unchanged) |
| `log2_poc_r39_vegeta_v2.sav` (byte copy of the v1 save) | `aa8efb2adaa7aa87f4cff27ceb7244368bd02759` |
| v1 ROM `log2_poc_r39_vegeta.gba` (read, not changed) | `cd9fd893c55d3bf8df40a2b7af6abf7b1a2d19f8` |

**Diff v1 to v2:** 299 bytes in 15 runs, 0 bytes outside the v2 sites and the v1 copies.

| Run | Bytes | What |
|---|---|---|
| `rom:0x3EC798` | 1 | seq 17 table word (low byte: the copy moved) |
| `rom:0x90A6C5`-`0x90A762` (12 runs) | 143 | seq 50 copy: the new first group and the fall; v1 equal bytes break the runs |
| `rom:0x90A764`-`0x90A788` | 37 | seq 50 copy end (2), the alignment gap `0x90A766`-`0x90A767` (v1 seq 17 bytes, now 0xFF), the moved seq 17 copy start |
| `rom:0x90A78A`-`0x90A7FF` | 118 | the moved seq 17 copy |

The seq 50 table word and the seq 52 byte did not change from v1. The listing names `0x90A766`-`0x90A788` "v1 seq17 copy" because its cut takes the first site that matches; the bytes from `0x90A768` on are the v2 seq 17 copy.

**Diff r39 to v2:** 1,275 bytes in 16 runs, 0 bytes outside the celljr v2 and vegeta v2 sites.
- Celljr v2 runs: `rom:0x3E9DC4`, `0x3EA478`, `0x3EA47A`, `0x3EB7E9`, `0x40DA84`, `0x40DA94`, and `rom:0x90A308`-`0x90A67B` (allocations).
- Vegeta runs: `rom:0x3EB232` (seq 52 byte), `rom:0x3EB7C8` (seq 50 word), `rom:0x3EC798` (seq 17 word), `rom:0x90A67C`-`0x90A765` (seq 50 copy), `rom:0x90A768`-`0x90A7FF` (seq 17 copy).
- The celljr allocations and the seq 50 copy are adjacent, so they show as one run `rom:0x90A4D0`-`0x90A765`.

**Tests:** `test_vegeta_ssj_scene.py` has 26 tests, all pass: the 18 v1 tests (3 changed for v2: the seq 50 tail in `SceneTests.check`, the set 58 count in `test_copies_carry_super_perfect_cell`, and anim 3 added to `ANIMS_USED` for `test_set_140_has_every_anim_the_attacks_use`) and 8 new tests in `VolleyAndFallTests`. Full suite: 726 tests, OK (718 before plus 8 new; 222 s) (`scripts\one-time\2026-10-24-vegeta-ssj\suite_v2.txt`).

---

## What to play

Load `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v2.gba` with the `.sav` next to it. It holds all trial changes (Cell Jr v2 and Vegeta v2).

1. Pick **slot 3**: Cell Games Arena arrival, map 14,1, Goku leads.
2. Play the Cell Games through to the self-destruct and Super Perfect Cell's return.
3. **Attack 1:** after "He's back!!!!", Cell knocks Trunks down and Vegeta says "He will pay!!!!".

> [!TIP]
> Your v1 save states (`.ss1`, `.ss2`) were not copied. A state taken before "He will pay!!!!" LIKELY works with the v2 ROM, because the scene reads its table word when it starts. A state taken inside the attack can break, because the v2 record has new bytes at those addresses.

Watch these points (each needs the emulator; I did not run one):
- Vegeta powers up gold as in v1, then fires 3 blasts about half a second apart (CONFIRMED timing, see Change 1).
- Cell flinches and flashes once for each of the 3 blasts. If he reacts fewer times or the scene stalls, tell me: the first try is the blast speed 120 (see the note under Change 1).
- Cell fires his 3 blasts. Vegeta flinches on each, then falls on the third (64 frames).
- His hair goes from gold to black as he falls (vanilla art, see the warning).
- Gohan walks in front of him while he falls, as in vanilla.
- Vegeta stays on the ground through Cell's line "Why do you protect Vegeta?", then leaves with the others in seq 52.
- He does not turn while lying down (LIKELY: the spawned Vegeta has no NPC steps).
- Attack 2 in the beam struggle plays as in v1.

---

## Files

| File | What |
|---|---|
| `scripts\permanent\patches\vegeta_ssj_scene.py` | The trial module, v2 |
| `scripts\permanent\tests\test_vegeta_ssj_scene.py` | 26 tests |
| `scripts\one-time\2026-10-24-vegeta-ssj\s4_knockdown.py`, `s4_knockdown_base.txt` | Ki ops of both attacks, all `ext 57 (x, 3)` sites, state and command code, sets 137 and 140 anims 2 and 3 |
| `scripts\one-time\2026-10-24-vegeta-ssj\sets_137_140_anim2_3.png` | Hurt and knock-down frames of sets 137 and 140 |
| `scripts\one-time\2026-10-24-vegeta-ssj\make_trial_vegeta_v2.py`, `make_trial_vegeta_v2.txt` | Build and diff proofs |
| `scripts\one-time\2026-10-24-vegeta-ssj\suite_v2.txt` | Full suite output |
| `scripts\one-time\2026-10-24-vegeta-ssj\bible_rows_v2.md` | Bible rows, tag VS2 |
| `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v2.gba`, `.sav` | The v2 trial ROM and save |
| `archive\2026-10-25-vegeta-ssj-v1\` | The v1 module and tests |
