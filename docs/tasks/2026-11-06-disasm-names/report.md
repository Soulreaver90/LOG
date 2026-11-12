# Disassembly naming, 2026-11-06

> **Controller note.** The agent could not write this file: this harness refuses a report `.md` from a
> subagent, so I saved its report below from the hand-back. Its machine readable output DID land as
> `tally.csv` beside this file, 1038 data rows.
>
> **What I verified myself, before relaying any of it:**
>
> | Claim | Check | Result |
> |---|---|---|
> | Commit `85096b1` on `naming-2026-11-05`, nothing pushed | `git log`, `git status` | CONFIRMED, tree clean, `master` still `075b23c` |
> | Baseline 1037, 212 names, 212 ledger rows | the three files | CONFIRMED, all three agree |
> | The one name and its evidence cell | `names.csv`, `NAMING_LEDGER.csv` | CONFIRMED |
> | The three withdrawn names are gone | grep of `names.csv` | CONFIRMED, 0 hits each |
> | `0x08022008` is a `dispatch` row | `FUNCTION_BOUNDS.csv:3065` | CONFIRMED, exactly `0x08022008,dispatch,runtime` |
> | 930 dispatch rows | count | CONFIRMED, exactly 930 |
> | README carries 1,037 | `README.md:42` | CONFIRMED |
> | `tally.csv` has 1038 rows | count | CONFIRMED |
> | `py -3.14` has no pytest | import | CONFIRMED, `py -3.15` has pytest 9.2.0 |
>
> **One agent claim I must correct.** The agent says `py -3.14` is needed and reports only the pytest
> gap. I checked Pillow too: `py -3.14` has Pillow 12.3.0 and **`py -3.15` has Pillow 13.0.0**. So
> `CLAUDE.md`'s reason for pinning 3.14, "py -3 is 3.15 with no Pillow", is no longer true. I did not
> change the pin, because I cannot prove what the right reason is now. It is a question for the owner.

Repo `GitHub\legacyofgoku2-disasm`, branch `naming-2026-11-05`. **Nothing was pushed.**

**Headline: the tally is the deliverable. Only 1 of the 52 device candidates survived scrutiny.**
Three the agent had already written, verified and committed were demoted after a review round found
their start addresses were wrong. That demotion is the honest result and it reinforces the tally's
main conclusion.

---

## 1. The tally of the 1038 address-named starts

Population: the 1249 rows of `tools\code\FUNCTION_BOUNDS.csv` with role `start` or `unreferenced`,
less the 211 named. That is exactly the set `NAMING-address-ratchet` counts. **The buckets sum to
1038 exactly.** Figures describe the tree before the commit; 1037 remain after it.

Each start is in exactly one bucket, assigned by the seeded run `NAMING.md` records: zeroed workspace
at `0x02000000`, `r0` at that base, `r1` to `r7` at `0x40` byte steps, through `tools\code\thumb_vm.py`.

| primary bucket | count | share | meaning |
| --- | --- | --- | --- |
| runs-under-the-seed | 520 | 50.1 % | the run reaches the return; a behaviour test can assert effects today |
| image-pointer | 322 | 31.0 % | `0x...+1 is outside the image and the writable space` |
| tail-branch | 173 | 16.7 % | `the run left the body at ...` |
| step-budget | 10 | 1.0 % | passes the 0x1000 step budget, normally a long loop |
| arm-switch | 6 | 0.6 % | the body switches to ARM |
| bios-call | 4 | 0.4 % | the body issues a SWI |
| arm-mode | 3 | 0.3 % | the start itself is ARM |
| **total** | **1038** | | |

CONFIRMED by measurement; every row is in `tally.csv`.

### Overlap columns (not buckets, may double count)

| overlap | count |
| --- | --- |
| touches a hardware register | 52, which matches the pool the controller handed it exactly, an independent cross-check |
| one callee and body 12 instructions or fewer | 118 |
| no census row, emitter writes nothing there | 51 |
| writes a register and calls nothing | 14 |
| issues a BIOS call | 5 |

