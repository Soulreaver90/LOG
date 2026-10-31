# Design study: Cell Jr fight and canon additions (2026-10-29)

Study and proposal only. No module, build list or ROM changed.

Labels: **C** = CONFIRMED (ROM bytes or listing quoted), **L** = LIKELY (guide, web page or a strong inference), **S** = SPECULATIVE. Web pages are quoted as sources, not as proof. All ROM facts read the base ROM `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba`. Scripts and listings: `scripts\one-time\2026-10-29-design-ideas\`.

---

## SHIPPED

| Ask (my words) | Where |
|---|---|
| "make it closer to the anime" | Part 1, "Anime and manga facts" (sources quoted) |
| What the game does today | Part 1, "What the game does today" |
| "See if there are examples in game of enemies/bosses whose stats are 'decreased'" | Part 1, "Decreased-stat table" (every type read from `rom:0x6D56AC`) |
| "Propose something ... fun and also display Gohan's greater strength" | Part 1, "Designs" (4 designs) and "Recommendation" |
| "I wonder if we should instead do a 1 v 1, then a 1 v 3" | Design A |
| "brainstorm anything else we should adjust/include in LOG2 ... Just canon stuff" | Part 2, ranked table and notes |
| Bible rows, tag DID | `scripts\one-time\2026-10-29-design-ideas\bible_rows.md` (sections 8, 11, 14) |

## PENDING

| Item | Why |
|---|---|
| Me: pick a design and an HP value | See "Open questions" |
| No emulator run | Every in-play claim is L or S |
| All numbers use the level 40 preset save | Gohan Rage 90/78/91, HP 906 (CJB). A real playthrough level changes every hit count |
| A second shape for "the fight ends only at HP 0" | The apply-hit path has no other HP test (C). An AI node that reads HP and starts a scene would not show in that listing |
| What `ext 104 (set, n)` does | It re-arms a beaten boss for the next round in two tables (C bytes). The meaning is L |
| Where the future epilogue lives | The guide says it plays after the credits (L). The ASCII scan found no line for it |
| Me: merge the DID rows | Merge notes are at the top of the rows file |

Housekeeping: one PowerShell call that tried to write a helper script to the user temp folder was blocked by the permission system. `Test-Path` shows that no file exists there. No call used `cd` or `Push-Location`. Nothing was written under `data\`.

---

## Part 1: the Cell Jr fight

### The core problem in one table

This table shows why my v5 fight still feels long. The numbers come from the exact damage port (`design_numbers.txt`, C model).

| Fight | Enemy HP | Rage Gohan punches to win | Enemy punches to KO Gohan |
|---|---|---|---|
| 4 Cell Jrs today (type 26, 4 x 4990) | 19,960 | **67** (16.8 a Jr) | 28 (Jr punch 28-30, crit 56-61) |
| Cell right after (type 24) | 6,500 | **26** | 24 (Cell punch 32-35) |

- The fodder fight is 2.5 times longer than the boss fight that follows (C model). In the anime it is the other way round.
- Jr STR changes little. STR 46 to 36 moves "Jr punches to KO Gohan" only from 28 to 41 (C model).
- **HP is the lever.** HP sets the length. The v5 AI (30-frame wait, 2.5 % blast) already handles the crowding.
- This matches the English dub: the Jrs are as strong as Cell but far less durable (L, fan wiki summary in the search results).

### Anime and manga facts

This section gives the canon events. Sources: Kanzenshuu wiki pages "Cell Jr", "Dragon Ball Chapter 408", "Dragon Ball Z Episode 184" and "185", and the Kanzenshuu forum thread "Cell Juniors in episode 185".

| Point | Manga | Anime (DBZ) | Label |
|---|---|---|---|
| Where | Chapter 406 (debut), 407 (16's head), 408 "Son Gohan Explodes!!" | Episodes 183, 184, 185. Kai episode 93 | L (Kanzenshuu) |
| How many | 7, "one for each of Gohan's friends who are spectating" | 7 spawned, but **8 die** on screen (animation miscount, "There's eight killed in the episode") | L |
| Who fights whom | Krillin, Yamcha, Tien, Trunks, Vegeta, Piccolo, Goku, one each | Same. Extra beats: Piccolo knocks his Jr into Tien's, Tien and Yamcha save Goku, a Jr breaks Yamcha's arm, a Jr blocks Vegeta's Final Flash | L |
| How the fighters fare | "Only Trunks and Vegeta manage to put up a fight; the others get pummeled." **No Jr dies before Gohan** | Same | L |
| Trigger | 16 tells Gohan to fight; Cell crushes 16's head | Same (episode 184 ends with SSJ2) | L |
| How Gohan wins | Punches the head off the Jr over Krillin. "The rest fly at him. He kills five of them, each with just one hit." The seventh "tries to flee", Gohan chases it and kills it with one strike | Kills the Jr hurting Goku first, then saves Krillin with a kick, beats 5 that attack at once, a shockwave, then the rest. The Jrs explode at his touch | L |
| Speed | Seconds. Then he tosses the senzu bag to Trunks | "so quickly that he is unseen" | L |

**Manga shape: 1, then 5 at once, then 1 that runs.** My "1 v 1, then 1 v 3" is the same shape with 4 Jrs.

### What the game does today

This section gives the vanilla order and the trial order (CJR, CJT, CJ5 reports; C unless marked).

| Step | Vanilla | Trial v5 |
|---|---|---|
| 1 | Gohan (Super Saiyan, playable) fights Cell type 23. Bar (30,60,100) | Same |
| 2 | 16 dies; Cell spawns 3 NPC Jrs (seq 27 `rom:0x3E9C50`) | 3, then 4 more (7 on screen) |
| 3 | Piccolo fights Jr item 8 (`ext 70 (1)`), Vegeta item 9, Trunks item 10. Each Jr dies. 50,000 EXP each | Same |
| 4 | Hercule brings 16's head; Cell destroys it; Rage (SSJ2) | Same |
| 5 | "You wretched child", SSJ2 Gohan vs Cell type 24 | **4 fresh Jrs at once** (items 13-16, trial type 96463, v5 AI), then a fade, "You wretched child", Cell |

- Gohan's stats in the Jr fight (level 40 preset): Rage 90/78/91, HP 906, regeneration 27 HP a second (CJB: C code, L in play).
- The relay fighters need many more punches per Jr: Piccolo 37, Vegeta 30, Trunks 54 (base forms, CJB). So the game already shows Gohan as far stronger per Jr. Only the group total hides it.

### Decreased-stat table

This table lists every LoG II enemy that is a weaker twin of a stronger one. Bytes: `type_census.txt`. Type entry = `rom:0x6D56AC` + 24 x type; +4 HP, +8 AI, +0xC/+0xD/+0xE STR/POW/END.

| Weak twin | Strong twin | HP | STR/POW/END | Scouter entries | Where | Label |
|---|---|---|---|---|---|---|
| **Dream Frieza, type 41** `rom:0x6D5A84` | Frieza, type 42 `rom:0x6D5A9C` | **130** vs 1974 (x0.07) | 3/2/3 vs 30/37/20 | None for type 41. Entry 34 "Frieza" `rom:0x6F90E8` names type 42 | Map 2,8 item 1 `rom:0x3EE770`, `set:48` (Frieza's art), **AI 21** (the Jr AI), boss descriptor, EXP 20. Type 42 has no spawn. Guide 2: "EXP: +20 ... He has around 150 HP" | C |
| **Perfect Cell vs Trunks, types 79 and 78** `rom:0x6D5E14`, `0x6D5DFC` | Cell Games types 21-24 (`rom:0x6D58A4`-`0x6D58EC`) | 5500 and 5160 vs 6500 (x0.85, x0.79) | 44/46/50 vs 50/55/60 (x0.88, x0.84, x0.83) | 14 `rom:0x6F8F58` (type 79), 13 `rom:0x6F8F44` (type 78); 15-18 `rom:0x6F8F6C`-`0x6F8FA8` (types 21-24) | Map 12,6 items 1 `rom:0x406F78` and 4 `rom:0x406FF0`, `set:30`, AI 148 | C |
| **Dr. Gero rematches, type 7** `rom:0x6D5754` | Android 20 first fight, type 6 `rom:0x6D573C` | 1900 vs 2810 (x0.68) | 25/21/17 vs 24/19/14 (higher) | 6 `rom:0x6F8EB8` (type 7), 5 `rom:0x6F8EA4` (type 6) | Type 7: maps 8,13, 8,27, 8,40 (3 spawns). In the 8,27 and 8,40 tables he flees and the table sets `flag:89` / `flag:88`; the 8,13 table word decodes to no record | C |
| Cell Jr relay | (none) | 4990 for all 3 | 46/50/46 | 20 `rom:0x6F8FD0` (type 26) | Same type 26 `rom:0x6D591C` for Piccolo, Vegeta, Trunks | C |

**Not a decreased stat: the "fight ends at 1/2" bosses.** The guides say Android 18 "ends at half", Android 17 at 3/4, 1/2, 1/4, Cell at 1/4. The ROM shows these are full-HP fights:
- The enemy dies only at HP 0: apply-hit `@0x0800E4A2`-`@0x0800E4CC` (C listing).
- The bar fill = start + HP x width / max HP, with start = a x 60 / 100 (HKP row, C). So with `ext 90 (11, 50, 100)` the bar stops at one half when 18's HP reaches 0.
- Every guide "end point" matches a segment start in `boss_sites.txt`: 18 (11,50,100), 17 (9,75,100) (9,50,75) (9,25,50), Semi-Perfect Cell (29,25,100) (C bytes, L that no AI node ends a fight on HP).
- So the bar slice is a vanilla trick: it shows the hero only denting the boss.

**Beaten but not dead (vanilla).** A boss-descriptor enemy stays on the map at HP 0. The boss release `@0x0801A82C` runs the EXP and event tasks only; the normal release `@0x0801A74C` also removes the enemy from the world (C listings). Android 18's table `rom:0x3D98AC` drives the beaten 18 (`push 11,3 ; ext 57`) and talks ("Nice try!") with no new spawn (C bytes). The Jr type uses the normal descriptor, so a Jr vanishes at once (CJR).

**Buu's Fury pattern (guide only, L).** Super Buu keeps HP 35330 and 50/65/55 in the Gotenks fights and the Gohan fight. "You don't even have to drain his bar completely; Two thirds of the way should do it" (Gohan, guide line 2231). Majin Buu goes from 14640 (vs Vegeta) to 45000 (vs Super Saiyan 3 Goku, "over in under ten seconds" if leveled). Spopovich and Yamu is a 2-on-1. So Buu's Fury shows the hero's strength by **raising the hero**, with bar slices. LoG II also uses the **weak twin** (dream Frieza). Both support a trial Jr type.

**Scouter.** The dream Frieza has no scouter entry; the scan shows type 42's numbers (C). So the v5 side effect (the trial Jr is not scanned) has a vanilla precedent. A scouter entry for the trial type is also possible: entries 13 and 14 show that two entries can share a name and a set (C).

### Designs

Four designs. Each keeps the 7-Jr spawn, the relay fights (except C), the v5 AI copy and the "You wretched child" flow. Hit counts are C model for Rage Gohan at level 40; in-play feel is S.

#### Design A: my "1 v 1, then 1 v 3"

- **What the player sees.** After the Rage transform, one Jr drops in (item 13). Gohan beats it. On its death the other 3 flash down from the top at once (items 14-16). Then the fade, "You wretched child", Cell.
- **Waves:** 1, then 3. At most 3 Jrs in reach.
- **Stats and AI:** the v5 trial type with **HP 1200** (dial: 900, 1200 or 1500). STR/POW/END 46/50/46 kept. v5 AI kept.
- **Precedent:** the vanilla relay builds the next Jr from a death event while no enemy is alive: item 8's death table `rom:0x3E9E24` runs `ext 84 (9)` (CJR, C). The trial's record X already builds 4 items in one scene (CJT, CJ2, C). A lower-HP twin: Perfect Cell vs Trunks (x0.79-0.85), Gero (x0.68); HP 1200 is x0.24, between those and the dream Frieza (x0.07).
- **Not a precedent:** the `push 3 ; ext 84` in Android 17's table `rom:0x3E6078` seq 1 and Perfect Cell's table `rom:0x3E77B0` seq 15 builds an NPC, not an enemy. Item 3 on map 11,6 (`rom:0x4066BC`) is NPC factory `0x0800D6DF` with set 28 (Imperfect Cell); item 3 on map 12,6 (`rom:0x406FC4`) is factory `0x0800B711` with set 137 (Vegeta) (C bytes). Vanilla boss rounds use a map reload (17: maps 11,4, 11,5, 11,6) or `ext 104` on the beaten actor.
- **Reuses:** v4 spawn copy, items 13-16, records X, C, N, table T, the v5 type and AI.
- **New work:** data and script only. The type HP word (4 bytes). Record X builds only item 13. Counter record C gets a branch: death 1 runs a new wave record W (flash, `ext 84` x3, walk-in as in v2); deaths 2-3 end; death 4 goes to word 29.
- **Risk: low.** Wave 2 is built when no Jr is alive, as in the vanilla relay. Deaths 2-3 still run C with live Jrs, as v1-v5 do today.
- **Dial:** the wave-1 Jr can keep type 26 (HP 4990, 16.8 punches, a real 1 v 1 duel as in Design D), and wave 2 uses the trial type at a lower HP. That is one more type word, not a new design.

| HP | Punches a Jr | Total | Jr punches to KO Gohan |
|---|---|---|---|
| 900 | 3.0 | 12 | 28 |
| **1200** | **4.0** | **16** | 28 |
| 1500 | 5.1 | 20 | 28 |

- 16 punches equals the vanilla 4-ninja groups on maps 2,35-2,38 (CJB: 4.0 punches each) and is under Cell's 26.

#### Design B: manga beat for beat, 4 Jrs

- **What the player sees.** Jr 1 dies to one punch, as in chapter 408. Then 2 Jrs rush in. The last Jr does not melee: it backs off and shoots, and Gohan chases it down ("tries to flee").
- **Waves:** 1, then 2 brawlers plus 1 runner.
- **Stats and AI:** Jr 1 HP 230 (Gohan's lowest punch is 231, so always one punch, C model). Brawlers HP 600 (2 punches, 1 on a crit 22.5 % of the time). Runner HP 600 with the CJB option J "shooter" AI (never reaches a punch leaf; hovers 72-120 px; blasts).
- **Precedent:** dream Frieza (a story enemy made very weak, same AI 21). The shooter AI is built from vanilla nodes (CJB design, C).
- **Reuses:** A's wave wiring; the v5 AI for the brawlers.
- **New work:** 2 more type entries, the shooter AI copy (about 320 bytes, CJB), wave records.
- **Risk: medium.** The runner AI is untested (CJB: S for the end game "2 shooters that back away"). Total about 7 punches, so it may read as trivial, which the merge design calls a defect (design section 1).

#### Design C: canon 7, the relay Jrs survive

- **What the player sees.** Piccolo, Vegeta and Trunks beat their Jrs, but each Jr gets back up and returns to Cell, as in canon (no fighter kills a Jr). Gohan then fights all 7: 1, then 5 at once, then 1 that runs.
- **Stats and AI:** relay Jrs: a trial type with the boss descriptor `0x086FF3C4`, so the Jr stays on the map at HP 0 (C, Android 18 precedent). Gohan's Jrs: HP 600, v5 AI.
- **New work:** large. Relay death tables get a "stands up, flies back" record. 3 more fight items (spawn list 18 to 21, above the vanilla maximum of 19, L risk) or re-use items 13-16 with `ext 84` twice (L: the builder has no "already built" test, CJR). OBJ VRAM: 7 NPC Jrs plus a text box overflow by about 4 units (CJR), so the Jrs must flash out before the 16 scene. Counter to 7.
- **Numbers:** 2 punches a Jr, about 14 in all. With 5 in reach, the hurt-state cap allows at most one damaging hit per 33 frames (C, BLK): 59 HP a second in, 27 regenerated, so about 29 s from full with no counterplay (C bound, L regeneration).
- **Risk: medium-high.** It changes 3 approved relay fights and is the most work.

#### Design D: one real fight, then a scripted rampage

- **What the player sees.** Gohan fights one Jr 1 v 1. When it dies, a short scene plays: Gohan blinks next to each remaining Jr, a flash and a hit sound, and the Jr is gone. Then "You wretched child".
- **Stats and AI:** the Jr can stay **type 26 (HP 4990)**: 16.8 punches, against 37 for Piccolo and 54 for Trunks (CJB). The 1 v 1 itself shows Gohan's strength. v5 AI.
- **Precedent:** every scene op is vanilla: place (`ext 53`), flash (`ext 42`), sound (`ext 46`), shake (`ext 65`), remove (`ext 52`) appear in the 17 and 18 tables (C bytes).
- **New work:** script only. X builds item 13 only; C's death 1 runs the rampage record. That record spawns 3 NPC Jrs with `ext 51 (31, x, y)`, as vanilla seq 27 does, and removes them one by one with `ext 52 (31)`. Items 14-16 stay unused.
- **Risk: low-medium.** Positions and timing need an eye in play. It is the closest to the anime's speed, but the least fighting.

### Recommendation

**Build Design A first, with HP 1200 and everything else from v5.**

| Why | Evidence |
|---|---|
| It is my idea and the manga's shape (1, then the rest) | Chapter 408 (L) |
| It is data and script only, with the vanilla relay pattern | Item 8's death table `rom:0x3E9E24` builds the next Jr with `ext 84 (9)` (CJR, C) |
| It cuts the fight from 67 to 16 punches, under Cell's 26, but keeps the Jr punch (28 to KO Gohan) | C model |
| It keeps a challenge: up to 3 Jrs in reach, with the v5 wait | CJB, CJ5 (S for feel) |

If A plays well, the next canon steps are D's rampage for the last wave (anime speed) or B's runner (the Jr that flees). Design C waits for a final decision on the relay fights.

---

## Part 2: other canon additions with no new sprites

### Ranked table

Each row reuses art already in LoG II (or official Buu's Fury art). Size: S (script or text only), M (new scene or data plus scene), L (new chapter or art port). The Label column covers the canon claim and the game claim. A canon claim from memory only is S.

| Rank | Idea | Canon | Map (where it fits) | Today in LoG II | Reuses | Work | Size | Risk | Label |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Krillin catches Android 18** when Cell spits her out | Spit: ch. 410-411, ep. 187 ("Cell spits No. 18 out of his mouth!", Kanzenshuu). The catch: memory | 14,3, Gohan's table after the spit (guide line 1236-1238) | Text "He spit out Android 18!" `rom:0x3EA567`; the guide says "18 WALKS away...Krillin doesn't go pick her up" (line 1238) | NPC Krillin `set:76` is on map 14,3 (CJR); 18 `set:11` | Walk Krillin to 18, a face turn, one line, both stand aside. Later "Great! And I'll take 18!" `rom:0x3EC1ED` still fits | S | Low | C text, L spit, S catch |
| 2 | **Trunks dies** to Cell's Death Beam; the first wish revives him | Ch. 411-413, ep. 188 ("death beam", Kanzenshuu); the death itself: memory | 14,3, self-destruct table `rom:0x3EB704` stretch | "Trunks is still alive, but barely!" `rom:0x3EAFD5`. The wish "Please revive all those on Earth who were killed by Cell!" `rom:0x3DC431` already covers him | Text only | Rewrite 2 text records (copy to the expansion if longer) | S | Low | C text, L beam, S death |
| 3 | **Cell stomps 16's head** instead of a blast | Ch. 407, ep. 184 ("Cell crushes No. 16's head", Kanzenshuu); the foot: guide line 1231 | 14,3, Gohan's table seq 19 | Blast at the head: guide line 1231 "(in the anime he STEPPED on the head)"; CJR row: seq 19 `ext 99`/`ext 100 (30, 616, 384)` | Cell `set:30` walk, shake `ext 65`, sound | Replace the blast ops: walk Cell to the head, shake and sound, remove the head | S-M | Low-medium (the head object and `ext 99` are L) | L |
| 4 | **Goku gives Cell a Senzu Bean** before Gohan fights | Ch. 402-404, ep. 181 ("Goku asks Kuririn for a senzu before throwing it to Cell", Kanzenshuu) | 14,3, Goku's give-up records (table `rom:0x3E93E8`) | No "Senzu" string in `rom:0x3E9000`-`0x3ED000` (C, one shape); the guide says "Cell's health is back to full" (line 1199) | NPC Goku `set:61`, Cell `set:30` | 2-3 text records and a walk in Goku's give-up stretch | S-M | Low | C absence (one shape), L canon |
| 5 | **Vegeta outclasses Semi-Perfect Cell** (same lever as the Jrs) | Memory | 12,4 item 1 (Tropical Islands) | Type 76 HP 4890, 39/41/46, bar (29,25,100); text "You are outclassed in every way." `rom:0x3E67E2` | Type 76 has one spawn, so an in-place change touches only this fight | Data: lower HP (and maybe STR) by the Perfect Cell vs Trunks ratio | S | Low (balance only) | C game, S canon detail |
| 6 | **Android 18 fights Vegeta**, not the current leader | Memory | 8,49 item 0 (Northern Mountains) | The 18 table branches on the leader (`call leader ; push 2 ; eq`, `rom:0x3D8C70`). The aftermath is already about Vegeta: "He is very ashamed of his defeat" `rom:0x3D9224` | `ext 70 (2)` (used by the Jr relay) | Force the leader to Vegeta before the fight | S | Low-medium (party state at map 8,49 is L) | C bytes, S canon |
| 7 | **Krillin and the shutdown remote** (he cannot use it on 18) | Memory | 12,x Tropical Islands, before Vegeta meets Cell (map not traced) | No "remote" string in the ROM (C, one shape) | Krillin 76, 18 `set:11`, 16 `set:8`, Bulma 23 | New scene with a new trigger | M | Medium (a new trigger) | C absence, S canon |
| 8 | **Vegeta's Final Flash** on Perfect Cell | Memory | 12,x, the Perfect Cell table around `rom:0x3E6D64` | Only the kick: "That kick! I put all my energy into it!" `rom:0x3E6D64` | Buu's Fury Final Flash art (the BF guide says Majin Vegeta uses it, line 1050) | Scene plus a beam art port; Cell's regrowth as a flash | L | Medium-high (art port) | C text, L asset, S canon |
| 9 | **Future epilogue**: Trunks beats 17 and 18 (and Imperfect Cell) | Memory | After the credits (guide lines 1281-1283); the future maps of the opening | The guide says it is shown after the credits. No ASCII line found | Future maps from the opening, `set:9`, `set:11`, `set:28`; types 3, 4, 60 | A playable end chapter before the Buu's Fury transition; weak twins as in Part 1 | L | High (end flow) | L guide, S canon |
| 10 | **Relay Jrs survive** (no fighter kills a Jr) | Ch. 407: "the others get pummeled" (Kanzenshuu) | 14,3 relay tables `rom:0x3E9E24`, `0x3E9E84`, `0x3EA400` | Each relay Jr dies (normal descriptor, CJR) | See Design C | See Design C | M-L | Medium-high | C game, L canon |

### Notes on each idea

1. **Krillin catches 18.** This is the cheapest visible canon fix. The scene already has Krillin on the map, and the post-fight line already has him carrying 18.
2. **Trunks dies.** The wish scene already revives "all those on Earth who were killed by Cell", so no wish text changes. Check that no later line has Trunks speak before the wish (L: the post-fight lines only carry him, `rom:0x3EC1CB` "I'll take Trunks.").
3. **The stomp.** The meaning of `ext 99` and `ext 100` is L (CJR). Read the op before the swap.
4. **The Senzu Bean.** It explains why Cell is at full HP for Gohan's fight. The guide line 1199 shows the refill already happens.
5. **Vegeta vs Semi-Perfect Cell.** The game's own text says Vegeta outclasses Cell, but the fight uses a full 4890 HP boss and the guide calls the Vegeta form "VERY sluggish". The Part 1 weak-twin lever applies here too.
6. **18 vs Vegeta.** The scene after the fight is written for Vegeta's defeat. Forcing Vegeta makes the fight and the scene agree.
7. **The remote.** It needs a new trigger point, so it is medium work.
8. **Final Flash.** It is the only idea here that needs an art port. Buu's Fury art is official, so I allow it.
9. **Future epilogue.** It gives a second "show the hero's strength" fight (Trunks against weak twins of 17 and 18, as the dream Frieza). It is the largest idea. Find where the after-credits text lives first.
10. **Relay Jrs survive.** This is Design C. It is canon, but it reworks 3 approved fights.

**Already canon in LoG II (no work):** 16 beats Imperfect Cell ("16 squashed the bug!" `rom:0x3E54D2`), Tien's stand (`rom:0x3E5B5B`), the 18 kiss, Krillin's second wish ("THAT WISH CANNOT BE GRANTED NOW." `rom:0x3DCABB`), Gohan protects Vegeta (`rom:0x3EB1C9`), Goku's sacrifice and the telepathy lines (C text).

**Kept as game-isms (not proposed):** the 3 Gero rematches (type 7) and the Northern Mountains generators. They are not canon, but they are gameplay.

**My own items (not repeated here):** the two Time Chamber fights (Buu's Fury chamber assets) and Grade 2/3 Trunks and Vegeta. Idea 5 touches the same fight as Grade 2 Vegeta, so plan them together.

---

## Open questions for me

1. Design A, B, C or D? The recommendation is A.
2. Jr HP for A: 900 (12 punches in all), 1200 (16) or 1500 (20)?
3. Keep the Jr punch as is (28 punches to KO Gohan), or also lower STR to 40 (35 punches)?
4. Should the trial Jr show in the scouter? Vanilla's dream Frieza does not (C). A new scouter entry is possible.
5. Part 2: which ideas go on the queue? The top 4 are S size.

## Files

| File | What |
|---|---|
| `type_census.py`, `type_census.txt` | All enemy types 0-108, spawns by map and item, scouter entries |
| `event_tables.py`, `event_tables.txt` | Death tables of 18, 17, 20, Perfect Cell vs Trunks, dream Frieza |
| `design_numbers.py`, `design_numbers.txt` | Hit counts both ways (uses the CJB damage port) |
| `strings_range.py`, `strings_cellgames.txt`, `strings_islands_perfect.txt`, `strings_wishes.txt`, `strings_wishes2.txt`, `text_probe.py`, `text_probe.txt` | Story text scans |
| `bible_rows.md` | DID rows |

All in `scripts\one-time\2026-10-29-design-ideas\`. Web sources: kanzenshuu.com/wiki/Cell_Jr, kanzenshuu.com/wiki/Dragon_Ball_Chapter_408, kanzenshuu.com/wiki/Dragon_Ball_Z_Episode_184, kanzenshuu.com/wiki/Dragon_Ball_Z_Episode_185, kanzenshuu.com/wiki/Dragon_Ball_Z_Episode_186, kanzenshuu.com/wiki/Dragon_Ball_Z_Episode_188, kanzenshuu.com/forum/viewtopic.php?p=66365.
