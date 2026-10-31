# Disasm port report: legacyofgoku2-disasm built with the GNU toolchain (2026-10-22)

| Ask | Status |
|---|---|
| 1. ADS dependency list | DONE, below |
| 2. Port plan | DONE, implemented |
| 3. Proof build | DONE: whole ROM, SHA-1 match, 0 differing ranges |
| 4. Names cross-check | DONE: `docs\names-crosscheck.md` in the clone |
| 5. Tool safety list | DONE, below |
| `docs\GNU_BUILD.md`, commits, bible rows | DONE, never pushed |

Repo: `%USERPROFILE%\Documents\GitHub\legacyofgoku2-gnu`, branch `gnu-port`. Bible rows: `scripts\one-time\2026-10-22-disasm-port\bible_rows.md`. Cross-check script: `scripts\one-time\2026-10-22-disasm-port\names_crosscheck.py`.

---

## 1. What the build needs from ADS

All CONFIRMED by reading the files.

| File:line | ADS dependency |
|---|---|
| `rebuild.cmd:5-9` | `ADS` defaults to `..\toolchains\ads12-build805`; sets `PATH`, `ARMHOME`, `ARMINC`, `ARMLIB` |
| `rebuild.cmd:24` | `armasm asm\buu.s -o build/buu.o` |
| `rebuild.cmd:27` | `armlink build/buu.o -noremove -scatter scatter.ld -map -symbols -o build/log2.axf` |
| `rebuild.cmd:30` | `fromelf build/log2.axf -bin -o build\ROM_START` |
| `scatter.ld:1-14` | ADS scatter syntax: load region `ROM_LOAD 0x08000000`, execution regions `ROM_START 0x08000000` (RomHeader), `ROM_CRT0 0x080000c0` (Init), `ROM_REMAINDER 0x08000100` (Remainder) |
| `asm\buu.s:1-11` | `INCLUDE`, `AREA RomHeader, CODE, READONLY`, `INCBIN`, `END` |
| `asm\crt0.s` | `AREA Init`, `CODE32`, ARM instructions with an `EQU` name (`#REG_DISPCNT`), `END` |
| `asm\registers.s`, `asm\memory.s` | `NAME EQU value` |
| `asm\remainder.s` | `AREA Remainder`, 1,333 `INCLUDE ..\build\code\*.s`, 6,271 `INCBIN` (retail gaps and `build\jcalg1\gen_*.bin`) |
| `tools\code\emit_code.py:49-56, 490, 500, 420-429` | Emits ADS dialect: bar labels `\|loc_X\|` and `\|sub_X\|` alone on a line, `CODE16`/`CODE32`, `DCD`/`DCW`/`DCB`, uppercase mnemonics, no EXPORT/IMPORT, no `LTORG` (pools are emitted as `DCD` files at fixed places) |
| `tools\compress\generate_containers.py:67-72` | Writes `remainder.s` in ADS syntax (`AREA`, `INCLUDE`, `INCBIN`) |
| `tools\gate\gate.py:18, 179` | The gate runs `rebuild.cmd`, so it needs ADS; it reads `build\ROM_START` (the `fromelf` output) |
| `tools\code\test_emit_code.py:30-35, 62-96` | Reassembly test needs `ADS12_HOME` or `ARMHOME` (`armasm`, `armlink`, `fromelf`), skips otherwise |
| `tools\research\library_match.py:210` | Reads the ADS C library (`%ARMLIB%\armlib`) |
| `INSTALL.md:3-5`, `README.md:62`, `.recomp.json:9` | Docs name ADS 1.2 |
| `extract.cmd`, `check.cmd`, CI `check.yml` | No ADS use |

## 2. Port plan (implemented)

The ADS sources stay the single source of truth; the GNU input is derived at build time.

