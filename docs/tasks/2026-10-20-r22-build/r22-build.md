# r22: the new Perfect Cell dialog portrait, id 40 (final, 2026-10-20 9:47 AM)

Personal GBA ROM hack (Legacy of Goku II, USA). Base: r21 (`archive\builds\log2_poc_r21.gba`, SHA-1 `a3e9963aee85aef98d0bd013981f7deddf733fb2`). Read first: `docs\tasks\2026-10-19-r21-build\r21-build-report.md` (how id 65 was added, and the two-call design of `portrait_remaster` with its allocator note), the header and tests of `scripts\permanent\patches\portrait_remaster.py`, and `docs\RE-BIBLE.md` section 5a.

## My ask

"Can you add it to the game?": I finished the Perfect Cell portrait (made from my manga reference with our pipeline, then my own edit). Put it in the game as dialog portrait id 40.

- Art: `art\portrait-sources\remaster\final_r22\cell_40.png` (64x64, indexed with the OBJ palette, 21 indices). Use only this file.
- I checked: the frame (outer 3 px) equals vanilla id 40; every index is in the OBJ palette; 37 and 89 are not in vanilla id 40 but other vanilla dialog portraits use them. Check this again yourself.

## Task

1. Add id 40 the same way r21 added id 65, without moving any r21 byte. Say how you fit a seventh frame with the allocator design (a further call, or an extension of the second call). If that design does not scale, say what the clean fix is, but do not change the shared `Allocator` in this build.
2. Status twin: say which status id pairs with 40 and what the status page shows now.
3. Where id 40 shows: every cutscene record (types 1-4, portrait byte at +3) and appearance entry with 40, with map and story point; label CONFIRMED or LIKELY. Say which one I can reach from my saves or states.
4. Tests: id 40 read back from the ROM equals the PNG pixel for pixel; id 65 and the other remaster portraits unchanged; the whole suite passes.

## Build

- Build `archive\builds\log2_poc_r22.gba` from the r21 list with the id 40 frame, no env vars. Do not add `file_select_dim`. Do not add the palette slot 172 change (a separate final decisions).
- Copy `log2_poc_r21.sav` and every `log2_poc_r21.ss*` to the r22 names. Never overwrite or edit the r21 files.
- Prove r22 differs from r21 only at the id 40 frame and its block word. List the diff regions.
- My test plan: the easiest scene from step 3.

## Parallel run

- An effects study writes only `scripts\one-time\2026-10-20-effects-trace\`. Do not touch it. I may edit files under `art\portrait-sources\remaster\anime\`; do not touch them.
- Bible rows in `scripts\one-time\2026-10-20-r22-build\bible_rows.md` (sections as in `scripts\one-time\2026-10-19-r21-build\bible_rows.md`). Do not edit `docs\RE-BIBLE.md`.

## Limits

- Never write under `data\`. Never overwrite a ROM, .sav or state file.
- Python: LF, no byte order mark, no em or en dashes. Never `cd` in any shell call (the r21 task did this six times; do not). Absolute paths only. A shell heredoc collapses backslashes: write files with Python, and check them for control characters. Tools installed with pip --user load with `py -3 -P`.
- Scripts in `scripts\one-time\2026-10-20-r22-build\`. Label findings CONFIRMED, LIKELY or SPECULATIVE.

## Report

Save it as `docs\tasks\2026-10-20-r22-build\r22-build-report.md`: the patch change, the id 40 users, the tests, the r22 SHA-1, the files copied, the diff proof and my test plan. Then reply with status, the r22 SHA-1, the test count and concerns only.

