# Vegeta Super Saiyan trial v3: the anime exchange

This report covers the v3 change to the Vegeta trial module.

My verdict on v2 (2026-10-25 12:44 PM): "Vegeta v2 is great!" The v3 ask: 5 quicker ki blasts if possible, else keep 3; Cell walks up and knocks Vegeta back and out with one punch; Gohan walks in and takes the blast that was meant for Vegeta.

---

## Status

The v3 trial ROM is built. It needs one play test by me.

| Ask | Status | Where |
|---|---|---|
| 5 ki blasts in quicker succession, else keep 3 | SHIPPED: kept 3 | Not possible without new code, see "Why 3 blasts" |
| Cell quickly walks up to Vegeta | SHIPPED | 24 px at 2 px a frame (twice the walk speed) |
| A single punch knocks Vegeta back and out | SHIPPED | Hurt pose, 24 px back, then the v2 fall (hair turns black) |
| Same Vegeta-to-Cell distance as v2 | SHIPPED | (52, 8) before and after, by test |
| Gohan walks in and takes Cell's ki blast, standard hit, then the dialogue | SHIPPED | Vanilla hit on the player, then seq 51 |
| Gohan's spot does not break seq 52 | SHIPPED | Seq 52 still places him at (432,472) first |
| Stop the aura loop in both copies | SHIPPED | Attack 1 at the knock-out, attack 2 when he leaves |
| Keep the power-up, the look, attack 2 and the black hair | SHIPPED | Transform, seq 17 and the fall unchanged |
| Tests, full suite, `--list` SHA-1s | SHIPPED | 33 module tests, 805 OK |
| v3 ROM and save (exclusive create) | SHIPPED | `builds\mockups\2026-10-24-vegeta-ssj\` |
| Diff runs v2_cj3 to v3 and r39 to v3 | SHIPPED | See "Proofs" |
| Bible rows (tag VS3) | SHIPPED | `scripts\one-time\2026-10-24-vegeta-ssj\bible_rows_v3.md` (not merged) |

| Pending | My action |
|---|---|
| Play test of attack 1 and the end of attack 2 | Steps in "What to play" |
| 5 blasts with new code | Say "new code" if you want a faster volley (see "Why 3 blasts") |
| Approval | The last line of `build_list_trial_vegeta.txt` moves into the build list |

---

## The new exchange

Seq 50 keeps the v1 power-up and the v2 volley. Cell's answer (the whole vanilla second group) is replaced by three steps.

```
Cell:   ext 121 (58, 1) ; ext 136 (58, 404, 408, 200) ; ext 57 (58, 6)           fast walk, one punch
group:  ext 112 (140, 34) ; ext 95 (140) ; ext 121 (140, 2) ;                    hit sound, flash, hurt pose
        ext 136 (140, 352, 416, 300) ; ext 57 (140, 3)                           knocked back, then the fall
        ext 53 (0, 376, 408) ; ext 55 (0, 3)                                     Gohan walks in
        ext 47 (55)                                                              aura loop off
group:  ext 96 (58, 0, 120) ; ext 60 (0) ; ext 112 (0, 34) ; ext 95 (0) ; ext 57 (0, 2)   Gohan takes the blast
        ext 55 (0, 3)                                                            Gohan faces Cell; seq 51 follows
