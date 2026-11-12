# How LOG draws hair across directions and movement

A study of the walk cycle (`anim 1`) hair of ten characters, read out of the USA ROM.
No art, module, test or build list was changed. No suite was run.

> [!NOTE]
> Every number below is CONFIRMED from ROM bytes unless the line says LIKELY.
> The measurement was calibrated first against the two numbers the brief already knew.
> See "Calibration" before trusting anything else.

---

## The short answer

1. **Sharing the pass frames is a house convention, not a Trunks shortcut.** 21 of 30 character
   and direction rows repeat a frame. In every one of those 21 rows the repeated pair is the
   **pass frames 1 and 3**. No other pair ever repeats. Six of those rows go further and repeat
   the extremes 0 and 2 as well, so the whole walk is two drawings.
2. **Visibility does not predict it.** The correlation between hair pixel count and the number
   of distinct drawings is `r = +0.14` over 30 rows. The owner's hypothesis is not supported.
3. **Every walk in the cast bobs the hair by exactly one row, and the pass frames are the high
   point.** The hair centroid alternates up and down in **30 of 30 rows**, by about 1.0 px. This
   is the most universal fact in the study, and it is stronger than the sharing convention.
4. **Most of the raw frame to frame change is that bob, not redrawing.** Measured raw, the cast
   changes 158 to 650 px per cycle. Measured after the one row bob is taken out, it changes 0 to
   566, mean 167. Three rows fall to zero: the artist drew ONE picture and moved it.
5. **What predicts the real redrawing is the TONE COUNT**, not how much hair is visible.
   `r = +0.74` for tone count against bob-aligned change per pixel, and `r = +0.25` for hair
   pixel count.

---

## Calibration

The brief carried two measured facts from the Trunks work. The method reproduces both exactly
before any other character was measured.

| The brief said | This study measured | Match |
|---|---|---|
| `set:128` back walk, 3 distinct hair drawings | frames 0, {1,3}, 2 | yes |
| `set:128` back walk, 374 px changing per cycle | 374 | yes |
| `set:134` back walk already has 4 distinct | 4 | yes |
| Front and side of both sets share 1 and 3 | they do | yes |

The delta definition that gives 374 is: sum over all four transitions, including the wrap from
frame 3 back to frame 0, of the pixels that differ in POSITION or in PALETTE INDEX inside the
union of the two hair masks. Body coordinates and screen coordinates are the same thing here,
because every walk record in all eleven sets carries `dx 0, dy -24` and a 16x32 box.

---

## Method

### How a hair pixel was identified

A pixel is hair when its palette index AND its position both say so. Never by index alone, and
never by a row band.

- **CORE** is an index this set uses for hair and for nothing else.
- **SHARED** is a hair index the set also uses elsewhere. `0x02` is the EYE WHITE in every set
  that draws a face, and a hair highlight in most of them.
- The mask is a 4-connected flood from the crown over CORE. A SHARED pixel joins only when two
  of its four neighbours are already hair.

Two tests forced those two rules, and a simpler mask fails both:

| Test | What breaks |
|---|---|
| Trunks front eye white at `(10,13)` | Hair `E5` sits directly above it at `(10,12)`, so one neighbour is not enough. |
| Android 18 hair line `0x17` | It is the dark SKIN tone, and it touches her neck diagonally, so 8-connected leaks. |

### Three shapes, reconciled

| Shape | What it is | What it found |
|---|---|---|
| A, hair mask | index plus position, as above | the numbers in this report |
| B, head box | every lit pixel in the hair bounding box, no index test | 3 of 30 rows disagree with A |
| C, index alone | every pixel of a hair index, no position test | **15 of 30 rows disagree with A** |

**Shape C is the mistake this study exists to kill.** Index alone reports "all four frames
differ" in half the rows, because the pupils, the eye whites and the reused garment ramps move
while the hair repeats.

Shape B found three real disagreements, and each one is a fact about the art:

| Row | Hair | Head box | Reading |
|---|---|---|---|
| `set:56` side | 3 distinct, 1 and 3 share | 4 distinct | the FACE changes between the pass frames, the hair does not |
| `set:11` back | 3 distinct, 1 and 3 share | 4 distinct | something below the hair changes, the hair does not |
| `set:134` front | 2 distinct | 3 distinct | the hair repeats 0 and 2, the face does not |

