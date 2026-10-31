# Chapter cards v5: report (2026-10-29)

Brief: `chapter-cards-trial-v5.md` in this folder. Labels: CONFIRMED (C) = read from ROM bytes or code, or proved by a test. LIKELY (L) = strong evidence, emulator check pending. SPECULATIVE (S) = a guess. LoG II addresses are the base ROM unless the text says r39 or v5.

---

## SHIPPED

| Ask (brief) | Result | Label and proof |
|---|---|---|
| 1. Titles and Continue: update `CHAPTERS` and the tests | Done. 8 rows, your titles, flags 26, 68, 86, 127, 148, 158, 195 | C: `test_eight_rows_with_rising_flags` |
| 1. "Check that a save made between 154 and 158 cannot exist, or say what Continue shows there" | Answered below. No save is possible inside the chamber exit scene. Saves with 154 set and 158 clear do exist, because an NPC also sets 154. Continue shows Chapter 6 there, which is correct | L (no save inside the scene) and C (the NPC SET, the saves, the pick rule). See Task 1 |
| 2. Story-point cards 2-8, the BF ext 183 model, card 1 on a new game | Built. New script op ext 145 at each story point. Card 1 plays on an empty slot | C: bytes and StoryTests. L: in play |
| 2. "Prove the scene still runs: decode each changed record before and after" | Done: `v5_inserts.txt` and the StoryTests (ops, jumps, end, next index) | C: `v5_inserts.txt` |
| 3. Clash check with the five trial modules | Done. One shared range: `relay_cooldown`'s ext 70 word. Rule: run `relay_cooldown` before `chapter_cards`. Wrong order refuses with no write | C: `v5_clash_check.txt`, `ClashTests` |
| 4. Tests: 8 rows, flags rising, each insert decoded, each record ends where its ops end. Full suite once | 56 tests in `test_chapter_cards.py`, OK. Full suite: 883 tests, OK | C: `full_suite_v5.txt` |
| 5. `--list` still gives r39 | `aa51dc16...`. No build list changed | C: `test_before_is_r39`, `build_chapters_v5.txt` |
| 6. Build v5 ROM and a copy of the v4 save (exclusive create) | `builds\mockups\2026-10-25-chapter-cards\log2_poc_r39_chapters_v5.gba` and `.sav` | C: SHA-1s in Build |
| 6. A save near a story point | Slot 3 of the v5 save reaches card 7. Slot 2 reaches card 8. No save reaches cards 2-6 | C: `v5_save_census.txt` (flags). L: slot 3 route to card 7 |
| 7. Render all 8 cards as one sheet and view it. Diff runs v4 to v5 | `scripts\one-time\2026-10-25-chapter-cards\v5_cards_sheet_x2.png` (viewed). Every v4 to v5 run is inside a declared site | C: `v5_render_cards.txt` (ROM picture equals `render_card` for all 8), `v5_diff_v4.txt` (0 outside) |
| 8. Bible rows, tag CH5 | `scripts\one-time\2026-10-25-chapter-cards\bible_rows_v5.md` (sections 8, 11, 12, 13, 14) | C: file written |

## PENDING

