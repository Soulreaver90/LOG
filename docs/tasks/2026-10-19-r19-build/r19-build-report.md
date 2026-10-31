# r19: Rage text says Super Saiyan 2, plus a small frame intake

Base: r18 `046e51ec`. Result: `archive\builds\log2_poc_r19.gba`, SHA-1 `edd3df2eec1df8f73a0d0f93e1afadd7552885fc`. The whole suite runs 316 tests, and all pass.

Labels: CONFIRMED means proven by script output, a byte compare or a code run in this session. LIKELY means inferred. SPECULATIVE means not checked.

---

## 1. SHIPPED and PENDING

**SHIPPED**

| Ask | State | Evidence |
|---|---|---|
| Rage text: "Gohan has transformed" / "into Super Saiyan 2!" | Done, with a one-byte correction to the brief (section 2) | `patches\rage_text.py`, section 3 |
| Reader checks before the patch | PASS | Section 3 |
| Tests for the patch | 10 tests, all pass | Section 4 |
| Frame intake from `snap_r19` | Done: 158 12.0.1, 12.0.2, 12.0.3 | Section 5 |
| Build, save, build line | Done | Section 6 |
| my save states copied and checked | Done | Section 7 |
| Diff proof r18 to r19 | PASS | Section 8 |
| Review sheet | Done, viewed | Section 9 |

**PENDING (mine)**

| Item | Why |
|---|---|
| In-game check of the message | The proof is code runs and bytes. See my test in section 7. |
| `file_select_dim` and the status screen patch | Not in the build, as the brief says. |

---

## 2. Brief correction: the line break is 0x0A, not 0x0B (CONFIRMED mechanism, LIKELY in-game look)

The brief says `0x0B` is a line break inside text. The code says `0x0B` ends the box.

- **Line breaker `sub_0801F7FC`** (args: canvas, text, width, out):
  - `0x0801F842` `cmp r6,#0xa ; beq` returns with done = 0: the line ends, the box goes on.
  - `0x0801F846` `cmp r6,#0xb ; bne` then `0x0801F84A` `mov r4,#0x1 ; str r4,[r3,#0xc]` sets done = 1.
  - `0x0801F82C` a `00` also sets done = 1.
  - The leading loop `0x0801F7FE`-`0x0801F818` skips space, `0x0A` and `0x0B` at the start of the next line.
- **Box text object `sub_0800B8B6`**:
  - `0x0800B93C` stores done at obj +0x1C. When done is set, `0x0800B8C8`-`0x0800B8D4` waits for the button, plays the sound and then reads the byte at the line end (`0x0800B8EC`). If it is not `00`, the box is cleared and a new page starts at that point (`0x0800B8F2`-`0x0800B916`).
- So Cell's "You wretched child!!!" `0B` "NOW TASTE MY TRUE POWER!!!" is two boxes in game (A press between).
- The vanilla ROM has 87 type 1 texts with `0x0B`, all between sentences. Only 2 have `0x0A`, and neither uses it inside the text (one is a leading byte, which the skip loop removes). The coordinator confirmed that the game's own one-box multi-line texts (for example "@#Attribute Bonus" `0A` "Strength: +%d") use `0x0A`.
- With `0x0B`, my test would fail: "into Super Saiyan 2!" would come in a second box after an A press.
- **Decision:** the patch writes `0x0A`. The coordinator accepted this during the run. The revert is one byte: `patches\rage_text.py:25`, `b"\x0a"` to `b"\x0b"`, and the matching tests.
- In-game look is LIKELY only: no vanilla text uses `0x0A` mid-text in a cutscene box. The code run below shows the layout.

**Code run (CONFIRMED, `scripts\one-time\2026-10-19-r19-build\layout.py`, test `LayoutTests`):** the game's `sub_0801F7FC` runs in the test interpreter (test_status `PageCpu` plus `stmia`) with width `0x90` and the dialog font `0x0802CC64` (the word `sub_0800BAB4` stores at canvas +0xC, pool `rom:0xBDA0`).

| Text | Line 1 | Line 2 |
|---|---|---|
| Vanilla Rage (calibration) | "^Gohan has entered Super", width 137, done 0 | "Saiyan Rage!", width 67, done 1 |
| Cell | "You wretched child!!!", width 107, **done 1 at `0B`** | next box |
| New, `0x0A` | "^Gohan has transformed", width 128, done 0 at `0A` | "into Super Saiyan 2!", width 105, done 1 at `00` |
| New, `0x0B` | same line 1, **done 1** (box ends) | second box |
| New, no break byte | "^Gohan has transformed", width 128 | "into Super Saiyan 2!", width 105 |

