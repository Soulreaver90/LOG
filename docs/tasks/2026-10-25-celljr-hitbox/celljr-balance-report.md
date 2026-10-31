# Cell Jr group fight balance: study report

Date: 2026-10-25. Brief: `docs\tasks\2026-10-25-celljr-hitbox\celljr-balance-study.md`. Study only: no patch, no build, no build-list change, `docs\RE-BIBLE.md` not edited. Labels: **C** = CONFIRMED (address or bytes quoted), **L** = LIKELY, **S** = SPECULATIVE.

| SHIPPED | Where |
|---|---|
| Why the Jrs behind the front Jr land punches, with addresses | "Crowding" |
| How many of 4 Jrs land at once, by a model of the mover, the occupancy grid and the guard | "Crowding", `crowd_model.txt`, `crowd_*.png` |
| Vanilla spacing and "wait your turn" search, two shapes | "Vanilla precedent" |
| Type 26 stats, both-way damage, hit counts, relay and group comparisons | "Stats and damage", `damage_model.txt` |
| Trial-only options with bytes, effect and risk, and one recommendation | "Options", "Recommendation" |
| Emulator steps | "Emulator steps" |
| Bible rows, tag `CJB` | `scripts\one-time\2026-10-25-celljr-balance\bible_rows.md` |

| PENDING | Why |
|---|---|
| Does a Jr in row 25 re-check the guard every frame (it stops at the first spot that lands), or walk onto Gohan? | The behaviour-tree return rule is not traced. The model gives both answers (STOP, CREEP); both give 4 of 4 in reach. Emulator step 5 |
| Frames between Gohan's hurt end and the next damaging hit | Needs a frame log in the fight. The `lock_model.py` numbers are S. Emulator step 4 |
| Rage HP regeneration running in this fight | Code is unchanged in v3 (C). It is not seen in a state yet. Emulator step 1 |
| AI 45 row 48 leaf `0x0801CCA9` and AI 52 row 55 leaf `0x0801CF73` | Not traced. They matter only for the punch-only option |

Housekeeping: test suite run once, `Ran 832 tests ... OK` (`scripts\one-time\2026-10-25-celljr-balance\suite.txt`), with absolute `-s` and `-t` paths. One Bash call started with `cd /dev/null`, which failed, so the directory did not change; no other call used `cd` or `Push-Location`. Script folder: `scripts\one-time\2026-10-25-celljr-balance\`.

---

## Short answer

- **Crowding is the main cause.** Enemies keep apart from each other only on an 8 x 8 cell grid. Gohan is not on that grid, so all 4 Jrs walk straight in to him from 4 sides (C). The punch guard tests only "my punch rect overlaps Gohan" (C). In the model, all 4 Jrs are in punch reach at once from the trial spots, and 3 or 4 are in reach in 98-99 % of random starts (C model, L in play).
- **The lock makes it worse.** Gohan's 32-frame hurt state blocks further damage, but nothing protects him after it ends (C, BLK). With 4 Jrs in reach, the next Jr punch lands a few frames after each hurt ends (S toy model: median gap 4 frames).
- **Stats.** A Jr has 4990 HP: Rage Gohan needs about 17 punches for each Jr, 67 for the group (C model). A Jr punch does only 28-30 to Rage Gohan, and Rage regenerates 27 HP a second (C code, L in play). So the stats make the fight long. They do not make it deadly by themselves.
- **Vanilla precedent.** No vanilla enemy waits its turn (C two shapes, L absence). But the common group-fight AIs (AI 8, 45, 52) wait 30 frames after every punch. AI 21, the Jr AI, chains its punches with no wait (C).
- **Recommendation:** a trial-only type and an AI 21 copy. The type has HP 3750 (was 4990) and POW 44 (was 50), with STR and END unchanged. The AI copy adds a 30-frame wait after each punch and halves the blast roll. Keep the 4 Jrs. The wait's effect on the lock is S until an emulator run. If the lock remains, split the 4 into 2 brawlers and 2 shooters (option J): a hard cap of 2 in melee with 4 still on screen. Details in "Recommendation".

---

## Crowding

This section explains why the Jrs behind the front Jr can punch Gohan.

### How a Jr picks its spot

| Rule | Evidence | Label |
|---|---|---|
| The approach mover walks toward **Gohan's footprint centre**. It stops when max(abs dx, abs dy) < 3 px | tick `@0x0801B17C` (B333 node, factory `@0x0801B332` builds `{vtable 0x08023BE0, speed}`); `cmp r6,#0x3` at `@0x0801B222` | C |
| A step is speed / 256 px on the larger axis. AI 21 speeds: row 22 0x133, row 24 0x80 (beyond 56 px), row 25 0x100 (within 64 px) | `@0x0801B27E`-`@0x0801B2AE` (divide `@0x08021F30` = r1 / r0, as the HUD call `@0x08008C80` shows); node bytes in `ai_tree.txt` | C |
| On a blocked step it slides: full step, then x only, then y only | three `bl 0x800e45e` at `@0x0801B2D4`, `@0x0801B2F8`, `@0x0801B316` | C |
| Nothing else chooses a spot: no "surround" or "flank" node exists in rows 21-28 | `ai_tree.txt` | C |

