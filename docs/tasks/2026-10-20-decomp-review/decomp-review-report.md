# Decomp review: the Buu's Fury decomp, and the same for LoG II (2026-10-20)

Scope cut to a high-level overview by me mid-run, so the sample mapping stops at what was already proven.

Clone: `%USERPROFILE%\Documents\GitHub\buusfury-decomp` (8870c2f), read as data only. Nothing in it was run, imported or edited. Evidence script: `scripts\one-time\2026-10-20-decomp-review\probe.py` (our code, `py -3 -I -B`, ROMs read-only). Outputs: `scripts\one-time\2026-10-20-decomp-review\mapping.md` (25 rows), `scripts\one-time\2026-10-20-decomp-review\bible_rows.md` (LoG II rows, sections 5, 9, 14).

---

## Recommendation

**Keep our own approach and borrow parts.** Do not adopt their build for LoG II.

| Borrow | Why |
|---|---|
| The Webfoot packer `tools\webfoot\webfoot_lz.py` `pack()` | We have no compressor (bible section 3). It is pure Python, MPL-2.0 (keep its licence header in the file). Review it, then test round trips with our own decoder before use. |
| Names and formats proven to match LoG II (see Gains) | Free names for the heap, AI nodes, sound and colour tables. |
| Their Buu's Fury table addresses | Direct pointers for the merge (Q4). |
| The idea of an INCBIN skeleton plus per-format generators | Useful if we ever build a source tree, but with GNU tools. |

Reasons not to adopt: the build needs ADS 1.2, the tree is not relocatable, and almost all of it is Buu's Fury specific constants.

---

## 1. What it really is

| Point | Finding | Label |
|---|---|---|
| Real C | 12 `src\sub_*.c` units are linked, 716 B of code in total (scatter regions `scatter.ld:194-285`). `src\GBARam.c` is a NONMATCHING reference, not built (`GBARam.c:1`). Plus 4,608 B of colour tables (`src\color_transforms.cpp`) and 89,012 B of generated strings | C |
| Assembly | 143,522 instruction lines, 16,587 labels, of which 60 have real names (the GBARam heap, BMP corners, `MaybeStart`, `Region_TitlescreenMenu`). Everything else is `sub_`/`loc_`/`unk_` (`probe.py census`) | C |
| Raw data | 3,344 `INCBIN baserom.gba_0x..` slices = 585,508 B; 9,419 INCBINs of build-time generated files | C |
| "92.7 %" | Every byte not INCBIN'd from a raw slice (`README.md:17-33`, `docs\DEFINITION_OF_DONE.md`). It counts 292,440 B of 0xFF fill, 733,911 B of PCM, and assets that generators re-encode from the user's ROM at build time. It does not mean named or understood code | C |
| Relocatable? | No. `scatter.ld:189-301` pins every region to a fixed address, and 5,480 operands are `|label| + offset` into raw slices (for example `asm\buu.s` `BL |inc_0x153f2_0x1a3f2| + 0x870`) | C |
| Build | `extract.cmd` checks the ROM SHA-1 (`tools\extract\extract.py`), writes 17 ROM-derived inputs; `rebuild.cmd` slices the ROM, compiles with `tcpp`/`armcpp`, assembles with `armasm`, links with `armlink` + scatter, converts with `fromelf` (`rebuild.cmd:5-10, 500-548`); `tools\gate\gate.py` checks the digest | C |
| Toolchain | ADS 1.2 build 805 (`INSTALL.md:56`). CONTRIBUTING says `tcpp -O2 -Otime -apcs /nointerwork` (`CONTRIBUTING.md:119-125`), but the real flags vary per unit: six units use `/interwork`, five of them without `-Otime` (`rebuild.cmd:503-525`) | C |
| Semantic depth | Thin. Field names are mostly `word_08`; the authors could not reach the first battle in their own runs (`docs\research\PLAY_CHECKLIST.md:489-491`). Their runtime tool is a private recompiler not in the repo (`PLAY_CHECKLIST.md:37`) | C |

### Can a free toolchain replace ADS 1.2?

- **Assembly: yes, with a converter.** The `.s` files use armasm syntax and an ADS scatter file. GNU as and ld (we have arm-none-eabi 15.2) could build the same bytes after a syntax and linker-script conversion. Every instruction is fixed, so encoding choices can fall back to `.hword`. LIKELY, not tried (a run would be needed).
- **C: no.** The C units match only under `tcpp` build 805. No free compiler reproduces those bytes. Our bible already found ARM-toolchain shapes in LoG II (section 14, DIS row), so LoG II has the same block. C (for BF), L (for LoG II).

