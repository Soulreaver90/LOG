# Finding: a bible "row N" is a FILE LINE NUMBER, so every merge silently re-points it

Found 2026-11-07 by me while closing the reader-tool audit. Measured, not inferred.

## The mechanism

`scripts\permanent\disasm\symbols.py` line 241 builds every bible row as `Row(n, ...)` where `n` is
`enumerate(...read_text().splitlines(), 1)`. So a row's identity **is its line number in
`docs\RE-BIBLE.md`**. `whatis` prints that number, which is where our citations come from.

Every merge inserts rows. Every row inserted above a cited row moves that citation to a different fact,
with no error, no warning and no broken link. The file grew from **2068 lines to 2154 in two days**.

## The measurement

**Inside the bible itself**, 13 citations of the form "bible row N". I read each cited line today:

| Verdict | Count | Examples |
|---|---|---|
| Still names the fact it claims | 4 | row 468 (item table stride), row 1048 (camera pointer), row 803, row 1018 |
| Clearly names a different fact | 5 | row 930, row 933, row 814, row 708, row 1119 (cited twice) |
| Ambiguous without reading the whole cited fact | 4 | row 1220, row 105, row 119 |

Two worked examples, both read off the disk today:

- Bible line 1085 says "bible row 930's `push 31`". Line 930 today is the flag 127 world map record and
  contains no `push 31`. In the 2026-11-06 arena-v6 snapshot, line 930 is a flag 129 CLR byte scan, which
  also contains no `push 31`. The citation resolves in neither version.
- Bible lines 1303 and 1308 both cite "bible row 1119" for map 6,1's layout props. Line 1119 today is
  `ext 104 is Sprite_ReplaceWithEntry`, which is a different subject.

**Project wide**, 65 live citations (snapshots and `scripts\one-time\` excluded):

| Where | Count | Why it matters |
|---|---|---|
| `docs\RE-BIBLE.md` itself | 14 | the bible cannot cross-reference itself reliably |
| shipped code under `scripts\permanent\` | 12 | `battle_arena.py`, `ending_fight.py`, `trunks_tank.py`, `item_index.py`, `warp_graph.py`, `scene_lib.py`, `state_dump.py` and four tests carry row numbers in comments |
| task reports, briefs and `rows.md` files | 35 | every brief that tells an agent "see bible row N" |
| `docs\ledger\progress.md` | 4 | |

## Why this is expensive, not cosmetic

This is the documentation-layer version of the mistake the owner named: building what already exists.
An agent told "see bible row 930" reads an unrelated fact, concludes the bible does not hold the answer,
and re-derives it from the ROM. That is a whole pass spent re-proving a known fact, and nothing in the
process reports a failure. It also silently weakens our own code comments: a reader who checks the cited
row and finds the wrong subject learns to distrust the comment rather than the numbering.

I cannot say how many past passes this caused. I can say the citations do not resolve.

## Two fixes, with their real cost

**Option A, stable ids (the structural fix).** Give every row a short permanent id in the row itself,
assigned once and never reused. The merge tool assigns the next id. `whatis` prints the id instead of the
line number. Citations then survive any merge.
Cost: one scripted pass over all 2154 lines, a change to the merge tool and to `whatis`, and then
**re-resolving the 65 existing citations by hand**, because the broken ones no longer say what they meant.
A backup goes to `archive\backups\` first, per the file-restructure rule.

**Option B, content anchors (the cheap fix).** Stop citing numbers. Cite the fact's own anchor, normally
a ROM address, which `whatis` and grep already resolve. Change the convention, fix the 65 citations, edit
no bible row.
Cost: much lower, no bible rewrite. It fails for the rows that carry no address, such as "the VM has an
expression-getter family", which would still need a quoted phrase.

**My recommendation is A, with B's anchors used inside it**, because A is the only one that makes a
citation survive the next merge, and we merge rows most sessions. But A rewrites the bible, so it is your
call, not mine.

Either way the 65 citations must be re-resolved one by one. That is the irreducible cost and it exists
already, whichever option we pick.