### What would escape all three shapes

- A hair tone that appears in no crown band and in no back view. The crown band proposal plus a
  back view check caught `0x2C` in Vegeta SSJ, which is used in the BACK walk only. A tone used
  only in a direction I did not read would still be missed.
- Hair drawn in an index that the set also uses for a LARGE neighbouring mass. The mask would
  merge the two, and the leak alarm only reports the row, not the error.
- A repeat that the game plays in a different frame ORDER. I read records in table order and
  assumed that is play order. The set header does not store frame timing (RE-BIBLE, `#sprite`).

### Known leaks, stated rather than hidden

Android 18 side walk takes about 8 px per frame of the shoulder outline at rows 18 and 19,
because her hair line `0x17` and her body outline are the same index and they touch. Her side
numbers are therefore about 5% high. Every other leak alarm resolves to hair that genuinely
hangs below the jaw.

---

## Q1. Pass frame sharing, every character and every direction

`A B C B` means frames 0 and 2 are different drawings and frames 1 and 3 are the same drawing.
`distinct` is the count of different hair drawings in the four frames. `raw cycle delta` is the
figure that reproduces the brief's 374. Q3 gives the same measurement with the one row bob removed.

| set | character | dir | hair px per frame | pattern | distinct | raw cycle delta |
|---|---|---|---|---|---|---|
| 60 | Goku base | front | 125 119 125 119 | A B C B | 3 | 212 |
| 60 | Goku base | back | 190 189 191 189 | A B C B | 3 | 174 |
| 60 | Goku base | side | 121 115 116 115 | A B C D | **4** | 144 |
| 61 | Goku SSJ | front | 124 122 118 122 | A B C B | 3 | 406 |
| 61 | Goku SSJ | back | 159 156 161 156 | A B C B | 3 | 490 |
| 61 | Goku SSJ | side | 145 146 145 146 | A B A B | **2** | 452 |
| 56 | Gohan base, armour | front | 116 116 116 117 | A B C D | **4** | 204 |
| 56 | Gohan base, armour | back | 158 161 158 163 | A B C D | **4** | 254 |
| 56 | Gohan base, armour | side | 138 142 141 142 | A B C B | 3 | 254 |
| 59 | Gohan SSJ | front | 154 158 160 158 | A B C B | 3 | 502 |
| 59 | Gohan SSJ | back | 180 183 180 183 | A B C B | 3 | 572 |
| 59 | Gohan SSJ | side | 168 168 168 168 | A B A B | **2** | 536 |
| 58 | Gohan SSJ2 | front | 158 154 155 148 | A B C D | **4** | 571 |
| 58 | Gohan SSJ2 | back | 199 200 198 199 | A B C D | **4** | 650 |
| 58 | Gohan SSJ2 | side | 170 185 169 180 | A B C D | **4** | 609 |
| 137 | Vegeta base | front | 107 107 108 107 | A B C B | 3 | 158 |
| 137 | Vegeta base | back | 190 190 191 190 | A B C B | 3 | 168 |
| 137 | Vegeta base | side | 131 131 131 131 | A B A B | **2** | 148 |
| 139 | Vegeta SSJ | front | 132 131 129 131 | A B C B | 3 | 438 |
| 139 | Vegeta SSJ | back | 189 190 186 190 | A B C B | 3 | 594 |
| 139 | Vegeta SSJ | side | 143 141 143 141 | A B A B | **2** | 432 |
| 11 | Android 18 | front | 122 114 143 118 | A B C D | **4** | 468 |
| 11 | Android 18 | back | 183 184 187 184 | A B C B | 3 | 562 |
| 11 | Android 18 | side | 158 153 152 154 | A B C D | **4** | 547 |
| 128 | Trunks base | front | 121 122 130 122 | A B C B | 3 | 358 |
| 128 | Trunks base | back | 128 130 133 130 | A B C B | 3 | **374** |
| 128 | Trunks base | side | 118 114 118 114 | A B C B | 3 | 372 |
| 134 | Trunks SSJ | front | 144 144 144 144 | A B A B | **2** | 492 |
| 134 | Trunks SSJ | back | 155 158 159 157 | A B C D | **4** | 528 |
| 134 | Trunks SSJ | side | 105 105 105 105 | A B A B | **2** | 320 |

