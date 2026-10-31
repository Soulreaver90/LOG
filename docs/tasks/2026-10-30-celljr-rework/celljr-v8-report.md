# Cell Jr v8: report (2026-10-30)

My ask: the v7 play test (11:20 PM). Brief: `celljr-v8.md`.

Labels: **C** = CONFIRMED (bytes, tests or a state), **L** = LIKELY, **S** = SPECULATIVE. No emulator run, so every in-game claim is L or S. Scripts and outputs: `scripts\one-time\2026-10-30-celljr-v8\`.

---

## SHIPPED

| Ask (my words) | Where |
|---|---|
| "Maybe have him teleport behind the top cell jr instead of flying" | Record F: the fly pose and the glide are gone. Gohan vanishes at the arena middle and appears north of the last Jr, faces south and punches south (C bytes, L in game) |
| "Copy the game's own teleport look. Do not invent one." | Goku's vanish, table `rom:0x3E6078` word 83 = record `rom:0x3E5E6A`. Its white flash pair now holds Gohan's move (C bytes). No fallback was needed |
| "Behind means north of the Jr" | Gohan at (456,344), the Jr at (456,368): the same column, 24 px above it, facing south (C) |
| The punch and the explosion do not change | `_melee()` and `_explode()` are untouched; only their knock spot changed (C, `v8_decode.txt`) |
| Spot, facing and knock path inside the view and on the open bands | All boxes open on the ss2 collision bitmap, inside the finish view and inside the v7 bands (C, `v8_spots.txt`) |
| Replace the fly-row test and its refusal, weaken nothing | 76 tests, OK (73 in v7): 2 removed, 5 added, see Tests. The v8 tests fail 9 times on the v7 module (C, `v8_tests_on_v7.txt`) |
| Do not touch a fly row that `vegeta_ssj_scene` uses | The main list still builds r40 `14d6b831` in memory (C, `v8_make.txt`). A test pins set 160 row 12 before and after this module |
| v8 ROM, exclusive create | `builds\mockups\2026-10-24-celljr\log2_poc_r40_celljr_v8.gba`, SHA-1 `db015ae8e6468d18be7d27938ba3876e46c25caa` (C) |
| `.sav` byte copy of the v7 save | `log2_poc_r40_celljr_v8.sav`, SHA-1 `aa8efb2adaa7aa87f4cff27ceb7244368bd02759` = v7 (C) |
| Diff v7 to v8 | 28 bytes in 6 runs, every run inside record F. 0 bytes outside a v7 or v8 site, 0 bytes below `rom:0x800000`. Decoded by name, only F changed (C, `v8_make.txt`) |
| Bible rows, tag CJ8 | `scripts\one-time\2026-10-30-celljr-v8\bible_rows.md` |

## PENDING

| Item | Why |
|---|---|
| My play test | No emulator run (steps below) |
| The 60-frame hold after the teleport | It is Goku's own value. If it reads as slow, change `TP_HOLD` to 20 (one line) |
| Stale docstring in `tests\test_vegeta_ssj_scene.py` line 236 | It says celljr_fight refuses "because it flies Gohan on the set 160 row". The refusal is now the notes guard. The test passes. That file is outside the brief |
| `docs\build-log.md` line for the v8 ROM | The brief limits edits. The exact line is in `v8_make.txt` |
| Me: merge the CJ8 rows | Rows file, with merge notes |
| Full suite | The brief runs `test_celljr_fight.py` only. I also ran one test of `test_vegeta_ssj_scene.py`, see Cross-file finding |

---

## The teleport, and where it comes from

Table `rom:0x3E6078` word 83, record `rom:0x3E5E6A` (20 bytes, the record right before Imperfect Cell's "#Instant transmission..." line). Goku vanishes (C, `v8_tp_decode.txt`):

```
push 10 ; ext 42      white flash out
push 60 ; ext 52      remove set 60 (Goku)
push 10 ; ext 43      flash back
push 60 ; ext 69      hold 60 frames
```

His arrival twin is word 72, record `rom:0x3E5C50`: `ext 42 (10)`, `ext 49 (25)`, `ext 51 (60, 408, 216)`, `ext 55 (60, 1)`, `ext 43 (10)`. So the effect is one white flash pair that holds the actor change. The `ext 49 (25)` is music (bible T6 row), so it is not copied: it would stop the fight music. Neither record uses a sound or a particle op.

Record F now runs (C, `v8_decode.txt`):

```
push 10 ; ext 42              white flash out      (Goku's value)
push 0,456,344 ; ext 62       Gohan moves
push 0,0 ; ext 55             he faces south
push 10 ; ext 43              flash back
push 60 ; ext 69              hold                 (Goku's value)
```

**Deviation, and why.** Goku's record removes an NPC set, and the scene builds him again only after a map load (word 85, `ext 39 (9,1,1,736,416)`). Gohan is the player and record F loads no map, so `ext 52` plus `ext 51` cannot bring him back in place (L). The module keeps the flash pair and the hold and swaps `ext 52` for `ext 62`, the player move that `_to_middle()` and record N already use (C).

## Spots

| Part | v7 | v8 | Why |
|---|---|---|---|
| Gohan | flies from (432,392) to (432,336) | appears at (456,344) | North of the Jr, same column |
| Jr C stands | (456,336) | (456,368) | Gohan's 16 x 32 frame reaches 24 px above his spot, and the finish view starts at y 312. Any Gohan spot above y 336 leaves the view, so C moved 32 px down (C, `v8_spots.txt`) |
| Jr C knock | (488,336), east | (456,392), south | He is punched from the north |
| Jr C walk-in | (456,288) to (456,336) | (456,288) to (456,368) | The start is unchanged |
| Facing | right | south | The Jr is below him |

Every box is open on the ss2 collision bitmap, inside the finish view, inside the v7 bands and clear of Cell at (512,472) (C). The punch gap stays 24 px, as the east punch does. F holds one `ext 31` and no `ext 33`, so the view does not move during the teleport (C by decode, L in game).

## Cross-file finding: the order guard

`tests\test_vegeta_ssj_scene.py` holds `test_celljr_fight_refuses_to_run_before_this_patch`. It ran green only because the v6 fly-row check refused. With the fly gone, that test failed (C, I ran that one test).

I did not edit that file. Instead `celljr_fight._check()` now names the two main modules it needs in `alloc.notes`: `superperfect_cell` (as before) and `vegeta_ssj_scene`. The module header already states this module runs after the whole main list, so no earlier allocation moves. The refusal is now true for its stated reason, the other file's test passes again, and `test_it_refuses_before_the_main_list_is_done` pins it here. The ROM is unchanged by this guard: the build still has SHA-1 `db015ae8...` (C, `v8_verify.txt`).

## Tests

76 tests, OK (v7: 73). 2 removed, 5 added. No other test was weakened.

| Removed | Replaced by |
|---|---|
| `test_a_missing_fly_row_refuses_before_writing` | `test_the_finish_needs_no_fly_row`: the module builds with set 160 row 12 zeroed, and writes no byte of that row. Plus `test_it_refuses_before_the_main_list_is_done` for the order |
| `test_gohan_flies_with_the_borrowed_row` | `test_gohan_teleports_north_of_the_last_jr`: the 5 teleport ops in order, the melee right after, the spot north of C in its column, the knock south. Plus `test_the_finish_has_no_fly_and_moves_only_the_jrs` (no `ext 121` and no `ext 136` on the player) and `test_the_teleport_is_the_games_own_effect` (Goku's record decodes to its 4 ops, this module changes none of those bytes, and F uses their shape) |

Restated values, not weakened checks: `FINISH_C` is (456,368), was (456,336). The v7 surround, walk-in and spot tests then run unchanged on the new value. `test_a_changed_source_byte_refuses_before_writing` also covers Goku's record now. `test_finish_spots_fit_the_view_and_clear_cell_and_gohan` checks Gohan's landing box in place of the flight sweep.

## Play steps (my checks)

1. Load `log2_poc_r40_celljr_v8.gba` (mGBA pairs the `.sav` by name), slot 3. Record F keeps its v7 length, so every record and item sits at its v7 address (C). A v7 state renamed to the v8 name may therefore still load (S). Make a new state at the 7 Jrs if it does not.
2. Play to the 1 v 1 Jr, then through the 1 v 3, as in v7.
3. Finish: Gohan punches right, blasts left. Then a white flash, and he stands above the top Jr facing it. After about a second he punches down, and the Jr explodes.
4. Report: a teleport that reads as a cut, a hold that feels long, a cramped head at the top of the screen, or a punch that does not connect by eye.

## Housekeeping

- Edits only in `celljr_fight.py` and `tests\test_celljr_fight.py`. The v7 module is rebuilt in `scripts\one-time\2026-10-30-celljr-v8\v7_backup\` for the mutation check, and it rebuilds the v7 ROM byte for byte (C).
- Rule breaks to log: 7 read-only shell calls started with `cd`, 6 of them into the LOG root and one into `C:\`. One text fix to a one-time script ran `python`, not `py -3.14 -P`. Neither wrote outside `scripts\one-time\2026-10-30-celljr-v8\`.
- Nothing written under `data\`, `docs\RE-BIBLE.md`, `docs\ledger\`, `build_list.txt`, `zhack\`, `chapter_cards.py` or `test_chapter_cards.py`. No ROM, save or state overwritten.
