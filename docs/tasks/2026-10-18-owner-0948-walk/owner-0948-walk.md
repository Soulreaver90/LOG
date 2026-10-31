# My walk-frame fixes: learn the rules, apply them, sweep for the same defects (final, 2026-10-18 9:48 AM)

Personal GBA ROM hack (Legacy of Goku II, USA). Run this after `owner-0853-fixes.md` is done; read its report first, and the headers of `scripts\permanent\art\gi_art.py`, `gi_post.py`, `rom_sheet.py`, `frame_lock.py`.

## Input: four hand-drawn frames (ground truth)

I hand-fixed gi base walk anim 1 dir 0, frames 0-3: `art\golden\owner\base_gi\a1_0948\62.png` (i0), `63.png` (i1), `64.png` (i2), `65.png` (i3). Each is 96x96 RGBA (32x32 at 3x), all colors on the OBJ palette. `ingest.py` in that folder converts them to 1x indices, aligns them to the r10 frames (dx 8, dy -2 for i0/i2, dy -1 for i1/i3 against the 16x32 record) and prints every changed pixel with the armor index under it. Comparison sheets: `compare_a1d0.png`, `compare_a1d0_b.png`. I say a1 dir 1 has similar issues.

My reading of my changes (LIKELY; confirm each against the pixels):
1. **i0, i2 (arm swinging across the chest):** the converter painted armor body pixels (armor 81, 10, 13) under and beside the crossing arm as skin 117 or wristband 72, so the chest read as bare skin. I restored the gi there (211 strap and edge lines, 88/89 gi) and gave the arm its own outline (23) and wristband (72), so the arm reads in front of the gi.
2. **i1, i3 (passing pose, arms at the sides):** skin 117 sat at both ends of the sash row and under it. I ran the sash (27) to the torso edges and put the dark wristband (72) at the hands.
3. **i1, i3 legs:** a dark centre line (211) between the legs on rows 24-25 (frame rows), so the two legs read apart.
4. **Shoes:** in i0/i2 the front foot comes toward the camera; I drew a full shoe on rows 28-30 (35/34) where the converter had trouser, hem and one shoe row. In i1/i3 the back foot's shoe sits one row higher (rows 26 trouser 89, 27 shoe).

## Task

