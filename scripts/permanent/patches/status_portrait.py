r"""
status_portrait.py - Patch: the status page shows the dialog portrait in the dialog colors (final, 2026-10-19).

Usage:   py -3 -I scripts\permanent\log2_build.py --out archive\builds\log2_poc_r20.gba gohan_gi ssj2_form
         gohan_portraits status_bonus ssj2_idle cutscene_portraits npc_gi rage_text portrait_remaster
         status_portrait rage_stats     (in the build from r20, appended so earlier allocations stay put)
Input:   the ROM after patches.status_bonus (alloc.notes["status_bonus"]: the page copy and its long-call stubs).
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["status_portrait"].
Method:  1. The page reads appearance +2 (the dialog portrait, OBJ palette indices) instead of +3 (the status twin):
            page copy +0x2F0 `ldrb r0,[r0,#0x3]` becomes `#0x2`. portrait() and the cutscene_portraits hook then
            give the status page the same id the dialog box shows.
         2. The canvas copy to BG VRAM (page copy +0x338, `bl` to the 0x080236B4 stub) becomes `bl paint`. paint:
            remaps the 64x64 portrait buffer ([canvas - 0x14]) in place: each OBJ index gets the next free slot of
            POOL (first come, first served; index 0 stays transparent); blits it again over the vanilla blit with
            the page's own rect (0x081D94E4, through the 0x080211C8 stub); copies the canvas to VRAM; then writes
            each used OBJ color (rom:0x1DA6C8) to its slot in BG palette RAM (0x05000000 + 2 slot). The palette
            write comes after the VRAM copy, so the old picture never shows in the new colors.
         3. POOL: 64 menu palette indices that nothing in the character menu context draws (census
            scripts\one-time\2026-10-19-status-portrait\s3_slots.py: every frame and constant color reachable from vt_char_menu and
            the sub-menus it opens, item and ability art, tab icons, widgets). Any portrait with up to 64 colors
            shows pixel-exact; every USA dialog portrait has 64 or fewer. Above 64, new colors reuse the last slot
            and are not loaded (a wrong color, never a corrupted slot); apply() refuses a reachable portrait that
            would overflow.
Rules:   Source: docs\tasks\2026-10-19-status-portrait\status-same-report.md. No ROM palette and no portrait frame is written; the
         status twins (ids 8-25, 116, 118, 120) stay in the ROM, unused by this page. Every site is checked
         against its old bytes first. Hand-assembled Thumb with the ssj2_form assembler; tests\test_status_portrait.py
         decodes it with thumb_dis and runs it.
"""
import struct

from patches.ssj2_form import _encode, assemble
from rom.webfoot_decompress import unpack_frame

# ===== constants =====
ROM_BASE = 0x08000000
PLUS_BYTE = 0x2F0                     # page copy offset of `ldrb r0,[r0,#0x3]` (vanilla 0x08003A8C)
BLIT_SITE, COPY_SITE = 0x304, 0x338   # page copy offsets of the portrait blit and the canvas copy BLs
BLIT_ARGS = bytes.fromhex("194a27a822991432")   # ldr r2,=0x081d94d0 ; add r0,sp,#0x9c ; ldr r1,[sp,#0x88] ; add r2,#0x14
COPY_ARGS = bytes.fromhex("1a4927a8")           # ldr r1,=0x06006940 ; add r0,sp,#0x9c
BLIT, COPY, UNPACK = 0x080211C8, 0x080236B4, 0x0801F394
RECT = 0x081D94E4                     # portrait rect {144, 4, 208, 68}: 0x081D94D0 + 0x14, as the page passes it
OBJ_PAL, BG_PRAM = 0x081DA6C8, 0x05000000
BLOCK_LITERAL, APPEARANCE_ENTRY = 0xBE10, 20
# Census s3_slots.txt (78 free); the first 64. Not 0 (transparent, and 0 marks "no slot" in the map).
POOL = (7, 19, 20, 21, 23, 24, 26, 27, 28, 30, 31, 35, 36, 48, 54, 55, 56, 59, 60, 61, 62, 63, 64, 65, 67, 70,
        75, 76, 77, 79, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 105, 109, 110, 111, 113, 114, 115, 116, 118,
        120, 123, 125, 129, 131, 132, 148, 155, 158, 162, 164, 172, 181, 182)

