# Gi base ingest: report (2026-10-30)

The 103 approved base-audit frames are now in a test build, through the trial module `gi_base_audit`. Main did not change.

## SHIPPED

| Ask (my words) | Result | Proof |
|---|---|---|
| "What about our Gohan sprites, have we ingested the latest changes?" | No, up to r40. r40 set 157 equals `art\gi_base` (last changed 2026-10-19) key for key. | `scripts\one-time\2026-10-30-gi-base-ingest\s1_map.txt` |
| "yes" to a test build with them | `builds\mockups\2026-10-30-gi-base\log2_poc_r40_gi_base.gba`, SHA-1 `d012a9f403cba1d02dbdbdd6f9cc9d1123fe69cf` | `s2_build.txt` |
| Save for the test build | `log2_poc_r40_gi_base.sav`, byte copy of `builds\log2_poc_r40.sav`, SHA-1 `d2fa5e1a016ae40fe3b264eb21008b807d391a1f` (same as the source) | `s2_build.txt` |
| Main unchanged | `build_list.txt` not touched. The main prefix of the trial list rebuilds to r40 `14d6b831` | `test_gi_base_audit` `test_before_is_r40` |
| Review by eye | `review_sheet.png` (before r40 / after trial pairs, 4x, one block per anim, changed keys framed in yellow) and `anim_00.gif` ... `anim_20.gif` (top row before, bottom row after, dirs 0-3 in columns, 160 ms a frame), all in the build folder, decoded from the two ROMs | viewed: every anim block of the sheet and one anim 20 GIF frame |
| Tests | `scripts\permanent\tests\test_gi_base_audit.py`: 17 tests, OK. Full suite (one run, 8:41 PM): 972 tests, 969 pass, 2 failures and 1 error, 307 s. All 3 are in files that other tasks edited during the run (8:38-8:42 PM): `test_celljr_fight` `test_n_puts_the_pair_in_the_vanilla_wretched_child_layout` (KeyError 30 in its own decoder) and `test_chapter_cards` `test_branch_per_leader`, `test_guard_first_landing_only`. Their lists do not include `gi_base_audit`; `build_list.txt` and `bf_ki_pool.py` did not change. `s2_build.txt` proves the trial's main prefix was r40 at build time. | `full_suite.txt` |

## PENDING

