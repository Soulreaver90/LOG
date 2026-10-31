# r27: Gohan and Goku in Super Saiyan through the Cell Games, plus no ki drain during scenes (final, 2026-10-20 1:00 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Base: r26 (`archive\builds\log2_poc_r26.gba`, SHA-1 `1a381ac7947cdaa2e9fdf0afaa44331a9b524dbf`), built from `scripts\permanent\build_list.txt` plus the art tables. Read first:
- `docs\tasks\2026-10-20-cellgames-ssj\cellgames-ssj-report.md` (the design; it was made on r22, and r23-r26 changed only portrait data, block words and palette 172) and `scripts\one-time\2026-10-20-cellgames-ssj\` (its scripts and site lists).
- `docs\tasks\2026-10-20-inject-tool\inject-tool-report.md` and `art\tables\README.md` (how builds work now: `log2_build.py --list`, `build_list.txt`, `art_inject`).
- `docs\RE-BIBLE.md` section 6 (forms, the Super Saiyan tick, the drain accumulator at player +0x184, rows tagged FRM and CGS) and the headers of `ssj2_form.py`, `rage_stats.py`, `npc_gi.py`.

## Final decisions

1. **Gohan:** as in the study design. NPC Gohan uses the gi Super Saiyan set 158 and the Super Saiyan gi portrait (115) through the stretch. Playable Gohan starts in Super Saiyan at both leader points. Rage still works. Base after Cell (already in the game).
2. **Gohan ki refill:** fill Gohan's ki (EP) to full at the start of his Cell fight (the Cell fight seq 1 insert).
3. **Goku is Super Saiyan from his arrival at the Cell Games until his death (the teleport).** This changes the study's recommendation:
   - Playable Goku transforms on arrival (the study's "seq 1" option), with the power-up animation before ext 73 (4,61), as the study describes.
   - Every NPC Goku in the stretch is Super Saiyan (set 61) with portrait 65, including the 14,1 NPC shown while another character leads, and after he gives up until he teleports.
   - If the player can switch leader on the arena maps and switch back to Goku, say what form Goku has then, and make him Super Saiyan. If that needs more than script and object edits, report it as an open point; do not guess.
4. **No ki drain while any scene plays, everywhere in the game** (me: "All scenes"). Drain runs as today in free play and in fights.
   - Find the game's "a scene or script is running" marker (a global flag, the script engine state, or the player control lock). Prove it with code quotes: it is set for the whole time a cutscene runs, including text boxes, and clear in free play and in fights. Use two independent search shapes.
   - Add the check to the form tick code we own (the `ssj2_form` re-encoding). It applies to Super Saiyan and Super Saiyan 2. Rage and every other form behave as today.
   - If the marker is also set during a boss fight that a script starts (for example the Cell fight itself), say so; drain must still run in fights.

## Build

- Add the patch `cellgames_ssj` (and the drain pause, in `ssj2_form` or its own patch, your call; say which) to `build_list.txt` at the end, as the study said, so no earlier byte moves. Read every npc_gi copy address from `alloc.notes`, never from the r22 report.
- Build `builds\log2_poc_r27.gba` with `log2_build.py --list`. Copy `log2_poc_r26.sav` and every `log2_poc_r26.ss*` to the r27 names. Never overwrite any ROM, .sav or state.
- Prove the r26 -> r27 diff touches only the expected sites (list them). Portrait frames, block words and palette 172 must be unchanged.
- Tests: the 12 from the study, plus: the drain pause (tick skips the drain with the marker set and drains with it clear), Gohan refill, Goku set 61 at every NPC site, portrait records. Existing tests that pin Cell Games bytes (npc_gi 157) must keep testing what they mean; give them the build list they need. The whole suite passes.
- My test plan: `.sav` slot 3 for the whole stretch, and which save state (if any) reaches each part.

## Parallel run

- Nothing else is running. I may edit files under `art\portrait-sources\`; do not touch them. Do not run `inject.py portrait` or `palette`.
- Bible rows in `scripts\one-time\2026-10-20-r27-build\bible_rows.md` (sections as in `scripts\one-time\2026-10-19-r21-build\bible_rows.md`). Do not edit `docs\RE-BIBLE.md`.

## Limits

- Never write under `data\`. Never overwrite a ROM, .sav or state file.
- Python: LF, no byte order mark, no em or en dashes. Code style: a header block per file, short functions, precise names, 1-2 line comments for the non-obvious why only. Never `cd` in any shell call; absolute paths only. A shell heredoc collapses backslashes: write files with Python, and check them for control characters. Tools installed with pip --user load with `py -3 -P`.
- Work scripts in `scripts\one-time\2026-10-20-r27-build\`. Label findings CONFIRMED, LIKELY or SPECULATIVE.

## Report

Save it as `docs\tasks\2026-10-20-r27-build\r27-build-report.md`: the marker and its proof, the patch changes with addresses, the tests, the r27 SHA-1, the files copied, the diff proof, open points and my test plan. Then reply with status, the r27 SHA-1, the test count and concerns only.

