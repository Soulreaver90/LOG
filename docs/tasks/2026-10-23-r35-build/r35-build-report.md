# r35 build report: Super Perfect Cell scouter text and +10% stats

Brief: `docs\tasks\2026-10-23-r35-build\r35.md`. Base: r34 `b5d3279a2af469321e272ebc6089d1c3697f390d` (the in-memory build equalled the r34 file before any edit). Built 2026-10-23 7:54 PM (build-log time). Labels: CONFIRMED (C), LIKELY (L), SPECULATIVE (S).

| SHIPPED | Where |
|---|---|
| Entry 19 has its own text, my words verbatim, in entry 13's format | `builds\log2_poc_r35.gba`, patch `superperfect_cell` step 7 |
| Text fit: 13 lines on a scrolling page (entry 13 has 14, vanilla most 21) | Section 1, mocks `scripts\one-time\2026-10-23-r35-build\fit_text_19_*.png` |
| Enemy type 25 stats: HP 9050, STR 66, POW 65, END 72 | Step 8; the scan screen shows them through entry 19 +0x10 |
| Type 25 is used only by the Super Perfect Cell fight (two shapes) | Section 2 |
| Saves, states, ROM pairs at r35 names | `builds\` (exclusive create) |
| Diff proof r34 to r35 | 381 bytes in 4 runs, all named |
| Suite | 578 tests, OK, 0 skipped |

| PENDING | Why |
|---|---|
| In-game look by me | Not seen in an emulator. Fit is proved by the game's wrap model, listings, a mock-up and tests |

---

## 1. The text (decision 1)

**Encoding (C):** the game's scouter texts are plain ASCII with a 00 end. No vanilla text holds a line break (`0x0A`) or an end byte (`0x0B`); the game wraps at run time and the page scrolls. A text has no page breaks. Entry 13 puts two spaces between sentences (125 of the 146 vanilla sentence gaps do). So the new string is my text with the sentence gap doubled. **The words are mine, unchanged; only the gap between sentences follows the game.** A test collapses the double gaps and compares with the quoted text in the brief.

- New string at `rom:0x908F00`, 373 bytes with the 00, right after the name (`rom:0x908EEC`, unchanged). Entry 19 +4 (`rom:0x6F8FC0`) goes from `0x086FA869` to `0x08908F00`.
- Entries 13-18 keep the shared Perfect text `rom:0x6FA869` (415 bytes, unchanged).
- Every byte of the new text occurs in a vanilla scouter text, so every glyph exists.

**How the page works (C, listings in `scripts\one-time\2026-10-23-r35-build\listings\` and `scripts\one-time\2026-10-23-r33-build\listings\`):**

| Step | Code | What it does |
|---|---|---|
| Count lines | `@0x08018A38` (scan), `@0x0801963C` (database) loop over `@0x0801F7FC` | Width 160 px, text font `0x0802CC64`. Skip leading spaces; add glyph width + 1 per byte; past 160 px, end at the last space |
| Scroll range | same | scroll max = 16 x lines - 56, clamped at 0 |
| Canvas | `@0x08018B14`, `@0x08019320` | 160 x (scroll max + 64) bytes on the heap; first line top y 2, line step 16 |
| Draw | `text_wrapped` `@0x0801F702` | Same wrap rule as the counter |
| Show | `@0x080192D6` | A 160 x 64 window (4 lines) at the scroll position goes to VRAM `0x06009800`, the database list area; up and down arrows show when there is more |

**Fit result: it fits (C for the model and numbers, L for the look).**

| Text | Bytes | Lines | Widest line | Scroll max | Canvas bytes |
|---|---|---|---|---|---|
| Entry 13 (Perfect, vanilla) | 415 | 14 | 160 px | 168 | 37120 |
| **Entry 19 (new)** | **372** | **13** | **159 px** | **152** | **34560** |
| Entry 5 (vanilla most) | 582 | 21 | 156 px | 280 | 55040 |

- The counter and the drawer give the same line count on all 62 vanilla texts and on the new one. No line is wider than 160 px. The canvas is smaller than entry 13's, so the heap need is within what vanilla already uses.
- Lines as the game draws them: "After self-destructing, Cell / regenerated from a single / surviving cell. Analysis of his / Namek cells reveals the ability / to rebuild an entire body. The / Saiyan cells in his structure / reacted to the near-death / experience and greatly / increased his power. Electrical / discharges now surround his / body. The effect on his / power level is so drastic that it / cannot be calculated." (`scripts\one-time\2026-10-23-r35-build\text_fit.txt`).
- Mocks (3x, the database frame with name and portrait, text window at x 40, y 88): `scripts\one-time\2026-10-23-r35-build\fit_text_19_top.png` (scroll 0), `fit_text_19_end.png` (scroll max), `fit_text_19_full.png` (the whole canvas); the same for entry 13 to compare. At scroll max the top row shows a part of a line, as vanilla does for entry 13.

## 2. Stats (decision 2)

**Type 25 is only this fight (C for both shapes, S for run-time builds).** `scripts\one-time\2026-10-23-r35-build\type25_sweep.txt`:

- **Shape A (spawn data):** of 666 aligned spawn records (+0 = `enemy_factory` `0x0800E77F`, no unaligned copy), only `rom:0x4090F8` has +8 = 25. One word names it: `rom:0x409148`, item 12 of the list `rom:0x409118`, which map table entry 325 (map 14,3, the Cell Games arena) names at `rom:0x40DA94`. The story builds it with `push 12 ; ext 84` (bible row SPC).
- **Shape B (pointers):** no word, at any alignment, names a byte of the type 25 entry `0x086D5904`-`0x086D591B`. The table base `0x086D56AC` sits in 3 literal pools only: `enemy_factory` (the one builder), the info screen `@0x0801790E` and the type match `@0x080190D4` (both scouter readers).
- **Scouter:** entry 19 is the only entry with +0x10 = 25.
- **What neither shape sees:** a spawn record or a type entry pointer built in RAM at run time.
- Extra check: an aligned-word search for 8230 finds only the HP field and 4 words inside raw tile data near `rom:0x701FCC`-`0x702BDC` (pixel bytes). A script push of 8230 is a varint and this search cannot see it, so a script compare against his absolute HP is not ruled out. S.

**Bytes (C):** `rom:0x6D5908` `26 20` to `5A 23` (HP u32 8230 to 9050), `rom:0x6D5910`-`0x6D5912` `3C 3B 41` to `42 41 48` (STR 66, POW 65, END 72). AI id and the other fields stay. The patch checks the old bytes before any write.

**The scouter shows the new stats by itself (C, tests):** the info screen reads HP, STR, POW, END from the enemy type entry of entry 19 +0x10 (25). The scan screen model gives `Cell, "S. Perfect"`, portrait 52, 9050, 66, 65, 72.

- The values are mine. 8230 x 1.1 is 9053; the brief says 9050, so I used 9050.

## 3. Build, copies and diff proof

**r35:** `builds\log2_poc_r35.gba`, SHA-1 **`736c778a1d576a86143d052e8af7847fd10bbf50`**. It equals the in-memory build of `build_list.txt` (default art folders, no `LOG_*` variables). The build added one line to `docs\build-log.md`.

Copies by exclusive create (`scripts\one-time\2026-10-23-r35-build\copy_files.py`, output `copy_files.txt`). No ROM, `.sav` or state was overwritten.

| Source | Copy | SHA-1 |
|---|---|---|
| `log2_poc_r34.sav` | `log2_poc_r35.sav` | `159601a376596afbd9d4124845a3b1355b46a839` |
| `log2_poc_r34_chamber2.sav` | `log2_poc_r35_chamber2.sav` | `8b0b74f4896ba1a57666499305861f5f42c40a06` |
| `log2_poc_r34_scouter.sav` | `log2_poc_r35_scouter.sav` | `43746ae5a8a7990b7ea5ca59dcbdaca76d59176e` |
| `log2_poc_r34.ss1`-`.ss5` | `log2_poc_r35.ss1`-`.ss5` | as r34 (`copy_files.txt`) |
| `log2_poc_r35.gba` | `log2_poc_r35_chamber2.gba`, `log2_poc_r35_scouter.gba` | `736c778a1d576a86143d052e8af7847fd10bbf50` |

**Diff proof r34 to r35** (`scripts\one-time\2026-10-23-r35-build\diff_proof.py`, output `diff_proof.txt`): **381 bytes in 4 runs, 0 outside a named site. Same size.** C.

| Region | Bytes | Item |
|---|---|---|
| `rom:0x6D5908`-`0x6D5909`, type 25 HP | 2 | 2 |
| `rom:0x6D5910`-`0x6D5912`, type 25 STR, POW, END | 3 | 2 |
| `rom:0x6F8FC0`-`0x6F8FC2`, entry 19 +4 text pointer | 3 | 1 |
| `rom:0x908F00`-`0x909074`, the new text and its 00 (was `FF`) | 373 | 1 |

**States (C, state scan of RAM words naming a changed byte, the new text, the Perfect text, entry 19 or the type 25 entry):**

| State | With r35 |
|---|---|
| `log2_poc_r35.ss1`-`.ss5` | Safe: no such word |
| `log2_poc_r34_scouter.ss1` (not in the brief's list, not copied) | **Not safe:** inside the Super Perfect Cell fight (type 25 entry in RAM) with the scouter text page open on the Perfect text. The enemy keeps the HP it was built with (8230), and the old text stays until the page is reopened (L for which fields the game re-reads) |
| `log2_poc_r34_scouter.ss2` (not copied) | **Not safe:** inside the same fight, HP as above |

To test the new stats, start the fight on r35 (load the save, not a mid-fight state).

## 4. Tests

Suite: `py -3 -P -m unittest discover -s ...\scripts\permanent\tests -t ...\scripts\permanent` ran **578 tests, OK, 0 skipped** after the build and the copies (`scripts\one-time\2026-10-23-r35-build\suite_final.txt`).

| Check | Test (`test_superperfect_cell.py`) |
|---|---|
| The text decodes to the brief's quoted text (double gaps collapsed); stored bytes = that text with two spaces per gap + 00; no break byte; vanilla glyphs only; placed after the name; only entry 19 +4 names it | `test_the_text_is_the_owner_text_in_entry_13_format` |
| Entries 13-18 keep pointer `0x086FA869`; its 415 bytes unchanged | `test_13_to_18_keep_the_perfect_text` |
| Only entry 19 +0, +4, +8, +0xC change in the table; +0x10 stays 25 | `test_only_entry_19_name_and_text_words_and_two_bytes_change` |
| Fit: counter and drawer agree on 62 vanilla texts (most 21, entry 13 has 14); entry 19 = 13 lines, each at most 160 px, scroll max 152 | `test_text_fits_the_text_page` |
| The model's constants are the code's (font, width 160, scroll formula, y 14, step 16, 160 x 64 window, last-space break) | `test_text_page_listings` |
| Stats 8230/60/59/65 to 9050/66/65/72, only bytes +4, +5, +0xC-+0xE change | `test_type_25_stats_are_up_10_percent` |
| Type 25 used once (shapes A and B), only entry 19 shows it | `test_type_25_is_only_this_fight` |
| Scan screen for entry 19 shows the new stats | `test_what_the_scan_screen_shows` |
| r34 to r35 is the text, its pointer and the 4 stat fields; r35 file = build; copies | `test_r34_to_r35_is_the_text_its_pointer_and_the_stats`, `test_r35_file_equals_the_build`, `test_r35_saves_states_and_rom_pairs_are_copies` |
| Fail closed: a changed text pointer or stat byte refuses | `FailClosedTests` (5 new offsets) |

Changed on purpose: `test_stats_unchanged` became the +10% test; `test_r34_file_equals_the_build` became the r35 one; the r32 to r33 test now takes the hook end from the notes (the name is no longer the last allocation). Backup of the two edited files before the change: `scripts\one-time\2026-10-23-r35-build\backup\`.

## 5. Changes

- `scripts\permanent\patches\superperfect_cell.py`: steps 7 and 8 (constants `OWNER_TEXT`, `SUPER_TEXT`, `TYPE25`, `STATS`; a stat check in `_check`; the text allocation after the name; note `text_19`), header lines. The Rules line "Cell's stats stay vanilla" is gone. `build_list.txt` unchanged.
- `scripts\permanent\tests\test_superperfect_cell.py`: section 4.
- Study and tools: `scripts\one-time\2026-10-23-r35-build\` (`listings\`, `text_fit.py` and `.txt`, `fit_text_*.png`, `type25_sweep.py` and `.txt`, `copy_files.py` and `.txt`, `diff_proof.py` and `.txt`, `suite_final.txt`, `bible_rows.md`, `backup\`).
- Bible rows: `scripts\one-time\2026-10-23-r35-build\bible_rows.md` (Sections 11, 12 and 14, tag R35, with a correction of the stat values in the SPC, R31 and R33 rows). `docs\RE-BIBLE.md` not edited.

## 6. My test plan

ROM `builds\log2_poc_r35_scouter.gba` with `log2_poc_r35_scouter.sav`, slot 2 (as r33 section 7).

| Beat | Expect |
|---|---|
| Select after "He's back!!!!", open his marker | `Cell, "S. Perfect"`, **HP 9050, STR 66, POW 65, END 72** |
| The text page: A on his row in the database (map 6,6, `@0x0801970A`); on the scan screen the key that opens it is not traced (L) | The new text, 4 lines at a time, down arrow; scroll to the end: "cannot be calculated." on the last line |
| A Cell Games fight before the self-destruct | Unchanged: `Cell, "Perfect"`, the Perfect text, 6500/50/55/60 |
| The fight | He has 9050 HP and hits a little harder |

## 7. Concerns

1. **I broke the no-`cd` rule.** About ten early read-only shell calls started with `cd` to the LOG root (study and listings only, before any edit). All later calls used absolute paths. No file was written by those calls except the `scripts\one-time\2026-10-23-r35-build\listings\` files and a `__pycache__` folder in `scripts\one-time\2026-10-23-r35-build\` that I deleted.
2. `log2_poc_r34_scouter.ss1` and `.ss2` are mid-fight states and are not safe with r35 (section 3). They were not in the brief's copy list, so I did not copy them.
3. Not seen in an emulator. The screen place of the text window (x 40, y 88) and the colors in the mocks are L.
4. HP 9050 is the brief's number, not 8230 x 1.1 = 9053.
5. Nothing under `data\`, `art\`, `scripts\one-time\2026-10-23-base-audit\` or `scripts\one-time\2026-10-22-superperfect-study\` was written. `inject.py` was not run.
