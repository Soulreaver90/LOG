# Brief: finish the map reader, section 9

Agent: study and build in one. Read `docs\tasks\global.md` first. Absolute paths only. Never `cd`.

## Why this exists

The battle arena shipped three times carrying doors it inherited and nobody could see, because no tool
prints a map's real exits. The owner's words for this class of mistake: "building things that exist in
vanilla". The owner approved arena v7 this morning, so this is the tool that should have existed first.

Read the specification before you write anything: `docs\design\2026-11-06-one-reader-per-section.md`.
Its decision governs this work: one bible, one READER per section, a reader holds no copy of a ROM fact,
a reader resolves live structures rather than hardcoding them.

## The two defects, both already documented and neither fixed

1. **`scripts\permanent\scene\map_view.py` mislabels regions as warps.** Its boxes labelled "warp" are
   REGION records from map entry `+0x10`. They are NOT the layout's own door list at `+0x40`/`+0x44`,
   so a map's real exits never appear. Its own output line prints `region cond ... warp rect ...`. It
   also draws no layout PROPS (`+0x24`/`+0x28`). Its `TOOL_INDEX_NOTE` at line 42 states both. Fix the
   tool, then rewrite that note to describe the tool as it then is.
2. **`scripts\permanent\scene\scene_probe.py --map` stops one pointer short.** It resolves `+0x2C` to
   the layout and never reads `+0x40`/`+0x44`. It already owns the decoder, so this is a few lines.

`scene\warp_graph.py` lines 40-42 already decode the layout door list and know both carriers: the
region list holds 69 of the game's doors and the layout list holds 586 of 655. Read it before you
write a decoder, and reuse rather than copy.

## What `scene_probe.py --map` must print when you are done

Extend the existing `--map`. Do NOT write a third tool.

- the map entry fields by name, not as raw words
- the layout chain
- BOTH door carriers decoded side by side, the region list and the layout list, each labelled for what
  it is, so the two can never be confused again
- the collision frame with its container type and its open counts
- the BG layer records

Resolve the map table through `scene_probe.map_table()`, which already reads this ROM's own literal at
`rom:0xEBD8`. Do not hardcode `0x409368`. `MAP_TABLE` and `MAP_COUNT` at line 32 stay as the base ROM's
documented values and must not become the read path.

## Prove it on the arena, which is the map that caused this

Run the finished reader on map 6,100 in
`builds\mockups\2026-11-05-ending-arena\log2_poc_r41_arena_v7.gba` and on its parent map 6,1 in the base
ROM, and put both outputs in your report. The arena must show 0 doors in BOTH carriers. If either
carrier shows a door, that is a live finding in approved work and you say so plainly.

## Out of scope, do not touch

- Any file under `scripts\permanent\rom\` or `scripts\permanent\art\`. A second agent owns those this
  morning.
- The full test suite. Run only `tests\test_map_view.py`, `tests\test_scene_probe.py` and any module you
  touch. I run the suite myself.

## Rules

- `py -3.14 -P`. Never put a Windows path inside a Python string literal in a heredoc.
- Never write under `data\`. Never overwrite a ROM, save or state.
- A generated page written from a build gets a suffixed filename, so it cannot overwrite a vanilla page.
- Give the bible rows you earn as a `rows.md` beside this brief, as `## Section N` table blocks, tag `MAP9`.
- Report: the two outputs asked for above, what you changed, your test counts with real exit codes, and
  anything you could not prove.

One report message, then stop. Do not add a byte order mark.
