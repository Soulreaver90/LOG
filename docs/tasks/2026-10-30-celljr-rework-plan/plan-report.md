# Plan: Cell Jr rework, Vegeta-only Android 18, training scenes (2026-10-30)

This is a study and a plan only. No module, build list or ROM changed.

Labels: **C** = CONFIRMED (bytes or listing quoted), **L** = LIKELY, **S** = SPECULATIVE. ROM facts read the base ROM `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba` unless a line names r39 or the v5 trial ROM. Scripts and listings: `scripts\one-time\2026-10-30-celljr-rework-plan\`. Renders: `scratch\review-renders\2026-10-30-celljr-plan\`.

---

## SHIPPED

| Ask (my words) | Where |
|---|---|
| Cell Jr rework: relay Jrs "stop at 1/4 health ... white flash and a ding", 1 v 1 with "standard AI" and a bar, 1 v 3 with "the v5 AI", HP 1500-1600, no bar, "scripted finish ... 3 new ones that fly in" | Part 1, questions 1-7 and the step table |
| Confirm or correct my reading; last 3 wait in the background from the start, or arrive later | Part 1, "Reading confirmed" |
| "only Vegeta fights Android 18. Isn't there a gate or something?" and I update "there is a flight path ... should we hard block to Vegeta ... the best way" | Part 2, item 8 |
| Senzu Bean to Cell before Gohan's fight: "If there are frames and animations to go, then yes, otherwise we leave as is." | Part 2, item 9 |
| "Three-year training: Gohan spars with Piccolo and then Goku, then ... Vegeta gravity room" | Part 2, item 10 |
| "Vegeta first Super Saiyan" and "have him transform after the dialogue (no permanent ki)" | Part 2, item 11 |
| "Have SSJ Trunks and SSJ Goku interact like the show" | Part 2, item 12 |
| Bible rows, tag CJP | `scripts\one-time\2026-10-30-celljr-rework-plan\bible_rows.md` |

## PENDING

| Item | Why |
|---|---|
| My answers to the open questions | End of this report |
| The source of the boss-end white flash | Not found in code by two traces (Q1). The plan adds an explicit flash, so the look does not depend on it. My check 1 |
| The Buu's Fury gravity chamber map | BF text is not plain ASCII; one candidate map entry (S). Item 10 |
| Senzu Bean dialogue lines | The source page summarizes episode 181 but quotes no lines. I supply them |
| Trunks and Goku dialogue lines | My supplies them (item 12 lists the slots) |
| No emulator run | Every in-game claim is L or S |
| Me: merge the CJP rows | Rows file |

---

# Part 1: Cell Jr rework (build-ready plan)

## Reading confirmed

My reading of my words fits the game. I recommend that the last 3 arrive later.

| Point | Verdict | Evidence |
|---|---|---|
| The 3 relay Jrs end beaten at 1/4 and become the 1 v 3 group | Fits | 3 relay items (8, 9, 10) = 3 in the group (C, CJR). They cannot be the same actors: see Q3 |
| The 1 v 1 Jr is a fresh one at full HP | Fits | 1 of the 4 extra Jrs the v4 spawn scene already adds (7 spawned, C, CJ4) |
| The last 3 are new Jrs that fly in | Fits | 3 + 1 + 3 = 7 = the 7 the spawn scene shows (C, CJT `test_spawned_jrs_equal_removed_jrs`) |
| Last 3: wait in the background or arrive later? | **Arrive later (recommended)** | (1) Gohan's table seq 1 reloads map 14,3 (`ext 39 (14,3,1,576,376)` in `0x0889A71C`, C bytes), so a Jr placed before it is gone after it (L). (2) Three idle NPC Jrs through the Hercule and Android 16 text boxes cost 48 of the OBJ pool while a box needs 224 contiguous units (CJR model, L). (3) Idle Jrs on screen during the 1 v 1 and 1 v 3 read as enemies that do not fight (S). "Fly in" is my own word |

## Q1. The white flash and the ding

The ding is sound 60 at the head of the boss death table. The flash is not in the scripts of Android 18 or Semi-Perfect Cell, and I did not find it in code.

| Fact | Evidence | Label |
|---|---|---|
| Every decoded boss death table runs `push 60 ; ext 46` in its word 0 record: Android 18 `0x083D8BC4` (`push 11,3 ; ext 57 ; push 60 ; ext 46 ; push 60 ; ext 69 ; ext 88`), Semi-Perfect Cell `0x083E6658`, Android 17 `0x083E4818` and `0x083E4A0C`, Android 20 `0x083D4874`, Perfect Cell `0x083E6F9C`, Cell types 22-25 (`0x083E8F68`, `0x083E9440`, `0x083EA484`, `0x083EB80C`) | `s2_boss_ends.txt` | C (bytes), L (sound 60 = the "ding") |
| The relay Jr tables start with `ext 88` and no sound 60: `0x083E9DCC`, `0x083E9E2C`, `0x0889A71C` | `s2_boss_ends.txt` | C |
| `ext 42` (white flash, PSL row) is in the Cell type 24 end (`push 10 ; ext 42` at `rom:0x3EA503`) and the type 25 end (`push 30 ; ext 42` at `rom:0x3EB81B`) only; not in 18's or Semi-Perfect Cell's end record | `s1_index_90_104_42.txt` (30 sites) | C |
| Code path: boss release `@0x0801A82C` calls only the EXP task `@0x0800E4D2` and the event task `@0x0800E39C(enemy, 1)`; the task's run `@0x080109AC` stores the point at `0x03001FD0` and calls the event struct; the runner `@0x080106B2` pushes the scene. No palette op on that path | listings in this study | C |
| The only code-made white pulse found (object vtable `0x08025808`, tick `@0x0801A344` blends to white over 64 frames through `@0x0800BE7A`) is built by a player ability `@0x0801327C` (EP -6, sound 40) and by `@0x080166A2`. Neither is on the death path | listings | C (listings), L (not the boss flash) |
| The normal release `@0x0801A74C` (type 26 today) adds a world remove `@0x080068CA`, an effect object `@0x0800FA1C` with 0x28 at the Jr's centre, and sound 31 or 32 (`rand_n(2) + 0x1F` into `sfx_table`): the Jr "poof" | listing | C |

**Answer.** The boss look = boss descriptor (the enemy stays) + sound 60 + the event scene. The white flash I see is S: it may be the hit flash of the last blow. The plan makes it certain: every Jr end that should look like a boss end runs `ext 46 (60)` and `ext 42 (10)`, the Cell type 24 shape (C precedent).

## Q2. The relay Jrs today, and type 26 with the boss descriptor

| Question | Answer | Label |
|---|---|---|
| Boss bar today? | Full bar, not a slice: Piccolo's seq 31 (trial copy `rom:0x90A308`) and the two relay records end `push 1 ; ext 86 ; push 31 ; ext 85 ; push 0 ; ext 33` | C (bytes, `s2_boss_ends.txt`) |
| Descriptor today | Type 26 `rom:0x6D591C` +0x14 (`rom:0x6D5930`) = `0x086D5654` = `{0x0801A7DF, 0, 0x0801A74D, 0x40}`: normal release, event parameter 0x40 | C (CJR, re-read) |
| Can type 26 switch to the boss descriptor? | Yes, one word: `rom:0x6D5930` `0x086D5654` to `0x086FF3C4`. Only items 8-10 name type 26 in vanilla (CJR); the trial adds item 13 | C |
| Do the relay Jrs stay scannable? | Yes. Scouter entry 20 names type 26, and the matcher `@0x080190D4` compares type entry pointers, not descriptors | C (CJ5 row) |
| What a beaten boss-descriptor Jr does | Stays in the world at HP 0 (no world remove). Descriptor +0 `@0x0801A824` returns state object `0x0300220C` (vtable `0x08023D78`); its tick `@0x08026590` is `mov r0,#0 ; bx lr`, so it never ends: no AI. A later hit does nothing: `@0x0800E48E`-`@0x0800E498` returns before the damage when HP is 0, so the event cannot run twice | C (listings), L (where the +0 node is installed is not traced) |
| What changes for the third Jr (Gohan's table `rom:0x3EA400`) | (1) No poof and no sound 31/32: the Jr stands until the fade. (2) The event starts with parameter 1, not 0x40, so the scene may start sooner (S: the parameter's use is not traced, CJR). (3) Seq 1 then reloads 14,3 (`ext 39`), which clears the beaten Jr (L). (4) Word 0 (`0x0889A71C`, an r27 relocation) gets the sound 60 and flash head in a copy | C (bytes), L/S as marked |
| Bar slice that ends at 1/4 | `ext 90 (31, 25, 100)`: start = 25 x 60 / 100 = 15, width = 60 - 15 = 45. At HP 0 the fill is 15 of 60 = one quarter (HKP formula) | C |

