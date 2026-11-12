# Bible rows from the dragonbyte-z review, tag DBZ

Merge with `merge_bible_rows.py`, passing this file, `DBZ`, and
`docs\tasks\2026-11-06-dragonbyte-review\catalogue.md`.

Only DIRECT facts, or facts I measured against our own ROM, are here. Everything SHARED ENGINE stays in the
catalogue until an address is re-derived.

## Section 2

| Fact | Tags | Label | Src |
|---|---|---|---|
| `github.com/siruiusamory-cmyk/dragonbyte-z` declares a ROM profile `legacy_of_goku_ii_usa_rev0_204142e1` that is OUR base ROM byte for byte: game code ALFE, 8,388,608 bytes, CRC32 `204142e1`, MD5 `4e1565aa1f0627c2bf5e51019440cb70`, SHA-1 `18e0715d...`, SHA-256 `6e6c370c...56ff75`. So every Legacy of Goku II measurement in that repository is a measurement of our exact file | #tool #decision | C (`config/roms.yaml:540-549`, SHA-1 equals the `global.md` pin) | DBZ |
| They declare a 384-byte free window at `rom:0x7FEA01` inside the canonical 8 MB (their LG2-068), audited and independently reviewed. Their own evidence says the size depends on a 1,024-byte clearance policy and falls to ZERO at a 1,216-byte margin, so it is a policy number, not a property of the ROM. We build at 16 MB and do not need it. Record it, do not spend it | #decision #open | L (their declaration read, not re-measured here) | DBZ |
| A 16 MiB Legacy of Goku II image boots to interactive gameplay and the CPU performs a data read at `0x08800000`, measured with a GDB `Z3` read watchpoint after relocating a 12-byte boot object from `0x081D4EE0` and rewriting its one literal at `0x08000204`. Independent corroboration of our 2026-10-16 expansion decision, by a different method | #decision #boot | C (their `LOGII_16MIB_RUNTIME.md`, runtime measured, two committed evidence files) | DBZ |

## Section 3

| Fact | Tags | Label | Src |
|---|---|---|---|
| The Webfoot packed-container grammar CLEARS the literal base when the stream returns to 8-bit literals, proven against the retail engine's own character memory. A stale base keeps token structure and tile geometry and shifts every palette index, so the symptom is correctly shaped tiles in the wrong colours. Our decoder already complies (`webfoot_decompress.py:142-144` sets `lit_base = 0` on every mode change) and our packer never emits 7-bit literal mode, so neither carries the defect | #codec #sprite #palette | C (their `WEBFOOT_LZ_LITERAL_BASE.md` for the rule; our two files read here) | DBZ |

## Section 8

