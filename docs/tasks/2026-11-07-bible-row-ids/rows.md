# Bible rows for the stable row id pass

Merge input, not a report. I did not merge it: a merge changes the bible after my proof ran, so the
controller owns that step.

Run (controller):
`py -3.14 -I scripts\one-time\2026-10-16-first-probes\merge_bible_rows.py docs\tasks\2026-11-07-bible-row-ids\rows.md BID "docs\tasks\2026-11-07-bible-row-ids\finding.md"`

Section 11 is `Captures and tools #tool`, which already holds the rows about our own tooling.

## Section 11

| Fact | Tags | Label | Src |
|---|---|---|---|
| Every bible data row carries a stable id in its last cell, `B0001` form, assigned once by `assign_ids` in `scripts\permanent\disasm\symbols.py` and never renumbered. Cite the id, never a line number: a merge moves every line below its insert point, and on 2026-11-07, 5 of the 13 in-bible "row N" citations already named a different fact. `whatis B0001` finds the row, matched whole against the Id cell, because 13 of the 2030 ids also appear inside another row's hex byte string. | #tool | C | BID |
| Id gap: `assign_ids` takes the next id from the highest id in the file, so deleting the newest row frees its id for reuse. `test_bible_ids.test_an_id_is_never_reused_after_its_row_is_deleted` is an expected failure that keeps this visible. A fix needs a high-water mark stored outside the rows. | #tool #open | C | BID |
| The bible table shape is `Fact, Tags, Label, Src, Id`. A parser reads the Id cell off the end FIRST, then reads the rest, because 146 decision and question rows hold only 3 cells and would otherwise read their id as Src, and 9 fact rows split into 5, 8 or 16 cells on an escaped pipe inside the fact text. | #tool | C | BID |
