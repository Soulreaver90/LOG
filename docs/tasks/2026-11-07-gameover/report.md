# The easter egg game-over card, 2026-11-07

Lose to Cell in the final arena and the game-over screen shows the owner's two caption boxes instead of
`@^You have died!`. Every other loss in the game still shows the vanilla line.

| | |
|---|---|
| Module | `scripts\permanent\patches\gameover_card.py` |
| Trial list | `scripts\permanent\build_list_trial_gameover.txt` (`include build_list_trial_plateau.txt`, then `gameover_card`) |
| Tests | `scripts\permanent\tests\test_gameover_card.py`, 22 tests, all green |
| ROM | `builds\mockups\2026-11-07-gameover\log2_gameover_v1.gba` SHA-1 `dfacc2392c487139e89c9fcb529f68c302f8f7fb` |
| Save beside it | `log2_gameover_v1.sav`, seeded from `builds\mockups\2026-11-07-plateau\log2_plateau_v4.sav` |
| Baseline for the diff | `baseline_plateau_v2.gba` SHA-1 `25b384a2cfee4b567025239967e65e1442d1c6dc`, the same list without this module, built in the same minute |
| Read-back proof | `builds\mockups\2026-11-07-gameover\readback_v1.txt` |
| Suite | 1603 tests, exit 1, 2 failures, NEITHER in my files (section 6) |

The wording is the owner's, unchanged:

```
@^Cell takes the time machine into the past...
@^The nightmare is just beginning.
```

---

## 1. The two questions that could have sunk this

### Caption capacity: a box holds 4 lines of 144 px a page, and a longer box pages on

The limit is not a character count. The handlers say so.

| Where | What it does |
|---|---|
| `@0x0800B224`-`@0x0800B244` | eats a leading `!`, `@` or `#` and picks the box y (`@` = 0x50) |
| `@0x0800BA98`-`@0x0800BAA4` | eats a leading `^`, sets the show-at-once flag at box +0x24 |
| `@0x0800B92A` | calls the line counter `@0x0801F7FC` with width `0x90` = 144 px |
| `@0x0800B948` | the y step between lines is 14 px |
| `@0x0800B976`-`@0x0800B980` | the show-at-once path measures at most 4 lines |
| `@0x0800B9A0` | at 4 lines the page ends and the box waits for A, then PAGES ON |
| `@0x0800B982`-`@0x0800B992` | a `^` box centres its lines: start y = 15 + 7 * (4 - lines) |

Both prefix bytes are consumed BEFORE the counter runs, so `@^` costs no width. Measured against the
ROM font `rom:0x2CC64` with the same rule the chapter-card tests already use.

