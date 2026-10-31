# r17: second r12fix intake plus a slower idle aura (final, 2026-10-18 8:24 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Base: r16 (`archive\builds\log2_poc_r16.gba`, SHA-1 1adfa726). Read first: `docs\tasks\2026-10-18-r12fix-intake\r12fix-intake-report.md` (the r15 intake: `hand_frames.py`, goldens, lock, tests), `docs\tasks\2026-10-18-npc-gi\npc-gi-report.md` (r16), the header of `scripts\permanent\patches\ssj2_idle.py`.

## Task 1: take in the new hand frames

1. Snapshot first: copy `art\hand-fixes\out\` and `edits.py` to `art\hand-fixes\snap_r17\`. I keep editing the live folder. Use only the snapshot.
2. Take in every `EDITS` key of the snapshot whose frame differs from its r15 golden or is new. Expected new or changed keys (verify against the snapshot, list any difference):
   - 159.1.0.0, 159.1.0.2, 159.13.0.3: the r13 aura bolts laid back over the hand fix (op "bolts").
   - 157.16.2.1.
   - 157.1.2.0, 158.1.2.0, 159.1.2.0: side walk arm, shoulder and back shoe.
   - 157.20.d.i for d 0-3, i 0-3: world map flight (anim 20).
3. Use the r15 mechanism (`hand_frames.py`, goldens, `frame_lock.py --golden`). New goldens are new files. A changed key gets a new golden file; never edit an existing `golden_*.png`. Say how a changed key replaces its r15 golden.
4. Each frame: every opaque pixel is an exact OBJ palette color, and each frame keeps its record size. Stop and report on any mismatch.
5. Check the dir 3 records of anim 20 and of every new key: if one shares a listed key's frame, list it as in r15. Anim 20 has its own dir 3, so it should not share.
6. Move the baseline of `test_hand_frames.test_no_other_key_differs_from_r14` to r16 (rename it), as the r15 report said.

## Task 2: slower idle aura

- "the electricity at idle is a bit fast". In `patches\ssj2_idle.py`, the idle shape index uses `(tick >> 2) % 3`, one shape per 4 frames (67 ms). Change it to `(tick >> 3) % 3`, one shape per 8 frames (133 ms). The `lsr r2,r2,#18` becomes `#19`.
- Check the divide-by-3 range note in the header (`tick >> 2 < 0x4000`) still holds for the new shift, update the notes, and update or add tests (the instruction bytes, and the shape sequence for a few tick values).
- Walk and run bolts are baked into the step frames. Do not change them.

## Build

- Build `archive\builds\log2_poc_r17.gba` from the r16 patch list, no env vars.
- Save: if `test-data\saves\log2_lv40_cellgames_v2.sav` exists at build time, copy it to `log2_poc_r17.sav`. Otherwise copy `log2_poc_r16.sav` and say so. Do NOT create `log2_poc_r17.ss1`: the r12-r16 state files are one stale state (47f898f3) whose RAM holds the old post-Cell slots. Never overwrite. Append the build line.
- Prove it from the ROM: every listed key equals its snapshot frame pixel for pixel, every other record of sets 157-160 equals r16, and r17 differs from r16 only in frame data and the idle hook's shift byte. List the diff regions.
- Review sheet `archive\2026-10-18-art-review-renders\r17_intake.png` (r16 row over r17 row, every listed key, 6x, lime). Look at it.

## Parallel run

- A save task edits `scripts\permanent\rom\log2_save.py`, `tests\test_save.py`, `test-data\saves\` and `scripts\one-time\2026-10-18-save-slots\`. A portrait task works in `art\portrait-sources\remaster\` and `scripts\one-time\2026-10-19-portrait-from-anime\`. Do not touch them.
- I edit `art\hand-fixes\` (live folder). Read only your snapshot. Do not edit `fix.py`, `view.py` or `edits.py`.
- Run your own tests while you work and the whole suite once before the build, from the `scripts\permanent` root. Report any failure in another task's files; do not fix it.

## Limits

- Never write under `data\`. Never overwrite a ROM or .sav. Never edit an existing `golden_*.png`.
- Install nothing. Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths. Review images on (191, 255, 7).
- A shell heredoc collapses backslashes. write files with Python, and check text files for control characters.
- Use your own scratch folder `scripts\one-time\2026-10-18-r17-intake\` for scripts.

## Report

Save it as `docs\tasks\2026-10-18-r17-intake\r17-intake-report.md`: the key list, the golden changes, the idle change (file:line, bytes), the test count, the r17 SHA-1, which save r17 got, the ROM proof and the review path. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with status, the r17 SHA-1, the test count and concerns only.

