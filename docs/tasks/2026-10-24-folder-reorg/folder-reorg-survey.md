# LOG folder survey and reorganization plan (final, 2026-10-24 9:53 AM). PLAN ONLY: move nothing.

Personal GBA ROM hack: Legacy of Goku II merged with Buu's
Fury. Not a git repo.

## My ask (verbatim)

"right now the LOG folder is a bit of a mess, everything is everywhere and hard for me to find where anything is. Maybe have
another task review and reorganize everything clearly and we stick to defined folders/logic."

"its a mess, i dont know where anything is and some dont seem to have a reaseon or rhyme? like what is "re". Sprites thrown
all over, etc."

## The house rules the layout must follow

`%USERPROFILE%\Documents\Projects\Workspace\README.md` (read it). In short: each project root holds only README.md;
`scripts\` (`permanent\<purpose>\` reusable, `one-time\`), `sql\`, `docs\`, `data\`, `test-data\`, `deploy\`, and `scratch\` for
throwaway only (deletable without asking). `Workspace\HALO` is the fully organized example: look at its top two levels.

## Task

1. **Inventory:** walk the whole tree (all levels; do not cut a listing short). For every folder: what it holds (file types,
   count, total size), what it is for in plain words, which tools or tests read or write it, and whether it is live, an
   archive, or throwaway. Count files per top-level folder and per `scratch\` subfolder.
2. **Find the pain:** where the same kind of thing lives in several places (sprites and art, ROM builds and saves, reports and
   briefs, research notes, tools), cryptic names (`re`, `sdd`, `slice1`, `ba_*`, `r12fix`, ...), live work that sits under
   `scratch\` although it is not throwaway, and dead or superseded files.
3. **Proposed layout:** a clear tree with plain-English folder names that I can browse without help (for example
   "research" not "re"), one home per kind of thing, and a one-line purpose for every folder. It must keep the house rules.
   Say where new work of each kind goes from now on (a short "where does X go" table).
4. **Move map:** old path to new path for every folder (and loose file where needed), as a table.
5. **Reference impact:** every place that names a path that would move: Python code under `scripts\` (constants, `ROOT /`
   joins, defaults), tests, `build_list.txt`, `docs\` (RE-BIBLE.md, build-log.md, design docs), briefs and reports, memory notes
   (my project notes, files whose name starts
   `feedback_log_` or `project_log_`). Use at least two search shapes per path (the path with backslashes, with forward slashes,
   and the folder name joined in code such as `"scratch" / "re"`), reconcile the counts, and say which shapes could still miss
   a reference. State which references must change for the build and the 605-test suite to stay green.
6. **Migration plan:** ordered steps that keep the build and suite green at each step, how to prove it (suite command:
   `py -3 -P -m unittest discover -s <root>\scripts\permanent\tests -t <root>\scripts\permanent`), a backup step first, and what
   to do with the RE-BIBLE's many old paths (rewrite, or a path-alias table at the top). Effort and risk per step.
7. **Final decisions:** the choices only I can make (names, what to archive or delete, whether old build ROMs r1-r35
   are kept).

## Report

`scratch\sdd\slice1\folder-reorg-plan.md`: written for me (plain words, tables, short sentences, no jargon without a
gloss). Lead with the proposed tree and the "where does X go" table, then the pain points, the move map, the reference impact,
the migration plan, the decisions. Raw inventory data goes in `scratch\sdd\slice1\folder-reorg-inventory.md`.

## Limits

- **Read only.** Move, rename, delete or edit nothing except the two report files. Never write under `data\`.
- Two other tasks may run: one in `scratch\re\hud_ki\`, one editing `scratch\re\base_audit\ba_sheet.py`. Only read.
- Never `cd`, in any shell; absolute paths only. Create files with Python. No em or en dashes.
- Label claims CONFIRMED (you read it), LIKELY or SPECULATIVE.

