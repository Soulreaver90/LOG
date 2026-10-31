# Portrait remaster v2: softer shading, version A only (final, 2026-10-19 7:31 AM)

Personal GBA ROM hack (Legacy of Goku II, USA). Read first: `docs\tasks\2026-10-18-portrait-remaster-study\portrait-remaster-study-report.md`, `portrait-vegeta-report.md`, `portrait-gohan-report.md`, and the scripts in `scripts\one-time\2026-10-19-portrait-from-anime\`.

## My verdict (verbatim)

"I think they are great! My only complaint is that the contrast between the colors, even with the Goku, is a bit strong. I want them to have shading, not appear like they are under studio lighting. With that said, I prefer OBJ for all of them."

So:
- Version A only (existing OBJ palette colors). Drop B.
- Keep the approach and the shapes: the cel shadow placement, the strand-following hair, the unchanged line art.
- Lower the contrast. The lit side and the shadow side sit closer in value. Use neighbouring steps of each ramp (light to mid, mid to shadow), never a jump that skips a step. The lit side should read as the character's normal skin, not a pale or yellowish highlight. Shadows stay as clear shapes, but softer and, where it reads better, a little smaller. Hair highlights the same: present, not glaring.
- No status twin. I want the same art on the dialog and status screens; a second task solves the status screen. Paint only the dialog art.

## Task

1. Portraits: Goku 63 (start from the new strand-hair A), Vegeta 106 (A), Gohan SSJ 115, SSJ2 117 and base gi 119 (A). I approved the Gohan set, including the base proposal.
2. For each, write a soft version as a new indexed PNG (keep every earlier file). The line art check stays: every outline and drawing pixel is unchanged. Only OBJ palette indices that USA dialog portraits already use.
3. Measure the change: per portrait, the value (luma) gap between the main lit skin and the main shadow skin, before (current A) and after. Aim to roughly halve the gap of the current A, and report the numbers.
4. Keep one light per drawing as before. For 115 and 117, keep each drawing's own lit side (I did not object).
5. Compare sheet `art\portrait-sources\remaster\compare_soft.png` at 4x on lime (191, 255, 7): one row per portrait, columns OLD (ROM) | current A | soft A. Look at it yourself and rate it honestly against my words.

## Limits

- No ROM build, no patch. Write only in `art\portrait-sources\remaster\` and `scripts\one-time\2026-10-19-portrait-from-anime\`.
- Install nothing. Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths. A shell heredoc collapses backslashes: write files with Python (no heredocs, no `sed -i`), and check text files for control characters.

## Parallel run

- A status screen task works in `scripts\one-time\2026-10-19-status-portrait\`, writes one new patch file and its test in `scripts\permanent\`, and reads your remaster folder. Do not touch its files. Do not edit `docs\RE-BIBLE.md`; put any bible rows in your report.

## Report

Save it as `docs\tasks\2026-10-19-portrait-soft\portrait-soft-report.md`: the file list, the luma gap table, what changed per portrait and your honest rating. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with the compare path and concerns only.

