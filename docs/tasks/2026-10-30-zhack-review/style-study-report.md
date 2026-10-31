# Style study: our sprites and portraits against the Z Hack (2026-10-30)

This report compares our gi Gohan, base characters and portraits with the Z Hack, explains the gap, and gives a clean-room style guide and a redraw plan.

> [!WARNING]
> Inspiration only (final, 9:39 AM and 9:41 AM). No hack pixel went into `art\`, a module or a build. The side-by-side sheets are in `LOG\zhack\study\` only. Drawing starts from our own sources (vanilla frames, official Buu's Fury art, anime stills) with the hack sheets closed. The guide below is written rules and measurements, not images.

Measured build: `builds\log2_poc_r39.gba`, SHA-1 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` (build-log line of 2026-10-24 2:04 PM). No file in `art\gi_base`, `gi_ssj_v2`, `gi_ssj2_aura` or `gi_rage_aura` is newer than it, so it holds our current gi art. C.

Labels: **O** = observed in their art (sheet and frame cited), **I** = our inference, **C** = confirmed by a listing, **L** = likely, **S** = speculative. Frame keys are anim.dir.index. Dir 0 = front, 1 = back, 2 = side, 3 = mirror of dir 2 in most anims.

## SHIPPED

| Ask (brief) | Result |
|---|---|
| 1. SSJ2 Gohan and the gi, anim by anim at 4x | 17 sheets `zhack\study\ssj2_a00.png` to `ssj2_a21.png` (rows per dir: vanilla 58, ours 160, ours 159, theirs 58, 59, 172). Per-anim tables in section 1 |
| 2. Base characters with bigger hair | Sheets `zhack\study\base_<set>_a00/a01/a04.png` for 56, 58, 59, 60, 61, 130, 139. Measures in section 2 |
| 3. Goku Super Saiyan finger pose | Found: their set 158 anim 0 dir 0 (2 frames) and anim 10 frame 3. Sheets `finger_158_a00.png`, `finger_158_a10.png`, our candidates `finger_ours_62_61_a04.png`. Section 3 |
| 4. Portraits | Measures for 19 redrawn, 18 new and our 8 table portraits; sheet `zhack\study\portraits_compare.png`. Section 4 |
| 5. How they did it, why we lag | Section 5, with counts from our own frames |
| 6. Style guide and redraw plan | Sections 6 and 7 |
| 6b. Canon outfit changes | Section 8, ranked |
| 7. Observed or inference | Every guide rule carries O or I |
| 8. Clean-room rules and checker | `style_similarity.py` (pixel share and shape share after removing what both keep from vanilla), baseline in section 9 |

## PENDING

| Item | Why |
|---|---|
| Episode numbers in section 8 | Update 4:23 PM (section 12): the finger block is sourced (DBZ ep 122). The rest stay S: the searches found no reliable source |
| State 25 to anim row on an NPC (finger pose scene) | Done in the update (section 12): state 25 = anim 10, 4 frames, then hold. C |
| Names of the hack maps 3,4, 3,6, 3,9 | Not looked up (also pending in the first review) |
| Bible rows | Proposed in section 10. The brief forbids writes to `docs\RE-BIBLE.md` |
| Correction to `zhack\index.md` | Done in the update: rows 56, 58, 59 now say purple gi; rows 134, 137, 138 carry notes |
| Redrawn sets 134, 137, 138 | Done in the update (section 12) |
| Unit suite | Not run: no permanent code changed |

---

## 1. SSJ2 Gohan and the gi

This section compares our sets 159 (gi SSJ2) and 160 (gi Rage) with the hack's set 58, which the hack redrew as **SSJ2 Gohan in the purple gi** (not armor). Their 56 (base) and 59 (SSJ) are also gi Gohans: purple 88 and 89 lead their census, and suit indices 79-81 are almost gone (`style_census.txt`). C.

### Whole-set numbers

| Measure | Vanilla 58 | Ours 159 | Theirs 58 | Source |
|---|---|---|---|---|
| Cells changed in opacity per frame against vanilla (shape redrawn) | | 36.5 (aura masked: the mask {191, 2, 9, 11} also drops eye white and grey, so about 4-6 of these cells per front frame are eyes) | 100.0 | `style_geometry.txt` |
| Head width, front idle (px) | 17.5 | 17 | 16 | `style_hair.txt` |
| Body width, front idle, aura masked (px) | 19 | 15 | 13 | `style_hair.txt` |
| Hair cells, front idle | 160 | 173 | 160 | `style_hair.txt` |
| Head cells that are 46 or 44 (light) | 18.6 % | 16.4 % | 10.4 % | `style_hair.txt` |
| Head cells that are 120 (deep gold shade) | 0 | 0.8 % | 9.7 % | `style_hair.txt` |
| Head cells that are 20 (gold line) | 26.3 % | 31.9 % | 43.1 % | `style_hair.txt` |
| Head cells that are 39 (orange) | under 0.8 % (not in the top 14) | 2.3 % | 0 | `style_hair.txt` |
| Aura bolt cells (191) in the set | 0 | 1,464 | 0 | `style_census.txt` |
| Colors in the set | 57 | 48 | 48 | `style_census.txt` |

The biggest gap is the hair, not the gi colors. They use 120 as a deep shade and keep 46 and 44 as small highlights. We flood 46 and have no deep shade. C (counts), I (cause).

### Palette indices per material (count of shades)

| Material | Theirs 58 | Ours 159 |
|---|---|---|
| Gold hair | 44, 46 highlights; 37 mid; 38 and 120 shade; 20 line; 2 glints. 5 fills + line | 44, 46, 37, 38, 39; 20 line; 191 bolts. 5 fills + line, light-heavy |
| Face skin | 114 lit, 116 shade (main); 115 rare; 23 and 21 lines. 2 main tones | 114, 115, 116, 117 at about equal shares. 4 tones |
| Eyes | 64, 65 teal, 2 white, 11 grey | Same indices |
| Gi | 89 base, 88 light, 211 line. 2 + line | 89, 88 (87 in anim 9), 211. 2 + line |
| Sash | 72, 195, 77 (blue, light centre) | 26, 27 (red, my rule) |
| Wristbands | 72, 195 | 72, 195 |
| Shoes | 35 body, 34 toe light, 1 outline | 35, 34 top light, 113 |

