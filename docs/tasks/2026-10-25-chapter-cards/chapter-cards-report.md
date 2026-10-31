# Chapter title cards: trial report (2026-10-25)

Brief: `chapter-cards-trial.md` in this folder, plus the coordinator messages of 11:04 AM, 11:23 AM and 11:40 AM. Labels: CONFIRMED (C) = read from bytes or code, or proved by a test. LIKELY (L) = strong evidence, emulator check pending. SPECULATIVE (S) = a guess. LoG II addresses are the base ROM unless the text says r39 or new. BF addresses are the Buu's Fury (USA) ROM.

---

## SHIPPED

| Ask (brief and my words) | Result |
|---|---|
| 1. BF chapter card study, render to PNG | Done. The real BF card is script ext 183, not `0x0803369E` (that is the credits roll; the BFP row is wrong). Backdrop render `scripts\one-time\2026-10-25-chapter-cards\bf_card_backdrop_x2.png` (right picture, wrong palette, see PENDING) |
| 2. Music port path | Design only. "Plays as is" is not proved. Stand-in: LoG II song 25 |
| 3. Map each chapter to its flag or event, with a start point (11:23 AM) | Done for 10 cards. Perfection has no clean start: drop or merge proposed. My cards 5 and 6 swap to the LoG II order |
| "Review the BF chapter break placement and copy that logic" (11:40 AM) | Done for 6 of 12 BF chapters. Section "BF chapter break pattern" |
| 4. Trial module and tests | `scripts\permanent\patches\chapter_cards.py`, `scripts\permanent\tests\test_chapter_cards.py` (27 tests, all pass) |
| "Continue from file select shows the card for the save's current chapter" | Built |
| "Titles are one table `CHAPTERS = [(number, title, start flag), ...]`" | Built (top of the module) |
| "Two centred lines, about 128 frames or until A or B" | Built: 16 frames fade in, 128 hold, 16 fade out; A or B ends the hold |
| My titles, ASCII, widths reported (11:04 AM) | Done. All fit 224 px. Widest "A Warning from the Future" 144 px |
| 5. `build_list_trial_chapters.txt` | Created. `build_list.txt` not changed, so `--list` still gives r39 |
| 6. Build and save | `builds\mockups\2026-10-25-chapter-cards\log2_poc_r39_chapters.gba` and `.sav` (exclusive create) |
| 7. Full suite once, diff runs | 798 tests, OK, 0 skipped. Diff runs listed below |
| 8. Bible rows, tag CHC | `scripts\one-time\2026-10-25-chapter-cards\bible_rows.md` (sections 8, 9, 11, 12, 13, 14) |
| Story-point triggers: "design them, do not build them" | Designed below. Not built |

## PENDING

| Ask | Why pending | My step |
|---|---|---|
| "Carry over the same backdrop" | The BF backdrop palette is not found (two searches failed). The trial card uses a black backdrop | In mGBA, at any BF chapter card, open Tools > Palette view and export the BG palette, or save a state there. Give me the file |
| "And music" (BF song 37) | The LoG II engine may not play the BF data as is. Needs a listening test after a port | Approve the port design below, then listen to a test build |
| BF timing | BF holds about 450 frames (100 fade in, 250 wait, 100 fade out) with no skip (L). The brief asked for about 128 frames plus A or B. I built the brief's numbers as constants `FADE` and `HOLD` | Pick BF timing or the brief timing |
| GameFAQs walkthroughs (11:40 AM) | WebFetch returned HTTP 403. I did not route around the block. The only local copy (`docs\research\sources\gamefaqs\faq30758.txt`) is a scouter guide with no story sections | Save the walkthrough pages as text under `docs\research\sources\gamefaqs\` if you want them read |
| The other 6 BF chapter breaks | Not in plain script bytes by my two shapes. LIKELY inside compressed script containers | None now |
| Final card list | Perfection drop or merge, and the 5/6 order, are proposals | Pick (section "Chapter table") |
| In-game check | Every runtime claim below is from tests and listings, not an emulator | Steps in "What to watch in play" |

---

## BF card facts

| Fact | Label | Proof |
|---|---|---|
| The BFP row and survey pick 4 name the wrong scene. `0x0803369E` is the credits roll | C | Constructor `0x080335BC` stores 0x54B (string 1355 "Webfoot Technologies, Inc.") at +0x10. Tick `0x0803377C` (vtable `0x08049338` +0x14) shows each string pair for 0x80 frames (`0x080337B8 cmp r0,#0x80`) and steps to 0x5A9 (1449 "***") |
| The chapter card trigger is ext 183 `0x08003126`, script bytes `1D 03 88 08 96 xx 96 yy 02 B7` | C | It pops (516, line 1 id, line 2 id), stores the ids in `[0x03001030]` +0 and +4, and runs script table `0x0879B704` entry 516 = `0x0879B038` through `0x08012588` |
| Card script: map load zone 0 area 96 (`push 0,96,1,0,0 ; ext 115`) | C | Stream `0x0879B004` |
| Music: song 37 (`00 25 02 23` at `0x0879B013`); `ext 36` stops it at the end | C | Bytes |
| Text: `ext 4 ; push 120,65 ; ext 178` and `ext 5 ; push 120,85 ; ext 178`: line 1 at y 65, line 2 at y 85, x 120 | C (bytes), L (x 120 = centred) | Ext listings `bf_card_ext_ops.txt` |
| Timing: `push 100 ; ext 121`, `push 250 ; ext 136`, `push 100 ; ext 120` | C (bytes), L (121 = fade in, 120 = fade out) | |
| No A or B skip in BF | L | Ext 136 tick `0x08019594` only counts down |
| Chapter strings 1450-1473, pointer table `0x0806BCE8`, ext 222 converts | C | |
| Backdrop map entry 29 `0x0808E938`; screenblock `0x0829B988` (raw cells 0-599, 30 x 20); tiles through my atlas (raw 4-599 = global tile 37756 + raw, banks 147-149) | C | `bf_card_backdrop.png` shows Dragon Balls and the DBZ logo |
| Backdrop palette | not found | `rom:0x5652C` is wrong for this map. Searches: `bf_card_palette_search.txt` |

