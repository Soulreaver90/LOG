# Trunks tank: review against the Saiyan armour sets

Date: 2026-11-08. Review only. No art was drawn and no frame was edited.

Our 32 tank frames derive from set 128 (base Trunks, jacket and sword) and set 134 (Super Saiyan Trunks,
jacket and sword). Sets 129 and 130 are the same character in Saiyan battle armour (bible **B0098**).
This review asks what the armour sets show in the places the jacket and the scabbard hide.

---

## 0. Read this first: how far the armour can be trusted

The armour is a reference for one form and not for the other. I measured this before anything else,
because every finding below depends on it.

| Pair | Head rows 0-14, pixels identical | Verdict |
|---|---|---|
| set 134 vs set 130, side idle (a0 d2 i0) | **240 of 240, 100%** | set 130 IS set 134's head |
| set 134 vs set 130, front idle (a0 d0 i0) | 232 of 240, 96.7% | near identical |
| set 134 vs set 130, back idle (a0 d1 i0) | 211 of 240, 87.9% | the difference is the collar and the hilt |
| set 128 vs set 129, front idle | 131 of 240, 54.6% | **a different drawing** |
| set 128 vs set 129, back idle | 130 of 240, 54.2% | **a different drawing** |
| set 128 vs set 129, side idle | 169 of 240, 70.4% | **a different drawing** |

> [!IMPORTANT]
> **Set 130 is a valid stand-in for set 134. Set 129 is NOT a valid stand-in for set 128.**
> MEASURED, CONFIRMED.

Two independent measurements say the same thing.

1. **Hair mask, back view.** For the Super Saiyan pair the jacket set's hair is a strict SUBSET of the
   armour set's hair: 168 shared, **0 pixels** hair in 134 and not in 130, 26 the other way. That is
   exactly the "the collar and the scabbard hid it" story, so set 130 is the uncovered answer.
   For the base pair: 114 shared, **16 pixels** hair in 128 and not in 129, 76 the other way. Not a
   subset, so it is a different hair drawing.
2. **The crown row.** Set 129 sits one row below set 128 in every frame measured (y3 against y2, y4
   against y3). Set 130 sits on exactly the same row as set 134 in every frame. Shifting set 129 by
   -1, 0 or +1 never lifts the head agreement above 71%.

Set 129 wears **long hair that hangs to row 18 beside the face**. Look at panel 3 of
`front_jaw_shoulder_vs_armour.png`. It covers the jaw sides, the neck and both shoulders, which are the
very rows we wanted it to answer. So for the BASE form the armour answers nothing about the jaw, the
neck or the shoulder.

> [!WARNING]
> **The armour is a garment too, and it covers MORE skin than the jacket.**
> Bare skin below row 16, counted over all 17 keys: set 128 shows 10 to 38 pixels, set 129 shows 0 to
> 11. Set 134 shows 10 to 38, set 130 shows 0 to 12. The armour wears a full bodysuit with sleeves,
> shoulder plates, a chest plate and gloves. **Sets 129 and 130 contain no bare arm anywhere in anim 0
> or anim 1.** MEASURED, CONFIRMED.
> So the armour can settle a SILHOUETTE question and it cannot settle a bare-skin question.

### Alignment

Every frame of sets 128, 129, 130 and 134 in anim 0 and anim 1, dirs 0, 1 and 2, is 16x32 at
`dx=0, dy=-24`. MEASURED from the four vanilla-set manifests. The boxes therefore align, so for this
comparison screen coordinates and body coordinates are the same thing, and no shift table is needed.
All four sets and our own PNGs carry one identical 256-entry palette, with 0 differing entries in every
pair. MEASURED.

### A trap this review walked into twice

**Index `14` is in the SKIN ramp AND it is the dark tone of the Super Saiyan hair.** It is
`(168, 120, 56)`, which sits between skin `13` and skin `15`. **Index `01` is the black tank AND the
sword's black outline.** Every count below that touches either index was re-done with the role read by
eye, never by index alone. Where a count still rests on an index, it is labelled.

---

## 1. Findings, ranked by what they cost your eye

