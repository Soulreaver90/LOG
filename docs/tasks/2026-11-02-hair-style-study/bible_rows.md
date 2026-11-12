# Bible rows from the 2026-11-02 hair style study

Merge with:

```
py -3.14 -I scripts\one-time\2026-10-16-first-probes\merge_bible_rows.py docs\tasks\2026-11-02-hair-style-study\bible_rows.md HAIR docs\tasks\2026-11-02-hair-style-study\report.md
```

## Section 4

| Fact | Tags | C/L | Source |
|---|---|---|---|
| Walk hair repeats the PASS frames: over 10 characters x 3 dirs (sets 11, 56, 58, 59, 60, 61, 128, 134, 137, 139), 21 of 30 rows repeat a hair drawing, and the repeated pair is always frames 1 and 3. 15 rows have 3 distinct drawings, 9 have 4, 6 have 2. In the 6 two-drawing rows frames 0 and 2 also repeat. No other pairing occurs | #sprite | C | HAIR |
| Hair sharing is a per-direction choice, not per character: mean distinct drawings back 3.3, front 3.2, side 2.8; 5 of the 6 two-drawing rows are side views. Only `set:128` (3 everywhere) and `set:58` (4 everywhere) hold one answer in all three dirs | #sprite | C | HAIR |
| Every walk in the cast BOBS the hair by exactly one row, and frames 1 and 3 sit one row higher than frames 0 and 2. Two independent measures agree: the hair centroid alternates up and down in 30 of 30 character and direction rows by about 1.0 px, and the vertical shift that minimises the frame to frame delta is -1, +1, -1, +1 in 120 of 120 transitions. The best shift has `dx 0` in 100 of 120; the 20 with `dx +/-1` are all in `set:58` and `set:139` | #sprite | C | HAIR |
| `set:59` side, `set:134` front and `set:134` side draw ONE hair picture for the whole walk: after the one row bob is removed their cycle delta is exactly 0. `set:134` back is 25 | #sprite char:gohan char:trunks | C | HAIR |
| Hair silhouette change per walk cycle is near constant across the cast and independent of tone count. Raw: 112 to 212 px, mean 159, about 40 px per step. After the one row bob is removed: 0 to 198 px, mean 61, about 15 px per step, with dark hair at 61 and light hair at 60. Most of the raw figure is the bob, not redrawing | #sprite | C | HAIR |
| What changes between walk frames depends on the tone count, not the view. Measured after the one row bob is removed, dark hair (1-2 tones, sets 60, 56, 137) is 18% shading and light hair (4-8 tones) is 71% shading. `set:60` Goku has ONE hair index, so its shading delta is exactly 0 in all three dirs. Comparing frames WITHOUT removing the bob charges the bob to shading: `set:134` front reads 356 px of shading raw and 0 aligned | #sprite | C | HAIR |
| Hair visibility does NOT predict how many distinct drawings a walk row has: `r = +0.14` between hair pixel count and distinct drawings over 30 rows, and `r = +0.25` against bob-aligned change per hair pixel. Tone count against bob-aligned change per pixel is `r = +0.74`, and `r = +0.77` within the 7 light haired characters alone. The 30 rows are not independent, 3 per character | #sprite | C | HAIR |
| In sets 11, 53, 54, 55, 56, 58, 59, 60, 61, 128, 129, 130, 134, 137, 139, 140 anim 1 has 4 frames in each of 4 dirs, every walk record is 16x32 at `dx 0, dy -24`, `dir 3` reuses the `dir 2` headers with `attr1 & 0x1000`, and all 4 frames of a dir have DIFFERENT headers, so hair sharing is pixel level and never record level | #sprite | C | HAIR |
| `set:139` and `set:140` are the same artwork: all 260 records point at the same frame headers | #sprite char:vegeta | C | HAIR |
| Trunks has two outfit pairs, not one: `set:128` base and `set:134` Super Saiyan share 91% of the body below the neck (jacket), `set:129` and `set:130` share 91% (armour), and `set:128` against `set:130` is only 43%. Both bible claims about `set:130` and `set:134` are right | #sprite char:trunks #form | C | HAIR |
| `set:54` is not Goku artwork: its body is 72% like `set:60`/`set:61` (the same orange gi), its head only 41% like `set:61`, and its hair ramp `8A 2B 2C 2E 85` with a `17` line is used by no other set. Future Gohan is the likely identity | #sprite char:gohan | C (bytes), L (identity) | HAIR |
| `set:55` and `set:56` share 88% of the body below the neck | #sprite char:gohan | C | HAIR |
| An accessory never carries more tones across a connected run than the run has pixels, and the tone count rises with width. Over 435 runs in 9 ramps in sets 11, 56, 60, 128, 137: a 1 px run is one tone in 143 of 143 cases, a 2 to 4 px run holds a median of 2 tones, and only a run of 9 px or more holds 4. Trunks' scabbard reads `3 2 3` down its length because its own grey metal bands cut the 3 px orange strap into 1 px and 2 px runs, NOT because the strap narrows | #sprite #palette | C (the counts), L (that it is a deliberate pattern rather than the existing 2-tones-plus-a-line rule) | HAIR |

