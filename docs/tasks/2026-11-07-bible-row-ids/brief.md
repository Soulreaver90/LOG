# Brief: give every bible row a stable id, pass 1

Agent: build. Read `docs\tasks\global.md` first. Absolute paths only. Never `cd`.
Read `docs\tasks\2026-11-07-bible-row-ids\finding.md` before anything else. It holds the measurement.
The owner chose this fix this morning. It is approved work, not a proposal.

## The problem in one line

A bible "row N" is a FILE LINE NUMBER, so every merge silently re-points every citation.

`scripts\permanent\disasm\symbols.py` line 241 builds `Row(n, ...)` from
`enumerate(BIBLE.read_text().splitlines(), 1)`. `whatis` prints that `n`, which is where our citations
come from. I merged 10 rows at 9:30 AM today and the tool reported inserts after lines 311, 682, 1665,
1825 and 2163, so every citation below each of those moved again while I watched.

## Scope of THIS pass

Pass 1 gives the ids and teaches the tools. **Pass 1 does NOT re-resolve the 65 existing citations.**
That is pass 2, and a second agent will do it after the map reader agent finishes. Do not touch them.

## The design, decided. Do not redesign it.

**Id format:** `B0001`, a capital B and four zero-padded digits. Assigned in the file's current top to
bottom order, so the first data row is `B0001`. The bible holds **2030 data rows** today, counted with
`symbols.py`'s own rule, so four digits leave room. An id is assigned once. **An id is never reused and
never renumbered, even when its row is deleted or rewritten.**

**Placement: a NEW TRAILING column.** The header becomes `| Fact | Tags | Label | Src | Id |` and the
separator gains a sixth pipe. This matters: `symbols.py` reads `cells[0]`, `cells[1]`, `cells[2]` and
`cells[3]`, so a trailing column leaves every existing index meaning what it means today. **Do not add a
leading column.** I checked the parsers: only `scripts\permanent\disasm\symbols.py` and
`scripts\permanent\rom\whatis.py` parse the bible. `patches\gohan_portraits.py` mentions it in a comment
only.

**Rows that are not 4-column fact rows** (question tables, decision tables, prose, section headings) get
no id. Use `symbols.py`'s own test for what a data row is, do not invent a second one.

## The work

1. **The bible.** One scripted pass that appends the `Id` column to every data row and fixes every table
   header and separator. I already took the backup:
   `archive\backups\2026-11-07_bible-stable-ids\RE-BIBLE.before-ids.md`, SHA-1 `de47cdc0`. Verify that
   file exists and matches before you write, and leave it alone.
2. **`disasm\symbols.py`.** `Row` carries the id. Keep the line number field as well, because other code
   may use it, and say in the docstring that the line number is NOT an identity.
3. **`rom\whatis.py`.** Print the id as the citation form for every bible hit. The line number may stay
   beside it, but the id is what a reader is meant to copy. Say so in the output, briefly.
4. **The merge tool**, `scripts\one-time\2026-10-16-first-probes\merge_bible_rows.py`. It must assign the
   next free id to every row it merges, by reading the highest existing id and counting up. Its summary
   line must report the ids it assigned, as it already reports the row count.
5. **A test module**, `scripts\permanent\tests\test_bible_ids.py`. It must pin at least:
   - every data row has an id, and the count equals the data row count
   - ids are unique
   - ids match `^B\d{4}$`
   - **the stability property, proved not assumed:** take the real bible in memory, insert a row near the
     top, re-run the id assigner, and assert that every pre-existing row keeps the id it had. This is the
     whole point of the change, so it must be a real red-provable test, not a shape check.

## Out of scope, do not touch

- Any file under `scripts\permanent\scene\`. Another agent owns that folder right now.
- The 65 existing "bible row N" citations. Pass 2 owns them.
- Any ROM fact. This pass changes no fact, no address and no ROM byte. If a row's text would change,
  stop and report it instead.
- The full test suite. Run your own module plus any module that parses the bible. I run the suite myself.

## Rules

- `py -3.14 -P`. Never put a Windows path inside a Python string literal in a heredoc.
- Never write under `data\`. Never overwrite a ROM, save or state.
- Never pipe a test run into `tail` or `head`: the pipe reports the pipe's exit code.
- Prove the bible is unharmed: the data row count, the tag counts and every row's first three cells must
  be byte identical to the backup, apart from the appended column. Report how you proved it.
- Report: what you changed, how you proved the row text is untouched, your test counts with real exit
  codes, and anything you could not prove.

One report message, then stop. Do not add a byte order mark.
