# promote-chain report: gi post-processing chain promoted to scripts\permanent

Status: DONE, with my items.

## Files and functions

| File | What |
|---|---|
| `scripts\permanent\art\gi_post.py` (new) | `transplant_heads`, `finish_golden_slots`, `rules`, `body_rules`, `ssj2_step_frames`, `run_all`, CLI `all`, `transplant`, `finish`, `body`, `step`. One ROOT and ART constant; every function takes `art=ART`. Constants and why comments kept. |
| `scripts\permanent\art\gi_review.py` (new) | `strips`, `base_step`, `ssj2_step`, `step_gif`, `run_all`, CLI `all`, `strips`, `base_step`, `ssj2_step`, `gif`. BACKGROUND (191, 255, 7), LABEL black. |
| `scripts\permanent\patches\gohan_gi.py:33-34` | Defaults: 158 `gi_ssj_v2`, 159 `gi_ssj2_v2`, 157 `gi_base` unchanged. Env overrides stay. Header lines 5-7 updated. |
| `scripts\permanent\tests\test_gi_post.py` (new) | 9 tests (list below). |
| `scripts\permanent\tests\test_gi.py:445` | `GI_IDS` 158 and 159 now name the v2 folders. Needed: `test_gi_sets_decode_to_manifest_pixels` compares the ROM with the folders gohan_gi reads, and failed with the old names (step frames dy -25 against -24). |
| `art\golden\work_r3\` | Exit guard (print "promoted to scripts\permanent\art\gi_post.py" or gi_review.py, exit 1) in `transplant`, `finish_v2`, `bodyfix`, `transform158` (gi_post) and `strips`, `base_step`, `transform_review`, `transform_gif` (gi_review). Each guard sits after the header comments and keeps that file's line ends. All 8 verified: exit 1. `aura.py`, `aura_review.py`, `aura2\` untouched. |
| `docs\RE-BIBLE.md` | Two new rows (gi_post, gi_review) before the `test_gi.py` row; two existing rows now name `gi_post.py` instead of `finish_v2.py` and `bodyfix.py`. |
| `docs\build-log.md` | r8 line appended by the builder, then annotated. |

## Equality proof (CONFIRMED)

Method: `gi_art.py all` (159, 159, 162 frames, failing 0), then the 4 scratch scripts in order (`bodyfix.py --apply`), then copied `gi_ssj2_v2` and `gi_ssj_v2` to a temp folder. Then deleted every file in `gi_ssj2_v2` (review\ kept), ran `gi_post.py all`, compared (script `cmp.py` in the task scratchpad).

| Folder | Files | PNG pixel, size and palette equal | PNG file bytes equal | manifest.json bytes | transplant.json bytes |
|---|---|---|---|---|---|
| gi_ssj2_v2 | 161 each side, same names | 159 of 159 | 159 of 159 | equal | equal |
| gi_ssj_v2 | 160 each side, same names | 159 of 159 | 159 of 159 | equal | n/a |

- Status counts match the scratch run: transplant ok 93, ok+grow 38, ok+shift1 10, flag 7, ok+shift2 5, ok+shift1+grow 4, ok+shift3+grow 1, ok+shift2+grow 1. Finish: golden 3, kept 5, flag 6.
- Gate: `{0: 1, 1: 0, 2: 0, 3: 0}` in both. `body_rules` applied nothing, as `bodyfix.py --apply` did. The rule is unchanged.
- A second check, `test_chain_is_repeatable`, runs the 4 steps on a temp copy of gi_ssj, gi_ssj2 and golden and compares every output byte with the folders on disk. It passes.

## Tests

- Whole suite, ROM-building tests included: `py -3 -I -m unittest discover -s scripts\permanent -p "test_*.py"` gives **113 tests, OK** (104 before plus 9 new).
- New tests: idle slots equal the SSJ2 goldens byte for byte (pixels, palette, size, 32x32 manifest, status "golden"); kept frames equal the source (pixels and keys); gate counts equal `rules()` on the goldens; gate decides (blocked gate leaves every byte of a temp gi_ssj2_v2 unchanged, goldens intact); step frames 1-3 keep frame 0's belt screen row (-1); only the 3 step frames differ from gi_ssj and each key has dy minus 1; chain repeatable; gohan_gi default folders; env overrides stay.

## r8 build

- Command, no env vars: `py -3 -I scripts\permanent\log2_build.py --out archive\builds\log2_poc_r8.gba gohan_gi ssj2_form gohan_portraits`. r8 did not exist before.
- **r8 SHA-1 5662dc0224bd5d6e4697d93069e59d9f13fcdfef.** It equals r7. The whole 16 777 216 byte ROM is identical.
- Sets 157-159 against r7 (`cmp_roms.py`), per record: tile bytes and geometry (dx, dy, w, h, attr0, attr1).

| Set | Offset r7 and r8 | Records | Keys equal | Geometry equal | Tile bytes equal |
|---|---|---|---|---|---|
| 157 | 0x81FE14 | 288 | yes | 288 | 288 |
| 158 | 0x83FDD0 | 276 | yes | 276 | 276 |
| 159 | 0x868B9C | 276 | yes | 276 | 276 |

## My items and findings

1. CONFIRMED: `body_rules` still applies nothing (gate `{0: 1, ...}`, R2 at golden d0 pixel (12, 19)). The 130 px in 70 frames from the gi-rules night report stay unfixed. Needs a final decision (the exemption proposed there).
2. CONFIRMED: the scratch transplant and finish scripts write `manifest.json` and `transplant.json` through `Path.write_text`, so they get CRLF line ends on Windows. `transform158` writes LF. I kept each call as it was to stay byte-identical. The port is therefore Windows-dependent for those two files (JSON content is the same on any platform). LIKELY harmless.
3. CONFIRMED: the step-frame manifest note still reads "SSJ2 golden head (transform158.py), dy -1". I kept the text so the manifest stays byte-identical. It names a script that now exits. Changing it is a one-line edit plus a re-run.
4. CONFIRMED: the old `strips.py` drew each cell on gray (150, 150, 150). The brief says never gray, so the port draws cells on the lime background too. The strips are the only visual change to a renderer. The other three renderers were already lime.
5. CONFIRMED: a command of mine in this run (a script that added the guards) failed after guarding only `transplant.py`, and `strips.py` ran unguarded once. It rewrote `art\gi_ssj2_v2\review\a*.png` from the scratch code (gray cells). I re-ran `gi_review.py all`, so the 17 strips are current and lime. No other output changed.
6. CONFIRMED: `gi_post.py` leaves `gi_ssj2_v2\review\` alone, but `ssj2_step_frames` deletes and recreates `gi_ssj_v2` (as the scratch did). Anything hand-placed there is lost on each run.
7. CONFIRMED: `test_gi.py` Art tests still read `gi_base`, `gi_ssj`, `gi_ssj2`; only the ROM comparison and slot-fit tests moved to v2.
8. SPECULATIVE: `gi_review.py base_step` needs `art\vanilla-sets\set56` (it ran).
9. I used `Set-Location` once to the LOG root (the shared working directory already). Python files: LF, no byte order mark, no em or en dashes (checked). Nothing written under `data\`, no golden file edited (16 golden PNGs unchanged in count), no ROM in `builds\` overwritten.
