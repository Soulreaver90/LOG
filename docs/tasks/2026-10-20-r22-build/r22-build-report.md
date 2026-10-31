# r22: dialog portrait id 40, Perfect Cell, from my final art

Base: r21 `a3e9963aee85aef98d0bd013981f7deddf733fb2` (the file hashes to it). Result: `archive\builds\log2_poc_r22.gba`, SHA-1 **`9287672b53f1757d43a46dc01a852f1142f0e115`**, CRC32 `3E8C676E`. The whole suite runs 355 tests, and all pass.

Art used: `art\portrait-sources\remaster\final_r22\cell_40.png`, SHA-1 **`f087e9429597774be1330c63b4cf42fb7fb907f2`**. I read this file after the 9:58 AM overwrite, and nothing was built before the re-read. I hashed it again after the build: same value.

Labels: CONFIRMED means proven by script output, a byte compare or a code run in this session. LIKELY means inferred. SPECULATIVE means not checked.

---

## 1. SHIPPED and PENDING

**SHIPPED**

| Ask | State | Evidence |
|---|---|---|
| "Add it to the game" as dialog id 40 | Done: frame `rom:0x89B5CC`, live block word `rom:0x894F50` | Sections 2, 6 |
| Status twin | None: id 40 has no appearance entry | Section 3 |
| Where id 40 shows | Listed: 40 cutscene records, 11 scene tables | Section 4 |
| Build, save, states | Done | Section 5 |
| Diff proof r21 to r22 | PASS | Section 6 |

**PENDING (mine)**

| Item | Why |
|---|---|
| In-game check | The proof is code runs and bytes. Test plan in section 7. |

---

## 2. Patch change (CONFIRMED)

**Art check (`scripts\one-time\2026-10-20-r22-build\check40.py`, `check40.txt`):**
- 64x64 indexed, 21 indices: 1, 2, 9-15, 23, 25, 30, 31, 37, 43, 89, 120, 132, 167, 211, 252.
- Every index is in the dialog set (ids 26-114), none is 0 or 168, and the PNG palette equals the OBJ palette at each used index. No palette change.
- Indices not in vanilla 40: 37 and 89, as I said. 37 (248,208,64) is used by vanilla dialog ids 26, 31, 32, 43, 75, 76, 82, 111. 89 (80,0,128) is used by 66 and 70.
- The outer 3 px ring (732 px) equals vanilla id 40: **0 pixels differ**. 2142 of 4096 pixels equal vanilla.

**`patches\portrait_remaster.py` (changed):**
- `PORTRAITS` has a seventh entry, 40 `cell_40.png`. `ART_DIR = {65: final_r21, 40: final_r22}`. `VANILLA_IDS = (40, 63, 65, 106)`: the live block word for 40 is checked first and must equal the vanilla word `0x086B7904`.
- **Allocator fit: no new call.** `LATE_IDS = (65, 40)`. The second call writes 65 first (same place as r21, `0x89A5C4`), then 40 at the next free word, `0x89B5CC` (frame 65 + 0x1008). The first call and the r20 part are unchanged. A third call still raises.
- **Does the design scale?** Yes for append-only work: each further late frame is one more tail entry in `LATE_IDS`, placed 0x1008 bytes after the last, with no byte moved. Constraints: the order of `LATE_IDS` is part of the build contract, and nothing may be added to the first call. Cost: the seven frames are not grouped by id. Clean fix if this grows: a reserved portrait region (a fixed gap before `status_portrait` in the allocator, or an allocate-from-top method on `Allocator`). That changes the shared module and moves bytes once, so it needs its own build. I did not change `rom_space.py`.
- **Old frame of 40: dead data.** Vanilla frame `rom:0x6B7904`, type 1, 8 + 1320 packed = **1328 bytes**. Aligned words equal to `0x086B7904` in r21: the vanilla block `0x3ECA74`, `gohan_portraits`' stale block `0x88E470` and the live block `0x894F50`. No other id shares it. It stays in the ROM.

---

## 3. Status twin (CONFIRMED)

- No twin exists. The vanilla table (22 entries) and the r21 live table (23 entries) have no entry with +2 or +3 equal to 40 (`check40.txt`). A test pins this (`test_id_40_old_frame_kept_and_no_status_entry_uses_it`).
- The status page shows nothing for 40 now, and nothing changes there. Id 40 is a dialog-only portrait. No twin was generated.

---

## 4. Where id 40 shows

**Appearance entries:** none (CONFIRMED). Leader and party lines (portrait byte 1-7) cannot show 40, because no appearance entry holds it.

**Cutscene records, types 1-4, portrait byte +3 = 0x28 (CONFIRMED, bytes):** 40 text-validated records, all type 1 or 2, in 11 scene tables (`scenes40.txt`, `scenes40b.txt`, `scenes40c.txt`). The table-to-map step differs by table:

