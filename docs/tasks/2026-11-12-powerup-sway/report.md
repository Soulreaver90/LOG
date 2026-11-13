# How a power-up sway is built in this ROM, and in our own work

Measured 2026-11-12 while helping the owner finish the Vegeta ascended power-up frames.

## Why it was measured

He asked for frame 3 spikier and shifted, and frame 4 the same hair shifted the other way, "just
like all previous powerups". He then pointed at our own Gohan Super Saiyan 2 work as a reference.
Two references, so both were measured rather than assumed.

## Method

Export each set with `log2_sprites.py export`, lay it out with `frames_by_anim.py --frames
--manifest`, then diff the two gold frames of `anim09_power_up/dir0_down` at several candidate
horizontal shifts. The shift with the FEWEST differing pixels is the one the artist actually used.
A single diff at `dx=0` cannot tell a shear from a move, which is the trap this avoids.

## Result

| Pair | Best shift | Differing pixels | Reading |
| --- | --- | --- | --- |
| vanilla `set:137` 02 to 03 | `dx=0` | 88, against 216 / 258 / 307 at -1 / -2 / -3 | a shear in place |
| our `set:159` 02 to 03 | `dx=-1` | 56, against 191 at 0 and 224 at -2 | a whole head move |

Vanilla's shear moves the apex 3 px, the upper rows 2, the middle 1, and nothing from the scalp
down. Our Super Saiyan 2 pair moves the whole head, face included, by 1 px.

**The two idioms are not interchangeable.** A first draft of the Vegeta pair built from the Super
Saiyan 2 reference would have moved his face.

## What the owner drew

He redrew the hair himself in Piskel and sent a straight frame plus a left and a right sway. The
file names do not say which is which, so each apex column was measured against the body centre at
col 16: left 15, straight 16, right 18. His swing is 3 px at the apex, 2 to 3 through the middle,
1 to 2 near the scalp and 0 at row 13, which is vanilla's shape with a little more motion in the
middle. Both sway frames pass `check_frames.py --set 137` on size and palette.

## Piccolo

`set:103` anim 9 is the turban and cape drop, four frames. `set:104` has no anim 9 row. His four new
Piccolo frames show the post-cape charge, so they belong on `set:104`, which is also the null row
that crashes a power-up on that set. The owner confirmed `set:104` on 2026-11-12.

## A tool gap closed

Every review tool here wants an indexed frame and he draws in RGBA, so an art round used to stall on
a file format. `scripts\permanent\art\to_indexed.py` converts against the shared OBJ palette and
refuses an unknown colour. Piskel writes a magenta key rather than alpha, so it takes `--key F800F8`.
