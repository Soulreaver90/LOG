# Disassembly study: report (2026-10-18)

This report answers my ask "Work on disassembly ... that will make modding easier" (brief `disasm-study.md`). Read only: no ROM was built, nothing was installed, nothing under `data\` or `scripts\permanent\` changed.

Labels: **C** = CONFIRMED (bytes, a listing, or a count from a tool you can re-run), **L** = LIKELY, **S** = SPECULATIVE.

---

## 0. Recommendation

Use route D: route C now, route B next (no install), route A only as a "patch toolchain" later.

| Step | Effort | What it is | What it unlocks for the mod |
|---|---|---|---|
| 1. Route C tools (built, section 5) | S (done) | Whole-ROM code map, symbol file, annotated listing, reference finder | Every raw address in a patch gets a name and a bible row; "who reads this table" is one command |
| 2. Adopt `symbols.py` in patches | S | Final decisions: move `symbols.py` to `scripts\permanent\`, patches import names | No more hand-listed literal sets (for example the 17 `TABLE_LITERALS`): `listing.py --refs` computes them |
| 3. Name the cheap mass | S | Name the 145 ext ops, 30 base ops, 48 states and the vtable classes from the existing scratch listings | Story scenes: every script verb has a function name in the listings |
| 4. Route B: Ghidra project with our map | S-M | Already installed; a script applies `symbols.json` and the codemap starts, then the decompiler works by name | New fights (enemy AI `0x0801AB2A`, knockback), faster research for every slice |
| 5. Route A-lite: patch toolchain | M (needs an install) | GNU `as` + `ld` (and `gcc`) build new code at expansion addresses against `symbols.json` | No hand assembler, no hand long-call stubs, new systems in C (Buu's Fury equipment, shops) |
| 6. Route A full: re-assemblable disassembly | L-XL | Code region as assembly, data as binary, byte-identical SHA-1 | Only when a slice must grow or move many base tables or functions; not needed for the next slices |

> [!IMPORTANT]
> **Correction to the brief: Ghidra is already installed.** Ghidra 12.1.4 is at `%USERPROFILE%\Tools\ghidra_12.1.4_PUBLIC`, and earlier sessions used it (`scratch\ghidra\LoG2.gpr`, `scripts\one-time\2026-10-16-task-5-gi-art\gh.sh`). Java 21 is present. Route B needs no install. The existing project was never auto-analyzed (67 functions in it), so this study ran a fresh analysis in its own folder (section 6). Label C.

---

## 1. What a disassembly would give us (question 1)

Today every patch works on raw bytes. A disassembly turns those bytes into names, references and relocatable code.

**Pains today, with evidence.**

| Pain | Evidence | Removed by |
|---|---|---|
| Hand-listed literal sets: a table move must repoint every pool word that holds its address | `ssj2_form.TABLE_LITERALS` (17 words); bible s5b "a later patch that repoints table literals must repoint rom:0x86FCD0 too"; portrait block literal `rom:0xBE10` plus the hook pool word (s5a, s8) | C (`listing.py --refs` lists them), A (symbols) |
| Stale offsets after records move | Bible s8 tool traps: scene-table words moved by `npc_gi`; `alloc.notes["gohan_portraits"]["block"]` stale after `npc_gi` | C partly (refs query), A fully (labels) |
| Hand-assembled Thumb with an in-house assembler | `ssj2_form.assemble`, used by `status_bonus` and `ssj2_idle`; tests decode it with `thumb_dis.py` | A-lite (GNU as), B (decompiler to read) |
| BL cannot reach the expansion area: 16-byte long-call stubs by hand | Bible s5b long-call stub row; `status_bonus` copies the whole status page (0x3A8 bytes) and rewrites 18 BL sites | A-lite (the linker makes the veneers) |
| Base tables cannot grow in place | Set table literal `0x0800959C` (s4), portrait block (s5a), appearance table has no free entry (s6), state slots `0x083B5268` + 0x10 (OVW) | A full (move and relink), C (find every user first) |
| About 220 raw hex constants across 9 patch files | Count of distinct hex constants per file in `scripts\permanent\patches\` (ssj2_form 85, npc_gi 37, status_bonus 29) | C (names), A-lite (link by name) |
| Pools are shared between neighbour functions | `get_set` `0x08009324` reads its 3 literals at `0x08009594`-`0x0800959F`, 0x224 bytes after its last instruction (listing in `proofs.txt`) | A full (labels move with code); today: never move a function without its pool. C |

**The real cost is data pointers, not code.** `ptrscan.py` counts aligned words that hold a ROM address (one shape, a floor for unaligned script pointers):

| Where the word sits | Points to code | Points to data |
|---|---|---|
| Code region (rom:0x0-0x28723) | 724 | 636 (1,350 of all 1,360 are pool words code loads) |
| Data region | 10,973 (10,024 exact Thumb function pointers: map factories, script op tables, item handlers) | 54,744 (densest: rom:0x3F0000, 0x400000 maps and scripts; 0x6D0000) |

A shiftable rebuild must turn all of these into symbols. The script VM bytecode is a second "code" layer on top, with unaligned pointers this count does not see. Label C (counts), L (that the unaligned ones exist: the bible's scene and record pointers are often odd addresses).

---

## 2. Routes (question 2)

| Route | Tools | Effort | Risk | Install |
|---|---|---|---|---|
| **A. Re-assemblable disassembly, byte-identical** | GNU `as`, `ld`, `objcopy`; an emitter from our code map | L for the code region with data kept as binary; XL to make data shiftable (65,000+ pointer words, script bytecode) | GNU as picks its own encoding for some forms (`add rd,rs,#0` against `mov`, literal pool placement): the emitter must write `.hword` / `.word` for any instruction that does not round-trip. A constant mistaken for an address breaks a shifted build silently. Pass or fail is the SHA-1 `18e0715d...` | Yes (list below) |
| **A, matching C (pret style)** | The original compiler | Not realistic | The game was built with ARM's own compiler (section 3.3), which is proprietary; GCC (agbcc) output will not match | n/a |
| **A-lite. Patch toolchain** | `as`, `ld` (optionally `gcc`) linking new code at expansion addresses against `symbols.json` | M | Low: base ROM stays bytes; new code only. Plain C functions use the same r0-r3 calling convention (L); C++ objects with base-relative vtables need hand care | Yes (same list) |
| **B. Ghidra with our symbols** | Ghidra 12.1.4 (installed), Java 21 (installed) | S-M | Out of the box Ghidra also decodes sprite data as code (section 6); seed it with our map instead | None |
| **C. Our Python tools, no installs** | `scripts\one-time\2026-10-18-disasm-study\*.py` | S (built) | Heuristic starts (stages 2-4) are LIKELY; 99.5 % of starts agree between two independent runs | None |
| **D. Mix** | C now, B next, A-lite when a slice needs new systems | S + S-M + M | Lowest | Only for A-lite |

