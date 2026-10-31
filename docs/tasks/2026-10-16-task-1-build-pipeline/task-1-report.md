# Task 1 report: build pipeline and free space

Status: DONE_WITH_CONCERNS. The base ROM has no usable free space.

## Implemented
- `scripts\permanent\rom\rom_space.py`: `find_free` (0xFF and 0x00 runs, 4-aligned start, dropped if any aligned LE u32 ROM word points into the run), `Allocator` (bump allocator, `alloc`, `used`, `notes` dict). CLI prints runs.
- `scripts\permanent\log2_build.py`: `build(base, out, patch_names, log=BUILD_LOG, regions=None)`. Raises ValueError for any output under `data\`. One Allocator for the whole build. Checks size stays 8388608. Prints SHA-1 and appends a line to the log. Extra keywords `log` and `regions` exist so tests do not touch the real log and can supply a region (the ROM has none).
- `scripts\permanent\patches\__init__.py` (empty), `patches\_probe.py` (test-only patch, writes `PROBE`), `tests\__init__.py` (empty), `tests\test_build.py` (7 tests).
- `docs\build-log.md` created with the Task 1 result. One tagged line added to `docs\RE-BIBLE.md` section 2.

## TDD evidence
- RED: `py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v` gave `ModuleNotFoundError: No module named 'log2_build'`, `Ran 1 test`, `FAILED (errors=1)`.
- GREEN (same command, also with `-W error`): `Ran 7 tests ... OK (expected failures=1)`.

## Free space found
- `find_free` total: **0x0 bytes, 0 runs** (target was 0x40000). No run over 0x10000.
- Raw runs of 0x1000 or more: one, 0x1AC8 bytes of 0xFF at rom:0x7FE538 to the ROM end (6,856 bytes). One word at rom:0x239A94 (0x087FE601) points into it, so the pointer rule drops it. It may be a stray value; unproven.
- Largest 0x00 run: 0xC98 at rom:0x35970. Under the minimum. Any other byte value: no run over 0x200.
- Test `test_free_space_found` keeps the spec assert (>= 0x40000) and is marked `expectedFailure` so the suite is green and the shortfall stays visible. Remove the decorator when space exists.

## Self-review and concerns
- Main concern: the 8 MB ROM is full. The plan needs space (about 3 gi sets as raw frames) by other means: e.g. reuse of the old Gohan armor set data is NOT possible (cutscenes keep it); candidates are compression (no compressor yet), dropping unused sets, or my decision on ROM expansion (anti-piracy risk). Final decisions needed before Task 2+.
- Pointer rule drops a whole run when one word points in; it does not split. Fine for this ROM.
- `memoryview.cast("I")` assumes a little-endian host (true on Windows x86/ARM).
- Test builds write to `scratch\test-roms\`, and the test log is `scratch\test-roms\build-log-test.md`. The real log has no build lines yet (tests never write it).
- No em or en dashes, no BOM in my files. Nothing written under `data\`.

---

## Fix round 1 (16 MB expansion)

Changes:
- `log2_build.py`: output padded with 0xFF to 16777216 bytes before patches; Allocator defaults to `EXPANSION = [(0x800000, 0x800000)]`; removed the `log=` and `regions=` keywords. `BUILD_LOG` is read at call time.
- `tests\test_build.py`: tests patch `log2_build.BUILD_LOG` to a temp file with `mock.patch.object` (the `log=` keyword is gone). `test_build_without_patches_is_padded_base` checks the first 8 MB equal the base, the rest is 0xFF, the return value is the SHA-1 of the full output, and it equals `11616203341e2eabc82527c43b823b3e868c34b9`. `test_free_space_found_and_size_kept` uses the brief's assertions. No `expectedFailure` remains. The probe test checks `PROBE` sits at 0x800000.
- `docs\build-log.md`: expansion decision and padded SHA-1 recorded. `docs\RE-BIBLE.md` already carried the decision lines (added by me), so I left it alone.
- Header docstrings are raw strings so `-W error` passes.

Command: `py -3 -I -W error -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v`

Output: `Ran 6 tests in 0.383s`, `OK`. Padded build `sha1=11616203341e2eabc82527c43b823b3e868c34b9`.
---

## Fix round 2

Changes:
- `log2_build.py`: inserts its own folder into `sys.path` before sibling imports (isolated mode omits it). New CLI options `--out PATH` and `--log PATH` (needed so the subprocess test does not touch the real build or log). `build()` raises ValueError when the base SHA-1 is not `18e0715dec419f3501c301511530d2edcd590f8b`. Usage line updated.
- `tests\test_build.py`: `build` wrapper silences stdout. New `test_command_line_runs_isolated` (subprocess `-I`, exit 0, padded SHA-1 in output, 16 MB file). New `test_build_rejects_modified_base` (modified temp copy). `test_base_has_no_free_space` asserts `find_free(base) == []`; the duplicate size check is gone.
- Ran the bare command `py -3 -I scripts/permanent/log2_build.py` from the root: works, one real line appended to `docs\build-log.md`.

Command: `py -3 -I -W error -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v`

Full output:
```
test_allocator_never_overlaps ... ok
test_base_has_no_free_space ... ok
test_build_never_writes_under_data ... ok
test_build_rejects_modified_base ... ok
test_build_without_patches_is_padded_base ... ok
test_command_line_runs_isolated ... ok
test_find_free_skips_pointed_runs_and_unaligned ... ok
test_patch_runs_with_shared_allocator ... ok

Ran 8 tests in 0.502s

OK
```
(Test names shortened here; the real output prints the full `(tests.test_build.BuildTests.<name>)` form. Nothing else prints.)
