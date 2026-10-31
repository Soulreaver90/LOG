# Golden sheet (model sheet) for final approval

Do this right after the purple-arm fix (Ruling 38), in the same run. I approve this sheet before any further art propagation.

## Golden frames

- 12 frames: idle (anim 0, index 0) in dirs 0-3 for gi base, gi Super Saiyan and gi Super Saiyan 2.
- Hand-perfect each one. Use the current converted frame as the start and fix every pixel by eye at 10x. Rules:
  - Arms are skin from shoulder to wristband. Never purple.
  - Blue wristband on every visible forearm. The fist past it is solid skin with a dark outline.
  - Red sash: one band at the waist only.
  - Brown boots. Gi purple torso and trousers (pal 88, 89, outline 211).
  - Front V-neck at most 2 px deep. Side: at most 1 skin px. Back: none.
  - Super Saiyan and Super Saiyan 2 eyebrows use the hair colors, never black.
- Keep each frame's pose and record geometry (w, h, dx, dy) from the original, inside the 1024-byte slot (32x32 max).

## New Super Saiyan 2 heads (my spec, 2026-10-17)

The Super Saiyan 2 golden frames carry a new head. Draw it new. Do not take it from the Buu's Fury teen Gohan sets (I ruled them out).

- **Volume:** full, like the fan mod screenshots (final, 7:41 AM: fuller hair than LoG II's condensed Rage hair).
- **Structure:** clean, distinct spikes with clear outlines and two or three shade steps per spike, like the LoG II Super Saiyan hair in set 59. Not chaotic or noisy.
- **Shape:** from the anime and manga Super Saiyan 2 references in `data\reference\` (`GohanSuperSaiyanIINV.webp`, `desawf2-...png`, `images.jpg`, `D6FHgvhUIAATrwf.jpg`). The spikes sweep up and back, with the single bang over the forehead.
- **Colors:** existing hair indices only (the set 58 and 59 gold ramp, pal 20/21 brows).
- **Fit:** the whole frame stays inside 32x32. Body and anchor unchanged.
- Make all four directions as a set that reads as one head turning.

## Lightning (Ruling 40)

Draw 2 or 3 blue spark overlay patterns (existing blue indices, light blue with a white core) placed around the body, inside 32x32. Show each one on the Super Saiyan 2 golden idle frame, so I can judge them. Do not apply them to other frames yet.

## The sheet

Save `art\golden\golden_sheet.png`:
- One row per form (base, Super Saiyan, Super Saiyan 2), with dirs 0-3 left to right.
- Each cell: the original frame and the golden frame side by side at 10x, on one anchor, with the 32x32 box drawn faintly.
- A fourth row: the 4 new Super Saiyan 2 heads at 10x, next to a crop of the reference art.
- A fifth row: the Super Saiyan 2 golden idle front frame with each lightning pattern.
- Also save each golden frame as its own indexed PNG in `art\golden\`.

Do not propagate the golden frames or the new heads to other frames. Do not build a ROM for this step. Report the sheet path and stop.