---

## BF chapter break pattern

Found by shape A (op 29 list `1D 03 <v> <v> <v> 02 B7`) and shape B (`02 B7` after a chapter id pair 1450-1473): 6 sites. A card called another way (for example from compressed script data) would not appear. Source `scripts\one-time\2026-10-25-chapter-cards\bf_chapter_sites.txt`.

| BF chapter | Card site | Where it starts | Kind of moment | Label |
|---|---|---|---|---|
| 1 The Other World | `rom:0x780433` | New game: card, then music 15, map load (0,2,0,0,0), fade in | Game start, map arrival | C |
| 2 Great Saiyaman | `rom:0x78291F` | After `ext 29 ; fade out 100`; then `ext 119 (2,1,0,136,112)`, fade in 100, wait 60 | Time skip and map change | C |
| 3 World Tournament | `rom:0x780C6F` | After `fade out 100`; the record ends | Scene end, next scene | C |
| 4 Babidi | not found | | | |
| 5 Majin Vegeta | `rom:0x78F32B` | After `fade out 50`; then `ext 154`, end | Scene end | C |
| 6 Dragonballs | not found | | | |
| 7 Majin Buu | not found | | | |
| 8 Janemba | not found | | | |
| 9 Super Buu | `rom:0x77EA84` | After waits and `fade out 100`; then `ext 117`, music 15 | Scene end, music change | C |
| 10 Fusion | not found | | | |
| 11 Kid Buu | `rom:0x79818B` | After `fade out 100`; the record ends | Scene end | C |
| 12 A New Beginning | not found | | | |

Pattern (C for the 6 found): every card comes right after a fade out that ends a cutscene, and before a new map, a time skip or a new scene. No card is mid-fight. I copied this rule: each LoG II card below starts at a fade, a map arrival or a time skip.

---

## Chapter table

My titles, 11:23 AM list. Start flag = the flag the Continue trigger reads. Start point = where a story-point trigger would show the card. Each flag has exactly one SET site by shape `00 NN 02 1B` in `rom:0x3B5000-0x420000`, and no CLR shape `00 NN 02 1C` there (C, `test_each_start_flag_has_one_set_site_and_no_clear_site`). A SET written another way (op 1 varint, op 29 list) would not appear.

| # | Title | Start flag (SET site) | Start point | Kind | Label |
|---|---|---|---|---|---|
| 1 | A Warning from the Future | none (new game) | New game | Game start | C |
| 2 | The Androids Appear | 68 (`rom:0x3B8571`) | `rom:0x3B8569`: music 25, fade out 240, SET 68, map load (2,1,2,592,584), "Three years later..." | Time skip | C |
| 3 | The Secret of Dr. Gero | 86 (`rom:0x3D542A`, table `rom:0x3D5524` record [46], no fade) | Record [0] `rom:0x3D4874`: after the fight, bar off, EXP 5000, fade out 120 | Fade after a fight | L |
| 4 | Nightmare Comes True | 125 (`rom:0x3D9FDB`) | Record `rom:0x3D9FD4`, start of the Gero lab table `rom:0x3DAE6C` (126 is SET at its end, `rom:0x3DADB3`) | Scene start | L |
| 5 | Birth of a Super Namekian | 127 (`rom:0x3D986F`) | `rom:0x3D9864`: fade out 90, SET 127, world map, leader Piccolo, fade in; the Kami fusion table `rom:0x3DF71C` follows | Fade, map arrival | C |
| 6 | His Name is Cell | 129 (`rom:0x3DF28F`) | `rom:0x3DF28C`: SET 129, fade out 90, map load (2,20,1,160,264), music 14. Other choice: flag 132 at `rom:0x3E0D62` (Gingertown) | Fade, map arrival | C |
| 7 | Bow to the Prince | 148 (`rom:0x3E605A`) | Table `rom:0x3E6074` record [86] `rom:0x3E5ED4`: fade out 180, map load 9,1, after the fight. The Vegeta and Trunks exit table `rom:0x3DE6F0` sets 149 | Fade, map arrival | L |
| 8 | Room of Spirit and Time | 158 (`rom:0x3DBDAA`) | Chamber exit table `rom:0x3DBDD4` seq 1 `rom:0x3DB4B0`: SET 154, fade out 240. Flag 154 has two SET sites, so Continue reads 158. r29 relocated this table to `rom:0x89B158` | Fade, time skip | L |
| 9 | The Cell Games | 191 (`rom:0x3DD32B`) | Start of the arena entry table `rom:0x3E8D98`, before `ext 104` (193 is SET after the fight starts, `rom:0x3E8D92`) | Map arrival | L |
| 10 | The Champion's Hour | 195 (`rom:0x3EC6A2`) | `rom:0x3EC678`: fade out 240, map load 6,3, SET 195, Hercule join check | Fade, map arrival | C |

**Perfection has no clean start point (C).** Flag 150 is SET at `rom:0x3E6237` inside the fight sequence ("CELL: It's you... Vegeta!"). The Perfect Cell death table `rom:0x3E77AC` starts with bar off and EXP 40000, and its record [15] `rom:0x3E76EC` sets 151 at `rom:0x3E7766`. Both are mid-fight. Proposal: drop it (the build does), or merge it into card 7 as one title.

