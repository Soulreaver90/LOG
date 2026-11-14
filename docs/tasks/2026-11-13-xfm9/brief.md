# XFM-9: Piccolo's ki bar. Green through Super Namek, yellow for Z+

Study and build in one pass. The owner decided the design on 2026-11-13. Do not redesign it.

## Read first

- `docs\tasks\2026-11-13-xfm9\spec.md`. It holds the decision, the measured cause and the
  recommended fix. Read all of it before you edit.
- `docs\tasks\2026-11-13-xfm9\baseline-failures.md`. It lists the 21 suite failures that already
  exist. A failure that is not on that list is yours.

## The goal, in the owner's words

Piccolo keeps a plain green bar for his base form AND for Super Namek. Neither form gets a ki pool.
Only Z+ gets a pool. The Z+ pool ramps to yellow and stays yellow.

Today Super Namek wrongly has a yellow pool. Z+ ramps orange and then snaps to yellow. The owner
reported the snap: "It shows the orange ramp and then stays yellow."

## Files you may edit

- `scripts\permanent\patches\piccolo_z_start.py` and its test
- `scripts\permanent\patches\piccolo_zplus.py` and its test
- `scripts\permanent\patches\ki_ramp.py` and its test

## Files you may NOT edit

- `scripts\permanent\patches\bf_ki_pool.py`. It ships in both masters. An edit there moves both
  master SHA-1s.
- `build_list.txt`, `build_list_dev.txt` and `build_list_core.txt`.
- Any module that is not named above. If the work needs one, stop and report instead.

## The two changes

1. **`pool_ref` must stop accepting Super Namek, and must accept Z+.** Entry 7 (Super Namek) and
   entry 24 (Z+) share form object `0x030021F0`, so an object compare cannot tell them apart. Test
   the ENTRY. Register `r3` holds the entry at the compare. The splice in `piccolo_z_start` is fixed
   size and already full, so the entry test may have to live in `piccolo_zplus`, which owns entry 24.
2. **`ki_ramp` must take its bar colour from what `pool_ref` would paint.** Today it reads bit 0 of
   the appearance entry the leader is LEAVING, which is a Saiyan rule that does not describe Piccolo.
   Then delete note 3b, the orange repaint of the Z+ bar. With Z+ yellow it has nothing to do, and
   the ledger already records that workaround as contradicted in game.

## Hard constraints

- **Entry 7's flags bit 0 must stay SET.** It drives `appearance_revert` on a leader change (bible
  B0554). Clearing it to fix a colour would change story behaviour silently.
- **Both master SHA-1s must not move.** Build both masters in memory and prove it:
  golden `778ccff59eddf7d34f432ece7e9a929595b2425f`, dev `49cdfd3c172d734956d74ecb6c6419d1a301da6e`.
- **Write no ROM, no save and no state.** Build in memory only. I build the ROM the owner plays.
- Never write under `data\`. Use absolute paths. Never `cd`.

## Proof I need

1. Decode the final blob. Show the accept path for entry 7 and for entry 24, side by side, before
   and after. A colour claim from a source diff is not proof.
2. Show that `ki_ramp` now reads the same source `pool_ref` reads.
3. Run the full suite ONCE:
   `py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent`
   Report the counts. Name any failure that is not in the baseline file.
4. Report every address you moved, and the two master SHA-1s you measured.

Do not commit. I own the commit.

One report message, then stop. Do not add a byte order mark.
