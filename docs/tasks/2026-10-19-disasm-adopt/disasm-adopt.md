# Adopt the disassembly tools and seed Ghidra (approved 2026-10-19 8:40 AM)

Personal GBA ROM hack (Legacy of Goku II, USA). Read first: `docs\tasks\2026-10-18-disasm-study\disasm-study-report.md` (route C tools, Ghidra findings, sections 6 and the recommendation), the tools in `scripts\one-time\2026-10-18-disasm-study\`, `scripts\permanent\rom\thumb_dis.py`, two patch files in `scripts\permanent\patches\` (how they name addresses today).

## Final approval

The approved: "use these tools now" and "load the code map and names into Ghidra". (The toolchain is a separate task.)

## Task 1: adopt the route C tools

- Move `codemap.py`, `symbols.py` and `listing.py` (and any helper they need) into `scripts\permanent\re\` as maintained tools. Keep the scratch copies. Outputs (`codemap.json`, `symbols.json`, `functions.csv`) go to `scripts\permanent\disasm\data\` or are regenerated on demand; choose one and say why.
- Each tool gets a header block, works from the `scripts\permanent` root with `py -3 -I`, and has tests in `scripts\permanent\tests\test_re_tools.py`: the 5 bible functions list with their names, `appearance_table --refs` returns the 18 known words, the function count and coverage on the USA ROM.
- A small import helper so a patch can write `sym("idle_tick")` instead of a raw address. Do not rewrite existing patches; show it in one new test only.

## Task 2: seed Ghidra

- Ghidra 12.1.4 is at `%USERPROFILE%\Tools\ghidra_12.1.4_PUBLIC`, Java 21 is installed. Create a NEW project in `scratch\ghidra\seeded\` (do not touch `scratch\ghidra\LoG2.gpr`).
- Import the USA base ROM (read only) as ARM v4T little endian at base 0x08000000, with RAM blocks for EWRAM 0x02000000, IWRAM 0x03000000 and the IWRAM code copy if the bible names its source.
- Turn off the analyzers that decode data as code (the study saw 2,353 false functions), then apply the codemap starts (Thumb vs ARM mode per start) and `symbols.json` names with a headless script (Ghidra Python or Java script, saved in `scripts\permanent\ghidra\`), then run function analysis.
- Prove it: a headless decompile of 5 named functions (for example `idle_tick` and the type 1 text handler `@0x0800B438`) to `scripts\permanent\ghidra\decomp\*.c`, with our names in the output. Report how many codemap starts became Ghidra functions and how many false functions remain.
- Write `scripts\permanent\ghidra\README.md`: how I open the project in the Ghidra GUI and how to rerun the seeding.

## Parallel run

- An r19 build task and a status screen task work in `scripts\permanent\` (patches, tests, `hand_frames`, `gi_*`) and `builds\`. Your files: `scripts\permanent\re\`, `tests\test_re_tools.py`, `scratch\ghidra\seeded\`, `scripts\one-time\2026-10-18-disasm-study\`. Do not edit `docs\RE-BIBLE.md`; put bible rows in your report.
- Run your own tests while you work and the whole suite once at the end, from the `scripts\permanent` root.

## Limits

- Install nothing new (Ghidra and Java already exist). Read ROMs only. Never write under `data\`.
- Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths. A shell heredoc collapses backslashes: write files with Python (no heredocs, no `sed -i`), and check them for control characters.
- Label findings CONFIRMED, LIKELY or SPECULATIVE.

## Report

Save it as `docs\tasks\2026-10-19-disasm-adopt\disasm-adopt-report.md`: the files, the test count, the Ghidra numbers, the decompile samples, and how to open the project. Then reply with status, the test count, the Ghidra numbers and concerns only.