**Install list for route A and A-lite (I approve or not).** Nothing below is installed.

| Item | Why | Notes |
|---|---|---|
| Arm GNU Toolchain for Windows, `arm-none-eabi` (zip, a current release, pinned) | `as`, `ld`, `objcopy`, `gcc` for ARMv4T Thumb | No admin rights needed for the zip. One item covers A and A-lite |
| or devkitARM (devkitPro installer) | Same tools plus `make` and libgba | Heavier; brings its own MSYS2 |
| `make` | Only for a Makefile build | Optional: `log2_build.py` can call `as` and `ld` from Python, as it calls patches today |

**Install list for route B: none.** Ghidra 12.1.4 and Java 21 are present (C).

---

## 3. Size of the job (question 3)

### 3.1 Code against data (USA)

| Measure | Value | Label |
|---|---|---|
| Code region | rom:0x0-0x28723, 165,668 bytes = 1.97 % of the ROM. The menu font `0x08028724` is the first data after it | C |
| IWRAM block | rom:0x7FD6BC, 0xE7C bytes, copied to `0x03000000` by crt0; 2,268 bytes decode as ARM code (10 functions: decompressor, bit reader, unpack helpers, IRQ handler) | C |
| Data | 8,219,232 bytes = 97.98 % of the ROM | C |
| Functions | 2,264 (2,234 Thumb, 30 ARM); a heuristics-only run finds 2,269; 2,252 are in both (99.5 %) | C (count), L (starts from stages 2-4) |
| Code region classified | 99.40 % (Thumb 84.66 %, vtables 6.22 %, pools 5.69 %, ARM 1.82 %, strings 0.36 %); 999 bytes left, mostly 24-byte secondary vtables | C |
| Missed code check | 0 BL-shaped pairs to a known start inside unclassified bytes | C |
| Boundary noise | 153 instructions sit in two bodies (shared tails) | C |

