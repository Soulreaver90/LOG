# Study: Super Perfect Cell after the self-destruct (final, 2026-10-22 5:43 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Current build: r27 (`builds\log2_poc_r27.gba`, SHA-1 `5c4befd8feb8a8840730882c330f3c1ed5d1e51c`). Read first: `docs\RE-BIBLE.md` (sprites, sets, frames, codec, portraits sections 5-5b, scenes 7-8, the Cell Games rows tagged CGS and R27, the SSJ2 aura work), `docs\tasks\2026-10-20-cellgames-ssj\cellgames-ssj-report.md`, `r27-build-report.md`, `inject-tool-report.md` and `art\tables\README.md`, and the SSJ2 aura reports in `docs\ledger\` (search them for "aura" and "bolt").

## My ask, word for word

"When perfect cell comes back after exploding, he should be in his super perfect cell form. The only different would be the same sprite but with the same electrical aura that ssj2 gohan has, just maybe bumped up in size to compensate for the bigger sprite. I'll also create a new portrait. Do we have room to add a whole new portrait?"

## Questions

1. **The stretch:** which scenes and fights show Cell after he returns from the self-destruct, until he is beaten (scene tables, seq numbers, maps, flags). Which actor or sprite set draws him there (NPC in scenes, enemy in the fight), and how each is chosen.
2. **The aura:** how Gohan's SSJ2 electric aura is drawn today: baked into his frames, a separate effect object, or palette work. Quote the code or data. What it takes to give Cell the same aura, scaled for his larger sprite: options (reuse the effect object attached to Cell's actor with a bigger size or offset; bake bolts into a copy of Cell's frames; scale the bolt frames), with the cost and risk of each. Cover scenes and the fight. Say whether the GBA object size limits (64x64 per object, OAM count) allow a bigger aura.
3. **A new portrait:** can we add a new dialog portrait id for Super Perfect Cell? The inject tool notes "ids above 121 need a bigger portrait block". List which ids exist, which are unused or reusable, the status-page twin, and what growing the block would take. Which scene records (portrait byte at +3) must switch to the new id in the stretch.
4. **Stats (only report):** what Cell's fight stats are now, so I can decide if Super Perfect Cell should be stronger. Do not propose values.

## Deliverable

- A design (not the patch): the chosen aura method and its alternatives, the sprite set and scene edits, the portrait plan, the tests, and an effort estimate in task sessions. Mark each point CONFIRMED, LIKELY or SPECULATIVE.
- What I must make: the portrait (64x64, OBJ palette, frame equal to vanilla's) and any art.
- Bible rows in `scripts\one-time\2026-10-22-superperfect-study\bible_rows.md` with "## Section N" headings as in `scripts\one-time\2026-10-19-r21-build\bible_rows.md`.

## Parallel run

- A build task writes `scripts\permanent\`, `tests\`, `builds\` and `scripts\one-time\2026-10-22-r28-build\`. A port task writes `%USERPROFILE%\Documents\GitHub\legacyofgoku2-gnu\` and `scripts\one-time\2026-10-22-disasm-port\`. I write `scratch\audio\`. Do not touch any of them. You write only `scripts\one-time\2026-10-22-superperfect-study\`.

## Limits

- Read-only on every ROM and save. Never write under `data\`. No patch in `scripts\permanent\`. Do not run `inject.py portrait` or `palette`.
- Python: LF, no byte order mark, no em or en dashes. Never `cd` in any shell call; absolute paths only. Write each file with Python. Tools installed with pip --user load with `py -3 -P`.
- Search with at least two independent shapes where you claim a list is complete, and reconcile the counts.

## Report

Save it as `docs\tasks\2026-10-22-superperfect-study\superperfect-study-report.md`. Then reply with the design summary, the portrait answer, the effort and concerns only.

