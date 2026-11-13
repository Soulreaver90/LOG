# Buu's Fury power-up reference: the dust, and what the aura is not

Exported 2026-11-12 from the Buu's Fury ROM, read only. Buu's Fury art is official and may be ported.

## The dust IS in the frames. The aura is NOT.

Buu's Fury Goku's power-up is set `rom:0x6AD1CC`, anim 10. It holds **11 records naming only 5
distinct sprites**, played in the order `0, 1, 2, 3, 2, 3, 2, 3, 2, 3, 4`. Sprite 4 is a genuine new
drawing at the end. Its Super Saiyan set `rom:0x6AD3B8` is identical in shape. Counting records
overstates the art by more than double, which is the trap: **a record can name a sprite another
record already names.**

Our own power-up is 4 records naming 4 sprites, with no reuse, in every set measured: Goku 60,
Vegeta 137, Piccolo 103, Gohan 59, Trunks 128 and 132.

**But our engine does support the technique.** Across 12 LoG II sets, 133 of 852 animation rows
reuse a sprite. `set:56` anim 18 is 7 records naming 3 sprites, order `0, 1, 2, 2, 2, 2, 2`. So
spreading 5 drawings over 11 records is something this ROM already does, just never in anim 9.

I looked at every one of the sprites in all four directions. **There is no aura in any of them.**
The ground debris IS drawn in. So the dust is pixels and costs nothing but art, while the aura is an
overlay and would need an engine change: our power-up state spawns no object at all (B0605, B0757).

## The dust, measured

- One colour: **`#D8B898`**. It is the only colour that appears in later frames and in no frame 0.
- **Rows 27-31** of the 32x32 frame, 34 to 71 pixels per frame.
- Two shapes that alternate, 55 and 71 pixels, which is what makes it shimmer.
- Frame 0 and the last frame have none: the ground is still before he starts and after he stops.
- `#580000` also appears only after frame 0. It is his open MOUTH, not debris. A colour that is new
  is not automatically the effect, and the sheet is how I caught it.

`#D8B898` is NOT in the LoG II OBJ palette. The nearest is index 242 `#E0A0A8`, 29.9 away and pink.
The mockup therefore uses `#D8A860`, a tan his own frames already carry, so it is buildable as drawn.
**The final colour is his to choose.**

## What the dust replaces

Buu's Fury draws NO shadow in these frames: the debris takes its place. His Vegeta frames have a
black drop shadow on exactly rows 27-31. Drawing the dust only on clear canvas put **zero** pixels on
his frames 3 and 4, which is how the shadow turned out to be the thing it replaces. The mockup lets
dust land on clear canvas or on his pure black shadow, and on nothing else of his.

## Folders

| Path | What |
| --- | --- |
| `frames\` | Buu's Fury's 11 power-up frames, as drawn |
| `dust\` | the same frames with ONLY the `#D8B898` debris kept, for superimposing |
| `dust_sheet.png` | the frames and the lifted dust, side by side |
| `mockup-vegeta\` | his four frames with the dust laid under him |
| `mockup-vegeta\with_dust.gif` and `without_dust.gif` | the pair to judge by eye |

## The open question that would make our transformation longer

Buu's Fury gets a richer power-up from the same amount of art by holding two frames in a 4x loop.
We could do the same with the drawings he already has. **The one unmeasured fact: the frame count
for a row may be fixed in CODE rather than read from the row** (the B0041 family, and the guard in
`vegeta_zplus.plan_anim_frames` that pins the record count to the lending row's). If it is fixed at
4 for anim 9, an 11 record row would not play. Nobody has read that yet.

## Still unknown

Which of Buu's Fury's 290 sets holds the aura, or whether it is a background effect rather than an
object. Every Buu's Fury frame is 32x32 or 16x32 (B0081), and the aura ring is bigger than the
character, so it is several sprites or a background layer. `bf_lib.py` can enumerate and decode all
290 sets, so this is findable.
