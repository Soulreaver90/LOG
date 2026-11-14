# Brief: group 3, the tests that compare against a frozen ROM

Read `docs\tasks\2026-11-13-the-34\triage.md` first.

Four files compare a fresh build against a ROM file sitting in `builds\`:

- `test_bf_hud.py`
- `test_chamber_spar.py`
- `test_superperfect_cell.py`
- `test_piccolo_gi_scene.py`

## The owner's instruction

"All I want is everything to be clean and fixed. Things should be done cleanly and correctly."

**You may not delete a test to make a number go green.** If a claim is genuinely unprovable, you
report it to the controller with your reasoning. You do not drop it quietly and you do not weaken
an assertion so it passes.

## The defect

These tests bolt two claims together. `test_chamber_spar` is the clearest example:

    self.assertEqual(R37.read_bytes(), r37_rom)          # 1
    self.assert_only_sites(r36.read_bytes(), r37_rom)    # 2

**Claim 1 is "the frozen file on disk IS what we build today".** That can never hold again. The
allocator bumps through one free region, so any module that changes size moves every later
allocation and the whole ROM differs. A historic ROM cannot be reproduced once the code moves on.
This claim is why the rows are red.

**Claim 2 is the real meaning:** "going from r36 to r37 changes exactly these sites and nothing
else." That claim is TRUE FOREVER and does not need a file at all.

## The fix: build both sides

Compute both sides fresh, in memory, from the build lists:

    before = assemble(BASE, names[:i])        # the list without the module
    after  = apply_patches(before, [module])  # with it
    assert_only_sites(before, after)

This proves the same thing, re-derives it on every run, and cannot go stale. Keep each test's
existing site list and its helpers (`assert_only_sites`, `diff`, `with_stats` and friends): the
sites are the knowledge, and they are stated independently of the build.

Where a test's two consecutive versions are two build lists rather than one module, diff the two
lists' builds the same way.

## What you MAY still pin

- **Frozen INPUTS.** `test_bf_hud` pins the SHA-1 of the hand made v2 and v2b mockup files. Those
  are inputs that nobody regenerates, so their hashes are correct to pin. Keep them.
- **Vanilla ROM addresses**, anything below file offset `0x800000`. They never move.

## What you MAY NOT do

- Do not write, create, move or overwrite any ROM, save or state. Not in `builds\`, not anywhere.
  This is a hard rule in this project. Everything you need is built in memory.
- Do not regenerate a mockup to make a comparison pass.

## `test_bf_hud` needs a judgement call, so report before deciding

Six of its rows claim the shipped ki bar is byte identical to the approved v2b mockup, relocated.
`test_mockup_files` fails as `4276 != 2084`: `bf_ki_pool`'s window DOUBLED when the orange Super
Saiyan bar was added. So the mockup no longer describes what ships, and no relocation fixes that.

Work out what those six can still prove and say so in your report. Do not delete them. If the
honest answer is "this proved the original Buu's Fury port, which the orange bar work superseded",
say that in writing with the evidence, and the controller takes it to the owner.

## Also in these files: stale module-list rows

`test_before_is_r28`, `test_before_is_r36` and `test_before_is_r38` are the same defect group 1
fixed: a pinned SHA-1 standing in for "this trial sits on the current master". Convert them the way
group 1 did. Read `test_relay_cooldown.test_before_is_r39` and
`test_beam_struggle.test_before_and_the_rom_are_pinned` for the pattern: compare MODULE LISTS and
check them against the note keys the build recorded, so it proves which modules actually ran.
`scripts\permanent\tests\masters.py` holds the two master hashes if you need one.

## MANDATORY: a mutation control per file

For at least one converted test per file, prove it still has teeth: perturb the thing under test on
a copy in memory, confirm the check goes red, and leave that control in the file permanently as a
`ControlTests` class. `test_roundtrip.py` has a good example to copy.

## Rules

- Absolute paths only. Never `cd`, `Set-Location` or `Push-Location`.
- Never write under `data\`.
- No em dashes or en dashes. ASD-STE100 in comments, WHY only.
- Do not run the whole suite. Do not commit.

## Proof required

Per file: tests run, failures, errors, skips, plus each mutation control and the text it produced.
Name any test whose meaning changed, and say exactly what it proves now against what it proved
before.

One report message, then stop. Do not add a byte order mark.

---

# UPDATE 2026-11-13, 8:20 PM. Read this before you start.

The Goku chamber exit work landed after this brief was written. Three things changed.

## 1. The group is now SIXTEEN rows, not six

The baseline is `docs\tasks\2026-11-13-xfm9\baseline-failures.md`. These sixteen are yours:

| File | Rows |
|---|---|
| `test_bf_hud.py` | 8: `test_before_is_r38`, `test_every_v2b_run_has_its_counterpart`, `test_mockup_files`, `test_r39_is_v2b_relocated`, `test_v2_to_r39_is_the_state_46_word_and_stub`, `test_r38_to_r39_files_differ_at_the_named_sites_only`, `test_r39_file_equals_the_build`, `test_new_space_follows_r38_and_skips_a_named_chunk` |
| `test_chamber_spar.py` | 3: `test_before_is_r36`, `test_r37_file_equals_the_build_and_differs_from_r36_at_the_sites`, `test_r38_file_equals_the_build_and_differs_from_r37_in_type_25_stats_only` |
| `test_superperfect_cell.py` | 4: `test_r32_to_r33_is_the_name_only`, `test_r33_to_r34_is_the_name_string_only`, `test_r34_to_r35_is_the_text_its_pointer_and_the_stats`, `test_r36_file_equals_the_build_and_r35_differs_by_portrait_52_only` |
| `test_piccolo_gi_scene.py` | 1: `test_r32_file_holds_this_scene` |

The five rows NOT in your group are the master SHA-1 re-pin, which I do myself, once.

## 2. Two constants in `test_piccolo_gi_scene.py` are today's values, not the answer

The Goku work re-pinned `R28_SHA1` and added `SHIFT = 0x24`. Both are correct today and both will
rot on the next size change, which is the whole defect this group exists to remove.

**Replace both.** Build the r28 side fresh from its own module list, and derive the shift by
comparing the two builds, rather than naming `0x24`. A constant that a build can compute is a
constant a test must not carry.

## 3. `test_ext_ops.py` needs a real fix, not a comment change

Line 29 reads:

    MOVED_TABLE, MOVED_LENGTH = 0x3DE6F4, 36  # map 9,3; fullpower_ssj moves word 32 into expansion

**That premise is now false.** `fullpower_ssj` no longer moves any word of that table: the chamber
entry record is back to vanilla and the work moved to the chamber exit. The file still passes 12 of
12, which is the worrying part. A test whose stated premise is false and which passes anyway may be
asserting nothing.

Read what those 12 tests actually exercise. If the premise is dead, give the test a live one or say
plainly that the coverage was never there. Do not just correct the comment.

## 4. The two masters moved

Golden is `778ccff59eddf7d34f432ece7e9a929595b2425f`. Dev is `49cdfd3c172d734956d74ecb6c6419d1a301da6e`.
Do not re-pin them anywhere. I own that one change.
