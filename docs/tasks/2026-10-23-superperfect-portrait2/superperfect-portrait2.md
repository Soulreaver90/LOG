# Super Perfect Cell portrait (id 52), take 2: one combined reference from all 4 refs (final, 2026-10-23)

Personal GBA ROM hack (Legacy of Goku II, USA). Read the take 1 brief and report first: `docs\tasks\2026-10-23-superperfect-portrait\superperfect-portrait.md` and `superperfect-portrait-report.md`. All its rules, inputs and limits still apply, except where this brief says otherwise.

## My feedback on take 1

"I had sent you 4 images but it seems like you based the portrait entirely on the cell-disturbing-power image. When the goal was to kind of combine them into one reference."

Take 1 picked `Cell-Disturbing-Power.avif` and used the others only for color and line. That is the defect.

## Task

1. Study all 4 refs in `art\portrait-sources\remaster\refs\superperfect\` (convert PNG copies into your work folder; never change the originals). For each ref, write what it contributes: pose and framing, head shape and crest, face and expression, line quality, color and shading, aura and sparks.
2. Build ONE composite reference image at full size from all 4: take each feature from the ref that shows it best, and align them to one pose and one framing that fits id 40's 64x64 portrait. Save the composite and a labeled breakdown image (which region came from which ref) for me.
3. Run the take 1 pipeline on the composite (`b1_label.py` to `b5_detail.py`, stop at vec4, the line rules in `feedback_log_portrait_pipeline.md`), in id 40's palette.
4. Bolts: 2 and 3 thin SSJ2-style bolts, as in take 1. Make both variants.
5. Edit pack per variant with `e0_owner_pack.py`. Run `inject.py check` on each and fix any off-palette pixel.
6. Put my files in `art\portrait-sources\remaster\superperfect\take2\`: both packs, the composite, the breakdown, and a 4x preview of take 1, take 2 and id 40 side by side. Do not change or delete take 1 files.

## Limits

- Two tasks may run now (final, 2026-10-23). The other task builds r35 under `builds\` and `scripts\permanent\`. I am editing `art\base-audit\` and `scripts\one-time\2026-10-23-base-audit\`. Do not touch any of those.
- Never write under `data\`. No ROM build. Never run `inject.py portrait`. Do not copy the fan artist's art into the result as is: use the cyothelion ref only as a guide for line and form, as the pipeline does.
- Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths only. Write and edit files with the Write and Edit tools. Work scripts in `scripts\one-time\2026-10-22-superperfect-study\portrait2\`. Load tools with `py -3 -P`.

## Report

Save it as `docs\tasks\2026-10-23-superperfect-portrait2\superperfect-portrait2-report.md`: what each ref gave, the composite, the stages, the variants, the check results and the paths. Then reply with the pack paths and concerns only.

## Scope change (final, 2026-10-23 9:01 PM, sent to the task)

No in-game portrait: no pipeline, no vec4, no bolt variants, no edit pack. Make one reference anime portrait, full size plus a plain 64x64 downscale framed like id 40. Base: perfect_cell_by_cyothelion_dftprrb-pre.jpg. The other refs are superimposed only to fill what the base lacks. Lightning from Cell-Disturbing-Power.avif. Add a labeled breakdown and a 4x preview next to id 40.
The Limits line on the fan artist's art is lifted for this reference image: I chose the cyothelion image as its base, for my own use.
