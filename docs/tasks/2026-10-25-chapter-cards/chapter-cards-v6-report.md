# Chapter cards v6: report (2026-10-30)

Brief: `chapter-cards-trial-v6.md` in this folder. Labels: CONFIRMED (C) = read from ROM bytes or code, or proved by a test. LIKELY (L) = strong evidence, no emulator run. SPECULATIVE (S) = a guess. LoG II addresses are the base ROM unless the text says r39, v5 or v6.

---

## SHIPPED

| Ask (brief) | Result | Label and proof |
|---|---|---|
| 1. Move card 5 to the flag 129 point: after fade 90 `rom:0x3DF293`, before the map 2,20 load | Done. Insert `00 05 02 91` in a copy of record `rom:0x3DF28C`. Word `rom:0x3DF764` names the copy | C: `v6_inserts.txt`, `test_card_5_is_the_kami_scene_end_before_the_time_machine_map` |
| 1. The v5 card 5 insert goes away; the 127 record is vanilla again | Word `rom:0x3D9968` = `0x083D9864` (r39 value). Record `rom:0x3D9864` equals the base. No v6 site covers either | C: `test_v5_card_5_point_is_vanilla_again`, `v6_inserts.txt` line 1 |
| 1. `CHAPTERS` row 5 flag 129, tests: flags rise, the insert decodes, every record ends where its `next` word says | Done. 60 tests in `test_chapter_cards.py` (4 new), OK | C: test run |
| 2. Clash check and the r40 order rule. Card inserts do not touch the Android 19 table `rom:0x3D40C8` | No overlap. `relay_cooldown` before `chapter_cards` still holds. `vegeta_19_reveal.py` did not exist at my run | C: `v6_clash_check.txt`, `test_android_19_table_is_untouched` |
| 3. Tests green, full suite once, `--list` gives r39 | 887 tests, OK. r39 `aa51dc16...` | C: `full_suite_v6.txt`, `test_before_is_r39`, `v6_build.txt` |
| 4. Build v6 ROM and a copy of `_pre_b2.sav` (exclusive create). Play steps | Built. Slot 1 shows Chapter 4 and leads to card 5 | C: SHA-1s below. L: the route in play |
| 5. Diff runs v5 to v6, all inside declared sites. Bible rows, tag CH7 | 93 runs, 0 outside. Rows in `bible_rows_v6.md` (sections 8, 11, 12, 13) | C: `v6_build.txt` |

## PENDING

| Ask | Why pending | My step |
|---|---|---|
| Card 5 in play | No emulator run | Play steps below |
| Card 4 | On hold (your footage review). v5 card 4 is unchanged in v6 (C: copy bytes equal v5) | Your decision |
| `vegeta_19_reveal` in the combined build | The file did not exist when I ran the clash check. My check covers the table range it will write, not its code | Run `v6_clash_check.py` again when the module exists. It picks the module up when the file imports |

---

## Short answer

1. **Card 5 now plays at the end of Kami's scene.** Piccolo says "...I'll be waiting.", the screen fades out over 90 frames, the card plays in black, then map 2,20 loads (Krillin: "We need to get Goku to Master Roshi's.") (C, bytes).
2. **Continue for card 5 reads flag 129.** A save made between the Android 18 fight and Kami's scene shows Chapter 4 (C, `chapter_for` and the pick test case `(26, 68, 86, 125, 127) -> 4`).
3. **The 127 point is vanilla again.** The post-Android 18 fade now goes straight to the world map (C).
4. **Nothing else moved in the story.** Cards 2, 3, 4, 6, 7 and 8 have the same copy bytes as in v5. The copies for 6, 7 and 8 sit at new addresses, because the card 5 copy grew (C, `v6_inserts.txt`: "same bytes as the v5 copy: True").

---

## The card 5 insert

Record `rom:0x3DF28C` is index 17 of the Kami table `rom:0x3DF720`. Map 9,6 item `rom:0x404478` names the table. The word before the table (`0x2164`) is a stray word, not word 0 (bible CH6 trap row). Index 17 is counted from the real word 0 (C, `v6_probe.txt`).

