# Report: the owner's finale dialogue, his music picks and the transition cut

Built 2026-11-08 from `docs\design\2026-11-08-finale-dialogue.md`, sections 1 to 4 plus the
transition cut. Files owned and changed: `scripts\permanent\patches\ending_fight.py`,
`scripts\permanent\patches\plateau.py`, `scripts\permanent\tests\test_ending_fight.py` and
`scripts\permanent\tests\test_plateau.py`.

> **One file outside the owned set was edited:** `scripts\permanent\tests\test_battle_start.py`.
> It is a SHARED test. One pin changed, the rule 5 census from 16 to 17, with a comment that names
> the reason. Nothing else in that file moved. The controller should check this against the
> parallel blast and death agent, because both of us can reach it.

Trial ROM: `builds\mockups\future\finale_dialogue_wip4.gba`, SHA-1
`d6c15081475a0c6c9f30943dd2dcf1cd61017674`, built from
`scripts\permanent\build_list_trial_plateau.txt` with no module added. Nothing is named `future_v3`,
and the controller names and ships the final ROM.

> Three earlier scratch ROMs are superseded and can be deleted:
> `builds\mockups\future\finale_dialogue_wip.gba`, `finale_dialogue_wip2.gba` and
> `finale_dialogue_wip3.gba`, with their `.log` files. I did not delete their paired `.sav` files,
> and I deleted no save of any kind.

---

## 1. What is in the build

Every record below was decoded OUT OF THE BUILT ROM, not out of the plan. The listings are in
`scripts\one-time\2026-11-08-finale-dialogue-build\05_readback.txt` and `06_tabled.txt`.

### Section 1, after Trunks beats future 17

Ending word 12 names a new type 1 record, portrait 101, next 13, with three boxes:

```
I wish I could say that it's all over,
but there is one more thing that has to be done
... Cell
```

`... Cell` has its own box, as the design settles. The vanilla record `rom:0x3B7E0E` keeps all 0x3B
of its bytes; only the table word moves.

### Section 2, the new caption

Ending word 24 names a new type 1 record, portrait 0, text `@^Three years later...`, next 25.

Track 42 starts at the END of record A, after the map load and immediately before `ext 45`, so the
box opens on it. The built order of record A is `wait(30)` → `fade_out(90)` → `appearance(3,132)` →
`leader(3)` → `load_map_at(6,100,1,248,624)` → `wait(120)` → `camera(136,456,40)` →
`header_bit1(0)` → `move_to(0,248,664)` → `music(42)` → `ext 45`, then word 24's box. The cue must
sit after the load: see section 3b.

### Section 3, at Capsule Corp

Ending word 22 names a new type 1 record, portrait 100 (base Trunks), next 23, with two boxes:

```
If you can get past me then you can to the past
But I wont let you!
```

The late `THE NIGHTMARE IS OVER CELL!!!!!` was NOT touched. Only the early copy, inside vanilla
record `rom:0x3B7FE0`, is replaced, and that record keeps all 0x36 of its bytes too.

Ending word 23, round 1's battle start, now opens with `music(28)`.

### Section 4, the plateau arena talk

Table D words 1 to 7, in his beat order. The two `[PLACEHOLDER ...]` records are gone.

| word | who | text |
|---|---|---|
| 1 | Cell (portrait 38) | `Your energy will be refreshing.` then `A nice treat to start of my journey in the time machine` |
| 2 | Trunks (portrait 100, base) | `Enough!` |
| 3 | the transform | `ext 73 (3,132) ; sound(55) ; pose(0,9) ; palette_fx(10) ; sound_stop(55) ; ext 73 (3,133) ; flash_wait(10) ; face(0,EAST)` |
| 4 | Trunks (portrait 101, Super Saiyan) | `You're overconfident Cell.` |
| 5 | Cell (portrait 38) | `There's no reason not to be,` then `I've come across thousands like you` |
| 6 | Trunks (portrait 101) | `But count me as the last!` |
| 7 | round 2 starts | `music(35) ; ext 104 (28,1) ; bar_set(28,0,50) ; header_bit1(1) ; camera_follow(0)` |

The transform sits between the two Trunks lines, as he wrote it, and the portrait turns Super Saiyan
only after it.

### The transition cut

All four values are in record A and all four moved. `REC13_SETTLE`, the `wait(120)`, was NOT touched.

