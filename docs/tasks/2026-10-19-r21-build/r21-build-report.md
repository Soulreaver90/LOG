# r21: dialog portrait id 65, Goku Super Saiyan, from my final art

Base: r20 `9b52833447b38db0e2b3b2c7b374b5ce389cc5a7` (full value confirmed by hashing `log2_poc_r20.gba`). Result: `archive\builds\log2_poc_r21.gba`, SHA-1 **`a3e9963aee85aef98d0bd013981f7deddf733fb2`**, CRC32 `002C3138`. The whole suite runs 351 tests, and all pass.

Labels: CONFIRMED means proven by script output, a byte compare or a code run in this session. LIKELY means inferred. SPECULATIVE means not checked.

---

## 1. SHIPPED and PENDING

**SHIPPED**

| Ask | State | Evidence |
|---|---|---|
| "Put it in the game as dialog portrait id 65" | Done: `patches\portrait_remaster.py`, raw frame `rom:0x89A5C4`, live block word `rom:0x894FB4` | Sections 2, 5, 7 |
| Status twin and status page | Said: twin is 15, the page now shows 65. No twin generated | Section 3 |
| Where id 65 shows | Listed: 3 cutscene records, 1 appearance entry | Section 4 |
| Build, save, states | Done | Section 6 |
| Diff proof r20 to r21 | PASS | Section 7 |

**PENDING (mine)**

| Item | Why |
|---|---|
| In-game check | The proof is code runs and bytes. Test plan in section 8. |
| Decision on the two-call patch list | Section 2 explains why `portrait_remaster` is listed twice. |

---

## 2. Patch change (CONFIRMED)

**Art check (`scripts\one-time\2026-10-19-r21-build\check65.py`, `check65.txt`):**
- `goku_ssj_65.png` is 64x64 indexed, 22 indices: 2, 9-13, 23, 28, 32, 33, 44, 57, 91, 92, 113-116, 128, 149, 225, 233.
- Every index is in the dialog set, none is 0 or 168, and the PNG palette equals the OBJ palette at each used index. No palette change.
- Index 28 (248,184,184) is the only index vanilla 65 lacks. 15 vanilla dialog ids use it: 27, 29, 36, 37, 42, 43, 48, 53, 55, 64, 79, 84, 89, 94, 111.
- The outer 3 px ring (732 px) equals vanilla id 65: **0 pixels differ**. Overall 1996 of 4096 pixels equal vanilla.

**`patches\portrait_remaster.py` (changed):**
- `PORTRAITS` has a sixth entry, 65 `goku_ssj_65.png`, last in the dict. `ART_DIR = {65: final_r21}`; the five r20 ids still read `final_r20`. `VANILLA_IDS` is now (63, 65, 106). The live block word for 65 is checked first: it must equal the vanilla word `0x086BDE20`.
- It writes the same raw type 0 frame `{0, 0x1000, pixels}` and repoints the block word, like 63, 106, 115, 117 and 119.
- **Decision (please confirm): the patch runs twice.** The allocator only moves forward. The r20 frames end at `0x89A490`, where the `status_portrait` pool starts. A sixth frame in the first call would move the pool, the paint code, the page copy `bl paint`, the `rage_stats` apply and the Rage vtable word (about 0x1008 bytes). That would break "r21 differs from r20 only at the id 65 frame and its block word". So `LATE_IDS = (65,)` is written by a second call, listed after `rage_stats`. The first call equals r20 byte for byte. A third call raises "already ran twice". `rom_space.py` is unchanged. Other choice I rejected: an allocate-from-top method on `Allocator` (a shared-module change and a reserved region at the end of the ROM).
- Frame 65 sits at `rom:0x89A5C4`, the first free word after the `rage_stats` apply (`0x89A55C` + 0x68).