## Section 5

| Fact | Tags | C/L | Source |
|---|---|---|---|
| One Super Saiyan hair ramp serves four characters, index for index: `14` (luma 125.6) line, `78` (166.7) fill, `2E` (234.1) light, `02` (248.0) spark, in `set:61` Goku, `set:59` Gohan, `set:134` Trunks and `set:139` Vegeta | #palette #sprite #form | C | HAIR |
| `set:139` Vegeta Super Saiyan adds a fifth hair tone `2C` (luma 243.4), and only in the BACK walk: 87 px there, 0 in front and 0 in side. A hair index set taken from the crown band alone misses it | #palette char:vegeta | C | HAIR |
| `0x02` (luma 248.0) is the EYE WHITE in every set that draws a face, and also a hair highlight in 9 of the 10 characters measured. Naming a pixel by index alone changes the distinct-drawing answer in 15 of 30 walk rows | #palette #sprite | C | HAIR |
| Hair ramps by relative luminance `0.2126R + 0.7152G + 0.0722B`: `set:60` Goku `01` 0.0 only; `set:137` Vegeta `01` 0.0, `0D` 112.0; `set:56` Gohan `01` 0.0, `0F` 64.0; `set:128` Trunks `E5` 57.1, `64` 119.3, `62` 187.4, `02` 248.0; `set:11` Android 18 `17` 86.2, `78` 166.7, `25` 206.1, `2D` 238.8, `02` 248.0; `set:58` Gohan SSJ2 `14` 125.6, `27` 157.4, `26` 181.5, `25` 206.1, `24` 225.0, `2E` 234.1, `2C` 243.4, `02` 248.0 | #palette #sprite | C | HAIR |
| Dark hair and light hair are drawn differently, not coloured differently. In sets 60, 56 and 137 the darkest tone is 93-100% of the hair mass and only 33-41% of it is on the outline, so the mass IS the line. In sets 11, 58, 59, 61, 128, 134, 139 the darkest tone is 33-51% of the mass and 59-91% of it is on the outline, so it is a line around a lighter fill | #palette #sprite | C | HAIR |
| A light hair mass is never lined in black. The line is one or two steps down its own ramp: `E5` luma 57 for Trunks, `17` luma 86 for Android 18, `14` luma 126 for every Super Saiyan head | #palette #sprite | C | HAIR |
| `set:11` Android 18 lines her hair with `0x17`, the dark SKIN tone, and it touches her body outline, so an 8-connected hair mask leaks into the neck and shoulder | #palette char:android18 | C | HAIR |
| `0x14` (luma 125.6) is the Super Saiyan hair line AND the face shadow of `set:60` Goku and `set:11` Android 18. Test a candidate hair tone in the BACK view, which has no face: `0x14` has 0 pixels in the back head box of either set | #palette #sprite | C | HAIR |
| `set:58` Gohan Super Saiyan 2 is the only 8-tone hair in the cast, and the only character with 4 distinct hair drawings in all three walk directions | #palette char:gohan #sprite | C | HAIR |