### Spacing between enemies

| Rule | Evidence | Label |
|---|---|---|
| View +0x74 is an **occupancy grid**: the map collision bitmap +0x6C with every enemy footprint stamped closed, 1 bit per 8 x 8 cell | stamp `@0x080063E0`; test `@0x08005D6C`; states `log2_poc_r39_celljr.ss1`/`.ss2`: +0x74 differs from +0x6C only at the enemy Cell's 3-4 cells (`occupancy.py`) | C |
| A moving enemy unstamps itself, tests the new cells, then stamps again. So **enemies never share a cell with each other**. They stack every 8 px vertically (16 x 8 footprint) and every 16 px across | `@0x0800E310` (1) at `@0x0801B26E`, test `@0x0800E45E`, `@0x0800E310` (0) at `@0x0801B32A`; generic step `@0x0801A8B0` and knockback use the same shape | C |
| **Gohan is not on the grid.** No player code stamps it, and his move tests read +0x6C only. Jrs can stand on his cells, and he walks through them | BL scan of `@0x080063E0` (47 sites, none in the player code); `move_test_b` `@0x08006380` `ldr r1,[r0,#0x6c]`; his cells are open in both states | C |
| No push-apart, no attacker cap, no turn token | see "Vanilla precedent" | C (shapes), L (absence) |

### The punch guard

`@0x0801BEB8` reads the player pointer `[@0x03001FA8]` and the Jr itself, and nothing else (C, listing):
- It requires player +0x168 != 0 (`@0x0801BEC6`-`@0x0801BECE`). The hurt enter `@0x0800831C` writes only +0x163 and +0x164 (`strb r0,[r4,#0x4] ; strb r0,[r4,#0x3]`, r4 = player +0x160), and the leave `@0x08008330` sets them back to 0x80. Nothing in the hurt state writes +0x168, so a Jr also swings, for 0 damage, at a hurt Gohan (C).
- It pre-tests the envelope (E.x0-4, E.y0, E.x1+3, E.y1-6) against Gohan's hurtbox (`@0x0801BF06`-`@0x0801BF26`) (C).
- It then builds the same rect as the punch `@0x0801BD2C` (facing from the box centres) and tests it (`@0x0801BFA6`-`@0x0801BFBE`) (C).
- No other enemy is tested. No line-of-sight test exists (C).

A vertical punch rect covers the Jr's own body, so its reach is 19-21 px (CJH). A Jr above or below Gohan therefore lands from 2 or 3 ranks deep. A side punch reaches only 6-7 px, so only the front Jr in a row lands (C model, `stack_lines.txt`):