| op | from | to |
|---|---|---|
| opening `wait` | 60 | 30 |
| `fade_out` | 180 | 90 |
| `fade_in` | 180 | 90 |
| `camera` speed | 2 | 40 |

The vanilla record `rom:0x3B7E4A` still holds all 0x29 of its own bytes, and the module still reads
and checks its `wait(60) ; fade_out(180)` head before it writes, so the 17/18 boundary cannot drift.

**The death camera did NOT move, and I checked rather than assumed.** `VIEW`'s speed went from 2 to
40, and `DEATH_VIEW` reads `VIEW`'s point, so this had to be proved. Before this build the two
lines were:

```
VIEW = (TRUNKS_SPOT[0] - 112, (CELL_SPOT[1] + TRUNKS_SPOT[1]) // 2 - 80, 2)   # both fighters, celljr's offsets
DEATH_VIEW = VIEW[:2] + (40,)
```

`DEATH_VIEW` took only `VIEW`'s point and carried its OWN hardcoded 40, deliberately kept apart from
record A's 2. An earlier bible row, tag RG5, says the same: "`DEATH_VIEW` = `VIEW`'s point at speed
40; record A still reads `VIEW` at speed 2". The death camera was 40 then and is 40 now. This build
only gave that literal a name, `DEATH_SPEED = 40`. Cell's death is untouched.

---

## 2. The caption decision, with the evidence

**I reused the vanilla STRING and the vanilla MECHANISM, and built a NEW RECORD.** Measured, not
assumed.

**The string and the mechanism are reusable.** `rom:0x3B8610` holds `@^Three years later...` and the
record that carries it starts four bytes earlier, at `rom:0x3B860C`: a plain type 1 record, portrait
0. It is word 8 of the time-skip table `rom:0x3B88A0` (one namer, `rom:0x3B88C0`). There is no
caption-specific mechanism at all: the `@` prefix sets the box y to 0x50 and the `^` shows the whole
box at once, and the box is then dismissed by the same A press that ends every dialog box (bible
B0893, B2095). CONFIRMED, both records decoded on the base ROM.

**The record is not reusable.** Its `+0` word is the next index 9, and an index only means something
inside its own table. Pointing an ending word at it would hand the ending's scene on to ending word
9, which is Cell's "It can't be!". So the 22 text bytes are read out of the ROM at build time and the
four byte header is rebuilt. CONFIRMED, the record header read.

**Where it runs, and why the screen is black.** The design asks for the box after the fade out and
before Capsule Corp, so it runs on black. That needs `ext 45`:

- `fade_out` ends in `Palette_LoadScaled` `@0x0800DA96`, which scales the saved snapshot and DMAs 512
  halfwords over the whole palette, BG half and OBJ half. CONFIRMED, the handler read in full in the
  disassembly: it builds 0x200 halfwords on the stack, then programs DMA3 twice at `0x05000000`.
- The OBJ palette writer census (bible B0270) names the title, `ext 45`, the party screen, the two
  menu scenes, the two fades and the zero fill. **No dialog box function writes palette RAM**, so
  opening a box after a fade restores nothing and the box would be black on black.
- `ext 45` `@0x08009BE4` is one DMA3 of the shared OBJ palette `rom:0x1DA6C8` and nothing else.
  CONFIRMED, the whole handler read: four pool loads, two stores, two halfword stores, `BX lr`.
- **The ending's own tail already does this.** `rom:0x3B8112` runs `ext 45` immediately before word
  24, `@^The End.`, which is the caption vanilla shows on a black screen. Record A copies that shape.

**Two indices were needed and two were free.** The ending table is 27 words with no spare, and the
caption needs one index of its own plus one for the rest of the arrival. Words 24 and 25 ARE free in
this build: vanilla chains 0 to 26 in order, so 24 is reached only from record 23 and 25 only from
record 24, and this module replaces record 23 with record F, whose next is 26. `_check_spare_indices`
walks the live table and refuses before any write if anything else reaches either index. The vanilla
end text and the `ext 97` exit are NOT orphaned: table D and table D2 name those two RECORDS by
address at their own words 24 and 25, so Cell's death still ends the game exactly as it did.
`future_androids` copies the LIVE ending table for each android enemy, so both copies inherit the
caption chain and run it identically.

---

## 3. Two real findings

### 3a. An `ext 31` above word 23 breaks the camera rule

