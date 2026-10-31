# One body: Gohan's gi Super Saiyan sets derived from the base body (r29 preview)

Brief: `docs\tasks\2026-10-22-one-body\one-body.md`. Base: r28 `eef01cf6aa37f660bbe0f07b87694d058252499c` (the tree rebuilds it byte for byte in memory before any change, `scripts\one-time\2026-10-22-one-body\repro.py`). Labels: CONFIRMED (C) = proven by a script, test or byte compare in this session; LIKELY (L) = inferred or seen by eye; SPECULATIVE (S) = not checked.

| SHIPPED | Where |
|---|---|
| Pipeline step: 158 and 159 = base body plus the form head | `scripts\permanent\art\gi_one_body.py`, step 5 of `gi_post.py all` |
| New folders | `archive\2026-10-22-gi-v3-preview\gi_ssj_v3\`, `gi_ssj2_v3\`, `gi_ssj2_aura_v3\` |
| Review pack | `archive\2026-10-18-art-review-renders\one_body\` (19 anim sheets, `vanilla_differs.png`, `exceptions.png`, `box.png`, `goldens.png`, `face_variant.png`, `lists.txt`) |
| Preview ROM | `builds\log2_poc_r29_preview.gba`, SHA-1 `8b6b8fbfbea1acde72cd8b1c4fcf649ed5f86626` |
| Saves and states | `log2_poc_r29_preview.sav`, `.ss1`-`.ss5`, `log2_poc_r29_preview_chamber.sav` |
| Diff proof | PASS, section 7 |
| Tests | 455 tests, OK (10 new) |

> [!WARNING]
> **Concerns, in order** (details in sections 2, 4.3 and 9):
> 1. **Head rule deviates from the brief (C).** v3 uses the form's face, not the base face with recolored eyes. The literal rule would change 545 px over 141 keys (158) and 1,131 px over 202 keys (159). The variant is ready as a sheet: `review\one_body\face_variant.png` (`scripts\one-time\2026-10-22-one-body\face_variant.py`).
> 2. **Form neck over the base collar (C).** Inside the form head mask, form pixels that are not hair replace base body pixels: 260 px in 78 keys (158) and 351 px in 100 keys (159). Of these, 111 and 159 px put form neck skin over base gi purple (collar, V-neck rows; 18.0.2-18.0.6 the most, 15-16 px each). My collar edits do not reach those pixels. Fix, not applied: outside the base head, body wins over the form face, hair still wins.
> 3. **Possible head bob (L).** The head offset against the base head changes inside 4 rows of 158 (5.1, 6.1, 7.1, 8.1) and 7 of 159 (2.1, 5.1, 6.1, 7.1, 7.2, 7.3, 8.1), by 1-2 px on one index. Most are back views, where few face pixels exist to match, so it may be measurement noise. 159 7.2.2 and 7.3.2 (side) need an eye check (`a8_checks.txt`).
> 4. **Box keys:** 6 frames need a bigger box than the slot or record allows and stay as today (section 4.3).
> 5. **Anim 21 (revert)** keeps the old body (no base counterpart). The 158 step frames 9.d.1-3 are kept whole, so their body does not follow base edits either.
> 6. **The below-head test is narrower than the brief's wording.** It checks the rows below the lowest head row. Body at head height (arms up in 11.x, the trailing legs in 12.0.x, the fists in 20.x) is covered by `test_flight_has_the_base_sash` for anim 20 only. Concern 2 is the measured gap.
> These were found after the preview was built. Fixing them changes the v3 art, so a fixed preview needs a new ROM name. I did not rebuild.

| PENDING (mine) | Why |
|---|---|
| Review the pack, then decide whether v3 becomes the main line | No main-line build, as the brief says |
| 6 keys that need a bigger box | Section 4.3 |
| 15 (158) and 31 (159) keys where vanilla poses differ | Section 4.2, kept as today |
| Anim 21 (revert) | Section 9 |

---

## 1. Method

This section says how a 158 or 159 frame is made. All work is in object space (record dx, dy and h-flip applied).

1. **Class.** Each key of 158 (`gi_ssj_v2` layout) and 159 (`gi_ssj2_v2` layout) is one of: derived, exception, vanilla pose, box, no base.
2. **Shift (C).** The vanilla form body (set 59 for 158; set 58, else 59, for 159) is aligned on the vanilla base body (set 56) within 2 px, both heads left out. (0, 0) wins ties.
   - Why: many vanilla Super Saiyan frames sit 1-2 px off the base frame, for example the SSJ walk 1 px left. The form head moves by the same shift, so it sits on the base neck as it sits on its own neck in vanilla.
3. **Compose.** Base `gi_base` pixels outside both heads; the shifted form pixels inside them. Where the base head was and the form has nothing, the pixel is transparent.
4. **Box.** Each record keeps its size (w, h, shape bits) and may move dx, dy by up to 2 px, so the body stays where base has it. A frame size never changes, because a bigger frame moves every later allocation of the build (section 7).
5. **Bolts (159).** `gi_aura.aura_folder` bakes the bolts after the derived body, in the brief's order: base body, derived SSJ2 body, bolts.
   - Same seeds (tag `gi_ssj2_aura`).
   - The bolt start points come from today's `gi_ssj2_v2` frame (`ring_pattern`), moved into the new record, so each bolt keeps its screen place.
   - Bolt drift on the new body: 17 of 942 bolt-blue pixels (C, `scripts\one-time\2026-10-22-one-body\a6_kept_bolts.txt`). Cause: the face-box and white-over-bright rules now read the new body.
6. **Pipeline.** `gi_post.py all` runs `one_body` last. `gi_aura.py all` then writes `gi_ssj2_aura_v3` (`V3_OUTPUTS`). A base edit therefore reaches 158 and 159 on the next run. I wrote the v3 folders with `scripts\one-time\2026-10-22-one-body\make_v3.py`, which calls only those two steps. It never ran `gi_post all` or `gi_aura all`, because both rewrite the current folders.

## 2. Head rule

This section defines the head that the form keeps.

- **Form head (C):** the vanilla head mask (`gi_art.head_mask` on the vanilla armor frame of the form). Then four additions on the form's own gi pixels:
  - grown through hair colors (`gi_art.GOLD` plus 16, 43, 45, 131, 142), because the golden SSJ2 head is larger than the set 58 head;
  - shine with 2 or more hair sides;
  - face pixels that the head encloses;
  - the vanilla SSJ2 sparks.
- **Base head (C):** the vanilla set 56 head mask. It is cleared where the form has no pixel.
- **Why vanilla masks:** `head_mask` on a gi frame would take the bare gi arms as face, because both are skin.
- **Face and eyes:** the face comes from the form frame, so the eyes carry the form's teal (64, 65) with no recolor step.
  - Face-skin pixels that differ from base inside the head: 529 in 158 (about 2 per key) and 1,069 in 159 (about 5 per key). C.
  - This deviates from the brief's wording "base face, eyes recolored" (concern 1). The variant sheet `face_variant.png` shows base | v3 | base-face variant for the 6 keys per set with the most change.
- **Form head over base body (C, `scripts\one-time\2026-10-22-one-body\a8_checks.txt`):** where the form head covers a base body pixel, the form wins. By the form pixel's class: hair 510 / 526 px (158 / 159), face 385 / 513, spark 0 / 41, other 33 / 12. The non-hair part is concern 2. I had first called these "mostly back views" without a check; the split above replaces that.
- **Glow ring (L):** 159 anim 9 frames 1-3 (the step glow of set 59) keep the gold ring around the whole body. Its colors are hair colors, so it counts as the form's head effect and sits over the base body edge.
  - Below the head row, the only non-hair differences from base are 8 px in 159 (6.2.3, 6.3.3, 8.2.3, 8.3.3). There, base white attack specks show as the SSJ2 spark blue 191 (Ruling 19). C, `a7_below.py`.
- **Base hair left:** none below the head row (C, same check).

## 3. Exceptions (kept as they are today)

This section lists the brief's exceptions with the anims named.

| Set | Keys | What |
|---|---|---|
| 158 | 9.d.1, 9.d.2, 9.d.3, all 4 dirs (12 keys, 3 PNGs) | SSJ to SSJ2 step frames: golden SSJ2 head, game face, flash ring |
| 159 | anim 0, all 6 records per dir (24 records; 8 body keys) | Idle. Today's 159 idle is the std golden body (`golden_gi_ssj2std_d0-3`, 3:15 PM) with the aura idle records |
| 159 | every aura bolt | `gi_ssj2_aura_v3` bolts (section 1.5) |
| 160 | all | Out of scope, not touched |

- **The "rage" stance (C by data, L as my meaning):** vanilla set 58 draws the fists-out stance in anim 0 (idle) and anim 4 (ki charge, all 16 keys). Set 59 does not.
  - In r28 the 159 idle already shows the std golden body (arms down). So the rage stance I see in 159 is anim 4.
  - Anim 4 stays as today through the vanilla-pose rule (section 4.2).

## 4. Lists

This section gives the counts and every non-derived key. The full lists with pixel counts are in `archive\2026-10-18-art-review-renders\one_body\lists.txt`.

### 4.1 Counts (C, `one_body.json`)

| | 158 `gi_ssj_v3` | 159 `gi_ssj2_v3` |
|---|---|---|
| Keys | 276 | 276 (body keys; the aura folder has 292) |
| Derived | 229 | 219 |
| Exception | 12 | 8 |
| Vanilla pose | 15 | 31 |
| Box | 4 | 2 |
| No base (anim 21) | 16 | 16 |
| Derived PNGs | 137 of 159 | 125 of 159 |
| Derived keys whose body changed after the shift | 188 (2,163 px) | 197 (3,422 px) |
| Derived keys with a body shift (not 0) | 43 | 44 |
| Records whose dx or dy moved to hold the frame | 37 | 12 |
| Records whose shown frame differs from r28 (ROM) | 188 | 199 |

- The 159 pixel counts compare with `gi_ssj2_v2`, the body before today's hand frames and bolts. Section 5 compares the hand-fixed keys with what the game shows today.
- 2 derived 158 keys (2.0.2, 4.0.2) lose 1 floating effect speck at the box edge (`clipped_specks`).

### 4.2 Vanilla differs (kept as today; side by side in `vanilla_differs.png`)

Rule: shape residual of the vanilla bodies after the best shift is 25 px or more. The data has a gap between 18 px (158 4.1.3) and 28 px (16.0.3). C, `scripts\one-time\2026-10-22-one-body\a3_shift.txt`.

| Set | Keys | Count |
|---|---|---|
| 158 | 16.0.1-16.0.3, 16.1.1-16.1.4, 16.2.1-16.2.4, 16.3.1-16.3.4 | 15 |
| 159 | the same 15 keys of anim 16, plus anim 4 (4.d.0-4.d.3, 16 keys) | 31 |

- Near misses that I derived (shape residual 1-18 px): 0.1.x and 0.2.x/0.3.x (1-2), 1.1.0, 2.0.0, 2.0.2, 4.0.2 (6-8), 4.1.3 (18), 6.0.0, 7.0.0 (7), 11.d.1 (6), 13.0.3 (5), 12.1.x (1). L that these are the same pose: I looked at 4.1.3 and 16.0.3 side by side.

### 4.3 Box (needs a bigger box; kept as today; `box.png` shows the unclipped frame in red)

| Set | Key | Clipped px | Why |
|---|---|---|---|
| 158 | 4.1.3 | 3 hair | head moves up 1 row: 33 rows |
| 158 | 6.0.0, 7.0.0 | 4 hair each | 33 rows |
| 158 | 13.0.3 | 2 body | 17 wide in a 16-wide record |
| 159 | 6.0.0, 7.0.0 | 3 hair each | 33 rows |

- **Brief conflict (C):** the brief allows boxes up to 64x64. The player slot holds 0x400 bytes (`log2_sprites.SLOT_BYTES`, refused by `build_set`), which is 32x32 at 8bpp. So 33-row frames cannot be built at all.
- **No growth by design:** a 16-wide record could grow to 32x32 within the slot. That would move every later allocation (set 159, set 160 and the later patches), and the r28 diff proof would no longer be limited to 158/159.
- My options per key: clip the hair tip, grow the record (allocations move), or keep today's frame.

## 5. Changed goldens (requirement 5; `goldens.png`, `lists.txt`)

This section lists every locked golden of 158/159 whose frame changes. "On screen" counts all pixels. "After the shift" moves the new frame back by the body shift and leaves bolt blue out, so it counts what changed beyond the 1 px move. C.

| Golden | Key | On screen | After the shift |
|---|---|---|---|
| `golden_gi_ssj_d0` | 158 0.0.0 | 303 | 0 (shift (1, 0)) |
| `golden_gi_ssj_a1_d0_i0`, `_i2` | 158 1.0.0, 1.0.2 | 260, 276 | 2, 1 |
| `golden_gi_ssj_a3_d{0,1,2}_i3` | 158 3.d.3 | 3 each | 3 each |
| `golden_gi_ssj_a1_d2_i0` | 158 1.2.0 | 2 | 2 |
| `golden_gi_ssj_a5_d0_i2` | 158 5.0.2 | 266 | 0 |
| `golden_gi_ssj_a8_d0_i3` | 158 8.0.3 | 14 | 14 |
| `golden_gi_ssj_a8_d2_i2` | 158 8.2.2 | 4 | 4 |
| `golden_gi_ssj_a12_d0_i0`, `_i1_r19`, `_i2_r19`, `_i3_r19` | 158 12.0.0-3 | 247-270 | 15, 15, 12, 15 |
| `golden_gi_ssj2std_a1_d0_i0_r17`, `_i2_r17` | 159 1.0.0, 1.0.2 | 296, 299 | 12, 10 |
| `golden_gi_ssj2std_a3_d{0,1,2}_i3` | 159 3.d.3 | 3 each | 3 each |
| `golden_gi_ssj2std_a13_d0_i3_r17` | 159 13.0.3 | 5 | 5 |
| `golden_gi_ssj2std_a1_d2_i0_r18` | 159 1.2.0 | 2 | 2 |
| `golden_gi_ssj2std_a5_d0_i2` | 159 5.0.2 | 323 | 0 |
| `golden_gi_ssj2std_a8_d0_i3` | 159 8.0.3 | 19 | 19 |
| `golden_gi_ssj2std_a8_d2_i2` | 159 8.2.2 | 4 | 4 |
| `golden_gi_ssj2std_a12_d0_i0`-`_i3` | 159 12.0.0-3 | 292-296 | 23, 21, 16, 21 |

- **Unchanged:** `golden_gi_ssj_d1`-`d3`; 158 13.0.3 (box) and 16.2.1, 16.2.4 (vanilla pose); 159 16.2.1, 16.2.4; `golden_gi_ssj2std_d0`-`d3` (idle, exception).
- **The SSJ idle golden:** `golden_gi_ssj_d0` is the base golden body 1 px to the left, pixel for pixel. The 1 px offset of the SSJ goldens is the vanilla set 59 offset. It is not a separate body.
- **No golden file was written.** The lock check (`frame_lock.py check --golden`) exits 0.

## 6. Hand frames (requirement 6)

This section says which hand frames remain and how the r19 fix carries.

- **All 32 v2 hand frames of 158 and 159 are body fixes (C, `scripts\one-time\2026-10-22-one-body\a5_hand.txt`).** Inside the form head they differ from the converter frame by 0 px, except 12.0.x: 1 px in 158 and 4-5 px in 159, where the base fix puts the trailing legs at the hair edge.
- **New `hand_frames.DERIVED`** (the derived sets' hand list):
  - `gi_ssj_v3`: none. Kept 158 keys copy `gi_ssj_v2`, which already holds its hand frames.
  - `gi_ssj2_aura_v3`: 16.2.1 and 16.2.4. These are kept as today (vanilla pose), and `gi_ssj2_v2` lacks their hand frames.
  - `HAND` (v2) is unchanged, because it still builds the frozen r28 folders and the 84-name lock. `GOLDEN_HAND` stays 64 names (each listed once).
- **Boot gray (r19 fix, 158 12.0.1-3 armor gray to shoe and pants):** it now carries through base. Base 12.0.x has no index 12, so the derived 158 12.0.x have none (test `test_boot_gray_carries_through_base`). C.

## 7. Preview ROM and diff proof

This section proves the preview differs from r28 only in 158/159.

- **Build:** `log2_build.py --out builds\log2_poc_r29_preview.gba --list`, with `LOG_GI_SSJ=gi_ssj_v3` and `LOG_GI_SSJ2=gi_ssj2_aura_v3` set in the process environment.
  - SHA-1 `8b6b8fbfbea1acde72cd8b1c4fcf649ed5f86626`. An in-memory build gives the same SHA-1.
  - `docs\build-log.md` got the auto line and one note line.
  - No r29 file existed before. r28 files are unchanged (section 10).
- **Copies (byte equal, no-clobber):**

| From | To | SHA-1 (first 12) |
|---|---|---|
| `log2_poc_r28.sav` | `log2_poc_r29_preview.sav` | `159601a37659` |
| `log2_poc_r28.ss1`-`.ss5` | `log2_poc_r29_preview.ss1`-`.ss5` | `177e917c7fe6`, `4487d1d348f2`, `e04c34dbbbf3`, `570ba9bb9457`, `8062e3d9b624` |
| `log2_poc_r28_chamber.sav` | `log2_poc_r29_preview_chamber.sav` | `dc95c334de0d` |

- **Proof (C, `scripts\one-time\2026-10-22-one-body\diff_proof.py`, output `diff_proof.txt`, PASS):**
  - Set offsets of 157-160 are equal. Every record keeps its address and frame header. Sets 157 and 160 are equal record for record (geometry and shown pixels).
  - Every 158/159 record shows exactly its v3 art frame (decoded, flips applied) with the v3 geometry.
  - 49 records moved dx or dy (37 in 158, 12 in 159); the list is in `diff_proof.txt`. No w, h or shape changed.
  - 11,651 bytes differ in 870 regions, `rom:0x820943`-`0x869AD9`:
    - 824 regions in 158/159 frame data;
    - 46 regions in the 12-byte records of moved 158/159 keys.
  - Nothing else differs. The ROM size is the same.
- **States (L):** the states load as before (the r19 report gives the mGBA CRC warning). Frames already in VRAM show the old pixels until the next upload.

## 8. Tests

This section lists the test changes. The whole suite ran 455 tests, OK (`scripts\one-time\2026-10-22-one-body\suite.txt`).

- **New `scripts\permanent\tests\test_one_body.py` (10 tests):**

| Test | What it checks |
|---|---|
| `test_kept_keys_are_listed` | The exception, vanilla-pose, box and no-base lists, written out in the test |
| `test_body_below_the_head_equals_base` | Every derived key equals 157 below the head row. Allowed: form hair, and the SSJ2 spark recolor 2 to 191 |
| `test_flight_has_the_base_sash` | Anim 20, all 16 keys, both sets: every base sash pixel is sash |
| `test_boot_gray_carries_through_base` | No index 12 in base or derived 158 12.0.x |
| `test_kept_keys_show_todays_frame` | Kept keys equal today's `gi_ssj_v2` / `gi_ssj2_aura` |
| `test_frames_keep_size_name_and_order` | Same PNG names, order, sizes, shape bits; dx, dy move at most 4 |
| `test_aura_adds_only_bolts_to_the_body` | `gi_ssj2_aura_v3` = `gi_ssj2_v3` plus bolt colors on derived keys |
| `test_hand_lists` | `DERIVED` contents; `GOLDEN_HAND` has no duplicate |
| `test_fresh_run_equals_the_folders` | A fresh run in a temp folder equals the 3 v3 folders byte for byte |
| `test_ring_on_its_own_body_changes_nothing` | `ring` = body reproduces `gi_ssj2_aura` byte for byte |

- **Each test fails on today's frames (C):** 158 of the 229 derived 158 keys and 161 of the 219 derived 159 keys differ from base below the head in `gi_ssj_v2` / `gi_ssj2_aura`. 8 flight keys per set lack the base sash.
- **Changed:** `tests\test_gi_post.py` `test_chain_is_repeatable` copies `gi_base` too and compares `gi_ssj_v3`, `gi_ssj2_v3` (header updated).

## 9. Open points

This section lists the decisions and risks left for me.

1. **Box keys (section 4.3):** clip, grow or keep, per key.
2. **Vanilla-pose keys (section 4.2):** anim 16 in both sets and anim 4 in 159 keep today's converter bodies. 158/159 16.2.1 and 16.2.4 keep their carried hand fixes. I decide whether to force base.
3. **Anim 21 (revert, 16 keys per set):** it has no base counterpart, so it keeps the old body at the vanilla offset. The 1-row sash drop at 21.d.3 (shared-body report 4.4) is still there.
4. **Face source and neck (concerns 1 and 2):** both are small changes in `gi_one_body.compose`. Each changes the v3 art, so a new preview needs a new ROM name.
4a. **Step frames 9.d.1-3 (158):** kept whole as the brief says. If "keep their golden SSJ2 head" means the head only, their body could be derived too.
5. **Main line:** `gohan_gi` still defaults to `gi_ssj_v2` / `gi_ssj2_aura`. Adopting v3 means changing those defaults and their test (`test_gi_post.GohanGiDefaultTests`), and retiring `HAND["gi_ssj_v2"]` and `HAND["gi_ssj2_aura"]` with a lock replace.
6. **Chamber save pairing (L):** mGBA pairs a save by ROM name. `log2_poc_r29_preview_chamber.sav` needs a ROM copy named `log2_poc_r29_preview_chamber.gba`, as I made for r28. I did not make one. The newer `log2_poc_r28_chamber2.*` files are not in the brief and were not copied.
7. **Not tested in game.** The proof is bytes and pixels.

## 10. Process, files and slips

This section lists what I wrote, what I left alone and where I broke a rule.

- **Old folder moved aside (C):** `archive\2026-10-22-gi-v3-preview\gi_ssj2_v3\` already existed: an unused 2026-10-17 aura experiment from `golden\work_r3\aura.py`, read by no build. I renamed it to `archive\2026-10-17-gi-art-rounds\gi_ssj2_v3_r3aura_20261017\` (178 files with its subfolders, unchanged) before writing the new `gi_ssj2_v3`. `work_r3\aura_review.py` still names the old path.
- **Untouched (C, `protect.py check`, 2008 files):** `gi_base`, `gi_ssj`, `gi_ssj2`, `gi_ssj_v2`, `gi_ssj2_v2`, `gi_ssj2_aura`, `gi_rage`, `gi_rage_aura`, `golden`, the moved folder, and every `log2_poc_r28*` file.
  - Nothing written under `data\`. No ROM, .sav or state overwritten.
  - `docs\RE-BIBLE.md`, `inject.py`, `portraits\` and `r12fix\` not touched.
- **Code changed** (backups in `scripts\one-time\2026-10-22-one-body\backup\`):
  - `gi_post.py`: step 5 `one_body`, header.
  - `gi_aura.py`: `ring`, `ring_pattern`, `V3_OUTPUTS`, header.
  - `hand_frames.py`: `DERIVED`, `KEPT_159`, `SOURCE`, FORM v3 names, `GOLDEN_HAND` dedupe, header.
  - `tests\test_gi_post.py`.
- **New code:** `gi_one_body.py`, `tests\test_one_body.py`.
- **Work scripts** in `scripts\one-time\2026-10-22-one-body\`: `a1_survey.py` to `a8_checks.py`, `face_variant.py`, `keysheet.py`, `view.py`, `repro.py`, `work_run.py` (work copy in `archive\2026-10-18-art-snapshots\r29-art\`), `make_v3.py`, `review_sheets.py`, `diff_proof.py`, `protect.py`, `append_buildlog.py`, `fix_line.py`, `text_check.py`.
- **Bible rows:** `scripts\one-time\2026-10-22-one-body\bible_rows.md`.
- **Text check (C):** every file above is ASCII and LF, with no BOM and no em or en dash (`text_check.py`).
- **Slips (C, no lasting effect):**
  - One Bash call began with `cd <LOG root> 2>/dev/null;` before a unittest run. The run used absolute paths and wrote nothing.
  - One edit to `hand_frames.py` went through a Python heredoc, not Python. The shell collapsed the backslashes of one comment line into control bytes. I repaired that line with `fix_line.py`, and the text check now passes.