> [!WARNING]
> The slice is display only. The relay Jr still loses all 4990 HP; the bar just shows a quarter left at the end, as Android 18's (11, 50, 100) and Semi-Perfect Cell's (29, 25, 100) do (DID row). Fight lengths do not change: Piccolo 37.1 punches base, Vegeta 29.7, Trunks 53.8 (CJB, level 40 preset).

## Q3. Getting back up: rebuild, not `ext 104`

**Pick: remove and rebuild trial-type items (items 14-16) when the 1 v 3 starts.**

| Evidence | Label |
|---|---|
| The beaten actors do not exist any more. After the third relay Jr, Gohan's seq 1 runs `ext 39 (14,3,1,576,376)` and rebuilds the map (`0x0889A71C`) | C (bytes), L (a reload drops script-made actors) |
| `ext 104 (actor, n)` (`@0x0800AAC6`) removes the actor and builds item n at its spot (CFS). It binds the actor by set, and find-by-set binds the newest set-31 actor (CJ2 row `@0x08006E0A`). The item it builds is also set 31, so a second `ext 104 (31, ...)` would bind the Jr it just built | C |
| The group needs the v5 AI and HP 1550, which only a trial type gives (the AI comes from the type, CJ5). `ext 104` builds whatever type the item names, so it brings no advantage over `ext 84` here | C |
| Precedent for the rebuild: record X already walks NPC Jrs in from the top and swaps them for enemy items with a flash (CJ2, v2-v5) | C |

The "same three get back up" reads in the scene: the 3 group Jrs walk in from the top, as the v5 group does today.

## Q4. The 1 v 1 Jr

| Point | Plan | Label |
|---|---|---|
| Item | Item 13, type word back to **26** (v5 has the trial type 96463 at `rom:0x90A56C`). Standard AI 21, HP 4990, scannable | C (v5 bytes) |
| Bar | `ext 85 (31)` full bar after `ext 84 (13)`; it binds item 13, the newest set-31 actor | C (CJ2 rule) |
| At HP 0 | Type 26 now has the boss descriptor, so the Jr stays, inert, and item 13's event table T1 runs | C/L as Q2 |
| How the script removes it | T1 word 0 (record K1): `ext 46 (60)` ding, `ext 88` bar off, `ext 42 (10)` flash, `ext 46 (31)` the normal death sound, `ext 52 (31)` (the only set-31 actor then). It reads as Gohan destroying it | C (op shapes), S (look) |
| How the 1 v 3 starts | K1 continues: `ext 139 (12500)`, `push 0 ; set var1`, then the v5 walk-in for 3 (`ext 46 (26)`, group of 3 x {`ext 51 (31, x, 248)` ; `ext 53 (31, x, y)`}), `ext 42 (5)`, 3 x `ext 52 (31)`, `ext 84 (14)`, `ext 84 (15)`, `ext 84 (16)`, `ext 43 (5)`, `ext 33 (0)`. No bar. Next index 1 = END, so the fight runs | C (the X shape, CJ2) |

