# Review: the modders' audio tool, sprite tool and the Buu's Fury compressor (final, 2026-10-22 3:17 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Current build r27 (`builds\log2_poc_r27.gba`). Read first: `docs\RE-BIBLE.md` (codec rows: search `#codec`, `#sprite`, `#audio`, `#music`; rows tagged DCR from the decomp review), `docs\research\re-sprite-decompression.md`, `docs\tasks\2026-10-20-decomp-review\decomp-review-report.md` (the `webfoot_lz.py pack()` note and the two decoder differences), and the work log entry "2026-10-21 7:50 PM" in `docs\ledger\progress.md`.

## My ask

"Have another task review the tools and compressor." The modders who shared these are friendly and share their findings. I want to know what we can use, and how safely.

## The three items

1. **Webfoot Audio Engine**: `%USERPROFILE%\Documents\GitHub\webfootaudioengine` (commit 1bb0085, no license file). Python plus a web UI. Scans Webfoot music and SFX tables, exports and imports Impulse Tracker `.it` modules, adds song slots with table relocation.
2. **Sprite Swapper and Image Extractor**: `%USERPROFILE%\Documents\GitHub\Sprite-Swapper-Image-Extractor` (README only; the tools are Windows `.exe` files in a GitHub release, V1.0.1, with a bundled `jcalg1.exe`). No license file.
3. **Buu's Fury compressor**: `webfoot_lz.py` `pack()` in `%USERPROFILE%\Documents\GitHub\buusfury-decomp` (MPL-2.0).

## Questions

1. **Audio tool:**
   - Read the code paths for `scan`, `import-it` (add-slot and replace) and `rom_support\debug_patches.py`. Say what each writes to a ROM and where.
   - How does it choose free space when it adds a song, relocates a table or writes samples? Could it write over 0xFF space our build reserves: the portrait region at `rom:0xF00000 + 0x1008 x id` (unused id slots are 0xFF), the old frame space reserved by `art_inject`, and allocator space used by later patches? Name the function and quote the lines.
   - Network calls, file writes outside the chosen output, subprocess calls, anything the web UI loads from the internet.
   - Does its table detection find LoG II USA's music and SFX tables? Compare its parsers with what the bible and the decomp review say (music record +8 sample directory).
   - Which song plays in Gohan's Rage scene at the Cell fight (map 14,3; find the script's music command if the bible or the tool's tables make it findable)? Mark the label.
   - The workflow for my MIDI: MIDI to `.it` in OpenMPT within the tool's limits (15 channels, effects list, direct volumes), then import. Say how to reuse LoG II's own samples.
2. **Sprite tool:** with no source, review only from the README and the release listing (`gh release view -R ghxstboyy/Sprite-Swapper-Image-Extractor-for-Buu-s-Fury-and-Legacy-Of-Goku`). Do not download or run the `.exe` files. What does it do that our tools do not? Its README says it compresses with JCALG1: is our sprite codec JCALG1 (compare the bible codec rows and `re-sprite-decompression.md` with the published JCALG1 format)? Say what its "larger sprites than the original" insert implies for our allocator and fixed regions.
3. **Compressor:** read `webfoot_lz.py` in full. Which formats does `pack()` emit, and do they match our decoder in `scripts\permanent\` (find it) and the ROM's ARM routine at `@0x03000000`? Check the two decoder differences the decomp review named. If the file is pure Python with no I/O, network or subprocess, you may copy the needed function into `scripts\one-time\2026-10-22-modder-tool-review\` (keep its MPL-2.0 header) and run a round trip: our decoder on its output equals the input, for at least 20 real LoG II sprite frames and portraits (decoded from r27), plus the compressed size against the original. Is it JCALG1 too?

## Running anything

- **Audio tool:** after you read the `scan` path and find no network, subprocess or write outside `--out`, you may run only `scan` on a copy of r27 in `scripts\one-time\2026-10-22-modder-tool-review\`, with `py -3 -I`, output into `scripts\one-time\2026-10-22-modder-tool-review\`. Never run the web UI, any `import-*` command or `build_webapp.py`. Never install its requirements; if `numpy` is missing under `-I`, say so and stop the run.
- **Compressor:** only the copied function, as above.
- **Sprite tool:** nothing.
- Never run anything inside the clones. Never change their files or git config.

## Deliverable

- A verdict per tool: use now, use with limits (which), or do not use, with the reasons.
- Bible rows in `scripts\one-time\2026-10-22-modder-tool-review\bible_rows.md` with "## Section N" headings as in `scripts\one-time\2026-10-19-r21-build\bible_rows.md`, only for LoG II facts you prove.

## Parallel run

- A build task writes `scripts\permanent\`, `tests\`, `builds\` and `scripts\one-time\2026-10-22-r28-build\`. Do not touch them. You write only `scripts\one-time\2026-10-22-modder-tool-review\`.

## Limits

- Read-only on every ROM and save. Never write under `data\`.
- Python: LF, no byte order mark, no em or en dashes. Never `cd` in any shell call; absolute paths only. Write every file with Python, and check it for control characters.
- Label every claim CONFIRMED, LIKELY or SPECULATIVE, and quote the file and line for each claim about the tools.

## Report

Save it as `docs\tasks\2026-10-22-modder-tool-review\tool-review-report.md`: the answers, the verdicts, the safety notes, the round-trip result and the open points. Then reply with the three verdicts, the top risks and the Rage song finding only.

