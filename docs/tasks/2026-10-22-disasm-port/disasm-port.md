# Study and proof: build the modder's LoG II disassembly with free tools (final, 2026-10-22 4:55 PM)

Our working repo: `%USERPROFILE%\Documents\GitHub\legacyofgoku2-gnu` (clone of github.com/siruiusamory-cmyk/legacyofgoku2-disasm at 1da4ef2, MPL-2.0; remote `upstream` fetch only, push disabled; branch `gnu-port`). Untouched reference clone: `%USERPROFILE%\Documents\GitHub\legacyofgoku2-disasm`. Our own LoG II work (`docs\RE-BIBLE.md`, `scripts\permanent\re\` symbols and code map, `scripts\one-time\2026-10-18-disasm-study\functions.csv`, `docs\tasks\2026-10-20-decomp-review\decomp-review-report.md`). Base ROM: `...\LOG\data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba` (SHA-1 18e0715dec419f3501c301511530d2edcd590f8b), read-only.

## Final decisions

- Our Level 1 is their tree, built with a free toolchain (GNU as and ld from devkitARM or arm-none-eabi binutils), byte-identical to the retail ROM. Never ADS: do not install, find or run ARM Developer Suite, armasm, armlink or fromelf.
- Level 2 (relocatable) comes later. Level 3 (matching C) is not ours.
- MPL-2.0: their files keep their license headers and NOTICE; our changes to them are MPL too.

## Questions

1. **What their build needs from ADS:** list every place that calls armasm, armlink, fromelf or ADS-specific syntax: `rebuild.cmd`, `check.cmd`, `extract.cmd`, `scatter.ld`, `tools\code\emit_code.py` (what assembler dialect it emits: AREA, DCD, DCW, EXPORT, IMPORT, CODE16/CODE32, literal pools, labels), and the gate. Quote file and line.
2. **The port plan:** for each item, the GNU equivalent (`.section`, `.word`, `.hword`, `.thumb`/`.arm`, `.global`, `.ltorg` or explicit pools, a GNU linker script with fixed addresses for every section, `objcopy -O binary`). Say whether to change `emit_code.py` to emit GNU syntax directly (preferred: one dialect switch) or convert its output.
3. **Proof:** install the free toolchain (installs are pre-approved for this project; prefer a portable or user-scope install; say exactly what you installed and where). Port enough to build the whole ROM, or if that is too big for one run, a proof on a slice (for example all code in `rom:0x0-0x28724` plus the raw slices) that reproduces those bytes exactly. Report the SHA-1 of what you build against the retail SHA-1 and list any differing ranges.
4. **Names cross-check:** they classify 1,094 functions; our code map lists 2,264 (`functions.csv`). Explain the difference with examples (split versus merged bodies, vtable targets, veneers). List the names we have that they lack (and the reverse), as a table in `docs\names-crosscheck.md` inside our working repo. Do not rename anything in their files yet.
5. **Their Python tools:** before running any of them, read it. List every tool that touches the network, runs an `.exe`, deletes folders, writes outside the repo (for example `%LOCALAPPDATA%` caches) or uploads. Run only what the build needs, after that read, and never an upload or a prebuilt `.exe`.

## Deliverable

- Commits on branch `gnu-port` in our working repo, one concern per commit, with a co-author trailer. Never push. Never change the `upstream` remote.
- A `docs\GNU_BUILD.md` in our working repo: how to build with the free toolchain, in a few steps.
- Bible rows only for new LoG II facts, in `scripts\one-time\2026-10-22-disasm-port\bible_rows.md` (sections as in `scripts\one-time\2026-10-19-r21-build\bible_rows.md`).

## Parallel run

- A build task writes `...\LOG\scripts\permanent\`, `...\LOG\tests\`, `...\LOG\builds\` and `...\LOG\scripts\one-time\2026-10-22-r28-build\`. Do not touch them. You write only in `%USERPROFILE%\Documents\GitHub\legacyofgoku2-gnu\` and `...\LOG\scripts\one-time\2026-10-22-disasm-port\`.

## Limits

- Never write under `...\LOG\data\`. Read the base ROM only; if their extract step needs the ROM inside the repo, copy it to the path their docs name, and make sure `.gitignore` keeps it out of git (never commit ROM bytes or extracted game data).
- Never `cd` in any shell call; absolute paths and `git -C`. Write each file with Python. LF, no byte order mark, no em or en dashes in files you write.
- Label findings CONFIRMED, LIKELY or SPECULATIVE.

## Report

Save it as `docs\tasks\2026-10-22-disasm-port\disasm-port-report.md`: the ADS dependency list, the port plan, what you installed, the proof result (SHA-1 match or differing ranges), the commits, the names cross-check summary, the tool safety list and the effort left. Then reply with status, the build result, the effort left and concerns only.

