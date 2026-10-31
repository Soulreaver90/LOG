# Vegeta Super Saiyan trial v5: Gohan flies in

This report covers the v5 change to the Vegeta trial module.

My verdict on v4b (2026-10-25 9:10 PM): "For the new Vegeta, it's great. One minor thing, Gohan jumps in front of Vegeta, he should fly in maybe. It's a short distance but looks less awkward."

---

## Status

The v5 trial ROM is built. It needs one play test by me.

| Ask | Status | Where |
|---|---|---|
| v4b section in the v4 report | SHIPPED | `vegeta-ssj-v4-report.md`, section "v4b: a plain wait in place of the fade" |
| Gohan flies to his spot in front of Vegeta | SHIPPED | `ext 121 (0, 12)` (the fly pose) in place of `ext 121 (0, 1)` (the walk) |
| Keep the timing: he arrives just before the blast, the blast hits him, standard hit | SHIPPED | Same move and speed as v4b: flies frames 17-23, stands from 24, hit at 33 |
| Keep everything else in v4b | SHIPPED | v4b to v5 is 17 bytes in 2 runs (see "Proofs") |
| Tests, full suite | SHIPPED | 47 module tests (6 new); full suite 860, OK |
| `--list` SHA-1s | SHIPPED | r39 `aa51dc16...` and celljr v4 `abbe5004...`, both unchanged |
| v5 ROM and save (exclusive create) | SHIPPED | `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v5.gba`, `.sav` |
| Render of Gohan's path | SHIPPED | `scripts\one-time\2026-10-24-vegeta-ssj\s14_v5_path.png` |
| Diff runs v4b to v5 | SHIPPED | See "Proofs" |
| Bible rows (tag VS5) | SHIPPED | `scripts\one-time\2026-10-24-vegeta-ssj\bible_rows_v5.md` (not merged; merge `bible_rows_v4.md` first) |

| Pending | My action |
|---|---|
| Play test of the fly-in | Steps in "What to play" |
| Approval | The last line of `build_list_trial_vegeta.txt` moves into the build list |

---

## The problem: Gohan's set has no flying pose

Gohan's set at "He will pay!!!!" cannot fly as built. So v5 needs one art-table write as well as the script op.

- **Gohan is set 160 here (CONFIRMED, VS4).** That is the gi Rage set, which copies the vanilla Rage set 58 layout.
- **Set 160 has no anim 12 (CONFIRMED).** Its row 12 is 4 zero words (`s13_v5_fly_r39.txt` section 1: `set 160 header rom:0x88d870 count 19: full [0, 1, 2, 3, 4, 5, 6, 7, 8, 13, 16, 18]`, `row 12 words 00000000 00000000 00000000 00000000`). Vanilla set 58 (armor Rage) is the same, so vanilla Rage Gohan never flies.
- **Fly with an empty row is unsafe (CONFIRMED code).** The state 12 enter loads the row with no check: `@0x0800E7AA ldr r0,[r1,#0x48] ; add r0,#0xff ; add r0,#0xd ; str r0,[r1,#0x4c]`, so +0x4C = set header + 0x10C (row 12). With a zero row the sprite reads address 0. That is the same fault class as Cell Jr's missing anim 12 (bible CJ2).
- **The fix (CONFIRMED bytes).** Row 12 of set 160 gets the 4 words of set 159's anim 12 (`0886976C 0886979C 088697CC 088697FC`), at `rom:0x88D97C`. Set 159 is the gi Super Saiyan 2 set, with the same gi and gold hair.
  - Set 159 has 4 records a direction, each 32x32 at (-8,-24). They decode to w x h bytes and fit set 160's slot 0x400 (`s13_v5_fly_r39.txt` section 4, test `test_every_borrowed_record_decodes_and_fits_the_slot`).
  - I viewed the sheet `s13_v5_fly_sheet.png`. Set 159 anim 12 dir 2 is a horizontal flight, head first to the left, in the gi. It matches set 160's body and hair.
- **No working path changes (CONFIRMED by the row bytes).** Before v5, any path that put set 160 into state 12 read a zero row, so it could not work. v5 only turns that dead path into a valid flying pose. Every path that worked before reads other rows and is unchanged. So a gameplay path to state 12, which I did not search for, does not matter.
- The `ssj2_idle` hook names the set 160 header (`@0x08894E2C ldr r3,=0x0888D870`), but it acts only on the anim 0 row (`@0x08894E36`-`@0x08894E3C`).

