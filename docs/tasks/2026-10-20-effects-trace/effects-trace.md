# Study: trace the 40 field-sourced OBJ VRAM users to their graphics, and prove none uses OBJ pal:172 (final, 2026-10-20 7:31 AM)

Personal GBA ROM hack (Legacy of Goku II, USA). Build: r21 (`archive\builds\log2_poc_r21.gba`, SHA-1 `a3e9963aee85aef98d0bd013981f7deddf733fb2`). Read first:
- `docs\tasks\2026-10-19-palette-slot\palette-slot-report.md` (all of it; the open item is "What the census cannot see"),
- `scripts\one-time\2026-10-19-palette-slot\p7_objsrc.txt` (the 40 OBJ VRAM users), `p8_dma.txt`, `p11_final.txt` and the scripts beside them,
- `docs\RE-BIBLE.md` (the object, sprite, codec and palette sections; search tags `#object`, `#sprite`, `#codec`, `#palette`),
- the disassembly tools: `scripts\permanent\re\` (`from re_sym import sym`), the seeded Ghidra project `scratch\ghidra\seeded\LoG2seeded.gpr` (Ghidra 12.1.4 at `%USERPROFILE%\Tools\ghidra_12.1.4_PUBLIC`, headless steps in `scripts\permanent\ghidra\README.md`).

## My context

I asked why 40 effects stayed "LIKELY clean" if we have a disassembly. Answer given: our disassembly is a partial map; these effects take their graphic address from an object field at run time. He chose the static route: trace every writer of those fields until each effect has a known graphic. The result also grows the disassembly (names and notes), which is a goal of its own.

## Task

1. For each of the 40 OBJ VRAM users in `p7_objsrc.txt`: name the object field (offset) or argument it reads the graphic source from.
2. For each such field: find every writer (stores to that offset on that object type, constructors, init tables, script commands). Use at least two independent search shapes, for example (a) `str`/`strh` to the offset with the object base from the same constructor family, and (b) literal pool words that point into the graphic data, plus init tables that the constructors copy from. Reconcile the counts; a disagreement is a finding.
3. Resolve each writer to the set of possible ROM graphics (address, format, size). Where a value comes from a table, enumerate the whole table.
4. Decode every graphic found (the frame header formats in the bible and the existing unpackers), with every remap table the palette-slot study found applied, and list which OBJ palette indices each can show. State for pal:172 (and the runner-up pal:86): used or not, per graphic.
5. Anything still open at the end: list it with why, and label it. Do not claim CONFIRMED for a path you did not trace.

## Deliverable

- `scripts\one-time\2026-10-20-effects-trace\effects_trace.txt`: one row per OBJ VRAM user: user function, field, writers, graphics, indices, verdict for 172 and 86.
- Names for the functions and fields you understand, as proposals in `scripts\one-time\2026-10-20-effects-trace\symbols_proposed.txt` (format of `scripts\permanent\re\` symbol files). Do not edit `scripts\permanent\`.
- Bible rows in `scripts\one-time\2026-10-20-effects-trace\bible_rows.md` with "## Section N" headings as in `scripts\one-time\2026-10-19-r20-build\bible_rows_sections.md`.

## Parallel run

- Nothing else is running. I edit art under `art\portrait-sources\remaster\anime\cell\owner_edit\`. Do not touch it. Write only `scripts\one-time\2026-10-20-effects-trace\`.

## Limits

- Read-only on every ROM. Never write under `data\`. No patch.
- Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths. A shell heredoc collapses backslashes: write files with Python, and check them for control characters. Tools installed with pip --user load with `py -3 -P`.
- Labels CONFIRMED, LIKELY or SPECULATIVE on every claim.

## Report

Save it as `docs\tasks\2026-10-20-effects-trace\effects-trace-report.md`: the method, the counts per search shape and how they reconcile, the per-user table summary, the verdict for pal:172 (CONFIRMED clean, or the exact users that block it), what stays open, and the symbols proposed. Then reply with the verdict, the open count and concerns only.