| Ask | Why pending | My step |
|---|---|---|
| In-game check of the story cards | No emulator run. Tests run the new code in the Thumb test CPU and decode every changed record | Play steps below |
| Card 4 look | The scene has no fade there. I added a 60-frame fade out before the card and a 60-frame fade in after it (my choice, constant `RESTORE_FADE`) | Say if you want another length or no fade out |
| Cards 2-6 in play | No save in `builds\` or `test-data\saves` comes before flag 148 (C, `v5_save_census.txt`) | Play from a new game, or give me a save from that part |
| r40 order | `relay_cooldown` must come before `chapter_cards` in the r40 list | Keep that order when the lists merge |

---

## Short answer

1. **Every card plays at its story point, once.** A new script op (ext 145) shows the card and returns. Six cards play in black, right after the scene's fade out. In each of the six records, a map load op comes after the card and before any fade in or jump: ext 38 (card 2), ext 39 (cards 3, 5, 6, 7), ext 35 (card 8) (C, `v5_inserts.txt`). That this map load also restores the graphics and music is L (see "Other cards" below).
2. **Card 4 is the special case.** Its scene ends on the same map with no fade. The op reloads the map graphics the way the game does after the area map, and plays the scene's music again (C: code and tests. L: the look in play).
3. **Card 1** plays when you pick an empty slot, before the new game starts. Vanilla Continue starts the new game from the same function (C, `0x08001842 beq 0x080018CE`).
4. **Continue** still shows the card of the save's chapter, now with your 8 titles.
5. **One clash.** The ext op table is full, so the module uses a copy of it. `relay_cooldown` writes one word of the old table. It must run first. If it runs after, it refuses (C, test and combined build).

---

## The 8 cards

Story point bytes from `scripts\one-time\2026-10-25-chapter-cards\v5_records_probe.txt`. Copies and bytes after from `v5_inserts.txt` (v5 ROM). Every insert is `push N ; ext 145` = `00 0N 02 91`.

| # | Title | Continue flag | Story point (record, table word) | Bytes before (base and r39) | Bytes after (v5 copy) | Label |
|---|---|---|---|---|---|---|
| 1 | The Mysterious Youth | none | New game: Continue on an empty slot, before the vanilla new game | (hook only) | (hook only) | C (code), L (in play) |
| 2 | Preparation | 26 | Fade 120, before SET 26. Record `rom:0x3BFDB4`, word `rom:0x3BFF38` | `rom:0x3BFDBB`: `0078 0228 001a` | `rom:0x92F8C7`: `0078 0228 0002 0291 001a` | C |
| 3 | The Androids Appear | 68 | "Three years later..." fade 240, before SET 68. Record `rom:0x3B8566`, word `rom:0x3B88BC` | `rom:0x3B856D`: `00f0 0228 0044` | `rom:0x92F8F3`: `00f0 0228 0003 0291 0044` | C |
| 4 | Into Gero's Lab | 86 | End of the post-Android 20 scene, where the three fly-off branches meet (after SET 86 `rom:0x3D542A`). Record `rom:0x3D540A`, word `rom:0x3D55DC` | `rom:0x3D54FC`: `0003 0234 0001` | `rom:0x92FA8A`: `0003 0234 003c 0228 0004 0291 003c 0229 0001` | C (place), L (look) |
| 5 | A New Horror | 127 | Fade 90, Piccolo flies to Kami. Record `rom:0x3D9864`, word `rom:0x3D9968` | `rom:0x3D9867`: `005a 0228 0001` | `rom:0x92FAA7`: `005a 0228 0005 0291 0001` | C |
| 6 | Perfection | 148 | Fade 180, Roshi's Island to the Lookout. Record `rom:0x3E5ED4`, word `rom:0x3E61CC` | `rom:0x3E5ED7`: `00b4 0228 1d051202028b408640` | `rom:0x92FADB`: `00b4 0228 0006 0291 1d05...` | C |
| 7 | The Cell Games | 158 | Chamber exit time skip, fade 240 (after SET 154 `rom:0x3DB4B3`). Record `rom:0x3DB4B0`, word 0 of the live chamber exit table (r39 `rom:0x89B158`) | `rom:0x3DB4BB`: `00f0 0228 1d0402080260` | `rom:0x92FB2F`: `00f0 0228 0007 0291 1d04...` | C |
| 8 | The Champion's Hour | 195 | Fade 240 after Cell. Record `rom:0x3EC678`, word `rom:0x3EC81C` | `rom:0x3EC67F`: `00f0 0228 0001` | `rom:0x92FB4F`: `00f0 0228 0008 0291 0001` | C |

**How each record changes (C, `v5_inserts.txt`, StoryTests).**

- The record is copied to the expansion area with the insert, and its one live table word names the copy. The old record stays unchanged and is named by no live word. No table offset moves.
- The record header `{next index, 0, type 0}` is kept. That `next` value is a table index, not a length (bible row "Scene runner"). Each copy still goes to the same next table entry.
- Each copy walks to its op 17 at its new length (old length + 4; card 4 + 12). Every jump is re-encoded: card 3 `rom:0x3B85DA -> 0x3B85EF` became `rom:0x92F964 -> 0x92F979`. Card 4's two `jmp` ops land on the inserted fade out, so the card plays on all three branches (`rom:0x92FA39 -> 0x92FA8E`, `rom:0x92FA66 -> 0x92FA8E`).
- Card 8's record is 0x4D bytes, not 0x4A: `jz +3` at `rom:0x3EC6BD` jumps over the first op 17. The module walks to the op 17 that no jump passes.
- Card 4's insert point: I did not put it right after SET 86. The scene goes on after it (camera, a walk, three fly-off branches). `rom:0x3D5500` is where the branches meet, right before "HUD on", the chime and "Journal Updated!" (C, `jmp` targets).

**Cards look (C, `v5_render_cards.txt`).** Each card picture drawn from the v5 ROM bytes (BF BG palette `rom:0x5632C` plus the two text entries, base tiles, screenblock, own tiles) equals the module's `render_card`. All 8 titles fit on one line. Sheet: `v5_cards_sheet_x2.png`.

---

## How the card op works

| Part | What | Label |
|---|---|---|
| Op slot | The ext table `0x083B5D28` has 145 code words, then data (bible DS8). No word is free: only ops 87 and 92 share a handler, and none is a bare `bx lr` (`v5_ext_probe.txt`) | C |
| Table copy | 146 words at v5 `rom:0x92F678`: words 0-144 copied from the live table, word 145 = `cc_story`. The two pool words that name the table, `rom:0x921C` (op 2) and `rom:0x92DC` (ops 21-26), name the copy. After the build no ROM word names the old table | C (`test_ext_table_copy_and_its_two_names`) |
| Dispatch | The vanilla op 2 code, run in the test CPU on `02 91`, reaches `cc_story`; on `02 45` and `02 46` it reaches the vanilla ext 69 and ext 70 | C (`test_op_2_reaches_the_card_op_and_the_vanilla_ops_through_the_copy`) |
| `cc_story` | Pops N as every ext handler does, shows card N through the same scene as Continue (`scene_push`, a nested frame loop, the BF ext 183 model), then returns. N = 0 or N > 8 shows nothing | C (`test_card_op_pops_n_and_shows_card_n`) |
| Card 4 return | Row byte +3 bit 1. After the card: `0x08005F1A(0x03001090, 1)`, the call the area map return makes (`0x08004D46`-`0x08004D4C`): palettes black, BG tiles, maps, BGxCNT, blend and DISPCNT from the map. Then the scene's song plays again if one played before (card leave stops the player). Then the script's `ext 41 (60)` fades in | C (code, `test_card_4_reloads_the_map_and_plays_the_scene_song_again`), L (look) |
| Other cards | No reload. Each of the six records has a map load op (ext 35, 38 or 39) after the card, before any fade in or jump (C, `v5_inserts.txt`). Each map load reaches `0x08005F1A` (`map_load 0x0800C584 -> 0x0800C390 -> 0x08006152 -> 0x08005F1A`; ext 35's path `0x0800C664 -> 0x08006152`) and sets the map's music (`0x0800C4DE`-`0x0800C50E`) | C (BL chain), L (no branch skips it) |
| Old saves | The save format does not change. Story cards depend on no flag | C |

---

## Task 1: flags 154 and 158

| Fact | Label | Proof |
|---|---|---|
| Card 7 plays at the chamber exit time skip: record `rom:0x3DB4B0` (table index 0) runs SET 154, `ext 86 (0)`, fade out 240, then the card, then map 1,4 | C | `v5_inserts.txt` card 7 |
| In r39, SET 158 is in the same scene run: `piccolo_gi_scene` moved it to the index 31 tail, after records 35-44 and the vanilla lines (index 30). The player gets control only after the scene ends (bible NGI row: "after seq 34"), and no record in that run saves | C (bytes), L (no save op: by structure) | `piccolo_gi_scene.py` header, bible row 660 |
| So a save made inside the chamber exit, with 154 from that scene and 158 clear, cannot exist | L | Above |
| Flag 154 has a second SET site: an NPC talk table `rom:0x3CE79C`. Index 0 tests 154 (`push 154 ; ext 19 ; jz +3 ; push 13 ; end ; push 1 ; end`). Index 3 `rom:0x3CE0F8` sets it (`push 154 ; ext 27 ; push 62 ; ext 46`) | C | Bytes; holder map object `rom:0x3F9F00`, set 88 at (488,576) (which NPC and map: L) |
| Saves with 154 set and 158 clear do exist: slot 3 of `log2_poc_r28_chamber.sav`, `log2_poc_r28_chamber2.sav` and their copies (v4 and v5 saves). Map 6,16,1, flags 148, 151, 154 set, 157 and 158 clear | C | `v5_save_census.txt`, `build_chapters_v5.txt` |
| Continue there shows Chapter 6 "Perfection". That is right: the chamber exit has not played yet. Reading 154 would show Chapter 7 too early | C (pick rule, test case `(26, 68, 86, 125, ..., 154, 156, 157) -> 6`) | `test_pick_returns_the_last_set_chapter` |

---

## Task 3: clash check

Two shapes (C, `scripts\one-time\2026-10-25-chapter-cards\v5_clash_check.txt`). Shape A: each module alone on r39, its declared sites against the ranges `chapter_cards` reads or writes in the base region. Shape B: one combined build r39 + `celljr_fight` + `vegeta_ssj_scene` + `beam_struggle` + `relay_cooldown` + `fullpower_hud` + `chapter_cards`, every changed byte mapped to the module that wrote it. Module sources hashed at the run (another task edits `celljr_fight.py`): `celljr_fight.py` `adc42087...`, `vegeta_ssj_scene.py` `e576c1da...`.

| Module | Scene tables and base words it writes | Touches a chapter_cards range? |
|---|---|---|
| `celljr_fight` | Table `rom:0x3E9D4C` word 30 (`rom:0x3E9DC4`), table `rom:0x3EA400` word 30 (`rom:0x3EA478`), table `rom:0x3EB704` word 57 (`rom:0x3EB7E8`), map 14,3 spawn count `rom:0x40DA84` and list word `rom:0x40DA94` | No |
| `vegeta_ssj_scene` | Table `rom:0x3EB704` word 49 (`rom:0x3EB7C8`), table `rom:0x3EC758` word 16 (`rom:0x3EC798`), seq 52 byte `rom:0x3EB232` | No. Card 8 uses word 49 (`rom:0x3EC81C`) of the same table `rom:0x3EC758`: a different word and a different record |
| `beam_struggle` | Map 14,4 layout word `rom:0x4091EC` | No |
| `relay_cooldown` | Ext table word 70 `rom:0x3B5E40` | **Yes**: inside the ext table that `chapter_cards` copies |
| `fullpower_hud` | Super Saiyan vtable `rom:0x24C60`, HUD vtable `rom:0x2409C` | No |

Combined build (C): it builds (SHA-1 `f05a27ef...`). No range `chapter_cards` reads was changed by the five before it. The copy's word 70 = `0x08914CBD` = the `relay_cooldown` wrapper. 197072 bytes differ from r39, and every one is inside a declared site. The only overlap of declared sites is `relay_cooldown`'s word with the retired table. With `chapter_cards` first, `relay_cooldown` refuses: "ext 70 word rom:0x3B5E40 is also written by chapter_cards ...: stop and report".

The rule for r40: `relay_cooldown` before `chapter_cards` (C, `ClashTests`). The module refuses any other changed ext word that no earlier module lists.

---

## Build

| Item | Value | Label |
|---|---|---|
| r39 (list before `chapter_cards`) | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` | C |
| v4 ROM (kept) | `7f3024f4b48064a850fce65b6504fed1c9508d87` | C |
| v5 ROM `log2_poc_r39_chapters_v5.gba` | `80cf4ab9b32d0ad802858294c1cc375ad0d1a1dc` | C |
| v5 save `log2_poc_r39_chapters_v5.sav` | `8b0b74f4896ba1a57666499305861f5f42c40a06`, a copy of the v4 save | C |
| Build log | One line appended to `docs\build-log.md` | C |