### 3.2 How much the bible already names

| Bible code-region addresses (USA rows) | Count |
|---|---|
| Function starts | 208 |
| Function pointers (start + 1) | 16 |
| Sites inside a function (named in listings as comments) | 79 |
| Vtables and the constructor list | 31 |
| Literal-pool words | 18 |
| IWRAM data | 3 |
| Unclassified | 0 |

The table counts the bible before this study (355 addresses). With the `DIS` rows added, `symbols.py check` reads 370 addresses: 212 starts, 16 pointers, 82 inside, 34 vtables or constructor lists, 20 pool words, 3 IWRAM data, 3 strings, 0 unclassified. Label C.

`symbols.py` names 226 functions (all 226 are codemap starts in both runs), 39 tables, 27 vtables and 23 RAM globals: 315 symbols. That is 10.0 % of the 2,264 functions. Label C.

### 3.3 How the game was compiled

`fingerprint.py` counts each shape in the code region.

| Shape | USA | Europe | Buu's Fury | Points to |
|---|---|---|---|---|
| Base-relative vtables (entry = base + word) | 336 (2,509 entries) | 331 | 685 (5,125) | not GCC's absolute vtables |
| Self-relative constructor vector (`ldr ; add rX,pc`) | 66 (+ a 3-entry list `0x08023690`) | 66 + 3 | 136 + 7 | ARM's position-independent C++ init |
| Starts with loads before the push | 198 (122 with one load) | 186 | 371 | armcc scheduling |
| `add pc` byte switch tables | 3 | 4 | 21 | armcc (GCC uses word tables) |
| GCC word switch `ldr r0,[r0] ; mov pc,r0` | 0 | 0 | 0 | |
| ARM divide `rsbs r12,r0,r1,lsr #3` | 4 | 4 | 4 | ARM C library |
| Divide by zero `mov r0,#2 ; mov r1,#2 ; b` | 1 | 1 | 1 | ARM C library signal numbers (SIGFPE 2) |
| `pop {r3} ; bx r3` returns | 12 | 12 | 117 | more interworking in Buu's Fury |
| `bx pc ; nop` veneers | 7 | 7 | 15 | armlink-style interworking veneers |
| "GCC" strings in the code region | 0 | 0 | 0 | the hits at rom:0xD5B02 and 0xEA93C are sample data |

Conclusion: ARM's own toolchain (the ADS / SDT family), C++ in Thumb, with a small ARM library (divide) and ARM IWRAM routines. Label L (shapes C, compiler name L).

Assert strings name the source files: `K:\Source\CharacterData.cpp`, `K:\Source\ByteCodeInterpreter\ByteCodeFunctionList.cpp`, `...\ByteCodeVariableList.cpp`, `K:\Source\AreaEntry.cpp` (C).

**Library code.** The EEPROM library (`0x080218E0`-`0x08021CEA`, its own `pop {r0|r1} ; bx` returns), the `call_via_r0`-`r7` table `0x08021D28`, the constructor runner `0x08021D74`, the ARM divide routines `0x08021F34` onward, 7 `bx pc ; nop ; ldr pc,[pc,#-4]` veneers `0x080236A8`-`0x080236FB`. The sound driver is a custom mixer (bible s14), compiled with the game. Label C (addresses), L (the library split).