| Fact | Tags | Label | Src |
|---|---|---|---|
| The 43-entry table `rom:0x6D68DC` is their "static43" script family, and its script pool is `rom:0x6D66C0`, 539 bytes. All 86 scripts reached from entry slots `+4` and `+8` decode cleanly with `scene_lib.op_end()` to the end op 17, and all 86 starts lie inside that pool. Their decoder and ours agree over their whole supported corpus, which validates our op-length table against work we did not do | #script #story #tool | C (measured, `scripts\one-time\2026-11-06-dragonbyte-review\varint_roundtrip.py`) | DBZ |
| `relocate(rom, rec, length, {})` returns the original bytes on all 86 static43 runs. Untouched ops are copied verbatim at `scene_lib.py:125` (`out += rom[s:_op_end(rom, s)]`), and `copy_and_redirect` preserves bytes on both arms at `scene_lib.py:636`. Neither writer path ever re-encodes an op, which is why the encoding traps below do not bite us | #script #tool | C (measured, same script) | DBZ |
| The script VM allows a negative zero and redundant `0x80` padding, and `scene_lib.zigzag()` can emit neither, so a decode then re-encode is lossy by construction. Measured in real data: across 7 scene tables, ALL 112 op-bearing type 0 records and the 962 varint operands a structural walk reaches, ZERO are non-canonical. A raw byte sweep of the script region produces false examples, because a varint reads at any byte: no aligned word in the ROM names `rom:0x3B0034`, `rom:0x3B0017` or `rom:0x3B0106`, and the byte at `rom:0x3B0034` is `0x01`, the op 1 OPCODE byte | #script #codec #open | C for the 962 operands (measured, `scene_varint_sweep.py`), L for "the three sites are artifacts" (`verify_direct.py`; those 7 tables could not reach that span by walking) | DBZ |
| `push()` picks the opcode from the value, so it is NOT the inverse of a decode: `push(0)` is `0000` (op 0), `push(255)` is `00ff` (op 0), `push(256)` is `1d018400` (op 29 list) and `push(-1)` is `1d0103`. A decoded op 1 or a one-value op 29 comes back as op 0, changing the length and the opcode. This fails closed: `relocate()` compares the caller's `old` hex against the ROM and raises before any write | #script #tool | C (measured, `varint_roundtrip.py` section E) | DBZ |
| The UI string pool is `rom:0x0E2C50`, 5,184 bytes, holding 246 distinct NUL-terminated ASCII strings that tile it exhaustively with no gap or overlap. The 260-entry table at `rom:0x0E2840` ALIASES: 9 targets are shared by 14 extra slots, so its pointers are neither unique nor ascending and no entry has per-entry ownership. That is why the table cannot be relocated | #text #menu #item | C (their `config/roms.yaml` text_strings evidence and `LOGII_TEXT_FORMAT.md`, 22 tests on our exact ROM) | DBZ |
| The enemy table `rom:0x6D56AC` holds exactly 109 records, bounded by usage rather than a terminator: the 128-entry scouter directory `rom:0x6F8E40` (stride 0x14) indexes it through its `+0x10` word, and the maximum index across all 128 entries is 108. The table base has exactly three references image-wide, at `@0x0800E79C`, `@0x08017A38` and `@0x0801912C` | #combat #object #menu | C (their `config/roms.yaml` enemy_stats evidence, instruction-cited) | DBZ |

## Section 10a

| Fact | Tags | Label | Src |
|---|---|---|---|
| `github.com/siruiusamory-cmyk/dragonbyte-z` (MPL-2.0, HEAD `5e8c3b9`, cloned 2026-11-06): a Buu's Fury editor SDK with deep research on BOTH games, 286 documents, 110 mGBA Lua scripts, 387 test files. The author is **Cale** (`siruiusamory@gmail.com`), the same address that authors all 50 commits of our `legacyofgoku2-disasm`, so we already depend on this person. Full catalogue: `docs\tasks\2026-11-06-dragonbyte-review\catalogue.md` | #community #tool | C | DBZ |
| In that repository `LOGX_*` means LOGExtractor-derived, NOT "Legacy of Goku generally". All 24 `LOGX_*.md` are measured on the Buu's Fury image `940AD5F0`, and a grep for `ALFE`, `LOGII` or "Legacy of Goku II" across all 24 returned nothing. So LOGX research is SHARED ENGINE and every address in it must be re-derived for our ROM | #community #tool game:bf | C (four search shapes) | DBZ |
| Their Buu's Fury static map collision work is BLOCKED at the evidence gate with no codec written, and they refuted their own candidate `0x08046AA4` by disassembling it to a row of `bx` trampolines. Our Legacy of Goku II collision format is confirmed from `collision_test @0x08005D6C` with stride and bit order pinned, so this is the strongest thing we can offer back | #community #map game:bf | C (their `COLLISION_FORMAT.md`) | DBZ |
| `github.com/mstan/DragonBallZLegacyofGokuIIRecomp` at `add98b5d76fb2b822be870f29fa27b22c9a95631` is a RECOMPILATION project for our exact ROM, cited by their `config/roms.yaml` as independent hash corroboration. A search of this bible for `mstan` returned nothing, so it is a lead we have not examined | #community #tool #open | L (cited, not yet opened) | DBZ |
| Evidence against our 2026-09 community row that Legacy of Goku II and Buu's Fury "do NOT share one engine": the two script VMs have DIFFERENT addresses and the SAME grammar. Buu's interpreter is `0x08004038` with primary dispatch table `0x080554C0`, 31 slots `0x00..0x1E`, slot `0x11` NULL meaning terminate; ours is `@0x080092E4` with table `rom:0x3B5C00`, slots 0 to 29, null at slot 17. Add the shared Webfoot container codec. Formats are shared, addresses are not, so soften the claim rather than call it refuted | #community #decision | L (grammar-level agreement from their two documents; no instruction compared across both ROMs here) | DBZ |

