# Give Vegeta Z+ and Piccolo Z+ their own power-up frames

Study and build in one run. Two characters, one shape, one agent, because both touch the same
helpers. Do Vegeta first and Piccolo second.

## What the owner approved

He drew the frames himself and signed them off on 2026-11-12. Your job is to put them in the ROM
without changing any other character's power-up. **Do not redraw, retouch or re-colour one pixel.**

| Character | His frames | Go on |
| --- | --- | --- |
| Vegeta Z+ | `art\kits\2026-11-12-vegeta-powerup\his-edit\v2\build-ready\` plus `Frame_1.png` and `Frame_2.png` in `art\kits\2026-11-12-vegeta-powerup\` | `set:140`, regular Super Saiyan, anim 9 |
| Piccolo Z+ | `art\kits\2026-11-12-piccolo-powerup\P_Frame1..4.png` | `set:104`, Super Namek, anim 9 |

## Why these sets, and not the base sets

Measured by me, see bible B2385 to B2389 and `docs\tasks\2026-11-12-powerup-sway\report.md`.

- Vanilla `set:137` anim 9 is black hair, a black to gold flash, then two gold frames. That is the
  BASE Z transformation and it must not change. His Vegeta frames are gold throughout, which is
  right for Z+ because Vegeta is already Super Saiyan when Z+ plays.
- `set:140` has NO anim 9. `vegeta_zplus.py` currently makes it borrow `set:137`'s row so Z+ does not
  crash. That borrow is the thing you replace: `set:140` gets its OWN row, drawn from his art.
- `set:103` anim 9 is Piccolo's turban and cape drop, which is his vanilla Z and must not change.
  `set:104` has NO anim 9. His Piccolo frames are the post-cape charge, so they are `set:104`'s row.
- The owner chose `set:104` explicitly on 2026-11-12.

## Facts to build on

- `scripts\permanent\patches\vegeta_zplus.py` already holds `anim_row`, `plan_anim_borrow` and
  `borrow_anim_row`. Read them first. `BORROWERS = (VEG_SSJ_SET, ZPLUS_SET)` is `(140, 139)`.
- `borrow_anim_row` refuses unless the target row is empty, the source row is whole in all four
  directions, the sets share one OBJ slot, and the geometry matches. Your new writer must keep every
  one of those checks, because they are what stop a silent mismatch.
- **Anim 9 uses the SAME four frame headers in all four directions** on both sets measured
  (B2388), so one front view covers up, down, left and right. Confirm it holds for `set:140` and
  `set:104` before you rely on it.
- Anim 9 frames are 32x32 (B2389). His frames are all 32x32 and pass `check_frames.py --set 137`.
- **Piskel writes a magenta key `#F800F8`, not alpha.** Convert with
  `py -3.14 -P scripts\permanent\art\to_indexed.py <outdir> <frame.png> --key F800F8` (B2390).
  The Vegeta sway pair is already converted in `build-ready\`. The Piccolo frames are NOT: check
  whether they carry the key before you convert.
- `set:139` keeps its borrow of `set:137`. Leave it alone. It only stops a crash.

## The one thing to decide and report

Appending new frame data and a new anim 9 row is more than a pointer edit. Say in the report where
the frames and the row go, how much space they take, and what moved. If the only safe route costs
more than you think the owner expects, STOP and say so rather than forcing it.

## Scope

- `scripts\permanent\patches\vegeta_zplus.py` may grow. A new shared helper is fine.
- A new module for Piccolo Z+ art is fine. **Do NOT build Piccolo Z+ itself**: no new appearance
  entry, no form object, no portrait, no unlock. That is a separate task. You add the animation row
  and its art only.
- Do NOT touch `build_list.txt` or `build_list_core.txt`. Use or extend
  `scripts\permanent\build_list_trial_vegeta_zplus.txt`, and make
  `scripts\permanent\build_list_trial_piccolo_art.txt` if Piccolo needs its own.
- Do NOT touch `scripts\permanent\patches\bf_ki_pool.py`, `fullpower_hud.py`, `test_bf_hud.py` or
  `test_bf_ki_pool.py`. Another task owns those.
- Do NOT edit anything under `art\kits\`. Read it only. His drawings are the input, never the output.

**A second agent is working in this same tree right now**, on `bf_ki_pool.py`, `fullpower_hud.py` and their two test files. Treat a suite failure in those files as its work, not yours: name it in the report and do not fix it. Run the suite once, at the end, and say in the report that a second agent was editing while it ran.
- Build trial ROMs to `builds\mockups\2026-11-12-powerup-art\`. Say which `.sav` each seeded from.

## Done means

1. The full suite runs with a real exit code. Never pipe it into `head` or `tail`.
2. Each trial ROM is built, its SHA-1 printed, and a line added to `docs\build-log.md`.
3. Your tests prove, at minimum: `set:140` anim 9 is no longer a borrow and resolves to the new
   frames in all four directions; `set:137` anim 9 is byte for byte unchanged; `set:104` anim 9
   resolves to the new frames; `set:103` anim 9 is byte for byte unchanged; each new frame decodes
   back to the owner's pixels.
4. About 17 golden pins already fail from other work in this tree. Leave them alone and say which of
   your own failures are new.
5. Bible rows in a `rows.md` beside this brief, as `## Section N` table blocks.
6. A `report.md` beside this brief. Label every RE claim CONFIRMED, LIKELY or SPECULATIVE.

## Files to read first

- `scripts\permanent\patches\vegeta_zplus.py` : the borrow helpers and the module shape
- `docs\tasks\2026-11-12-powerup-sway\report.md` : how the sets and frames were measured
- `scripts\permanent\art\to_indexed.py` : the RGBA to index route and the Piskel key
- `docs\tasks\global.md` : the global constraints, which all apply

Report any place where my facts above disagree with the ROM you read. Deviate and flag it.

One report message, then stop. Do not add a byte order mark.
