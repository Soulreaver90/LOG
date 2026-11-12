# Brief: Trunks tank, the UP walk (set 128, anim 1, dir 1)

This completes the walk cycle. Down (dir 0) and side (dirs 2 and 3) are drawn and approved. This is the
last direction.

**Read `docs\sprite-guide.md` first, all of it.** Its "Pre-flight" checklist is the distilled cost of six
rounds on the down walk. I have already run that checklist for you and the findings are below, so do not
repeat it. Spend your time drawing.

## The four frames

| idx | header | serves | size |
|---|---|---|---|
| 0 | `0x3503EC` | (1,1,0) | 16x32 |
| 1 | `0x3504F4` | (1,1,1) | 16x32 |
| 2 | `0x350604` | (1,1,2) | 16x32 |
| 3 | `0x350710` | (1,1,3) | 16x32 |

Each header serves exactly ONE key, so four frames buy four records. No frame is shared.

Vanilla pixels: `art\vanilla-sets\set128\frame_<HEADER>.png`.
His approved back stand: `art\trunks_tank\trunks_tank_base_back.png`.
Write your output to `scripts\one-time\2026-11-02-up-walk\tank\up_walk_<N>.png`.

## Pre-flight findings, already measured. Do not re-derive these

1. **Each frame has its OWN offset, and frames 1 and 3 use MINUS 1.** The down walk sat at `+1`. Assuming
   one sign for the whole row finds nothing and sends you off to draw from scratch. Measured against the
   VANILLA back stand:

   | frame | offset | rows free | what that is |
   |---|---|---|---|
   | up1, up3 | **-1** | **0-16** | the WHOLE head, the band and the top of the shoulders |
   | up0 | **0** | 0-7 | the top of the hair |
   | up2 | **0** | 0-5 | the top of the hair |

2. **Lift the free rows from his approved back TANK stand, not from vanilla.** At offset -1, walk row `y`
   takes stand row `y+1`. At offset 0 it takes stand row `y`. The match was measured on vanilla, so
   wherever a vanilla walk row equals the vanilla stand row, whatever he drew for that stand row is the
   correct content for that walk row.

3. **Rows 17-25 match nothing, swept from -4 to +4, in all four frames.** Every torso is hand drawn. That
   is the real work, and it is why this row is harder than the down walk, not easier. The sweep is
   bounded, not a proof of impossibility, but the same sweep finds 18 matching rows for up1 and up3 at
   -1, so the method does detect matches where they exist.
4. **His back stand carries no jacket at all**, 0 of a vanilla 57. It is a complete reference for what the
   back looks like without the coat.
5. The jacket mask is `{0x4E, 0x4F, 0x50, 0x51}`. `0x4D` is NOT jacket.

## The scabbard, which is what makes the back different

The back carries the whole sword, 35 to 49 orange pixels a frame against 3 on the front. The owner decided
on 2026-11-02 to REVEAL the strap where the jacket was covering it, because leaving it makes the scabbard
flicker across the cycle and he objected to exactly that on the front view.

I already updated his back stand with its own 4 strap pixels, so the stand you lift from is current.

**Reveal these, and only these. The index is given because the frames that do draw the strap agree:**

| frame | pixel | vanilla | set to |
|---|---|---|---|
| up0 | (3,20) (4,19) (6,17) (7,16) (9,14) | jacket | `0x23` each |
| up1 | (11,17) | `0x51` | `0x23` |
| up2 | (6,17) (7,16) | jacket | `0x23` each |
| up2 | (10,20) | `0x51` | `0x22` |
| up3 | (11,17) | `0x51` | `0x23` |

**Do NOT reveal `(10,18)` or `(11,18)` in any frame.** Each is drawn as scabbard in one frame only, which
is the torso twist moving the strap rather than the jacket hiding it.

**One open pixel: `up2 (7,17)`.** The frames that draw it disagree, `0x23` in the stand and up0, `0x22` in
up1 and up3. Both are scabbard tones in the same ramp. Pick whichever matches its immediate neighbours in
up2 itself, and NAME your choice in the report so the owner can overrule it by eye.

## Method

The down walk proved this. A rule that scores well on a straight armed stand still draws the forearm down
the coat tail in a swing extreme, so:

- Copy rows for what REPEATS. Hand draw what does not.
- A jacket adds bulk. Taking it off must SHRINK the silhouette. Remove pixels, do not just recolour them.
- Find both hands in the vanilla frame first. They are already bare skin. Draw the arm toward the hand and
  cut whatever lies outboard of it.
- Nothing above the band row can be arm.

## Gate, run it yourself

- `py -3.14 -I scripts\permanent\rom\sprite_guard.py check <vanilla.png> <edited.png> --garment 51,50,4F,4E --body-from <row>`
  on all four. Always pass `--body-from`: the jacket blues are also his irises.
- Every frame has FEWER opaque pixels than its vanilla source.
- Rows 0-12 byte identical to vanilla in all four frames.
- Render all four with `scripts\permanent\rom\sprite_look.py` and LOOK at them head to foot before you
  report. The guide's primary instrument is looking.

## Do NOT

- Do not build a ROM. The owner asks for builds himself.
- Do not edit `art\trunks_tank\manifest.json` or copy anything into `art\`. I promote the frames after he
  approves them.
- Do not touch any other frame, any patch module, or any build list.
- No em dashes, no en dashes, no byte order mark.
- Absolute paths in every command. Never `cd`. Python is `py -3.14 -P`.

## Report

Per frame: pixels changed, silhouette before and after, and the guard's verdict. Name the `up2 (7,17)`
choice you made and why. Name anything you could not resolve rather than guessing past it. Give me the
path to your review sheet.

One report message, then stop. Do not add a byte order mark.
