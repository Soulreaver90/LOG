# Study: one new portrait color, a free OBJ palette slot for #F8E0D0 (final, 2026-10-19 8:32 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Current build: r21 (`archive\builds\log2_poc_r21.gba`, SHA-1 `a3e9963aee85aef98d0bd013981f7deddf733fb2`). Read first: `docs\RE-BIBLE.md` sections 5a and 5b (portraits, the OBJ palette `rom:0x1DA6C8`, the status page palette `rom:0x1D4F50`, `status_portrait` and its 64-slot BG palette pool), the tools in `scripts\permanent\re\` (`from re_sym import sym`), and `scripts\one-time\2026-10-19-portrait-from-anime\anime\e8_pal_usage.py`.

## My goal

All remaster portraits (Goku, Vegeta, the Gohans, Goku Super Saiyan, later Cell and others) share one anime skin ramp. The shadows exist (OBJ 115, 116). The lit skin does not: it needs (248, 224, 208), #F8E0D0, BGR555 `0x6B9F` (bytes `9F 6B`). The plan is to write that color into one OBJ palette index that nothing else needs.

## Questions (answer each with quoted code or bytes)

1. How the OBJ palette reaches palette RAM `0x05000200`: who copies `rom:0x1DA6C8`, how many entries, when (boot, map load, menu, dialog open), and whether anything rewrites parts of it later (sprite palette banks loaded per actor or per map, fades, flashes, palette effects for forms or auras).
2. Dialog portraits are 8bpp OBJ: index N uses bank N / 16, entry N % 16. Which banks stay as `rom:0x1DA6C8` has them while a dialog portrait is on screen, and which banks the game reloads for actors, effects or the HUD in the field, in cutscenes and in battle scenes that show dialog?
3. Candidates: the 73 indices no dialog portrait uses (`e8_pal_usage.py` lists them). For each candidate bank, say whether any 4bpp sprite, the HUD, an effect or a menu uses it, with evidence. Prefer an index that is CONFIRMED unused on every screen where a portrait shows.
4. The status page: `status_portrait` paints the dialog portrait into a BG palette pool. Say how a new OBJ color would reach it (does the pool copy colors from the OBJ palette by index or by value?) and what must change, if anything.
5. Fades: if the game fades by rewriting palette RAM from the ROM palette, say whether a changed ROM entry fades correctly.

## Deliverable

- A recommended index with its evidence, and one runner-up. Labels CONFIRMED, LIKELY or SPECULATIVE on every claim; search with at least two independent shapes (for example, literal pool references to `0x1DA6C8` or to palette RAM, and DMA or CpuSet calls with `0x05000200` or bank offsets) and reconcile the counts.
- A test you can run now: a copy of r21 in `scratch\rom-copies\palslot\` with only that one palette entry changed to `0x6B9F`, and a check that the change is the only diff. Do not build an official r22 and do not touch `builds\`.
- Bible rows in `scripts\one-time\2026-10-19-palette-slot\bible_rows.md`, with "## Section N" headings as in `scripts\one-time\2026-10-19-r20-build\bible_rows_sections.md`.

## Parallel run

- A portrait task writes `scripts\one-time\2026-10-19-portrait-from-anime\anime\` and `art\portrait-sources\remaster\anime\cell\`. Do not touch them.
- You write only `scratch\rom-copies\palslot\`. Read anything else.

## Limits

- Never write under `data\`. Never overwrite a ROM, .sav or state file. No patch in `scripts\permanent\`; propose the patch in the report.
- Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths. A shell heredoc collapses backslashes: write files with Python, and check them for control characters. Tools installed with pip --user load with `py -3 -P`.

## Report

Save it as `docs\tasks\2026-10-19-palette-slot\palette-slot-report.md`: the answers, the recommended index and runner-up, the test copy and its diff proof, the proposed patch, and the risks. Then reply with the recommendation, the test copy path and concerns only.

