# Cell Jr trial v5: AI changes only (2026-10-29)

The v5 trial ROM is built. The 4 fight Jrs use a trial copy of AI 21 with a 30-frame wait after each punch and a 2.5 % blast roll. Their stats stay those of type 26. The main build is still r39.

Labels: **C** = CONFIRMED (listing, bytes or test), **L** = LIKELY, **S** = SPECULATIVE. Addresses are in the v5 ROM unless a line says otherwise. Code addresses are equal in base, r39 and v5.

---

## SHIPPED

| Ask | Result |
|---|---|
| "Let's try just the AI changes, not the stats." | The 4 trial Jrs get a new AI: AI 21 with a **30-frame wait after each punch** and a **2.5 % blast roll** (was 5 %). HP 4990, STR 46, POW 50, END 46, factors and death descriptor are type 26's (C, bytes and test) |
| Never change AI 21 or type 26 in place | AI 21 rows, the whole node block `rom:0x6D0000`-`0x6D5193`, the AI table and type 26 are byte-equal to r39. Items 8-10 (the relay Jrs) still name type 26 (C, test) |
| Route, with evidence | The AI comes from the type entry, so a trial type entry was added (CJH option 1b shape) with +8 = the trial AI. See "Route" |
| Type words found through the spawn items, v4 moved nothing | Items 13-16 found through the spawn list copy: their type words are `rom:0x90A56C`, `0x90A59C`, `0x90A5CC`, `0x90A5FC`, the same words as v3 and v4. Every v4 allocation is at its v4 address (C, `make_trial_v5.txt`) |
| Keep the rest of v4 | 7 Jrs spawn, 4 fight at once, Jrs 3-4 at (388,366) and (476,370). The v4 to v5 diff touches only the 4 type words and new data after the spawn list (C) |
| Tests | `test_celljr_fight` 47 OK (v4: 39): 8 new, 1 updated. `test_vegeta_ssj_scene` 47 OK, not edited (C) |
| `--list` still gives r39 | CLI `--list` SHA-1 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`, bytes equal to `builds\log2_poc_r39.gba` (C) |
| v5 ROM and save, exclusive create | `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr_v5.gba` and `.sav` (C) |
| Diff runs v4 to v5 | 6 runs, 948 bytes, 0 outside a site. See "Diff runs" |
| Expected effect in numbers | See "Numbers" |
| Full suite, once at the end | `Ran 868 tests ... OK` (C, `suite_v5.txt`) |
| Bible rows, tag CJ5 | `scripts\one-time\2026-10-24-celljr-trial\bible_rows_v5.md` (sections 8, 11, 12, 13, 14) |

## PENDING

| Item | Why |
|---|---|
| Me: emulator play test | No emulator run in this task. Every in-game claim is L or S |
| Pins changed: **none** | The brief expects tests that pin the trial list SHA-1. Three search shapes found none: a quoted 40-hex literal in `test_celljr_fight.py` and `test_vegeta_ssj_scene.py`; `abbe5004`, `470f62a6` (and the new SHA-1s) across `scripts\permanent\art\*.py`, before and after the change; `abbe5004` and `470f62a6` in every file under `scripts\permanent` (control: `aa51dc16` is found in 3 tests). Also, the full suite passed after the trial SHA-1 changed. So no pin was edited. The Vegeta list now builds `24f52a6b...` in memory (C) |
| Scouter over a trial Jr | The type matcher finds no entry for the trial type, and its only caller skips such an enemy (guarded, no save write). See "Route" (C code, L screen effect) |
| Roll cadence and the real gap after a hurt | Not traced. The blast and lock numbers are S until CJB emulator steps 4 and 6 run |
| Me: merge the CJ5 rows | See the merge notes in the rows file |
| Approval | As before: move the `celljr_fight` line to `build_list.txt` and update the 3 tests the v1 report names |

---

## Route (C)

The enemy constructor reads the AI id from the type entry, not from the spawn item:

| Step | Evidence |
|---|---|
| Enemy +0x180 = the type entry | `@0x0800E2D4`-`@0x0800E2DC`: r5 = r7 - 0x1C = enemy +0x180; `str r1,[r5,#0x0]` |
| AI id = type +8 | `@0x0800E302` `ldr r0,[r5,#0x0]`, `@0x0800E304` `ldr r1,[r0,#0x8]`, `@0x0800E308` `bl 0x801aa98` |
| Row = id x 8 + table, u32 | `@0x0801AAA2` `lsl r0,r1,#3`, `ldr r1,=0x086d5194` |
| PUSH and JUMP ids are u32 too | PUSH factory `@0x0801AB64` stores `{0x08024FF4, [node +0xC]}`, tick `@0x0801AB50` calls `@0x0801AA46` (`lsl r0,r1,#3`); JUMP `@0x0801B512` `ldr r0,[r0,#0xc]` |
| Hits go back to the type's AI | Rows 22-28 share hit list `0x086FF4C4`. Its methods `@0x0801C456`-`@0x0801C47A` read enemy +0x180, then type +8, then `[table + 8 x id + 4]`. For the trial type that is row 21', which runs `PUSH 21'` then `JUMP 18` |
| No hit row names 21-28 | A walk of every in-block word from rows 16-20 reaches push and jump ids 16, 17, 19, 20 only (`study_v5.txt`, test) |

A spawn item has no AI field, so the type entry is the only trial-only route. The item +8 word was already in each item that the module builds, so no vanilla word changes.

**Every reader of the two tables (two shapes, `readers_v5.py`, `readers_v5.txt`):**
- Shape A, BL callers of the scouter type matcher `@0x080190D4`: one, `@0x0800E5EE`. It is guarded: `add r3,r0,#1 ; bne 0x800e5fa ; mov r0,#0x0` (`@0x0800E5F2`-`@0x0800E5F6`), so a -1 (no entry) returns 0 before the list write at `@0x0800E60A`. No save bit is touched (C).
- Shape B, `ldr` from a literal pool word `0x086D56AC` (type table): `@0x0800E782` (enemy factory, spawn +8 as u32), `@0x08017964` (reads scouter entry +0x10, not an actor, so entry 20 still shows type 26), `@0x080190DA` (the matcher). From `0x086D5194` (AI table): `@0x0801AA4C`, `@0x0801AAA4`, `@0x0801B514`, `@0x0801B528`, `@0x0801C458`, `@0x0801C472`. All 6 shift a u32 id left by 3 (C).
- A reader that holds a table base in a register, or reads through enemy +0x180, would not show. Readers through +0x180 get a valid entry.

**Side effect (C code, L screen):** the matcher compares `24 x [entry +0x10] + 0x086D56AC` with the type entry. Entry 20 (`set:31`) holds 26, so a trial Jr matches no entry, and the caller `@0x0800E5EE` leaves it out of its list. So a trial Jr is likely missing from the scouter scan. The relay Jrs are unchanged.

## The AI change (C)

| What | Where | Value |
|---|---|---|
| Trial type entry | `rom:0x90AA14` = `0x6D56AC` + 24 x **96463** | `00000000 7e130000 076b0400 2e322e 8080 000000 54566d08`: type 26 except +8 |
| Trial AI rows 21'-28' | `rom:0x90A9CC` = `0x6D5194` + 8 x **289543** | ids 289543-289550, 64 bytes |
| Node copy | `rom:0x90A67C`-`0x90A9CB` | 39 nodes, 848 bytes (844 + 4 for row 26') |
| Item type words | `rom:0x90A56C`, `0x90A59C`, `0x90A5CC`, `0x90A5FC` | 26 -> 96463 |
| Post-punch wait | row 26' SEQ `0x0890A8F0` | n=3 {PUNCH `0x086D25BC`, wait `0x086D1FC4`, OR' `0x0890A8D4`}. Vanilla row 26 `0x086D2630` is n=2 {PUNCH, OR} |
| Blast roll | row 22' RANDOM `0x0890A6EC` +0xC | `0x666`. Vanilla `rom:0x6D23E4` stays `0xCCC` |

- **Roll scale.** `rand16` `@0x0802142E` takes `rand & 0xFFFF` (`lsl/lsr #16`) and returns 1 when it is below p (`cmp r0,r4 ; bcs`). So 0xCCC = 5.00 % and 0x666 = 2.50 % (C).
- **Wait.** The shared vanilla node `0x086D1FC4` = `{0x0801BBAD, 0, 0, 0x1E}`, as AI 8, 45 and 52 use it. Factory `@0x0801BBAC` allocates a fresh `{0x08023BF0, n}` for each use, so sharing it is safe. Tick `@0x0801BB94` returns done when the count reaches 0, so it lasts 30 ticks (C).
- **Every punch.** The only punch leaf that rows 21-28 reach is `0x086D25BC`, and its only parent is row 26's SEQ. Rows 25 and 26 reach it only by PUSH row 26. So the wait follows every Jr punch, chained ones too (C, walk and test).
- **The copy.** Module functions `ai_tree()`, `to_copy()` and `trial_ai()` walk rows 21-28 from the ROM. They copy the nodes that name a row 21-28 or reach one, in address order, re-point children, and renumber PUSH 21-28. Shared: the 10 block nodes `ai_copy_plan.txt` lists (JUMP 18 among them), the wait node and every `0x086FFxxx` singleton. An unknown node factory raises. A test compares the copy tree against rows 21-28 node by node: the roll and row 26' are the only differences (C).
- Trees side by side: `scripts\one-time\2026-10-24-celljr-trial\study_v5.txt`.

## Numbers

From `numbers_v5.py` (`numbers_v5.txt`). Swings are punch attempts; a damaging hit is a swing that lands outside Gohan's hurt state.

**Hard bounds (C from node bytes and state lengths; L for the 16-frame enemy punch state):**
- The wait starts only after the punch state ends: the punch leaf tick `@0x0801BE78` returns the enemy's vtable +0x2C (0), which is `@0x0800E590`: 1 when enemy +0x18 is the state 0 object `[0x0840DB00]` (C).

| Bound | Before (AI 21) | After (trial AI) |
|---|---|---|
| One Jr chaining punches back to back | one every 16 frames = 3.75/s | one every 46 frames = 1.30/s |
| Damaging hits, any number of Jrs | one per 32-frame hurt state = 1.875/s | same cap |

**Toy model (S: a ready Jr in reach swings with 50 % a frame; rows 27 and 28 cost 0-20 frames; the CJB lock toy, extended to count every chained swing):**

| Case | Before | After |
|---|---|---|
| Punches per second, one Jr | 2.50 | **1.11** |
| Punches per second, 4 crowded Jrs | 9.89 (2.47 a Jr) | **4.44** (1.11 a Jr) |
| Damaging hits per second, one Jr | 1.40 | 1.11 |
| Damaging hits per second, 4 crowded Jrs | 1.68 | **1.34** |
| Median free frames after each hurt, 4 Jrs | 3 | **14** |
| Rage Gohan from full HP, 4 Jrs, no counterplay, with 27 HP/s regeneration | about 33 s | about 55 s |

- The CJB toy showed WAIT30 raising one-Jr hits (1.19 to 1.25). That was because it did not count the 25 % chained swings as hits. This model counts them. One Jr now drops from 1.40 to 1.11.

**Blasts per minute (S: the roll cadence is not traced):**
- A Jr rolls only in row 22, at 72-120 px from Gohan, after the line-up. **Within 72 px a Jr never rolls**: row 22's near branch (d2 `0x1440`) pushes row 24 first. So the crowded Jrs do not blast, before and after (C, node bytes). From 72 px out a Jr can reach the roll: row 28's far branch (over 80 px) and row 24's (over 88 px) push row 22.
- The line-up tick `@0x0801AFA0` returns done at once when the Jr is lined up (`cmp r1,#0x3` `@0x0801B036`). So a parked, lined-up Jr reaches the roll on that tick (C).
- One blast costs a 32-frame blast state plus 1/p rolls: 20 rolls before, 40 after.

| Rolls of a parked, lined-up Jr | Before | After | Change |
|---|---|---|---|
| Every frame | 69 a minute | 50 a minute | -28 % |
| Every 2 frames | 50 | 32 | -36 % |
| Every 4 frames | 32 | 19 | -42 % |
| Every 8 frames | 19 | 10 | -45 % |

- Blast damage stays 32-35 (POW 50 unchanged).

## SHA-1s (C)

| File | SHA-1 |
|---|---|
| `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr_v5.gba` | `19485fed16ab4121c7817c36ef5fb59e92812e51` |
| `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr_v5.sav` (copy of the v4 save) | `aa8efb2adaa7aa87f4cff27ceb7244368bd02759` |
| CLI `--list` (main) | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` = r39, bytes equal |
| CLI `--list build_list_trial.txt` | `19485fed...` = the v5 ROM (was `abbe5004...`) |
| `build_list_trial_vegeta.txt`, in memory only (no file) | `24f52a6bf2cdcafb7170cda3f27c201c8830c365` (was `470f62a6...`) |
| Sources checked before the build | r39 `aa51dc16...`, celljr v4 `abbe5004...`, Vegeta v5 `470f62a6...`; before the module edit, all three lists rebuilt in memory to these values |

- Both targets were checked before the first write and opened with `"xb"`. No ROM, save or state was overwritten. `docs\build-log.md` has one new line (7:05 PM).

## Diff runs (C, `make_trial_v5.txt`)

**v4 to v5: 948 bytes in 6 runs, 0 outside a site.** The node copy and the rows are adjacent, so they form one run cut in 2 at the site edge.

| Run | Bytes | Site |
|---|---|---|
| `rom:0x90A56C`-`0x90A56E` | 3 | item 13 type word (26 -> 96463; the 4th byte stays 00) |
| `rom:0x90A59C`-`0x90A59E` | 3 | item 14 type word |
| `rom:0x90A5CC`-`0x90A5CE` | 3 | item 15 type word |
| `rom:0x90A5FC`-`0x90A5FE` | 3 | item 16 type word |
| `rom:0x90A67C`-`0x90AA0B` | 848 + 64 | trial AI nodes, then trial AI rows 21'-28' |
| `rom:0x90AA14`-`0x90AA2B` | 24 | trial type entry |

- `rom:0x90AA0C`-`0x90AA13` is alignment slack. It stays 0xFF and is in no site.
- **r39 to v5:** 1818 bytes in 13 runs, 0 outside a site, no site without a change.
- **Vegeta v5 file to the Vegeta list now:** 1394 bytes in 21 runs, 0 outside a site. The `vegeta_ssj_scene` copies move to `rom:0x90AA3C` and `rom:0x90AB68`. Its base sites and the set 160 row `rom:0x88D97C` keep their addresses.

## Tests

| Run | Result |
|---|---|
| `test_celljr_fight` | 47 OK |
| `test_vegeta_ssj_scene` | 47 OK, file not edited |
| Full suite, once at the end (`py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent -v`) | `Ran 868 tests in 163.393s`, `OK` (`suite_v5.txt`) |

**New, class `TrialAiTests`:**
- `test_ai_21_type_26_and_the_node_block_are_unchanged`
- `test_the_trial_type_is_type_26_with_the_trial_ai` (both grid checks: (address - base) is a multiple of 24 and of 8)
- `test_the_4_fight_jrs_use_the_trial_type_and_the_relay_jrs_keep_26` (items found through the spawn list)
- `test_the_copy_is_rows_21_to_28_with_only_the_two_changes` (node count, size, shared set, tree compare)
- `test_row_26_waits_30_frames_after_the_punch_and_row_22_rolls_2_5_percent`
- `test_the_punch_leaf_is_reached_only_through_row_26`
- `test_a_hit_returns_to_the_trial_ai` (code pins for the ctor, AI start, JUMP, hit singleton, `rand16`, wait tick; the hit-path walk)
- `test_a_changed_ai_byte_refuses_before_writing`

**Updated:** `test_new_items_are_item_8_with_own_place_tail_and_event` now expects the trial type at item +8 and keeps item 8's 26 as the source.

**Mutation check:** with the roll left at 0xCCC, 2 new tests fail. With one copied PUSH left at row 21, 1 new test fails (C).

## Files

| File | What |
|---|---|
| `scripts\permanent\patches\celljr_fight.py` | AI constants, `node_shape()`, `ai_tree()`, `to_copy()`, `trial_ai()`, `_alloc_on_stride()`, the `_check` additions, the v5 block at the end of `apply()`, new notes keys, header Method item 6 |
| `scripts\permanent\tests\test_celljr_fight.py` | 47 tests |
| `scripts\one-time\2026-10-24-celljr-trial\study_v5.py`, `study_v5.txt` | Route listings, both AI trees, hit-path walk, scouter match |
| `scripts\one-time\2026-10-24-celljr-trial\numbers_v5.py`, `numbers_v5.txt` | The numbers |
| `scripts\one-time\2026-10-24-celljr-trial\readers_v5.py`, `readers_v5.txt` | Table readers and the scouter matcher caller, two shapes |
| `scripts\one-time\2026-10-24-celljr-trial\make_trial_v5.py`, `make_trial_v5.txt` | ROM and save by exclusive create, CLI proofs, diffs |
| `scripts\one-time\2026-10-24-celljr-trial\suite_v5.txt` | Full suite output |
| `scripts\one-time\2026-10-24-celljr-trial\bible_rows_v5.md` | CJ5 rows |

- CLI proofs: `scratch\test-roms\celljr_v5_cli_main.gba` and `celljr_v5_cli_trial.gba` (log `celljr-v5-cli-log.md`).
- **Limit breach:** one read-only Bash call began with `cd` into `scripts\one-time\2026-10-25-celljr-balance` to walk the hit lists. It wrote no file, and its paths were absolute. No other call used `cd` or `Push-Location`. One temporary mutation script was written to the user temp folder and deleted.
- **Not touched:** `chapter_cards.py`, `relay_cooldown.py`, `fullpower_hud.py`, `beam_struggle.py`, `vegeta_ssj_scene.py` and their tests, every build list, `docs\RE-BIBLE.md`, `docs\ledger\`, `scripts\one-time\2026-10-25-chapter-cards\`.

---

## What to watch in play

Load `log2_poc_r39_celljr_v5.gba` with its `.sav`, slot 3, as before. Old `.ss*` states belong to their own ROMs. Do not load them on v5.

1. **The spawn and the walk-in are v4.** 7 Jrs, the 2 circle spots, the Jrs walk down from the top.
2. **After a Jr punches, it stands still for about half a second** (30 frames) before it moves or punches again. In a 4-Jr crowd, expect gaps after each hit. The model says about 14 free frames (a quarter second), up from about 3 (S).
3. **Blasts.** Jrs at range (about 72-120 px, after a back-off or a knock-back) still shoot, but less: 28 to 45 % fewer, depending on how often a Jr rolls (S). Jrs within 72 px do not shoot, as before (C).
4. **The fight is no shorter.** Each Jr still has 4990 HP: about 17 Rage punches a Jr, 67 for the group (CJB model).
5. **Hits still return to the trial AI.** After you knock a Jr back, it should keep the pause after its punches. If it chains punches with no pause, report it: that would mean a hit sent it into AI 21 (the code says it cannot, C).
6. **Select (scouter) during the fight** likely leaves the trial Jrs out (L). The code skips them safely (C). The relay Jrs are unchanged.
7. **The relay Jr fights (Piccolo, Vegeta, Trunks) are unchanged.** They still use type 26 and AI 21.

## Risks

| Risk | Status | Label |
|---|---|---|
| A large type or AI id breaks a reader | Every `ldr` of either table base (3 type, 6 AI sites) handles a u32 id or reads a scouter entry; the one matcher caller is guarded. A reader with the base in a register would not show | C (both shapes), L (other shapes) |
| The copy misses a pointer | The walker raises on an unknown factory. A test compares the trees node by node, and the mutation check shows the test catches a wrong PUSH | C |
| The wait is too weak or too strong | The effect size is S until CJB emulator step 4 measures the gap after a hurt | S |
| Vegeta all-trials ROM | Not rebuilt (not asked). Its list now gives `24f52a6b...` in memory; no file holds it | C |
