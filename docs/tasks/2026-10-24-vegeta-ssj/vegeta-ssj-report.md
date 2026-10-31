# Vegeta goes Super Saiyan when he attacks Super Perfect Cell: trial report

This report covers the trial module for my ask.

My ask (2026-10-24 9:05 PM): "Also when Vegeta attacks S perfect cell, have him go super saiyan please!"

---

## Status

The trial ROM is built. It needs one play test by me.

| Ask | Status | Where |
|---|---|---|
| Find the scene where Vegeta attacks Super Perfect Cell | SHIPPED | Two scenes, see "The scenes" |
| Find Vegeta's Super Saiyan look and reuse the vanilla mechanism | SHIPPED | Set 140, vanilla NPC transform |
| Form, ki drain, ki pool and cooldown if he is the controlled fighter | SHIPPED (no change) | He is a scene actor only |
| Trial module `vegeta_ssj_scene.py` with tests | SHIPPED | `scripts\permanent\patches\`, `scripts\permanent\tests\` |
| New list `build_list_trial_vegeta.txt` | SHIPPED | `scripts\permanent\` |
| Trial ROM and save | SHIPPED | `builds\mockups\2026-10-24-vegeta-ssj\` |
| Full suite and diff runs | SHIPPED | See "Proofs" |
| Bible rows (tag VSJ) | SHIPPED | `scripts\one-time\2026-10-24-vegeta-ssj\bible_rows.md` (not merged) |

| Pending | My action |
|---|---|
| Play test of both scenes | Steps in "What to play" |
| Keep attack 2 (beam struggle) or drop it | Say "keep" or "drop" |
| Approval | Move the last line of `build_list_trial_vegeta.txt` into the build list |

> [!NOTE]
> The module changes two scenes. Your words cover both, because Vegeta attacks Super Perfect Cell twice. Attack 2 sits in the beam struggle, which another study reads. That study writes no patch, so there is no clash today.

---

## The scenes

Vegeta attacks Super Perfect Cell twice. In both, he is a scene actor (NPC set 137), not the controlled fighter.

| | Attack 1 | Attack 2 |
|---|---|---|
| Map | 14,3 | 14,4 (beam struggle) |
| Table | `rom:0x3EB704` (type 24 Cell's death event) | `rom:0x3EC758` (type 25 Cell's death event) |
| Lead-in | seq 49 "He will pay!!!!" (after Trunks falls) | seq 12 "VEGETA: ARGHHH!!!", seq 16 "SAY GOODBYE!!!" |
| Record | seq 50, word 49 `rom:0x3EB7C8`, record `0x083EB134` (0x91 bytes) | seq 17, word 16 `rom:0x3EC798`, record `0x083EBD7C` (0x74 bytes) |
| What Vegeta does | walks to (376,416), fires at Cell (`ext 96 (137, 58, 100)`), takes 3 blasts | flies to (208,376), fires a big blast (`ext 142 (137, 58, 100)`) |
| Where he leaves | seq 52 `push 137 ; ext 52` at `rom:0x3EB231` | the same record removes 137; seq 20 spawns base 137 again |

Evidence (CONFIRMED, bytes, `s1_scene_r39.txt`):
- Attack 1 opens with `rom:0x3EB137 1d03821285708640 push 137,376,416` and `rom:0x3EB13F 0235 ext 53`.
- Attack 2 holds `rom:0x3EBDAF 1d038212748148 push 137,58,100` and `rom:0x3EBDB6 028E ext 142`.
- Vegeta is map 14,3 item 1 (`rom:0x408F40`, set 137) and map 14,4 item 1 (`rom:0x409218`, set 137, (112,272)).

**Leader (CONFIRMED).** Gohan leads from Gohan's table `rom:0x3EA400` seq 1 (`ext 70 (0)`) to post-Cell seq 20 (`ext 70 (1)`) (bible CGS rows). Both records address Gohan as actor 0, for example `rom:0x3EB1B3 push 0,400,408 ; ext 53`.

---

## The mechanism

Vegeta's Super Saiyan look exists. The module reuses the vanilla NPC transform.

**The set (CONFIRMED).** Set 140 is the game's own Super Saiyan look for set 137.
- Appearance entry 8 is `00 89 6A 18 0B 0B`: set 137, transform target entry 11.
- Entry 11 is `01 8C 6B 19 08 08` with form object `0x030021EC`: set 140, Super Saiyan.
- Set 139 (Super Vegeta, entry 10) decodes to the same tiles as set 140 in all 64 rows (`s3_set_compare_r39.txt`). So the choice does not change the look. Set 140 is the pair of the NPC's set 137.
- `sets_137_140.png` shows gold hair in the same armor as set 137.

**The transform (CONFIRMED, vanilla).** Vanilla turns an NPC Super Saiyan in three scenes. The module copies Goku's at `rom:0x3D35D4`:

```
ext 46 (55) ; ext 57 (60, 9) ; ext 46 (23) ; ext 52 (60) ; ext 51 (61, 432, 408) ; ext 69 (90) ; ext 55 (61, 3)
```

Trunks does the same at `rom:0x3B7C1C` (132 to 133) and `rom:0x3BE134` (128 to 134). State 9 plays the power-up anim, which ends gold. The swap is a remove and a spawn, with no flash. The module drops the 90-frame wait.

**The changes.** The module writes three base sites and two new records.

| Site | Old | New |
|---|---|---|
| `rom:0x3EB7C8` (table `rom:0x3EB704` word 49) | `0x083EB134` | the seq 50 copy `0x0890A67C` |
| `rom:0x3EB232` (seq 52 remove) | `89` (137) | `8C` (140) |
| `rom:0x3EC798` (table `rom:0x3EC758` word 16) | `0x083EBD7C` | the seq 17 copy `0x0890A734` |

Each copy is the vanilla record with two edits:
1. The transform goes in at one point, with Vegeta's spot: (376,416) after he walks there and faces right (attack 1), or (112,272) after the camera pan and before the camera follows him (attack 2).
2. Every later push of 137 becomes 140: 13 pushes in seq 50 and 6 in seq 17, including the remove at the end of seq 17.

**Set 140 has every anim the attacks use (CONFIRMED for rows, LIKELY for the state to anim link).**
- Anims used: 0 (stand), 1 (walk, `ext 53`), 2 (hurt, `ext 57 (n, 2)`), 5 (ki, `ext 96` and `ext 142`), 12 (fly, `ext 54`). Set 140 has all of them.
- `ext 96` and `ext 142` put the attacker in state 5: `mov r1,#0x5` at `@0x08011AC4` and `@0x0801EBF8`, then actor vtable +0x28.
- `ext 60`, `ext 95` and `ext 112` set no state (listings `@0x080260D0`, `@0x08011A7C`, `@0x08016310`).
- Set 140 lacks anims 9, 14 and 17. Only the power-up uses anim 9, and it runs on set 137 before the swap.

