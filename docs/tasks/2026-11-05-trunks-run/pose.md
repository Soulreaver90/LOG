# The down run, read as a pose (anim 13, dir 0, set 128)

Done the way `docs\sprite-guide.md` says, and the way I skipped on the first two drafts. Name the action,
say what the body must do, find the regions by eye, then place the limbs. No pixel was drawn first.

## 1. The action, the direction, the phase

Trunks runs toward the camera. Four frames. The head sits 4 rows below its idle position in frames 0 and
2, and 2 rows below in frames 1 and 3. **That bob names the phases**: 0 and 2 are the two foot contacts,
1 and 3 are the two airborne passes. It also explains why frames 0 and 2 are the closest pair.

## 2. What the body must be doing, before looking at a pixel

Two arms, 180 degrees out of phase. In a view from the front, an arm swung back is further from the
camera, so it reads HIGH and OUT to its own side. An arm swung forward is nearer the camera, so it reads
LOW and crosses the body centre. Each arm therefore travels an oval: up and out, then down and across.

## 3. What is NOT a limb

Three traps, each one caught by looking rather than by a colour rule.

| Mass | Looks like | Actually is | How I proved it |
|---|---|---|---|
| Wide black blob, rows 27-31 | ground shadow | **the boots**, black with a gold cuff | the idle and the walk carry the same blob |
| Brown flanking the face, rows 14-19 | raised arms | **the face**, shaded dark at its edges | identical in the idle; stays skin in the Super Saiyan set, where the hair one row above turns gold |
| Grey at the upper left | trousers | **the sword hilt** over his shoulder | same pixels in the idle, which the owner has already approved |

The face is wide: it fills cols 2 to 14 at the eye rows. Only the eyes at cols 6-10 are narrow.

## 4. Where the limbs are

Skin that is NOT the face, per frame. Everything here was read off the grid, then checked against the
frame before and after it.

| Frame | Phase | FAR hand (back, high, out) | NEAR fist (forward, low, across) |
|---|---|---|---|
| run 0 | contact | cols 0-1, rows 16-18 | cols 4-7, rows 21-24 |
| run 1 | pass | cols 0-3, rows 18-20 | cols 10-13, rows 20-23 |
| run 2 | contact | cols 14-15, rows 14-17 | cols 8-11, rows 21-24 |
| run 3 | pass | cols 12-15, rows 18-20 | cols 2-5, rows 19-22 |

Frames 0 and 2 hold mirrored POSES, and so do 1 and 3. They are not mirrored pixels: flipped, frame 0
differs from frame 2 by 167 px against 98 px unflipped. Each frame is drawn by hand. Nothing may be
flipped to make another frame.

## 5. Which arm is forward, proved rather than assumed

My first write-up of the owner's annotation had these labels the wrong way round. Two pieces of evidence
agree, and both point the same way.

**Occlusion.** In frame 0, a lighter blue band runs unbroken from the right shoulder at (11,21) through
(10,22) and (9,23) into the fist. It is drawn OVER the belly, directly below the torso. **An arm behind
the body cannot be drawn over the belly.** So the right arm is the one in front.

**The owner's own sentence.** He said "the arm that is in front of him is mostly gone in yours". In the
rejected draft, that exact band at cols 8-11, rows 21-24 was filled with tank top, which deleted the
forearm. His words name the region the draft destroyed.

So: **the arm raised up and out to the side is the BACK arm. The arm whose forearm crosses the belly to
the low fist is the FRONT arm.**

## 5b. The cycle check

Follow ONE arm around all four frames and see whether it moves like an arm.

- Screen-left arm: up and out (frame 0), dropping (frame 1), crossed over the belly (frame 2), swinging
  back out (frame 3), and back to the start. One continuous oval.
- Screen-right arm runs the same oval, half a cycle behind it.

**No frame contradicts step 2.** The reading stands.

Two honest limits on this check. The screen-left wrist moves about 1.4 px from frame 0 to frame 1, then
about 7 px from frame 1 to frame 2, because the arm crosses the body in one step of a four frame cycle.
And in the two pass frames neither hand overlaps the body, so occlusion cannot say which arm is in front.
Those two frames are labelled "passing" for both arms, not front and back.

Forearm lengths run from 1.4 to 3.6 px against the guide's constraint of about 2.5 px at this size. The
short ones are the arms pointing away from the camera, which foreshorten. None is short enough to mean a
joint is in the wrong place.

## 6. What this means for the tank top, which is the whole point

Both sleeves are ARMS, not bulk.

- The far sleeve runs from the shoulder up and out to the far hand. Removing the jacket means drawing a
  **bare upper arm and forearm along that line**, not clearing it.
- The near sleeve runs from the opposite shoulder down and across to the fist. Same: a **bare arm**.
- **Almost no torso shows in the two contact frames.** The crossing forearm covers the belly. Rows 21 to
  24 hold ZERO torso pixels in any of the four frames. The whole jacket there is arm. The first pass of
  this map got that wrong, and called the same band torso in frame 0 and sleeve in frame 2.
- The torso is 3 or 4 pixels in a contact frame and 7 in a pass frame, and it sits at rows 17 to 20. One
  of them is the column beside the jaw, which the owner's approved tank idle already draws as `01`.
- A bare arm is NARROWER than a sleeve, about 3 px across on the owner's approved frames. Every pixel the
  narrower arm gives back becomes what is behind it: tank top where the torso is behind, cleared where it
  falls outside the silhouette. His five approved front frames cleared 60 of about 267 jacket pixels, so
  the clearing is real. Filling a whole sleeve with skin gives fat arms.

> [!IMPORTANT]
> Both rejected drafts failed here. The first cleared the near sleeve, which deleted the forward arm. The
> second filled it with tank top, which put the chest where the arm is. The sleeve is an ARM.

## 7. The files

- `regions.txt` letters every pixel of all four frames, and carries the joints.
- `regions_all4.png` and `regions_contact.png` draw the naming and the limbs back over the sprite.
- The transcription check passes on all four: every lit pixel has a letter, no dead pixel has one.

Rendered with `scripts\permanent\rom\show_regions.py`, which this session promoted out of the side-walk
task folder so it serves every sprite set, and gave a joints panel.

## 8. Still open

Whether the raised arm in frame 0 is his left or his right in the fiction. It changes no pixel: front and
back are settled, and that is what the drawing needs. Not holding the work on it.
