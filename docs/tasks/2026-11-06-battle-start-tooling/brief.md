# Brief: the standard battle start, as a helper and a checker

Build task. Run the full suite once at the end. **Do not change any patch module and do not fix the arena.**
Follow `docs\tasks\global.md`. The design is decided; do not redesign it.

## Why

The owner's instruction: "if anything can be built into our tooling so all future battles dont need this
trouble again, just a standard battle start." The arena fight shipped four times with a hard camera jump while
the answer sat in the bible. He wants a mechanism, not a promise.

**The checker must FAIL on the arena as it stands.** That failure is the deliverable, because it proves the
check works. A later task fixes the arena. If your tests pass against today's build, you have built the wrong
thing.

## The source of truth

Read `docs\tasks\2026-11-06-vanilla-battle-starts\report.md` first. It holds the census, the vanilla template,
the invariant and the five obligations. Its section 3 is your specification. The bible rows are merged under
tag `VBS`.

Two facts from it that your code depends on, both CONFIRMED:

- The vanilla template, `rom:0x3E9384`, map 14,3, the Cell Games start, is the only vanilla record that both
  shows a bar and loads a map:
  `fade_out(120) ; load_map_at(14,3,1,368,440) ; ext84(5) ; leader(0) ; face(30,2) ; face(0,3) ;
  camera(328,344,10) ; spawn(60,552,96) ; fade_in(120) ; wait(60) ; camera_follow(0) ; header_bit1(1) ;
  bar_set(30,60,100) ; set_flag(192)`
- Of 302 scene tables, 48 set a fixed camera. Counting only what runs after the LAST `ext 31`, the number that
  give control back and reclaim the camera by nothing is **zero**. The rule has no exception.

## What to build

### 1. `battle_start()` in `scripts\permanent\scene\scene_lib.py`

Beside the existing `camera`, `spawn`, `face`, `pose`, `move_to` and `leader` emitters, because `scene_lib`
already owns the op vocabulary. Signature from the report:

```python
def battle_start(*, leader_who, zone, area, var, player_xy, facing,
                 frame_xy, frame_speed=10, hold=60, cover=("fade", 120),
                 bar=None, bar_range=None, spawn_list=None,
                 appearance=None, follow=0) -> bytes:
```

It emits the five obligations in the template's order: cover, load, form, frame, reveal, hold, HUD, bar.
`appearance=(who, set)` emits `ext 73` before the `ext 70` leader change, which is the order the report proves
survives `appearance_revert`. Do not emit `camera_follow` when `follow` is None.

### 2. Two fields on `scripts\permanent\scene\scene_harness.py`

It already runs a record or table op by op. Add:

- `camera_owner`: which object owns `0x03000FF4` at the end of the run. `ext 31` sets the fixed camera,
  `ext 33` the follow camera, `ext 119` the other object, and a map load installs the follow camera on a
  walking map (`map_load @0x0800C584` replaces the camera and never eases, per the report).
- `screen_covered`: whether a fade or flash is open at each op.

Treat `ext 34` as "covered by no op we can name", not as proved uncovered. The report says its effect was
never read.

### 3. `scripts\permanent\tests\test_battle_start.py`

Five tests, one per assertion, each running `scene_harness` over the live build. Follow the existing pattern
in `tests\test_golden.py` for obtaining a ROM; do not invent a new fixture.

1. `test_map_load_is_covered`: every record that loads a map and then shows a bar has a fade or flash open
   across the load.
2. `test_camera_is_handed_back`: if any op before the control record set a fixed camera, the table reclaims it
   after the LAST `ext 31`, by `ext 33`, `ext 37` or a map load.
3. `test_form_survives_the_leader_change`: a record running `ext 73` and `ext 70` either names the same
   character in both, or runs `ext 73` after `ext 70`.
4. `test_player_ops_address_the_player`: a record our modules own names no NPC set that the design moved onto
   set 0.
5. `test_control_record_shows_the_hud`: a record that shows a bar also runs `header_bit1(1)`.

**Order is NOT part of the shape.** The three control ops appear in three orders across `rom:0x3D40B2`,
`rom:0x3EA3EC` and `rom:0x3EB6E8`. A test that asserts their order is a defect.

### 4. The deviation convention

An optional `BATTLE_START_EXCEPTIONS = {record_offset: "one line of why"}` in a patch module. The test reads
it, asserts the record is actually in that module, and **fails on a stale entry**. Do not add the dict to any
module yet; just support it and test the support with a fixture.

## What the check cannot know, and must not assert

Story-flag gating on a form (Super Saiyan 2 is flag 195), whether `frame_xy` survives the map view clamp
(bible rows 1168 and 1507), the boss's real set and bar range, which `map_load` branch a map takes (layout
`+0x3C`), and anything about timing, animation or combat. It reads WALK order, which is not execution order
where a `jz` or a next index branches: say so in the header and do not pretend otherwise.

## Expected result

Assertion 1 should fail on arena record F, which loads a map and shows a bar with no cover. Assertion 2 should
fail on table `rom:0x3B8140`, where `camera(384,368,2)` at `rom:0x3B7B8F` is never reclaimed before record F
gives control. **Report both failures as successes of the checker.** Do not make them pass.

If a test fails on a VANILLA record you believe is legitimate, that is a finding about the rule, not a licence
to weaken the test. Report it and leave the test failing.

## Rules

- `docs\tool-index.md` before any new script. A new module is the wrong answer here; the report explains why.
- Python header block on every file, no em or en dashes, no byte order mark.
- Label every reverse-engineering claim CONFIRMED, LIKELY or SPECULATIVE.
- Run the suite once at the end: `py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent`. Never pipe it into `tail`, `head` or `Select-Object`.
- Report the pass and fail counts, and name every failing test with the reason.
- Write `docs\tasks\2026-11-06-battle-start-tooling\report.md` and, if you learn a ROM fact, `rows.md` with
  tag `BST`.

One report message, then stop. Do not add a byte order mark.
