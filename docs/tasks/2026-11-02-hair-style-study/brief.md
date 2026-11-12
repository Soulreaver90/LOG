# Study: how LOG draws hair across directions and movement

## Why

We have been measuring one sprite, Trunks `set:128`, in great detail, and I have twice invented a
rule to fill a gap when the answer was already in the art. The owner's point: learn the house
style from the whole cast, then draw in it. LOG has a distinct style that is hard to hit because
of the pixel budget, and we want to become good at THAT style, not at pixel art in general.

This is a STUDY. No pixel work, no module changes, no build, no test suite.

## The one finding that prompted it

In Trunks `set:128`, every walk direction uses only **3 distinct hair drawings for 4 frames**:
walk frames 1 and 3, the two pass frames, share one drawing. The owner redrew the BACK walk so all
four differ, and in a loop his version reads as hair swaying side to side while vanilla and my
version read as a vibration, because a repeated frame in a loop is a hitch.

Measured, back walk, hair pixels only: vanilla 374 px changing per cycle with 3 distinct drawings,
his 394 with 4. Trunks SSJ `set:134` BACK walk already has 4 distinct. Front and side of both sets
share 1 and 3.

**The question this study answers: is sharing the pass frames a house convention, an artist's
shortcut on one character, or something that varies with how visible the hair is?**

## Characters and sets, from `docs\RE-BIBLE.md`

| character | sets |
|---|---|
| Goku | `60` base, `61` Super Saiyan |
| Gohan | `56`, `58`, `59` |
| Vegeta | `137`, `139`, `140` |
| Android 18 | `11`, header `rom:0x1EE160` |
| Trunks | `128` base, `134` SSJ, our reference |

Resolve every set through the live table, the word at `rom:0x959C`, entry `id - 7`. Read records
with `set_records` from `rom.log2_sprites`. Confirm each set's character rather than trusting the
table above: the bible also claims `set:130` is Super Saiyan Trunks, which I have not reconciled
with `134`, and `set:54` is Future Gohan and not Goku. Say what you find.

Vanilla frames are already exported under `art\vanilla-sets\set<N>\`. Check the set is there
before reading the ROM for it.

## Questions, in priority order

1. **Pass-frame sharing.** For every character, every walk direction: how many distinct hair
   drawings in the 4 frames, and which frames share? Give a table. Is 3-of-4 universal?
2. **Does visibility predict it?** Count hair pixels per view. The owner's hypothesis is that an
   obscured view needs more work than an open one. Test it: does the sharing, or the amount of
   per-frame change, track how much hair is visible?
3. **What moves.** When hair does differ between frames, is it the silhouette, the shading, or
   both? Give the split.
4. **The tone ramp.** How many tones does each character's hair use, and how are they ordered?
   Report relative luminance `0.2126R + 0.7152G + 0.0722B`, never the HSV max channel: four tones
   in Trunks' palette share a max channel of 0.97 and span 119 to 248 in luminance.
5. **Counted patterns elsewhere.** Trunks' scabbard draws a repeating **3 2 3** run, where the
   number is how many steps of the tone ramp are visible. Look for the same kind of counted
   pattern in other characters' accessories, belts, sashes, armour trim. Does LOG do this
   generally?
6. **Blonde against purple.** Android 18 and the Super Saiyan sets are light hair. Does a light
   hair mass get shaded differently from a dark one, in tone count or in where the dark sits?

## Method rules, learned the hard way today

- **Identify a feature by palette index AND position, never by row and never by index alone.**
  `0x02` is a hair highlight AND the eye white in `set:128`. A row band is not a body part.
- **Measure the cycle, not the frame.** Count distinct drawings, measure frame-to-frame delta all
  the way round including last back to first, and flag any repeated frame.
- **Use two independent measurement shapes and reconcile them.** If they disagree, that is the
  finding. State what a feature drawn some third way would not be caught by.
- Label every claim CONFIRMED (read from bytes) or LIKELY (reasoned). Never state a count as a
  fact about "all" sprites: say which shapes you searched and what would escape them.

## Deliverables

1. `docs\tasks\2026-11-02-hair-style-study\report.md`. The tables, the answers, and a short
   section "rules for drawing LOG hair" written so an artist can follow it.
2. `docs\tasks\2026-11-02-hair-style-study\bible_rows.md`, as `## Section N` table blocks, ready
   for the merge script. Section 4 is Sprites, Section 5 is Palette.
3. Review sheets as PNGs in the same folder: for each character, the 4 walk frames of each
   direction side by side, zoomed, so the owner can look. He decides by eye.

## Do not

- Do not write under `data\`. Do not create or overwrite a ROM, save or state.
- Do not change any file in `art\`, any module, any test, or any build list.
- Do not touch `art\trunks_tank\`, `scripts\permanent\patches\trunks_tank.py`, the manifest, or
  `scripts\one-time\2026-11-02-trunks-ssj\`. Another agent is working there right now.
- Absolute paths only. Never `cd`, `Set-Location` or `Push-Location`.
- Python is `py -3.14 -P`. `py -3` is 3.15 and has no Pillow.
- Put scratch scripts in `scripts\one-time\2026-11-02-hair-style-study\`.

One report message, then stop. Do not add a byte order mark.
