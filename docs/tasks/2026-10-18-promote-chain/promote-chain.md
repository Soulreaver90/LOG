# Promote the gi post-processing chain from scratch scripts to scripts\permanent (me, 2026-10-18 night)

Personal GBA ROM hack (Legacy of Goku II, USA). The approved Super Saiyan and Super Saiyan 2 gi frames come from `scripts\permanent\art\gi_art.py` followed by scratch scripts in `art\golden\work_r3\`. I asked (2026-10-17 3:26 PM) to promote that chain before the next default build. Read first: the headers of `gi_art.py`, `patches\gohan_gi.py`, the RE-BIBLE rows on gi_art, `docs\tasks\2026-10-18-gi-rules-night\gi-rules-night-report.md`, and these scratch scripts in full: `transplant.py`, `finish_v2.py`, `bodyfix.py`, `transform158.py`, `strips.py`, `base_step.py`, `transform_review.py`, `transform_gif.py`.

## What the chain does today

1. `gi_art.py all` writes `art\gi_base\`, `gi_ssj\`, `gi_ssj2\`.
2. `transplant.py`: golden SSJ2 heads on every gi_ssj2 frame, writes `gi_ssj2_v2\`.
3. `finish_v2.py`: golden frames in the idle slots, powered-down frames kept from the source.
4. `bodyfix.py --apply`: crotch line and arm line rules (front and back only).
5. `transform158.py`: set 158 anim 9 frames 1-3 (the SSJ to SSJ2 step) get the golden SSJ2 head, game face kept, sway, flash ring; writes `gi_ssj_v2\`.
6. Review: `strips.py`, `base_step.py`, `transform_review.py`, `transform_gif.py`.
7. The build reads gi_ssj_v2 and gi_ssj2_v2 only when `LOG_GI_SSJ=gi_ssj_v2` and `LOG_GI_SSJ2=gi_ssj2_v2` are set.

## Task

1. New module `scripts\permanent\art\gi_post.py` with steps 2-5 as named functions (`transplant_heads`, `finish_golden_slots`, `body_rules`, `ssj2_step_frames`) and a CLI `py -3 -I scripts\permanent\art\gi_post.py all` that runs them in order after `gi_art.py all`. Keep each rule and constant from the scratch scripts, with their why comments. Paths from one ROOT constant.
2. Equality first: before any cleanup, prove the module writes `gi_ssj2_v2\` and `gi_ssj_v2\` byte-identical in pixels and manifest to what the scratch scripts write from the same gi_art output. Save the scratch outputs to a temp folder first, then compare. Report the comparison. Any difference is a defect in the port unless you can show the scratch script had a bug; then report it and ask nothing, keep the scratch behavior, and list it as my item.
3. Review renderers move to `scripts\permanent\art\gi_review.py` (strips, both step sheets, the step GIF loop). Background (191, 255, 7) lime, never gray (palette index 13 is gray). Output stays under `art\...\review\` and `art\golden\work_r3\anim\`.
4. `gohan_gi.py` defaults: set 158 reads `gi_ssj_v2`, set 159 reads `gi_ssj2_v2`; the env overrides stay. Update its header. Do not change set 157.
5. Leave the scratch scripts in place, but put an exit guard at the top of each promoted one (print "promoted to scripts\permanent\art\gi_post.py" and exit 1), so a later run cannot silently write stale output. Do not touch `aura.py`, `aura_review.py` or `aura2\` (the aura is not approved).
6. Tests `scripts\permanent\tests\test_gi_post.py`: golden idle slots of gi_ssj2_v2 equal the SSJ2 goldens byte for byte; kept frames equal the source; body rules change no golden frame; step frames 1-3 keep the belt on frame 0's screen row; gohan_gi default folders. Run the whole suite: `py -3 -I -m unittest discover -s scripts\permanent -p "test_*.py"` and give the count.
7. Build a check ROM to the NEW path `archive\builds\log2_poc_r8.gba` with NO env vars set: `py -3 -I scripts\permanent\log2_build.py --out archive\builds\log2_poc_r8.gba gohan_gi ssj2_form gohan_portraits`. Its sets 157-159 frame data must equal r7's (built with the env vars). Prove it by comparing the frame tile bytes of every record of sets 157-159 in both ROMs. Append the build line to `docs\build-log.md`.
8. RE-BIBLE rows for gi_post and gi_review; describe the system as it is.

## Limits

- Never write under `data\`. Never overwrite an existing ROM in `builds\`. Never edit `art\golden\golden_*.png`.
- Python files: LF line ends, no byte order mark, no em or en dashes. Install nothing.

## Report

Save it as `docs\tasks\2026-10-18-promote-chain\promote-chain-report.md`: files and functions (file:line), the equality proof (counts per folder), test count, r8 SHA-1 and the set 157-159 comparison against r7, my items. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with status and a 3-line summary only.

