# Task 5 part 2: Steps 6-7 (patch and test ROM)

Read `task-5-brief.md` Steps 6-7 and `global.md` first. They are your requirements.

## My decisions for this part

- **Art status.** I reviewed your fix round 1 and accepts the art for a test build (Ruling 33). My art gate stays open: I may still ask for changes, so the build must come from `gi_art.py` output with no hand step, and a rebuild must be one command.
- **Set ids (Ruling 18).** 157 gi base (set 56 layout), 158 gi Super Saiyan (set 59 layout), 159 gi Super Saiyan 2 (set 59 layout, your 159 frame headers). Relocate the set table (literal rom:0x959C) to the expansion area with words for 157-159. Set id N >= 7 uses entry N-7.
- **Patch sites (re-outfit.md section 6).** rom:0x1D96A5 `38` to 157 (0x9D), rom:0x1D96E1 `3B` to 158 (0x9E). Repoint rom:0x42F0 to an unchanged copy of the appearance table (the reverse lookup 0x080042BC must still find the original ids). Store every offset in `alloc.notes["gohan_gi"]`, including the set 159 offset that Task 6 needs.
- **Geometry (Ruling 30, your concern 1).** Each gi record keeps its frame's own w, h, dx, dy, attr0 and attr1 from your manifest, including the 22 enlarged SSJ2 records and the 64x32 lying record. Extend `clone_set` (or add a sibling) so a frame can carry its own record geometry. Keep the Task 2 tests green.

## Facts to CONFIRM before code builds on them

1. **Set id range.** Find every reader of the set id (appearance +1) and the set table. Confirm no bound check rejects ids 157-159 (a `cmp` against a set count, a table length, or a u8 limit in a lookup). Quote the disassembly.
2. **Player OBJ VRAM size.** Find how the game reserves VRAM tiles for the player sprite and the largest frame it allows. Confirm every gi frame fits, the enlarged 32x64 and 64x32 SSJ2 records included. If a frame does not fit, report it and stop for my ruling. Do not change the VRAM layout on your own.
3. **Shape and size bits.** Confirm attr0 and attr1 shape and size bits match each enlarged w and h (GBA OBJ shape/size table).
4. **Raw frames.** Confirm the decoder plays type 0 (raw) frames on the player path, as Task 2 found.

## Tests

- Un-skip and pass the two part 2 tests: `test_appearance_2_resolves_to_gi_clone` (Review Focus 1) and `test_armor_sets_untouched` (Review Focus 2).
- Add: every record of sets 157-159 decodes to w*h bytes and equals the manifest PNG pixels (Review Focus 5); the Super Saiyan entry resolves to 158; set table words for ids 7-156 are unchanged; rom:0x42F0 points at a table that equals the original bytes.

## Build

Build `builds\log2_poc_gi.gba` with `log2_build.py` and patch `gohan_gi`. Print and log the SHA-1 in `docs\build-log.md`. Add RE-BIBLE lines for every confirmed fact.

## Report

Write `docs\tasks\2026-10-16-task-5-gi-art\task-5-part2-report.md`. Give status, the confirmed facts with quotes, the test count, the build SHA-1 and any concern. Never write under `data\`.
