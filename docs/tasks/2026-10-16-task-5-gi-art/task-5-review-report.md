# Task 5 review report (art, patch and build)

Scope: snapshot base-T5 to live (task-5-review.diff), against task-5-brief.md, progress.md Rulings 18 and 20-35, task-5-fix-r1.md, task-5-part2-dispatch.md and global.md. Read-only. I did not re-run the suite.

## Spec Compliance

**Pass, with Minor deviations.** All four named risks hold. I checked each one against the diff and with one focused check per risk.

### Named risk 1: churn in webfoot_decompress.py, test_sprites.py, RE-BIBLE.md (and log2_sprites.py)

- **Most of the churn is line endings.** In base-T5 these four files are LF only (CR=0). In live they are CRLF on every line (for example webfoot_decompress.py: base CR=0 LF=255, live CR=257 LF=257). `git diff --no-index --ignore-cr-at-eol` gives the real size:
  - webfoot_decompress.py: +7 / -5 (not 512)
  - test_sprites.py: +14 / -0 (not 316)
  - RE-BIBLE.md: +46 / -4 (not 560)
  - log2_sprites.py: +58 / -0 (not 436)
- **The real webfoot change is in scope and safe.** Only `read_set` changed, plus a new constant `SET_DIRS = 4`. It now reads u16 +0 as `slot` and always walks 4 directions. That is Ruling 35's "fix read_set" order. The decompressor (`unpack_frame`, the stream code, `frames_of`, `read_record`) has no change. For Gohan sets byte +1 was already 4, so set 53-59 parsing is unchanged. All callers of `read_set` (log2_sprites.py:86, :131, :178; webfoot_decompress.py:233; test_sprites.py) use `dirs`, `anims`, `table`, `ptrs` only. They take the new value without change.
- **The real test_sprites change** is one new test, `test_read_set_uses_four_directions` (test_sprites.py:105-118). It is in scope.

### Named risk 2: patches\gohan_gi.py writes into the base 8 MB

Holds. Focused check: byte diff of `builds\log2_poc_gi.gba` against the base ROM over rom:0x0-0x7FFFFF.

- Changed runs: rom:0x42F0 (3 bytes, the literal), rom:0x959C (3 bytes, the literal), rom:0x1D96A5 (1 byte), rom:0x1D96E1 (1 byte). Nothing else in the base 8 MB changed.
- rom:0x42F0 now holds 0x08800000. The 440 bytes there equal the original appearance table at rom:0x1D967C.
- rom:0x959C now holds 0x08863548. The first 600 bytes (ids 7-156) equal the original table at rom:0x3B4E90. Ids 157, 158, 159 hold 0x0881FE14, 0x0883FDD0, 0x0886339C.
- Appearance entry 2 +1 = 157 and entry 5 +1 = 158.
- Built ROM SHA-1 is 40d66d64dfda1179365b094194083ff828f1b6dd, the same as the build-log line.
- The code matches: `_expect` checks the two literals and the two old bytes first (gohan_gi.py:56-59). The appearance copy is taken before any edit (gohan_gi.py:62-64). `build_set` and the table write only into `alloc.alloc` space, and the build Allocator has one region, rom:0x800000 size 0x800000 (log2_build.py:30, :41).

### Named risk 3: build_set and read_set encoding

Holds. Focused check: I walked sets 157-159 in the built ROM through the relocated table.

- Header: u16 +0 = 0x400 in all three. Header plus the 4 x 16-byte boxes equal the layout set (56, 59, 59) byte for byte. The null pattern of the animation table equals the layout set.
- Keys: 288, 276, 276 records. The key set equals the layout set's key set.
- Records: 12 bytes, packed as `<bbBBHHI` (dx, dy, w, h, attr0, attr1, GBA pointer) at log2_sprites.py:209. This matches `read_record` (webfoot_decompress.py:177).
- Frames: every record points at a type 0 header whose size word equals w*h. Shape and size bits match w and h in every record. The largest frame is 1024 bytes. All records and frame headers are 4-aligned (the DMA at 0x0800784C copies 32-bit words).
- Set word +8 (the remap pointer that becomes obj+0x24) is 0 in base sets 56 and 59 and in built sets 157, 158 and 159. So the upload at 0x080077E6 takes the type test, and type 0 frames are read straight from ROM (part 2 fact 4).
- build_set refuses a missing key, an extra key, a wrong byte count, a frame larger than the header slot, and wrong shape bits (log2_sprites.py:186-202).
- Byte spot checks of the part 2 RE claims on the base ROM agree with the quoted disassembly: rom:0x75B0 = 0x8809 (`ldrh r1,[r1,#0]`), rom:0x75B6 = 0x81E1 (`strh r1,[r4,#0xe]`), rom:0x934C = 0x2807 (`cmp r0,#7`), rom:0x77D8 = 0x7881 (`ldrb r1,[r0,#2]`), rom:0x781C = 0x3008 (`add r0,#8`).