```

**Spots.** Every final spot is 24 px left of v2. So the layout is the v2 layout, moved left.

| Actor | v2 end spot | v3 end spot |
|---|---|---|
| Cell | (428,408) (seq 40 walk) | (404,408), the punch spot |
| Vegeta | (376,416) | (352,416), after the knock-back |
| Gohan | (400,408) | (376,408), between them |

Vegeta to Cell is (52, 8) in both (CONFIRMED, test `test_knock_back_keeps_the_v2_distance`).

---

## Each step: vanilla precedent and timing

Frame counts are at 60 frames a second. A count marked C comes from a constant in the code. A count marked L uses the mover formula (count = largest axis distance x 256 / speed), which fits the bible's "ext 53 = 1 px a frame" but whose divide argument order I did not trace.

| Step | What runs | Vanilla precedent | Frames |
|---|---|---|---|
| Walk in, power up | v1, unchanged | Goku `rom:0x3D35D4` | 24 (L) + about 160 (L, state 9) |
| 3 blasts | v2 volley group, unchanged | Cell's volley `rom:0x3EB169` | 32 per blast (C) |
| Cell walks up | `ext 121 (58, 1)` then `ext 136 (58, 404, 408, 200)` | ext 136: Cell's punch on Hercule `rom:0x3E8C18` (n 1000) | 12 (L) |
| One punch | `ext 57 (58, 6)` | Cell's scene melee: `rom:0x3E8BE2` (Hercule), table `rom:0x3E6F30` seq 18 and 23 | 16 (C) |
| Hit on Vegeta | `ext 112 (140, 34)`, `ext 95 (140)` | Trunks hit, self-destruct seq 40 (`ext 112 (132, 34)`, `ext 95 (132)`) | 1-2 (L) |
| Knocked back | `ext 121 (140, 2)` then `ext 136 (140, 352, 416, 300)` | Hercule: hit state then `ext 136` (`rom:0x3E8C18`); `ext 121 (x, 2)`: 7 vanilla sites, e.g. `rom:0x3E5907` | 8 (L) |
| Knocked out | `ext 57 (140, 3)` (v2 fall, hair turns black, holds) | Trunks `rom:0x3EAD02` | 64 (C) |
| Aura loop off | `ext 47 (55)` in the same group | `rom:0x3D8C14`: `ext 57 (0, 3)` then `ext 47 (55)` in one group | 0 |
| Gohan walks in | `ext 53 (0, 376, 408)`, in parallel with the fall | v2 vanilla walk `ext 53 (0, 400, 408)` | 56 (L) |
| Cell's blast hits Gohan | the second group | Table `rom:0x3D98AC` seq 1 `rom:0x3D8BF6`: `ext 96 (11, 0, 100)`, `ext 60 (0)`, `ext 112 (0, 34)`, `ext 95 (0)`, `ext 57 (0, 2)` | 16 to fire (C), the flight, 32 hurt (C) |

### Why each choice

**Fast walk (CONFIRMED mechanism, LIKELY look).** ext 136 is the only vanilla move op with a speed. Its handler `@0x0800A346` queues vtable `0x08024C04`. The start `@0x0801D2BC` sets speed = n x 0x290 >> 8 and keeps the facing (`ldrb r7,[r5,#0x10]` `@0x0801D2E0`, `strb r7,[r5,#0x10]` `@0x0801D306`). It sets no state, so a plain ext 136 slides Cell in his stand pose. ext 121 (58, 1) first puts him in the walk state:
- NPC +0x28 `@0x0800D6A6` reads the NPC state table `@0x083ED21C`; word 1 is the NPC walk object `0x03001F30`.
- ext 53's move state calls the same +0x28 with 1 (`mov r1,#0x1` `@0x0800D5AE`). So the walk anim is the one every vanilla NPC walk shows.
- NPC +0x30 (called by the ext 136 start) is `bx lr` (`@0x080260A0`), so the walk state stays during the move.
- No vanilla script runs ext 121 (x, 1). This pair of ops is new; each op is vanilla.

**One punch (CONFIRMED).** State 6 is Cell's vanilla scene melee. Its enter `@0x0800E160` shows anim 6 and starts a swing sound; its tick `@0x0800E19C` ends after 0x10 frames (`cmp r2,#0x10` `@0x0800E1A8`) and sets state 0. Set 58 has anim 6 in all 4 directions (test `test_set_58_has_every_anim_cell_uses`).

**No hit wait on the punch (a choice).** Hercule's precedent waits with `ext 60 (72)` for the punch. That wait asks the world about the actor's spot (message 0x11, not traced), and I do not know the contact distance it needs. So Vegeta's reaction starts after the punch, as in table `rom:0x3E6F30` seq 18 (`ext 57 (29, 6)`, then the victim's sound, pulse and fall, no ext 60). This cannot freeze the scene. The cost: the reaction comes up to about 8 frames after the arc shows (the arc is frames 2-3 of 4).

**Punch spot (LIKELY look).** `s6_reach.py` measures each frame's opaque box from the actor spot. Cell's anim 6 facing left reaches x - 11 (frame 1, the fist) and x - 20 (frame 2, the arc). At x 404 the fist reaches Vegeta's hair and the arc crosses his head (`s6_reach.png`, row 2). Spots 396, 408 and 412 are in the same sheet.