My first build parked the view on an empty corner of the arena for the caption and put the view back
in record A2. `test_battle_start.test_camera_is_handed_back` went red on it:

```
table rom:0x3B8140 runs camera((384, 368, 2), (0, 0, 40), (136, 456, 40)) and gives control
back at rom:0x940768, but the camera is still owned by fixed
```

The checker reads a table in **walk order**, word 0 to word 26, and it says so in its own docstring.
Record A2 is word 25, so its `ext 31` read as the table's LAST fixed camera, after record F's
`camera_follow(0)` at word 23. In execution order the camera IS handed back, but any `ext 31` at an
index above 23 produces this reading, and no free index below 23 exists.

**I fixed the design, not the test.** A declared `BATTLE_START_EXCEPTIONS` entry would have been
wrong twice over: it is keyed by record address and `excused()` is global, so excusing record F for
rule 2 would silently excuse it from rule 6 as well, and
`test_exactly_the_four_scene_openings_are_declared` exists precisely to keep record F out of that
list.

The screen is made empty with `ext 62` instead of a camera move, and record A2 now sets no camera:

- Against the parked view, y 456 to 616, **the NPC Cell is already off screen**. He stands at
  `CELL_START` (288,392) and set 28 reaches 8 px below its point (bible B0246), so his lowest pixel
  is y 400, 56 px above the view top.
- Only the player pokes in. He is built at `TRUNKS_START` (248,624) and reaches 24 px up, so his top
  16 px sit inside the frame. Record A moves him to (248,664) with `ext 62` before `ext 45`, which
  puts his top at 640, 24 px below the view. Record A2 moves him back before the fade in.
- `ext 62` on the player is already shipped: record K and record S both use it.
- **Nothing else on the map is a sprite in that frame.** The arena keeps three props,
  `battle_arena.ARENA_PROPS` = (0, 3, 4), copied byte for byte from map 6,1, so they keep their
  source rects: (224,64)-(288,96) the glass door, (198,95)-(214,127) and (294,95)-(310,127) the two
  entrance pillars. Every one ends at y 127 or above, which is 329 px above the parked view top of
  y 456. No rain or weather module appears in any build list: the only `rain` hit across all of them
  is the word `scene_drain_pause`. So `ext 45` lights no sprite the frame can show. CONFIRMED,
  `battle_arena.py:131`, `test_battle_arena.SOURCE_PROP_RECTS` and a grep of every build list.

The HUD also comes off for the box. It is ON entering record A, measured: ending words 8 and 11 both
end with `header_bit1(1)` and nothing between word 11 and word 13 touches it. Record A runs
`header_bit1(0)` and record A2 runs `header_bit1(1)`, so the talk sees exactly the state it saw
before and only the caption changes.

Taking the HUD off has one side effect on the checker. Rule 5 scopes any record that shows a bar and
sits in a table that hid the HUD, so the whole of table `rom:0x3B8140` entered that scope and the
census went from 16 records to 17. Record F passes it, because it raises the bar and runs
`header_bit1(1)`. The pin in `test_battle_start.test_the_scoped_rule_5_...` is updated from 16 to 17
with a comment that names record A as the reason.

### 3b. A music cue in FRONT of a map load is overwritten by the map's own song

My first build put `music(42)` at the top of record A, before the `load_map_at`. That is wrong, and
it would have shipped the caption on the wrong track.

Bible B2176: `ext 35` never reads a map's `+0x24` music word, but **`ext 38` and `ext 39` DO**, by
way of `sub_0800C584` and `loc_0800C390`. The read skips `music_play` only when that exact song is
already playing. The arena map 6,100 carries the literal 38 in its `+0x24`. So the load would have
started 38 over my 42 the moment the arena came up.

The cue now runs AFTER the load, between the `ext 62` and the `ext 45`, which is the order the built
ROM shows at `rom:0x94068A`. One consequence the owner should hear for: song 42 now plays through
the whole Cell talk, where before the talk ran under the arena's own 38. It stops when record F or
record R starts 28. CONFIRMED, B2176 plus map 6,100's own `+0x24`, and the built record decoded.

---

## 4. The measured widths

The dialog box holds 4 lines of 144 px a page (bible B2095) and pages on past that. The widest box
the ending talk is seen to render is 294 px: ending word 3, "ANDROID 18: I guess he wants to die like
everyone else.", 3 lines. Measured on the ROM font `rom:0x2CC64` with the same line-counter model
`test_chapter_cards` uses.