**Order 5 and 6 swap (L).** LoG II sets the Kami fusion flag (127) before the Cell reveal flag (129). Proof: the world map landing conditions at `rom:0x3FB9BB`-`rom:0x3FBA6F` form a chain of states `86 and not 127`, `127 and not 129`, `129 and not 132` (`00 7F 02 14 00 56 02 13 04` and the same shape for the others). The anime order is Cell first.

**Story order of the start flags (L).** The module checks only that the flag numbers rise. The pick rule needs the flags to be set in table order. Evidence: the chain above (86, 127, 129), and a prefix check on every distinct slot in the build saves (6 distinct flag sets): in each slot the table flags that are set are rows 1 to k, with no gap. Two of these slots are hand-edited test saves, so this is not proof of play order.

**A different LoG II set (proposal, I pick).** The LoG II story has clean time skips and map arrivals at 68, 127, 129 and 195 (all C). If you want fewer cards with only clean fades, keep 1, 2, 5, 6, 7, 9, 10 and fold 3 and 4 into 2, and 8 into 7.

**Title widths (C, dialog font `0x0802CC64`, `card_widths.txt`).** "Chapter N" 49-57 px. Titles: 144, 112, 121, 120, 137, 84, 94, 127, 83, 111 px. Limit 224 px (8 px margins). All fit.

---

## Music port result

| Fact | Label | Proof |
|---|---|---|
| BF song 37 record `0x083A618C` {`0x083A5DFC`, sample dir `0x0836D18C`, control `0x0836D540`, 0x473}, table `0x083BB78C` | C | Bytes |
| Record and sample formats match LoG II (12-byte entries) | C | Bytes |
| Control tables are a permutation that differs in one value: BF `046170804025083407e10f69162d`, LoG II `0461807008256940070f342de10c` | C | Bytes |
| Sound update code matches in only 5 of 32 chunks | C | Byte compare |
| The player reads the sample and control tables only through record +8 and +0xC | C | No code literal names `0x0814A8A4` or `0x0814AD60` |
| `music_play` `0x08020A4C` takes (player `0x030026C8`, record pointer), so a new 20-byte record in the expansion area needs no table growth | C | `title_enter` call, card code |
| "Plays as is" | S | Engine code differs; needs a listening test |

**Design (not built).** Copy BF song 37's song data, its sample directory, the samples it uses and the BF control table to the expansion area. Repoint the internal pointers. Build one 20-byte record with the BF control table at +0xC. Set `CARD_SONG` to that record. If the LoG II player mis-plays the BF control values, use the LoG II control table instead and remap the one differing value. A listening test decides.

**Stand-in: LoG II song 25 (C).** Record `0x081D4D20` (table `0x081D4B2C` + 20 x 25). Vanilla plays it right before "Three years later..." (`rom:0x3B8569`).

---

## Trial module

| Part | Address (new ROM) | Label |
|---|---|---|
| Hook: file select vtable `0x08023B0C` +0x2C, `rom:0x23B38`, vanilla `0xFFFDDD01` (= `0x0800180D`) | new word `0x008F3471` (= `0x08916F7D`) | C |
| Code, vtable, chapter table | `rom:0x916F7C` +0x24C (`cc_continue` `0x08916F7C`, `cc_pick` `0x08916FB4`, `cc_run` `0x08916FDE`, `card_enter` `0x08917000`, `card_tick` `0x08917078`, `card_leave` `0x089170B0`, vtable `rom:0x917148`, table `rom:0x917178`) | C |
| Skipped chunk | `rom:0x916D30` +0x24C: named by the r39 word at `rom:0x4CE02C` (`0x08916D85`) | C |
| Cards (10) | `rom:0x90A308` to `rom:0x916D30`, 4740-5636 bytes each | C |

What it does (C, tests):

1. Continue with slot 0-2 and a used slot: read the slot image story flags (file select obj +0x14 + 0x164 x slot + 0xB4). Vanilla Continue copies exactly these 0x164 bytes to the save struct (`0x08001844`-`0x08001852`).
2. Pick the last `CHAPTERS` row whose flag is set (row 1 always matches).
3. Push a 20-byte card scene with `scene_push` `0x0801F2F4`, then call vanilla Continue. Vanilla Continue also calls `scene_push` (`0x080018C8`), so a nested scene from Continue is a vanilla pattern.
4. Card enter: keep DISPCNT, BG3CNT, BLDCNT and BLDALPHA; set the copyright image scene registers (BG3CNT 0x1F83, DISPCNT 0x0800, BLDCNT 0x2048); copy the menu palette and the card to VRAM; start song 25 unless it already plays.
5. Card tick: EVA 1-16, hold 128 frames, a new A or B press (`0x030022B0` bit 0 or 1) starts the fade out, EVA 15-0, end at frame 160.
6. Card leave: BG palette black, the four registers back as file select left them, free the object.

The card text is pre-rendered at build time from `CHAPTERS` with the game's dialog font: "Chapter N" in gold (index 88), the title in white (index 2), gray shadow (index 9). Renders: `scripts\one-time\2026-10-25-chapter-cards\card_01.png` to `card_10.png`, sheet `cards_sheet_x2.png`.

Edit titles: change `CHAPTERS` in the module and rebuild. The module refuses a table whose row 1 has a flag, whose numbers are not 1 to N, or whose flags do not rise.

---

## Story-point trigger design (not built)

| Option | How | Cost | Label |
|---|---|---|---|
| A. Hook ext 27 (SET) | Wrap the ext 27 table word. After the vanilla SET, if the flag is a `CHAPTERS` start flag, run `cc_run` for that row. No script edits | One table word. The card shows at the SET moment, so it fits only where the SET follows a fade: 68, 127, 195 (C by the start points above). For 86, 129, 148, 158 the SET is before the fade or in another record | L |
| B. New ext op | Repoint an unused ext table word (LoG II ext table `0x083B5D28`) to a handler that pops a chapter number and runs `cc_run`. Insert `push N ; ext X` (4 bytes) after the fade out at each start point. Relocate each edited record as r29 did for the chamber table | 9 record relocations, each with its own test | L |
| Recommended | B for all 9, because my rule is "at the start of a major section", which is the fade, not the flag | | |