| Slot | Map | Flags (of 26, 68, 86, 127, 148, 151, 154, 157, 158, 191, 195) | Continue shows | Next story card in play |
|---|---|---|---|---|
| 1 | 6,1,1 Capsule Corp | all | Chapter 8 The Champion's Hour | none (after Cell) |
| 2 | 9,1,1 Lookout | all but 195 | Chapter 7 The Cell Games | Card 8, after you beat Cell |
| 3 | 6,16,1 Capsule Corp TV room | 26-148, 151, 154 | Chapter 6 Perfection | Card 7, at the chamber exit |

Slot 3 reaches the chamber exit (L): map 6,16 region 1 holds Cell's announcement scene (bible R22 row: flag 151 set and 157 clear, as in this slot). That scene ends with the type 5 record `rom:0x3D152C` (`09 00 05 00`), whose +4 word names the chamber exit table (r39 `0x0889B158`) (C, bytes).

### Diff runs

- **r39 to v5:** 917 runs, 0 outside a declared site (C, `build_chapters_v5.txt`, `test_r39_to_new_diff_is_the_declared_sites`). Base-region runs: the hook `rom:0x23B38`, the pool words `rom:0x921C` and `rom:0x92DC`, and the 7 table words. The vanilla ext table is listed as a site with no byte changed.
- **v4 to v5:** 3592 runs (C, `v5_diff_v4.txt`). Every byte is inside a v5 site, or is v4 data that v5 no longer writes (v5 holds 0xFF there).