**Knock-back (CONFIRMED mechanism).** ext 121 (140, 2) sets the hurt pose with no wait (done check `@0x08026498` returns 1). ext 136 then moves him back 24 px with the pose kept. The move tick `@0x0801090A` sets state 0 when he arrives, so the fall (state 3) follows the move, not the other way round. A fall first would make him stand up at the end of the move.

**Gohan's walk (CONFIRMED path).** Gohan walks from (432,464): self-destruct seq 8 (`0x083EA638`) puts him there, and no move op names actor 0 in seq 9-49 (test). He walks while Vegeta falls, as he walked during Cell's volley in v2.

**The blast hits Gohan, not Vegeta (a choice).** Cell's ext 96 targets Gohan (actor 0). Gohan stands on the line between them, so the shot reads as the blast meant for Vegeta. A blast aimed at Vegeta would leave `ext 60 (0)` waiting for a hit that may never come. The group is the vanilla shape at `rom:0x3D8BF6`, where an NPC hits the player.

---

## Why 3 blasts

Vegeta keeps 3 blasts. A quicker volley needs new code (CONFIRMED, listings `s7_v3_code_base.txt` section 1):
- Every ki op stores a fixed hold: ext 96 `mov r1,#0x20` `@0x0800A19A`, ext 142 `@0x0800A1F6`, ext 99 `mov r2,#0x20` `@0x0800A258`.
- The ticks fire at count 0x10 (`cmp r0,#0x10` `@0x08011AEE`, `@0x08011EB6`) and end at 0.
- No ki op takes a hold argument. One actor fires at most one blast every 32 frames.
- No vanilla scene does better: no group has more than 3 `ext 96` from one attacker (table walk over 1,823 records, `s5_v3_ops_base.txt` section 4). Byte pairs find 3 more `02 60` pairs, and all 3 are noise: one inside push operands, two in map items (LIKELY, `s8_b_only_base.txt`). A script that no aligned word names would not appear in either shape.

5 blasts at the same rate are possible, but they are not quicker (160 frames instead of 96). Your words say "If not keep the 3", so I kept 3. Cell's reaction to each hit stays vanilla (v2).

> [!TIP]
> A faster volley is possible with new code: a copy of the ext 96 handler with a hold of, for example, 0x18 in a free ext slot. That is engine code, so I did not build it. Say "new code" if you want it.

---

## The aura loop

Both copies now stop sound 55 (the Super Saiyan aura loop) once (CONFIRMED, bytes and test `test_aura_loop_stops_in_both_copies`).

**Vanilla rule (CONFIRMED, table walk, `s5_v3_ops_base.txt` section 5).** Every script start of sound 55 in the base ROM has a stop later in its own table. An NPC's loop stops when he reverts or the scene ends:
- Goku's power-up `rom:0x3D35E9` (seq 10) stops at `rom:0x3D37AD` (seq 20, the scene end).
- Trunks `rom:0x3B7C2C` stops at `rom:0x3B80FD`, right after his revert (`ext 57 (133, 21)`, `ext 52 (133)`, `ext 51 (132, ...)`). Trunks `rom:0x3BE144` stops at `rom:0x3BE5E9` the same way.
- `rom:0x3D8C14` stops a loop in the same group as the player's knock-down.

This extends the fullpower-hud row that found no stop within 0x400 bytes of three starts: their stops sit further on, in the same table. A second shape agrees: the fullpower-hud byte sweep finds 9 starts in r39, these 8 plus the r27 copy `rom:0x89A693`.

**Attack 1.** `ext 47 (55)` is in the knock-out group, as at `rom:0x3D8C14`. A non-actor op in a group runs when the script reaches it, so the hum stops as the punch reaction starts (LIKELY, the same as the vanilla group).

**Attack 2.** `ext 47 (55)` follows `ext 52 (140)`, where Vegeta leaves at the end of seq 17. This mirrors the Trunks revert.

> [!NOTE]
> `sound_stop` `@0x0801FC22` ends the first channel that plays entry 55. If Gohan's own form loop also plays in this stretch, the stop can end that channel instead of Vegeta's. The number of loops is still back to what it was before Vegeta's power-up, and both play the same sample (LIKELY; channel order not traced).

