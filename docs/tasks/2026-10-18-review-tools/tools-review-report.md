# Tools review report: rom_sheet.py and frame_lock.py (2026-10-18)

Status: DONE. Suite: 149 tests OK (140 before, 9 new in `test_tools.py`).

## Files and functions

- `scripts\permanent\rom\rom_sheet.py`: `live_set_offset` (line 41), `row_frames`, `build_sheet`, `row_gif_frames`, CLI `_main`. Reuses `gi_review.BACKGROUND` (191, 255, 7), `log2_sprites.SLOT_BYTES`, `PALETTE_OFF`, `set_records`, `tiles_to_image`.
- `scripts\permanent\art\frame_lock.py`: `fingerprint`, `lock_folder`, `check_folder`, `changed_sheet`, CLI `_main`. Reuses `gi_review.BACKGROUND`.
- `scripts\permanent\tests\test_tools.py`: 9 tests (live_set_offset on poc for ids 7, 56, 156; base ROM ids 7-156 all equal `SET_TABLE`; moved-table synthetic ROM; sheet row order; fingerprint ignores PNG encoding; fingerprint catches a 1-pixel change; check differences with keys; CLI exit codes 0, 1, 2 plus `--sheet` and `--replace`; `only` list). Every write goes to a temp folder.
- `docs\RE-BIBLE.md`: 3 rows added in section 11 (rom_sheet, frame_lock, the d3 flip fact).
- Files are LF, no BOM, ASCII only (checked after a CRLF fix; the writer had produced CRLF).

## Sheets

- `archive\2026-10-18-art-review-renders\r7_base.png` (sets 56,157, anims 0,1,9) and `archive\2026-10-18-art-review-renders\r7_ssj.png` (sets 59,158,159, anims 0,9) on `log2_poc_r7.gba`.
- r9 check: `r9_ssj.png` and `r9_base.png` in the same folder. SHA-256 of both equals the r7 sheets (CONFIRMED: r9 matches r7 for these sets and anims).
- No record is over `SLOT_BYTES` in any row (CONFIRMED).
- `--gif` ran once on r7_base (24 GIFs written, then deleted; not a deliverable).

## ROM against art (CONFIRMED, script run on r7, not kept)

- Set 157 vs `gi_base`, 158 vs `gi_ssj_v2`, 159 vs `gi_ssj2_v2`: 288, 276, 276 ROM records, 0 mismatches in pixels or dx, dy, and no art key missing from the ROM.
- Idle (anim 0 index 0) d0-d2 of 157, 158, 159 equal the golden PNGs byte for byte.

## Golden lock (`art\locks\golden\`, note "approved 2026-10-18 12:15 AM")

`check --golden` right after: 0 differences, exit 0. gi_* folders not locked.

```
golden_gi_base_d0.png  7ab747a216b685072e287ca3b47231ab1b65930f
golden_gi_base_d1.png  3d00969b2430d7a39dcb7c62a024dfa936041e56
golden_gi_base_d2.png  3101f7a2b1e017fddbbc181aacabb8193ddcb76a
golden_gi_base_d3.png  c080a823282866dc3acdf0286d2f4b5ddec2ad6d
golden_gi_ssj_d0.png   f19732e09b05ad876340404a1f4676a0ad737916
golden_gi_ssj_d1.png   e8778f916af34b30e102126affe1cf3a03713f85
golden_gi_ssj_d2.png   0108873eef656e7c6d002be00a0d5129e4e5b15c
golden_gi_ssj_d3.png   4d7b922764fb7b6c25db34a97f4b7088ec0f079f
golden_gi_ssj2_d0.png  48593ac60b0eadbf03fec79b6cbe5f5329a9305d
golden_gi_ssj2_d1.png  74a26036e0bc1a6e1d721fb64183536fb24f8326
golden_gi_ssj2_d2.png  5499c1d0a1304fad9b74d0e082c125e3f79d9071
golden_gi_ssj2_d3.png  6419288406e16ee0166ce62c7fd786bae26f7dab
```

## Seen in the sheets and concerns

- CONFIRMED, not a defect: ROM d3 equals ROM d2 pixels with the h-flip bit (attr1 0x1000). The golden d3 PNG is the mirror of golden d2, so a raw byte compare of ROM d3 with golden d3 shows "different". Sheets draw the flip, so d3 looks right. In RE-BIBLE.
- Sheets look sane: no offset jumps seen, set 157 matches set 56 geometry, set 158 and 159 idle frames show the golden heads. Set 158 a9 frames 2-3 show the large flash ring; set 159 a9 shows SSJ2 in all 4 frames (the base set 59 starts a9 as base then powers up, so 159 differs by design, LIKELY expected).
- CONFIRMED limitation: the fingerprint covers pixel indexes, not the palette. A palette-only change gives no difference. Frames are indexed into the shared ROM palette, so this fits the project, but it is a blind spot.
- CONFIRMED limitation: a lock is named by the folder name only. Two folders with the same name in different parents share one lock.
- The golden lock records empty keys: the golden folder has no manifest.json.
- `check` has no way to accept a change except `lock --replace` (moves the old lock aside). No partial re-lock of single frames.
- The row-count of sheets grows with sets x anims x dirs; 3 sets x 2 anims x 4 dirs is 3600 px tall at 4x. Use `--dirs` or `--scale` for smaller sheets.