### What this says about tooling

1. **Half the remainder already runs** (520). The lever is a batch harness that records a seeded run's
   effects and asserts them, not 520 hand tests. LIKELY the largest win. Caveat: the 520 still include
   judgment refusals (`seed-not-separating`, `effect-without-a-module`) and some mis-bounded tails, so
   520 is an upper bound on what is mechanically nameable.
2. **The 322 image-pointer refusals are only partly a seed problem.** SPECULATIVE, downgraded on
   review: `NAMING.md`'s own image-pointer rows fault on pointers read from FIXED addresses
   (`0x081D9094`, `0x083B5268`, `0x0840DAF4`), which an argument seed cannot fix. How many of the 322
   are argument driven against fixed address is not measured.
3. **`seed-not-separating` and `effect-without-a-module` are deliberately absent** from the table.
   Both are judgments made AFTER a run succeeds, so they are a subset of the 520. This sweep does not
   measure them and the agent did not extrapolate.

## 2. Corrected finding: 68 starts are mis-bounded tails

68 of the 1038 pop `pc` with no `PUSH` that saves `lr` anywhere in the body, so they are tails of
earlier functions and their arguments do not arrive at that address.

**The agent first reported 134; that was wrong.** Its first test required `PUSH` to be the FIRST
instruction, which miscounted bodies that load a literal before pushing. Corrected figure is 68.
CONFIRMED.

It also claimed these were "most of the 173 tail-branch bucket". **That claim was false.** The cross
tab against `tally.csv`:

| bucket | tail-entry in it | bucket size |
| --- | --- | --- |
| runs-under-the-seed | 51 | 520 |
| image-pointer | 16 | 322 |
| step-budget | 1 | 10 |
| tail-branch | **0** | 173 |

The two classes are disjoint. The tail entry starts RUN under the seed and return normally, which is
worse: they produce a clean, nameable looking result for a function that does not begin there.

## 3. Population finding: the census covers 1198 starts, not 1249

`device_access.census` intersects census starts with emitted addresses, so **51 of the 1038 have no
census row** and the research tools built on it cannot see them. The agent ran the seeded run on all
51 directly, which is why the buckets still total 1038. Any future sweep built on that census alone
will silently miss them. CONFIRMED.

## 4. The 0x08022008 census question

It is a **fourth** state, not one of the three the controller listed, and the repo already has a class
for it.

```
tools\code\FUNCTION_BOUNDS.csv:3065
0x08022008,dispatch,runtime
```

Source of that row:

```
tools\recomp\RUNTIME_LABELS.csv:836   rom,0x08022008,thumb
tools\recomp\RUNTIME_LABELS.csv:837   rom,0x0802200c,arm
```

Not absent, not a fragment, not `unreferenced`: one of the 930 `dispatch` rows. `NAMING.md` says a
dispatch row is "named by neither a function name nor the address form", so the block is that clause,
not a missing row. **The ledger is correct and nothing needs closing.** CONFIRMED. Note
`tools\code\RUNTIME_LABELS.csv` has only 94 rows and does not contain it; the dispatch set comes from
the RECOMP copy.

The real gap underneath: bytes at `0x08022008` are `47 78` = `BX pc`, then `00 00`, then ARM at
`0x0802200C`, the ADS veneer that makes an ARM member Thumb callable, hence the `__16_` prefix. None
of the four limbs can reach it: `BX pc` saves no `lr` so it is no prologue, no emitted `bl` reaches
it, it is no vector and no table word. `library_match.py` proves the start from 196 matched bytes
anyway. **LIKELY finding: a byte exact library match is start evidence the split's limb rules
structurally cannot produce.** Closing it needs a census change plus the gate, so the agent left it
alone.

## 5. The one name

| address | name | class | evidence (ledger cell) |
| --- | --- | --- | --- |
| `0x0800da96` | `Palette_LoadScaled` | device-register | scales 0x200 colours from the record at +0x4 by r1/0x100 on each 5 bit channel into a stack buffer, then runs two DMA3 transfers with count (0x040000DC)=0x100 and CNT_H (0x040000DE)=0x8000 from SAD (0x040000D4) to DAD (0x040000D8) 0x05000000 and 0x05000200 |