| # | Finding | Frames | Size | Label |
|---|---|---|---|---|
| A | The sword eats the right quarter of the Super Saiyan back head | 5 | 21 to 33 px a frame | CONFIRMED |
| B | The scabbard and the sword stand on 252 safe px, 118 unsplit px and 247+ metal px | 32 | see section 3 | CONFIRMED |
| C | We revealed 44 scabbard pixels the jacket had hidden | 14 | 44 px total | CONFIRMED |
| D | We drew a 3 px crossguard vanilla never showed | 6 | 3 px a frame | CONFIRMED |
| E | The Super Saiyan hair tip at (4,15) and (12,15) is missing in the front | 2 | 2 px a frame | CONFIRMED |
| F | The front shoulder is 1 px wider each side than any jacket reference | 6 | 2 px a frame | LIKELY |
| G | The side arm cannot be judged from the armour | 10 | not measurable | CONFIRMED negative |
| H | The magenta key is a viewer problem, not a build problem | 13 | no build effect | CONFIRMED |
| I | 18 leftover JACKET pixels (`4E`) sit in the side frames | 10 | 1 to 2 px a frame | LIKELY |

**One open question for you, in section 4: with the sword gone, does the cyan baldric stay?**
If it goes, bible rows **B0214** and **B0215**, which set the strap's path and its order across a torso
row, stop applying to this art.

---

## 2. Finding A: the Super Saiyan back head

**Sheets: `ssj_back_hair_rows10-22.png` and `ssj_back_walk_row_vs_armour.png`.**

> [!NOTE]
> **Plain answer.** The hair we drew is the right shape as far as it goes. It agrees with set 130 on
> its left half and on its bottom edge at row 15. What is wrong is that the sword and the scabbard
> occupy the head's right quarter. **So do not replace the shape. Remove the gear, and set 130 answers
> most of what is left behind.**

> [!WARNING]
> **Do NOT lift set 130's rows wholesale.** Set 130 puts bodysuit `51` at (4,15) and (10,15). A
> wholesale lift paints bodysuit blue into a tank frame. The fill has to go by class.

The idle's 27 gear pixels in rows 10 to 16, by what the fill needs:

| Class | Count | What to do |
|---|---|---|
| Set 130 draws hair | 6 | **lift from set 130** |
| Set 130 draws skin | 5 | **lift from set 130** |
| Set 130 draws bodysuit or plate | 6 | **not a lift.** Needs the guide's four-outcome call, by eye |
| Set 130 draws nothing | 10 | **cut to transparent** |

21 of the 27 are in rows 10 to 15. The other 6 are in row 16.
Separately, 5 hair pixels in the LEFT half disagree on shading. They are listed at the end of this
section and they are a different decision, not part of the removal.

Frame key `trunks_tank_ssj_back.png`, set 134, anim 0 dir 1 index 0, headers `0x373F38` and `0x376930`.

**Gear pixels in rows 10 to 16, and what set 130 draws underneath them.** Gear here is the grey ramp,
the scabbard orange ramp, and black `01` at x11 or further right, which is the sword outline in this
view. Black at x7 or further left is the tank strap and is excluded. That split was read by eye from the
index grid. MEASURED.

| Frame | Gear px, rows 10-16 | over hair | over skin | over suit or plate | over clear |
|---|---|---|---|---|---|
| `trunks_tank_ssj_back.png` | 27 | 6 | 5 | 6 | 10 |
| `trunks_tank_ssj_back_walk_0.png` | 28 | 13 | 3 | 7 | 5 |
| `trunks_tank_ssj_back_walk_1.png` | 32 | 9 | 5 | 11 | 7 |
| `trunks_tank_ssj_back_walk_2.png` | 21 | 5 | 5 | 3 | 8 |
| `trunks_tank_ssj_back_walk_3.png` | 33 | 9 | 5 | 12 | 7 |

The idle, coordinate by coordinate:

| Set 130 draws | Our pixels | Note |
|---|---|---|
| hair | (13,11) (9,13) (10,13) (9,14) (10,14) (9,15) | **6 px of hair the sword took** |
| skin | (13,12) (12,13) (13,13) (11,14) (12,14) | the nape, 5 px |
| suit or plate | (10,15) (8,16) (9,16) (10,16) (11,16) (12,16) | the scabbard crossing the upper back |
| nothing at all | (14,11) (15,11) (14,12) (15,12) (14,13) (15,13) (13,14) (11,15) (12,15) (13,16) | **the hilt stands outside the armour's whole silhouette** |

