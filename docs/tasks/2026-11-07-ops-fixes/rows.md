# Bible rows, tag OPS2

Merge with:
`py -3.14 -I scripts\one-time\2026-10-16-first-probes\merge_bible_rows.py docs\tasks\2026-11-07-ops-fixes\rows.md OPS2 docs\tasks\2026-11-07-ops-fixes\report.md`

## Section 8

| Fact | Tags | Confidence | Source |
|---|---|---|---|
| **A scene table's length rule, settled.** `scene_lib.table_length()` walks while a word is an END entry or a record pointer, and stops at the first word that is neither. A record pointer is a word inside the vanilla script region `0x3B0000`-`0x420000` **or** inside the expansion area `0x800000`-`0xF00000`, because a patch moves records there. A walker that knows only the script region reads a BUILD short with no error: on `log2_poc_r41_arena_v7`, table `rom:0x3DE6F4` reads 32 words that way against its real 36, because `fullpower_ssj` moved word 32 to `rom:0x89A9C0`. `table_end()` is kept as a floor and must not be used for a census | #script #tool | C (measured on the base ROM and on the v7 build; `test_ext_ops.py`) | OPS2 |
| **Our own module tables were the worst victims of the first-END rule.** A module that copies a vanilla table allocates its copy in expansion, and the copy's first END entry can sit at a very low index. `celljr_fight`'s copy of table `rom:0x3EA400`, allocated at `rom:0x93AE74`, has its first END at index 2 of 33 words, so the old walk checked 2 of its 33 and never read 31 records of our own code. The battle-start census over the live build rose from 22 vanilla bar records to **31** when it switched to `table_length()` | #script #tool | C (`test_battle_start.py` census over the live build) | OPS2 |
| **The widened census made the fight-start claim stronger.** Over the 31 vanilla bar records the full walk reaches, not one opens a scene: none loads a map and none opens a fade. The single record in the game that does is the Cell Games template `rom:0x3E9384`, which one of our modules now owns a copy of. The earlier figure of 22 was a truncated population, not a different answer | #script #combat | C (census assertion, live build) | OPS2 |
| **ext 131, 132 and 133 push the level-up stat gains.** Each handler reads one byte of the pool pointer `0x03001FC0` and raises the VM stack depth: `@0x08009466` pushes `[0x03001FC1]`, `@0x08009478` pushes `[0x03001FC2]`, `@0x0800948A` pushes `[0x03001FC3]`. Bible row 1904 already names `0x03001FC1`-`0x03001FC3` as the level-up stat gains, so the names `gain_str`, `gain_pow` and `gain_end` were right and only the ARITY was wrong: they take no argument and they are getters, not setters | #script #save | C (all three handlers read in full; the pool literal at `rom:0x95A8` resolves to `0x03001FC0` for all three) | OPS2 |

## Section 11

| Fact | Tags | Confidence | Source |
|---|---|---|---|
| **Evidence that the full table walk does not over-run.** Over the 302 readable map-owned tables of the base ROM, not one table's span `[start, start + 4*length)` contains another table's start, under the full rule or the first-END rule. This is evidence against over-run and not proof of none: it sees only the tables the map walk reaches, so a table named only by Thumb code could still sit inside a span. Pinned by `test_ext_ops.OverRunTests` | #tool #script | C (measured; the check is in the suite) | OPS2 |
| **Map 6,3 names a scene table through a null pointer.** The map walk reaches 302 readable tables plus this one unreadable pointer, which is where the "303 tables" figure came from. `op_usage.scene_tables()` now leaves it out and reports it, so a page says 302 reached and names the bad pointer, instead of counting a table nothing can read | #tool #map | C (`docs\research\scene-op-usage.md`, generated) | OPS2 |
