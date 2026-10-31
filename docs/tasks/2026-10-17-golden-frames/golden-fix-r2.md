# Golden sheet fix round 2: Super Saiyan 2 head, front candidates

Personal GBA ROM hack (Legacy of Goku II). You draw the new Super Saiyan 2 (SSJ2) head for teen Gohan's purple gi sprites. Read `docs\tasks\2026-10-17-golden-frames\golden-brief.md` for the golden-frame context and rules.

## My verdict on round 1 (9:21 AM, verbatim)

"That honestly looks terrible. From the front and back, its basically ssj with some bad spikes. Side is very spiky. The bang that sticks out is the ssj2 defining featur and its missing. It shoudl be defined but fluffy, look at the new reference images."

## Void these round 1 rules

`golden-fix-r1.md` caused the failure. These lines from it no longer apply:
- Start from the set 59 Super Saiyan head.
- The width cap (x5-26, 22 px) and "taller than wide".
- "No spike points forward past the face."
- The spike angle numbers.

Hard limits that still apply:
- The whole frame stays inside the 32x32 slot (1024 bytes).
- The body, anchor and record geometry (w, h, dx, dy) do not change.
- Use existing hair color indices only (set 58 and 59 gold ramp, pal 20/21 brows).

## The look (my references)

References are in `data\reference\`. Never write under `data\`. Look at every one before you draw:

| View | File |
|---|---|
| Front | `images (1).jpg`, `images (5).jpg`, `images (3).jpg`, `images (4).jpg`, `ssj2.jpg`, `GohanSuperSaiyanIINV.webp` |
| Side profile | `658a54f58b6fc3e5fa7e1e3839e44a51.jpg` (the key image for the bang), `images (2).jpg` |
| Back | `gohans-awakening-v0-ym8rmzomcun31.webp`, `gohan-ssj2-was-something-else-such-a-simple-design-and-yet-v0-p0r3cxb9lvig1.webp` |

Describe what you see in your own words in the report. These points come from I:

- **Mass:** a big volume of hair that sweeps up and back behind the skull. It is clearly larger than the Super Saiyan head, and it must read as a different form at 1x.
- **Spikes:** layered clumps with inner shade lines. "Defined but fluffy." Not thin parallel needles, not noise. Tip lengths vary.
- **The bang (the defining feature):** one long strand. It leaves the hairline as its own outlined shape, with forehead skin visible on both sides of it, and falls to about eye level. It must read as a separate strand at 1x.
- **Side view:** the bang hooks forward and down in front of the forehead. It is the one thing allowed past the face line. The rest of the mass sweeps back.

## Base and technique

- **Base (final, 9:25 AM, verbatim):** "The ssj2 from the game is a good base to work from, it just needs to be defined and reshaped." Start every candidate from the game's own Super Saiyan 2 head: set 58, the armored "original" column of the Super Saiyan 2 row in `art\golden\golden_sheet.png`. Keep its volume. Define it: clear clump outlines and shade steps instead of its noisy texture. Reshape it toward the references: mass up and back, a clear bang.
- For how large hair volume reads at this scale, look at `data\sprites\Game Boy Advance - Dragon Ball Z_ Buu's Fury - Playable Characters - Goku (Super Saiyan).png` (I named it as the expanded-hair look). Look only. Do not copy pixels from it or from the fan mod.

## This round: front only

Draw 3 clearly different dir 0 (front) head candidates, A, B and C. Vary the mass shape and the bang. Do not draw the side or back yet. I pick one first.

Save:
- `art\golden\ssj2_front_A.png`, `_B.png`, `_C.png`: the full dir 0 golden frame with each head, indexed.
- `art\golden\ssj2_front_candidates.png`: one row per candidate. In each row, show the Super Saiyan golden front, then the candidate at 1x, 3x and 10x. Show the front reference images at the left at a similar height.
- Also show candidate A with each of the 3 lightning patterns (`golden_gi_ssj2_d0_lightning_*.png`). I have not picked one yet.

## Your own check, by eye, before you report

Put each candidate at 1x and 3x next to the Super Saiyan golden front. Answer for each:
1. Does it read as a different form from Super Saiyan?
2. Is the bang visible as its own strand?
3. Does it look fluffy and layered, not like needles or noise?

If any answer is no, redraw that candidate. Report each answer honestly. Numbers do not replace this check.

## Do not

- Do not change `golden_gi_ssj2_d*.png`, base or Super Saiyan golden frames, or anything outside `art\golden\`.
- Do not build a ROM. Never touch `builds\log2_poc.gba`.
- Do not use em or en dashes in any file or the report.
