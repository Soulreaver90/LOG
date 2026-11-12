# Report: an address lookup tool

Written by the build agent, 2026-11-05. Saved by the controller: the harness refused the agent file
write, so the text was recovered verbatim from the session transcript and de-indented. Nothing was
reworded.

Controller note on finding 6.2: the conflict is now closed. I renamed our symbol `player_ptr` to
`Sprite_CurrentDirectory` in `scripts\permanent\disasm\symbols.py`, and `test_whatis.py` now fails if
the old name comes back.

---

# Report: the address lookup tool (`whatis.py`)

**The harness refused the write to `docs\tasks\2026-11-05-whatis-tool\report.md`** ("Subagents should return
findings as text, not write report files"). The brief says to return the full text in that case, so the
report is below. The code and tests ARE on disk and the suite ran against them.

---

## 1. What I built

| File | State |
|---|---|
| `C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\scripts\permanent\rom\whatis.py` | New, 583 lines. READ ONLY. |
| `...\scripts\permanent\tests\test_whatis.py` | New, 223 lines, 29 tests. |
| `...\scripts\permanent\log_paths.py` | Edited: added `GITHUB`, `DISASM_REPO`, `GNU_REPO`. |
| `...\docs\tool-index.md` | Regenerated with `make_tool_index.py`. Row 44 is `whatis.py`. |

I read `docs\tool-index.md` first. `disasm\listing.py --refs` already prints references to one address, so
`whatis.py` does not repeat it: `listing.py` owns the annotated listing and the BL callers, `whatis.py` owns
the written sources and the reference shapes. Bible rows come from `disasm\symbols.bible_rows()`, so the
project still has ONE bible parser.

```
py -3.14 -P scripts\permanent\rom\whatis.py 0x409368 --stride 56 --count 327
py -3.14 -P scripts\permanent\rom\whatis.py 0x03001FA8
py -3.14 -P scripts\permanent\rom\whatis.py set:56
py -3.14 -P scripts\permanent\rom\whatis.py combat --limit 0
```

Query forms: `rom:0x409368`, `0x08409368`, `0x0800A680`, `0x03001FA8`, `sub_`/`loc_` labels, a symbol name,
a bible tag (`set:56`, `flag:195`, `pal:88`, `char:gohan`), or free text.

## 2. Sources, each printed with its path so a claim can be traced

bible (`docs\RE-BIBLE.md`, with line number, section, tags, label, source doc), our symbol table
(`disasm\symbols.py`), `RAM_LEDGER.csv` with its behaviour test, `CODE_INDEX.md`, `FUNCTION_ENDS.csv` plus
`FUNCTION_BOUNDS.csv` for containment, the generated `.s` file, and `patches\*.py` plus `scene\scene_lib.py`.

A source with no hit prints "the search returned nothing" with its path and row count. A missing file prints
"could not read", which is a different fact. When nothing is found anywhere, the tool lists every path and
ends: "That is the state of our notes, not a statement that the thing does not exist."

## 3. The shapes

- **A**: aligned words equal to the address, equal to the Thumb pointer `address|1`, and equal to the bare
  file offset. Three counts, printed apart.
- **B**: every pc-relative load in the code region, walked FORWARD and dereferenced. Mask `hw >> 11 == 9`
  (`0x4800`-`0x4FFF`, any Rd), literal at `((A+4) & ~3) + imm*4`.
- **C**: words landing INSIDE the structure, with the entry index and offset for each hit, plus a separate
  count of words equal to the byte ONE PAST the end.

Two deliberate design points:

- **B does not start from A.** `listing.py --refs` finds the equal words first and then looks back for loads,
  so its B can never disagree with its A. Here B walks forward, so the two can disagree and be seen to.
- **B uses the full mask.** The 4th map table literal is loaded by `ldr r4,[pc,#0x84]`, halfword `0x4C21`. A
  literal `0x48xx` match misses exactly the case this tool exists for. A test plants a `0x4C04` site.

Shape C needs an extent, and the tool says where the extent came from: declared (`--stride`/`--count` or
`--span`, or a function's own body from `FUNCTION_ENDS.csv`) earns a **SHAPES DISAGREE** verdict; a guessed
`0x1000` prints **GUESSED** and says it is not yet a verdict; a RAM word with no extent skips shape C and
says so. I added that last rule after a guessed span reported 130 unrelated RAM globals for `0x03001FA8` and
shouted DISAGREE. A warning that fires on every query is a warning nobody reads.

## 4. Verification, five known-answer queries, real output

**4.1 `0x03001FA8`** PASS. 19 bible rows (246, 442, 444, ... 1491). `RAM_LEDGER.csv` row
`Sprite_CurrentDirectory [behaviour-test]`. Shape A 41 words, shape B 56 load sites, including
`ldr at rom:0xa6b8 (sub_0800a680+0x38)`, which is the guarded block bible line 1491 describes. Shape C not
run, and the verdict says "Shape C did not run, so nothing here rules out a word pointing INTO a structure".

**4.2 `0x0800A680`** PASS. 5 bible rows including line 1491, the guarded appearance block.

```
  0x0800a680 is the start of Character_SetActiveIndex, file Character_SetActiveIndex.s
    ...\legacyofgoku2-gnu\build\code\code_0800a680.s  (on disk under the address name;
     CODE_INDEX names Character_SetActiveIndex.s)
  contained by Character_SetActiveIndex 0x0800a680-0x0800a70c (thumb), +0x0 in, role start
  shape A (aligned words equal to 0x0800a680): 0
  shape A (words equal to the Thumb pointer 0x0800a681): 1
    rom:0x3b5ef4  data
  shape B: 0 site(s)
```

The shape A split earned its place: the plain address appears ZERO times. A sweep for it alone would report
no references at all for a function the game calls.

**4.3 `combat`** PASS. 234 bible rows. Required rows present: line 1074 (map 7,1, "combat +8 = 1"), line 1076
(computer room map 6,6), and 5 rows with the `ARN` source. The default `--limit 12` shows the first 12 in
bible line order and prints the full count; `--limit 0` shows all. Nothing is truncated silently.

**4.4 `0x409368 --stride 56 --count 327`** PASS, and this is the case the tool exists for.

```
  shape A (aligned words equal to 0x08409368): 3
    rom:0x5adc   rom:0x5d5c   rom:0xebd8      (all code region)
  shape A (words equal to the Thumb pointer 0x08409369): 0
  shape B (pc-relative loads in rom:0x0-rom:0x28724): 7 site(s)
    ldr at rom:0x18d6 (sub_080018d6+0x0)   reads rom:0x195c = 0x08409410
    ldr at rom:0x5778 (sub_08005724+0x54)  reads rom:0x5adc = 0x08409368
    ldr at rom:0x598c (sub_08005926+0x66)  reads rom:0x5adc = 0x08409368
    ldr at rom:0x5a6e (sub_080059f8+0x76)  reads rom:0x5adc = 0x08409368
    ldr at rom:0x5c18 (sub_08005b50+0xc8)  reads rom:0x5d5c = 0x08409368
    ldr at rom:0xe178 (sub_0800e160+0x18)  reads rom:0xe1d0 = 0x0840daf0
    ldr at rom:0xeb8a (Table_FindByPair+0xe) reads rom:0xebd8 = 0x08409368
  shape C (words landing INSIDE 0x08409368-0x0840daf0): 52, 1 in the code region
    rom:0x195c holds 0x08409410 = base +0xa8 (entry 3, +0x0)
    51 further word(s) in the data region
  shape C, one past the end (words equal to 0x0840daf0): 1  rom:0xe1d0

SHAPES DISAGREE: shape C found 1 code-region word(s) that shape A cannot see, because they point
INTO the span, not at 0x08409368.
  rom:0x195c holds 0x08409410 = base +0xa8 (entry 3, +0x0)
  Treat this as the finding. A scan for the base address alone would have reported 3 references, not 4.
NOTE: 1 word(s) hold 0x0840daf0, one past the end. A loop bound or the next structure's base.
```

Every address matches the `ARN` row (bible line 1172) exactly.

**4.5 `0x3B8140`** PASS. 5 bible rows (66, 1040, 1041, 1042, 1484). Shape A finds exactly
`rom:0x3c4e94` and `rom:0x3dd040`, the pointer words of the two type 5 records at `rom:0x3C4E90` and
`rom:0x3DD03C`. Shape B 0, which is right for a table reached through a record.

**4.6 A query with no answer** PASS. `zzznotathing` prints "the search returned nothing" per source, then
lists all seven source paths, then: "That is the state of our notes, not a statement that the thing does
not exist."

## 5. The suite

Final run, exit code written into the output file by the command itself, never read from a pipe:

```
Ran 1271 tests in 428.625s
OK
SUITE EXIT=0
```

`test_whatis.py` alone: 29 tests, exit 0. No failures or errors anywhere in the suite.

## 6. What the tool revealed

The headline is the premise of the brief, confirmed: **three things I was about to write up as new findings
were already in the bible, and `whatis.py` found each in about a second.** `rom:0xE1D0` and the one-past-the-end
pointer is bible line 1174 (`ARN`). `rom:0x3B5EF4` as ext 115's table word is bible line 588 (`FCD`). The
`0x0800A680` guarded block is line 1491 (`ESS`). Re-derivation is the failure this tool prevents, and it
prevented it on me during this task.

Genuine observations, stated hedged. I did NOT touch `docs\RE-BIBLE.md`. Rows are in bible shape for you to
merge or reject.

**6.1 The `ARN` row's count sentence is off by one (LIKELY, prose only; the row's claim is CONFIRMED).**
Bible line 1172 ends "52 more words land inside the table, all in art and audio data, and no LDR names any
of them". Measured: 3 words equal the base, 52 land strictly inside, of which 1 is `rom:0x195C` in the code
region and 51 are data, and 1 more word equals the exclusive end. Under the strict reading the 52 INCLUDES
`rom:0x195C`, which an LDR does name, so "52 more" and "no LDR names any of them" overlap by one word; the
data-only figure is 51. An inclusive end gives 53, of which two are LDR-named code literals, so that reading
does not resolve it either. I label this LIKELY an off-by-one in the prose, not CONFIRMED, because I cannot
see which range the original scan used. The row's headline, that there are FOUR literals and a base-only
scan cannot see the fourth, is CONFIRMED in full.

```
| Words naming the map table `rom:0x409368` (56 x 327) by three shapes: 3 equal the base (`rom:0x5ADC`, `0x5D5C`, `0xEBD8`), 52 land strictly inside of which `rom:0x195C` is the one code-region literal and 51 are data words in art and audio, and 1 (`rom:0xE1D0`) equals the first byte past the end. 7 LDR sites in all | #map #tool | C (whatis.py, three shapes) | WIS |
```

**6.2 `0x03001FA8` carries two names, and 61 of our symbols now read differently in the disassembly repo.**
Ours is `player_ptr`; `RAM_LEDGER.csv` says `Sprite_CurrentDirectory`, backed by a behaviour test. I am not
adjudicating. I first made this a NAME CONFLICT alarm, then measured: 61 of our `symbols.py` entries already
carry a different PascalCase name in `CODE_INDEX.md`, so an alarm would fire 61 times. The tool now prints a
neutral "also named X (source)" line instead. Per the LOG rule, the handler decides, not a label.

```
| `0x03001FA8` carries two names: `player_ptr` (our `disasm\symbols.py`) and `Sprite_CurrentDirectory` (`RAM_LEDGER.csv`, behaviour-test). 61 of our symbols also read under a different name in `CODE_INDEX.md`. Open the handler before using either name | #object #tool #open | C (both files) | WIS |
```

**6.3 `CODE_INDEX.md` and the generated tree disagree, observed while the `naming` agent was working.**
251 of the 1249 index rows name a `.s` file that is not on disk. 95 of those exist under the emitter's
address name, so the tool now tries `code_<addr>.s` as a second shape and reports "on disk under the address
name". 156 rows name no file on disk under either name. I report this as a live state during another agent's
run, not as a defect, and I changed nothing in either repo.

**6.4 `set_leader` cannot be found by a literal sweep.** No aligned word equals `0x0800A680`, and no Thumb
pc-relative load in `rom:0x0`-`rom:0x28724` names it. Its only stored pointer is the Thumb word
`0x0800A681` at `rom:0x3B5EF4`, which is `script_ext_ops` (`rom:0x3B5D28`) `+0x1CC`, slot 115. This is the
ROM-level proof of bible lines 588 and 678. Anyone sweeping for its callers must use BL. IWRAM ARM code and
unaligned words were not scanned.

## 7. Limits the tool prints about itself

- A module that computes an address (`MAP_TABLE + 3 * 56`) cannot appear in a static text search. Printed
  under every module block.
- A BL caller is a fourth shape `whatis.py` does not run. It points at `disasm\listing.py`.
- Shape B scans `rom:0x0`-`rom:0x28724`, the code region from the committed `codemap.json`, with the same
  value as a fallback constant if that file cannot be read.
- `FUNCTION_ENDS.csv` has a recorded end for 1409 of the 3431 `FUNCTION_BOUNDS.csv` rows, so containment also
  uses two shapes: the recorded end, then the nearest start above, marked "end not recorded". A fragment row
  resolves to the parent its evidence names.
- The bible search reads the bare file-offset form too, so a row using the same value as a count or a size
  can match. The tool says to read the row, not count it.
- Coverage is the seven sources in section 2. A fact written only in a one-time script's `.txt`, or in a task
  report the bible never indexed, would not appear.

## 8. Process notes

- No `cd` in the final commands, absolute paths throughout, `py -3.14 -P` everywhere.
- No Windows path inside any `python -c` argument. All four touched files checked after writing: no BOM, no
  control bytes, no em dash, no en dash.
- Nothing written under `data\`. Nothing written to `RE-BIBLE.md`. The tool has a test that fails if
  `write_text`, `write_bytes`, `mkdir` or `unlink` ever appears in its source.
- One mid-task collision: the `naming` agent renamed `sub_0800a680` in `CODE_INDEX.md` while my tests ran,
  which broke a test of mine that hardcoded the old name. I made my tests rename-proof rather than editing
  anything in that repo.