| Scene table | Records (seq) | First line | Map and story point | Label |
|---|---|---|---|---|
| `rom:0x3D1530` (8 words) | `0x083D1220` 2, `0x083D12C0` 3, `0x083D1354` 4, `0x083D1400` 5, `0x083D14EC` 6 | "CELL: I am Cell. Your boring lives are about to get a lot more interesting." | Map 6,16 (entry 160) region 1, cond script `0x083FAC98`: flag 151 set and flag 157 clear, rect (169,193)-(232,248). Cell announces the Cell Games | CONFIRMED (holder word `0x3FACB4`, item `0x083FACA4` in the region list) |
| `rom:0x3E8D98` (28 words) | `0x083E8AA6` 17, `0x083E8CA0` 25 | "CELL: Your ignorance is painful." | Map 14,2 (entry 324) region 0, cond always, rect (313,625)-(592,816). Cell Games arena | CONFIRMED (item `0x08408E98` in the region list) |
| `rom:0x3E93E8` (21 words) | `0x083E9070` 8, `0x083E9148` 10, `0x083E9248` 16, `0x083E9362` 20 | "CELL: Surely you're joking Goku." | Map 14,3 (entry 325), the entry's layout pointer `0x08408F04` | CONFIRMED (word `0x40DAAC`) |
| `rom:0x3E8F50` (5), `0x3E9D4C` (31), `0x3EA400` (32), `0x3EB704` (65), `0x3EC758` (55) | `0x083E8E20`, `0x083E8EDC`; `0x083E9488`-`0x083E9CCE` (6); `0x083EA15C`, `0x083EA250`, `0x083EA3B4`; `0x083EAD70`-`0x083EB3D0` (5); `0x083EB89E`-`0x083EBDF0` (5) | "CELL: I want to make this fight a little more interesting." (Cell vs Goku), "I know I'm hurting you Gohan" (vs Gohan), Cell Jr. scene, "My aim is as good as ever", "These are your last minutes boy!" | Maps 14,2 (first table) and 14,3 (others): the holder items sit inside the address range of those two map entries. The holder word is found, but the item is not in a region list | LIKELY |
| `rom:0x3E6F30` (26), `0x3E7104` (2), `0x3E77B0` (16) | `0x083E6D90` 22; `0x083E6FC0` 2; `0x083E7130`-`0x083E75B4` (6) | "Now, do you understand what I mean by perfection?", "CELL: Impressive, Trunks.", "CELL: All you've done is pump up your muscles" | Map 12,4 (entry 302) and map 12,6 (entry 304) by address range: the Cell and Trunks scenes | LIKELY |

- Raw sweep, second shape (`{x,0,type 1-5,0x28}`, no text check, rom:0x3B0000-0x41FFFF): extra hits `0x083B092B` (type 5, odd), `0x083B527D`, `0x083ED221`, `0x083F3A71`, `0x0840DB05` (type 3, odd addresses), `0x08409B46` and `0x0840A716` (halfword aligned only; records of types 2-4 need 4-alignment). All rejected. A record built at run time would not appear (SPECULATIVE gap), and neither would a script that pushes 0x28 to an ext op, or the Europe ROM.
- The trigger decode for each scene (`0x0800D765` and the factories) is not done here. When a scene fires is LIKELY.

**Which can I reach from my saves or states? (CONFIRMED for the flags, LIKELY for the triggers)**
- Slot 3 (`log2_poc_r22.sav` slot 3 and `.ss3`): Goku leads, Lv 40, flag 191 set, flag 195 clear, map visited bits 294-296 (arena maps 14,1-14,3) unvisited (`log2_save.py info`). The Cell Games arena scenes (map 14,2 and 14,3) have not run in this save. This is the one I can reach: world map, Cell Games Arena (region 25), then maps 14,2 and 14,3.
- Slots 1 and 2: flag 195 set (Cell beaten). The arena scenes were played. They likely do not replay.
- Map 6,16 needs flag 157 clear. All three slots have flag 157 set (flags 148-158 listed). It does not replay without a flag edit.
- Maps 12,4 and 12,6: in all slots the story flags past them are set (LIKELY not to replay).

---

## 5. Build and copies (CONFIRMED)

