# Take my r12fix frames into the build: r15 (final, 2026-10-18 6:24 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Base: r14 (`archive\builds\log2_poc_r14.gba`, SHA-1 94d3028d, 239 tests OK). Read first: the headers of `scripts\permanent\art\gi_art.py`, `gi_post.py`, `frame_lock.py`, `patches\gohan_gi.py`, and how my walk frames were taken in (`art\golden\owner\base_gi\a1_0948\ingest.py`, the goldens `golden_gi_base_a1_d0_i0..3.png`, `docs\tasks\2026-10-18-owner-0948-walk\owner-0948-walk-report.md`).

## Why

I play-tested r14 and saw the old r12 flying frame. The hand-fixed frames live only in `art\hand-fixes\` (`edits.py` lists them, `fix.py` writes `out\<set>_aNN_dD_iI.png`, 1x RGBA in the ROM OBJ palette colors). I review them there and wants them in game.

## Task

1. Snapshot first: copy `art\hand-fixes\out\` and `edits.py` to `art\hand-fixes\snap_r15\`. I keep editing the live folder. Use only the snapshot. Take every key of `EDITS` in the snapshot `edits.py`. List any `out\` file that is not in `EDITS`, and leave it out.
2. Each frame to palette indices: every opaque pixel must be an exact OBJ palette color of r14 (`log2_sprites.PALETTE_OFF`). Stop and report on any color that is not. Each frame must keep the size of its r12 record (159 frames are 32x32).
3. Take them in so they survive a regeneration (`gi_art.py all`, `gi_post.py all`): the way my walk frames are taken in (locked goldens placed by key), extended to any (form, anim, dir, index). A hand fix to the art folders alone is not enough, because the next run reverts it. Lock them with `frame_lock.py` (the `--golden` set grows by these names) and report how.
4. Regenerate, run the whole suite plus new tests (each listed key in the art folder equals its snapshot frame; no other key changed against r14's art), and `frame_lock.py check --golden` exits 0.
5. Build `archive\builds\log2_poc_r15.gba`, no env vars, the r14 patch list. Copy `log2_poc_r14.sav` and `.ss1` to the r15 names (never overwrite). Append the build line.
6. Prove it from the ROM: `rom_sheet.py --frames` on r15. Every listed key's record equals its snapshot frame pixel for pixel. Every other record of sets 157-160 equals r14. r15 differs from r14 only in frame data (and the table words that point at it). List the diff regions.
7. Review: `archive\2026-10-18-art-review-renders\r15_intake.png` (r14 row over r15 row, every listed key, 6x, lime). Look at it.

## Parallel run

- I edit `art\hand-fixes\edits.py` and `out\` while you work. Read only the snapshot.
- Do not edit `fix.py`, `view.py` or `edits.py`.

## Limits

- Never write under `data\`. Never overwrite a ROM or .sav. Never edit the existing `golden_*.png` files.
- Install nothing. Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths. Review images on (191, 255, 7).
- A shell heredoc collapses backslashes. write files with Python, and check text files for control characters.
- Use your own scratch folder `scripts\one-time\2026-10-18-r12fix-intake\` for scripts. Never run a script from a shared scratchpad that you did not write.

## Report

Save it as `docs\tasks\2026-10-18-r12fix-intake\r12fix-intake-report.md`: the key list, the intake mechanism (file:line), lock change, test count, r15 SHA-1, the ROM proof, the review path. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with status, the r15 SHA-1, the test count and concerns only.

