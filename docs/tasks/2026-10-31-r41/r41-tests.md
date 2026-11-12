# r41: bring the suite to the promoted build lists

`build_list_core.txt` now ends with three modules that were trial-only until today:

    chapter_cards       # r41 (card 4 v12)
    vegeta_19_reveal    # r41
    celljr_fight        # r41 (v10 facings)

`build_list_trial.txt`, `build_list_trial_chapters.txt` and `build_list_trial_vegeta19.txt` are now plain
aliases of `build_list_dev.txt`, like `build_list_trial_beam.txt`.

New SHA-1s, built and confirmed before this brief:

| list | SHA-1 |
|---|---|
| `build_list.txt` (golden) | `acf1b15f46628255bdf00d025464b807ce7410a9` |
| `build_list_dev.txt` (dev) | `ffbd2bfc766f7766d6ebe8c0f1905a53e6c4ce07` |
| `build_list_trial_gi_base.txt` | `d1cb26258cfdc346d7104835ddfa66393eb1eb13` |
| `build_list_trial_spritelab.txt` | `d432f64076982bfe3764b60573ceacb730cf54f5` |
| the six alias lists | same as dev |

## The job

Ten tests fail. Every one encodes "these three modules are not in main yet". Make the suite describe the
world as it is now. **Change tests only. Do not change a patch module or a build list.**

    tests/test_art_inject.py      test_build_list_replaces_both_portrait_remaster_calls
    tests/test_celljr_fight.py    test_before_is_r40
    tests/test_chapter_cards.py   test_main_to_new_diff_is_the_declared_sites
    tests/test_chapter_cards.py   test_android_19_table_is_untouched
    tests/test_gi_base_audit.py   test_before_is_r40
    tests/test_golden.py          test_dev_still_rebuilds_to_r40
    tests/test_golden.py          test_golden_builds_to_its_pinned_sha1
    tests/test_sprite_lab.py      test_the_dev_list_still_rebuilds_to_r40
    tests/test_vegeta_19_reveal.py  test_before_is_r40
    tests/test_vegeta_19_reveal.py  test_main_to_trial_diff_is_the_word_and_the_copy

Two kinds, and they need different treatment:

1. **Pinned SHA-1s.** `R40_SHA1` and `GOLDEN_SHA1` constants in eight test files (grep `14d6b831` and
   `232fcceb` under `tests/`). Repoint to the table above and fix the comment beside each so it names r41
   and the date. `test_vegeta_ssj_scene.py` pins one too and currently passes; check whether it still means
   what it says.

2. **Tests whose premise changed.** A test that builds "main without this module" and asserts the diff is
   still worth having, but its baseline can no longer be r40, and a trial-against-main diff is now empty.
   Keep each test's intent: the module must still change exactly the sites it declares and nothing else.
   Rebuild the baseline as "the current core list minus this one module" rather than a pinned old ROM.
   `test_android_19_table_is_untouched` asserts main leaves that table alone, which main now deliberately
   does not. Move the assertion to whatever still holds, or say plainly why it cannot, rather than deleting it.

## Gate, run it yourself and quote real numbers

- Full suite green: `py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent`.
  Redirect to a file and read the real exit code. Never read an exit code through a pipe.
- Both masters still build to the SHA-1s in the table.
- `git diff --stat` touches only files under `scripts\permanent\tests\`.

## Report

Per test: what you changed and why, in one line. Name any test whose intent you could not preserve, and say
what is no longer covered. Quote the suite's `Ran N tests` line, the `OK`, and the real exit code.

One report message, then stop. Do not add a byte order mark.

## Addendum, 2026-11-02, checked before handing this over

This brief is still accurate. I re-ran the full suite today: 1165 tests, 10 failures, real exit code 1. The
10 are byte for byte the 10 named above, matched on module AND method. Nothing drifted in two days.

Four corrections and clarifications to the text above:

1. **Seven test files pin the old SHA-1s, not eight.** `grep -rln "14d6b831\|232fcceb" tests\*.py` returns
   `test_celljr_fight`, `test_chapter_cards`, `test_gi_base_audit`, `test_golden`, `test_sprite_lab`,
   `test_vegeta_19_reveal` and `test_vegeta_ssj_scene`.
2. **`test_vegeta_ssj_scene.py` line 35 is mislabelled, and I confirmed it.** It reads
   `R40_SHA1 = "14d6b831..."` with the comment `build_list.txt r40`. That value is the DEV master's r40
   SHA-1, while `build_list.txt` is the GOLDEN master. Fix the comment to name the dev list. Do not change
   the value without first proving what the constant is actually compared against.
3. **`test_art_inject` pins a module LIST, not a SHA-1.** It fails on
   `assertEqual(built()["names"], LIST)`, because the built list now ends with `chapter_cards`,
   `vegeta_19_reveal` and `celljr_fight`. It belongs to category 2, not category 1.
4. **The SHA-1 table is confirmed reproducible.** My run today rebuilt both masters from this tree and got
   `acf1b15f` and `ffbd2bfc`, matching the table.

Out of scope for you, I am doing these myself after your report lands. Do not touch them, because the gate
above requires your diff to stay inside `scripts\permanent\tests\`:

- `CLAUDE.md` lines 46 and 47, which still record `232fcceb` and `14d6b831`.
- `docs\build-log.md`, which has no r41 line and neither new SHA-1.

Also ignore the existing uncommitted change in `tests\test_build.py`. It is mine, from the trunks_tank
work, and has nothing to do with r41. Leave it exactly as it is.
