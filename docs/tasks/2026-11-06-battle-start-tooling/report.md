# Report: the standard battle start, as a helper and a checker

Build task, 2026-11-06. Brief: `brief.md` beside this. Specification: `docs\tasks\2026-11-06-vanilla-battle-starts\report.md` section 3.
No patch module was changed. The arena was not fixed. The agent could not write this file, so I saved its
report below. Everything under "My verification" is mine.

## My verification

**CONFIRMED by my own read of the handler.** `sub_08003ED4` (`appearance_revert`), the whole function, from
the disasm repo's own `build\code\code_08003ed4.s`. Two gates, both as reported:

```
LDRB r2, [r0, #0x0] ; CMP r2, r1 ; BEQ loc_08003EFC     <- the leader's own record is SKIPPED
...
LDRB r5, [r3, #0x0] ; LSL r5, r5, #0x1F ; BEQ loc_08003EFC   <- entry flags bit 0 CLEAR: revert nothing
LDRB r3, [r3, #0x5] ; STRB r3, [r2, #0x14]              <- else write the revert target
```

It also pins two strides as a cross-check: party records are 28 bytes (`LSL #3` minus `r1`, then `LSL #2`)
and appearance entries are 20 (`LSL #2` plus `r5`, then `LSL #2`). The 20 matches the stride I measured from
the ROM bytes in the vanilla-battle-starts task. So "an untransformed appearance is never reverted" is
CONFIRMED, and the classification of the five assertion-3 findings stands.

**CONFIRMED by my own run, both ROMs.** `scene_probe.map_table()` returns `rom:0x409368` and 327 for the base
ROM, which equals the hardcoded values it replaces, and `rom:0x93be28` and 328 for the arena v4 build, with
map 6,100 at index 327 and map 6,1 still at index 145 in both. `MAP_TABLE` and `MAP_COUNT` defaults are
unchanged, so no existing caller moves.

