# Save slot 3: a real state just before the Cell Games (final, 2026-10-18)

Personal GBA ROM hack (Legacy of Goku II, USA). Read first: `docs\tasks\2026-10-18-save-slots\save-slots-report.md` (the current slot 3 and how it was made), the header and `PRESET_SETS` of `scripts\permanent\rom\log2_save.py`, `scripts\permanent\tests\test_save.py`, `docs\RE-BIBLE.md` (save, flag, script and quest rows), `docs\tasks\2026-10-18-npc-gi\npc-gi-report.md` section 5 (the r16 test plan for slot 3).

## My ask

- "Save 1 and 3 take place after the Cell Games ... have save 3 take place before the Cell Games."
- After the first fix: "I can confirm no save is before the Cell Games, all of them take place after."

The current slot 3 (`log2_lv40_cellgames.sav`, SHA-1 c755acf0) is the post-Cell flag set minus flags 192-195, with Goku leading on Dende's Lookout. I still sees it as after the Cell Games. I have not said what showed it.

## Task

1. **Find every story state that differs between "flag 191 just set" and "after Cell".** Flags are only one part. Check, with evidence:
   - Every flag that any script SETs or CLEARs between the flag 191 record (`0x083DD2F0`) and the end of the post-Cell chain. Use more than one search shape: literal pushes, computed flag numbers, ext ops that write flags, and flag writes from code (not scripts). For each shape, say what it cannot find.
   - Story data in the save that is not a flag: chapter or progress bytes, map object states, opened chests, quest table state, party bits, outfit and appearance entries, levels and EXP, items, world map unlocks, the current map's state.
   - What each post-Cell flag changes on screen: NPC dialogue conditions, map object conditions, world map icons, Journal entries, music.
2. **List the visible "post-Cell" signs** that the current slot 3 still shows (for example an NPC line, a Journal entry, a map object, Gohan's outfit or the party). Rank them by how likely I saw them.
3. **Build the new slot 3** from the "flag 191 just set" state. The leader and place stay Goku on the Lookout unless the evidence says the game puts the player elsewhere at that point. Keep slots 1 and 2 byte for byte.
4. **Prove it from the scripts:** for each sign in step 2, show the condition now reads "before the Cell Games". Run `log2_save.py journal` on the new save.
5. **Optional, only if cheap:** a state at the Cell Games Arena door (map 14,1), before the barrier scene. List it as an option; do not replace the Lookout slot with it.

## Output

- New save: `test-data\saves\log2_lv40_cellgames_v2.sav`. Never overwrite any .sav or ROM. Do not build a ROM. The next ROM build (r17) takes this save.
- Extend `log2_save.py` with a new preset (for example `cellgames2`), keep the old presets, and add tests to `test_save.py` for each state you change.

## Parallel run

- A portrait study task works in `art\portrait-sources\remaster\` and `scripts\one-time\2026-10-19-portrait-from-anime\`. Do not touch them.
- I edit `art\hand-fixes\`. Do not touch it.
- Your files: `scripts\permanent\rom\log2_save.py`, `tests\test_save.py`, `test-data\saves\`, `scripts\one-time\2026-10-18-save-slots\` (scripts), the RE-BIBLE rows you add. Run only `test_save.py` while you work, then the whole suite once at the end, from the `scripts\permanent` root.

## Limits

- Never write under `data\`. Never overwrite a ROM or .sav. Read ROMs only (use `archive\builds\log2_poc_r16.gba` and the base ROM).
- Install nothing. Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths. A shell heredoc collapses backslashes: write files with Python, and check them for control characters.
- Label findings CONFIRMED, LIKELY or SPECULATIVE. If you cannot trace a piece, say so and do not guess.
- Add bible rows for each new confirmed fact in `docs\RE-BIBLE.md`, tagged. Add only your own rows.

## Report

Save it as `docs\tasks\2026-10-18-save-slot3\save-slot3-report.md`: the state diff table (state, post-Cell value, flag 191 value, evidence), the visible signs ranked, the new save's SHA-1, the test count, and my test plan (what to check in game to see "before the Cell Games"). Then reply with status, the SHA-1, the test count and concerns only.