### Per anim

Rows: what differs between theirs (58, or 59 for our 59-layout anims) and ours. Share = mean similarity per frame from `style_similarity.txt` (low is good).

| Anim | Their change (O) | Ours today (C) | Share |
|---|---|---|---|
| 0 idle | d0: narrow body, arms as 1-2 px skin columns close to the torso; crossing lapel V in 211; blue sash with a light 77 centre; flared pants with one 211 parting; hair clumps split by short 20 strokes, 120 shade, 2-3 white glints; one bang lock reaches the eye row. d1 and d2: same slim body, no bolts | Armor silhouette recolored, broader arms; hair as parallel vertical strands with full-height 20 lines; a solid 20 row across the forehead at y -11; bolts on all 6 records per dir | 0.144 |
| 1 | Poses follow vanilla. Slim body in all dirs; hair light shifts per frame (frame 1.0.2 has 27 cells of 46, frames 1.0.0, 1.0.1, 1.0.3 have 8-11) | Same head on every frame (44: 3, 46: 27-29 in d0) | 0.163 |
| 2 | Poses follow vanilla; sparks kept | Poses follow vanilla | 0.157 |
| 3 knocked down | Frame 0 head has a white flash; frame 1 hair pale (powering down); frames 2-3 black hair | Frame 1 keeps the full gold head: the transplant overwrote vanilla's dim step | 0.179 |
| 4 | **Re-posed**: frames 1 and 3 raise both fists to the shoulders (d0 and d1), frames 0 and 2 stand; white sparks over the hair | Vanilla pose with arms out, plus bolts | 0.097 |
| 5 ki blast | d0 re-posed arms; d2 follows vanilla | Vanilla poses | 0.110 |
| 6, 7, 8 melee | Follow vanilla poses and white swooshes; slimmer body; hair redrawn per frame | Follow vanilla; bolts in some frames | 0.129, 0.133, 0.162 |
| 9 power up (their 59) | **New**: frame 0 a crouch with fists in; frames 1-3 a Buu's Fury style aura oval inside the 32x32 box (yellow 8, 45, 43, white 2, pink ground glow) | Vanilla 1 px gold ring | 0.060 |
| 11 (their 59) | Frame 1 fists raised; wristbands drawn on both fists | Same pose | 0.129 |
| 12 (their 59) | d2 lying flat; slimmer legs | Same pose | 0.097 |
| 13 walk | Slimmer body, hair redrawn per frame | Bolts in frames 1-3 | 0.129 |
| 16 | 7 frames follow vanilla; hair light varies per frame | Same head on most frames | 0.086 |
| 18 kamehameha charge | Hands cupped at the chest; hair keeps white sparkles while charging | Vanilla lights the hair white in frames 3-6 (d2); ours lost it (one head on all frames) | 0.120 |
| 20 flight (their 59) | Spikier SSJ hair, slim body | Round full head | 0.096 |
| 21 revert (their 59) | Frame 1 pale gold, frame 2 brown with 20 lines, frame 3 spiky black hair (their new base hair) | Frame 1 dim gold with dark lines | 0.154 |

Direction notes: in every anim their d1 (back) shows a narrower body with the sash as one blue band, and their d2 (side) keeps a 12 px body against vanilla 16. Our d2 front-idle body is 12 px with the aura masked, so our side views are close in width; the gap is the front view and the hair. C (`style_hair.txt`).

Rage (ours 160) matches 159 except the idle and the bolts; their set has no separate Rage look. Shares for 160 are in `style_similarity.txt` (mean 0.130).

---

## 2. Base characters with bigger hair

This section measures how they widen hair inside the 32x32 box. Head zone = rows above y -7 (anchor 0,0), medians over frames, front idle (`style_hair.txt`).

| Set | Head width vanilla > theirs | Hair cells | Hair left / right of face | Body width | Height |
|---|---|---|---|---|---|
| Goku base 60 | 16 > 25 (side 16 > 23) | 129 > 172 | 3 / 2 > 8 / 6 | 16 > 17 | 17, same |
| Gohan base 56 | 15 > 16 | 119 > 146 | 3 / 1 > 3 / 2 | 15 > 13 | 15, same |
| Gohan SSJ 59 | 16 > 16 | 143 > 144 | 2 / 3 > 3 / 2 | 15 > 13 | 17, same |
| Vegeta SSJ 139 | 15 > 17 | 121 > 159 | | 16 > 17 | 17, same |
| Trunks SSJ 130 | 15 > 19 (side 13 > 17) | 140 > 173 | | 15 > 17 | 17, same |

How they do it (O, `base_60_a00.png`, `base_130_a00.png`):

- **Sideways, never up.** The top stays at y -24, the frame top. Goku's spikes reach out horizontally to 25 px; the face stays 11 px.
- **Records widen only where the hair needs it** (`style_frames.txt`, record sizes EU against the hack). Goku 60: all 142 16x32 records become 32x32 (316 of 316). Trunks 130: 50 records widen (16x32 86 to 36). Vegeta 139: 25 widen (94 to 69). Gohan 56 and Goku 61: no size change. Gohan 58 and 59 go the other way: 27 and 20 records **narrow** from 32x32 to 16x32, because the slimmer body and the tighter SSJ2 hair now fit in 16 px. C.
- **Denser fill, not only a wider box.** Gohan 56 gains 23 % hair cells in nearly the same box: fewer background gaps between spikes, and the grey 15 shine doubles (5.5 % to 11.8 % of head cells).
- **What they give up:** no body pixels and no height. The cost is data: each widened record is a raw 32x32 frame of 1024 bytes against 512 for 16x32, still inside the 0x400 slot. C (ZHK row, record counts). Their SSJ Gohan head is almost vanilla (head-zone shares within 1 % of vanilla), so the bigger look there comes from the slimmer body. I.