By eye on the sheet: in all five of our back frames the gold bell has a black and grey block punched
through its right side at rows 11 to 15. Set 130's bell is clean and symmetric. The four 1x thumbnails
under our frames in `ssj_back_walk_row_vs_armour.png` all read as a dark smudge on the right of the
head. The four armour thumbnails do not.

**Hair SHADING.** Inside the rows that both draw as hair, our back hair is mostly flat `14` where set
130 alternates `78` and `14`. The disagreement is **5 pixels**: (5,13), (6,13), (7,13), (8,13) and
(7,14). This is not a defect. Our Super Saiyan back hair came from your base back art, recoloured by
role (`trunks_tank.py`, bible row TSB), and set 130 is the authentic Super Saiyan shading.
**Taking set 130's shading overrides your TSB role mapping in those 5 pixels, so it is your call.**

**Our base back frame is a separate question.** Set 129 cannot answer it, for the reason in section 0.

---

## 3. Finding B: the scabbard and sword job

**The armour carries no scabbard, no sword and no hilt.** I checked all 17 unique keys in both armour
sets, 34 frames, with nothing clipped. **32 of 34 carry zero pixels of the scabbard orange ramp
(`21 22 23 25 27`).** The two that do are `set130 a0d2i0` and `set130 a0d2i1`, each with one pixel, at
**(7,30), index `25`, which is a boot sole highlight at the bottom of the frame.** MEASURED, CONFIRMED.
So the armour agrees with your decision to drop the scabbard, and it shows what belongs in the space.

### How each number was made, and what it cannot do

- **Scabbard orange**: runs of `21 22 23 25 27` above the boots, with the belt excluded. The belt is
  identified from set 130, which draws it olive `28 29` at **x5-x9, rows 20-21 only**. MEASURED.
- **Sword metal**: grey `09 0A 0B 0C 0D 0E 0F` in rows 10 to 21 where **set 130** draws hair, skin or
  nothing. Set 129 is never used as a control, for the reason in section 0. **The number in the table
  is taken from the Super Saiyan frame of each key**, because set 130 is a valid control only there.
  Our base and Super Saiyan frames are byte identical from row 16 down. I checked this: **0 differing
  pixels in rows 16 to 31, on all 15 keys that exist in both forms.** MEASURED, and it agrees with
  bible row **B0222**. So the BODY gear is the same in both forms.
  The HEAD rows 10 to 15 differ between the forms, as they must, and running the same control on a base
  head disagrees on 6 of the 15 keys by 1 or 2 px. Those 6 disagreements are head rows only, and the
  base head's metal count is **NOT measured**, because set 130 cannot control a purple head.
  Keys `a0 d0 i0` and `a0 d0 i1` exist only in the base form, so their 10 and 9 carry the same caveat.
  **This column is a LOWER BOUND.** It misses metal standing over the armour's own plate or suit, which
  is most of the scabbard's grey bands in the back view, and it misses everything below row 21.
- The cyan baldric `47 4D` is NOT in these totals. It has its own table in section 4.

> [!WARNING]
> **The back view is NOT split into belt and scabbard, and nobody should erase from it yet.**
> In the back view the scabbard crosses the belt at rows 20 to 22, and both are the same orange ramp.
> I could not separate them by eye at this scale with confidence, so I have not guessed.
> **Rows 10 to 19 are scabbard with no belt in them**, because set 130 puts its belt at rows 20-21 only.
> That part is safe. **Rows 20 to 23 are a mixed band** and need a hand written region map
> (`scripts\permanent\rom\show_regions.py`) before one pixel is removed.

### Per frame

