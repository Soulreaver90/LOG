# Task 5 part 2 report (Steps 6-7)

Date: 2026-10-17. Status: **BLOCKED on fact 2 (player OBJ VRAM size)**. The dispatch says: "If a frame does not fit, report it and stop for my ruling. Do not change the VRAM layout on your own." 18 gi Super Saiyan 2 frames do not fit. I did not write `patches\gohan_gi.py`, did not change `clone_set`, did not change the tests and did not build a ROM.

---

## Summary

This section gives the result of each of the four facts.

| # | Fact | Result | Label |
|---|---|---|---|
| 1 | No bound check rejects set ids 157-159 | Holds | CONFIRMED |
| 2 | Every gi frame fits the player OBJ VRAM slot | **Fails for set 159**: 18 frame headers (48 keys) are 2048 bytes; the slot is 1024 bytes. Sets 157 and 158 fit | CONFIRMED |
| 3 | attr0 and attr1 shape and size bits match w and h | Holds for all 840 keys, all 8bpp | CONFIRMED |
| 4 | The player path plays type 0 (raw) frames | Holds; raw frames are read straight from ROM | CONFIRMED |

> [!WARNING]
> A 2048-byte frame on the player overwrites the 1024 bytes of OBJ VRAM after the player's slot. In the save state `builds\log2_pad16.ss1`, that space holds a live sprite (OAM tile 442 = player tile 410 + 32).

Disassembly came from Ghidra headless on `scratch\ghidra\log2.gba` (unchanged base ROM). Listings: `scripts\one-time\2026-10-16-task-5-gi-art\dis_upload.txt`, `dis_vram.txt`, `dis_chain.txt`, `dis_setid.txt`, `dis_14.txt`, `dec1.txt`-`dec3.txt`. Wrapper: `scripts\one-time\2026-10-16-task-5-gi-art\gh.sh` (it sets JAVA_HOME to the installed Temurin JDK 21; Java is not on PATH).

---

## Fact 2: player OBJ VRAM size (CONFIRMED, does not fit)

The player's tile slot size is the u16 at set header +0, read once when the player object is built.

**Slot allocation.** Sprite root constructor 0x080075A8 (r1 = set pointer):

```
080075b0  ldrh r1,[r1,#0x0]          ; r1 = u16 at set+0
080075b6  strh r1,[r4,#0xe]          ; obj+0xE = slot size in bytes
080075b4  ldr r0,=0x081da970 ; ldr r0,[r0]
080075bc  bl 0x080067ac              ; OBJ VRAM allocator (size >> 6 = 64-byte units, best fit)
080075c0  strh r0,[r4,#0xc]          ; obj+0xC = tile index
080075c6  str r5,[r4,#0x48]          ; obj+0x48 = set
080075de  ldrh r0,[r5,#0x0] ; bl 0x0801f08c ; str r0,[r4,#0x30]   ; heap buffer of the same size
```

**Player constructor chain.** r1 passes unchanged: 0x080129B8 (player, vtable 0x08025F28) calls 0x080086D4 (r1 = r6 = r1), then 0x0800F80C (`0800f810 bl 0x080078e4`), then 0x080078E4 (`080078ea bl 0x08019b30`), then 0x08019B30 (`08019b34 bl 0x080075a8`). None of them writes r1 before the call.

**VRAM copy, no clamp.** 0x0800784C:

```
0800784c  ldrh r1,[r0,#0xc] ; ldr r2,=0x06010000 ; ldr r3,=0x040000d4
08007852  lsl r1,r1,#0x5 ; add r1,r1,r2       ; dst = 0x06010000 + tile*32
08007856  ldr r2,[r0,#0x34] ; ldr r0,[r0,#0x38]  ; src = obj+0x34, bytes = obj+0x38
0800785a  str r2,[r3] ; str r1,[r3,#4] ; lsr r0,#2 ; strh r0,[r3,#8] ; 0x8400 -> [r3,#0xa]   ; DMA3, 32-bit words
```

obj+0x38 is w*h of the record (`080077d8 ldrb r1,[r0,#2] ; ldrb r2,[r0,#3] ; mul r1,r2 ; str r1,[r4,#0x38]`). Nothing compares it with obj+0xE.

