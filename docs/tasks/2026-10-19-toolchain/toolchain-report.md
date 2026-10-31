# ARM toolchain and assembler proof: report (2026-10-19)

This report answers the brief `toolchain.md` (approved 2026-10-19 8:40 AM).

Labels: **CONFIRMED** (bytes, a hash or a tool run you can repeat), **LIKELY**, **SPECULATIVE**.

---

## 1. Install (task 1)

The toolchain is installed in user scope. No admin rights, PATH change or registry change.

| Item | Value | Label |
|---|---|---|
| Version | Arm GNU Toolchain **15.2.Rel1** (Build arm-15.86), host `mingw-w64-x86_64`, target `arm-none-eabi` | CONFIRMED |
| Requested URL | `https://developer.arm.com/-/media/Files/downloads/gnu/15.2.rel1/binrel/arm-gnu-toolchain-15.2.rel1-mingw-w64-x86_64-arm-none-eabi.zip` | CONFIRMED |
| Served from | 302 redirect to `https://armkeil.blob.core.windows.net/developer/files/downloads/gnu/15.2.rel1/binrel/arm-gnu-toolchain-15.2.rel1-mingw-w64-x86_64-arm-none-eabi.zip` (Arm's download store) | CONFIRMED |
| Size, date | 295,922,350 bytes, Last-Modified 2025-12-15 | CONFIRMED |
| Checksum file | The same URL plus `.sha256asc` (same redirect) | CONFIRMED |
| SHA-256 | `7936cac895611023ffb22a64b8e426098c7104cb689778c1894572ca840b9ece`. Python `hashlib` and `certutil` both **match** the `.sha256asc` value | CONFIRMED |
| Download folder | `%USERPROFILE%\Tools\downloads\arm-gnu\` (new and empty before): the zip and the `.sha256asc` | CONFIRMED |
| Install folder | `%USERPROFILE%\Tools\arm-gnu-toolchain-15.2.rel1\`. The zip has no top folder, so `bin\` is directly under it. 7,320 files in the zip, 7,320 extracted, path-traversal check on every entry | CONFIRMED |

**Tool versions** (each run by absolute path from `...\arm-gnu-toolchain-15.2.rel1\bin\`):

```
GNU assembler (Arm GNU Toolchain 15.2.Rel1 (Build arm-15.86)) 2.45.1.20251203
GNU ld (Arm GNU Toolchain 15.2.Rel1 (Build arm-15.86)) 2.45.1.20251203
GNU objcopy (Arm GNU Toolchain 15.2.Rel1 (Build arm-15.86)) 2.45.1.20251203
GNU nm (Arm GNU Toolchain 15.2.Rel1 (Build arm-15.86)) 2.45.1.20251203
```

**How the version was chosen.**

- The HTML downloads page `developer.arm.com/downloads/-/arm-gnu-toolchain-downloads` now returns a 301 to `gitlab.arm.com/tooling/gnu-toolchains-for-arm`. That host sits behind a WAF challenge, and plain curl gets "Access Denied" from the old page. So the checksum came from the sibling `.sha256asc` file on the media path, not from the HTML page. CONFIRMED.
- A probe of the developer.arm.com media path: `15.2.rel1` and `14.3.rel1` exist (302). `15.3.rel1` and `16.1.rel1` return 404. So 15.2.rel1 is the newest release on developer.arm.com. CONFIRMED.
- A newer 15.3.rel1 may exist on gitlab.arm.com. The only evidence is an AUR package title. The brief allows developer.arm.com only, so I did not use it. SPECULATIVE.

---

## 2. Byte compare (task 2)

GNU as reproduces the hook **byte for byte**, literal pool and pad included. CONFIRMED.

| Item | Value |
|---|---|
| Source | `scripts\one-time\2026-10-19-toolchain\ssj2_idle\ssj2_idle.s` (the patch `CODE`, with comments changed from `;` to `@`) |
| Flags | `as -mcpu=arm7tdmi -mthumb`. The source has `.syntax divided` and `.thumb` |
| Symbols | `SET_SSJ2=0x08869C7C`, `SET_RAGE=0x0888D870`, `VANILLA=0x08007571`, `ANIM0_ROW=0x4C` (from the r19 pool words) |
| Load address | `0x08894E24`. The vtable `0x08025A84` +4 word gives `0x08894E25` in r18, r19 and r20 |
| Size | 0x50 bytes: 31 instructions (0x3E), pad `0000`, 4 pool words |
| Labels (`nm`) | `idle` 0x08894E24, `idle_vanilla` 0x08894E32, `idle_ours` 0x08894E36, `idle_store` 0x08894E5E. The same as `ssj2_form.assemble` |

| Compare | Result |
|---|---|
| GNU bytes against rom:0x894E24 of `log2_poc_r18.gba` | match, 0x50 bytes |
| GNU bytes against rom:0x894E24 of `log2_poc_r19.gba` | match, 0x50 bytes |
| GNU bytes against `ssj2_form.assemble(ssj2_idle.CODE, 0x08894E24, syms)` (the bytes `ssj2_idle.py` writes) | match, 0x50 bytes |
| r20 (`log2_poc_r20.gba`, built by the other task) hook bytes | the same 0x50 bytes (read only) |

Bytes: `8a6c0f4b9a4204d00e4b9a4201d00e4a10474c32cb6c9a42f9d1488a013048820204d20c094b53431b0cd21ad21ad21a0006000ef12800db03328a82704700007c9c860870d888087175000856550000`

**No differences to explain.** These points could have broken the match. Each one was checked:

- Comment character: in ARM gas, `;` separates statements. The `.s` file uses `@`.
- Encoding choice: divided syntax and `-mcpu=arm7tdmi` give one 16-bit encoding per line. `add r2,#0x4c` is `324c`, and `ldr r3,=0x5556` is a pool load, not `movw`.
- Pool order and dedupe: gas puts the pool words in order of first use, as the in-house assembler does.
- Pad before the pool: gas `.ltorg` pads with `0000`. A test copy without `.balign` gave the same bytes (`out\nobalign.*`). The source keeps `.balign 4, 0`, so the pad does not depend on that default.
- The brief says r18 and the caller said r19. The hook bytes are the same in both, so the report gives both compares.

Work files: `scripts\one-time\2026-10-19-toolchain\ssj2_idle\out\` (the `.o`, `.elf` and `.bin` of the manual run, `reloc.o` of section 4).

---

## 3. Helper: `build_stub.py`

`scripts\one-time\2026-10-19-toolchain\build_stub.py` assembles a `.s` file at a load address. CONFIRMED (tests pass).

| Part | What it does |
|---|---|
| API | `build(src, load_addr, defsyms=None) -> (bytes, {label: address})`. The same return shape as `ssj2_form.assemble` |
| CLI | `py -3 -I scripts\one-time\2026-10-19-toolchain\build_stub.py <file.s> <addr> [NAME=VALUE ...]` |
| Config | `TOOLCHAIN_BIN` at the top: an absolute path, no PATH lookup |
| Steps | `as --defsym` for each symbol, `ld` with a generated script (`.text` at the address), `objcopy -O binary -j .text`, `nm` for the labels |
| Guards | `ld --orphan-handling=error`. An `ASSERT` fails the link when the stub has `.data`, `.rodata` or `.bss` (tested). A start that ld moved for alignment is an error. The `objcopy` size must equal the `.text` size. Any stderr from a tool is an error |

Test: `scripts\one-time\2026-10-19-toolchain\test_build_stub.py` (3 tests, OK). It compares the GNU bytes with `ssj2_form.assemble` (bytes and labels) and with r18 and r19 at rom:0x894E24. It checks that a 2-aligned load address is refused. It skips when the toolchain is absent.

Run: `py -3 -I -B -m unittest discover -s scripts\one-time\2026-10-19-toolchain -p "test_*.py" -v`

---

## 4. Recommendation: how a patch could use it (not applied)

**Constraint first.** The stub bytes are not fixed. The pool words come from `alloc.notes` (set addresses), and the load address comes from `alloc.alloc`. A test with checked-in final bytes proves only one build.

| Option | How | Reproducible without the toolchain | Cost |
|---|---|---|---|
| A. Assemble in `apply()` | The patch calls `build_stub.build` at build time | **No**: every build needs the toolchain on the machine | Breaks the rule |
| B. Template plus fixups | Check in the template bytes and a fixup list (pool-word offset, symbol). Make the list from the `R_ARM_ABS32` relocations of the unlinked `.o`: assemble without `--defsym` for the address symbols, so they stay relocations. `apply()` copies the bytes and writes each fixup in Python. A test rebuilds the template with the toolchain and compares | Yes | A small generator, one more file per stub |
| C. In-house assembler builds, GNU as is the oracle | Keep `ssj2_form.assemble` as the build path. Keep the `.s` next to the patch, or generate it from `CODE`. A test assembles both at the real address with the real symbols and compares. It skips when the toolchain is absent | Yes | The in-house assembler must learn each new instruction |

**Evidence for option B.** I assembled `ssj2_idle.s` with `--defsym ANIM0_ROW=0x4C` only. `readelf -r` on the `.o` shows exactly 3 `R_ARM_ABS32` entries: `.text` offsets 0x40 `SET_SSJ2`, 0x44 `SET_RAGE`, 0x48 `VANILLA`. There is none for the 0x5556 pool word and none for the branches. CONFIRMED. Two limits:

- An immediate (`add r2,#ANIM0_ROW`) cannot be a fixup. Such a constant must stay an assembler-time `--defsym` or a `.equ` in the source. CONFIRMED (gas needs the value to encode the instruction).
- The fixups must be read from the `.o`. A linked ELF has no relocations left, because `ld` resolves every symbol. CONFIRMED (standard `ld` behavior, the linked `.elf` of section 2 holds only resolved words).

**Recommended now: C** for the existing hand-assembled stubs. It changes no build output and adds no install to the build. It gives every stub an independent check against a real assembler. LIKELY the best fit while stubs stay small.

**Recommended for new code (route A-lite): B.** When a patch needs instructions the in-house assembler lacks, long calls or C, write the `.s` (or `.c`) and check in the template. The build then needs only Python. The test pins the toolchain version (15.2.rel1), so a toolchain change shows up as a test failure, not a silent byte change. LIKELY.

**Position rule for both.** A Thumb stub with an `ldr =` pool keeps its bytes only at 4-aligned load addresses. Evidence, CONFIRMED:

- `build_stub.build` at `0x08894E24` and at `0x08894F24` (+0x100) gives identical bytes.
- `ssj2_form.assemble` at `0x08894E26` (+2) gives 0x4E bytes, not 0x50. The pad disappears, and two pool loads change (`0f4b` to `0e4b`, `0e4a` to `0d4a`), because the offset uses `(pc + 4) & ~3`.

So a template (option B) is valid only when `alloc.alloc` returns a 4-aligned address for code with a pool. `build_stub.build` refuses a 2-aligned address.

---

## 5. Bible rows (for RE-BIBLE, not edited by me)

Source tag `TC` = this report (`docs\tasks\2026-10-19-toolchain\toolchain-report.md`). Add it to the source list on line 27. All rows go in section 11 (`#tool`), in the bible's column order.

| Fact | Tags | Label | Src |
|---|---|---|---|
| Arm GNU Toolchain 15.2.Rel1 (binutils 2.45.1, `arm-none-eabi`, host `mingw-w64-x86_64`) is at `%USERPROFILE%\Tools\arm-gnu-toolchain-15.2.rel1\` (user scope, no PATH). The zip SHA-256 `7936cac895611023ffb22a64b8e426098c7104cb689778c1894572ca840b9ece` matches Arm's `.sha256asc`. Call the tools by absolute path | #tool | C | TC |
| The Arm downloads page now redirects to gitlab.arm.com (WAF challenge). The developer.arm.com media path `/-/media/Files/downloads/gnu/<ver>/binrel/` still serves 15.2.rel1 and 14.3.rel1 (15.3.rel1 and 16.1.rel1: 404) | #tool | C | TC |
| GNU as flags for LoG II Thumb stubs: `-mcpu=arm7tdmi -mthumb`, `.syntax divided`, `.thumb`. In gas, `@` starts a comment and `;` separates statements. `.ltorg` pads to 4 with `0000` | #tool | C | TC |
| `scripts\one-time\2026-10-19-toolchain\build_stub.py`: `build(src, addr, defsyms) -> (bytes, labels)`, the same shape as `ssj2_form.assemble`. GNU as output equals `ssj2_form.assemble` for `ssj2_idle` (0x50 bytes at `@0x08894E24`, pool and pad included) and equals r18, r19 and r20 | #tool | C | TC |
| A Thumb stub with an `ldr =` pool keeps its bytes only at 4-aligned load addresses. At +2 the `ssj2_idle` stub loses its pad and two pool offsets change | #tool | C | TC |
| Pool words that hold a symbol not given to `as` become `R_ARM_ABS32` relocations in the `.o` (`ssj2_idle`: offsets 0x40, 0x44, 0x48). A template with Python fixups can use them. An immediate operand cannot | #tool #decision | C (relocs), L (template design) | TC |

---

## 6. Concerns

- The brief asked for the "current" version from developer.arm.com only. 15.2.rel1 is the newest there. A 15.3.rel1 on gitlab.arm.com is SPECULATIVE and not used.
- The zip came from Arm's Azure blob store by redirect from developer.arm.com. The checksum file came the same way. So the check proves integrity against Arm's published file, not against a separate signature. LIKELY enough for a personal tool.
- `scripts\permanent\` and `docs\RE-BIBLE.md` are unchanged. The test imports `patches.ssj2_idle` and `patches.ssj2_form` read only, with bytecode writes off.