| Frame | Key | Scabbard orange | of which safe (rows 10-19) | of which mixed (rows 20-23) | Sword metal (min) |
|---|---|---|---|---|---|
| `trunks_tank_base_front.png` | a0 d0 i0 | 2 | n/a | n/a | 10 |
| `trunks_tank_base_back.png` | a0 d1 i0 | 26 | 13 | 13 | 16 |
| `trunks_tank_base_side.png` | a0 d2 i0 | 9 | n/a | n/a | 0 (see note) |
| `trunks_tank_base_front_stand1.png` | a0 d0 i1 | 2 | n/a | n/a | 9 |
| `trunks_tank_base_side_stand1.png` | a0 d2 i1 | 9 | n/a | n/a | 0 (see note) |
| `trunks_tank_base_side_walk_0.png` | a1 d2 i0 | 12 | n/a | n/a | 1 |
| `trunks_tank_base_side_walk_1.png` | a1 d2 i1 | 9 | n/a | n/a | 0 (see note) |
| `trunks_tank_base_side_walk_2.png` | a1 d2 i2 | 2 | n/a | n/a | 0 |
| `trunks_tank_base_side_walk_3.png` | a1 d2 i3 | 9 | n/a | n/a | 0 (see note) |
| `trunks_tank_base_front_walk_0.png` | a1 d0 i0 | 1 | n/a | n/a | 8 |
| `trunks_tank_base_front_walk_1.png` | a1 d0 i1 | 2 | n/a | n/a | 11 |
| `trunks_tank_base_front_walk_2.png` | a1 d0 i2 | 0 | n/a | n/a | 7 |
| `trunks_tank_base_front_walk_3.png` | a1 d0 i3 | 2 | n/a | n/a | 11 |
| `trunks_tank_base_back_walk_0.png` | a1 d1 i0 | 29 | 15 | 14 | 14 |
| `trunks_tank_base_back_walk_1.png` | a1 d1 i1 | 26 | 16 | 10 | 15 |
| `trunks_tank_base_back_walk_2.png` | a1 d1 i2 | 21 | 9 | 12 | 16 |
| `trunks_tank_base_back_walk_3.png` | a1 d1 i3 | 26 | 16 | 10 | 15 |
| `trunks_tank_ssj_side.png` | a0 d2 i0 | 9 | n/a | n/a | 0 (see note) |
| `trunks_tank_ssj_side_stand1.png` | a0 d2 i1 | 9 | n/a | n/a | 0 (see note) |
| `trunks_tank_ssj_side_walk_0.png` | a1 d2 i0 | 12 | n/a | n/a | 1 |
| `trunks_tank_ssj_side_walk_1.png` | a1 d2 i1 | 9 | n/a | n/a | 0 (see note) |
| `trunks_tank_ssj_side_walk_2.png` | a1 d2 i2 | 2 | n/a | n/a | 0 |
| `trunks_tank_ssj_side_walk_3.png` | a1 d2 i3 | 9 | n/a | n/a | 0 (see note) |
| `trunks_tank_ssj_front_walk_0.png` | a1 d0 i0 | 1 | n/a | n/a | 8 |
| `trunks_tank_ssj_front_walk_1.png` | a1 d0 i1 | 2 | n/a | n/a | 11 |
| `trunks_tank_ssj_front_walk_2.png` | a1 d0 i2 | 0 | n/a | n/a | 7 |
| `trunks_tank_ssj_front_walk_3.png` | a1 d0 i3 | 2 | n/a | n/a | 11 |
| `trunks_tank_ssj_back.png` | a0 d1 i0 | 26 | 13 | 13 | 16 |
| `trunks_tank_ssj_back_walk_0.png` | a1 d1 i0 | 29 | 15 | 14 | 14 |
| `trunks_tank_ssj_back_walk_1.png` | a1 d1 i1 | 26 | 16 | 10 | 15 |
| `trunks_tank_ssj_back_walk_2.png` | a1 d1 i2 | 21 | 9 | 12 | 16 |
| `trunks_tank_ssj_back_walk_3.png` | a1 d1 i3 | 26 | 16 | 10 | 15 |
| **TOTAL, 32 frames** | | **370** | | | **247** |

**The job size, stated in three parts rather than one misleading number:**

| Part | Pixels | Confidence |
|---|---|---|
| Scabbard orange, safe to remove | **252** | CONFIRMED. Front, side, and back rows 10-19 |
| Scabbard orange, belt not split out | **118** | Back rows 20-23 only. **May contain belt** |
| Sword metal | **247 and up** | Lower bound. See the three gaps in section 10 |

**Every one of the 32 frames carries scabbard or sword. None is clean.**

> [!NOTE]
> **The side "metal 0" rows are a row-window artefact, not a clean frame.**
> The side idle's scabbard chape sits at (14,23) index `0C` and (13,24) (14,24) index `0D`, which is
> below the row 21 window. Read by eye, the side idle's scabbard is **12 pixels**:
> (11,20) (12,20) (11,21) (12,21) (11,22) (12,22) (13,22) (12,23) (13,23) orange, then (14,23) (13,24)
> (14,24) metal. Set 130 draws nothing at x11 or beyond on rows 20 to 24. CONFIRMED.
> The same 3 chape pixels apply to the 8 side frames with the idle geometry.

