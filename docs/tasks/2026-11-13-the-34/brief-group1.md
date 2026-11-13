# Brief: group 1 of the 34, the pinned SHA-1s

Read `docs\tasks\2026-11-13-the-34\triage.md` first. It lists all 34 failures with evidence.
You own **group 1 only**: the 12 rows that fail as `'<hash>' != '<hash>'`. Do not touch group 2,
3 or 4. Another agent has those.

## Why these fail

The build system allocates ROM space with a bump allocator over one free region. A module that
changes size moves every later allocation, so both master ROMs get a new SHA-1 with no build list
change. 12 tests type a hash that is now historic.

Worse, the SAME hash is copy-pasted into separate files. `ffbd2bfc766f7766d6ebe8c0f1905a53e6c4ce07`
is `DEV_SHA1` in `test_celljr_fight.py:147`, `test_gi_base_audit.py:32` and `test_golden.py:28`.
Three places to update, so in practice none were.

## What to build

### 1. One home for the master hashes

Create `scripts\permanent\tests\masters.py`. It holds exactly two values, the golden master and
the dev master, with a comment saying that changing them is a deliberate act and must name the
build that moved them. Every test that needs a master hash imports from here.

Do NOT read the expected hash from `docs\build-log.md`. The build writes that log, so a build
checked against it proves only that the build agrees with itself. The pin must stay a hand edited
tripwire. That is its whole job.

Leave the two values EXACTLY as they are today, wrong. The controller re-pins once at the end,
after every other group lands. If you re-pin now, the later groups will move them again.

### 2. The "before" tests state what they mean

These are the rows named `test_before_is_r39`, `test_before_is_r40`, `test_before_and_r40_are_pinned`,
`test_before_and_the_dev_master_are_pinned`, `test_before_is_the_dev_master`,
`test_before_is_r39_plus_relay_cooldown`, `test_before_is_r40_plus_chapter_cards`,
`test_the_dev_list_still_rebuilds_to_the_dev_master`, `test_on_r39_alone_it_is_the_trial_rom_the_owner_played`
and `test_before_and_the_rom_are_pinned`.

Each builds a ROM from "the master list minus this trial module" and checks it against a hash
frozen when that trial was new. The dev list has changed many times since, so the build is no
longer that historic ROM and the hash can never match again.

The INTENT is "this trial sits on top of the current master". Assert that directly, by comparing
MODULE LISTS, not hashes. `test_relay_cooldown.test_trial_list_is_the_main_list_plus_the_trial_line`
already does exactly this, including the case where the trial was approved into dev. Follow it.

Keep a hash comparison only where the thing compared is a CURRENT master, and then take the value
from `masters.py`.

### 3. Do not delete coverage

If removing a hash leaves a test asserting nothing, give it the assertion the name promises. A test
named `test_before_is_r39` that checks nothing is worse than one that fails. Say in your report
which tests changed what they prove.

## Rules

- Absolute paths only. Never `cd`, `Set-Location` or `Push-Location`.
- Never write under `data\`. Never overwrite or create a ROM, a save or a state anywhere.
- No em dashes or en dashes anywhere. ASD-STE100 in comments: short sentences, active voice.
- Comments explain WHY, never what. One or two lines, never a paragraph.
- Do not run the whole suite. The controller runs it.

## Proof required

Run each file you touched, alone, and give a table of: tests run, failures, errors, skips.

Expected end state: the 12 group 1 rows no longer fail for a stale hash. `test_golden`'s two
master tests STILL FAIL, because the controller has not re-pinned yet. That is correct and
expected. Say so rather than fixing it.

Report any test that now fails for a NEW reason. Do not weaken an assertion to make it pass.

One report message, then stop. Do not add a byte order mark.
