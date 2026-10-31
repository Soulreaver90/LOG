# owner-0804-fixes report

Status: DONE.
Acknowledged: fix 1 is cancelled; BONUS_TEXT stays "split". I had set "live" and edited test_status.py before the cancel; both are reverted (status_bonus.py line 46 and test_status.py are back to the original text, the full suite passes). No header or RE-BIBLE row was changed.

## Changes (fix 2)
- `scripts/permanent/art/gi_post.py`: `rules(img, front_back, front=False)` (line ~218): in a front view the first R2 row (gi top + 2) keeps a gi pixel whose image-left neighbor is the arm outline 23. `body_rules` passes `front` = (dir == 0) in the gate and in the apply loop. Header comment and API line updated.
- `body_rules` now skips the 5 `KEEP` frames (powered-down, black hair). CONFIRMED need: with the rules applied again, `test_kept_frames_equal_the_source` failed on frame_2B6794 (a 211 pixel pair added). The skip keeps the existing invariant. I may want a different call.
- `scripts/permanent/tests/test_gi_post.py`: `test_gate_passes_on_all_goldens`, `test_r2_changes_an_arm_line_and_spares_the_armpit` (synthetic: armpit pixel stays 88 in front view, becomes 211 without the exemption, image-right armpit pixel and the row below still change), and the existing gate test now passes the `front` argument.

## Armpit rule (CONFIRMED)
Run of the old rule on the four SSJ2 goldens: d0 changes 1 pixel, d1 0, d2 0, d3 0.
- d0: gi top row = 17 (collar 211 at x 11 and 19), so R2 starts at row 19. Pixel (12, 19) is 89, its left neighbor (11, 19) is 23, its right neighbor (13, 19) is 89. The rule would make it 211. It is my chest.
- d1 (back): gi top 17, no R2 candidate. d2 (side): gi top 16, candidates (15, 20) and (15, 21), but they are in a side view, where R2 does not run. d3 mirrors d2.
- Exemption: front view only (dir 0), row = gi top + 2, left-neighbor arm. After the change the gate prints {0: 0, 1: 0, 2: 0, 3: 0}.

## What R1 and R2 change now
- 121 px in 67 frames of gi_ssj2_v2 (night report before the exemption: about 130 px in 70 frames; the 3 frames and 9 px that dropped are KEEP frames).
- I did not split the count between R1 and R2.

## Tests
151 OK (`py -3 -I -m unittest discover -s scripts\permanent -p "test_*.py"`; 149 before plus 2 new). `frame_lock.py check --golden` exits 0.

## Build
- Chain run: gi_art all, gi_post all, gi_review all, no errors.
- `archive/builds/log2_poc_r10.gba` SHA-1 `ad9e0d1976f13da6e55698217f6c62e47a14d85e` (r9: f61fd3b7c978d12dc7e05b1ba5723c4bf238bcc7). `log2_poc_r10.ss1` copied from r9. Build line appended to `docs/build-log.md`.

## r9 to r10 difference (CONFIRMED)
- 121 differing bytes in 120 runs, all in rom:0x84162B-0x8673E5.
- Set 157 and set 158 decode identical frames and records. Set 159: 276 records and all headers identical; 101 records decode to different tiles, backed by 67 distinct compressed frame blocks. Every differing byte lies in a set 159 frame block. No code, table or status byte differs.

## Sheet
`archive/2026-10-18-art-review-renders/r10_armline.png`: r9 left, r10 right, set 159 anims 0, 1, 4, all dirs, 4x on (191, 255, 7). I looked at it. r10 shows the dark arm line beside the arms on front and back frames; the golden chest on the idle front looks unchanged. At 4x I did not inspect individual pixels (LIKELY fine).
