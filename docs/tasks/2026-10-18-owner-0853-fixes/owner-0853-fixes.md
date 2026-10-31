# My frame fixes: shared SSJ/SSJ2 body, golden torso per frame, pink pixels, review ROM r11 (final, 2026-10-18 8:53 AM)

Personal GBA ROM hack (Legacy of Goku II, USA). I am play-testing and reporting frame issues. Read first: the headers of `scripts\permanent\art\gi_art.py`, `scripts\permanent\art\gi_post.py`, `scripts\permanent\rom\rom_sheet.py`, `scripts\permanent\art\frame_lock.py`; reports `docs\tasks\2026-10-18-gi-rules-night\gi-rules-night-report.md`, `promote-chain-report.md`, `owner-0804-fixes-report.md`.

Pipeline today: `gi_art.py all` writes gi_base (set 157, from armor set 56), gi_ssj (158, from set 59), gi_ssj2 (159, from Rage set 58, with set 59 bodies for anims 9, 11, 12, 20, 21 that set 58 lacks). `gi_post.py all` puts the golden SSJ2 heads on gi_ssj2 (transplant), places the goldens, runs body rules R1/R2, writes gi_ssj2_v2, and makes the SSJ to SSJ2 step frames in gi_ssj_v2. The build reads gi_base, gi_ssj_v2, gi_ssj2_v2.

## Fix 1: SSJ2 uses the same gi body as SSJ (final decisions)

Me: "is there a reason why the body/gi differs between ssj1 and ssj2?" My finding: the armor bodies of sets 58 and 59 are almost the same in most poses, but the converter runs per form, so only 14 of 150 SSJ/SSJ2 gi body pairs are identical (compare by screen position, record dx/dy, rows from 5 above the sash down). I chose: one gi body per pose; only the hair differs.

1. For every key (anim, dir, index) of set 159: if the armor body of set 58 equals the armor body of set 59 at the same screen position (below the head; define the head boundary by rule and report it), the gi SSJ2 frame takes the gi SSJ body (gi_ssj, not the step frames of gi_ssj_v2), and the SSJ2 head goes on top as the transplant does now (hair over the body stays on top). Keys set 58 lacks already use the set 59 body, so they take the gi SSJ body too.
2. Where the armor bodies differ (the SSJ2 power-pose idle anim 0, the ki charge anim 4, and any other the comparison finds), keep the SSJ2 body as it is. List those keys.
3. Body rules R1/R2 must not split the two forms again: apply them to the shared body so SSJ and SSJ2 stay equal, or apply them to neither. The goldens of every form must pass the gate (frame_lock `check --golden` exit 0). Pick the option that keeps the goldens and report why.
4. The SSJ2 golden idle slots stay the goldens byte for byte.
5. Count after the fix: SSJ/SSJ2 body pairs identical, by the same screen-position compare. Every non-identical pair must be in the list of point 2.

## Fix 2: golden torso per frame, not per animation

Me: "Set 157 a4 back doesn't match the back gold standard." Anim 4 is the ki charge: frames 0 and 2 (arms down) have the idle pose, frames 1 and 3 raise the arms. The golden torso rule is all-or-none per (anim, dir), so all of anim 4 kept the old torso.

1. Apply the golden torso to each frame whose armor torso window equals the idle armor (the existing `torso_shift` test), whatever the other frames of that animation do. Two frames of the same pose get the same treatment, so nothing blinks.
2. Do the same for the strap rule if the same all-or-none choice blocks it.
3. All forms. Report every frame that gains the golden torso or the strap, per form. Verify 157 a4 d1 i0 and i2 equal golden base d1 in the torso rows by eye at 6x.

## Fix 3: pink pixels in SSJ2

Me: "set 159 a1d3 (or a1d2) there is a random pink pixel in the hair." OBJ indices 239 (248,32,224) and 240 (248,32,248) come from the Rage set 58 and sit in 10 gi_ssj2_v2 frames (1.2.1, 1.2.3, 1.3.1, 1.3.3, 4.2.1, 4.2.2, 4.3.1, 4.3.2, 16.2.1, 16.3.1). Remove them by rule: the pixel takes the most common non-zero 4-neighbour index, or 0 when it sits outside the outline. After fix 1 some may be gone already. Test: no 239 or 240 in any gi folder.

## Tool: individual frame export

Add `--frames <out_dir>` to `rom_sheet.py`: for each requested set, write every record as its own transparent PNG at 1x and 3x, named `<set>_a<anim:02>_d<dir>_i<index>.png` and `..._3x.png`, skipping dir 3 (dir 3 is dir 2 drawn with the OBJ h-flip bit; say so in the header). A test for names and the d3 skip.

## Build and export

1. `gi_art.py all`, `gi_post.py all`, `gi_review.py all`. Whole suite: `py -3 -I -m unittest discover -s scripts\permanent -p "test_*.py"` (151 OK today) plus your new tests.
2. New ROM `archive\builds\log2_poc_r11.gba`, no env vars: `py -3 -I scripts\permanent\log2_build.py --out archive\builds\log2_poc_r11.gba gohan_gi ssj2_form gohan_portraits status_bonus`. Copy `log2_poc_r10.ss1` to `log2_poc_r11.ss1`. Append the build line to `docs\build-log.md`.
3. r11 differs from r10 only in sets 157, 158, 159 frame data. Prove it.
4. Full review export from r11 into `archive\2026-10-18-art-review-renders\full_r11\`: per anim `a<NN>_base.png` (sets 56, 157) and `a<NN>_ssj_ssj2.png` (sets 59, 158, 159), all dirs, scale 4, skipping a set that lacks the anim. Individual frames into `archive\2026-10-18-art-review-renders\frames_r11\` with subfolders `armor_56`, `gi_base_157`, `armor_59`, `gi_ssj_158`, `armor_58`, `gi_ssj2_159`.
5. A before/after sheet of every frame fixes 1-3 change: `archive\2026-10-18-art-review-renders\r11_changes_<set>.png` (r10 row over r11 row). Look at all of them yourself at 4x or more.

## Limits

- Never write under `data\`. Never overwrite an existing ROM in `builds\`. Never edit `art\golden\golden_*.png`; `frame_lock.py check --golden` must exit 0 at the end.
- Do not touch `art\golden\work_r3\aura2\`.
- Python files: LF line ends, no byte order mark, no em or en dashes. Install nothing. Never `cd`; use absolute paths.
- Review images use background (191, 255, 7), never gray.

## Report

Save it as `docs\tasks\2026-10-18-owner-0853-fixes\owner-0853-fixes-report.md`: changes (file:line), the head boundary rule, keys that keep their own SSJ2 body, identical-pair count before and after, frames each fix changes per form, test count, r11 SHA-1, the r10 to r11 proof, the export paths. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with status, the r11 SHA-1, the test count and concerns only.

