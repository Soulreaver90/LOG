# Inject tool: one command for a portrait or a palette entry

Brief: `docs\tasks\2026-10-20-inject-tool\inject-tool.md`. Base: r22 `9287672b53f1757d43a46dc01a852f1142f0e115` (the file hashes to it, and the old patch list rebuilds it byte for byte). Result: `archive\builds\log2_poc_r23.gba`, SHA-1 **`397b2a9b3298b2c429d8600e2d2e7b4c01768471`**, CRC32 `EC0374DC`. The whole suite runs **375 tests, all OK**.

Labels: CONFIRMED means proven by script output, a byte compare or a code run in this session. LIKELY means inferred. SPECULATIVE means not checked.

---

## 1. SHIPPED and PENDING

**SHIPPED**

| Ask | State | Evidence |
|---|---|---|
| "One table" for portraits | `art\tables\portraits.json`, 7 ids, PNGs copied byte for byte | Section 2 |
| "One table for palette entries" | `art\tables\palette.json`, empty, writes both ROM copies | Section 2 |
| "One patch", fixed region, no moves | `patches\art_inject.py` replaces both `portrait_remaster` calls | Section 3 |
| "One command" | `scripts\permanent\art\inject.py portrait / palette / check / list` | Section 4 |
| Save state safety | Code byte-identical r22 to r23; states scan clean | Section 5 |
| Tests | 19 + 18 new tests; suite 375 OK | Section 6 |
| First run as the proof | r23 built by the tool in **1.07 s** end to end | Section 7 |
| Docs | `art\tables\README.md` | Section 8 |

**PENDING (mine)**

| Item | Why |
|---|---|
| In-game check of r23 | The proof is bytes and code runs. r23 must look exactly like r22. |
| Slot 172 color | The palette table is empty, as the brief says. `inject.py palette 172 248,224,208` adds it. |

---

## 2. Tables (CONFIRMED)

**`art\tables\portraits.json`:** dialog id to `{"png": "portraits/NNN_name.png", "note": ...}`. Seven entries, each PNG copied from the file r22 used. The SHA-1 of each copy equals its source.

