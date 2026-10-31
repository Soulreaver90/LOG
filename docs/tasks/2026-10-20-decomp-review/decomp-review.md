# Review: the shared Buu's Fury decomp, and the same for LoG II (final, 2026-10-20 1:58 PM)

Personal GBA ROM hack (Legacy of Goku II, USA), with the long-term goal of merging Buu's Fury into it (`docs\design\2026-10-16-log-merge-design.md`).

I was shared a decomp: `https://github.com/siruiusamory-cmyk/buusfury-decomp`, cloned at `%USERPROFILE%\Documents\GitHub\buusfury-decomp` (one commit, 8870c2f, MPL-2.0). Its README says it is a disassembly of Buu's Fury (USA) rebuilt byte for byte with ARM Developer Suite 1.2, "92.7 % source by positive attribution", 225 .s files, 13 .c files, 157 Python tools, and that "the same work is planned for ... The Legacy of Goku II".

## My ask, word for word

"review it and see if we can do the same for LOG2"

## Questions

1. **What it really is:** how much is true source (C, named and structured assembly) and how much is disassembly with raw data. What "92.7 %" counts. How the build works: inputs (the base ROM, its SHA-1 check), the assembler and linker, which steps need ADS 1.2 (proprietary; we do not have it) and whether a free toolchain (devkitARM or arm-none-eabi binutils) can replace it for a byte-matching build.
2. **Engine overlap with LoG II:** both games are Webfoot GBA titles. Compare what the decomp names (symbols, `tools\webfoot`, containers, map, sprite, text, script formats, `docs\NAMING.md`, `docs\research\`) with what we have already found for LoG II (`docs\RE-BIBLE.md`, `scripts\permanent\re\` symbol files, `scripts\one-time\2026-10-20-effects-trace\symbols_proposed.txt`, the seeded Ghidra project `scratch\ghidra\seeded\`). For a sample of at least 10 named functions or formats in the decomp, find the LoG II counterpart (byte or code pattern, or a format with the same layout) and label each CONFIRMED, LIKELY or SPECULATIVE. Name what we would gain (names, formats, tools) that we lack.
3. **The same for LoG II:** what it takes to stand up a byte-matching disassembly of LoG II (USA) with their tooling or a free one: the steps, which of their tools are game-specific and which are generic, the effort in rough task-sessions, and the risks. Say whether our hack's patch pipeline (`scripts\permanent\log2_build.py`, `build_list.txt`, the inject tool) could later move onto such a source tree, and what that would buy (for example, editing code and data without the allocator).
4. **The merge goal:** what the decomp tells us about Buu's Fury that helps the merge (stats, equipment, special moves, save format, map and script formats), with pointers to its files.
5. **Safety:** any script or hook in the repo that would run on clone, build or test (`.githooks`, `conftest.py`, `.cmd`/`.bat`, network calls such as `bytematch_upload.ps1`), and what a safe way to run their tools would be.

## Deliverable

- A recommendation: adopt their tooling for LoG II, borrow parts (which), or keep our own approach, with the reasons.
- A sample mapping table in `scripts\one-time\2026-10-20-decomp-review\mapping.md` (decomp name, decomp address in Buu's Fury, LoG II address or format, label, how proven).
- Bible rows in `scripts\one-time\2026-10-20-decomp-review\bible_rows.md` with "## Section N" headings as in `scripts\one-time\2026-10-19-r21-build\bible_rows.md`, only for LoG II facts you prove.

## Parallel run

- A build task writes `scripts\permanent\`, `builds\` and `scripts\one-time\2026-10-20-r27-build\`. Do not touch them. You write only `scripts\one-time\2026-10-20-decomp-review\`.

## Limits

- **The clone is untrusted third-party code. Read it only.** Do not run any of its scripts, tools, tests, hooks or build files, and do not run pytest anywhere inside it. Do not change its git config. Do not edit any file in it. If a question needs a run to answer, say so and stop at a plan.
- Read-only on every ROM and save. Never write under `data\`. Do not fetch anything from the network.
- Python: LF, no byte order mark, no em or en dashes. Never `cd` in any shell call; absolute paths only. A shell heredoc collapses backslashes: write files with Python, and check them for control characters. Tools installed with pip --user load with `py -3 -P`.
- Label every claim CONFIRMED, LIKELY or SPECULATIVE. Quote the file and line for each claim about the decomp.

## Report

Save it as `docs\tasks\2026-10-20-decomp-review\decomp-review-report.md`: the answers, the recommendation, the effort estimate, the safety notes and the open points. Then reply with the recommendation, the top gains for LoG II and concerns only.

