# Krillin catches Android 18: scene plan (2026-10-30)

This is a study and a plan only. No module, build list, test or ROM changed.

Labels: **C** = CONFIRMED (bytes, listing or state quoted), **L** = LIKELY, **S** = SPECULATIVE. ROM facts read the base ROM `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba` unless a line names r40 or a trial ROM. Scripts and listings: `scripts\one-time\2026-10-30-krillin-18\`.

---

## SHIPPED

| Ask (brief words) | Where |
|---|---|
| "Find the spit stretch on map 14,3: the record, the bytes, the text ... how 18 appears and walks off, where Krillin (`set:76`) stands, and what plays next" | Part 1 |
| "Plan the catch with existing art only ... Name the exact insert point, the copy-and-redirect method ... every op and its args" | Part 2 (Plan A, byte exact in `s5_plan.txt`; Plan B as the in-view variant) |
| "Offer 2 drafts from the show" | Part 2, "The line" |
| "Check what the later lines assume ... and any position 18 must hold later" | Part 3 |
| "Conflicts: the Cell Jr rework also changes map 14,3 tables" | Part 4 |
| "Risk and a test plan ... a presave ... say which flag" | Part 5 |
| Bible rows, tag K18 | `scripts\one-time\2026-10-30-krillin-18\bible_rows.md` |

## PENDING

| Item | Why |
|---|---|
| My answers | "my questions" at the end. Question 1 is a canon point the sources raise |
| No emulator run | Every look, timing and in-play claim is L or S |
| The module itself (`krillin_18`) | The brief is study only. Part 2 gives the ops; Part 5 the tests |
| Me: merge the K18 rows | Rows file |

---

# Part 1: the scene as it is

## The table and its namer

The spit plays in the death event of Cell type 24 (map 14,3, item 11). One word names the table.

| Fact | Evidence | Label |
|---|---|---|
| Item 11 `rom:0x4090C8` = enemy type 24, `set:30`, cond 1, at (512,472); its event struct `rom:0x4090C0` = `{0x080106B3, 0x083EB704}` | `s4_bytes.txt` (bytes `b3 06 01 08 04 b7 3e 08`) | C |
| Table `rom:0x3EB704` has 65 record words (0-64) and word 65 = 0 (END) at `rom:0x3EB808`; seq 65's next index is 65. Its only namer is `rom:0x4090C4`. Each record of words 0-6 has one namer, its own table word | `s4_bytes.txt` section 2; bytes `e8 b6 3e 08 00 00 00 00` at `rom:0x3EB804` | C |
| Each record's +0 byte is its next index. A type 0 record that leaves one value on the stack replaces it. A word below 0x10000 ends the scene. Type 5 jumps to another table at index 0 and does not return | Bible row (runner `@0x0800B520`, R19/NGI) | C |

## Words 0-7 (base, r40 and the Cell Jr v5 trial are byte equal here)

| Word | Record | What it does | Label |
|---|---|---|---|
| 0 `rom:0x3EB704` | seq 1 `rom:0x3EA484`, 0xAF bytes, SHA-1 `91590acb...` | Cell state 3, sound 60, bar off, HUD off, fade out, **reload 14,3** `ext 39 (14,3,1,432,416)`, camera `ext 31 (320,344,30)`, fade in, Gohan attacks (`ext 57 (0,7)`, Cell hurt), `ext 42 (10)` flash, **`ext 51 (11, 464, 408)`: 18 appears**, `ext 52 (30)`, `ext 51 (29, 428, 408)` (Cell loses Perfect form), `ext 43 (10)`, Gohan walks to (432,440), faces up, `push 50 ; ext 46`, end | C (`s1_spit_base.txt`) |
| 1 | `rom:0x3EA534` type 1 p39 | "CELL: You're not a boy!  You're a monster!" | C |
| 2 | `rom:0x3EA564` type 1 p90 | "PICCOLO: He spit out Android 18!" The brief's `rom:0x3EA567` is this record's portrait byte (0x5A = 90); the text starts at `rom:0x3EA568` | C |
| 3 | seq 4 `rom:0x3EA58A`, 0x1D bytes | `ext 55 (29, 3)` Cell faces right; **`ext 53 (11, 512, 328)`: 18 walks up and right**; `ext 52 (11)`; `ext 55 (29, 0)` Cell faces down | C |
| 4 | `rom:0x3EA5A8` type 1 p39 | "I'll get you for this!!!!" | C |
| 5 | seq 6 `rom:0x3EA5C6`, 10 bytes | `push 29,6 ; ext 57` | C |
| 6 | `rom:0x3EA5D0` type 2 p39 | "...I'm going to blow myself up now! Say goodbye to your precious planet!" | C |
| 7 | seq 8 `rom:0x3EA638` | Flash, Cell becomes `set:27` (inflated), Gohan to (432,464), Tien 121, Yamcha 156, Goku 60 spawn, then every fighter flies in with `ext 54`: Krillin to (496,456) | C |

**How 18 "walks away".** `ext 53` is the walk (state 1, bible VS4 row). The camera view is x 320-559, y 344-503 (`ext 31 (320,344,30)` sets the view's top left, L by the follow-camera row). So 18 walks out of the top of the view to (512,328) and is removed (C ops, L view). She never lies down, and nobody goes to her.

> [!NOTE]
> The shared decoder `scenes.py` labels ext 53 "place?" and ext 54 "walk". By the bible rows, ext 53 is the walk and ext 54 the fly (state 1 then 12, 2 px a frame). This report uses the bible meanings.

## Where Krillin stands

| Fact | Evidence | Label |
|---|---|---|
| Map 14,3 item 6 `rom:0x408FF0` = NPC factory `0x0800D6DF`, cond 0, (448,112), `set:76`, one face-the-player step | bytes `df d6 00 08 00 00 00 00 c0 01 70 00 4c 00 ...` (`s4_bytes.txt`) | C |
| In the Rage Cell fight, after Gohan's own 14,3 reload, Krillin stands at (448,112). Vegeta 137 (296,104), Trunks 132 (256,112) and Piccolo 103 (520,104) stand at their item spots too. Tien, Yamcha and Goku are not on the map | states `log2_poc_r29.ss3`-`.ss5`, `log2_poc_r39_vegeta.ss1`, `log2_poc_r39_vegeta_v2_cj3.ss2` (`s3_actors.txt`) | C (states) |
| At the spit, Krillin is at (448,112): 184 px above the view top, out of sight | Word 0's reload rebuilds the cond 0 items as Gohan's reload does | L |
| After seq 8 he is at (496,456), facing left | my v3 state `log2_poc_r39_vegeta_v3.ss1` | C (state) |

## What plays next

Seq 9-23: Tien and Piccolo despair, Goku's Instant Transmission goodbye, Goku and Cell vanish. Seq 24-31: Gohan cries, Krillin comforts him. **Seq 32 (word 31, type 2 p73): "Android 18! I almost forgot about her. She needs our help! She's still alive!"** Seq 33 (`rom:0x3EABAC`): Vegeta faces Krillin, Krillin looks up, right, up, left. **Seq 34 (p106): "Krillin! Leave that Android alone right now! It's still alive! We should destroy it now!"** Seq 35-52: Cell returns as Super Perfect Cell, shoots Trunks, Vegeta attacks, seq 52 fades out and builds the fight (C, `s1_spit_base.txt`). In vanilla, no `set:11` actor exists from seq 4 on (C: no `push 11` actor op in words 4-64).

## What the sources say about the catch

| Source | Says | Label |
|---|---|---|
| Kanzenshuu, DBZ episode 187 | "a still-intact Artificial Human 18 emerges from his mouth and lies unconscious on the ground" | L (web) |
| Kanzenshuu, DBZ episode 188 | Cell "grabs Artificial Human No. 18's unconscious body as if to reabsorb her". After Goku's sacrifice, Krillin helps Gohan up "before noticing No. 18 still laying in the dirt. He picks her up." Vegeta demands to know what he is doing; Krillin says she did not seem to be a bad person | L (web) |
| Kanzenshuu, chapter 411 | Only the spit: "Cell then gets a weird look on his face, before finally spitting up... No. 18!" | L (web) |

> [!WARNING]
> These summaries show no catch at the spit. They show 18 lying unconscious, then Krillin picking her up **after Goku leaves**. The vanilla game already has that second beat as text only (seq 32-34). This study plans my catch as asked; my question 1 offers the source version.

---

# Part 2: the plan

## Why three words and no table copy

New lines need table slots, and the table is full (words 0-64, the END word 65, then the next record at `rom:0x3EB80C`). The usual way to add slots is a table copy with its one namer `rom:0x4090C4` repointed. That breaks stacking here (C, module code):
- `celljr_fight` (trial, runs after the main list) writes word 57 (`rom:0x3EB7E8`) of the **in-place** table and checks words 51 and 64. After a table copy, its word 57 write would land in a dead table.
- `vegeta_ssj_scene` (main) and `celljr_fight` check that each record they copy has exactly one namer. A table copy gives every record two.

So Plan A reuses slots. Word 3 (seq 4, the walk-off) becomes Krillin's line. The catch moves into a copy of seq 1. The "aside" moves into a copy of seq 6. Every next index stays as vanilla (C, `s5_plan.txt`).

## Plan A (recommended): catch, line, carry her out of view

**Method.** Copy-and-redirect, as `vegeta_ssj_scene` does: each changed word names a new record in the expansion; the old records stay unchanged and unnamed. Three base words change, nothing else.

| Word | Base address | Was | Becomes |
|---|---|---|---|
| 0 | `rom:0x3EB704` | `0x083EA484` (seq 1) | seq 1 copy + catch (247 bytes, next 1) |
| 3 | `rom:0x3EB710` | `0x083EA58A` (seq 4, 18 walks off) | new type 1 Krillin line (58 or 70 bytes, next 4) |
| 5 | `rom:0x3EB718` | `0x083EA5C6` (seq 6) | aside head + seq 6 ops (84 bytes, next 6) |

**What the player sees (beat order).**

| # | Word | Beat | Frames (estimate) | Label |
|---|---|---|---|---|
| 1 | 0 (vanilla part) | Gohan's blow, flash, 18 appears at (464,408), Cell loses his form, fade back | as vanilla | C |
| 2 | 0 (insert) | Cell faces 18. **18 reels (anim 3) while Krillin flies down from the top and lands at her right**, (488,408). They face each other; Cell faces down again | about 60 for the flight (299 px at about 5 px a frame) | C (ops), L (speed), S (look) |
| 3 | 1, 2 | "CELL: You're not a boy! You're a monster!", "PICCOLO: He spit out Android 18!" | as vanilla | C |
| 4 | 3 (new) | **Krillin's line** (my text) | text | C (record shape) |
| 5 | 4 | "I'll get you for this!!!!" | as vanilla | C |
| 6 | 5 (copy) | Cell watches; **Krillin and 18 leave up and to the right as a pair**, out of the view top (the same way vanilla 18 walked off); 18 is removed off view; Krillin stands off view; Cell faces down; Cell state 6 (vanilla) | about 34 (100 px at about 3 px a frame) | C (ops), L (off view), S (look) |
| 7 | 6, 7 ... | Self-destruct line; seq 8 flies Krillin in from (536,320) to his vanilla spot (496,456) | as vanilla | C (ops), L |

**Insert point (word 0).** In the seq 1 copy, after `push 0,1 ; ext 55` (Gohan faces up) and before the last `push 50 ; ext 46 ; end`. That is record offset +0xAA, base `rom:0x3EA52E` (C: bytes `00 32 02 2e 11` at +0xAA).

**Every op (Plan A).** Facings: 0 down, 1 up, 2 left, 3 right (C: `set:11` sheet, d0 front and d1 back; module constants).

Word 0 insert (78 bytes):

| Op | Why | Precedent | Label |
|---|---|---|---|
| `ext 55 (29, 3)` | Cell watches 18 | vanilla seq 4 head | C |
| `ext 46 (26)` | flight whoosh | before every vanilla flight (seq 48, map 8,48 pad) | C |
| `ext 63` | group open: 18 and Krillin move at once | vanilla groups | C |
| `ext 57 (11, 3)` | 18 reels: `set:11` anim 3 is 4 upright frames, head down; the state holds its last frame | vanilla 18 death record `0x083D8BC4` starts `push 11,3 ; ext 57`; NPC state 3 hold: `vegeta_ssj_scene` `ext 57 (140, 3)` | C (rows, op), S (look) |
| `ext 55 (76, 0)` | Krillin faces down for the flight | | C |
| `ext 121 (76, 12)` | fly pose; `set:76` row 12 exists in all 4 directions (the state 12 enter has no null check) | VS4 Cell dash `ext 121 (58, 12)` | C |
| `ext 136 (76, 488, 408, 500)` | flies from (448,112) to 18's right, about 5 px a frame | VS4 `DASH_N` 500 | C (op), L (speed) |
| `ext 64` | group close | | C |
| `ext 121 (76, 0)` | Krillin stands | r40 post-Cell seq 20 copy `ext 121 (58, 0)`, `ext 121 (0, 0)` | C |
| `ext 55 (76, 2)`, `ext 55 (11, 3)` | they face each other | | C |
| `ext 55 (29, 0)` | Cell faces down again | vanilla seq 4 tail | C |

Word 5 copy (84 bytes; header `06 00 00`):

| Op | Why | Label |
|---|---|---|
| `ext 55 (29, 3)`, `ext 55 (76, 1)`, `ext 55 (11, 1)` | Cell watches; both face the way they leave | C |
| `ext 46 (26)` | whoosh | C |
| `ext 63` ; `ext 121 (76, 12)` ; `ext 136 (76, 536, 320, 300)` ; `ext 136 (11, 512, 320, 300)` ; `ext 64` | one group, the same vector (+48, -88) and speed, so they move side by side. `ext 136` keeps 18 in her reel pose (VS4: ext 136 keeps the state on an NPC). 18's end spot is near the vanilla walk-off spot (512,328) | C (ops), L (pair timing), S (reads as "carried") |
| `ext 52 (11)` | 18 removed while off view | C (op), L (off view: y 320 is 24 px above the view top) |
| `ext 121 (76, 0)` | Krillin stands, off view, until seq 8 flies him in | C |
| `ext 55 (29, 0)`, then the vanilla `push 29,6 ; ext 57` | Cell faces down and powers up as in vanilla | C |

Full bytes, decoded back, are in `s5_plan.txt` (built with the `piccolo_gi_scene` encoders, decoded with `sites.dis`). Total new bytes: 389 with draft 1. The seq 1 copy equals the source around the insert (C).

**Why Plan A is low risk.**
- OBJ VRAM: 18 lives from word 0 to word 5, as in vanilla (word 0 to word 3). She is gone before seq 8 builds Tien, Yamcha, Goku and the 64-unit `set:27`. Krillin's slot exists in vanilla too (he is an item actor). So the OBJ use is the vanilla use (L, the CJR pool model).
- Later lines still fit (Part 3).
- Base writes: 3 words. No other module writes them or their records (Part 4).

## The line (I pick the words)

The sources quote no line for this beat (Part 1). So both drafts are mine, in the game's Krillin style (type 1, portrait 73, `!KRILLIN: ` prefix as `rom:0x3EAA5A`). A type 1 record holds `0x0B` box breaks (Tien `rom:0x3EA702`, C). Labels: S (not quotes).

| Draft | Text | Size |
|---|---|---|
| 1 | "!KRILLIN: Got her!" / "She's out cold... but she's alive." | 58 bytes |
| 2 | "!KRILLIN: Hang on, 18! I've got you!" / "I'll get her somewhere safe." | 70 bytes |

Draft 2 fits Plan A best: it says where he takes her. Draft 1 fits both plans.

## Plan B (the in-view variant): she stands aside until Cell's fight

Plan B shows 18 at the side through Goku's goodbye and Vegeta's "Leave that Android alone". It is the brief's "both stand aside" read literally.

| Change from Plan A | Cost | Label |
|---|---|---|
| Word 5 copy: the pair moves to a side spot **in** the view (for example 18 (536,480), next to Krillin's seq 8 spot (496,456)); no `ext 52 (11)` | none | C (ops), S (spot) |
| Remove 18 in seq 52 (word 51 `rom:0x3EB7D0`): a copy of the **as-built** seq 52 with `push 11 ; ext 52` after `push 76 ; ext 52` | (1) `celljr_fight` checks word 51 = `0x083EB21C` and raises if it changed: the build order must be main, then `celljr_fight`, then `krillin_18`. (2) `vegeta_ssj_scene`'s in-place byte `rom:0x3EB232` (140) and `superperfect_cell`'s two set 58 bytes in seq 52 become dead in place; the copy carries them, and a K18 test must check that | C (module code) |
| Optional: copy seq 33 (word 32) so Krillin's look-around ends facing her | one more word | C |
| OBJ: +16 units through the seq 8-22 peak: about 460 of 492 with a 224-unit text box open | a text box that finds no contiguous block draws garbage tiles (no -1 test, CJR) | L (model), medium risk |

`set:11` has no lying frame (anim 3 is upright, C rows and sheet), so in Plan B she stands, head down.

---

# Part 3: what later lines assume

| Line | Where | Assumes | Fits Plan A | Fits Plan B | Label |
|---|---|---|---|---|---|
| "Android 18! I almost forgot about her. She needs our help! She's still alive!" | word 31, `rom:0x3EAB5C` type 2 p73 | 18 is somewhere near and alive. Seq 33 then has Krillin look around | Yes: he set her down off view. "I almost forgot about her" reads a little odd right after the catch (my question 5) | Yes, better: she is on screen | C (text), S (reading) |
| "Krillin! Leave that Android alone right now! It's still alive!" | word 33, `rom:0x3EABE8` p106 | Krillin is busy with 18 | Yes | Yes | C (text) |
| "Great!  And I'll take 18!" | map 14,4 table `rom:0x3EC758` word 30, record `rom:0x3EC1EA` type 1 p73. The brief's `rom:0x3EC1ED` is its portrait byte (0x49 = 73); the text starts at `rom:0x3EC1EE` | 18 is with the group | Yes | Yes | C |
| Seq 30 before it: `ext 55 (76, 0)` (Krillin faces down) | `rom:0x3EC1DE` | nothing about her spot | | | C |

**Position 18 must hold later: none.** No `set:11` actor op in words 4-64 of `rom:0x3EB704` or in the 55 words of `rom:0x3EC758` (base and r40, `s1_spit_*.txt`, `s1_post_*.txt`). Map 14,4 has no `set:11` item (CGS row: NPCs 30, 137, 103, 76, 121, 156). Map 14,4 is a reload, so no 14,3 actor carries over (C bytes, L reload).

Optional follow-up (not planned): spawn 18 on 14,4 so "I'll take 18" shows her, and fly her off with Krillin in the seq 37 walk-off. That table holds records of `superperfect_cell`, `vegeta_ssj_scene`, `beam_struggle` and `npc_gi`, so it is a separate study.

---

# Part 4: conflicts and stacking

**Shared table `rom:0x3EB704`.** Every writer and checker, by module code and by byte diffs of r40 and the trial ROMs (C):

| Module | List | Words or bytes it writes | What it checks | Plan A overlap |
|---|---|---|---|---|
| `cellgames_ssj` | main | set 60 to 61 and portrait bytes inside seq 8-23 records (`rom:0x3EA679`-`0x3EA9CA`) | | none (records of words 7-22) |
| `superperfect_cell` | main | set 30 to 58 bytes in seq 40-65 records; records of words 49, 51, 64 | | none |
| `vegeta_ssj_scene` | main | word 49 (seq 50 copy), byte `rom:0x3EB232` in seq 52 | word 51 = `0x083EB21C`, one namer per copied record | none |
| `celljr_fight` v5 and the rework | trial | word 57 (seq 58 copy) | words 51 and 64, seq 52 place bytes, seq 58 and 65 bytes, item 11 spot (512,472) | none |
| `krillin_18` Plan A | new | words 0, 3, 5 | words 0, 3, 5 vanilla; records seq 1, 4, 6 SHA-1; one namer each | |

Records of words 0-6 and table words 0-7 are byte equal to base in r40, the Cell Jr v5 trial, the chapter v6 trials and the Vegeta 19 trial (`s4_bytes.txt` and a range diff, C).

**Other map 14,3 data the Cell Jr rework changes.**

| Rework site | Plan A uses it? | Stack |
|---|---|---|
| Spawn list copy and count byte (`rom:0x40DA94`, `rom:0x40DA84`) | No. It reads item 6 only through the map reload. The trial list copy keeps index 6 = `0x08408FF0` (C, v5 trial ROM) | disjoint |
| Item 11 spot check and N's `ext 84 (11)` | No write. N rebuilds item 11, whose struct still names `rom:0x3EB704`, so the K18 words run | disjoint |
| Gohan's table `rom:0x3EA400` (words 0, 30), relay tables, type 26 +0x14, items 13-17, records T, T1, K1, C, F, N | No | disjoint |
| Stand-in Jrs and beaten Jrs | Word 0's reload clears script actors before the catch (L, CJP) | no shared actor |
| Shared `set:160` row 12 (Gohan's fly row) | No: Plan A flies Krillin (`set:76`), not Gohan | disjoint |

**Tests and tools that walk the table.** A search of `scripts\permanent\art\*.py` and `scripts\permanent\tests\*.py` for `3EB704`, `SPC_TABLE`, `RETURN_TABLE`, `3EA484`, `3EA58A`, `3EA5C6`, `3EB710`, `3EB718`, `0x408FF0` and `4090C4` finds these consumers. None reads words 0, 3 or 5 in a way Plan A breaks (code read, L until the suite runs with K18):

| Consumer | What it reads | With Plan A |
|---|---|---|
| `test_superperfect_cell` `test_cell_before_the_return_stays_30` | actor pushes of set 30 / 58 in words 1-39 = 9 / 0 | Plan A adds pushes of 11, 29 and 76 only; word 0 is outside the range. Still 9 / 0 |
| `test_cellgames_ssj` `STRETCH` (`0x3EB704: 65`) | set hits for 157, 158, 60, 61; `(0x3EB704, 51, 61)` | Plan A adds none of these sets. The walk must accept a type 1 record at word 3 (word 2 is already one) |
| `test_vegeta_ssj_scene` | words 49-64 and seq 52 | untouched |
| `test_celljr_fight` | word 57 | untouched |

The search for a combined-list test ("combined") in `tests\` returned nothing. The combined build of the bible V19 row is a study script, not a test.

**Build order.** Plan A is order-free against both modules: the words are disjoint, and neither module checks words 0, 3 or 5. Each trial module allocates in the expansion, so add `krillin_18` at the end of its own list (`build_list_trial_krillin18.txt` = `include build_list.txt` + `krillin_18`), as the other trials do. A combined list (main, `celljr_fight`, `krillin_18`) only moves K18's addresses; tests read `alloc.notes`. Plan B needs main, then `celljr_fight`, then `krillin_18` (Part 2).

---

# Part 5: risk and test plan

## Risks (Plan A)

| Risk | Level | Note |
|---|---|---|
| Krillin's start spot after word 0's reload is not (448,112) | Low (L) | The states show the item spots after Gohan's reload. If wrong, the flight still ends at (488,408); only its length changes |
| Most of the flight is out of sight | L | From y 112 to the view top y 344 is about 46 of the 60 frames. The player sees 18 reel alone, then a quick drop-in. Dial: `ext 62 (76, 448, 320)` (move_to, seq 1 already uses `ext 62 (30, 428, 408)`) before the group puts him just above the view, so the whole drop is seen (97 px: about 20 frames at n 500, about 33 at n 300) |
| The pair does not read as "carried" | S | 18 slides in her reel pose next to flying Krillin. Dial: `ext 121 (11, 12)` puts her in her fly pose (anim 12, horizontal in directions 2 and 3) |
| Flight timing | L | `ext 136` speed n 500 / 300 = about 5 / 3 px a frame (VS4 model) |
| Facing ops on 18 during her state 3 hold | S | The facing may show only when the next state starts |
| "I almost forgot about her" after the catch | S | My question 5 |
| OBJ VRAM | Low (L) | Neutral against vanilla |

## Unit tests for the copied records (`test_krillin_18`)

| Test | Checks |
|---|---|
| `test_three_words_name_the_new_records_and_no_other_word_changes` | words 0, 3, 5 name the K18 records; the other 62 words equal the input ROM; namer of the table is still `rom:0x4090C4` |
| `test_seq1_copy_is_the_source_plus_the_catch` | copy[:0xAA] = source[:0xAA]; insert = `catch_ops()`; tail = `00 32 02 2e 11`; source SHA-1 `91590acb...` |
| `test_seq6_copy_ends_with_the_vanilla_ops` | header `06 00 00`; ends `push 29,6 ; ext 57 ; end` |
| `test_next_indexes_walk_0_to_7` | stack-model walk from word 0: 0, 1, 2, 3, 4, 5, 6, 7; each type 0 record leaves an empty stack |
| `test_krillin_line_is_type_1_portrait_73_ascii` | type 1, portrait 73, ASCII, ends `00`, no em or en dash, at most 2 boxes |
| `test_only_sets_0_11_29_76_are_acted_on` | every actor op in the new ops names 0, 11, 29 or 76; `set:11` rows 3 and 12 and `set:76` row 12 are nonzero in all 4 directions |
| `test_18_is_removed_off_view_before_seq_8` | `ext 52 (11)` follows the group in word 5; 18's end y + 8 < 344; no actor op names 11 in words 6-64 |
| `test_the_pair_moves_together` | same vector and same speed for 76 and 11 |
| `test_old_records_are_unchanged` | seq 1, 4, 6 bytes equal base |
| `test_no_shared_write` | no K18 site overlaps an earlier module's `sites` |
| `test_stacks_with_celljr_fight` | in memory: main + `celljr_fight` + `krillin_18`, and main + `krillin_18` + `celljr_fight`: both build; word 57 holds celljr's copy and words 0, 3, 5 hold K18's |
| Diff proof | 0 bytes outside the declared sites; `--list build_list.txt` still gives r40 |

## Presave

- Zone 14 has no save point (CGS row, C).
- A save placed on 14,3 does not help. Item 0 (type 22 Cell, cond 0) is built on every 14,3 load, and the fights after it start only from enemy deaths (C bytes, L load rule).
- Story flags do not skip fights. Flags 192-194 are set by those death events (CGS row).
- **So the closest slot is the existing preset `cellgames2_arena`, slot 3:** map 14,1,1 at (264,304), Goku leads, **`flag:191` set, `flag:192`-`flag:195` clear**. Build it with `py -3 -I scripts\permanent\rom\log2_save.py build builds\log2_poc_r40.sav builds\mockups\2026-10-30-krillin-18\log2_poc_r40_krillin18.sav --set cellgames2_arena`. The Cell Jr trial save `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr.sav` is the same preset.
- I then plays Goku's fight, Gohan's fight, the 3 relay Jrs and the Rage fight. A state saved on the trial ROM just before Cell's last quarter of HP gives quick repeats.
- Do not use the r29 states (`log2_poc_r29.ss3`-`.ss5`, in the Rage fight): they hold r29 RAM, and r39/r40 code has hooks that r29 RAM lacks (S risk, no scan done).

## What I check in play

1. After Gohan's blow and the flash: 18 reels, Krillin flies down from the top and lands at her right. Report whether it reads as a catch.
2. The two vanilla lines, then Krillin's line with his portrait.
3. After "I'll get you for this!!!!": Krillin and 18 leave up and right together and are gone; no 18 remains on screen.
4. Seq 8: Krillin flies in from the top right to his vanilla spot. Nothing else changes after that.
5. Seq 32-34 and, on 14,4, "Great! And I'll take 18!" still read well.

---

## My questions

1. **Canon.** Kanzenshuu's summaries have no catch: 18 lies unconscious after the spit, and Krillin picks her up after Goku leaves (seq 32-34 in the game). Keep the catch at the spit (Plan A), or show the source version (18 stays dazed at the spit spot; Krillin goes to her at seq 33; Plan B costs)?
2. **Plan A or Plan B?** A: she leaves the view with Krillin; 3 base words; no build-order rule; OBJ neutral. B: she stands aside in view until the Super Perfect Cell fight; a seq 52 copy, a build-order rule, +16 OBJ units.
3. **The line:** draft 1, draft 2, or your words? One record holds up to 2 boxes.
4. **18 while moved:** her reel pose (default) or her fly pose?
5. **Seq 32:** keep "I almost forgot about her", or reword it (one more word, `rom:0x3EB780`, a new type 1 record; no module writes it)?
6. **Fly-in speed:** about 1 s (`ext 121` + `ext 136`, default) or the vanilla fly `ext 54` (2 px a frame, about 2.5 s)?

## Files

All in `scripts\one-time\2026-10-30-krillin-18\`.

| File | What |
|---|---|
| `s1_spit.py`, `s1_spit_base.txt`, `s1_spit_r40.txt`, `s1_post_base.txt`, `s1_post_r40.txt` | Table `rom:0x3EB704` (65 words) and `rom:0x3EC758` (55 words), base and r40 |
| `s2_sets.py`, `s2_sets_base.txt`, `s2_sets_r40.txt`, `s2_sheet_11_76.png`, `s2_sheet_11_a3.png` | Anim rows and slots of the sets in the stretch; sheets of 18 and Krillin |
| `s3_actors.py`, `s3_actors.txt` | Actors in the 14,3 states |
| `s4_bytes.py`, `s4_bytes.txt` | Site bytes, namers and per-build equality |
| `s5_plan.py`, `s5_plan.txt` | Plan A records, byte exact, decoded back |
| `bible_rows.md` | K18 rows |

Housekeeping: two Bash calls began with a `cd`, against the brief: one into this study folder, one into `/tmp` before a read-only BOM and dash scan. Every path in both calls was absolute, and they wrote only into this folder. No other call used `cd`, and no call used `Push-Location`. Nothing was written under `data\`, `builds\`, `docs\RE-BIBLE.md`, `docs\ledger\`, `LOG\zhack\`, any patch module, build list or test. The test suite was not run (no code changed).
