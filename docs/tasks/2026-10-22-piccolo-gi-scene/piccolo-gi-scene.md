# r29: new scene on Dende's Lookout, Piccolo gives Gohan the gi (final, 2026-10-22 8:40 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Base: r28 (`builds\log2_poc_r28.gba`, SHA-1 `eef01cf6aa37f660bbe0f07b87694d058252499c`), built from `scripts\permanent\build_list.txt`. Read first: `docs\tasks\2026-10-22-r28-build\r28-build-report.md` (sections on the chamber exit scene, the 34-record exit scene, flags 149-158, section 13 and `log2_poc_r28_chamber2.sav`), `cellgames-ssj-report.md` and `r27-build-report.md` (how records were inserted, grown and repointed), `r19-build-report.md` and `patches\rage_text.py` (a new text record), `docs\RE-BIBLE.md` sections 7-8 (scripts, cutscene record types, ext ops, text encoding, movement, facing, fades, flash, sound), and the patches `fullpower_ssj.py`, `npc_gi.py`, `gohan_gi.py`, `cutscene_portraits.py`.

## My storyboard, verbatim (final)

"Before the user gets control of Goku on Dende's lookout, both he and Gohan should already be ssj. Gohan will still be in armor.
There should be a transition (whatever the game has, a fade maybe) where Gohan approaches Piccolo on the lookout. This can be near the edge on the left side, Piccolo is standing, facing the right, and Gohan walks up to him from offscreen. The game uses quotes from the anime so here is the script:

Gohan: Piccolo, can I have a new outfit just like yours?
Piccolo: ...
Gohan: You were my first teacher
Piccolo: Yeah kid, it will make you look really sharp.

Piccolo raises his hands at Gohan, there is a bright blue flash.
Gohan is in the new gi, admiring it.

Gohan: Thank you, its awesome!
Goku walks in from off screen:
Goku: You look great Gohan

Then game cuts back to Goku playable."

My rulings (say if any cannot be met):
- Text: use the lines as written, with one fix: "its awesome" becomes "it's awesome" if the font has an apostrophe (check the text encoding; if not, keep "its"). Add no other words. Line-break each box the way the game's own boxes do.
- Looks and portraits per beat:
  - Gohan before the flash: armor Super Saiyan (set 59), armor Super Saiyan dialog portrait (find its id).
  - Gohan after the flash: gi Super Saiyan (set 158), portrait 115.
  - Goku: Super Saiyan (as r28 has him at that point), portrait 65.
  - Piccolo: his usual set and dialog portrait (94 or the one the game uses for him there).
- Where: the Lookout map of the chamber exit scene, near the left edge. Piccolo stands facing right. Gohan walks in from off screen to stand before him; Goku walks in from off screen at the end.
- The transition into the scene: the game's own fade (or the cut the scene already uses), before Gohan walks in. The cut back to playable Goku: the scene's existing end, so the game continues exactly as r28 does after this point (flag 158, "Journal Updated!", control as Goku).
- "Piccolo raises his hands": use the closest existing Piccolo animation (name it). "Bright blue flash": use the game's flash effect; if no blue flash exists, use the closest existing one and say what it looks like. "Gohan admiring it": use an existing pose or a short pause; say which.
- After this scene, every later appearance follows r28 (Gohan gi Super Saiyan through the stretch).

## Task

1. **Study (read-only first):** map the chamber exit scene records around the Lookout part: actors, positions, facing, the ops for walk-to, face, fade, flash, sound, wait, spawn and remove, and where Goku gains control. Two search shapes for any list you call complete.
2. **Design:** the exact records to insert, where, and how the scene grows (moved to free space and repointed, as r27 did). Text records with their encoding. If anything in the storyboard cannot be done with existing ops, stop at the design for that beat, build the rest, and list it.
3. **Build:** a new patch (your name for it) appended at the end of `build_list.txt` so no earlier byte moves. Build `builds\log2_poc_r29.gba` with `log2_build.py --list`. Copy `log2_poc_r28.sav`, every `log2_poc_r28.ss*`, and `log2_poc_r28_chamber2.sav` (as `log2_poc_r29_chamber2.sav`) to the r29 names. Never overwrite any ROM, .sav or state.
4. **Proof:** the r28 -> r29 diff touches only the expected sites (list them). Tests: the new records decode to the storyboard (text, portraits, sets), the scene list word points at the new record, the scene still reaches flag 158 and Goku control, and the whole suite passes.
5. **My test plan:** load `log2_poc_r29_chamber2.sav` slot 3 (with a ROM copy named to pair, `log2_poc_r29_chamber2.gba`), what I should see beat by beat.

## Parallel run

- A sprite task writes `archive\2026-10-22-gi-v3-preview\gi_ssj_v3\`, `gi_ssj2_v3\`, `gi_ssj2_aura_v3\`, `archive\2026-10-18-art-review-renders\one_body\`, `scripts\one-time\2026-10-22-one-body\`, `builds\log2_poc_r29_preview*`, and may edit `scripts\permanent\art\gi_post.py`, `hand_frames.py`, `frame_lock.py` and add a test file. Do not touch those. You write your new patch and its test file, `build_list.txt`, `docs\build-log.md` (one line), `scripts\one-time\2026-10-22-piccolo-gi-scene\`, and `builds\log2_poc_r29.*` / `log2_poc_r29_chamber2.*` only. Do not run `inject.py`.

## Limits

- Never write under `data\`. Python: LF, no byte order mark, no em or en dashes. Code style: a header block per file, short functions, precise names, 1-2 line comments for the non-obvious why only. Never `cd` in any shell call; absolute paths only. Write each file with Python. Tools installed with pip --user load with `py -3 -P`.
- Label findings CONFIRMED, LIKELY or SPECULATIVE. Bible rows in `scripts\one-time\2026-10-22-piccolo-gi-scene\bible_rows.md` (sections as in `scripts\one-time\2026-10-19-r21-build\bible_rows.md`). Do not edit `docs\RE-BIBLE.md`.

## Report

Save it as `docs\tasks\2026-10-22-piccolo-gi-scene\piccolo-gi-scene-report.md`: the study, the records inserted (with bytes), the substitutions for flash, raise-hands and admire, the r29 SHA-1, the files copied, the diff proof, the tests and my test plan. Then reply with status, the r29 SHA-1, the test count, the substitutions and concerns only.

