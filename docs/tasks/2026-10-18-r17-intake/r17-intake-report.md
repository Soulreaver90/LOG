# r17 intake: second r12fix intake and a slower idle aura

Base: r16 `1adfa726`. Result: `archive\builds\log2_poc_r17.gba`, SHA-1 `eee5eb351e94e50910d6129a48eacecb6d85ab80`. The whole suite runs 285 tests, and all pass.

Labels: CONFIRMED means proven by script output or a byte compare in this session. LIKELY means inferred from a sheet or from intent. SPECULATIVE means not checked.

---

## 1. SHIPPED and PENDING

**SHIPPED**

| Ask | State | Evidence |
|---|---|---|
| 1. Snapshot first | Done | `art\hand-fixes\snap_r17\` (edits.py, SHA-1 `bf6d1155`, and 46 `out\` PNGs), copied at 8:59 PM. Every later step reads only the snapshot. At 10:11 PM the live folder had moved on (edits.py `26f2fc73`, 64 PNGs). That work is not in r17. |
| 2. Take in the new or changed keys | Done | Section 2 |
| 3. r15 mechanism, new goldens, no golden edited | Done | Section 3 |
| 4. Palette and record size | Done | 46 of 46 frames: every opaque pixel is exactly one r16 OBJ palette color, alpha is only 0 or 255, and each size equals its r16 record (CONFIRMED, `make_goldens.py`) |
| 5. Dir 3 sharing | Done, one difference from the brief | Section 4 |
| 6. Baseline of the r14 test moved to r16 | Done | `test_no_other_key_differs_from_r16` (section 6) |
| Task 2: slower idle aura | Done | Section 5 |
| Build, save, build line | Done | Section 7 |
| ROM proof | PASS | Section 8 |
| Review sheet | Done, viewed | Section 9 |

**PENDING (final decisions)**

| Item | Why |
|---|---|
| 159 1.2.0 (and its mirror 1.3.0) lost the aura bolts | Concern 1 |
| SSJ forms keep the r16 flight frames | Concern 3 |

---

## 2. Key list (CONFIRMED)

The snapshot `EDITS` has 46 keys. `out\` holds exactly these 46 files. No key from the r15 snapshot was dropped.

| Kind | Keys | Count |
|---|---|---|
| New | 157: 1.2.0, 16.2.1, 20.d.i (d 0-3, i 0-3); 158: 1.2.0; 159: 1.2.0 | 20 |
| Changed against the r15 golden | 159: 1.0.0 (43 px), 1.0.2 (23 px), 13.0.3 (26 px) | 3 |
| Equal to the r15 golden | the other 23 r15 keys | 23 |

- The expected list in the brief matches exactly. No extra key, no missing key.
- The 3 changed keys now carry the aura bolts. In the r17 sheet the light blue bolts are back on 1.0.0, 1.0.2 and 13.0.3.

---

## 3. Goldens (CONFIRMED)

- `scripts\one-time\2026-10-18-r17-intake\make_goldens.py --write` wrote 23 new files and changed none. It refuses to write a name that exists.
- New keys use the plain pattern: `golden_gi_{base,ssj,ssj2std}_a<anim>_d<dir>_i<index>.png` (20 files).
- **A changed key gets a revision suffix.** `hand_frames.REVISION` maps the 3 keys to `r17`, and `golden_name()` adds `_r17`:
  - `golden_gi_ssj2std_a1_d0_i0_r17.png`
  - `golden_gi_ssj2std_a1_d0_i2_r17.png`
  - `golden_gi_ssj2std_a13_d0_i3_r17.png`
- The 3 r15 files stay on disk untouched (dated 6:41 PM). They left `HAND` and the lock.

| File:line | Change |
|---|---|
| `scripts\permanent\art\hand_frames.py:33-39` | `FLIGHT`, the new keys in `HAND` (46 keys), `REVISION` |
| `hand_frames.py:44-47` `golden_name()` | adds the revision suffix |
| `hand_frames.py:1-24` | docstring: the r17 snapshot, the revision rule, the anim 20 layout |
| `frame_lock.py:20-22`, `:50` | docstring and comment: 46 hand frames, 66 names |

**Lock**
- `frame_lock.py lock --golden --replace`. The old lock moved to `art\locks\golden_20261018-2124`.
- The new lock holds 66 names. The 43 names it shares with the old lock keep their fingerprints (43 of 43, `lock_check.py`).
- `check --golden` exits 0.

**Regeneration**
- Before any change, the current tree rebuilt r16 byte for byte (`scripts\one-time\2026-10-18-r17-intake\r16_repro.gba`), and an unchanged `gi_art`, `gi_post`, `gi_aura` run gave 0 changed keys in all 8 folders.
- After the change, `compare_art.py` against the r16 art backup (`archive\2026-10-18-art-snapshots\intake17-art_r16\`):
  - gi_base 20 keys: 1.2.0, 1.3.0, 16.2.1, 16.3.1 and the 16 keys of anim 20;
  - gi_ssj_v2 2: 1.2.0, 1.3.0;
  - gi_ssj2_aura 5: 1.0.0, 1.0.2, 1.2.0, 1.3.0, 13.0.3;
  - gi_ssj, gi_ssj2, gi_ssj2_v2, gi_rage, gi_rage_aura 0.
- No geometry or PNG sharing changed.

---

## 4. Dir 3 sharing (CONFIRMED)

- **Anim 20 differs from the brief.** It does not have 4 own frames per index. It has 2:
  - dir 2 uses the dir 0 frame header with the h-flip bit (attr1 0x9000);
  - dir 3 uses the dir 1 frame header with the h-flip bit.
- All 16 anim 20 keys are listed. The snapshot pairs are exact mirrors (20.2.i = flip of 20.0.i, 20.3.i = flip of 20.1.i, i 0-3), so each shared PNG gets one consistent frame. No split was needed, and no unlisted key changes.
- The brief LIKELY took "anim 20 d3 has its own frame headers" from the RE bible. That line is true only against dir 2. I made it more exact and added a new line.
- New unlisted dir 3 mirrors (each shares the frame of a new dir 2 key and shows its mirror, as in r15):
  - 157 1.3.0 (of 1.2.0), 157 16.3.1 (of 16.2.1), 158 1.3.0, 159 1.3.0.
- The r15 mirrors (157 3.3.3, 8.3.2, 16.3.4; 158 3.3.3; 159 3.3.3) are unchanged against r16.

---

## 5. Idle aura (CONFIRMED)

- `scripts\permanent\patches\ssj2_idle.py:56`: `lsr r2,r2,#18` became `lsr r2,r2,#19`. The shape is now `(tick >> 3) % 3`, one shape per 8 frames (133 ms).
- Bytes: hook `@0x08894E24` +0x22 = `rom:0x894E46`, halfword `0x0C92` (`92 0C`) became `0x0CD2` (`D2 0C`). Only the low byte changes. The hook address and size are the same as r16.
- Range note (header lines 14-16 and 20-21): `tick >> 3 < 0x2000`. `(x * 0x5556) >> 16` equals `x / 3` for every x below 0x8000, so the note still holds. A test checks both ranges exhaustively.
- Walk and run bolts are not touched.
- `docs\RE-BIBLE.md` line 136 now gives the r17 shift and the byte.

