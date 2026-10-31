# Base gi Gohan (set 157): frame-by-frame review and redraw against the armor frames (final, 2026-10-23)

Personal GBA ROM hack (Legacy of Goku II, USA). Current build: r33 (`builds\log2_poc_r33.gba`). Read first: the headers of `scripts\permanent\art\gi_art.py`, `gi_post.py`, `hand_frames.py`, `frame_lock.py`, `log2_sprites.py`; `docs\tasks\2026-10-18-r17-intake\r17-intake-report.md` (how my hand frames in `art\hand-fixes\` are taken in); `docs\RE-BIBLE.md` sprite rows for sets 56, 157 and the gi.

## My instruction, verbatim

"No need to change the sprite size, the issue is the frames are poorly drawn in many of them. This is what should be done. You review each base frame, compare to the armor version. The golden master are the ones I've drawn and approved. Hands should have the blue wrist, chest should have the V chest exposed if possible and makes sense, feet should be the brown shoes and must not be long like the armor boots. Also run the frames and animations yourself to see the context of what is being done, like a kick, to help determine what should be what. ASK or put all question frames in a folder so I can highlight or answer questions."

Defects I already found (all from the armor-to-gi conversion): flight anim 20 has the limb colors swapped (trailing legs painted as skin arms with wristbands, forward arms painted as purple pants and brown boots); anim 12 side views lack the sash and have a hand with a blue wrist in the middle of the body; anim 16 and 18 feet look cut or wrong; anim 11 had stray hair. "There are too many issues to list."

## The gi look (the target)

- **Golden masters:** the frames I drew and approved: the `frame_lock.py` goldens for set 157 and the `hand_frames.HAND` frames for `gi_base` (list them by key in the report). They are the style reference. Never change one. If a golden breaks a rule below (the flight frames may), do not touch it: put it in the questions folder.
- **Hands:** skin, with the blue wristband at the wrist.
- **Chest:** the V of exposed chest at the gi collar, where the pose shows the front and it makes sense at this size.
- **Feet:** the brown shoes, short. Never the long armor boots.
- **Clothes:** purple gi top and pants, the red sash at the waist, as on the goldens.
- **Which limb is which:** decide from the armor frame (set 56: gloves and boots are both white, so read the pose), the animation in motion, and what the move is (a kick extends a leg, a punch an arm). Never decide a limb from color position alone.

## Method (per frame, by eye; no rule passes on art)

1. For every anim of set 157, and every dir and index, export the armor frame (set 56, same key) and the current base frame (`art\gi_base\`).
2. **Run the animations:** make GIFs per anim and dir with the game's own timing, side by side: armor 56 | current 157. Watch them before you judge any frame of that anim, and write one line on what the move is.
3. Review each frame against the armor frame, the animation and the goldens. Where it is wrong, redraw it by hand, pixel by pixel, keeping the gi palette indices the goldens use. Keep the pose, the outline and the frame box of the current frame; the size does not change.
4. Where you are not sure (which limb, whether a V chest makes sense, whether a cut-off foot is drawn that way in the armor frame), do not guess: make a question frame.

## Output (no ROM, no change to `gi_base`, `hand_frames.py` or any pipeline script)

- Proposed frames: `art\base-audit\proposed\157_a{anim}_d{dir}_i{idx}.png`, the same format and palette as `art\hand-fixes\out\`, so the approved ones can go through the existing hand-frame intake. Only frames you changed.
- Review sheets for me, one per anim: `art\base-audit\sheets\anim_NN.png`, rows per key: armor 56 | current 157 | proposed 157 | changed-pixel overlay, at 6x, with the key, a one-line note of what changed, and "golden" on golden keys.
- Animations: `art\base-audit\gifs\anim_NN_dD.gif`: armor | current | proposed, game timing, 4x.
- Questions: `art\base-audit\questions\`: one PNG per question, `qNNN_157_aA_dD_iI.png`: armor | current | proposed (if any) at 8x with a 1 px grid, large enough to mark up; plus `questions.md`, numbered, one short question per item, naming the pixel area. Golden conflicts go here.
- Keep a running log `art\base-audit\log.md` per anim (move, keys reviewed, changed, questioned), so a successor can continue if you stop.

## Limits

- One task runs at a time; nothing else is running. Never write under `data\`. Never overwrite any file under `art\` except inside `art\base-audit\`. Do not build a ROM. Never run `inject.py`.
- Sets 158 and 159 are out of scope now: they are derived from base after I approve. Do not touch them.
- Python: LF, no byte order mark, no em or en dashes. Code style: a header block per file, short functions, precise names, 1-2 line comments for the non-obvious why only. Never `cd` in any shell call, not even for reads; absolute paths only. Write and edit files with the Write and Edit tools, never `sed -i` or a heredoc. Work scripts in `scripts\one-time\2026-10-23-base-audit\`. Tools installed with pip --user load with `py -3 -P`.
- Art is judged by my eye. Label technical findings CONFIRMED, LIKELY or SPECULATIVE.

## Report

Save it as `docs\ledger\base-audit-report.md`: the goldens list, per anim the move, the keys reviewed, changed and questioned, the question count, and anything you could not cover. Then reply with the counts, the question count and concerns only.