1. Put the four my frames into gi_base for keys 1.0.0-1.0.3 byte for byte (I win), the same way the golden idle overlay works, and add them to the golden lock (`frame_lock.py lock --golden --replace` with the 4 new files saved as `art\golden\golden_gi_base_a1_d0_i{0..3}.png`; extend the golden set definition to include them, and say how).
2. Turn each of my change into a converter rule where it generalises (crossing arm over the torso keeps the gi and gets its own outline; sash runs to the torso edge; leg centre line; front-foot shoe in front walk frames). Each rule must leave every golden unchanged. Where a change does not generalise, say so.
3. Sweep every frame of all three forms for the same defects with at least two independent search shapes per defect (for example: armor torso pixels turned skin between the torso outlines; skin touching a sash end; legs with no gap line; front-foot shoe shorter than the armor boot's visible top). Give counts per shape and per form, list the frames, and reconcile the counts. a1 d1 must be in the list or explained.
4. Apply the rules, regenerate (`gi_art.py all`, `gi_post.py all`, `gi_review.py all`), and make a before/after sheet of every changed frame (`archive\2026-10-18-art-review-renders\walkfix_<set>.png`, lime background). Look at all of them yourself at 4x or more. Do not apply a rule that makes any frame worse by eye; report it instead.
5. Whole suite plus new tests (one per rule, and my 4 frames byte-equal in gi_base). Build `archive\builds\log2_poc_r12.gba` with no env vars (same patch list as r11), copy the newest .ss1, append the build line, and re-export `archive\2026-10-18-art-review-renders\full_r12\` and `frames_r12\` like r11.

## Limits

- Never write under `data\`. Never overwrite an existing ROM in `builds\`. Never edit the existing `golden_gi_*_d*.png` files; `frame_lock.py check --golden` must exit 0.
- Python files: LF, no byte order mark, no em or en dashes. Install nothing. Never `cd`; absolute paths. Review images on (191, 255, 7), never gray.

## Report

Save it as `docs\tasks\2026-10-18-owner-0948-walk\owner-0948-walk-report.md`: what I changed and why (confirmed per pixel group), the rules (file:line), sweep counts per shape and form, frames changed, frames left for me, test count, r12 SHA-1, export paths. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with status, the r12 SHA-1, the test count and concerns only.

## Addendum (9:52 AM): armor reference art

`art\golden\owner\armor_ref\ref_armor_base_0952.png` and `ref_armor_ssj_0952.png` (official-style art of teen Gohan in Saiyan armor). What they show, and why it matters for the converter:
- The arms, legs and torso sides are one blue bodysuit (sprite 80/81). Color alone cannot tell an arm from the torso. That is the root of defect 1 (chest under a crossing arm turned to skin).
- The chest plate is white with yellow bands and shoulder pads (sprite 2/12/13 white-gray, yellow trim). The plate ends at the waist in a yellow band; below it is bodysuit.
- Gloves and boots are white. An arm is the blue run from the shoulder pad to a white glove; a leg is the blue run from the waist to a white boot.
Use shape, not color, to split arm from torso: an arm segment is blue connected to a glove (white at its end) and to a shoulder pad; torso blue touches the chest plate or the waist band and lies between the torso outlines. Prove the classifier on my 4 frames (it must reproduce where I kept gi versus skin), then apply it. The gi has bare arms, so only the arm segment becomes skin.

## Addendum (9:55 AM): back walk a1 dir 1

My screenshot `art\golden\owner\base_gi\a1_0948\owner_note_a1d1_0955.png` (armor row over gi row, a1 d1 i0-i3): "similar issue from the back, the arms overtake the gi when swinging." In the gi row the swinging arms are skin over most of the torso sides, so the gi back shrinks to a narrow strip; the armor row shows the blue torso stays full width behind the arms. Required: the gi back keeps the width and strap shape of the base back golden (`golden_gi_base_d1.png`) from shoulder to sash in every walk frame; only the arm segment (shoulder pad to glove) becomes skin, with its own outline where it crosses the gi. This is the same root cause as defect 1; the shape classifier must fix both views. I say other frames have other issues too: put every frame your sweep flags into one review sheet per form so I can mark them.

## Addendum (9:56 AM): base anim 2, back and side

My identified my two screenshots as gi base anim 2 dir 1 and dir 2 (sparkles on frames 0-2; sheet `archive\2026-10-18-art-review-renders\owner_0956_a02.png`, armor row over gi row).
1. Back (a2 d1): "the red sash". The sash sits on different rows from the armor waist: in i2 and i3 it drops to the hips while the armor's yellow waist band stays higher. Rule to test: the sash goes on the rows of the armor's own waist band in the same frame (the yellow band at the bottom of the chest plate, per the reference art), never anchored to another frame when the waist moves. Sweep every frame of all forms for sash rows that differ from the armor waist band rows; list them with counts from two search shapes.
2. Side (a2 d2): "the body is a garbled mess, can't tell where the arms or legs are." In the crouched and turned poses, arm, torso and legs become one purple mass with skin patches. Expected: each limb reads on its own: the arm segment (shoulder pad to glove) is skin with its 23 outline, the torso is gi with 211 edges, the legs are trousers with a 211 line between them and the shoe at each boot. Apply the shape classifier here and give these frames their own before/after rows. If a pose still does not read after the rules, list it for me to draw instead of forcing it.
I will keep reporting frames; collect all of them into the per-form review sheets.

## Addendum (me, 10:00 AM): carry-overs from me-0853-fixes (r11)

Read `docs\tasks\2026-10-18-owner-0853-fixes\owner-0853-fixes-report.md` first. Base for this pass is r11 (77084b63), not r10. Build r12 on the r11 patch list.
1. The SSJ and SSJ2 bodies are now shared on 128 SSJ2 frames, and the SSJ2 arm line (R1/R2) runs only on the 11 own-body frames, because R1/R2 would change the SSJ goldens. The arm outline I draw in his 4 frames (arm segment outlined in 23 where it meets the gi) is the arm line done right. Implement it in the shared converter rules so all forms get it and every golden stays unchanged. Then retire R2 if it is no longer needed, and say so.
2. SSJ anim 4 frames 0 and 2 miss the idle armor torso by 2, 24 and 1 px (d0, d1, d2), so they keep the old torso while base anim 4 got the golden one. Find what those pixels are. If they are effect sparkles or other non-torso pixels, exclude them from the pose match by rule. Do not add a blind pixel tolerance.
3. The golden torso alternates in 157 1.0 (frames 1/3 golden, 0/2 not) and 159 4.0. My 4 frames replace 157 1.0. Check 159 4.0 by eye and report.
4. Dir 3 is not always the flip of dir 2 (anim 20 has its own dir 3 headers; anims 9, 11, 21, 14, 17 reuse dir 2 with no flip). Check every rule that assumes the mirror.

## Addendum (10:30 AM): boots and the kick swoosh

My screenshot `art\golden\owner\base_gi\notes_1030\69.png` and `70.png` (rows: armor, gi r10, gi r11; yellow boxes mark the defects). My sheet of the base attacks: `archive\2026-10-18-art-review-renders\owner_1030_a5_8.png`.
1. **69.png (side view):** the back foot's armor boot (white/gray beside the ground shadow) became black shadow pixels in the gi: no shoe on that foot. Find the frame(s) by sweep: an armor boot part (white 2 / gray 12, 13 at the bottom of a leg) with no shoe pixel (34, 35) in the gi at the same place. List every frame, all forms.
2. **70.png (front kick, my match: base anim 8 dir 0 frames 2 and 3; anims 6 and 7 share swoosh frames):** the swoosh effect and the boots are both white (index 2). In the swoosh frames the boot by the swoosh is lost or merged into the effect; in the leg-raised frame the raised leg (blue from waist to the white boot) became skin like an arm. Rules: the swoosh arc stays effect white (it is a thin curve outside the body, touching the ground shadow); a boot is the white part at the end of a leg and becomes a shoe; a leg is the blue run from the waist to a boot and becomes trousers, whatever its direction. The shape classifier from the main task must handle horizontal and raised legs.
Put every frame these sweeps flag into the per-form review sheets.

## Addendum (10:52 AM): marked frames 5.0.1, 6.0.1, 7.0.1, 8.0.1, 16.0.2, 16.0.4

My sheet `art\golden\owner\base_gi\notes_1030\71_1052.png` (gi base, rows armor / r10 / r11, red boxes mark the errors). Me: "Arms colored with gi, wrong colors for the white air effect, long red sash."
1. **Arms colored with gi (5.0.1, 6.0.1):** the forearm crossing the body (armor blue sleeve ending at a white glove) became gi purple instead of skin. Same classifier: an arm segment ends at a glove.
2. **Long red sash (8.0.1):** in the horizontal kick the sash row runs out along the extended leg. The sash covers only the waist (the armor's yellow waist band span), never a limb.
3. **White air effect recolored (16.0.4, all three rows):** swoosh pixels at the lower left became brown and shoe colors. The effect keeps its own white; only a boot at the end of a leg becomes a shoe.
4. 7.0.1 and 16.0.2 are on the sheet without a box; compare them by eye against the armor and report what you see.

## Addendum (me, 10:55 AM): part-consistency check (required deliverable)

Me: "How are you missing these?" Root cause of the misses: every check so far tested the rules (goldens unchanged, silhouette unchanged, no gi on armor skin), never whether each body part became the right thing. A forearm painted gi purple passes all of them.
Add `check_parts` to the test suite and the manifest checks, for every frame of every form:
1. Build a part map of the armor frame by shape (the classifier of this pass): arm (shoulder pad to glove), torso, leg (waist to boot), boot, glove, head, effect (swoosh, sparkles: white or light pixels outside the body outline), ground shadow.
2. The gi frame must map each part to its class: arm and glove to skin with a 23 outline and the wristband, torso to gi (88/89/211, sash only on the waist band span), leg to trouser, boot to shoe (34/35 with the hem), head unchanged except the hair rules, effect pixels unchanged, shadow unchanged.
3. Every mismatch is a defect, listed per frame with pixel counts. The goldens and my 4 frames must pass; if a golden fails, the check is wrong, not the golden.
4. Report the count before and after this pass per form, and put every frame that still fails into the per-form review sheets. All of my reported frames (a1 d0, a1 d1, a2 d1, a2 d2, the 69/70 frames, 5.0.1, 6.0.1, 8.0.1, 16.0.4) must fail the check on r11 (prove the check catches them) and pass on r12 or be listed for me.

## Addendum (11:03 AM): r11 regression in the side charge, 16.0.2, a missing purple spot

My files in `art\golden\owner\base_gi\notes_1103\`: `73.png` (two versions of a frame), `74.png` (16.0.2: armor, r10, r11), `72.png` (a close crop of one spot).
1. **REGRESSION from me-0853 fix 2 (CONFIRMED by me on `archive\2026-10-18-art-review-renders\r11_changes_157.png`):** `73.png` is gi base 4.2.0 (and 4.2.2 the same), the side ki charge. In r10 the near arm is skin with its wristband; in r11 the per-frame golden torso pasted the golden side torso over that arm, so "the arm is gone" (purple blob). The golden torso may replace only torso pixels: never pixels that the armor part map calls arm, glove or wristband. Check every frame that fix 2 changed (r11_changes_157.png, r11_changes_159.png) for the same overwrite, and make check_parts catch it.
2. **16.0.2 (`74.png`):** me: "the red sash is too short in the kick, should move it one pixel up maybe". In r11 the sash sits low and short under the crossing arm. Put it on the armor waist band rows and full waist width (the waist-band rule of the 9:56 addendum), then compare with "one pixel up".
3. **`72.png`:** me: "should be purple in that spot for the gi". It is a close crop (orange-brown, gray and purple blocks). I could not place it with certainty; LIKELY the chest of 16.0.2 r11, where brown outline lines (23) cross the gi. Find the spot by matching the crop's color blocks against the 16.0.2 frames (and other frames if no match); report where it is. The fix: gi pixels there become gi purple.