| Item | Value | Label |
|---|---|---|
| Table word | `rom:0x3DF764` (index 17). Only this word names the record (base and r39) | C |
| Record | 0x82 bytes, header `12 00 00` (next 18, type 0), SHA-1 `46ba206e3b3614e94d6394336f17a794d2cc648a`, equal in base and r39 | C |
| Bytes before (base, r39) `rom:0x3DF28F` | `0081 021b` SET 129, `005a 0228` fade 90, `1d0504280282408410 0227` push 2,20,1,160,264 ; ext 39 | C |
| Bytes after (v6 copy `rom:0x92FAA4`, from `rom:0x92FAA7`) | `0081 021b`, `005a 0228`, **`0005 0291`** (push 5 ; ext 145), `1d0504280282408410 0227` | C |
| Copy | 0x86 bytes (0x82 + 4). Header kept. 49 ops: the 47 source ops, unchanged and in order, plus the 2 new ops. No jumps in this record | C: `v6_inserts.txt` (op table) |
| Flag 129 | One SET `00 81 02 1B` in the script region (`rom:0x3DF28F`), no CLR | C: `v6_probe.txt`, `test_each_start_flag_has_one_set_site_and_no_clear_site` |

After the map load the record goes on as before: music 14, party joins, Trunks set 128, leader Trunks, spawns, fade in 90 (C, op table). Card leave stops the BF song. Then the map load and `push 14 ; ext 49` set the music again (C: bytes. L: in play).

### "Every record ends where its `next` word says"

The +0 header of a type 0 record is the next table index, not a length (bible "Scene runner" row). For each story record I checked the header against the table counted from its real word 0 (C, `test_each_record_ends_where_its_next_word_says`, `v6_probe.txt`):

| Card | Table word 0 (holder) | Index | Next | Word at next names | Gap after the record end |
|---|---|---|---|---|---|
| 2 | `rom:0x3BFDDC` (`rom:0x3F1E80`) | 87 | 88 | 0: the table ends | n/a |
| 3 | `rom:0x3B88A0` (`rom:0x3EDD64`) | 7 | 8 | `rom:0x3B860C` | 0 bytes |
| 4 | `rom:0x3D5524` (`rom:0x3FD7A4`) | 46 | 47 | `rom:0x3D550A` | 1 zero byte |
| 5 | `rom:0x3DF720` (`rom:0x404478`) | 17 | 18 | `rom:0x3DF310` | 2 zero bytes |
| 6 | `rom:0x3E6078` (`rom:0x4066E0`) | 85 | 86 | `rom:0x3E5F1C` | 1 zero byte |
| 7 | r39 `rom:0x89B158` (`rom:0x3CF7E4`, `rom:0x3D1530`) | 0 | 1 | `rom:0x3DB4D0` | 0 bytes |
| 8 | `rom:0x3EC758` (`rom:0x4090F4`) | 49 | 50 | `rom:0x3EC6C6` | 1 zero byte |

Each copy keeps the header, so it goes to the same next record (C, `test_each_copy_is_its_source_plus_the_card_ops_with_jumps_re_encoded`). The next words are unchanged in v6 (C, same test as above).

---

## Clash check

Shapes (C, `scripts\one-time\2026-10-25-chapter-cards\v6_clash_check.txt`): A = each trial alone on r39, its sites against the `chapter_cards` base-region ranges. B = one combined build r39 + `celljr_fight` + `vegeta_ssj_scene` + `beam_struggle` + `relay_cooldown` + `fullpower_hud` + `chapter_cards`. The read ranges come from `chapter_cards.STORY`, so the new card 5 record and word are in them. A site that writes by a shape other than a declared site would not show in shape A. Shape B catches it as a changed byte with no input from me.

