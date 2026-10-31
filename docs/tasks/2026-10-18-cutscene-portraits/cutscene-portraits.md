# Gi portraits in cutscenes after the Time Chamber (final, 2026-10-18 3:30 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Build on r13 (`archive\builds\log2_poc_r13.gba`, SHA-1 2f8de787, verified: 222 tests OK, golden lock 0). New ROM: `log2_poc_r14.gba`. Read first: `docs\research\re-portraits.md` (speaker ids, lines 50-60), `docs\RE-BIBLE.md` section 5a and the `#script` rows, the headers of `scripts\permanent\patches\gohan_portraits.py`, `ssj2_form.py`, `status_bonus.py` (for the +3 literal move).

## My report

Screenshot (pasted in chat): post-Cell, Kami's lookout, Dragon Balls, Gohan says "That was how I was able to beat Cell! My dad helped me." The field sprite is the gi; the dialog portrait is the armor. Me: "portrait still shows armor".

## My facts (verify, do not trust)

- Speaker ids 1-7 resolve through the party record's appearance +2, so they already show the gi. Cutscenes that pass a raw id > 7 read the portrait table directly (`gohan_portraits.py` header: "Cutscenes keep the armor: they use raw speaker ids"). This line is that case. CONFIRMED by the header, the exact id is not known.
- Gohan's armor ids (+2 dialog): 56 entry 0, 58 entry 1, 59 entry 2, 60 entry 3, 61 Rage, 62 Super Saiyan. Gi ids: 115 gi SSJ, 117 gi SSJ2, 119 gi base.
- The gi field sprite comes from appearance entry 2 (+1 = 157). Entry 2 is the post-chamber look.

## Task

1. Find the record of this line in the script region (type 1 record: portrait byte then text) and quote its bytes. Then list every type 1 record whose portrait byte is a Gohan id (56-62), with the text start and the story point (before or after the Time Chamber; use the nearby flags or map ids and say how you placed each one).
2. Pick the fix by the evidence and report why:
   - A. A hook in `portrait()` `@0x0800BDCC` (id > 7 path): when the raw id is a Gohan armor id and Gohan's party record is in a gi appearance entry (2, 5 or 22), return the gi frame (59 to 119, 62 to 115; other ids only if step 1 shows them after the chamber). Pre-chamber scenes stay armor by state, not by a list.
   - B. Repoint the portrait byte of each post-chamber record found in step 1.
   Prefer A if Gohan's record state is reliable during cutscenes (prove how a cutscene reads it); else B.
3. Rage in the Cell fight: if a Cell-fight cutscene shows id 61 while Gohan is in the gi Rage set (set 160 from `aura-rage`), map it to 117 (gi SSJ2 portrait). Report the records.
4. Keep the box style switch at `@0x0800B25E` unchanged (it tests the speaker id, not the portrait id). No palette change. The status page +3 path (`rom:0x86FCD0`) is not touched.
5. Tests: the hook or byte edits with the existing Thumb test interpreter (`test_ssj2.py` style): for each Gohan id, record in entry 1 (armor) returns the armor frame; in entry 2/5/22 returns the gi frame; a non-Gohan id (94 Piccolo) is unchanged.

## Build and review

1. Whole suite plus new tests; `frame_lock.py check --golden` exits 0.
2. New ROM `archive\builds\log2_poc_r14.gba`, no env vars, the r13 patch list plus the new patch. Copy `test-data\saves\log2_lv40_cellgames.sav` and the newest .ss1 to the new name (never overwrite). Append the build line.
3. Render the portrait each listed record would show, armor state and gi state, into `archive\2026-10-18-art-review-renders\cutscene_portraits.png` on (191, 255, 7). Look at it yourself.
4. My test plan: how to reach this lookout scene from the test save `test-data\saves\log2_lv40_cellgames.sav` (slot 1 Capsule Corp and slot 2 Roshi's Island are post-Cell, slot 3 is the Lookout before the Cell Games), or say which slot is past it.

## Parallel run

I hand-edits frames in `art\hand-fixes\` at the same time. Do not touch that folder, `art\gi_*`, or the golden files.

## Limits

- Never write under `data\`. Never overwrite an existing ROM or .sav in `builds\`. Never edit `art\golden\golden_*.png`.
- Install nothing. Python files: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths.
- If the record or the hook site cannot be proven, stop that part and report instead of guessing.

## Report

Save it as `docs\tasks\2026-10-18-cutscene-portraits\cutscene-portraits-report.md`: the record list with bytes and story placement, the fix chosen and why, hook listing or byte edits, test count, ROM SHA-1, review path, test plan. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with status, the SHA-1, the test count and concerns only.