CONFIRMED. The unpack of three 5 bit channels, multiply by `r1`, shift by 8 and repack are explicit in
the body. The destinations and the fixed count `0x100` with CNT_H `0x8000` exactly mirror
`Palette_Save` at `0x0800DA68`, which the ledger already names `device-register` for the same pair in
the other direction. Its start is sound: the previous function returns at `0x0800DA94` (`BX lr`), this
one opens `PUSH {r4-r7}` and closes with the matching `POP` plus `BX lr`. Role is
`unreferenced,block`, which `NAMING.md` explicitly permits a name on.

### Three demotions, with the proving bytes

These three were committed, then withdrawn when a review round asked the agent to check the start
addresses. Its own checks (`--ledger`, lints) **cannot** see this class of error, because neither
looks at where a function begins.

- **`0x08002902`, withdrawn. Not a function start.** `xxd -s 0x2900 -l 8` gives `ff22 1932` =
  `MOV r2,#0xFF` then `ADD r2,#0x19`. The body it named begins at the second instruction, so `r2` is
  0x118 only when entry is at `0x08002900`. The census carries `0x08002900,dispatch,runtime`, so the
  runtime entered there. A table word at `0x08074D34` does hold `0x08002903`, so there may be two
  entry points with different `r2` contracts. Ambiguous, so no name.
- **`0x0801F494`, withdrawn. Not code.** `Dma3_HalfwordFill` at `0x0801F43C` loads its pool word FROM
  `0x0801F494`, and `Dma3_WordFill` loads from `0x0801F498`. The two words are `0x03003910` and
  `0x03003914`, the DMA fill scratch. The split decoded literal pool data as instructions, which is
  exactly why the first four "instructions" read as dead code. Real code starts at `0x0801F49C`, which
  has no start row, so the name cannot move there either. **This is a census defect worth its own look.**
- **`0x08011F88`, withdrawn on class, not on start.** Its role is `start,table+block` and its entry
  pointer `0x08011F89` appears word aligned at `0x08012380`, so the start is the best proven of the
  four. It reads VCOUNT (`0x04000006`) and copies four words into the BG2 affine block at `0x04000020`
  with stride `0x10`. But it writes **no fixed constant**, and every device-register precedent does
  (`Dma3_StartCopy` writes CNT_H `0x8400`; `Dma3_CopyAndWait` writes the `0x80000000` bit). So the
  class does not admit it. **This is the single best behaviour-test candidate in the pool**: proved
  start, fully readable effect, and `thumb_vm`'s memory map covers `0x04000006` so it can be seeded.

### Why not more of the 52

- 4 already carry a measured refusal in `NAMING.md`: `0x08002FF8`, `0x08006C24`, `0x080143A8`,
  `0x08020D40`.
- 34 also call `Container_Decode`, `Tilemap_FillRect`, `Text_DrawLine` or similar; the `0x08006C24`
  precedent puts that many separate effects in `effect-without-a-module`.
- Of the 14 that write a register and call nothing: 5 are mis-bounded tails (`0x080105E8`,
  `0x08018010`, `0x08018038`, `0x080120c8`, plus `0x0801F494` which proved to be pool data), 3 are 43
  to 109 instruction blit loops judged **effect-without-a-module** (`0x0801278A`, `0x0801C4FA`,
  `0x080054A4`, correcting an earlier wrong reason of its own: `0x0801278A` and `0x0801C4FA` DO write
  a fixed CNT_H of `0x8400` via `0x21<<0xA`), 1 is `0x08020D40` already refused, 1 is `0x08018082`
  which it did NOT examine and leaves unmeasured, and 3 are the demotions above. That leaves 1.
- **The callee-role pool looked bigger and is not.** 185 starts have 5 instructions or fewer, but only
  13 hold a `bl`; most of those are mis-bounded tails or forward to an unnamed callee. A pure
  forwarder to a named callee carries no information beyond the callee's own name, so any
  distinguishing name would claim more than the bytes show. All 13 refused.