- The calibration matches the brief's 23 visible characters on line 1 of the vanilla box. The `^` (`0x5E`) after `@` is not a prefix: `dialog_box` strips only `!`, `@` and `#`, so `^` is the first byte the breaker sees.
- Both new lines fit in `0x90` px. Plain word wrap would give the same two lines, so the `0x0A` only pins the break.

---

## 3. Reader evidence and the patch

**Reader checks (CONFIRMED, `listing.py` on the vanilla codemap, `refs.py` on vanilla and r18)**

- **`scene_run` `0x0800B520`:** reads the list at obj +0 with the index at obj +8 (`0x0800B558`-`0x0800B55E`). A word with a nonzero high half is a record pointer. It stores the record's u16 at +0 as the next index (`0x0800B57A`), reads the type at +2 and calls the handler from the table `0x083EC84C` with r1 = the record pointer (`0x0800B57E`-`0x0800B586`). No address range test.
- **`scene_type1` `0x0800B438`:** text = r1 + 4 (`0x0800B43C`), portrait = byte at r1 + 3 (`0x0800B442`), then `dialog_box` `0x0800B1E2`. No range test.
- **`dialog_box` `0x0800B1E2`:** skips a leading `!`, `@`, `#` (`0x0800B224`-`0x0800B244`) and passes the text pointer to `sub_0800BAB4`, which stores it at obj +0x10 (`0x0800BAF8`-`0x0800BAFC`).
- **Text read at use time:** `sub_0800B8B6` reads bytes through obj +0x10/+0x14 from the pointer, one glyph per call, and `sub_0801F7FC` stops at the first `00`. Nothing copies the text to RAM. So a record in the expansion area reads the same as one in the script region, as in the `npc_gi` precedent (three type 0 records at `rom:0x895098`, `0x89516C`, `0x8953D0`).
- **References:** on both vanilla (8 MB) and r18 (16 MB), the only word equal to `0x083EA388` is `rom:0x3EA474`, and the only one equal to `0x083EA3B4` is `rom:0x3EA478`. Aligned and unaligned scans agree. "Super Saiyan Rage!" has one copy, at `rom:0x3EA3A0`.
- **Scene list:** the Cell fight list starts at `rom:0x3EA400` (32 records, ends with `0`), referenced from `rom:0x409094`. The Rage record is list[29] (seq 0x1E), Cell's line is list[30].

**Patch `scripts\permanent\patches\rage_text.py`**

- `:25` the new text: `40 5E` "Gohan has transformed" `0A` "into Super Saiyan 2!" `00` (45 bytes).
- `:38`-`:40` checks before any write: the old record `1E 00 01 00` + old text + `00 00`, the next record head `1F 00 01 28`, and the two list words.
- `:41` refuses a line over 21 characters.
- `:45` `alloc.alloc(49)` (4-aligned), `:46` writes `1E 00 01 00` + the new text, `:47` repoints `rom:0x3EA474`. Notes: `alloc.notes["rage_text"]` = record and size.
- In r19 the record is at `rom:0x895434`, right after the last `npc_gi` record.
- The old record bytes stay. The next record and its word stay.

---

## 4. Tests

- **New: `scripts\permanent\tests\test_rage_text.py`, 10 tests.** It builds the r18 patch list in memory, then `rage_text`.
  - Record: old record untouched; new record bytes, 49 bytes, 4-aligned, in the expansion area, `FF` before; pointer word (old address has no reference left, the new one has exactly `rom:0x3EA474`); next record and its pointer untouched; byte diff only at the word and the record; `apply` fails closed on 6 single-bit changes.
  - Layout (runs the game code): font word; vanilla Rage wraps after "Super"; the new text is two lines in one box; `0x0B` in Cell's record ends the box.
- **Changed for the intake:** `tests\test_hand_frames.py` (baseline r18, section 5) and the comment of `tests\test_owner_walk.py` line 70 (r19 named; the count stays 84).
- **Whole suite:** 316 tests, OK (`scripts\one-time\2026-10-19-r19-build\suite.txt`). r18 had 294. Mine add 10. The other 12 are `test_status_portrait.py`, the status screen task's file. It passed. No failure in another task's file.