| Item | Why |
|---|---|
| My play test and by-eye review of the trial | The frames were approved one by one in the audit sheets; this is the first time they run in the game. |
| Promotion to main | My call. Two ways: move the `gi_base_audit` line into `build_list.txt`, or carry the frames into `art\gi_base` through `hand_frames` (so `gi_art.py` keeps them on a rerun). The second needs a brief. |
| Forms 158, 159, 160 (Super Saiyan, Super Saiyan 2, Rage) | Not changed. Main builds them from `gi_ssj_v2`, `gi_ssj2_aura` and `gi_rage_aura`, not from the base frames. The "one body" route (`gi_one_body.py`) would carry body fixes to 158 and 159; that is a separate step. |
| Frames not approved (list below) | They stay as in r40 until I approve them. |
| My question: approve 12.1.x and 13.x? | My own drawings 12.1.0 and 13.0.0 (`owner\`) sit in `proposed\` with 0 px difference, next to drafts of 12.1.1-12.1.3 and 13.x, but have no approved copy. Approve 12.1.x and 13.x to add them to the next trial build. |

## Frame map

Each approved PNG `157_a<anim>_d<dir>_i<index>.png` replaces the set 157 frame that key shows in r40. The module writes the frame data in place: 39 frame headers, no allocation, no pointer change. All 103 keys pass the build rules (mode P, size = the record, at most the 0x400 slot, shape bits, index 0 clear, every color = the OBJ palette color). No frame failed.

| Anim | What it is (source) | Keys approved / keys in set | Frame headers | Bytes changed |
|---|---|---|---|---|
| 0 | idle; the blink frames 0.0.1, 0.2.1, 0.3.1 (ledger 2026-10-25 9:24 AM) | 3 / 8 | 2 | 9 |
| 3 | fall, ends lying down (look of the sheet, L) | 12 / 16 (index 3 not approved) | 3 | 162 |
| 5 | ki blast pose (bible CJP row) | 12 / 12 | 9 | 186 (5.0.1 already equal) |
| 9 | power up (bible T5 row) | 16 / 16 | 4 | 135 |
| 11 | arms up, front view in every dir | 8 / 8 | 2 | 17 |
| 12 | dirs 2-3 lying on the side (look, L) | 8 / 16 (dirs 0-1 not approved) | 4 | 276 |
| 14 | front view in every dir, 5 frames (look, L) | 20 / 20 | 5 | 172 |
| 17 | halo over the head (look, L) | 8 / 8 | 2 | 104 |
| 20 | flight | 16 / 16 | 8 | 704 |
| Total | | 103 / 288 | 39 | 1765 |

r40 to trial: 1765 bytes in 675 runs, `rom:0x800536`-`0x81F250`. Every run is inside one `gi_base_audit` site. Sets 158-160 and every other set 157 frame are unchanged.

**Hand-drawn frames (`owner\`).** 6 of the 11 files are carried into `approved\` with 0 px difference: 3.0.0, 3.0.1, 3.0.2, 5.0.2, 12.2.0, 20.0.3. The 3 `owner_157_a5_d0_i2_piskel32*.png` files are 32x32 working canvases of 5.0.2 (a 16x32 frame), not frames. 12.1.0 and 13.0.0 equal their `proposed\` copies (0 px) but have no approved frame, so they are left out (my question in PENDING).

**Index 14 (#585858).** It is new to set 157: 2 px under the eyes of 11.x.0. It is the armor face gray, kept on purpose (`edits_a11.py`: "under the eyes: armor gray 14, base had navy 211"). The approved anim 11 as drafted (2026-10-24 1:10 AM). It is in the OBJ palette, so it passes. The other new indices are gi master ramps (25, 30, 33, 172) and the anim 9 glow 222.

## Frames left out

| Folder | Frames | Why |
|---|---|---|
| `proposed\` | 48 keys with no approved copy: 1.1.x-1.3.x (12, walk, my notes applied 2026-10-25, no approval in the ledger), 3.x.3 (4, draft), 12.1.x (4), 13.x (7), 18.0.x, 18.2.x, 18.3.x (21) | Not approved. The other 102 proposed keys equal their approved copy. |
| `to_edit\` | 12 PNGs (12.1.0 v2, 12.2.0 v2 and suggest, 13.0.0, 13.1.0 and v1, 13.2.0 and v1, 18.0.0, 18.0.1, 18.2.0, 5.0.2) and `anim16\` (18 frames and a sheet) | My work in progress, not approved. |
| `owner\` | 12.1.0, 13.0.0 | My drawings with no approved frame. |

## Where to look in game

- Load slot 1 (map 6,1) or slot 2 (map 11,1) of `log2_poc_r40_gi_base.sav`. Gohan leads in the base gi (appearance 2 = set 157 in the build; `log2_save info` prints set 56 from the base table).
- Stand still for the blink (anim 0). Fire a ki blast (anim 5). Power up (anim 9). Fly (anim 20). Take a knock-down hit in a fight (anim 3, L).
- Set 157 is also NPC Gohan in the Cell Games scenes (`npc_gi`) and Gohan after the chamber spar (`chamber_spar`), so those scenes show the new frames too.

## Files

- Module: `scripts\permanent\patches\gi_base_audit.py`. Test: `scripts\permanent\tests\test_gi_base_audit.py`. List: `scripts\permanent\build_list_trial_gi_base.txt`.
- Scripts and listings: `scripts\one-time\2026-10-30-gi-base-ingest\` (`s1_map.py`/`.txt` map and checks, `s2_build.py`/`.txt` build and diff, `s3_review.py` sheet and GIFs, `full_suite.txt`, `bible_rows.md`).
- One line appended to `docs\build-log.md`, as the other trial builds do.
- Nothing under `art\` changed.