# ===== new code (ARMv4T Thumb). Symbols in caps are filled in at assembly =====
CODE = """
paint:                      ; r0 = main canvas (page sp+0x9C), r1 = BG VRAM. Replaces the page's canvas copy
    push {r4,r5,r6,r7,lr}
    sub sp,#0x108           ; sp+0 map: slot per OBJ index (0 = none); sp+0x100 canvas; sp+0x104 VRAM
    str r0,[sp,#0x100]
    str r1,[sp,#0x104]
    add r4,r0,#0
    sub r4,#0x14
    ldr r4,[r4,#0x0]        ; portrait pixels: the 64x64 canvas (page sp+0x64) +0x24 = page sp+0x88
    add r5,sp,#0x0
    mov r0,#0x0
    mov r1,#0xfc
paint_zero:
    str r0,[r5,r1]
    sub r1,#0x4
    bge paint_zero
    mov r6,#0x0             ; next POOL position
    mov r7,#0x0             ; pixel
paint_px:
    ldrb r0,[r4,r7]
    cmp r0,#0x0
    beq paint_next          ; index 0 stays transparent
    ldrb r1,[r5,r0]
    cmp r1,#0x0
    bne paint_set
    ldr r2,=POOL_AT
    cmp r6,#POOL_N
    blt paint_new
    mov r3,#POOL_LAST       ; pool full: reuse the last slot, load no color (never for a checked portrait)
    ldrb r1,[r2,r3]
    b paint_set
paint_new:
    ldrb r1,[r2,r6]
    add r6,#0x1
    strb r1,[r5,r0]
paint_set:
    strb r1,[r4,r7]
paint_next:
    add r7,#0x1
    mov r0,#0x80
    lsl r0,r0,#5
    cmp r7,r0
    blt paint_px
    ldr r0,[sp,#0x100]
    add r1,r4,#0
    ldr r2,=RECT
    bl FAR_BLIT             ; the remapped portrait over the vanilla blit, same rect
    ldr r0,[sp,#0x100]
    ldr r1,[sp,#0x104]
    bl FAR_COPY             ; the page's canvas copy
    mov r7,#0xff
paint_pal:
    ldrb r1,[r5,r7]
    cmp r1,#0x0
    beq paint_pal_next
    lsl r0,r7,#1
    ldr r2,=OBJ_PAL
    add r2,r2,r0
    ldrh r0,[r2,#0x0]       ; dialog color: OBJ palette entry
    lsl r1,r1,#1
    ldr r2,=BG_PRAM
    add r1,r1,r2
    strh r0,[r1,#0x0]       ; BG palette RAM, halfword (palette RAM ignores byte writes)
paint_pal_next:
    sub r7,#0x1
    bne paint_pal
    add sp,#0x108
    pop {r4,r5,r6,r7,pc}
"""


# ===== helpers =====

def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _bl(at: int, target: int) -> bytes:
    return _encode(at + ROM_BASE, "bl", ["T"], {}, {"T": target}, [], 0)


def _u32(rom, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def dialog_ids(rom, table: int) -> list:
    """Appearance +2 of every entry of the relocated table (23 entries: 22 vanilla and ssj2_form's entry 22)."""
    return [rom[table + APPEARANCE_ENTRY * e + 2] for e in range(23)]


def colors_of(rom, pid: int) -> int:
    """Distinct indices of portrait pid, read through the live portrait block (rom:0xBE10)."""
    block = _u32(rom, BLOCK_LITERAL) - ROM_BASE
    return len(set(unpack_frame(rom, _u32(rom, block + 4 + 4 * pid) - ROM_BASE)[2]))


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    if "status_bonus" not in alloc.notes or "ssj2_form" not in alloc.notes:
        raise ValueError("status_portrait needs the status_bonus and ssj2_form notes: run them first")
    page, stubs = alloc.notes["status_bonus"]["page"], alloc.notes["status_bonus"]["stubs"]
    table = alloc.notes["ssj2_form"]["table"]
    _expect(rom, page + PLUS_BYTE, bytes.fromhex("c078"))
    _expect(rom, page + BLIT_SITE - len(BLIT_ARGS), BLIT_ARGS)
    _expect(rom, page + BLIT_SITE, _bl(page + BLIT_SITE, stubs[BLIT] + ROM_BASE))
    _expect(rom, page + COPY_SITE - len(COPY_ARGS), COPY_ARGS)
    _expect(rom, page + COPY_SITE, _bl(page + COPY_SITE, stubs[COPY] + ROM_BASE))
    _expect(rom, page + COPY_SITE + 4, bytes.fromhex("0bac"))              # add r4,sp,#0x2c: the page goes on
    if len(set(POOL)) != len(POOL) or 0 in POOL:
        raise ValueError("POOL must be distinct non-zero indices")
    for pid in set(dialog_ids(rom, table)):
        if colors_of(rom, pid) > len(POOL):
            raise ValueError(f"dialog portrait {pid} has more colors than the {len(POOL)} pool slots")

    pool = alloc.alloc(len(POOL))
    syms = {"POOL_AT": pool + ROM_BASE, "POOL_N": len(POOL), "POOL_LAST": len(POOL) - 1, "RECT": RECT,
            "OBJ_PAL": OBJ_PAL, "BG_PRAM": BG_PRAM, "FAR_BLIT": stubs[BLIT] + ROM_BASE,
            "FAR_COPY": stubs[COPY] + ROM_BASE}
    size = len(assemble(CODE, pool + ROM_BASE, syms)[0])  # any expansion address: the BLs stay in range
    code = alloc.alloc(size)
    blob, labels = assemble(CODE, code + ROM_BASE, syms)
    if len(blob) != size:
        raise ValueError(f"code assembled to 0x{len(blob):X} bytes, allocated 0x{size:X}")

    rom[pool:pool + len(POOL)] = bytes(POOL)
    rom[code:code + size] = blob
    rom[page + PLUS_BYTE:page + PLUS_BYTE + 2] = bytes.fromhex("8078")    # ldrb r0,[r0,#0x2]
    rom[page + COPY_SITE:page + COPY_SITE + 4] = _bl(page + COPY_SITE, labels["paint"])
    alloc.notes["status_portrait"] = {"pool": pool, "code": code, "paint": labels["paint"] - ROM_BASE,
                                      "plus_byte": page + PLUS_BYTE, "copy_site": page + COPY_SITE}