**No conflict (CONFIRMED, checked in code and tests).**
- Records `0x083EB134` and `0x083EBD7C` hold 8 and 3 superperfect_cell bytes (set 58). The module copies them and writes none of them.
- None of the three base sites is a superperfect_cell or celljr_fight site.
- The old records stay in the ROM, unchanged and unnamed.

> [!WARNING]
> **Merge note for a later beam struggle trial.** This module repoints `rom:0x3EC798` (table `rom:0x3EC758` word 16, seq 17). A beam struggle module that checks or edits that word or record `0x083EBD7C` must run before `vegeta_ssj_scene` in the list, or build on this module's copy. Otherwise its source check fails.

---

## Form, ki and cooldown

Vegeta is never the controlled fighter in these scenes. No form rule changes.

- **Records (CONFIRMED).** The new bytes hold no `ext 70`, `ext 73`, `ext 82`, `ext 83` or `ext 115` (test `test_no_leader_record_or_unlock_op`). His record stays at entry 8, and Gohan stays the leader.
- **Form, ki drain, ki pool (CONFIRMED).** These run on the leader's record entry. Gohan leads and his entry does not change, so they run exactly as in v2.
- **Cooldown (CONFIRMED for the player state table).** The cooldown is one value for the whole party (save struct +8, bible FCD). The power-up does not touch it:
  - Player state 9 is object `0x03002174` (state table `@0x083B5278` word 9), vtable `0x08025B80` (init `@0x08023230`).
  - Its tick +4 is `@0x08011D4A`, the shared anim helper. That helper writes no struct +8; the FCD two-shape sweep finds the only writers at `@0x080155EE` (state 0x23), `@0x08015632` (state 0x25 tick `@0x0801560E`) and `@0x08017036` (base tick).
  - Its done callback +0x14 is `@0x08011D94` (`bl 0x08007688`), not `transform` (`@0x0801563C`, which only state 0x25 names).
  - ext 57 reaches the state through the actor's vtable +0x28 (command start `@0x0800DF60`). The NPC class's state table was not traced (LIKELY the same objects, as the three vanilla NPC power-ups use state 9 the same way).
- Vegeta's own Cell Jr fight (`rom:0x3E9E24`, `ext 70 (2)`) comes earlier and is not touched. There he can transform by the vanilla rules (ability 12, pool form, the FCD cooldown carry-over from Piccolo).

---

## Proofs

**Builds** (`make_trial_vegeta.txt`):