### 3.4 Is a byte-identical rebuild realistic?

| Kind | Realistic? | Why |
|---|---|---|
| Assembly-level, data as binary, nothing moved | Yes (L, the usual result for GNU as with `.hword` fallbacks) | 165 KB of code, every byte classified |
| Assembly-level, code shiftable | Yes with work (L) | 1,350 pool words, 2,509 vtable words (relative: `.word fn - vt`), 10,024 data words that hold function pointers must become symbols |
| Data shiftable (move maps, scripts, sprites) | Large (XL) | 54,744 data-to-data pointer words plus unaligned script pointers |
| Matching C | No | Proprietary compiler (3.3) |

---

## 4. Buu's Fury (question 4)

Same engine family and toolchain; about a quarter of the LoG II code is shared byte for byte. The same tools run on it unchanged (read only).

| Fact | Value | Label |
|---|---|---|
| crt0 words at rom:0x140 | Same layout: IWRAM copy `0x087B79A4` to `0x03000000`, 0x1004 bytes; main `0x0800419D` | C |
| Code region | rom:0x0-0x54FBB, 348,092 bytes (2.1 times LoG II); 4,399 functions (58 ARM); 98.59 % classified; 31 BL-shaped pairs left in gaps, 3 unresolved switches | C |
| Toolchain shapes | Same base-relative vtables, same constructor vector, same ARM divide and div0 (table 3.3); more interworking returns and ARM code | C (shapes), L (same compiler) |
| Shared code (`match.py`, offsets masked) | 25.3 % of USA Thumb functions with 8 or more instructions match a Buu's Fury body (37 % of short, 8 % of long ones); Europe matches 88.9 % | C |
| What matches | The object and world system, scene manager, region and warp items, frame unpack, sound start and music play, EEPROM read and write, IRQ init, constructor runner (37 of the 226 named functions) | C |
| What differs | Script VM, menus, player, forms, status page | C (no match), L (rewritten, not just moved) |
| Source files | Same tree on another drive: `T:\Source\AreaEntry.cpp`, `CharacterData.cpp`, `ByteCodeInterpreter\ByteCodeInterpreter.cpp`, `GameData.cpp` | C |
| Pointer surface | 16,975 data-to-code words (15,298 function pointers), 75,265 data-to-data | C |

This agrees with the community note in the bible (s10a): siblings, not one engine. For the merge, `match.py --names` carries 37 LoG II names to Buu's Fury addresses today.

---

## 5. Route C tools, built and proven (question 5)

