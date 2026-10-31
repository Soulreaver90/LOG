# Vegeta Super Saiyan trial v4: Gohan blocks the blast in flight

This report covers the v4 change to the Vegeta trial module.

My verdict on v3 (2026-10-25 4:38 PM): Cell fired after Gohan already stood in front of Vegeta, and the blast barely travelled. The v4 ask: knock Vegeta farther, Vegeta at the far right, Cell in the centre, Cell fires at Vegeta first, then Gohan runs in front of Vegeta and takes the blast.

---

## Status

The v4 trial ROM is built. It needs one play test by me.

| Ask | Status | Where |
|---|---|---|
| Vegeta knocked farther, to the far right of the screen | SHIPPED | 80 px knock-back; he lies at screen x 203-231 of 240 |
| Cell in the centre | SHIPPED | Cell's body at screen x 95-114 (a little left of centre) |
| Cell fires at Vegeta first | SHIPPED | The blast leaves at frame 16 on the line through Vegeta's body |
| Gohan runs in while the blast flies and takes it | SHIPPED | He starts as the blast leaves, stops 9 frames before it reaches him |
| A visible flight | SHIPPED | 39 px in 17 frames |
| Keep 3 blasts, power-up, punch, black hair, aura stops, attack 2, seq 52 | SHIPPED | All unchanged (tests) |
| Tests, full suite, `--list` SHA-1s | SHIPPED | 41 module tests, 854 OK, both SHA-1s unchanged |
| v4 ROM and save (exclusive create) | SHIPPED | `builds\mockups\2026-10-24-vegeta-ssj\` |
| Layout render, before and after | SHIPPED | `scripts\one-time\2026-10-24-vegeta-ssj\s12_v4_layout.png` |
| Diff runs v3_cj4 to v4 | SHIPPED | See "Proofs" |
| Bible rows (tag VS4) | SHIPPED | `scripts\one-time\2026-10-24-vegeta-ssj\bible_rows_v4.md` (not merged) |

| Pending | My action |
|---|---|
| Play test of attack 1 | Steps in "What to play" |
| Blast speed | Say "faster blast" if 2.4 px a frame looks slow (see "Knobs") |
| Approval | The last line of `build_list_trial_vegeta.txt` moves into the build list |

---

## Why the approach changed

Vegeta stands left of Cell, so no camera can show him on the right while Cell is in the centre. One of them has to cross over.

- **The v3 view followed Cell (CONFIRMED).** Self-destruct seq 40 runs `push 58 ; ext 33` at `rom:0x3EAD62` (bytes `00 3A 02 21`). Table `rom:0x3EB704` seq 41-51 has no ext 31, 33 or 119 (table walk, `s9_v4_camera_r39.txt`).
- **Your v3 state proves it (CONFIRMED).** In `log2_poc_r39_vegeta_v3.ss1` the current camera `0x030020C0` has +4 = Cell's actor `0x02035B90`. The OAM gives a view of (320,327), which is Cell's footprint centre (440,412) minus (120,84).
- **So Vegeta sat on the left (CONFIRMED for the state, LIKELY for v3 play).** At "He will pay!!!!" Vegeta (352,424) is at screen x 32. In v3 the follow moved left with Cell's walk, so Vegeta stayed near screen x 48-76.

**What I changed:**
1. Cell flies left past Vegeta to his left side (fly pose, 5 px a frame). Vegeta's walk-in, power-up and volley stay as in v2.
2. `ext 31 (248, 328, 4)` stops the follow and fixes the view on the fight.
3. Both turn to face each other. Cell punches Vegeta to the right, 80 px, past Cell's old spot.

> [!NOTE]
> Cell is a little left of the exact centre. With Cell exactly centred, the blast would fly about 20 px less before it reaches Gohan. The allies 103 and 76 also stay out of view this way.

---

## The screen layout

The view is (248,328) to (487,487), fixed from the camera pan to seq 52. Screen x = world x - 248, screen y = world y - 328. Each spot is the actor's anchor.

| Actor | At the punch | When Cell fires | At the hit |
|---|---|---|---|
| Cell (58) | (93,80), body x 95-114 | (93,80) | (93,80) |
| Vegeta (140) | (128,88), standing | (208,96), lying x 203-231 | (208,96) |
| Gohan (player) | (184,136), standing | (220,116), beside Vegeta's head | (183,97), in front of Vegeta |
| 121 | (120,128) | (120,128) | (120,128) |
| 103, 76 | out of view (x 240, 248) | out of view | out of view |

Before (v3) and after (v4), as a model render on flat ground (`s12_v4_layout.png`): top, the v3 view when Cell fires; middle, the v4 view when Cell fires, with the blast path (yellow), Gohan's run (blue) and the hit point (orange); bottom, the v4 view at the hit.

**Clearance (CONFIRMED, opaque boxes from the ROM, `s12_v4_layout_r39.txt` section 5).** Vegeta lying covers world (451,412)-(479,431). 103 starts at x 489, so it does not touch him and is out of view. 121 and 76 are clear too.

---

## Order and timing

Frame counts are at 60 frames a second. C = a constant in the code. L = the mover formula (largest axis x 256 / speed).

| Step | Ops | Frames |
|---|---|---|
| Walk-in, power-up, 3 blasts | v1 and v2, unchanged | as v3 |
| Cell flies past Vegeta | `ext 121 (58, 12)`, `ext 136 (58, 341, 408, 500)` | 17 (L) |
| Camera stops on the fight | `ext 31 (248, 328, 4)` | up to 6 (model) |
| They face each other | `ext 55 (58, 3)`, `ext 55 (140, 2)` | 0 |
| One punch | `ext 57 (58, 6)` | 16 (C) |
| Knock-out group: hit sound, flash, hurt pose, knock-back | `ext 112`, `ext 95`, `ext 121 (140, 2)`, `ext 136 (140, 456, 424, 600)` | 13 (L) |
| ... then the fall, hair turns black | `ext 57 (140, 3)` | 64 (C) |
| ... Gohan walks beside Vegeta, faces Cell (parallel) | `ext 53 (0, 468, 444)`, `ext 55 (0, 2)` | 36 (L) |
| ... aura hum off | `ext 47 (55)` | 0 |
| Blast group: Cell aims and fires | `ext 96 (58, 0, 80)` | fires at 16, holds 32 (C) |
| ... Gohan's ops wait for the shot | `ext 43 (16)` | 16 |
| ... Gohan runs in front of Vegeta | `ext 121 (0, 1)`, `ext 136 (0, 431, 425, 500)` | 7 (L), frames 17-24 |
| ... the blast reaches Gohan | `ext 60 (0)` | frame 33: a 17-frame flight |
| ... standard hit | `ext 112 (0, 34)`, `ext 95 (0)`, `ext 57 (0, 2)` | 32 (C) |
| Gohan faces Cell, then seq 51 (Cell's line) | `ext 55 (0, 2)` | 0 |

**The blast (frame model, `s12_v4_layout_r39.txt` section 3).**
- It spawns at (381,387), the front of Cell's facing-right hurtbox at centre height.
- It flies toward Gohan's hurtbox centre (477,436) at 2.40 px a frame in x and 1.22 in y.
- The line enters Vegeta's lying body at x 451 and is still inside it at x 465. So it reads as a shot at Vegeta.
- Gohan stops at frame 24. The blast first touches his box at frame 33. The margin is 9 frames.

---

## Why each choice

**The blast is aimed at Gohan, not at Vegeta (CONFIRMED). Aiming at Vegeta freezes the scene.**
- `ext 60 (0)` asks the world with message 0x11 (`@0x08011D1E mov r1,#0x11`).
- The scene blast answers only when the asking actor is its own target: `@0x08011CB4 ldr r1,[r2,#0]`, `@0x08011CB6 ldr r3,[r0,#0x40]`, `cmp r1,r3`, `bne` to "no hit".
- Its +0x40 is the ext 96 target: `@0x08011B8C ldr r2,[r4,#0xc]`, then `@0x08011C02 str r6,[r4,#0x40]`.
- So a blast aimed at 140 would never end `ext 60 (0)`. It would also fly through Gohan's sprite.

