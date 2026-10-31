# r21: the new Goku Super Saiyan dialog portrait, id 65 (final, 2026-10-19 7:30 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Base: r20 (`archive\builds\log2_poc_r20.gba`, SHA-1 starts `9b528334`; confirm the full value in `docs\tasks\2026-10-19-r20-build\r20-build-report.md`). Read first: `docs\RE-BIBLE.md` section 5a (portrait format, `portrait()` `@0x0800BDCC`, the raw type 0 frames and the live block `rom:0x894EAC` from `portrait_remaster`), the header and tests of `scripts\permanent\patches\portrait_remaster.py`, and `r20-build-report.md`.

## My ask

I finished a new Goku Super Saiyan portrait, made from an anime frame with our pipeline and my own finishing touches: "final". Put it in the game as dialog portrait id 65.

- Art: `art\portrait-sources\remaster\final_r21\goku_ssj_65.png` (64x64, indexed with the OBJ palette, 22 indices). Use only this file.
- Every index is in the OBJ palette `rom:0x1DA6C8`, so there is no palette change. Index 28 (248,184,184) is the lit skin. It is not one of vanilla id 65's colors, but 15 vanilla dialog portraits use it. Check that the frame pixels (outer 3 px) equal vanilla id 65's.

## Task

1. Add id 65 to `portrait_remaster` the same way it writes 63, 106, 115, 117 and 119: a raw type 0 frame `{0, 0x1000, data}` in free space, and the live block word for 65 repointed. Say whether the vanilla frame of id 65 becomes dead data and how big it is.
2. Status twin: say which status id pairs with 65 (if any) and what the status page shows now that `status_portrait` reads the dialog id. Do not generate a twin.
3. Where id 65 shows in the game: find every cutscene record (types 1-4, portrait byte at +3) and every appearance entry that uses 65. List them with their scene (map, story point) so I can find one to check. Label each CONFIRMED or LIKELY.
4. Tests: the id 65 frame read back from the ROM equals the PNG pixel for pixel; the other remaster portraits are unchanged; the existing suite passes.

## Build

- Build `archive\builds\log2_poc_r21.gba` from the r20 patch list with the extended `portrait_remaster`, no env vars. Do not add `file_select_dim`.
- Copy `log2_poc_r20.sav` to `log2_poc_r21.sav`, and every `log2_poc_r20.ss*` to the r21 name. Never overwrite or edit the r20 files.
- Prove r21 differs from r20 only at the id 65 frame and its block word. List the diff regions.
- My test plan: the scene from step 3 that is easiest to reach from my saves or states.

## Parallel run

- Nothing else is running. I edit only `docs\ledger\progress.md` and files under `scripts\one-time\2026-10-19-portrait-from-anime\anime\` while you run.
- Put bible rows in `scripts\one-time\2026-10-19-r21-build\bible_rows.md` (sections as in `scripts\one-time\2026-10-19-r20-build\bible_rows_sections.md`). Do not edit `docs\RE-BIBLE.md`.

## Limits

- Never write under `data\`. Never overwrite a ROM, .sav or state file.
- Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths. A shell heredoc collapses backslashes: write files with Python (no heredocs, no `sed -i`), and check them for control characters. Tools installed with pip --user load with `py -3 -P`, not `-I`.
- Scripts in `scripts\one-time\2026-10-19-r21-build\`. Label findings CONFIRMED, LIKELY or SPECULATIVE.

## Report

Save it as `docs\tasks\2026-10-19-r21-build\r21-build-report.md`: the patch change, the id 65 users, the tests, the r21 SHA-1, the files copied, the diff proof and my test plan. Then reply with status, the r21 SHA-1, the test count and concerns only.