---

## 3. Goku Super Saiyan finger pose

This section describes their finger block, for our own Trunks scene drawing.

| Point | Finding | Label |
|---|---|---|
| Where | Their new set 158 (Super Saiyan Goku, Yardrat outfit). The pose is the **idle of dir 0**: anim 0 dir 0, both frames. Anim 10 dirs 0 and 2 hold 3 arm-down frames, then frame 3 = the same finger frame (byte-equal to 0.0.0) | C (`style_dump_finger.txt` in `zhack\study\`) |
| Rows | The bounded walker finds anims 0, 1 (dir 1 and 2 only, base Yardrat frames) and 10 (`style_frames.txt`). `new_sets.txt` lists "rows [0, 2, 4, ...]" because it counts non-null pointers. Those other rows give no valid list to the bounded walker, so they likely point at lists of other sets (the header is a copy of 54 and 62) | C (rows found), L (where the other pointers go) |
| Scene | EU table `rom:0x713224`: seq 45 swaps 62 for 158 after the power-up; seq 69 `face(158, 0)`; seq 73 Trunks `state(134, 25)` and Goku `state(158, 0)` then `state(158, 25)`; seq 75 reverts (state 21) and swaps back to 62 | C (`scenes_hack_full.txt`) |
| What state 25 shows on 158 | Anim 10: 4 frames at 16 ticks each, then a hold on frame 3. Traced in the update (section 12.3) | C (USA code) |
| Pose (measured, written only) | 3/4 view facing image left. Near arm raised in front of the body: elbow at chest level about 2 px out from the torso, forearm angled up and in, hand beside the face at eye level, 3 px wide, index finger 1 px wide and 2-3 px tall above the knuckles. The far arm is hidden. Feet and stance are the idle's | O (`finger_158_a00.png`) |
| Frames per direction | Dir 0: 2 idle frames (finger held). Dirs 0 and 2 of anim 10: 4 frames (3 arm down, 1 finger up). No dir 1 or 3 | C |

**Our candidates.** Vanilla set 62 anim 4 (Goku's surprise gesture, 4 frames per dir, black hair) has one arm raised high; it is not a finger block. Set 61 has no finger pose. Sheet `finger_ours_62_61_a04.png`. I.

**Build note for our scene (I).** Their trick is cheap: the held pose costs 2 frames because it is the idle of the facing that the scene turns to. Our version needs (a) a Super Saiyan Yardrat head (my question 10 of the Cell Jr plan) and (b) 2-4 frames: arm-down, arm rising, finger up, held. Draw from an anime still of the episode, with their sheet closed.

---

## 4. Portraits

This section compares their portraits with ours. Measures in `style_portraits.txt`; sheet `zhack\study\portraits_compare.png`.

| Point | Theirs | Ours |
|---|---|---|
| Size and format | 64x64, 8 bits per pixel, row order (the game's format) | Same |
| Palette | Shared 256-entry OBJ palette, no own palette | Same. **The "16-colour limit" does not apply**: each portrait may use any OBJ index |
| Colors per portrait | Redrawn 14-30 (mean 20.8), new 16-34 (mean 22.5); vanilla mean 24.8 | 16-35 (mean 21.6) |
| Storage | New ids 115-132: 16 raw type 0, 2 packed type 1. Redrawn: 15 packed, 4 raw (59, 62, 95, 102). Block grown in place over the id 8 frame | Raw type 0 at fixed slots `rom:0xF00000` + 0x1008 x id (`art_inject`) |
| Line work | Clean dark lines (23, 21, black only for hair masses), one line weight around the face | Lines from a shrunk anime frame: broken, uneven weight (115, 117) |
| Skin | 2 main tones plus a line tone, cel shaded | Soft gradients from the shrink |
| Eyes | Large, white sclera, single highlight, both eyes complete | Smaller or cut; 117 shows an open mouth at an odd angle |
| Hair | Strands with one highlight band; SSJ2 hair (62) has white glints | Light flood (65 near-white, my choice) |
| Composition | Face centred, whole head in frame, shoulders cropped low, 3/4 view | Off-centre crops: 115 cuts the face at the right edge, 117 cuts top and chin |
| Background | Per-character two-color gradient with ordered dither (red for Gohan, orange for Goku) | Flat or soft fills (green behind 115 and 117) |

The pixel measures (colors, lone-pixel share) do not separate the two styles: their dithered backgrounds raise their lone-pixel share. The difference is drawing, seen on the sheet. O (sheet), C (measures).

---

## 5. How they did it, and why we lag

### Their likely process (I, from the data)

1. **Hand drawn per frame on vanilla poses.** Every frame of their 56, 58, 59 and 60 changes about 88-103 cells of shape against vanilla, yet the poses, anchors and frame counts track vanilla in anims 1, 2, 5-8, 13, 16 and 18. C (counts), I (method).
2. **One model, applied everywhere.** Their gi Gohan has the same slim body, sash band and lapel V in all three forms; their SSJ head stays vanilla while the SSJ2 head is new. O.
3. **Shared ramps from the vanilla palette.** 120 appears as the deep gold shade in their 58, 59 and 172; no palette entry changed (ZHK row). C.
4. **Frame reuse.** 158's finger frame serves as idle and as anim 10 frame 3; 172 shares 41 frames with 58; new NPC sets borrow Vegeta 137 rows (first review). C.
5. **Re-posing only where it pays**: anim 4 fists, anim 9 aura oval, anim 3 flash. O.

### Root causes of our gap (C unless marked)

1. **Our gi is the armor recolored, not redrawn.** Ours 157 changes 0.0 cells of shape per frame against vanilla 56 (214 of 216 frames identical in silhouette); 158 changes 5.3 (191 of 207 identical). Theirs change 88-103 per frame, 0 identical. So our gi keeps the armor's shoulder pads as wide skin arms and the boot cuffs as shoe height. `style_geometry.txt`.
2. **Rule passes made the shading.** `gi_art.py` rule C shades each horizontal gi run by its length (bible T5 row), and `gi_post.py` `body_rules` draws crotch and arm lines by rule. I rejected a rule pass on 2026-10-18 ("worse in every way"), and later hand fixes in `art\hand-fixes\edits.py` patch frames one at a time on the same armor geometry.
3. **One SSJ2 head on every frame.** `gi_post.py` `transplant_heads` pastes the golden SSJ2 head on every `gi_ssj2` frame. Our d0 hair holds 44: 3 and 46: 27-29 cells in 17 of 18 frames of anims 1, 16 and 18; over the same frames (d0 and d2) vanilla 44 ranges 8-22 and 46 ranges 11-33 (`style_heads.txt`). That removed vanilla's per-frame hair life: the anim 3 dim step and the anim 18 charge glow.
4. **The hair ramp is light-heavy.** 46 is 13.9 % of our head cells (theirs 5.8 %); we use 39 orange (2.3 %) and almost no 120 (0.8 %, theirs 9.7 %). Our 20 lines run full height as parallel vertical strands (159 0.0.0 rows -21 to -13), so the hair reads as stripes on a helmet, not clumps.
5. **Bolts on every SSJ2 and Rage frame** (`gi_ssj2_aura`, `gi_rage_aura`, 1,464 cells of 191 in 159). They widen the silhouette and hide the body. I (effect).
6. **No model sheet.** Our goldens (`art\golden\golden_gi_base_a*_d*_i*.png`) are fixed armor frames, approved one by one. Nobody drew a turnaround (front, back, side) first, so proportions come from the armor.
7. **The review checks rules, not art.** `test_gi.py` `GoldenRuleTests` checks shoe rows, hems and run shading; sheets are reviewed at 3x on lime. Memory rule: tests and diff proofs do not check art.
8. **Portraits are shrunk anime frames.** `portrait-from-anime-report.md` step 2: a crop at 5.5 anime px per game px, then a box shrink and layer cleanup. A shrink gives soft, noisy lines and the anime frame's crop, not a composed portrait.

---

## 6. Style guide (clean room)

Rules for our own redraw. Draw from vanilla frames, official Buu's Fury art and anime stills, with the hack sheets closed. My gi rules (`global.md` and the gi drawing lessons) win over anything observed: those traits are marked **observed, not adopted**.

### Hair, gold (SSJ and SSJ2)

Ramp: 44 glint > 46 light > 37 mid > 38 shade > 120 deep shade > 20 line. White 2 for SSJ2 glints only.

- Do: keep 44 plus 46 near 10-12 % of head cells. O (their 58: 10.4 %).
- Do: use 120 as the deep shade between clumps, near 10 % of head cells. O (their 58: 9.7 %).
- Do: split clumps with short 20 strokes, 2-4 px, on diagonals that follow each spike. O (`ssj2_a00.png`, their 0.0.0).
- Do: give SSJ2 one bang lock that crosses the forehead down to the eye row. O (their 58 0.0.0).
- Do: put 1-3 white 2 glints per SSJ2 head. O.
- Do: redraw the hair on every frame where the head moves, dims (anim 3 frame 1, anim 21) or glows (anim 18). O (vanilla and theirs).
- Don't: run 20 lines the full height of the hair in parallel. I (our 159).
- Don't: use 39 orange in the hair. O (theirs 0 %).
- Don't: close the forehead with a solid row of 20. I (our 159 row -11).

### Hair, black (base)

Ramp: 15 shine > 1 fill; 23 where hair meets skin.

- Do: raise 15 shine to about 10-12 % of head cells, as 2-3 px streaks along the spikes. O (their 56: 11.8 %, vanilla 5.5 %).
- Do: widen sideways only; keep the top at y -24. Goku: 25 px wide front, 23 side, face 11. O (their 60).
- Do: fill the spike gaps; aim for about +20-30 % hair cells in the same box. O.

### Skin and face

Ramp: 114 lit > 116 shade; 115 only as a 1 px step; lines 23 and 21. 172 is our lit skin since r26 (`art\tables\palette.json` override; the RGB in `style_census.txt` is the USA value).

- Do: shade the face with 2 main tones. O (their 58: 114 and 116 lead, 115 rare).
- Don't: spread 4 skin tones evenly. I (our 159).
- Do: keep teal eyes 64 and 65 with 2 white and 11 grey. Both already do this.

### Body and proportions

- Do: front idle body about 13-14 px wide, head 16, arms as 1-2 px skin columns close to the torso. O (their 58 a00: body 13, head 16; ours 15 and 17; vanilla 19 and 17.5).
- Do: draw a turnaround first (front, back, side) and derive every frame from it, not from the armor silhouette. I.

### Gi (my colors)

Ramp: 88 light > 89 base > 211 line. Sash 30, 25, 26, 27 (red). Wristbands 77, 195, 72, 215. Shoes 32-35 with 33 highlight. No white neck piece.

- Do: draw the top as two lapel strokes in 211 crossing into a V, with skin inside. O (their 58 0.0.0).
- Do: light the outer edge of each leg with 88 and part the legs with one 211 pixel. O (their pants), matches I lesson.
- Do: let the pants flare a little at the knee. O.
- Observed, not adopted: their blue sash (72, 195, 77) and their shoes without a 33 highlight. My rule: red sash, shoes with 33.

### Outline

- Do: 211 on the gi, 23 on skin, 20 on gold hair, 1 on black hair, shoes and the shadow. O (theirs), matches ours.

### Motion and effects

- Do: re-pose only the frames that read as a move: anim 4 fists up in frames 1 and 3, anim 9 a crouch then a full aura. O (their 58 anim 4, 59 anim 9).
- Ask: keep or drop the SSJ2 bolts on idle and walk. Theirs show no bolts; sparks are white 2 pixels. O.

---

## 7. Redraw plan

Sizes count unique frame headers (a dir 3 record that reuses dir 2 is a flip, not a drawing). `style_frames.txt`.

**Model sheet first (I draw, about 9 frames):** gi Gohan base idle d0, d1, d2 (3); SSJ2 head front, back, side on that body (3); one SSJ head front (1); Goku base front and side with the wide hair (2). Every later frame starts from these.

| Order | Set | What | Frames to draw | Notes |
|---|---|---|---|---|
| 1 | 159 gi SSJ2 | Body from the model sheet, hair per frame | 163 (anim 0: 9, 1: 12, 2: 12, 3: 4, 4: 12, 5: 9, 6-8: 12 each, 9: 4, 11: 2, 12: 12, 13: 12, 16: 18, 18: 9, 20: 8, 21: 4) | Start with 0, 1, 13 (seen most), then 4, 9, 18 |
| 2 | 160 gi Rage | Same bodies as 159, Rage effect only | up to 139, most shared with 159 if I allow | My question 3 |
| 3 | 157 gi base | Bigger, denser black hair, slim body | 162 | |
| 4 | 158 gi SSJ | 157 bodies with the SSJ head | 159 | One-body rule (memory) |
| 5 | Yardrat SSJ Goku for the Trunks scene | SSJ head on 62 bodies plus the finger pose | about 4-8 (finger 2-4) | Unblocks plan item 12 |
| 6 | Goku 60, 61 | Wide hair | 173, 171 | 60 needs 32x32 records |
| 7 | Vegeta 139, Trunks 130 | Wider SSJ hair | 158, 161 | |
| 8 | Portraits 115, 117, 119, then 63, 65 | Drawn, not shrunk: centred head, 2-tone skin, dithered background | 5 | I draw (portrait pipeline memory) |

---

## 8. Canon outfit changes in the hack (6b)

The outfit sets of `zhack\index.md` that I viewed on the sheets (new sets 157-174 and redrawn 33, 54, 62, 128, 129, 132, 135). Sets 134, 137 and 138 were viewed in the update (section 12.2). Episodes are S (from memory, not sourced). "LOG fit" is our idea, L. "Frames" = the hack's unique frame headers, which include rows borrowed from Vegeta 137. "NPC" = unique frames in anims 0 and 1 only, the size of a talk NPC for us.

| Rank | Set | Character and outfit | Canon moment | Hack use | LOG fit | Frames (NPC) |
|---|---|---|---|---|---|---|
| 1 | 170 | Android 18 in new casual clothes | After she beats Vegeta, the androids take new clothes from a shop (my words; DBZ about ep 141-143, S) | NPC on maps 9,7, 11,4-6; scouter 132 | Every 18 NPC after the Vegeta fight flag | 28 (17) |
| 2 | 172 / 58 | SSJ2 teen Gohan in the purple gi | Cell Games, Gohan's awakening (about ep 182-184, S) | Beam struggle NPC; 58 for the player | Our 159, already planned | 12 (5) |
| 3 | 171 | SSJ Gohan, purple gi and white cape | Arrival at the Cell Games (about ep 166, S) | Map 14,1 NPC, scouter 130 | Cell Games arrival scene, cape removed at the fight | 21 (17) |
| 4 | 158 | SSJ Goku, Yardrat outfit, finger block | Goku blocks Trunks' sword with a finger (DBZ ep 122 "Mystery Revealed", sourced in section 12.4) | Goku meets Trunks scene | Our plan item 12 | 14 |
| 5 | 159 | Vegeta, pink shirt and yellow pants | Goku's arrival, waiting for Goku (about ep 119-120, S) | Talk NPC maps 3,4, 3,6, 3,9; arrival scene | Capsule Corp and arrival NPCs | 103 (17) |
| 6 | 160 | Bulma, curly hair, red outfit | Same arrival scene (S) | Talk NPC | Same | 56 (13) |
| 7 | 161 | Yamcha, white shirt and navy pants | Same arrival scene (S) | Talk NPC | Same | 41 (17) |
| 8 | 162 | Tien, casual | Same arrival scene (S) | Talk NPC | Same | 100 (17) |
| 9 | 169 | Bulma, orange jumpsuit and Capsule Corp cap | Android saga field trip (S) | Map 10,8 talk NPC | Same map in our flow, L | 21 (17) |
| 10 | 54 (redrawn), 157 | Future Gohan base with a power-up, then SSJ, orange gi | History of Trunks special (S) | Future prologue | Prologue, if in scope (first review question 4) | 42, 47 (15 for 54) |
| 11 | 165, 167 | Future Trunks: black tank top (base and SSJ frames); armor (base) | History of Trunks and the Cell saga epilogue (S) | Epilogue fights | Epilogue chapter | 22, 29 (9, 3) |
| 12 | 164, 166 | Future Bulma: pink shirt and red pants; white coat | Future timeline (S) | Epilogue | Epilogue | 9, 7 (8, 7) |
| 15 | 163 | Black-haired fighter in a blue suit, white flash frames, a white pod with a purple dome | Epilogue arrival (S: the time machine) | Epilogue | Epilogue chapter, if any | 11 (11) |
| 13 | 33 (redrawn) | Chi-Chi, dress recolored purple and pink | Android and Cell saga dress (S) | Chi-Chi NPC | Chi-Chi at home | 26 (17) |
| 14 | 174 | Cooler, first form | Movie 5, not series canon | Cooler scene | Only if Cooler stays | 14 (7) |

173 (Tien, new art) and the 128-138 Trunks and Vegeta edits are art fixes, not outfit changes.

---

## 9. Clean-room checker and baseline

`scripts\one-time\2026-10-30-zhack-review\style_similarity.py`. For a frame of ours and the matching frame of theirs, it drops cells where both equal vanilla, then reports the share of the remaining cells where ours equals theirs. The **shape share** counts only cells whose opacity differs from vanilla, so a shared recolor of vanilla geometry (both map armor 81 to gi 89) does not count. The control compares our frame with their frame of the next anim (chance level).

| Set (ours vs theirs, vanilla) | Mean share | Control | Shape share | Frames over 0.35 |
|---|---|---|---|---|
| 159 vs 58 (usa 58), 12 anims | 0.134 | about 0.09 | 0.009-0.056 (both 159 rows) | 0 |
| 159 vs 59 (usa 59), 5 anims | 0.107 | | see above | 0 |
| 160 vs 58 | 0.130 | | 0.014-0.056 | 0 |
| 157 vs 56 | 0.131 | | 0.000 (we drew no new shape) | 0 |
| 158 vs 59 | 0.137 | | 0.000-0.001 | 17 |

The 17 flags on 158 (highest 8.2.2 and 8.3.2 at 0.448 over 134 cells) all have shape share 0.000 over 4-22 cells: both sides recolored the same armor geometry with the same gi indices. Our `gi_ssj_v2` frames date from 2026-10-19; the hack arrived 2026-10-30. Not copying. C (dates, counts).

For new drawings, use the shape share: redraw any frame whose shape share is unusually high (for example above 0.2) after a fresh draw.

---

## 10. Proposed bible rows (tag ZHK, for me to merge)

| Fact | Tags | Label |
|---|---|---|
| Z Hack sets 56, 58, 59 are purple gi Gohans (base, SSJ2, SSJ): 88 and 89 lead each census, suit 79-81 under 70 cells; sash and wristbands 72, 195, 77; no 26 or 27 | #sprite char:gohan game:log2eu | C (`style_census.txt`) |
| Z Hack 58 head zone: 20 43.1 %, 37 11.9 %, 120 9.7 %, 38 9.4 %, 46 5.8 %, 44 4.6 %; ours 159: 20 31.9 %, 37 14.2 %, 46 13.9 %, 38 12.7 %, 39 2.3 %, 120 0.8 % | #palette char:gohan | C (`style_hair.txt`) |
| Opacity change against vanilla per frame: ours 157 0.0 (214 of 216 frames none), 158 5.3, 159 36.5 and 160 28.5 (mask 191, 2, 9, 11, which also drops some eye cells); Z Hack 56 88.0, 58 100.0, 59 100.0, 60 102.9 | #sprite char:gohan | C (`style_geometry.txt`) |
| Z Hack finger block: set 158 anim 0 dir 0 (2 frames) and anim 10 frame 3 are one frame; scene `rom:0x713224` seq 69 faces 158 to dir 0, seq 73 runs state 25 on 158 | #sprite #script char:goku game:log2eu | C (frames, script), L (state 25 = anim 10) |
| Z Hack portraits: new ids 115-132 are 16 raw and 2 packed; redrawn ids 15 packed and 4 raw (59, 62, 95, 102); 14-34 OBJ indices each | #portrait game:log2eu | C (`style_portraits.txt`) |
| Tool: `style_similarity.py` (share and shape share against a hack frame after removing shared vanilla cells; `baseline`, `geometry`) | #tool | C |

---

## 11. My questions

1. **Hair ramp first?** The cheapest visible gain is a hair pass on 159 with the guide's ramp (120 shade, less 46, no 39). Do you want that before the full redraw?
2. **Model sheet:** will you draw the 9 model frames (section 7), or should I prepare a 32x32 kit for each (palette, vanilla frame, anime still)?
3. **Rage 160:** may it share the 159 bodies and differ only in the effect?
4. **Bolts:** keep the SSJ2 and Rage bolts on idle and walk, or use small white sparks only?
5. **Sash color:** the canon Cell Games gi has a blue sash; your rule is red. Keep red?
6. **Slim body:** the guide sets a 13-14 px front body (vanilla armor 19). Is that the look you want for teen Gohan?
7. **Outfits:** which of section 8 do you want first? My ranking puts 18's casual clothes first.

---

## 12. Update 2026-10-30 4:23 PM: pending items and the Cell Jr fly row

This section closes the PENDING items I asked for and estimates a Cell Jr fly row. Same rules: inspiration only, clean room, read-only on the sources.

### 12.1 SHIPPED in this update

| Ask (final, 4:23 PM) | Result |
|---|---|
| 1. Correct `zhack\index.md` | Rows 56, 58, 59 now say purple gi Gohan (vanilla armor). Rows 134, 137, 138 carry what changed |
| 2. View 134, 137, 138 | Done: sheets `zhack\study\changed_134_a10.png`, `_a18.png`, `_a21.png`, `changed_137_a09.png`, `changed_138_a09.png`. Keys in `style_changed.txt`. Section 12.2 |
| 3. State 25 to anim row | **State 25 = anim 10**, 4 frames, then the actor holds frame 3. C (USA code). Section 12.3 |
| 4. Episode numbers | Finger block sourced: DBZ episode 122 "Mystery Revealed". The other rows stay S. Section 12.4 |
| 5. Cell Jr fly row | How the hack adds rows, and our own estimate: 4 frames per dir, 16x32, a grown header of 284 bytes. Section 12.5 |

### 12.2 Redrawn sets 134, 137, 138

| Set | Changed keys | What changed (O, sheets above) |
|---|---|---|
| 134 SSJ Trunks (NPC) | 23: 10.3.0-3, 18.3.0-6, 21.1-3.0-3 | **New anim 10 dir 3**: 4 frames, Trunks draws the sword and slashes. **Anim 18 dir 3**: a sword rush with afterimage blade streaks (7 frames). **Anim 21** (revert): vanilla shows the front view in every dir, and the hack draws back and side views for dirs 1-3 |
| 137 Vegeta | 15: 9.0.1-3, 9.1.0-3, 9.2.0-3, 9.3.0-3 | Anim 9 power-up: frame 0 gets a back view (dir 1) and side views (dirs 2, 3) where vanilla shows the front in every dir. Frames 1-3 get the Buu's Fury style aura oval, as on their Gohan 59 anim 9 |
| 138 Vegeta | 15, same keys | Same as 137 |

What this adds to the study (I):
- **They draw only the facing a scene uses.** Trunks' new sword frames exist in dir 3 only. The Goku meets Trunks scene faces Trunks to dir 3 (seq 38 `face(128, 3)`, seq 55 `face(134, 3)`) and plays `state(134, 25)` in seq 63 and 73. With 12.3, that state is anim 10: the new sword draw. C (script), I (intent).
- **They fix the vanilla shortcut of front-only rows** (anim 9 and anim 21 show the front in every dir). Our gi sets inherit that shortcut.
- Both the Trunks attack and Goku's finger raise run on state 25 (anim 10). One state gives each character a scripted 4-frame pose.

### 12.3 State 25 is anim 10, then hold

| Point | Evidence | Label |
|---|---|---|
| NPC state table | USA `rom:0x3ED21C` (word n = state n). Word 25 = object `0x03002178`. The player table `@0x083B5278` word 25 is the same object | C (bytes) |
| Vtable | `@0x08023240` `ldr r1,=0x03002178 ; ldr r0,=0x08024DBC ; str r0,[r1,#0x0]` | C (listing) |
| Enter | Vtable +0 = `@0x08011F78`: `bl 0x0800E130` (the state 3 enter), then `ldr r0,[r4,#0x48] ; add r0,#0xec ; str r0,[r4,#0x4c]`. Row = (0xEC - 0x4C) / 16 = **anim 10** | C (listing) |
| Tick | Vtable +4 = `@0x0800E142` (shared with state 3): count +0x12, frame +0x14 = count >> 4 (frames 0-3, 16 ticks each), and at 0x40 ticks `bl 0x08007688` | C (listing) |
| End | `@0x08007688` puts the hold state on the actor. Hold enter and tick are `bx lr`, so the actor keeps anim 10 frame 3 until the next state (bible row on `@0x08007688`) | C |
| Check of the method | The same enter scan gives state 12 = anim 12, 26 and 27 = anim 19, 29 = anim 2, 30 = anim 18. These match the bible PGS and BMS rows | C (scan run inline, method in `style_rows.py` notes) |
| Vanilla use | State 25 on set 61 in the Goku vs 19 scene (`@0x083D3CAF`). Set 61 anim 10 is the knock-out with hair turning black (SPR pose row) | C (site), L (that it is the heart virus collapse) |
| The hack, EU | Seq 73 `state(158, 0)`, then `state(158, 25)`: Goku stands, then raises the finger over 64 ticks (about 1.1 s) and holds it. Their 158 anim 10 frames 0-2 are arm-down and frame 3 is the finger, which matches. Their dir 0 idle is also the finger frame, so the pose survives a return to state 0 | C (USA code), L (EU runs the same table and code, not listed) |

For our Trunks scene: one `ext 57 (goku, 25)` plays a 4-frame raise and holds the last frame. Our Goku set then needs an anim 10 row of 4 frames in the facing the scene uses. Set 61 has anim 10 (knock-out frames), so a new Super Saiyan Yardrat set carries its own.

### 12.4 Episode sources

| Outfit (section 8) | Episode | Label |
|---|---|---|
| 158 finger block | DBZ episode 122 "Mystery Revealed" (anime of manga chapter 333 "The Boy from the Future"): "Goku blocks every slash with a single finger, never flinching" | Sourced: daddyjim.com episode guide (https://daddyjim.com/dragon-ball/episode/dbz-122-mystery-revealed) and the Dragon Ball Wiki technique page (https://dragonball.fandom.com/wiki/Shining_Sword_Slash) |
| 159-162 arrival cast | Same arrival arc, about episodes 118-122 | S: the sources above do not describe the outfits |
| 170 Android 18 casual | After she fights Vegeta (the episode "18 Has No Blind Spot" covers that fight) | S: the searches found no reliable page for the outfit change. The Dragon Ball Wiki page returned HTTP 402 |
| 171, 172, 157, 165, 167, 164, 166, 169, 33 | | S: not searched further |

### 12.5 A Cell Jr fly row of our own

I want the three finishing Jrs to fly in. `set:31` has rows 0, 1, 2, 5, 6, 7, 8 and an anim count of 9 (bible CJP row).

**How the fly pose works (C).** `ext 54` (fly) sets state 1, then state 12. State 12 enter `@0x0800E7A0` stores set + 0x10C (anim 12). Its tick `@0x0800E7B4` sets frame = (count >> 3) & 3. So a fly row is **4 frames per dir, looping, 8 ticks (about 133 ms) each**. On `set:31`, set + 0x10C lies past the 9-row table and reads whatever follows the header.

**How the hack adds rows (C, `style_rows.txt`).** It never grows a header. Every row it adds fills a null pointer inside the existing anim count:

| Set | Anim count | Rows the hack fills |
|---|---|---|
| 54 Future Gohan | 13 | Anim 9, all 4 dirs, 4 records each, 32x32 at dx -8, dy -24 |
| 62 Yardrat Goku | 13 | Anim 9, all 4 dirs, the same shape |
| 103 Piccolo | 23 | Anims 10 and 15, dir 1, 4 records each, 16x32 |
| 134 SSJ Trunks | unchanged | Anim 10, dir 3, 4 records |
| New sets 157-174 | 13 (headers copied from 54 and 62) | Their own rows, often a few dirs only |

All set headers stay in place with the same slot. Their NPC fly rows (anim 12) in new sets: 157 (16 records, 4 unique frames), 160 (16, 12), 170 (12, 6), 171 (4, 4, dir 0 only), 173 (16, 5), 174 (8, 3). So they draw 3-6 unique fly frames for most NPCs, not 12. I: they draw only the dirs and frames the scene shows.

**Vanilla fly rows (C, `style_rows.txt`).** Every humanoid fly row has 4 records per dir and 12 unique frames (dir 3 flips dir 2). Sizes mix 16x32 (dx 0) and 32x32 (dx -8), at dy -24. Cell's rows (28, 29, 30) are 64x64 (Cell's slot is 0x1000).

**Set 31 today (C).** Header USA `rom:0x246D80`, slot 0x400 (1,024 bytes a frame), anim count 9, header 220 bytes. All frames sit at dy -24: idle, walk, hurt and anim 8 are 16x32 at dx 0, and anims 6 and 7 are 32x32 at dx -8. 100 records, 74 unique frames.

**Estimate (I, our own technique).**

| Part | Work |
|---|---|
| Art | Dir 0 (facing down, the fly-in from the top of the screen): 4 records. 2 unique frames are enough (upright hover, legs together, a flicker or a tail sway), as the hack does for NPCs. Full row: 12 unique frames (dirs 0, 1, 2; dir 3 flips dir 2). 16x32 at dx 0, dy -24 fits an upright Jr. A horizontal dash pose needs 32x32 at dx -8. Both fit the 0x400 slot. I draw from vanilla Jr frames and anime stills |
| Header | Copy the 220-byte header to the expansion and grow it to 13 anims (12 + 64 + 13 x 16 = 284 bytes). Rows 9, 10, 11 = 0 (no state reaches them on a Jr). Row 12 = 4 pointers to new record lists (12 bytes a record; dir 3 records reuse the dir 2 frame headers with the h-flip bit) |
| Frames | Raw type 0, 520 bytes each at 16x32 (8-byte header + 512): 2 frames = 1 KB, 12 frames = 6.2 KB |
| Pointer | One set-table word. LOG already reads sets through the copied table (`rom:0x959C`, `gohan_gi`), so the word for id 31 changes there. The enemy Jr (type 26) also uses set 31 and never enters state 12, so the grown header is a safe superset. Option: a new id (161) for the NPC Jrs only |
| Script | The finishing Jrs use `ext 54 (31, x, y)` (2 px a frame), or `ext 121 (31, 12)` with `ext 136` as the Vegeta v5 fly-in did (bible VS5 row). All three Jrs share set id 31, so check how the Cell Jr trial addresses each one (CJT rows) before choosing |
| Size | Art S (2-4 frames) to M (12 frames). Code S: one small patch module that mirrors `build_set` |

My question: dir 0 only with 2 frames (cheapest, fits the fly-in from the top), or a full fly row in all dirs (12 frames)?

### 12.6 Proposed bible rows (this update)

| Fact | Tags | Label |
|---|---|---|
| NPC and player state 25 = object `0x03002178`, vtable `0x08024DBC` (set at `@0x08023240`): enter `@0x08011F78` calls `@0x0800E130`, then stores set + 0xEC (anim 10). Tick `@0x0800E142`: frame = count >> 4, and at 0x40 ticks `@0x08007688` (hold on frame 3) | #state #sprite | C (listings) |
| NPC state table USA `rom:0x3ED21C` (word n = state n). By enter scan: state 12 = anim 12, 25 = anim 10, 26 and 27 = anim 19, 29 = anim 2, 30 = anim 18 | #state #script | C |
| State 12 tick `@0x0800E7B4`: frame = (count >> 3) & 3, a 4-frame loop at 8 ticks a frame | #state #sprite | C |
| Z Hack adds anim rows only by filling null pointers within the header's anim count (54 and 62 anim 9, 103 anims 10 and 15 dir 1, 134 anim 10 dir 3). No header moved or grew. New sets use 13-anim headers copied from 54 and 62 | #sprite game:log2eu | C (`style_rows.txt`) |
| Z Hack 134 (SSJ Trunks): new anim 10 dir 3 sword draw (4 frames) and anim 18 dir 3 sword rush, played by `state(134, 25)` in the Goku meets Trunks scene. 137 and 138 anim 9 get side and back frame 0 and an aura oval | #sprite char:trunks char:vegeta game:log2eu | C (keys, script), O (look) |
| Goku's finger block on Trunks' sword is DBZ episode 122 "Mystery Revealed" | #story char:goku | Sourced (daddyjim.com, Dragon Ball Wiki) |

### 12.7 Files in this update

- `zhack\index.md` (rows 56, 58, 59, 134, 137, 138)
- `scripts\one-time\2026-10-30-zhack-review\style_rows.py` and `style_rows.txt` (row additions, fly rows, set 31)
- `style_sheets.py changed` and `style_changed.txt`; sheets `zhack\study\changed_*.png`
- `style_frames.py sizes` (record sizes and NPC frame counts, appended to `style_frames.txt`)

---

## Files

- Report: `docs\tasks\2026-10-30-zhack-review\style-study-report.md`
- Scripts (all `py -3.14 -I`, in `scripts\one-time\2026-10-30-zhack-review\`): `style_common.py`, `style_census.py`, `style_sheets.py`, `style_dump.py`, `style_hair.py`, `style_similarity.py`, `style_portraits.py`, `style_frames.py`
- Listings (same folder): `style_census.txt`, `style_metrics.txt` (superseded for hair and width by `style_hair.txt`: its hair set counts index 20 on their sash and shoes, and index 1 on shadows), `style_hair.txt`, `style_heads.txt`, `style_similarity.txt`, `style_geometry.txt`, `style_portraits.txt`, `style_frames.txt`
- Study sheets (`zhack\study\`, study only): `ssj2_a*.png`, `base_*_a*.png`, `finger_*.png`, `portraits_compare.png`, and the frame grids `style_dump_a00.txt`, `style_dump_finger.txt`

Writes: only the `style_*` scripts and listings above, `zhack\study\` and this report. Nothing in `art\`, a module, a build, `data\`, `docs\RE-BIBLE.md` or `docs\ledger\`.