**Gohan waits on Cell's line, behind Vegeta (CONFIRMED mechanism).**
- The velocity is fixed at the fire tick, toward the target's hurtbox centre (`@0x08011B04`-`@0x08011B7A`). The tick only adds it each frame (`@0x08011C74`-`@0x08011C82`). There is no homing.
- So Gohan must stand on the line when Cell fires. I put him beside Vegeta's head, on the line from Cell's hand through Vegeta's body. He runs along that same line (test: both of his spots are within 2 px of it).
- Cell turns toward his target at the command start. From (341,408) to (468,444) dx is 127 and dy is 36, so Cell faces right.

**Gohan's ops wait 16 frames inside the group (CONFIRMED code, LIKELY in game).**
- `ext 43` builds its wait and calls `scene_push` with no group-flag read (`@0x08009BB6`).
- `actor_queue` pushes its own wait only when the flag is 0 (`@0x0800E066`-`@0x0800E072`).
- The ext 43 wait and the group wait share the same per-frame update `0x08004EA9` (camera and world). So Cell's ext 96 keeps running during the 16 frames.
- No vanilla group holds an ext 43 or ext 31 (0 of 183, `s11_v4_boxes_r39.txt` section 4). That is why the in-game label is LIKELY.

**The hit wait is safe after the run (CONFIRMED order, LIKELY timing).**
- Inside a group, commands run in order per actor. So `ext 60 (0)` starts its check only after Gohan's run ends.
- The blast speed and the run speed come from the code (C). The frame counts use the divide `@0x08021F30` as r1 / r0. Two call sites agree on that order, but I did not disassemble the ARM body (L).

