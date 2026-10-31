r"""
status_bonus.py - Patch: the status page shows the form bonus as a gold bar segment on a 125-point scale.

Usage:   py -3 -I scripts\permanent\log2_build.py --out builds\log2_poc.gba gohan_gi ssj2_form gohan_portraits status_bonus
Input:   the ROM after patches.ssj2_form (alloc.notes["ssj2_form"]["table"] is the +3 literal in the page pool).
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["status_bonus"].
         gold_image() -> 600 bytes; page_bls(rom, start) -> [(page offset, BL target)].
Method:  1. Copy the status page @0x0800379C (0x3A8 bytes, code and pool) to the expansion area at a 4-aligned
            address, so every `ldr =` and `add rX,pc` still reads the copied pool. Each BL to base code goes to a
            16-byte Thumb stub `push {r7} ; ldr r7,=target ; mov r12,r7 ; pop {r7} ; bx r12` that keeps r0-r7,
            sp and lr. Outside the splice the copy equals the page except the BL offsets.
         2. Splice: the stat rows (page +0x166 to +0x280, @0x08003902-0x08003A1B) become `bl stats`, then the r6
            and r7 values the page reads after them. stats draws label, number and bar per stat: the base part
            from the vanilla image, then a gold part from the base end to the live end, both on the 125 scale.
         3. Live values come from find_player: the player pointer @0x03001FA8, else message 7 to the suspended
            object list @0x03001D18 (the Europe method, EU @0x080159FC). Bonus = live - base, never below 0.
         4. Base ROM: entry stub at 0x0800379C (to the copy), find_player stub at 0x080037AC (dead page code).
            The STR, POW and END item checks `ldr r0,=0x03001fa8 ; ldr r0,[r0]` become `bl 0x080037AC`, so a
            stat item used in the menu reapplies the form (0x080086A2) and live never lags base.
Rules:   Source: docs\research\research-status-screen.md. No palette is written: the gold uses menu palette entries
         58, 69 and 34 (rom:0x1D4F50). Every site is checked against its old bytes before any write.
         Hand-assembled Thumb with the ssj2_form assembler; tests\test_status.py decodes it with thumb_dis
         and runs it. The +3 portrait literal the game reads is now the copy's pool word (notes "plus3_literal").
"""
import hashlib
import struct

from patches.ssj2_form import _encode, assemble

# ===== constants =====
ROM_BASE = 0x08000000
PAGE, PAGE_LEN, CODE_LEN = 0x379C, 0x3A8, 0x362         # code @0x0800379C-0x08003AFD, pool to 0x08003B43
PAGE_SHA1 = "413bf637654b2f44be643c823b22b1cbc59204a9"  # vanilla page bytes (checked in apply)
PLUS3_LITERAL, APPEARANCE = 0x394, 0x081D967C           # page offset of the +3 table literal, vanilla value
VANILLA_FORMAT = 0x388                                  # page offset of "%d/100"
SPLICE = (0x166, 0x280)                                 # stat rows @0x08003902-0x08003A1B
ENTRY_STUB, PLAYER_STUB = 0x379C, 0x37AC                # both inside the dead page code
ITEM_SITES = {0xF4AA: "8b480068002801d0f9f7f6f8",       # STR, POW, END item: ldr r0,=0x03001fa8 ;
              0xF512: "71480068002801d0f9f7c2f8",       # ldr r0,[r0] ; cmp r0,#0 ; beq ;
              0xF57A: "57480068002801d0f9f78ef8"}       # bl 0x80086a2 (reapply form). The first 4 bytes change