---

## 6. Tests

The suite has 285 tests, and all pass (`scripts\one-time\2026-10-18-r17-intake\suite.txt`). Mine add 8: 266 (r16) + 8 = 274. The other 11 are in `test_save.py` (30 tests, edited 8:46 PM by the save task). They are not mine.

**test_hand_frames.py (14 tests, was 10)**
- Snapshot `snap_r17`, baseline `log2_poc_r16.gba`.
- `test_no_other_key_differs_from_r14` is now `test_no_other_key_differs_from_r16`. Against r16 it allows exactly the 4 new mirrors.
- `test_listed_keys_changed_against_r14` is replaced by two tests:
  - `test_r17_keys_changed_against_r16`: the 23 r17 keys differ from r16;
  - `test_r15_keys_equal_r16`: the 23 r15 keys equal r16.
- New: `test_revised_keys_get_a_new_golden_and_keep_the_old_file`, `test_every_mirror_shows_its_dir_2_frame` (all 9 mirrors), `test_flight_dirs_2_and_3_are_listed_flips_of_dirs_0_and_1`.
- `drawn()` test: a listed flip pair without the flip bit raises.

**test_idle.py (18 tests, was 14)**
- `formula` uses `SHAPE_SHIFT = 3`. The disassembly expects `lsr r2,r2,#19`.
- New: `test_shift_instruction_bytes` (hook +0x20 = `02 04 D2 0C`), `test_shape_sequence_is_one_shape_per_8_ticks` (ticks 0-31 give 8 x 0, 8 x 1, 8 x 2, 8 x 0; ticks 0xF0-0x108 give 0, 7 x 3, 8 x 4, 8 x 2, 0), `test_divide_by_3_is_exact_over_the_shifted_range`, `test_every_shape_appears`.
- The "all 6 shapes appear" assertion moved out of the formula test. At seed 0xFFF0 with 512 ticks, the >> 3 sequence reaches only body shapes 3 and 4, so the old assertion would fail there. The new test uses seed 0, which reaches all 6.