**Header values.** Sets 53, 55, 56, 57, 58 and 59 all have u16 0x0400 at +0. Across all 150 sets in the table, no record is larger than its set's u16 (sizes: 0x400 x77, 0x200 x54, 0x1000 x15, 0x100 x3, 0x40 x1). The largest original Gohan frame is 1024 bytes (32x32).

**Save state check.** `log2_pad16.ss1`, player object 0x02031CA0 (pointer at 0x03001FA8, set 55): +0xC = 0x019A (tile 410), +0xE = 0x0400, +0x30 = +0x34 = 0x02031898, +0x38 = 0x200. OAM obj 3 uses tile 442 = 410 + 32, so the next allocation starts right after the 1024-byte slot.

**Frames that do not fit (gi Super Saiyan 2 only).** Keys over 1024 bytes:

- 32x64: 9.x.1, 9.x.2, 9.x.3 (transform), 11.x.0, 11.x.1 (arms up), 20.x.0-20.x.3 (flying), 21.x.0 (revert), each in all 4 dirs.
- 64x32: 12.2.0-12.2.3 and 12.3.0-12.3.3 (lying).
- Total 48 keys, 18 frame headers. gi base and gi Super Saiyan: 0 keys over 1024.

**Two findings that limit the options:**

1. **Transform does not reallocate. CONFIRMED for the direct path.** 0x08014D58 sets `str r0,[r4,#0x48]` (0x08014DA2), calls vtable +0x28 (player vtable 0x08025F28 +0x28 = 0x08012A04: it allocates a 16-byte state object with heap `bl 0x0801f08c`, then `bl 0x0800763c`), then `bl 0x080086a2` (sets obj+0x180 from the appearance form object). None of them calls the VRAM allocator 0x080067AC. So the slot keeps the size of the set the player was built with (map load and similar constructor paths). Raising only set 159's u16 would not help on the step from Super Saiyan into Super Saiyan 2.
2. **Header byte +1 is the high byte of the size u16, not a direction count.** In every set, byte +1 equals size >> 8 (4 for 0x400, 2 for 0x200, 16 for 0x1000). The game hardcodes the rows (`08007568 ldr r0,[r4,#0x48] ; add r0,#0x4c`, which is 12 + 16*4 for anim 0). `read_set` in `webfoot_decompress.py` takes dirs from byte +1, so a set with size 0x800 would parse as 8 directions. The sets with 0x200 or 0x1000 may already parse wrong in the tools. This is an open item for the tools. I did not change them.

### Options for me

I give the cost of each option. I do not choose one.

| Option | What | Cost and risk |
|---|---|---|
| (a) | Shrink the 18 enlarged SSJ2 frames to 1024 bytes or less (32x32, or 64x16 / 16x64 where the shape fits) | Art rework. It partly reverses the Ruling 30 acceptance: the set 58 head on the set 59 body does not fit 32x32 in these poses, so hair or fists are clipped or the head is scaled. No code change |
| (b) | Set the u16 to 0x0800 in all three gi set headers (157, 158, 159) | All three need it, because the slot is sized at construction and the transform keeps it. Doubles the player's OBJ VRAM (1024 more bytes). Needs proof of allocator headroom in the busiest scenes (allocator returns -1 when full, effect not traced). Needs the `read_set` dirs fix first, or the tools read 8 directions |
| (c) | Draw each enlarged frame as two OBJs | New code in the OAM build at 0x08007772 (one record gives one OAM entry today). Largest change |

> [!NOTE]
> Sets 157 and 158 fit. A partial build with gi base and gi Super Saiyan only is possible if I rule for it. Set 159 is needed by Task 6.

---

## Fact 1: set id range (CONFIRMED)

`get_set` 0x08009324 has no upper bound:

```
08009328  cmp r0,#0x0 ; bne 0x0800934c
0800934c  cmp r0,#0x7 ; bge 0x08009364
08009364  ldr r1,=0x083b4e90 (literal rom:0x959C) ; lsl r0,r0,#2 ; add r0,r0,r1 ; sub r0,#0x40 ; ldr r0,[r0,#0x24]
```

So id N reads word N-7 of the table at the literal. The relocated table needs at least 153 words (ids 7-159).

