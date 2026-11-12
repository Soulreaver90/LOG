# Research index

Generated reference pages. **Every one of these is regenerated from the ROM by a tool**, so fix the tool
and re-run, never hand-edit a page here.

Before writing a scene op, read `docs\playbooks\scene-recipes.md`. It turns these pages into recipes.

## The generated pages

| Page | Answers | Tool |
| --- | --- | --- |
| `scene-vm-ext-ops.md` | What does ext op N do: arguments, getter or predicate, what it calls | `scripts\permanent\disasm\ext_ops.py` |
| `scene-op-usage.md` | Which vanilla records use op N, with their arguments | `scripts\permanent\scene\op_usage.py` |
| `scene-index.md` | What each scene DOES: fight, load, camera, form, flags | `scripts\permanent\scene\scene_index.py` |
| `flag-index.md` | Which records set, clear or test story flag N | `op_usage.py --flags` |
| `map-index.md` | Every map's entry fields, plus a field-shape census | `scripts\permanent\scene\map_index.py` |
| `warp-graph.md` | Every door in the game, from both carriers | `scripts\permanent\scene\warp_graph.py` |
| `item-index.md` | All 50 items by number, with names and handlers | `scripts\permanent\rom\item_index.py` |
| `enemy-type-census.txt` | Every enemy type with stats, spawns and scouter names | `scripts\one-time\2026-10-29-design-ideas\type_census.py` |

## The filters worth remembering

```
scene_index.py --does fight      every fight start in the game
scene_index.py --does form       every scene that transforms a character
op_usage.py --op 104             every site of one op, with arguments
op_usage.py --flag 191           every record that touches one story flag
warp_graph.py --from 6,1         where one map's doors lead
item_index.py --find card        find an item by name
```

## Reading these honestly

**Every count on these pages is a FLOOR, never a total.** The walk reaches tables a MAP owns. A table
named only by Thumb code, by another table's next index, or by a script region's script is not reached.
The ending table `rom:0x3B8140` is one of those, which is why ops the ending uses can show zero sites.

Say "the walk found N", never "there are N".

**A site's address is the ext op, not the push before it.** Many bible rows cite the push, which sits 2
bytes earlier for a one byte push. Row 814's `0x083D045B` is this index's `rom:0x3D045D`. Same site.

**A `--rom <build>` run writes its own file**, suffixed with the ROM's name, so a build's numbers can
never be mistaken for the game's.

## Three traps these tools were built around

1. A tool that hardcodes the base ROM's map table reads the **dead** table in a build, silently, and
   cannot see an appended map at all. Resolve it from the literal at `rom:0xEBD8` instead.
2. `scene_lib.table_end` stops at the **first END entry**, but END entries are interleaved, not terminal.
   It truncated 229 of 303 scene tables and lost 1,398 words. **Fixed 2026-11-07:** call
   `scene_lib.table_length()`. `table_end` stays as a floor and nothing in `scripts\permanent` calls it
   any more, outside the tests that pin the difference.
3. A record pointer is not only a word in the script region. A build moves records into the expansion
   area `0x800000`-`0xF00000`, so a walker that checks only `0x3B0000`-`0x420000` reads a BUILD short
   with no error. Measured on the v7 arena ROM: table `rom:0x3DE6F4` read 32 words against its real 36.