---

## 5. Frame intake (CONFIRMED)

- **Snapshot:** `art\hand-fixes\snap_r19\` (`out\` 64 PNGs, `edits.py` SHA-1 `6fda4d07`, and `fix.py`), times kept. `edits.py` is from 12:19 AM. At 9:11 AM the live folder still equals snap_r19 (edits.py `6fda4d07`, 64 `out\` PNGs, all equal by hash).
- **Keys (`scripts\one-time\2026-10-19-r19-build\analyze.txt`):** 64 keys, `out\` equals EDITS, none new, none dropped. Changed against the current golden: exactly 158 12.0.1, 12.0.2, 12.0.3. The other 61 are equal.
- **Pixels (`px_diff.txt`):** 7 pixels, all index 12 (144, 144, 144), the armor boot gray of r18 concern 1:
  - 158 12.0.1 and 12.0.3: (12, 4), (12, 5), (12, 6) to index 35 (120, 48, 0), shoe brown.
  - 158 12.0.2: (2, 9) to index 89 (80, 0, 128), pants purple.
  - The brief says 4 pixels. That is 4 positions; the count is 7 pixels in 3 frames.
- **Sharing:** none of the 3 frames shares its header with another record (no dir 3 twin for anim 12).
- **Goldens:** `make_goldens.py --write` wrote 3 new files and changed none: `golden_gi_ssj_a12_d0_i{1,2,3}_r19.png`. The old plain files stay on disk, out of `HAND` and the lock. The golden folder went from 107 to 110 files.
- **Code:** `scripts\permanent\art\hand_frames.py` `REVISION["gi_ssj_v2"]` = r19 for the 3 keys, docstring names snap_r19. `scripts\permanent\art\frame_lock.py` docstring names r19.
- **Lock:** `frame_lock.py lock --golden --replace`. The old lock moved to `art\locks\golden_20261019-0832`. New lock 84 names. 81 shared names keep their fingerprints (`lock_check.py`). Only old: the 3 plain 12.0.x names. Only new: the 3 `_r19` names. `check --golden` exits 0.
- **Regeneration:** before any change the tree rebuilt r18 byte for byte (`scripts\one-time\2026-10-19-r19-build\r18_repro.gba`, `046e51ec`, own log file), and an unchanged `gi_art`, `gi_post`, `gi_aura` run gave 0 changes in all 8 folders. After the change, `compare_art.py` against the r18 art backup `archive\2026-10-18-art-snapshots\r19-art_r18\`: gi_ssj_v2 pixels 3 (12.0.1, 12.0.2, 12.0.3); the other 7 folders 0; no geometry, sharing, added or removed change.
- **test_hand_frames.py (15 tests, backup `scripts\one-time\2026-10-19-r19-build\test_hand_frames_r18.py.bak`):** snapshot `snap_r19`, earlier keys from `snap_r18`, baseline `log2_poc_r18.gba`. Renamed: `test_no_other_key_differs_from_r18` (no mirrors expected), `test_r19_keys_changed_against_r18` (3 keys), `test_earlier_keys_equal_r18`. The count test expects 3 r19 keys.

---

## 6. Build and save (CONFIRMED)

- Command: `log2_build.py --out archive\builds\log2_poc_r19.gba gohan_gi ssj2_form gohan_portraits status_bonus ssj2_idle cutscene_portraits npc_gi rage_text`. No `LOG_*` env vars. No `file_select_dim` and no status screen patch.
- r19 SHA-1 `edd3df2eec1df8f73a0d0f93e1afadd7552885fc`. r18 unchanged (`046e51ec`).
- No r19 file existed before. `log2_poc_r18.sav` copied to `log2_poc_r19.sav` (SHA-1 `159601a3`, equal).
- `docs\build-log.md`: the auto line and a descriptive line (LF, ASCII, through Python).

---

## 7. My save states

**Copies (CONFIRMED):** `log2_poc_r18.ss1`, `.ss2`, `.ss3` copied to `log2_poc_r19.ss1`-`.ss3`. SHA-1 pairs equal: `177e917c`, `d793ca4d`, `e04c34db`. The r18 files are untouched.

**Header and CRC (CONFIRMED, `scripts\one-time\2026-10-19-r19-build\states.txt`)**

- Each state is a PNG with the state zlib-compressed in the `gbAs` chunk (`state_dump.load_state`), 0x61000 bytes, version magic `0x01000007`.
- Stored title `DBZLGCYGOKU2` and game code `ALFE` equal the r19 cartridge header. r19 does not change the header: the first 0xC0 bytes of r18 and r19 are equal.
- Stored ROM CRC32 `8656B1E5` = r18. r19's CRC32 is `BC0FF228`.
- **What mGBA 0.10.5 does** (`src/gba/serialize.c` `GBADeserialize`, quoted through a fetch of the 0.10.5 tag): a different title or id sets `error = true` ("Savestate is for a different game"). A different `romCrc32` only logs "Savestate is for a different version of the game" with no error. So the states load on r19, with that warning in the log (CONFIRMED from the source text; not run in mGBA).

**No code or RAM layout change (CONFIRMED)**

- The r18 to r19 diff (section 8) is only the list word, a new record in former `FF` space, and the pixel bytes of 3 frames. No code byte, hook stub, pool word or table that a RAM copy is made from changed. `rage_text` writes no RAM and adds no code.
- The exact-byte search found no copy of any changed bytes (r18 or r19 version) in IWRAM, EWRAM or VRAM of any state (`ram_copies.txt`). It cannot see a remapped frame upload (`0x080077E6` through `@0x0300029C` maps each nonzero byte through a table).
- Each changed item is read from ROM at use time: the list word by `scene_run` when it reaches index 29, the text by the box object, the frames by the frame unpacker when the animation shows them.

**What I will see**

- **ss3 is in the Cell fight scene, before the Rage message (CONFIRMED by bytes, LIKELY in game).** On its live stack (sp `0x03007CCC`) the scene runner at `0x03007D70` holds list `0x083EA400` (the Cell fight list), next index 22, and an active handler. list[21] is Gohan's "@ANDROID 16!!!!!!!" line. The Rage record is list[29]. So when the scene reaches it, `scene_run` reads `rom:0x3EA474` from the r19 ROM and shows the new text.
- **ss1 and ss2** hold no pointer into the Cell fight records or list.
- A state saved while a message box is open would keep its text pointer into the old record and finish the old text. The old record stays intact, so that pointer stays valid. None of the three states is in that case.
- Frames already in VRAM at save time show the old pixels until the game uploads that frame again (the next animation step). The search found no raw copy of the 158 anim 12 changes in VRAM (CONFIRMED). That none is in VRAM in any form is LIKELY only.

**My test:** load `log2_poc_r19.ss3` (or play the Cell fight from save slot 3). After "ANDROID 16!!!!!!!", the Rage message should read "Gohan has transformed" with "into Super Saiyan 2!" on the next line in the same box. mGBA may log a ROM CRC warning for the state.

---

## 8. Diff proof r18 to r19 (CONFIRMED, `scripts\one-time\2026-10-19-r19-build\rom_proof.py`, output `rom_proof.txt`, PASS)

- All 64 listed keys equal `snap_r19` pixel for pixel, decoded from the r19 records with flips applied.
- All 1076 records of sets 157-160: no geometry change, no frame header moved, set offsets equal, changed shown pixels exactly 158 12.0.1, 12.0.2, 12.0.3.
- The ROM size is the same. 59 bytes differ in 5 regions (gaps of up to 8 equal bytes joined):

| Region | Bytes differ | What |
|---|---|---|
| `rom:0x3EA474`-`0x3EA476` | 3 | scene list word, `0x083EA388` to `0x08895434` |
| `rom:0x832324`-`0x832334` | 3 | frame data of header `0x8322B8` (158 12.0.1) |
| `rom:0x832552` | 1 | frame data of header `0x8324C0` (158 12.0.2) |
| `rom:0x832734`-`0x832744` | 3 | frame data of header `0x8326C8` (158 12.0.3) |
| `rom:0x895434`-`0x895464` | 49 | new Rage record (`rage_text`) |

- The old record `rom:0x3EA388`-`0x3EA3B7` is equal in r18 and r19. The proof fails any region outside these.

---

## 9. Review

- `archive\2026-10-18-art-review-renders\r19_intake.png` (564x500): set 158 anim 12, r18 row over r19 row, 6x on (191, 255, 7), each frame at its record dx, dy; 12.0.0 unchanged for context, a star marks the r19 keys. I viewed it.
- What the eye sees: in r18, 12.0.1 and 12.0.3 have a gray 3-pixel column at the top right (the trailing boot), and 12.0.2 has a gray pixel at the left. In r19 they are brown shoe and purple pants, like 12.0.0 (LIKELY reads as fixed).

---

## 10. Concerns

1. **The brief's `0x0B` was wrong for this use (CONFIRMED).** See section 2. Patch and tests use `0x0A`, accepted by the coordinator. The in-game look of a mid-text `0x0A` in a cutscene box is LIKELY, not seen.
2. **States carry r18's CRC32 (CONFIRMED).** mGBA logs a warning and loads (from the source; not run).
3. **The blue bar at the top left of 158 12.0.2 is still there (CONFIRMED in the sheet).** It is in r18 too (r18 concern 1 note). Not in this intake.
4. **The test count includes another task's file (CONFIRMED).** `test_status_portrait.py` adds 12 tests, and they pass. Its patch is not in the build. During my run its `test_before_is_r18` (a SHA-1 pin on the in-memory r18 build) disappeared from the file. A pin like that would fail now, because the tree's art changed in r19.
5. **Not tested in game.** The proof is code runs and bytes.

**RE bible rows (for me; I did not edit `docs\RE-BIBLE.md`)**

- "Text control bytes in the dialog box (`sub_0801F7FC`, `sub_0800B8B6`): `0x0A` ends the line in the same box; `0x0B` ends the box (A press, then a new box from the next byte); `00` ends the text. Leading space, `0x0A` and `0x0B` of a line are skipped. Vanilla cutscene texts use `0x0B` 87 times, `0x0A` mid-text never | #text #script | C (code, run) | R19"
- "Dialog line width `0x90` px in font `0x0802CC64` (canvas +0xC, pool `rom:0xBDA0`); glyph width = font[font[c]] + 1; wrap at the last space | #text | C (run) | R19"
- "Cell fight scene list `rom:0x3EA400` (32 records, ref `rom:0x409094`); list[29] = Rage message (seq 0x1E), list[30] = Cell. `scene_run` obj +0 list, +8 next index (= seq of the record run), +0x18 active handler | #script #story | C | R19"
- "Rage text (`rage_text`, r19): record `rom:0x895434` (49 bytes) `1E 00 01 00` `40 5E` "Gohan has transformed" `0A` "into Super Saiyan 2!" `00`; `rom:0x3EA474` repointed; old record `rom:0x3EA388` unreferenced | #text #form char:gohan | C (bytes, tests), L (in game) | R19"

---

## 11. Files

- **New:** `scripts\permanent\patches\rage_text.py`, `scripts\permanent\tests\test_rage_text.py`; 3 goldens `art\golden\golden_gi_ssj_a12_d0_i{1,2,3}_r19.png`; `archive\builds\log2_poc_r19.gba`, `.sav`, `.ss1`-`.ss3`; `archive\2026-10-18-art-review-renders\r19_intake.png`; snapshot `art\hand-fixes\snap_r19\`.
- **Changed:** `scripts\permanent\art\hand_frames.py`, `frame_lock.py` (docstring), `tests\test_hand_frames.py`, `tests\test_owner_walk.py` (comment), `docs\build-log.md`; the lock `art\locks\golden\`.
- **Regenerated:** the 8 gi art folders (r18 backup in `archive\2026-10-18-art-snapshots\r19-art_r18\`).
- **Scripts (mine) in `scripts\one-time\2026-10-19-r19-build\`:** `layout.py`, `refs.py`, `analyze.py`, `make_goldens.py`, `px_diff.py`, `lock_check.py`, `rom_proof.py`, `states.py`, `state_sp.py`, `ram_copies.py`, `review_sheet.py`, `append_buildlog.py`, `text_check.py`. Outputs: `analyze.txt`, `px_diff.txt`, `compare_art.txt`, `suite.txt`, `rom_proof.txt`, `states.txt`, `ram_copies.txt`, baseline and regen logs, `r18_repro.gba`.
- I did not edit `fix.py`, `view.py`, `edits.py`, `docs\RE-BIBLE.md`, the other tasks' files, or anything under `data\`. No ROM, .sav, state or existing golden was overwritten.
