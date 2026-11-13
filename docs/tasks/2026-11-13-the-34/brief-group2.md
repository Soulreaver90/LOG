# Brief: group 2 of the 34, the typed addresses

Read `docs\tasks\2026-11-13-the-34\triage.md` first. You own **group 2 only**, the 14 rows in its
group 2 table. Four files:

- `test_fullpower_hud.py` (6 rows)
- `test_roundtrip.py` (5 rows)
- `test_vegeta_zplus.py` (2 rows)
- `test_piccolo_z_start.py` (1 row: `test_the_patch_writes_four_runs_and_none_of_them_is_save_code`)

## Do not touch

- `test_piccolo_z_start.test_the_base_and_non_pool_forms_still_get_nothing`. It fails with
  `50346496 != 0`, which is `0x3003A00`, an IWRAM pointer. That is a real behaviour question and
  the controller owns it.
- The group 1 row in `test_fullpower_hud` is already converted. Leave it.
- Any other file. Groups 3 and 4 belong to other passes.

## EXCEPTIONS FIRST: addresses that are RIGHT to type

Read this before you change a single number. "Fixing" one of these creates a defect.

1. **Vanilla ROM addresses.** The free region the allocator hands out is file offset `0x800000` to
   `0xF00000`. Anything BELOW `0x800000` is original game code or data. It never moves. A hook site,
   a vanilla table, a record offset in the base ROM: all correct as literals, all must stay.
2. **The region boundaries themselves.** `0x800000`, `0x900000`, `0xF00000` and similar appear as
   bounds and in planted buffers inside unit tests. They are not allocations.
3. **Any address the test computes and then re-checks.** Only a HAND TYPED expectation is the defect.

## The defect, and the fix

The allocator is a bump allocator (`rom\rom_space.py`). Patches run in build list order and each
takes the next slot, so an address is a function of the total size of everything before it. A module
that grows moves every later allocation. These tests type the result.

Every patch already records its real addresses. Run this to see them:

    py -3.14 -P -c "import sys;sys.path.insert(0,r'<LOG>\scripts\permanent');import log2_build;r,a=log2_build.assemble(log2_build.BASE,log2_build.read_build_list(log2_build.DEV_LIST));print({k:list(v)[:6] for k,v in a.notes.items()})"

For example `alloc.notes["bf_ki_pool"]` carries `window`, `yellow`, `orange`, `code`, `code_len`
and `fix`. `alloc.notes["fullpower_hud"]` carries `code`, `size`, `sites`. Read the address from
there. Each file's `built()` already keeps the allocator or its notes, so the value is in reach.

If a value a test needs is genuinely not recorded, add it to that PATCH's notes rather than typing
it in the test. Say so in your report.

## MANDATORY: a mutation control per file

A test that reads its expectation from the patch it is testing can decay into "the patch wrote where
the patch said it wrote", which proves nothing. For **at least one converted test in each of the four
files**, prove it still has teeth:

1. Build normally. Confirm the test passes.
2. In a scratch copy, perturb the thing under test (shift the patch's write, change a byte it
   emits, or hand the test a deliberately wrong note value).
3. Confirm the test FAILS.
4. Put that control in the test file permanently, in the style of `test_log_paths_exist.py`, which
   carries its own control class. If a control cannot be made permanent for a given test, say why
   in your report and show the one-off run instead.

A conversion without a demonstrated control is not finished work.

## Rules

- Absolute paths only. Never `cd`, `Set-Location` or `Push-Location`.
- Never write under `data\`. Never create or overwrite a ROM, save or state anywhere.
- No em dashes or en dashes. ASD-STE100 in comments. WHY only, one or two lines.
- Do not weaken an assertion to make a test pass. If a test now fails for a real reason, report it.
- Do not run the whole suite. The controller runs it.
- Do not commit.

## Proof required

Per file: tests run, failures, errors, skips. Plus the mutation control result for each file, as
"perturbed X, test Y failed with Z".

Expected end state: all 14 rows pass, and each of the four files carries a control that fails when
the thing under test moves.

One report message, then stop. Do not add a byte order mark.
