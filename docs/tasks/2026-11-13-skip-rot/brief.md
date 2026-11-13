# Brief: stop the reorg's silent skips

## The defect

The 2026-11-13 reorganisation moved every build file out of the `builds\` root into
`builds\masters\`, `builds\variants\<stem>\` and `builds\early\`. Four test files still join
`log_paths.BUILDS / "log2_poc_rNN.gba"` flat. The file is not there, the `.exists()` guard fails,
and the test SKIPS. The suite stayed green and 22 tests quietly stopped running.

Two registry constants are stale the same way. Both name a folder that no longer exists.

## Task 1: route the four test files through `log_paths.build_file`

`log_paths.build_file(name)` already solves this. It finds a build file by NAME across the new
folders and returns a path even when the file is absent, so `.exists()` guards keep their meaning.

In these four files, replace every join of a build FILE NAME onto `BUILD` or `log_paths.BUILDS`
with a `log_paths.build_file(<name>)` call:

- `scripts\permanent\tests\test_chamber_spar.py` (5 sites)
- `scripts\permanent\tests\test_piccolo_gi_scene.py` (9 sites)
- `scripts\permanent\tests\test_superperfect_cell.py` (10 sites)
- `scripts\permanent\tests\test_r31_saves.py` (3 sites)

Some sites join a loop variable, not a literal: `(BUILD / dst).exists()` becomes
`log_paths.build_file(dst).exists()`. Keep each call site's shape. Do not restructure the tests.

Delete the now unused `BUILD = log_paths.BUILDS` line in a file where nothing else uses it.

## Task 2: fix the two stale constants

In `scripts\permanent\log_paths.py`:

- `ARENA_MOCKUPS` must name `builds\mockups\future\archive\2026-11-05-ending-arena`.
- Delete `ARENA_V3_MOCKUPS`. The arena v3 save states are in that same folder now, because the owner
  asked for one mockup folder per TYPE.
- In `scripts\permanent\tests\test_state_dump.py`, line 17, read `ARENA_MOCKUPS` instead.

## Task 3: add the guard that would have caught this

Add `scripts\permanent\tests\test_log_paths_exist.py`. It must assert that every `Path` constant in
`log_paths` exists on disk. Iterate the module's own attributes, so a constant added later is
covered without an edit. Report EVERY missing constant in one failure message, not the first.

This is the shape the reorg needed and did not have: a moved folder with a stale constant is
invisible, because a skip reads as a pass.

## Proof required

Run only these, and give the exact counts in your report:

    py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent ^
      -p "test_chamber_spar.py" -v

Repeat per file for `test_piccolo_gi_scene.py`, `test_superperfect_cell.py`, `test_r31_saves.py`,
`test_state_dump.py`, `test_scene_probe.py`, `test_log_paths_exist.py`.

Report, per file: tests run, failures, errors, skips, and the reason text of any skip that is LEFT.
Do NOT run the whole suite. The controller runs it.

A test that now FAILS where it used to skip is a real result, not a regression to hide. Report it.
Do not edit a test's assertions to make it pass.

## Rules

- Absolute paths only. Never `cd`, `Set-Location` or `Push-Location`.
- Never write under `data\`. Never overwrite a ROM, save or state.
- No em dashes or en dashes. ASD-STE100 style in code comments.
- Do not touch `art\Owner Build - Trunks Tank`.

One report message, then stop. Do not add a byte order mark.