> [!NOTE]
> This is the first time `vegeta_ssj_scene` writes inside another module's output: 16 bytes of `gohan_gi`'s set 160 header. `gohan_gi` names no sites, so the module checks the bytes itself before the write and names the write in its own "sites". The main list (r39) keeps row 12 empty: `--list` still gives `aa51dc16...`.

---

## The fly-in

**Op (CONFIRMED bytes, LIKELY in game).** The blast group in the seq 50 copy is now:

| Op | Args | What |
|---|---|---|
| `ext 96` | (58, 0, 80) | Cell aims and fires at Gohan, on the line through Vegeta (unchanged) |
| `ext 69` | (16) | Gohan's ops wait for the shot (unchanged, v4b) |
| `ext 121` | (0, **12**) | **v5:** the fly state (v4b: state 1, the walk) |
| `ext 136` | (0, 431, 425, 500) | the move to his spot in front of Vegeta (unchanged) |
| `ext 60`, `ext 112`, `ext 95`, `ext 57` | (0), (0, 34), (0), (0, 2) | the standard hit (unchanged) |

- This is the pose and move pair of Cell's v4 dash (`ext 121 (58, 12)`, `ext 136 (58, 341, 408, 500)`). I played v4b, Cell's dash included, and called it great. Here the pair runs on the player.
- The player state table word 12 is the NPC word `0x03002130` (VS4, test `FLY_STATE`). The player vtable +0x30 and +0x34 are `bx lr`, so `ext 136` keeps state 12 while it moves him (VS4). The move tick ends in state 0 (`@0x08010934`, test pin), so he lands standing.
- No vanilla script sets state 12 on the player with `ext 121`. So the in-game result is LIKELY, not CONFIRMED.
- Pose: set 160 anim 12, now set 159's records. He faces left, from the knock-out group's `ext 55 (0, 2)`. `ext 136` keeps the facing (`@0x0801D2E0` `ldrb r7,[r5,#0x10]`, `@0x0801D306` `strb`, test pins), so he flies in dir 2.

**The vanilla fly, and why v5 does not use it (CONFIRMED).**
- The vanilla way to fly an actor is `ext 54 (set, x, y)`. Flying Gohan: the chamber exit seq 32 record `rom:0x3DBD5C` (table `rom:0x3DBDD4` word 31 at `rom:0x3DBE50`; bible R30, R31) runs `push 26 ; ext 46` (fly sound), then `push 56,840,480 ; ext 54` at `rom:0x3DBD63` (`1D 03 70 8D 10 87 40 02 36`), then `push 56 ; ext 52` (`00 38 02 34`). Armor Gohan (set 56) flies off screen in his anim 12 pose and is removed.
- A player example is record `rom:0x3D3DE4`: `push 0,424,416 ; ext 54` at `rom:0x3D3DF3` (`1D 03 00 86 50 86 40 02 36`). The table walk finds 21 player sites in 8 records, none in table `rom:0x3EB704`.
- `ext 54` moves at a fixed 2 px a frame: `@0x0800E842 mov r0,#0x1 ; lsl r0,r0,#9` (speed 0x200), then `bl 0x0800D5B8` (state 1, then state 12).
- The move is 37 px (largest axis), so `ext 54` takes 18 frames. Gohan would still fly until about frame 35, and the blast reaches his spot at frame 33. `ext 60` checks the hit only after his move ends, and the blast does not home. So the blast would pass him and the scene would freeze. Test `test_gohan_flies_where_he_ran` holds this.

**Path (model, `s14_v5_path_v5.txt` and `s14_v5_path.png`).** The camera is fixed at (248,328), so screen = world - (248,328). Frame 0 = the `ext 96` start.

| Frame | Gohan world | Gohan screen | Pose | Blast screen |
|---|---|---|---|---|
| 16 | (468,444) | (220,116) | stand, beside Vegeta's head | in Cell's hand, fires |
| 17 | (468,444) | (220,116) | stand, his ops start | (135,60) |
| 18 | (462,441) | (214,113) | fly | (137,61) |
| 20 | (452,436) | (204,108) | fly | (142,63) |
| 23 | (437,428) | (189,100) | fly | (149,67) |
| 24 | (431,425) | (183,97) | stand, in front of Vegeta | (152,68) |
| 33 | (431,425) | (183,97) | the blast touches him: hit | (173,79) |

