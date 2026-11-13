# Trunks tank: edit kit

The base for you to edit. Front and side. Base form and Super Saiyan form.

## What to edit

| File | What it is |
|---|---|
| `EDIT_base_front_1x.png` | The front frame, 16x32, real size. Agreed, with your 11 px edit in |
| `EDIT_base_side_1x.png` | The side frame. **This is the one that needs you.** Pass one only |
| `EDIT_ssj_front_1x.png`, `EDIT_ssj_side_1x.png` | The Super Saiyan frames, same bodies |
| `EDIT_*_12x.png` | The same frames at 12x, if you would rather draw big |
| `VANILLA_*_1x.png` | The untouched jacket frames, to compare against |
| `PALETTE_legal.png` | Every colour this sprite may use |

## How the side was made

Driven from the jacket mask in code, not hand drawn. `..\trail\draw_side.py` holds it. The mask is 44 px and
exactly 44 px changed, so every other pixel is vanilla by construction. Each jacket pixel became:

| Where | Becomes |
|---|---|
| x2-4, rows 16-17, the near arm inside the sleeve | bare skin |
| rows 16-19, x6-11, the torso above the belt | black tank |
| rows 20-23, the jacket skirt | the trousers grey beside it |
| row 15, the collar at jaw level | cleared, as the front does |

The face, the chest sliver at x5, the belt at x4-6, the cyan baldric, the scabbard at x11-14, the hand at x2-3
and the legs are all vanilla and untouched.

## Two rules

**Stay on the palette.** 23 colours are legal, and they are all in `PALETTE_legal.png` with their numbers.
Any other colour fails the build. If you want a colour that is not there, tell me and I will check whether the
set can take it.

**Edit one body, not two.** Rows 16 and below are the same bytes in both files. Edit the base, tell me, and I
rebuild the Super Saiyan frame from it. That keeps the two forms in step. If you edit both by hand they drift.

If you work at 12x, send it back at 12x and I will reduce it and re-index.

## What is vanilla in these frames, and what I drew

| Rows | State |
|---|---|
| 0-14 hair, face, eyes | **Vanilla, byte for byte** |
| 15 jaw and mouth | Vanilla. Only the sword hilt moved, and the jacket collar cleared at x3-4 and x12-13 |
| 16-18 chest x6-10 | **Vanilla, byte for byte.** The exposed chest is untouched |
| 16-19 x5 and x11 | Mine: the black tank straps |
| 16-21 arms | Mine: bare arms where the jacket sleeves were |
| 19-21 belt x6-10 | Vanilla |
| 22-31 hands, legs, boots | **Vanilla, byte for byte** |

## Known soft spots

- The sword is 3 px and still reads small against skin. It was 2 px in vanilla and sat against the blue
  jacket, which is why it used to show.
- The baldric from the sword down to the belt is not drawn. Drawing it costs chest pixels, so I left it out.
- The side view is not started.