| Check | Result | Label |
|---|---|---|
| Android 19 table words `rom:0x3D40C8`-`0x3D4170` (42 words, named by `rom:0x3FD4F4`) | No `chapter_cards` range overlaps. Bytes equal r39 after `chapter_cards`, alone and in the combined build | C (overlap, bytes), L (table end: my walk stops at the first word that is not a script pointer) |
| Android 19 records `rom:0x3D3810`-`0x3D40C8` | No overlap. Bytes equal r39 | C |
| `vegeta_19_reveal.py` | No file at my run (12:19 PM listing and the clash run). Not in the combined build | C (file listing) |
| Combined build | Builds, SHA-1 `ce6e424c...`. 197154 bytes differ from r39. Every byte has an owning module. 0 with no source | C |
| `chapter_cards` read ranges (19) changed by the five trials | None | C |
| Site overlaps | One: `relay_cooldown` ext 70 word inside the retired vanilla table, as in v5 | C |
| Wrong order (`chapter_cards` first) | `relay_cooldown` refuses, ROM unchanged | C |
| Module source hashes at the run | `celljr_fight.py` `adc42087...`, `vegeta_ssj_scene.py` `e576c1da...` (both equal the v5 run) | C |

Note on `vegeta_ssj_scene` alone: "base bytes changed 18, outside its sites 11". It runs after `celljr_fight` (its trial list order), so the 11 bytes are `celljr_fight`'s sites. The v5 script did the same (C, script).

r40 rule (unchanged): `relay_cooldown` before `chapter_cards` (C, `ClashTests`).

---

## Build