A scene pushed from a script ext handler runs inside the field tick. Vanilla does nested pushes from scene ticks (Continue), so this is LIKELY to work. An emulator test decides.

---

## Build

| Item | Value | Label |
|---|---|---|
| r39 (list before `chapter_cards`) | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` | C (`test_before_is_r39`, build script check) |
| New ROM `log2_poc_r39_chapters.gba` | `1bc996a3d881e4a9b4eb4aef54c3a86c17877c6f` | C |
| Save `log2_poc_r39_chapters.sav` | `8b0b74f4896ba1a57666499305861f5f42c40a06`, a copy of `builds\log2_poc_r35_chamber2.sav` | C |
| Build log | One line appended to `docs\build-log.md` at 3:19 PM | C |

The save comes from r35, because no r39 save has three different chapters. The save format did not change, so it is valid (C, `global.md` rule; checksums good by `log2_save.adler32`).

| Slot | Map | Card shown on Continue | Label |
|---|---|---|---|
| 1 | 6,1,1 (Capsule Corp) | Chapter 10 The Champion's Hour | C (pick rule), L (in play) |
| 2 | 9,1,1 (Lookout) | Chapter 9 The Cell Games | C, L |
| 3 | 6,16,1 (Capsule Corp TV room; Vegeta leads, after Perfect Cell, before Goku and Gohan leave the chamber) | Chapter 7 Bow to the Prince (148 set, 158 clear) | C, L |

No copied save can show chapters 1-6. The interpreter test `test_pick_returns_the_last_set_chapter` covers the pick for all ten. Chapter 1 never shows in this trial, because New Game does not go through Continue.

### Diff runs r39 to new (23 runs, all inside the declared sites; C, `test_r39_to_new_diff_is_the_declared_sites`)

| Run | Site |
|---|---|
| `rom:0x23B38` +0x4 | Hook word |
| `rom:0x90A308` +0xCA28 | 10 cards |
| `rom:0x916F7C` +0x6A, `0x916FE7` +0x2, `0x916FEA` +0x10, `0x916FFB` +0x2, `0x916FFE` +0x66, `0x917065` +0x2, `0x917068` +0x74, `0x9170DD` +0x2, `0x9170E0` +0x6B, `0x91714C` +0x2, `0x917150` +0x1, `0x917154` +0x3, `0x917158` +0x3, `0x91715C` +0x1, `0x917160` +0x3, `0x917164` +0x3, `0x917168` +0x3, `0x91716C` +0x3, `0x917170` +0x3, `0x917174` +0x3, `0x917178` +0x50 | Code, vtable, table (`rom:0x916F7C` +0x24C; bytes that stay 0xFF split the runs) |

### Tests

| Run | Result |
|---|---|
| `test_chapter_cards.py` | 27 tests, OK |
| Full suite, once, `py -3 -I -m unittest discover -s ...\scripts\permanent\tests -t ...\scripts\permanent` | 798 tests in 149.7 s, OK, 0 skipped (`scripts\one-time\2026-10-25-chapter-cards\full_suite.txt`) |

What the tests do not cover: the real hardware timing, the sound engine, and the field after the card. These are the emulator steps below.

---

## Claims about the hand-off to the field

| Claim | Label | Proof |
|---|---|---|
| After the card, DISPCNT, BG3CNT, BLDCNT and BLDALPHA hold the file select values, as in vanilla | C | `test_leave_restores_file_select_registers_and_frees_the_object` |
| Remaining differences from vanilla at Continue: BG palette black, VRAM `0x06000000`-`0x06000E00` (card tiles, largest card 0xDF4 bytes), screenblock 31 (`0x0600F800`), BG3 scroll 0 | C | Card code, blob sizes |
| The field does not depend on those: the copyright scene already overwrote `0x06000040`-`0x06009640` and screenblock 31 earlier in every boot, and file select draws BG1 and BG2 from char base 0 with its own tiles. So any field data there is loaded after file select | L | Copyright enter `0x0801EDFA` (240 x 160 x 1 byte from `0x06000040`), file select enter `0x0800127C` (BG1CNT 0x1D83, BG2CNT 0x1E83) |
| The palette goes straight to `0x05000000` (no RAM shadow), as in the copyright scene | C | `0x0801EE5C`-`0x0801EE6A` DMA3 |
| Only `frame_loop`, `scene_push`, `0x0801F2CE` and `0x0801F346` call slots on the current scene; they use +4, +8, +0xC and +0x14. So the copied image scene slots +0x18 to +0x28 are not called | C by shape (13 pool readers of `0x03000E1C`); a call through another pointer copy would not appear | |
| Soft reset (A+B+Select+Start) stays on during the card; the module does not touch input byte +1 | C | `0x0801EF3C`-`0x0801EF50` |

---

## What to watch in play

My check steps (mGBA, cold boot: a save state carries its own slot image and skips the save file):

1. Put `log2_poc_r39_chapters.gba` and `.sav` in one folder. Open the ROM. Do not load a state.
2. At file select, choose slot 3 and Continue. Expect: black, "Chapter 7" (gold) and "Bow to the Prince" (white) fade in, song 25 plays, about 2.7 seconds, fade out, then the chamber map loads as normal.
3. Continue again (reset first) and press A during the hold. The fade out starts at once. Try B. Start and Select do nothing.
4. Slot 1 shows Chapter 10, slot 2 shows Chapter 9.
5. After each card, check the map colours, the HUD and the music. The map music should replace song 25.
6. New Game shows no card (by design).

Watch for:

- The cut from file select to the card is abrupt. BF fades out before its card. A short fade out of file select is a possible follow-up.
- File select sprites may flash for a frame after the card, because the OBJ layer comes back with file select's DISPCNT until the map loads (L).
- On a map that starts no music, song 25 may keep playing (L).
- Slot 3 shows Chapter 7. That is me order: card 8 "Room of Spirit and Time" comes after Perfection and starts when Goku and Gohan leave the chamber (exit table `rom:0x3DBDD4` seq 1: fade out 240; flag 158 is SET at seq 32 of the same table, before the player gets control, bible R28 rows). Map 6,16 is the Capsule Corp TV room, not the chamber. If you want card 8 when Goku and Gohan go in, its flag is 149 (`rom:0x3DE69C`, Vegeta and Trunks exit, Goku walks in, then fade out 180); then cards 7 and 8 swap.
- The text uses the menu palette; the BF backdrop and BF colours come later.

---

## Files

- `scripts\permanent\patches\chapter_cards.py`, `scripts\permanent\tests\test_chapter_cards.py`, `scripts\permanent\build_list_trial_chapters.txt`
- `builds\mockups\2026-10-25-chapter-cards\log2_poc_r39_chapters.gba`, `.sav`
- `scripts\one-time\2026-10-25-chapter-cards\`: `build_chapters.py` and `.txt`, `render_cards.py`, `card_01.png`-`card_10.png`, `cards_sheet_x2.png`, `card_widths.txt`, `bf_card_backdrop*.png`, `bf_chapter_sites.txt`, `bf_card_ext_ops.txt`, `log2_flag_sites.py`, `log2_scene_tables.txt`, `full_suite.txt`, `bible_rows.md`

---

# v2

Final decisions, 2026-10-25 4:25 PM: "Card length should match BF, with the music that should be ported over. Hold the other questions such as card 8 timing for later." Update 4:31 PM: the backdrop palette and the title font wait for his BF rips. Titles, flags and the Continue trigger are as in v1. v1 (`log2_poc_r39_chapters.gba`) is kept. Its suite run (798 tests) was for v1; the v2 run below supersedes it.

## v2 SHIPPED

| Ask (my own words) | Result |
|---|---|
| (1) "Timing exactly as BF (fade in 100, wait 250, fade out 100 ... no A/B skip, as BF)" | Built. 450 frames, no button skips it (tests `test_tick_has_bf_timing`, `test_no_button_skips_the_card`) |
| (2) "Port BF song 37 so it plays in LoG II" | Built as a data-only port: no player code change was needed. Proof below |
| "Prove it with the sound data decoded" | Done: decoder checked on every song of both games; the LoG II row decoder, run as ROM code on the port, gives the same channel bytes as the BF row decoder on the original for 195 rows |
| New ROM and save, exclusive create, keep v1 | `log2_poc_r39_chapters_v2.gba` and `.sav` |
| Full suite once, diff runs r39 to v2 | 832 tests, OK, 0 skipped. Diff runs below |
| Bible rows tag CH2 in `bible_rows_v2.md` | Done (sections 8, 11, 13, 14) |

## v2 PENDING

| Ask | Why pending |
|---|---|
| (3) BF backdrop with the right palette | Held by the coordinator at 4:31 PM: waits on my rips. One finding for that work: my screenshot shows the balls and the logo in other places than my map 29 render. So map 29 may not be the card backdrop, or my render is mis-assembled (S). I did not spend more on it |
| (4) BF title font (small caps with outline) | Held: waits on the rips. The card keeps the LoG II dialog font |
| (4) "Render the new card for each title next to my screenshot" | Part of item 4, so it also waits on the rips |
| Listening test | Static proof only. I must listen in mGBA (steps below) |
| Card 8 timing, Perfection | Held by me ("later") |

## Timing (C)

The BF card script bytes at `0x0879B004` are `... 00 64 02 79` (ext 121, 100), `00 FA 02 88` (ext 136, 250), `00 64 02 78` (ext 120, 100), `02 24` (ext 36). Ext 121 and 136 each build a scene object and run it with `0x0803D8A0`, BF's scene_push. So the three steps run one after another: 450 frames (C by listing). No step reads the keys (L, wait tick `0x08019594`).

v2 card tick: EVA = frame x 41 >> 8 for frames 1-100 (0 to 16), EVA 16 for frames 101-350, EVA = (450 - frame) x 41 >> 8 for frames 351-449, scene end at frame 450. Leave now stops the music (player +5 = 0), as BF ext 36 does at the end of its card. LoG II ext 50 (`0x08009CBA`) is the same code. One correction to v1: the music bytes `00 25 02 23` are at `0x0879B011`, not `0x0879B013`.

## Song 37 port result

**The LoG II player can play BF song 37 as is. Only the data must be copied (C).**

| Proof | Label | Where |
|---|---|---|
| Both games run the same Webfoot tracker player. Byte equal: row decoder (LoG `0x08020820`, BF `0x0803EEE4`), note trigger (`0x0801FE20`, `0x0803E4E4`), 120-entry note table (`0x087FC93C`, `0x087B6724`). Equal but for BL offsets: music_play (3 bytes), tick (4), sequencer (2), mixer `0x0801FA14` +0x210 (26 bytes: 24 in BL pairs, plus 2 literal-pool offsets `0x0801FA4C` and `0x0801FA52` that load the same values 0x1063 and 0x7FF). The BL callees were not compared byte by byte beyond the functions named here. Both effect tables have 32 handlers that match by signature. Only the SFX voice copy code differs | C | `v2_sound_diff.txt`, `v2_sound_diff_core.txt`, test `test_the_two_players_read_songs_the_same_way` |
| The player reads every song field through the 20-byte record: patterns +0, orders +4, sample directory +8, mask table +0xC, tempo +0x10, ticks per row +0x11. So the v1 worry (the two "control tables" differ) is not a problem: each song carries its own mask table | C | Row decoder `0x08020834`-`0x080208B8`, note trigger `0x0801FE7C` |
| The pattern format decodes every song in both games with no error (44 LoG II, 53 BF): notes < 120 or note off, effects < 32, instruments inside the directory | C | `v2_song_decode.txt` |
| Song 37: one 96-row pattern, channels 1-8, 10 instruments (51955 sample bytes), effects 24 and 7 only, tempo 115, 4 ticks per row | C | `v2_song_decode.txt` |
| The ported song decodes to the same events; its used samples are the BF bytes; every pointer stays inside the port | C | `test_ported_song_decodes_to_the_bf_song`, `test_used_samples_are_bf_bytes_and_entries_keep_their_fields`, `test_unused_entries_are_silent_and_every_pointer_stays_in_the_port` |
| The LoG II row decoder (ROM code, run in the test CPU) on the port gives the same channel bytes as the BF row decoder on the original, for 195 rows (two passes and the loop) | C | `test_lg_row_decoder_reads_the_port_as_bf_reads_the_original` |
| One pass is 384 ticks, about 8.3 s or 500 frames (timer 0 reload 0xFBE6 in both games, about 15978 Hz; 40000 / 115 samples per tick). The 450-frame card stops it before the loop, as in BF | L | Arithmetic from the code constants |

**What the port copies (module `chapter_cards`, SONG PORT).** The record (pointers rebased, tempo and speed kept), the pattern pointer table, the order bytes, the 16-byte mask table, directory entries 0-62 (the 10 used entries keep their flags, loop, length and rate; the others name 16 silent bytes), the pattern, and the 10 samples plus 16 tail bytes each. The BF ROM is read at build time and its SHA-1 is checked, as `bf_hud` does. The record and every song value are checked before the first write. Size 0xD250 bytes at `rom:0x916D30`. The card plays it with music_play, the same call v1 used for song 25.

**Map music after the card (C).** Map load sets the music on every load (`0x0800C4DE`-`0x0800C50E`): the map's song, or a stop when the map has none. So the card song never runs on into the field. This retires the v1 watch item "song 25 may keep playing".

## v2 build

| Item | Value | Label |
|---|---|---|
| r39 (list before `chapter_cards`) | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` | C |
| v1 ROM (kept) | `1bc996a3d881e4a9b4eb4aef54c3a86c17877c6f` | C |
| v2 ROM `log2_poc_r39_chapters_v2.gba` | `f3aa0c960dc40a3c433a20874649ec2bd3f5e732` | C |
| v2 save `log2_poc_r39_chapters_v2.sav` | `8b0b74f4896ba1a57666499305861f5f42c40a06` (a copy of `builds\log2_poc_r35_chamber2.sav`, same as v1) | C |
| Build log | One line appended to `docs\build-log.md` at 5:19 PM | C |
| Slots | 1: Chapter 10, 2: Chapter 9, 3: Chapter 7 (as v1) | C (pick rule), L (in play) |

