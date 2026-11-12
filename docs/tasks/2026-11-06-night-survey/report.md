# Night survey, 2026-11-06: indexing the engine so we stop rebuilding vanilla

You asked for two things before bed: let the v7 build finish, and work out what we keep getting wrong.
This is the second one. The short answer is in one line, and the rest of the night was spent making that
line impossible to hit again.

## The one line

**We kept asking "how do I build X" when the question was "where does this game already do X".**

Every defect in the arena run traces to that. The fight start, the camera hand-back, the actor swap, the
doorway collision and the map props were all already in the ROM, in plain sight, unindexed.

## What now exists that did not exist last night

Seven generated indexes, all in `docs\research\`, all regenerable from the ROM.

| Page | What it answers | Size |
| --- | --- | --- |
| `scene-vm-ext-ops.md` | What does ext op N do, how many arguments, what does it call | 145 ops |
| `scene-op-usage.md` | Which vanilla records use op N, with their arguments | 5,304 sites |
| `flag-index.md` | Which records set, clear or test story flag N | 174 flags |
| `item-index.md` | Every inventory item, by number, with its name | 50 items |
| `scene-index.md` | What does each scene DO (fight, load, camera, form, flags) | 302 scenes |
| `map-index.md` | Every map's fields, with a field-shape census | 327 maps |
| `warp-graph.md` | Every door in the game, both carriers | 655 doors |

Three are filterable from the command line. The one that matters most:

```
py -3.14 -P scripts\permanent\scene\scene_index.py --does fight
```

That prints **every fight start in the game**. Had it existed yesterday morning, the arena would have been
one build.

## The six findings that would have saved builds

**1. A fight start does not load a map, and does not fade.** Of the 35 records that raise a boss bar,
exactly **1** also loads a map. Of the 17 scenes that convert an NPC into an enemy, only **2** load a map
and only **1** opens a fade at all. We built our helper from that single exception because it matched the
scene we had already designed.

**2. Nine doors in ten were invisible to us.** A map carries doors in two places. `scene_probe` reads the
region list, which holds **69** of the game's **655** doors. The other **586** are in the layout list,
which nothing in this project could decode. The Capsule Corp front door is one of them: rect
(224,88)-(273,105) to map 6,2. In vanilla it fires before you can stand in the recess. The arena deleted
it and left the floor, which is the hole you walked through.

**3. Props are the common case.** 194 of 327 maps carry layout props. Any map copied as a template brings
them along, which is why the save point and the map post survived emptying the item list.

**4. Four entries in our own op table are wrong.** Checking all 145 handlers against `scene_lib.EXT_OPS`:
50 of 54 agree. `ext 23 visited` pops two values, not one. `ext 131`, `132` and `133` pop nothing at all,
they push a byte. They are getters, and we had them as setters taking an argument.

**5. The map music field has two forms.** `+0x24` holds a literal song id in 230 maps and a **script** in
62, which tests story flags and pushes a different song per branch. Map 6,1 is a scripted one.

**6. The VM has a whole op family we never knew about.** ext 0-16 plus 75, 126, 129 and 131-133 are
getters that push a value and take no argument, and ten more ops are predicates that replace the top of
stack with a result so `jz` can read it. That is 30 ops of the 145, and our table named almost none of
them correctly.

## The bug that was hiding half the game

`scene_lib.table_end` decides how long a scene table is by stopping at the **first END entry**. An END
entry is not a terminator: it is an ordinary table word carrying a resume index, and tables interleave
them freely.

Measured both ways over the 303 map-owned tables: **229 of them were truncated, losing 1,398 words.**

The Dende table `rom:0x3DD380` is the proof. The old rule gives it length 3. Its real length is 11, and the one record in the game that sets `flag:191` sits at index **6**, which is why my first flag
index could not find a flag the bible already documents.

Re-walking correctly raised the census from 4,725 op sites to **5,304**, and from 94 to **102** distinct
ops, **while the decode failure count stayed at exactly 1**. Walking 1,398 more words with no new failures was the only
check I had that night, and it was not enough: see the 2026-11-07 report for what the walk really does
at a table's tail.

It also made the headline finding stronger, not weaker: **34 of 35** bar records load no map, where the
truncated walk said 26 of 27. And there are **27** vanilla boss fights, not 19.

Everything any of us has counted through `table_end` before today is a floor, including the battle-start
study that produced the "27 of 27" figure. `scene_probe --table` still truncates its listings this way and
needs the same fix.

## The mistake I nearly made tonight, and the rule it earned

My first handler profiler disagreed with **22 of 54** ops we already knew. Every one of those was my bug:
`r0` stops being the VM stack at the first `BL`, so a handler's stores into a freshly allocated struct
look exactly like stack pops. Validating against the known ops turned 22 false findings into the 4 real
ones above.

> **A measurement that has not reproduced a known answer is not a measurement.**

Two more rules this run earned:

> **Count the population before copying an example.** "Vanilla does it this way" needs a number. 34 of 35
> is evidence; one matching record is not.

> **Search the bible for what you are about to BUILD, not only for what you are about to read.**

## Also done

- The seven `builds\mockups` arena folders are merged into one, matching every other mockup. Your save
  states are all in `builds\mockups\2026-11-05-ending-arena\` now, v1 through v6.
- `scene_probe.map_entry` resolves this ROM's own map table instead of the base ROM's constants. That
  silently broke `map_view --rom` too, so neither tool could open map 6,100 at all.
- Backlog item 14 is struck. The blue at y 200-223 is floor reflection art, not a door.
- `docs\retrospective-2026-11-06-arena.md` has the full failure list with evidence.
- dragonbyte-z pulled: README, CHANGELOG and INSTALL only, no new research or tools.

## Closed before you woke

The op fixes and the walker are done. The tool audit is narrowed, not finished. The detail is in
`docs\tasks\2026-11-07-ops-fixes\report.md`.

- The 4 wrong `EXT_OPS` entries are fixed, and `tests\test_ext_ops.py` now pins all 53 named ops
  against the handlers, so that table cannot drift again.
- `scene_lib.table_length()` is the length rule. `table_end()` is marked a floor, and nothing in
  `scripts\permanent` calls it any more outside the tests that pin the difference.
- The 33 rows are merged into the bible, with 6 more from the fixes.
- The full suite runs 1,395 tests with one failure, the known RED `test_form_survives_the_leader_change`.

Two numbers in this page were corrected after the walk was fixed: the fight-start shape is **34 of 35**,
and the pages reach **302** tables plus one unreadable pointer, not 303.

## Still open

- An audit of the other permanent tools for base-ROM constants a build moves. The map table and the
  table walker are both fixed; nothing else has been checked.
- `fullpower_ssj` runs `appearance()` before `leader()` at `rom:0x89A9C0`, so the form is undone.
  That is the one red test, and the reorder is your call.
- The seven items the v7 agent left for you, in `docs\tasks\2026-11-06-arena-v7\report.md`.