**Three of his segments ran past 294 px as one box, and each was split into two boxes.** Every
character, every space and every punctuation mark is his. The break was placed at a mark HE wrote: a
comma, a full stop and a comma. No word changed and nothing was re-punctuated.

| line | as one box | split after | result |
|---|---|---|---|
| "I wish I could say that it's all over, but there is one more thing that has to be done" | **419 px, 4 of 4 lines** | `all over,` | 173 px, 2 lines, then 242 px, 2 lines |
| "Your energy will be refreshing. A nice treat to start of my journey in the time machine" | **445 px, 4 of 4 lines** | `refreshing.` | 156 px, 2 lines, then 285 px, 2 lines |
| "There's no reason not to be, I've come across thousands like you" | **334 px, 3 lines** | `not to be,` | 145 px, 2 lines, then 185 px, 2 lines |

Every shipped box, measured in the built ROM:

| box | px | lines |
|---|---|---|
| `I wish I could say that it's all over,` | 173 | 2 |
| `but there is one more thing that has to be done` | 242 | 2 |
| `... Cell` | 31 | 1 |
| `If you can get past me then you can to the past` | 247 | 2 |
| `But I wont let you!` | 95 | 1 |
| `Your energy will be refreshing.` | 156 | 2 |
| `A nice treat to start of my journey in the time machine` | 285 | 2 |
| `Enough!` | 41 | 1 |
| `You're overconfident Cell.` | 131 | 1 |
| `There's no reason not to be,` | 145 | 2 |
| `I've come across thousands like you` | 185 | 2 |
| `But count me as the last!` | 131 | 1 |
| `Three years later...` (the caption) | 97 | 1 |

Two tests now hold this, one per module, so a later edit that over-fills a box goes red.

---

## 5. The BG1 numbers, and BG0

Measured out of the BUILT ROM's own tiles, which is the only way to measure them.

| quantity | was | is |
|---|---|---|
| BG1 cells over reachable walkable ground (`test_plateau`) | 477 | **488** |
| BG1 cells that draw anywhere (the plateau docstring) | 1100 | **1109** |
| open collision cells | 4987 | **4988** |
| cells reachable from the fight spot | 4848 | **4849** |
| the sealed pocket | 139 | **139**, unchanged |

**`bg0` is 0.** BG0 draws no cell anywhere on his map, so nothing was blanked away from it and
nothing of it hides the player. That is not a defect and nothing was updated to hide one.

The number was READ, once, out of the build, and then written into the constant and the docstring.
No value was tried.

**Two different counts exist and they must not be confused.** `plateau`'s own notes carry
`art_cells: 1110`, which is one more than the docstring's 1109. That is not an error in either.
`plateau.art_cells()` counts a cell as drawing when its tile INDEX is not 0, which over-counts by
design and never under-counts. The docstring and the test count a cell as drawing only when its
tile holds a non-zero PIXEL, read from the built ROM's tile data. On this map the two differ by
exactly one cell. `09_bg1.py` prints both side by side against the shipped SHA-1:

```
bg0: draws 0 cell(s) anywhere, 0 over reachable walkable ground
bg1: draws 1109 cell(s) anywhere, 488 over reachable walkable ground
plateau.art_cells(doc): 1110   notes['art_cells']: 1110
```

`art\plateau\map_142.json` was not copied again and not edited.

---

## 6. The suite and the base footprint

The full suite ran twice: once mid-work as a diagnostic, and once at the end on the shipped tree.
Both runs were redirected to a file and the exit code was read from the shell, never through a pipe.

**The final run.**

```
Ran 1856 tests in 421.804s
FAILED (failures=1, skipped=10, expected failures=1)
SUITE_EXIT=1
```

The one failure is `test_battle_start.test_form_survives_the_leader_change`:

```
record rom:0x89A9C0 (table rom:0x3DE6F4 word 32, map 9,3 region, fullpower_ssj) runs
appearance(character=4, set=61), entry 20, before leader(2), so appearance_revert undoes it
```

**It is red in `fullpower_ssj`, it predates this work, and it is not mine.** It names a record my two
modules never write, in a table neither of them touches. It is untouched.

The mid-work run showed two failures. The second was
`test_battle_start.test_the_scoped_rule_5_...`, a census that my `header_bit1(0)` moved from 16 to
17. That is explained in section 3a, and the pin is updated. It is green in the final run.

