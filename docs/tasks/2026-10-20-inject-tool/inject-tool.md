# Tool: one-command image inject for portraits and palette entries (final, 2026-10-20 10:00 AM)

Personal GBA ROM hack (Legacy of Goku II, USA). Base: r22 (`archive\builds\log2_poc_r22.gba`; its SHA-1 is in `docs\tasks\2026-10-20-r22-build\r22-build-report.md`). Read first: `r21-build-report.md` and `r22-build-report.md` (how ids 65 and 40 were added, and the two-call allocator workaround), `scripts\permanent\patches\portrait_remaster.py` and `gohan_portraits.py` with their tests, the build script and patch list in `scripts\permanent\`, `docs\RE-BIBLE.md` sections 5, 5a and 5b, `docs\tasks\2026-10-19-palette-slot\palette-slot-report.md` (the two ROM palette copies) and `scripts\one-time\2026-10-19-portrait-from-anime\anime\f0_final.py` and `f8_cell_final.py` (how I check a PNG of mine).

## My ask, word for word

"We need a proper image inject! We need proper tools. Hand tooling is time consuming. Spend the time now building a simple tool so that all future work takes only a few seconds."

Today a single portrait takes a task about 45 minutes: a hand edit of `portrait_remaster`, a second patch call so earlier bytes do not move, new tests, scene hunting, a diff proof and a report. The goal is that adding or replacing a portrait, or changing a palette entry, is one command that runs in seconds.

## What to build

1. **One table** as the single source of truth, for example `art\tables\portraits.json`: dialog portrait id -> PNG path (under a fixed art folder in the workspace, for example `art\tables\portraits\`), plus an optional note. Move every existing remaster portrait into it: 63, 106, 115, 117, 119, 65, 40, with each PNG copied in (byte for byte from the files r22 used).
2. **One table for palette entries**, for example `art\tables\palette.json`: OBJ index -> color. It writes both ROM copies (`rom:0x1DA6C8` BGR555 and the RGB table at `rom:0x3ECBA4`, OBJ part at +768). Leave it empty for now; slot 172 waits for me. The tool must accept an entry without code changes.
3. **One patch** that reads the portrait table and writes every frame into one reserved portrait region at a fixed ROM address, in a stable order (slot per id, append-only), and repoints the live block word per id. Adding or replacing one portrait must never move another portrait or any code. Replace the two-call `portrait_remaster` workaround. `gohan_portraits` art (115, 117, 119) may move into the table too, if the block and ids stay right; say what you did.
4. **One command**, for example `py -3 -P scripts\permanent\art\inject.py portrait <id> <png>` and `inject.py palette <index> <r,g,b>`, that:
   - checks the PNG: 64x64; every color is in the OBJ palette (with the palette table applied), mapped by value to an index; reports any off-palette color with its nearest index and stops (a `--snap` flag maps them to the nearest, as I did for the 23 near-black pixels on Cell); the frame (outer 3 px) equals the vanilla portrait's frame;
   - copies the PNG into the art folder, updates the table;
   - builds the next ROM `builds\log2_poc_rN.gba` from the current build list, copies the latest `.sav` and `.ss*` to the new names (never overwrite);
   - verifies: each table portrait read back from the ROM equals its PNG; the diff against the previous build touches only the expected regions; prints the new SHA-1 and the diff regions;
   - writes one line to `docs\build-log.md`.
   Add `inject.py check <png> [id]` that only validates, and `inject.py list` that prints the table.
5. **Save state safety:** code addresses must not change when portraits or palette entries change. Prove it for the move from the r22 layout to the new layout (list the code patch addresses before and after), and say whether an mGBA state from r22 still works on the first build made by the tool.
6. **Tests:** the table round trip, the validation failures (wrong size, off-palette, frame changed), the stable layout (adding a portrait leaves the others and all code byte-identical), the palette writer (both copies), and the whole suite.
7. **First run as the proof:** use the tool to rebuild r22's content as `log2_poc_r23.gba` (same portraits, new layout). Report how long `inject.py portrait 40 <the Cell png>` takes end to end, the r23 SHA-1, and the diff from r22 (expected: only the moved portrait data and block words).
8. **Docs:** a short `art\tables\README.md` with the commands and one example. Keep it to what I need.

## Parallel run

- An effects study writes only `scripts\one-time\2026-10-20-effects-trace\`. Do not touch it. I may edit files under `art\portrait-sources\remaster\anime\`; do not touch them.
- Bible rows in `scripts\one-time\2026-10-20-inject-tool\bible_rows.md` (sections as in `scripts\one-time\2026-10-19-r21-build\bible_rows.md`). Do not edit `docs\RE-BIBLE.md`.

## Limits

- Never write under `data\`. Never overwrite a ROM, .sav or state file.
- Python: LF, no byte order mark, no em or en dashes. Code style: a header block per file, short functions, precise names, 1-2 line comments for the non-obvious why only. Never `cd` in any shell call; absolute paths only. A shell heredoc collapses backslashes: write files with Python, and check them for control characters. Tools installed with pip --user load with `py -3 -P`.
- Work scripts in `scripts\one-time\2026-10-20-inject-tool\`. Label findings CONFIRMED, LIKELY or SPECULATIVE.

## Report

Save it as `docs\tasks\2026-10-20-inject-tool\inject-tool-report.md`: the design (tables, region, patch, command), the state safety proof, the tests, the r23 SHA-1, the timing of one inject, and the diff proof. Then reply with status, the r23 SHA-1, the command timing, the test count and concerns only.

