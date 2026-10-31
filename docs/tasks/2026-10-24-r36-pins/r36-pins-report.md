# r36 pins report

Suite: `Ran 578 tests in 167.612s` then `OK` (0 failures, 0 skips). Run before the docstring-only edit in test_piccolo_gi_scene.py.

## Cause of each failure

All six trace to one cause: `art\tables\portraits.json` now holds id 52 (`portraits/052_sp52_owner_v3.png`), so `art_inject` writes
word 52 and slot 52. No other cause found. The build list puts `art_inject` before `piccolo_gi_scene` and
`superperfect_cell`, so every "before" ROM made from `names[:i]` carried the art step. This is the leak.

1. test_art_inject `test_each_table_portrait_reads_back_equal_to_its_png`:
   `self.assertEqual(sorted(self.png), [40, 63, 65, 106, 115, 117, 119])` got `[40, 52, 63, ...]`. The table has 52.
2. test_piccolo_gi_scene `test_before_is_r28`: `self.assertEqual(hashlib.sha1(self.before).hexdigest(), R28_SHA1)`.
   `before` = `assemble(BASE, names[:i])` runs `art_inject` with the live tables, so it was no longer the r28 bytes.
3. test_superperfect_cell `DiffTests.test_only_named_sites_change`: `self.assertTrue(any(a <= i < a + n for i in self.changed), hex(a))`
   failed at 0x894f80 (block word 52). `before` already had word 52 at slot 52, so superperfect's before to rom diff
   no longer changed it.
4. `test_r35_file_equals_the_build`: `self.assertEqual(path.read_bytes(), self.rom)`. The build now has portrait 52. Diff
   is word 52 and slot 52 only (not re-measured by me beyond the test; the main loop measured 4107 bytes in 2 runs).
5. `PortraitTests.test_52_shows_the_same_face_as_40`: first failure
   `self.assertEqual(block_word(self.before, 52), VANILLA_52 + ROM_BASE)` (150159776 != 141274928): before has the slot.
   By design 52 no longer copies 40.
6. `ScouterTests.test_what_the_scan_screen_shows`: `self.assertEqual(block_word(self.rom, 52), block_word(self.rom, 40))`
   (150159776 != 150110528).

## Method fix (the leak)

Both "before" builds are made by `log2_build.assemble(BASE, names[:i], notes)`. `art_inject` reads
`alloc.notes["art_input"]` when staged. New helper `art_input_without(pid)` in test_art_inject.py stages the live tables
minus one id. test_piccolo_gi_scene and test_superperfect_cell build "before" with `art_input_without(52)`. Proof:
`test_before_is_r28` passes again with the unchanged `R28_SHA1` (`eef01cf6...`), so the staged method gives the exact r28 bytes.

## Changes (tests only, `scripts\permanent\tests\`)

- test_art_inject.py: new helper `art_input_without`; list pin adds 52; `test_owner_art_copies_are_the_files_the_owner_made`
  also proves table portrait 52 equals `sp52_owner_v3.png` (24 colours, no snaps, note names "my final v3").
- test_piccolo_gi_scene.py: "before" staged without 52; docstring says so. `R28_SHA1` unchanged.
- test_superperfect_cell.py:
  - `built()`: "before" = list up to the patch, art minus 52 (r29 plus scene; 52 vanilla). "rom" = the whole list
    assembled with the live tables (r36). Docstring updated, title says r30-r36.
  - `test_52_shows_the_same_face_as_40` becomes `test_52_shows_the_owner_portrait`: before word 52 is vanilla; rom word 52 is
    `art_inject.slot(52)`, not 40's word; frame equals `sp52_owner_v3.png`; differs from 40's frame; 40 unchanged; note
    `portrait_52` is "me".
  - `ScouterTests.test_what_the_scan_screen_shows`: last line now asserts word 52 names `art_inject.slot(52)`.
  - `named_sites`: adds the slot 52 site `(art_inject.slot(52), art_inject.FRAME)` (0xF341A0, 4104 bytes); word 52 site kept.
  - `test_r35_file_equals_the_build` becomes `test_r36_file_equals_the_build_and_r35_differs_by_portrait_52_only`: r36 file equals
    the build; r35 file equals the same list built with art minus 52 (r35 is still proven); diff r35 to r36 lies inside
    the 2 sites (word 52, slot 52) and touches both. Folded into one test so the count stays 578.
- FailClosedTests, CopyTests, r32-r35 diff tests: unchanged. They use "before" (52 vanilla), so the vanilla refusal path stays tested.

No pin value changed except the list in test 1 and the named-build file (r35 to r36). No tool changed. No ROM, save or state written.