- Start screen x 220, end screen x 183 (anchor). He flies 37 px left and 19 px up, at 5.00 px a frame, for 7 frames (frames 17-23, as the v4 run).
- The render's top panel shows the full view: Cell, lying Vegeta, Gohan's frames 17, 19, 21, 23 and 24 (labelled G), and the blast at 17, 20, 24, 28 and 33 (labelled b). The bottom panel zooms 6x on the flight, with Gohan's hurtbox at the block spot.
- The flying body (set 159 anim 12 dir 2) covers (-7,-20)-(21,-4) from his spot, so the sprite rises off the ground line while he flies. During the flight it crosses in front of Vegeta's head and chest.

---

## Timing against the blast

The timing is the v4b timing, to the frame. Only the pose changed.

| Step | Frame | Label |
|---|---|---|
| `ext 96` starts, Cell turns right | 0 | C (code) |
| The blast leaves Cell's hand at (381,387) | 16 | C (`cmp r0,#0x10` `@0x08011AEE`) |
| Gohan's `ext 69 (16)` ends; `ext 121 (0, 12)` | 16-17 | C (wait), L (the one frame for ext 121, as v4) |
| He flies, 7 frames at 5.00 px a frame | 17-23 | C (mover formula), L (the divide order, VS4) |
| He stands at (431,425); `ext 60 (0)` starts its check | 24 | L |
| The blast first overlaps his hurtbox (428,399)-(452,435) | 33 | model from C constants |
| Margin | 9 frames; blast flight 17 frames | test `test_gohan_stops_before_the_blast_reaches_him` (6 or more) |

The blast speed is n 80: 2.40 px a frame in x and 1.22 in y. Velocity 8.8 = (614, 313).

---

## Proofs

**Builds** (`scripts\one-time\2026-10-24-vegeta-ssj\make_trial_vegeta_v5.txt`, all CONFIRMED):