| Line of Jrs (offset from Gohan's anchor) | Jr guard passes | One Gohan punch hits (broadcast) |
|---|---|---|
| Column above: (0,-8) (0,-16) (0,-24) (0,-32) | Y Y Y n | Y Y Y Y |
| Column below: (0,8) (0,16) (0,24) (0,32) | Y Y Y n | Y Y Y Y |
| Row to the right: (16,0) (32,0) (48,0) | Y n n | Y n n |
| Right, second rank 8 px down: (16,0) (24,8) (32,16) | Y n n | Y Y n |

Gohan's punch goes through `world_broadcast` `@0x08006DA6`, which calls every actor and ORs the results with no early stop. So one Gohan punch hits every Jr in its rect (C). The knockback tick uses the same occupancy test (BL `@0x0801AC6E`-`@0x0801ACA4`), so a struck Jr with another Jr behind it stops early and can stay in reach (C code, L in play).

### How many land at once

`crowd_model.py` ports the mover, the grid and the guard. Gohan (`set:160`) stands at (576,376). The Jrs start from the v3 item 13-16 spots read from the ROM: (528,344), (528,408), (624,344), (624,424). Two policies cover the untraced row 25 rule: **STOP** (a Jr stops on the first frame it can land) and **CREEP** (it keeps walking in).

| Case | Jrs whose guard passes at rest | One Gohan punch hits | Label |
|---|---|---|---|
| v3 spots, STOP, any Gohan facing | **4 of 4**, at the 4 diagonals 20-23 px out, settled in 77-79 frames | 0 (facing up or down) or 2 (left or right) | C model, L play |
| v3 spots, CREEP, any facing | **4 of 4**, packed on Gohan at (-8,0) (0,8) (8,0) (16,8) | 1-4 | C model, L play |
| 300 random starts 60-88 px out, STOP | 4: 238, 3: 59, 2: 3 | best facing: 1-4 | C model |
| 300 random starts, CREEP | 4: 219, 3: 75, 2: 6 | best facing: mostly 4 | C model |
| Upper bound around Gohan | 13-15 cell-disjoint Jr spots pass the guard | | C model |

Renders: `crowd_stop_v3.png` and `crowd_creep_v3.png` (4x zoom, Gohan facing right). Green = Gohan's hurtbox, orange = his punch, blue = Jr footprint and its 8 x 8 cells, red = Jr punch rect whose guard passes.

### Why it feels unfair: the lock

| Fact | Evidence | Label |
|---|---|---|
| Gohan's hurt state lasts 32 frames and sets his damage factors to 0 | BLK rows, hurt enter `@0x0800831C` | C |
| A 0-damage hit does nothing: no new hurt, no knockback | `@0x08008806` returns when hit +0x18 = 0 | C |
| Nothing protects Gohan after the hurt state ends | hurt leave `@0x08008330` sets the factors back to 0x80 (BLK); CJR risk row "no invulnerability after it" | C |
| The hurt push is about 24 px away from the attacker, and Jrs do not block him, so it can push him into another Jr's reach | BLK hurt move; grid row above | C, L |
| With k Jrs in reach the next hit comes soon after each hurt ends. Toy model: k = 1: median gap 17 frames; k = 4: median gap **4 frames**, 1.58 damaging hits a second | `lock_model.txt` (inputs assumed) | S |

---

## Vanilla precedent

This section lists what vanilla does for spacing and for "wait your turn".

| Behaviour | Where | Label |
|---|---|---|
| **Spacing:** the 8 x 8 occupancy grid. It applies to every enemy, so vanilla groups also surround the player | grid rows above | C |
| **Post-punch wait:** AI 8 row 10, AI 45 row 51 and AI 52 row 58 run `PUNCH ; wait 30 frames ; push row` with the shared wait node `0x086D1FC4` = `{0x0801BBAD, 0, 0, 0x1E}`. AI 59 row 65 waits 16 (`0x086D20E8`). These three AIs drive 234 of the 487 enemy records on the 75 maps with 4 or more enemies | `punch_waits.txt`, `group_fights.txt` | C |
| **AI 21 has no wait:** row 26 is `PUNCH` then 25 % punch again, 25 % row 28, else row 27 (only row 27 has a 10-frame wait, inside 40 px) | `ai_tree.txt` row 26 `0x086D2630` | C |
| **Engage gate:** the roots of AI 8, 11, 45, 66, 74, 106 (wake node `0x0801D749`, 72-80 px) and AI 52 (DIST 60 px) send a far enemy to the idle node `0x086FF3E0`. AI 21's root sends a far Jr to row 22, which still approaches at 0x133 beyond 120 px. So vanilla groups wake one by one as the player comes near; the Jrs never idle. The v3 spots (58-68 px out) are inside those radii, so this is precedent, not a fix | `ai_tree.txt` rows 8, 45, 52, 66, 74, 106 | C (bytes), L (`0x086FF3E0` = idle, not traced) |
| **No attacker cap or turn token.** Shape 1: no literal in the AI code `@0x0801A600`-`@0x0801EC00` names the world object or its holders (`0x0840DAF4`, `0x0840DB00`, `0x03001120`). Shape 2: from that range, 0 BL calls go to `world_query` and 0 to find-by-set. Of 4 calls to `world_broadcast`, 3 send hit message 0 (`@0x0801CA12`, `@0x0801CE86`, `@0x0801E3EE`). One sends message 0x16 (`@0x0801A6AA`), which only draws a string (handler `@0x0801A62A`) | `blscan.py`, listings | C (shapes), L (a read through the enemy object would not show) |
| AI 21 is used by no vanilla group of 4 or more (only 14,3 with 3 Jrs, one at a time) | `group_fights.txt`, CJR row | C |

---

## Stats and damage

This section gives the numbers both ways. Damage is an exact port of `@0x0800F910` (`damage_model.py`). The port uses `rand16` `@0x0802142E`, `rand_n` `@0x0802141C`, move table `@0x086DB2CC` (punch id 2 `{0, 0x400}` shared by Gohan `@0x08007E02` and the Jr `@0x0801BE16`; ki blast id 3 `{1, 0x400}` `@0x0800E9E8`) and mult 0x400 in all three (C). Both apply-hit paths subtract hit +0x18 (enemy `@0x0800E4A4`, player `@0x080087AE`) (C).

| Actor | HP | STR / POW / END | Factors | Source | Label |
|---|---|---|---|---|---|
| Cell Jr, type 26 | 4990 | 46 / 50 / 46 | 0x80 / 0x80 | `rom:0x6D591C` (`00000000 7e130000 15000000 2e322e 8080 000000 54566d08`); enemy +0x160..+0x164 copied from type +0xC..+0x10 at `@0x0800F7F2`-`@0x0800F806` | C |
| Type 26 EXP | 0 | | | +0 = 0; the trial gives 12,500 a Jr by script (CJT) | C |
| Rage Gohan (trial) | 906 | 90 / 78 / 91 | 0x80 / 0x80 | slot 3 Lv40 70 / 58 / 71; v3 `rage_stats` apply `rom:0x89A55C` adds 20 (`ldrh r2,[r1,#0xa] ; lsr r2,r2,#8 ; add r2,#0x14`) | C |
| Rage regeneration | +9 HP every 20 frames = 27 HP/s | | | tick `@0x0801710E` (equal to base in v3): +0xCCD a frame, overflow adds max HP x 0x290 >> 16 | C code, L play |

The save is the `log2_save` level 40 preset, not a real playthrough (C, CJT row). The relay records are from the same save.

| Matchup (attacker on defender) | Damage per hit | Crit | Mean | Hits from full | Label |
|---|---|---|---|---|---|
| **Rage Gohan punch on a Jr** | 231-254 | 462-508, 22.5 % | 297 | **16.8 per Jr, 67 for 4** (fewer when one punch hits 2 or more) | C model |
| Rage Gohan ki blast on a Jr | 167-183 | none | 175 | 28.5 per Jr | C model |
| **Jr punch on Rage Gohan** | 28-30 | 56-61, 11.5 % | 32.3 | **28** with no regeneration; about 52 with regeneration at the fastest rate (one hit every 33 frames) | C model, L (regeneration in play) |
| Jr ki blast on Rage Gohan | 32-35 | none | 33.2 | 27 | C model |
| 4-Jr full lock, toy model (1.58 hits/s) | | | 51 HP/s in, 27 regen | about 38 s from full (18 s with no regeneration) | S |

Relay fights (one Jr, level 40 records, base form and transformed form):

| Fighter | Punches per Jr | Jr punch on him | Jr punches from full |
|---|---|---|---|
| Piccolo base / Super Namek (+6) | 37.1 / 30.6 | 48-106 / 44-96 | 19 / 21 |
| Vegeta base / Super Vegeta (+15/+10/+15) | 29.7 / 18.9 | 51-113 / 40-88 | 19 / 25 |
| Trunks base / Super Trunks (+15/+10/+15) | 53.8 / 32.6 | 66-146 / 55-121 | 15 / 18 |
| **Rage Gohan vs 4 Jrs** | 16.8 each (67) | 28-61 | 28, plus 27 HP/s |

Group comparison: maps 2,35-2,38 each hold 4 x type 86 (HP 1400, AI 52, 37 / 31 / 31, `set:98`) (C, `group_fights.txt`). Rage Gohan needs 4.0 punches for each one (16 for the group), and their punch does 20-44 (C model). The Jr group has 3.6 times the HP (19,960 against 5,600), and its AI does not wait after a punch.

**Reading:** for each Jr, Rage Gohan is far stronger than any relay fighter. The difficulty comes from 4 at once with no wait (the lock) and a 19,960 HP pool. The Jr's per-hit damage is not the problem (L).

---

## Options

All options change only the trial Jrs, except where the table says otherwise. Two facts apply to every row:
- A new type entry must sit where (address - `0x086D56AC`) is a multiple of 24.
- A new AI row must sit where (address - `0x086D5194`) is a multiple of 8.

Both ids are read as u32 with no bound (`@0x0800E780`, `@0x0801AA98`, CJH) (C). The 4 item type words are `rom:0x90A56C`, `0x90A59C`, `0x90A5CC`, `0x90A5FC` in v3 (CJH). v4 is in progress, so a patch should find them through the items.

| # | Option | Bytes and data | Effect on the numbers | Risk |
|---|---|---|---|---|
| A | **New trial type** (copy of type 26) | 24 bytes in the expansion; 4 type words (16 bytes) changed. Death descriptor `0x086D5654` kept | None alone | Low. The Select scan matches by type, so the trial Jrs show no scouter marker unless an entry is added (R33, CJH) (C) |
| B | Lower HP (in A) | type +4 | 3750: 12.6 punches a Jr, 51 for 4. 3500: 11.8 / 47. 2500: 8.4 / 34 (`option_numbers.txt`) | Low |
| C | Lower attack (in A) | type +0xC STR, +0xD POW | STR 40: Jr punch 22-24 (crit 45-49), 35 punches from full. STR 36: 19-21, 41. POW 44: blast 26-28. POW 40: 22-24 | Low |
| D | Lower blast roll (AI 21 copy) | Copy rows 21-28: 39 nodes, 844 bytes, every PUSH re-pointed, plus 8 AI rows (64 bytes). The 10 other nodes and the `0x086FF4xx` singletons hold no row id and stay shared (C, bytes in `bible_rows.md`). Change the copy of `rom:0x6D23E4` (`0x0CCC`, 5 %), for example to `0x0666` (2.5 %) (`ai_copy_plan.txt`) | Half as many blasts. The blast damage is unchanged unless C lowers POW | Medium: a wrong pointer breaks the AI. A static test can walk the copy (every node decodes, every PUSH id is 21'-28' or 18) |
| E | **Post-punch wait** (in the D copy) | Row 26' SEQ n=2 becomes n=3 `{PUNCH, 0x086D1FC4 (wait 30), OR}`: 4 more bytes. The vanilla AI 8 / 45 / 52 shape | Toy model, 4 Jrs in reach: 1.28 damaging hits/s (was 1.58), median gap after each hurt 15 frames (was 4) | Medium (same copy). The effect size is S until emulator step 4 |
| F | Punch-only AI (in A) | Type +8 = 52, 45 or 8. No node copy | No blasts. AI 52 / 45 also bring the 30-frame wait | Low bytes. Behaviour: AI 52 row 55 (`0x0801CF73`) and AI 45 row 48 (`0x0801CCA9`) run untraced moves that may need anims `set:31` lacks (S). AI 8 is passive: 10 % guarded punch |
| G | Spacing behaviour (in the D copy) | Row 24' near branch becomes OR(RANDOM p then row 25', back-off mover `0x0801C431` then row 24'): about 60 bytes of vanilla node shapes | Fewer Jrs commit at once, on average. There is no cap, because no vanilla node counts attackers | Medium; effect S |
| H | Wider spacing by footprint | A cloned set with a larger footprint (set bytes +3, +4) | Fewer Jrs fit in reach | High: a new set id needs the set table moved (SPC) |
| I | Fewer Jrs at once (script, 2 + 2 or tag-team) | Records X and C only | 2 in reach at most | Low code risk, but it conflicts with the final decisions of 2026-10-24: "Gohan then fights 4 fresh Jrs at once" and "keep ... the 4 Jrs" (bible section 12) |
| J | **Melee cap, 4 Jrs on screen:** items 13-14 use the brawler type (A + D + E), items 15-16 a second trial type whose AI is a shooter variant of rows 21-24 that never pushes row 25 (row 24S near branch = back-off `0x086D26E0`, then row 22S) | A second type entry (24 bytes), 2 of the 4 type words, about 320 bytes of new nodes in vanilla shapes (shared: line-up `0x086D2040`, approach `0x086D2404`, back-off `0x086D26E0`, blast `0x086FF478`, JUMP 18 `0x086D23A0`) and 4 AI rows (32 bytes) | **At most 2 Jrs in melee**, by construction: no punch leaf is reachable from the shooter rows (C design). Toy lock model at 2 in reach: 1.41 hits/s and a 9-frame median gap without the wait, 1.25 and 15 with it (S). The 2 shooters hover at 72-120 px and blast | Medium. Two Jrs that never melee change the feel. If both brawlers die first, the fight ends against 2 shooters that back away (S) |

Not trial-only, listed for completeness: a short invulnerability after Gohan's hurt state (player code, every fight); changing type 26 (relay fights).

---

## Recommendation

Use **A + B + C (POW only) + D + E**. Keep 4 Jrs at once and keep STR. This keeps the fight hard and removes the lock.

| Item | Value | Why |
|---|---|---|
| Trial type entry | EXP 0, **HP 3750**, AI = the copy's row 21', **STR 46**, **POW 44**, END 46, factors 0x80 / 0x80, death `0x086D5654` | HP -25 % cuts the slog. STR stays, so each Jr punch still hurts |
| AI 21 copy | rows 21'-28' (848 bytes of nodes + 64 bytes of rows) | Needed to change the Jr AI without touching Androids 17 and 18, the relay Jrs and types 29, 41, 106 |
| Post-punch wait | 30 frames in row 26' | The vanilla group-AI rule. The Jrs swing at the hurt Gohan, then sit out, so he gets a window |
| Blast roll | 5 % to 2.5 % (`0x0CCC` to `0x0666`) | I call the blast a headache, but not the main issue |

| Number | Now | Recommended | Label |
|---|---|---|---|
| Gohan punches to clear the group | 67 (16.8 a Jr) | **51** (12.6 a Jr) | C model |
| Jr punch on Gohan | 28-30, crit 56-61 | same | C model |
| Jr blast on Gohan | 32-35 at 5 % a roll | **26-28 at 2.5 %** | C model |
| Damaging hits/s with 4 in reach | 1.58 | **1.28** | S |
| Median free frames after each hurt, 4 in reach | 4 | **15** | S |
| Time to lose under a full 4-Jr lock, no counterplay | about 38 s (18 s with no regeneration) | **about 65 s (22 s with no regeneration)** | S, and L for regeneration |

Total size: about 950 bytes in the expansion and 4 changed type words. No code. Build it as a trial ROM next to v4.

> [!WARNING]
> The crowding benefit of this recommendation comes only from the 30-frame wait (E), and that number is S: it comes from the toy model. It stays S until emulator step 4 measures the gap after each hurt. The model still puts all 4 Jrs in reach.

If step 4 shows that the lock remains, use option J in the same copy: 2 brawlers and 2 shooters. J gives a hard cap of 2 Jrs in melee by construction, and it still shows 4 Jrs. It is not the first choice because it changes the feel of the fight (2 Jrs never punch) and has an end-game risk (S). Option G is the softer step between them.

---

## Emulator steps

Use `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr_v3.gba` with its `.sav`, slot 3. Play into Gohan's 4-Jr fight. List actors with `scripts\one-time\2026-10-24-celljr-trial\state_actors_v3.py`.

1. **Regeneration.** Take a hit, then read Gohan's HP (u16 `0x03000E9C`, record 0 +0) every 20 frames 3 times. Expected: +9 each time, up to 906.
2. **Live stats.** Player `[0x03001FA8]` +0x160..+0x164: expected `5A 4E 5B 80 80`. A Jr (vtable `0x080252A4`) +0x160..+0x164: expected `2E 32 2E 80 80`; +0x188 = its HP.
3. **Damage.** Read Gohan's HP on the frame before and after a Jr punch, away from a regeneration tick. Expected: 28-30, or 56-61 on a crit.
4. **Lock gap.** Step frame by frame from the frame Gohan's +0x163 goes from 0 back to 0x80 (hurt end) to the frame his HP next drops. Log 20 cases with the number of Jrs within 30 px. Expected (S): a few frames when 3-4 Jrs are near.
5. **STOP or CREEP.** Let 3-4 Jrs crowd Gohan while he stands still for 3 s, then take a state. List Jr anchors minus Gohan's anchor. STOP predicts about 20-23 px out on the diagonals. CREEP predicts within 16 px, on his cells.
6. **Blast rate** (CJH step 4). Over 60 s, count the frames where any Jr has +0x18 = `0x03002224`.

---

## Files

All in `scripts\one-time\2026-10-25-celljr-balance\`:

| File | What |
|---|---|
| `occupancy.py`, `occupancy.txt` | Bitmap +0x6C / +0x70 / +0x74 compare on the two celljr states |
| `crowd_model.py`, `crowd_model.txt`, `crowd_stop_v3.png`, `crowd_creep_v3.png` | Mover, grid and guard model |
| `stack_lines.py`, `stack_lines.txt` | Jrs in a line |
| `damage_model.py`, `damage_model.txt`, `option_numbers.py`, `option_numbers.txt` | Damage port and option numbers |
| `lock_model.py`, `lock_model.txt` | Stun-lock toy (S) |
| `ai_tree.py`, `ai_tree.txt`, `ai_census.txt`, `punch_waits.py`, `punch_waits.txt`, `ai_copy_plan.py`, `ai_copy_plan.txt` | AI trees, node census, post-punch waits, copy size |
| `group_fights.py`, `group_fights.txt`, `blscan.py` | Group maps, BL scan |
| `bible_rows.md` | `CJB` rows |
