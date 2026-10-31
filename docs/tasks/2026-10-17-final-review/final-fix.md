# Slice 1 final review fix round

Read `docs\tasks\2026-10-17-final-review\final-review-report.md` first. Fix these items. Do not change any ROM byte: the rebuild of `builds\log2_poc.gba` (`gohan_gi ssj2_form gohan_portraits`) must give SHA-1 `345ae98c1145f669d936cad62cad8635467f3824`.

## Docs (design and plan)

1. **Important 1.** In `docs\design\2026-10-16-log-merge-design.md` section 8.3, reword acceptance test 3: the Super Saiyan 2 lightning is blue spark pixels in the set 159 sprite frames (anim 4 idle and others), not a separate aura object (Task 6, CONFIRMED). Reword test 6: the Time Chamber exit cutscene keeps the armor; the gi shows from the first moment Gohan is playable (final, design 6.6). Keep each test's pass condition clear.
2. **Important 2.** In section 8.2 D, add a superseding note: the build keeps Rage on armor set 58 (Global Constraints, Ruling 31). In the Cell fight, gi Gohan becomes armored Rage. Changing this is my call (see my questions in progress.md). Remove or correct the claim of an existing Rage aura.
3. **Minor 5.** In `docs\design\plans\2026-10-16-slice1-poc-plan.md`, add a short "Superseded by rulings" note under Tasks 5 and 6 that names Rulings 13, 18, 19, 27, 30, 31, 35 and 36 with one line each, pointing to `docs\ledger\progress.md`.

## Docs (RE)

4. **Minor 1.** `docs\research\re-sprite-decompression.md` lines 153-162 and 180: set header +1 is the high byte of the u16 VRAM slot size at +0, not a direction count; the game hardcodes 4 directions (Ruling 35, Task 5 part 2 fact 2).
5. **Minor 2.** `docs\research\re-outfit.md`: line 11 credits the hang fix to rom:0x42F0 (not 0x959C); line 31 is answered by `docs\research\re-forms.md` section 2; section 8 questions 1 and 2 are answered by me (quote the design 6.6 my lines).
6. **Minor 3.** `docs\RE-BIBLE.md` line 224: verify the flag 195 SETFLAG address from the script bytes (the review says rom:0x3EC6A2, after the map load, not 0x3EC67B). Correct the line with the bytes you read.
7. **Minor 4.** `docs\RE-BIBLE.md` line 153: update the portrait ids to the Task 7 values (entry 5 `73 74`, entry 22 `75 76`, entry 2 `3B 0A`).
8. **Minor 8.** `docs\build-log.md`: add a Task 5 section like the Task 6 and 7 sections (set offsets, SHA-1 40d66d64dfda1179365b094194083ff828f1b6dd, Ruling 35).

## Code

9. **Minor 6.** Add one test on the three-patch build that resolves entries 2, 5 and 22 through the code's own literals (one of the 17 relocated literals, then the rom:0x959C set table) to sets 157, 158 and 159, and entry 4 to set 58.
10. **Minor 7.** In `ssj2_form.py` and `gohan_portraits.py`, turn a missing `alloc.notes` key into a `ValueError` that names the patch to run first. Add a test for each.

## Proof

Run the full suite. Rebuild and prove the SHA-1 is unchanged. Use LF line endings, no byte order mark, no em or en dashes. Never write under `data\`. Write a short report to `docs\tasks\2026-10-17-final-review\final-fix-report.md`.
