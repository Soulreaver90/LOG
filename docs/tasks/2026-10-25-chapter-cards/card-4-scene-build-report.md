# Card 4 arrival scene: build report (chapters v8, 2026-10-30)

Brief: `card-4-scene-build.md`. Labels: CONFIRMED (C) = ROM bytes, listing or a test-interpreter run; LIKELY (L) = strong evidence, no emulator run; SPECULATIVE (S) = a guess.

---

## SHIPPED

| Ask | Result |
|---|---|
| 1. Scene in `chapter_cards.py` | Built in the module (no new module), first-choice trigger. Section "Build" |
| 2. Tests | Guard, Continue option c, branch per leader, text bytes, removed old card 4 point, plus two interpreter runs. `test_chapter_cards.py` 68 tests OK |
| 3. ROM | `builds\mockups\2026-10-25-chapter-cards\log2_poc_r40_chapters_v8.gba`. Every diff run sits inside a declared site. Section "Sites and diff" |
| 4. Test saves | `log2_poc_r40_chapters_v8.sav` next to it: slot 1 Gohan, slot 2 Piccolo, slot 3 Vegeta. Section "Save slots" |
| 5. Full suite | 948 tests, OK (`scripts\one-time\2026-10-25-chapter-cards\c4b_full_suite.txt`). After it, two test lines were rewrapped (no logic change); `test_chapter_cards.py` then ran again: 68 OK |
| Bible rows | `scripts\one-time\2026-10-25-chapter-cards\bible_rows_c4b.md`, tag C4B |

## PENDING

| Item | Why | My step |
|---|---|---|
| The scene in play | No emulator run. A scene item started on world map 6,99 is not vanilla (S). The card on 6,99 is open too: fade, the card's VRAM writes and register restore, then a load off the world map (bible CH8 open row) | Play steps below; watch for a world map flash or garbage between card 4 and the 8,1 fade in |
| Camera and row positions | The 8,1 camera clamp is not read | Check by eye: `ext 31 (92,44)`, row x 152-248, y 128 |
| Build log line | `docs\build-log.md` is outside this task's files | Append the v8 line, or ask me to |

---

## Build

**Why in `chapter_cards.py`:** card 4 is one chapter rule. In a second module, `_check_chapters` could not prove that every chapter 2-8 has exactly one card point.