`set:140` is left out of the table. It points at exactly the same 260 frame headers as
`set:139`, so its numbers are identical by construction.

### The convention, stated exactly

- **3 of 4 is the plurality, not a law.** 15 rows of 30 have 3 distinct drawings, 9 have 4 and
  6 have 2.
- **The repeated pair is ALWAYS the pass frames 1 and 3.** Zero exceptions in 30 rows. In the
  six two drawing rows the extremes 0 and 2 also repeat. No other pairing occurs anywhere.
- **Sharing is a per direction decision, not a per character one.** Only two characters hold one
  answer in all three directions: Trunks base, which is 3 everywhere, and Gohan SSJ2, which is 4
  everywhere. Every other character mixes.
- **The side view shares most.** Mean distinct: back 3.3, front 3.2, side 2.8. Front and back
  tie, since 3.3 against 3.2 is one row of difference. Five of the six two drawing rows are side
  views, and that gap is real.
- **The sharing is never at record level.** All four walk frames of every direction of all
  eleven sets have four DIFFERENT frame headers. `dir 3` is `dir 2` with the OBJ h-flip bit
  `attr1 & 0x1000` in every set, so it is a flip and not a drawing.

### Every walk bobs the hair by one row

Two independent measures agree, and neither was built from the other.

| measure | result |
|---|---|
| hair centroid y per frame | alternates up and down in **30 of 30 rows**, swing about 1.0 px |
| the vertical shift that minimises the frame to frame delta | `dy -1` then `+1` then `-1` then `+1`, in **120 of 120 transitions** |

Frames 1 and 3 sit ONE ROW HIGHER than frames 0 and 2. The pass frames are the top of the bob,
which is what a walk does: the head is highest when the legs pass.

The horizontal component is almost always zero. The best shift has `dx 0` in 100 of 120
transitions. The 20 that prefer `dx +/-1` are all in `set:58` and `set:139`, and only in
`set:139` does the horizontal component cut the residual by much, 512 px to 270 px in the back
walk. So: **vertical bob everywhere, a horizontal component in two sets.**

In three rows the bob is the WHOLE animation. The four frames are one drawing moved up and down,
and the aligned delta is exactly zero:

| row | aligned delta |
|---|---|
| `set:59` side | 0 |
| `set:134` front | 0 |
| `set:134` side | 0 |
| `set:134` back, for comparison | 25 |

So the softest hair walk the ROM draws is one picture and a one row bob. The owner's note that a
repeated frame reads as a vibration sits beside this: in vanilla a repeated PAIR is never drawn
at the same height, so it is never an exact repeat on screen.

---

## Q2. Does visibility predict the sharing?

**No.** Measured over all 30 rows. The change figures below are bob-aligned, so they measure
redrawing and not the one row bob.

| pair | Pearson r |
|---|---|
| hair pixel count against distinct drawings | **+0.14** |
| hair pixel count against aligned change per hair pixel | +0.25 |
| tone count against distinct drawings | +0.20 |
| tone count against aligned change per hair pixel | **+0.74** |

| direction | mean hair px | mean distinct | mean raw change per hair px |
|---|---|---|---|
| front | 130 | 3.2 | 0.72 |
| back | 174 | 3.3 | 0.63 |
| side | 140 | 2.8 | 0.67 |

> [!WARNING]
> Three cautions on these correlations, and they matter.
> The 30 rows are NOT independent. Each character contributes three of them.
> Tone count falls into two clusters, three dark base heads and seven light heads, so any r
> against tone count is close to a dark against light comparison. Within the seven light
> characters alone it still holds at `r = +0.77`, so it is not only the cluster.
> A one tone head has a shading delta of zero by construction, so part of the correlation is
> arithmetic rather than a choice the artist made.

The back view shows the most hair, because no face is in the way, and front and back tie on
distinct drawings at 3.2 and 3.3, which is one row of difference. The side view clearly shares
the most. So the data does not support "an obscured view needs more work". Goku's side walk is
the smallest hair mass in his set, 117 px, and it is the only direction of his with four
distinct drawings. Gohan SSJ2's side is 176 px and also four.

