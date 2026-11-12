# Brief: turn ONE scripted ending kill into a real fight

Build a trial module that makes the Imperfect Cell kill in the ending a real player fight. This proves
the pattern. The other two fights repeat it later. Do NOT build all three.

## Read first

1. `docs\tasks\2026-11-05-trunks-boss-fights\design.md` - the owner's design and his decisions.
2. `docs\tasks\2026-11-05-trunks-boss-fights\report.md` - the study, blockers B1 to B11, evidence index.
3. `scripts\permanent\patches\celljr_fight.py` - the module that already does this shape. Copy its method.

## The target

Ending scene table `rom:0x3B8140`, word 23 at `rom:0x3B8016`. Today it is a scripted kill of `set:28`,
Imperfect Cell, by `set:133`. CONFIRMED by me with `scripts\permanent\scene\scene_probe.py`.

Chosen first because it has the shortest death event chain and no always-on step region over the fight
spot. Blocker B1 does not apply here.

## What to build

- A real fight against `set:28` at that point, with VANILLA Imperfect Cell stats. Change no stat.
- Trunks is the player for the fight. `leader` is ext op 70. The ending runs with Trunks as an ACTOR,
  not as the player, so this step is required (blocker B2).
- On death: Cell COLLAPSES, then the existing scripted ki blast finishes him, then the ending resumes.
  The blast already exists in word 23. Reuse it, do not write a new one.
- A loss sends the player to the vanilla save point at Capsule Corp. Do not add new loss handling.

## Hard constraints

- A trial module on its OWN build list, `build_list_trial_ending.txt`. Do NOT touch `build_list.txt`,
  `build_list_dev.txt` or `build_list_core.txt`. The owner has not approved promotion.
- Do not edit `art\trunks_tank\`, `scripts\permanent\patches\trunks_tank.py`,
  `scripts\permanent\build_list_trial_trunkstank.txt` or `docs\RE-BIBLE.md`. Another agent and I are in
  those. Put your bible rows in `docs\tasks\2026-11-05-ending-fight-1\bible_rows.md` instead, in the
  `## Section N` table shape, and I will merge them.
- Never find a scene table start by walking backward. A stray word before word 0 reads as an END and
  shifts every index by one. Reach a table through the item, event or type 5 record that names it.
- `--find-text` in `scene_probe.py` is CASE SENSITIVE.
- Read `docs\tasks\global.md` and follow every rule in it, including the expansion area, the untouched
  OBJ palette and the unchanged save format.
- Label every reverse engineering claim CONFIRMED, LIKELY or SPECULATIVE. Build only on CONFIRMED.

## Verification before you report

1. The full suite passes: `py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent`.
   Run it directly. Never pipe it into `tail`, because the pipe reports tail's exit code and a red suite
   reads as green. Report the real exit code.
2. Write tests for the new module in `scripts\permanent\tests\test_ending_fight.py`.
3. Build a trial ROM to `builds\mockups\2026-11-05-ending-fight-1\`. Print its SHA-1. Check the output
   name is absent first and never overwrite a ROM or a save.
4. State plainly what you could NOT verify without the owner playing it.

One report message, then stop. Do not add a byte order mark.