## Q5. The 3 that fly in, and the scripted finish

| Point | Plan | Label |
|---|---|---|
| Fly-in | `set:31` has no anim 12 (also no 3 or 4): its rows are 0, 1, 2, 5, 6, 7, 8 (`s4_sets.txt`). So: spawn each Jr above the view with `ext 51 (31, x, 248)` and glide it down with `ext 136 (31, x, y, 300)` in its stand pose (state 0). `ext 136` keeps the current state while it moves an NPC (VS4: Cell 58 and Vegeta 140) | C (rows, op precedent), S (look: "flying upright") |
| Why not a borrowed fly row for the Jr | `set:31`'s table has 9 rows; row 12 is past it, so a fly row needs a copied, longer set header and a repointed set table entry (8 bytes in the r38+ set table copy) plus a fly frame. No Jr fly frame exists: I would draw it. Size M | C (rows), S (size) |
| Gohan's fly row | `vegeta_ssj_scene` writes `set:160` row 12 = `set:159`'s fly row at `rom:0x88D97C` (VS5) and refuses when that row is already filled (its FlyTests). **Move that 16-byte write into one small shared patch** (for example `gohan_fly_row`) that runs before both trial modules; both modules then check that the row holds `set:159`'s 4 words and refuse if not. Change the VS5 refuse test into a "requires" test | C (VS5 bytes and test), L (plan) |
| Binding order | Every op binds the newest set-31 actor (CJ2). So spawn C (the fly target) first, then B (blast), then A (punch): A is newest and goes first, then B, then C | C (rule) |
| Jr reactions | Hit: `ext 57 (31, 2)` (hurt, anim 2). Knock-back: `ext 121 (31, 2)` + `ext 136 (31, x, y, 600)` (the VS4 Vegeta knock-back). Vanish: `ext 42 (10)`, `ext 46 (31)`, `ext 52 (31)`. **Never** `ext 57 (31, 3)` (knock-down, anim 3) or `ext 121 (31, 12)`: the rows are empty and frame select has no bound (CJ2, BLP) | C (rows, op precedent) |

**The finish, beat by beat (record F, table T word 28).** Frame counts are at 60 frames a second.

| Beat | Ops | Frames | Label |
|---|---|---|---|
| 0. HUD off, camera | `ext 86 (0)`, `ext 31 (x, y, 2)` on Gohan | about 10 | L |
| 1. Three Jrs fly in | `ext 46 (26)` whoosh; group: C, B, A each `ext 51 (31, x, 248)` then `ext 136 (31, x, y, 300)` (about 100 px at 3 px a frame) | about 33 | C (op shapes), L (speed formula, VS4) |
| 2. Punch A (A lands next to Gohan) | group: `ext 57 (0, 7)` Gohan attack, `ext 60 (31)`, `ext 112 (31, 34)`, `ext 95 (31)`, `ext 57 (31, 2)` (the vanilla shape at `0x083EA484`: Gohan Rage attacks Cell with state 7); then `ext 121 (31, 2)` + `ext 136 (31, x+64, y, 600)`; then `ext 42 (10)`, `ext 46 (31)`, `ext 52 (31)` | 16 attack + 32 hurt + 11 knock-back + 10 flash = about 70 | C (precedent), L (state 7 length) |
| 3. Blast B | `ext 55 (0, d)` face B; group: `ext 96 (0, 31, 100)` (player shoots, the 17 table precedent `push 0,28,100 ; ext 96`), `ext 60 (31)`, `ext 112 (31, 34)`, `ext 95 (31)`, `ext 57 (31, 2)`; then flash, sound, `ext 52 (31)` | fire at 16 + flight about 15-25 + 32 + 10 = about 80 | C (fire tick, VS4), L (flight) |
| 4. Fly at C | `ext 121 (0, 12)` + `ext 136 (0, cx-16, cy, 500)` (the v5 Gohan fly-in), lands in state 0 (`@0x08010934`, VS5); then the beat 2 melee group on C, knock-back, flash, sound, `ext 52 (31)` | 7-15 dash + about 70 = about 85 | C (VS5 shape), L |
| 5. Into N | Next index 29 = N (fade, Cell back, "You wretched child", Cell fight), unchanged from v5 | | C |

Total about 280 frames (under 5 s). The ext 96 rule from VS4 holds: `ext 60 (31)` must bind the same actor as the shot's target. Both bind the newest set-31 actor (B), and nothing spawns between them (C, VS4 `@0x08011CB4`).

## Q6. Limits