### The job by view

| View | Frames | Typical size | What it is |
|---|---|---|---|
| Back | 10 | 35 to 45 px | the full scabbard diagonal plus the hilt and the guard. **The big job, and the one needing a region map** |
| Side | 10 | 2 to 15 px | the block behind the hip at x11-x13, rows 20-24, plus its chape |
| Front | 12 | 7 to 13 px | the hilt and the guard at x0-x4, rows 10-16, plus 2 px past the left hip |

---

## 4. Finding C: 44 scabbard pixels we added, and the baldric question

The sprite guide rule "an accessory under the garment is continuous, reveal it where the garment hid it"
was applied to the scabbard. Those reveals are now pure waste, and they are the easiest part of the job
to undo, because they are the same two or four coordinates every time.

| Where | Pixels | Frames |
|---|---|---|
| Side view, (11,20) and (11,21) revealed behind the hip | 2 a frame | 8 side frames |
| Front view, (11,21) and (12,21) revealed past the left hip | 2 a frame | 6 front frames |
| Back walk 0, 4 extra scabbard pixels | 4 a frame | 2 back frames |
| **Total** | **44** | **14 frames** |

MEASURED by comparing our orange pixel set against the vanilla frame at the same key. CONFIRMED.

### The cyan baldric, and the question I cannot answer for you

The baldric is the cyan strap `47` and `4D` that carries the sword across the chest. **You said
"scabbard". You did not say "baldric". A strap with no sword on it has nothing to carry.**

**110 cyan pixels across the 32 frames, a net 40 of them reveals we added.** MEASURED.

| Frames | Ours a frame | Vanilla a frame | Revealed |
|---|---|---|---|
| 6 front frames with the full strap | 9 | 5 | +4 |
| `base_front_walk_0`, `ssj_front_walk_0` | 7 | 5 | +2 |
| `base_front_walk_2`, `ssj_front_walk_2` | 8 | 5 | +3 |
| 6 side frames with the idle geometry | 2 | 1 | +1 |
| `base_side_walk_0`, `ssj_side_walk_0` | 1 | 0 | +1 |
| `base_side_walk_2`, `ssj_side_walk_2` | 4 | 4 | 0 |
| `ssj_side`, `ssj_side_stand1` | 2 | 3 | **-1** |
| all 10 back frames | 0 | 0 | 0 |

> [!IMPORTANT]
> **The question: with the sword and the scabbard gone, does the cyan baldric go too?**
> If it goes, that is 110 more pixels and the chest opens up by 9 px in each front frame.
> If it stays, it needs a reason to be there, and the 40 reveals still have to be re-judged.
> Sets 129 and 130 wear no strap of any kind, so the armour cannot decide it.

**The `-1` on `ssj_side` and `ssj_side_stand1` is NOT our mistake.** It is the one-body rule working as
written, and it is worth recording. MEASURED coordinates:

| Frame | Cyan pixels |
|---|---|
| vanilla set 128 side idle | (5,19) |
| vanilla set 134 side idle | (4,17) (5,19) (5,20) |
| **our base side idle** | (5,19) (7,20) |
| **our Super Saiyan side idle** | (5,19) (7,20) |

Vanilla's two forms disagree about the strap in the side view, by 2 pixels. Our two frames agree,
because they share one body. So the Super Saiyan frame DROPS vanilla 134's (4,17) and (5,20). That is
the documented trap in the sprite guide, "vanilla does not always obey this ... state what is dropped".
I grepped `RE-BIBLE.md` for `baldric` and `one body` and found no row that states this drop, so it
looks unrecorded. 2 pixels, in 2 frames.

### A new finding: 18 leftover JACKET pixels in the side frames

I chased index `4E` because it sits on the strap's diagonal in the front view. It is not strap.

- **`4E` is `(88, 48, 248)`, the top step of the jacket ramp** `4E 4F 50 51`. Bible row **B0319** says
  so, and `sprite_guard.py`'s own usage line gives the garment set as `51,50,4F,4E`.
- **The front frames removed every `4E`.** Vanilla set 128's front has it at (5,18) and (10,20). Our
  front frames have none. Correct.
