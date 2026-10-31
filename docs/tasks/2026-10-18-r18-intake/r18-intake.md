# r18: third r12fix intake (2026-10-18 11:50 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Base: r17 (`archive\builds\log2_poc_r17.gba`, SHA-1 eee5eb35). Read first: `docs\tasks\2026-10-18-r17-intake\r17-intake-report.md` and `r12fix-intake-report.md` (the intake mechanism, goldens, lock, tests).

## Task: take in the new hand frames

1. Snapshot first: copy `art\hand-fixes\out\` and `edits.py` to `art\hand-fixes\snap_r18\`. Use only the snapshot.
2. Take in every `EDITS` key of the snapshot whose frame differs from its current golden or is new. Expected (verify against the snapshot, list any difference):
   - 158 and 159: 5.0.2, 8.0.3, 8.2.2, 16.2.1, 16.2.4, 12.0.0-12.0.3 (base fixes carried over with the new "delta" op in `fix.py`).
   - 159.1.2.0: now with the r13 aura bolts (r17 concern 1).
3. Use the same mechanism as r17: new golden files for changed keys; never edit an existing `golden_*.png`. Every opaque pixel is an exact OBJ palette color; each frame keeps its record size. Stop and report on any mismatch.
4. List the dir 3 records that share a listed key's frame, as before.
5. Move the r16 baseline of the hand frame test to r17.
6. No patch change. Do not add `patches\file_select_dim.py` to the build list; it waits for me.

## Build

- Build `builds\log2_poc_r18.gba` from the r17 patch list, no env vars.
- Copy `log2_poc_r17.sav` to `log2_poc_r18.sav`. Do NOT create `log2_poc_r18.ss1`. Never overwrite. Append the build line.
- Prove it from the ROM: every listed key equals its snapshot frame pixel for pixel, every other record of sets 157-160 equals r17, and r18 differs from r17 only in frame data. List the diff regions.
- Review sheet `archive\2026-10-18-art-review-renders\r18_intake.png` (r17 row over r18 row, every listed key, 6x, lime). Look at it.

## Parallel run

- A disassembly task writes only `scripts\one-time\2026-10-18-disasm-study\`, its report and rows in `docs\RE-BIBLE.md`. Do not edit `docs\RE-BIBLE.md`; put any bible rows in your report.
- I may edit `art\hand-fixes\` (live folder). Read only your snapshot. Do not edit `fix.py`, `view.py` or `edits.py`.
- Run your own tests while you work and the whole suite once before the build, from the `scripts\permanent` root.

## Limits

- Never write under `data\`. Never overwrite a ROM or .sav. Never edit an existing `golden_*.png`.
- Install nothing. Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths. Review images on (191, 255, 7).
- A shell heredoc collapses backslashes. write files with Python (no heredocs, no `sed -i`), and check text files for control characters.
- Use your own scratch folder `scripts\one-time\2026-10-18-r18-intake\` for scripts.

## Report

Save it as `docs\tasks\2026-10-18-r18-intake\r18-intake-report.md`: the key list, the golden changes, the test count, the r18 SHA-1, the ROM proof and the review path. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with status, the r18 SHA-1, the test count and concerns only.