- Appearance call sites go from `ldrb r0,[r0,#0x1]` straight to `bl 0x08009324`, with no compare between: 0x08001ADA/0x08001ADC, 0x08008624/0x08008626, 0x0800C5CE/0x0800C5D0, 0x08010C4E/0x08010C50, 0x080111E4/0x080111E6, 0x08014D9C/0x08014D9E, 0x0802646A/0x0802646C. I read the 14 instructions before each of the 17 BLs. The only compares there are `0800937a cmp r0,#0` (id 0 test), `0800a94c cmp r4,#0` (player object test) and `08019118 cmp r0,r5` (after the call).
- The other call sites (0x0800AF1C, 0x0800B01A, 0x0800B718, 0x0800D6E4, 0x0800E2A2, 0x08018F24, 0x0801902C, 0x08019114) take ids from scripts or data. They never receive 157-159 in this patch.
- Reverse lookup 0x080042BC compares appearance +1 bytes with its argument (`080042ca ldrb r3,[r3,#0x1] ; cmp r3,r1`). It reads the unchanged copy at the rom:0x42F0 literal.
- Set ids are u8 at every appearance read (`ldrb`). 157-159 fit.

## Fact 3: shape and size bits (CONFIRMED)

The OAM build copies the record's attr0 and attr1 into OAM and changes only the position fields:

```
08007784  ldr r1,[r4,#0x3c] ; ldr r1,[r1,#0x4]   ; record +4 word = attr0 | attr1 << 16
08007788  str r1,[r0,#0x0]
0800778c  and r1,r3 (0xFE00FFFF)                  ; clear attr1 x
08007798  lsr r1,#8 ; lsl r1,#8 ; orr y           ; replace attr0 y
```

All 840 gi keys (288 base, 276 Super Saiyan, 276 Super Saiyan 2) have shape (attr0 >> 14) and size (attr1 >> 14) equal to the GBA table for their w and h. 32x64 is shape 2, size 3. 64x32 is shape 1, size 3. Every key has attr0 bit 13 set (8bpp). 0 mismatches.

## Fact 4: raw frames on the player path (CONFIRMED)

The upload 0x08007772 runs for the player (vtable chain above). For Gohan sets obj+0x24 = set word +8 = 0, so it takes the type test:

```
080077e6  ldr r2,[r4,#0x24] ; ldr r0,[r0,#0x8] ; cmp r2,#0 ; beq 0x080077f6
080077f6  ldr r1,[r0,#0x0] ; cmp r1,#0x0 ; beq 0x0800781c   ; header type 0 = raw
080077fc  add r1,r5,#0 ; bl 0x0801f394                       ; type 1 or 2: unpack to the stack buffer
08007802  ...DMA3 stack buffer -> obj+0x30, obj+0x34 = obj+0x30
0800781c  add r0,#0x8 ; str r0,[r4,#0x34] ; mov r0,#1        ; raw: obj+0x34 = header + 8 (ROM)
```

A raw frame skips the heap buffer and the 0x1000-byte stack buffer. 0x0800784C then copies it from ROM to VRAM. The overflow risk from fact 2 is in VRAM only. The heap buffer (obj+0x30) is never written for raw frames.

---

## Tests and build

