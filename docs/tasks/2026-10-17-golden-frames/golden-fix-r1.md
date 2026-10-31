# Golden sheet fix round 1: Super Saiyan 2 heads

I checked the golden sheet at 14x. Base and Super Saiyan golden frames pass. Keep them unchanged.
The Super Saiyan 2 heads fail the brief (`golden-brief.md`, "New Super Saiyan 2 heads"). Redraw only the 4 Super Saiyan 2 heads.

## Defects

1. **Silhouette is a horizontal fan.** The front head spans about 28 px (x2-29) on a 16 px body. The outer spikes point sideways, near horizontal. It reads as a bush or a mane, not as Super Saiyan 2.
2. **Side head (dir 2) is symmetric.** Spikes point both forward and back at equal length. The brief asks for spikes that sweep up and back.
3. **Bang is not clear.** The single bang over the forehead does not read at 1x.

## Target

- **Silhouette:** taller than wide. Keep it inside x5-26 (22 px max) for dirs 0 and 1. Use the full height up to y0.
- **Spike angle:** every spike points up, from vertical to about 45 degrees outward. No spike below 30 degrees from horizontal.
- **Structure:** start from the set 59 Super Saiyan head (the golden `golden_gi_ssj_d*.png`). Make it fuller: 5-7 distinct spikes on the front, each with its own dark outline and 2-3 shade steps. Not noisy.
- **Bang:** one strand that hangs from the hairline to brow level, slightly left of center on the front view, 1-2 px wide with an outline. Same strand on the side view, in front of the face.
- **Side (dir 2):** the front edge of the hair rises almost vertical above the forehead. All spikes sweep up and toward the back of the head. No spike points forward past the face. Width at most 20 px. Dir 3 stays the mirror of dir 2.
- **Back (dir 1):** spikes radiate up and out, mostly up, fuller than the set 59 back.
- **Turn test:** dirs 0, 2, 1 must read as one head turning.
- **Unchanged:** colors (existing hair indices, pal 20/21 brows), body, anchor, record geometry, 32x32 slot.

## Sheet

- Re-render `art\golden\golden_sheet.png` with the new heads and the 3 lightning patterns on the new front frame.
- Add a row: Super Saiyan golden head next to the new Super Saiyan 2 head, per direction, at 10x. I compare structure.
- Overwrite `golden_gi_ssj2_d0..d3.png` and the lightning PNGs.

Do not propagate. Do not build a ROM. Do not touch `builds\log2_poc.gba`.