| Limit | Value | Label |
|---|---|---|
| OBJ VRAM, relay fights | Player 16, ally NPCs, the fighting Jr 16, 1-2 standing beaten Jrs 16-32, HUD 20, bar 8. No text box in the relay tables (`s2_boss_ends.txt`) | L (CJR model) |
| OBJ VRAM, 1 v 1 | Player 16, NPCs 64, NPC Cell 64, HUD 20, bar 8, 1 Jr 16 = 188 of 492 | L |
| OBJ VRAM, 1 v 3 | 16 + 64 + 64 + 20 + 48 = 212 of 492 | L |
| OBJ VRAM, finish | 16 + 64 + 64 + 3 NPC Jrs 48 + shot = about 195; HUD off; no text box until N, and the Jrs are gone by then | L |
| Spawn list | 18 items (0-12 vanilla, 13 the 1 v 1 Jr, 14-16 the group, 17 NPC Cell), as v5. The vanilla maximum is 19 (map 2,1). The fly-in Jrs are `ext 51` NPCs, not items | C (v5 count byte `rom:0x40DA84` = 18) |
| Counter | VM var 1, reset in K1, counts the 3 group deaths. Var 0 is the 14,3 ambient scratch (CJR) | C/L (CJR) |
| EXP | Relay 50,000 each (vanilla `ext 139`). Proposal: 1 v 1 12,500 (K1), group 12,500 each (C), finish 0. Gohan's total stays 50,000, as v5 | C (op), my call |
| Level-up mid-fight | `ext 139` can open the level-up scene while Jrs live (CJT risk). The level 40 preset needs 3,335,510 EXP for the next level | S |

## Q7. The plan

**Step table (what the player sees, and what builds it).** Base sites are vanilla words the module repoints; "new" items live in the expansion.

| # | Player sees | Records and items | Types and bytes | Risk |
|---|---|---|---|---|
| 1 | Spawn scene: 3 Jrs, then 4 more (7) | v4 seq 31 copy `rom:0x90A308`, unchanged except step 2's bar | none | none (played in v4) |
| 2 | Piccolo fights a Jr; the bar ends at 1/4; ding and flash; fade | Seq 31 copy: `ext 85 (31)` becomes `ext 90 (31, 25, 100)` (record grows; next allocations move) | type 26 +0x14 `rom:0x6D5930` = `0x086FF3C4` | Low |
| 3 | Fade in: the beaten Jr stands at the side; Vegeta fights a new Jr, same bar | New record R8 named by `rom:0x3E9E24` (table word 0, was `0x083E9DCC`): `ext 46 (60)`, `ext 42 (10)`, `ext 69 (40)`, then the vanilla body with, after its fade out: `ext 52 (31)` (the beaten Jr), `ext 51 (31, sx, sy)` stand-in, and the vanilla `ext 84 (9)`; `ext 85 (31)` becomes `ext 90 (31, 25, 100)` | stand-in before `ext 84 (9)` so item 9 is the newest | Low; stand-in spot S |
| 4 | Trunks fights the third Jr, same | R9 at `rom:0x3E9E84` word 0 (was `0x083E9E2C`), same shape with `ext 84 (10)` | | Low |
| 5 | Ding and flash on the third Jr, then Gohan's scene as today | R10 at `rom:0x3EA400` word 0 (was `0x0889A71C`, an r27 copy): sound 60 and flash head + the r27 body. The `ext 39` reload clears both stand-ins and the beaten Jr | check `0x0889A71C` before the write | Low |
| 6 | Transform to Super Saiyan 2, as today | vanilla and r27/r39 records | none | none |
| 7 | One Jr comes down from the top; flash; 1 v 1 with a full bar | Record X (`rom:0x3EA478` word 30) rebuilt: Cell swap to item 17, camera, 1 NPC Jr walk-in, flash, `ext 52 (31)`, `ext 84 (13)`, `ext 86 (1)`, `ext 85 (31)` | item 13 +8 = 26 (was 96463); item 13 event struct names new table T1 | Low |
| 8 | Gohan beats it: ding, flash, boom, it is gone; 3 Jrs come down; 1 v 3, no bar | T1 word 0 = K1 (Q4), word 1 = END | items 14-16 +8 = trial type; trial type +4 HP = **1550**; +0x14 stays `0x086D5654` (the module builds it from the `TYPE26` constant, `celljr_fight.py` line 416) | Low |
| 9 | Each group death: EXP; after the third, the finish | T word 0 = C: `inc var1 ; push 12500 ; ext 139 ; ext 1 ; push 3 ; lt ; jz +3 ; push 1 ; end ; push 28 ; end` | T: word 28 = F (+0 = 29), 29 = N (+0 = 30), 30 = "wretched" `0x083EA3B4`, 31 = seq 32 `0x083EA3EC`, 32 = END | Low |
| 10 | Three Jrs fly in; punch, blast, fly-and-strike | F (Q5) | needs the shared `set:160` row 12 | Medium (first scene with the player as a melee and blast attacker on NPC Jrs, L) |
| 11 | Fade, "You wretched child", the Cell fight | N, unchanged | | none |

**New data, by size (S estimate):** R8, R9, R10 (about 120 bytes each, copies with a 12-byte head), seq 31 copy +5 bytes, X (shorter than v5), T1 (2 words) + K1 (about 140 bytes), C (25), F (about 200), the shared fly-row patch (16 bytes), 1 type word changed, 4 item type words, 1 HP word. Base sites: `rom:0x6D5930`, `rom:0x3E9E24`, `rom:0x3E9E84`, `rom:0x3EA400` (new), plus the 5 v5 sites.

**Tests (module `test_celljr_fight`).**

