# Set table readers: build report

Agent build, 2026-11-07. The agent could not write this file itself, so its report is saved below.
Everything under "My verification" is mine. Treat the agent's text as unverified except where I say so.

## Deliverable

| Item | Value |
|---|---|
| Brief | `docs\tasks\2026-11-07-set-table-reader\brief.md` |
| New resolver | `rom\webfoot_decompress.set_table(rom)` and `set_offset(rom, set_id)` |
| New test module | `scripts\permanent\tests\test_rom_constants.py`, 12 tests |
| Bible rows | `rows.md`, 9 rows, tag `RDR` |

## The agent's report

**Deliberate exceptions it did not change**, because these read the base constant on purpose:
`patches\gohan_gi.py` lines 97, 111 and 130 (it checks, lays out from, and copies the vanilla table),
`disasm\symbols.py` line 129 (`0x083B4E90` is a base ROM symbol by design), `rom\rom_sheet.py` line 15
(a docstring mention; its resolver already uses the literal), and `disasm\ext_ops.py` (out of scope, and
it has no hit at all).

It corrected my brief: I wrote "every PATCH resolves through `0x959C`", and that is not literally true,
because `gohan_gi` must read the vanilla table to copy it.

| File | Change |
|---|---|
| `rom\webfoot_decompress.py` | added `set_table(rom)`, `set_offset(rom, set_id)`, `SET_TABLE_LITERAL = 0x959C`, `FIRST_ID = 7`; `SET_TABLE` kept, comment now says it is the BASE value; `cmd_set` points at `set_offset` |
| `rom\log2_sprites.py` | import and `_main` export point at `set_offset` |
| `art\gi_aura.py` | `_layout_rows` points at `set_offset` |
| `tests\test_rom_constants.py` | NEW, 12 tests |

It added `set_offset(rom, id)` as well as `set_table(rom)`, because all three call sites held the same
`rom_ptr(rom, T + 4 * (id - 7))` expression and `set_table()` alone would have left it copied three times.

**Measured on `log2_poc_r41_arena_v7.gba`:**

| Command | Before | After |
|---|---|---|
| `webfoot_decompress.py set <v7> 58` | `set 0x2AB508`, 205 record lines, exit 0 | `set 0x908D54`, 177 record lines, exit 0 |
| `webfoot_decompress.py set <v7> 157` | `TypeError`, exit 1 | `set 0x81FE14`, 21 anims, 289 record lines, exit 0 |

So set 157 did not merely read the wrong art. It CRASHED, because `rom_ptr` returns `None` for the word
past the end of the vanilla table.

`gi_aura._layout_rows` reads `BASE_ROM`, so its change has no behaviour effect today. It is a consistency
fix, not an arena v7 fix.

**The two constant groups.** `item_index.py`'s `TABLE = 0x6ADE24` (5 aligned literals) and
`STRING_TABLE = 0x0E2840` (20) hold in a dev master build and in arena v7. For `log2_save.py` the split
matters: its CODE reads only `QUEST_TABLE` from the ROM (line 336, the journal), and `0x081D9548`,
`0x086F6D8C`, `0x086F8E40` and `0x086ADE24` appear in COMMENTS only, so no reader can go stale on them
today. All five pinned anyway. Nothing moved, so it guessed no fix.

**Tests, real exit codes, no pipe:** `test_rom_constants` 12 OK, `test_sprites` 10, `test_aura` 13,
`test_tools` 10, `test_golden` 14, `test_gi_post` 13, `test_hand_frames` 15, `test_one_body` 13,
`test_make_tool_index` 6. It did not run the full suite. `test_golden` green means both masters still
match their pinned SHA-1s, so its edits changed no ROM byte.

**The guard is proven red, not assumed.** `scripts\one-time\2026-11-07-set-table-reader\prove_red.py`
patches each reader's `set_offset` back to the old expression and runs the two call-site tests: 2 of 2
fail. The test module builds the dev master in memory rather than reading a file from `builds\`, because
a file on disk never changes and would pin nothing.

**Search completeness, in its own words:** five shapes used, `SET_TABLE`, `0x3B4E90`, `959C`,
case-insensitive `3b4e90` (catches the GBA form) and `sym_rom("set_table")`. A reader that computed the
address another way, for example from a RAM dump or by arithmetic, would not appear in any of them.

**Hedges and deferrals it recorded:**

- Id 161 does not exist. A forward walk of v7's live table counts 155 entries, but `gohan_gi` writes 154
  words for ids 7-160. `0x88D9EC + 154 x 4 = 0x88DC54`, which the bible SPC row names as the start of the
  appearance table copy, so the 155th "entry" is that table's first word.
- `rom_sheet.live_set_offset` is a second copy of the new resolver. Left alone, correct and out of scope.
- `test_tools.py::test_matches_set_table_on_poc_for_old_ids` compares against the DEAD table for ids 7, 56
  and 156 and passes only because nothing repaints those three. A weak pin that will one day go red for
  the wrong reason. Logged as a bible row; not changed.
- It did not touch `docs\backlog\active-todos.md`, because I had it open.

## My verification

I did not take the headline on trust. I read the new `set_table` and `set_offset` out of the file, then
ran both resolutions myself against arena v7:

```
set 58:  through the VANILLA table -> 0x2ab508 ; through THIS ROM's table -> 0x908d54
set 157: through the VANILLA table -> None     ; through THIS ROM's table -> 0x81fe14
```

And I ran the tool itself: `webfoot_decompress.py set <v7> 157` now prints
`set 0x81FE14: 21 animations x 4 directions, table 0x81FE60` and exits 0.

The `None` for set 157 is explained by a fact the bible already held: row 105 says the vanilla set table
`rom:0x3B4E90` ends at `rom:0x3B50E7` and `rom:0x3B50E8` is a different table. Id 157 through the vanilla
table lands exactly on `0x3B50E8`, so the crash is the next table's first word failing the pointer test.

I confirmed it edited nothing under `scripts\permanent\scene\`, which the second agent owns this morning.

Full suite: not run yet. The second agent was still editing the tree, and a suite run during that is
worthless in both directions.
