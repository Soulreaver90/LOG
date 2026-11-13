## Section 4

| Fact | Tags | Label | Src | Id |
|---|---|---|---|---|
| **Vanilla `set:137` anim 9 frames 02 and 03 are a SHEAR IN PLACE, not a whole frame move.** Differing pixels over rows 0-19 by candidate shift: `dx=0` 88, `dx=-1` 216, `dx=-2` 258, `dx=-3` 307. Every shift makes it worse, so the two frames share an origin and only the hair edges move. Per row the hair moves 3 px at the apex, 2 px in the upper rows, 1 px in the middle and 0 from the scalp down, which is a pivot at the head. This is the house idiom for a power-up sway | #sprite #form char:vegeta set:137 | C (pixel diff of the exported frames, 4 candidate shifts) | VPS | |
| **Our own `set:159` (gi Super Saiyan 2) anim 9 frames 02 and 03 are the OPPOSITE: a whole head 1 px move, face included.** Differing pixels over rows 0-16: `dx=-1` 56, `dx=0` 191, `dx=-2` 224. Rows 15 and 16 are the face and they move with the hair. So the two power-ups in this project do not share an idiom, and copying one onto the other is wrong | #sprite #form char:gohan set:158 set:159 | C (pixel diff, 3 candidate shifts) | VPS | |
| `set:103` (base Piccolo) anim 9 is the TURBAN AND CAPE DROP, not a charge: 4 frames, turban off, turban falling, a white cape swirl that fills the frame, then Piccolo revealed with the cape flying. `set:104` (Super Namek) has NO anim 9 row at all, which is the null row that crashes a power-up on that set. So Piccolo's vanilla Z transformation animation is the cape drop on the BASE set, and the Super Namek set has no power-up of its own | #sprite #form char:piccolo set:103 set:104 | C (export and manifest of both sets, base ROM) | VPS | |
| **Anim 9 uses the SAME four frame headers in all four directions, in both sets checked.** `set:137` dir 0-3 all read `38D4C4, 38D5D8, 38D6EC, 38D820`; `set:103` dir 0-3 all read `30BED0, 30C01C, 30C144, 30C240`. So one front view drawing covers up, down, left and right for a power-up row. Checked on two sets only: a set that varies by direction would not appear here | #sprite #form set:103 set:137 | C (frames_by_anim on both sets) | VPS | |
| Anim 9 frames are 32x32 in `set:103` and `set:137`, while the stand frames of `set:103` and `set:104` are 16x32. A hand drawn power-up frame must be 32x32 | #sprite set:103 set:104 set:137 | C (Pillow size read) | VPS | |

## Section 11

| Fact | Tags | Label | Src | Id |
|---|---|---|---|---|
| `scripts\permanent\art\to_indexed.py`: turn hand drawn RGBA frames into indexed frames on the shared OBJ palette, so `sprite_loop.py` and `sprite_look.py` accept them. A colour at several indices takes the lowest that is not reserved at run time (0 and 168). A colour not in the palette stops the run and is named, never matched to a near neighbour. **`--key F800F8` treats a key colour as clear: Piskel exports magenta instead of an alpha channel.** Without the flag those pixels are refused as an unknown colour, which is the safe default | #tool #sprite #palette | C | VPS | |