### Diff runs r39 to v2 (882 runs, every changed byte inside a declared site; C, `test_r39_to_new_diff_is_the_declared_sites`)

| Site | Runs | Note |
|---|---|---|
| `rom:0x23B38` +0x4, hook | 1 | |
| `rom:0x90A308` +0xCA28, 10 cards | 1 | One run `rom:0x90A308` +0xCA41: the cards end at `rom:0x916D30`, where the song starts, so the run goes on 0x19 bytes into the song |
| `rom:0x916D30` +0xD250, BF song 37 port | 859 | Sample bytes equal to 0xFF split the runs. Full list: `build_chapters_v2.txt` |
| `rom:0x9241D4` +0x254, code, vtable, table | 21 | Bytes that stay 0xFF split the runs |

The code block moved from `rom:0x916F7C` (v1) to `rom:0x9241D4`, because the song takes the space after the cards. v1 skipped `rom:0x916D30` for code because the word at `rom:0x4CE02C` is `0x08916D85`. That word is the same in the base ROM and in r39 (C), so it is base data noise, not a patch pointer. The song is data, so the code-only name check does not apply to it.

v1 cannot be rebuilt now: the trial list and the module build v2. `log2_poc_r39_chapters.gba` (`1bc996a3...`) is the only copy of v1.