**Old frame of 65: dead data (CONFIRMED by aligned-word scan, `check65.txt`).** The vanilla frame `rom:0x6BDE20` is a type 1 frame, header 8 + 1224 packed = **1232 bytes**. Aligned words equal to `0x086BDE20` in r20: 3 (the vanilla block `rom:0x3ECAD8`, `gohan_portraits`' stale block `rom:0x88E4D4`, the live block `rom:0x894FB4`). In r21: 2, both in unreferenced blocks. No halfword-aligned hit. No other id shares the frame.

---

## 3. Status twin (CONFIRMED by table and by a test run of the page)

- Vanilla and r20 live table (23 entries): only **entry 20** has +2 = 65. Its +3 is **15**. Entry 20 is Goku Super Saiyan (set 61). Entry 19 (Goku base, set 60) is 63 and 14. Entry 19 +4 = 20 and entry 20 +4 = 19, so Goku moves between them by transform.
- With `status_portrait` the page reads +2. For entry 20 it shows id 65: the new PNG pixel for pixel, in the OBJ colors (test `test_status_page_shows_the_dialog_art`, entry 20). In r20 the same page showed the old art (test `test_goku_super_saiyan_entry_pairs_65_with_twin_15`).
- The twin 15 frame (`rom:0x6B0F18`, 1196 packed + 8 = 1204 bytes) has no reader now. It stays in the ROM. No twin was generated.
- Dead data total for id 65: 1232 + 1204 = 2436 bytes.

---

## 4. Where id 65 shows

**Appearance entries (CONFIRMED):** vanilla and r20 live table, entry 20 only (`scripts\one-time\2026-10-19-r21-build\scan65.txt`, `check65.txt`). Every portrait() caller, not only the dialog box, shows the new art: the dialog box, `sub_08018C72` and the scouter (CONFIRMED in r20 from the callers of `@0x0800BDCC`).

**Cutscene records, types 1-4, portrait byte +3 = 0x41 (CONFIRMED, bytes):**

| Record | Seq | Type | Text | Scene table | Map and story point |
|---|---|---|---|---|---|
| `0x083D375C` | 19 | 2 | "Alright, have it your way. But I wouldn't bank on it if I were you." | `rom:0x3D37BC`, 20 records | Map 7,1 (Southern Continent, entry 177) region 1, condition flag 76 clear, rect (-15,289)-(376,328), item `0x083FC070`. Android 19 and 20 meet Goku and Piccolo, Goku turns Super Saiyan. Seq 20 sets flag 76 |
| `0x083D3A70` | 9 | 2 | "GOKU: Uggghhh... What's happening? *cough* *cough*" | `rom:0x3D40C8`, 42 records | Map 7,15 (Southern Continent, entry 191) region 0, condition always, rect (-15,-7)-(952,768), item `0x083FD4E4`. Goku's heart virus attack in the Android 19 fight |
| `0x083D3ADC` | 13 | 1 | "I feel so weak... can't... give... up..." | same table (slot `rom:0x3D40F8`) | same as above |

- The holder shape is CONFIRMED by `regions_177_191.txt`: the item data +0 holds each scene table pointer (`0x083D37BC`, `0x083D40C8`).
- When the scenes fire is LIKELY: trigger `0x0800D765` is not decoded here. Map 7,1 needs flag 76 clear. Flag 76 is **set in all three save slots** (the flag list reads 73-100), so the 7,1 scene does not replay from any of my saves. The 7,15 scene has the condition "always"; whether its records guard themselves is SPECULATIVE.
- Raw sweep, second shape (`{x,0,type 1-5,0x41}`, no text check, rom:0x3B0000-0x41FFFF): 4 more hits, all rejected. `0x083F41E6` is type 4 but not 4-aligned. `0x083FBD71` and `0x083FBD85` are at odd addresses. `0x0841BF71` is type 5 (no portrait byte) at an odd address. A record built at run time would not appear.
- **Leader and party lines (LIKELY):** a record with portrait byte 1-7 resolves through the leader or party appearance +2. Any such line spoken while Goku is in entry 20 shows 65. The 7,15 scene has two such lines (seq 30, 32, text "VEGETA: ...", byte 1). Which lines occur with Goku leading is not enumerated.
- Not covered (SPECULATIVE): a script that pushes 0x41 to an ext op, and the Europe ROM.

---

## 5. Tests

| File | Tests | What |
|---|---|---|
| `tests\test_portrait_remaster.py` (changed) | 13 (was 7) | All six ids read back from the ROM equal their PNGs; id 65 equals my PNG read independently with PIL (22 indices); id 65 outer 3 px ring equals vanilla; index rule for six PNGs; first call changes only the five r20 words and frames; **second call changes only the id 65 word and its 0x1008-byte frame, in free (0xFF) space, other words equal r20**; frame 65 follows `rage_stats`; old frames, twins 116/118/120/15 and the vanilla block kept; status page for entries 19, **20**, 8, 9, 5, 22, 4, 2; entry 20 pairs 65 with 15 and r20 showed the old art; r19 Rage twin; fails closed for every id (both calls, bad index in both calls); a third call raises |

Whole suite: **351 tests OK** (`scripts\one-time\2026-10-19-r21-build\suite.txt`). r20 had 345; the file gained 6. No failure in another file. No test pins an r20 offset or hash that the change moved.

---

## 6. Build and copies (CONFIRMED)

- Command: `log2_build.py --out archive\builds\log2_poc_r21.gba gohan_gi ssj2_form gohan_portraits status_bonus ssj2_idle cutscene_portraits npc_gi rage_text portrait_remaster status_portrait rage_stats portrait_remaster`. No `LOG_*` env var. No `file_select_dim`. Output file did not exist before.
- r21 SHA-1 **`a3e9963aee85aef98d0bd013981f7deddf733fb2`**.
- `docs\build-log.md`: the auto line and a descriptive line.
- **Files copied** (each target was checked absent first; no `-Force`): `log2_poc_r20.sav`, `.ss1`, `.ss2`, `.ss3` to `log2_poc_r21.sav`, `.ss1`, `.ss2`, `.ss3`. SHA-1 pairs equal: `159601a3`, `177e917c`, `d793ca4d`, `e04c34db`. Byte equality confirmed again by `scripts\one-time\2026-10-19-r21-build\states.py`. The r20 files are untouched.
- No RAM word in the three states names the old id 65 frame or changed ROM (`states.txt`). The states keep r18's CRC32, as in r19 and r20; mGBA logs a "different version" warning only.

---

## 7. Diff proof r20 to r21 (CONFIRMED, `scripts\one-time\2026-10-19-r21-build\rom_proof.py`, `rom_proof.txt`, PASS)

- The in-memory r20 list equals the r20 file. The in-memory r21 list equals the r21 file. Same size, header 0x00-0xBF unchanged.
- **4107 bytes differ in 2 contiguous runs; 0 bytes outside the two sites.**

| Region | Bytes differ | What |
|---|---|---|
| `rom:0x894FB4`-`0x894FB6` | 3 | live block word id 65: `0x086BDE20` to `0x0889A5C4` (the 4th byte, `08`, is equal) |
| `rom:0x89A5C4`-`0x89B5CB` | 4104 | new raw type 0 frame id 65 (`00 00 00 00 00 10 00 00` + 4096 pixels); all 0xFF in r20 |

---

## 8. My test plan

1. **Easiest: `log2_poc_r21.ss2`.** Goku leads in Super Saiyan (appearance entry 20, set 61; `states65.txt`). Open Start, then status. The portrait must be the new art (anime-frame Goku SSJ with the lit skin) in the dialog colors. Page flip to the other characters: Vegeta and Gohan show their mid art as in r20.
2. **Dialog, same state:** talk to anyone whose line uses the leader's portrait. Goku in Super Saiyan shows the new art (LIKELY which NPC does).
3. **From `log2_poc_r21.sav` slot 3** (Goku leader, Lookout, entry 19 base): transform Goku to Super Saiyan, open the status page. Same art. Goku base shows the mid art from r20 (id 63).
4. **Cutscene records (no save of mine reaches them):** map 7,1 and map 7,15 are early Android 19/20 scenes. Reaching them needs a test save: `log2_save.py set <in> <out> 3 map=7,15,1 pos=... flag-=76` writes a new file (I did not create one; flag edits may break later story state, SPECULATIVE).
5. **Regression look:** Goku base dialog, Vegeta, Gohan gi art, the Rage status page (gi SSJ2) and the Cell Rage +20 all as in r20.

---

## 9. Concerns

1. **Not tested in game.** The proof is code runs and bytes.
2. **Two-call patch list** (section 2) is a design choice. The r21 build command differs from r20 by one extra trailing `portrait_remaster`. Any later build that adds ids must keep this order or accept moved addresses.
3. **Scenes are not reachable from my saves** (flag 76 set; the other scene is story-gated or needs a flag edit). The status page in ss2 is the check that works today.
4. **Dead data:** 2436 bytes for id 65 (old frame and twin 15), plus the 24 KB from r20.
5. **Index 28** (248,184,184) shows on the lit skin. Vanilla Goku SSJ never used it; 15 other dialog ids do, so no palette change was needed.
6. **Process slip:** Two Bash calls and four PowerShell calls started with `cd`, against the brief. Later calls used absolute paths. No file was affected.
7. **Mid-state in `ss2`:** none. ss2 holds Goku in entry 20 and the status page rebuilds its portrait on open (CONFIRMED from the page code in r20, LIKELY in mGBA).

**RE bible rows:** `scripts\one-time\2026-10-19-r21-build\bible_rows.md` (6 rows). I did not edit `docs\RE-BIBLE.md`.

---

## 10. Files

- **Changed:** `scripts\permanent\patches\portrait_remaster.py`, `scripts\permanent\tests\test_portrait_remaster.py`, `docs\build-log.md` (two lines appended).
- **New:** `archive\builds\log2_poc_r21.gba`, `.sav`, `.ss1`-`.ss3`.
- **Scripts and outputs (mine) in `scripts\one-time\2026-10-19-r21-build\`:** `scan65.py`/`.txt`, `scenes65.py`/`.txt`, `scenes65b.py`/`.txt`, `regions_177_191.txt`, `check65.py`/`.txt`, `states65.py`/`.txt`, `states.py`/`.txt`, `rom_proof.py`/`.txt`, `lint.py`, `recs65.txt`, `build.txt`, `suite.txt`, `bible_rows.md`.
- Not touched: `data\`, `docs\RE-BIBLE.md`, any r20 file, `rom_space.py`, `docs\ledger\progress.md`, `scripts\one-time\2026-10-19-portrait-from-anime\anime\`.
