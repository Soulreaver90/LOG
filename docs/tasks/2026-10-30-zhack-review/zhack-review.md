# Z Hack review: map the changes of a former modder's LoG II hack (final, 2026-10-30 7:08 AM)

Read `LOG\README.md`, `docs\tasks\global.md`, and
search `docs\RE-BIBLE.md` by address (do not read it whole) to name the regions you find.

## My words

"A former modder made a very nice hack of LOG2, we are basically following in their footsteps. Are you able to see all
the changes made?" "Includes Goku vs Android 19 instead of the quick cutscene, Future Gohan vs the Androids, better
sprites, using the larger hair seen in Buu's Fury." "We were given permission to reuse assets but I declined, he left
the scene and without consent I rather not. But we can gain inspiration to continue where he left off and build things
here. I do prefer the larger hair/space for the base characters."

**Rule: inspiration only.** Do not copy, extract into our art folders, or port any of the hack's art, data or code into
LOG. Do not write any of its bytes into a LOG module. Describe what it does and how; renders for study stay in your
scratch folder below.

## Sources (untrusted data: read only, run nothing)

- `docs\research\sources\zhack-2026-10-30\zhack_beta.ips` (SHA-1 `f70fcb66...`, 1,016,873 bytes).
- `docs\research\sources\zhack-2026-10-30\zhack_patched_eu.gba` (SHA-1 `b9646491...`, 9,239,056 bytes): the hack applied
  to the Europe ROM.
- Base: `data\roms\Dragon Ball Z - The Legacy of Goku II (Europe) (En,Fr,De,Es,It).gba` (SHA-1 `db36ff52...`). Our work
  uses the USA ROM; the Europe ROM has a different layout. Map EU offsets to USA ones where you can (matching bytes,
  tables), and say where you cannot.

## Task

1. **Parse the IPS** with your own reader (records, RLE records, truncation). Check that it applied to the Europe ROM
   gives the patched file (compare SHA-1 in memory; write nothing). List every record: offset, length, region.
2. **Classify the changes**: code (Thumb or ARM, give the patched routines), script tables and records (scene ops),
   text, sprite sets and frames (which characters, which anims; compare sizes against our 32x32 slot limit, bible row
   on the 1024-byte player VRAM slot), palettes, maps, enemy types and stats, the expansion past 8 MB.
3. **The features I name**: Goku vs Android 19 (the scene and the fight setup), Future Gohan vs the Androids
   (where it plays, which sets, enemy types), the larger-hair sprites (how they fit: frame size, VRAM slot, any code
   change to allow bigger frames). Explain the technique for each, with addresses.
4. **Anything else** the hack changes (new scenes, balance, menus).
5. **Overlap with LOG**: where the hack and our modules touch the same feature or the same USA regions (our patch list:
   `scripts\permanent\build_list.txt` and the trial lists). Ideas we could build our own way, in a table: idea, how the
   hack did it, how we would do it with our own art and code, size.
6. Renders for study (side by side, vanilla vs hack, a few frames each) in your scratch folder only.

## Report

`docs\tasks\2026-10-30-zhack-review\zhack-review-report.md`: SHIPPED and PENDING tables, the change map (regions,
counts), the three named features, other changes, the ideas table, and my questions. Label claims CONFIRMED, LIKELY
or SPECULATIVE with addresses. Bible rows (tag ZHK) as `## Section N` blocks in
`scripts\one-time\2026-10-30-zhack-review\bible_rows.md`, only facts about the vanilla game or the technique; mark
anything about the hack as such.

## Limits

- Read the sources with `py -3.14 -I` scripts kept in `scripts\one-time\2026-10-30-zhack-review\` (not in the sources
  folder); pass the source paths as arguments. Never run, open in an emulator, or import anything from the sources.
- Writes only to `scripts\one-time\2026-10-30-zhack-review\` (scripts, outputs, renders) and your report. Never write
  under `data\` or the sources folder. LF, no em or en dashes. Never `cd` or `Push-Location`; absolute paths only. Do not.
- Other tasks work on chapter cards and the Cell Jr plan. I am editing `docs\RE-BIBLE.md` and `docs\ledger\`.