**Why the first choice:** the interpreter showed no failure. The vanilla factory runs on the copy, and ext 23 reads bit 211. Vanilla scene items also load maps mid-table. So the first choice stands, and the 8,1 walk-in region (the report's second choice) is the fallback if play fails.

| Change | Detail | Label |
|---|---|---|
| Trigger | Region word `rom:0x3FBE54` names a copy of item `rom:0x3FBC5C` with factory `0x0800D7E1` (scene item). The trigger, rect and region condition (flag 86) are the same. The vanilla item and script stay, unnamed | C (bytes, tests) |
| Factory on the copy | The vanilla factory, run on the test interpreter, builds vtable `0x08023E44`, index 0, table = ours | C (test) |
| Table survives the load | Activate `0x0800D7A0` runs the table in a nested frame loop (`scene_push`). 14 vanilla scene-item records load a map mid-table (`c4b_probe.txt` section 3) | C (listing, bytes) |
| Guard | Record 0: `push 8,1 ; ext 23`. ext 23 run on the interpreter pushes 1 with bit 211 set and 0 with it clear | C (test) |
| First landing | Fade 60, card 4, `ext 39 (8,1,1,272,128)` (load, no fade, sets bit 211), then the scene under black | C (bytes), L (play) |
| Later landings | The vanilla `ext 38 (8,1,1,272,128)`, then END | C (bytes), L (play) |
| Music after the card | `map_load_core` plays the map's music unless the same song is already playing, and card leave stops the music. So 8,1 music 2 starts | C (listing `0x0800C4E0`-`0x0800C50E`) |
| Continue option c | Pick row kind bit 1 = "also needs the visited bit": `mov r1,#0x4D ; ldrb r2,[r0,r1] ; lsl r2,r2,#28` (flags + 0x33 + 211 >> 3, bit 3) | C (tests) |
| Old card 4 point | The post-Android 20 record `rom:0x3D540A` and its word `rom:0x3D55DC` are vanilla again. No site covers them | C (test) |

**Changes from the report draft (ROM quality):**

- Record 0 loads with `ext 39`, not `ext 38`. The camera move, the HUD off and the spawns now run under black, and `ext 41 (60)` fades in on the set scene. This is the vanilla card 5 pattern (fade, card, `ext 39`). The draft's `ext 38` would fade in first and then pan in view.
- `ext 86 (0)` moved from the world map record to the arrival records, after the load. No HUD op runs on 6,99.
- Card 4 left the in-field path. On 6,99, a card with the in-field path would reload the world map graphics and restart its song just before the 8,1 load. Nothing uses that path now, so its Thumb code (map reload, song replay) and source checks are removed.
- `MAX_TRIES` 8 to 32: on r39 (the clash test) the code chunk landed in a span that stray data words name. That build needed 11 skips. r40 needs none.

**Scene table** (`landing_records()`; 17 words, 1666 record bytes):

| Index | Content |
|---|---|
| 0 | Guard (above), next 1 |
| 1 | Leader pick: 2 Vegeta goes to 4, 1 Piccolo to 3, any other value to 2 (Gohan) |
| 2, 3, 4 | HUD off, the player faces down, `ext 31 (92,44,255)`, five `ext 51 (id, x, 300)`, fade in 60, sound 26, a fly-in group to y 128, faces (Vegeta branch: the player faces left, Trunks right) |
| 5, 6 | Piccolo (portrait 3), Tien (95) |
| 7 | Exit pick: Piccolo leads goes to 14, else 13 |
| 8-12 | Vegeta (4) and Trunks (98) exchange |
| 13, 14, 15 | A fly-off group (`ext 112 (id, 26)`, `ext 54` to y -40), remove the five, `ext 33 (0)`, HUD on, END |

Rows, left to right at x 152-248 (24 px apart), y 128, the player at x 272 (S, check by eye): Gohan leads: Krillin, Tien, Trunks, Vegeta, Piccolo. Piccolo leads: Krillin, Trunks, Vegeta, Gohan, Tien. Vegeta leads: Krillin, Tien, Gohan, Piccolo, Trunks.

Text: only my words, no "NAME:" prefixes. The box splits are the report's. The test pins at most 4 lines per box and the three lines that are exactly 144 px wide.

---

## Sites and diff

| Item | Value |
|---|---|
| r40 (list before `chapter_cards`) | SHA-1 `14d6b8314f5f418f80021fe60ef8d052b5dcf2be` |
| v7 | SHA-1 `57896c9fba8cc144c1ded4306de6625710c2be82` (rebuilt byte for byte from the pre-change module, sites in `c4b_v7_sites.json`) |
| **v8 ROM** | `log2_poc_r40_chapters_v8.gba` SHA-1 `d44cf091f81c11afa975a0ae69c700202628817f` |
| **v8 save** | `log2_poc_r40_chapters_v8.sav` SHA-1 `d5a44ccc83b741f0265024fc1848dd0b134a9765` |
| New sites | Landing chunk `rom:0x93A148` +0x6DA (item `0x93A148`, table `0x93A15C`, records `0x93A1A0`); region word `rom:0x3FBE54` +4 |
| Moved sites | Code `rom:0x93A824` +0x314; story copies of cards 5-8 and the fade table shift (the card 4 copy is gone) |
| r40 to v8 | 921 runs, 0 outside a v8 site |
| v7 to v8 | 101 runs (3563 bytes), 0 outside. Every byte is inside a v8 site or reverted to r40 inside a v7 site (the v7 card 4 word and record) |

Listing: `scripts\one-time\2026-10-25-chapter-cards\c4b_build.txt`.

---

## Save slots

`log2_poc_r40_chapters_v8.sav`, made from slot 3 of `log2_poc_r40_chapters_v7_pre_a.sav` (7,18, flag 85 set, 86 clear). Each slot has flags 86 and 87 set (the post-20 scene and the Southern Continent exit are the only SETs between), map 6,99,1 at (2616,1064) inside the landing star, and visited bit 211 cleared. Each slot is resealed (checksums valid).

| Slot | Leader | Continue shows |
|---|---|---|
| 1 | Gohan | Chapter 3 (option c: no bit 211 yet) |
| 2 | Piccolo | Chapter 3 |
| 3 | Vegeta | Chapter 3 |

The Thumb pick, run on each slot image, gives card 3, and card 4 once bit 211 is set (C, `c4b_save_check.txt`). A Continue onto the world map is not a vanilla save state (L: it loads).

> [!NOTE]
> If a slot does not load on 6,99, use a 7,18 save with flag 86 set and fly out through the Southern Continent exit.

## Play steps

1. Load `log2_poc_r40_chapters_v8.gba` with `log2_poc_r40_chapters_v8.sav`. Continue slot 1, 2 or 3: card 3, then the world map.
2. Press A on the Northern Mountains star. Expect a fade, card 4 "Into Gero's Lab", then black. The view fades in on 8,1 with the camera on the row, and the team flies in from the south.
3. Check the lines: Gohan or Piccolo leading gets the Piccolo and Tien lines; Vegeta leading gets the exchange with Trunks.
4. Then the five fly north off the view, the camera returns to the player, the HUD comes on, and control returns. The 8,1 music plays.
5. Leave 8,1 to the world map and land again: a plain landing with no card and no scene.
6. Save on 8,1 and Continue: card 4.
7. Watch: the row and camera at the view edges, Vegeta's look (party id 3 shows his current form), and the text box style when the speaker leads.

---

## Notes

- Region 12 of 6,99 shares region 11's rect and flag 86 condition. Its item `rom:0x3FBC70` has factory `0x0801A6B3` and data `0xDE`: it is not a script or scene item (C). That it starts no landing, and that it is a label or marker, is L.
- Process: two early Bash calls started with `cd` into the LOG folder. The brief forbids it. No file changed by them. Four early probes ran from `LOG\scratch\`; they were deleted and the kept ones are `c4b_` files in the one-time folder.

## Files

- Module and tests: `scripts\permanent\patches\chapter_cards.py`, `scripts\permanent\tests\test_chapter_cards.py`. `build_list_trial_chapters.txt` is unchanged (the scene is in the module it already lists).
- One-time: `c4b_v7_sites.py` and `.json`/`.txt`, `c4b_probe.py` and `.txt`, `c4b_factory.py` and `.txt`, `c4b_build.py` and `.txt`, `c4b_save_check.py` and `.txt`, `c4b_full_suite.txt`, `bible_rows_c4b.md`.