- **The side frames kept it.** Our side frames hold `4E` at (4,17) and (5,20). MEASURED:

| Frames | `4E` kept |
|---|---|
| `base_side`, `base_side_stand1`, `base_side_walk_1`, `base_side_walk_3` | (4,17) and (5,20) |
| `ssj_side`, `ssj_side_stand1`, `ssj_side_walk_1`, `ssj_side_walk_3` | (4,17) and (5,20) |
| `base_side_walk_2`, `ssj_side_walk_2` | (4,17) only |
| `base_side_walk_0`, `ssj_side_walk_0` | none |
| **Total** | **18 px, in 10 frames** |

(4,17) is the stronger case. Vanilla set 128's neighbours there are `51 51 51` above and to the left,
so it is a jacket highlight sitting inside the jacket mass. In our frame it is a 1 px violet sliver on
the chest's front edge, with skin `13` beside it and black tank `01` behind it.
(5,20) sits between belt orange `25` and grey `09`, so it is less certain.

**LIKELY, not CONFIRMED**, because the role comes from the palette ramp, the neighbours and bible row
B0319, not from a hand written region map. It is cheap to settle: look at (4,17) at 12x and say what it
is. The edit kit's own README claims rows 16-17 at x4-x6 became bare skin, so (4,17) was meant to go.

---

## 5. Finding D: a crossguard vanilla never drew

Frame key `trunks_tank_base_front.png`, row 15 and row 16.

| Pixel | Vanilla set 128 | Ours | set 129 |
|---|---|---|---|
| (3,15) | `51` jacket | `0B` guard | hair |
| (4,15) | `51` jacket | `0D` guard | hair |
| (2,16) | `51` jacket | `0B` guard | hair |

We followed the guide rule "copy the gear's SHAPE, not just its position" and drew the full 3 px
crossguard, `0D 0B 0D` over `0D 0B`, into space the jacket had filled. Vanilla set 128 shows only `0D`
at (2,15) and `0D` at (1,16). So **3 pixels a frame of sword are ours, not vanilla's.**

CONFIRMED, and I checked which frames: `base_front`, `base_front_stand1`, `base_front_walk_1`,
`base_front_walk_3`, `ssj_front_walk_1`, `ssj_front_walk_3`. **6 frames.** The other four front frames
(`walk_0` and `walk_2` in both forms) carry no added guard pixel.

---

## 6. Finding E: the Super Saiyan hair tip at the jaw, front view

**Sheet: `front_jaw_shoulder_vs_armour.png`, panels 4, 5 and 6.**

| Pixel | set 134 (jacket) | set 130 (armour) | Ours |
|---|---|---|---|
| (4,15) | `51` collar | **`14` gold hair** | `0D` sword guard |
| (12,15) | `51` collar | **`14` gold hair** | `00` clear |

Set 130's head rows 0-14 are 96.7% identical to set 134's in this frame, so it is good evidence. The
armour says the gold hair hangs one row lower than our frame shows, at x4 and x12, either side of the
jaw. We cut (12,15) to clear and we put sword at (4,15).

**2 pixels a frame.** I checked all four Super Saiyan front frames in the manifest. **It affects only
`trunks_tank_ssj_front_walk_1.png` and `trunks_tank_ssj_front_walk_3.png`**, plus the unused
`trunks_tank_ssj_front.png`. In `ssj_front_walk_0` and `ssj_front_walk_2` ours, set 134 and set 130 all
put skin `17` at (4,15) and (12,15), so there is nothing to fix. MEASURED, CONFIRMED.

The jaw row itself needs nothing. At row 16 all three of ours, set 134 and set 130 put the same 5 px
skin run at x6-x10. At row 17 ours and set 128 are byte identical on the chest, x6-x10. The chest rows
are vanilla and untouched, which is correct.

**For the BASE front there is no finding, because set 129 cannot answer it.** Its long hair fills
(2,15) through (5,15) and (11,15) through (14,15), which is a different hairstyle, not an uncovered jaw.

---

## 7. Finding F: the front shoulder

The only pixels we ADDED anywhere in rows 12 to 25, across all 32 frames, are five coordinates.
MEASURED against each frame's own vanilla source.