### Tests

| Run | Result |
|---|---|
| `test_chapter_cards.py` | 33 tests, OK |
| Full suite once, `py -3 -I -m unittest discover -s ...\scripts\permanent\tests -t ...\scripts\permanent` | 832 tests in 180.1 s, OK, 0 skipped (`full_suite_v2.txt`) |

## v2 what to watch in play

1. Cold boot `log2_poc_r39_chapters_v2.gba` with its `.sav` (no state load).
2. Continue slot 3. Expect: black, then the card fades in over about 1.7 s, holds about 4.2 s, fades out over about 1.7 s (7.5 s in all). BF song 37 plays from the start. Buttons do nothing. The music stops when the card ends, then the map music starts.
3. Compare the song with a BF chapter card by ear. A wrong instrument or pitch would mean a mixer difference I did not find (the code says no).
4. Slots 1 and 2 show Chapters 10 and 9.

## v2 files

- `scripts\permanent\patches\chapter_cards.py` (v2), `scripts\permanent\tests\test_chapter_cards.py` (v2)
- `builds\mockups\2026-10-25-chapter-cards\log2_poc_r39_chapters_v2.gba`, `.sav`
- `scripts\one-time\2026-10-25-chapter-cards\`: `build_chapters_v2.py` and `.txt`, `v2_sound_diff.py`, `v2_sound_diff.txt`, `v2_sound_diff_mixer.txt`, `v2_sound_diff_core.txt`, `v2_sound_compare.py`, `v2_song_decode.py` and `.txt`, `full_suite_v2.txt`, `bible_rows_v2.md`

---

# v3

2026-10-25 6:46 PM: there are no rips; the images are game screenshots. "If you can find the backdrop and whether the text is generated with a specific font or hardcoded." v3 builds the BF backdrop, its palette and BF's title font. Timing and song 37 are as in v2. v1 and v2 ROMs are kept.

## v3 SHIPPED

| Ask (my own words) | Result |
|---|---|
| (a) "Find the backdrop" (tiles, map, palette) | Found. Map entry 29 (as in v1) with BG palette `rom:0x5632C`. The render matches the screenshot |
| (b) "Whether the text is generated with a specific font or hardcoded" | Generated: the card draws each title at run time from a string table with one font. It uses no title image (no ROM-wide image search was run). Addresses below |
| Build v3 with the BF backdrop and palette, titles drawn the BF way | Built. The text uses BF's own glyphs and BF's draw rule (fill, 4-neighbour outline), BF's colours, BF's positions |
| Fix the data-chunk check (refused on beam_struggle data `0x08926D91` at `rom:0x910C94`) | Fixed: only real pointer words count. Regression tests added |
| Render each new card next to the Chapter 2 screenshot | `v3_card_01.png`-`v3_card_10.png`, `v3_cards_sheet.png`, plus the module check `v3_card_check_ch2.png` |
| New ROM and save, exclusive create | `log2_poc_r39_chapters_v3.gba` and `.sav` |
| Full suite once, diff r39 to v3 | 854 tests, OK. Diff below |
| Bible rows tag CH3 in `bible_rows_v3.md` | Done (sections 8, 11), with the CH2 corrections |

## v3 PENDING

| Ask | Why pending |
|---|---|
| Two titles are too wide for BF's font on one line | "A Warning from the Future" is 262 px and "Birth of a Super Namekian" is 246 px; one BF line fits 238 px. I did not change my titles. v3 wraps them onto two lines (see "Wrap"). My choice: keep the wrap, or give shorter titles |
| `.` and `'` in "Dr. Gero" and "The Champion's Hour" | BF's font has blank glyphs for both (BF titles use neither). v3 draws our own 2 px dot and tick in BF's style (`EXTRA_GLYPHS`). Not BF art: my review |
| Text colour bank | Colours match OBJ bank 0 (C). That BF uses bank 0 for the title OBJ is L: the OBJ attribute was not traced |
| In-game look | Static proof only. My check steps below |
| Card 8 timing, Perfection | Held by me ("later") |

