# Cell Jr trial v2: my play-test changes (2026-10-24)

The v2 trial ROM is built with all three changes. The main build is still r39.

Labels: **C** = CONFIRMED (bytes, listing or test), **L** = LIKELY, **S** = SPECULATIVE. Addresses are r39 (`builds\log2_poc_r39.gba`, SHA-1 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`, read and checked) unless a line names the v2 ROM. Listings come from `scripts\permanent\rom\thumb_dis.py`.

---

## SHIPPED

| Ask | Result |
|---|---|
| 1. Cell faces Gohan during the Jr fight | Cell is now spawn item 17, an NPC with the vanilla "face the player" step. X builds him with `ext 84 (17)`; no fixed facing is set (C bytes, L in game) |
| 2. The 4 Jrs come in from the top of the screen | X moves the camera to the fight view, spawns each Jr 40 px above it and walks it down to its fight spot in one actor group. A flash covers the swap from scene Jrs to enemy Jrs (C bytes, L in game) |
| 3. Gohan faces Cell before the Super Perfect Cell fight (8:53 PM) | Self-destruct table word 57 names a copy of seq 58 with `ext 55 (0, 3)` (right, toward Cell), not `ext 55 (0, 0)` (down). See the scope note below (C bytes, L in game) |
| Keep difficulty, 4 Jrs, EXP, flow; no HP refill | Unchanged: type 26, 12,500 EXP each, counter C, record N, table T (C, tests) |
| Module tests for the changes | 9 new tests, 33 in `test_celljr_fight`, OK |
| Full suite once at the end | 700 tests OK (691 + 9). `scripts\one-time\2026-10-24-celljr-trial\suite_v2.txt` |
| Main `--list` still gives r39 | CLI `--list` SHA-1 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`, bytes equal to `builds\log2_poc_r39.gba` (C, `make_trial_v2.txt`) |
| v2 ROM, exclusive create | `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr_v2.gba`, SHA-1 `1826ca8f6b498844323f9c487cee1864025c3aa8`. The CLI trial build gives the same SHA-1 |
| v1 save copied for v2 | `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr_v2.sav`, SHA-1 `aa8efb2adaa7aa87f4cff27ceb7244368bd02759` (byte copy, exclusive create). The v1 ROM, save and states are untouched |
| Diff runs v1 to v2 and r39 to v2 | Below, and in full in `make_trial_v2.txt` |
| Bible rows, tag CJ2 | `scripts\one-time\2026-10-24-celljr-trial\bible_rows_v2.md` (sections 4, 8, 9, 11, 12, 13) |

## PENDING

| Item | Why |
|---|---|
| Me: confirm the scene for change 3 | I wrote "about to fight S. Perfect Cell ... facing down while the dialogue is going on". The coordinator mapped it to record N ("You wretched child"). N already runs `ext 55 (0, 3)` in v1 (C, `restore()`), so that reading would change nothing. The Super Perfect Cell talk matches the words: vanilla seq 58 turns Gohan down for Goku's telepathy lines. v2 fixes that scene. If Gohan also faces down at "You wretched child" in play, report it: the cause is then not in N's bytes |
| Emulator play test (checklist below) | No emulator run in this task. Every in-game claim is L or S |
| Jr fly pose | `set:31` has no anim 12, so the Jrs come down in their walk pose at 1 px a frame. A real fly pose needs new art (I draw). With an anim 12 in `set:31`, X can switch its 4 `ext 53` to `ext 54`; `_check` needs only anim 1, and `test_no_record_flies_set_31` skips itself |
| Me: merge the CJ2 rows | The rows file relabels two S rows (CPR, CJT) and one L row (BLK). See its merge notes |
| Approval | As v1: move the `celljr_fight` line to `build_list.txt` and update the 3 tests the v1 report names. No new test breaks by two shapes: (A) no test outside `test_celljr_fight` names `0x3EB7E8`, `0x3EB4C4`, `0x40DA84` or `0x40DA94`; (B) the table walkers that read `rom:0x3EB704` (`test_cellgames_ssj.set_hits`, `test_superperfect_cell.actor_values`) give the same counts for that table on r39 and v2 (set 30: 9, set 58: 15, set 0: 23). A test that reads the seq 58 bytes through another route would not show in A or B |

---

## Change 1: Cell faces Gohan

**Vanilla mechanism (C).** NPC spawn items carry a list of steps. Step `{0x08010099, 0x7D00}` makes the NPC face the player every frame:
- Factory `@0x08010098` builds an object with vtable `0x08024C48`.
- Its tick `@0x08010038` reads the player: `ldr r2,=0x03001fa8 ; ldr r2,[r2,#0x0]`.
- It compares abs dx and abs dy of +0x158/+0x15C, then stores the facing: `mov r2,#0x3 ; strb r2,[r1,#0x10]` (right), 2 left, 0 down, 1 up.
- The step controller at NPC +0x160 (`@0x0800D156`) rebuilds the step when its 32000 frames run out.

**Vanilla use (C).** 24 NPC items use this step (`npc_steps.py`). On map 14,3 they are items 1-4, 6, 7: Vegeta, Trunks, Gohan, Piccolo, Krillin, Android 16. Piccolo: step `rom:0x408F98` = `99000108 007d0000`, item `rom:0x408FA0`.

**No script op tracks the player (C).**
- `ext 55` stores a fixed direction once: `@0x0800DFFC ldrb r0,[r0,#0x8] ; strb r0,[r1,#0x10]`.
- `ext 56` turns an actor toward another actor once: `@0x0800DF98`.
- `ext 51` NPCs use the template at `0x03000C04` and get no steps from the script.

So the route is a spawn item, not a script op.

**What v2 does (C, test `test_item_17_is_an_npc_cell_with_the_face_player_step`).**
- New item 17 = `{0x0800D6DF, cond 1, (616,384), set 30, 1, step}`. Its own step copy is `{0x08010099, 0x7D00}`.
- Cond 1 means the item is not built at map load. The self-destruct seq 1 reloads 14,3 with `ext 39`, and any other cond would build a second NPC Cell there.
- X runs `ext 52 (30)`, then `ext 84 (17)`. The v1 `ext 51 (30,...)` and `ext 55 (30, 2)` are gone (test `test_x_sets_no_fixed_facing_on_cell`).
- `ext 84` calls the item's own factory: `@0x0800C74A ldr r1,[r0,#0x0] ; bl 0x8021d2a` (`bx r1`), then `world_add`.
- N still removes him with `ext 52 (30)` before `ext 84 (11)`: same set, same lookup.

Label: C for bytes and code. L that the step keeps running while combat is on. The vanilla spectators use it in scenes and fights, but this was not watched.

---

## Change 2: the Jrs come from the top

**Vanilla precedent (C).** Self-destruct seq 8 (`rom:0x3EA638`, table `rom:0x3EB704` word 7):
- Seq 1 sets the camera top to y 344 (`ext 31 (320,344,30)`).
- `push 61,424,96 ; ext 51` spawns Goku far above the view.
- `ext 63 ; ... push 61,464,472 ; ext 54 ; ... ext 64` moves him down with the others in one group.

**Scene actors that become enemies (answer to the brief).** The Jrs come in as NPCs (scene actors) and are then swapped for the 4 enemy items. Why:
- The vanilla arrivals move NPCs. Vanilla Super Perfect Cell also goes from NPC to enemy: seq 52 `push 58 ; ext 52`, then `push 12 ; ext 84` (`rom:0x3EB21C`).
- An enemy built by `ext 84` starts its AI 21 at once.
- The 4 enemies share set 31, and a script finds an actor by set, so it cannot address one of them.
- No vanilla script moves an enemy with `ext 53` or `ext 54`.

**Why walk, not fly (C).** `ext 54` (fly) enters state 12, whose enter stores set + 0x10C (anim 12, bible R30 row). `set:31` has 9 anims (0, 1, 2, 5-8 in 4 directions). Anim 12 lies past its table, and frame select has no bound (BLP row). `ext 53` (walk) uses anim 1, which `set:31` has in all 4 directions. Both ops share the mover `@0x0800D1AC`, which ignores collision (PGS row). Test `test_no_record_flies_set_31`.

**Binding each walk to its Jr (C).**
- A script finds an actor through `@0x08006E0A`, which walks world list 1 from the end: `ldr r4,[r0,#0x4] ; sub r4,#0x1 ; ... sub r4,#0x1 ; bpl`.
- It stops at the first object that answers.
- `world_add` `@0x080068B8` appends: `ldr r1,[r0,#0x0] ; add r3,r1,#1 ; str r3,[r0,#0x0]`.
- So the newest set-31 actor wins. Each `ext 53 (31, ...)` comes right after its own `ext 51 (31, ...)`, and the lookup runs when the op is queued (`@0x08009E52 bl 0x8009370`).
- Test `test_each_walk_follows_its_own_spawn`.

**Record X in v2 (C, tests).** Gohan table word 30, 153 bytes at `rom:0x90A3C8`:

1. `push 0 ; set var1` (counter reset).
2. `ext 52 (30)` (enemy Cell out), `ext 84 (17)` (NPC Cell in).
3. `ext 31 (456,288,2)`: camera to the fight view. Gohan (576,376) is near its centre (L).
4. `ext 46 (26)`: the vanilla fly sound, played before the vanilla flights (seq 48 `push 26 ; ext 46`).
5. `ext 63`, then 4 x (`ext 51 (31, x, 248)` ; `ext 53 (31, x, y)`) to (528,344), (528,408), (624,344), (624,424), then `ext 64`. Y 248 is 40 px above the view top 288 (L: the sprite is drawn from y - 24). Each walk ends on its item's spot (test `test_each_jr_walks_down_from_above_the_view_to_its_item_spot`).
6. `ext 42 (5)`, 4 x `ext 52 (31)`, `ext 84` 13-16, `ext 43 (5)`. Every NPC Jr goes before the first enemy exists, so no remove can bind an enemy Jr (test `test_every_npc_jr_goes_before_the_first_jr_enemy`).
7. `ext 33 (0)`, `ext 86 (1)`, next 32 = END: the fight runs.

---

## Change 3: Gohan faces Super Perfect Cell

**The vanilla scene (C).** Self-destruct table `rom:0x3EB704`:

| Word | Record | Bytes | Effect |
|---|---|---|---|
| 51 (seq 52) | `0x083EB21C` | `push 0,432,472 ; ext 62 ; push 0,3 ; ext 55 ; push 12 ; ext 84` | Gohan at (432,472) faces right; Super Perfect Cell (item 12, (512,472)) is built |
| 57 (seq 58) | `0x083EB4C4` | `3a0000 1d0200000237 11` = `push 0,0 ; ext 55` | Gohan faces down for "Dad!? Where are you?" and Goku's lines (seq 59-64) |
| 64 (seq 65) | `0x083EB6E8` | `push 0,3 ; ext 55 ; ...` | Gohan faces right again; the fight starts |

**Vanilla facing mechanism (C).** `ext 55 (actor, dir)` `@0x08009EFC`. Its command stores the dir at actor +0x10. 148 vanilla sites run `push 0,d ; ext 55` on the player. Seq 52 and seq 65 use it on this same pair of actors. `ext 56 (0, 58)` (face an actor) was not used: no vanilla site with an enemy target was found, and a fixed right is exact here (same y, Cell at a larger x).

**What v2 does (C, tests `test_seq_58_copy_faces_gohan_right_with_the_same_next_index`, `test_right_is_toward_super_perfect_cell`).**
- A copy of seq 58 at `rom:0x90A4C4`: `3a0000 1d0200060237 11` = `push 0,3 ; ext 55`, next index 58 as vanilla.
- Word `rom:0x3EB7E8` names the copy. It was the only word that named `0x083EB4C4`.
- The vanilla record stays byte equal and is now unreferenced.

---

## Diff runs

**r39 to v2 (C, `make_trial_v2.txt`): 882 bytes in 12 runs, 0 bytes outside the 27 named sites.**

| Run | Bytes | Site |
|---|---|---|
| `rom:0x3E9DC4`-`0x3E9DC6` | 3 | spawn table word 30 |
| `rom:0x3EA478`, `0x3EA47A` | 2 | Gohan table word 30 |
| `rom:0x3EB7E9`-`0x3EB7EA` | 2 | self-destruct table word 57 (new in v2) |
| `rom:0x40DA84` | 1 | map 14,3 spawn count (13 to 18) |
| `rom:0x40DA94`-`0x40DA96` | 3 | map 14,3 spawn list word |
| `rom:0x90A308`-`0x90A3C5` | 190 | seq 31 copy (7 Jrs), as v1 |
| `rom:0x90A3C8`-`0x90A460` | 153 | record X |
| `rom:0x90A464`-`0x90A47C` | 25 | record C |
| `rom:0x90A480`-`0x90A4C0` | 65 | record N |
| `rom:0x90A4C4`-`0x90A4CD` | 10 | seq 58 copy |
| `rom:0x90A4D0`-`0x90A553` | 132 | table T |
| `rom:0x90A554`-`0x90A613` | 192 | items 13-16 with tails and event structs (4 x 48) |
| `rom:0x90A614`-`0x90A633` | 32 | item 17 step (8) and item 17 NPC Cell (24) |
| `rom:0x90A634`-`0x90A67B` | 72 | spawn list copy (18 items) |

The table counts sites, not runs: adjacent sites form one run in the 12-run count.

**v1 to v2 (C): 564 bytes in 55 runs.**
- Base data: word 57 `rom:0x3EB7E9`-`0x3EB7EA` (new), count `rom:0x40DA84`, list word `rom:0x40DA94`-`0x40DA95`.
- Expansion: record X grew (99 to 153 bytes), so C, N, T, the items and the list moved. `make_trial_v2.txt` lists every changed run from `rom:0x90A3D3` to `0x90A67B` with its v2 site.
- The seq 31 copy `rom:0x90A308`-`0x90A3C5` is byte equal to v1.
- 11 bytes are outside every v2 site: `rom:0x90A461`-`0x90A463`, `0x90A47D`-`0x90A47F`, `0x90A4C1`-`0x90A4C3`, `0x90A4CE`-`0x90A4CF`. They are v1 data in alignment gaps that v2 leaves at the r39 fill (0xFF, read back).

---

## Tests

| Run | Result |
|---|---|
| `test_celljr_fight` | 33 OK (v1 24, updated for 5 base sites and 18 items, plus 9 new) |
| Full suite (`py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent`) | 700 OK |

New tests:
- Change 1: `test_vanilla_14_3_spectators_use_the_face_player_step`, `test_item_17_is_an_npc_cell_with_the_face_player_step`, `test_x_sets_no_fixed_facing_on_cell`.
- Change 2: `test_each_walk_follows_its_own_spawn`, `test_each_jr_walks_down_from_above_the_view_to_its_item_spot`, `test_every_npc_jr_goes_before_the_first_jr_enemy`, `test_no_record_flies_set_31`.
- Change 3: `test_seq_58_copy_faces_gohan_right_with_the_same_next_index`, `test_right_is_toward_super_perfect_cell`.

The module `_check` also refuses a changed source before the first write for each new source: Piccolo's step and item, `set:31`'s anim 1 rows, seq 52's Gohan ops, seq 58, seq 65, item 12's spot, and the one word that names seq 58. The full suite ran once more after a last `_check` edit (anim 1 only); the v2 build bytes did not change (in-memory SHA-1 `1826ca8f...`). The test `test_a_changed_source_byte_refuses_before_writing` covers seq 58, Piccolo's step and seq 65.

---

## Files

| File | What |
|---|---|
| `scripts\permanent\patches\celljr_fight.py` | The module, v2 (v1 copy: `archive\2026-10-24-celljr-v1\celljr_fight.py`) |
| `scripts\permanent\tests\test_celljr_fight.py` | 33 tests (v1 copy in the same archive folder) |
| `scripts\one-time\2026-10-24-celljr-trial\make_trial_v2.py`, `make_trial_v2.txt` | v2 ROM and save by exclusive create, CLI proofs, both diffs cut at site edges |
| `scripts\one-time\2026-10-24-celljr-trial\npc_steps.py` | NPC step factory survey of all 327 map entries |
| `scripts\one-time\2026-10-24-celljr-trial\facing_writers.py` | Functions that store a facing after a position compare (how the step was found) |
| `scripts\one-time\2026-10-24-celljr-trial\edit_tests_v2.py` | The one-time test edit |
| `scripts\one-time\2026-10-24-celljr-trial\suite_v2.txt` | Full suite output |
| `scripts\one-time\2026-10-24-celljr-trial\bible_rows_v2.md` | CJ2 rows |
| `docs\build-log.md` | One line: `build log2_poc_r39_celljr_v2.gba ... sha1=1826ca8f...` |

The CLI proofs went to `scratch\test-roms\celljr_v2_cli_main.gba` and `celljr_v2_cli_trial.gba` (log `scratch\test-roms\celljr-cli-log.md`). PNG copies of my v1 states, for viewing only, are in `scratch\review-renders\2026-10-24-celljr-v2\`.

---

## What to watch in play

Load `log2_poc_r39_celljr_v2.gba` (mGBA pairs the `.sav` by name), slot 3, as in v1. The v1 `.ss1` and `.ss2` belong to the v1 ROM: do not load them on v2.

1. **Fight start.** After "Gohan has transformed into Super Saiyan 2!", Cell becomes an NPC where he stood. The camera moves a little to frame Gohan. Pass: no jump cut, Cell does not vanish for long.
2. **The Jrs come down.** One whoosh, then 4 Jrs come down together from above the screen to their spots, in the walk pose. Pass: each starts off screen, none shows a broken frame, all 4 stop at their spots.
3. **The swap.** A short flash, then the 4 fight. Pass: 4 enemy Jrs, no extra still Jr left behind.
4. **Cell turns.** Move around Gohan during the fight. Pass: Cell turns to face Gohan, and he does not attack.
5. **After the 4th kill.** Fade, "You wretched child", the Cell fight, as v1. Pass: Gohan faces Cell (right) at the line. If he faces down here, report it (see PENDING).
6. **Super Perfect Cell talk.** From "Now I understand what Dr. Gero meant" to "I will!": Pass: Gohan faces right, toward Cell, through Goku's telepathy lines, then the fight starts as r39.
7. **v1 checks that still hold.** The 7-Jr spawn scene, the 3 ally fights, EXP per kill, a loss gives the normal game over.

## Risks

| Risk | Status | Label |
|---|---|---|
| Face step stops during combat | Vanilla spectators use it on this map; not watched in a fight | L |
| Jrs visible at spawn | Y 248 is 40 px above a view top of 288; the camera move may still run when they spawn (from y 336 up to 288, so the view top is never above 288) | L |
| Walk pose reads as walking in the air | `set:31` has no fly pose | C (art), my call |
| Swap flicker | 4 blocking removes (one frame or more each) under the `ext 42 (5)` flash | L |
| OBJ VRAM at fight start | 4 NPC Jrs (64 units) exist only while the HUD is off and before the enemies; the peak is the v1 fight model | L |
| World list order after a remove | Only adds happen between each spawn and its walk, so the newest rule holds there | C (listing), L (remove keeps order) |
| Change 3 scene | See PENDING | S |
