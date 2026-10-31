# Task 5 part 1, fix round 1 (my visual review, 2026-10-17)

I looked at every form's strips at 4x and at 10x crops (archive\2026-10-18-art-review-renders\). The new method is a large step up. Base and Super Saiyan read clean in anims 0-2, 5-9, 13, 14, 16 and 21. Fix these items, then run all checks and the strip and GIF review again.

## Defects

1. **Anim 18 front, frames 18.0.2-18.0.6, all three forms.**
   - A dark navy band runs across the face, over and around the eyes. In the original it is the blue sleeves of the crossed arms in front of the face. The gi is sleeveless, so these are skin forearms with a dark outline and a blue wristband near each hand.
   - The lower torso has a light lavender block. In the original it is white with gray shading (the hands at the belly, or a glow). Decide which from the original pixels and the neighbor frames. Hands become skin fists with blue wristbands. A glow keeps its original white. Lavender is never right.
   - Back frames 18.1.2-18.1.6: a dark band sits at the waist where the original has gold armor. Use the red sash at the waist line and gi purple above it.
2. **Anim 12 front, frames 12.0.x, all three forms.** The fists above the head read as pink ears or horns. Give each fist a blue wristband below it and a clean dark outline, so it reads as a hand.
3. **Gi Super Saiyan 2, lying frames 12.2.x (shared by 12.3.x).** The Super Saiyan 2 head stands upright on a lying body. Turn the head to match the lying head in gi Super Saiyan 12.2.x: the hair lies along the ground. A 90-degree turn of a set 58 head is lossless. Repaint the join by hand.
4. **Gi Super Saiyan 2 arms-up stand-ins, 11.0.1 (and its dirs).** The fists are buried in the taller hair, and the wristbands sit at eye level. Show the fists above or on top of the hair, like gi Super Saiyan 11.0.1. Keep the face visible between the arms.
5. **Gi Super Saiyan 2 flying front stand-ins, 20.0.x and 20.2.x.** The large head covers most of the body. The raised arm and fist must read clearly in front of the hair, and a little torso must show below the chin.
6. **Wristbands, your flagged frames 7.2.3 and 16.2.3, all forms.** Add the wristband where the forearm shows, even 1 pixel.

## Keep as is (checked, not defects)

- Knocked-down frames 3.x.2-3.x.3 show the base black hair in Super Saiyan and Super Saiyan 2. The originals (sets 59 and 58) do the same.
- The pink pixel next to the head in SSJ2 16.2.1 and 16.3.1 is in the original.
- The dithered chest in the transform aura frames (anim 9) follows the original glow dither.
- Enlarged SSJ2 stand-in records (your concern 1): accepted under Ruling 30. Part 2 handles size and VRAM.

## Report

Add a "Fix round 1" section to docs\tasks\2026-10-16-task-5-gi-art\task-5-report.md. Give before and after 10x crops of every fixed frame in one sheet, archive\2026-10-18-art-review-renders\fix_r1_before_after.png.
