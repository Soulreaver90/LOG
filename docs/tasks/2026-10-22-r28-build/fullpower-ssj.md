# r28: "Full Power" Super Saiyan for Goku and Gohan, from the chamber until Cell is beaten (final, 2026-10-20 2:55 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Base: r27 (`builds\log2_poc_r27.gba`, SHA-1 `5c4befd8feb8a8840730882c330f3c1ed5d1e51c`), built from `scripts\permanent\build_list.txt` with `log2_build.py --list`. Read first:
- `docs\tasks\2026-10-20-r27-build\r27-build-report.md` and `cellgames-ssj-report.md` (what r27 added: `cellgames_ssj`, `scene_drain_pause`, the scene marker).
- `docs\RE-BIBLE.md` section 6 (forms, the form tick, transform input, B revert, Rage, the HUD Z and Z2 icons and their grayed state, rows tagged FRM, HZ2, CGS, R27), sections 7-8 (scripts, flags), and the save format (rows tagged SAV, `docs\research\re-save-format.md`).
- The headers of `ssj2_form.py`, `rage_stats.py`, `scene_drain_pause.py`, `cellgames_ssj.py`, and the Time Chamber work (Gohan's purple gi after the chamber: `npc_gi.py`, the outfit reports in `docs\ledger\`).

## My ask, word for word

"I am debating on having goku and gohan enter the chamber as super saiyans and just have them like that. They wont lose any ki from the super saiyan form, leave the death animation of them going back to normal as is, remove the code that has them detransform when ki is at 0, have the Z unselectable (the grayed out version of it when its unusable). When goku is unlocked any point after, he is at base without this unlimited ssj and gohan same, after cell games he is back to base without the unlimited ssj."

## Final decisions

1. **The stretch:** Goku from entering the Time Chamber, Gohan from entering it if the game has a Super Saiyan sprite set for his pre-chamber outfit, otherwise from leaving the chamber (in the purple gi). Both end when Cell is beaten. Say which applies to Gohan, with proof.
2. **In the stretch, for Goku and Gohan only:**
   - They are Super Saiyan whenever they lead or show as NPCs (sets and portraits as r27 already does at the Cell Games; extend to the whole stretch).
   - The form never drains ki. Attacks still cost ki as today.
   - They never revert at 0 ki.
   - **B (manual revert) is disabled.**
   - **The Z icon shows its grayed-out (unusable) state**, and Z cannot be selected.
   - The knockout (death) animation that shows them reverting stays as it is. Say what form they have after a knockout and continue, and make it Super Saiyan if the stretch is still on.
   - Rage at the Cell fight still gives Gohan Super Saiyan 2 with its text, as today.
3. **After Cell is beaten:** both are base, and Super Saiyan works as normal (drain, revert, B, Z), for Goku whenever he is unlocked later too.
4. **Remove from r27:** Goku's power-up scene at the arena (the 28-byte insert). Remove any other r27 step that the stretch makes useless (the Gohan Super Saiyan start inserts, the Gohan refill), but only if removing it changes nothing the player sees; say what you removed and what you kept and why. Keep `scene_drain_pause` for the other characters.
5. **Other characters** (Vegeta, Trunks, Piccolo, and any other form) behave exactly as in r27.

## My test save (required)

I need a save "right before they leave the chamber".
- First look for an existing my save or state at that point (`builds\*.sav`, `*.ss*`, and older builds). If none, make a new `.sav` from the closest my save by setting only the story flags, map and leader the save format needs, with a correct checksum. Prove it with the save tools and the bible's save rows: name every byte you changed.
- Write it as a new file, `builds\log2_poc_r28_chamber.sav` (never overwrite any file), and say which slot holds the chamber point. Also state if the r27 states still work on r28.

## Build

- Patch name and place in `build_list.txt`: your call, appended so no earlier byte moves. Edits to `cellgames_ssj` are allowed; say what changed.
- Build `builds\log2_poc_r28.gba`. Copy `log2_poc_r27.sav` and every `log2_poc_r27.ss*` to the r28 names. Never overwrite any ROM, .sav or state.
- Prove the r27 -> r28 diff touches only the expected sites. Portrait frames, block words and palette 172 unchanged.
- Tests: the stretch start and end flags; no drain and no revert at 0 for Goku and Gohan in the stretch; B and Z blocked in the stretch and working after; other characters unchanged; Rage still gives Super Saiyan 2; the knockout case; the save file (flags and checksum). The whole suite passes.
- My test plan: the chamber save, then the Cell Games with r27's slot 3.

## Parallel run

- A tool-review task writes only `scripts\one-time\2026-10-22-modder-tool-review\`. Do not touch it. I may edit files under `art\portrait-sources\`; do not touch them. Do not run `inject.py portrait` or `palette`.
- **Resume note (2026-10-22):** an earlier task on this brief was stopped in its research step and wrote nothing outside `scripts\one-time\2026-10-22-r28-build\`. Reuse its work there (`state_senders`, `stretch_sweep`, `ops`, `reconcile`: a two-shape sweep of the form-setting sites from the chamber to the Cell Games), but re-check any result you rely on.
- Bible rows in `scripts\one-time\2026-10-22-r28-build\bible_rows.md` (sections as in `scripts\one-time\2026-10-19-r21-build\bible_rows.md`). Do not edit `docs\RE-BIBLE.md`.

## Limits

- Never write under `data\`. Never overwrite a ROM, .sav or state file.
- If a decision above cannot be built without guessing (for example, no clean way to gray the Z icon), stop at that point, build the rest, and report it as an open point.
- Python: LF, no byte order mark, no em or en dashes. Code style: a header block per file, short functions, precise names, 1-2 line comments for the non-obvious why only. Never `cd` in any shell call; absolute paths only. Write every file with Python (not heredocs), and check them for control characters. Tools installed with pip --user load with `py -3 -P`.
- Work scripts in `scripts\one-time\2026-10-22-r28-build\`. Label findings CONFIRMED, LIKELY or SPECULATIVE.

## Report

Save it as `docs\tasks\2026-10-22-r28-build\r28-build-report.md`: the stretch flags and proof, Gohan's start point, the patch changes with addresses, what was removed from r27, the tests, the r28 SHA-1, the save file and its byte changes, the files copied, the diff proof, open points and my test plan. Then reply with status, the r28 SHA-1, the test count and concerns only.

