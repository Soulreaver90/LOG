# Portrait remaster: Gohan Super Saiyan and Super Saiyan 2 (final, 2026-10-18 8:31 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Read first: `docs\tasks\2026-10-18-portrait-remaster-study\portrait-remaster-study-report.md` and `portrait-vegeta-report.md` (method, palette audit, strand rule, checks), the scripts in `scripts\one-time\2026-10-19-portrait-from-anime\`, the header and notes of `scripts\permanent\patches\gohan_portraits.py` (which portrait ids are Gohan's, which art this hack made, how the status twins are paired), `docs\research\re-portraits.md`, `docs\RE-BIBLE.md` section 5a.

## My ask

"Gohan SSJ2 and SSJ need the same treatment as Goku. For some reason they have the odd skin tone and it's very bare of any coloring or contrast, basically flat."

I chose version A: existing OBJ palette colors only. No new colors, no palette change.

## Task

1. List every Gohan dialog portrait id in the current build (`archive\builds\log2_poc_r16.gba`): base, SSJ, SSJ2, Rage, armor and gi, and which ones this hack made. Unpack the SSJ and SSJ2 gi dialog portraits (and base gi, for reference) as indexed PNGs.
2. Say why SSJ and SSJ2 look flat: count their skin shades and contrast against Goku 63 and vanilla Gohan portraits. Find the cause (for example a color remap in `gohan_portraits.py`).
3. Repaint SSJ and SSJ2 by hand in the Goku study's style, version A only:
   - anime skin tones with a clear light, mid and shadow ramp, the same as Goku's A;
   - hard cel shadows: under the eyes, under the chin, the side of the face away from the light;
   - the darker line color where the Goku A used it;
   - Super Saiyan hair: gold with its own highlights and shadows. Shading follows each strand and stops at its outline (the strand rule from the Vegeta report). No stroke floats or crosses a strand line.
   - Every outline and drawing pixel stays unchanged; the script checks this.
   SSJ and SSJ2 must read as the same person with the same skin and lighting.
4. Base gi Gohan: compare it with your SSJ result. If its skin and shading clearly mismatch, make a base version too, the same way, and say why.
5. Status twins: generate each status portrait from your dialog art with the existing pairing map. Show them.
6. Compare sheet `art\portrait-sources\remaster\compare_gohan.png` at 4x on lime (191, 255, 7): one row per form, columns OLD | ours A | status twin. Add Goku A in the corner as the style reference. Look at it yourself and rate it honestly.

## Limits

- No ROM build, no patch. Write only in `art\portrait-sources\remaster\` and `scripts\one-time\2026-10-19-portrait-from-anime\`. Do not touch `scripts\permanent\`, `builds\`, `art\hand-fixes\`, `art\golden\` or `art\gi_*`.
- Install nothing. Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths. A shell heredoc collapses backslashes: write files with Python (no heredocs, no `sed -i`), and check text files for control characters.

## Parallel run

- An intake task is building r17. It edits `scripts\permanent\`, `art\` (except the remaster folder), goldens and `builds\`. Stay out of them.

## Report

Save it as `docs\tasks\2026-10-18-portrait-gohan\portrait-gohan-report.md`: the id list, the cause of the flat look, what changed per portrait, the checks, the compare path and your honest rating. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with the compare path and concerns only.

