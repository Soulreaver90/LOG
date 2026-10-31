# Study: Gohan vs the Cell Jrs before Cell

Study only. No ROM was built and no file outside `scripts\one-time\2026-10-24-celljr-fight-study\` and this report was written. All addresses are r38 (`builds\log2_poc_r38.gba`, SHA-1 `7a7cb85fa5873c4a44d360b33b6755d4e71e18e3`, checked). r39 is in flight, so rebase every address before a build.

Labels: **C** = CONFIRMED (bytes or listing read), **L** = LIKELY, **S** = SPECULATIVE.

---

## Verdicts

My idea is feasible with script and data edits only. No Thumb code change is needed.

| Ask | Verdict | Effort |
|---|---|---|
| Cell spawns 7 Cell Jrs, not 3 | Feasible, with one limit: 7 NPC Jrs plus an open dialog box overflow OBJ VRAM by about 4 units (256 bytes). Spawn the extra 4 in a code record with no text line after it (L) | S |
| Piccolo, Vegeta and Trunks each beat one, as today | No change. The three fights stay byte equal | none |
| Gohan (SSJ2) fights the remaining 4 at once, after the transform | Feasible. Needs 4 new spawn items (14,3 spawn list copied and grown 13 to 17), a new death event table with a death counter, and Cell held out of the fight as an NPC | M |
| Then "You wretched child", then SSJ2 Gohan vs Cell as today | Feasible. The two vanilla records run from the new event table; Cell is rebuilt with `ext 84 (11)` first | S (inside the M above) |
| Separate stats for Gohan's 4 Jrs | No free enemy type. Reuse type 26 (S) or add a type entry (M) | me |

Three facts drive the design:
1. **Cell is already a live enemy at the insert point (C).** Gohan's table seq 1 runs `push 11 ; ext 84`, which builds Cell type 24 before the Android 16 lines. If the scene ends after the transform, Cell's AI 138 joins the Jr fight, and a Cell kill would run the self-destruct table out of order. The design swaps Cell to an NPC for the Jr fight and rebuilds him after.
2. **No vanilla precedent for several event-carrying enemies alive at once (C).** All 28 enemy spawns with a death event are single bosses; no event table is shared (`event_share_r38.txt`). The "all 4 down" counter is new mechanics.
3. **The real VRAM limit is the dialog box (C model, L composition).** The world allocator pool is 492 units of 64 bytes in all 6 measured states; a text box takes 224 contiguous units.

---

## Current sequence map (r38)

### Spawn items on map 14,3

Map entry 325 at `rom:0x40DA80`; spawn count byte `rom:0x40DA84` = 13 (C); spawn list word `rom:0x40DA94` = `0x08409118` (C). Enemy item: +4 cond, +8 type (u32), +0xC x, y (s16), +0x10 set, +0x14 event struct `{0x080106B3, table}`.

| Item | Address | Cond | Type | Pos | Set | Event table | Label |
|---|---|---|---|---|---|---|---|
| 0 | `rom:0x408F18` | 0 (always) | 22 | (500,440) | 30 | `0x083E93E8` (Me? Fight Cell?) | C |
| 5 | `rom:0x408FC8` | 1 (never at load) | 23 | (500,440) | 30 | `0x083E9D4C` (Android 16, Cell Jr spawn) | C |
| 8 | `rom:0x409038` | 1 | 26 | (432,376) | 31 | `0x083E9E24` (to Vegeta) | C |
| 9 | `rom:0x409068` | 1 | 26 | (432,376) | 31 | `0x083E9E84` (to Trunks) | C |
| 10 | `rom:0x409098` | 1 | 26 | (432,376) | 31 | `0x083EA400` (to Gohan, Rage) | C |
| 11 | `rom:0x4090C8` | 1 | 24 | (512,472) | 30 | `0x083EB704` (self-destruct) | C |
| 12 | `rom:0x4090F8` | 1 | 25 | (512,472) | 58 | `0x083EC758` (post-Cell) | C |

Items 1-4, 6, 7 are NPCs: Vegeta 137, Trunks 132, Gohan 158 (only while `flag:192` is clear), Piccolo 103, Krillin 76, Android 16 `set:8` (only while `flag:194` is clear). The list ends at `rom:0x40914C`, where obj18 data starts, so it cannot grow in place (C).

### Steps

| # | Step | Where | Label |
|---|---|---|---|
| 1 | Cell type 23 "dies" (Gohan's first Cell fight); its event runs table `rom:0x3E9D4C` (32 words) | item 5 event `rom:0x408FC0` | C |
| 2 | Seq 1 reloads 14,3 (`ext 39 (14,3,1,400,440)`), spawns NPC Goku `set:61` at (552,96); the reload builds item 0 (type 22 Cell, set 30) and the NPCs | record `0x083E9440` | C |
| 3 | Android 16 lines; seq 22 Cell kills 16 (`ext 52 (8)`), SET `flag:194` | record `0x083E9A5C` | C |
| 4 | Seq 26 "Hrmm... Still not angry enough Gohan?" | `0x083E9C0C` | C |
| 5 | **Spawn: seq 27 = 3 NPC Cell Jrs** by `ext 51 (31, x, y)` at (408,392), (432,376), (456,392), each with `ext 42 (5)` flash, `ext 43 (5)`, `ext 69 (40)`. **The count is the number of ext 51 calls in this record; there is no count variable** | record `0x083E9C50` (79 bytes), table word `rom:0x3E9DB4` | C |
| 6 | Seq 28 "What the heck are those things?", seq 30 "My children! Give them pain!" | `0x083E9CA0`, `0x083E9CCE` | C |
| 7 | **Piccolo fight (playable):** seq 31 fades, music 35, removes NPC Piccolo 103, 3 x `ext 52 (31)`, removes set 30, `ext 70 (1)`, `ext 84 (8)` builds one Jr enemy, `ext 86 (1)` (HUD on), `ext 85 (31)` boss bar, `ext 33 (0)` | record `0x083E9CF0` (90 bytes, ends at the table start), table word `rom:0x3E9DC4` | C |
| 8 | **Vegeta fight (playable):** item 8 death runs `rom:0x3E9E24` (2 words): `ext 88`, `ext 139 (50000)`, music 39, removes NPC 137, `ext 70 (2)`, `ext 84 (9)`, boss bar | record `0x083E9DCC` | C |
| 9 | **Trunks fight (playable):** item 9 death runs `rom:0x3E9E84`: same shape, music 38, removes 132, `ext 70 (3)`, `ext 84 (10)` | record `0x083E9E2C` | C |
| 10 | **Gohan transform scene:** item 10 death runs `rom:0x3EA400` (33 words). Seq 1 (r27 copy `0x0889A71C`): `ext 139 (50000)`, ext 73 (0, 158), `ext 110 (0, 5000)`, `ext 70 (0)`, reload 14,3 at (576,376), music 37, removes set 30, **`ext 84 (11)` builds Cell type 24**, spawns Hercule 72 | table `rom:0x3EA400`, word 0 | C |
| 11 | Hercule carries 16's head; Cell crushes it (seq 19 `ext 99`/`ext 100 (30, 616, 384)`) | `0x083EA222` | C (bytes), L (op meaning) |
| 12 | Seq 27 Rage: music 20, state 9, flash, HP and EP refill (var 13, var 15), **ext 73 (0, 160)** | `0x083EA33C` | C |
| 13 | Seq 30 "Gohan has transformed into Super Saiyan 2!" (r19 `rage_text`), next index 30 | record `0x08895434`, word 29 `rom:0x3EA474` | C |
| 14 | **Seq 31 "You wretched child!!! NOW TASTE MY TRUE POWER!!!!!!"**, next 31 | record `0x083EA3B4`, word 30 `rom:0x3EA478` | C |
| 15 | **SSJ2 Gohan vs Cell:** seq 32 `ext 33 (0)`, `ext 86 (1)`, `ext 90 (30, 25, 100)`; word 32 = END, the scene ends and the fight runs | record `0x083EA3EC`, word 31 `rom:0x3EA47C` | C |

Other facts used:
- Cell Jr: scouter entry 20 `rom:0x6F8FD0` ("Cell Junior", set 31, portrait 0, type 26); type 26 entry `0x086D591C`: EXP 0, HP 4990, AI 21, STR 46, POW 50, END 46, factors 0x80, death descriptor `0x086D5654` (C). Only items 8-10 use type 26 or enemy set 31 (aligned factory scan, C).
- Type 26 does not use the boss descriptor. `0x086D5654` = `{0x0801A7DF, 0, 0x0801A74D, 0x40}`, the normal death node with param 0x40 (normal enemies 8). The release `0x0801A74C` runs the EXP task, queues the event task `0x0800E39C(enemy, param)` and removes the enemy from the world at once (C). What the param does (frame delay before the event) is not traced (S).
- `ext 139 (n)` = give n EXP to the leader (`0x08003D58`: record +0x10 += n, level recomputed, level-up scene `0x083B6524`). The Jr tables run it before `ext 70`, so the winner gets 50000 EXP (C).
- `ext 84 (n)` = `0x0800C73A`: builds item n when n < count, no condition test (C). Enemy factory `0x0800E77E` reads the type as a u32 with no bound (C).
- Rage form (entry 4) has no EP drain and regenerates 1 % max HP every 20 frames (`re-forms.md`), so Gohan stays SSJ2 through a longer fight (C, from FRM).
- Map 14,3 has no region list (+0x10 = 0), so the player cannot leave the arena (C).

---

## Design (smallest change)

One new patch, for example `celljr_fight.py`. It owns 4 words and 1 count byte in base data plus new allocations. It edits no record in place.

### Part 1: spawn 7 (S)

- Copy record seq 31 (`0x083E9CF0`) to the expansion and repoint table word `rom:0x3E9DC4`.
- At the head of the copy, add 4 x `{ext 42 (5) ; ext 51 (31, x, y) ; ext 43 (5) ; ext 69 (40)}` with 4 new positions (for example (384,408), (480,408), (408,424), (456,424); check by eye). Then a short pause, then the vanilla body with 4 more `push 31 ; ext 52` (7 removes in all). About 190 bytes.
- Seq 27 stays vanilla (3 spawns), so both text lines run with 3 Jrs on screen. The other 4 pop out after "My children! Give them pain!" and before the fade.
- **Why not 7 in seq 27:** at seq 28 the actor set is player 158, NPCs 137, 132, 103, 76, Goku 61 (6 x 16 units), Cell set 30 (64), 7 Jrs (112): 272 of the 492-unit pool, 220 free. The text box needs 224 contiguous. With 3 Jrs, 284 are free (C arithmetic, L actor set; no state exists at seq 27). A failed allocation is not checked: `0x080075BC` stores -1 as the tile, and the frame DMA `0x0800784C` writes outside the slot (C code, L visual result). 6 Jrs would fit (236).

### Part 2: the 3 ally fights (none)

Tables `rom:0x3E9E24`, `rom:0x3E9E84` and items 8-10 stay byte equal. Item 10's event still opens Gohan's table.

### Part 3: Gohan vs 4 Cell Jrs (M)

1. **Spawn list:** copy `rom:0x409118` (13 words) to the expansion with 4 more words, repoint `rom:0x40DA94`, set `rom:0x40DA84` from 13 to 17. Items 0-12 keep their addresses, so `superperfect_cell`'s in-place edit of item 12 stays valid. Vanilla maps reach 19 items (map 2,1), so 17 is inside the known range (C). Precedent: `chamber_spar` copied the 6,70 lists (CPR).
2. **4 new enemy items (13-16):** copies of item 8 (cond 1, type 26 or a new type, set 31), each at its own position around Gohan, who stands at (576,376) (for example (528,344), (528,408), (624,344), (624,424); Cell stands at (616,384); check by eye). Each +0x14 names one new event struct `{0x080106B3, T}`.
3. **Fight start:** a new record X, named by word 30 of Gohan's table (`rom:0x3EA478`, today `0x083EA3B4`). X has next index 32, which is already END, so the scene ends and the fight runs. X body:
   - `push 0 ; set var1` (reset the counter).
   - `push 30 ; ext 52` (remove the type 24 Cell enemy), `push 30, 616, 384 ; ext 51` (NPC Cell where `ext 100` left him).
   - Optional flash, then `push 13 ; ext 84` ... `push 16 ; ext 84`.
   - `push 0 ; ext 33`, `push 1 ; ext 86` (camera on Gohan, HUD on), `end`.
   - No boss bar: there is one bar object with one target (HKP).
4. **Death counter:** event table T (33 words, new). Word 0 = counter record C, word 1 = END, words 2-28 = 0, word 29 = Cell restore record N, words 30, 31 = copies of the "wretched" line and the seq 32 record, word 32 = END.
   - C: `inc var1 ; call ext_1 ; push 4 ; lt ; jz L ; push 1 ; end ; L: push 29 ; end`. A single value left on the stack replaces the next index (SS3 row), so deaths 1-3 end the scene at word 1 and death 4 goes to word 29.
   - N: `ext 88 ; push 0 ; ext 86 ; push 30 ; ext 52 ; push 11 ; ext 84 ; push 30, 616, 384 ; ext 62 ; push 30, 1 ; ext 55`, next 30. Optional `ext 139 (EXP)`.
   - Words 30, 31: copy the two vanilla records instead of reusing them. Record +0 holds the next index, so a reused record forces its index in every table that names it.
5. **Why var 1:** VM vars 0-3 are IWRAM `0x03001FB0`-`0x03001FBC` (setters `rom:0x3B5F70`, getters ext 0-3, C). They are not in the save. **Var 0 is taken:** the 14,3 obj18 ambient script `0x083EE6A8` runs `push 100 ; ext 17 ; set var0` (C). Var 1 has no user by shape A (scripts reached by aligned pointers: var 0 has 40 sets and 239 reads, var 1-3 have 0 in the script region) and by the literal shape (only the VM getter and setter pools name `0x03001FB0`) (C for the shapes, L for "unused"). Shape B (raw byte pairs) is dominated by data noise and does not settle it. A computed or unaligned script pointer, or a Thumb bulk write, would not show.
6. **Death timing:** the release removes each Jr from the world at death and queues one event per death, so a double kill runs C twice in turn (C code, L order). The 64-frame param (0x40) may delay the line after the last kill (S).

### Part 4: the line and the Cell fight as today (S)

Covered by N and the two copied records. `ext 84 (11)` rebuilds type 24 with full HP; its event is still the self-destruct table, so the rest of the stretch is unchanged.

### Bytes touched in base data

`rom:0x3E9DC4` (word), `rom:0x3EA478` (word), `rom:0x40DA84` (count byte), `rom:0x40DA94` (word). New: seq 31 copy, spawn list copy (17 words), 4 items (0x20 bytes each), 1 event struct, table T (132 bytes), records X, C, N and the two copies. Add a tool-trap row: tools that read `rom:0x409118` or bound table words to the script region read stale data.

---

## Effort

| Part | Effort | Note |
|---|---|---|
| 1 Spawn 7 | S | One record copy, one word |
| 2 Ally fights | none | |
| 3 Gohan vs 4 | M | List copy, 4 items, event table, 3 records, NPC Cell swap |
| 4 Line and Cell fight | S | Two record copies |
| New Jr stats (option) | M | Type entry outside the table, see final decisions |
| Tests, diff proof, emulator pass | M | Needs a save state at seq 28 to confirm the VRAM model, and a play test of the 4-fight |
| **Total** | **M** | |

---

## Risks

| Risk | Detail | Label |
|---|---|---|
| OBJ VRAM at the spawn lines | 7 NPC Jrs plus a text box leave 220 of 224 units. Part 1 avoids it. Pool 492 units in `log2_poc_r20.ss2`, `r22.ss3`, `r27.ss4`, `r27.ss5`, `r34_scouter.ss1`, `r38_scouter.ss1` (free plus all slots) | C (model), L (seq 28 actor set) |
| OBJ VRAM in the 4-fight | Player 16, NPCs 64, NPC Cell 64, HUD 20, 4 Jrs 64 = 228; 264 free. The "wretched" box after the fight: the Jrs are gone and N turns the HUD off | L |
| Cell joins the Jr fight | Removed by the NPC swap in X; rebuilt in N | C (cause), L (fix) |
| Counter clobbered | Var 0 is the 14,3 ambient scratch (C). Var 1 has no found user (L) | C / L |
| Mid-fight event scenes | Deaths 1-3 each push a one-record scene while other Jrs live. No vanilla precedent. Scene setup broadcasts world messages 0xD and 0xE (R27); a HUD flicker or a cancelled player action is possible | S |
| Stun-lock | 4 AI 21 enemies. The hurt state zeroes damage for 32 frames, with no invulnerability after it (BLK). No vanilla map has 4 or more AI 21 enemies. Vanilla has 73 maps with 4 or more enemies at load (up to 15 on 4,59) | L |
| CPU, OAM, heap, world list | 4 more enemies sit well under vanilla's 15-enemy maps; world list cap 128 (17 used in the 14,3 states); heap 179 KB free | L |
| Softlock | No exit on 14,3 (C). A Jr stuck in a wall stops the counter: pick open positions. If the player dies, the vanilla game over runs | L |
| Save flags | None added; the counter is RAM only and reset in X. The Cell Games has no save point, so a game over replays from 14,1 | C |
| Rebase | All addresses are r38. r39 may move expansion allocations; the 4 base-data sites are vanilla bytes today (`rom:0x3EA478` = `0x083EA3B4`, `rom:0x3E9DC4` = `0x083E9CF0`) | C |

Ext op meanings used but not listed in this study: 39 (reload map at a position), 24, 62 (place), 69 (wait), 99, 100. Label L.

---

## Final decisions

1. **Jr stats for Gohan's fight.** Type 26 is HP 4990, STR 46, POW 50, END 46, so 4 Jrs = 19,960 HP against Cell type 24's 6500. Rage Gohan has base+20 stats and regenerates HP, so the fight may be long but easy. Options:
   - (a) Reuse type 26: S, ally fights unchanged.
   - (b) Retune type 26: S, but it changes the 3 ally fights.
   - (c) New type: M. Types 95 (chamber spar), 96 and 97 (scouter entries 107, 111) are taken. A type entry in the expansion works through the unbounded u32 index, but the Select scan then shows no marker for those Jrs (the scan matches by type entry).
2. **Spawn timing of the extra 4.** Default: after "My children! Give them pain!" (fits VRAM). Seven before "What the heck are those things?" overflows by about 4 units.
3. **Where the 4 survivors are during the ally fights and the Android 16 scene.** Default: off screen (removed with the others, as vanilla does with 3), then they flash in at X. Option: 4 NPC Jrs stand near Cell from Gohan's seq 1. That costs 64 units, leaving about 44 free while Hercule talks (L).
4. **Boss bar.** Default none. A bar can follow one Jr at a time (`ext 88` then `ext 85 (31)` in each C run).
5. **EXP.** Vanilla gives 50000 EXP per ally Jr win via `ext 139`. Gohan's 4-fight gives none unless N adds `ext 139`.
6. **Line timing.** "You wretched child" plays after the 4th death event; the 0x40 param may add a short delay (S). Confirm the feel in play.
7. **Loss path.** Default: the vanilla game over ("You have died!", title). A retry path like `chamber_spar` is possible but is M.

---

## Expansion (later)

My note 2026-10-24 1:57 PM: Goku fights a Cell Jr, and the Jrs do not explode, so Gohan faces 7 at once. Keep the 4-Jr fight as the main design.

| Idea | What it takes | Effort |
|---|---|---|
| Goku fights one Cell Jr | One more link in the chain. Item 10's event becomes a new Goku table: `ext 88`, `ext 139`, remove NPC Goku 61, `ext 70 (4)`, `ext 84` of a new item, `ext 85 (31)`. The new item's event opens Gohan's table `rom:0x3EA400`. `ext 70` runs `appearance_revert`, so Goku may need `ext 73 (4, 61)` to stay Super Saiyan (fullpower_ssj stretch rules, R28). The ally fights then use 4 Jrs, so 3 remain for Gohan unless the spawn grows to 8 | M |
| Gohan faces all 7 at once (Jrs do not die in the ally fights) | The ally fights cannot "lose" a Jr: events run only at death. So the ally fights become scripted beatdowns (ext 57 states, no playable fight), or they are cut. Then X builds 7 items and C counts to 7 | M (scripted beatdowns), S (cut the ally fights) |

Limits that decide whether 7 at once works:
- **OBJ VRAM in combat:** player 16, NPCs 64, NPC Cell 64, HUD 20, 7 Jrs 112 = 276 of 492; 216 free. Fits (L).
- **OBJ VRAM in scenes:** 7 NPC Jrs standing through a text box overflow (see Part 1). Stand-ins during the Android 16 scene would leave about 12 units, and about -4 while Hercule talks. So the 7 must flash in at fight start, or fewer NPCs stand on screen during the lines (L).
- **Enemy cap:** no per-map enemy cap found. World list 128 actors; vanilla runs 15 enemies on map 4,59; the spawn list would be 20 items, above the vanilla maximum of 19 but inside the u8 count (L).
- **Stun-lock and difficulty** grow with 7 AI 21 enemies; tune the type (see decision 1).

---

## Files

- Report: `docs\tasks\2026-10-24-celljr-fight-study\celljr-fight-study-report.md`
- Bible rows (tag CJR): `scripts\one-time\2026-10-24-celljr-fight-study\bible_rows.md`
- Tools in `scripts\one-time\2026-10-24-celljr-fight-study\`: `cj_dump.py` (14,3 spawns and Jr tables), `extq.py` (ext handler table, listings, BL users), `vram_budget.py` (OBJ allocator, actors, heap in states; set slot sizes), `var_sweep.py` (VM var users, shapes A and B), `event_share.py` (event-carrying spawn precedent)
- Outputs: `cj_dump_r38.txt`, `vram_budget_r38.txt`, `event_share_r38.txt`