**Cell's fly dash (CONFIRMED mechanism, LIKELY look).** `ext 121` starts like `ext 57` (vtable `0x08025ED4` slot 1 = `0x0800DF61`) and sets state 12, the fly state ext 54 sets (state table word 12 = `0x03002130` for NPCs and the player). Set 58 has anim 12 in all 4 directions. No vanilla script runs `ext 121 (x, 12)`.

**Gohan's run (CONFIRMED mechanism).** `ext 121 (0, 1)` sets the walk state that `ext 53` sets. The player vtable +0x30 and +0x34 are `bx lr`, as for NPCs, so `ext 136` keeps that walk state while it moves him. Set 160 has no fly pose (anim 12), so Gohan runs in his walk pose at 5 px a frame.

**The punch (LIKELY look).** Facing right, Cell's anim 6 reaches x + 43 (`s11_v4_boxes_r39.txt`). From x 341 it reaches 384, 7 px into Vegeta, the same depth as v3.

---

## Knobs

Each knob is one constant in the module.

| Knob | Now | Effect |
|---|---|---|
| `BLAST_N` | 80 (2.4 px a frame; vanilla uses 100 and 120) | 100: flight 14 frames, margin 6. 120: flight 12, margin 4 (too tight). 60: flight 23, margin 15 |
| `DASH_N` | 500 (5 px a frame) | Cell's fly dash speed |
| `KNOCK_N` | 600 (6 px a frame) | Vegeta's knock-back speed |
| `RUN_N` | 500 (5 px a frame) | Gohan's run speed |

---

## Proofs

**Builds** (`scripts\one-time\2026-10-24-vegeta-ssj\make_trial_vegeta_v4.txt`):

