# Test save: slot 2 on Roshi's island, slot 3 before the Cell Games (final, 2026-10-18 3:32 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Read first: `docs\research\re-save-format.md` (all), the header and presets of `scripts\permanent\rom\log2_save.py`, `scripts\one-time\2026-10-18-save-slots\maps.txt`, `flag_set.txt`, `conds.txt`, `sdis.py`.

## My report

"Save 1 and 3 take place after the Cell Games, and I can't leave East District 439, so let's set it at Roshi's island instead and have save 3 take place before the Cell Games."

## Wanted

| Slot | Story point | Place |
|---|---|---|
| 1 | After Cell (as now) | Capsule Corporation save point (as now) |
| 2 | After Cell (as now) | Master Roshi's Island (zone 11, areas 2-6 in `maps.txt`), where I can walk out to the world map |
| 3 | After the Time Chamber, before the Cell Games: "Enter the Cell Games" is the active quest | A place from which I can travel to the Cell Games and start them |

## My facts (verify, do not trust)

- Quest "Enter the Cell Games": active when flag 191 (set at `@0x083DD32B`, "DENDE: Good luck in the Cell Games"), done when 193 (`@0x083E8D92`). Flags 192 `@0x083E93E0`, 194 `@0x083E9BBB`, 195 `@0x083EC6A2` (Cell beaten) follow. So slot 3 is likely the post-Cell flag set minus 192-195 and minus any flag whose only SET site is in a Cell Games script. Prove each removed flag by its site.
- Hercule joins at Cell's defeat (`ext_29` with 5 at `@0x083EC67B`). Before that he is not in the party: give slot 3 the party state the game has at flag 191 (Hercule record and +0x14 bits as the game has them before he joins; read how ext_29 adds him).
- Appearances at that point: Gohan after the chamber (`ext 73 (0, 56)` at `@0x083DB62B`, entry 2, which the hack draws as the gi). Find the Vegeta and Trunks outfit at flag 191 by script order, not ROM address order; say how you placed it.
- East District 439: I cannot leave it from slot 2. Find out why (anti-piracy point, map exit condition, or a flag) and report it; that knowledge goes to the bible.

## Task

1. Find a position on Roshi's island that the game itself uses: a save point rectangle on zone 11, an `ext_35` map load into zone 11, or an arrival marker (+0x20). Quote the bytes. Confirm the island map has an exit the player can use (to the world map), and which story flags it needs.
2. Slot 3: the flag set, party, appearances, items and place as above. Prefer a place the game loads you to at flag 191 (the lookout after Dende's line, or wherever that script sends you), quoted from the script.
3. Extend `log2_save.py`: a second preset set (or a preset field for the story point) so `build` makes this new 3-slot file in one run. Keep the old `build` output byte for byte reachable (a flag or a second command), and keep its tests. New tests: slot 3 has 191 set and 192-195 clear, the journal shows "Enter the Cell Games" active (the quest table evaluation of section 5), slot 2 map is zone 11.
4. Write `test-data\saves\log2_lv40_cellgames.sav` (new file; never overwrite `log2_lv40_postcell.sav`). mGBA loads the .sav that has the ROM's name. Copy the new file next to the newest verified ROM only if that ROM has no .sav yet. Otherwise report the path, and I rename it. Never overwrite a .sav.
5. Update `docs\research\re-save-format.md` sections 5-7 and add bible rows (sections 8 and 11 of `docs\RE-BIBLE.md`: flag 191 to 194 meaning, slot places, the East District exit finding), tagged and labeled.

## Parallel run

Another task is building r13 at the same time. It edits `scripts\permanent\art\gi_*.py`, `rom_sheet.py`, `frame_lock.py`, `check_parts`, `art\` and `builds\`, and it runs the whole suite.
- Do not touch those files or folders. The only exception is the one .sav copy of step 4, and only after r13 exists and has no .sav.
- Keep `log2_save.py` and its tests importable and green at every save: write each change complete, never a half edit. While you work, run only the save tests (`test_*save*.py`). Run the whole suite once at the end.
- Do not edit `docs\RE-BIBLE.md` until your last step, and then edit only the rows you add.

## Limits

- Never write under `data\` (read my .sav there only as the base, as `build` does now). Never overwrite a ROM or .sav.
- Install nothing. Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths.
- If a position or the slot 3 party state cannot be proven, label it LIKELY and say what I should check first.

## Report

Save it as `docs\tasks\2026-10-18-save-slots\save-slots-report.md`: each slot's map, position and source bytes, the slot 3 flag diff from the post-Cell set with sites, the party and appearance choices, the East District finding, test count, the new .sav SHA-1 and path, and my test plan (load, walk out, reach the Cell Games, see Rage). Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with status, the SHA-1, the test count and concerns only.