## (a) Backdrop (C)

The backdrop is BF map entry 29, the map the card script loads (`0x0879B004`: map load 0, 96, 1, 0, 0). v2 had the right tiles and layout. Only the palette was wrong.

| Fact | Label | Proof |
|---|---|---|
| BG palette = `rom:0x5632C` (0x200 bytes). BF copies `0x0805632C` to `0x05000000` and `0x0805652C` to `0x05000200` at `0x0802C9C0`-`0x0802C9D4` (literals `0x0802CAAC`, `0x0802CAB0`) | C | Listing; `v3_palette_search.txt`: best of all 2-aligned 512-byte ROM runs, mean error 1.08 per 5-bit channel, next best 4.00 |
| v1 and v2 used `rom:0x5652C`, which is the OBJ palette | C | Same listing |
| Map 29 layout matches the screenshot: balls and logo in the same places. The CH2 "open" row (layout differs) was a misread of a small thumbnail and is wrong | C | `v3_bf_text_compare.png` (x3) |
| Tiles: raw cell 1-3 = bank 20 tile 89, bank 55 tile 92, bank 111 tile 73; raw 4-599 = global tile 37756 + raw (banks 147-149); no flips | C (the render matches the screenshot), L (the rule comes from my atlas data, not from BF code) | `bf_card_backdrop.txt`; the module pins the render SHA-1 `20b7eb0c...` |

## (b) Text: run-time font, not images (C)

The card draws both lines at run time through ext 178, from a string with one font. I ran no ROM-wide search for title images; the card uses none. One card script serves all 12 chapters with a computed string id (L): the strings come in pairs and my Chapter 1 and 8 screenshots have the same layout, but I did not decode the id expression in the script bytes (`1D 02 81 70 81 02` and `1D 02 81 70 81 2A`).

| Step | Address | Label |
|---|---|---|
| Card script: two lines at (120, 65) and (120, 85) through ext 4/5 + ext 178 | `0x0879B004` | C (bytes) |
| Ext 178 pops 3 values, calls `0x0802BFBC(id, &xy)`, then shows the OBJ with `0x0801191A` | `0x08003030` | C |
| String = `[0x0806BCE8 + 4 x id]`, UTF-16, mixed case. Ids 1450-1473 are the 12 chapters ("Chapter 2" / "Great Saiyaman" = 1452 / 1453, "Chapter 8" / "Janemba" = 1464 / 1465) | `0x0802BFBC` | C |
| Width = sum (glyph width + 1) with the font object `[0x08753A18 + 4]` = `0x087548DC` | `0x0803FFE8` | C |
| Render into an OBJ buffer, centred, then copied to OBJ VRAM `0x06010000` | `0x0802BECC` | C |
| Glyph table `0x08753A20`: u16 index per char, then u16 width and one u16 column per pixel (bit 0 at the top). Small caps are the lower-case glyphs | font +0 | C |
| Glyph draw: fill (white) where a bit is set, outline (black) where a left, right, up or down neighbour is set | `0x0803F70C` | C |
| Colours: OBJ palette `rom:0x5652C` bank 0, entry 1 `0x0000`, entry 2 `0xFFFF` (white) | | C (match), L (bank) |