---

## 2. Gains for LoG II (proven against LoG II bytes)

| Gain | LoG II fact | Label |
|---|---|---|
| Heap allocator names | `malloc` `@0x0801F08C` (309 BL sites), `free` `@0x0801F110`, init, free-list helpers; heap at `0x02000800`, free-list tail `@0x030022B4`. Same bodies as BF `GBARam_*` | C |
| AI node format | 152 rows at `@0x086D5194`; nodes `{activate, evaluate, release, count}`; composites `0x0801B63F` (seq) and `0x0801B887` (or). Clean walk, 340 nodes | C (format), L (names) |
| Enemy +0x14 | The "death descriptor" is an AI-node-shaped record, the same field as BF enemy +0x14 | C (shape) |
| Sound | Music record fields: +8 is a 12-byte sample directory (101 slots, the SFX layout), not "instruments"; `sound_start` and `music_play` match BF bodies | C |
| Map format | 56-byte map entry with the same count/pointer pairs in both games; layer factories match | C |
| Colour LUTs | 14 index remap tables at `rom:0x6D0DD0`-`0x6D1BCF`: grey, dim, red x3, white x5, green x4; IWRAM pointer words follow | C (class), L (names) |
| crt0 | 32 of 38 words equal to BF; only literals and one branch differ | C |
| Codec | Same Webfoot bit grammar as ours. Two differences to check against the ARM routine: their decoder seeds the literal width from the header type (`webfoot_lz.py:253-258`), ours errors on a literal before the mode is set; their raw run reads 2 bytes per continue bit (`webfoot_lz.py:187-192`), ours 256 (`webfoot_decompress.py:136-139`, as does their `tools\research\jcalg1.py:145-151`). Real data decodes with both, so this is LIKELY unreached code | L |
| Codec identity | Their gate rebuilds the packed assets with `compress.exe` built from JCALG1 and claims a digest match (`NOTICE:144-147`, `tools\research\generate_jcalg1.py:1-13`). That supports bible row 462 (codec = JCALG1) | L (their claim, not run) |

Not matched by masked signature: the 12 `src\sub_*.c` units, the script interpreter `0x08004038`, `MaybeStart`, the placement and sibling factories. This agrees with the DIS row: the script VM and menus differ between the games.

---

## 3. The same for LoG II

### Steps (with our tools, not theirs)

1. Emit asm for the code region `rom:0x0-0x28723` and the IWRAM block from our codemap (2,264 functions, 99.4 % classified) with `thumb_dis`; pools as `.word`; the other 98 % of the ROM as `.incbin` slices.
2. Assemble and link with arm-none-eabi as and ld at fixed addresses; compare SHA-1 `18e0715d...`.
3. Optional and large: make it shiftable. Turn every pointer into a symbol (bible DIS row: 1,350 code pool words, 10,973 data-to-code words, 54,744 data-to-data words, plus unaligned script pointers), with format parsers for maps, layouts, sprites, scripts and AI nodes.

### Their tools: generic or game-specific

| Generic, reusable | Game-specific (hard-coded BF `BASE`, `COUNT`, `CONSUMER` constants) |
|---|---|
| `webfoot_lz.py`, `tilebank\tilebank.py`, `payload_store.py`, `intervals.py`, `encode_cache.py`, the gate idea | `mapcontainer\*`, `spritecontainer\*`, `structured\families.py`, `assetrecords\*`, `text\strings_table.py`, nearly all of `research\*` |

### Effort (rough task sessions)

| Stage | Sessions | Label |
|---|---|---|
| Byte-matching, fixed-address asm build of LoG II with GNU tools | 1-2 | L |
| Shiftable tree (pointer symbolization plus format parsers, shift tests in mGBA) | 8-15 | S |
| Matching C | blocked without ADS 1.2 | C |

### Could our patch pipeline move onto it?

- **Fixed-address tree:** little gain. Patches become readable asm diffs, but `log2_build.py`, the allocator and the expansion area stay, because nothing can grow in place.
- **Shiftable tree:** real gain. Code and tables (set table, appearance table, map table, scripts) could grow in place, with no allocator and no repointing. The cost is the 8-15 sessions above and the risk that a missed pointer breaks the game silently.
- So the advice is: keep `log2_build.py` and the inject tool now; revisit a shiftable tree only if repointing work starts to dominate later slices.