| Build | SHA-1 |
|---|---|
| `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v5.gba` (new, exclusive create) | `470f62a6bac3933a2ffd2fe723305e0dcb5001fc` |
| CLI `--list build_list_trial_vegeta.txt` | `470f62a6bac3933a2ffd2fe723305e0dcb5001fc` (equal) |
| CLI `--list` (main) | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` (r39, unchanged, bytes equal) |
| CLI `--list build_list_trial.txt` | `abbe5004f7d645329e8a141fadf70096ef6960c5` (celljr v4, unchanged) |
| `log2_poc_r39_vegeta_v5.sav` (byte copy of the v4b save) | `aa8efb2adaa7aa87f4cff27ceb7244368bd02759` |
| v4b ROM `log2_poc_r39_vegeta_v4b.gba` (read, not changed) | `d3d0a89aaf58bc46b81f6b9c218a8fcf8eb8becd` |

**Diff v4b to v5: 17 bytes in 2 runs, 0 bytes outside the v5 sites.**

| Run | Bytes | Old | New | What |
|---|---|---|---|---|
| `rom:0x88D97C`-`0x88D98B` | 16 | `00` x 16 | `6C978608 9C978608 CC978608 FC978608` | set 160 anim 12 row = set 159's |
| `rom:0x90A77D` | 1 | `02` | `18` | seq 50 copy: `push 0,1` to `push 0,12` before `ext 121` |

**Diff r39 to v5:** 1,361 bytes in 16 runs (r39 to v4b was 1,345 in 15), 0 bytes outside the celljr v4 and vegeta v5 sites. Allocations did not move: seq 50 copy `rom:0x90A67C`-`0x90A7A7`, seq 17 copy `rom:0x90A7A8`-`0x90A843`.

**Tests.** `test_vegeta_ssj_scene.py` has 47 tests, all pass.
- Changed: `EXCHANGE` holds `(121, (GOHAN, FLY))`; `test_gohan_stops_before_the_blast_reaches_him` expects the fly op. `test_gohan_set_has_the_walk_and_hurt_anims` became `test_gohan_set_has_the_stand_fly_and_hurt_anims`.
- New, `FlyTests` (6):
  - the vanilla player fly at `rom:0x3D3DF3`, the state 12 enter and the ext 54 speed (code bytes);
  - Gohan flies where he ran, with no ext 54, because ext 54 would be slower than the blast;
  - set 160 had no row 12 before, now equals set 159's, and the write is a named site, with no other change in the set 160 header;
  - every borrowed record decodes to w x h and fits the slot (4 records a dir);
  - he flies facing left;
  - a filled set 160 row or an empty set 159 row refuses before any write.

**Full suite:** 860 tests, OK, 178 s (`scripts\one-time\2026-10-24-vegeta-ssj\suite_v5.txt`). That is the v4 count of 854 plus the 6 new tests.

---

## What to play

Load `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v5.gba` with the `.sav` next to it. It holds all trial changes (Cell Jr v4 and Vegeta v5).

1. Pick **slot 3**: Cell Games Arena arrival, map 14,1, Goku leads.
2. Play the Cell Games through to the self-destruct and Super Perfect Cell's return.
3. **Attack 1:** after "He's back!!!!", Cell knocks Trunks down and Vegeta says "He will pay!!!!".
4. Win the Super Perfect Cell fight. **Attack 2** comes in the beam struggle, after "SAY GOODBYE!!!".

> [!WARNING]
> Make a save state just before "He will pay!!!!" and keep it. A freeze after Cell fires means the blast missed Gohan. v5 keeps every v4b address and length, so a v4b state is LIKELY to load, but I did not test one. Start from the `.sav` to be sure.

Watch these points. Each needs the emulator; I did not run one.
- **The lift-off:** as the blast leaves Cell's hand, Gohan switches to the flying pose, horizontal, head first to the left. He flies up and left about 37 px in 7 frames and lands standing in front of Vegeta.
- **The aura:** the flying frames are set 159's (gi Super Saiyan 2). They have no Rage outline aura, so the bolts stop during the 7 frames and come back when he stands. Tell me if that shows.
- **A hop or a flight:** the fly pose shows for only 7 frames (about 0.12 s). If it still reads as a hop, say "slower fly". The knob is `GOHAN_FLY_N` (now 500, 5 px a frame): 400 gives 9 fly frames with a margin of 7, and 350 gives 10 frames with a margin of 6, the test floor.
- **Draw order:** his flight crosses in front of Vegeta's head and chest. I expect Gohan drawn over Vegeta (his y is larger), but I did not trace the sort.
- **The hit:** the blast reaches him about 9 frames after he lands. Then the standard hit and Cell's line "Why do you protect Vegeta?".
- Everything else plays as in v4b: power-up, 3 blasts, Cell's fly dash, punch, knock-back, black hair, aura stop, attack 2.

---

## Files

| File | What |
|---|---|
| `scripts\permanent\patches\vegeta_ssj_scene.py` | The trial module, v5 |
| `scripts\permanent\tests\test_vegeta_ssj_scene.py` | 47 tests |
| `scripts\one-time\2026-10-24-vegeta-ssj\s13_v5_fly.py`, `s13_v5_fly_r39.txt`, `s13_v5_fly_sheet.png` | Anim rows of Gohan's sets, vanilla fly sites, state 12 and ext 54 listings, the donor row and its sheet |
| `scripts\one-time\2026-10-24-vegeta-ssj\s14_v5_path.py`, `s14_v5_path_v5.txt`, `s14_v5_path.png` | Frame model of the fly-in and the path render |
| `scripts\one-time\2026-10-24-vegeta-ssj\make_trial_vegeta_v5.py`, `make_trial_vegeta_v5.txt` | Build and diff proofs |
| `scripts\one-time\2026-10-24-vegeta-ssj\suite_v5.txt` | Full suite output |
| `scripts\one-time\2026-10-24-vegeta-ssj\bible_rows_v5.md` | Bible rows, tag VS5 (v4b and v5) |
| `builds\mockups\2026-10-24-vegeta-ssj\log2_poc_r39_vegeta_v5.gba`, `.sav` | The v5 trial ROM and save |

> [!NOTE]
> `s12_v4_layout.py` reads the module constant `RUN_N`, which v5 renamed `GOHAN_FLY_N`. The v4 study script no longer runs against the v5 module. Its outputs stay valid for v4.