---

## The module change

The module changes the seq 50 and seq 17 copies only. The base sites are the v1 sites.

- `exchange()` builds the three steps above. Constants: `PUNCH_SPOT`, `KNOCKED_TO` and `GOHAN_TO` derive from the v2 end spots and `SHIFT` = 24.
- `SHAPE["seq50"]` replaces +0x35 (the whole vanilla second group, 0x5B bytes, `CELL_ANSWER`) with `exchange()`. The v2 +0x7F entry is gone.
- `EDITS["seq50"]` has no 137 pushes left: the two SHAPE spans hold every 137 after the insert. The nested-edit guard would raise otherwise.
- `SHAPE["seq17"]` puts `ext 47 (55)` before `push 58,0,0` at +0x63, right after the remove of 140.
- The source checks are unchanged and run before the first write. A second run raises.
- Seq 50 copy: 0xEA bytes in v2, 0x101 in v3. Seq 17 copy: 0x98 to 0x9C.

The v2 module and tests are backed up in `archive\2026-10-25-vegeta-ssj-v2\`.

---

## Proofs

**Builds** (`scripts\one-time\2026-10-24-vegeta-ssj\make_trial_vegeta_v3.txt`):

| Build | SHA-1 |
|---|---|
| `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v3.gba` (new, exclusive create) | `6d80e874d14e81cca1898ef8b1fd5324c3b277f8` |
| CLI `--list build_list_trial_vegeta.txt` | `6d80e874d14e81cca1898ef8b1fd5324c3b277f8` (equal) |
| CLI `--list` (main) | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` (r39, unchanged, bytes equal) |
| CLI `--list build_list_trial.txt` | `76e610fb3ca4febcf1cefd1199ef39fad10ccbf8` (celljr v3, unchanged) |
| `log2_poc_r39_vegeta_v3.sav` (byte copy of the v2_cj3 save) | `aa8efb2adaa7aa87f4cff27ceb7244368bd02759` |
| v2_cj3 ROM `log2_poc_r39_vegeta_v2_cj3.gba` (read, not changed) | `f94fd65807a7db0957fcbc34b65c0473282f6b09` |

**Diff v2_cj3 to v3:** 265 bytes in 18 runs, 0 bytes outside the v3 sites and the v2 copies.

| Run | Bytes | What |
|---|---|---|
| `rom:0x3EC798` | 1 | seq 17 table word, low byte (the copy moved from `0x90A768` to `0x90A780`) |
| `rom:0x90A703`-`0x90A77C` (10 runs and the first 2 bytes of the next) | 111 | seq 50 copy from +0x87: the exchange; v2 equal bytes break the runs |
| `rom:0x90A77D`-`0x90A784` (the rest of that run) | 8 | alignment gap `0x90A77D`-`0x90A77F` and the start of the moved seq 17 copy |
| `rom:0x90A786`-`0x90A81B` (6 runs) | 145 | the moved seq 17 copy |

The listing names `0x90A77D`-`0x90A784` "v2 seq17 copy" because its cut takes the first site that matches. The first 0x87 bytes of the seq 50 copy (the transform and the volley) did not change.

**Diff r39 to v3:** 1,302 bytes in 16 runs, 0 bytes outside the celljr v3 and vegeta v3 sites.
- Celljr v3 runs: `rom:0x3E9DC4`, `0x3EA478`, `0x3EA47A`, `0x3EB7E9`, `0x40DA84`, `0x40DA94`, and `rom:0x90A308`-`0x90A4CD` (5 runs).
- Vegeta runs: `rom:0x3EB232` (seq 52 byte), `rom:0x3EB7C8` (seq 50 word), `rom:0x3EC798` (seq 17 word), `rom:0x90A780`-`0x90A81B` (seq 17 copy).
- The celljr allocations and the seq 50 copy are adjacent, so they show as one run `rom:0x90A4D0`-`0x90A77C`.

