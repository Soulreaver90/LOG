# Bible rows, the easter egg game-over card, 2026-11-07

Tag `GOC` = `docs\tasks\2026-11-07-gameover\report.md`

## Section 8

| Fact | Tags | Conf | Src |
|---|---|---|---|
| Game-over record 0 `rom:0x3B6104` reads the CURRENT MAP, and the two ops that do it are named: `ext 8` `@0x0800942A` pushes byte +0 and `ext 9` `@0x0800943E` pushes byte +1 of the struct at `[0x083B5C78 + 0x10]` = `0x03002080`, the map info word. So the vanilla 6,70 test is `ext 8 ; push 6 ; eq ; ext 9 ; push 70 ; eq ; and ; jz 3 ; push 4 ; end` at `rom:0x3B6107`, 16 bytes, and the `jz` operand is a BYTE COUNT that skips the 3 bytes `push 4 ; end`. Corrects nothing; it names the ops the CFS row left as "tests map 6,70" | #script #map #story | C (both handlers read in full, pool word `rom:0x9594` = `0x083B5C78`, record bytes) | GOC |
| Record 0 reads the map BEFORE its own `ext 39` map load, so the test sees the map the player died on, never map 1,7. Record layout: header 3 bytes, the 6,70 test at +3, `push 4 ; end` at +0x10, and the death-screen setup from +0x13 (`push 16 ; ext 49` music, `push 0 ; ext 86` HUD off, fade 120, `ext 39 (1,7,1,112,144)`, `ext 121 (0,17)`, fade in 120, `end`). The record is `rom:0x3B6104`-`rom:0x3B6138`, 0x35 bytes, and `rom:0x3B6139` is an alignment pad | #script #story #map | C (record_end, byte decode) | GOC |
| The game-over table cannot grow in place: its 24 words end at `rom:0x3B6413` and `rom:0x3B6414` is the `@Game Saved!` type 1 record. Growing it means copying the table and repointing the one literal `rom:0x8870`, which is still its only namer in a dev-plus-four-trials build (chamber_spar edits words 4 and 15 in place and adds no namer) | #script #story | C (byte read, `words_naming` on the build) | GOC |
| A caption box holds FOUR LINES OF 144 PX A PAGE, not a character count, and a longer box PAGES ON rather than truncating. `@` and `^` are both consumed before any measuring: the prefix loop `@0x0800B224`-`@0x0800B244` advances the pointer past `!`, `@` and `#`, and `@0x0800BA98` advances it past `^` and sets the show-at-once flag at box +0x24. The line counter `@0x0801F7FC` is then called with width 0x90 (`@0x0800B92A`), the y step is 14 px (`@0x0800B948`), the instant path measures at most 4 lines (`@0x0800B976`-`@0x0800B980`), and the page ends at 4 (`@0x0800B9A0`). A `^` box also centres its lines: start y = 15 + 7 * (4 - lines) (`@0x0800B982`-`@0x0800B992`). So the 38-character longest vanilla caption is a sample, never a limit | #text #script | C (listings read in full) | GOC |
| `gameover_card` (trial, 2026-11-07, never in `build_list.txt`): a loss on map 7,100 shows two caption boxes instead of `@^You have died!`. The 27-word table copy, the record 0 copy, the death-screen setup copy and the two cards are ONE chunk (0x130 bytes, `rom:0x951170` on the plateau trial). Below `rom:0x800000` the module writes ONE WORD, the literal `rom:0x8870`, of which 3 bytes change (both tables are in bank `0x08`). Record 0' = header, the new `ext 8 ; push 7 ; eq ; ext 9 ; push 100 ; eq ; and ; jz 3 ; push 24 ; end`, then vanilla record 0 byte for byte. Word 24 = the setup copy (next 25), word 25 = "@^Cell takes the time machine into the past..." (next 26), word 26 = "@^The nightmare is just beginning." (next 2, the vanilla `ext 67 ; fade 240 ; ext 97`) | #script #story #patch char:cell char:trunks | C (read back out of the built ROM, 22 tests) | GOC |
| Card 1, 44 characters, measures TWO lines of the caption box, 142 px and 73 px of the 144 px width. Card 2 measures 110 px and 49 px. Both fit one page with two lines to spare, so neither needs a split. Line 1 of card 1 has 2 px of slack, so any added word moves the break | #text #decision | C (the dialog line counter rule on the ROM font `rom:0x2CC64`) | GOC |

## Section 9

| Fact | Tags | Conf | Src |
|---|---|---|---|
| An APPENDED clone map reports its own zone and area at the map info word `0x03002080` while the player stands on it, so a script map test works on a map the base ROM never had. Measured on three of the owner's own states: `log2_plateau_v4.ss1` reads (7,100), `log2_plateau_v1.ss1` reads (1,100) and `log2_plateau_v1.ss2`-`ss5` read (4,100), and maps 1,100 and 4,100 both exist in that build as entry index 329. Extends the WRP row, which measured only arena 6,100 | #map #debug | C (state_dump on the owner's states, 2026-11-07) | GOC |
| The three trial arenas are three different maps, so a map test tells them apart: Cell against Trunks is `plateau` map 7,100, future 18 and future 17 are BOTH `future_androids` map 1,100, and `battle_arena` 6,100 is now unused by the ending. A card for 18 or for 17 alone therefore cannot be a map test: 18 and 17 share one map and need a flag, a VM variable or two maps | #map #script #open | C (module constants, the built ROM's one `ext 39 (7,100,1,248,624)` at `rom:0x940662`) | GOC |

## Section 11

| Fact | Tags | Conf | Src |
|---|---|---|---|
| Tools `scripts\one-time\2026-11-07-gameover\`: `dump.py` (hex a ROM range), `wrap.py` (break any caption the way the dialog line counter does, the C4S rule), `namers.py` (the live game-over table, its namers, its length and record 0's extent in any build), `find_arrival.py` (which map the ending's arena load names in a build), `readback.py` (the whole game-over chain out of a built ROM: raw bytes beside the decode, plus every byte run that differs from a baseline). `readback.py` exists because `scene_probe --record` folds op 0 pushes away, so its listing of record 0 shows neither `push 6` nor `push 70` | #tool #script | C (tool runs) | GOC |

## Section 13

| Fact | Tags | Conf | Src |
|---|---|---|---|
| Open (owner): does a loss to future 18 or future 17 also get its own card? They share map 1,100, so a map test cannot tell them apart. Cost if he says yes: one shared test plus a VM read that names the fight, about 3 table words a card. Open (owner): card 2 as written, "@^The nightmare is just beginning.", or the colder "@^The nightmare was never over." Open (emulator): the card in play, which nothing in this task could run, because the capture harness has a `savestate` step and no `loadstate` step | #open #story char:cell | S | GOC |