| Build | SHA-1 |
|---|---|
| `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta.gba` (new, exclusive create) | `cd9fd893c55d3bf8df40a2b7af6abf7b1a2d19f8` |
| CLI `--list build_list_trial_vegeta.txt` | `cd9fd893c55d3bf8df40a2b7af6abf7b1a2d19f8` (equal) |
| CLI `--list` (main) | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` (r39, unchanged) |
| CLI `--list build_list_trial.txt` | `1826ca8f6b498844323f9c487cee1864025c3aa8` (v2, unchanged) |
| `log2_poc_r39_vegeta.sav` (byte copy of the v2 save) | `aa8efb2adaa7aa87f4cff27ceb7244368bd02759` |

**Diff v2 to new:** 340 bytes in 5 runs, 0 bytes outside the vegeta sites.

| Run | Bytes | Site |
|---|---|---|
| `rom:0x3EB232` | 1 | seq 52 remove byte |
| `rom:0x3EB7C8`-`0x3EB7CA` | 3 | seq 50 table word |
| `rom:0x3EC798`-`0x3EC79A` | 3 | seq 17 table word |
| `rom:0x90A67C`-`0x90A730` | 181 | seq 50 copy |
| `rom:0x90A734`-`0x90A7CB` | 152 | seq 17 copy |

**Diff r39 to new:** 1,222 bytes in 16 runs, 0 bytes outside the celljr v2 and vegeta sites. The 11 celljr runs are the v2 runs (`rom:0x3E9DC4`, `0x3EA478`, `0x3EA47A`, `0x3EB7E9`, `0x40DA84`, `0x40DA94` and `rom:0x90A308`-`0x90A67B`), plus the 5 runs above.

**Tests:** 18 new tests in `test_vegeta_ssj_scene.py`, all pass. Full suite: 718 tests, OK (700 before plus the 18 new; 127 s) (`scripts\one-time\2026-10-24-vegeta-ssj\suite.txt`).

---

## What to play

Load `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta.gba` with the `.sav` next to it. It holds all trial changes (Cell Jr v2 and this one).

1. Pick **slot 3**: Cell Games Arena arrival, map 14,1, Goku leads.
2. Play the Cell Games through: Goku's fight, Gohan's fight, the three ally Jr fights, Gohan's 4-Jr fight, the Cell fight, the self-destruct, Goku's goodbye.
3. **Attack 1:** after "He's back!!!!", Cell hits Trunks and Vegeta says "He will pay!!!!".
4. Win the Super Perfect Cell fight. **Attack 2** comes in the beam struggle, after "SAY GOODBYE!!!".

Watch these points (each needs the emulator; I did not run one):
- The power-up anim plays to its gold frame before the swap. (LIKELY: vanilla relies on the same order.)
- No gap, jump or flicker at the swap. The new Vegeta appears where the old one stood, facing right.
- Vegeta fires and takes the three hits with gold hair (attack 1), and flies and fires with gold hair (attack 2).
- In attack 2 the camera follows the gold Vegeta.
- Base Vegeta is back after the struggle (seq 20, "That was brave what you did." scene).
- The beam struggle sound still plays after Vegeta's power-up. Sounds 55 and 23 are new in that stretch; seq 20 stops sound 43 (`ext 47 (43)`), so a struggle sound may run during seq 17.

> [!TIP]
> If you want the attack 2 power-up one beat earlier, it can move to seq 11, so he transforms right before "VEGETA: ARGHHH!!!". Say so and I change one record.

---

## Files

| File | What |
|---|---|
| `scripts\permanent\patches\vegeta_ssj_scene.py` | The trial module |
| `scripts\permanent\tests\test_vegeta_ssj_scene.py` | 18 tests |
| `scripts\permanent\build_list_trial_vegeta.txt` | Trial list = `build_list_trial.txt` + `vegeta_ssj_scene` |
| `scripts\one-time\2026-10-24-vegeta-ssj\s1_scene.py`, `s1_scene_r39.txt` | Scene dump, set rows, set 137 sites, state 9 sites |
| `scripts\one-time\2026-10-24-vegeta-ssj\s2_vanilla_powerup.py`, `s2_vanilla_powerup_base.txt` | The vanilla NPC transforms |
| `scripts\one-time\2026-10-24-vegeta-ssj\s3_set_compare.py`, `s3_set_compare_r39.txt`, `sets_137_140.png` | Sets 137-140 |
| `scripts\one-time\2026-10-24-vegeta-ssj\make_trial_vegeta.py`, `make_trial_vegeta.txt` | Build and diff proofs |
| `scripts\one-time\2026-10-24-vegeta-ssj\bible_rows.md` | Bible rows, tag VSJ |