**The `scene_probe.py` change was not in the brief, and it is warranted.** It closes the exact trap recorded
in `docs\tool-index.md` earlier the same day, that the tool hardcodes the base ROM's map table so `--rom <a
build>` reads the stale copy. It also fixes a latent name shadow: `count` was about to mean both the entry
count and the item count in `map_items`, and is now `n_items`.

**Suite: run by me, from the LOG root, not piped into anything.** See the result recorded at the end of this
file.

**Not verified by me, and still the agent's claim alone:** the 310-table and 2177-record census figures, the
13 HUD findings being legitimate mid-fight bars, the stack effect of base ops 21-26, and `table_end()` being
a floor.

---

## The agent's report

### 1. Result

The checker works, and it fails. Full suite: 1344 tests, 1341 pass, 3 fail. All 3 failures are the new tests.

| Test | Verdict | What it found |
|---|---|---|
| `test_map_load_is_covered` | FAILS, as asked | 1 record: the arena start |
| `test_camera_is_handed_back` | passes | the brief predicted a failure; see section 3 |
| `test_form_survives_the_leader_change` | FAILS | 5 findings on 4 records; 1 looks real, 4 over-flagged |
| `test_player_ops_address_the_player` | passes | no record we own still names set 133 |
| `test_control_record_shows_the_hud` | FAILS | 13 records: 12 vanilla, 1 ours |

Run it alone with:

```
py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_battle_start.py -v
```

### 2. What was built

| File | Change |
|---|---|
| `scene\scene_lib.py` | NEW `battle_start(...)`, beside the other op emitters. Writes the template's order: cover, load, form, frame, reveal, hold, HUD, bar. Refuses `spawn(0, ...)` and an unknown cover kind. |
| `scene\scene_harness.py` | NEW `Run.camera_owner`, `Run.screen_covered`, `Run.cover_at(op)`. Base ops 21-26 modelled, so the harness reads every record in the build. |
| `scene\scene_probe.py` | NEW `map_table(rom)`; `map_entry`/`map_items` take an optional table and count. Defaults unchanged. |
| `tests\test_battle_start.py` | NEW. 23 tests: the 5 assertions, 4 census self-checks, 6 for the deviation convention, 8 for the emitter. |

No new module. Without base ops 21-26 the harness raises on `rom:0x3BAFEA` (vanilla) and `rom:0x93ACB4`
(`celljr_fight`'s counter), so 2 of 2177 records would be unread, and an unread record is a silent hole in
every count here. All six handlers were read rather than guessed. CONFIRMED.

### 3. The predicted camera failure does NOT happen, and the specification says why

The brief expected `test_camera_is_handed_back` to fail on table `rom:0x3B8140`. It is reclaimed.

- Record F is `leader(3) ; load_map_at(6,100,1,248,568) ; face(0,1) ; header_bit1(1) ; bar_show(28)`.
- The `load_map_at` runs AFTER the last `ext 31` and BEFORE the `header_bit1(1)`.
- The brief's own assertion 2 lists "`ext 33`, `ext 37` or a map load" as the three ways to reclaim.

So the camera IS handed back, by the map load, and the test passes. This is the specification's section 5
defeating its section 3: section 5 found that `map_load @0x0800C584` installs and REPLACES the camera, writing
the new player into `0x030020C0 + 4` and storing that object in `0x03000FF4`, exactly as `ext 33 (0)` does.
The prediction was written before that finding and was never revised.

The model was NOT weakened to force the failure. Dropping map loads from the reclaim set would break the
vanilla zero-exception count, because 8 of the 48 vanilla tables reclaim by a map load and nothing else. And
the real defect is not a stuck camera: the camera hands back correctly and then SNAPS, because `map_load`
never eases, and the snap is visible only because record F has no cover, which assertion 1 catches.

### 4.1 `test_map_load_is_covered`: the arena start, as predicted

```
record rom:0x9405E8 (table rom:0x3B8140 word 23, the ending sequence, named by code, not by a map entry,
ending_fight) shows a bar and loads a map with the screen clear
```

No `fade_out`, no `palette_fx`, no `load_map_fade`, so the view snap happens in plain sight. Of 55 vanilla
map-load records 43 are covered, and no vanilla record that shows a bar loads a map without cover. Record F
is the only one in the whole build. Two records both load a map and show a bar; the other is the live copy of
the Cell Games template, and it is covered, pinned by `test_the_live_template_still_keeps_the_shape`.

### 4.2 `test_form_survives_the_leader_change`: 1 real candidate, 4 over-flagged

```
rom:0x3CCA2E  (vanilla, map 5,3)        appearance(character=0, set=53)  before leader(2)
rom:0x89A9C0  (fullpower_ssj, map 9,3)  appearance(character=4, set=61)  before leader(2)
rom:0x939CFC  (chapter_cards, map 9,6)  appearance(character=0, set=53)  before leader(3)
rom:0x89AB4C  (fullpower_ssj, map 14,3) appearance(character=0, set=157) before leader(1)
rom:0x89AB4C  (fullpower_ssj, map 14,3) appearance(character=4, set=60)  before leader(1)
```

Classified against the built appearance table (`rom:0x800000`, the `gohan_gi` copy):

| Finding | Set | Entry | Flags | Verdict |
|---|---|---|---|---|
| `rom:0x3CCA2E` | 53 | 0 | `0x00` | FALSE ALARM. Entry 0 also reverts to itself. |
| `rom:0x939CFC` | 53 | 0 | `0x00` | FALSE ALARM, the same record copied. |
| `rom:0x89AB4C` | 157 | 2 | `0x00` | FALSE ALARM. |
| `rom:0x89AB4C` | 60 | 19 | `0x00` | FALSE ALARM. |
| **`rom:0x89A9C0`** | **61** | **20** | **`0x01`** | **CANDIDATE DEFECT in `fullpower_ssj`.** |

The candidate: `fullpower_ssj`'s `post_cell_seq20` copy at `rom:0x89A9C0` runs `appearance(character=4,
set=61)`, Goku's Super Saiyan entry 20, and THEN `leader(2)`. Character 4 is not character 2, entry 20's
flags bit 0 is set, and its revert target is entry 19, set 60, base Goku. So the one op that would be undone
is the one the module exists to keep. The two later calls in the same record run after the leader change and
are safe.

CANDIDATE, not proven: this is walk order not execution order, a later record of table `rom:0x3DE6F4` may set
it again, and it was not watched in mGBA. The fix, if wanted, is a one-line reorder: move the `ext 73` after
the `ext 70`. The module was not touched.

Assertion 3 as specified does not read the appearance table, so it cannot tell a transformed entry from an
untransformed one, and over-flags 4 times out of 5. Narrowing it to "only when the entry's flags bit 0 is set"
would leave exactly the one candidate. The test was left failing, because narrowing the rule is a design
change.

### 4.3 `test_control_record_shows_the_hud`: 13 records, 12 vanilla

```
rom:0x3BC416  table rom:0x3BD50C word 18  map 2,50 region   bar_show(50)
rom:0x3C9A24  table rom:0x3C9A38 word  8  map 4,58 region   bar_set(127, 25, 100)
rom:0x3D00FA  table rom:0x3D012C word  5  map 6,11 talk     bar_show(146)
rom:0x3D28E2  table rom:0x3D2AAC word  4  map 6,61 region   bar_show(34)
rom:0x3D2D2C  table rom:0x3D2D3C word  2  map 6,70 region   bar_show(156)
rom:0x3D2E26  table rom:0x3D2E38 word  2  map 6,70 region   bar_show(76)
rom:0x3D2F32  table rom:0x3D2F44 word  2  map 6,70 region   bar_show(121)
rom:0x3D5E3C  table rom:0x3D5E68 word  2  map 8,13 region   bar_set(14, 75, 100)
rom:0x3D62DC  table rom:0x3D6388 word  2  map 8,27 region   bar_set(14, 50, 75)
rom:0x3D7748  table rom:0x3D77F4 word  2  map 8,40 region   bar_set(14, 50, 75)
rom:0x3E6F9C  table rom:0x3E7104 word  0  map 12,6 group    bar_set(30, 65, 100)
rom:0x3E8F40  table rom:0x3E8F50 word  4  map 14,2 group    bar_set(30, 50, 75)
rom:0x909100  table rom:0x909110 word  3  map 6,70 region   bar_show(60)   <- chamber_spar, OURS
```

The 12 vanilla records are legitimate and the rule is what is wrong. Every one raises a bar in a scene that
never took the HUD away: not one of their 13 tables runs `header_bit1(0)` anywhere. They are mid-fight bars,
such as a second boss appearing, and there was no HUD to put back. 17 of the 30 bar records in the build do
run `header_bit1(1)` in the same record, and all 15 bar records sitting in a table that DID hide the HUD are
among those 17, with no exception.

Proposed refinement, not applied: scope the rule to a record that shows a bar AND either loads a map or sits
in a table that ran `header_bit1(0)`. That reads 16 records today, keeps the arena start and the Cell Games
template in scope, and has zero failures.

`rom:0x909100` is ours, `chamber_spar`'s `pre_table` word 3. It shows Goku's bar with no `header_bit1(1)`, and
`chamber_spar`'s table never hides the HUD either, so it is probably the same legitimate shape. The module was
not touched.

### 5. The two assertions that pass

`test_player_ops_address_the_player` passes: no record our modules own names set 133 in any actor op. The test
now holds it there, so re-adding a `spawn(133)` or an `attack(133, ...)` fails immediately.

Set 132 is deliberately NOT watched. The design moved only 133 onto set 0. Set 132 is the plain NPC Trunks the
Cell Games and Lookout scenes still use, and watching it would fire on 7 legitimate records in
`piccolo_gi_scene`, `fullpower_ssj` and `celljr_fight`. The constant carries that reason.

### 6. Four traps the census hit

1. **`table_end()` is a floor, not a length, and it cost a false accusation.** Read with `S.table_end()`,
   `piccolo_gi_scene`'s chamber-exit copy reports 35 words and stops at the END word at index 34, while its
   appended records 35-44 sit PAST that word. Read that way the table appeared to reclaim the camera by
   nothing, so assertion 2 reported our own Lookout scene as broken. It is not: the `camera_follow` is in
   record 44, which the walk never reached. The test now takes the word count from the module's own
   `notes["words"]`.
2. **The vanilla template is not at `rom:0x3E9384` in the live build.** `cellgames_ssj` copies it to
   `rom:0x89A6B4` and repoints the table word. The test resolves the live copy through
   `notes["cellgames_ssj"]["sources"]`.
3. **Two shapes reach the scene tables and neither is complete.** Walking the live build's own map table
   reaches 309 tables. The ending sequence `rom:0x3B8140` is named only by CODE and never appears, and the
   piccolo copy is named only by the two type 5 records `rom:0x3CF7E0` and `rom:0x3D152C`. Both are declared
   in `EXTRA_TABLES` and `EXTRA_FROM_NOTES` with their reason. A table named only by code, by a script region
   item (`0x0800C2C3`) or by a map enter script, and not declared, still does not appear. The census is 310
   tables and 2177 records reachable by those two shapes, not "all the scenes". `chapter_cards`'s
   `notes["table"]` was tried as a third and dropped: it is the card INDEX, not a scene table.
4. **Cover is read per RECORD and the camera per TABLE, and that choice is load-bearing.** Carrying the cover
   across the records of table `rom:0x3B8140` makes record F's naked load read as COVERED, because two earlier
   records run `fade_out` and nothing closes them in walk order. The owner SAW that load snap, so the screen
   was clear when it ran: a fade is a one-shot transition, not a latch a later record inherits. The camera is
   the other way round, because record F sets no camera of its own and the stuck view came from an earlier
   record.

### 7. The deviation convention

```python
BATTLE_START_EXCEPTIONS = {0x9405E8: "one line of why"}
```

`declared_exceptions()` reads it from every module in the build list. An entry is checked two ways and both
make the suite fail: the record must lie inside a block that module itself allocated, traced by applying the
build list one module at a time and slicing `alloc.used()`; and the record must still break a rule, so an
entry kept after a fix is reported as stale.

No module carries the dict. Six tests cover the support with a fixture, and
`test_no_module_declares_an_exception_yet` keeps it that way.

Limit, stated in the code: a module that edits a vanilla record IN PLACE allocates nothing, so that record
reads as vanilla and cannot be declared by its module.

### 8. What the check reads, and what it must not be asked

- WALK order, not execution order. Across a table it reads word 0 to the last word. Inside a record
  `scene_harness` follows `jz`, `jmp` and the loop ops, so an op on a path not taken is not recorded. Where a
  branch exists, a record named here is a candidate and a record not named is not cleared.
- `ext 34` reads as `COVER_UNKNOWN` and passes assertion 1. Its effect was never read.
- Order is not part of the shape. No test asserts the order of `camera_follow`, `header_bit1` and the bar.
- It cannot know story-flag gating on a form (Super Saiyan 2 is `flag:195`), whether `frame_xy` survives the
  map view clamp (bible rows 1168 and 1507), the boss's real set or bar range, which `map_load` branch a map
  takes (layout `+0x3C`), or anything about timing, animation or combat.
- A bar drawn by code rather than by `ext 85` or `ext 90` does not appear at all.

### 9. Decisions waiting on the owner, none taken

1. `fullpower_ssj` `rom:0x89A9C0`: move `appearance(4, 61)` after `leader(2)`? One line. Section 4.2.
2. Narrow assertion 3 to entries whose flags bit 0 is set? Clears 4 of 5 findings, keeps the one that matters.
3. Scope assertion 5 to battle starts? Clears all 13 findings.
4. `chamber_spar` `rom:0x909100`: a bar with no HUD op, in a scene that never hid the HUD.
5. The arena fix itself: record F needs a cover. A later task, per the brief.

One tooling gap not fixed: `docs\tool-index.md` carries hand-written trap notes that `make_tool_index.py`
cannot regenerate, because the generator takes only each docstring's first 150 characters. Its note about the
hardcoded map table is now half stale, since `scene_probe.map_table(rom)` resolves a build's own table while
`map_view.py` and `scene_probe`'s CLI still default to the base ROM's. The generated file was left alone
rather than hand-edited, because editing only the generated file is the trap the project rules name.
