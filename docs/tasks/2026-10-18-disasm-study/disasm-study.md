# Study: a disassembly of Legacy of Goku II to make modding easier (final, 2026-10-18 9:18 PM)

Personal GBA ROM hack (Legacy of Goku II, USA; Buu's Fury merge later). Read first: `docs\RE-BIBLE.md` (all sections, skim), `docs\research\re-overview.md` (engine code map), `docs\data-index.md`, `scripts\permanent\rom\thumb_dis.py`, `scripts\permanent\log2_build.py` and two patch files in `scripts\permanent\patches\` (how we patch today: byte edits plus allocations in the expanded ROM).

## My ask

"Work on disassembly. Not sure if we can disassemble the game; that will make our lives easier, make modding easier."

## Questions to answer, with evidence

1. **What a disassembly would give us** over today's method (byte patches, Thumb stubs, a free-space allocator): relocatable code, named functions and data, a rebuild that matches the original byte for byte, easy data edits. Which of our pains it would remove (list them from the bible and patch headers, for example stale offsets after moving records, hand-assembled Thumb, pointer tables).
2. **Routes, each with effort, tools and risk:**
   - A. A full re-assemblable disassembly that rebuilds a byte-identical ROM (the pret style used for Pokemon GBA games, or a tool such as a GBA disassembler that emits assembler source). Needs an ARM assembler and linker (for example devkitARM or arm-none-eabi binutils): none is installed, and installs need my approval. Say exactly what would have to be installed.
   - B. A Ghidra (or similar) project with our symbols. Java 21 is installed (`C:\Program Files\Eclipse Adoptium\jdk-21.0.12.101-hotspot`); Ghidra is not. Same install question.
   - C. Our own Python tooling with no installs: extend `thumb_dis.py` into a whole-ROM code map and an annotated listing (function discovery from BL targets, vtables and pointer tables; code vs data split; names from the bible), plus a symbol file our patches can import instead of raw addresses.
   - D. Any mix (for example C now, A later).
3. **Size of the job:** how much of the ROM is code vs data (estimate from the code map you can build), how much the bible already names, how the code was compiled (ARM/Thumb mix, compiler fingerprints, library code such as the sound driver), whether a byte-identical rebuild is realistic.
4. **Buu's Fury:** whether the same tooling applies to it (same engine, same compiler?), read-only.
5. **A first step with no installs (route C), built and proven:**
   - `scripts\one-time\2026-10-18-disasm-study\codemap.py`: walk the USA ROM from the entry point, the IRQ handler, every BL target, the vtables and the pointer tables the bible names. Emit `scripts\one-time\2026-10-18-disasm-study\functions.csv` (address, size, Thumb or ARM, name if known, callers count) and the code-vs-data coverage.
   - `scripts\one-time\2026-10-18-disasm-study\symbols.py` (or .json): names for every function and table the bible names, with its bible row tag.
   - `scripts\one-time\2026-10-18-disasm-study\listing.py <addr|name>`: an annotated listing of one function with names for calls and known data.
   - Prove it: run it on 5 functions the bible documents and show the names line up.
   Do not change `scripts\permanent\`; I decide on adoption.

## Deliver

- A recommendation: which route, in what order, with effort per step (S, M, L) and what each step unlocks for the mod (story scenes, new fights, sprites, Buu's Fury merge).
- The install list for routes A and B, for me to approve or not.
- The route C tools, working, with their coverage numbers.
- Bible rows for each new confirmed fact, tagged.

## Limits

- Install nothing. Do not download tools. Read ROMs only. Never write under `data\`.
- Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths. A shell heredoc collapses backslashes: write files with Python (no heredocs, no `sed -i`), and check them for control characters.
- Other tasks edit `scripts\permanent\`, `art\` and `builds\`. Write only in `scripts\one-time\2026-10-18-disasm-study\`, the report and your bible rows.
- Label findings CONFIRMED, LIKELY or SPECULATIVE.

## Report

Save it as `docs\tasks\2026-10-18-disasm-study\disasm-study-report.md`. Then reply with the recommendation in 3 lines, the coverage numbers, the install list and concerns only.

