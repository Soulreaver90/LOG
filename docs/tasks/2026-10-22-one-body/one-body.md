# Pipeline: derive Gohan's Super Saiyan gi sets from the base body (final, 2026-10-22 7:30 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Current build: r28 (`builds\log2_poc_r28.gba`, SHA-1 `eef01cf6aa37f660bbe0f07b87694d058252499c`), built from `scripts\permanent\build_list.txt`. Read first: the headers of `scripts\permanent\art\gi_art.py`, `gi_post.py`, `gi_aura.py`, `hand_frames.py`, `frame_lock.py`, `patches\gohan_gi.py`, `patches\ssj2_idle.py`; `docs\RE-BIBLE.md` sprite and gi rows; the intake reports `docs\tasks\2026-10-18-r17-intake\r17-intake-report.md`, `r18-*`, `r19-build-report.md`, `shared-body-1240-report.md`, `gi-fix-1125-report.md`; and `art\base-audit\` (sets 157-160 exported from r28; each equals its art folder pixel for pixel).

## My rule, word for word

"Of course, that is the whole point, the body stays the same, only the hair and eye color changes, and the 'rage' stance that ssj2 has." And: "I am not going to hand edit 3 copies of the same body, just the base."

## The defect

Sets 158 (gi Super Saiyan, `gi_ssj_v2`) and 159 (gi Super Saiyan 2, `gi_ssj2_aura`) are converted on their own from the armor Super Saiyan frames, and my hand fixes were applied per folder. `hand_frames.HAND` gives `FLIGHT` (anim 20, 16 frames) and 13.0.0, 13.0.2 to `gi_base` only, so the Super Saiyan sets still show the old flat sash in world map flight and other errors. r28 keeps Gohan Super Saiyan from the chamber to Cell, so I see them.

## Requirement

1. **One body.** For every frame key of 158 and 159 that has a counterpart in 157 (same anim, dir, index): the frame is the 157 frame (the body I edit, including all its hand frames) with the form's head: hair and eye color. Set 157 is the single source; I edit only it.
2. **The head.** Take the form's hair from the current 158/159 frame of the same key (or its golden, where one exists), and recolor the eyes to the form's eye color. Handle a taller hair box: grow the frame box and keep the manifest geometry (dx, dy, w, h) consistent so the body stays where base has it. A frame box larger than 64x64 is not allowed; report any key that would need it.
3. **Exceptions, kept as they are today:** the SSJ2 "rage" idle stance of 159 (name the anims) and every aura bolt on 159 (`gi_aura.py` bakes bolts after the body; keep that order: base body -> derived SSJ2 body -> bolts). Set 160 (Rage, its own layout 58) is out of scope. The 3 SSJ->SSJ2 step frames of 158 anim 9 keep their golden SSJ2 head.
4. **Where vanilla itself differs.** Compare the armor sets (56 base, 59 SSJ, 58 SSJ2) below the neck for every key. Where vanilla's body poses differ between forms, do not force base: list those keys for me with a side-by-side, and keep today's frame until he decides.
5. **Goldens.** Where a locked golden of 158/159 (`frame_lock.py`) has a body that differs from base, my rule wins: derive it, and list each such golden with the pixel count changed, so I see what moved.
6. **Pipeline, not a hand copy.** Implement it as a step the pipeline runs (in `gi_post.py` or a new script it calls), so a future base edit flows to 158/159 on the next run. `hand_frames.HAND` for 158/159 keeps only head-only fixes (the boot gray r19 fix is a body fix: say how it carries now).

## Deliverable (no main-line build yet)

- New folders, never overwriting the current ones: `archive\2026-10-22-gi-v3-preview\gi_ssj_v3\`, `gi_ssj2_v3\`, `gi_ssj2_aura_v3\`.
- Review sheets for me in `archive\2026-10-18-art-review-renders\one_body\`: per anim, rows of base 157 | current 158 | new 158 | current 159 | new 159, at 6x; plus a list of changed keys with pixel counts, and the exception and vanilla-differs lists.
- A preview ROM: `builds\log2_poc_r29_preview.gba` built from `build_list.txt` with `LOG_GI_SSJ=gi_ssj_v3` and `LOG_GI_SSJ2=gi_ssj2_aura_v3`. Copy `log2_poc_r28.sav`, `log2_poc_r28_chamber.sav` (as `log2_poc_r29_preview_chamber.sav`) and every `log2_poc_r28.ss*` to the preview names. Prove it differs from r28 only in sets 158 and 159 frame data (and any geometry those frames need).
- Tests: a test that 158/159 equal 157 below the head mask for every non-exception key; the exception list is explicit in the test. The whole suite passes.

## Parallel run

- Nothing else is running. I may edit files under `art\portrait-sources\` and `art\hand-fixes\`; do not touch them. Do not run `inject.py`.

## Limits

- Never write under `data\`. Never overwrite a ROM, .sav or state file, or the current art folders `gi_base`, `gi_ssj_v2`, `gi_ssj2_v2`, `gi_ssj2_aura`, `gi_rage_aura`.
- Python: LF, no byte order mark, no em or en dashes. Code style: a header block per file, short functions, precise names, 1-2 line comments for the non-obvious why only. Never `cd` in any shell call; absolute paths only. Write each file with Python. Tools installed with pip --user load with `py -3 -P`.
- Work scripts in `scripts\one-time\2026-10-22-one-body\`. Label findings CONFIRMED, LIKELY or SPECULATIVE.
- Bible rows in `scripts\one-time\2026-10-22-one-body\bible_rows.md` (sections as in `scripts\one-time\2026-10-19-r21-build\bible_rows.md`). Do not edit `docs\RE-BIBLE.md`.

## Report

Save it as `docs\tasks\2026-10-22-one-body\one-body-report.md`: the method, the head rule, the exception list, the vanilla-differs list, the changed goldens, the counts, the preview SHA-1, the diff proof, the tests and the open points. Then reply with status, the counts, the lists' sizes, the preview SHA-1 and concerns only.

