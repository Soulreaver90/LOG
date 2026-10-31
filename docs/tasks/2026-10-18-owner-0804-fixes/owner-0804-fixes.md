# Two approved fixes and review ROM r10 (final, 2026-10-18 8:04 AM)

Personal GBA ROM hack (Legacy of Goku II, USA). Read first: `scripts\permanent\art\gi_post.py` (`body_rules`), `scripts\permanent\patches\status_bonus.py` (`BONUS_TEXT`), `docs\tasks\2026-10-18-gi-rules-night\gi-rules-night-report.md` concern 1, `docs\tasks\2026-10-17-status-gold\status-gold-report.md`.

## Fix 1: status text shows the live value

I chose "120" (the live value alone), not "100+20". Set `BONUS_TEXT = "live"` in `status_bonus.py`. Update the tests that pin the text, the header and the RE-BIBLE row. I approved the gold rows as built (`GOLD_ROWS` 58/69/34): keep them.

## Fix 2: SSJ2 arm line (bodyfix R2) with my chest kept

`body_rules` applies nothing today because rule R2 (a gi pixel beside the arm outline 23 becomes 211) would change my SSJ2 front golden pixel (12, 19) from 89 to 211, and the golden gate then refuses every change. I approved the proposed fix: exempt the image-left armpit row from R2, so the golden gate passes and R1 and R2 apply again.

1. Prove which row and side the exemption must cover on all three SSJ2 goldens (d0, d1, d2). Define the armpit row by a rule (for example: the first gi row below the shoulder, on the image-left side, in front views), not by a fixed coordinate. Quote the pixels.
2. The golden gate must then print zero changes for every golden, and `body_rules` applies again. Report the frames and pixel counts it changes (the night report said about 130 px in 70 frames before the exemption).
3. Keep the 12 goldens byte-identical: `py -3 -I scripts\permanent\art\frame_lock.py check --golden` must exit 0.
4. Tests in `scripts\permanent\tests\test_gi_post.py`: the gate passes on all goldens; R2 changes a synthetic arm-line case; R2 leaves the exempt armpit pixel alone.

## Build

1. `py -3 -I scripts\permanent\art\gi_art.py all`, then `py -3 -I scripts\permanent\art\gi_post.py all`, then `py -3 -I scripts\permanent\art\gi_review.py all`.
2. Run the whole suite: `py -3 -I -m unittest discover -s scripts\permanent -p "test_*.py"` (149 OK today).
3. Build the new path `archive\builds\log2_poc_r10.gba` with no env vars: `py -3 -I scripts\permanent\log2_build.py --out archive\builds\log2_poc_r10.gba gohan_gi ssj2_form gohan_portraits status_bonus`. Copy `log2_poc_r9.ss1` to `log2_poc_r10.ss1`. Append the build line to `docs\build-log.md`.
4. Prove what differs from r9: only set 159 frame data (fix 2) and the status text code or data (fix 1). Use `scripts\permanent\rom\rom_sheet.py` to render set 159 anims 0, 1, 4 on r9 and r10 side by side into `archive\2026-10-18-art-review-renders\r10_armline.png`, and look at it yourself.

## Limits

- Never write under `data\`. Never overwrite an existing ROM in `builds\`. Never edit `art\golden\golden_*.png`. Do not touch `art\golden\work_r3\aura2\` (I am drawing there).
- Python files: LF line ends, no byte order mark, no em or en dashes. Install nothing. Never `cd`; use absolute paths.
- Review images use background (191, 255, 7), never gray.

## Report

Save it as `docs\tasks\2026-10-18-owner-0804-fixes\owner-0804-fixes-report.md`: changes (file:line), the armpit rule with quoted pixels, frames and pixels R1 and R2 change, test count, r10 SHA-1, the r9 to r10 difference, the sheet path. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with status, the r10 SHA-1, the test count and concerns only.

