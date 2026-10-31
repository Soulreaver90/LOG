# Story rule for Gohan's outfit in cutscenes: armor until control after the chamber, gi after (final, 2026-10-18 6:29 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Base: r14 (`archive\builds\log2_poc_r14.gba`, SHA-1 94d3028d). Read first: `docs\tasks\2026-10-18-cutscene-portraits\cutscene-portraits-report.md` (the portrait hook and the 11 post-chamber id-59 lines), `docs\research\re-outfit.md` (ext 73, ext 51 spawns, the chamber exit script `@0x083DB59F`), `docs\RE-BIBLE.md` sections 4, 5a and the `#script` rows, the headers of `scripts\permanent\patches\gohan_gi.py` and the cutscene portrait patch.

## My rule (verbatim)

"Anything Cell Games should be with gi, no armor. The time chamber, depends: there are scenes where Vegeta and Gohan are waiting for Vegeta and Trunks inside the chamber and they should have the armor in that scene. If it's after Goku and Gohan coming out of the chamber, we discussed making a scene where Gohan gets the gi from Piccolo, but for now when he is controllable, it's all gi after, anything before that it's armor."

So: Gohan wears the armor (sprite and portrait) in every scene up to the end of the chamber-exit cutscene. From the moment the player controls him after the chamber, he wears the gi everywhere: playable sprite, NPC sprite and portrait.

## Task

1. The r14 report lists 6 lines where NPC Gohan uses the armor set 56 next to a gi portrait: chamber exit `0x083DB930`, `0x083DBABC`; Cell Games `0x083E8170`, `0x083E81A0`, `0x083E9230`, `0x083E934C`. Place each of the 11 post-chamber id-59 lines, and every scene that spawns or sets Gohan with set 56, 58 or 59 after the chamber, on the timeline: before or after the player regains control after the chamber exit. Quote the script bytes and say how you placed each.
2. Scenes before control (the chamber exit cutscene and anything earlier): Gohan shows the armor portrait, even if his record is already in entry 2. Find the smallest change that gives that, for example a raw id the hook does not map (a copy of portrait 59 at a new id, pointed to by those records only). Prove the hook still maps every after-control line.
3. Scenes after control (all Cell Games scenes and any later one): NPC Gohan uses the gi sprite. Repoint each NPC spawn or outfit call that gives Gohan set 56 (or 59 in SSJ scenes, 58 for Rage) to the gi set (157, 158 or 160) in those scripts only. List each site with its bytes. Pre-control sites stay armor; list them too.
4. Inside the chamber (the waiting scenes I name): confirm Gohan is armor there in r14, both sprite and portrait. Change nothing if so.
5. New patch file in `scripts\permanent\patches\` (style of the others: `_expect` checks, `apply(rom, alloc)`, notes), run after the cutscene portrait patch. Tests: each site's old and new bytes, the hook result for the pre-control records (armor) and the after-control records (gi).

## Build

- A second task is taking my r12fix frames into the build as r15. Build your ROM only after `docs\tasks\2026-10-18-r12fix-intake\r12fix-intake-report.md` exists. Then build `archive\builds\log2_poc_r16.gba` from the r15 patch list plus yours, no env vars.
- If that report does not exist when your patch and tests are done, do not build. Report "ready, waiting for r15" and stop.
- Copy the r15 .sav and .ss1 to the r16 names (never overwrite). Append the build line. Prove r16 differs from r15 only at your sites and your new data.
- My test plan: which slot and route reaches a Cell Games scene and the chamber exit, and what I should see.

## Parallel run

- The intake task edits `scripts\permanent\art\gi_art.py`, `gi_post.py`, `frame_lock.py`, their tests, `art\` and the goldens. Do not touch them.
- I edit `art\hand-fixes\`.
- While you work, run only your own tests. Run the whole suite once before you build. If a failure is in the intake task's files, report it and do not fix it.
- Use your own folder `scripts\one-time\2026-10-18-npc-gi\` for scripts. Never run a script from a shared scratchpad that you did not write.

## Limits

- Never write under `data\`. Never overwrite a ROM or .sav. No palette change. Install nothing.
- Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths. A shell heredoc collapses backslashes: write files with Python and check them for control characters.
- If a site cannot be placed on the timeline, list it as open and leave it unchanged.

## Report

Save it as `docs\tasks\2026-10-18-npc-gi\npc-gi-report.md`: the timeline table (site, bytes, scene, before or after control, change), the patch (file:line), test count, r16 SHA-1 or "waiting for r15", the test plan. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with status, the SHA-1, the test count and concerns only.