| ADS | GNU | Where |
|---|---|---|
| `\|loc_X\|` label line, `\|loc_X\|` operand | `loc_X:`, `loc_X` | `emit_code.py --dialect gnu` (one switch, `gnu_text`) |
| `CODE16`/`CODE32` | `.thumb`/`.arm` | same |
| `DCD`/`DCW`/`DCB` | `.word`/`.hword`/`.byte` | same |
| `AREA X, CODE, READONLY` | `.section .X, "ax", %progbits` | `tools\gnu\build_gnu.py` translates `asm\*.s` into `build\gnu\asm\` |
| `NAME EQU v` | `.equ NAME, v` | same |
| `INCLUDE`, `END` | `.include "build/gnu/..."`, dropped | same |
| `INCBIN baserom.gba_0xA_0xB.extracted` | `.incbin "baserom.gba", 0xA, 0xB-0xA` (no slice files) | same |
| `scatter.ld` | `gnu_rom.ld`: `.RomHeader 0x08000000`, `.Init 0x080000C0`, `.Remainder 0x08000100`, with size asserts | repo root |
| `fromelf -bin` | `objcopy -O binary` | `build_gnu.py` |
| Literal pools | No `.ltorg` needed: every pool is already explicit `.word` data at its fixed place | n/a |

Decision: `emit_code.py` emits GNU directly behind `--dialect gnu` (default stays `ads`, its output is unchanged: `--check` passes against the old ADS output). The five hand-written wrappers are translated, not forked, so upstream edits flow through.

Two encodings differ between the assemblers (CONFIRMED by the first build's 6 differing 2-byte ranges):
- ARM immediates with several imm8/rotation forms: ADS (and the retail ROM) take the smallest left rotation, GNU as the smallest right one. Sites: `@0x080000D8` (`0x04000000`), `@0x08000120` (`0x84000000`). The GNU text writes `#0x40, 12`. The first rule I tried (largest imm8) broke `add sp,sp,#4`; the left-rotation rule matches every site in the tree. Label: CONFIRMED for this tree, LIKELY as the general ADS rule.
- Thumb `sub rd, rd, #imm3`: GNU as uses the 8-bit form. The GNU text emits `.inst.n 0x1FC0`. All 4 sites are actually the literal word `0x03001FC0` that their `gap-fill code` decodes as Thumb (CONFIRMED: 11 pc-relative `ldr` read them).

## 3. What I installed

