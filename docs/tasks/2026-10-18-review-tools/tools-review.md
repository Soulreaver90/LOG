# Two review tools: ROM frame sheet and approved-frame lock (me, 2026-10-18 night)

Personal GBA ROM hack (Legacy of Goku II, USA). Read the headers of `scripts\permanent\rom\log2_sprites.py`, `scripts\permanent\rom\webfoot_decompress.py`, `scripts\permanent\patches\gohan_gi.py` and `art\golden\work_r3\sheet.py` first. Follow the style of the existing `scripts\permanent` tools: an `r"""` header block (Usage, API, Rules, Source), grouped sections, precise names, 1-line comments for the non-obvious why only.

## Why

1. Today we review art folders, not what the built ROM holds. A frame can be right in the folder and wrong in the ROM (wrong env folder, stale build). `log2_sprites.py export` resolves a set id through the base set table constant `SET_TABLE`, so it cannot read the new sets 157-159 in a built ROM: `gohan_gi.py` copies the table and points the literal at rom:0x959C to the copy.
2. I approve frames one by one. After a converter run, nobody can tell quickly which approved frames changed. I asked for a fingerprint of every approved frame so any later change needs re-approval.

## Tool 1: `scripts\permanent\rom\rom_sheet.py`

- `py -3 -I scripts\permanent\rom\rom_sheet.py <rom.gba> <set>[,<set>...] <out.png> [--anims 0,1,9] [--dirs 0,1,2,3] [--scale 4] [--gif]`
- Set id N resolves through the live table: the u32 at rom:0x959C is the table address, entry N - 7. Put this lookup in a function `live_set_offset(rom, set_id)` and use it; prove on the base ROM that it gives the same offset as `SET_TABLE` for ids 7-156.
- One row per (set, anim, dir), sets interleaved so the same anim and dir of each set sit on adjacent rows. One cell per frame index, every cell the same size, each frame drawn at its record dx, dy against one anchor per cell, so offset jumps show. Label each row (`set 157 a9 d0`) and each cell index.
- Background (191, 255, 7) lime, never gray (palette index 13 is gray). Palette: the shared OBJ palette at rom:0x1DA6C8 read from the given ROM. Color 0 transparent.
- `--gif`: one looping GIF per (set, anim, dir) next to out.png, 150 ms a frame (the real frame time is not known; say so in the header).
- Print per row: the frame count and any record whose w x h is over the player slot (`SLOT_BYTES`).

## Tool 2: `scripts\permanent\art\frame_lock.py`

- `lock <art_folder> [--note text]`: write `art\locks\<folder name>\lock.json` plus a copy of every PNG. Fingerprint = SHA-1 of (width, height, the pixel index bytes), not the file bytes (PNG encoding can change without a pixel change). Record per PNG: fingerprint, the keys (anim, dir, index) that use it from the folder manifest, time, note. Refuse to overwrite an existing lock unless `--replace` is given; `--replace` moves the old lock folder to `<folder name>_<yyyymmdd-hhmm>`.
- `check <art_folder> [--sheet out.png]`: compare the folder with its lock. Print changed, added and removed PNGs with their keys. Exit code 1 if any change. `--sheet` writes a lime 6x sheet, one row per changed frame: locked | current | difference mask (changed pixels in black on lime).
- Also accept the golden set: `lock --golden` locks exactly the 12 files `art\golden\golden_gi_{base,ssj,ssj2}_d{0,1,2,3}.png` as one set named `golden`. The folder also holds 3 `golden_gi_ssj2_d0_lightning_*.png` drafts; leave them out.

## Tests

`scripts\permanent\tests\test_tools.py`: live_set_offset equals the SET_TABLE entry for ids 7, 56, 156 on `builds\log2_poc.gba`; a synthetic ROM copy with the 0x959C literal pointed at a moved table resolves through the copy; frame_lock fingerprint ignores PNG encoding (same pixels saved two ways give one fingerprint) and catches a 1-pixel change; check exit codes 0 and 1. Use a temp folder for every write. Run the whole suite: `py -3 -I -m unittest discover -s scripts\permanent -p "test_*.py"` and give the count.

## Run once (deliverables)

1. `rom_sheet.py archive\builds\log2_poc_r7.gba 56,157 ...\r7_base.png --anims 0,1,9` and `59,158,159` the same way (if r7 does not exist, use the newest `log2_poc_r*.gba` and say which). Look at both sheets yourself and report anything odd.
2. Lock I-approved state: `lock --golden --note "approved 2026-10-18 12:15 AM"`. Do NOT lock the gi_* art folders; I have not approved the regenerated frames yet. Report the 12 fingerprints.
3. Add RE-BIBLE rows for both tools (`docs\RE-BIBLE.md`, tool section; read its row format first). Describe the system as it is.

## Limits

- Read-only on every ROM. Never write under `data\` or `builds\`. Never edit `art\golden\golden_*.png` or any art folder; the lock tool only reads them and writes under `art\locks\`.
- Python files: LF line ends, no byte order mark, no em or en dashes. Install nothing.

## Report

Save it as `docs\tasks\2026-10-18-review-tools\tools-review-report.md`: files and functions (file:line), test count, sheet paths, the 12 golden fingerprints, anything odd seen in the sheets. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with status and a 3-line summary only.