All files are in `scripts\one-time\2026-10-18-disasm-study\`. Python, LF, no byte order mark, read only.

| File | What it does |
|---|---|
| `codemap.py [--game usa\|eu\|bf] [--no-symbols]` | Whole-ROM code map: `functions.csv`, `coverage.txt`, `codemap.json` (USA here, `eu\` and `bf\` for the others) |
| `symbols.py [list\|check\|json]` | 315 names with their bible row tag; `check` classifies every bible address against the map; `addr("get_set")`, `S.get_set`, `rom("set_table")` for patches |
| `symbols.json` | The same names for Ghidra or other tools |
| `listing.py <addr\|name> [--refs]` | Annotated listing: names for calls, literals (functions, tables, RAM with offset, strings), virtual calls, bible rows on the line they name; `--refs` lists every word that holds an address and the `ldr` sites that load it |
| `ptrscan.py`, `fingerprint.py`, `match.py`, `codemap_vs_ghidra.py` | Pointer surface, compiler shapes, cross-ROM function match, Ghidra comparison |
| `ghidra\FuncList.java`, `ghidra\SeedEntry.java` | Read-only Ghidra export and the two-seed pre-script |
| `proofs.txt` | The five listings below plus the appearance-table refs |

**How `codemap.py` finds functions.** Stage 1 (confident): the header branch, `main`, the IRQ vector store, recursive descent with BL closure, tracked `ldr` values for `bx` and `call_via`, `add pc` switch tables, literal-pool function pointers, the self-relative constructor list, the bible pointer tables. Stage 2: base-relative vtables (an even literal; each entry must decode clean and look like a start). Stage 3: aligned ROM words that point into the code range. Stage 4: prologue search in what is left. Each stage runs to a fixed point before the next.

**Proof: five bible functions, names line up** (full listings in `proofs.txt`).

| Function | Bible fact | Listing shows | Label |
|---|---|---|---|
| `get_set` `0x08009324` | `cmp r0,#0`, `cmp r0,#7`; set table literal `0x0800959C` = `0x083B4E90` (s4) | `cmp r0,#0x0` at `0x08009328`, `cmp r0,#0x7` at `0x0800934C`, `.word 0x083b4e90 ; set_table` at `0x0800959C`; calls `appearance_set`; 17 BL sites | C |
| `idle_tick` `0x08007570` | Bytes `48 8A 01 30 48 82 00 06` (`ssj2_idle._expect`); vtable +4 of states 0, 22, 38 (s4) | Same bytes; "vtable slots (3): vt_state38+0x4, vt_state22+0x4, vt_state0_idle+0x4" | C |
| `portrait` `0x0800BDCC` | `cmp r0,#7 ; bgt` at `0x0800BDF0`; literal `rom:0xBE10` = `0x083EC9D0` (s5a) | `bgt 0x800be06` at `0x0800BDF0`, `.word 0x083ec9d0 ; portrait_block` at `0x0800BE10`; callers include `status_page`, `dialog_box`, `appearance_portrait` | C |
| `damage` `0x0800F910` | `0x80 - END` at `0x0800F94E`; multiply at `0x0800F974`; f(S) constants 26, -701, 115618 (s14) | `sub r0,r1,r0` with r1 = 0x80 at `0x0800F94E`; `mul r0,r5` at `0x0800F974`; literals `0xfffffd43` (-701), `0x0001c3a2` (115618), `mov r0,#0x1a` (26); calls `rand16`, `rand_n` | C |
| `status_page` `0x0800379C` | Code 0x362 bytes (`status_bonus.CODE_LEN`), +3 portrait literal `rom:0x3B30` (s5a) | Extent 0x362; `ldr r1,=0x081d967c ; appearance_table` at `0x08003A82`; bible rows on `0x0800391A` and `0x08003A8C` | C |

**Proof: the reference finder reproduces a hand list.** `listing.py appearance_table --refs` returns 18 pool words: the 17 in `ssj2_form.TABLE_LITERALS` plus `rom:0x42F0` (the reverse lookup copy `gohan_gi` keeps), each with its named `ldr` users, and 0 words outside the code region. Label C.

**Caller counts match the bible.** `frame_unpack` 72 BL sites (bible 72), `veneer_decompress` 14 (bible 14). `world_add` has 133 sites in code; the bible's 134 includes one BL-shaped pair in data at `0x081114C6` (correction row added). Label C.

---

## 6. Ghidra cross-check

Ghidra 12.1.4 auto-analysis ran headless on a new project (`scratch\ghidra\LoG2auto`, LoG2auto), with the same two seeds codemap uses (`SeedEntry.java`) and the export script `FuncList.java`. `codemap_vs_ghidra.py` compares the two lists.