**The better predictor is how many tones the hair has.** Nothing else in this data comes close.

---

## Q3. What moves: silhouette or shading

Two numbers are needed, and conflating them was the first draft's mistake.

- **Raw** is what the viewer sees: the frames compared where they sit. It is the number that
  reproduces the brief's 374.
- **Aligned** is what the artist redrew: the same comparison after the one row bob is removed.

A one row shift of a multi-tone mass repaints almost every pixel whose vertical neighbour holds
a different index, so a raw split charges the bob to shading. `set:134` front is the proof. Its
raw cycle delta is 492 px, of which 356 is called shading, and its aligned delta is **zero**.
Not one pixel of it was redrawn.

| hair type | raw sil | raw shade | aligned sil | aligned shade | aligned shading share |
|---|---|---|---|---|---|
| dark, 1 to 2 tones (sets 60, 56, 137) | 164 | 26 | 61 | 14 | 18% |
| light, 4 to 8 tones (the other seven) | 157 | 332 | 60 | 145 | **71%** |

Two findings survive the correction, and one changes value:

- **The silhouette budget is a constant, and it is smaller than the raw figure suggests.**
  Aligned, it is 0 to 198 px per cycle, mean 61, which is about **15 pixels of outline change
  per walk step**. Dark hair averages 61 and light hair 60, so the constant holds across the
  whole cast.
- **A light hair mass spends about 70% of its redrawing on shading.** That survives alignment,
  at 71%.
- Goku base remains the clean case. His hair is ONE index, so his shading delta is exactly
  **0** in all three directions, raw and aligned. Every pixel of his hair animation is outline.

Worked example, Trunks base back walk, raw per transition including the wrap:

```
0 -> 1   94 px     1 -> 2   93 px     2 -> 3   93 px     3 -> 0   94 px
```

The four transitions are almost equal, which is what a repeated pass frame plus a steady bob
looks like. Aligned, the same cycle costs 124 px rather than 374.

`set:58` Gohan SSJ2 is the one character the bob does not explain: 650 px raw and 438 aligned in
the back walk. It genuinely redraws its mane every frame.

---

## Q4. The tone ramp

Relative luminance `0.2126R + 0.7152G + 0.0722B` from the shared OBJ palette at `rom:0x1DA6C8`.
The count is hair pixels over all twelve walk frames.

| set | character | ramp, dark to light |
|---|---|---|
| 60 | Goku base | `01` 0.0 (1714) |
| 137 | Vegeta base | `01` 0.0 (1663), `0D` 112.0 (51) |
| 56 | Gohan base | `01` 0.0 (1558), `0F` 64.0 (110) |
| 128 | Trunks base | `E5` 57.1 (602), `64` 119.3 (442), `62` 187.4 (346), `02` 248.0 (90) |
| 11 | Android 18 | `17` 86.2 (654), `78` 166.7 (487), `25` 206.1 (183), `2D` 238.8 (365), `02` 248.0 (163) |
| 61 | Goku SSJ | `14` 125.6 (867), `78` 166.7 (396), `2E` 234.1 (277), `02` 248.0 (160) |
| 59 | Gohan SSJ | `14` 125.6 (779), `78` 166.7 (363), `2E` 234.1 (605), `02` 248.0 (281) |
| 134 | Trunks SSJ | `14` 125.6 (761), `78` 166.7 (421), `2E` 234.1 (336), `02` 248.0 (107) |
| 139 | Vegeta SSJ | `14` 125.6 (658), `78` 166.7 (352), `2E` 234.1 (507), `2C` 243.4 (87), `02` 248.0 (242) |
| 58 | Gohan SSJ2 | `14` 125.6 (696), `27` 157.4 (12), `26` 181.5 (147), `25` 206.1 (706), `24` 225.0 (57), `2E` 234.1 (272), `2C` 243.4 (199), `02` 248.0 (26) |

Findings:

- **One Super Saiyan ramp serves four characters.** `14, 78, 2E, 02` is the hair of `set:61`
  Goku, `set:59` Gohan, `set:134` Trunks and `set:139` Vegeta, index for index. Super Saiyan
  hair is not drawn per character in LOG. It is one palette ramp over four silhouettes.