**Tests:** `test_vegeta_ssj_scene.py` has 33 tests, all pass.
- Changed for v3: `SceneTests.check` tails (seq 50: volley plus exchange; seq 17: the aura stop), the set 58 count in `test_copies_carry_super_perfect_cell` (+9 over vanilla), and the v2 fall test, now `test_fall_after_the_knock_back_and_nothing_after`.
- New: 6 tests in `ExchangeTests` (the exchange ops, the v2 distance, Gohan between them and seq 52, the aura stop in both copies, the vanilla precedents, the code constants) and `test_set_58_has_every_anim_cell_uses`.

**Full suite:** 805 tests, OK (`scripts\one-time\2026-10-24-vegeta-ssj\suite_v3.txt`, 132 s). That is 771 plus 27 `test_chapter_cards` tests from another task plus my 7.

---

## What to play

Load `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v3.gba` with the `.sav` next to it. It holds all trial changes (Cell Jr v3 and Vegeta v3).

1. Pick **slot 3**: Cell Games Arena arrival, map 14,1, Goku leads.
2. Play the Cell Games through to the self-destruct and Super Perfect Cell's return.
3. **Attack 1:** after "He's back!!!!", Cell knocks Trunks down and Vegeta says "He will pay!!!!".
4. Win the Super Perfect Cell fight. **Attack 2** comes in the beam struggle, after "SAY GOODBYE!!!".

> [!WARNING]
> Do not load a v2 or v2_cj3 save state inside attack 1. The seq 50 record has new bytes at the same address. A state taken before "He will pay!!!!" LIKELY works, because the scene reads its table word when it starts.

Watch these points. Each needs the emulator; I did not run one.
- The power-up and the 3 blasts play as in v2.
- **Cell's walk:** he walks to Vegeta at twice his walk speed, in his walk pose, facing left. If he slides in his stand pose, tell me; the fallback is the plain walk (24 frames).
- **The punch:** one swing with a swing sound. Does it look like it connects? If it falls short or goes too deep, the spot is one constant.
- **The knock-back:** Vegeta flashes, takes the hit sound, flies back 24 px in his hurt pose facing Cell, then falls (gold to black hair). Look for one frame of a standing pose between the flight and the fall (LIKELY 0 or 1 frame).
- **The aura hum stops** at the punch reaction.
- **Gohan** walks in while Vegeta falls and stops between them, facing Cell.
- **Cell's blast:** he fires once at Gohan; Gohan flinches with the standard hit. Then Cell says "Why do you protect Vegeta?". If the scene stops after the blast, tell me (the hit wait on Gohan is the vanilla shape, so I do not expect it).
- Vegeta lies with black hair through Cell's line, then leaves in seq 52 (v2).
- **Attack 2:** the aura hum stops when Vegeta leaves at the end of the struggle.

---

## Files

| File | What |
|---|---|
| `scripts\permanent\patches\vegeta_ssj_scene.py` | The trial module, v3 |
| `scripts\permanent\tests\test_vegeta_ssj_scene.py` | 33 tests |
| `scripts\one-time\2026-10-24-vegeta-ssj\s5_v3_ops.py`, `s5_v3_ops_base.txt` | ext 136 sites, ext 121 and ext 57 by state, ki ops on the player, ext 96 runs per group, sound 55 starts and stops |
| `scripts\one-time\2026-10-24-vegeta-ssj\s6_reach.py`, `s6_reach_r39.txt`, `s6_reach.png` | Frame boxes from the actor spot; Cell's punch against Vegeta at 4 spots |
| `scripts\one-time\2026-10-24-vegeta-ssj\s7_v3_code.py`, `s7_v3_code_base.txt` | The listings behind the design |
| `scripts\one-time\2026-10-24-vegeta-ssj\s8_b_only.py`, `s8_b_only_base.txt` | The byte-pair-only sites of ext 136, 121 and 96, sorted into calls or noise |
| `scripts\one-time\2026-10-24-vegeta-ssj\make_trial_vegeta_v3.py`, `make_trial_vegeta_v3.txt` | Build and diff proofs |
| `scripts\one-time\2026-10-24-vegeta-ssj\suite_v3.txt` | Full suite output |
| `scripts\one-time\2026-10-24-vegeta-ssj\bible_rows_v3.md` | Bible rows, tag VS3 |
| `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v3.gba`, `.sav` | The v3 trial ROM and save |
| `archive\2026-10-25-vegeta-ssj-v2\` | The v2 module and tests |
