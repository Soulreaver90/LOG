# Rung 5: the Cell fight splits into two rounds

Built 2026-11-08. Trial ROM `builds\mockups\2026-11-08-rung5\log2_rung5_v5.gba`,
SHA-1 `f21a6ce0a71210edc48b34cbe2179d655b59c4fe`, 16 MB, with `log2_rung5_v5.sav` beside it
(seeded from `builds\log2_poc_r40.sav`, the highest numbered save in `builds\`).
Build list `scripts\permanent\build_list_trial_plateau.txt`. `build_list.txt` was not touched.

The ask, in the owner's words: "Cell: Trunks starts NOT Super Saiyan / half way: white flash + ping
-> cutscene, Cell punched off screen, Trunks flies after him / final arena: our own enclosed grassy
plateau", and "yeah we did this for cell jr as well ... then half way we do the scene where he
punches cell of screen and trunks flies after him which takes him to our placeholder plateue".

---

## 1. What the ROM did before this build, read first

**Trunks WAS Super Saiyan when the Cell fight began, and one byte did it.** `ending_fight`'s record A,
ending table word 13, ran `ext 73 (3, 133)`. `future_androids` word 4 transforms him to set 133 for the
two android fights, nothing between word 4 and word 13 changes him back, and record A's `ext 73` then
re-asserts 133 in front of the map load that builds his body.

**That op is now `ext 73 (3, 132)`, the base Trunks body.** The change is the second zigzag byte of the
push, `0x0A` to `0x08`. It runs after record A's own `fade_out(180)`, so the body swap happens under
the black. Read back from the built ROM, record A is
`wait(60) ; fade_out(180) ; appearance(3,132) ; leader(3) ; load_map_at(6,100,1,248,624) ; wait(120) ;
camera(136,456,2) ; fade_in(180) ; walk(0,248,568) ; wait(100)`.

**The plateau also used to take the whole fight.** `plateau.py` repointed record A's load from map
6,100 to map 7,100, which moved the talk AND the fight onto the plateau. Rung 5 takes that edit off:
record A loads the arena again, and the plateau is reached from the round boundary instead.

---

## 2. What rung 5 builds

| beat | where it lives | what it is |
|---|---|---|
| Trunks base | `ending_fight.arrive()` | `ext 73 (3, 132)` |
| round 1 | `plateau.round1()`, record R | `ext 104 (28,1) ; ext 90 (28,50,100) ; ext 86 (1) ; ext 33 (0)` |
| the split | `plateau.split()`, record S | ping, flash, staging, punch, flight, load, round 2 |
| round 2 | the same record S, its last four ops | `ext 104 (28,1) ; ext 90 (28,0,50) ; ext 86 (1) ; ext 33 (0)` |
| round 2's death | the plateau's own item list and table D2 | `ending_fight`'s record K, unchanged |

### The split is a ROUND BOUNDARY, not a new mechanism

`B0832`'s vanilla wiring and our own Cell Jr relay agree, and where they differ I followed ours.

- **The head is celljr's relay head, byte for byte**: `ext 46 (60)` ping, `ext 42 (10)` / `ext 43 (10)`
  white flash pair, `ext 69 (40)` hold. Those are celljr's own `DING`, `RELAY_FLASH` and `DING_HOLD`
  (`B0898`, `B0938`), which he has play tested three times. Vanilla's own hand-off `rom:0x3EC758`
  word 0 (`B0748`) opens the same way, so the two do not disagree here.
- **The punch is celljr's `_melee()`**, set 28 in place of set 31 (`B0900`):
  `ext 63 ; ext 57 (0,7) ; ext 69 (8) ; ext 112 (28,34) ; ext 95 (28) ; ext 121 (28,2) ;
  ext 136 (28,244,392,600) ; ext 64`.
- **The flight is celljr's "fly to C" pair**: `ext 121 (0,12)` then `ext 136 (0,248,392,500)`.
- **The hand-off is `B0748`'s shape**: a cover, `ext 39`, a settle, the facing, the camera park, the
  reveal. A death event that loads the next map is vanilla (`B0654`: Cell type 21's death event loads
  map 14,3 with `ext 39`).
- **The re-arm is `B0832`'s**: `ext 104` rebuilds the beaten actor from the map's own enemy item, and
  `ext 90` shows the next slice of the same bar.

### Record S, decoded out of the built ROM

```
ext 88 ; header_bit1(0) ; sound(60) ; palette_fx(10)
  move_to(0,248,568) ; face(0,1) ; remove(28) ; spawn(28,244,504) ; face(28,0) ; camera(136,432,40)
flash_wait(10) ; wait(40)
block_begin ; pose(0,7) ; wait(8) ; hit(28,34) ; face_target(28) ; fly_pose(28,2)
             ; walk_fast(28,244,392,600) ; block_end ; wait(20)
fly_pose(0,12) ; walk_fast(0,248,392,500) ; wait(20)
fade_out(30) ; load_map_at(7,100,1,248,568) ; wait(120) ; face(0,1) ; camera(136,432,2)
             ; fade_in(30) ; wait(60)
ext104(28,1) ; bar_set(28,0,50) ; header_bit1(1) ; camera_follow(0) ; next 26 = END
```

The staging block hides under the white flash. A beaten boss keeps the boss descriptor and stays
standing wherever the fight left him, which is nowhere in particular, so the record puts the pair back
on the fight spots before anyone sees them. The `ext 52` plus `ext 51` swap for a plain NPC Cell is
`ending_fight`'s record K's own shape.

---

## 3. The bar: an even split is legal, and it is MEASURED, not assumed

The owner's call was a true half. It stands, and the measurement that settles it is `ext 85`'s handler.

- `ext 90 bar_set` is `sub_0800AB44`: it pops three values and calls `Sprite_NewSpan @0x080104C0`
  with the actor in r1 and the two numbers in r2 and r3.
- `ext 85 bar_show` is `sub_0800AB1A`: it pops ONE value and calls **the same builder** with
  `r2 = 0` and `r3 = 0x64`.

So **the whole bar IS `(0, 100)`**. `lo = 0` is not a new value the engine has never seen; it is the
value every single bar in the game already passes. `(50, 100)` then `(0, 50)` is therefore as legal as
vanilla's uneven slices, and it reads as two true halves.

`Sprite_NewSpan` stores the segment as two bytes, `+0x15` = f(lo) and `+0x16` = f(hi) - f(lo), where
f scales by 60 and divides. So `lo` is the segment's START on the 60 px bar and `hi - lo` its WIDTH,
and nothing divides by `lo`. **Limit:** I could not find the code that DRAWS from `+0x15` and `+0x16`.
Two searches of the disassembly for readers of those offsets returned only the builder itself. So the
arithmetic is confirmed and the look on screen is not.

Each round is a FULL HP round. `ext 104` rebuilds Cell from the item, so round 2 starts him at type
60's own HP 5210 again. That is vanilla's shape too: Perfect Cell's two rounds are HP 5160 then 5500.

---

## 4. The defect the checks caught: THREE words named record F, not one

`future_androids` gives each android enemy a COPY of the live 27 word ending table (its step 8), so
ending word 23 exists in three places. In this build they are `rom:0x3B819C`, `rom:0x940AC0` and
`rom:0x940B2C`. **After a real android fight the scene runs out of the android's own copy**, so
repointing only the ending table's word 23 would have left the old whole-bar record F running on every
path that actually goes through a fight, which is every path the player can take.

All three now name record R. `plateau._check` builds that list from `future_androids`' own notes and
then proves no OTHER word inside any module's allocation still names record F.

A fourth namer, `rom:0x3936CC`, is a vanilla data word that happens to hold the same four bytes. It is
not a table word and it is left alone; the check treats only a namer inside a module's own allocation
as a finding.

---

## 5. Round 2 needed its own item, or the fight would never end

Until rung 5 the plateau entry carried **battle_arena's own item list**. An item carries its death
event at `+0x14`, so map 7,100's enemy was map 6,100's enemy, with the same death table. Making table
D word 0 the split would then have split the fight again on the plateau, for ever.

The plateau now carries its own 2 item list:

- item 0, NPC Imperfect Cell, condition 0, at `(244,504)`, so the map load builds him and `ext 104`
  has an actor of set 28 to replace. The arena's NPC stands at `(288,392)` because the vanilla talk
  walks him; nothing walks him here, so the item carries the fight spot itself.
- item 1, the enemy, condition 1, vanilla type 60 (HP 5210, AI 80, boss descriptor), with its OWN
  event struct naming table D2. D2 is the live 27 word table with word 0 left at `ending_fight`'s
  record K, so round 2's death runs the collapse, the vanilla blast and the vanilla tail into
  "@^The End.".

Vanilla splits the same way: Perfect Cell's two rounds are map 12,6 items 4 and 1, two items with two
death tables (`B0981`).

The plateau's TILES, COLLISION and LAYOUT ART were not touched and were not regenerated. The entry
changed from two words to three: `+0x00` zone, `+0x14` item list, `+0x2C` layout array.

The music does not restart across the split. The plateau entry carries song 38, the same song the
arena carries and the same song the ending itself started, and `loc_0800C4F4` skips `music_play` when
that exact record is already playing. So record S needs no `ext 49`, and it has none.

---

## 6. The sprite envelope, proved by arithmetic

Bible `B0246`: set 28 reaches 20 left, 44 right, **56 up** and 8 down; the Trunks sets reach 8, 24,
**24 up** and 8 down. A view is 240 x 160 from its TOP LEFT.

| actor | spot | drawn box |
|---|---|---|
| Imperfect Cell | (244, 504) | x 224..288, y **448**..512 |
| Trunks | (248, 568) | x 240..272, y 544..576 |
| the parked view (136, 432) | | x 136..376, y 432..**592** |

So both fit whole, with 16 px of clear air over Cell's head. **`ending_fight`'s own `VIEW`,
`(136,456,2)`, would have cut 8 px off the top of his tallest frames**, which is why record S parks
its own view and does not reuse it. `(136,432)` is vanilla record 13's own pair.

After the punch Cell sits at `(244,392)`, feet at 400, which is 32 px above the view top: off screen.
Trunks follows to `(248,392)`, feet at 400, also off screen. Both numbers are asserted in
`plateau._check_design`, so a later change to a spot or a view fails the build rather than the eye.

The camera clamps read back from the built ROM allow both parks: map 6,100 is (273, 553) and map
7,100 is (1041, 1121), so the top left may reach (272, 552) and (1040, 1120).

`CELL_SPOT` and `TRUNKS_SPOT` are both already in the plateau's `FIGHT_SPOTS`, so `_check_design`
proves the ground under Cell's whole 56 px envelope is open. **When the owner composes the real map
7,100, those two spots and the air above them have to stay open.**

Set 28 has anims 0-3, 5-10, 12, 18 and 19 (`B0244`), so it has state 2 (hurt) and state 12 (fly) and
nothing here asks it for the anim 4 it does not have. Set 132 has 0-9, 11-14, 16-18 and 20 (`B0242`),
so the player has state 7 (attack) and state 12 (fly).

### 6a. The camera pan had to be fast, and the number is measured

`ext 31` BLOCKS until the move reports done, in distance/speed + 1 frames (`B0766`), and the screen
holds WHITE between `ext 42` and `ext 43`. Round 1 ends with the FOLLOW camera on the player, and he
may stand anywhere inside map 6,100's clamp (273, 553). The worst pan from there to `(136,432)` is
about 180 px.

- At speed 2 that is about 90 frames, so about **1.5 seconds of solid white**.
- At speed 40 it is about 5 frames, which the flash hides. `SPLIT_VIEW` is therefore `(136, 432, 40)`.
  The precedent is celljr's record N, which parks vanilla seq 11's camera at speed 40 under its fade.

`ARRIVE_VIEW` keeps speed 2. The map load has just centred the camera at `(248 - 112, 568 - 76)`,
which is `(136, 492)`, so its pan is a known 60 px, about 31 frames, and it runs under a fade.

### 6b. The same trap in record K, and how it was separated

**`ending_fight`'s record K had the same problem, worse, and round 2 is what exposes it.** Record K is
the death record: it opens `fade_out(30)` and parked `ext 31 (136, 456, 2)`. It parks from wherever
the FOLLOW camera left the view when the enemy died, which is wherever the player was standing, and
it now runs on the 1280 x 1280 plateau, whose clamp is (1041, 1121).

| where the player beat Cell | pan to (136,456) | frames at speed 2 | black screen |
|---|---|---|---|
| the middle of the arena top | about 255 px | about 128 | about 2.1 s |
| the far south east of the top | about 770 px | about 385 | about 6.4 s |

**The shared constant was NOT raised.** Record A and record K both read `VIEW`, and record A's park is
on the arena, which the owner has approved. So `ending_fight` now carries a second constant,
`DEATH_VIEW = VIEW[:2] + (40,)`, and only record K reads it. Record A still reads `VIEW` and still
parks at speed 2.

**The proof that the arena path did not move.** `zigzag(2)` and `zigzag(40)` are both ONE byte, so the
record does not change length and no allocation moves. Read out of the two built ROMs:

- **v4 and v5 differ in exactly ONE byte**, `rom:0x9406ED`, the speed byte inside record K.
- Record A, `rom:0x94064C`, 65 bytes: byte-identical to v4, and it still carries `ext 31 (136,456,2)`.
- Record R, `rom:0x94CAD0`, 26 bytes: byte-identical to v4.
- Record S, `rom:0x94CAEC`, 199 bytes: byte-identical to v4.
- Record K, `rom:0x9406A8`, 154 bytes: the only record that changed, and its length is the same.
- **`ext 31 (136,456,2)` occurs exactly ONCE in the whole 16 MB ROM**, at `rom:0x940672`, which is
  inside record A. `ext 31 (136,456,40)` also occurs exactly once, inside record K.

The one side effect, said plainly: in `build_list_trial_ending.txt` and `build_list_trial_future.txt`,
which carry no plateau, record K still runs on the arena and now parks at speed 40 there too. That is
a shorter black screen, never a longer one, on two lists the rung 5 build supersedes.

---

## 7. The future androids now explode. Both questions answered.

**(a) Does the spark effect id and the sound suit an android rather than a Cell Jr? YES, because
neither is keyed to a set.**

- `ext 94 (actor, dx, dy)` builds ONE fixed effect, id `0x27`, descriptor `0x086D7750`, at the
  actor's own centre (`B0793`). Nothing on that path reads the actor's set, and the effect follows
  the body it is built on.
- Sound 31 is not a Cell Jr sound. It is one of the two the engine's OWN enemy poof picks at random,
  `rand_n(2) + 0x1F` (`B2007`), so it is the game's generic enemy death sound.
- **What it cannot be:** the real smoke is effect `0x28`, and no script op builds it. The two `ext 94`
  call sites pass `0x27`, and only the normal death release passes `0x28` (`B2014`). So `0x27` plus
  sound 31 is the closest a script can get for any actor, and `B0900` records that it reads as an
  explosion in play.

**(b) Does the boss descriptor suppress the poof here? YES, and there is nothing to suppress.**
Read back from the BUILT ROM: enemy type 3 (Android 17) HP 3550, AI 21, `+0x14` = `0x086FF3C4`; type 4
(Android 18) HP 2910, AI 21, the same. `future_androids` writes no type entry, so both keep it. That
descriptor's release `@0x0801A82C` runs the EXP task and the event task only, with no world remove and
no effect (`B2004`, `B2006`). The NORMAL descriptor is the one that builds the poof. So the engine
shows nothing at all when an android reaches HP 0, which is exactly what he saw, and the explosion has
to be scripted.

**What I did NOT copy, and why.** celljr's `_explode()` wraps the remove in `ext 42` and `ext 43`, a
fade to white and back. Both ops are on `future_androids`' own `NO_TRANSITION_OPS` list, which carries
his "NO transition" rule for these two records. So the explosion is `ext 94 (set,0,0) ; ext 46 (31) ;
ext 69 (12) ; ext 52 (set)`: spark, sound, a short hold, then the body goes. **Ask him whether he wants
the white flash as well.** It is one constant away, and it is what makes the Cell Jr version read as a
bang rather than a spark.

---

## 8. The suite

`py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent`,
run whole, never piped.

- **Before the test updates:** 1710 tests, 3 failures, 6 errors, 3 skipped, 1 expected failure.
  The count is lower than the final one partly because `test_plateau`'s whole class counted as ONE
  error when its `setUpClass` raised, instead of its 31 tests.
- **The whole suite, on the v4 tree: 1774 tests, 1 failure, 3 skipped, 1 expected failure, REAL
  EXIT CODE 1.** The count moved from 1745 to 1774 between two runs 15 minutes apart, and none of
  those 29 tests is mine: `editor-persist` was writing `test_map_editor_io.py` and a new
  `test_map_editor_cells.py` in the same tree while this ran. Both are green.
- **I did NOT run the whole suite again for v5, and the reason is that the tree is not quiet.**
  `editor-persist` wrote `map-editor\editor\tools.js`, `map-editor\editor\cells.js`,
  `tests\test_map_editor_io.py` and `tests\test_map_editor_cells.py` while this change was being
  made. A whole-suite run across another agent's half-written files proves nothing either way.
  Instead I ran the 13 test files this change can reach, whole, each with its own exit code:

  | file | tests | result |
  |---|---|---|
  | `test_ending_fight` | 49 | OK |
  | `test_plateau` | 31 | OK |
  | `test_future_androids` | 44 | OK |
  | `test_battle_arena` | 61 | OK |
  | `test_battle_start` | 38 | FAILED, the known one |
  | `test_build` | 21 | OK |
  | `test_golden` | 14 | OK |
  | `test_bible_ids` | 11 | OK, 1 expected failure |
  | `test_celljr_fight` | 83 | OK |
  | `test_scene_lib` | 40 | OK |
  | `test_cellgames_ssj` | 31 | OK |
  | `test_vegeta_ssj_scene` | 48 | OK |
  | `test_beam_struggle` | 27 | OK |

  **498 tests, 1 failure, 1 expected failure, worst exit code 1.**
  The one failure, in both runs, is the known
  `test_battle_start.test_form_survives_the_leader_change`, which flags `fullpower_ssj`'s record
  `rom:0x89A9C0` on map 9,3 and has nothing to do with this work.

Tests changed, all of them expectation updates to match the new design:

- `test_ending_fight.py`: record A's form op is `(73, (3, 132))`, in `ARRIVE_OPS` and in
  `test_the_form_and_the_leader_are_set_in_front_of_the_load`. Added `BASE_TRUNKS` so the constant
  reads as what it is. `DEATH_HEAD` carries the new camera speed, and a new test,
  `test_the_two_camera_parks_share_a_point_and_not_a_speed`, pins the separation itself so nobody
  collapses the two constants back into one.
- `test_future_androids.py`: `blast_ops()` ends with the new `explode_ops()`, and `EXT_ARITY` learned
  ext 46 and ext 94 so the branch evaluator can run the two death records.
- `test_plateau.py`: the two record-A tests are gone, replaced by eight that read the round split out
  of the built ROM: every namer of record F moves, round 1's bar, the split's shape and order, the two
  halves meeting at 50, round 2's own item and event struct, D2's words 0, 24 and 25, the NPC on the
  fight spot, and both parked views against the envelopes.

---

## 9. What I could NOT prove without a play test

Stated plainly. None of these is covered by a green suite.

1. **`ext 136` on an NPC.** celljr drove the `ext 121` + `ext 136` knock-back on an ENEMY object. The
   split drives it on the plain NPC Cell the record spawns. LIKELY, not confirmed. If the throw does
   not play, Cell stands still while Trunks flies off, and `ext 54 fly` is the one-line fallback.
2. **How the two bar halves LOOK.** The handler arithmetic is confirmed; the code that draws from
   `+0x15` and `+0x16` was not found and not read.
3. **Whether the white flash really covers the staging.** The pan is now bounded (section 6a) but
   not timed in play. If it shows, the flash length is the dial.
8. **The white flash on the android deaths is still an open question for him** (section 7). His answer
   had not arrived when this build was made, so it is not in v5.
4. **Whether the base body swap at record A is visible.** It runs after `fade_out(180)` and the player
   object already exists on map 1,100 at that point, so `sub_0800A8EC` rebuilds his body live. It
   should be under the black. His eye decides.
5. **Whether the punch reads as a punch.** `ext 57 (0,7)` is the player attack state and the hit lands
   on a fixed frame count, not on a hit test.
6. **Whether 120 frames is the right settle and 60 the right hold** on the plateau arrival.
7. **The whole of round 2's feel**: the same enemy at full HP again, twice in a row.

---

## 10. Files changed

```
scripts\permanent\patches\ending_fight.py        record A's form op, DEATH_VIEW, the docstrings
scripts\permanent\patches\future_androids.py     explode(), and the death beat docstring
scripts\permanent\patches\plateau.py             the round split: round1(), split(), the item
                                                 builders, the checks and the wiring
scripts\permanent\build_list_trial_plateau.txt   its header comment
scripts\permanent\tests\test_ending_fight.py     the form expectation
scripts\permanent\tests\test_future_androids.py  the explosion expectation
scripts\permanent\tests\test_plateau.py          the round split tests
```

Nothing was committed.

---

# Rung 5 refinements: the base portrait, weaker future enemies, the punch in close

Built 2026-11-08 on top of v5. Trial ROM `builds\mockups\2026-11-08-rung5\log2_rung5_v6.gba`,
SHA-1 `5bd306c547bec83004d6f202b0af12ee38d0aa87`, 16 MB, with `log2_rung5_v6.sav` beside it (seeded
from `builds\log2_poc_r40.sav`). Same trial list, `build_list_trial_plateau.txt`. `build_list.txt`
was not touched, and v4 and v5 are both still there, byte for byte.

His words, from `docs\backlog\active-todos.md`: "the portrait for trunks when talking to cell should
use base / The stats for future 17 and 18 should be weaker than vanilla, that is actually canon.
Same for cell, this is cell before he absorbs people ... Weaker stats, like 25% / For the cutscene,
trunks should walk to cell and punch him, not punch him a mile away. Otherwise much better."

Every value below was read back out of the BUILT ROM, not out of a module.

---

## 11. The Cell talk shows BASE Trunks

**The pair is the appearance table's own, read on the base ROM.** Entry 15 is set 132 with dialog
portrait **100**; entry 16 is set 133 with dialog portrait **101**. Ids above 7 are raw table
indices and skip the record, so a cutscene record carries one of those two numbers directly.

**Four records changed, one byte each, and all four are the CELL talk.**

| ending word | record | type | was | now |
|---|---|---|---|---|
| 14 | `rom:0x3B7E74` | 1 | 101 | **100** |
| 16 | `rom:0x3B7EB0` | 1 | 101 | **100** |
| 20 | `rom:0x3B7F10` | 2 | 101 | **100** |
| 22 | `rom:0x3B7FE0` | 1 | 101 | **100** |

**Four more records still read 101, on purpose.** Words 5, 7, 10 and 12 all sit before the boundary
at `rom:0x3B7E5E`, the map load inside record 13, so they belong to the 17/18 scene, where he really
is Super Saiyan. The ROM read back confirms each is 101 and byte identical to the base.

**The edit is one byte at a record's +3, so nothing moves.** Each record keeps its address, its
length and its next index, so no table word has to move and a save state paused inside one still
runs to its end. **Proved on v6, by a WHOLE SPAN diff and not per record**: across `rom:0x3B7E74`
to `rom:0x3B8016`, which is record 14 to the start of vanilla record 23 and holds the entire Cell
talk, exactly FOUR bytes differ from the base ROM, and they are `rom:0x3B7E77`, `rom:0x3B7EB3`,
`rom:0x3B7F13` and `rom:0x3B7FE3`. The whole 17/18 span, `rom:0x3B7B08` to `rom:0x3B7E74`, is byte
identical. A span diff was used because a type 2 record's +4 word is NOT a pointer: word 20 is 80
bytes of inline stream, and every one of its payload bytes is unchanged, so no second portrait id
survives inside it.

**It reaches every path, because the records are SHARED, not copied.** `future_androids` copies the
live 27 word ending TABLE three times, and all three copies name the same four record addresses:
word 14 is named by `rom:0x3B8178`, `rom:0x940AC8` and `rom:0x940B34`, and words 16, 20 and 22 the
same way. So a byte in the record is seen by every copy.

**The dialog box does not change, only the face.** The box reads the +3 byte for the layout (cases
0, 1 and 2-7), for the style switch `@0x0800B25E` (cases 0x28, 0x31, 0x32, 0x35, 0x46, 0x54, 0x56,
0x60 and a jump table over 26-39) and for `portrait()`. 100 and 101 are both outside every one of
those cases, so both take the same default (bible `B0339`).

---

## 12. The three future enemies are 25 percent weaker

**MY READING, which he should correct if it is wrong: 25 percent WEAKER than vanilla, not reduced to
25 percent of vanilla.** That is what is built. If he meant a quarter of vanilla, the Cell fight
would drop to about 1300 HP a round, which is less than a Cell Jr, so the weaker reading is also the
defensible one.

### The boundary, and why no vanilla type entry was edited

All three of these types ALSO spawn in the main game, so editing any of them in place would have
weakened fights he ruled out on 2026-11-07 ("We do not touch any earlier 18 and 17 fights").

| type | who | vanilla spawns |
|---|---|---|
| 3 | Android 17 | map 11,4 item 1, map 11,5 item 0, map 11,6 items 0 and 4 (Piccolo's fights) |
| 4 | Android 18 | map 8,49 item 0 |
| 60 | Imperfect Cell | map 10,20 item 0 |

**So each future enemy gets its OWN type entry, and that is our own worked example.** `celljr_fight`
already allocates a trial type entry in the expansion area ON the enemy table's 24-byte stride, so
(entry - 0x6D56AC) / 24 is a type id the factory resolves (`@0x0800E780`: `ldr r1,[r0,#0x8]`,
`ldr r2,=0x086d56ac`, `add r2,r1,r2`, with no bound check). That has shipped in `build_list.txt`
since r41 and he has play tested it, so a type id of this size is proven in play.

### The table, read out of v6

| enemy | type id | entry | EXP | HP | AI | STR | POW | END | descriptor |
|---|---|---|---|---|---|---|---|---|---|
| vanilla Android 17 | 3 | `rom:0x6D56F4` | 0 | 3550 | 21 | 32 | 39 | 34 | boss |
| **future Android 17** | 105698 | `rom:0x940BDC` | 0 | **2660** | 21 | **24** | **29** | **26** | boss |
| vanilla Android 18 | 4 | `rom:0x6D570C` | 0 | 2910 | 21 | 29 | 34 | 27 | boss |
| **future Android 18** | 105694 | `rom:0x940B7C` | 0 | **2180** | 21 | **22** | **26** | **20** | boss |
| vanilla Imperfect Cell | 60 | `rom:0x6D5C4C` | 0 | 5210 | 80 | 32 | 32 | 37 | boss |
| **future Cell** | 105654 | `rom:0x9407BC` | 0 | **3910** | 80 | **24** | **24** | **28** | boss |

**The rounding rule, stated.** HP is value x 3 / 4, rounded half up onto a multiple of 10, because
all three vanilla values are multiples of 10. STR, POW and END are value x 3 / 4, rounded half up.
So END 34 becomes 26, which is 23.5 percent off, and POW 39 becomes 29, which is 25.6 percent off.
Nothing is more than one unit from the exact quarter.

**What I changed, and what I left.**

- **Changed:** HP, STR, POW and END. Those are the four the scouter calls an enemy's stats
  (bible `B1793`) and the four he named.
- **Left, and why:** EXP is already 0 on all three, so there is nothing to scale. The AI id stays
  (21, 21 and 80), because he asked for a weaker fighter and not a different one. The two damage
  factors at +0x10 stay at 0x80/0x80, the value almost every type carries. The death descriptor at
  +0x14 stays the BOSS one, because every death record here poses the body down and removes it
  itself, which the normal descriptor's own poof and remove would fight.
- **Confidence:** HP is CONFIRMED to decide the fight's length. STR, POW and END are LIKELY the
  enemy's damage and defence: they are what the scan screen reads out of the type entry, and the
  player's own END feeds the damage formula as `0x80 - END` (`B0445`), but I did not read the enemy
  side of that formula.

### FOUR items were retyped, not two

| item | map | who | names |
|---|---|---|---|
| `rom:0x940BA4` | 1,100 item 2 | future Android 18, set 11 | type 105694 |
| `rom:0x940C00` | 1,100 item 3 | future Android 17, set 9 | type 105698 |
| `rom:0x93B628` | 6,100 item 1 | round 1's Cell, set 28 | type 105654 |
| `rom:0x94CB2C` | 7,100 item 1 | round 2's Cell, set 28 | type 105654 |

Both Cell items name the SAME entry, so the two rounds fight the same enemy. The plateau's item is a
live copy of the arena's, so it inherits the type, and `plateau._check` now proves the two agree
rather than trusting the copy.

### Proof that the main game did not move

Read back from v6:

- Enemy types 3, 4 and 60 are **byte identical to the base ROM**.
- The six vanilla spawns still name them: map 8,49 item 0 (type 4), map 10,20 item 0 (type 60), map
  11,4 item 1, map 11,5 item 0 and map 11,6 items 0 and 4 (type 3), each item byte identical.
- A walk of every enemy item in every map of v6 finds exactly FOUR items on a type above 108, and
  they are the four in the table above. `celljr_fight`'s own trial type 104780 (HP 1550) is
  untouched beside them.
- **Nothing in the 16 MB ROM points at any of the three vanilla entries.** A scan for the words
  `0x086D56F4`, `0x086D570C` and `0x086D5C4C` returns zero hits, so no code special-cases these
  enemies by their type entry. The object keeps the entry POINTER at +0x180, so a new entry cannot
  collide with a vanilla one.

### The limit he needs to know about

**The three future enemies cannot be SCANNED, and the no-match path is guarded.** The engine has
TWO scouter matchers, and an ENEMY uses the one that matches by TYPE:

- `Table_FindByDirectory @0x08019102` matches an object by its SET, walking all 128 entries and
  taking the first hit. Its caller is `sub_08007B08`, the NPC-side message handler.
- `sub_080190D4` matches by the object's TYPE ENTRY POINTER, which an enemy keeps at +0x180: for
  each of the 128 entries it computes `0x6D56AC + 24 x entry +0x10` and compares. Its ONE caller
  in the whole ROM is at `rom:0xE5EE`, inside the ENEMY object's message handler.

Our three new entries are named by no scouter entry, so `sub_080190D4` falls out of its loop and
returns -1 (`mov r0,#0 ; mvn r0,r0`). **The caller guards that exactly**: `add r3,r0,#1 ; bne ... ;
mov r0,#0 ; b exit`, so it returns 0 and appends nothing to the list it builds. Nothing crashes,
nothing is read out of range, and no index is used; the enemy is simply not offered to the scouter.
`celljr_fight`'s three trial Jrs have had the same property since r41 and he has played them.
While Cell is still the NPC, before `ext 104`, the SET path would find entry 11 and show vanilla
type 60's numbers. His own next item, the three new scouter entries, is what closes both, and it
was out of scope here.

---

## 13. The punch lands in close

**What it was.** The staging under the white flash put the player on `TRUNKS_SPOT` (248,568) and
Cell on `CELL_SPOT` (244,504), 64 px apart, and the punch fired from there. That is the "mile".

**What it is.** After the flash and the 40 frame hold, the player WALKS north to `PUNCH_FROM`
(248,528) and is held facing up; then the punch group runs exactly as he approved it.

```
... flash_wait(10) ; wait(40)
walk(0, 248, 528) ; face(0, 1)
block_begin ; pose(0,7) ; wait(8) ; hit(28,34) ; face_target(28) ; fly_pose(28,2)
            ; walk_fast(28,244,392,600) ; block_end ...
```

**The gap is celljr's own melee gap, twice over.** In `celljr_fight`'s finish, Gohan stands at
`MIDDLE` (432,392) and punches `PUNCH_AT` (456,392), 24 px away, and he teleports to (456,344) to
punch (456,368), again 24 px. `PUNCH_FROM` is 24 px below `CELL_SPOT`.

**The walk BLOCKS, so the punch cannot start early, and BOTH handlers were opened to prove it.**
`sub_08009D4A` (ext 53) ends in `BL Queue_Append @0x0800E04C`, with the same four instruction tail
as `sub_08009FC4` (ext 57), the op this module already relies on to block. `Queue_Append` appends
the command and then, when the group flag word is 0, runs `BL 0x0800DE20` and `BL 0x0801F2F4`, the
frame loop, before it returns. The command tick is the shared mover `@0x0801090A`, which runs until
the actor arrives (`B0691`, `B0787`). An `ext 63` group is what makes several moves run in PARALLEL,
which is why celljr's arrivals use one and this does not. Walk, then punch, is also vanilla's own
shape: table `rom:0x3E6F30` seq 18 runs `ext 53 (29,176,192)` then `ext 57 (29,6)` (`B0789`).
**Correction to an earlier citation:** `B0604` and `B1775` are about `ext 57` and the scene push
and say nothing about `ext 53`; `future_androids`' own docstring cites them the same way and should
be corrected in the next wave that touches it.

**It is a straight walk north, and that is checked.** `PUNCH_FROM` shares TRUNKS_SPOT's x, so the
mover cannot leave him facing sideways at the moment of the punch, and the `ext 55` after it pins
the facing anyway. 40 px at `ext 53`'s own 1 px a frame (`B0691`) is about 40 frames.

**The envelope, and the ground.** The parked view (136,432) covers y 432..592.

| actor | spot | drawn box |
|---|---|---|
| Imperfect Cell | (244, 504) | y 448..512, whole |
| Trunks, staged | (248, 568) | y 544..576, whole |
| **Trunks, at the punch** | **(248, 528)** | **y 504..536, whole** |

The two boxes overlap by 8 px at the punch, which is what a punch should look like: celljr's own
pair overlap by 20.

**The ground is proved on the ARENA, which is where the punch happens.** `_check_design` proves the
PLATEAU's generated collision, so it could not have covered this. `plateau._check` now reads map
6,100's own live collision frame and proves every 8 px cell under Trunks' envelope is open at every
step of the walk, from y 568 to y 528. Read back from v6, the whole block x 208..300, y 480..584 is
open on map 6,100 and on map 7,100 alike.

**Record S is 214 bytes now, against 199 in v5**, so v5's "exactly one byte differs" proof does not
carry over and was not reused. Everything else in the record is unchanged, op for op.

---

## 14. The suite

Run per file, each whole, never piped, each with its own real exit code. **The full suite was NOT
run, because another agent is writing `scripts\permanent\map-editor\` and the map tests in the same
tree, and a whole-suite run across another agent's half-written files proves nothing either way.**

| file | tests | exit | result |
|---|---|---|---|
| `test_ending_fight` | 58 | 0 | OK |
| `test_plateau` | 33 | 0 | OK |
| `test_future_androids` | 46 | 0 | OK |
| `test_battle_arena` | 61 | 0 | OK |
| `test_build` | 21 | 0 | OK |
| `test_golden` | 14 | 0 | OK |
| `test_bible_ids` | 11 | 0 | OK, 1 expected failure |
| `test_celljr_fight` | 83 | 0 | OK |
| `test_scene_lib` | 40 | 0 | OK |
| `test_chamber_spar` | 27 | 0 | OK |
| `test_superperfect_cell` | 48 | 0 | OK |
| `test_cellgames_ssj` | 31 | 0 | OK |
| `test_vegeta_ssj_scene` | 48 | 0 | OK |
| `test_beam_struggle` | 27 | 0 | OK |
| `test_status` | 27 | 0 | OK |
| `test_art_inject` | 19 | 0 | OK |
| `test_chapter_cards` | 75 | 0 | OK |
| `test_bf_ki_pool` | 35 | 0 | OK |
| `test_fullpower_hud` | 22 | 0 | OK |
| `test_capture` | 46 | 0 | OK |
| `test_roundtrip` | 22 | 0 | OK |
| `test_battle_start` | 38 | **1** | FAILED, the known one |

**832 tests, 1 failure, 1 expected failure, worst exit code 1.** The one failure is
`test_battle_start.test_form_survives_the_leader_change`, which flags `fullpower_ssj`'s record
`rom:0x89A9C0` on map 9,3 and has nothing to do with this work.

`test_chamber_spar` and `test_superperfect_cell` were added to the list because both read the enemy
type table; both are green, so the new entries disturbed neither. `test_bf_ki_pool`,
`test_fullpower_hud`, `test_capture` and `test_roundtrip` were added because a grep of the tests for
the enemy table and for the id 101 matched them; all four are green.

Tests changed or added:

- `test_ending_fight.py`: `TalkPortraitTests` (4 tests: the appearance pair, the four Cell talk
  records, the four 17/18 records that stay, and the one-byte proof) and `WeakCellTests` (5 tests:
  the rounding rule, vanilla type 60 untouched, the new entry on the stride with only four fields
  moved, the arena item retyped, and map 10,20's own item still on type 60). The base footprint test
  now expects the two table words plus the four portrait bytes.
- `test_future_androids.py`: the enemy item test now expects the new type ids; two new tests, one
  for each weaker entry and one proving the five main game android items still name types 3 and 4.
- `test_plateau.py`: two new tests, the walk before the punch (order, spot and gap) and the punch
  spot against the ARENA's own collision frame and the parked view.

---

## 15. What needs HIS eye

1. **Is "25 percent weaker" the right reading?** Say so if he meant a quarter of vanilla.
2. **Two full rounds now cost 2 x 3910 = 7820 HP**, against 5210 for the main game's one-round
   Imperfect Cell. The split makes the fight longer even after the weakening.
3. **Does the walk read as a walk?** It is 40 px, about 40 frames, straight north.
4. **Does the punch still read as a punch at 24 px**, with the two sprites overlapping by 8 px?
5. **The three future enemies cannot be scanned** while they are live enemies (section 12). That
   is his own next item, the three new scouter entries, and it is safe, not broken.
6. Everything in v5's own section 9 is still open and still needs a play test: `ext 136` on an NPC,
   how the two bar halves look, whether the flash covers the staging, and the white flash on the
   android explosions, which he has not answered yet.

---

## 16. Files changed

```
scripts\permanent\patches\ending_fight.py        the four portrait bytes, weaken(), weak_type(),
                                                 _alloc_on_stride(), the future Cell type
scripts\permanent\patches\future_androids.py     a weaker type per android, and the item retype
scripts\permanent\patches\plateau.py             the walk before the punch, the arena ground check,
                                                 the round 1 and round 2 type agreement check
scripts\permanent\tests\test_ending_fight.py     9 new tests, 1 expectation updated
scripts\permanent\tests\test_future_androids.py  2 new tests, 1 expectation updated
scripts\permanent\tests\test_plateau.py          2 new tests
```

`battle_arena.py` and `celljr_fight.py` were NOT edited; their SHA-1s are unchanged from before this
work. Nothing was committed.