- **Vegeta SSJ adds a fifth tone, `2C`, and only in the BACK walk.** 87 px there, zero in the
  front and zero in the side. A crown band proposal alone misses it, which is why a back view
  check is part of the method.
- **Gohan SSJ2 is the only eight tone head in the cast**, and it is the only character with four
  distinct drawings in all three directions. The two facts probably belong together. A mane that
  big and that finely graded has no plain frame to repeat.
- **`0x02` is the eye white in every set that draws a face**, and a hair highlight in nine heads
  of ten. That one index is the whole reason this study needed a position test.
- **A ramp does not share a high nibble.** Trunks runs `E5, 64, 62, 02`, across three nibbles.
  The guide already records that as disproven. Luminance order is the only thing that puts a
  ramp in order.

---

## Q5. Counted patterns elsewhere

The brief reports the Trunks scabbard as a repeating `3 2 3`. Measured first, then generalised.

Trunks `set:128` back stand, scabbard ramp `20 21 22 23`, distinct tone steps per row going down
the strap:

```
y15  y16  y17  y18  y19  y20  y21  y22  y23
 1    2    2    3    3    2    3    3    1
```

The `3 2 3` is in the ROM. **The mechanism is not what it looks like.** Reading the rows:

| row | the pixels across the strap | what is happening |
|---|---|---|
| y18 | `23 22 21` at x6-8 | 3 px of unbroken orange, so all three tones fit |
| y19 | `22 21 22 23` at x6-9 | 4 px of unbroken orange, still three tones |
| y17 | `23` at x7, `0D 0B` at x8-9, `22 23` at x10-11 | the grey metal BAND crosses it and splits the orange into a 1 px run and a 2 px run |

So the "2" rows are rows where a band crosses, not rows where the strap narrows. The strap is a
**three tone cross-section, dark edge, mid, light edge**, and the rhythm down its length is
produced by the grey chape and bands cutting across it.

The wider claim was re-measured per CONNECTED RUN, with its width, over nine ramps in five sets,
all three stand directions. The earlier per-row count merged separate objects and was wrong.

| run width | runs measured | distinct tones, min to max | median |
|---|---|---|---|
| 1 px | 143 | 1 to 1 | 1 |
| 2 px | 102 | 1 to 2 | 2 |
| 3 px | 57 | 1 to 3 | 2 |
| 4 px | 69 | 1 to 4 | 2 |
| 5 px | 28 | 1 to 4 | 3 |
| 7 px | 15 | 2 to 3 | 3 |
| 9 px | 15 | 1 to 4 | 4 |
| 10 to 11 px | 4 | 4 to 4 | 4 |

**What is CONFIRMED:** a run never carries more tones than it has pixels, a 1 px run is always
exactly one tone over 143 cases, and the tone count rises with width. A narrow run, 2 to 4 px,
takes a median of 2 tones. Only a run of 9 px or more holds 4.

**What is LIKELY, not confirmed:** that this is a deliberate counted pattern. It is equally well
explained by the guide's existing law, "2 main tones plus a line colour, and a third tone only
as a 1 px step". The `3 2 3` of the scabbard is one object interrupted by its own metal fittings,
and I did not find a second object in the cast that produces a repeating count for a different
reason.

---

## Q6. Blonde against purple, light against dark

Where the darkest tone of the hair sits. "On the edge" means the pixel has a 4-neighbour that is
not hair.

| set | character | darkest tone | share of all hair | share of it on the edge |
|---|---|---|---|---|
| 60 | Goku base | `01` L0 | **100%** | 40% |
| 137 | Vegeta base | `01` L0 | **97%** | 33% |
| 56 | Gohan base | `01` L0 | **93%** | 41% |
| 61 | Goku SSJ | `14` L126 | 51% | 59% |
| 134 | Trunks SSJ | `14` L126 | 47% | 68% |
| 128 | Trunks base | `E5` L57 | 41% | 72% |
| 59 | Gohan SSJ | `14` L126 | 38% | **79%** |
| 139 | Vegeta SSJ | `14` L126 | 36% | **91%** |
| 11 | Android 18 | `17` L86 | 35% | **86%** |
| 58 | Gohan SSJ2 | `14` L126 | 33% | 79% |

