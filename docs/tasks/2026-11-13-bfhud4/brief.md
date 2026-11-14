# Brief: the last four rows of the 34, in `test_bf_hud.py`

Four rows stay red after the group 3 work. They all assert that today's build still matches the
approved HUD v2b mockup AS A WHOLE.

- `EquivalenceTests.test_r39_is_v2b_relocated`
- `EquivalenceTests.test_every_v2b_run_has_its_counterpart`
- `EquivalenceTests.test_v2_to_r39_is_the_state_46_word_and_stub`
- `FileTests.test_r39_file_equals_the_build`

## Read first

- `scripts\permanent\tests\test_bf_hud.py`, all of it, including the `EquivalenceTests` docstring and
  the file header. The previous agent wrote its measurement there.
- `docs\tasks\2026-11-13-the-34\brief-group3.md`, for the claim 1 and claim 2 split that governs
  this whole group.

## The ruling this work rests on, which is MINE and not the owner's

The v2b mockup has two halves. The HUD half still ships. The ki pool half was superseded by the
ORANGE Super Saiyan bar, which the owner approved later and which `game-status.md` records as
**PRS-3, IN**: "The second ki bar is orange, not red." The orange image sits between the yellow one
and the code inside the window, so every word that names inside the window moved by its own amount
and the code was rewritten to pick a colour.

So "the whole mockup still ships" is a stale claim, not a defect in the ROM. **I am telling the
owner I made this call.** If he says the mockup must still ship whole, the fix is in the ROM and not
in these tests, and this work is reverted.

## What must be true when you finish

**The claim that survives is stronger than the one you are replacing, and you must assert it:**
every byte of the HUD half of the approved mockup still ships byte for byte. That is a real
regression guard. Losing it would be worse than the red rows.

## Two measurements that disagree by 8 bytes. Reconcile them FIRST.

| Who | Method | bf_hud bytes that still match v2b | bytes that differ |
|---|---|---|---|
| the previous agent | region aware buckets | 13854 | 104 (38 hook words, 66 ability words) |
| me | everything outside the window `0xE11000`, size `0x1000` | 13862 | 96 |

Both agree v2b changed **16031** bytes of r38 and that **2073** of them are inside the window.

My guess, which you must prove or disprove: 8 of the 104 pointer bytes happen to hold the same value
in the build as in v2b, so a crude split counts them as matching. Say which number is right and why,
and use the region aware one if it is.

## Row by row

1. `test_r39_file_equals_the_build`. The r39 FILE is the ROM the owner played. It can never equal a
   fresh build again. Do not keep a claim that cannot hold. Replace it with the claim the file is
   actually good for: it is a frozen record, so pin its SHA-1 the way `test_mockup_files` pins the
   two mockups, and say in the docstring that it is an input pin and not a build check.
2. `test_r39_is_v2b_relocated`. Whole ROM compare, so base drift alone kills it. Replace it with the
   HUD half claim above. **It currently holds `self.assertEqual(self.size, MOCK_SIZE)`, which group 3
   moved here out of `test_mockup_files`.** That assertion is about the mockup's own window size and
   is still true of the mockup. Put it somewhere it belongs and keep it running.
3. `test_every_v2b_run_has_its_counterpart`. Re-base it on the r38 FILE, which is v2b's own base, and
   it becomes a true claim 2 form. It will then differ only at the hook and ability words. Assert
   exactly that set, named, so a NEW difference fails the test.
4. `test_v2_to_r39_is_the_state_46_word_and_stub`. Split it in two. "v2 to v2b is the state 46 word
   and the stub" is provable from the two pinned mockups alone, measured as
   `runs_of(v2, v2b) == [(0x258BC, 4), (0xE1181C, 8)]`. Verify that yourself. "The build carries the
   state 46 fix" is provable in the build. Both halves are true claims.

## Hard rules

- **You may not delete a test, narrow a test, or weaken an assertion to make a number go green.** If
  a claim is genuinely unprovable, report it and leave it failing.
- Add a `ControlTests` case for the HUD half claim: perturb one byte of a bf_hud region in a build
  and show the check goes red. A check with no control can decay into the build agreeing with itself.
- Edit `test_bf_hud.py` only. No other file.
- Write NO ROM, save or state. Build in memory only. Do not commit.
- Python is `py -3.14 -P`. Absolute paths. Never `cd`. Never put a Windows path in a `python -c`
  string literal; pass it as argv.
- Build lists live in `scripts\permanent\build-lists\`. Reach them through `log_paths.BUILD_LISTS`.
- Masters: golden `778ccff59eddf7d34f432ece7e9a929595b2425f`, dev `49cdfd3c172d734956d74ecb6c6419d1a301da6e`.
  Do not re-pin them. Do not edit `masters.py`.
- ASD-STE100. No em dashes, no en dashes.

## Proof I need

Run the full suite ONCE. The baseline is **2152 tests, 4 failures, 0 errors**, and the four are the
rows above. Report the counts and name any failure that is not one of those four.

One report message, then stop. Do not add a byte order mark.
