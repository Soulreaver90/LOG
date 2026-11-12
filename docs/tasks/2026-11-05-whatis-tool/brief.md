# Brief: an address lookup tool

## Why

The single most expensive failure of 2026-11-05 was not reverse engineering. It was **re-deriving
facts the project had already written down**, repeatedly, because `docs\RE-BIBLE.md` is 747 KB and
cannot be searched by address.

Four instances in one night:

1. The map combat flag `+0x08` was re-derived by a full table scan. The bible already had it, in
   the map 7,1 row ("combat +8 = 1") and the map 6,6 row ("no spawns, combat 0").
2. "A new map needs a moved table" was re-derived. The bible already said it, in the `CPR` row.
3. The map count getter `@0x0800E0AC` and the table literals were re-derived. Same `CPR` row.
4. A CAUTION row was raised claiming map 6,1's item list "does not parse". It parses fine; the
   bible's own `TLS` row already said `+0x14` is a list of POINTERS. A false alarm against a
   correct row.

A fifth failure had a different shape and the tool should help with it too: a scan for the map
table's BASE address found 3 literals and missed a 4th, `rom:0x195C`, which names map ENTRY 3. A
pointer into the middle of a table never contains that table's base address.

## What to build

A tool that answers "what do we already know about this?" for an address, a RAM word, a function,
a set id or a free-text term, across every source this project has.

Suggested: `scripts\permanent\rom\whatis.py`. **Read `docs\tool-index.md` FIRST**: if something
close already exists, extend it rather than writing a second tool. Writing a duplicate is the
documented default failure of this project.

Given a query it should search and report, each with its source so a claim can be traced:

| Source | Path |
|---|---|
| The bible | `docs\RE-BIBLE.md`, matching rows, with their tag and confidence label |
| Named RAM words | `GitHub\legacyofgoku2-disasm\docs\RAM_LEDGER.csv`, with the behaviour test |
| The function index | `GitHub\legacyofgoku2-disasm\docs\CODE_INDEX.md` |
| Function bounds | `GitHub\legacyofgoku2-disasm\tools\code\FUNCTION_BOUNDS.csv` (which function CONTAINS an address) |
| Generated assembly | `GitHub\legacyofgoku2-gnu\build\code`, the `.s` file for a function |
| Our own modules | `scripts\permanent\patches\*.py` and `scripts\permanent\scene\scene_lib.py` |

It must accept a ROM address (`0x3B8140` or `rom:0x3B8140`), a code address (`0x0800A680`), an
EWRAM or IWRAM address (`0x03001FA8`), and plain text.

### The part that matters most

For a ROM address, also report **who references it, in more than one shape**, because the one-shape
sweep is how the 4th literal was missed:

- shape A: word-aligned ROM words equal to the address, and equal to `address | 0x08000000`.
- shape B: Thumb pc-relative loads that name it. For an instruction at `A`, the literal is at
  `((A + 4) & ~3) + imm`, where `imm` is the low byte of a `0x48xx` halfword times 4.
- shape C: **words that land INSIDE a structure the address belongs to**, not just equal to its
  base. Take a base and a stride and report any word pointing into that range. This is the shape
  that would have found `rom:0x195C`.

Print the shapes separately with their counts, and say plainly when they disagree, because a
disagreement between two shapes is itself the finding.

## Verification, which you must do yourself

The tool is only useful if it finds things that are actually there. Prove it on cases with known
answers, and put the results in the report:

| Query | Must find |
|---|---|
| `0x03001FA8` | `Sprite_CurrentDirectory` in `RAM_LEDGER.csv`, plus the bible rows about its writers |
| `0x0800A680` | the leader change core, and the bible row about its guarded appearance block |
| `combat` | the map 7,1 row, the map 6,6 row and the `ARN` rows |
| `0x409368` | the map table rows, and in shape C the 4th literal `rom:0x195C` |
| `0x3B8140` | the ending table rows, including the two type 5 records that call it |

A query that returns nothing must say "the search returned nothing", never "it does not exist", and
must name which sources it searched.

## Rules

- `docs\tasks\global.md` applies in full. Absolute paths only, never `cd`.
- Python is `py -3.14 -P`. Header block like the other scripts. No em or en dashes. No byte order mark.
- The tool is READ ONLY. It never writes to a ROM and never writes to the bible.
- Add tests under `scripts\permanent\tests\`, and the full suite must pass. Capture unittest's OWN
  exit code and NEVER pipe the run into `tail` or `head`.
- Add the tool to `docs\tool-index.md` in the same session, and regenerate it with
  `scripts\permanent\make_tool_index.py` if that is how it is maintained.
- Never put a Windows path inside a `python -c` argument or an executed shell heredoc: on this
  machine a quoted heredoc collapses backslashes and Python then reads `\t`, `\r` and `\2` as
  escapes. Build paths from forward slashes or `chr(92)`.

## Report

Write `docs\tasks\2026-11-05-whatis-tool\report.md`: what you built, the verification table above
with real output, the suite result with the exit code you observed, and anything the tool revealed
that nobody had noticed.

One report message, then stop. Do not add a byte order mark.
