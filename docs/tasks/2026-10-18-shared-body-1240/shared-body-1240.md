# One gi body per pose for base, SSJ and SSJ2, plus the r12 eye-review defects (final, 2026-10-18 12:40 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Read first: `docs\tasks\2026-10-18-owner-0948-walk\owner-0948-walk-report.md` (the last pass, r12), `owner-0853-fixes-report.md` (the SSJ/SSJ2 shared body), `eye-review-r12.md` (my defect list), and the headers of `scripts\permanent\art\gi_art.py`, `gi_post.py`, `rom_sheet.py`, `frame_lock.py`. Base for this pass: r12 `archive\builds\log2_poc_r12.gba` (50a9f95d).

## Final decisions

1. **One gi body per pose across all three forms** (me: "Yes"): wherever the armor body of set 56 matches the armor body of set 59 (and of set 58 for SSJ2) at the same screen position below the head, the SSJ and SSJ2 frames take the base gi body (set 157, which carries my hand fixes); only the head differs. Same method as the SSJ/SSJ2 share of me-0853 (head boundary rule, head on top, own-body list where the armor bodies differ). The SSJ2 power-pose idle and ki charge keep their own body. List every key that keeps its own body per form and why.
2. **Back hurt sash, 2.1.2 and 2.1.3:** "Match the golden row": the sash stays on the back golden's sash row, not the armor waist band.
3. **8.0.3:** I am checking whether the white at the chest is a fist or a raised leg. Do not change 8.0.3 in this pass.

## Defects to fix (my eye review of r12, `eye-review-r12.md`)

Base: 13.0.0/13.0.2 (front run torso all skin under the crossing arm: apply my front-walk pattern), 8.0.1 and 8.2.2 (extended leg colored skin: a leg is waist to boot in any direction), 16.2.4 (sash along the leg), 3.0.3/3.1.3/3.2.3 (long horizontal sash on the lying body: the sash covers the waist span only), 12.0.0-12.0.3 (front flying: body nearly all navy, no gi purple), 2.0.3 (legs a brown and navy mass), 5.0.2 (brown mass at the lower left). SSJ/SSJ2 rows of the list are fixed by decision 1. 2.2.0/2.2.2/2.2.3 stay on draw list.
Make check_parts catch each of these on r12 first (prove it), then fix by rule.

## Build and review

1. Regenerate (`gi_art.py all`, `gi_post.py all`, `gi_review.py all`); whole suite plus new tests; `frame_lock.py check --golden` exits 0 (all 16 golden files).
2. New ROM `archive\builds\log2_poc_r13.gba`, no env vars, same patch list as r12. Copy the newest .ss1. Append the build line. Prove only sets 157-159 frame data differ from r12.
3. Before/after sheets of every changed frame per set (`archive\2026-10-18-art-review-renders\r13_changes_<set>.png`), and the full eye sheets `archive\2026-10-18-art-review-renders\eye_r13\` (per anim: `base_aNN.png` sets 56,157 dirs 0-2 at 6x; `ssj_aNN.png` sets 59,158,159 at 5x). Look at every eye sheet yourself, armor row against gi rows, part by part, and list what still looks wrong. Do not report a frame as fixed unless you looked at it.
4. check_parts counts per form, r12 to r13.

## Limits

- Never write under `data\`. Never overwrite an existing ROM in `builds\`. Never edit `art\golden\golden_*.png`.
- Do not touch `art\golden\work_r3\aura2\` or `work_r3\idle_std\` (my mockups).
- Never run a regeneration command with half-finished code: run the unit tests first, and write review output only from a consistent tree. I review what lands in `art`.
- Python files: LF, no byte order mark, no em or en dashes. Install nothing. Never `cd`; absolute paths. Review images on (191, 255, 7), never gray.

## Report

Save it as `docs\tasks\2026-10-18-shared-body-1240\shared-body-1240-report.md`: own-body keys per form with reasons, rules changed (file:line), each eye-review defect with its result, check_parts counts, what still looks wrong from your own eye pass, test count, r13 SHA-1. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with status, the r13 SHA-1, the test count and concerns only.

## Addendum (3:15 PM): power pose for Rage only, standard idle for playable SSJ2

Me: "use the power pose against Cell only, and post Cell it uses the idle pose." My facts: playable SSJ2 (set 159) unlocks with `flag:195`, which is set when Cell is beaten, so set 159 only ever plays post-Cell. Against Cell the game uses Rage (`ext 73 (0, 58)` at `@0x083EA369`, vanilla armor set 58). I then chose: Rage becomes a gi SSJ2 with the power-pose idle; playable SSJ2 uses the standard idle.
Changes to this pass:
1. Before you unify set 159, copy the current gi_ssj2_v2 (power pose, own-body keys) to `art\gi_rage\` unchanged (manifest included). It is the art for a future gi Rage set; a later pass builds it and repoints Rage. Do not build or repoint Rage now.
2. Set 159 takes the shared body in every key, including idle anim 0 and the ki charge anim 4 (no own-body exception for the power pose any more). Its idle slots use I mockup `art\golden\work_r3\idle_std\ssj2_std_d0..d3.png` (SSJ2 golden head on the SSJ golden idle body), unless your shared-body rule gives the same pixels; report any difference.
3. The 4 SSJ2 goldens `golden_gi_ssj2_d0..d3.png` become the Rage goldens: do not edit or delete them; the lock keeps them. Add the 4 mockup frames as `golden_gi_ssj2std_d0..d3.png` and extend the golden set (I review them in r13). If the lock or tests assume the SSJ2 idle slots equal `golden_gi_ssj2_*`, point those checks at the Rage art folder instead and say how.

## Addendum (3:19 PM): 8.0.3 decided

I marked `art\golden\owner\base_gi\notes_1103\75_803_1519.png` (armor 8.0.2, armor 8.0.3, gi r12 8.0.3, red boxes). The white at the chest stays a fist (arm unchanged). Two fixes:
1. **Under the neck:** gi purple sits where the chest should be bare (the V opening). Make it skin with the skin shadow pixels, the same V shape and shading as the front goldens.
2. **Foot:** the armor's dark mass at the bottom is mostly the sole of the foot, lifted a little after the kick. In the gi the shoe sits low and the sole does not read. Draw the shoe a bit higher with the dark sole under it, following the armor's boot and sole shape.
Make the rule general if other frames have a lifted foot with a visible sole (sweep and list them); otherwise fix 8.0.3 alone (all forms through the shared body).
