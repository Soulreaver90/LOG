# Portrait id block: the reader census

Measured 2026-11-14 on the base USA ROM and the byte exact disassembly. No ROM was written.

The queue calls this block "the real prereq, not the scouter" and says it gates Trunks Z+ and
Piccolo Z+, because "portrait id 121 is the LAST free dialog id".

> [!CAUTION]
> **That row is STALE and the premise is wrong twice.** Id 121 was never free: `npc_gi.py:36` has
> held it since r16 as a copy of word 59, the armor frame. And the block has since grown TWICE more
> on its own. Read out of the shipped `log2_poc_r44_rough.gba`, the live block is at `0x08953B90`
> and holds **ids 0-123**: 122 is `vegeta_zplus`, 123 is `piccolo_zplus`, and 124 is not a pointer.
> Both new slots land exactly on `0xF00000 + 0x1008 * id`, the `art_inject` scheme of B0355.
>
> So the grow is not a prereq for anything. It is a solved, twice-proven, one-word-per-module edit.
> **Trunks Z+ is blocked on HIS DRAWING ALONE.** Id 124 is free and the pattern is proven.
>
> The census below still stands as the reader census, and answers why the grow is this cheap.

> [!IMPORTANT]
> **The bible already held this answer, and I re-derived it. My search shape was wrong.**
> The FIRST row of section 5a says: "`portrait(id)` `@0x0800BDCC` ... id > 7 the word at
> `@0x083EC9D4` + 4 x id; **no upper bound** (`cmp r0,#7 ; bgt` only)". I grepped the bible for
> `portrait` near `block|0xBE10|121|114|dialog`, and that row carries none of those, so it never
> surfaced. Finding it first would have made this census ten minutes instead of forty.
>
> What this page adds that the bible did NOT hold: the verified live block state in a BUILD, the
> codemap hole, the two false positives ruled out by reading them, and the B0324 nearby-base gap.
> The rest is independent confirmation, which is worth something but was not the plan.

## The answer: vanilla puts NO upper bound on a portrait id

`Scene_GetEntry` (`0x0800BDCC`, `Scene_GetEntry.s`) is the only reader of the block. Read end to end:

| id | path | what it does |
|---|---|---|
| 0 | returns at once | nothing |
| 1 | `loc_0800BDE0` | indexes through block word 0, calls `Scene_SelectCode` |
| 2 to 7 | `CMP r0,#0x7 ; BGT` falls through | `(id-2)*28` through block word 0, calls `Scene_SelectCode` |
| **8 and up** | `loc_0800BE06` | `LDR r1,[pc,#0x8]` (the block base) `; LSL r0,r0,#2 ; ADD r1,#4 ; LDR r0,[r1,r0]` |

**The id > 7 path is a raw indexed load with no clamp.** `block[4 + id*4]`, straight out.
`Scene_SelectCode` (`0x08026440`), which feeds it, reads the appearance entry's `+0x2` byte and
passes it through with no check either.

So growing the block needs no bound raised anywhere. That is the whole difference from the scouter
menu, where the hardcoded 128 cap was the job.

## Shapes run, and what each one cannot see

| Shape | What it covered | Result |
|---|---|---|
| A, `CMP rX,#imm8` across every `code_0800b*.s` | 61 immediates in the dialog and portrait family | **no portrait bound** |
| B, value scan for `0x083EC9D0` across all 1476 generated files | every literal pool in the image | **exactly one**, `pool_0800be10.s` |
| C, read the only reader end to end | `Scene_GetEntry` and `Scene_SelectCode` | **no clamp on either** |
| D, read the live block out of a BUILD | `log2_poc_r44_rough.gba` through `0xBE10` | ids 0-123, no collision |

Shape B independently confirms bible B0324, which reached the same count by scanning ROM words.

**What none of these can see:** a bound built by `mov`+`lsl` rather than a `CMP` immediate, a bound
compared against a count held in a register, and anything outside the ranges named above. Shape A is
the adjacent-immediate shape that under-counted the scouter by five sites, so it is a FLOOR here too.
The claim is "no bound reachable by shapes A, B and C", not "no bound exists".

> [!WARNING]
> **Shape B cannot see a NEARBY-BASE reader, and bible B0324 says three exist.** B0324 names readers
> at `@0x0800BBB4`, `@0x0800B86E` and `@0x0800BDB8` that "use nearby base addresses", and says
> "index >= 5 at `0x0800BBB4` reaches the block". Their bases are in the pools I printed:
> `0x083EC9A0` in `pool_0800bd90.s` and `0x083EC9B0` in `pool_0800ba70.s`, which are the block base
> minus `0x30` and minus `0x20`. Shape B searched for `0x083EC9D0` EXACTLY, so by construction it
> could not have found either. That is the very trap this section warns about, hit inside this page.
>
> **Open, and not traced here:** what indexes those three. Since `npc_gi` RELOCATED the block, a
> nearby-base reader still points into the ORIGINAL `rom:0x3EC9A0` region, which is untouched vanilla
> data. If any of them indexes far enough to reach a portrait id, it has been reading the stale
> vanilla block since r16. Every build since has shipped and played, which is evidence but not proof.
> Trace them before anyone edits that region. This is a bible-correctness item, not a blocker,
> because the grow needs no edit there.

**Still to read, and it is the one that matters now:** our own hook. After `cutscene_portraits`,
`rom:0x0800BE06`-`0x0800BE0F` is replaced by `ldr r1,=hook ; bx r1` plus the hook word (bible B0500),
so OUR hook at `rom:0x894E74` does the block read in every build. A bound in our code would not
appear in any vanilla shape above.

## Two false positives I ruled out by reading them

- **`CMP r0,#0x7E` at `code_0800b9d6.s:39` is not an id bound.** `[r4,#0x44]` steps by 2 between
  `0x22` and `0x7E` under two bits of the halfword at `[r6+0]+0x12`. That is a settings slider driven
  by input, not a portrait index. 126 sitting just above our 121 is what makes it look convincing.
- **`CMP r3,#0x5E` at `code_0800ba84.s:17` is not an id bound.** `0x5E` is `^`, the caption prefix
  the bible already records. The function counts 8 frames at `+0x30` and advances the text pointer at
  `+0x10`. It is the typewriter.

## The structural finding: the portrait family sits in a codemap hole, same as the scouter

`docs\CODE_INDEX.md` has no function row between `sub_0800bab4` (`0x0800bab4`) and `Scene_GetEntry`
(`0x0800bdcc`). That is a 792 byte hole, and the bible's portrait readers `@0x0800BB3E`,
`@0x0800BBB4`, `@0x0800BDB8` and `@0x0800BDF0` all fall inside it.

This is the SECOND family found in such a hole in two days. The scouter menu sits in a 2.4 KB one
between `sub_080191ca` and `Scene_New`. A census built from named functions returns almost nothing in
either place, and says nothing while it does. Build a census from an address range, never from the
function list.

One more hole seen while looking: `0x08018CE4`, the menu consumer bible row B0488 names, is not the
start of any indexed function either, and `code_08018c40.s` is only 26 lines, so it does not reach it.