Two different drawings, not two colourings of one drawing:

- **Dark hair is a silhouette.** The darkest tone is the whole mass, 93% to 100% of it. Only a
  third of it is on the edge, because nothing else is inside. The Vegeta base back view is a
  solid black dome with no internal detail at all. Goku base has no second tone anywhere. Vegeta
  base and Gohan base carry a second tone as 4 to 9 sparks per frame, and nothing else.
- **Light hair is an outlined mass.** The darkest tone is a third to a half of the pixels, and
  68% to 91% of it is on the edge. It is a LINE, not a fill. The fill is the mid tones, and the
  brightest tone is a sparse spark, 90 to 280 px over twelve frames.
- **The line colour is never black for light hair.** Trunks lines at L57, Android 18 at L86, and
  every Super Saiyan head at L126. A light hair mass takes a line in its own hue, not black.
  LIKELY, and only three distinct line values: the apparent trend that a deeper hair colour
  takes a darker line rests on three points and should not be quoted as a measurement.
- **The Android 18 hair line is `0x17`, the dark SKIN tone.** She is the only character whose
  hair line is borrowed from another body part ramp.

---

## Set identity, checked against bytes

The brief asked for this to be confirmed, not trusted. Rows below the neck were compared pixel
for pixel between stand frames.

| claim | evidence | verdict |
|---|---|---|
| `set:60` Goku, `set:61` Goku SSJ | bodies 96% identical | CONFIRMED pair |
| `set:137` Vegeta, `set:139` Vegeta SSJ | bodies 99% identical | CONFIRMED pair |
| `set:139` and `set:140` are both SSJ Vegeta | all 260 records point at the same frame headers | CONFIRMED. One artwork, two set ids |
| `set:128` Trunks, `set:134` Trunks SSJ | bodies 91% identical | CONFIRMED pair, the jacket outfit |
| `set:130` is Super Saiyan Trunks | bodies 91% identical to `set:129`, only 43% to `set:128` | CONFIRMED, and it pairs with `129`, not `128`. Sets `129` and `130` are the ARMOUR Trunks, `128` and `134` the jacket Trunks. Both bible claims are right and they do not conflict |
| `set:54` is Future Gohan, not Goku | body 72% like `set:60` and `set:61`, head only 41% like `set:61`, and its hair ramp is `8A 2B 2C 2E 85` with a `17` line, which no other set uses | CONFIRMED not Goku artwork. LIKELY Future Gohan, who wears the same orange gi |
| `set:55` and `set:56` | bodies 88% identical | LIKELY one Gohan outfit, two variants |

Also confirmed: `set:11` is Android 18, blonde bob, blue vest. `set:58` has a 32x32 stand, and
its WALK frames are 16x32 like every other set, so it measures alongside the rest.

---

## Rules for drawing LOG hair

Written for an artist, in the order the decisions come up.

### 1. Decide the tone count first, because it decides everything after it

| hair | tones | what the tones do |
|---|---|---|
| black | 1, or 2 with a spark | the mass IS the line colour |
| a colour, such as Trunks purple | 4 | line, fill, light, spark |
| Super Saiyan | 4, from one shared ramp | line `14`, fill `78`, light `2E`, spark `02` |
| Super Saiyan 2 | 8 | a fully graded mane |

Do not give black hair a second fill tone. Vegeta and Gohan carry a 4 to 9 pixel spark and
nothing more. Do not spread four tones evenly on a small head either. The guide rule holds: two
main tones plus a line, and a third only as a 1 px step.

### 2. Line a light hair mass in its own hue, and put the line on the edge

A third to a half of a light hair mass is its darkest tone, and 70% to 90% of that tone sits on
the outline. Draw the outline first, fill inside it, then add the spark. Never line light hair
with black. Trunks lines at luminance 57, Super Saiyan at 126.

Black hair has no separate line. Draw the shape and stop.

### 3. Draw three hair drawings for four walk frames, and make frames 1 and 3 the same one