`ending_fight`'s whole base footprint is **six ending table words (12, 13, 22, 23, 24, 25) and three
one-byte portrait ids** (records 14, 16, 20, each one byte at `+3`, each 101 to 100). Word 23 already
belonged to the module as record F; this build only adds its `music(28)` op.

This is measured, not assumed. `08_attribute.py` builds the trial list one module at a time and
watches the 27 words change, so each word is named with the module that wrote it. The rebuilt list
reproduces the ROM file's SHA-1 `d6c15081...` exactly, which ties the attribution to this build:

| word | module |
|---|---|
| 0, 4, 6, 8, 11 | `future_androids` |
| 12, 13, 22, 24, 25 | `ending_fight` |
| 23 | `ending_fight`, then `plateau` repoints it to its own record F |

> An earlier draft of this report called words 0, 4, 6, 8 and 11 part of `ending_fight`. That was
> wrong. A word that differs from vanilla only proves that something wrote it. The `MOVED` marker in
> `05_readback.py` does not name a writer, and the five belong to `future_androids`.

The byte diff covers the WHOLE ending region, `rom:0x3B7B08` (the lowest vanilla ending record) to
`rom:0x3B81AC` (the end of the 27 word table). It names 36 changed bytes: 33 inside the table, which
are the 11 moved words at 3 bytes each, and exactly 3 inside record bodies, which are the three
portrait ids at `rom:0x3B7E77`, `rom:0x3B7EB3` and `rom:0x3B7F13`. **No vanilla record body is
touched anywhere in the region except those three bytes.** CONFIRMED, `08_attribute.txt`.

Every vanilla record the moved words left behind is byte for byte, compared at its own exact length,
not through a fixed window:

| record | length | unchanged |
|---|---|---|
| word 12 `rom:0x3B7E0E` | 0x3C | yes |
| word 13 `rom:0x3B7E4A` | 0x29 | yes |
| word 22 `rom:0x3B7FE0` | 0x36 | yes |
| word 24 `rom:0x3B8116` (`@^The End.`) | 0x24 | yes |
| word 25 `rom:0x3B813A` (`ext 97`) | 0x06 | yes |
| the time skip caption `rom:0x3B860C` | 0x1B | yes |

> The first pass used a flat 0x40 byte window and read three of these as CHANGED. That was the
> window running into the next record, not a real edit. `07_exact.py` compares each record at its
> own length and lists every changed byte with the record it belongs to. A fixed window cannot tell
> the two apart.

---

## 7. What I could not do, and what to watch in the play test

1. **"if he is not already" is not a branch.** No scene op reads the player's current form, so the
   transform cannot test it. It forces the base body first instead, with `ext 73 (3,132)`, which
   makes the power-up legal whatever the player did in round 1. That matters because only the base
   set carries anim 9 (bible B2179). A player who never transformed sees no change; a player who did
   sees his aura drop for a few frames and then power up again. If the owner dislikes that, the
   alternative is to drop the `ext 57 (0,9)` pose, which costs the whole power-up animation.
2. **The caption on black is reasoned, not seen.** Every step is CONFIRMED from the handlers and from
   vanilla's own `ext 45` before "The End.", but no emulator ran. Watch that the box is lit, that
   nothing else is on the screen behind it, and that the HUD is gone while it is up.
3. **`ext 62` to (248,664) is a placement, not a walk.** The spot was not checked against map 6,100's
   collision frame, because the player never moves from it: record A2 puts him back on
   `TRUNKS_START` before the fade in. If he ever appears stuck there, that is the op to look at.
4. **Section 5 and the blast are another agent's.** Nothing here touches the Kamehameha pose, the
   death loop or the beam.
5. **Track 42 is already the 17/18 scene's opening song.** Ending word 0, which `future_androids`
   writes, opens with `music(42)` and ends with `music(38)`. Re-issuing 42 at the caption may
   restart it from the top. That is what he asked for, and it is worth a listen.
6. **Song 42 now covers the whole Cell talk.** Because the cue has to run after the map load, it
   outlasts the caption box and plays under ending words 14 to 22, where the arena's own 38 used to
   play. It stops when record F or record R starts 28. If he wants 38 back for the talk, the fix is
   one more `music(38)` op at the top of record A2, and it needs his word first.