| Test | Checks |
|---|---|
| New: `test_type_26_uses_the_boss_descriptor_and_only_jr_items_name_it` | `rom:0x6D5930` = `0x086FF3C4`; items naming 26 are 8, 9, 10, 13 |
| New: `test_group_type_is_hp_1550_with_the_normal_descriptor` | trial type +4 = 1550, +0x14 = `0x086D5654` |
| New: `test_every_jr_end_has_sound_60_and_a_flash` | R8, R9, R10, K1 start with `ext 46 (60)` and hold `ext 42` |
| New: `test_relay_bars_end_at_a_quarter` | seq 31 copy, R8, R9 run `ext 90 (31, 25, 100)` and no `ext 85 (31)` |
| New: `test_stand_in_spawns_before_the_next_jr` | in R8 and R9, `ext 52 (31)` < `ext 51 (31, ...)` < `ext 84 (n)` |
| New: `test_finish_removes_newest_first` | F spawn order C, B, A; remove order A, B, C; `ext 96` and its `ext 60` bind with no spawn between |
| New: `test_counter_ends_two_kills_and_finishes_on_the_third` | stack model: deaths 1-2 leave 1, death 3 leaves 28 |
| Extend: `test_no_record_flies_set_31` | also no `ext 57 (31, 3)`, `(31, 4)`, `ext 121 (31, 12)` |
| New (shared patch): `test_set_160_row_12_is_set_159s_fly_row` | 16 bytes at `rom:0x88D97C` |
| Update | `test_ai_21_type_26_and_the_node_block_are_unchanged` (type 26 +0x14 now changes), `test_ally_fights_keep_their_bytes` (tables word 0 repointed), `test_the_4_fight_jrs_use_the_trial_type...` (3 plus item 13), the v5 counter test, VS5 FlyTests "refuses a filled row" (becomes "requires the row") |
| Diff proof | 0 bytes outside the named sites; the main `--list` stays r39 `aa51dc16...` |

**Expected punch counts (Rage Gohan, level 40 preset, mean punch 297, `design_numbers.txt`).**

| Fight | Punches |
|---|---|
| Relay: Piccolo / Vegeta / Trunks (base) | 37.1 / 29.7 / 53.8, unchanged (CJB) |
| 1 v 1 (type 26, HP 4990) | 16.8 |
| 1 v 3 (HP 1500 / 1550 / 1600) | 5.1 / 5.2 / 5.4 a Jr; 15.2 / 15.7 / 16.2 in all |
| Cell type 24 after | 26.4 |

The Jr punch on Gohan stays 28-30 (28 punches to KO him) in every Gohan fight (C model).

**What I check in play.**
1. Each relay Jr: the bar stops at one quarter, then a ding and a white flash, then the fade. Report whether the flash looks like 18's end.
2. After each fade-in, the beaten Jr stands at the side and does not move or fight.
3. The third relay Jr: the ding and flash, then Gohan's scene as today, with no Jr left after the cut.
4. The 1 v 1 Jr fights like the relay Jrs (no wait after punches) and has a full bar.
5. Its end: ding, flash, boom, gone; then 3 Jrs come down; the 1 v 3 has no bar and the Jrs pause after each punch.
6. The finish: 3 Jrs glide down upright; Gohan punches one away, blasts one, flies at the third. Report any broken frame, a Jr that does not vanish, or a freeze (a freeze after the blast means `ext 60` waits on the wrong Jr).
7. Select during each fight: relay and 1 v 1 Jrs scan as "Cell Junior"; the group does not (as v5).

---

# Part 2: checks and plans for the other asks

## 8. Vegeta-only Android 18

There is a flight pad, and the game already has a leader gate on the same map. A clean hard block exists.

**What the game does (C unless marked).**

| Fact | Evidence |
|---|---|
| The flight pad is map 8,48 (entry 250) region 0: condition `0x0002007F` (flag 127 clear, L by the `0x000200C9` shape, CSV), item `rom:0x403218` = script item (factory `0x0800C2C3`, trigger `0x0800D839`, rect (513,105)-(560,144), script `0x084031F4`) | `s3_map.py` output; list `rom:0x403294`, item word `rom:0x403298` |
| Its script: `push 26 ; ext 46 ; push 0,536,-32 ; ext 54 ; push 8,49,1,208,792 ; ext 38 ; push 0,208,712 ; ext 54 ; end`: fly up, warp to 8,49, fly in | bytes at `rom:0x4031F4` |
| Map 8,49 region 0 (always): scene item, step trigger `0x0800D765`, rect (-15,577)-(416,760), table `rom:0x3D8B60`: the 17, 18, 16 car talk; seq 24 `0x083D8B38` builds 18 with `ext 84 (0)` and `ext 90 (11, 50, 100)` | `s2_18_tables.txt` |
| The same map 8,48 already has a leader gate: region 3, condition script `rom:0x403254` = `push 136 ; flag ; leader ; push 3 ; ne ; and ; push 140 ; notflag ; and`, table `rom:0x3D8654` = sound 28 + "Only Trunks is allowed to pass through this barrier." The Cell Games has "Only Goku is allowed to pass through this barrier." (`rom:0x3E8084`, condition `rom:0x408D30` = leader != 4) | bytes |
| The level gates in the guides ("Lv. 30 Character Gate") are break objects whose condition tests the leader and `level(n) > N-1` (bible row: 14,1 break object `@0x08408DD4` = leader 4, level(4) > 39) | CGS row (C) |
| The 18 tables expect Vegeta: death table seq 3 `call leader ; push 2 ; eq ; call 126 ; and` then `ext 57 (0, 36)` (revert); seq 24/26/28 place Vegeta, Piccolo or Gohan by the leader; text "He is very ashamed of his defeat" | `event_tables.txt` (DID), C bytes; L (ext 126 meaning) |
| After the fight the game resets the party: seq 48 `0x083D9864` sets flag 127, `ext 70 (1)` (Piccolo leads), `ext 81 (0)`, `ext 81 (2)`. So Gohan and Vegeta were selectable during the fight | C (bytes), L (selectable before) |

**Options.**