---

## 4. Buu's Fury facts for the merge (from their files, checked against the BF ROM)

| Item | Where | Label |
|---|---|---|
| All text is UTF-16 (99.5 % ASCII code points): `rom:0x5792C`, 1,534 strings per `tools\text\strings_layout.json`; "Gohan" has 21 UTF-16 hits and 0 ASCII hits. Corrects bible row 655 (BF text "not ASCII"): it is ASCII in 16-bit units | C |
| Sprite definitions: 297 at table `rom:0x6B6BDC` (`spritefamily.py`), 1,017 animations, 10,980 frames; a frame is `{u32 piece count, u32, pieces}` and each 12-byte piece is the LoG II frame record. 21 frames have 2 or 4 pieces. Refines the BFS "290 sets, 20-byte record" | C |
| Map entries `rom:0x8E2E0` (452, same layout as LoG II); tile banks `rom:0x179764` (187) | C |
| Enemy stats `rom:0x711274` (150 x 28 B: EXP, HP, id, 4 stat bytes, 2 factors, descriptor, extra pointer) | L (fields beyond HP and +0x14) |
| AI rows `rom:0x70F514` (828); event pool `rom:0x77C5A4` with index `rom:0x79B704` (522 records, header `{n, 0, type}`) | C (bounds), L (role) |
| Music `rom:0x3BB78C` (53 x 20 B), sample directory `rom:0x36D18C` (79 x 12 B); palettes BG `rom:0x5632C`, OBJ `rom:0x5652C` (`tools\extract\extract.py`) | C |
| Save, EEPROM, equipment, special moves: the search returned nothing by two shapes (keywords in `.md/.py/.json/.s`; the EEPROM and SRAM addresses `0x0D000000`, `0x0E000000`). The decomp does not cover them | C (absence by these shapes only) |

These are `game:bf` facts, so they are not in `bible_rows.md` (the brief limits it to LoG II). I may add them as `game:bf` rows.

---

## 5. Safety

| Item | Risk |
|---|---|
| `.githooks\pre-commit` | Opt-in only. `core.hooksPath` is not set in the clone (checked read-only). If enabled, it runs `tools\lint\lints.py` and `tools\check_links.py` on commit |
| `conftest.py` | pytest would load it on any test run in the tree; it only makes a temp folder. CI (`.github\workflows\check.yml`) runs pytest on GitHub, not locally |
| `tools\bytematch_upload.ps1` | Network: POSTs a report to `https://bytematch.dev` with `BYTEMATCH_TOKEN` (lines 24-25). Runs the whole gate first |
| `tools\compress\compress.exe` | Prebuilt Windows binary from a third party. `generate_tilebank.py:106`, `generate_mapcontainer.py:475`, `other_compressed.py:97` and `generate_jcalg1.py` execute it during `extract.cmd`/`rebuild.cmd` |
| `tools\encode_cache.py:21` | Writes a machine-wide cache under `%LOCALAPPDATA%\buusfury-decomp\` |
| `rebuild.cmd:10`, `gate.py:221-226` | `cd /d` into the tree; the gate deletes build outputs and caches with `rmtree`, and runs `extract.cmd` and `rebuild.cmd` through `cmd.exe` |
| `tools\runtime\recomp_read_sweep.py:37, 83-88` | Launches a private exe at `C:\Dev\_ref\...` and changes process priority through `ctypes` |
| `tools\gate\evict_file_cache.py` | Allocates 12 GiB by default to evict the file cache |
| `build.bat` | Legacy path: runs `cmake` to build `compress.exe`, calls `grit`, then `rmdir /S /Q build` |
| `format.cmd` | Runs `clang-format -i`, which rewrites every file under `src\` and `include\` in place |

Safe way to use any of it: do not run the build. To try `webfoot_lz.py`, copy only that file into a new, empty folder under our scratch tree, read it fully, keep its MPL-2.0 header, and call it from our own test with `py -3 -I -B`. Never run `compress.exe`, `gate.py`, `extract.cmd` or `rebuild.cmd`.

---

## Open points

- The two codec differences in section 2 need a check against the ARM routine at `@0x03000000`.
- The free-assembler route and the effort figures are estimates: no build was run (the brief limits this review to reading).
- The sample mapping has 25 rows, cut early by my scope change.