## 6. Checks and real exit codes

| check | exit |
| --- | --- |
| `device_access.py --ledger` before | 0, 211 rows, 0 failed |
| `device_access.py --ledger` after | 0, **212 rows, 0 failed**, one new PASS line for `0x0800da96` with all six quoted tokens verified present |
| `tools\lint\lints.py` before | 0, LINT PASS, 0 findings over 83 files |
| `tools\lint\lints.py` after | 0, LINT PASS, 0 findings; INDEX PASS; ratchet accepts 1037 |
| `code_index.py --write` | 0 |
| `pytest -q tools\code tools\research` | 1, **8 failed, 169 passed, 1 skipped** |

**The 8 failures pre-date the work.** The agent proved it rather than assumed it: it stashed its
changes, re-ran those three test files at HEAD and got the identical 8 failures (`8 failed, 17
passed`), then restored and verified the files were byte identical by md5. They are in
`tools/research` only (`test_callers`, `test_data_census`, `test_runtime_watch_results`) and pin image
derived counts, for example `assert found[0x0801FC9C] == 50` fails with `55 == 50` while called with
an empty names dict, so `names.csv` cannot be the cause.

**Counts, exact and consistent at the commit:** baseline `1037`; README line 42 "1,037 of the 1,249";
`CODE_INDEX.md` "212 carry a name and 1037", regenerated by `code_index.py --write` and never hand
edited; `names.csv` and `NAMING_LEDGER.csv` 212 data rows each.

**Commit `85096b1`** "Name the scaled palette loader", the only commit beyond `007ab18`. Tree clean.
The commit body states plainly that the gate was not run and why. Diff is 6 insertions and 4 deletions
across 5 files, additions only in the two CSVs.

### The gate was not run, and what it would still have to prove

`gate.py`, `rebuild.cmd`, `check.cmd`, `armasm`, `armlink` and `fromelf` were all left alone, because
the only ARM Developer Suite on this machine sits in the owner's Downloads folder and whether it may
be executed is his open decision. Naming needed none of it.

The gate would have to prove the renamed label assembles and links to the same bytes, so the image
still matches at 8,388,608 of 8,388,608. Risk is low but not zero: a name is emitted verbatim into the
link, so a collision with an existing symbol or an equate in `asm\registers.s` or `asm\memory.s`
breaks the link. The agent verified `Palette_LoadScaled` is absent from `names.csv`, and
`NAMING-symbol` checks the same, but only the link proves it. No files under `build/` are tracked, so
no stale emitted file is left behind.

## 7. Two process findings worth carrying forward

1. **`py -3.14` has no pytest on this machine.** `lints.py` and `code_index.py` cannot even be
   imported under it, because both pull in `tools\testkit.py` which imports pytest at module scope.
   `py -3.15` has pytest 9.2.0. Every check above ran under `py -3.15 -P`, not the `py -3.14 -P` the
   brief names. The research tools run under either. **Controller addition: `py -3.15` also has
   Pillow 13.0.0, so `CLAUDE.md`'s stated reason for the 3.14 pin is stale.**
2. **`--ledger` is weaker than it looks.** It only matches 8 hex digit tokens against addresses the
   body touches. It never checks a CONSTANT, and it silently skips any row without exactly 5 cells, so
   an unquoted comma in an evidence cell passes unchecked. Neither it nor the lints check **where a
   function starts**, which is precisely how three wrong names passed every check the agent had.

## Recommendation

The owner's rate problem is not solved by naming harder. **The census boundaries are the lever.** 68
measured mis-bounded tails, a literal pool decoded as a function at `0x0801F494`, a start two bytes
inside its own function at `0x08002902`, and 51 starts invisible to the research census all point the
same way. Fixing `function_bounds.py` would convert starts in batches and would stop the false
positives that cost three names today. That work needs the byte exact gate, so it needs the owner's
decision on the ARM Developer Suite first.