| Option | How | Bytes | Risk |
|---|---|---|---|
| **(a) The pad refuses unless Vegeta leads (recommended)** | Region 0's item word `rom:0x403298` names a new scene item (factory `0x0800D7E1`, the same trigger `0x0800D839` and rect; the 6,4 door uses this pair, CSV). Its table P: word 0 `call leader ; push 2 ; eq ; jz +3 ; push 3 ; end ; push 28 ; ext 46 ; end` (+0 = 1); word 1 the line, for example "Only Vegeta can face Android 18." (my text); word 2 END; word 3 the vanilla flight ops in a scene record (`ext 38` in a scene is vanilla: Tien's win table `rom:0x3D2FE0`); word 4 END | 1 base word, about 80 new bytes, 1 line | Low. The leader test runs when the player presses, so a switch at the save point works at once (C by construction). The player must switch to Vegeta (L: the save point and Switch Characters are on the pad screen per guide 1 lines 686-690) |
| (b) The pad makes Vegeta the leader | Copy script `0x084031F4` with `push 2 ; ext 70` after the fly-up and before `ext 38`; repoint the item +0x10 word `rom:0x403228` | 1 base word, about 30 bytes | Low-medium. `ext 70` runs `set_leader` and `appearance_revert` (RCD, FCD rows), so the old leader's form drops; Vegeta may be under-levelled. The 18 table's seq 48 sets the leader back to Piccolo anyway (C) |
| (c) Leave as is | none | 0 | none |

**Recommendation: (a).** It is the game's own barrier shape on the same map, it changes no party state, and the player picks the moment. (b) is the fallback if I want no extra step. Size S for either.

## 9. Senzu Bean to Cell

My rule was "if there are frames and animations to go". Goku's frames are there; a bean in flight and a Cell eating pose are not.

| Point | Finding | Label |
|---|---|---|
| Where | Goku's give-up table `rom:0x3E93E8`: seq 19 "Okay. I'll do it.", seq 20 "Wonderful. Let's get started!", seq 21 (r27 copy) fades, reloads, builds Cell type 23 at full HP with `ext 84 (5)` and sets flag 192. Goku leads here (his lines use the leader portrait id 1; seq 21 runs `ext 70 (0)`) | C (bytes `s2_giveup.txt`) |
| Goku poses | `set:61` (Super Saiyan Goku) anim 5 (3 frames, arm straight out, the ki blast pose) and anim 4 (4 frames, arms up) exist (`s4_sets.txt`, `goku61.png`). Anim 5 reads as a hand-out or toss | C (rows), L (look) |
| A bean sprite | The Senzu item (item 0, `rom:0x6ADE24`) has a 16x16 world icon at `rom:0x6D0640` and a menu icon at `rom:0x6CF054` (frame headers, they decode). These are pickup and menu icons, not a sprite set; `ext 51` spawns by set id, so no scene op can throw one | C (bytes), L (no op) |
| A ki ball as the bean | `ext 96 (0, 30, n)` would show the toss pose and a flying shot, but the shot is a ki ball and Cell would take a hit | C (op), my call |
| Cell eats | `set:30` has no anim 4 (arms up) or 9 (power up); rows 0-3, 5-8, 12, 18 (`s4_sets.txt`). State 30 plays anim 18 and never ends (PGS), so it must not be used | C |
| Dialogue (episode 181) | Kanzenshuu's episode 181 page: Goku asks Kuririn (Krillin) for a senzu, throws it to Cell, says he is playing fair because Cell is tired; Cell says Goku will regret it, eats it and returns to full strength. The page quotes no lines | L (web source, `https://www.kanzenshuu.com/wiki/Dragon_Ball_Z_Episode_181`) |

**Recommendation: leave as is**, per my rule. If I want a light version: a scene record between seq 19 and seq 20 with 3-4 of my lines (Goku asks Krillin, Krillin hands it over, Goku tosses it, Cell's reply), Goku in anim 5 by a short pose op, a flash on Cell. No bean on screen. Size S (a table copy, about 5 records).

## 10. Three-year training

**Where it fits (C).** The prologue ends in table `rom:0x3BFDDC` seq 87 "Yeah dad, let's head home." and seq 88 (`0x083BFDB4`: fade, SET flags 26, 24, 27, warp to 2,1). "Three years later..." is table `rom:0x3B88A0` (named by `rom:0x3EDD64`) at Goku's house: seq 6 "GOHAN: So we have three years to train, dad?", seq 7 "That's right - and we better make them count.", seq 8 `0x083B8566` (fade out 240, SET flag 68, HP and EP refills, `ext 73 (0, 53)`, level +1 for Gohan and Piccolo, `ext 39 (2,1,2,592,584)` reload, place Goku 60 and Piccolo 103 or Gohan 53 by the leader, fade in), seq 9 "Three years later...". The party then is Gohan and Piccolo (seq 8 branches on leader 0 or not) (C bytes, `s2_prologue.txt`).

**Best insertion point:** between seq 7 and seq 8 of `rom:0x3B88A0`. My "after the flag 26 fade" holds: flag 26 is set long before.

**How opponents work.**

| Opponent | How | Label |
|---|---|---|
| Goku | `chamber_spar` (r37): enemy type 95 = Goku (HP 3500, AI 98, 34/36/34, `set:60`), built with `ext 104 (60, 7)` in NPC Goku's place, bar `ext 85 (60)`, a win event table, no flag (`chamber_spar.py`) | C |
| Piccolo | The same shape: a trial type entry in the expansion (types 95-97 are taken; the u32 index works, CJ5) with AI 98. AI 98 sets use anims {0-6, 12} (CFS row); `set:103` has 0-9, 11-14, 16-20, 22 (`s4_sets.txt`), so it covers them. No scouter entry (dream Frieza precedent) | C (rows), L (AI 98 on 103 in play) |
| Vegeta as the player | Party and leader ops exist: `ext 79 (2)` party add, `ext 70 (2)` leader, later `ext 70 (0)` and `ext 91 (2)` party remove (precedent record `0x083CCA2E`: `ext 79 (2) ; ext 79 (1) ; ext 70 (2)`; `ext 91 (3)` at `rom:0x3B7ABA`). Vegeta's level is set to 18 later by the space scene (`ext 98 (2, 18)` in `rom:0x3D21F0` seq 3), so the spar needs its own `ext 98 (2, n)` | C (ops), L (party state) |
| Vegeta's sparring targets | (1) The LoG II training room 6,70 already hosts spars (Yamcha, Krillin, Tien; plus `chamber_spar`'s Goku) (CPR rows). (2) Destroyer robots (`set:37`-`39`, types 31-33, scouter entries 25-27) read as "training machines". Final call | C (data), my call |