| Item | Value | Label |
|---|---|---|
| r39 (list before `chapter_cards`) | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` | C |
| v5 ROM (kept) | `80cf4ab9b32d0ad802858294c1cc375ad0d1a1dc` | C |
| v6 ROM `builds\mockups\2026-10-25-chapter-cards\log2_poc_r39_chapters_v6.gba` | `6e024850f49243c5d0482db1c780359e133c94f5` | C |
| v6 save `log2_poc_r39_chapters_v6.sav`, a copy of `log2_poc_r39_chapters_v5_pre_b2.sav` | `8bd87bfcda7cb96edaef74dc7defb447db6953fe` (equal to the source) | C |
| Both written with `open(path, "xb")` | Neither file existed before (checked) | C |
| Build log | One line appended to `docs\build-log.md` | C |
| Build list | No list changed | C |

| Slot | Map | Card flags set (of 26, 68, 86, 125, 127, 129, 145, 148, 154, 158, 195) | Continue shows | Next story card |
|---|---|---|---|---|
| 1 | 8,48,1 | 26, 68, 86, 125 | Chapter 4 Into Gero's Lab | Card 5, after the fight, the flight and Kami's scene |
| 2 | 11,1,1 | 26, 68, 86, 125, 127, 129, 145 | Chapter 5 A New Horror | Card 6 |
| 3 | empty | | Chapter 1 (new game) | Card 1 |

C: `v6_build.txt`.

### Diff runs

- **r39 to v6:** 918 runs, 0 outside a declared site (C, `v6_build.txt`, `test_r39_to_new_diff_is_the_declared_sites`). Base-region runs: hook `rom:0x23B38`, pool words `rom:0x921C` and `rom:0x92DC`, and the 6 base-region table words (`rom:0x3BFF38`, `0x3B88BC`, `0x3D55DC`, `0x3DF764`, `0x3E61CC`, `0x3EC81C`). Card 7's word is `rom:0x89B158`, in r39's expansion area.
- **v5 to v6:** 93 runs, 0 outside (C, `v6_build.txt`). Each byte is classed as one of: inside a v6 site, or inside a v5 site with the v6 byte equal to r39 ("reverted").

| Class | Runs |
|---|---|
| v6 code block (moved from `rom:0x92FB9C` to `rom:0x930148`) | 28 |
| Reverted: the old v5 code block area | 27 |
| v6 card 5 story record (new bytes in the old v5 card 5 copy area) | 14 |
| v6 card 6 story record (moved) | 12 |
| Runs that cross two neighbouring sites (story copies 5-8, v5 code area) | 4 |
| Reverted: `rom:0x3D9968` (v5 card 5 table word, back to `0x083D9864`) | 1 |
| Table words: card 5 `rom:0x3DF764`, card 6, card 7, card 8 (new copy addresses) | 4 |
| Hook word `rom:0x23B38` (code moved) | 1 |
| Ext table copy word 145 (code moved) | 1 |
| Card 8 story record | 1 |
| Total | 93 |

The card art, song and backdrop did not move (C: the same site addresses as v5).

Why the code block moved past a gap (C, `notes["chapter_cards"]["skipped"]` from an in-memory build): the card 8 copy ends at `rom:0x92FBED`. The code chunk rule skipped `rom:0x92FBF0` (named by the ROM word at `rom:0x9ECC`) and `rom:0x92FE9C` (named at `rom:0x9ECC` and `rom:0x6EA45C`). So the code went to `rom:0x930148`. Those two chunks stay 0xFF. I did not check why the v5 chunk at `rom:0x92FB9C` passed the same rule (S: the naming words reach only the higher addresses).

---

## Tests

| Run | Result | Label |
|---|---|---|
| `test_chapter_cards.py` | 60 tests, OK (v5: 56) | C: test run |
| Full suite once, `py -3.14 -P -m unittest discover` (absolute paths) | 887 tests in 156.3 s, OK, 0 failures, 0 errors | C: `full_suite_v6.txt` |

Changed in the tests: `WANT_CHAPTERS` row 5 = 129, `SET_SITES` 129 at `rom:0x3DF28F` (replaces 127), `STORY_WANT[5]` and `FADE_BEFORE[5]` = the 129 record, a pick case for 127 set and 129 clear (Chapter 4).

New tests:

- `test_each_record_ends_where_its_next_word_says`: the table above, from the real word 0 and its holder word.
- `test_v5_card_5_point_is_vanilla_again`: word `rom:0x3D9968` and record `rom:0x3D9864` equal the base. No site covers them.
- `test_card_5_is_the_kami_scene_end_before_the_time_machine_map`: source and copy bytes.
- `test_android_19_table_is_untouched`: no site, story word or story record overlaps the table or its records, and the bytes equal r39.

The tests do not import `vegeta_19_reveal` (another task writes it now).

---

## Play steps (mGBA)

1. Put `log2_poc_r39_chapters_v6.gba` and `log2_poc_r39_chapters_v6.sav` in one folder. Open the ROM. Do not load a state (a state holds old code).
2. Continue slot 1. Expect the Chapter 4 "Into Gero's Lab" card, then Vegeta on map 8,48 (C: flags; L: play).
3. Press A at the start point. You fly to 8,49, the Androids talk, and the Android 18 fight starts. Win it.
4. The post-fight scene plays. After its 90-frame fade, expect **no card**. The world map loads with Piccolo as leader (C: the 127 record is vanilla).
5. Fly to the Lookout and land. Walk into the building and through the first door (map 9,6, Kami's throne room). The scene starts when you arrive: "KAMI: Piccolo. You've returned." (C: bytes. L: fires on arrival).
6. Read through the talk. After Piccolo's "...If you need more time, then take it. I'll be waiting.", the screen fades out over 90 frames. Expect "Chapter 5 / A New Horror" for 7.5 seconds with the BF song (L).
7. Then map 2,20 loads, the music changes, and the scene goes on with "KRILLIN: We need to get Goku to Master Roshi's." Trunks joins (L).

Watch for: map 2,20 loads clean, with its tiles and colours, and the music after the card. A save made on the Lookout before the throne room shows Chapter 4 on Continue (C, pick rule).

---

## Process note

I ran one `cd` into the LOG root inside a Bash call, for a read-only Python word search. The brief forbids `cd`. No file changed by it. All other calls used absolute paths.

## Files

- `scripts\permanent\patches\chapter_cards.py` (v6: `CHAPTERS` row 5, `STORY[5]`, header), `scripts\permanent\tests\test_chapter_cards.py` (v6)
- `builds\mockups\2026-10-25-chapter-cards\log2_poc_r39_chapters_v6.gba`, `.sav`
- `scripts\one-time\2026-10-25-chapter-cards\`: `v6_probe.py` and `.txt`, `v6_clash_check.py` and `.txt`, `v6_build.py` and `.txt`, `v6_inserts.py` and `.txt`, `full_suite_v6.txt`, `bible_rows_v6.md`