**Proof against the screenshot.** The module draws BF's own strings 1452 and 1453 over the backdrop. In the text band (rows 52-99), 8 of 11424 pixels differ by more than 200 (channel sum); the screenshot is blurred. Every pixel the model calls fill is bright (1251 of 1251), and every outline pixel is dark (1056 of 1056). Files: `v3_bf_text.txt`, `v3_render_cards.txt`, `v3_card_check_ch2.png`.

## Wrap

BF's centring puts the left outline at x = 120 - (width + 1) // 2 - 1, so one line fits 238 px. My two titles are wider. v3 breaks such a title at the space that keeps the wider part narrowest. The block stays centred on y 75 with BF's 20 px pitch: lines at y 55, 75 and 95.

| Card | Lines (BF widths) | Other split |
|---|---|---|
| 1 | "Chapter 1" (93), "A Warning from" (154), "the Future" (105) | "A Warning" (104) / "from the Future" (155) |
| 5 | "Chapter 5" (99), "Birth of a" (91), "Super Namekian" (152) | "Birth of a Super" (153) / "Namekian" (90) |

The other 8 titles fit on one line (149-229 px).

## Data-chunk check fix (C)

v2 refused a data chunk when any word in the expansion area held a value inside it. Packed data (beam_struggle `0x08926D91` at `rom:0x910C94`) matched by chance. v3 counts only real pointer words that earlier modules wrote:

1. An aligned ROM-range word inside a "sites" entry below 8 MB (hooks, vtable and pool words in vanilla code).
2. A pool word that a Thumb `ldr rd,[pc,#imm]` inside any "sites" entry loads.

Not seen by these two shapes: a pointer kept in another module's data table, or a pointer outside every "sites" entry. Tests: packed data that names a chunk passes; a pool word that names a chunk refuses with no write; a word in a vanilla site that names a chunk refuses. The current beam list (`build_list_trial_beam.txt`) plus `chapter_cards` also builds in memory. Its word at `rom:0x910C94` is now `0x4A75FE60`, so the regression test sets the reported word itself.

## v3 build

| Item | Value | Label |
|---|---|---|
| r39 (list before `chapter_cards`) | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` | C |
| v3 ROM `log2_poc_r39_chapters_v3.gba` | `fd5135eaadb0464f9561cbc1a309992ad7fc3049` | C |
| v3 save `log2_poc_r39_chapters_v3.sav` | `8b0b74f4896ba1a57666499305861f5f42c40a06` (a copy of `builds\log2_poc_r35_chamber2.sav`) | C |
| Build log | One line appended to `docs\build-log.md` at 8:15 PM | C |
| VRAM | 599 base tiles + at most 106 card tiles = 705, below the 992 that fit under the screenblock | C |
| Slots | 1: Chapter 10, 2: Chapter 9, 3: Chapter 7 | C (pick rule), L (in play) |

v2 cannot be rebuilt now: the module builds v3. `log2_poc_r39_chapters_v2.gba` (`f3aa0c96...`) is the only copy of v2.

### Diff runs r39 to v3 (901 runs, every changed byte inside a declared site; C, `test_r39_to_new_diff_is_the_declared_sites`)

| Site | Runs | Note |
|---|---|---|
| `rom:0x23B38` +0x4, hook | 1 | |
| `rom:0x90A308` +0x13FE8, 10 cards | 13 | The cards sit back to back, so some runs cross from one card into the next |
| `rom:0x91E2F0` +0xD250, BF song 37 port | 859 | Sample bytes equal to 0xFF split the runs. The last run goes on into the backdrop |
| `rom:0x92B540` +0x97C0, backdrop (palette, 599 tiles) | 7 | |
| `rom:0x934F64` +0x264, code, vtable, table | 21 | Bytes that stay 0xFF split the runs |

Full list: `build_chapters_v3.txt`.

### Tests

| Run | Result |
|---|---|
| `test_chapter_cards.py` | 41 tests, OK |
| Full suite once | 854 tests in 212.9 s, OK (`full_suite_v3.txt`) |

## v3 what to watch in play

1. Cold boot `log2_poc_r39_chapters_v3.gba` with its `.sav` (no state load).
2. Continue slot 3. Expect the purple BF backdrop with the Dragon Balls and the logo, and "CHAPTER 7 / BOW TO THE PRINCE" in white small caps with a black outline. It fades in, holds and fades out over 7.5 s with BF song 37.
3. Compare it with my Chapter 2 screenshot. A wrong colour would point to the palette entries 247 and 248.
4. Slots 1 and 2 show Chapters 10 and 9. Card 10 shows the apostrophe from `EXTRA_GLYPHS`.
5. To see cards 1 and 5 (the wrapped titles), a save at the new game or after flag 127 is needed. None of the three slots shows them; the renders `v3_card_01.png` and `v3_card_05.png` show them.

## v3 files

- `scripts\permanent\patches\chapter_cards.py` (v3), `scripts\permanent\tests\test_chapter_cards.py` (v3)
- `builds\mockups\2026-10-25-chapter-cards\log2_poc_r39_chapters_v3.gba`, `.sav`
- `scripts\one-time\2026-10-25-chapter-cards\`: `v3_palette_from_shot.py` and `.txt`, `v3_backdrop_shotpal.png`, `v3_palette_search.py` and `.txt`, `v3_backdrop_rompal.png`, `v3_bf_text.py` and `.txt`, `v3_bf_text_compare.png`, `v3_render_cards.py` and `.txt`, `v3_card_check_ch2.png`, `v3_card_01.png`-`v3_card_10.png`, `v3_cards_sheet.png`, `build_chapters_v3.py` and `.txt`, `full_suite_v3.txt`, `bible_rows_v3.md`
