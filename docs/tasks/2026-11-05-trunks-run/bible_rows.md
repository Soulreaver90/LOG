# Bible rows from the Trunks down run pose read, 2026-11-05

Merge into `docs\RE-BIBLE.md`. Tag: `TDR`.
Source: `docs\tasks\2026-11-05-trunks-run\pose.md` and `regions.txt`, both built from the vanilla frames
of set 128 anim 13 dir 0 and checked against set 134 and the owner's approved tank idle.

## Section 4

| Fact | Tags | Label | Tag |
|---|---|---|---|
| Set 128 anim 13 dir 0 is the DOWN RUN, four frames, headers `rom:0x357690`, `rom:0x357784`, `rom:0x35788C`, `rom:0x35797C`, all 16x32 with dx 0. The head sits 4 rows below its idle row in frames 0 and 2 and 2 rows below in frames 1 and 3. That bob names the phases with no guesswork: 0 and 2 are the foot contacts, 1 and 3 are the airborne passes, which is also why 0 and 2 are the closest pair at 98 differing pixels | #sprite set:128 | C (frame grids) | TDR |
| Three masses in the down run are not what they look like, and no colour rule separates any of them. The wide black mass at rows 27 to 31 is the BOOTS, black with a gold cuff, and the idle and the walk carry the same shape. The brown flanking the face at the eye rows is the FACE, shaded dark at its edges: it is identical in the idle, and it stays skin in set 134 where the hairline one row above turns gold. The grey at the upper left is the SWORD HILT over his shoulder, which the owner's approved tank idle already draws | #sprite #palette set:128 set:134 | C (compared against the idle and set 134) | TDR |
| In the down run the two arms travel one oval each, half a cycle apart: up and out to its own side, then down and across the body. The hand that is forward crosses the body centre and reads LOW, and the hand that is back reads HIGH and out past the head. Frames 0 and 2 hold mirrored POSES but are NOT mirrored pixels: flipped, frame 0 differs from frame 2 by 167 px against 98 px unflipped, so no frame may be made by flipping another | #sprite set:128 | C (region maps, all four frames) | TDR |
| In all four down run frames, rows 21 to 24 hold ZERO jacket-over-torso pixels. The forward forearm crosses the belly, so that entire band is sleeve, and the torso is only 3 or 4 pixels in a contact frame and 7 in a pass frame, all at rows 17 to 20. For an outfit swap this means the band is a bare ARM, not chest and not bulk. Filling it with the garment body deletes the forward arm, which is the error the owner rejected twice | #sprite set:128 | C (region maps) | TDR |
| A lit cylinder is how a limb reads under a garment: a lighter band (`4F`, `50`) with the darkest shade (`51`) on both sides of it. In down run frame 0 that band runs from (11,21) through (10,22) to (9,23) and into the bare fist, which is what proves the forearm is drawn OVER the belly and so is in FRONT of the body. An arm behind the body cannot be drawn over the belly | #sprite #palette set:128 | C (frame grid) | TDR |

## Section 11

| Fact | Tags | Label | Tag |
|---|---|---|---|
| `scripts\permanent\rom\show_regions.py` draws a hand written region map back over its frames in up to four panels: the sprite, the naming, body against gear, and the joints. It was promoted out of `scripts\one-time\2026-11-01-trunks-side-walk\` on 2026-11-05 so it runs on any set. The regions file now carries its own `#png`, `#palette` and `#bone` lines, so one file holds the frames, the lettering and the skeleton. Its coverage report is a TRANSCRIPTION check only: it proves every lit pixel has a letter and no dead pixel does, and it cannot tell you an arm is really a scabbard | #tool #sprite | C | TDR |