### Named risk 4: tests assert real behavior on the built ROM

Mostly holds. GiPatchTests builds a real ROM in setUpClass (test_gi.py:195-203) and reads it through the relocated literals.

- The chain is not circular. GiArtTests compares the manifest geometry with the original records read from the base ROM at fixed offsets (test_gi.py:29, :107-123). `test_gi_sets_decode_to_manifest_pixels` then proves that the ROM equals the manifest and the PNGs (test_gi.py:235-255). Together they tie the ROM to the original geometry.
- `test_armor_sets_untouched` checks the records and pixels of sets 55, 56, 58, 59, and also that the relocated table gives the same set offsets (test_gi.py:217-221).
- One tautology: see Minor 3.

### Missing

- None that blocks. The brief's `make_gi_base` and `make_gi_form` interfaces do not exist. See Minor 5.

### Extra

- RE-BIBLE section 10a (community prior art) and the design-doc additions (hair, chest, Piccolo risk, Buu's Fury scope, slice 3-4 engine risk) are not Task 5 work. They carry my dates and match Rulings 19-21 and 34. I cannot tell who wrote them. They are not defects.

### Misunderstood

- None found in behavior.
- One contract deviation: the `alloc.notes["gohan_gi"]` keys differ from the names in Ruling 1. See Minor 4. If Task 6 uses the Ruling 1 names, it fails loudly with a KeyError. It does not fail silently.

### Cannot verify (warnings)

1. In-game behavior: the gi shows when Gohan is playable, cutscenes keep the armor, ext op 73 (0, 56) does not hang, and no VRAM overwrite happens. The report labels these LIKELY. Only my test can confirm them.
2. Art quality after the Ruling 35 trim. The lying SSJ2 frames 12.2.x and 12.3.x lost 9 of about 13 hair columns (part 2 report). I did not look at images. My art gate is still open.
3. The full Ghidra listings for facts 1-4. I spot-checked 5 instructions only.
4. ext op 73 (0, 56) in the post-Cell scene. The reverse lookup finds entry 2 through the unchanged copy, and that entry index goes into the record. docs\research\re-outfit.md:87 (section 3, CONFIRMED) says that ext 73 sets the player sprite from the raw argument (56), not from the appearance table. So the scene keeps the armor, and Gohan shows the gi again when he is playable. That is the slice 1 intent. Only my play test confirms it in the game.

## Strengths

- The patch is small, ordered and fail-closed. It checks every old byte before it writes, it copies the appearance table before the edits, and it writes nothing outside the four planned sites in the base ROM.
- `build_set` is a clean sibling of `clone_set`. It leaves the Task 2 path unchanged and validates every record against the slot and the GBA shape table.
- `read_set` now matches the game (u16 slot, 4 hardcoded directions). The new test proves it over all 150 sets: no record is larger than its slot, and set 136 now walks 24 records.
- The art pipeline enforces Ruling 35 at generation time (`make_gi_set` raises above SLOT_BYTES, gi_art.py:939). A future art change cannot bring back an oversize frame.
- The art tests recompute checks from the PNGs (torso skin, armor white) instead of trusting the manifest numbers. The report shows mutation evidence that they can fail.
- The RE-BIBLE gained tagged, sourced lines for every part 2 fact, with addresses.
- The rebuild is one command and reproducible (two builds gave the same SHA-1).

## Issues

### Critical

None.

### Important

None.

### Minor

1. **Line-ending churn (all four churned files, plus mixed endings).**
   - What: webfoot_decompress.py, test_sprites.py, log2_sprites.py and RE-BIBLE.md went from LF to CRLF. gi_art.py and test_gi.py are CRLF. gohan_gi.py, log2_build.py, rom_space.py and build-log.md are LF.
   - Why: The review diff grew by about 1,500 noise lines. This hid a 12-line decompressor change inside a 512-line hunk. The next snapshot diff will have the same problem.
   - Fix: Convert the Task 5 files back to LF, to match the base. Compare snapshots with `--ignore-cr-at-eol` until then.

2. **Stale RE-BIBLE lines that contradict Ruling 35 and Ruling 27.**
   - What:
     - RE-BIBLE.md:87 still says "18 gi SSJ2 frames (48 keys, 32x64 and 64x32) do not fit" and is tagged `#open`.
     - RE-BIBLE.md:260 still says "22 of 159 frames need a larger OBJ record (32x32 or 32x64)" and is tagged `#open`.
     - RE-BIBLE.md:74 keeps the disproved "+1 dirs" claim with label L.
     - RE-BIBLE.md:277 and the design doc line 114 say "the body from set 53". Ruling 27 makes set 53 a style reference only. The part 1 report concern 7 flagged this.
   - Why: The global constraints make RE-BIBLE the first source for every task. Lines 87 and 260 carry the C label and are now false. Task 6 reads this index first, so I may want this fixed before it dispatches Task 6.
   - Fix: Mark RE-BIBLE lines 87 and 260 answered by Ruling 35 (every frame now 32x32 or smaller), and drop `#open`. Relabel line 74 as superseded. Add a note on line 277 that Ruling 27 replaced the set 53 body.

3. **Tautological assert in the Review Focus 1 test.**
   - What: test_gi.py:208 asserts `set_offset(rom, rom[APPEARANCE + 41]) == set_offset(rom, 157)` right after asserting that the byte is 157. It cannot fail on its own.
   - Why: The brief asked for `resolve_playable_appearance(rom, 2) == gi_base_set_offset(rom)`, which compares against an independent value. The coverage holds today only because `test_gi_sets_decode_to_manifest_pixels` separately proves that id 157 decodes to the gi_base art.
   - Fix: Compare with an independent value, for example `alloc.notes["gohan_gi"]["set_157"]` returned from the build. Or assert that the set at that offset decodes to the gi_base manifest.

4. **The `alloc.notes` keys differ from Ruling 1.**
   - What: gohan_gi.py:85-86 stores `appearance_copy`, `set_table`, `set_157`, `set_158`, `set_159`. Ruling 1 named `{"base", "ssj", "ssj2"}`.
   - Why: Task 6 consumes the set 159 offset through this hand-off. Task 6 is not built yet, so nothing breaks today.
   - Fix: I pick one name set and tells the Task 6 implementer. Or gohan_gi adds the Ruling 1 aliases.

5. **The brief's art interfaces were replaced without a recorded ruling.**
   - What: `make_gi_base(set53_dir, out_dir)` and `make_gi_form(...) -> list[str]` do not exist. The live API is `make_gi_set(name, layout, out_dir, palette, fixes)` and `form_layout(name)` (gi_art.py:875, :884). Unmatched keys go to the report (section 5), not to a return value.
   - Why: Ruling 27 changed the method, so the change is justified. No ruling names the new interface, and no test calls these functions directly.
   - Fix: Record the new API in progress.md as a ruling note. No code change is needed.

6. **Control flow keyed on note text.**
   - What: gi_art.py:918 and :924 test `"base head kept" in note`. The string is built at gi_art.py:666.
   - Why: If someone edits that message, the trim loop and the body-only IoU change behavior with no error.
   - Fix: Return a flag from `stand_in_head`, or use a named constant for the marker.

7. **Hand fixes use image coordinates.**
   - What: `_PUNCH_BAND` (gi_art.py:1293) sets pixels (6,19) and (6,20) in the output image of 7.2.3.
   - Why: If a later rule enlarges or moves that record, the band lands on the wrong pixels and no check catches it.
   - Fix: Store the fix in object space (as PART_HINTS does). Or assert that the record geometry is unchanged before the fix is applied.

8. **Duplicated constants and helpers.**
   - What: `OBJ_SHAPES` (log2_sprites.py:32) and `OBJ_SIZES` (gi_art.py:84) are the same table. The slot size 0x400 appears in gi_art.py:87, test_gi.py:261 and the gohan_gi docstring. `_untile` (test_gi.py:264) repeats the tile walk in log2_sprites.tiles_to_image.
   - Why: There are two places to keep in sync.
   - Fix: gi_art imports `OBJ_SHAPES` from log2_sprites. The test uses `tiles_to_image(...).tobytes()`.

9. **gi_art.py structure (1373 lines).**
   - What: One module holds the armor-to-gi conversion, the per-frame checks, the contact sheets, the animation strips and GIFs, the transform comparison, the HUD icon, the hand fixes and the CLI. `armor_to_gi` is a 145-line function (gi_art.py:335-477) with many inline thresholds (0.55, 1.4, 2.5, 3.5) and palette indices (72, 195, 23, 114-117). Named constants exist for some of these.
   - Why: The sections are clearly marked and the per-frame checks guard the output, so the module works today. But a change to one heuristic is hard to reason about, and the review code (about 300 lines) is mixed with the generator that the build depends on.
   - Fix (later, not a blocker): Split it into three modules: the generator with its checks, the review sheets and GIFs, and the HUD icon. Break `armor_to_gi` into part classification, arms and cuffs, and repaint. Use the named palette sets (WRISTBAND, SKIN) in place of literals. The outer variable `far` (gi_art.py:351) is reused with another meaning at :433. Rename one of them.

10. **Duplicate build-log line.** docs\build-log.md has two identical `log2_poc_gi.gba` lines (00:57 and 00:58). The report states this. It is harmless and accurate, so keep it or annotate it.

## Assessment

**Task quality: Approved.** The patch writes only the four planned base-ROM sites. The relocated tables equal the originals, and every gi record is a raw 12-byte record of w*h bytes within the 1024-byte slot. I confirmed this on the built ROM. The large churn is mostly LF to CRLF conversion around a small, in-scope `read_set` fix. The Minor items are documentation drift, test precision and maintainability. I can fix them in a later pass.
