# r12fix intake: r15 report

Base: r14 `94d3028d`. Result: `archive\builds\log2_poc_r15.gba`, SHA-1 `34e3e3de03344608534001c74dc9de7a7cf9691d`. The suite has 249 tests (239 + 10 new), and all pass. The whole tests folder now runs 266 tests OK. The other 17 are in `test_npc_gi.py`, which a parallel pass wrote at 7:00 PM. They are not mine.

---

## 1. SHIPPED and PENDING

**SHIPPED**

| Ask | State | Evidence |
|---|---|---|
| 1. Snapshot first, use only the snapshot | Done | `art\hand-fixes\snap_r15\` (edits.py and 26 `out\` PNGs), copied at 6:27 PM. Every later step reads only the snapshot. |
| 2. Palette indices, record size | Done | 26 of 26 frames: every opaque pixel is an exact r14 OBJ palette color (indices 1-255), and alpha is only 0 or 255. The r14 palette has no duplicate colors. Each size equals its r12 and r14 record (CONFIRMED, `make_goldens.py`). |
| 3. Intake that survives a regeneration | Done | Section 3 |
| 4. Regenerate, suite, new tests, `check --golden` 0 | Done | `gi_art.py all`, `gi_post.py all`, `gi_aura.py all`. 249 OK. `frame_lock.py check --golden`: 0 differences, exit 0. |
| 5. r15, no env vars, r14 patch list, saves, build line | Done | `log2_build.py --out archive\builds\log2_poc_r15.gba gohan_gi ssj2_form gohan_portraits status_bonus ssj2_idle cutscene_portraits`. `log2_poc_r15.sav` and `.ss1` are byte copies of r14 (no overwrite, both new). The build line and a descriptive line are in `docs\build-log.md`. |
| 6. Proof from the ROM | Done | Section 4 |
| 7. Review sheet | Done, viewed | `archive\2026-10-18-art-review-renders\r15_intake.png` (section 5) |

**PENDING (final decisions)**

| Item | Why |
|---|---|
| 159 1.0.0, 1.0.2 and 13.0.3 have no aura bolts | The snapshot frames come from r12, which had no aura. The spec says ROM = snapshot, so I followed it. Concern 1. |
| Set 160 (Rage) keeps the old lying frame | Concern 3 |

---

## 2. Key list (CONFIRMED)

The snapshot `EDITS` has 26 keys. `out\` holds exactly these 26 files: no `out\` file is outside `EDITS`, and no key lacks a file.

| Set | Keys |
|---|---|
| 157 (gi base) | 3.0.3, 3.1.3, 3.2.3, 5.0.2, 8.0.3, 8.2.2, 12.0.0, 12.0.1, 12.0.2, 12.0.3, 13.0.0, 13.0.2, 13.0.3, 16.2.4 |
| 158 (gi SSJ) | 1.0.0, 1.0.2, 3.0.3, 3.1.3, 3.2.3, 13.0.3 |
| 159 (gi SSJ2) | 1.0.0, 1.0.2, 3.0.3, 3.1.3, 3.2.3, 13.0.3 |

- In each set, the 3 lying frames 3.0.3, 3.1.3 and 3.2.3 are byte-identical in the snapshot. They share one frame in the ROM.
- No listed key has a flip bit (attr1 0x8000 on all), so each golden is stored as shown.

---

## 3. Intake mechanism

Each frame goes into the folder that its set builds from. One table holds them all.

| File:line | What |
|---|---|
| `scripts\permanent\art\hand_frames.py:28` | `HAND`: the final folder (gi_base = 157, gi_ssj_v2 = 158, gi_ssj2_aura = 159) mapped to its keys |
| `hand_frames.py:26`, `golden_name` | Golden names `golden_gi_{base,ssj,ssj2std}_a<anim>_d<dir>_i<index>.png`, the same pattern as the walk frames. `ssj2std` is set 159, because "ssj2" means Rage 160 in `frame_lock`. |
| `hand_frames.py:62` `drawn()` | It returns the stored bytes for the keys of one PNG. It flips back a key with a flip bit. It raises when listed keys of one PNG differ, when the size differs, or when an unlisted key shares the PNG and is not the dir 3 h-flip of a listed dir 2 key. |
| `hand_frames.py:83` `place()` | It writes the goldens over the PNGs of a final folder, adds a "hand frame" note to the manifest entry, and raises when a key is not found. |
| `gi_art.py:1906` | gi_base render loop, right after I walk frames. The hand frame wins over every rule, and the manifest checks run on it. |
| `gi_post.py:346` | End of `ssj2_step_frames` (gi_ssj_v2, set 158). Placing it in gi_ssj instead would leak into the gi_ssj2 shared bodies. |
| `gi_aura.py:259` | End of `aura_folder` (gi_ssj2_aura, set 159), after the bolts. In gi_art, 159 1.0.x is 16x32. In gi_post, the bake would rewrite it. |
| `gi_art.py:1064`, `:1939` | `HAND_EXCEPTION`: a gi_base hand frame that fails a converter check gets this reason. |

- PNGs are overwritten in place and never split. A split adds frames, which moves every later allocation. Shared PNGs (the lying frame, 8.2.2 and 16.2.4) carry their dir 3 h-flip twin.
- **Survival proof (CONFIRMED):** I ran the whole chain twice. The baseline ran before any change and reproduced the r14 art exactly: 0 keys differ in all 8 folders. The intake run changed only the listed keys and their dir 3 mirrors (`compare_art.py`):
  - gi_base 17 keys;
  - gi_ssj_v2 7;
  - gi_ssj2_aura 7;
  - gi_ssj, gi_ssj2, gi_ssj2_v2, gi_rage and gi_rage_aura 0.
- Before the edit, the current tree rebuilt r14 byte for byte (`scripts\one-time\2026-10-18-r12fix-intake\r14_repro.gba`, with its own log file).

**Lock change (CONFIRMED)**
- `frame_lock.py:41,50`: `GOLDEN_FILES = GOLDEN_IDLE + GOLDEN_WALK + GOLDEN_HAND`, 46 names. The docstring is updated.
- I ran `lock --golden --replace`. The old lock moved to `art\locks\golden_20261018-1857`.
- The 20 old fingerprints in the new lock equal the moved lock (20 of 20).
- `check --golden` exits 0.

**Tests**
- New: `tests\test_hand_frames.py` (10 tests):
  - the table equals the snapshot keys;
  - each listed key equals its snapshot frame by RGB;
  - the goldens equal the placed PNGs;
  - no other key of 157-159 differs from the r14 ROM, except the 5 named mirrors, which must equal the flip of their dir 2 frame;
  - each listed key differs from r14 (this proves that the comparison can see a change);
  - the lock holds the 46 fingerprints;
  - the gi_base notes;
  - `drawn()` refuses an unlisted key on a shared PNG, a dir 3 key without the flip bit, and a wrong size;
  - the flip-back.
- Changed tests, each named:
  1. `test_owner_walk.test_golden_set_has_20_names` is now `..._46_names`.
  2. `test_gi.test_every_opening_has_its_shape` skips hand frames. Base 8.0.3 draws its own bare-chest V (3:19 PM).
  3. `test_gi.test_shoe_rows` skips hand frames. Base 8.2.2 is my drawing, and the shoe rule would move 6 px.
  4. `test_aura` (bolts only, and no-aura frames equal the body) skips hand frames, which replace the baked frame.
  5. `test_gi_post.test_step_frames_only_frames_1_to_3_change` now allows exactly the 4 set 158 hand PNGs too.

---

## 4. ROM proof (CONFIRMED, `scripts\one-time\2026-10-18-r12fix-intake\rom_proof.py`, output `rom_proof.txt`)

- I ran `rom_sheet.py log2_poc_r15.gba 157,158,159,160 --frames archive\2026-10-18-art-review-renders\frames_r15`. It wrote 1638 PNGs. The 26 listed keys equal their snapshot frames pixel for pixel (26 of 26).
- `--frames` skips dir 3 records that reuse a dir 2 header. So I also compared all 1076 records of sets 157-160 with `set_records`:
  - Geometry changed: none. Frame header moved: none. The set offsets are equal.
  - Changed shown pixels: the 26 listed keys plus 157 3.3.3, 8.3.2, 16.3.4, 158 3.3.3 and 159 3.3.3. These are the dir 3 records that h-flip a listed dir 2 frame. Set 160: 0.
- Byte diff r14 to r15: 921 bytes in 103 regions, rom:0x804BEB-0x85D2C4. Each region lies inside the frame data of a listed key's frame. None is in a table word or a record. Sample regions:
  - 157: 0x804BEB-0x804C7C (lying frame, header 0x8048B8), 0x806A4D-0x806ADF (5.0.2), 0x80ECB7-0x80EDF9 (8.0.3), 0x8107AD-0x8109DF (8.2.2), 0x8122ED-0x812ABD (12.0.0-12.0.3), 0x8143EE-0x8143FF (13.0.0), 0x8147D1 (13.0.2), 0x814A43-0x814B11 (13.0.3), 0x81AF56-0x81B16D (16.2.4);
  - 158: 0x820AFA-0x820BD0 (1.0.0), 0x820F09-0x820FA5 (1.0.2), 0x824A14-0x824A74 (lying), 0x834838-0x834908 (13.0.3);
  - 159: 0x8423FF-0x84277C (1.0.0), 0x842CFA-0x842F90 (1.0.2), 0x849400-0x849460 (lying), 0x85D12C-0x85D2C4 (13.0.3).
  - The full list of 103 regions is in `scripts\one-time\2026-10-18-r12fix-intake\rom_proof.txt`.
- `log2_poc_r14.gba` is unchanged: `94d3028d`.

---

## 5. Review

- `archive\2026-10-18-art-review-renders\r15_intake.png` (3484x1976): 6x on (191, 255, 7), each frame at its record dx, dy. There is one band per set with the r14 row over the r15 row. A fourth band shows the 5 dir 3 mirrors. I viewed it.
- **Flying 157 12.0.0-12.0.3:** the gray boots above the head are now brown shoes and purple legs. The arms under the body are skin with bands (LIKELY reads as I asked at 5:03 PM).
- **Lying, all forms:** the hand at the face and the lower arm are skin with a band. The sash crosses the hip. The mirrors follow.
- **159 1.0.0, 1.0.2 and 13.0.3:** the blue bolts are gone (concern 1).
- The other frames show small edits that match the edits.py comments.

---

## 6. Concerns

1. **Aura loss on 3 set 159 frames (CONFIRMED).** The snapshot 159.1.0.0, 1.0.2 and 13.0.3 were drawn on r12 frames, before the r13 aura.
   - The snapshot differs from r12 by 19, 15 and 25 px, and from r14 by 62, 38 and 51 px. The extra pixels are the bolts.
   - In r15, these walk and run frames have no bolts, and their neighbours keep them. In play the aura LIKELY flickers.
   - Fix options: redraw the 3 frames on r14, or place them before the bake. The second option breaks "ROM = snapshot".
2. **Dir 3 mirrors change (CONFIRMED, LIKELY intended).** 157 3.3.3, 8.3.2, 16.3.4, 158 3.3.3 and 159 3.3.3 share the frame of a listed dir 2 key, so they show its mirror. A split would leave the left-facing frame unfixed and shift the build. The tests and the proof allow exactly these 5.
3. **Set 160 (Rage) keeps the r12 lying frame (CONFIRMED).** gi_rage is a frozen r12 copy. Its 3.0.3, 3.1.3 and 3.2.3 equal r12 159, so the hand-at-face defect stays in Rage. Its 5.0.2, 8.0.3, 8.2.2 and 16.2.4 also equal r12 159. I did not change 160.
4. **The converter checks flag 9 of the gi_base hand frames (CONFIRMED).** They are 3.0.3 (parts), 5.0.2 (parts), 8.2.2 (light, sleeve, parts), 12.0.0-12.0.3 (chest, parts), 13.0.0 (parts) and 16.2.4 (sleeve, parts). They pass by `HAND_EXCEPTION`. The checks read the armor's part map, and my fixes repaint those parts, so this is LIKELY a check limit, not a defect.
5. **SSJ forms keep some base-only fixes as r12 (SPECULATIVE).** The 157 fixes for 5.0.2, 8.x, 12.0.x, 13.0.0/2 and 16.2.4 have no 158 or 159 entry in EDITS. If the same defect exists there, it stays.
6. **Process slip.** One Bash call (the r14 repro build) started with `cd`. It had no effect, because the scripts use `__file__` paths and the output went to my scratch folder with `--log`. `docs\build-log.md` did not get the repro line (CONFIRMED).
7. **The new test is pinned to r14 (CONFIRMED by design).** `test_hand_frames.test_no_other_key_differs_from_r14` compares the art with the r14 ROM and allows only the 5 named mirrors. The next pass that changes any other frame of sets 157-159 will fail this test until its baseline moves to the new ROM. That failure is expected and is not a regression.
8. **Parallel work.** `patches\npc_gi.py` and `tests\test_npc_gi.py` appeared at 7:00-7:04 PM. One run caught `test_npc_gi` mid-edit (1 failure). The final run passes all 266. These files are not in the r15 patch list. The build inputs (patches and helpers) were unchanged since the r14 repro, which matched r14.

---

## 7. Files

- New: `scripts\permanent\art\hand_frames.py`, `scripts\permanent\tests\test_hand_frames.py`, and 26 goldens `art\golden\golden_gi_{base,ssj,ssj2std}_a*_d*_i*.png` (mode P, transparency 0). No existing golden was written.
- Changed: `gi_art.py`, `gi_post.py`, `gi_aura.py`, `frame_lock.py`, `tests\test_gi.py`, `tests\test_aura.py`, `tests\test_gi_post.py` and `tests\test_owner_walk.py`. All are LF, with no byte order mark, no dashes and no control characters (checked).
- Regenerated: `art\gi_base`, `gi_ssj`, `gi_ssj_v2`, `gi_ssj2`, `gi_ssj2_v2`, `gi_ssj2_aura` and `gi_rage_aura`, plus the gi_art sheets. The r14 art backup is in `archive\2026-10-18-art-snapshots\intake-art_r14\`.
- Scripts (mine): `scripts\one-time\2026-10-18-r12fix-intake\analyze.py`, `compare_art.py`, `make_goldens.py`, `rom_proof.py` and `review_sheet.py`.
- I did not edit `fix.py`, `view.py` or `edits.py`, and wrote nothing under `data\`.

Labels: CONFIRMED means proven by script output or a byte compare in this session. LIKELY means inferred from a sheet or from intent. SPECULATIVE means not checked.
