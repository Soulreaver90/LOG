# LOG folder inventory (raw data for the reorganization plan)

Survey date: 2026-10-24, about 10:00 AM to 11:30 AM Eastern. Read only: nothing was moved, renamed, deleted or edited.
The plan that uses this data: `scratch\sdd\slice1\folder-reorg-plan.md`.

Labels: **C** = CONFIRMED (I read the file or ran the count), **L** = LIKELY, **S** = SPECULATIVE.
Counts come from a Python walk of the whole tree (all levels, no cut-off). A size column "1M" is rounded.
The counts are a point in time. Two tasks were writing under `scratch\re\hud_ki\` and `scratch\re\base_audit\`, and `scratch\art\base_audit\` also changed while I counted.

---

## 1. Totals

| Folder | Files | Size | Share of all files |
|---|---|---|---|
| LOG root (loose) | 1 (`README.md`) | 1 KB | |
| `data\` | 2,760 | 224 MB | 6 % |
| `docs\` | 14 | 550 KB | 0.03 % |
| `scratch\` | 46,393 | 2.0 GB | 94 % |
| `scripts\` | 164 | 3 MB | 0.3 % |
| **Total** | **49,332** | **about 2.3 GB** | |

File types over the whole tree (C): 42,398 `.png`, 2,158 `.py`, 1,116 `.pyc`, 795 `.txt`, 512 `.json`, 420 `.gif`, 99 `.gba` (ROMs, 1.3 GB), 70 `.sav`.

### Files per `scratch\` subfolder (C)

| `scratch\` subfolder | Files | Size | Newest file |
|---|---|---|---|
| `art` | 17,589 | 126 MB | 10-24 10:01 (live, being edited) |
| `re` | 10,867 | 562 MB | 10-24 10:01 (live, being edited) |
| `sdd` (all in `sdd\slice1`) | 10,765 | 93 MB | 10-24 09:53 |
| `sprites` | 3,173 | 4 MB | 10-17 23:31 |
| `venv` | 2,450 | 68 MB | 10-22 18:03 |
| `research` | 988 | 10 MB | 10-18 02:14 |
| `build` | 249 | 1.2 GB | 10-24 08:42 |
| `audio` | 243 | 125 MB | 10-22 19:07 |
| `captures` | 37 | 2 MB | 10-16 17:00 |
| `ghidra` | 25 | 60 MB | 10-19 10:18 |
| `saves` | 3 | 24 KB | 10-18 20:46 |
| `verify` | 3 | 2 KB | 10-16 16:52 |
| `sprites_backup_2330` | 1 | 2 KB | 10-17 23:31 |

### Files per `scripts\` and `docs\` subfolder (C)

| Folder | Files | Note |
|---|---|---|
| `scripts\one-time\` | 0 | Empty |
| `scripts\permanent\` (loose) | 22 | 19 `.py` tools, `build_list.txt`, `__pycache__` |
| `scripts\permanent\patches\` | 40 | 20 patch modules plus their `.pyc` |
| `scripts\permanent\tests\` | 61 | 30 test files (605 `def test_` methods, C), plus `.pyc` |
| `scripts\permanent\re\` | 10 | Disassembly tools (`codemap.py`, `listing.py`, `symbols.py`) and `re\data\` snapshots |
| `scripts\permanent\art\` | 13 | Portrait and palette tables the inject tool reads, 10 portrait PNGs |
| `docs\` (loose) | 13 | Bible, build log, data index, design, 9 research write-ups |
| `docs\plans\` | 1 | Slice 1 plan |

---

## 2. What every folder is for

Status words: **LIVE** = the build, a tool or a test reads or writes it now. **MINE** = holds my own files (irreplaceable). **EVIDENCE** = cited as a source by the bible, the build log or a report. **ARCHIVE** = superseded copy. **THROWAWAY** = can be regenerated or is a render.

### 2.1 `data\` (my originals, read only)

| Folder | Holds | What it is for | Read by | Status |
|---|---|---|---|---|
| `data\roms\` | 3 `.gba` (LoG II USA, LoG II EU, Buu's Fury), 1 `.sav`, 2 states, 1 cheats file | Base ROM and references | `log2_build.py`, `gi_art.py`, `gi_aura.py`, `gohan_portraits.py`, `re\codemap.py`, `re\symbols.py`, 9 test files (C) | LIVE, MINE |
| `data\reference\` | 20 images (`.jpg`, `.png`, `.webp`, `.gif`); 7 files are just named `images` | Portrait sheets and art reference | `gohan_portraits.py` reads `122601.png` (C) | LIVE, MINE |
| `data\sprites\` | 26 loose sprite sheets (`Game ...png`) plus `Buu_Fury_Character_Sprites\characters\` (232 character folders, 1,887 PNGs) | Ripped sprite sheets, art reference | No code (C, two search shapes) | MINE |
| `data\Inferred\all\` | 187 `bank-NNN` folders (2 PNG plus 1 JSON each) and `manifest.json` | Buu's Fury tileset atlases | No code (C) | MINE |
| `data\Sound\` | 244 `.wav` | Sound effects | No code (C) | MINE |
| `data\items\` | 6 JSON catalogs, 6 PNG sheets | Buu's Fury item catalogs | No code (C) | MINE |

### 2.2 `docs\`

| File or folder | What it is | Read by | Status |
|---|---|---|---|
| `RE-BIBLE.md` (946 lines) | Index of every ROM fact. "RE" means reverse engineering | `scripts\permanent\re\symbols.py` (`BIBLE` constant, C), every task | LIVE |
| `build-log.md` (128 lines) | One line per build with SHA-1 | Written by `log2_build.py` and `inject.py` (`BUILD_LOG`, C) | LIVE |
| `data-index.md` | What is in `data\` | People | LIVE |
| `2026-10-16-log-merge-design.md` | Approved design | People | LIVE |
| `plans\2026-10-16-slice1-poc-plan.md` | Slice 1 plan | People | LIVE |
| `re-forms.md`, `re-outfit.md`, `re-overview.md`, `re-portraits.md`, `re-save-format.md`, `re-sprite-decompression.md` | Research write-ups ("re-" = reverse engineering) | People, bible source keys | LIVE |
| `research-bf-sprites.md`, `research-notes.md`, `research-status-screen.md` | Research write-ups (same kind, other prefix) | People, bible source keys | LIVE |

### 2.3 `scripts\`

| Folder | What it is for | Status |
|---|---|---|
| `scripts\permanent\` | The build (`log2_build.py`, `inject.py`, `build_list.txt`), art pipeline (`gi_art.py`, `gi_post.py`, `gi_one_body.py`, `gi_aura.py`, `gi_review.py`, `hand_frames.py`, `frame_lock.py`), ROM tools (`rom_info.py`, `rom_sheet.py`, `rom_space.py`, `state_dump.py`, `thumb_dis.py`, `find_*.py`, `webfoot_decompress.py`, `log2_sprites.py`, `log2_save.py`, `re_sym.py`) | LIVE |
| `scripts\permanent\patches\` | One module per ROM change; `build_list.txt` names 17 of the 20 (C) | LIVE |
| `scripts\permanent\tests\` | The 605-test suite (C, count of `def test_`) | LIVE |
| `scripts\permanent\re\` | Own disassembler (code map, listing, symbols). Named `re`, so it cannot be a Python package (clash with the standard `re` module); `re_sym.py` loads it by file path (C) | LIVE |
| `scripts\permanent\art\` | `portraits.json`, `palette.json`, `portraits\*.png`, `README.md`: the art tables `inject.py` and `art_inject.py` read (`art_tables.ART_DIR`, C) | LIVE |
| `scripts\one-time\` | Empty | |
| `__pycache__\` (4 places, 72 `.pyc`) | Python cache | THROWAWAY |

### 2.4 `scratch\art\` (17,589 files)

| Folder or file | Holds | What it is for | Read or written by | Status |
|---|---|---|---|---|
| `gi_base\` | 162 PNG plus manifest | Gohan gi base frames, set 157. My hand frames are placed into it | `gohan_gi.py` (build, C), `gi_one_body.py`, many tests | LIVE, build input |
| `gi_ssj\`, `gi_ssj2\` | 159 PNG each | First-stage gi Super Saiyan and Super Saiyan 2 frames | `gi_post.py` input, `test_gi.py` (C) | LIVE |
| `gi_ssj_v2\`, `gi_ssj2_v2\` | 159-176 PNG | Set 158 and the 159 body; `gi_ssj_v2` is the build default for set 158 | `gohan_gi.py` (`LOG_GI_SSJ` default, C), tests | LIVE, build input |
| `gi_ssj2_aura\`, `gi_rage_aura\` | 163 and 139 PNG | Sets 159 and 160 with bolts; build defaults | `gohan_gi.py` (C) | LIVE, build input |
| `gi_rage\` | 176 PNG | Set 160 body before bolts | `gi_aura.py` (C) | LIVE |
| `gi_ssj_v4\`, `gi_ssj2_v4\`, `gi_ssj2_aura_v4\` | 159-163 PNG | "One body" versions (preview builds r32_preview, r32_preview2) | `test_one_body.py`, `test_gi_post.py` (C) | LIVE (tests) |
| `gi_ssj_v3\`, `gi_ssj2_v3\`, `gi_ssj2_aura_v3\` | 159-163 PNG | r29 preview art | No code in `scripts\permanent` (C) | ARCHIVE |
| `gi_ssj2_v3_r3aura_20261017\` | 176 PNG | Dated copy from 2026-10-17 | No code (C) | ARCHIVE |
| `golden\` (515 files; `owner\`, `work\`, `work_r2\`, `work_r3\`) | Approved model frames (golden PNGs), my drawings and notes in `owner\`, drafting scripts | `gi_art.py`, `gi_post.py`, `gi_aura.py`, `hand_frames.py`, `frame_lock.py`, 4 tests (C) | LIVE, MINE |
| `locks\` (9 lock folders) | Fingerprints of approved frames; 6 dated `golden_2026...` older locks | `frame_lock.py` (C) | LIVE (3), ARCHIVE (6, L) |
| `r12fix\` (`edits.py`, `fix.py`, `snap_r15` to `snap_r19`, `out`, `zoom`) | Per-frame hand fixes the main loop draws (memory note `feedback_log_sprite_fixes_by_eye`) | `test_hand_frames.py` reads `snap_r18`, `snap_r19` (C) | LIVE, tool |
| `cell_aura\` (`plain`, `scale_15`, `scale_20`, `scale_25`) | Super Perfect Cell aura frames; I picked `scale_15` | `superperfect_cell.py` via `ART_FOLDER = "cell_aura/scale_15"` (C), `test_superperfect_cell.py` | LIVE (`scale_15`), choices |
| `hud_z2_usable.bin`, `hud_z2_dim.bin`, `hud_z2.png` | Z2 HUD icons | `ssj2_form.py` `Z2_ICONS` (C) | LIVE, build input |
| `portraits\` (308 files; `src\`, `remaster\`, `work\`) | Gohan portrait outputs and source; `remaster\` holds remasters, my edits (`final_r24`, `superperfect\owner`, `anime\owner_edit`), refs | `gohan_portraits.py` (build), `test_art_inject.py`, `test_status_portrait.py`, `test_superperfect_cell.py` (C) | LIVE, MINE |
| `base_audit\` (`approved`, `owner`, `proposed`, `sheets`, `gifs`, `to_edit`) | Current gi base frame audit; `owner\` holds 7 of my PNGs | `scratch\re\base_audit\ba_*.py` (C) | LIVE (being edited now), MINE |
| `ingame_r28\` (sets 157-160) | Frames exported from build r28 | `ba_sheet.py` reads `set157` (C) | LIVE for the base audit |
| `anim\` | Strips and GIFs | Written by `gi_review.py` and `gi_art.py` (C) | THROWAWAY (regenerated) |
| `review\` (8,205 files: `frames_r10` to `frames_r15`, `full_r9` to `full_r12`, `eye_r12`, `aura_r13`, `one_body*`, `owner_0804`, `cell_aura`) | Review renders and before/after sheets | No code (C) | THROWAWAY |
| `work\` (3,505 files: `r0_`, `r1a_`, `r1b_`, `rA_`, `r34_`, `rAroot`, `*_old_method`, `armrev`) | Early gi method rounds (2026-10-16 to 17) | `gi_art.py` reads `work\gi_ssj_old_method` for one compare sheet (C, line 2083) | ARCHIVE (except `gi_ssj_old_method`, L) |
| Loose: `gi_*_sheet.png`, `gi_overview.png`, `gi_ssj_9_2_test_cases.png`, `portraits_*.png` | Contact and review sheets | Written by `gi_art.py`, `gohan_portraits.py` (C) | THROWAWAY |

### 2.5 `scratch\re\` (10,867 files): one folder per study or build round

Each folder holds study scripts, text listings and sheets. Most also hold `RE-BIBLE.before-merge.md` (a full bible copy, 38 copies in the tree, 6.3 MB, C) and `bible_rows.md` (rows later merged into the bible).

| Folder | Files | What it is (matched to its brief in `sdd\slice1`) | Status |
|---|---|---|---|
| (loose, 22 files) | 22 | First probes 2026-10-16: `dis_iwram.txt` (the bible cites it), `dis_callers*.txt`, probe scripts, `gohan_sets.png` | EVIDENCE |
| `asm\` | 15 | Assembler toolchain trial (toolchain task) | EVIDENCE |
| `aura\` | 2 | Aura diff scripts (aura-rage) | EVIDENCE |
| `base_audit\` | 342 | Current base audit tools `ba_*.py` plus exports `set56`, `set59` | LIVE (a task edits `ba_sheet.py` now) |
| `block\` | 57 | Block study and block pose (today); `mockups\` has 5 ROMs and 5 saves (80 MB) | LIVE (today) |
| `cellgames\` | 21 | Cell Games Super Saiyan study | EVIDENCE |
| `chamber\` | 32 | Chamber fights study | EVIDENCE |
| `chamber_proto\` | 22 | Chamber spar prototype (r37) | EVIDENCE, recent |
| `cutscene\` | 10 | Cutscene portraits | EVIDENCE |
| `decomp-review\` | 4 | Buu's Fury decomp review | EVIDENCE |
| `disasm\` | 54 (224 MB) | The disassembler before adoption, plus `ghidra\proj\LoG2auto.rep` (214 MB Ghidra project) | EVIDENCE; project is regenerable (L) |
| `disasm-port\` | 3 | Disassembly port review | EVIDENCE |
| `effects\` | 88 | Effects trace, 53 listings | EVIDENCE |
| `file_select\` | 20 | File select dim | EVIDENCE |
| `forms\` | 8 | Super Saiyan forms research | EVIDENCE |
| `gamefaqs\` | 2 | A downloaded walkthrough (`.txt`, `.json`) | Reference (L) |
| `gi\` | 40 | Task 5 gi work (state dumps, fixes) | EVIDENCE |
| `hud_ki\` | 59 | Ki HUD study and prototype; `mockups\` holds a ROM and save | LIVE (a task works here now) |
| `inject\` | 14 | Inject tool build | EVIDENCE |
| `intake\`, `intake17\`, `intake18\` | 1,759 / 1,332 / 1,339 | my art intake rounds r14, r16, r17. 97-100 % of the PNGs are copies (`art_r14`, `art_r16`, `art_r17`) | ARCHIVE (copies), scripts EVIDENCE |
| `npc_gi\` | 6 | NPC gi | EVIDENCE |
| `obfix\` | 1,038 | One-body fix; `art\` is a 987-file copy | EVIDENCE plus ARCHIVE copy |
| `outfit\`, `overview\`, `save\`, `portraits\` | 15 / 54 / 46 / 23 | Early research behind `docs\re-*.md` | EVIDENCE |
| `palette_census\`, `palette_use\`, `palslot\` | 32 / 6 / 28 | Palette studies; `palslot` holds 2 ROM copies (34 MB) | EVIDENCE |
| `piccolo\` | 14 | Piccolo gi scene | EVIDENCE |
| `r19\`, `r20\`, `r21\`, `r22\`, `r27\` to `r35\`, `r38\` | 4 to 1,387 | Per-build work: sweeps, listings, proofs. `r19\art_r18` and `r29\art` are art copies; `r30`, `r31` hold set exports; `r20` holds a ROM | EVIDENCE plus copies |
| `remaster\` | 188 | Portrait remaster pipeline (`anime\b1_label.py` to `b5_detail.py`, `e0`-`e3`); the memory note calls it the pipeline to reuse | LIVE tool kept in scratch |
| `set57_png\` | 200 | Export of sprite set 57 | THROWAWAY (regenerable) |
| `status_same\` | 16 | Status portrait study | EVIDENCE |
| `superperfect\` | 307 | Super Perfect Cell study, aura and portrait work | EVIDENCE |
| `t6\` | 6 | Task 6 helpers | EVIDENCE |
| `toolreview\` | 8 | Third-party tool review; a ROM copy (16 MB) | EVIDENCE |
| `__pycache__\` | 1 | Cache | THROWAWAY |

### 2.6 `scratch\sdd\slice1\` (10,762 files)

"sdd" is the name of the task method used. "slice1" is the first slice of the merge plan.

| Part | Files | What it is | Status |
|---|---|---|---|
| Loose files | 186 | Task briefs (`X.md`), reports (`X-report.md`), review diffs (`.diff`), the ledger `progress.md` (150 KB), morning reports, `global.md` (rules every brief cites), `snap.sh` and `package.sh` (review snapshot tools) | LIVE, EVIDENCE |
| `gi-fix-1125\`, `gi-fix-step-work\`, `gi-rules-night-work\`, `owner-0853-work\`, `owner-0948-work\`, `shared-body-1240-work\` | 489 to 3,575 each | Art rounds with before and after copies, plus scripts | ARCHIVE (80 % of all PNGs here are copies, C) |
| `snapshots\` (12 snapshots) | 251 | Copies of `scripts\permanent` and `docs` for review diffs | ARCHIVE |
| `backups\` | 5 | One backup set | ARCHIVE |

### 2.7 Other `scratch\` folders

| Folder | Holds | What it is for | Read by | Status |
|---|---|---|---|---|
| `sprites\` (20 `setNN` folders) | Vanilla sprite sets exported from the base ROM | Reference for the gi pipeline | `gi_art.py`, `gi_one_body.py`, `gi_review.py`, `test_one_body.py` (C) | LIVE; regenerable with `log2_sprites.py export` (L) |
| `build\` (240 loose) | 66 ROMs (r1 to r38, previews, twins), 58 `.sav`, 136 `.ss1`-`.ss5` states | Every build and my saves | `inject.py` (numbering), `log2_build.py` (default out), 8 test files (C) | LIVE, MINE (saves) |
| `build\test\` | 8 test ROMs, `build-log-test.md` | Rebuilt by tests on every run | 5 test files (C) | THROWAWAY |
| `saves\` | 3 `.sav` | Level 40 test saves | `test_save.py` (C), `log2_save.py` comment | LIVE (test input) |
| `research\bf-sprites\`, `research\status\` | 907 / 81 | Evidence for `docs\research-bf-sprites.md` and `research-status-screen.md` | No code (C) | EVIDENCE |
| `audio\` | 243 | Rage music work: 3 scripts, MIDI, MP3, drafts, exports, test ROMs | Uses `scratch\venv\webfoot-audio` (C) | EVIDENCE plus my own inputs (L) |
| `venv\webfoot-audio\` | 2,450 | Python virtual environment (numpy, mido, miniaudio) | `scratch\audio\a*.py` (C) | THROWAWAY; `pyvenv.cfg` stores the absolute path (C), so recreate it, never move it |
| `ghidra\` | 25 | First Ghidra project (`LoG2.gpr`), seeded project, 4 `.java` scripts, a ROM copy | People | Projects regenerable (L); `.gpr` files are empty and the `.prp` files hold no absolute path (C) |
| `captures\` | 37 | mGBA RAM captures, 2026-10-16 | Bible cites it (3 refs) | EVIDENCE |
| `verify\` | 3 `.bin` | First checks, 2026-10-16 | No reference found (C) | ARCHIVE |
| `sprites_backup_2330\` | 1 PNG | One backup frame | 1 report mention | ARCHIVE |

---

## 3. Duplicates (content hash, C)

The scan hashed every `.png`, `.gba`, `.sav`, `.md` and `.py` outside `venv` and `__pycache__`.

| Type | Files | Extra copies | Space in extra copies |
|---|---|---|---|
| `.png` | 42,398 | 27,805 (66 %) | 72 MB |
| `.gba` | 99 | 39 | 600 MB |
| `.sav` | 70 | 57 | 0.4 MB |
| `.py` | 1,274 | 344 | 2 MB |
| `.md` | 370 | 65 | 1 MB |

Caveat (C): one sprite set can hold the same PNG under two keys, so a few "extra copies" inside one live folder are by design. The `.gba` copies are mostly twins (for example `r33_chamber2.gba` and `r33_scouter.gba` are byte copies of `r33.gba`, which the tests check).

Folders that are mostly copies (extra copies / files):

| Folder | Copies | Folder | Copies |
|---|---|---|---|
| `scratch\sdd\slice1` (subfolders) | 8,441 / 10,496 | `scratch\re\obfix` | 978 / 1,012 |
| `scratch\art\review` | 4,573 / 8,151 | `scratch\art\locks` | 646 / 646 |
| `scratch\art\work` | 1,773 / 3,463 | `scratch\research\bf-sprites` | 688 / 884 |
| `scratch\re\intake` | 1,616 / 1,626 | `scratch\art\r12fix` | 214 / 332 |
| `scratch\re\r29` | 1,322 / 1,366 | `scratch\re\superperfect` | 206 / 286 |
| `scratch\re\intake17` | 1,294 / 1,314 | `scratch\re\base_audit` | 163 / 335 |
| `scratch\re\intake18` | 1,294 / 1,313 | `data\sprites\Buu_Fury_Character_Sprites` | 917 / 1,887 (my rip, leave) |
| `scratch\re\r19` | 1,294 / 1,310 | | |

---

## 4. Builds and saves that code and tests name (C)

Search shape: `log2_poc(_rNN...)?.(gba|sav|ssN)` and `log2_lv40_*.sav` over `scripts\permanent` (`.py`).

| File | Who reads it | Guard if missing |
|---|---|---|
| `log2_poc.gba` | `test_tools.py` line 23, at import | **None: the whole file errors** |
| `log2_poc_r18.gba` | `test_hand_frames.py` line 94, `setUpClass` | **None: the class errors** |
| `log2_poc_r27.sav`, `log2_poc_r28_chamber.sav`, `log2_poc_r28_chamber2.sav` | `test_fullpower_ssj.py` | `skipUnless` |
| `log2_poc_r29.gba`, `r29_chamber2.ss3`, `r30`-`r32` ROMs and twins | `test_piccolo_gi_scene.py` | `skipTest` or `continue` |
| `r30.sav`, `r30_chamber2.sav`, `r31*.sav`, `r31` twins | `test_r31_saves.py` | `SkipTest` |
| `r30`-`r38` ROMs and twins | `test_superperfect_cell.py` | `skipTest` or `continue` |
| `r36.gba`, `r36.sav`, `r37.gba`, `r37_spar.gba`, `r37_spar.sav`, `r38.gba` | `test_chamber_spar.py` | `skipTest` |
| `scratch\saves\log2_lv40_postcell.sav`, `log2_lv40_cellgames.sav` | `test_save.py` lines 103, 190 | `if X.exists():` (passes silently) |

Skip guards: 48 lines in 9 test files (shape `skipTest|SkipTest|skipUnless|skipIf|.exists()`, C).
No test reads r1 to r17 or r19 to r26 from disk (C). Those names appear only in docstrings and in `test_inject.py` temp folders.

Non-code files tests read (C): `scratch\sdd\slice1\r35.md` (`test_superperfect_cell.py` line 58, no guard), my PNGs under `scratch\art\portraits\remaster\final_r24\` and `...\superperfect\owner\sp52_owner_v3.png`, `scratch\art\golden\`, `scratch\art\r12fix\snap_r18\`, `snap_r19\`.

---

## 5. Path references (raw counts)

Script: a Python scan of 3,000+ text files (`.md .py .txt .json .sh .diff .java .csv .gpl`) under LOG (without `venv`, `__pycache__` and Ghidra `.rep` folders) plus the 9 LOG memory files and the project notes.
Shapes: **bs** = backslash path (`scratch\re`, also inside absolute paths), **fs** = forward slash (`scratch/re`), **code** = Python join (`"scratch" / "re"`), **bare** = the folder name without its parent (`re\r29\`, `sdd\slice1`, a doc name alone).

Areas: "briefs+reports" = the 186 loose files in `sdd\slice1`. "sdd subfolders" = its work folders and snapshots. "scratch other (re)" includes the 38 bible copies.

| Old path | Area | Files | bs | fs | code | bare |
|---|---|---|---|---|---|---|
| `scratch\art` | scripts code | 11 | 31 | 0 | 12 | |
| `scratch\art` | scripts tests | 10 | 6 | 0 | 12 | |
| `scratch\art` | docs\RE-BIBLE.md | 1 | 21 | 1 | 0 | |
| `scratch\art` | docs\build-log.md | 1 | 7 | 0 | 0 | |
| `scratch\art` | docs other | 2 | 8 | 0 | 0 | |
| `scratch\art` | memory | 3 | 3 | 1 | 0 | |
| `scratch\art` | briefs+reports | 123 | 463 | 2 | 14 | |
| `scratch\art` | sdd subfolders | 101 | 235 | 89 | 59 | |
| `scratch\art` | scratch other (re) | 212 | 660 | 93 | 156 | |
| `scratch\art` | scratch other (art) | 49 | 62 | 22 | 33 | |
| `scratch\build` | scripts code | 19 | 19 | 0 | 2 | |
| `scratch\build` | scripts tests | 13 | 11 | 0 | 14 | |
| `scratch\build` | docs\RE-BIBLE.md | 1 | 14 | 0 | 0 | |
| `scratch\build` | docs\build-log.md | 1 | 6 | 0 | 0 | |
| `scratch\build` | docs other | 3 | 8 | 0 | 0 | |
| `scratch\build` | memory | 1 | 1 | 0 | 0 | |
| `scratch\build` | briefs+reports | 148 | 331 | 1 | 12 | |
| `scratch\build` | sdd subfolders | 94 | 163 | 1 | 56 | |
| `scratch\build` | scratch other (re) | 210 | 273 | 8 | 153 | |
| `scratch\re` | scripts code | 9 | 10 | 0 | 0 | |
| `scratch\re` | scripts tests | 4 | 6 | 0 | 0 | |
| `scratch\re` | docs\RE-BIBLE.md | 1 | 60 | 0 | 0 | |
| `scratch\re` | docs\build-log.md | 1 | 10 | 0 | 0 | |
| `scratch\re` | docs other | 7 | 50 | 0 | 0 | |
| `scratch\re` | memory | 3 | 4 | 0 | 0 | |
| `scratch\re` | briefs+reports | 124 | 613 | 6 | 1 | |
| `scratch\re` | sdd subfolders | 73 | 376 | 0 | 0 | |
| `scratch\re` | scratch other (re) | 373 | 1,346 | 143 | 47 | |
| `scratch\sdd` | scripts code | 15 | 15 | 0 | 0 | |
| `scratch\sdd` | scripts tests | 13 | 15 | 0 | 1 | |
| `scratch\sdd` | docs\RE-BIBLE.md | 1 | 28 | 19 | 0 | |
| `scratch\sdd` | docs other | 5 | 6 | 0 | 0 | |
| `scratch\sdd` | memory | 1 | 4 | 0 | 0 | |
| `scratch\sdd` | briefs+reports | 134 | 237 | 2 | 0 | |
| `scratch\sdd` | scratch other (re) | 105 | 822 | 261 | 5 | |
| `scratch\sprites` | scripts code | 3 | 3 | 0 | 3 | |
| `scratch\sprites` | scripts tests | 1 | 0 | 0 | 1 | |
| `scratch\sprites` | docs (bible, build log, other) | 3 | 5 | 0 | 0 | |
| `scratch\sprites` | briefs+reports | 10 | 16 | 0 | 2 | |
| `scratch\saves` | scripts code / tests | 2 | 2 | 0 | 2 | |
| `scratch\saves` | docs (bible 5, build log 3, other 14) | 6 | 22 | 0 | 0 | |
| `scratch\saves` | briefs+reports | 21 | 31 | 1 | 0 | |
| `scratch\captures` | docs (bible 3, other 7) | 4 | 10 | 0 | 0 | |
| `scratch\captures` | briefs+reports | 6 | 18 | 0 | 0 | |
| `scratch\ghidra` | docs (bible 4, other 3) | 2 | 7 | 0 | 0 | |
| `scratch\ghidra` | briefs+reports | 16 | 29 | 2 | 0 | |
| `scratch\research` | docs other | 2 | 23 | 0 | 0 | |
| `scratch\research` | briefs+reports | 4 | 9 | 0 | 0 | |
| `scratch\audio` | briefs+reports | 3 | 11 | 0 | 0 | |
| `scratch\audio` | its own scripts | 3 | 0 | 3 | 0 | |
| `scratch\venv` | audio scripts / 1 report | 4 | 1 | 3 | 0 | |
| `scratch\sprites_backup_2330` | 1 report | 1 | 1 | 0 | 0 | |
| `scratch\verify` | (none) | 0 | 0 | 0 | 0 | |
| `permanent\re` | scripts code | 3 | 3 | 0 | 0 | |
| `permanent\re` | docs\RE-BIBLE.md | 1 | 1 | 0 | 0 | |
| `permanent\re` | memory | 1 | 1 | 0 | 0 | |
| `permanent\re` | briefs+reports | 9 | 19 | 2 | 0 | |
| `docs\plans` | README, memory, 5 reports | 7 | 5 | 10 | 0 | |
| `data\Inferred`, `data\Sound` | anywhere | 0 | 0 | 0 | 0 | 1 bare in `data-index.md` |
| `docs\re-*.md` (explicit `docs\re-`) | 73 files | 73 | 95 lines | | | |
| `docs\research-*.md` (explicit) | 11 files | 11 | 15 lines | | | |
| Research doc names alone | 170 files | | | | | 795 |
| `re\<sub>` alone | 39 files | | | | | 64 |
| `art\gi_...` alone | 7 files | | | | | 7 |

### 5.1 Live code sites (the only ones the build and suite need)

Shape A, the join `"scratch"` in `.py` under `scripts\permanent`: **47 lines in 31 files** (C).

- Tools and patches (17 lines): `frame_lock.py` 45, 46; `gi_art.py` 84, 85; `gi_aura.py` 44; `gi_one_body.py` 65, 66; `gi_post.py` 44; `gi_review.py` 23, 123; `hand_frames.py` 34; `inject.py` 52; `log2_build.py` 29; `patches\gohan_gi.py` 37; `patches\gohan_portraits.py` 49, 50; `patches\ssj2_form.py` 29.
- Tests (30 lines): `test_art_inject.py` 123, 130; `test_aura.py` 25; `test_build.py` 26; `test_chamber_spar.py` 38; `test_fullpower_ssj.py` 43, 44; `test_gi.py` 27, 535; `test_gi_post.py` 24; `test_hand_frames.py` 26, 29; `test_one_body.py` 25, 26; `test_owner_walk.py` 20; `test_piccolo_gi_scene.py` 77; `test_portraits.py` 29; `test_r31_saves.py` 21; `test_save.py` 21, 22; `test_ssj2.py` 32, 33; `test_status.py` 30; `test_status_portrait.py` 32; `test_superperfect_cell.py` 58, 64, 65, 66, 714; `test_tools.py` 23.

Shape B, a quoted string that holds `scratch\` or `scratch/`: 0 lines (C). Shape C, `os.path`, `../`, `getcwd`: 0 lines; `cwd=str(ROOT)` once in `test_build.py` 75 (C). The 110 other `scratch` lines in `scripts\permanent` are docstrings and comments.

Paths relative to the art root that stay right only if the inside names stay (C): `superperfect_cell.ART_FOLDER = "cell_aura/scale_15"` (resolved through `gohan_gi.ART`), `gohan_gi` defaults `LOG_GI_SSJ = gi_ssj_v2`, `LOG_GI_SSJ2 = gi_ssj2_aura`, `ssj2_form.Z2_ICONS` (two `.bin` files at the art root), `gi_art.WORK = ART / "work"`, `GOLDEN = ART / "golden"`, test folder names (`"gi_ssj2_v4"`, `"r12fix" / "snap_r19"`, ...), `portraits.json` PNG paths (relative to `scripts\permanent\art`).

Depth math (C): tools use `parents[2]` and patches and tests use `parents[3]` to find the LOG root. Moving a file one level changes it.

Study scripts (not live): 381 `.py` files under `scratch\` compute the root with `parents[N]`, and 266 hold the absolute `Workspace\LOG` path (C). They break when moved unless edited.

---

## 6. `sdd\slice1` loose files grouped by task (C, by name stem and oldest file date)

94 groups. A few stems need a hand merge (`tools-review` and `tools`, `tool-review` and `tool`, `decomp-review` and `decomp`, `cellgames` and `cellgames-ssj`).

| Date | Task stem | Files |
|---|---|---|
| 2026-10-16 | task-1 to task-8, global, snap, package | 4, 3, 3, 4, 8, 6, 5, 1, 1, 1, 1 |
| 2026-10-17 | final, final-fix, morning, golden, gi-fix-1125, portraits-piccolo, hud-z2-next, status-gold, gi-fix-step | 2, 2, 1, 3, 2, 2, 2, 2, 2 |
| 2026-10-18 | gi-rules-night, promote-chain, bible-pending-1018, tools-review, morning-report-1018, owner-0804-fixes, owner-0853-fixes, owner-0948-walk, eye-review-r12, shared-body-1240, save-slots, aura-rage, cutscene-portraits, r12fix-intake, npc-gi, portrait-remaster-study, chamber-fights-study, save-slot3, portrait-vegeta, r17-intake, portrait-gohan, file-select, disasm-study, r18-intake | 2 each, except 1 for bible-pending, morning-report-1018, eye-review-r12 |
| 2026-10-19 | portrait-soft, status-same, r19, disasm-adopt, toolchain, r20, portrait-from-anime, portrait-vector, r21, portrait-cell, palette-slot | 2 each |
| 2026-10-20 | effects-trace, r22, inject-tool, cellgames-ssj, cellgames-build, decomp-review, r27 | 2, 2, 2, 2, 1, 2, 1 |
| 2026-10-22 | fullpower-ssj, tool-review, disasm-port, superperfect-study, one-body, r28, piccolo-gi-scene, superperfect-aura | 1, 2, 2, 2, 2, 1, 2, 2 |
| 2026-10-23 | r30, r31, r32, one-body-fix, r33, base-audit, r34, superperfect-portrait, r35, superperfect-portrait2, palette-census-r35 | 2 each, except 1 for base-audit |
| 2026-10-24 | r36-pins, hud-ki-study, chamber-proto, block-study, morning-2026-10-24, block-pose, r38, hud-ki-proto, progress, folder-reorg-survey | 2, 2, 2, 2, 1, 2, 3, 1, 1, 1 |

---

## 7. Folder table, depth 1 to 4 (raw)

Columns: files under it (all levels), files directly in it, size, newest file (month-day time), top 5 types.
Not listed one by one: `data\Inferred\all\bank-000` to `bank-186` (187 folders, 3 files each), `data\sprites\Buu_Fury_Character_Sprites\characters\*` (232 folders), `scratch\audio\export\bf_copy.gba\it\song_000` to `song_052` (53 folders, 2 files each), `scratch\venv\*` (a Python environment), and folders deeper than 4 levels (they sit under `scratch\art\golden`, `scratch\art\portraits\remaster`, `scratch\re\intake\art_r14\golden`, `scratch\re\disasm\ghidra\proj` and the `sdd\slice1` work folders and snapshots).

| Folder | All | Direct | Size | Newest | Types |
|---|---|---|---|---|---|
| `data` | 2760 | 0 | 224M | 10-18 00:13 | .png 2298, .wav 244, .json 194, .jpg 11, .webp 3 |
| `data\Inferred` | 562 | 0 | 168M | 09-26 02:45 | .png 374, .json 188 |
| `data\Inferred\all` | 562 | 1 | 168M | 09-26 02:45 | .png 374, .json 188 |
| `data\Sound` | 244 | 244 | 17M | 11-29 18:08 | .wav 244 |
| `data\items` | 12 | 12 | 441K | 03-09 11:58 | .json 6, .png 6 |
| `data\reference` | 20 | 20 | 3M | 10-18 00:13 | .jpg 11, .png 5, .webp 3, .gif 1 |
| `data\roms` | 9 | 9 | 24M | 10-16 18:14 | .gba 3, .cheats 1, .sav 1, .ss1 1, .ss2 1 |
| `data\sprites` | 1913 | 26 | 11M | 10-16 18:20 | .png 1913 |
| `docs` | 14 | 13 | 550K | 10-24 09:03 | .md 14 |
| `docs\plans` | 1 | 1 | 19K | 10-17 03:05 | .md 1 |
| `scratch` | 46393 | 0 | 2G | 10-24 10:01 | .png 40090, .py 2084, .pyc 1044, .txt 793, .gif 420 |
| `scratch\art` | 17589 | 12 | 126M | 10-24 10:01 | .png 16817, .gif 387, .py 164, .txt 105, .json 67 |
| `scratch\art\anim` | 292 | 19 | 3M | 10-19 08:33 | .gif 236, .png 56 |
| `scratch\art\anim\compare` | 13 | 13 | 64K | 10-19 08:33 | .gif 13 |
| `scratch\art\anim\gi_base` | 90 | 90 | 841K | 10-19 08:32 | .gif 72, .png 18 |
| `scratch\art\anim\gi_ssj` | 85 | 85 | 950K | 10-19 08:32 | .gif 68, .png 17 |
| `scratch\art\anim\gi_ssj2` | 85 | 85 | 1020K | 10-19 08:33 | .gif 68, .png 17 |
| `scratch\art\base_audit` | 236 | 4 | 2M | 10-24 10:01 | .png 163, .gif 72, .gpl 1 |
| `scratch\art\base_audit\approved` | 44 | 44 | 45K | 10-24 09:10 | .png 44 |
| `scratch\art\base_audit\gifs` | 72 | 72 | 681K | 10-24 10:01 | .gif 72 |
| `scratch\art\base_audit\owner` | 7 | 7 | 5K | 10-24 09:39 | .png 7 |
| `scratch\art\base_audit\proposed` | 68 | 68 | 70K | 10-24 09:39 | .png 68 |
| `scratch\art\base_audit\sheets` | 18 | 18 | 1011K | 10-24 10:01 | .png 18 |
| `scratch\art\base_audit\to_edit` | 23 | 4 | 114K | 10-24 09:15 | .png 23 |
| `scratch\art\cell_aura` | 430 | 0 | 757K | 10-22 21:40 | .png 426, .json 4 |
| `scratch\art\cell_aura\plain` | 100 | 100 | 164K | 10-22 21:40 | .png 99, .json 1 |
| `scratch\art\cell_aura\scale_15` | 110 | 110 | 196K | 10-22 21:40 | .png 109, .json 1 |
| `scratch\art\cell_aura\scale_20` | 110 | 110 | 198K | 10-22 21:40 | .png 109, .json 1 |
| `scratch\art\cell_aura\scale_25` | 110 | 110 | 199K | 10-22 21:40 | .png 109, .json 1 |
| `scratch\art\gi_base` | 163 | 163 | 1M | 10-19 08:32 | .png 162, .json 1 |
| `scratch\art\gi_rage` | 178 | 161 | 727K | 10-18 15:16 | .png 176, .json 2 |
| `scratch\art\gi_rage\review` | 17 | 17 | 409K | 10-18 15:16 | .png 17 |
| `scratch\art\gi_rage_aura` | 140 | 140 | 248K | 10-19 08:33 | .png 139, .json 1 |
| `scratch\art\gi_ssj` | 160 | 160 | 1M | 10-19 08:32 | .png 159, .json 1 |
| `scratch\art\gi_ssj2` | 160 | 160 | 1M | 10-19 08:32 | .png 159, .json 1 |
| `scratch\art\gi_ssj2_aura` | 164 | 164 | 299K | 10-19 08:33 | .png 163, .json 1 |
| `scratch\art\gi_ssj2_aura_v3` | 164 | 164 | 305K | 10-22 20:42 | .png 163, .json 1 |
| `scratch\art\gi_ssj2_aura_v4` | 164 | 164 | 305K | 10-23 13:37 | .png 163, .json 1 |
| `scratch\art\gi_ssj2_v2` | 178 | 161 | 727K | 10-19 08:33 | .png 176, .json 2 |
| `scratch\art\gi_ssj2_v2\review` | 17 | 17 | 409K | 10-18 12:09 | .png 17 |
| `scratch\art\gi_ssj2_v3` | 161 | 161 | 377K | 10-22 20:42 | .png 159, .json 2 |
| `scratch\art\gi_ssj2_v3_r3aura_20261017` | 178 | 161 | 722K | 10-17 22:26 | .png 176, .json 2 |
| `scratch\art\gi_ssj2_v3_r3aura_20261017\review` | 17 | 17 | 429K | 10-17 12:53 | .png 17 |
| `scratch\art\gi_ssj2_v4` | 161 | 161 | 416K | 10-23 13:37 | .png 159, .json 2 |
| `scratch\art\gi_ssj_v2` | 160 | 160 | 1M | 10-19 08:33 | .png 159, .json 1 |
| `scratch\art\gi_ssj_v3` | 161 | 161 | 1M | 10-22 20:42 | .png 159, .json 2 |
| `scratch\art\gi_ssj_v4` | 161 | 161 | 1M | 10-23 13:37 | .png 159, .json 2 |
| `scratch\art\golden` | 515 | 106 | 13M | 10-19 08:31 | .png 342, .txt 86, .py 55, .pyc 16, .gif 15 |
| `scratch\art\golden\owner` | 103 | 14 | 1M | 10-18 15:19 | .png 89, .txt 12, .webp 1, .py 1 |
| `scratch\art\golden\work` | 123 | 69 | 2M | 10-18 00:13 | .png 73, .txt 35, .py 11, .pyc 4 |
| `scratch\art\golden\work_r2` | 42 | 22 | 6M | 10-17 09:57 | .png 27, .txt 8, .py 5, .pyc 2 |
| `scratch\art\golden\work_r3` | 141 | 58 | 3M | 10-18 15:20 | .png 47, .py 38, .txt 31, .gif 15, .pyc 10 |
| `scratch\art\ingame_r28` | 627 | 0 | 860K | 10-22 19:25 | .png 623, .json 4 |
| `scratch\art\ingame_r28\set157` | 163 | 163 | 219K | 10-22 19:25 | .png 162, .json 1 |
| `scratch\art\ingame_r28\set158` | 160 | 160 | 219K | 10-22 19:25 | .png 159, .json 1 |
| `scratch\art\ingame_r28\set159` | 164 | 164 | 230K | 10-22 19:25 | .png 163, .json 1 |
| `scratch\art\ingame_r28\set160` | 140 | 140 | 192K | 10-22 19:25 | .png 139, .json 1 |
| `scratch\art\locks` | 655 | 0 | 870K | 10-19 08:32 | .png 646, .json 9 |
| `scratch\art\locks\gi_rage` | 160 | 1 | 218K | 10-18 16:37 | .png 159, .json 1 |
| `scratch\art\locks\gi_ssj2_v2` | 160 | 1 | 218K | 10-18 16:37 | .png 159, .json 1 |
| `scratch\art\locks\golden` | 85 | 1 | 110K | 10-19 08:32 | .png 84, .json 1 |
| `scratch\art\locks\golden_20261018-1016` | 13 | 1 | 15K | 10-18 02:28 | .png 12, .json 1 |
| `scratch\art\locks\golden_20261018-1636` | 17 | 1 | 21K | 10-18 10:16 | .png 16, .json 1 |
| `scratch\art\locks\golden_20261018-1857` | 21 | 1 | 28K | 10-18 16:36 | .png 20, .json 1 |
| `scratch\art\locks\golden_20261018-2124` | 47 | 1 | 61K | 10-18 18:57 | .png 46, .json 1 |
| `scratch\art\locks\golden_20261019-0002` | 67 | 1 | 88K | 10-18 21:24 | .png 66, .json 1 |
| `scratch\art\locks\golden_20261019-0832` | 85 | 1 | 111K | 10-19 00:02 | .png 84, .json 1 |
| `scratch\art\portraits` | 308 | 7 | 22M | 10-24 01:27 | .png 275, .py 8, .gpl 6, .json 4, .txt 4 |
| `scratch\art\portraits\remaster` | 256 | 50 | 21M | 10-24 01:27 | .png 232, .gpl 6, .txt 4, .json 3, .svg 3 |
| `scratch\art\portraits\src` | 1 | 1 | 1K | 10-17 15:48 | .png 1 |
| `scratch\art\portraits\work` | 44 | 44 | 194K | 10-17 15:47 | .png 36, .py 8 |
| `scratch\art\r12fix` | 351 | 17 | 1M | 10-19 08:28 | .png 319, .py 13, .gif 12, .pyc 7 |
| `scratch\art\r12fix\__pycache__` | 3 | 3 | 33K | 10-19 00:19 | .pyc 3 |
| `scratch\art\r12fix\anim` | 12 | 12 | 251K | 10-18 17:38 | .gif 12 |
| `scratch\art\r12fix\out` | 64 | 64 | 37K | 10-19 00:19 | .png 64 |
| `scratch\art\r12fix\single` | 9 | 9 | 7K | 10-18 17:38 | .png 9 |
| `scratch\art\r12fix\snap_r15` | 28 | 1 | 25K | 10-18 18:30 | .png 26, .py 1, .pyc 1 |
| `scratch\art\r12fix\snap_r17` | 48 | 1 | 39K | 10-18 21:00 | .png 46, .py 1, .pyc 1 |
| `scratch\art\r12fix\snap_r18` | 67 | 2 | 63K | 10-18 23:54 | .png 64, .py 2, .pyc 1 |
| `scratch\art\r12fix\snap_r19` | 67 | 2 | 64K | 10-19 08:28 | .png 64, .py 2, .pyc 1 |
| `scratch\art\r12fix\zoom` | 36 | 36 | 223K | 10-18 21:30 | .png 36 |
| `scratch\art\review` | 8205 | 98 | 41M | 10-23 13:39 | .png 8151, .gif 52, .txt 2 |
| `scratch\art\review\aura_r13` | 39 | 39 | 569K | 10-18 16:43 | .gif 38, .png 1 |
| `scratch\art\review\cell_aura` | 9 | 9 | 19M | 10-22 21:42 | .gif 6, .png 3 |
| `scratch\art\review\eye_r12` | 35 | 35 | 1M | 10-18 12:24 | .png 35 |
| `scratch\art\review\frames_r10` | 864 | 0 | 947K | 10-18 08:54 | .png 864 |
| `scratch\art\review\frames_r11` | 2452 | 0 | 2M | 10-18 09:44 | .png 2452 |
| `scratch\art\review\frames_r12` | 2452 | 0 | 2M | 10-18 12:11 | .png 2452 |
| `scratch\art\review\frames_r14` | 446 | 446 | 396K | 10-18 19:46 | .png 446 |
| `scratch\art\review\frames_r15` | 1638 | 1638 | 1M | 10-18 19:12 | .png 1638 |
| `scratch\art\review\full_r11` | 35 | 35 | 2M | 10-18 09:44 | .png 35 |
| `scratch\art\review\full_r12` | 35 | 35 | 2M | 10-18 12:11 | .png 35 |
| `scratch\art\review\full_r9` | 35 | 35 | 2M | 10-18 08:07 | .png 35 |
| `scratch\art\review\one_body` | 25 | 25 | 3M | 10-22 20:56 | .png 24, .txt 1 |
| `scratch\art\review\one_body_v4` | 26 | 26 | 2M | 10-23 13:39 | .png 25, .txt 1 |
| `scratch\art\review\owner_0804` | 16 | 16 | 299K | 10-18 08:05 | .png 8, .gif 8 |
| `scratch\art\work` | 3505 | 377 | 30M | 10-17 08:18 | .png 3375, .py 88, .json 24, .txt 13, .pyc 5 |
| `scratch\art\work\__pycache__` | 5 | 5 | 170K | 10-17 07:42 | .pyc 5 |
| `scratch\art\work\armrev` | 64 | 64 | 1M | 10-17 08:18 | .png 64 |
| `scratch\art\work\cur` | 0 | 0 | 0B | - | |
| `scratch\art\work\gi_base_old_method` | 163 | 163 | 1021K | 10-16 22:31 | .png 162, .json 1 |
| `scratch\art\work\gi_ssj2_old_method` | 160 | 160 | 1M | 10-16 22:31 | .png 159, .json 1 |
| `scratch\art\work\gi_ssj_old_method` | 160 | 160 | 1M | 10-16 22:31 | .png 159, .json 1 |
| `scratch\art\work\r0_gi_base` | 163 | 163 | 1M | 10-17 00:02 | .png 162, .json 1 |
| `scratch\art\work\r0_gi_ssj` | 160 | 160 | 1M | 10-17 00:02 | .png 159, .json 1 |
| `scratch\art\work\r0_gi_ssj2` | 160 | 160 | 1M | 10-17 00:02 | .png 159, .json 1 |
| `scratch\art\work\r1a_gi_base` | 163 | 163 | 1M | 10-17 00:12 | .png 162, .json 1 |
| `scratch\art\work\r1a_gi_ssj` | 160 | 160 | 1M | 10-17 00:12 | .png 159, .json 1 |
| `scratch\art\work\r1a_gi_ssj2` | 160 | 160 | 1M | 10-17 00:12 | .png 159, .json 1 |
| `scratch\art\work\r1b_gi_base` | 163 | 163 | 1M | 10-17 00:27 | .png 162, .json 1 |
| `scratch\art\work\r1b_gi_ssj` | 160 | 160 | 1M | 10-17 00:27 | .png 159, .json 1 |
| `scratch\art\work\r1b_gi_ssj2` | 160 | 160 | 1M | 10-17 00:27 | .png 159, .json 1 |
| `scratch\art\work\r34_gi_ssj2` | 160 | 160 | 1M | 10-17 00:50 | .png 159, .json 1 |
| `scratch\art\work\rA_gi_base` | 163 | 163 | 1M | 10-17 07:12 | .png 162, .json 1 |
| `scratch\art\work\rA_gi_ssj` | 160 | 160 | 1M | 10-17 07:12 | .png 159, .json 1 |
| `scratch\art\work\rA_gi_ssj2` | 160 | 160 | 1M | 10-17 07:12 | .png 159, .json 1 |
| `scratch\art\work\rAroot` | 483 | 0 | 3M | 10-17 07:17 | .png 480, .json 3 |
| `scratch\art\work\tmpcmp` | 1 | 1 | 6K | 10-17 00:53 | .png 1 |
| `scratch\audio` | 243 | 3 | 125M | 10-22 19:07 | .wav 104, .json 63, .it 58, .gba 6, .py 3 |
| `scratch\audio\drafts` | 7 | 7 | 21M | 10-22 18:58 | .it 4, .wav 3 |
| `scratch\audio\export` | 215 | 0 | 5M | 10-22 17:05 | .wav 101, .json 60, .it 54 |
| `scratch\audio\export\bf_copy.gba` | 108 | 0 | 4M | 10-22 17:05 | .json 55, .it 53 |
| `scratch\audio\export\log2_r27_copy.gba` | 107 | 0 | 1M | 10-22 16:57 | .wav 101, .json 5, .it 1 |
| `scratch\audio\midi` | 2 | 2 | 15K | 10-21 19:11 | .mid 2 |
| `scratch\audio\mp3` | 1 | 1 | 3M | 10-21 19:16 | .mp3 1 |
| `scratch\audio\rom` | 2 | 2 | 24M | 10-20 14:03 | .gba 2 |
| `scratch\audio\test` | 13 | 13 | 71M | 10-22 18:58 | .gba 4, .json 3, .sav 2, .ss2 2, .ss1 1 |
| `scratch\build` | 249 | 240 | 1G | 10-24 08:42 | .gba 74, .sav 58, .ss1 40, .ss2 26, .ss3 24 |
| `scratch\build\test` | 9 | 9 | 128M | 10-24 08:42 | .gba 8, .md 1 |
| `scratch\captures` | 37 | 1 | 2M | 10-16 17:00 | .bin 26, .png 10, .txt 1 |
| `scratch\captures\01-gohan-base` | 13 | 13 | 557K | 10-16 16:27 | .bin 8, .png 5 |
| `scratch\captures\02-gohan-gi` | 16 | 16 | 522K | 10-16 16:47 | .bin 12, .png 4 |
| `scratch\captures\03-ss3` | 7 | 7 | 450K | 10-16 17:00 | .bin 6, .png 1 |
| `scratch\ghidra` | 25 | 2 | 60M | 10-19 10:18 | .dat 6, .prp 4, .bak 4, .java 4, .gbf 3 |
| `scratch\ghidra\LoG2.rep` | 9 | 1 | 22M | 10-18 23:44 | .dat 3, .prp 2, .bak 2, .gbf 2 |
| `scratch\ghidra\LoG2.rep\idata` | 5 | 2 | 22M | 10-18 23:44 | .gbf 2, .bak 1, .dat 1, .prp 1 |
| `scratch\ghidra\LoG2.rep\user` | 1 | 1 | 63B | 10-16 16:34 | .dat 1 |
| `scratch\ghidra\LoG2.rep\versioned` | 2 | 2 | 126B | 10-18 23:44 | .bak 1, .dat 1 |
| `scratch\ghidra\scripts` | 4 | 4 | 6K | 10-16 17:01 | .java 4 |
| `scratch\ghidra\seeded` | 10 | 2 | 30M | 10-19 10:18 | .dat 3, .prp 2, .bak 2, .gpr 1, .gba 1 |
| `scratch\ghidra\seeded\LoG2seeded.rep` | 8 | 1 | 22M | 10-19 10:18 | .dat 3, .prp 2, .bak 2, .gbf 1 |
| `scratch\re` | 10867 | 22 | 562M | 10-24 10:01 | .png 9380, .py 597, .txt 550, .json 88, .md 79 |
| `scratch\re\__pycache__` | 1 | 1 | 5K | 10-16 16:37 | .pyc 1 |
| `scratch\re\asm` | 15 | 4 | 170K | 10-19 11:26 | .o 3, .md 2, .py 2, .s 2, .bin 2 |
| `scratch\re\asm\__pycache__` | 2 | 2 | 12K | 10-19 10:56 | .pyc 2 |
| `scratch\re\asm\ssj2_idle` | 9 | 1 | 15K | 10-19 11:14 | .o 3, .s 2, .bin 2, .elf 2 |
| `scratch\re\aura` | 2 | 2 | 7K | 10-18 16:43 | .py 2 |
| `scratch\re\base_audit` | 342 | 14 | 508K | 10-24 10:01 | .png 321, .py 14, .pyc 5, .json 2 |
| `scratch\re\base_audit\__pycache__` | 5 | 5 | 33K | 10-24 08:50 | .pyc 5 |
| `scratch\re\base_audit\set56` | 163 | 163 | 219K | 10-23 14:29 | .png 162, .json 1 |
| `scratch\re\base_audit\set59` | 160 | 160 | 219K | 10-23 14:29 | .png 159, .json 1 |
| `scratch\re\block` | 57 | 28 | 89M | 10-24 09:03 | .png 18, .py 16, .txt 6, .gba 5, .sav 5 |
| `scratch\re\block\__pycache__` | 3 | 3 | 40K | 10-24 08:35 | .pyc 3 |
| `scratch\re\block\mockups` | 12 | 12 | 80M | 10-24 08:49 | .gba 5, .sav 5, .txt 2 |
| `scratch\re\block\pose` | 14 | 14 | 550K | 10-24 09:03 | .png 9, .py 3, .md 2 |
| `scratch\re\cellgames` | 21 | 19 | 275K | 10-20 11:38 | .txt 9, .py 8, .md 2, .pyc 2 |
| `scratch\re\cellgames\__pycache__` | 2 | 2 | 12K | 10-20 11:22 | .pyc 2 |
| `scratch\re\chamber` | 32 | 32 | 575K | 10-19 00:18 | .txt 17, .png 7, .py 3, .bin 3, .md 2 |
| `scratch\re\chamber_proto` | 22 | 19 | 472K | 10-24 03:42 | .py 11, .txt 8, .md 2, .png 1 |
| `scratch\re\chamber_proto\backup` | 3 | 3 | 59K | 10-24 03:14 | .py 2, .txt 1 |
| `scratch\re\cutscene` | 10 | 9 | 74K | 10-18 18:19 | .py 7, .txt 2, .pyc 1 |
| `scratch\re\cutscene\__pycache__` | 1 | 1 | 5K | 10-18 17:50 | .pyc 1 |
| `scratch\re\decomp-review` | 4 | 4 | 207K | 10-20 14:44 | .md 3, .py 1 |
| `scratch\re\disasm` | 54 | 14 | 224M | 10-19 10:43 | .py 8, .txt 8, .java 6, .log 5, .c 5 |
| `scratch\re\disasm-port` | 3 | 3 | 192K | 10-22 19:25 | .md 2, .py 1 |
| `scratch\re\disasm\__pycache__` | 2 | 2 | 109K | 10-18 23:52 | .pyc 2 |
| `scratch\re\disasm\bf` | 3 | 3 | 429K | 10-18 23:45 | .json 1, .txt 1, .csv 1 |
| `scratch\re\disasm\eu` | 3 | 3 | 222K | 10-18 23:45 | .json 1, .txt 1, .csv 1 |
| `scratch\re\disasm\ghidra` | 32 | 17 | 222M | 10-19 10:22 | .java 6, .log 5, .c 5, .txt 4, .bak 3 |
| `scratch\re\effects` | 88 | 34 | 557K | 10-20 10:10 | .txt 68, .py 17, .md 2, .pyc 1 |
| `scratch\re\effects\__pycache__` | 1 | 1 | 18K | 10-20 08:36 | .pyc 1 |
| `scratch\re\effects\listings` | 53 | 53 | 246K | 10-20 07:33 | .txt 53 |
| `scratch\re\file_select` | 20 | 19 | 71K | 10-18 23:01 | .png 12, .py 4, .txt 3, .pyc 1 |
| `scratch\re\file_select\__pycache__` | 1 | 1 | 5K | 10-18 22:46 | .pyc 1 |
| `scratch\re\forms` | 8 | 8 | 18K | 10-16 19:58 | .py 4, .png 4 |
| `scratch\re\gamefaqs` | 2 | 2 | 47K | 10-23 17:12 | .json 1, .txt 1 |
| `scratch\re\gi` | 40 | 24 | 754K | 10-17 01:14 | .txt 12, .py 11, .crlf 6, .bin 6, .md 2 |
| `scratch\re\gi\rfix` | 10 | 10 | 222K | 10-17 01:14 | .crlf 6, .py 2, .sha1 2 |
| `scratch\re\gi\state1` | 6 | 6 | 387K | 10-17 00:38 | .bin 6 |
| `scratch\re\hud_ki` | 59 | 41 | 17M | 10-24 09:59 | .py 21, .png 18, .txt 11, .pyc 4, .md 2 |
| `scratch\re\hud_ki\__pycache__` | 2 | 2 | 16K | 10-24 03:01 | .pyc 2 |
| `scratch\re\hud_ki\mockups` | 6 | 6 | 16M | 10-24 03:02 | .txt 2, .gba 1, .sav 1, .ss2 1, .png 1 |
| `scratch\re\hud_ki\proto` | 10 | 8 | 64K | 10-24 09:59 | .py 5, .txt 2, .pyc 2, .png 1 |
| `scratch\re\inject` | 14 | 10 | 220K | 10-20 12:11 | .py 7, .txt 4, .md 2, .pyc 1 |
| `scratch\re\inject\backup` | 4 | 3 | 33K | 10-20 11:20 | .py 3, .pyc 1 |
| `scratch\re\intake` | 1759 | 12 | 36M | 10-18 19:19 | .png 1564, .txt 91, .py 60, .pyc 16, .gif 15 |
| `scratch\re\intake\art_r14` | 1747 | 0 | 19M | 10-18 16:22 | .png 1564, .txt 86, .py 55, .pyc 16, .gif 15 |
| `scratch\re\intake17` | 1332 | 29 | 23M | 10-18 22:21 | .png 1300, .py 12, .json 10, .txt 8, .md 1 |
| `scratch\re\intake17\art_r16` | 1303 | 0 | 7M | 10-18 18:57 | .png 1293, .json 10 |
| `scratch\re\intake18` | 1339 | 36 | 23M | 10-19 00:16 | .png 1299, .txt 13, .py 12, .json 10, .bak 3 |
| `scratch\re\intake18\art_r17` | 1303 | 0 | 7M | 10-18 21:22 | .png 1293, .json 10 |
| `scratch\re\npc_gi` | 6 | 5 | 32K | 10-18 19:50 | .py 5, .pyc 1 |
| `scratch\re\npc_gi\__pycache__` | 1 | 1 | 16K | 10-18 18:38 | .pyc 1 |
| `scratch\re\obfix` | 1038 | 33 | 6M | 10-23 13:53 | .png 989, .py 21, .txt 15, .json 10, .md 2 |
| `scratch\re\obfix\__pycache__` | 1 | 1 | 7K | 10-23 13:18 | .pyc 1 |
| `scratch\re\obfix\art` | 987 | 0 | 5M | 10-23 13:37 | .png 978, .json 9 |
| `scratch\re\obfix\backup` | 6 | 4 | 76K | 10-23 13:05 | .py 6 |
| `scratch\re\obfix\look` | 11 | 11 | 446K | 10-23 13:22 | .png 11 |
| `scratch\re\outfit` | 15 | 15 | 539K | 10-16 19:24 | .txt 9, .py 6 |
| `scratch\re\overview` | 54 | 53 | 219K | 10-17 04:50 | .txt 41, .py 12, .pyc 1 |
| `scratch\re\overview\__pycache__` | 1 | 1 | 6K | 10-17 04:02 | .pyc 1 |
| `scratch\re\palette_census` | 32 | 32 | 1M | 10-24 01:02 | .json 11, .py 10, .txt 9, .md 2 |
| `scratch\re\palette_use` | 6 | 6 | 308K | 10-23 23:42 | .py 3, .md 2, .png 1 |
| `scratch\re\palslot` | 28 | 28 | 34M | 10-19 21:33 | .py 12, .txt 11, .md 2, .gba 2, .json 1 |
| `scratch\re\piccolo` | 14 | 14 | 446K | 10-22 21:47 | .png 5, .txt 4, .py 3, .md 2 |
| `scratch\re\portraits` | 23 | 23 | 595K | 10-17 02:25 | .py 12, .png 10, .md 1 |
| `scratch\re\r19` | 1334 | 31 | 23M | 10-19 10:43 | .png 1293, .py 13, .txt 13, .json 10, .md 3 |
| `scratch\re\r19\art_r18` | 1303 | 0 | 7M | 10-19 00:02 | .png 1293, .json 10 |
| `scratch\re\r20` | 11 | 11 | 16M | 10-19 10:43 | .md 4, .py 3, .txt 3, .gba 1 |
| `scratch\re\r21` | 21 | 21 | 171K | 10-19 20:20 | .txt 11, .py 8, .md 2 |
| `scratch\re\r22` | 15 | 15 | 194K | 10-20 10:14 | .txt 8, .py 5, .md 2 |
| `scratch\re\r27` | 12 | 12 | 216K | 10-20 14:35 | .txt 6, .py 4, .md 2 |
| `scratch\re\r28` | 34 | 29 | 2M | 10-22 20:20 | .txt 15, .py 12, .pyc 5, .md 2 |
| `scratch\re\r28\__pycache__` | 5 | 5 | 46K | 10-22 20:15 | .pyc 5 |
| `scratch\re\r29` | 1387 | 30 | 8M | 10-22 21:47 | .png 1314, .py 50, .json 13, .txt 7, .md 2 |
| `scratch\re\r29\__pycache__` | 1 | 1 | 25K | 10-22 20:56 | .pyc 1 |
| `scratch\re\r29\art` | 1312 | 0 | 6M | 10-22 20:35 | .png 1300, .json 12 |
| `scratch\re\r29\backup` | 30 | 5 | 526K | 10-22 20:18 | .py 30 |
| `scratch\re\r29\look` | 14 | 14 | 434K | 10-22 20:56 | .png 14 |
| `scratch\re\r30` | 350 | 18 | 800K | 10-23 09:10 | .png 332, .txt 8, .py 5, .md 2, .json 2 |
| `scratch\re\r30\set59` | 160 | 160 | 219K | 10-23 08:12 | .png 159, .json 1 |
| `scratch\re\r30\set61` | 172 | 172 | 239K | 10-23 08:12 | .png 171, .json 1 |
| `scratch\re\r31` | 354 | 20 | 825K | 10-23 10:11 | .png 332, .py 13, .txt 5, .md 2, .json 2 |
| `scratch\re\r31\backup` | 4 | 4 | 65K | 10-23 09:36 | .py 4 |
| `scratch\re\r31\set103` | 170 | 170 | 245K | 10-23 09:29 | .png 169, .json 1 |
| `scratch\re\r31\set158` | 160 | 160 | 219K | 10-23 09:29 | .png 159, .json 1 |
| `scratch\re\r32` | 18 | 15 | 331K | 10-23 12:49 | .py 9, .txt 7, .md 2 |
| `scratch\re\r32\backup` | 3 | 3 | 67K | 10-23 12:33 | .py 3 |
| `scratch\re\r33` | 55 | 28 | 468K | 10-23 14:30 | .txt 30, .png 16, .py 6, .md 2, .pyc 1 |
| `scratch\re\r33\__pycache__` | 1 | 1 | 11K | 10-23 14:30 | .pyc 1 |
| `scratch\re\r33\backup` | 1 | 1 | 22K | 10-23 12:38 | .py 1 |
| `scratch\re\r33\listings` | 25 | 25 | 126K | 10-23 13:58 | .txt 25 |
| `scratch\re\r34` | 11 | 9 | 58K | 10-23 14:32 | .py 5, .txt 4, .png 2 |
| `scratch\re\r34\backup` | 2 | 2 | 42K | 10-23 14:29 | .py 2 |
| `scratch\re\r35` | 28 | 17 | 389K | 10-23 20:56 | .txt 14, .py 6, .png 6, .md 2 |
| `scratch\re\r35\backup` | 2 | 2 | 43K | 10-23 18:32 | .py 2 |
| `scratch\re\r35\listings` | 9 | 9 | 30K | 10-23 18:04 | .txt 9 |
| `scratch\re\r38` | 4 | 4 | 289K | 10-24 08:45 | .md 2, .py 1, .txt 1 |
| `scratch\re\remaster` | 188 | 96 | 9M | 10-23 17:36 | .py 86, .png 81, .txt 21 |
| `scratch\re\remaster\anime` | 92 | 88 | 5M | 10-23 17:36 | .py 50, .png 38, .txt 4 |
| `scratch\re\save` | 46 | 21 | 875K | 10-18 23:17 | .txt 18, .py 15, .pyc 12, .sh 1 |
| `scratch\re\save\__pycache__` | 7 | 7 | 33K | 10-18 23:17 | .pyc 7 |
| `scratch\re\save\slot3` | 18 | 13 | 280K | 10-18 20:47 | .txt 8, .py 5, .pyc 5 |
| `scratch\re\set57_png` | 200 | 200 | 204K | 10-16 16:47 | .png 200 |
| `scratch\re\status_same` | 16 | 10 | 558K | 10-19 08:42 | .bin 6, .py 4, .txt 4, .md 2 |
| `scratch\re\status_same\st_r18` | 6 | 6 | 387K | 10-19 07:36 | .bin 6 |
| `scratch\re\superperfect` | 307 | 31 | 24M | 10-23 22:37 | .png 252, .py 31, .txt 16, .md 3, .json 2 |
| `scratch\re\superperfect\aura_work` | 209 | 9 | 471K | 10-22 21:46 | .png 203, .py 4, .json 2 |
| `scratch\re\superperfect\ids` | 4 | 4 | 11K | 10-22 18:52 | .png 4 |
| `scratch\re\superperfect\portrait` | 25 | 9 | 7M | 10-23 17:53 | .png 16, .py 9 |
| `scratch\re\superperfect\portrait2` | 38 | 6 | 15M | 10-23 22:37 | .png 29, .py 6, .npy 2, .pyc 1 |
| `scratch\re\t6` | 6 | 6 | 60K | 10-17 02:00 | .py 3, .sh 1, .txt 1, .md 1 |
| `scratch\re\toolreview` | 8 | 4 | 16M | 10-22 16:44 | .py 3, .md 2, .txt 1, .csv 1, .gba 1 |
| `scratch\re\toolreview\out` | 2 | 2 | 66K | 10-22 16:37 | .txt 1, .csv 1 |
| `scratch\re\toolreview\rom` | 1 | 1 | 16M | 10-20 14:03 | .gba 1 |
| `scratch\re\toolreview\vendor` | 1 | 1 | 6K | 10-22 16:35 | .py 1 |
| `scratch\research` | 988 | 0 | 10M | 10-18 02:14 | .png 893, .py 43, .bin 25, .json 12, .txt 9 |
| `scratch\research\bf-sprites` | 907 | 137 | 8M | 10-17 03:30 | .png 861, .py 23, .json 12, .txt 6, .pyc 4 |
| `scratch\research\bf-sprites\__pycache__` | 4 | 4 | 21K | 10-17 03:23 | .pyc 4 |
| `scratch\research\bf-sprites\log2` | 735 | 5 | 1005K | 10-17 03:28 | .png 725, .txt 5, .json 5 |
| `scratch\research\bf-sprites\view` | 31 | 31 | 2M | 10-17 03:30 | .png 31 |
| `scratch\research\status` | 81 | 43 | 2M | 10-18 02:14 | .png 32, .bin 25, .py 20, .txt 3, .md 1 |
| `scratch\research\status\bf` | 10 | 10 | 92K | 10-17 03:40 | .png 10 |
| `scratch\research\status\overflow` | 2 | 2 | 6K | 10-17 22:14 | .png 1, .py 1 |
| `scratch\research\status\states` | 26 | 2 | 2M | 10-17 03:37 | .bin 24, .png 2 |
| `scratch\saves` | 3 | 3 | 24K | 10-18 20:46 | .sav 3 |
| `scratch\sdd` | 10765 | 3 | 93M | 10-24 09:53 | .png 9836, .py 390, .md 273, .txt 103, .json 64 |
| `scratch\sdd\slice1` | 10762 | 186 | 93M | 10-24 09:53 | .png 9836, .py 390, .md 270, .txt 103, .json 64 |
| `scratch\sdd\slice1\backups` | 5 | 0 | 142K | 10-17 22:22 | .md 3, .py 2 |
| `scratch\sdd\slice1\gi-fix-1125` | 489 | 5 | 4M | 10-17 12:46 | .png 484, .json 3, .py 1, .bak 1 |
| `scratch\sdd\slice1\gi-fix-step-work` | 2305 | 26 | 17M | 10-17 23:29 | .png 2272, .json 15, .py 11, .gif 3, .orig 2 |
| `scratch\sdd\slice1\gi-rules-night-work` | 902 | 77 | 7M | 10-18 01:10 | .png 869, .py 21, .json 6, .txt 4, .md 1 |
| `scratch\sdd\slice1\owner-0853-work` | 901 | 44 | 6M | 10-18 09:50 | .png 838, .py 43, .pyc 11, .json 6, .diff 1 |
| `scratch\sdd\slice1\owner-0948-work` | 3575 | 37 | 28M | 10-18 12:20 | .png 3475, .py 52, .json 22, .pyc 17, .txt 6 |
| `scratch\sdd\slice1\shared-body-1240-work` | 2148 | 34 | 25M | 10-18 15:57 | .png 1898, .py 99, .txt 88, .pyc 33, .gif 15 |
| `scratch\sdd\slice1\snapshots` | 251 | 0 | 2M | 10-17 02:43 | .py 161, .md 90 |
| `scratch\sprites` | 3173 | 0 | 4M | 10-17 23:31 | .png 3153, .json 20 |
| `scratch\sprites\set103` to `set140`, `set53` to `set61` (20 folders) | 103-174 each | all direct | 140K-245K each | 10-16 to 10-17 | .png, 1 manifest.json each |
| `scratch\sprites_backup_2330` | 1 | 1 | 2K | 10-17 23:31 | .png 1 |
| `scratch\venv` | 2450 | 0 | 68M | 10-22 18:03 | .py 887, .pyc 887, .pyi 275 |
| `scratch\verify` | 3 | 3 | 2K | 10-16 16:52 | .bin 3 |
| `scripts` | 164 | 0 | 3M | 10-24 08:34 | .py 74, .pyc 72, .png 10, .json 4, .txt 2 |
| `scripts\one-time` | 0 | 0 | 0B | - | |
| `scripts\permanent` | 164 | 22 | 3M | 10-24 08:34 | .py 74, .pyc 72, .png 10, .json 4, .txt 2 |
| `scripts\permanent\__pycache__` | 18 | 18 | 583K | 10-23 13:36 | .pyc 18 |
| `scripts\permanent\art` | 13 | 3 | 21K | 10-24 01:27 | .png 10, .json 2, .md 1 |
| `scripts\permanent\art\portraits` | 10 | 10 | 18K | 10-24 01:27 | .png 10 |
| `scripts\permanent\patches` | 40 | 20 | 403K | 10-24 08:24 | .py 20, .pyc 20 |
| `scripts\permanent\patches\__pycache__` | 20 | 20 | 243K | 10-24 08:24 | .pyc 20 |
| `scripts\permanent\re` | 10 | 3 | 472K | 10-19 09:10 | .py 3, .pyc 3, .json 2, .txt 1, .csv 1 |
| `scripts\permanent\re\__pycache__` | 3 | 3 | 132K | 10-19 09:10 | .pyc 3 |
| `scripts\permanent\re\data` | 4 | 4 | 272K | 10-19 09:07 | .json 2, .txt 1, .csv 1 |
| `scripts\permanent\tests` | 61 | 30 | 1M | 10-24 08:34 | .pyc 31, .py 30 |
| `scripts\permanent\tests\__pycache__` | 31 | 31 | 1M | 10-24 08:34 | .pyc 31 |

`scratch\build` file names (C): `log2_hack`, `log2_pad16` (3), `log2_poc` (3), `log2_poc_gi`, `log2_poc_t6`, `log2_poc_r2` to `r38` with `.sav`, `.ss1`-`.ss5`, and twins `_chamber`, `_chamber2`, `_scouter`, `_spar`, `_preview`, `_preview2`, `_hud`. 66 `.gba`, 58 `.sav`, 136 state files.