| Pixel | Frames | Vanilla 128 | set 129 | set 134 | set 130 | Verdict |
|---|---|---|---|---|---|---|
| (2,17) | 6 front | clear | clear | clear | `51` plate | **LIKELY a defect** |
| (14,17) | 4 front | clear | clear | clear | `51` plate | **LIKELY a defect** |
| (15,20) | 4 front | clear | `0D` lit | `51` lit | `0D` lit | **not a defect, three sets agree** |
| (15,21) | 4 front | clear | `0D` lit | `51` lit | `0D` lit | **not a defect, three sets agree** |
| (11,17) | 4 side | clear | clear | clear | clear | **LIKELY a defect, 1 px** |

On (2,17) and (14,17): three of the four references leave those columns clear, and the one that lights
them is set 130's **shoulder plate**, which is bulk. A bare deltoid cannot claim a pauldron's width.
Our front silhouette at row 17 is 13 px wide against the jacket's 11 px, so the shoulder got WIDER when
the jacket came off. That runs against the guide rule at line 120.

I am labelling this LIKELY and not CONFIRMED for two reasons. You drew and approved this front yourself.
And the whole-frame numbers are good: every one of our 32 frames is a net shrink, from -1 to -11 px,
with the front idle at -10 (4 added, 14 cut). The widening is local to one row.

On (15,20) and (15,21): I checked these because they look like the same class and they are not.
Set 134, set 129 and set 130 all light x15 on those rows and only set 128 does not. Our base front
agrees with the majority. Leave them.

---

## 8. Finding G: the side arm

> [!WARNING]
> **The armour cannot answer this question, and I will not guess at it.**

Set 130's side view, rows 16 to 25, carries a long sleeved bodysuit from the shoulder to the elbow and a
grey gauntlet from row 22 down. Set 129 is the same. **Neither armour set draws one pixel of bare arm.**
Bare skin below row 16 in the side idle: set 128 has 23 px, set 129 has 2 px; set 134 has 23 px, set 130
has 3 px. MEASURED.

What the armour DOES settle, and it is worth having:

**Our side silhouette is already exact against the armour.** Rows 15 through 19 of
`trunks_tank_ssj_side.png` have pixel for pixel the same lit footprint as set 130: x4-x9 at row 15,
x5-x10 at row 16, x4-x11 at rows 17, 18 and 19. Row 15 is byte identical. CONFIRMED.
So the arm sits in the right place and takes the right room. Only its interior is open.

Measured arm widths, side idle, rows 17 to 23:

| Row | Our bare arm | set 130 sleeve or glove |
|---|---|---|
| 17 | 4 px, x8-x11 | 4 px, sleeve |
| 18 | 4 px | 4 px, sleeve |
| 19 | 4 px | 4 px, sleeve |
| 20 | 3 px | 3 px, sleeve |
| 21 | 3 px | 2 px sleeve plus plate |
| 22 | 4 px | 4 px, glove |
| 23 | 4 px, vanilla hand | 4 px, glove |

Our bare arm is the same width as the armour's SLEEVE. A sleeve is bulk, so a bare arm at the same width
has not shrunk. That is a pointer and not a finding, because the sprite guide's own table, measured off
your approved front idle, says a bare arm in this set is 3 px and 4 at the widest, which is what we have.
Two rules disagree and the armour cannot break the tie.

The other modder's version is not reviewable here. The clean room rule covers a review as well as a
build. If you want this arm improved, the evidence has to be your own eye or a frame you draw.

---

## 9. Finding H: the magenta key

> **REFUTED as stated, and the real shape is wider. There is no build effect.**

