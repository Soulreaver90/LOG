# Verified: Grok 4.7 high on the bf_hud test split (commit bb2bf5e)

Asked one question only: did the rewrite preserve real coverage, or did it quietly delete it? Grok
was told the ruling was not its to review.

**Verdict: an honest narrowing of a claim that became untrue. No defect found.**

I verified the one claim that contradicted me, and it is right. Every finding below is CONFIRMED by
Grok against a quoted line, and the two that changed my own account I re-checked in the repository.

## What it corrected in my account

The dropped assertion `self.assertEqual(self.size, MOCK_SIZE)` was NOT in `test_mockup_files`. It
was line 317 of the old file, inside `test_r39_is_v2b_relocated`, which the rewrite deleted whole. I
checked this myself with `git show bb2bf5e^`. My earlier account put it in the wrong row. The
conclusion is not affected: no coverage was lost either way.

## What is genuinely no longer covered

Two things, named concretely. Both are the orange bar claim the rewrite was told to retire, so both
come back if the owner overturns the ruling.

1. **The pool code past the yellow image.** A byte in the pool window after `YELLOW_LEN` (0x500),
   outside the state 46 stub, can change and every row in this file stays green. The yellow image
   row says so on its face: "The code behind it was rewritten to pick a colour, and no row compares
   that."
2. **The single delta on the hook and ability words.** No row now compares a hook word or an
   ability word to the mockup. A hook word can take any value that still resolves to the patch's own
   label. Two other rows still check those words against the patch labels, which is a real check,
   but not a mockup check.

## What still has a row that can go red

The HUD slices, the 4034 bytes inside them that v2b shares with its own base, the yellow image, the
vacated `0xE11000` page, the v2 to v2b state 46 fix, the built state 46 stub, and the `MOCK_SIZE`
boundary.

## Two things it confirmed that I claimed

- `MOCK_SIZE` is load bearing in two independent places: both new assertions in `test_mockup_files`
  index on it, and it is the window length in the frozen site list at line 249.
- The new pair is **stronger** than the assertion that went, not weaker. The old equality compared
  the build window size to a constant and never read the mockup page. The new pair reads the
  SHA-1 pinned mockup and fails in three separate directions: too small, too large on the page, and
  past the page.

## An independent cross-check of my corrected count

Grok derived the shared bytes as `17888 - 13854 = 4034`, from the test constants alone. That agrees
with the corrected 13854 and not with the 13862 I first wrote.

## Every control, checked

Grok read all six `ControlTests` rows and found each one exercises the check it names. It noted that
`test_without_the_namer_the_pool_takes_the_first_chunk` has its tooth in the `skipped == []`
assertion, because the line after it reads cached notes rather than the reapplied image. That is a
true reading and not a defect: the row still goes red if the patch skips the first chunk.

Raw output: `scratch\cursor\2026-11-13-bfhud-split\raw.txt`. Prompt: the `prompt.md` beside it.
