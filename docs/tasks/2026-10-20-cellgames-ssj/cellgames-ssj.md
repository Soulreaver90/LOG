# Study: Gohan in Super Saiyan through the Cell Games (final, 2026-10-20 10:15 AM)

Personal GBA ROM hack (Legacy of Goku II, USA). Current build: r22 (`archive\builds\log2_poc_r22.gba`, SHA-1 `9287672b53f1757d43a46dc01a852f1142f0e115`). Read first: `docs\RE-BIBLE.md` sections 6 (forms, appearance entries, `form_reapply`, ext 73), 7-8 (scripts, cutscene records), the NPC work (`scripts\permanent\patches\npc_gi.py` and its report in `docs\ledger\`), `ssj2_form.py` and `rage_stats.py` headers, the r19 and r20 reports (Cell fight scene list `rom:0x3EA400`, Rage), and the tools in `scripts\permanent\re\`.

## My ask, word for word

"Gohan, can we have him super saiyan at the cell games in his NPC form and start super saiyan when playable? In the anime he arrives ssj, he can be base (default) after cell is beaten, only adjust in the cell games."

Added by me at 10:19 AM: "When goku enters the cell games arena, can we also have him transform? he should be ssj as well before fighting cell". Apply questions 1-6 to Goku too: his NPC set (the SSJ gi set, if one exists), his playable form if he is playable in the stretch (fight Cell as Goku), his dialog portrait (65 is the remastered SSJ Goku), and what sets him back after. Say whether he is ever playable at the arena; if he is only an NPC, the design covers the NPC and portrait only.

Decisions already made by me:
1. Ki drain: Super Saiyan drains ki normally, as playable SSJ does today.
2. Scope: from Gohan's arrival at the Cell Games through the end of the Cell fight, as the NPC and when playable. After Cell is beaten he is base (default) again.

## Questions (answer each with quoted code, script bytes or flags)

1. **The stretch:** which maps, scenes and flags make up "arrival at the Cell Games" to "Cell beaten"? List the scene tables in order with the flags that gate them (start and end flag of the stretch).
2. **NPC Gohan:** which actor or set draws Gohan as an NPC in those scenes (the gi set 157 from `npc_gi`, or another), and how the set is chosen (actor spawn record, script command, appearance entry). What the gi Super Saiyan set (158) would need to show instead, and whether its frames cover every pose those scenes use (walk, stand, talk, any special pose). List missing poses.
3. **Playable Gohan:** where the game makes Gohan the leader for the Cell fight, and which form he starts in (ext 73 calls, appearance entries, `form_reapply`). How to start him in Super Saiyan there (the playable SSJ entry, with its normal ki drain), and how the existing Rage step (ext 73 to set 160, the "transformed into Super Saiyan 2" text) still works from SSJ.
4. **After Cell:** what sets Gohan back, and what must be added so he is base (default) after the fight: the leader form, the NPC set, and the portrait.
5. **Portraits:** which dialog portrait ids show for Gohan in the stretch, and whether they should switch to the Super Saiyan gi portrait (115) while he is Super Saiyan.
6. **Saves:** what my saves (`archive\builds\log2_poc_r22.sav`, `.ss1`-`.ss3`) hold for these flags, and which slot or state lets me test the stretch.

## Deliverable

- A patch design (not the patch): every byte or table entry to change, the new patch name and its place in the build list, and the tests it needs. Mark each point CONFIRMED, LIKELY or SPECULATIVE.
- Risks: anything that could leave Gohan stuck in Super Saiyan outside the stretch, or base inside it, and how the design prevents it.
- Bible rows in `scripts\one-time\2026-10-20-cellgames-ssj\bible_rows.md` with "## Section N" headings as in `scripts\one-time\2026-10-19-r21-build\bible_rows.md`.

## Parallel run

- A tool task writes `scripts\permanent\`, `tests\`, `builds\` and `scripts\one-time\2026-10-20-inject-tool\`. Do not touch them. You write only `scripts\one-time\2026-10-20-cellgames-ssj\`.

## Limits

- Read-only on every ROM and save. Never write under `data\`. No patch in `scripts\permanent\`.
- Python: LF, no byte order mark, no em or en dashes. Never `cd` in any shell call; absolute paths only. A shell heredoc collapses backslashes: write files with Python, and check them for control characters. Tools installed with pip --user load with `py -3 -P`.
- Search with at least two independent shapes where you claim a list is complete, and reconcile the counts.

## Report

Save it as `docs\tasks\2026-10-20-cellgames-ssj\cellgames-ssj-report.md`: the answers, the patch design, the risks, the test slot and the open points. Then reply with a summary of the design, the missing poses (if any), and concerns only.

