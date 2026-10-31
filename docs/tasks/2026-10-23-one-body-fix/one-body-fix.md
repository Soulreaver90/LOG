# One-body fix pass: collar, head position, revert and step frames (final, 2026-10-23)

Personal GBA ROM hack (Legacy of Goku II, USA). Base: r32 (`builds\log2_poc_r32.gba`, SHA-1 `185dcc766e9a563270a74d5926426e98e412c02b`), built from `scripts\permanent\build_list.txt`. Tests: `py -3 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent` (559 OK on r32). Read first: `docs\tasks\2026-10-22-one-body\one-body.md` (the first brief) and `one-body-report.md` (what was built and its concerns), `scripts\permanent\art\gi_one_body.py`, `gi_post.py`, `gi_aura.py`, `hand_frames.py`, `frame_lock.py`, `tests\test_one_body.py`, and `docs\RE-BIBLE.md` rows tagged OBD.

## My rule and decisions

- Rule: Gohan's gi sets share one body. Set 157 (base) is the only body I edit; 158 (Super Saiyan) and 159 (Super Saiyan 2) are derived from it. "I am not going to hand edit 3 copies of the same body, just the base."
- **Faces (2026-10-23):** keep each form's own face, as `gi_ssj_v3` and `gi_ssj2_v3` have it. The Super Saiyan hair changes the forehead, so the head shapes differ.
- **Box keys (2026-10-23):** the 6 keys that need more than 32x32 (158: 4.1.3, 6.0.0, 7.0.0, 13.0.3; 159: 6.0.0, 7.0.0) stay as they are today.
- Exceptions kept as in v3: the SSJ2 idle (159 anim 0), the aura bolts, the vanilla-differs keys (anim 16 in both sets, 159 anim 4) until I decide.

## Task (change the pipeline step, then rerun it)

1. **Collar (report concern 2).** The form neck paints skin over the gi collar (111 px in 158, 159 px in 159; 18.0.2-18.0.6 worst). Rule: form pixels win only inside the form head (hair and face); everywhere else the base body wins. Define the head region so the face and the hair stay whole and the collar stays base. Show the before and after of the worst keys.
2. **Head position (concern 3).** Check the rows where the head moves 1-2 px against base from frame to frame (4 rows in 158, 7 in 159; 159 7.2.2 and 7.3.2 for the eyes). Where the move is a defect, anchor the head to base the same way across the row. Where vanilla itself bobs the head, keep it and say so.
3. **Revert and step frames (concern 5).** 158 anim 9 indices 1-3 (the step to SSJ2) keep their golden SSJ2 head, but take the base body of the same key. Anim 21 (revert, no base counterpart): find the base frame with the same body pose for each key, by shape. Derive where the match is clear, and list the rest for me with a side-by-side. Do not guess a pose.
4. **Tests (concern 6).** Make the one-body test cover the neck and collar rows, not only the rows below the head, and keep the exception lists explicit.

## Deliverable (no main-line build)

- New folders, never overwriting the old ones: `art\gi_ssj_v4\`, `gi_ssj2_v4\`, `gi_ssj2_aura_v4\`. The pipeline step writes v4 when run.
- Review sheets in `archive\2026-10-18-art-review-renders\one_body_v4\`: per anim, base 157 | v3 158 | v4 158 | v3 159 | v4 159 at 6x, plus a list of the keys that changed from v3 with pixel counts.
- Preview ROM `builds\log2_poc_r32_preview.gba`, built from `build_list.txt` with `LOG_GI_SSJ=gi_ssj_v4` and `LOG_GI_SSJ2=gi_ssj2_aura_v4`. Copy `log2_poc_r32.sav`, `.ss1`-`.ss5` and `log2_poc_r32_chamber2.sav` (as `log2_poc_r32_preview_chamber2.sav`), plus `log2_poc_r32_preview_chamber2.gba` (a byte copy). Use exclusive create. Prove the preview differs from r32 only in the 158/159 frame data and the records that point at it.
- The whole suite passes.

## Limits

- One task runs at a time; nothing else is running. Never write under `data\`. Never overwrite a ROM, .sav or state, or the art folders `gi_base`, `gi_ssj_v2`, `gi_ssj2_v2`, `gi_ssj2_aura`, `gi_rage_aura` and the v3 folders. Do not touch `art\portrait-sources\` or `art\hand-fixes\`. Never run `inject.py`.
- Art is judged by my eye: show, do not decide. Label findings CONFIRMED, LIKELY or SPECULATIVE.
- Python: LF, no byte order mark, no em or en dashes. Code style: a header block per file, short functions, precise names, 1-2 line comments for the non-obvious why only. Never `cd` in any shell call, not even for reads; absolute paths only. Write files with Python, never a heredoc. Tools installed with pip --user load with `py -3 -P`.
- Work scripts in `scripts\one-time\2026-10-23-one-body-fix\`. Bible rows in `scripts\one-time\2026-10-23-one-body-fix\bible_rows.md` with tag `OBF`, under `## Section N` headers. Do not edit `docs\RE-BIBLE.md`.

## Report

Save it as `docs\tasks\2026-10-23-one-body-fix\one-body-fix-report.md`: the head-region rule, the collar counts before and after, the head-position findings, the revert and step results, my list, the preview SHA-1, the diff proof and the tests. Then reply with status, the counts, my list size, the preview SHA-1 and concerns only.

