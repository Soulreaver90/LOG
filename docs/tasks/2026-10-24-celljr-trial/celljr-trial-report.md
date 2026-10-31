# Cell Jr fight: trial patch module report (2026-10-24)

The trial patch `celljr_fight` is built, tested and paired with a test save. The main build is unchanged.

Labels: **C** = CONFIRMED (bytes, listing or test), **L** = LIKELY, **S** = SPECULATIVE. All addresses are r39 (`builds\log2_poc_r39.gba`, SHA-1 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`, read and checked).

---

## SHIPPED

| Ask | Result |
|---|---|
| Trial patch module under `scripts\permanent\patches\` | `scripts\permanent\patches\celljr_fight.py` |
| Second build list, approval = move one line | `scripts\permanent\build_list_trial.txt` = the 19 main lines + `celljr_fight` |
| `--list <file>` option with a test | `log2_build.py --list FILE.txt`; `--list` alone keeps `build_list.txt`. Test `test_build.BuildTests.test_list_option_reads_the_main_list_or_a_named_file` |
| Module tests (addresses, bytes, counter logic, EXP split) | `scripts\permanent\tests\test_celljr_fight.py`, 24 tests, OK |
| Full suite once at the end | 691 tests OK (baseline 666 + 24 + 1). `scripts\one-time\2026-10-24-celljr-trial\suite.txt` |
| Trial ROM, exclusive create | `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr.gba`, SHA-1 `093c1667ad99d8279a8f2d5d61fcf8325a1b548d` |
| Main `--list` still gives r39 | CLI `--list` SHA-1 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`, bytes equal to `builds\log2_poc_r39.gba` (C) |
| Trial differs from r39 only inside the module's ranges | 780 bytes, 0 outside the 22 named sites, 0 named sites without a change (C) |
| Test save next to the ROM, scouter on in every slot | `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr.sav`, SHA-1 `aa8efb2adaa7aa87f4cff27ceb7244368bd02759` |
| Bible rows, tag CJT | `scripts\one-time\2026-10-24-celljr-trial\bible_rows.md` (sections 8, 11, 12, 13) |

## PENDING

| Item | Why |
|---|---|
| Emulator play test (checklist below) | No emulator run in this task. Every in-game claim is L or S |
| Me: HP refill before the Cell fight? | Gohan goes into the Super Saiyan 2 Cell fight with the HP the 4 Jrs left. Vanilla refills HP and EP in the Rage scene, before the Jrs. Not added (not asked) |
| Me: positions | The 4 extra NPC Jrs and the 4 fight Jrs use the study's first guesses (S) |
| Me: merge the CJT rows into `docs\RE-BIBLE.md` | The brief asks for a rows file only. Add `CJT` to the source list |
| Approval | Move the `celljr_fight` line to the end of `build_list.txt`. The same change must update 3 tests, or they fail: `test_art_inject.LIST` (the full main list), `test_bf_hud.test_build_list_ends_with_the_hud` (`names[-3:]`), and `test_celljr_fight.built()` (reads `build_list_trial.txt`; switch it to `read_build_list()` before the trial list is deleted). `test_celljr_fight.ListTests.test_trial_list_is_the_main_list_plus_the_trial_line` skips by itself once the line is in the main list |

---

## Files

| File | What |
|---|---|
| `scripts\permanent\patches\celljr_fight.py` | The module. `apply(rom, alloc)`; every write in `alloc.notes["celljr_fight"]["sites"]` |
| `scripts\permanent\build_list_trial.txt` | The trial build list |
| `scripts\permanent\log2_build.py` | `--list FILE.txt` (2 lines and the Usage text) |
| `scripts\permanent\tests\test_celljr_fight.py` | 24 module tests |
| `scripts\permanent\tests\test_build.py` | 1 new test for `--list` |
| `scripts\one-time\2026-10-24-celljr-trial\make_trial.py`, `make_trial.txt` | Trial ROM and save by exclusive create, CLI proofs, save info |
| `scripts\one-time\2026-10-24-celljr-trial\diff_proof.py`, `diff_proof.txt` | r39 to trial diff cut at site edges |
| `scripts\one-time\2026-10-24-celljr-trial\suite.txt` | Full suite output |
| `scripts\one-time\2026-10-24-celljr-trial\bible_rows.md` | CJT rows |
| `docs\build-log.md` | One line: `build log2_poc_r39_celljr.gba ... sha1=093c1667...` |

Build commands:
- Trial: `py -3 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial.txt --out <new .gba>`
- Main (unchanged): `py -3 -P scripts\permanent\log2_build.py --list --out <new .gba>`

The CLI proofs went to `scratch\test-roms\celljr_cli_main.gba` and `celljr_cli_trial.gba`, with their log in `scratch\test-roms\celljr-cli-log.md`. The trial CLI SHA-1 equals the exclusive-create file (C, `make_trial.txt`: "cli --list build_list_trial.txt sha1 093c1667... == trial ROM: True").

---

## What the module does

The design follows the study (Parts 1-4) and the 6 final decisions. All source bytes, words and records are checked before the first write, and a second run raises (C, `_check`, tests `test_a_changed_source_byte_refuses_before_writing`, `test_second_run_raises`).

1. **Spawn 7 (decision 2).** Spawn table `rom:0x3E9D4C` word 30 (`rom:0x3E9DC4`) names a copy of seq 31 at `rom:0x90A308`. The copy spawns 4 NPC Jrs (set 31) at (384,408), (480,408), (408,424), (456,424) with the vanilla seq 27 pattern (`ext 42 (5)`, `ext 51`, `ext 43 (5)`, `ext 69 (40)`). Then the vanilla body runs with 7 removes of set 31, not 3. Seq 27 stays vanilla, so the two lines show 3 Jrs (C, tests `test_seq_27_is_vanilla_with_3_jrs`, `test_spawned_jrs_equal_removed_jrs`: 7 spawned = 7 removed).
2. **Spawn list (decisions 1, 3).** Map 14,3 count `rom:0x40DA84` 13 to 17. List word `rom:0x40DA94` names a 17-word copy at `rom:0x90A5D0`. Items 13-16 are item 8's 0x20 bytes (type 26, set 31, cond 1), each with its own tail copy and event struct `{0x080106B3, T}`, laid out as vanilla does. Positions (528,344), (528,408), (624,344), (624,424) (C, `test_new_items_are_item_8_with_own_place_tail_and_event`).
3. **Fight start X (decisions 3, 4).** Gohan's table `rom:0x3EA400` word 30 (`rom:0x3EA478`) names X at `rom:0x90A3C8`. Rage line word 29 goes to index 30, so X runs right after "Gohan has transformed into Super Saiyan 2!". X: `push 0 ; set var1`, `ext 52 (30)` (type 24 Cell out), `ext 51 (30, 616, 384)` (NPC Cell), `ext 55 (30, 2)`, then 4 x (`ext 42 (5)`, `ext 84 (13..16)`, `ext 43 (5)`, `ext 69 (40)`), `ext 33 (0)`, `ext 86 (1)`. Next index 32 = END, so the fight runs. No `ext 85` (no boss bar) (C, `test_x_swaps_cell_and_builds_items_13_to_16`).
4. **Counter C (decisions 4, 6).** Table T at `rom:0x90A48C` word 0: `inc var1 ; push 12500 ; ext 139 ; ext 1 ; push 4 ; lt ; jz +3 ; push 1 ; end ; push 29 ; end`. A stack model runs it for deaths 1-4: next index 1, 1, 1, 29; EXP 4 x 12,500 = 50,000 (C, `test_counter_ends_three_kills_and_restores_on_the_fourth`, `test_a_double_kill_still_reaches_29_once`).
5. **Restore N (decision 5).** T word 29: `ext 88`, `ext 86 (0)`, `ext 40 (120)` fade out, `ext 52 (30)` NPC Cell out, `ext 84 (11)` type 24 Cell back (its event stays the self-destruct table `rom:0x3EB704`), `ext 62 (30, 616, 384)`, `ext 55 (30, 2)`, `ext 62 (0, 576, 376)`, `ext 55 (0, 3)`, `ext 31 (432, 336, 40)`, `ext 41 (120)` fade in. Next index 30 (C, `test_n_fades_and_brings_cell_back`).
6. **The line and the Cell fight.** T words 30 and 31 name the vanilla records "You wretched child" `0x083EA3B4` and seq 32 `0x083EA3EC`. Their +0 next indexes are 31 and 32, which fit T, so the study's copies are not needed. Word 32 = END, then the Cell fight runs as today (C, `test_table_t_layout`). Deviation from the study: reuse, not copies. Reason: one source for the line.

### Proving lines

| Claim | Proof | Label |
|---|---|---|
| Each death starts T at word 0 | Event runner `0x080106b8 mov r1,#0x0` ; `0x080106ba strh r1,[r3,#0x24]` (r3 = sp), then `bl 0x0800b4ae` with r2 = sp+0x24 | C |
| `push a ; push b ; lt` = a < b | Op 15 `0x080090d4 ldr r2,[r0,#0x4]` (top) ; `ldr r3,[r0,#0x0]` ; `cmp r3,r2 ; blt` | C |
| `jz +3` skips `push 1 ; end` | Op 19 `0x08009118 ldrb r3,[r0,#0x0]` ; `add r0,#0x1` ; `cmp r2,#0x0 ; bne` ; `add r0,r0,r3` | C |
| `inc var1` leaves the stack unchanged | Op 21 calls ext 1 (`0x080093a4 ldr r1,=0x03001fb0 ; ldr r2,[r1,#0x4]`, push), pops, `add r0,#0x1`, setter 1 (`0x0800b060 str r0,[r1,#0x4]`) | C |
| One value left replaces the next index | Bible row SS3 (scene runner `@0x0800B520`, type 0 `@0x0800B19C`) | C (SS3) |
| NPC Cell by `ext 51 (30, ...)` has a vanilla precedent | `rom:0x3E6C8C push 29 ; ext 52 ; push 30,136,184 ; ext 51` | C |
| `ext 52 (30)` removes an enemy Cell without its death event | Vanilla Gohan seq 1 (`0x0889A71C`) runs `push 30 ; call 52` on the type 22 Cell enemy after the `ext 39` reload, and that enemy's event table `0x083E93E8` does not run there. X does the same to the type 24 enemy | C (bytes), L (no event fires) |
| `ext 88` in N is safe with no boss bar on | ext 88 `@0x0800AC00` calls `@0x08006E0A` (world, 0x10, 0), which loops over the world lists (`ldr r4,[r0,#0x4] ; sub r4,#0x1 ; bmi`) and sends message 0x10 to each object's vtable +0x24 handler. With no bar object, no handler takes it; nothing reads a bar pointer | C (listing), L (no other object acts on 0x10) |
| Superseded targets have no other name | `0x083E9CF0` and `0x08409118`: 0 aligned words in the trial ROM; `0x083EA3B4`: only T word 30 (test `test_superseded_targets_have_no_other_name`) | C |
| Ally fights unchanged | Tables `rom:0x3E9E24`, `rom:0x3E9E84`, their seq 1 records and items 8-10 keep their bytes (test `test_ally_fights_keep_their_bytes`) | C |

---

## Diff r39 to trial

780 bytes changed, all inside the 22 named sites (C, `diff_proof.txt`: "changed bytes outside every site: 0", "sites with no change: []").

| Run | Bytes changed | Site |
|---|---|---|
| `rom:0x3E9DC4`-`0x3E9DC6` | 3 | spawn table word 30 |
| `rom:0x3EA478`-`0x3EA47A` | 2 | Gohan table word 30 |
| `rom:0x40DA84` | 1 | map 14,3 spawn count |
| `rom:0x40DA94`-`0x40DA96` | 3 | map 14,3 spawn list word |
| `rom:0x90A308`-`0x90A3C5` | 190 | seq 31 copy (7 Jrs) |
| `rom:0x90A3C8`-`0x90A42A` | 99 | record X |
| `rom:0x90A42C`-`0x90A444` | 25 | record C |
| `rom:0x90A448`-`0x90A488` | 65 | record N |
| `rom:0x90A48C`-`0x90A613` | 392 | table T (132), items 13-16 with tails and event structs (4 x 48), spawn list copy (68) |

The base data changes only at the 4 words and the count byte (C, test `test_base_data_changes_only_at_the_four_sites`). `make_trial.txt` shows the last run as one 392-byte run marked "OUTSIDE A NAMED SITE": its first classifier needed one site to hold a run whole. `diff_proof.py` cuts the run at the site edges and names every byte.

---

## Test save

`builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr.sav` (C, `log2_save.py info` in `make_trial.txt`: every slot "checksum ... valid", header flags 0x07, scouter bit 1).

| Slot | Map | Leader | Story |
|---|---|---|---|
| 1 | Capsule Corporation save point, 6,1,1 (432,591) | Gohan | post-Cell |
| 2 | Master Roshi's Island arrival, 11,1,1 (416,160) | Gohan | post-Cell |
| **3** | **Cell Games Arena world-map arrival, 14,1,1 (264,304)** | **Goku** | `flag:191` set, 192-195 clear, arena maps unvisited |

Slot 3 is the latest safe entry. The Cell Games has no save point (CJR). The arena landing is the vanilla world-map warp (`@0x083FBDC4` = `push 14,1,1,264,304 ; ext 38`, SS3), the `log2_save` preset `cellgames2_arena`. A slot deeper on 14,2 or 14,3 would skip the entry scenes and is not proven. My test of this preset is still pending (SS3 row, L).

Made by `log2_save.make_slot` per preset slot, header +1 bit 2 set, `seal_slot`, then `log2_save.write` (refuses an existing file). Base bytes from `builds\log2_poc_r39.sav`.

---

## Emulator check still needed

Load `log2_poc_r39_celljr.gba` (mGBA pairs the `.sav` by name), slot 3. Make a state before Gohan's first Cell fight ends: the Jr scene needs Goku's fight and that fight first.

1. **Spawn scene.** 3 Jrs pop out after "Hrmm... Still not angry enough Gohan?". After "My children! Give them pain!", 4 more pop out with a flash each, then the fade. Pass: 7 Jrs, no corrupt tiles while they stand.
2. **Ally fights.** Piccolo, Vegeta and Trunks each fight one Jr as today. Pass: no extra Jr on screen in any of them.
3. **Gohan's transform scene** plays as today up to "Gohan has transformed into Super Saiyan 2!".
4. **Fight start.** Cell stays where he stood, 4 Jrs flash in around Gohan, the HUD shows, no boss bar. Pass: Cell does not attack during the Jr fight.
5. **The fight.** Each kill gives EXP (12,500 each). Watch for a HUD flicker or a cancelled attack at each kill (deaths 1-3 run a short event scene). Pass: the fight goes on after kills 1-3.
6. **After the 4th kill.** Fade out, then fade in on Gohan and Cell, "You wretched child!!! NOW TASTE MY TRUE POWER!!!!!!", then the Cell fight with its boss bar. Pass: the Cell fight, the self-destruct and Super Perfect Cell run as in r39.
7. **Loss.** Let the Jrs win once. Pass: the normal game over.
8. **Positions.** Check that no Jr spawns inside a wall or off screen (positions S).

---

## Risks from the study, with status

| Risk | Status | Label |
|---|---|---|
| OBJ VRAM at the spawn lines | Avoided as the study planned: seq 27 keeps 3 Jrs through both text lines; the other 4 spawn in the seq 31 copy, where no text box follows | C (bytes), L (VRAM in game) |
| OBJ VRAM in the 4-fight | Unchanged from the study model (264 units free). N turns the HUD off before the "wretched" box, and the Jrs are gone then | L |
| Cell joins the Jr fight | X removes the type 24 enemy and spawns an NPC Cell; N rebuilds the enemy with `ext 84 (11)` | C (bytes, tests), L (in game) |
| Counter clobbered | Var 1 is reset in X and has no other user by the study's shapes. Var 0 (14,3 ambient scratch) is not used | C (var 0 user), L (var 1 free) |
| Mid-fight event scenes | Deaths 1-3 each run one code record (C) and end. No vanilla precedent | S |
| Stun-lock with 4 AI 21 enemies | Not tested | L |
| CPU, OAM, heap, world list | 17 spawn items, 4 enemies at once, under vanilla's 15-enemy maps | L |
| Softlock | No exit on 14,3. A Jr stuck in a wall would stop the counter. Positions are first guesses | S |
| Save flags | None added. The counter is RAM only and reset in X | C |
| Rebase from r38 | Done: every site was read on r39 and is checked before the write. The 4 base words held the vanilla values (`rom:0x3E9DC4` = `0x083E9CF0`, `rom:0x3EA478` = `0x083EA3B4`, `rom:0x40DA94` = `0x08409118`, `rom:0x40DA84` = 13) | C |
| New: level-up scene mid-fight | `ext 139` runs on each kill while other Jrs live. A level-up opens a scene. Not at Lv40 with the test save (the next level needs 3,335,510 EXP) | S |
| New: death param delay | The 0x40 death param may delay N after the 4th kill (CJR) | S |
| New: item tail | Items 13-16 carry a copy of item 8's tail `{0x0800CB0F, 0x00017D00}`. Its meaning is not traced | C (bytes), S (meaning) |