| Site (v5 unless noted) | Runs |
|---|---|
| BF card backdrop (moved) | 774 |
| BF song 37 port (moved) | 539 |
| Cards 2-8 (new titles, card 1 unchanged) | 2238 |
| v4 code, vtable, table (now free) | 21 |
| Hook, 2 pool words, 7 table words | 10 |
| Runs that cross two or more neighbouring sites (cards, song, backdrop, ext table copy, story records, code), some with v4-only bytes that v5 left free | 10 |
| Total | 3592 |

## Tests

| Run | Result | Label |
|---|---|---|
| `test_chapter_cards.py` | 56 tests, OK | C: test run output |
| Full suite once, `py -3.14 -P -m unittest discover` (absolute paths) | 883 tests in 187.2 s, OK, 0 failures, 0 errors. The `celljr_fight` and `vegeta_ssj_scene` tests also passed at that moment. Another task edits them, so a later run can differ | C: `full_suite_v5.txt` |

New tests:

- The 8 rows and rising flags.
- Each source record is the base bytes, with the fade right before the insert.
- Each copy is its source plus the card ops, with jumps re-encoded.
- Each copy ends where its ops end.
- The live word names the copy, and the old record stays.
- The ext table copy and its two names. Op 2 dispatch through the copy.
- `cc_story` for every N, the card 4 return, and the area map call it copies.
- New Game shows card 1.
- `relay_cooldown` before `chapter_cards` is carried. After it, it refuses.

