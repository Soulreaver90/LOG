# One-body fix: collar, head position, revert and step frames (r32 preview)

Brief: `docs\tasks\2026-10-23-one-body-fix\one-body-fix.md`. Base: r32 `185dcc766e9a563270a74d5926426e98e412c02b`; the tree rebuilt it byte for byte in memory before any change (`scripts\one-time\2026-10-23-one-body-fix\repro.py`). Labels: CONFIRMED (C) = proven by a script, test or byte compare in this session; LIKELY (L) = inferred or seen by eye; SPECULATIVE (S) = not checked.

| SHIPPED | Where |
|---|---|
| Pipeline step changed: head rule, step frames, revert 21.d.3, 159 flight head anchor | `scripts\permanent\art\gi_one_body.py` (still step 5 of `gi_post.py all`); `gi_aura.V4_OUTPUTS`; `hand_frames` v4 names |
| New folders | `art\gi_ssj_v4\`, `gi_ssj2_v4\`, `gi_ssj2_aura_v4\` |
| Review pack | `archive\2026-10-18-art-review-renders\one_body_v4\` (19 anim sheets, one per anim with frames in `gi_base`, `gi_ssj_v4` or `gi_ssj2_aura_v4`; anims 10, 15 and 19 have none there, `collar.png`, `step.png`, `revert.png`, `revert_owner.png`, `anchor.png`, `head_rows.png`, `changed.txt`) |
| Preview ROM | `builds\log2_poc_r32_preview2.gba`, SHA-1 `7fc0ec2dfd5f30e42a44fe6d044d3640b643f7f0` (name differs from the brief, see concern 1) |
| Saves, states, chamber2 pair | `log2_poc_r32_preview2.sav`, `.ss1`-`.ss5`, `log2_poc_r32_preview2_chamber2.sav`, `log2_poc_r32_preview2_chamber2.gba` |
| Diff proof | PASS, section 6 |
| Tests | 562 tests, OK (559 on r32 before; 3 new) |

| PENDING (mine) | Why |
|---|---|
| Review the pack, then decide whether v4 becomes the main line | No main-line build, as the brief says |
| Anim 21 indices 0-2: 6 frames, 24 keys (12 per set), no base pose | Section 4, `revert_owner.png` |
| 159 flight head moved down 2 rows (8 keys) | Section 3, `anchor.png`: I moved it, I judge by eye |
| Delete or keep the stale first preview `log2_poc_r32_preview*` (9 files) | Concern 1 |

> [!WARNING]
> **Concerns, in order:**
> 1. **The preview has a new name (C).** I built `log2_poc_r32_preview.gba` (SHA-1 `fa593f2b...`) first. The full suite then failed: the flight head anchor put 1 brown pixel on the sash in 159 20.0.x and 20.2.x. Fixing that changed the v4 art, and the brief forbids overwriting a ROM, .sav or state. So the fixed build is `log2_poc_r32_preview2`. The first preview is stale in 12 records of 159 (20.0.x, 20.2.x, and 12.0.x, whose anchor I then removed). I did not delete it.
> 2. **The 159 flight anchor goes past the brief's "rows that bob" (C measured).** The golden SSJ2 head sits 2 rows above the vanilla head in 20.0.x and 20.2.x at every index. The new collar rule then showed the base chin and mouth under the raised face (8 holes per key). I moved those heads down to the vanilla place.
> 3. **159 12.0.x is 1 row high too, and I kept it (C).** Moved down, the taller golden face puts its open mouth on the base collar line. These are my goldens `golden_gi_ssj2std_a12_d0_i0`-`_i3`; v4 shows them exactly as v3. `anchor.png` shows both rows.
> 4. **The irises win over the base collar (L, not measured per pixel).** In 158 and 159 7.2.3 and 7.3.3 the vanilla SSJ head sits about 1 row lower than base, so the lower iris pixel lands on the collar line. I kept the eye whole, so the collar shows about 1 px less in those 4 keys. The same 4 keys also get 1 px of form body under base hair (concern 5). Check both at 6x in `anim_07.png`.
> 5. **Form body behind base hair (L, my eye).** Where base hair covered the body and the form head does not, the form body fills the gap: 63 px in 35 keys of 158 and 32 px in 20 keys of 159 (23 / 15 px in the collar band, 40 / 17 px of arms and sleeves by the head). The most are 5 px in 8.2.1 and 8.3.1 of both sets. Per-key counts: field `gi_under_hair` in `one_body.json` of each v4 folder. This is how v3 filled them too.
> 6. **The r29 "worst collar keys" 18.0.2-18.0.6 were mostly face shading.** Set 56 anim 18 shades the face with the gi outline navy 211. The real collar fix lands on the back views and on 159 flight.

---

## 1. Head-region rule (task 1)

This section states which pixel wins where. All work is in object space after the body shift (and the flight head anchor, section 3).

- **On top:** form head pixels in `ON_TOP` win over everything except the base sash: hair (`HAIR`), shine, sparks, the step flash ring, and the irises 64, 65, 203. So the hair and the eyes stay whole.
- **Base gi (`torso`):** base pixels in `BODY` colors (gi 87, 88, 89, 211, 215; sash 24-27; wristbands 72, 77, 195, 167; boots 34, 35) whose 8-connected part reaches below the lowest row of the vanilla set 56 head mask. These stay, collar included, except under `ON_TOP`. The sash never changes.
  - Why "reaches below the head": set 56 anim 18 shades the face with 211, and 11.x draws its pupils in 211. Those parts sit inside the head rows, so they are face (C, pixel dumps).
- **Face:** every other form head pixel wins over every other base pixel, as in v3. The form's own body never shows there: a BODY color in the form head is dropped, except a 195 beside an iris (the 18.x SSJ eyes use 195 with 203, C).
- **Base head left over:** a base head pixel that the form head does not cover is cleared. A form pixel there shows ("leak"), unless it is form body:
  - base neck skin under the form gi stays (`neck_kept`: 3 px in 158, 104 px in 159);
  - where base hair covered the body, the form body fills the gap (`gi_under_hair`: 63 / 32 px, concern 5);
  - a cleared base pixel that the new frame encloses on 4 sides stays, so no 1 px hole opens (`pits_kept`: 13 / 22 px).
- **Faces:** each form keeps its own face, as I decided.

### Collar counts (C, `scripts\one-time\2026-10-23-one-body-fix\s8_checks.py`, output `s8_checks_v4.txt`)

| Over the derived keys | 158 v3 | 158 v4 | 159 v3 | 159 v4 |
|---|---|---|---|---|
| Base gi pixels shown as form skin (neck over collar) | 91 | 0 | 110 | 0 |
| Form gi pixels where base has none (form collar over the base neck or chest) | 78 | 0 * | 314 | 0 * |
| Base gi pixels changed by anything but `ON_TOP`; base sash pixels changed | not 0 | 0; 0 | not 0 | 0; 0 |
| Face pixels the base gi now covers (`face_lost`) | - | 91 | - | 110 |
| New enclosed holes against v3 | - | 0 | - | 0 |
| Irises lost against the head source | - | 0 | - | 0 |

\* Outside the named exceptions: form body where base hair covered the body (63 / 32 px) and 195 eye pixels (10 / 0 px).

- The 159 v3 worst keys were flight 20.0.x and 20.2.x: 30 px of form gi each over the base chest and chin. v4 shows the base body there.
- Before and after of the worst v3 keys: `collar.png` (10x head crops: base | v3 158 | v4 158 | v3 159 | v4 159): 16.1.0, 8.3.1, 8.2.1, 7.1.2, 6.1.2, 2.1.2, 20.0.0, 20.2.0, 13.1.1, and 18.0.2 last.
- The brief's 111 / 159 px (r29) used a different class split (any form face pixel over the base body). By the gi-only measure above, v3 had 91 / 110.

## 2. Head position (task 2)

This section says whether the head moves against base from frame to frame.

- **Method (C):** for every derived key, the irises of the derived frame against the irises of the vanilla form frame at the body shift (`s7_head_vs_vanilla.py`, output `s7_v4.txt`). Same form, same eye drawing, so hair shape adds no noise. Back views have no eyes; there I tracked each head within its own form (`s4_bob_frames.py`).
- **Result (C for front and side):** in every front and side derived key of 158, and of 159 outside 12.0.x, the derived head sits exactly where the vanilla form head sits on its body. So every move against base in those rows is the vanilla form's own motion.

| Row (r29 concern 3) | Finding | Label |
|---|---|---|
| 158 5.1, 6.1, 7.1, 8.1; 159 2.1, 5.1, 6.1, 7.1, 8.1 (back views) | Vanilla bob: the move against base equals the vanilla 59/58 move against 56 at each index. Kept | L (no eyes) |
| 159 7.2, 7.3 (side, the brief's eye check) | Vanilla bob: the derived irises match vanilla at every index. Kept. Set 58 draws the head about 1 px off set 56 at index 2 and 1 row lower at index 3 | C (follows vanilla), L (size of the move) |
| 159 20.0.x, 20.2.x (flight) | Not a bob: the golden head sits 2 rows above vanilla at every index. Anchored (0, 2) | C |
| 159 12.0.x | 1 row above vanilla at every index. Kept (concern 3) | C |

- The head-mask check also flags 159 2.2.3, 2.3.3, 20.1.0, 20.3.0 by 1 px. By eye at 9x (`scripts\one-time\2026-10-23-one-body-fix\look\159_head_weak.png`), the 20.1 head is steady; this is set 59 hair against the golden hair. Not changed. L.
- `head_rows.png` shows the flagged rows at 8x: base | v4 158 | v4 159 | set 56 | set 59 | set 58.

## 3. Head anchor table

This section lists the explicit anchor table: `gi_one_body.HEAD_ANCHOR`, pinned by `test_pinned_lists`.

| Set | Keys | Head move | Why |
|---|---|---|---|
| 159 | 20.0.0-3, 20.2.0-3 | (0, 2) | Transplanted golden head 2 rows high; v4 showed the base chin and mouth under it |

- 20.1.x and 20.3.x (back) are not anchored.
- Removing an entry undoes its move on the next run.

## 4. Revert and step frames (task 3)

This section gives the new derivations and my list.

- **158 anim 9 indices 1-3 (step to SSJ2), 12 keys, 3 PNGs (C):** now derived. Each takes the base body of the same key with the golden SSJ2 head, the game face and the flash ring of `gi_ssj_v2`. All 3 PNGs have status `derived` (no shared fallback), and the box holds them (0 px clipped). Test `test_step_frames_keep_the_golden_head` checks that every golden hair pixel of the head is in place. `step.png`: base | v2 today | v3 | v4.
  - The flash ring around the shoulders and arms is `ON_TOP`, so it stays over the base outline. L that this is the intended look.
- **Anim 21 (revert), by vanilla body shape (C, `s5_revert.py`):** each index shows one frame in all 4 dirs.

| Index | Best set 56 key | Shape residual | Result |
|---|---|---|---|
| 21.d.3 (standing, hair black) | 0.0.0 (0.0.1 ties with the same body) | 1 | Derived on base 0.0.0 (`POSE_MATCH`), 4 keys per set. The 1-row sash drop is gone |
| 21.d.0-2 (power down) | 0.0.0 | 26-27 | No clear match (the vanilla-pose range starts at 25). Kept as today |

- **my list: 6 frames, 24 keys** (21.d.0-2 in 158 and in 159). `revert_owner.png`: vanilla set 59 | set 56 0.0.0 | base 0.0.0 | 158 today | 159 today. `revert.png` shows all 4 indices in v3 and v4.

### Counts (C, `one_body.json`)

| | 158 `gi_ssj_v4` | 159 `gi_ssj2_v4` |
|---|---|---|
| Derived | 245 (v3 229) | 223 (v3 219) |
| Exception | 0 (v3 12) | 8 |
| Vanilla pose | 15 | 31 |
| Box (me: keep) | 4 | 2 |
| No base (21.d.0-2) | 12 (v3 16) | 12 (v3 16) |
| Keys whose frame differs from v3 | 65, 513 px | 90, 1,890 px (body folder) |

- The per-key list with pixel counts is `archive\2026-10-18-art-review-renders\one_body_v4\changed.txt`.

## 5. Goldens and hand frames

This section says what happens to the locked frames.

- **No golden file was written.** `frame_lock.py check --golden` exits 0 (C).
- **Locked keys whose frame changed against v3 (C):** 158 1.0.0 (`golden_gi_ssj_a1_d0_i0`) and 159 1.0.0 (`golden_gi_ssj2std_a1_d0_i0_r17`), 1 px each, by the collar rule. Every other locked key of 158/159 (the hand-frame keys and the 158 idle) shows the v3 frame.
- `hand_frames.DERIVED`, `SOURCE` and `FORM` name `gi_ssj_v4` (no hand frames) and `gi_ssj2_aura_v4` (16.2.1, 16.2.4). `GOLDEN_HAND` is unchanged (64 names).

## 6. Preview ROM and diff proof

This section proves the preview differs from r32 only in 158/159.

- **Build (C):** `scripts\one-time\2026-10-23-one-body-fix\build_preview.py log2_poc_r32_preview2`: `build_list.txt` in memory with `LOG_GI_SSJ=gi_ssj_v4`, `LOG_GI_SSJ2=gi_ssj2_aura_v4`, every file written with exclusive create. SHA-1 `7fc0ec2dfd5f30e42a44fe6d044d3640b643f7f0`; a second in-memory build gives the same SHA-1 (`repro.py`). `docs\build-log.md` got a build line and a note line for each of the two previews; the preview2 note says it replaces the first.
- **Copies (exclusive create, byte equal):**

| From | To | SHA-1 (first 12) |
|---|---|---|
| `log2_poc_r32_preview2.gba` | `log2_poc_r32_preview2_chamber2.gba` | `7fc0ec2dfd5f` |
| `log2_poc_r32.sav` | `log2_poc_r32_preview2.sav` | `159601a37659` |
| `log2_poc_r32.ss1`-`.ss5` | `log2_poc_r32_preview2.ss1`-`.ss5` | `177e917c7fe6`, `4487d1d348f2`, `e04c34dbbbf3`, `570ba9bb9457`, `8062e3d9b624` |
| `log2_poc_r32_chamber2.sav` | `log2_poc_r32_preview2_chamber2.sav` | `8b0b74f4896b` |

- `log2_poc_r32_chamber2.gba` is a byte copy of `log2_poc_r32.gba` (C), so the preview2 chamber2 ROM is a byte copy of preview2.
- **Proof (C, `scripts\one-time\2026-10-23-one-body-fix\diff_proof.py`, output `diff_proof.txt`, PASS):**
  - Set offsets of 157-160 are equal; every record keeps its address and frame header; sets 157 and 160 are equal record for record.
  - Every 158/159 record shows exactly its v4 art frame with the v4 geometry. 210 (158) and 208 (159) records show other pixels than r32.
  - 49 records moved dx or dy (listed in `diff_proof.txt`); no w, h or shape changed.
  - 12,767 bytes differ in 934 regions, `rom:0x820943`-`0x869AD9`: 888 in 158/159 frame data, 46 in moved 158/159 records. Nothing else differs; the ROM size is the same.
- **The first preview** (`fa593f2b...`) fails the same proof in exactly 12 records: 159 12.0.x and 20.0.x, 20.2.x (C).
- **States (L):** they load as before; frames already in VRAM show old pixels until the next upload. Not tested in game.

## 7. Tests (task 4)

This section lists the test changes. The whole suite ran 562 tests, OK (`scripts\one-time\2026-10-23-one-body-fix\suite_after.txt`; 559 OK on r32 before, `suite_before.txt`).

- **`tests\test_one_body.py` (13 tests, v4 paths):**

| Test | What it checks |
|---|---|
| `test_kept_keys_are_listed` | Exception, vanilla-pose, box and no-base lists, written out |
| `test_pinned_lists` (new) | `KEPT_BOX` = my 6 keys; 158 has no exception; `POSE_MATCH` = 21.d.3 to 0.0.0 at residual 8 or less; `HEAD_ANCHOR` written out |
| `test_collar_and_neck_rows_are_base` (new) | Every row of every derived key: each base gi pixel is unchanged unless the new pixel is `ON_TOP`; the sash never changes; no form gi shows (named exceptions: where base hair covered the body, a 195 eye pixel). The collar band (head bottom -2 to +3) holds base gi in every derived key except the lying frames 3.d.2-3, listed |
| `test_step_frames_keep_the_golden_head` (new) | 158 9.d.1-3 are derived, with the golden hair in place |
| `test_body_below_the_head_equals_base` | Now uses the base key and the head shift |
| `test_flight_has_the_base_sash`, `test_boot_gray_carries_through_base`, `test_kept_keys_show_todays_frame`, `test_frames_keep_size_name_and_order`, `test_aura_adds_only_bolts_to_the_body`, `test_hand_lists`, `test_fresh_run_equals_the_folders`, `test_ring_on_its_own_body_changes_nothing` | As in v3, on the v4 folders |

- **The new collar test fails on v3 (C by count):** v3 shows 91 / 110 base gi pixels as skin and 78 / 314 form gi pixels.
- **`tests\test_gi_post.py`:** `test_chain_is_repeatable` compares `gi_ssj_v4` and `gi_ssj2_v4`.

## 8. Process and files

This section lists what I wrote and what I left alone.

- **Code changed** (backups in `scripts\one-time\2026-10-23-one-body-fix\backup\`): `gi_one_body.py` (rule, tables, header), `gi_post.py` (header), `gi_aura.py` (`V4_OUTPUTS`, header), `hand_frames.py` (v4 names), `tests\test_one_body.py`, `tests\test_gi_post.py`.
- **v4 folders** were written by `scripts\one-time\2026-10-23-one-body-fix\make_v4.py`, which runs only `gi_one_body.run_all` and `V4_OUTPUTS`. `gi_post all` and `gi_aura all` never ran. A work copy in `archive\2026-10-18-art-snapshots\obfix-art\` equals them byte for byte.
- **Untouched (C, `protect.py check`):** 6,667 files hashed before any change (the art folders `gi_base`, `gi_ssj`, `gi_ssj2`, the v2, v3 and aura folders, `golden`, `locks`, `portraits`, `r12fix`, `review\one_body`, every file under `builds` and `data\`).
  - 1 changed: `scratch\test-roms\build-log-test.md`. The test suite writes it on every run (`test_build`, the patch tests); the baseline run did too.
  - 18 new: the 9 first-preview files and the 9 preview2 files.
  - No ROM, .sav or state was overwritten. `docs\RE-BIBLE.md`, `inject.py`, `portraits\` and `r12fix\` were not touched.
- **Work scripts** in `scripts\one-time\2026-10-23-one-body-fix\`: `s1_collar.py`-`s8_checks.py` (s1-s3 ran on the v3 code before the change), `look.py`, `review_v4.py`, `build_preview.py`, `diff_proof.py`, `repro.py`, `protect.py`, `make_v4.py`. Bible rows: `scripts\one-time\2026-10-23-one-body-fix\bible_rows.md` (tag `OBF`).
- **Text check (C):** every file I wrote is ASCII and LF, with no BOM and no em or en dash.
- **Slips (C, no lasting effect):**
  - Several edits did not go through the Write or Edit tool: `sed -i` on `hand_frames.py`, `gi_aura.py`, `gi_post.py`, `look.py` and `review_v4.py`, and Python heredoc scripts that rewrote parts of `test_one_body.py`, `s8_checks.py`, `review_v4.py` and `gi_one_body.py`, and created `diff_proof.py` from the r29 copy. Two `sed` patterns with backslashes did not match; I fixed those lines with an in-place edit.
  - My first Bash call began with `cd /dev/null 2>/dev/null;`. It fails, and nothing ran in another folder. Every other call used absolute paths.
