# 2026-11-07: closing the gaps the night survey left open

The night survey found four wrong ops and a walker that read half of every long scene table. It did not
fix them, because an agent held the files. This is the fix, plus one regression the fix introduced and
the check that caught it.

---

## What changed

| Change | File | Why |
|---|---|---|
| `ext 23` takes two arguments, not one | `scene\scene_lib.py` | the handler pops twice, and `chapter_cards` already emitted two |
| `ext 131`, `132`, `133` take none and push a byte | `scene\scene_lib.py` | they are getters: the handlers raise the stack depth |
| `table_length()` added, `table_end()` marked a floor | `scene\scene_lib.py` | the first-END rule truncated 229 of 303 tables |
| `is_record_pointer()` accepts the expansion area | `scene\scene_lib.py` | a build moves records there, and the walk stopped at the first one |
| The census and `run_table` walk the full table | `tests\test_battle_start.py`, `scene\scene_harness.py` | they pinned a truncated population |
| A null table pointer is reported, never walked | `scene\op_usage.py` | map 6,3 names one, and silence is the wrong answer |
| New `test_ext_ops.py`, 10 tests | `tests\` | the op table can never drift from the handlers again |

33 bible rows from the night survey are merged, with 6 more from this work.

---

## The regression this stretch nearly shipped

The first `table_length()` accepted only the vanilla script region `0x3B0000`-`0x420000`. Every patched
record lives in the expansion area instead, so the walker stopped at the first one.

Measured on `log2_poc_r41_arena_v7`, table `rom:0x3DE6F4`: 32 words read, 36 real. The old `table_end()`
read it correctly. The fix would have made our own builds HARDER to read than vanilla, silently.

> The base ROM could not show this. A walker has to be measured on a build, because a build is the
> only ROM with records outside the vanilla regions.

---

## What the wider walk found

**Our own module tables were the worst victims.** `celljr_fight` copies table `rom:0x3EA400` into
expansion at `rom:0x93AE74`. That copy's first END entry sits at index **2** of 33 words, so the census
checked 2 of 33 and never read 31 records of our own code.

The vanilla bar-record census rose from **22 to 31**, and the claim held over all 31: not one opens a
scene. More records made the rule stronger.

> Two counts in this page measure different things. **31** is the live BUILD's bar records that no
> module owns, which is what the suite pins. **34 of 35** is every bar record in the base ROM. They
> are not a contradiction.

**The over-run question, and my first check was the wrong one.** I asked whether a table's span reaches another TABLE's start. None does. But vanilla puts a scene's records just BEFORE its table,
so the bytes after a table are the next scene's RECORDS, and a record header below `0x10000` reads
exactly like an END entry. Measured properly: **150 of the 302 tables over-read, always by one word,
always the last word of the walk, and in all 150 that word is a record header reading as an END
entry.** Every walker skips END entries, so the census is unchanged at 5,304 sites and 102 ops: only
the length was wrong. `S.table_length(rom, at, records=...)` is now exact, and the hand-decoded
Piccolo table `rom:0x3E47F8` is the proof, at 8 words loose-9 exact-8.

---

## Corrections to what you may have read

- The fight-start figure is **34 of 35**, not 26 of 27. The truncated walk produced the smaller pair.
  Fixed in the bible, the retrospective and the night report.
- `ext 131`-`133` keep the names `gain_str`, `gain_pow` and `gain_end`. The handlers read
  `0x03001FC1`-`0x03001FC3`, which bible row 1904 already names as the level-up stat gains. The names
  were right; only the arity was wrong.
- The research pages now say **302** tables reached plus 1 unreadable pointer, where they said 303.

---

## Suite

Full run after the op fixes: `Ran 1395 tests`, one failure, the known RED
`test_form_survives_the_leader_change` with its single `fullpower_ssj` finding at `rom:0x89A9C0`. That
one is yours to decide and is untouched by this work.

---

## Two more found while auditing the reader tools

**`item_index.py` had no `out_name()` guard.** The other four index tools got one on 2026-11-06 and this
one was missed, so my own `--rom` audit run wrote the v7 build's items over the vanilla reference page.
Caught by the file timestamp, not by any test. Fixed, and the vanilla page is regenerated.

**`symbols.json` is generated and had to be re-run.** Renaming three symbols in `disasm\symbols.py` left
the exported JSON stale, and `test_re_tools` caught it. Regenerated with
`py -3.14 -I scripts\permanent\disasm\symbols.py json`, 315 symbols.

**What the audit actually covered.** I ran four page generators against the v7 build and checked each
wrote its own suffixed file: `map_index`, `warp_graph`, `scene_index` and `op_usage`. `item_index` is
the fifth and it is the one that was broken. `item_index` hardcodes the item table at `rom:0x6ADE24`
and the string table at `rom:0x0E2840`, and I checked those by hand rather than assuming: both
literals appear at the same addresses in the base ROM and in v7, 5 of one and 20 of the other, so no
patch moves either today. Nothing pins that, and a test should.

**Not covered.** `map_view` and `scene_probe` take `--rom` and were not re-run this stretch; the map
table fix of 2026-11-06 is what they rest on. `whatis.py`, `codemap.py` and `listing.py` also take
`--rom` and were not looked at at all. So the tool audit is narrowed, not finished.
