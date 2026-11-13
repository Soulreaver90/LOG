# Approved transformation art, one folder per character

This holds the finished power-up animations, approved by the owner. Nothing in here is a draft.
Working history lives in `art\kits\`, which retires once every character is done.

| Character | State | Goes on | Row today |
| --- | --- | --- | --- |
| [vegeta](vegeta) | approved 2026-11-12 | `set:140` anim 9, regular Super Saiyan | empty in vanilla |
| [piccolo](piccolo) | approved 2026-11-12 | `set:104` anim 9, Super Namek | empty in vanilla |
| [trunks](trunks) | not drawn | `set:133` or `set:134` anim 9, Super Trunks | empty in vanilla |

## The shape every one of these follows

A power-up row is **4 frames, 32x32, and the SAME four frames play in all four directions**, so one
front view covers up, down, left and right. Measured on sets 103, 128, 132 and 137. See bible B2388
and B2389.

Vanilla plays the four as: the character before the change, a flash part way, then two frames that
alternate. The last two carry the motion and are the ones that repeat.

**A second transformation does not reuse the base row.** The base row starts from the unpowered
colours, which is wrong when the character is already transformed. Every super set in this game has
an EMPTY anim 9, so each of these drops into a row that is free. The base row is never touched.

## Two copies of each frame

- `rgba\` : the owner's own files, as he drew them.
- `indexed\` : the same frames on the shared OBJ palette, which is what a build writes. Made with
  `scripts\permanent\art\to_indexed.py`. Piskel exports need `--key F800F8`.

Every approved frame passes `check_frames.py --set 137` on size and palette.