Nothing new. The Arm GNU Toolchain 15.2.Rel1 (binutils 2.45.1) was already at `%USERPROFILE%\Tools\arm-gnu-toolchain-15.2.rel1\` (bible row, source TC). The build finds it through `ARM_GNU_BIN` or `PATH`.

For the tests only: a venv at `legacyofgoku2-gnu\build\venv` (ignored by git) with `pytest` 9.1.1 from PyPI. The system Python has no pytest.

ROM: copied the base ROM to `legacyofgoku2-gnu\baserom.gba` (path their docs name). `.gitignore` line `baserom.gba*` keeps it out of git (`git check-ignore` CONFIRMED). Nothing written under `LOG\data\`.

## 4. Proof result

Whole ROM, not a slice.

```
python tools\gnu\build_gnu.py     (ARM_GNU_BIN = the toolchain bin folder)
image sha1=18e0715dec419f3501c301511530d2edcd590f8b
retail sha1=18e0715dec419f3501c301511530d2edcd590f8b
image sha256=6e6c370c339ec9171cb1956adf837a0d342a197f78964882ef46c3086656ff75
DIGEST MATCH
```

- Differing ranges: none. Re-run after the reboot on commit `40ad6b3`: still DIGEST MATCH.
- Output: `build\gnu\log2.gba` (8,388,608 bytes).
- Assembled from source: 84,404 bytes of code and pools (1,333 files). Everything else is `.incbin` of the retail image.
- The packed container runs are retail slices in this build, because their re-encoder is the prebuilt `compress.exe` (see 6). In the ADS build those 2.68 MB count as "source", so the GNU build's honest source share is about 1 %, not 32.95 %.
- 45 assembler warnings, all "will not write back the base register" on Thumb `ldmia rN!, {..rN..}`. Bytes are retail.
- Tests: `tools\code\test_emit_code.py` 9 passed, 1 skipped (the ADS reassembly test); `tools\gnu\test_build_gnu.py` 4 passed (includes the full build). Their whole-tree lints: `LINT PASS: 0 finding(s) over 63 file(s)` and `check_links: 0 finding(s)`. Note: their READABILITY lint needs `build\code` from an ADS-dialect emit; without it it fails `ram=0` whatever the change.

## 5. Commits on `gnu-port` (never pushed, upstream remote unchanged)

| Commit | Title |
|---|---|
| `1fbfa86` | Add a GNU as dialect to the code generator |
| `4dae06e` | Build the ROM with the GNU Arm toolchain |
| `72eeff6` | Document the GNU toolchain build |
| `39f3049` | Cross-check the function census against a code map |
| `eee3573` | Correct the veneer cause in the cross-check |
| `40ad6b3` | Name the four Thumb pin sites in GNU_BUILD.md |

Flaw: the body of `eee3573` mentions the GNU_BUILD.md note, which landed one commit later in `40ad6b3` (an Edit failed). No other effect.

Files: `tools\code\emit_code.py` and its test (modified, MPL like the rest), new `tools\gnu\build_gnu.py`, `tools\gnu\test_build_gnu.py`, `gnu_rom.ld`, `docs\GNU_BUILD.md`, `docs\names-crosscheck.md`, one pointer line in `README.md`. No renames in their files.

## 6. Names cross-check summary

Full doc: `docs\names-crosscheck.md` (causes, examples, 305-row name table).

- Theirs 1,094 starts (770 `start` + 324 `unreferenced`) plus 1,353 fragments. Ours 2,264. Shared: 857.
- Ours only (1,407): 1,289 in bytes they leave unclassified (vtable 891, `bl` 98, prologue 87, constructor list 67, symbols 60, ROM pointer 38, other 48 including 16 veneers); 56 inside their code but not an entry (`0x080000C0` crt0: they split at the scatter boundary `0x08000100`); 49 are their fragments (split versus merged, `0x080019D4` folded into `0x08001960`); 10 IWRAM overlay (they class it as data); 3 inside their literal pools (`0x0800D6C8` is LIKELY code: `push {r4,lr}; mov r4,r0`, 2 vtable refs).
- Theirs only (237): 134 inside one of our function bodies (we merge, `0x08000302` in our `0x080002F8`); 103 not in our map, 100 of them `unreferenced` "block" starts, mostly `gap-fill code`, several on data or a `0x0000` pad (`0x080056AE`).
- Veneers: our 37 flags, 21 are their starts. Both pad forms appear in both groups, so the pad does not explain the 16 misses (my first guess, corrected in `eee3573`). One of our 37 is wrong: `0x08022E60` is the C library signal strings ("Divide By Zero" ...), and the real veneer is at `0x08022EC0` (CONFIRMED).
- Names: 32 addresses named on both sides, 0 spelled alike, some differ in meaning (`0x08003C24` `save_defaults` vs `Scene_Clear`; `0x0801F2CE` `scene_set` vs `Handler_Restore`): review before any rename. 194 names only ours, 79 only theirs (all 79 are our unnamed starts).

## 7. Tool safety list (read before running)

| Tool | Network | Runs an `.exe` | Deletes | Writes outside repo | Uploads | I ran it |
|---|---|---|---|---|---|---|
| `tools\compress\jcalg1.py` `encode` | no | **yes: prebuilt `compress.exe`** | temp dir | `%TEMP%` (TemporaryDirectory) | no | no |
| `tools\compress\generate_containers.py` | no | **yes, through `jcalg1.encode`** on each cache miss | no | no (writes `build\`, repo-root slices, `asm\remainder.s` with `--write`) | no | no |
| `rebuild.cmd` | no | ADS `armasm`/`armlink`/`fromelf`, and the above | no | no | no | no |
| `tools\gate\gate.py` | no | `cmd.exe /c rebuild.cmd` and `extract.cmd`, `git ls-files` | `build\*.o`, image, repo-root slices; `--cold` does `rmtree build\compress-cache` | no | no | no (only read) |
| `tools\runtime\watch_sweep.py` | localhost socket to a GDB stub | **yes: any `--exe` you pass** (emulator), sets its process priority via `ctypes` | no | `--out` directory you pass | no | no |
| `tools\lint\lints.py` | no | `git`, and `python -m pytest` on cited behaviour tests | no | no | no | yes |
| `tools\research\library_match.py` | no | no | no | reads `%ARMLIB%` (ADS) | no | no |
| `tools\code\emit_code.py` | no | no | `*.s` in its `--out` folder | no | no | yes |
| `code_split.py`, `export_inputs.py`, `function_bounds.py`, `name_table.py`, `code_index.py`, `check_links.py` | no | no | no | no (`--write` rewrites tracked docs) | no | `emit_code` imports; `check_links.py` ran |
| `tools\extract\slice_rom.py`, `tools\incbin.bat` | no | no | no | beside the image | no | no |
| Tests: `test_gate.py`, `test_lint.py` | no | no | their own `tempfile.mkdtemp` folders | `%TEMP%` | no | no |

No tool in the tree uploads anything or reaches the internet. The one prebuilt binary is `compress.exe`; nothing I ran calls it.

## 8. Effort left

| Item | Size | Note |
|---|---|---|
| Free JCALG1 encoder (Python or built from the MIT source) so the GNU build re-encodes the containers like `rebuild.cmd` | medium | Without it the GNU build carries 2.68 MB as retail slices |
| A `gate.py --gnu` mode (source accounting for the GNU build) | small | Today `build_gnu.py` checks only the digest |
| Level 2 (relocatable): labels for pool words that hold code and data addresses, then a shift test | large | Bible row: 1,350 pool words and about 66,000 data words hold ROM addresses |
| Review the 32 double-named addresses and the 3 pool-or-code conflicts before any rename | small | Listed in `docs\names-crosscheck.md` |
| Fix our code map row `0x08022E60` (strings, not a veneer) | small | Bible row in `bible_rows.md` |

## Concerns

- The ADS rotation rule is proven only on the sites in this tree. New ARM code from upstream could hit an untested case; the digest check would catch it.
- `0x0800D6C8` (code classed as pool by them) and the 4 pool words classed as code show their split has errors in both directions. The bytes are still exact, but names keyed to their starts can sit on data.
