# r36 test pins (main loop, 2026-10-24 1:30 AM)

Personal GBA ROM hack (Legacy of Goku II).

## What happened

The approved his final Super Perfect Cell portrait. The main loop ran
`inject.py portrait 52 art\portrait-sources\remaster\superperfect\owner\sp52_owner_v3.png`. It built
`builds\log2_poc_r36.gba`, SHA-1 `eb4a1b4155eca4fa408bafe8c47949c67f85aa3d`. The tool reported a 4107-byte diff from r35
in 2 runs: `rom:0x894F80` (word 52, 3 bytes) and `rom:0xF341A0`-`0xF351A7` (slot 52, 4104 bytes). The art tables in `art\`
now hold portrait 52.

The suite (`py -3 -P -m unittest discover -s <root>\scripts\permanent\tests -t <root>\scripts\permanent`) now has 6 failures
of 578:

1. `test_art_inject.ArtInjectTests.test_each_table_portrait_reads_back_equal_to_its_png`: the list now has 52.
2. `test_piccolo_gi_scene.SceneTableTests.test_before_is_r28`: the "before" SHA-1 changed.
3. `test_superperfect_cell.DiffTests.test_only_named_sites_change`: 0x894f80.
4. `test_superperfect_cell.DiffTests.test_r35_file_equals_the_build`.
5. `test_superperfect_cell.PortraitTests.test_52_shows_the_same_face_as_40`: by design, 52 no longer copies 40.
6. `test_superperfect_cell.ScouterTests.test_what_the_scan_screen_shows`.

## Task

For each failure, read the test and prove its cause. Expected cause: the portrait 52 inject (word 52 and slot 52), nothing else.
If a failure has any other cause, stop and report it. Do not change a pin.

Then update each test to the r36 truth and keep its intent:
- A pin that names the latest build moves to r36, with the 2 new sites named.
- 52 now shows my portrait. Test that it reads back equal to `sp52_owner_v3.png`, and that its word no longer points at 40's frame.
- A test that rebuilds an older build from the build list must still prove that older build. Find out how these tests make the
  "before" ROM, and fix the method, not just the hash, if the art step leaks into it.

Do not weaken a test, delete a test or skip a test. Run the full suite at the end. Expect 578 tests and 0 failures.

## Limits

- Edit only `scripts\permanent\tests\`. Change a tool only if a test proves the tool wrong; if so, report it before you change it.
- No new build. Never overwrite any ROM, save or state. Never write under `data\`.
- Python: LF, no byte order mark, no em or en dashes. `py -3 -P`. Never `cd`; absolute paths only. Write and edit files with the Write and Edit tools.
- Other work is running in `scripts\one-time\2026-10-24-hud-ki\` and `%USERPROFILE%\Documents\GitHub\buusfury-decomp\` (read-only). Do not touch them.

## Report

`docs\tasks\2026-10-24-r36-pins\r36-pins-report.md`: the cause of each failure (quoted line), each change, and the final suite line.

