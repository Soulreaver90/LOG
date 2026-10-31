# Portrait remaster test: base Vegeta (final, 2026-10-18 8:18 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Read first: `docs\tasks\2026-10-18-portrait-remaster-study\portrait-remaster-study-report.md` (the Goku study, its method, palette audit and Vegeta plan), the scripts in `scripts\one-time\2026-10-19-portrait-from-anime\`, `docs\research\re-portraits.md`, `docs\RE-BIBLE.md` section 5a.

## My verdict on the Goku study

"The portrait looks good, the hair is the one that is a bit odd, the lines don't match the hair that much, but everything else is much better. Would the task be able to do one for Vegeta base as a test?"

So: keep the skin, line and shadow approach. Fix the hair: highlight strokes must follow the hair's own strands and line art. A stroke sits inside one strand, runs along that strand's direction, and stops at its outline. No stroke crosses a strand line or floats in the black mass.

## Task

1. Base Vegeta dialog portrait, id 106 (status twin id 24, per the study). Unpack it from the USA ROM as an indexed PNG.
2. Repaint it by hand, row by row, by judgment, in the Goku study's style. Make version A (existing OBJ palette colors only) and version B (the same 6 new colors as Goku's B, no more). Every outline and drawing pixel stays unchanged; the script checks this, as in the Goku study.
3. Vegeta's hair: an upswept flame. Map its strands first (write the strand list with pixel ranges in your notes), then place highlights per strand. Do the same hair fix on Goku A and B (new files, keep the old ones).
4. Status twin: generate id 24 from your 106 with the existing pairing map. Show it.
5. Compare sheets at 4x on lime (191, 255, 7):
   - `art\portrait-sources\remaster\compare_vegeta.png`: OLD (ROM 106) | ours A | ours B | status twin from A.
   - `art\portrait-sources\remaster\compare_goku_v2.png`: OLD | example | old A | new A | new B.
   Look at both yourself and rate them honestly.

## Limits

- The RayenBox example is a style target only. Never copy, sample or trace its pixels. Online images are references only; save any download in `art\portrait-sources\remaster\refs\` with its URL, and never run anything you download.
- No ROM build, no patch, no change outside `art\portrait-sources\remaster\` and `scripts\one-time\2026-10-19-portrait-from-anime\`.
- Install nothing. Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths. A shell heredoc collapses backslashes: write files with Python, and check text files for control characters.

## Parallel run

- A save task edits `scripts\permanent\rom\log2_save.py`, `tests\test_save.py`, `test-data\saves\` and `scripts\one-time\2026-10-18-save-slots\`. I edit `art\hand-fixes\`. Do not touch them, `scripts\permanent\` or `builds\`.

## Report

Save it as `docs\tasks\2026-10-18-portrait-vegeta\portrait-vegeta-report.md`: the strand map, what changed, the checks, the compare paths and your honest rating. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with the compare paths and concerns only.

