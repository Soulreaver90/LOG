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
