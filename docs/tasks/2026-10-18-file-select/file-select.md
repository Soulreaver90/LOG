# File select: unselected slots draw a wrong gi Gohan (final, 2026-10-18 8:14 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Read first: `docs\RE-BIBLE.md` (sprite, palette, save and menu rows), `docs\research\re-overview.md`, `docs\research\re-save-format.md`, `docs\tasks\2026-10-18-save-slot3\save-slot3-report.md` (file select load path `0x08003F9C`, slot loop `0x080019EE`), the headers of `scripts\permanent\patches\gohan_gi.py` and `scripts\permanent\rom\rom_sheet.py`, `scripts\permanent\rom\thumb_dis.py`.

## My report

Screenshot (pasted in chat). The file select shows three slots, each with Gohan and Piccolo. The selected slot shows the current gi Gohan correctly. The unselected slots show "a weird version of our gi, looks like one of the earlier sprites we built": a large orange V on the chest, dark purple shoulders, a darker face. Piccolo looks the same in all slots.

## Task

1. Trace how the file select draws a slot's characters: which set, anim, dir and frame for selected and unselected slots, which palette (256-color OBJ or 16-color banks, palette RAM writes, blending registers), and any software remap of pixel indices (for example a dim table that maps each index to a darker index).
2. Find why our gi looks wrong only when unselected. Candidates, each to prove or rule out with evidence:
   - a remap or dim table whose entries for the indices our gi uses (87-89, 211, 26-27, 34-35, 72, 195, 113-117 and others) point to unrelated colors;
   - a separate frame, set or graphic for the file select, built by an earlier converter or never converted;
   - a different palette bank.
   Vanilla armor Gohan in the same screen must look right; explain why.
3. Propose the smallest fix and its blast radius (what else reads the same table or frame). Write it as a new patch file in `scripts\permanent\patches\` (style of the others: `_expect` checks, `apply(rom, alloc)`, notes) with tests, but do NOT add it to the build list and do not build a ROM. I take it into the next build.
4. Render proof: an image of the unselected-slot Gohan as the game draws it now and as it will draw it after the fix, using your model of the remap. Save it as `archive\2026-10-18-art-review-renders\file_select_fix.png` on lime (191, 255, 7). Look at it.

## Parallel run

- An intake task builds r17. It edits `scripts\permanent\art\gi_art.py`, `gi_post.py`, `gi_aura.py`, `frame_lock.py`, `hand_frames.py`, `patches\ssj2_idle.py`, their tests, `art\` and `builds\`. Do not touch them. A portrait task works in `art\portrait-sources\remaster\` and `scripts\one-time\2026-10-19-portrait-from-anime\`.
- Your files: your new patch file, its new test file, `scripts\one-time\2026-10-18-file-select\`, the review image, your bible rows. Run only your own tests while you work and the whole suite once at the end, from the `scripts\permanent` root.

## Limits

- Read ROMs only. Never write under `data\`. Never overwrite a ROM or .sav. Install nothing.
- Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths. A shell heredoc collapses backslashes: write files with Python (no heredocs, no `sed -i`), and check them for control characters.
- Label findings CONFIRMED, LIKELY or SPECULATIVE. If you cannot trace a piece, say so and do not guess.
- Add bible rows for each new confirmed fact in `docs\RE-BIBLE.md`, tagged. Add only your own rows.

## Report

Save it as `docs\tasks\2026-10-18-file-select\file-select-report.md`: the draw path with addresses, the cause, the fix and its blast radius, the patch file and test count, the proof image path. Then reply with status, the cause in one line, the test count and concerns only.