**Buu's Fury gravity chamber (timeboxed).** The BF guide places it in chapter 3 at Capsule Corporation: "In the Gravity Chamber, Trunks and Vegeta are training ... you'll have to hit Vegeta" (guide lines 526-536). BF story text is not plain ASCII (0 hits for "ravity", `s5_bf_text.py`). A scan of plain BF map loads finds 42; the nearest to the chapter 3 card (`rom:0x780C6F`, CH rows) is `ext 115 (0, 51, 1, 0, 0)` at `rom:0x781033`; BF map entry 20 (`rom:0x8E740`, (0,51)) has 6 regions (`0x08073AC8`), no spawns, layout `0x080739A4` (`s8_bf_maploads.txt`). That this is the chamber is **S**. Its tiles, palette and any training targets were not studied: they follow once my save in BF confirms the map, and they are part of the port. Porting a BF map is size **L** (tiles, palette, layout, collision; the beam struggle port is the size reference, BM rows).

**Scene order (proposal) and work size.**

| # | Scene | How | Size |
|---|---|---|---|
| 1 | Seq 6-7 lines at the house, as today | vanilla | none |
| 2 | Fade; Gohan spars Piccolo | New table T3 (a copy of `rom:0x3B88A0` whose word 7 names a "go train" record). That record reloads a field map with `ext 39` (in-scene reload, as Gohan's seq 1 does on 14,3), places NPC Piccolo, 2 lines, `ext 84` of a new cond-1 enemy item in that map's copied spawn list, bar, END. No flag or region is needed | M |
| 3 | Gohan spars Goku | Piccolo's death table: 2 lines, `ext 84` the Goku item (type 95 or a copy), bar | S |
| 4 | Vegeta in the gravity room | Goku's death table: fade, `ext 79 (2)`, `ext 70 (2)`, `ext 98 (2, n)`, reload 6,70 (or a BF port), robots by `ext 84`, a group counter like the Jr counter C | M (6,70) or L (BF port) |
| 5 | "Three years later..." | The last death table: `ext 70 (0)`, `ext 91 (2)`, then a table whose words 7-23 equal `rom:0x3B88A0`'s, so vanilla seq 8 onward runs unchanged (each record's +0 index fits, the CJT reuse rule) | S |

Total M-L. Risks: the party ops mid-scene (L), Gohan's look (child set before `ext 73 (0, 53)`) and Vegeta's level at that point (L). Recommend 6,70 for the Vegeta part first; the BF chamber later, after my state in BF confirms the map.

## 11. Vegeta's first Super Saiyan at Android 19

