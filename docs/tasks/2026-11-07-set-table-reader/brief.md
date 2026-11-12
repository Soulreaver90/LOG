# Brief: readers must resolve the live sprite set table, not the vanilla one

Agent: build. Owner approved arena v7 this morning, so this is plumbing behind approved work.
Read `docs\tasks\global.md` first. Absolute paths only. Never `cd`.

## The defect, already measured by me

`scripts\permanent\rom\webfoot_decompress.py` line 20 holds `SET_TABLE = 0x3B4E90`. That is the
VANILLA sprite set table. `scripts\permanent\patches\gohan_gi.py` line 130-133 COPIES that table into
the expansion area, appends ids 157-160, and repoints the ROM literal at `rom:0x959C` at the copy.
Every PATCH resolves through `0x959C`. Three READERS do not.

Measured by me on 2026-11-07, not estimated:

| ROM | literal `rom:0x959C` resolves to | ids 7-156 identical to vanilla |
|---|---|---|
| base USA ROM | `0x3B4E90` (the same table) | yes |
| `log2_poc_r41_arena_v7.gba` | `0x88D9EC` | **no, id 58 differs** |

So on a build, a reader using `SET_TABLE` reads a DEAD copy. Today that is one wrong set, 58
(`superperfect_cell`). It also means those readers can never see ids 157-160 at all, because the
vanilla table has only 150 entries and the gi sets live past its end.

This matters because the reader says nothing. It returns vanilla art and looks correct.

## The three readers to fix

| File | Line | What it does |
|---|---|---|
| `scripts\permanent\rom\webfoot_decompress.py` | 232 | `rom_ptr(rom, SET_TABLE + 4 * (int(key) - 7))` |
| `scripts\permanent\rom\log2_sprites.py` | 239 | the same expression |
| `scripts\permanent\art\gi_aura.py` | 185 | the same expression |

`scripts\permanent\emu\actors.py` line 33 and 92 ALREADY resolve from `0x959C`. Copy that, not a new idea.

## The pattern to copy

`scripts\permanent\scene\scene_probe.py` `map_table()` resolves the map table from the literal at
`rom:0xEBD8` and keeps `MAP_TABLE` as the base ROM's documented value. Do the same shape here:

- Add `set_table(rom)` to `webfoot_decompress.py`, reading the literal at `rom:0x959C`.
- Keep `SET_TABLE = 0x3B4E90` as the base ROM's value, with its comment saying it is the BASE value
  and that `set_table()` resolves the live one.
- Point all three call sites at `set_table(rom)`.
- On the base ROM `set_table()` must return `SET_TABLE`, so base behaviour does not change.

## Also in scope: two constants nothing pins

1. `scripts\permanent\rom\item_index.py` lines 29-30, `TABLE = 0x6ADE24` and `STRING_TABLE = 0x0E2840`.
   I checked by hand that both literals sit at the same addresses in the base ROM and in arena v7, so
   no patch moves them today. Nothing pins that. Add a test that asserts it against both ROMs.
2. `scripts\permanent\rom\log2_save.py` lines 36-40 and 175: `0x081D9548`, `0x086F6D8C`, `0x086F8E40`,
   `0x086ADE24`, `QUEST_TABLE = 0x086D68DC`. Check each the same way and pin what holds. If one DOES
   move on a build, say so and do not guess a fix.

## Out of scope, do not touch

- `scripts\permanent\disasm\ext_ops.py`. It reads the base ROM by design.
- `scripts\permanent\scene\scene_probe.py` and `scene\map_view.py`. A second agent owns those files
  this morning. Do not edit them, and do not edit any file under `scripts\permanent\scene\`.
- The full test suite. Run only the test modules for the files you touch. I run the suite myself.

## Rules

- Measure every claim on a BUILD, not only the base ROM. The base ROM cannot show a constant a build
  moves, which is the whole reason this defect survived.
- `py -3.14 -P`. Never put a Windows path inside a Python string literal in a heredoc.
- Never write under `data\`. Never overwrite a ROM, save or state.
- Give the bible rows you earn as a `rows.md` beside this brief, as `## Section N` table blocks, tag `RDR`.
- Report: what you changed, the measured before and after on arena v7, your test counts with real exit
  codes, and anything you could not prove.

One report message, then stop. Do not add a byte order mark.
