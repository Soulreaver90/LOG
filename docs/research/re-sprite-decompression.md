# LoG II sprite decompression (USA, ALFE)

Date: 2026-10-16. ROM SHA-1 `18e0715dec419f3501c301511530d2edcd590f8b`. Addresses are GBA addresses. "ROM 0x..." is a file offset (address minus 0x08000000).

Labels: **CONFIRMED** = proved here with quoted evidence. **LIKELY** = strong evidence, not proved. **SPECULATIVE** = a guess.


## Result in one paragraph

The game decompresses sprite frames with a custom ARM bitstream LZ codec. The codec runs from IWRAM 0x03000000. Its bytes match ROM 0x7FD6BC. The crt0 literal triple at ROM 0x148 is `087FD6BC 03000000 00000E7F` (source, destination, count), so the boot code LIKELY copies it there. Each frame is stored as `{u32 type, u32 size, stream}`. The output is 8bpp tiles in 1D order, ready for a DMA to OBJ VRAM. `scripts\permanent\rom\webfoot_decompress.py` rebuilds the codec. It unpacks the frame header at ROM 0x299DE4 to 512 bytes that are byte-identical to `probe_obj3.bin` (same SHA-1). A brute-force scan of every 4-byte aligned ROM offset finds exactly one stream with the probe: 0x299DEC (the header plus 8). All 11,598 frame records reachable by the set walker (`frames_of`, 4,771 unique frames) unpack cleanly, with output size equal to the header size and to width x height. A second capture adds six exact matches on other characters (see below).

## Proof match (CONFIRMED)

```
> py -3 -I scripts\permanent\rom\webfoot_decompress.py frame <rom> 299DE4 scripts\one-time\2026-10-16-first-probes\frame_299DE4.bin
0x299DE4 type=1 size=512 unpacked=512 packed=240 sha1=28064069dfc5e9583e93875d6b07324a5ade7ff5
> cmp scripts\one-time\2026-10-16-first-probes\frame_299DE4.bin scripts\one-time\2026-10-16-first-probes\captures\01-gohan-base\probe_obj3.bin   -> identical
  probe_obj3.bin sha1                                       28064069dfc5e9583e93875d6b07324a5ade7ff5
> py -3 -I scripts\permanent\rom\webfoot_decompress.py find <rom> probe_obj3.bin    (15 s, all 2M offsets)
0x299DEC unpacked=512 packed=240 probe_at=0
```

The same 512 bytes also sit in the capture at WRAM 0x020315A0 and at VRAM 0x06017800. The decoded output of every walked frame with 4 or more distinct byte values was searched in the RAM dumps. Only these hits came back: 0x299DE4 (set 57) at WRAM 0x020315A0 and VRAM 0x06017800, and set 33 frame 0x247BF4 at VRAM 0x06017C00.

**Correction:** OBJ tile 960 is at VRAM **0x06017800** (0x06010000 + 960 x 32), not 0x060178C0 as the brief said. The decoded frame is at 0x06017800 in `vram.bin`.

### Second capture (CONFIRMED)

