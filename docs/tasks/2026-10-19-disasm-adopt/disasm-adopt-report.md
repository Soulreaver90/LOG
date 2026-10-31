# Disassembly tools adopted and Ghidra seeded: report (2026-10-19)

This report answers the brief `disasm-adopt.md`, which I approved at 8:40 AM on 2026-10-19. No ROM was built or changed. Nothing under `data\` was written. `docs\RE-BIBLE.md` was not edited: proposed rows are in section 6.

Labels: **C** = CONFIRMED (a test, a count or output you can re-run), **L** = LIKELY, **S** = SPECULATIVE.

---

## 1. Summary

| Ask | Result | Label |
|---|---|---|
| Adopt `codemap.py`, `symbols.py`, `listing.py` | In `scripts\permanent\re\`, with header blocks. They run from the `scripts\permanent` root with `py -3 -I`. Scratch copies kept | C |
| Outputs | Committed snapshot in `scripts\permanent\disasm\data\` (reason in section 2) | C |
| Tests | `tests\test_re_tools.py`: 12 tests, all pass. Whole suite: 328 tests, OK (159 s) | C |
| `sym("idle_tick")` helper | `scripts\permanent\rom\re_sym.py`, shown in one test only. No patch changed | C |
| New Ghidra project | `scratch\ghidra\seeded\LoG2seeded.gpr`. The old `scratch\ghidra\LoG2.gpr` is untouched (last write 2026-10-16) | C |
| Codemap starts that became Ghidra functions | **2,264 of 2,264** seeded starts kept through analysis, all in their codemap mode (Thumb or ARM). The seeding forces these starts in, so this does not confirm the stage 2-4 starts: those stay LIKELY | C (kept), L (stage 2-4 starts) |
| Error bookmarks (bad instructions, disassembly conflicts) | **0** in every block: Ghidra's own disassembler decodes all forced starts without a conflict | C |
| False functions left (functions Ghidra added in data) | **0** (the study run had 2,353) | C |
| Decompile of 5 named functions | `idle_tick`, `scene_type1` (`@0x0800B438`), `get_set`, `damage`, `portrait`, with our names in the output | C |

---

## 2. Task 1: the adopted tools

### Files

| File | What it is |
|---|---|
| `scripts\permanent\disasm\codemap.py` | Whole-ROM code map. Default output is now `scripts\permanent\disasm\data\` (USA) or `scripts\permanent\disasm\data\<game>\` |
| `scripts\permanent\disasm\symbols.py` | 315 names. New: `ptr(name)` (start + 1 for Thumb, start for ARM) and `mode_of(addr)`. `json` writes `scripts\permanent\disasm\data\symbols.json`. `check` reads `scripts\permanent\disasm\data\codemap.json` |
| `scripts\permanent\disasm\listing.py` | Annotated listing and `--refs`. Default `--map` is `scripts\permanent\disasm\data\codemap.json` |
| `scripts\permanent\disasm\data\` | `codemap.json`, `coverage.txt`, `functions.csv`, `symbols.json` (USA) |
| `scripts\permanent\rom\re_sym.py` | The import helper for patches: `sym`, `sym_rom`, `sym_ptr` |
| `scripts\permanent\tests\test_re_tools.py` | The tests |

Only the path lines and header blocks changed in the three tools. A fresh `scripts\permanent\disasm\codemap.py` run writes a `codemap.json` that is byte-identical to the scratch run of 2026-10-18 (SHA-256 match). Label C.

### Why a committed snapshot, not regenerate on demand

- `listing.py` and the Ghidra seeding both read `codemap.json`. A snapshot makes them work without a 7 s rebuild first.
- `listing.py` refuses a `codemap.json` made from another ROM (SHA-1 check).
- `test_snapshot_matches_a_fresh_build` rebuilds the map and fails when the snapshot is stale. After a change to `codemap.py` or the `symbols.py` function list, re-run `py -3 -I scripts\permanent\disasm\codemap.py` and `py -3 -I scripts\permanent\disasm\symbols.py json`.
- The test compares `codemap.json` only. `functions.csv` and `symbols.json` carry bible row tags, which change each time a task adds a bible row. Comparing them would make the test fail for reasons that have nothing to do with code.

### Why `re_sym.py` sits outside `re\`

`re\` cannot be a Python package, because `re` is the standard regex module. A `re\__init__.py` could shadow it in any process that has `scripts\permanent` first on `sys.path`. So `re_sym.py` sits at the `scripts\permanent` root and loads `scripts\permanent\disasm\symbols.py` by file path. It is the one file outside the brief's file list. It is new and has a unique name, so it cannot collide with the parallel tasks.

A patch uses it like this (not applied to any patch):

```python
from re_sym import sym, sym_ptr
VANILLA_TICK = sym_ptr("idle_tick")                         # 0x08007571
VTABLES = (sym("vt_state0_idle"), sym("vt_state38"))         # 0x08025A84, 0x08024BA0
```

An unknown name raises `KeyError` with the three closest names, for example `sym("idle_tik")`.

### Tests (12, all pass)

| Test | Pins | Label |
|---|---|---|
| `test_function_count_and_modes` | 2,264 functions: 2,234 Thumb, 30 ARM | C |
| `test_code_region_and_coverage` | `code_hi` 0x08028724, 99.40 % classified, 0 stray BL pairs, 2,268 IWRAM bytes decoded | C |
| `test_every_func_symbol_is_a_start_with_its_mode` | All 226 function symbols are codemap starts in their mode | C |
| `test_snapshot_matches_a_fresh_build` | `scripts\permanent\disasm\data\codemap.json` equals a fresh build | C |
| `test_get_set`, `test_idle_tick`, `test_portrait`, `test_damage`, `test_status_page` | The 5 bible functions of the study (section 5), by name: set table literal, idle bytes and 3 vtable slots, `bgt` and `portrait_block`, damage constants and `rand16` / `rand_n`, extent 0x362 and the `appearance_table` load | C |
| `test_appearance_table_refs_are_the_hand_list` | `--refs` returns exactly `ssj2_form.TABLE_LITERALS` plus `REVERSE_LITERAL` (18 words), 0 outside the code region | C |
| `test_names_are_unique_and_json_matches` | 315 unique names; `symbols.json` matches `symbols.py` | C |
| `test_patch_constants_by_name` | The helper: `ssj2_idle` constants equal `sym` / `sym_ptr` results | C |

Run (from `scripts\permanent`): `py -3 -I -m unittest discover -s . -p "test_re_tools.py"` (about 17 s). Note: `-m unittest tests.test_re_tools` fails under `-I`, because isolated mode leaves the current folder off `sys.path`.

---

## 3. Task 2: the seeded Ghidra project

### How it was built

| Step | Detail | Label |
|---|---|---|
| Import | `analyzeHeadless` with BinaryLoader, `ARM:LE:32:v4t`, compiler spec `default`, base 0x08000000. The ROM is a copy in `scratch\ghidra\seeded\log2_usa.gba` (SHA-1 `18e0715d...` checked), because the batch file fails on the parentheses in the original name | C |
| Memory | `rom_code` 0x08000000-0x08028723 (read, execute), `rom_data` to the end (read only, no execute), `iwram_code` 0x03000000-0x03000E7B from rom:0x7FD6BC (bible s14 #boot row, crt0 copy), `iwram` to 0x03007FFF, `ewram` 0x02000000 (0x40000 bytes), `io` 0x04000000 (0x400 bytes, volatile) | C |
| Analyzers off | Names taken from a dump of the program's options (`AnalyzerList.java`), not from memory: Function Start Pre Search, Function Start Search, Function Start Search After Code, Function Start Search After Data, Create Address Tables, Embedded Media. ARM Aggressive Instruction Finder and Aggressive Instruction Finder were already off; the script sets them off anyway | C |
| Seeds | `SeedSetup.java` sets TMode on each of the 2,264 starts first (1 Thumb, 0 ARM), then disassembles, creates the functions, applies 226 names with a bible-tag plate comment, fixes the bodies, and adds 89 labels for tables, vtables and RAM globals | C |
| Analysis | Full auto-analysis with the remaining analyzers. It finished, with no timeout. The whole import took 54 s. `SeedReport.java` counts 0 Error bookmarks in the program. The final numbers come from a second run of the README commands exactly as written (the `-overwrite` path) | C |

### Numbers (`seeded_compare.py`)

| Measure | Seeded (2026-10-19) | Study run, unseeded (2026-10-18) |
|---|---|---|
| Ghidra functions | 2,289 | 3,202 |
| Codemap starts that are Ghidra functions, same mode | **2,264 of 2,264** (seeded, so kept, not found) | 780 of 2,254 code-region starts (found by Ghidra) |
| Error bookmarks | 0 | not counted |
| Codemap starts in the other mode, or missing | 0 | n/a |
| Ghidra only, inside a codemap body | 25 | 33 |
| Ghidra only, elsewhere in code | 0 | 2 |
| Ghidra only, outside code (false functions) | **0** | 2,353 |
| Symbol names kept after analysis | 226 of 226 | n/a |

The 25 extra functions are all ARM halves of Thumb `bx pc ; nop` veneers, at codemap start + 4 (checked: each such start holds `bx pc`, 0x4778, and Ghidra has the half in ARM mode). Codemap flags 37 bodies as veneers; Ghidra split 25 of them. They are real code, not false functions. Ghidra makes them thunks, for example `thunk_FUN_03000348`. Label C.

Two changes came together: analyzers off and `rom_data` not executable. This run does not show which change removes the false functions. Label S for the split. The result (0) is C.

### Decompile samples (`scripts\permanent\ghidra\decomp\*.c`)

`Decomp.java` runs read-only and honours the read-only ROM, so literal-pool loads fold to constants and RAM symbols show by name. All 5 files contain our names (grep). Label C.

| Function | Names and facts in the output |
|---|---|
| `idle_tick` | Own name and bible tag (leaf: no callees). `obj+0x12 += 1; obj+0x14 = (0xf0 < (tick & 0xff))`, as bible s4 |
| `scene_type1` `@0x0800B438` | Calls `dialog_box(...)` with the record + 4 as the text |
| `get_set` | `player_ptr`, `save_struct`, `appearance_set(...)`; ids 7 and up read `0x083B4E74 + id * 4` (set table - 7 * 4) |
| `damage` | `rand16(STR * 0xa4)`, `rand_n(0x1a)`, and the s14 f(S) as `S * (S * (S * 0x1a - 0x2bd) + 0x1c3a2) >> 8` (26, -701, 115618) |
| `portrait` | `save_struct`, `appearance_portrait(...)`, ids 8 and up read `portrait_block + 4 + id * 4` |

`get_set` (excerpt):

```c
/* get_set  (bible s4 #sprite #form C OUT) */
undefined4 get_set(int param_1)
{
  ...
  if (param_1 == 0) {
    if (player_ptr == 0) {
      uVar1 = appearance_set(&DAT_03000e9c + (uint)save_struct * 0xe);
    }
    else {
      uVar1 = *(undefined4 *)(player_ptr + 0x48);
    }
  }
  else if (param_1 < 7) {
    uVar1 = appearance_set(&DAT_03000e9c + (param_1 + -1) * 0xe);
  }
  else {
    uVar1 = *(undefined4 *)(&DAT_083b4e74 + param_1 * 4);
  }
  ...
```

### Files in `scripts\permanent\ghidra\`

`SeedSetup.java` (pre-script), `SeedReport.java` (export), `Decomp.java`, `AnalyzerList.java` (probe), `seeded_compare.py`, `README.md`, `decomp\*.c`, and the logs `seeded_*.txt|log` and `decomp_*.txt|log`. The study files (`FuncList.java`, `SeedEntry.java`, `proj\`) are unchanged.

---

## 4. How I open the project

1. Start `%USERPROFILE%\Tools\ghidra_12.1.4_PUBLIC\ghidraRun.bat`.
2. Select **File > Open Project** and open `scratch\ghidra\seeded\LoG2seeded.gpr`.
3. Double-click `log2_usa.gba`. If Ghidra asks "Analyze now?", select **No**.
4. Press **G** and type a name such as `idle_tick`.

The rerun commands are in `scripts\permanent\ghidra\README.md`. A rerun uses `-overwrite` and deletes GUI edits.

---

## 5. Concerns

- **`re_sym.py` is outside the brief's file list** (section 2). It is a new root file.
- **The test imports `patches.ssj2_form` and `patches.ssj2_idle`.** The proof is that the helper and `--refs` match the patch constants. If the r19 task changes those constants, `test_re_tools` fails on purpose.
- **The snapshot must be refreshed by hand** after a change to `codemap.py` or the symbol list. The snapshot test says so when it fails.
- **Two copies of the tools now exist.** The scratch copies still write to `scripts\one-time\2026-10-18-disasm-study\`. Only the `scripts\permanent\re\` copies are maintained.
- **A rerun of the seeding wipes GUI work** (`-overwrite`). A later "apply names only" script on an existing program would fix that. Not built.
- **GUI analysis settings.** `SeedSetup.java` stores the analyzer options in the program. A GUI analysis should respect them. Label L: not tested in the GUI.
- **The 8 MB ROM copy** in `scratch\ghidra\seeded\` exists only because of the batch-file quoting problem.

---

## 6. Proposed bible rows (not written to the bible)

Source tag `DSA` (this report), with tags from the bible's own list (section 1). The section numbers follow the study's `DIS` rows. Add to the section 1 source list: `DSA` = `docs\tasks\2026-10-19-disasm-adopt\disasm-adopt-report.md`.

| Section | Fact | Tags | Label | Src |
|---|---|---|---|---|
| 11 | Route C tools adopted (2026-10-19): `scripts\permanent\disasm\codemap.py`, `symbols.py`, `listing.py`; snapshot outputs in `scripts\permanent\disasm\data\`; patches name addresses with `from re_sym import sym, sym_rom, sym_ptr` (`re\` cannot be a package: stdlib `re`); tests `tests\test_re_tools.py` (12) | #tool | C | DSA |
| 11 | Seeded Ghidra project `scratch\ghidra\seeded\LoG2seeded.gpr` (program `log2_usa.gba`, a ROM copy): all 2,264 seeded codemap starts kept as functions in their mode, 0 Error bookmarks, 226 names, 89 labels, 0 functions in data, analysis 54 s; rerun steps in `scripts\permanent\ghidra\README.md`. The seeding does not confirm the stage 2-4 starts | #tool | C (counts), L (stage 2-4 starts) | DSA |
| 11 | Ghidra 12.1.4 analyzer names that search data for code on this ROM: Function Start Pre Search, Function Start Search, Function Start Search After Code, Function Start Search After Data, Create Address Tables, Embedded Media (ARM Aggressive Instruction Finder is off by default). Turned off together with `rom_data` (rom:0x28724 on) not executable: 0 functions in data against 2,353 | #tool #decision | C (names, count), S (which change does it) | DSA |
| 14 | Thumb `bx pc ; nop` veneers: for 25 of the 37 codemap veneer bodies, Ghidra makes the ARM half at start + 4 a separate thunk function; codemap keeps it in the Thumb body | #boot #codec | C | DSA |
| 14 | Ghidra decompile of `@0x0800F910` (damage), ROM read only: `S * (S * (S * 0x1a - 0x2bd) + 0x1c3a2) >> 8`, `rand16(S * 0xa4)`, `rand_n(0x1a)`; same constants as the s14 f(S) row | #combat | C | DSA |