CODE_END = 0x08030000                                   # base code ends before this (RSS section 3.2 scans)
QUERY = 0x08006E0A                                      # (list, message, arg): first non-zero answer
STAT_TARGETS = {"FAR_TEXT": 0x0801F636, "FAR_PRINTF": 0x0801F6D8, "FAR_BLIT": 0x08021188, "FAR_QUERY": QUERY}
BAR_X, BAR_W, MAX_PX, POINTS = 0x3E, 75, 75, 5          # 3 px a segment, 5 points a segment: full at 125
GOLD_ROWS = (58, 69, 69, 69, 69, 34, 34, 34)            # pale top, gold body, bronze foot (report: contrast)
BONUS_TEXT = "split"                                    # me, 2026-10-18: "split" = "100+20" (reads as a buff); "live" = "120"
TEXT_MODES = {"split": (b"%d+%d\0", ""), "live": (b"%d\0", "add r2,r2,r3")}

STUB = """
    push {r7}
    ldr r7,=TARGET
    mov r12,r7
    pop {r7}
    bx r12
"""

SPLICE_SRC = """
    ldr r0,[sp,#0xd8]
    ldr r1,[r0,#0x0]        ; shown character
    add r0,sp,#0x9c         ; canvas
    bl STATS
    mov r6,#0x57            ; the page reads r6 = 87 (NEXT y) and r7 = canvas after the stat rows
    add r7,sp,#0x9c
    b CONT
"""

# ===== new code (ARMv4T Thumb). Symbols in caps are filled in at assembly =====
CODE = """
find_player:                ; r0 = player or 0: pointer 0x03001FA8, else message 7 to the suspended list
    push {lr}
    ldr r0,=0x03001fa8
    ldr r0,[r0,#0x0]
    cmp r0,#0x0
    bne find_done
    ldr r0,=0x03001d18
    ldr r0,[r0,#0x0]
    cmp r0,#0x0
    beq find_done           ; no suspended list: the query would read [0 + 4]
    mov r2,#0x0
    mov r1,#0x7
    bl FAR_QUERY
find_done:
    pop {pc}
width:                      ; r0 = stat value -> r0 = bar pixels, min(v, 125) / 5 * 3. Leaf, uses r1
    mov r1,#0x0
width_loop:
    cmp r0,#POINTS
    blt width_done
    sub r0,#POINTS
    add r1,#0x3
    cmp r1,#MAX_PX
    blt width_loop
width_done:
    add r0,r1,#0
    bx lr
stats:                      ; r0 = canvas, r1 = shown character, r4 = record, r5 = vanilla bar image. Keeps r4-r7
    push {r4,r5,r6,r7,lr}
    sub sp,#0x18            ; sp+0 blit rect {x0, y0, x1, y1}, sp+0x10 base STR POW END, sp+0x14 live
    add r7,r0,#0            ; r7 = canvas: +4 text x, +8 text y
    add r6,sp,#0x10
    ldrh r0,[r4,#0xa]
    lsr r0,r0,#8
    strb r0,[r6,#0x0]
    strb r0,[r6,#0x4]
    ldrh r0,[r4,#0xc]
    lsr r0,r0,#8
    strb r0,[r6,#0x1]
    strb r0,[r6,#0x5]
    ldrh r0,[r4,#0xe]
    lsr r0,r0,#8
    strb r0,[r6,#0x2]
    strb r0,[r6,#0x6]
    ldr r0,=0x081d94d0
    ldr r0,[r0,#0x0]
    ldrb r0,[r0,#0x0]
    cmp r0,r1
    bne stats_rows          ; not the leader: live = base, as vanilla
    bl find_player
    cmp r0,#0x0
    beq stats_rows
    add r0,#0xff
    add r0,#0x61            ; player +0x160: live STR, POW, END
    ldrb r1,[r0,#0x0]
    strb r1,[r6,#0x4]
    ldrb r1,[r0,#0x1]
    strb r1,[r6,#0x5]
    ldrb r1,[r0,#0x2]
    strb r1,[r6,#0x6]
stats_rows:
    mov r4,#0x0             ; r4 = row: 0 STR, 1 POW, 2 END
stats_row:
    mov r0,#0x3b
    str r0,[r7,#0x4]
    lsl r0,r4,#4
    add r0,#0x2f
    str r0,[r7,#0x8]        ; label at (59, 47 + 16 row)
    lsl r1,r4,#2
    ldr r0,=0x080e2840
    add r0,r0,r1
    ldr r1,[r0,#0x70]
    add r0,r7,#0
    bl FAR_TEXT
    mov r0,#0x88
    str r0,[r7,#0x4]
    ldr r0,[r7,#0x8]
    add r0,#0x8
    str r0,[r7,#0x8]        ; number at (136, 55 + 16 row), right-aligned
    ldrb r2,[r6,r4]         ; base
    add r1,r4,#0x4
    ldrb r3,[r6,r1]         ; live
    ldr r1,=FMT_VANILLA
    cmp r3,r2
    ble stats_print         ; no bonus: vanilla "%d/100"
    sub r3,r3,r2            ; r3 = bonus
    TEXT_ARGS
    ldr r1,=FMT_BONUS
stats_print:
    add r0,r7,#0
    bl FAR_PRINTF
    ldrb r0,[r6,r4]
    bl width
    add r0,#BAR_X
    str r0,[sp,#0x8]        ; base end
    mov r0,#BAR_X
    str r0,[sp,#0x0]
    lsl r0,r4,#4
    add r0,#0x28
    str r0,[sp,#0x4]        ; y 40 + 16 row
    add r0,#0x8
    str r0,[sp,#0xc]
    mov r3,#BAR_W
    add r2,sp,#0x0
    add r1,r5,#0
    add r0,r7,#0
    bl FAR_BLIT             ; base part: vanilla image columns 0 to base px
    add r0,r4,#0x4
    ldrb r0,[r6,r0]
    bl width
    add r0,#BAR_X           ; live end
    ldr r1,[sp,#0x8]
    cmp r0,r1
    ble stats_next          ; no bonus pixels
    str r1,[sp,#0x0]
    str r0,[sp,#0x8]
    ldr r0,=GOLD_X0
    add r1,r1,r0            ; gold image + base px: the segment pattern stays in phase
    mov r3,#BAR_W
    add r2,sp,#0x0
    add r0,r7,#0
    bl FAR_BLIT             ; gold part: base end to live end
stats_next:
    add r4,#0x1
    cmp r4,#0x3
    blt stats_row
    add sp,#0x18
    pop {r4,r5,r6,r7,pc}
"""