- Command: `log2_build.py --out archive\builds\log2_poc_r22.gba gohan_gi ssj2_form gohan_portraits status_bonus ssj2_idle cutscene_portraits npc_gi rage_text portrait_remaster status_portrait rage_stats portrait_remaster`. No `LOG_*` env var (count 0). No `file_select_dim`. No palette slot 172 change. The output file did not exist before. Output: `scripts\one-time\2026-10-20-r22-build\build.txt`.
- r22 SHA-1 **`9287672b53f1757d43a46dc01a852f1142f0e115`**, CRC32 `3E8C676E`.
- `docs\build-log.md`: the auto line and one descriptive line appended.
- **Files copied** (each target checked absent first; `cp` without force): `log2_poc_r21.sav`, `.ss1`, `.ss2`, `.ss3` to `log2_poc_r22.sav`, `.ss1`, `.ss2`, `.ss3`. SHA-1 pairs equal: `159601a3`, `177e917c`, `d793ca4d`, `e04c34db`. The r21 files are untouched. No RAM word in the three states names the old id 40 frame or changed ROM (`states.txt`). The states keep r18's CRC32; mGBA logs a "different version" warning only.

---

## 6. Diff proof r21 to r22 (CONFIRMED, `scripts\one-time\2026-10-20-r22-build\rom_proof.py`, `rom_proof.txt`, PASS)

- The in-memory r21 list (id 40 removed through a patched `PORTRAITS` and `LATE_IDS`) equals the r21 file. The in-memory r22 list equals the r22 file. Same size 16777216, header 0x00-0xBF unchanged.
- **4107 bytes differ in 2 contiguous runs; 0 bytes outside the two sites.**

| Region | Bytes differ | What |
|---|---|---|
| `rom:0x894F50`-`0x894F52` | 3 | live block word id 40: `0x086B7904` to `0x0889B5CC` (4th byte `08` equal) |
| `rom:0x89B5CC`-`0x89C5D3` | 4104 | new raw type 0 frame id 40 (`00 00 00 00 00 10 00 00` + 4096 pixels); all 0xFF in r21 |

Id 40 read back from the r22 file equals the PNG (SHA-1 `f087e942...`) pixel for pixel.

**Tests** (`scripts\permanent\tests\test_portrait_remaster.py`, 17 tests, was 13): all seven ids read back equal to their PNGs; id 40 equals the PNG read independently with PIL (21 indices); id 40 ring equals vanilla; id 40 old frame and vanilla block kept and no status entry uses 40; second call changes only the words and frames of 65 and 40 (against the in-memory r20 list), in free 0xFF space; frame 65 stays at `0x89A5C4` and frame 40 is `0x1008` after it; ids 65, 63, 106, 115, 117, 119 words equal r20 outside the two late ids; fail-closed loop covers id 40 in the second call; third call raises. Whole suite: **355 tests OK** (`suite.txt`, run twice, 355 both times). r21 had 351.

---

## 7. My test plan

1. **Easiest: `log2_poc_r22.sav` slot 3 (or `.ss3`).** Goku leads at Dende's Lookout, flag 191 set. Walk to the Cell Games Arena by the world map (region 25), enter map 14,1, then 14,2. The Cell lines in the arena show the new Perfect Cell portrait with the same colors (LIKELY which scene fires first). Frame edge looks as vanilla; new colors are on the face and shading.
2. **Regression look:** Goku base and Super Saiyan status page (entries 19 and 20, ids 63 and 65), Vegeta, Gohan gi art and the Rage page, all as in r21.
3. **Map 6,16 Cell announcement (no save of mine reaches it):** needs `flag-=157` on a test save (SPECULATIVE effect on later story). Not created.

---

## 8. Concerns

1. Not tested in game. The proof is code runs and bytes.
2. The two-call patch list is unchanged from r21. A future build must keep the second call after `rage_stats` and the `LATE_IDS` order (65, 40).
3. Table-to-map holder links for 8 of 11 tables are LIKELY by address range. The CONFIRMED set is maps 6,16, 14,2 and 14,3 (3 tables).
4. Dead data for id 40: 1328 bytes.
5. Indices 37 and 89 are new for Cell, but 10 other vanilla dialog ids use them: no palette change needed.
6. The PNG changed at 9:58 AM. The build and the tests used the new file (SHA-1 above).

**RE bible rows:** `scripts\one-time\2026-10-20-r22-build\bible_rows.md`. I did not edit `docs\RE-BIBLE.md`.

---

## 9. Files

- **Changed:** `scripts\permanent\patches\portrait_remaster.py`, `scripts\permanent\tests\test_portrait_remaster.py`, `docs\build-log.md` (two lines appended).
- **New:** `archive\builds\log2_poc_r22.gba`, `.sav`, `.ss1`-`.ss3`.
- **Scripts and outputs (mine) in `scripts\one-time\2026-10-20-r22-build\`:** `check40.py`/`.txt`, `scenes40.py`/`.txt`, `scenes40b.py`/`.txt`, `scenes40c.py`/`.txt`, `rom_proof.py`/`.txt`, `states.txt`, `build.txt`, `suite.txt`, `bible_rows.md`.
- Not touched: `data\`, `docs\RE-BIBLE.md`, any r21 file, `rom_space.py`, `scripts\one-time\2026-10-20-effects-trace\`, `art\portrait-sources\remaster\anime\`.
