# Style study: our sprites against the Z Hack's (final, 2026-10-30 9:39 AM)

Read `LOG\README.md`, `docs\tasks\global.md`,
`docs\tasks\2026-10-30-zhack-review\zhack-review-report.md`, `LOG\zhack\index.md` and the sheets in `LOG\zhack\`,
the gi art reports (`docs\tasks\2026-10-16-task-5-gi-art\`, the base-audit notes in `scripts\one-time\2026-10-23-base-audit\`),
and the bible rows tagged T5, T5P2, OUT, SPR and ZHK. Our art lives in `art\` and is built by `scripts\permanent\patches\gohan_gi.py`
and the related modules.

## My words

"Their Gohan SSJ2 puts ours to shame, including the gi." "They also have the Goku SSJ finger pose that we queued to
do. They are much farther ahead, but also very closely aligned with our version." He asked for a side-by-side study
that becomes a style guide for our own redraw. Earlier: "I do prefer the larger hair/space for the base characters."

**Rule: inspiration only.** I declined to reuse the hack's art. Do not copy pixels, trace, or write any hack
bytes into `art\` or a module. Describe what makes theirs work, so we can redraw our own.

## Task

1. **SSJ2 Gohan and the gi.** Compare our SSJ2 gi Gohan sets (159, 160 and the related idle and Rage sets) with the
   hack's matching sets, anim by anim and direction by direction, at 4x. Render side-by-side sheets (ours, theirs) in
   `LOG\zhack\study\`. For each anim list the concrete differences: hair silhouette and volume inside the 32x32 box,
   hair shading levels and highlight placement, face and eyes, gi shading levels (light, mid, dark, outline), fold
   lines, sash, wristbands, boots, outline use (where they drop or colour the outline), body proportions and stance,
   motion (key poses, overlap), and the palette indices each uses (count of shades per material).
2. **Base characters with bigger hair.** The same comparison for base Goku (set 60), base Gohan (56, 58, 59), Vegeta
   (139) and Trunks (130) against vanilla: how they widen the hair inside 32x32, what they give up to make room.
3. **Goku Super Saiyan finger pose.** Find the hack's finger block pose (set, anim, frames), and describe how it is
   built (pose, arm angle, the finger, the frames per direction) as a reference for our own drawing in the Trunks scene.
   Compare with our candidate (Goku set 62 anim 4, or set 61) from
   `docs\tasks\2026-10-30-celljr-rework-plan\plan-report.md` item 12.
4. **Portraits.** Me (9:41 AM): "Review their portraits, their sprites, understand how they were accomplished, how
   and why we lack so badly." Compare their new and redrawn portraits (`LOG\zhack\portraits\`) with ours
   (`art\tables\portraits.json`, the portrait modules, `docs\research\re-portraits.md`): size, palette count and ramps, line
   work, shading style (cel or soft), eyes and hair rendering, how they handle the 16-colour limit, and how each portrait
   is stored and named in the ROM (format, palette slot).
5. **How they did it, and why we lag.** For sprites and portraits, explain the likely process behind theirs (hand
   drawn per frame, consistent model sheet, shared palette ramps, frame reuse) from what the data shows. Then the root
   causes of our gap, from our own history: our process (rule passes and repaints of armor frames, `gohan_gi.py`, the
   base-audit and hand-fix notes), palette choices, missing model sheets, review method. Be blunt and specific: cite our
   files and frames.
6. **Style guide.** Write the rules we take from this, as short do and don't lines per material (hair, skin, gi,
   outline), with the palette ramps we would use (our palette indices from `art\tables\palette.json`), and an ordered redraw
   plan: which sets first, size per set (frame count), and which frames I should draw as the model sheet.
6b. **Canon outfit changes.** Me (9:57 AM): "The outfit changes are also great, they match the changes in the show,
   like 18's casual she wears after she fights Vegeta, among others." List every outfit change in the hack (new and
   redrawn sets in `LOG\zhack\index.md`): character, outfit, the canon moment it matches (episode, sourced or marked
   S), where the hack uses it (scene table, if known), and where it would fit in LOG (map, flag or scene). Rank them as
   ideas for our own drawings, with frame counts.
7. Mark each rule as observed in their art (cite the sheet and frame) or as our inference.
8. **Clean-room rules (approved 9:41 AM).** The style guide must be usable without their sheets: written rules
   and measurements (hair span in px, shade counts, ramps by our palette indices), not images to copy. Put the
   side-by-side sheets in `LOG\zhack\study\` only, and say in the guide that drawing starts from our own sources (vanilla
   frames, official Buu's Fury art, anime stills) with their sheets closed. Write a small one-time checker
   (`style_similarity.py`) that, for a frame of ours and the matching frame of theirs, reports the share of matching
   pixels after removing the pixels both share with the vanilla frame; run it on our current SSJ2 Gohan as a baseline.

## Report

`docs\tasks\2026-10-30-zhack-review\style-study-report.md`: SHIPPED and PENDING tables, the comparison per anim (short
tables), the finger pose section, the style guide, the redraw plan and my questions. Keep it readable: tables and
short sentences, with the sheet file names.

## Limits

- Read the hack sources with `py -3.14 -I` scripts kept in `scripts\one-time\2026-10-30-zhack-review\` (names starting
  `style_`); run nothing from the sources. Writes only to those scripts, `LOG\zhack\study\` and the report. Never write
  into `art\`, a module, a build, `data\`, `docs\RE-BIBLE.md` or `docs\ledger\`.
- Python: `py -3.14 -P` for our own art tools. LF, no em or en dashes. Never `cd` or `Push-Location`; absolute paths
  only.