## Section 13

| Fact | Tags | Label | Src |
|---|---|---|---|
| A per-actor palette may be reachable WITHOUT touching the shared OBJ palette: colour depth is per sprite (OAM `attr0` bit 13) and the palette bank is `attr2` bits 12-15, so a 4bpp OBJ would get its own 16-colour bank. The precondition is already confirmed on our ROM: `@0x08007784` copies the frame record's `+4` word (attr0, attr1) into OAM verbatim (bible row 119), so an actor's own record decides bit 13. Their mechanism addresses (`0x0800F254`, `0x0800F2A0`) are BUU's, not ours, so both sites must be re-derived around `@0x08007784`. This cuts across the standing rule that the OBJ palette at `rom:0x1DA6C8` is not changed, so it needs an owner ruling before any work | #palette #sprite #open #decision | L (their `CELL_PALETTE_ROUTE_C.md`, Buu addresses; the OAM precondition is C on our ROM from bible row 119) | DBZ |

## Section 11

| Fact | Tags | Label | Src |
|---|---|---|---|
| Stock mGBA 0.10.5 Qt (the owner's build) has NO Lua startup switch, so an observer must be loaded through the Scripting window; it DOES accept a savestate startup switch. `emu:setBreakpoint` and `emu:readRegister` are 0.11-dev only, and under a GDB launcher a Lua `frame` callback recorded ZERO ticks, so GDB and Lua do not combine in one run | #tool #debug | C (their `consumer-analysis.md:580` and `docs/skills/mgba-runtime.md` sections 1 and 2) | DBZ |
| Proven on stock mGBA 0.10.5: `emu:setKeys`/`addKey`/`clearKey`, the `frame` callback as a clock, `emu:screenshot`, `emu:reset` and `emu:saveStateFile`. So a Lua script CAN produce a save state on the owner's build with nobody holding the pad. `rom006_bootstrap.lua` is the 57-line pattern: assert game code and ROM size, reset, pulse A on named frames, screenshot, `saveStateFile`, remove the callback, stop. NOT proven on 0.10.5: `emu:loadStateFile`, whose single Lua caller wraps it in `pcall` | #tool #input | C for the API (their allowlist note and script), but the save-state call is proven on Buu's Fury only, not yet on our ROM | DBZ |
| Input from Lua was confirmed reaching the console ON OUR ROM by reading `KEYINPUT` `@0x04000130`: `0x037F` LEFT, `0x03DF` UP, `0x03EF` RIGHT, `0x03BF` DOWN. Writes to `KEYINPUT` are NOT evidence: it is read-only hardware reloaded from the pad every frame, so a debugger poke proves nothing about input | #tool #input | C (their `LOGII_16MIB_RUNTIME.md`, measured on a 16 MiB derivative of our image) | DBZ |
| Rule for any silent probe, learned twice in their project: give every observer a LIVENESS channel, a second breakpoint on something known to fire in the same run. Target silent plus liveness silent proves NOTHING; target silent plus liveness firing is a real negative. A construction-time breakpoint is silent by construction in a run that loads a savestate, so it is not a liveness channel there | #tool #debug | C (their `docs/skills/mgba-runtime.md` section 8, two invalidated tickets) | DBZ |
| Search-shape trap proven on this engine: a map root's door-list reader loads its count and pointer with `ldm r1, {r1, r2}` after `adds r1, #0x40`, so a constant-immediate scan for `ldr ..., #0x40` finds only unrelated sites and misses the consumer. When hunting the Legacy of Goku II equivalent of the `+0x40`/`+0x44` door list, search for an `ldm` on a map root, never for the displacement | #map #tool #open | C (their `LOGX_CONNECTOR_PROVENANCE.md` sections 3.4 and 3.5, Buu addresses) | DBZ |
