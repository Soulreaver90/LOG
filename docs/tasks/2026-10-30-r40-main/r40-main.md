# r40: new main build and trial lists that include main (final, 2026-10-30 12:45 PM)

Read `LOG\README.md`, `docs\tasks\global.md`,
`scripts\permanent\log2_build.py`, `build_list.txt`, every `build_list_trial*.txt`, the tests that read or pin build
lists or SHA-1s (search the tests for `build_list`, `aa51dc16`, `read_build_list` and 40-hex strings), and the earlier
promotion records in `docs\ledger\progress.md` (r27-r39) and `docs\build-log.md`. Search `docs\RE-BIBLE.md` for R39 rows.

## Final decisions (verbatim)

- "Let's build the master ROM of what is approved so far and all builds build on those, like a GitHub main with
  branches. Anything new builds on top of main; if main is updated so will the builds." r40 content approved: r39 plus
  `relay_cooldown`, `fullpower_hud`, `beam_struggle` (v2) and `vegeta_ssj_scene` (v5).
- Approved: trial lists include main instead of copying its lines.

Known order rules: `beam_struggle` before `vegeta_ssj_scene`; `relay_cooldown` before `chapter_cards` (chapter cards stays
a trial). `vegeta_ssj_scene` runs without `celljr_fight` (module header line 6).

## Task

1. **Include directive.** Add to `read_build_list` a line form `include <file>` (path relative to the list's folder) that
   expands that list's names in place, with a cycle guard and a clear error for a missing file. Keep comments and blank
   lines as today. Tests: expansion, nesting, cycle, missing file, a name listed twice is an error.
2. **r40 main.** Append the four modules to `build_list.txt` in a working order (state it and why), with an `r40` comment
   per line as the earlier lines have. If a module needs an earlier module that is not in main, stop and report.
3. **Trial lists.** Rewrite each `build_list_trial*.txt` as `include build_list.txt` plus only its own modules (for
   example the Cell Jr list: `celljr_fight`; the chapters list: `chapter_cards`; the Vegeta 19 list:
   `vegeta_19_reveal`). Lists whose module is now in main (cooldown, fullpower, beam, vegeta) become main only: say
   whether to delete them or keep them as aliases, and do the simpler safe thing (keep, with a comment). Make sure each
   trial still applies on top of r40 (allocations may move: that is expected; a refusal is not).
4. **Tests.** Update the tests that pin r39 or copy main's lines so they pin r40 and read lists through the include
   rule. List every pin you changed (old value, new value, file and line). No test may be weakened to pass: if one
   fails for a real reason, stop and report.
5. **Build.** `builds\log2_poc_r40.gba` (exclusive create) through `log2_build.py --list scripts\permanent\build_list.txt`,
   with a log line. Diff runs r39 to r40: every run inside a declared site of the four modules. Fresh saves for r40 the
   way r39 had them (read the R39 save rows: `log2_poc_r39.sav`, `_spar.sav`, `_computer.sav` as byte copies or with the
   same edits), exclusive create.
6. **Trials on r40.** Build each trial list once in memory and give its SHA-1 (Cell Jr, chapters, Vegeta 19 if its module
   exists). Build files only for the chapters trial (`builds\mockups\2026-10-25-chapter-cards\log2_poc_r40_chapters_v6.gba`
   with copies of `log2_poc_r39_chapters_v5_pre_a.sav`, `_pre_b2.sav` and the v5 save under r40 names) so I can
   retest with the approved features; exclusive create.
7. Full suite once at the end.

## Report

`docs\tasks\2026-10-30-r40-main\r40-report.md`: SHIPPED and PENDING tables, the include rule, the r40 order, SHA-1s,
diff runs, the pins changed, the trial SHA-1s on r40, test counts, the saves made. Bible rows (tag R40) as
`## Section N` table blocks in `scripts\one-time\2026-10-30-r40-main\bible_rows.md`. Label claims CONFIRMED, LIKELY or
SPECULATIVE.

## Limits

- Python: `py -3.14 -P`. Never write under `data\`. Never overwrite a ROM, save or state: exclusive create. LF, no em or
  en dashes. Never `cd` or `Push-Location`; absolute paths only. Scripts go in
  `scripts\one-time\2026-10-30-r40-main\`.
- Do not change any patch module's behavior. Edit only `log2_build.py`, the build lists and the tests named above.
- I am editing `docs\RE-BIBLE.md` and `docs\ledger\`. Do not touch them, or `LOG\zhack\`.