Capture `scripts\one-time\2026-10-16-first-probes\captures\02-gohan-gi\`: every probe equals one walked frame, byte for byte.

| Probe | Set id | Anim, dir, frame | Record (ROM) | Frame header (ROM) |
|---|---|---|---|---|
| probe_obj5 (Piccolo, player) | 103 | 0, 0, 0 | 0x305060 | 0x304ADC |
| probe_obj8 (Gohan, battle armor, NPC) | 56 | 0, 0, 0 | 0x2904F8 | 0x2900D4 |
| probe_obj3 | 137 and 138 | 0, 1, 0 | 0x388020 | 0x387D90 |
| probe_obj6 | 76 | 0, 2, 0 | 0x2E4A6C | 0x2E489C |
| probe_obj7 | 121 | 0, 2, 0 | 0x330B18 | 0x330928 |
| probe_obj9 | 156 | 0, 2, 0 | 0x3AC0AC | 0x3ABEB8 |

The OBJ palette half of both captures equals ROM 0x1DA6C8 in 254 of 256 entries. Entry 0 and one other differ. LIKELY the game sets them at run time.

### The sprite object and the WRAM buffer (CONFIRMED)

The capture-01 WRAM holds Gohan's sprite object at 0x020319A8. Its fields match the offsets that the upload code uses.

| Field | Value | Meaning |
|---|---|---|
| +0x10 (u8) | 0 | animation table index |
| +0x14 (u16) | 0 | frame index |
| +0x20 | 0x0829A234 | last uploaded record (the upload is skipped when unchanged, 0x080077C6) |
| +0x24 | 0 | remap table (0 = plain unpack path) |
| +0x30 | **0x020315A0** | DMA3 destination of the unpacked frame (0x0800780C) |
| +0x38 | 0x200 | frame size (w * h) |
| +0x3C | 0x0829A234 | current record |
| +0x40, +0x44 | 0x70, 0x39 | X and Y, equal to OAM obj3 X and Y |
| +0x48 | 0x082A1470 | sprite set 57 |
| +0x4C | 0x082A14BC | its animation table |

The frame upload DMAs into the WRAM staging buffer 0x020315A0, not into VRAM. A later step copies the buffer to OBJ VRAM. That step is not traced.

## Routine addresses

| Address | What | Label |
|---|---|---|
| 0x03000000 (ROM 0x7FD6BC, 0xC0C bytes copied with the helpers below) | ARM decompressor `decompress(r0 = dst, r1 = src)`. Uses r0 and r1 only. r2 is unused. r3 and r4 are not initialized: the stream must set them (see literal mode) | CONFIRMED |
| 0x0300024C | Subroutine: read r8 bits into r7, MSB first | CONFIRMED |
| 0x080236A8 | Thumb-to-ARM veneer: `4778 46C0` (bx pc, nop), `E51FF004` (ldr pc,[pc,#-4]), literal `03000000` | CONFIRMED |
| 0x0801F394 | Frame unpack dispatcher `unpack(r0 = header, r1 = dst)`: type 0 -> raw copy (0x08021DF0) of `size` bytes; type 1 or 2 -> decompressor on `header + 8` | CONFIRMED |
| 0x08007772 | Character frame upload. Reads the 12-byte frame record, unpacks to a 0x1000-byte stack buffer, then DMA3 to obj+0x30 (the WRAM staging buffer for Gohan) | CONFIRMED |
| 0x0800775A | Frame record lookup: `rec = animTable[obj.b10] + obj.h14 * 12`, stored in obj+0x3C | CONFIRMED |
| 0x08009364 | Sprite set lookup for set id >= 7: `set = *(0x083B4E90 + (id - 7) * 4)` | CONFIRMED |
| 0x0801F3BA, 0x0300029C | Second dispatcher, used when obj+0x24 (a remap table) is set: type 0 -> byte remap through a 256-byte table, type 1 -> rectangle blit (0x03000480) | CONFIRMED (code), purpose LIKELY |
| 0x03000348, 0x03000480, 0x030002F0 | Linear-bitmap-to-tile copy, rectangle-to-tile copy, copy of nonzero bytes. They are not on the sprite frame path | CONFIRMED (code) |

The decompressor has 14 Thumb call sites (BL to 0x080236A8): 0x08000318, 0x08000424, 0x08000F2C, 0x0800141C, 0x08002BB4, 0x08002BC2, 0x08002D00, 0x08002D0E, 0x08002DA8, 0x08002EB0, 0x08005038, 0x0800B32A, 0x0800B3C2, 0x0801F3AC. The dispatcher 0x0801F394 has 72 call sites, so the codec serves backgrounds and UI too. The search shape was "Thumb BL whose target is the veneer". A call through a register or a different veneer would not appear in this list.

Key disassembly (Ghidra 12.1.4, IWRAM loaded from `iwram.bin`):

```
03000024  subs  r10,r10,#1      ; getbit: r10 = bits left in r6
03000028  ldrmi r6,[r1],#4      ;   empty -> load next 32-bit LE word
0300002c  movmi r10,#0x1f
03000030  adds  r6,r6,r6        ;   carry = top bit
03000034  bcs   0x03000014      ; 1 -> literal: r7 = readbits(r3) + r4; strb
...
030000b8  mov   r4,#0           ; 001 0000 0 b : literal mode
030000cc  adc   r3,r4,#7        ;   r3 = 7 + b
030000d0  cmp   r3,#8
030000dc  bl    0x0300024c      ;   if 7 bits: r4 = readbits(8) (base)
...
030001e4  cmp   r12,#0x10000    ; long match length bonus by offset
030001e8  addcs r9,r9,#3
030001f0  ldr   r8,=0x37FF ... addcs r9,r9,#2
03000200  ldr   r8,=0x027F ... addcs r9,r9,#1
03000210  cmp   r12,#0x7f ; bhi ; add r9,r9,#4
03000224  ldrb  r8,[r0,-r12]    ; byte-wise copy from dst - offset
```

```
0801F398  push {r3,lr}          ; r2 = header, r0 = dst
0801F39A  ldr  r3,[r2,#0]       ; type
0801F39C  add  r1,r2,#0 ; add r1,#8   ; stream = header + 8
0801F3A0  cmp r3,#0 ; beq raw   ; type 0 -> 0x08021DF0(dst, header+8, size)
0801F3A4  cmp r3,#1 ; beq call ; cmp r3,#2 ; bne ret
0801F3AC  bl   0x080236A8       ; decompressor
```

```
080077D8  ldrb r1,[r0,#2] ; ldrb r2,[r0,#3] ; mul r1,r2   ; size = rec.w * rec.h
080077E8  ldr  r0,[r0,#8]                               ; frame header
080077FE  bl   0x0801F394                               ; unpack to sp+4
0800780A  str  r5,[DMA3SAD] ; str r0,[DMA3DAD] = obj+0x30 ; strh size/4 ; strh 0x8400 (32-bit, enable)
```

## Stream format (CONFIRMED by disassembly and by the 11,598-record sweep)

**Frame header:** `u32 type` (0 = raw, 1 or 2 = compressed, 1 seen in all sprite sets), `u32 size` (unpacked bytes), then the stream at +8. The stream is 4-byte aligned.

**Bit reader:** the stream is 32-bit little-endian words. Bits are consumed MSB first. `bits(n)` returns n bits as an integer, MSB first, and can span two words.

**Gamma code:** `v = 1; repeat { v = 2v + bit } while (bit)`. Each step reads one value bit and one continue bit. The smallest value is 2.

**State at entry:** last offset = 1, offset width = 8, literal mode undefined.

| Code | Meaning |
|---|---|
| `1` + bits(litBits) | Literal byte = (value + litBase) & 0xFF |
| `01` + gamma G, G = 2 | gamma L, copy L bytes from the last offset |
| `01` + gamma G, G >= 3 | offset = ((G - 3) << offBits) + bits(offBits). L = gamma, plus 3 if offset >= 0x10000, plus 2 if >= 0x37FF, plus 1 if >= 0x27F, plus 4 if <= 0x7F. Copy L bytes. last offset = offset |
| `000` + bits(7) = O, O != 0 | copy bits(2) + 2 bytes from offset O. last offset = O |
| `000 0000000` + bits(2) = W, W = 0 | end of stream |
| `000 0000000` + bits(2) = W, W != 0 | offBits = bits(W + 3) (new long-match offset width) |
| `001` + bits(4) = 1 | output byte 0 |
| `001` + bits(4) = N, N >= 2 | copy 1 byte from offset N - 1 |
| `001 0000 1` | raw run: 256 bytes of bits(8), then repeat another 256 while the next bit is 1 |
| `001 0000 0` + bit b | literal mode: litBits = 7 + b. litBase = 0 if b = 1, else bits(8) |

Copies are byte-wise, so an overlapping copy (offset < length) repeats a pattern. Because r3 and r4 are not initialized, a stream must set literal mode before its first literal. The decoder raises an error otherwise, and no walked frame raised it. The Gohan frame starts with word 0x20914F48. Its top byte 0x20 is `001 0000 0`.

The tag layout resembles aPLib (gamma-coded long matches, a repeat-offset code, a short 7-bit match, a 4-bit single-byte match). The bit assignments differ, so no aPLib tool decodes it. SPECULATIVE that it derives from aPLib.

**Output:** 8bpp pixels already in OBJ tile order (64 bytes a tile, 1D mapping, rows of w/8 tiles). The game DMAs the buffer to obj+0x30 with no conversion (0x0800780A). CONFIRMED.

## Sprite indexing (step 6)

**Sprite set table** at ROM 0x3B4E90 (address 0x083B4E90, literal at 0x0800959C, loaded by `ldr r1` at 0x08009364). Set id N >= 7 uses entry N - 7. Ids 1-6 come from a run-time table of 28-byte records (`[r1+0x20] + (id-1)*28 + 0xC`, 0x08009350): LIKELY the six party slots. 150 entries walk cleanly. CONFIRMED.

**Set header** (LIKELY for the unknown fields):

```
+0  u16 slot size    (bytes of OBJ VRAM and heap buffer for the object; 0x400 for sets 53-59)
    (byte +1 is the high byte of this u16, not a direction count: set 56 header bytes at 0x299C48 are `00 04 15 10`, so +1 = 0x04 and u16 = 0x0400)
+2  u8  anims
+3  u8  ?            (0x08, 0x10, 0x18, 0x20, 0x30)
+4  u32 ?            (0x8, 0x10, 0x18)
+8  u32 remap ptr    (0, or a 256-byte palette index remap table, e.g. set 52 -> 0x0827B234)
+12 4 dirs x 16 bytes  (four s32 per direction: -2, -24, 18, 10 for Gohan; LIKELY a collision box)
then anims x 4 u32 pointers to frame record lists (0 = unused)
```

**Animation table entry** = `anim * 4 + dir`. The game hardcodes 4 directions (Ruling 35, T5P2). The game indexes it with obj+0x10 (0x0800775A). CONFIRMED for the lookup. LIKELY for the anim/dir split. In the sets seen the 4th direction often reuses the 3rd direction's frames with attr1 bit 12 (H-flip) set (41 of 200 records in set 57). Some animations reuse the frames without the flip (set 57, anim 17).

**Frame record**, 12 bytes (0x08007772):

```
+0 s8  dx    +1 s8 dy   (LIKELY draw offset: 0, -24 for a 16x32 frame)
+2 u8  w     +3 u8 h    (CONFIRMED: size = w*h is the DMA length)
+4 u16 attr0 template   (CONFIRMED: word copied to OAM, then X and Y patched in)
+6 u16 attr1 template   (0x8000 = size 2; 0x9000 adds H-flip)
+8 u32 frame header pointer
```

The record lists of one animation are contiguous. The frame count of an animation is not stored in the set header. `frames_of()` in the script stops at the next direction's list or at the first invalid record. That rule gave zero size mismatches in 11,598 records. The real count must come from animation timing data elsewhere (open question 2).

### Gohan's sets

Identified by eye from the rendered first frame of each animation (`scripts\one-time\2026-10-16-first-probes\gohan_sets.png`, `scripts\one-time\2026-10-16-first-probes\sets_sheet.png`). Set 57 is CONFIRMED: it holds the captured frame. The other Gohan labels are LIKELY.

| Set id | Header (ROM) | Anim table (ROM) | Anims x 4 dirs (fixed) | Records | Look |
|---|---|---|---|---|---|
| 53 | 0x285234 | 0x285280 | 21 x 4 | 288 | Gohan, black hair, purple and red outfit |
| 55 | 0x28FF38 | 0x28FF84 | 21 x 4 | 216 | Gohan, purple and white outfit |
| 56 | 0x299C48 | 0x299C94 | 21 x 4 | 288 | Gohan, battle armor: CONFIRMED by capture-02 probe_obj8 |
| 57 | 0x2A1470 | 0x2A14BC | 18 x 4 | 200 | Gohan, casual green outfit: **the captured frame** (anim 0, dir 0, frame 0, record 0x29A234, header 0x299DE4) |
| 58 | 0x2AB508 | 0x2AB554 | 19 x 4 | 204 | Super Saiyan Gohan |
| 59 | 0x2B69C8 | 0x2B6A14 | 22 x 4 | 276 | Super Saiyan Gohan, second variant |

Set 54 (0x287EFC, 13 x 4) shows a blond character in an orange gi. It is SPECULATIVE that it is Super Saiyan Goku and not Gohan. Sets 60 and 61 look like Goku and Super Saiyan Goku.

Run `webfoot_decompress.py set <rom> 57 <png_dir> scripts\one-time\2026-10-16-first-probes\captures\01-gohan-base\palette.bin` to list every record of a set and write one PNG for each frame.

## Open questions

1. **WRAM 0x020315A0 to VRAM.** The fill is closed: the upload unpacks to a stack buffer in IWRAM (that fits the tile at 0x03006C5C), then DMAs into 0x020315A0 (sprite object above). The copy from the buffer to OBJ VRAM is not traced. Fallback: a read watchpoint on 0x020315A0 in the mGBA debugger (mine).
2. **Frame count and timing** of each animation are not in the set header. Find the animation script that advances obj+0x14.
3. **Which set id is the active party Gohan.** Ids 1-6 resolve through a run-time table. Find where the game fills it for each form and outfit.
4. **Sets with all-null animation tables** (for example ids 10, 32, 37, 66, 74, 105). Some have a sibling with a remap pointer and a filled table (37 -> 38, 39). LIKELY the null sets are filled or replaced at run time.
5. **Unknown header fields:** set +3 and +4, and the four s32 values for each direction.
6. **Reinsertion** needs a compressor. Any stream that follows the table above decodes. The simplest valid encoder writes the literal-mode code `001 0000 1` (8-bit literals), then one `1` + 8 bits per byte, then `000 0000000 00`. New data can go in free ROM space, with the record's +8 pointer moved to it. Not written or tested.

## Files

| File | Purpose |
|---|---|
| `scripts\permanent\rom\webfoot_decompress.py` | Codec, frame unpack, brute-force `find`, set walker with PNG export |
| `scratch\ghidra\LoG2.gpr` (+ `.rep`) | Headless Ghidra project: raw ROM at 0x08000000, IWRAM and EWRAM blocks from the capture |
| `scratch\ghidra\log2.gba` | A copy of the ROM (same SHA-1). The Ghidra batch file cannot handle the parentheses in the original path |
| `archive\2026-10-16-ghidra-first-scripts\SetupGba.java`, `Dis.java`, `Xref.java` | GhidraScripts: add RAM blocks, print a disassembly of the given ranges, list references |
| `scripts\one-time\2026-10-16-first-probes\dis_*.txt` | Raw Ghidra listings quoted above |
| `scripts\one-time\2026-10-16-first-probes\iwram_src.py`, `find_bl.py`, `find_ldr.py` | Find IWRAM code in ROM, Thumb BL callers, PC-relative literal loads |
| `scripts\one-time\2026-10-16-first-probes\brute.py`, `scan.py`, `wf.py` | First prototype codec and parallel scan (superseded by the permanent script) |
| `scripts\one-time\2026-10-16-first-probes\captures\02-gohan-gi\` | Second capture from the coordinator, used for the six extra matches |
| `scripts\one-time\2026-10-16-first-probes\sweep_sets.py` | Walk all 150 sets and check every frame's size |
| `scripts\one-time\2026-10-16-first-probes\sheet.py`, `sheet2.py`, `sets_sheet.png`, `gohan_sets.png` | Contact sheets used to name the sets |
| `scripts\one-time\2026-10-16-first-probes\frame_299DE4.bin`, `probe_linear.bin` | Proof output, and the probe in linear order (not needed: the output is already tiled) |