This is the house default and it holds in 21 of 30 measured rows. The repeated pair is ALWAYS
the pass frames. No example anywhere in the cast has frames 0 and 1 sharing, or 1 and 2.

Then choose one of the three patterns on purpose:

| pattern | where the cast uses it | reads as |
|---|---|---|
| `A B C B`, 3 drawings | the default, 15 of 30 rows | a sway with one repeat |
| `A B C D`, 4 drawings | the biggest manes and most faces, 9 of 30 | a full sway |
| `A B A B`, 2 drawings | 5 of the 6 cases are side views | a ping pong |

> [!WARNING]
> This is the vanilla convention, not an instruction. The owner redrew the Trunks BACK walk so
> all four frames differ, because the vanilla repeat read to him as a vibration. State the
> convention, show him the frames, and let his eye decide. `set:58` and `set:134` back already
> break it inside vanilla, so a four drawing walk is house style too.

### 3b. Whatever you choose, bob the hair one row, and put the pass frames at the top

This is the one rule with no exception in the cast: 30 of 30 rows bob, and 120 of 120
transitions move by exactly one row. Frames 1 and 3 sit one row higher than frames 0 and 2. A
repeated pass frame in vanilla is therefore never an exact repeat on screen, because the two
copies are drawn at different heights. Shift vertically. Only `set:58` and `set:139` add a
horizontal component.

### 4. Budget about 15 pixels of real outline change per step

Measured after the one row bob is taken out, the silhouette delta per walk cycle is 0 to 198 px,
mean 61 over four steps. Dark hair averages 61 and light hair 60, so the budget does not depend
on the palette. Raw, the same measurement reads 40 px per step, and most of that is the bob.

This is a range observed in vanilla, not a threshold. I did not test what a different number
looks like, so treat it as the house range and judge the result by eye.

### 5. Spend the rest on shading, and only if the hair has tones to shade with

A light hair mass spends about 70% of its real redrawing on shading rather than on the outline.
A one tone head cannot do this at all, so its whole animation has to be outline. Goku base is
the proof: his shading delta is exactly zero in every direction.

### 6. Do not make a view share frames because the hair is hidden there

Visibility does not drive this choice in the ROM, `r = +0.14`. The back view shows the most hair
and shares the least. The side view shares the most. Decide per direction, by eye, on whether
the sway reads.

### 7. A light hair mass hangs below the jaw, so plan for it

The back view hair reaches rows 15 to 18 in every set. The Android 18 hair falls to row 18 in
the side view, and past the jaw on both sides in the front. The guide rule for Trunks, that the
back hair must reach `y15` to match the front head box, is cast-wide behaviour and not a Trunks
special case.

### 8. Give an accessory as many tones as its WIDTH allows, and no more

Measured over 435 runs in nine ramps. A 1 px run is always one tone, with no exception in 143
cases. A 2 to 4 px run takes a median of 2 tones. Only a run of 9 px or more holds 4.

The `3 2 3` of the Trunks scabbard is a 3 px strap carrying all three of its tones, cut across
by its own grey metal bands, which split some rows into a 1 px run and a 2 px run. Draw the
fittings and the rhythm follows. Do not write a rhythm into a plain strap.

### 9. Never name a hair pixel by its colour alone

`0x02` is the eye white in every face in this game, and a hair highlight in nine heads of ten.
`0x14` is the Super Saiyan hair line and also the Goku face shadow and the Android 18 jaw
shadow. `0x17` is the dark skin tone and the Android 18 hair line. Identify by index AND
position, every time. Index alone changes the answer in half the measured rows.

---

## Files

| file | what it is |
|---|---|
| `report.md` | this |
| `bible_rows.md` | the rows for `docs\RE-BIBLE.md`, sections 4 and 5 |
| `review_set<N>_walk.png` | 12 walk frames per character, large, with repeat letters and the mask |
| `scripts\one-time\2026-11-02-hair-style-study\` | `hairlib.py`, `hairmask.py`, `mask2.py`, `cast.py`, `measure.py`, `review_sheets.py` |
| `scripts\one-time\2026-11-02-hair-style-study\measure.json` | every number in this report, machine readable |

Run the measurement again with this command.

```
py -3.14 -P scripts\one-time\2026-11-02-hair-style-study\measure.py
```