# ===== helpers =====

def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _word(v: int) -> bytes:
    return struct.pack("<I", v & 0xFFFFFFFF)


def gold_image() -> bytes:
    """75x8, row order: two colored columns then one index 0 column (transparent), as the vanilla bar."""
    return bytes(0 if x % 3 == 2 else GOLD_ROWS[y] for y in range(8) for x in range(BAR_W))


def page_bls(rom: bytes, start: int) -> list:
    """[(page offset, GBA target)] of every BL in the page code at file offset start."""
    out, off = [], 0
    while off < CODE_LEN:
        hi = struct.unpack_from("<H", rom, start + off)[0]
        if hi >> 11 != 0x1E:
            off += 2
            continue
        lo = struct.unpack_from("<H", rom, start + off + 2)[0]
        if lo >> 11 != 0x1F:
            raise ValueError(f"rom:0x{start + off:X} BL prefix without its second half")
        disp = ((hi & 0x7FF) << 12 | (lo & 0x7FF) << 1) - ((hi & 0x400) << 13)
        out.append((off, ROM_BASE + start + off + 4 + disp))
        off += 4
    return out


def _bl(at: int, target: int) -> bytes:
    return _encode(at + ROM_BASE, "bl", ["T"], {}, {"T": target}, [], 0)


def _stub(at: int, target: int) -> bytes:
    blob = assemble(STUB, at + ROM_BASE, {"TARGET": target | 1})[0]
    if len(blob) != 16:
        raise ValueError(f"stub at rom:0x{at:X} is 0x{len(blob):X} bytes, expected 0x10")
    return blob


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    if "ssj2_form" not in alloc.notes:
        raise ValueError("status_bonus needs the ssj2_form notes: run ssj2_form first")
    table = alloc.notes["ssj2_form"]["table"] + ROM_BASE
    _expect(rom, PAGE + PLUS3_LITERAL, _word(table))
    vanilla = bytearray(rom[PAGE:PAGE + PAGE_LEN])
    vanilla[PLUS3_LITERAL:PLUS3_LITERAL + 4] = _word(APPEARANCE)
    if hashlib.sha1(vanilla).hexdigest() != PAGE_SHA1:
        raise ValueError(f"status page rom:0x{PAGE:X} is not the vanilla page")
    for off, old in ITEM_SITES.items():
        _expect(rom, off, bytes.fromhex(old))
    bls = page_bls(rom, PAGE)
    targets = sorted({t for _, t in bls} | {QUERY})
    for t in targets:
        if not ROM_BASE <= t < CODE_END or PAGE <= t - ROM_BASE < PAGE + PAGE_LEN:
            raise ValueError(f"page BL target {t:#x} is not base code outside the page")
    fmt, text_args = TEXT_MODES[BONUS_TEXT]

    # 1. allocate everything; nothing is written until the code size is checked
    page = alloc.alloc(PAGE_LEN)
    stubs = {t: alloc.alloc(16) for t in targets}
    text = alloc.alloc(len(fmt))
    gold = alloc.alloc(BAR_W * 8)
    syms = {"FMT_VANILLA": page + VANILLA_FORMAT + ROM_BASE, "FMT_BONUS": text + ROM_BASE,
            "GOLD_X0": gold + ROM_BASE - BAR_X, "POINTS": POINTS, "MAX_PX": MAX_PX, "BAR_X": BAR_X,
            "BAR_W": BAR_W, **{k: stubs[t] + ROM_BASE for k, t in STAT_TARGETS.items()}}
    src = CODE.replace("TEXT_ARGS", text_args)
    size = len(assemble(src, page + ROM_BASE, syms)[0])  # any expansion address: far BLs stay in range
    code = alloc.alloc(size)
    blob, labels = assemble(src, code + ROM_BASE, syms)
    if len(blob) != size:                    # a size change would shift every later ROM byte
        raise ValueError(f"code assembled to 0x{len(blob):X} bytes, allocated 0x{size:X}")
    if page % 4:
        raise ValueError("the page copy must keep the 4-byte alignment of its pool")

    # 2. relocated page: copy, BLs to stubs, splice the stat rows
    copy = bytearray(rom[PAGE:PAGE + PAGE_LEN])
    for off, target in bls:
        copy[off:off + 4] = _bl(page + off, stubs[target] + ROM_BASE)
    start, end = SPLICE
    splice = assemble(SPLICE_SRC, page + start + ROM_BASE,
                      {"STATS": labels["stats"], "CONT": page + end + ROM_BASE})[0]
    if len(splice) > end - start:
        raise ValueError("splice does not fit the stat rows")
    copy[start:end] = splice + bytes(end - start - len(splice))

    # 3. write
    rom[page:page + PAGE_LEN] = copy
    for t, at in stubs.items():
        rom[at:at + 16] = _stub(at, t)
    rom[text:text + len(fmt)] = fmt
    rom[gold:gold + BAR_W * 8] = gold_image()
    rom[code:code + size] = blob
    rom[ENTRY_STUB:ENTRY_STUB + 16] = _stub(ENTRY_STUB, page + ROM_BASE)
    rom[PLAYER_STUB:PLAYER_STUB + 16] = _stub(PLAYER_STUB, labels["find_player"])
    for off in ITEM_SITES:
        rom[off:off + 4] = _bl(off, PLAYER_STUB + ROM_BASE)

    alloc.notes["status_bonus"] = {"page": page, "stubs": {t: at for t, at in stubs.items()}, "text": text,
                                   "gold": gold, "code": code, "plus3_literal": page + PLUS3_LITERAL,
                                   **{k: v - ROM_BASE for k, v in labels.items()
                                      if k in ("find_player", "width", "stats")}}