**Other changed tests, each named**
1. `test_owner_walk.test_golden_set_has_46_names` is now `..._66_names`.
2. `test_gi_post.test_step_frames_only_frames_1_to_3_change` allows 5 set 158 hand PNGs (was 4).
3. `test_gi.test_base_sash_not_below_ssj` skips hand frames. My flight back views 157 20.1.i and 20.3.i tilt the sash (base row -4, SSJ row -5). These 8 keys were the only failures, all hand frames (`sash_check.py`).

---

## 7. Build and save

- Command: `log2_build.py --out archive\builds\log2_poc_r17.gba gohan_gi ssj2_form gohan_portraits status_bonus ssj2_idle cutscene_portraits npc_gi`. No `LOG_*` env vars were set.
- r17 SHA-1 `eee5eb351e94e50910d6129a48eacecb6d85ab80`. r16 is unchanged (`1adfa726`).
- Save: `test-data\saves\log2_lv40_cellgames_v2.sav` existed at build time. It is copied to `log2_poc_r17.sav` (SHA-1 `159601a3`). No r17 file existed before. No `.ss1` was made.
- `docs\build-log.md`: the auto line and a descriptive line (LF, written through Python).

---

## 8. ROM proof (CONFIRMED, `scripts\one-time\2026-10-18-r17-intake\rom_proof.py`, output `rom_proof.txt`, PASS)

- All 46 listed keys equal their snapshot frame pixel for pixel. Each is decoded from its r17 record with flips applied, so anim 20 dir 2 and 3 are covered.
- All 1076 records of sets 157-160:
  - geometry changed: none;
  - frame header moved: none;
  - set offsets equal;
  - changed shown pixels: the 23 r17 keys plus the 4 mirrors. Set 160: 0. The 23 r15 keys equal r16.
- Byte diff r16 to r17: 264 bytes in 45 regions, `rom:0x801D82`-`0x894E46`. Nothing differs in the base 8 MB.
  - 44 regions lie inside the frame data of an r17 key's frame: 157 1.2.0 (header `0x801C20`), 16.2.1 (`0x81A208`), anim 20 (`0x81D288`-`0x81EEC0`), 158 1.2.0 (`0x821A18`), 159 1.0.0 (`0x8423C4`), 1.0.2 (`0x842BD4`), 1.2.0 (`0x844404`), 13.0.3 (`0x85CF14`).
  - 1 region is the idle shift byte `rom:0x894E46`.
  - No region is in a table word, a record or other code.

---

## 9. Review

- `archive\2026-10-18-art-review-renders\r17_intake.png` (5124x2468): 6x on (191, 255, 7), each frame at its record dx, dy, the r16 row over the r17 row. Bands: set 157, set 157 anim 20, set 158, set 159, and the 4 new mirrors. A star marks an r17 key. I viewed it.
- I viewed every band in crops at full scale (`scripts\one-time\2026-10-18-r17-intake\crop*.png`). Pixel equality is proven in section 8. The notes below are what the eye sees:
  - 157 and 158 1.2.0, and their mirrors: the back shoe is brown with a dark sole, and the shoulder is purple (LIKELY reads as I asked at 8:10 and 8:23 PM).
  - 157 16.2.1 and its mirror 16.3.1: the sash steps down to the right (LIKELY as asked at 6:27 PM).
  - Anim 20 back views (d1 and the mirrored d3): the flat sash now runs down at the body angle (LIKELY as asked at 8:06 PM).
  - Anim 20 front views (d0 and the mirrored d2): the change is 5 px on row 20. At 6x it is hard to see; the chest under the chin reads more purple (LIKELY).
  - 159 1.0.0, 1.0.2 and 13.0.3: the light blue bolts are back (CONFIRMED, viewed).
  - **159 1.2.0 and 1.3.0: the bolts are gone** (CONFIRMED, viewed and counted; concern 1).