- Tests: not changed. The last run gave 29 tests, OK, 2 skipped (the two part 2 tests).
- Build: none. No `log2_poc_gi.gba`, no build-log line.
- Nothing written under `data\`. No git.

## RE-BIBLE

I added lines for facts 1-4, the slot allocation, the VRAM copy, the transform, the header +0 size word and the `read_set` open item. Source tag `T5P2` = this report.

## Concerns

1. Option (b) needs an OBJ VRAM budget check. I did not measure free VRAM in busy scenes (bosses use 0x1000 slots).
2. The SSJ2 frames were enlarged under Ruling 30 because the set 58 head on the set 59 body is taller than 32 px in these poses. Option (a) loses pixels in those poses.
3. The tools' `read_set` reads directions from header +1. That is wrong for sets whose size u16 is not 0x400. Gohan sets are not affected.

---

## Ruling 35 round (2026-10-17)

Status: **DONE**. All 18 gi Super Saiyan 2 frames fit the 1024-byte player slot. The part 2 patch is in and the tests pass. `builds\log2_poc_gi.gba` is built.

| Item | Result |
|---|---|
| Build | `builds\log2_poc_gi.gba`, SHA-1 `40d66d64dfda1179365b094194083ff828f1b6dd`, logged in `docs\build-log.md`. A second build gave the same SHA-1 |
| Rebuild command | `py -3 -I scripts\permanent\log2_build.py --out builds\log2_poc_gi.gba gohan_gi` (reads the `gi_art.py` output, no hand step) |
| Tests | 35 ran, OK, 0 skipped |
| Art checks | `gi_art.py all`: 162/159/159 frames, failing 0. Largest key in every form: 1024 bytes |
| Review sheet | `archive\2026-10-18-art-review-renders\fix_r35_before_after.png` (18 frames, before and after, 10x). "Before" copies: `archive\2026-10-17-gi-art-rounds\art-work\r34_gi_ssj2\` |
| Z2 files | Unchanged (22:22) |

### 1. The 18 frames fit 32x32

The stand-in head loses hair lines until the frame fits the slot. The body pixels do not move.

- `slot_window(rec)` is the 32x32 box with the set 59 record's centre column and bottom row. For a 32x32 record it is the record itself (dx -8, dy -24).
- `slot_overflow` measures how far the frame leaves that box (hair is kept 1 px off the edge). `make_gi_set` calls `stand_in_head` again with that `squeeze` until it fits (at most 8 tries).
- `_squeeze` drops rows (top) or columns (left, right), spread evenly between the hair tip and 2 px short of the eyes, so the spikes keep their shape. A back view (no eyes) uses the head centre.
- `make_gi_set` refuses any frame over `SLOT_BYTES` (0x400), so a future art change cannot bring back a 32x64 frame.

| Frames | Lines dropped | Record now |
|---|---|---|
| 9.x.1, 9.x.2, 9.x.3 | 1 row | 32x32, dx -8, dy -24 |
| 11.x.0, 11.x.1 | 1 row (11.x.1: hair top at row -23, the fist skin at -22, fists drawn in front of the hair) | 32x32, dx -8 or -7, dy -24 |
| 12.2.x, 12.3.x (lying) | 9 columns | 32x32, dx -8, dy -24 |
| 20.0.x, 20.2.x, 20.1.x, 20.3.x | 2 rows | 32x32, dx -8, dy -24 |
| 21.x.0 | 1 row | 32x32, dx -8, dy -24 |

I reviewed every frame at 10x, and the anim 9, 12 and 20 strips. The fists, face and body are whole in all 18 frames. The flipbooks show no jump between the trimmed frames and their neighbors.

> [!WARNING]
> The lying frames (12.2.x, 12.3.x) lost 9 of about 13 hair columns. The hair reads as a short spiky fringe, much smaller than the upright Super Saiyan 2 head. The body takes x -1 to 21, so the 32-px box leaves no more room. I should look at this at the art gate.

### 2. `read_set` fix

- `webfoot_decompress.read_set` now uses `SET_DIRS = 4` and returns `slot` (u16 +0). Byte +1 is no longer read as a direction count.
- Effect: sets with slot 0x200 or 0x1000 now walk correctly. For example, set 136 gave 0 records before and gives 24 now. Gohan sets are unchanged.
- New test `test_read_set_uses_four_directions` checks all 150 sets: 4 directions, `slot` equals u16 +0, table at +0x4C, and no record larger than its slot.

### 3. Part 2 patch

- `log2_sprites.build_set(rom, src_set_off, records, frames, alloc)` is new. Every record carries its own dx, dy, w, h, attr0 and attr1 from the manifest, and every frame is raw type 0. It writes each distinct record list once and points the table entries at it. This matters because sets 56 and 59 share some lists between directions, and the gi art may differ per direction. It refuses a missing key, an extra key, a frame larger than the header slot, and shape or size bits that do not match w and h. `clone_set` is unchanged, so the Task 2 tests stay green.
- `scripts\permanent\patches\gohan_gi.py` performs these steps:
  1. It checks the original bytes at every patch site.
  2. It copies the appearance table (440 bytes) before any edit and points rom:0x42F0 at the copy.
  3. It builds sets 157, 158 and 159 from `art\gi_*`.
  4. It copies the set table (150 words) with 3 new words and points rom:0x959C at it.
  5. It writes 157 at rom:0x1D96A5 and 158 at rom:0x1D96E1.
  6. The set header slot stays 0x400.
- `alloc.notes["gohan_gi"]` in this build: `appearance_copy` 0x800000, `set_157` 0x81FE14, `set_158` 0x83FDD0, `set_159` 0x86339C (for Task 6), `set_table` 0x863548. Expansion used: 0x637AC bytes.

### 4. Tests added or un-skipped (`test_gi.py`, `GiPatchTests`, one build per class, logged to `scratch\test-roms\build-log-test.md`)

| Test | Checks |
|---|---|
| `test_appearance_2_resolves_to_gi_clone` | Entry 2 +1 = 157, and it resolves to the set 157 offset in the expansion area (Review Focus 1) |
| `test_super_saiyan_resolves_to_158` | Entry 5 +1 = 158, entry 2 +4 still = 5 |
| `test_armor_sets_untouched` | Sets 55, 56, 58, 59: same records and pixels, same table words through the relocated table (Review Focus 2) |
| `test_set_table_words_7_to_156_unchanged` | The relocated table's first 150 words equal the original |
| `test_reverse_lookup_reads_original_table` | rom:0x42F0 points at bytes equal to the original 440; first +1 match: 53 at entry 0, 56 at entry 2, 58 at entry 4 |
| `test_gi_sets_decode_to_manifest_pixels` | Every record of 157-159: slot 0x400, geometry equals the manifest, w*h <= slot, raw type 0 of w*h bytes, pixels equal the PNG (Review Focus 5) |
| `test_every_gi_frame_fits_the_slot` | Every manifest key of the three art folders is 1024 bytes or less |

### RE-BIBLE

- I added a gi build line with the offsets and a decision line for Ruling 35.
- I marked the `read_set` line fixed and the ruling open row answered.

### Concerns

1. The lying Super Saiyan 2 hair is much smaller (see the warning above).
2. The in-game effects are still LIKELY until I play the build: gi when playable, armor in cutscenes, and ext op 73 (0, 56) with no hang.
3. The build log has two identical `log2_poc_gi.gba` lines (00:57 and 00:58), because I rebuilt once to confirm the SHA-1.

---

## Review fix round (2026-10-17)

This section covers the fixes for the Task 5 review (task-5-review-report.md), Minor 1, 2, 3, 6, 7 and 8. I did not do Minor 9. Minor 4, 5 and 10 are my items.

| Minor | Fix |
|---|---|
| 1 | gi_art.py, log2_sprites.py, webfoot_decompress.py, test_gi.py, test_sprites.py and RE-BIBLE.md are LF again (0 CR bytes). Each conversion changed line endings only: `diff --strip-trailing-cr` against the CRLF copies (`scripts\one-time\2026-10-16-task-5-gi-art\rfix\*.crlf`) shows no difference. Cause: Python `write_text` on Windows writes CRLF. Later edits used byte writes or an in-place edit |
| 2 | RE-BIBLE line 74 is labelled superseded. Lines 87 and 260 say "Answered by Ruling 35", and the `#open` tag is gone. Line 277 notes that Ruling 27 superseded the set 53 body |
| 3 | `test_appearance_2_resolves_to_gi_clone` now compares the resolved offset with `alloc.notes["gohan_gi"]["set_157"]` from a separate `gohan_gi.apply` on a fresh padded base. The Super Saiyan test does the same with `set_158` |
| 6 | `stand_in_head` returns a fourth value, `new_head`. The trim loop and the body-only check use that flag, not the note text |
| 7 | `FIX_GEOMETRY = {"7.2.3": (32, 32, -8, -24)}`. `make_gi_set` refuses a hand fix when the record's (w, h, dx, dy) differs. A mutation with dy -23 raised the error |
| 8 | There is one table: `log2_sprites.OBJ_SHAPES` (gi_art and test_gi use it, and `OBJ_SIZES` is gone). There is one slot constant: `log2_sprites.SLOT_BYTES` (gi_art, test_gi and the gohan_gi docstring use it). test_gi uses `tiles_to_image`, and `_untile` is gone. I also removed an unused `px` variable from the decode test |

**Proof:**
- **Art.** `gi_art.py all` gives byte-identical frame PNGs: the SHA-1 lists of all 480 PNGs before and after are equal (`scripts\one-time\2026-10-16-task-5-gi-art\rfix\png_before.sha1`, `png_after.sha1`). The art checks report 162/159/159 frames, failing 0.
- **Build.** The rebuild gives SHA-1 `40d66d64dfda1179365b094194083ff828f1b6dd`, logged at 01:14.
- **Tests.** 35 ran, OK.
- **Files.** No BOM, no em or en dashes, 0 CR bytes in the changed files.

