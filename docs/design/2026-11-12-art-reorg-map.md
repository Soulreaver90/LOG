# `art\`: the map, before anything moves

The owner, 2026-11-09: "The whole art thing is such a mess with folders scattered all over." He
parked the reorganisation for Thursday 2026-11-12 and said step 1 is a MAP, not a move. This is it.
**Nothing has been moved, renamed or deleted.**

## What is there

34 folders, over 11,000 files, and 16 loose files at the root. `art\Owner Build - Trunks Tank\` is
his live art and was not counted, opened or listed.

## The finding that changes the job

**29 of the 34 folders are live build inputs.** This is not a tidying problem. Only four folders
have no reader anywhere in `scripts\permanent\`:

| folder | readers |
|---|---|
| `finale` | none |
| `gi_base_v2` | none |
| `gi_ssj_v5` | none |
| `gi_ssj2_aura_v5` | none |
| `kits` | none, and I created it on 2026-11-12. My addition to the mess. |

Everything else is named by a module, a tool or a test. The `gi_*` family looks like abandoned
rounds but is not: 11 of its 14 folders are read by live code, including `gi_ssj_v2`, `gi_ssj_v4`,
`gi_ssj2_v2`, `gi_ssj2_v4` and `gi_ssj2_aura_v4`.

## Why it has stayed a mess: the folder names are hardcoded 344 times

| name | string mentions |
|---|---|
| `anim` | 206 |
| `gi_ssj` | 199 |
| `gi_ssj2` | 111 |
| `gi_base` | 88 |
| `golden` | 85 |
| `portraits` | 31 |
| `tables` | 21 |

**55 files, 344 mentions in all.** `log_paths.py` centralises only five art paths today: `ART`,
`HAND_FIXES`, `PORTRAIT_SOURCES`, `SPRITES` and `ART_TABLES`. Every other folder is spelled out at
each use site. So moving one folder means editing dozens of files and hoping the grep was complete,
which is exactly the kind of sweep that misses a site and breaks a build quietly.

## The structural fix, and it is cheap relative to the payoff

**Name every art folder exactly once, in `log_paths.py`.** After that the physical layout is a
one-file change, now and every future time. The reorganisation he actually wants becomes possible;
today it is not, at any sensible cost.

This is a mechanical refactor with a test that can prove it: after it, no file under
`scripts\permanent\` outside `log_paths.py` may contain an art folder name as a string literal.
That test is the thing that keeps the mess from coming back.

## Proposed order

**Phase 1, safe today, no code change and no risk to a build.**

1. Fix the four faults he already listed on 2026-11-09:
   - `portraits.json` resolves against `art\tables\`, but portraits belong in `art\portraits\`.
   - `art\tables\portraits\` still holds 10 older finals that must move with it.
   - Three filenames carry `owner`, which he has corrected twice:
     `040_cell_40_owner_v2.png`, `052_sp52_owner_v3.png`, `065_goku_ssj_65_owner_dl7.png`.
   - Decide the split between `portrait-kit`, `portrait-sources` and `portraits`, or collapse it.
2. Retire the four dead folders, and `art\kits\` with them once the power-up frames are drawn.
3. Give the 16 loose root files a home. They are review sheets, HUD icon blobs and overview images.

**Phase 2, needs his go-ahead.** The `log_paths.py` refactor above, then the layout he wants.

**Not part of this.** Adding portrait ids 28 and 29 to `portraits.json` moves both master SHA-1s and
breaks two pins in `test_golden`. That is a separate decision.

## Rules that hold throughout

- Copy, never move, until he says otherwise (his instruction, 2026-11-12).
- Never read from, write to or delete anything in `art\Owner Build - Trunks Tank\`.
- Ask before touching any file he may have open.