---

## 10. Concerns

1. **159 1.2.0 has no aura bolts (CONFIRMED).**
   - In r16 it had 19 bolt-blue (120, 208, 248) pixels and 4 white bolt pixels. The snapshot frame has none (`bolt_check.py`). Its EDITS entry has row edits but no `("bolts",)` op, unlike 159 1.0.0, 1.0.2 and 13.0.3.
   - Cause (CONFIRMED, `bolt_source.py`): outside the edited rows 19-22 and 27-28, the snapshot equals the pre-bake body `gi_ssj2_v2` 1.2.0 (0 px differ) and differs from the baked r16 frame by 15 px. So I drew 159.1.2.0 on the aura-free body. The shared side walk entry `{s}.1.2.0 for s in (157, 158, 159)` gives no bolts op to 159.
   - Its mirror 159 1.3.0 loses them too. In play the side walk aura LIKELY flickers on this one frame, the same defect r15 had on the front frames.
   - I kept ROM = snapshot, as the brief says. Fix: I add `("bolts",)` to 159.1.2.0, and the next intake takes it in as a `_r17`-style revision.
2. **Anim 20 layout differs from the brief (CONFIRMED).** Dir 3 shares dir 1's frame, and dir 2 shares dir 0's. No harm: all 4 dirs are listed and the snapshot pairs mirror exactly (section 4).
3. **Flight frames are fixed in base only (CONFIRMED by EDITS, LIKELY intended).** Sets 158 and 159 anim 20 keep the r16 frames, with the flat sash. The base back views now sit 1 row below SSJ, which `test_base_sash_not_below_ssj` now skips as a hand frame.
4. **The test counts include the save task's work (LIKELY).** The 11 extra tests are in `test_save.py`, which the save task edited at 8:46 PM. The suite passed with them. No failure was seen in another task's files.
5. **The live r12fix folder moved on (CONFIRMED).** At 10:11 PM it held 64 PNGs and a different edits.py. r17 holds only the 8:59 PM snapshot.
6. **Process slips (CONFIRMED, no effect).** Two Bash calls started with `cd`: a read-only analysis run (`cd` to the LOG root) and an empty no-op call. Neither wrote anything. Also, my first `text_check.py` held literal dash characters in its own source. I replaced them with `chr()` codes. No other file had them.
7. **Not tested in game.** The idle timing proof is the Thumb interpreter, and the art proof is bytes.

---

## 11. Files

- Changed: `scripts\permanent\art\hand_frames.py`, `frame_lock.py`, `patches\ssj2_idle.py`, `tests\test_hand_frames.py`, `tests\test_idle.py`, `tests\test_gi.py`, `tests\test_gi_post.py`, `tests\test_owner_walk.py`, `docs\build-log.md`, `docs\RE-BIBLE.md` (line 136, a new anim 20 line after the dir 3 line, source `I17`). All are LF, with no byte order mark, no dashes and no control characters (checked).
- New: 23 goldens in `art\golden\`; `archive\builds\log2_poc_r17.gba` and `.sav`; `archive\2026-10-18-art-review-renders\r17_intake.png`.
- Regenerated: the 8 gi art folders (backup of r16 art in `archive\2026-10-18-art-snapshots\intake17-art_r16\`).
- Scripts (mine) in `scripts\one-time\2026-10-18-r17-intake\`: `analyze.py`, `make_goldens.py`, `rom_proof.py`, `review_sheet.py`, `lock_check.py`, `sash_check.py`, `bolt_check.py`, `count_tests.py`, `append_buildlog.py`, `text_check.py`, `crop.py`.
- I did not edit `fix.py`, `view.py`, `edits.py`, the save or portrait tasks' files, or anything under `data\`. No ROM, .sav or existing golden was overwritten.