| Result | Count | Label |
|---|---|---|
| Analysis finished | No: it timed out at 2,700 s; the export ran on the partial result; 532 ERROR lines in `headless.log` | C |
| Ghidra functions | 3,202 (3,032 Thumb, 170 ARM) | C |
| In the code region rom:0x0-0x28723 | 849 | C |
| Outside the code region (data decoded as code, mostly sprite data rom:0x280000-0x7E0000) | 2,353 | C |
| Same start in both | 780 of codemap's 2,254 code-region functions (34.6 %) | C |
| codemap only | 1,474. By codemap stage: vtable 803 of 1,012; data tables 145 of 183; ROM words 138 of 184; prologue scan 114 of 139; constructor list 68 of 68; bible symbols 97 of 210; BL closure 88 of 426; other 21 | C |
| Ghidra only, within 8 bytes of a codemap start | 34 | C |
| Ghidra only, inside a codemap body | 33 | C |
| Ghidra only, elsewhere in the code region | 2: `0x080239B4` and `0x08024816`, both words inside base-relative vtables (`0x08023990`, `0x08024810`) | C |

**What this means.** In a 2,700 s run, Ghidra placed 780 of 2,254 codemap starts, and 73 % of the functions it made were data. 1,268 of the 1,474 misses are starts that only pointer data reaches (vtables, tables, ROM words, the constructor list) or the prologue scan; Ghidra finds those slowly or not at all. 88 misses are BL-reachable, which a finished run would likely find; 97 are bible symbols and 21 are literal or tail starts. So the miss pattern is LIKELY a method limit, not only the timeout; a finished run was not tested. Ghidra is still the right viewer and decompiler (route B), but only after a script imports `codemap.json` and `symbols.json`, disables the aggressive instruction finder, and clears everything outside the code region. Label L.

---

## 7. Bible rows added

Source tag `DIS` = this report. Rows are in RE-BIBLE sections 11 and 14 (search `| DIS |`).

| Section | Row (short) | Label |
|---|---|---|
| 11 | Ghidra 12.1.4 is installed; the old project was never analyzed; the auto-analysis numbers of section 6 | C |
| 11 | The route C tools in `scripts\one-time\2026-10-18-disasm-study\` | C |
| 14 | Code map: code region rom:0x0-0x28723, IWRAM block, 2,264 functions, 99.40 % classified | C (map), L (heuristic starts) |
| 14 | Compiler: ARM's own toolchain, not GCC, with the shape counts | C (shapes), L (name) |
| 14 | `call_via_r0`-`r7` table and the base-relative virtual call shape | C |
| 14 | Literal pools are shared by neighbour functions (`get_set` example) | C |
| 14 | Source file names from the assert strings | C |
| 14 | Correction: `world_add` 133 BL sites in code (the 134th is data at `0x081114C6`) | C |
| 14 | Appearance table: 18 pool words, all known to `ssj2_form` plus `rom:0x42F0` | C |
| 14 | Pointer surface counts | C (counts), L (floor) |
| 14 | Buu's Fury code map and toolchain shapes (`game:bf`) | C, L (same compiler) |
| 14 | Buu's Fury shared code: 25.3 % of USA functions match (`game:bf`) | C |

---

## 8. Concerns and limits

- **Starts from stages 2-4 are heuristics (L).** Two runs (with and without the bible seeds) agree on 2,252 starts; 12 and 17 differ, mostly off-by-4 pairs and splits near the script VM handlers `0x08009xxx`. The bible-seeded run is the one to use.
- **The code-region boundary is a measurement.** Nothing reached from code lies past `0x08028723`; code reached only from data the scans miss (a computed pointer) would not appear. Shapes used: BL closure, literals, vtables, ROM words, prologue search.
- **Secondary vtables** (`vt + 0x6C`, for example `0x08024938`, made by `add r0,#0x6c`) are not read; they are most of the 999 unclassified bytes.
- **Pointer counts are one shape** (aligned words). Unaligned script pointers are not counted; a data word that happens to look like an address is.
- **My new analysis wrote only to `scratch\ghidra\LoG2auto\`.** My export from the old project `scratch\ghidra\LoG2.gpr` used `-process -noanalysis -readOnly` (11:23 PM). The old project's index files then changed at 11:31 PM and 11:44 PM on 2026-10-18. Other tasks ran `gh.sh` on that project in the same window, which may explain it. Label LIKELY: I did not prove which run wrote them.
- `scripts\permanent\` is unchanged. Adopting `symbols.py` there is my decision (step 2).
