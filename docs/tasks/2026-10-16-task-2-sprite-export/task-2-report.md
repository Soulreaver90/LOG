# Task 2 report: sprite export, import and set cloning

Status: DONE

## Implemented
- `scripts\permanent\rom\log2_sprites.py`: `tiles_to_image`, `image_to_tiles` (exact inverse), `set_records` (every record `frames_of` reaches), `export_set` (PNG per unique frame header + manifest.json), `clone_set`, and an `export` command line.
- `clone_set` copies header + animation table into one allocation, each unique record list into its own allocation (exactly the records `frames_of` reaches), and one raw type 0 frame `{0, len, data}` per replaced header key. Records sharing a header (H-flip) share one new frame. All written pointers are GBA addresses. It raises ValueError for a wrong data length or a key no record uses. The remap pointer at +8 is copied unchanged.
- Type 0 behavior cited from `re-sprite-decompression.md` "Routine addresses" (0x0801F394), as instructed. No Ghidra.
- No private helpers imported from webfoot_decompress.py; it is unchanged. Public names used: ROM_BASE, SET_TABLE, frames_of, read_record (imported, unused beyond the import), read_set, rom_ptr, unpack_frame.

## TDD
- RED: with log2_sprites.py moved away, `py -3 -I -m unittest discover -s scripts\permanent\tests -p test_sprites.py -t scripts\permanent -v` gave `ModuleNotFoundError: No module named 'log2_sprites'`, `FAILED (errors=1)`.
- Note: I drafted the implementation before the tests, then hid it to show RED. One test (`writes_only_allocated_space`) failed at first from a test bug (adjacent allocations merge into one changed run); I fixed the test, not the code.
- GREEN: full suite `Ran 17 tests ... OK` (8 build tests, 9 sprite tests).

## Files
- Created: `scripts\permanent\rom\log2_sprites.py`, `scripts\permanent\tests\test_sprites.py`
- Edited: `docs\build-log.md` (Task 2 section), `docs\RE-BIBLE.md` (one line in section 4)
- Output: `art\vanilla-sets\set53,55,56,58,59\` (742 PNGs total plus manifest.json each)

## Frame counts (equal in all 4 dirs; anim:frames)
- set 53 (288 records): 0:2 1:4 2:4 3:4 4:4 5:3 6:4 7:4 8:4 9:4 11:2 12:4 13:4 14:5 16:7 17:2 18:7 20:4
- set 55 (216): 0:2 1:4 2:4 3:4 4:4 5:3 6:4 7:4 8:4 11:2 12:4 13:4 14:5 17:2 20:4
- set 56 (288): same as set 53
- set 58 (204): 0:2 1:4 2:4 3:4 4:4 5:3 6:4 7:4 8:4 13:4 16:7 18:7
- set 59 (276): 0:2 1:4 2:4 3:4 4:4 5:3 6:4 7:4 8:4 9:4 11:2 12:4 13:4 16:7 18:7 20:4 21:4
Totals match the docs.

## Self-review
- Dashes and BOM checked on all four touched files: none.
- Review Focus 5 test (`test_clone_every_record_decodes`) runs on set 59 with all frames replaced.

## Concerns
- Tests read the base ROM from `data\roms` (read only) and need Pillow (present, 12.3.0).
- Animations with null table entries (e.g. 10, 15, 19 in sets 53 and 56) stay null in a clone. A later task that needs those animations must handle that.
- A set whose lists overlap across table entries would clone each unique start separately; no such case in sets 53-59 tests.