What the tests do not cover: real hardware timing, the sound, and the field after a story card. These are the play steps.

---

## Play steps (mGBA)

1. Put `log2_poc_r39_chapters_v5.gba` and `.sav` in one folder. Open the ROM. Do not load a state (a state skips the save file and holds old code).
2. **Card 7.** Continue slot 3. Expect Chapter 6 "Perfection" on Continue. Walk into the TV room where Cell makes his announcement. After the chamber exit fade (about 4 seconds), expect "Chapter 7 / The Cell Games" for 7.5 seconds with the BF song. Then the map 1,4 time skip caption plays as in vanilla.
3. **Card 8.** Continue slot 2 (Lookout, before the Cell Games). Play the Cell Games and beat Cell. After the fade to Capsule Corp, expect "Chapter 8 / The Champion's Hour". Then Capsule Corp loads, the Hercule join check runs, and SET 195.
4. **Card 1.** Copy the ROM to a new name with no `.sav` next to it, or erase a slot. Pick an empty slot. Expect "Chapter 1 / The Mysterious Youth", then the new game.
5. **Cards 2-6.** From a new game:
   - Card 2 after "Yeah dad, let's head home."
   - Card 3 at "Three years later..."
   - Card 4 after the fly-offs that follow the Android 20 fight.
   - Card 5 after the Android 18 fight.
   - Card 6 when Goku teleports from Roshi's Island to the Lookout.

Watch for:

- **Card 4** (the only card on a live field): after the card, the map must come back with the right tiles and colours, the HUD must return, and the map music must play again. A wrong background layer offset would point at BG3 scroll, which the card sets to 0 and cannot read back (L: the field updates scroll each frame during the fade in).
- Cards 2, 3, 5-8 play in black between a fade out and a map load. The next map should load clean, with its own music.
- Continue still shows a card before every loaded save.

---

## Process note

I ran one `Set-Location` by mistake during a test run and set the shell back to its start folder at once. No file outside the scope changed.

## Files

- `scripts\permanent\patches\chapter_cards.py` (v5), `scripts\permanent\tests\test_chapter_cards.py` (v5)
- `builds\mockups\2026-10-25-chapter-cards\log2_poc_r39_chapters_v5.gba`, `.sav`
- `scripts\one-time\2026-10-25-chapter-cards\`: `v5_ext_probe.py` and `.txt`, `v5_records_probe.py` and `.txt`, `v5_save_census.py` and `.txt`, `v5_clash_check.py` and `.txt`, `build_chapters_v5.py` and `.txt`, `v5_diff_v4.py` and `.txt`, `v5_inserts.py` and `.txt`, `v5_render_cards.py` and `.txt`, `v5_cards_sheet_x2.png`, `full_suite_v5.txt`, `bible_rows_v5.md`
