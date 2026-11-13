# Portrait layers: a frame, your art, a background

Draw your portrait with NO background and stack three layers:

| Layer | File |
| --- | --- |
| top | `frames/frame_0.png` |
| middle | your portrait, transparent background |
| bottom | a file from `backgrounds/` |

**Never draw on the frame.** The art table rejects an imported portrait whose outer 3 px
ring does not match the ring that id already had.

## Frames (2)

Nearly every portrait uses one frame. A ring differing by at most 16 pixels is counted as
that frame with a slip rather than as a separate frame.

| Frame | Portraits | Ids |
| --- | --- | --- |
| `frames/frame_0.png` | 88 | 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114 |
| `frames/frame_1.png` | 1 | 47 |

6 portraits slip a few ring pixels: 49 (1 px), 50 (1 px), 70 (8 px), 88 (1 px), 89 (1 px), 91 (1 px).

## Backgrounds (4)

Every file is a complete 64x64 field, so it works as a bottom layer. The percentage in
the name is how much of it was READ from the ROM. The rest is the fitted circle
carried on through the middle, where your drawing goes.

A background is a few nearly identical shades in solid circular bands, with an
ordered dither between one band and the next. Its centre sits LOW, behind the
character, not in the middle of the picture. Keep both when you paint over it.

`proof/` shows each background beside the real portraits it came from. Look there
before trusting one.

| Background | Measured | Portraits it came from |
| --- | --- | --- |
| `backgrounds/bg_66pct_id035.png` | 66% | 35, 77, 103 |
| `backgrounds/bg_58pct_id033.png` | 58% | 33, 57, 59, 74, 88, 95 |
| `backgrounds/bg_47pct_id030.png` | 47% | 30, 53, 84, 86 |
| `backgrounds/bg_46pct_id046.png` | 46% | 46, 51, 85, 90, 94 |

## The 64 portraits with a background of their own

Fewer than 3 portraits share these, so too few independent characters can
corroborate what is background and what is not. No background file is written for
them on purpose. Use the
portrait itself as your reference:

    26, 27, 28, 29, 31, 32, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 47, 48, 49, 50, 52, 55, 56, 58, 60, 61, 62, 63, 64, 65, 66, 67, 69, 70, 72, 73, 75, 76, 79, 80, 81, 82, 83, 89, 91, 93, 96, 97, 98, 99, 100, 101, 102, 104, 106, 107, 108, 109, 110, 111, 112, 113, 114

## Why these are not grouped by colour

The portraits do not share a handful of backgrounds. Measured on the top corners,
where a head almost never reaches, only 43 of 394 same-colour pairs actually match.
Most portraits have a background of their own, so a background here is built only from
portraits that agree at least 95 percent.