| Id | Art copy | Source (r22) | SHA-1 |
|---|---|---|---|
| 40 | `040_cell_40.png` | `final_r22\cell_40.png` | `f087e942...` (the brief's value) |
| 63 | `063_goku_mid_A.png` | `final_r20\goku_mid_A.png` | `c008893a...` |
| 65 | `065_goku_ssj_65.png` | `final_r21\goku_ssj_65.png` | `df36e996...` |
| 106 | `106_vegeta_mid_A.png` | `final_r20\vegeta_mid_A.png` | `284cdb8a...` |
| 115 | `115_gohan_ssj_mid_A.png` | `final_r20\gohan_ssj_mid_A.png` | `72dfffa0...` |
| 117 | `117_gohan_ssj2_mid_A.png` | `final_r20\gohan_ssj2_mid_A.png` | `c96a9e27...` |
| 119 | `119_gohan_base_mid_A.png` | `final_r20\gohan_base_mid_A.png` | `7088a3d2...` |

**`art\tables\palette.json`:** OBJ index to `[r, g, b]`. Empty. One entry writes `rom:0x1DA6C8` + 2i (BGR555) and `rom:0x3ECBA4` + 3 x (256 + i) (RGB888). A test proves that entry 172 = (248,224,208) changes exactly the 5 bytes the palette-slot report named (`rom:0x1DA820` `9F 6B`, `rom:0x3ED0A8` `F8 E0 D0`). No code change is needed for a new entry.

**Rules (`scripts\permanent\art\art_tables.py`):**
- A PNG is 64x64 and opaque. It can be indexed or RGB.
- Each color maps by value to an OBJ index (palette table applied). The index must be one a vanilla dialog portrait uses (182 indices) or one the palette table sets, never 0 or 168.
- The vanilla OBJ palette has no duplicate color (CONFIRMED), so the map is one to one. A palette entry whose color another allowed index already has is refused.
- An indexed PNG whose palette equals the OBJ palette at each used index keeps its indices. Value mapping the 7 table PNGs as RGB gives the same bytes (test).
- At most 64 colors (the `status_portrait` pool).
- The outer 3 px ring must equal the frame the id shows without the table: vanilla for ids up to 114, the `gohan_portraits` art for 115/117/119, word 59 for 121. All 7 table PNGs pass with 0 differing pixels.
- Valid ids: 26-121, except the status twins 116, 118, 120 (BG palette). Ids 1-7 are leader and party lookups.

---

## 3. Patch and region (CONFIRMED)

**`patches\art_inject.py`** reads both tables (or the copy `inject.py` stages in `alloc.notes["art_input"]`):
1. Palette entries go to both ROM copies. It checks first that the two copies agree.
2. Each table id gets a raw type 0 frame `{0, 0x1000, pixels}` at **`slot(id) = rom:0xF00000 + 0x1008 x id`**, and its live block word (`rom:0x894EAC` + 4 + 4 x id) points at it.
3. One allocation of 0x5028 bytes (`LEGACY_GAP`, left 0xFF) where the old first call put five frames. This keeps `status_portrait` and `rage_stats` at their r22 addresses.

**Design choices:**
- **Slot per id, not append order.** The brief suggested "slot per id, append-only". I made the slot a function of the id alone. Order in the table, removals and later additions can never move a frame, and no slot list must be kept.
- **The region is outside the allocator.** `log2_build.ART_REGION = (0xF00000, 0x100000)`, and `EXPANSION` now ends at `rom:0xEFFFFF`. No allocation moved: the cursor was at `0x89C5D4`. The patch also checks that no allocation overlaps the region and that each slot is 0xFF.
- **Fail closed.** Every check runs before the first write: notes present, `rom:0xBE10` and the hook pool name the `npc_gi` block, each block word still names the frame earlier patches gave it, pixels valid, slots free. A second run raises.
- **`gohan_portraits`:** I left it unchanged. It still writes its own 115-120 frames, and the table owns 115, 117 and 119 through the live block, as `portrait_remaster` did. Moving its art out would move every later allocation (sets, status code, Rage).
- **`portrait_remaster`:** removed from the build and deleted with its test. Backups are in `scripts\one-time\2026-10-20-inject-tool\backup\`. Its still-valid checks are ported to `tests\test_art_inject.py`.
- **Build list:** new file `scripts\permanent\build_list.txt` (`art_inject` where the first call was). `log2_build.py --list` builds it: `py -3 -I scripts\permanent\log2_build.py --list --out scratch\test-roms\list.gba --log scratch\test-roms\list-log.md` gave the r23 SHA-1 `397b2a9b...` (test outputs deleted). `log2_build` also gained `assemble()` and `apply_patches()`; `build()` behaves as before.

---

## 4. Command (CONFIRMED)

| Command | Does |
|---|---|
| `py -3 -P scripts\permanent\art\inject.py portrait <id> <png> [--snap] [--note TEXT]` | Check, stage, build the next ROM, verify, then write |
| `py -3 -P scripts\permanent\art\inject.py palette <index> <r,g,b>` | Same for one palette entry |
| `py -3 -P scripts\permanent\art\inject.py check <png> [id] [--snap]` | Validate only (about 0.5 s) |
| `py -3 -P scripts\permanent\art\inject.py list` | Print the tables, slots and the next build name |

**Flow of `portrait` and `palette`:**
1. Refuse if a `LOG_*` environment variable is set, or if any target file (`log2_poc_rN.gba`, `.sav`, `.ss*`) exists.
2. Build the list up to `art_inject` in memory. Check the PNG against that ROM: size, colors, 64-color cap, ring. An off-palette color is listed with its nearest index (the first 10 colors by count, then a total). `--snap` maps them. Example: my `cell_owner_wip2.png` reports `(4, 5, 5) x23 px, nearest index 1 (0, 0, 0)`, the same fix I made by hand.
3. Stage the new table in memory and finish the build.
4. **Verify:** every table portrait reads back equal to its pixels through the live block, at its slot, with a raw header. Every palette entry reads back in both copies. Every byte that differs from the previous `log2_poc_rN.gba` must lie in a slot, a block word, a palette site, or a freed old frame (an old raw frame that is now all 0xFF). Any other byte refuses the build. Only the id the command names may show new pixels (`palette`: none). Another id may only move to its slot with the same pixels, which covers the one-time move from the r22 layout. So a table PNG edited by hand is refused, not built silently.
5. Only then write: the art copy (my bytes if the PNG is already in stored form, else a normalized indexed PNG), the table, the ROM, copies of the latest `.sav` and `.ss*` (exclusive create, never overwrite), and one line in `docs\build-log.md`.

Nothing is written when a check fails (tests prove it for a bad PNG, a bad palette entry, an existing state name and an unexpected diff).

---

## 5. Save state safety (CONFIRMED for bytes, LIKELY in mGBA)

**Code addresses before and after (`scripts\one-time\2026-10-20-inject-tool\layout_proof.py`, `layout_proof.txt`, PASS):**
- The in-memory r22 list (with the backed-up `portrait_remaster`) equals the r22 file. The in-memory r23 list equals the r23 file.
- `alloc.notes` of all 10 other patches are equal: `gohan_gi`, `ssj2_form`, `gohan_portraits`, `status_bonus`, `ssj2_idle`, `cutscene_portraits`, `npc_gi`, `rage_text`, `status_portrait`, `rage_stats`.
- All 891 allocations by other patches are identical in offset and size.

| Patch site | r22 | r23 |
|---|---|---|
| `npc_gi` live block | `rom:0x894EAC` | `rom:0x894EAC` |
| `rage_text` record | `rom:0x895434` | `rom:0x895434` |
| Portrait frames | 5 frames `rom:0x895468`-`0x89A48F`, 2 frames `rom:0x89A5C4`-`0x89C5D3` | `LEGACY_GAP` `rom:0x895468` + 0x5028 (0xFF); slots `rom:0xF28140`-`0xF783BF` |
| `status_portrait` pool, paint | `rom:0x89A490`, `rom:0x89A4D0` | `rom:0x89A490`, `rom:0x89A4D0` |
| `status_portrait` page sites | `rom:0x8948D4`, `rom:0x89491C` | same |
| `rage_stats` apply, vtable word | `rom:0x89A55C`, `rom:0x24E4C` | same |
| Allocator end | `rom:0x89C5D4` | `rom:0x89A5C4` |

**States (`scripts\one-time\2026-10-20-inject-tool\states.py`, `states.txt`):**
- r23 `.sav`, `.ss1`-`.ss3` equal the r22 files byte for byte.
- The stored ROM CRC32 is still r18's `8656B1E5` (mGBA header +0x08). mGBA logs a "different version" warning only, as for r19-r22.
- No IWRAM or EWRAM word in the three states names a byte that changed from r22 to r23, or the live block.

**Answer: an r22 state should work on r23 (LIKELY).** Every code and data byte outside the portrait frames and block words is identical, and the scan is clean. Not run in mGBA.

**Future injects:** a slot depends only on its id, and code never moves. So a state from build N works on build N+1 after any portrait or palette inject (CONFIRMED by the stable-layout tests, LIKELY in mGBA).

---

## 6. Tests (CONFIRMED)

| File | Tests | What |
|---|---|---|
| `tests\test_art_inject.py` (new) | 19 | Build list; all 7 ids read back equal to their PNGs (read with PIL); 65 and 40 copies equal my files (SHA-1 for 40); rings equal the pre-table frames; RGB copies of the 7 PNGs map to the same bytes; index rule; **code addresses equal r22** (notes, gap, no allocation in the region); art alone changes only slots and words; disk and staged tables build the same ROM; **adding id 94 changes only slot 94 and word 94**, every other byte equal; **replacing 63 changes one byte of its slot**; **palette writer, both copies** (exact 5 bytes); empty table writes no palette byte; a palette entry makes its index usable; status page shows the table art for entries 19, 20, 8, 9, 5, 22, 4, 2; old frames, twins, vanilla block kept, gap 0xFF; fail-closed (8 bad inputs and a changed word for every id, ROM and allocator unchanged); second run and missing notes raise; slot frames unpack as raw |
| `tests\test_inject.py` (new) | 18 | **Table round trip** (the saved JSON equals the committed file); build name and state file matching; diff and classify; check accepts my PNG and its RGB twin; **refuses wrong size, off-palette (with nearest index; `--snap` passes), a changed frame, 65 colors, transparency, id 116**; `portrait` adds id 94 and builds r2, copies `.sav` and `.ss1`, stores an indexed PNG, adds one log line, diff only slot and word; replacing 63; `palette 172` writes both copies and the table; never overwrites and writes nothing when refused; a failed check writes nothing; an unexpected diff (a changed code byte in the previous ROM) is refused; **a hand-edited table PNG is refused** for `portrait 40` and `palette 172`, nothing written; `LOG_*` refused; `list` |
| `tests\test_portrait_remaster.py` | removed (17) | Pinned the two-call offsets; ported checks above |

Whole suite: **375 tests OK** (`scripts\one-time\2026-10-20-inject-tool\suite.txt`). r22 had 355: minus 17 removed, plus 19 and 18 new. The command tests run against a temporary folder and never touch `builds`, the real tables or `docs\build-log.md`.

---

## 7. First run as the proof (CONFIRMED)

Command, from the LOG root, with the table already holding the 7 ids:

```
py -3 -P scripts\permanent\art\inject.py portrait 40 art\portrait-sources\remaster\final_r22\cell_40.png
```

- **Timing: 1.07 s end to end** (PowerShell stopwatch around the command; the tool itself printed 0.8 s). `check` alone takes about 0.5 s.
- Output: `archive\builds\log2_poc_r23.gba`, SHA-1 **`397b2a9b3298b2c429d8600e2d2e7b4c01768471`**. Copies: `log2_poc_r22.sav`, `.ss1`, `.ss2`, `.ss3` to the r23 names. One line in `docs\build-log.md`. Log in `scripts\one-time\2026-10-20-inject-tool\r23_inject.txt`.
- Portrait pixels changed: none.

**Diff r22 to r23: 57477 bytes in 16 runs, 0 bytes outside the expected sites** (the tool's verify step and `layout_proof.py` agree):

| Region | Bytes differ | What |
|---|---|---|
| `rom:0x894F50`, `0x894FAC`, `0x894FB4`, `0x895058`, `0x89507C`, `0x895084`, `0x89508C` | 3 each | live block words 40, 63, 65, 106, 115, 117, 119 (the 4th byte `08` is equal) |
| `rom:0x895468`-`0x89A48F` | 20520 | r22 frames 63, 106, 115, 117, 119, now 0xFF (`LEGACY_GAP`) |
| `rom:0x89A5C4`-`0x89C5D3` | 8208 | r22 frames 65 and 40, now 0xFF (free space after `rage_stats`) |
| `rom:0xF28140`, `0xF3F1F8`, `0xF41208`, `0xF6A350`, `0xF73398`, `0xF753A8`, `0xF773B8` | 4104 each | new slots 40, 63, 65, 106, 115, 117, 119 |

A dry run in a scratch copy (after the verify rule was tightened) gave the same 57477-byte move from r22, and the same inject again gives a 0-byte diff. An earlier dry run showed that `palette 172 248,224,208` gives exactly the 5 palette bytes. The dry run outputs are deleted.

---

## 8. Docs

`art\tables\README.md`: the tables, the five commands, one example, the check rules, the slot rule and the no-overwrite rule.

**RE bible rows:** `scripts\one-time\2026-10-20-inject-tool\bible_rows.md` (sections 5, 5a, 11; source tag `INJ`). I did not edit `docs\RE-BIBLE.md`.

---

## 9. Concerns

1. **Not tested in game.** r23 must look exactly like r22. The proof is bytes and code runs.
2. **Dead space:** the 0x5028-byte gap and the 0x2010 bytes after `rage_stats` are free (0xFF). Old vanilla and `gohan_portraits` frames stay as dead data, as before.
3. **Other r22 states (SPECULATIVE):** the three I state hold no pointer into changed ROM (CONFIRMED). A different r22 state, saved while a table portrait was on screen, might hold that portrait's r22 frame address in RAM. In r23 that address is 0xFF, so a re-read after the load would get a bad frame. This applies only to the one-time move to the new layout. After it, a replaced portrait keeps its slot, so such a pointer reads the new art.
4. **A palette change to an index that a table portrait uses stops the build.** This is by design: the art would change color. Inject that portrait again, or pick another index.
5. **Code changes still go through `log2_build.py`.** `inject.py` refuses any diff outside the art sites. After a new code patch, add it to `build_list.txt` and build with `log2_build.py --list --out builds\log2_poc_rN.gba`. Later injects then diff against that build.
6. **Ids above 121** need a bigger live block. That is a separate change.
7. **Stale usage text:** the `Usage` headers of `patches\status_portrait.py` and `patches\rage_stats.py` still show the r20 command with `portrait_remaster`. I did not edit those files.

---

## 10. Files

- **New:** `scripts\permanent\art\inject.py`, `scripts\permanent\art\art_tables.py`, `scripts\permanent\patches\art_inject.py`, `scripts\permanent\build_list.txt`, `scripts\permanent\art\` (`portraits.json`, `palette.json`, `README.md`, `portraits\*.png` x7), `scripts\permanent\tests\test_art_inject.py`, `scripts\permanent\tests\test_inject.py`.
- **Changed:** `scripts\permanent\log2_build.py` (`ART_REGION`, `EXPANSION` ends at `rom:0xEFFFFF`, `assemble`, `apply_patches`, `read_build_list`, `--list`), `docs\build-log.md` (one line).
- **Removed (backups in `scripts\one-time\2026-10-20-inject-tool\backup\`):** `scripts\permanent\patches\portrait_remaster.py`, `scripts\permanent\tests\test_portrait_remaster.py`.
- **New ROM and states:** `archive\builds\log2_poc_r23.gba`, `.sav`, `.ss1`-`.ss3`.
- **Work scripts and outputs in `scripts\one-time\2026-10-20-inject-tool\`:** `layout_proof.py`/`.txt`, `states.py`/`.txt`, `dry_run.py`, `lint.py`, `r23_inject.txt`, `suite.txt`, `bible_rows.md`, `backup\`.
- Not touched: `data\`, `docs\RE-BIBLE.md`, any r22 file, `scripts\one-time\2026-10-20-effects-trace\`, `art\portrait-sources\remaster\anime\` (read only).