| Box | Chars | Lines | Widths |
|---|---|---|---|
| `@^Cell takes the time machine into the past...` | 44 | 2 of 4 | 142 px, 73 px |
| `@^The nightmare is just beginning.` | 32 | 2 of 4 | 110 px, 49 px |
| `@^The nightmare was never over.` (the alternative) | 29 | 2 of 4 | 132 px, 25 px |
| `@^You have died!` (vanilla, for the rule's sake) | 14 | 1 of 4 | 75 px |

**No split is needed.** Card 1 breaks after "machine":

```
Cell takes the time machine
into the past...
```

One caution: line 1 has 2 px of slack out of 144. Any extra word moves the break.

CONFIRMED. Evidence: the listings above, plus `scripts\one-time\2026-11-07-gameover\wrap.py`.

### The map the death routine sees: the arena, not the death screen

The vanilla record already answers this, because my test reads the map at the SAME instruction point.

1. `ext 8` `@0x0800942A` pushes byte +0 and `ext 9` `@0x0800943E` pushes byte +1 of the struct at
   `[0x083B5C78 + 0x10]`. The pool word `rom:0x9594` makes that `0x083B5C78`, and `rom:0x3B5C88`
   makes the struct `0x03002080`, the map info word. **CONFIRMED**, both handlers read in full.
2. Record 0's own `ext 39 (1,7,1,112,144)` is the first map load in the chain, and it sits 0x13 bytes
   AFTER the test. **CONFIRMED** from the record bytes, and the read-back shows my test earlier still.
3. On the plateau the map info reads (7,100). **CONFIRMED** on the owner's own state
   `builds\mockups\2026-11-07-plateau\log2_plateau_v4.ss1`, taken today at 12:52 PM.
4. The one link I could not measure: that nothing writes `0x03002080` in the 200 frames between HP 0
   and the table run. Supporting, not proof: the vanilla 6,70 test is the same read and it works in
   play (`chamber_spar`, bible B0715), and a map load in those frames would move the player off the
   arena, which does not happen.

I call the chain CONFIRMED and link 4 LIKELY. Section 7 says why I could not run it live.

---

## 2. What the module does

The engine already branches the game-over screen on the map, so this copies that shape.

| Index | Record | Next |
|---|---|---|
| 0 | a copy of vanilla record 0 with the 7,100 test in FRONT of the 6,70 test | 1 |
| 24 | a BYTE COPY of record 0's death-screen setup: music 16, HUD off, fade 120, load map 1,7 at (112,144), pose, fade in 120 | 25 |
| 25 | `@^Cell takes the time machine into the past...` | 26 |
| 26 | `@^The nightmare is just beginning.` | 2 |
| 2 | the VANILLA tail, `ext 67 ; fade 240 ; ext 97` | 3 (END) |

The new test is the vanilla shape with three numbers changed:

```
ext 8 ; push 7 ; eq ; ext 9 ; push 100 ; eq ; and ; jz 3 ; push 24 ; end
```

The `jz` operand is a byte count: 3 skips `push 24 ; end`, exactly as the vanilla `jz 3` skips
`push 4 ; end`.

The cards draw on the normal death screen, not over the arena, because index 24 repeats record 0's own
setup byte for byte. Nothing about the death screen changes except the words.

**Why the table moved.** It needed 3 more words and could not grow: its 24 words end at `rom:0x3B6413`
and `rom:0x3B6414` is the `@Game Saved!` record. So the whole table is copied to the expansion area and
the ONE literal that names it, `rom:0x8870`, points at the copy. `words_naming` on the build confirms
`rom:0x8870` is still its only namer, and the chamber_spar words 4 and 15 are read live and carried over.

---

## 3. Read back out of the built ROM

Full listing in `builds\mockups\2026-11-07-gameover\readback_v1.txt`. `scene_probe --record` folds op 0
pushes away, so `readback.py` prints the raw bytes beside the decode.

```
literal rom:0x8870 = 0x08951234  ->  table rom:0x951234
  words naming the new table: ['0x8870']
  word  0 = 0x08951170  <- REPOINTED (was 0x083B6104)
  word  4 = 0x089091DC          (chamber_spar, carried over)
  word 15 = 0x08909204          (chamber_spar, carried over)
  word 24 = 0x089511B5  <- NEW
  word 25 = 0x089511DA  <- NEW
  word 26 = 0x0895120D  <- NEW

  INDEX 0  rom:0x951170  next 1  type 0
      rom:0x951173  02 08    ext 8
      rom:0x951175  00 07    push 7
      rom:0x951177  0B       eq
      rom:0x951178  02 09    ext 9
      rom:0x95117A  00 64    push 100
      rom:0x95117C  0B       eq
      rom:0x95117D  04       and
      rom:0x95117E  13 03    jz +3
      rom:0x951180  00 18    push 24
      rom:0x951182  11       end
      rom:0x951183  02 08    ext 8          <- the vanilla 6,70 test, untouched
      rom:0x951185  00 06    push 6
      ...
      rom:0x9511A8  02 27    ext 39         <- the map load, AFTER both tests

  INDEX 24  rom:0x9511B5  next 25  type 0   <- a byte copy of record 0's death-screen setup
  INDEX 25  rom:0x9511DA  next 26  type 1  portrait 0
      text  '@^Cell takes the time machine into the past...'
  INDEX 26  rom:0x95120D  next 2   type 1  portrait 0
      text  '@^The nightmare is just beginning.'
  INDEX  2  rom:0x3B6150  next 3   type 0   <- vanilla: ext 67 ; fade 240 ; ext 97

byte runs that differ from the baseline: 2
  rom:0x8870    0x3 bytes
  rom:0x951170  0x130 bytes
```

Two runs, both declared. The run at `rom:0x8870` is 3 bytes, not 4, because the old and the new table
are both in bank `0x08`. **Below `rom:0x800000` this module writes ONE WORD, `rom:0x8870`, and nothing else. Three of its four bytes change.** The
vanilla table, vanilla record 0 and the `@Game Saved!` record are byte identical to the baseline, and
`@^You have died!` still reads as it did.

---

## 4. How the owner reproduces it

The trial ROM and its save:

```
builds\mockups\2026-11-07-gameover\log2_gameover_v1.gba
builds\mockups\2026-11-07-gameover\log2_gameover_v1.sav
```

**I did not walk this route.** Steps 1 to 3 are INHERITED from the plateau trial save and the
`ending_fight` and `future_androids` docstrings. Steps 5 and 6 are EXPECTED, not observed.

1. Open the ROM in mGBA. The `.sav` is the plateau trial save, so the route is the one that already
   works for the plateau build.
2. Continue on **slot 1**: Gohan leads, map 6,1 at (432,591), level 40, flag 195 set (Cell beaten) and
   flag 196 clear (the final goodbye not yet done). These values I DID read, with `log2_save.py info`.
3. Play the farewell. The future epilogue runs. Trunks fights future 18, then future 17, then Cell on
   the plateau. INHERITED: this is the plateau trial's own route and I did not play it.
4. **Take a save state the moment the Cell fight starts.** No save point lies between the Lookout
   farewell and the ending (bible B0985, a decode), so a loss costs the whole farewell otherwise.
5. To lose on purpose: put the pad down. Cell is HP 5210 with AI 80 and Trunks will not heal, so he
   should die on his own. Do not press anything. EXPECTED from the stats, not observed.
6. About 200 frames after the Trunks HP reaches 0 the screen should fade, the death screen load, and
   the two cards come up in place of "You have died!". A advances a box, as in any box.

That a loss in this fight reaches the game-over table at all is a decode, not a play test: the
`ending_fight` docstring says it adds no loss handling, and bible B0985 reads the vanilla table.

**No save-state shortcut.** His mid-fight state `log2_plateau_v4.ss1` was taken on
`log2_plateau_v4.gba`, and that ROM differs from this trial in 12 byte runs besides my two, because
`plateau` moved on to v5 after it. So the state does not belong to this ROM and the long route is the
only one I can offer.

To check the vanilla side in the same run: losing to future 18 or future 17 should still show
"You have died!", because both of those fights are on map 1,100.

---

## 5. Scope, and what the 18 and 17 cards would cost

The brief scoped this to Cell only. The map test is exactly that scope.

| Fight | Map | Card |
|---|---|---|
| Cell against Trunks | **7,100**, `plateau` | the new pair |
| future 18 | 1,100, `future_androids` | vanilla "You have died!" |
| future 17 | 1,100, `future_androids` | vanilla "You have died!" |
| Capsule Corp sparring | 6,70 | the vanilla sparring loss, untouched |
| everything else | any | vanilla "You have died!" |

CONFIRMED: `future_androids.CLONE_ZONE, CLONE_AREA = 1, 100`, and the built ROM holds exactly one
`ext 39 (7,100,1,248,624)`, at `rom:0x940662`, with no `ext 39 (6,100,...)` left.

**If he says yes to an 18 or 17 card, it is not free.** 18 and 17 share map 1,100, so a map test cannot
tell them apart. One card for "any future android" is cheap: one more 16-byte test block in record 0 and
about 3 table words. Two different cards need something the map does not carry, such as a VM variable
set by each fight's own record, which is new work inside `future_androids`.

---

## 6. Tests

`test_gameover_card.py`, 22 tests: the list shape, four fail-closed cases (second run, moved literal,
changed record 0, missing map 7,100), the diff being only the declared sites, the vanilla bytes being
untouched, the whole chain read back out of the build, the wrap of both cards, and the scope check
against 6,100 and 1,100.

Two of its tests check the RULE and not just my build: the vanilla death box must still measure one
line, and the vanilla death record must still read `@^You have died!`.

**Full suite: 1603 tests, 448 s, exit 1.** Two failures, three skips, one expected failure. Neither
failure is in a file I wrote or touched.

| Failure | Whose |
|---|---|
| `test_battle_start.BattleStartTests.test_form_survives_the_leader_change` | the KNOWN failure named in my brief. It reports a `fullpower_ssj` record at `rom:0x89A9C0` whose `appearance(4, 61)` runs before `leader(2)`. It predates me. |
| `test_future_androids.DeathTables.test_each_death_record_hands_back_to_the_right_cutscene_word` | `future_androids`, which another agent was editing while the suite ran. Its own test and its own module. |

Other agents were editing `future_androids.py` and `plateau.py` throughout. The first build attempt
failed inside `future_androids.apply` with `NameError: move_to`, then with `NameError: LEFT`, both from
their half-done state, and the build went green on a later retry with no change of mine. Read the suite
result with that in mind: it was not a quiet tree.

---

## 7. What I could not prove

| | |
|---|---|
| The card IN PLAY | Not run. The capture harness `scripts\permanent\emu\capture.py` has a `savestate` step and **no `loadstate` step**, so I could not resume the mid-fight state, and playing from a cold boot to the future epilogue is out of reach. His play test is the only close. |
| Nothing writes `0x03002080` in the 200 frames after HP 0 | LIKELY, not measured. Section 1 gives the chain; the vanilla 6,70 test is the same read and it works in play. |
| How the card READS on screen | The lines fit and the box centres them, but whether two boxes feel right after a fade is the owner's eye. The colder alternative `@^The nightmare was never over.` is one string change if he prefers it. |

---

## 8. Files

| File | What |
|---|---|
| `scripts\permanent\patches\gameover_card.py` | the module |
| `scripts\permanent\build_list_trial_gameover.txt` | the trial list |
| `scripts\permanent\tests\test_gameover_card.py` | 22 tests |
| `scripts\one-time\2026-11-07-gameover\dump.py` | hex a ROM range |
| `scripts\one-time\2026-11-07-gameover\wrap.py` | break any caption the way the dialog line counter does |
| `scripts\one-time\2026-11-07-gameover\namers.py` | the live table, its namers, its length, the record 0 extent |
| `scripts\one-time\2026-11-07-gameover\find_arrival.py` | which map the ending arena load names in a build |
| `scripts\one-time\2026-11-07-gameover\readback.py` | the whole chain out of a build, raw bytes beside the decode |
| `docs\tasks\2026-11-07-gameover\rows.md` | bible rows, tag `GOC` |