| Build | SHA-1 |
|---|---|
| `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v4.gba` (new, exclusive create) | `6ebc2736bf2058f3a1fa227d6c86cd830ec5762b` |
| CLI `--list build_list_trial_vegeta.txt` | `6ebc2736bf2058f3a1fa227d6c86cd830ec5762b` (equal) |
| CLI `--list` (main) | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` (r39, unchanged, bytes equal) |
| CLI `--list build_list_trial.txt` | `abbe5004f7d645329e8a141fadf70096ef6960c5` (celljr v4, unchanged) |
| `log2_poc_r39_vegeta_v4.sav` (byte copy of the v3_cj4 save) | `aa8efb2adaa7aa87f4cff27ceb7244368bd02759` |
| v3_cj4 ROM `log2_poc_r39_vegeta_v3_cj4.gba` (read, not changed) | `b5e2019f579a8cbffceaf2588678242004cc0129` |

**Allocations.** Seq 50 copy `rom:0x90A67C`-`0x90A7A7` (0x12C bytes, v3 0x101). Seq 17 copy `rom:0x90A7A8`-`0x90A843` (0x9C, moved from `0x90A780`).

**Diff v3_cj4 to v4: 278 bytes in 32 runs, 0 bytes outside the v4 sites.**

| Run | Bytes | What |
|---|---|---|
| `rom:0x3EC798` | 1 | seq 17 table word, low byte (`0x90A780` to `0x90A7A8`) |
| `0x90A706`, `0x90A70C`-`0x90A70D`, `0x90A710`-`0x90A711`, `0x90A715`-`0x90A720`, `0x90A722`-`0x90A727`, `0x90A729`-`0x90A73A`, `0x90A73C`-`0x90A74D`, `0x90A74F`-`0x90A75D`, `0x90A75F`-`0x90A765`, `0x90A767`, `0x90A769`-`0x90A76B`, `0x90A76D`, `0x90A76F`-`0x90A773`, `0x90A775`-`0x90A781`, `0x90A783`-`0x90A79C`, `0x90A79F`-`0x90A7A2`, `0x90A7A4` | 135 | seq 50 copy from +0x8A: the v4 exchange (17 runs) |
| `0x90A7A6`-`0x90A7B4` | 15 | the last 2 bytes of the seq 50 copy and the first 13 of the moved seq 17 copy |
| `0x90A7B7`, `0x90A7B9`, `0x90A7BB`, `0x90A7BD`, `0x90A7C1`, `0x90A7C3`-`0x90A7DD`, `0x90A7DF`, `0x90A7E1`, `0x90A7E3`-`0x90A7FC`, `0x90A7FE`-`0x90A814`, `0x90A816`, `0x90A818`, `0x90A81A`-`0x90A843` | 127 | the moved seq 17 copy (13 runs); equal bytes break the runs |

The first 0x8A bytes of the seq 50 copy (walk-in, transform, volley) did not change. The seq 50 table word and the seq 52 byte did not change.

**Diff r39 to v4:** 1,345 bytes in 15 runs, 0 bytes outside the celljr v4 and vegeta v4 sites.

**Tests:** `test_vegeta_ssj_scene.py` has 41 tests, all pass.
- Replaced on purpose: `test_knock_back_keeps_the_v2_distance` (the brief changes that distance). `test_gohan_ends_between_them_as_in_v2` became `test_gohan_walks_from_his_seq_8_spot_and_seq_52_places_him`.
- Changed: `EXCHANGE` (v4 ops), the set 58 count in `test_copies_carry_super_perfect_cell` (+10 over vanilla), the knock-back target in `test_fall_after_the_knock_back_and_nothing_after`.
- New, `LayoutTests` (8): the cross-over and the v3 follow camera; the punch reach from the left; the screen layout and the bystanders; Cell faces right when he fires; the line crosses Vegeta and Gohan blocks first; the 6-frame minimum margin and a 12-frame minimum flight; the blast binds to Gohan and nothing waits on Vegeta (code bytes); waits inside a group run the world update. New in `SetTests` (1): set 160 has the walk and hurt anims; set 58 also has anim 12.

**Full suite:** 854 tests, OK (`scripts\one-time\2026-10-24-vegeta-ssj\suite_v4.txt`, 213 s). `test_chapter_cards` passed too.

---

## What to play

Load `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v4.gba` with the `.sav` next to it. It holds all trial changes (Cell Jr v4 and Vegeta v4).

1. Pick **slot 3**: Cell Games Arena arrival, map 14,1, Goku leads.
2. Play the Cell Games through to the self-destruct and Super Perfect Cell's return.
3. **Attack 1:** after "He's back!!!!", Cell knocks Trunks down and Vegeta says "He will pay!!!!".
4. Win the Super Perfect Cell fight. **Attack 2** comes in the beam struggle, after "SAY GOODBYE!!!".

> [!WARNING]
> Make a save state just before "He will pay!!!!" and keep it. A freeze after Cell fires means the blast missed Gohan. Do not load a v3 state inside attack 1: the seq 50 record has new bytes at the same address.

Watch these points. Each needs the emulator; I did not run one.
- The power-up and the 3 blasts play as in v3.
- **Cell's dash:** he flies left past Vegeta in his fly pose. His sprite crosses Vegeta for about 13 frames; tell me if one draws over the other badly.
- **The camera:** a short pan, then it stays. Cell sits a little left of centre.
- **The punch:** both turn, Cell swings once, Vegeta flashes and flies right about 80 px in his hurt pose, then falls near the right edge with black hair.
- **The aura hum** stops at the knock-out.
- **Gohan** walks up beside Vegeta's head during the fall and faces Cell.
- **The blast:** Cell aims, the blast leaves his hand toward Vegeta. Gohan dashes in front of Vegeta, stops, and the blast hits him about 9 frames later. Then the standard hit and Cell's line "Why do you protect Vegeta?".
- Vegeta lies with black hair through Cell's line, then leaves in seq 52.
- **Attack 2:** unchanged from v3.

---

## Files

| File | What |
|---|---|
| `scripts\permanent\patches\vegeta_ssj_scene.py` | The trial module, v4 |
| `scripts\permanent\tests\test_vegeta_ssj_scene.py` | 41 tests |
| `archive\2026-10-25-vegeta-ssj-v3\` | The v3 module and tests |
| `scripts\one-time\2026-10-24-vegeta-ssj\s9_v4_camera.py`, `s9_v4_camera_r39.txt`, `s9_v4_state_oam.txt`, `s9_dumps\` | Camera and placement ops of the table; actors and camera in your v3 state |
| `scripts\one-time\2026-10-24-vegeta-ssj\s10_v4_blast.py`, `s10_v4_blast_base.txt` | The listings: scene blast, ext 60, spawn point, ext 43, groups, camera tasks, vtables |
| `scripts\one-time\2026-10-24-vegeta-ssj\s11_v4_boxes.py`, `s11_v4_boxes_r39.txt` | Hurtboxes, footprints, blast frames, frame boxes, ops inside groups, ki n values |
| `scripts\one-time\2026-10-24-vegeta-ssj\s12_v4_layout.py`, `s12_v4_layout_r39.txt`, `s12_v4_layout.png` | Frame model of the exchange and the before/after render |
| `scripts\one-time\2026-10-24-vegeta-ssj\make_trial_vegeta_v4.py`, `make_trial_vegeta_v4.txt` | Build and diff proofs |
| `scripts\one-time\2026-10-24-vegeta-ssj\suite_v4.txt` | Full suite output |
| `scripts\one-time\2026-10-24-vegeta-ssj\bible_rows_v4.md` | Bible rows, tag VS4 |
| `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v4.gba`, `.sav` | The v4 trial ROM and save |

---

## v4b: a plain wait in place of the fade

v4b is v4 with one op changed. The v5 task added this section on 2026-10-29. The v4 task stopped before it wrote it.

**The change (CONFIRMED, `make_trial_vegeta_v4b.txt`).**
- In the blast group, `ext 43 (16)` becomes `ext 69 (16)`. Gohan's ops still wait 16 frames for the shot.
- It is one byte in the seq 50 copy: `rom:0x90A779` `2B` (ext 43) to `45` (ext 69). The v4 ROM reads `02 60 00 10 02 2B` there and v4b reads `02 60 00 10 02 45`.
- v4 to v4b: 1 byte in 1 run, 0 bytes outside the vegeta sites.

**Why ext 43 went (CONFIRMED code, LIKELY look).**
- `ext 43` is a timed fade from white, not a plain wait. Its task vtable `0x0802545C` has slot +0x2C = `0x0800DC39`. That tick adds 1 to +4, computes 0x100 - (+4 << 8) / n, and calls `@0x0800DC50 bl 0x0800BE7A`.
- `@0x0800BE7A` sets `r2`, `r1`, `r0` to `0xFF` (white) and branches to the blend at `0x0800BE14`. So the screen would flash white and fade back while Cell fires.
- This corrects the v4 report's "ext 43 builds its wait": it also blends the palette. The v4 model, which treated ext 43 as a wait only, was wrong.
- `ext 69 (n)` is the plain wait. The handler `@0x0800A65C` builds an 8-byte task {vtable `0x0802585C`, n} and calls `scene_push` with no group flag read. Its vtable slot +0x2C is `0x0800DEBD`: that tick subtracts 1 from +4 and ends at 0, so it waits n frames. The two vtables differ in slot +0 and +0x2C only (slots +0 to +0x2C read).
- Its update +0xC is `0x08004EA9`, the same camera and world update as the group wait. So Cell's ext 96 keeps running during it (test `test_waits_inside_a_group_run_the_world`).
- The module tests pin both code facts: `EXT43_FADE` and `GROUP_WAIT` in `test_vegeta_ssj_scene.py`.

**Proofs (`scripts\one-time\2026-10-24-vegeta-ssj\make_trial_vegeta_v4b.txt`).**

| Item | Value |
|---|---|
| `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v4b.gba` (exclusive create) | `d3d0a89aaf58bc46b81f6b9c218a8fcf8eb8becd` |
| CLI `--list build_list_trial_vegeta.txt` | `d3d0a89a...` (equal) |
| CLI `--list` (main) | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` (r39, bytes equal) |
| CLI `--list build_list_trial.txt` | `abbe5004f7d645329e8a141fadf70096ef6960c5` (celljr v4) |
| `log2_poc_r39_vegeta_v4b.sav` (byte copy of the v3_cj4 save) | `aa8efb2adaa7aa87f4cff27ceb7244368bd02759` |
| v3_cj4 to v4b | 278 bytes in 32 runs, 0 outside the vegeta sites |
| r39 to v4b | 1,345 bytes in 15 runs, 0 outside the celljr v4 and vegeta v4b sites |

**Tests.** `test_vegeta_ssj_scene.py` had 41 tests for v4b (`EXCHANGE` holds `(69, (GOHAN_WAIT,))`).
- `suite_v4.txt` shows 854 tests, OK, in 325.7 s. It was written at 8:59 PM, after the v4b build at 8:53 PM. Its run time is not the 213 s this report gives. So it is LIKELY the v4b run, written over the v4 run.
- The v5 full suite on 2026-10-29 (860 tests, OK) covers the v4b code as well.

**My verdict on v4b** (2026-10-25 9:10 PM): "For the new Vegeta, it's great. One minor thing, Gohan jumps in front of Vegeta, he should fly in maybe." v5 makes that change: see `vegeta-ssj-v5-report.md`.