| Point | Finding | Label |
|---|---|---|
| The line | "So, does a machine like yourself ever experience fear?" = table `rom:0x3D40C8` (named by `rom:0x3FD4F4`) word 40, seq 41 `0x083D4076` | C (`s7_text_find.txt`) |
| How the fight starts | Word 41, seq 42 `0x083D40B2`: `push 1 ; ext 86 ; push 12,2 ; ext 104 ; push 12 ; ext 85 ; push 0 ; ext 33 ; end`; word 42 END | C |
| Is Vegeta forced? | Yes. Record `0x083CCA2E` runs `ext 79 (2)`, `ext 79 (1)`, `ext 73 (0, 53)`, **`ext 70 (2)`**, `ext 80 (2)`, **`ext 81 (1)`, `ext 81 (0)`**: Vegeta leads and Gohan and Piccolo cannot be picked. The next `ext 80 (1)` / `(0)` site found is `rom:0x3D4826` in table `rom:0x3D486C` (after 19). The 19 table also speaks as Vegeta ("VEGETA: Nobody kills Kakarot...", seq 30) | C (bytes), L (no other re-enable between; the guides agree) |
| So: the leader is not Vegeta? | Cannot happen in vanilla flow | C/L as above |
| Does the game already show his first transformation? | Yes, earlier: table `rom:0x3D21F0` (Vegeta in space): seq 7 `ext 82 (2)`, `ext 83 (2, 1)`, `push 0,35 ; ext 57`; seq 8 "Yes! I've finally done it! I'm finally a Super Saiyan!"; seq 12 the form tutorial; seq 14 revert `ext 57 (0, 36)`, SET flag 77 | C |
| Plan | Copy seq 42 with a head: `push 0,35 ; ext 57` (the space scene's transform, C precedent `rom:0x3D1FD2`), then the vanilla 4 ops. Repoint word 41 `rom:0x3D416C`. State 35 calls `transform(player, 1)` at frame 0xA0 (HKP row), so the form is the normal playable Super Saiyan: it drains ki, the player can drop it with B | C (precedent), L (in play) |
| Size | S: one record (about 20 bytes), one base word | |

The `vegeta_ssj_scene` NPC set swap is not the model here: that swap is for an NPC. The player needs the real form state.

## 12. Trunks tests Goku

| Point | Finding | Label |
|---|---|---|
| The scene | Prologue table `rom:0x3BFDDC` (named by `rom:0x3F1E80`): seq 37 "TRUNKS: Goku, can I have a word with you?", seq 38 walks Trunks (`set:128`) to (592,232) and Goku (`set:62`) to (568,256); seq 39-78 the private talk; seq 79 they return; seq 88 ends with flag 26 | C (`s2_prologue.txt`) |
| Trunks Super Saiyan | `set:128` to `set:134` by the vanilla NPC transform (power-up `ext 57 (128, 9)`, remove, spawn 134; the revert uses anim 21, `rom:0x3BE134` / `rom:0x3BE5E9`, VS rows) | C |
| Trunks' sword attack | `set:128` and `set:134` anim 16: 7 frames, a jump and overhead sword slash; anim 18: 7 frames, a horizontal slash (`trunks.png`, `goku62_trunks134.png`). `ext 57 (134, 16)` plays anim 16 for 0x38 frames (PGS row) | C (rows), L (look) |
| Goku Super Saiyan here | **No art.** Goku wears the Yardrat outfit, `set:62`, which has only anims 0, 1, 4, 12. Sets 63, 64, 135, 136 are not a Yardrat Super Saiyan. `set:61` is Super Saiyan Goku in the orange gi | C (rows) |
| A pose for the finger block | `set:62` anim 4 (4 frames: one arm raised; the game uses it as Goku's surprise gesture, `ext 57 (62, 4)` in seq 46, 63, 73) | C (rows, uses), S (reads as a finger block) |
| Flash | `ext 42 (10)` at the clash, the Cell type 24 shape | C |

**Beats (inserted after seq 40 "you have my word", before seq 42 "My name is Trunks").** Insert with the CJT rule: copy the table (92 + about 10 words), let word 40's copy jump to the new words at 92+, and let the last new record's +0 return to 41. One base word (`rom:0x3F1E80`).

| Beat | Ops | Line slot (my text) |
|---|---|---|
| 1 | Trunks faces Goku | Trunks asks Goku to turn Super Saiyan |
| 2 | Goku: power-up stand-in (anim 4) and a flash; see the Goku question below | Goku agrees |
| 3 | Trunks transforms 128 to 134 (vanilla NPC shape) | Trunks says he will attack with his sword |
| 4 | Group: `ext 57 (134, 16)` slash; Goku `ext 57 (62, 4)` raised arm; `ext 42 (10)` flash and a hit sound at the clash frame | (none) |
| 5 | Hold, then Trunks reverts (134 to 128, anim 21) | Trunks: impressed; Goku: he knew Trunks would stop |
| 6 | Return to seq 42 | |

Size M (table copy, about 10 records, 4-6 lines). Goku stays in base form unless I pick an option below.

---

## Open questions for me

1. **1 v 3 HP:** 1500, 1550 or 1600? The plan uses 1550 (15.7 punches for the group).
2. **Beaten relay Jrs:** stand at the side after each fight (16 OBJ units each, no text in those scenes), or vanish behind the fade? The plan stands them at the side.
3. **EXP:** keep 50,000 for Gohan (1 v 1 12,500, group 12,500 each, finish 0)?
4. **1 v 1 end:** the Jr explodes (flash, boom, gone), so Gohan kills only after Super Saiyan 2, as in canon. Keep?
5. **Fly-in look:** the 3 finish Jrs glide down upright (no fly frame). Or would you draw a Jr fly frame (size M)?
6. **Android 18:** option (a) refuse with a line (recommended), (b) switch to Vegeta, or (c) leave? If (a), the line text.
7. **Senzu:** leave as is, or the text-only beat with your episode 181 lines?
8. **Training:** start with Piccolo and Goku spars plus Vegeta on map 6,70 (M), and the BF gravity chamber later (L)? Vegeta vs robots or vs the vanilla partners?
9. **Vegeta at 19:** the space scene (flag 77) already shows his first Super Saiyan. Keep it as is, or cut its transform so 19 is the reveal?
10. **Trunks and Goku:** Goku has no Super Saiyan art in the Yardrat outfit. Pick: base Goku blocks (no new art), swap to the orange gi Super Saiyan set 61 for the test (outfit jump), or you draw a Yardrat Super Saiyan head (art). Then send the dialogue.

## Files

All in `scripts\one-time\2026-10-30-celljr-rework-plan\` unless noted.

| File | What |
|---|---|
| `s1_index.py`, `s1_index_90_104_42.txt`, `s1_index_party.txt`, `s1_index_27.txt` | Every reachable ext call by number (shape A) with B-pair counts |
| `s2_tables.py`, `s2_boss_ends.txt`, `s2_18_tables.txt`, `s2_giveup.txt`, `s2_prologue.txt`, `s2_vegeta19.txt` | Scene table decodes |
| `s3_map.py` | Map region and spawn lists (8,47-8,50, 14,1) |
| `s4_sets.py`, `s4_sets.txt` | Anim rows per set; sheets in `scratch\review-renders\2026-10-30-celljr-plan\` (`goku61.png`, `trunks.png`, `goku62_trunks134.png`) |
| `s5_bf_text.py` | BF ASCII search (0 hits) |
| `s6_senzu_icon.py` | Senzu icon decode (`senzu_icons.png`; the tile order of the render is not right, the colours are) |
| `s7_text_find.py`, `s7_text_find.txt` | Text record search through table words |
| `s8_bf_maploads.py`, `s8_bf_maploads.txt` | BF plain map loads |
| `bible_rows.md` | CJP rows |

Housekeeping: one read-only check (BOM and dash scan of this report and the rows file) started with `cd`; every path in it was absolute and no write depended on it. No call used `Push-Location`. The 4 renders went to `scratch\review-renders\2026-10-30-celljr-plan\`, outside the brief's write allowance; they are review aids only and can be deleted. Nothing was written under `data\`, `builds\`, `docs\RE-BIBLE.md` or `docs\ledger\`. No module, list or test changed. The test suite was not run (no code changed).