- **Palette index 0 is `(248, 0, 248)` magenta in all 33 PNGs in `art\trunks_tank\`**, the side frames
  included. The key index and its colour are the same everywhere. MEASURED.
- The real difference is the PNG `tRNS` chunk. **20 files carry `transparency=0` and 13 do not.** You
  named three. The 13 without it are:

| | |
|---|---|
| `trunks_tank_base_front.png` | `trunks_tank_base_back.png` |
| `trunks_tank_base_front_stand1.png` | `trunks_tank_base_back_walk_0.png` |
| `trunks_tank_base_front_walk_0.png` | `trunks_tank_base_back_walk_1.png` |
| `trunks_tank_base_front_walk_1.png` | `trunks_tank_base_back_walk_2.png` |
| `trunks_tank_base_front_walk_2.png` | `trunks_tank_base_back_walk_3.png` |
| `trunks_tank_base_front_walk_3.png` | `trunks_tank_ssj_front.png` |
| `trunks_tank_ssj_front_walk_0.png` | |

  So it is every base front frame, every base back frame, and two Super Saiyan front frames.
  `trunks_tank_ssj_front_walk_1/2/3` DO carry the chunk, which is why the set looks mixed.
- **No build effect.** `image_to_tiles` in `scripts\permanent\rom\log2_sprites.py` line 71 reads
  `px = img.tobytes()`, which is the raw palette index. The `tRNS` chunk is never read. Index 0 becomes
  GBA colour 0, which is transparent, with or without the chunk. CONFIRMED by reading the loader.
- It is a **viewer and edit kit problem only**: a file without the chunk opens as a magenta rectangle in
  an image viewer or in Piskel, and one with it opens on a checkerboard. Worth normalising so the kit
  looks the same every time, but no frame in any ROM is affected.

**Related, and not a defect.** `trunks_tank_ssj_front.png` is on disk and is NOT one of the 32 manifest
entries, so it never reaches a build. This matches `trunks_tank.py`, which states that the three front
facing Super Saiyan idles are held back and wait on you.

---

## 10. What I did not measure

Said plainly, rather than estimated.

- **The belt and the scabbard in the back view, rows 20 to 23.** They cross and they share one orange
  ramp. 10 to 14 pixels a frame, over 10 frames, are in that band. They need a region map.
- **Sword metal below row 21.** Trouser grey and sword grey are the same indices and the armour draws
  grey there too, so the two cannot be separated without a region map. The 247 px figure is a lower
  bound.
- **Sword metal that overlaps the armour's own plate or suit.** My rule only counts metal where set 130
  answers hair, skin or clear, so the scabbard's grey bands at rows 16 to 21 in the back view are not in
  the count either.
- **The base form's jaw, neck, chin, shoulder slope and back hair.** Set 129's long hair covers all of
  them. No armour evidence exists for set 128.
- **Why set 129 has a different hairstyle from set 128.** I measured that it does. I did not find out
  why, and I did not check whether set 129 is a different character. Bible row B0098 rates the "who"
  as LIKELY, not CONFIRMED.
- **Anims other than 0 and 1.** This review covers the 32 manifest frames only.
- **dir 3.** It reuses the dir 2 record with the h-flip bit, so it is not a separate drawing.

---

## 11. Candidate bible rows

Three facts here are new, measured, and worth keeping. They are offered, not merged.

1. Set 130's head rows 0-14 are **100% identical** to set 134's in the side idle and 96.7% in the front
   idle. That is direct proof that sets 130 and 134 are one character, which strengthens the LIKELY
   "who" in B0098.
2. Set 129 draws a **different hairstyle** from set 128: long hair to row 18 beside the face, 76 hair
   pixels that set 128 does not have, and a crown one row lower in every frame.
3. Sets 129 and 130 wear a full bodysuit, shoulder plates, a chest plate and gloves. They show **0 to 12
   bare skin pixels below row 16**, against 10 to 38 in sets 128 and 134, and **no scabbard orange at
   all** except one boot sole highlight at (7,30) in the two side idles of set 130.

---

## 12. Sheets made for this review

All in `art\trunks_tank\edit-kit\`. Made with `scripts\permanent\rom\sprite_look.py`. No new script was
written for the pictures.

| Sheet | What it shows |
|---|---|
| `armour_vs_ours_idles.png` | Base: ours, set 128 and set 129, for front, back and side. Whole figure. Shows set 129's long hair |
| `armour_vs_ours_ssj_idles.png` | Super Saiyan: ours, set 134 and set 130, for back, side and front. Whole figure |
| `ssj_back_hair_rows10-22.png` | Finding A, with the palette index in every cell |
| `ssj_back_walk_row_vs_armour.png` | Finding A across all four back walk frames, plus 1x thumbnails |
| `side_arm_vs_armour.png` | Finding G. Ours, set 134, set 130, then our base side and set 129 |
| `front_jaw_shoulder_vs_armour.png` | Findings E and F. Both forms, ours against jacket against armour |

Two sheets already in the folder were read before any of these were made:
`ssj_back_sword_vs_armour.png` and `run_anim13.png`.
