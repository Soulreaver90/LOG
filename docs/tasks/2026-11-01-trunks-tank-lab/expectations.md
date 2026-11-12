# What I expect to see, written before I look

Written 2026-11-01, while the lab build was still running, so these are predictions and not excuses.

Sources: `docs\sprite-guide.md` section 4, the vanilla set 128 frames, and the reference folder
`data\reference\Trunks-Tank\`.

## What the references establish

Read `sticker-png-future-trunks-render-thumbnail.png` and `z3as2o18yvnb1.jpg`:

| Feature | What the references show |
|---|---|
| Tank | Black, covers the whole torso, tucked in at the belt |
| Shoulder strap | **Wide.** It covers the inner half of the deltoid, it is not a thin cord |
| Neckline | A scoop, showing the collarbone and upper chest |
| Arms | Bare from the shoulder cap down. The largest single skin area on the figure |
| Trousers | Grey, with a gold belt. This agrees with the ROM, whose legs are `0F`, `0D` and `0B` |
| Baldric | Present only when he carries the sword. Cyan in our set, `0x4D` and `0x47` |

## The 10 checks, each with a pass condition

These are run against frames **read back out of the built ROM**, never against the PNGs. The guide is explicit:
a thing is only in the build when it has been read out of a built ROM.

| # | Check | Pass condition |
|---|---|---|
| 1 | No jacket left | No index in `51 50 4F 4E` on rows 13-23, except the 2-4 px the owner deliberately kept |
| 2 | Arm is the hero | Bare skin is the largest changed area, and sits in the back half of the torso, around x8-11 |
| 3 | Tank reads | A black mass at the chest, in front of the arm, continuous down the chest rows |
| 4 | **Silhouette shrank** | Every frame has FEWER opaque pixels than its vanilla source. A frame that did not shrink is a recolour, not a swap |
| 5 | Hem is trouser | Rows 20-23 fill with leg grey, shaded `0F` at the leading edge, never a flat wall and never a hole |
| 6 | Head untouched | Rows 0-12 byte identical to vanilla in all four frames |
| 7 | Baldric kept | Cyan `0x4D` and `0x47` still present wherever vanilla had them |
| 8 | Reads at 1x | At game size it still reads as Trunks with bare arms. The game is played at 1x |
| 9 | No flicker | Across frames 0-3 the tank's width and the shoulder line stay consistent. The arm may move; the shirt may not |
| 10 | Promotion held | The ROM bytes equal `art\trunks_tank\*.png`. Frames 1 and 3 match the approved idle's torso treatment |

## Where I expect to be wrong

Honest predictions of the weak spots, so I cannot claim them as finds afterwards:

- **Frames 0 and 2.** They came from the rule, not from his art. Frames 1 and 3 copy his idle byte for byte
  and should be clean.
- **The shoulder strap may be too thin.** The references show a wide strap. My rule gives the tank only the
  2 columns in front of the arm. On the side that may be right, since a profile hides the strap's width, but
  it is the first thing to check against check 9.
- **Walk 0's hem.** It has been fixed twice already, once for a flat grey wall and once for an over-cut chest.
- **The arm band is fixed at x8.** In a swing frame the real arm moves. Where it moved, the band is wrong.
