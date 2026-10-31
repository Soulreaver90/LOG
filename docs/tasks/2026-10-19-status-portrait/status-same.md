# Status screen: show the dialog portrait art in the same colors (final, 2026-10-19 7:31 AM)

Personal GBA ROM hack (Legacy of Goku II, USA). Read first: `docs\research\research-status-screen.md`, `docs\research\re-portraits.md`, `docs\RE-BIBLE.md` sections 5, 5a and 5b, the header and pairing code of `scripts\permanent\patches\gohan_portraits.py`, `docs\tasks\2026-10-18-portrait-gohan\portrait-gohan-report.md` (status twins, the pairing map, the drift), `scripts\one-time\2026-10-18-disasm-study\` (`listing.py`, `symbols.json`: use them to read code by name).

## My ask (verbatim)

"The status twin of A is too burnt, not sure why we have a status version, just use the same for both."

Today each dialog portrait has a status twin: the same drawing remapped by a pairing map into the status screen's own palette. The remap shifts skin toward red and merges shades. I want the status screen to show the dialog art with the dialog colors.

## Task

1. Trace how the status screen draws its portrait: which id and data it loads, BG or OBJ, which palette (address, bank, size), when the palette is loaded, and what else on that screen uses the same palette slots. Use the disassembly tools.
2. Find the smallest way to show the dialog art in dialog colors there. Candidates, each with evidence, effort and blast radius:
   - point the status screen at the dialog portrait id and load the dialog (OBJ) colors it needs into the status palette, if the slots are free or only the portrait uses them;
   - draw the status portrait as OBJ with the OBJ palette;
   - load the needed OBJ colors into free status palette slots and remap once at build time to exact matches (no nearest-color fallback).
   The result must be pixel-exact to the dialog art's colors (within GBA 15-bit color).
3. Blast radius: the change will LIKELY apply to every character's status portrait. Say exactly which portraits change, and show a before and after for 3 vanilla characters (for example Goku, Vegeta, Piccolo) and for gi Gohan.
4. Write the fix as a new patch file in `scripts\permanent\patches\` (style of the others: `_expect` checks, `apply(rom, alloc)`, notes) with a new test file. It must work with the current portraits and with the softer remaster PNGs a second task is painting in `art\portrait-sources\remaster\` (read only). Do NOT add it to the build list and do not build a ROM. If the existing pairing logic in `gohan_portraits.py` must change, describe the change and its test impact; do not edit that file.
5. Proof image `archive\2026-10-18-art-review-renders\status_same.png` on lime (191, 255, 7): for each sample, dialog art | status now | status after. Look at it.

## Parallel run

- A portrait task writes in `art\portrait-sources\remaster\` and `scripts\one-time\2026-10-19-portrait-from-anime\`. Read them only.
- Your files: the new patch, its new test, `scripts\one-time\2026-10-19-status-portrait\`, the proof image. Do not edit `docs\RE-BIBLE.md`; put your bible rows in `scripts\one-time\2026-10-19-status-portrait\bible_rows.md` (tagged, bible row format) for me to merge.
- Run only your own tests while you work and the whole suite once at the end, from the `scripts\permanent` root.

## Limits

- Read ROMs only (base ROM and `builds\log2_poc_r18.gba`). Never write under `data\`. Never overwrite a ROM or .sav. Install nothing.
- Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths. A shell heredoc collapses backslashes: write files with Python (no heredocs, no `sed -i`), and check them for control characters.
- Label findings CONFIRMED, LIKELY or SPECULATIVE. If you cannot trace a piece, say so and do not guess.

## Report

Save it as `docs\tasks\2026-10-19-status-portrait\status-same-report.md`: the draw path with addresses, the options table, the chosen fix and blast radius, the patch file and test count, the proof image path. Then reply with status, the chosen fix in one line, the test count and concerns only.

