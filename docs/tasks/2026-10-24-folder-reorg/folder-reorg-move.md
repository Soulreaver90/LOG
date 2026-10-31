# LOG folder move: execute the approved plan (final, 2026-10-24)

Personal GBA ROM hack. Not a git repo. You are the only task
running; I make no edits inside LOG until you report.

## Approved plan

`scratch\sdd\slice1\folder-reorg-plan.md` (read all of it) with my answers in its section 7, and the inventory
`folder-reorg-inventory.md`. Answers in short: top-level `art\` and `builds\`; archive old builds r1-r17 and r19-r26 (with
twins) to `archive\builds\`, test inputs stay; archive every copy and the review renders (delete nothing); keep `RE-BIBLE.md`;
rename `scripts\permanent\re\` to `disasm\`; keep the gi folder names and explain them in `art\README.md`; one dated folder per
task under `docs\tasks\`; study scripts in `scripts\one-time\<date-task>\` with reports in `docs\tasks\<date-task>\`; promote
reused tools later (not now).

Since the survey, new things landed. Re-inventory before you start and fold them in:
- r39 build: `scripts\permanent\patches\bf_hud.py`, `bf_ki_pool.py`, tests `test_bf_hud.py`, `test_bf_ki_pool.py`, a new build
  input read from `data\roms\` (read only), `scratch\build\log2_poc_r39*`, `scratch\re\r39\`. Latest build r39 (SHA-1
  `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`), suite 666 OK.
- New study folders: `scratch\re\celljr\`, `scratch\re\computer_save\`, `scratch\re\hud_ki\proto\`, `scratch\re\block\pose\`.
- New briefs and reports in `scratch\sdd\slice1\`.
- `scratch\re\base_audit\ba_sheet.py` changed (HANDFIX status). The base audit tools and `scratch\art\base_audit\` (proposed,
  approved, to_edit, me, sheets) are my live sprite work: move them as one unit and keep them working.

## Task

1. **Step 0, backup:** copy the whole LOG tree except `data\` to
   `archive\backups\2026-10-24_pre-reorg\` (exclude that folder from
   every later step). Prove it: file count and total size equal to the source (minus `data\`).
2. **Execute the plan's migration steps in order** (plan section 5), starting with the single paths module (`log_paths.py`)
   so later moves are one-line changes. After **every** step run the plan's five gates (5.1): per-test ok/skip list equal to
   before, every needed file exists, a rebuild with `log2_build.py` gives the r39 SHA-1 (into scratch, exclusive create, then
   delete that test output only), old paths stay gone, the before/after hash list matches for moved files. If a gate fails,
   undo that step, stop, and report. Never continue past a red gate.
3. **`data\` renames:** do NOT rename anything under `data\`. List each proposed rename (old name, new name, why, what reads
   it) in the report for my per-item yes.
4. Rewrite live path references (code, tests, build list, `docs\`, the `feedback_log_*` and `project_log_*` memory notes in
   my project notes) and add the alias table at the
   top of `docs\RE-BIBLE.md` and `docs\build-log.md` for history. Write `LOG\README.md` (the map and the "where does X go"
   table) and `art\README.md`.
5. Final proof: full suite (count and OK), the r39 rebuild SHA-1, the top two levels of the new tree, file counts per top folder
   before and after (they must reconcile, with the backup counted separately).

## Report

`docs\tasks\2026-10-24-folder-reorg\folder-reorg-move-report.md` (or the plan's equivalent path; say where it went): SHIPPED and
PENDING tables, each step with its gate results, the final proof, the `data\` rename list, anything left and why.

## Limits

- Never write under `data\`. Never overwrite any ROM, save or state (moves keep bytes; prove with hashes). Delete nothing except
  your own temporary gate outputs.
- Python: LF, no byte order mark, no em or en dashes. `py -3 -P`. Never `cd`, in any shell; absolute paths only. Move files with
  Python (`shutil.move` after an existence check) or PowerShell `Move-Item` with explicit paths, never a wildcard you have not
  listed first.

