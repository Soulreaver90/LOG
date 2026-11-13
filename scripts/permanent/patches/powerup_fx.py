r"""
powerup_fx.py - Patch: the power-up plays the Buu's Fury aura and the Buu's Fury ground dust.

Usage:   py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_vegeta_fx.txt
         --out builds\mockups\2026-11-12-powerup-fx\log2_vegeta_fx_v1.gba
Input:   the ROM after bf_ki_pool (it owns the state 35 tick) and after at least one of vegeta_zplus
         (set 140) or piccolo_powerup_art (set 104), whose drawn frames the dust goes into.
         Art: art\transformations\_buus-fury-reference\aura\frames\0*.png and ..\dust\0*.png, and the
         owner's own power-up PNGs, all read and never written.
API:     apply(rom, alloc) -> None; addresses, labels and the hook word in alloc.notes["powerup_fx"].
Method:  1. AURA. It is an effect record (bible B1768, B2403), not a sprite set, so it is a spawned
            object. The generic effect class answers everything: ctor @0x080135E0(0, &pos, records,
            count, step, vram_bytes, layer) mallocs 0x44, allocates OBJ VRAM and fills the object;
            vtable 0x080245C0 ticks it (@0x08013656: step the record list, then remove itself from
            the world when the count runs out), culls it, writes its OAM and DMAs its pixels. The
            caller @0x08013828 is copied for the argument shape and for world_add @0x080068B8.
         2. WHEN. State 35's tick runs every frame of the transformation and gets the actor in r1.
            The actor counts its own frames at +0x12 (powerup_tick @0x08011D4A), which holds frames
            1 and 2 for 16 ticks each and then alternates frames 3 and 4 every 32 ticks to 0xA0.
            So +0x12 == 0x20 is exactly where the 3/4 loop starts, which is where the owner put the
            aura on the mockups. One spawn, 8 records at 16 ticks each = the 128 ticks that are left,
            so the object removes itself as the form lands.
         3. WHOSE. The spawn is gated on the actor's own set pointer (+0x48): set 140 takes the gold
            aura, set 104 the white one, and every other power-up in the game is untouched.
         4. ABOVE HIM. Draw order is the world sort @0x08027E74: byte +0x8 first (both the actors and
            this class carry 0x28, which is OBJ priority 2), then word +0x4, and the aura's +0x4 is
            set to the actor's +0x4 plus 1 after the ctor. Drawn behind, the pale inner ring reads as
            a halo, which the owner rejected (bible B2408).
         5. ANCHOR. The effect class puts its frame at (pos - dx, pos - dy) and the actor draw puts
            his at (anchor + dx, anchor + dy), measured in a save state. The two signs are opposite,
            so the aura carries (8, 24), which is the anim 9 pair (-8, -24) negated, and NOT the
            Buu's Fury pair (16, 31). The two 32x32 boxes then coincide, which is what the approved
            mockup composites.
         6. COLOUR. Three of the four Buu's Fury gold colours are absent from the LoG II OBJ palette
            (bible B2407). Taking them would repaint three shared indices, so the gold is drawn on
            the four nearest entries the palette already holds and no palette entry is taken. The
            white recolour the owner picked for Piccolo needs no substitution at all.
         7. DUST. Buu's Fury draws it into its own frames and it replaces the shadow, so it is pixels
            and needs no object. The four drawn frames of each character are rewritten in place
            through the frame headers in the earlier module's notes: frame 1 keeps the still ground,
            frames 2, 3 and 4 take dust shapes 1, 2 and 3, which is cell for cell what the owner
            approved on aura_dust_sheet.py's sheet. Every frame is read back and checked against his
            own PNG before it is rewritten, so this cannot land on art it does not recognise.
         8. INTERRUPTED. A hit mid transform leaves state 35, and the aura must go with it. Buu's Fury
            does exactly this at BF 0x0801C552, the +0xC slot of its transform vtable 0x0804DCA4: it
            zeroes the bar it was ramping and then removes the aura object at state +0xC from the
            world. LoG II's state vtables carry the leave in the same slot, +0xC (bible B1842), and
            the state switch @0x0800763C calls it with r0 = the old state and r1 = the actor. So the
            spawn keeps the object at RAM 0x03003A1C and the leave takes it back with the same
            world_remove call the effect's own tick makes at @0x08013672. Three gates stand between
            that word and the call: a stamp, because this IWRAM is not cleared at power-on (bible
            B1632); the object's own vtable word; and its records-left count, which is 0 only when it
            has already removed itself on the landing frame. The word is cleared on EVERY leave, so a
            pointer can never outlive the transformation that spawned it.
Rules:   Every site is checked against its live bytes before the first write, and the state 35 tick
         word must still hold bf_ki_pool's own tick_xform, so this module cannot run out of order or
         twice. No module file or build list of the two masters is edited, so both master SHA-1s are
         unchanged. Hand-assembled Thumb with the ssj2_form assembler; tests\test_powerup_fx.py
         decodes and runs it.
"""
import struct

from PIL import Image

from art.to_indexed import flat_palette, frame_indices, index_of
import log_paths
from patches.ssj2_form import assemble
from patches.vegeta_zplus import PISKEL_KEY, namers, set_at
from rom.log2_sprites import image_to_tiles
from rom.webfoot_decompress import ROM_BASE

# ===== constants: the effect class, read in the base ROM 2026-11-12 =====
M32 = 0xFFFFFFFF
EFFECT_CTOR, WORLD_ADD = 0x080135E1, 0x080068B9      # @0x080135E0(0, &pos, records, count, ...), @0x080068B8
EFFECT_VTABLE = 0x080245C0                            # tick @0x08013656, OAM @0x080136F2, DMA @0x08013750
WORLD_PTR = 0x086DB354                                # [+4] is the world @0x03001120, as the vanilla caller reads it
WORLD_REMOVE, WORLD_LIST = 0x080068CB, 0x086DB34C     # the pair the effect tick uses on itself @0x08013672
XFORM_VTABLE, XFORM_SLOT = 0x08025D9C, 0x04           # state 35 (transform): bf_ki_pool's tick_xform
LEAVE_SLOT, VANILLA_LEAVE = 0x0C, 0x080155F7          # state vtable +0xC is the leave (bible B1842)
AURA_RAM, AURA_RAM_LEN = 0x03003A1C, 8                # +0 the spawned aura, +4 the stamp; past ki_ramp's block
AURA_LIVE = 0x5A03                                    # a magic stamp: this IWRAM is not cleared at power-on
SPAWN_AT = 0x20                                       # actor +0x12: the tick that starts the 3/4 loop
STEP, FRAMES, VRAM_BYTES, LAYER = 0x1000, 8, 0x400, 0x28   # 16 ticks a record, 8 records, 32x32 8bpp, actor layer
ORDER = (0, 1, 2, 0, 1, 2, 0, 1)                      # the three aura frames, cycled over the 128 ticks left
AURA_DX, AURA_DY, AURA_W, AURA_H = 8, 24, 32, 32      # the negated anim 9 record offsets (bible B2395)
ATTR0, ATTR1 = 0x2000, 0x8000                         # 256 colour, square, size 2 (32x32)
NO_SET = 0xFFFFFFFF                                   # a set pointer nothing equals: that colour is not in the build

REF = log_paths.BF_REFERENCE
AURA_PNGS = {"gold": tuple(log_paths.BF_AURA_FRAMES / f"{k:02d}_bf_aura.png" for k in (1, 2, 3)),
             "white": tuple(log_paths.BF_AURA_FRAMES / f"{k:02d}_bf_aura_white.png" for k in (1, 2, 3))}
# The gold aura drawn on entries the LoG II OBJ palette already holds, so no shared index is repainted.
# Chosen by nearest colour over the whole palette; the ramp keeps its order dark to light.
GOLD_SWAP = {(0xF8, 0xD0, 0x00): (0xF8, 0xD0, 0x40),      # index 37
             (0xF8, 0xF8, 0x00): (0xF8, 0xF8, 0x00),      # index 8, the one exact match
             (0xF8, 0xF8, 0x90): (0xF8, 0xF8, 0x78),      # index 45
             (0xF8, 0xF8, 0xD8): (0xF8, 0xF8, 0xF0)}      # index 43
WHITE_SWAP = {}                                           # the owner's white recolour is already on palette

DUST_PNGS = tuple(log_paths.BF_DUST_FRAMES / f"{k:02d}_dust.png" for k in (1, 2, 3))   # frames 2, 3 and 4 take these
DUST_RGB, SHADOW_RGB = (0xD8, 0xA8, 0x60), (0x00, 0x00, 0x00)   # his own tan; the dust may take his shadow only
FRAME_PX = AURA_W * AURA_H                                 # 1024 bytes of 8bpp pixels a frame
RAW_HEADER_LEN = 8                                         # raw type 0 frame: {u32 0, u32 len, data}

# Who gets which aura: (the module whose notes hold the frames, its set, the colour, the notes key of the headers).
JOBS = (("vegeta_zplus", 140, "gold", "anim_frames"),
        ("piccolo_powerup_art", 104, "white", None))
KITS = {"vegeta_zplus": None, "piccolo_powerup_art": None}   # filled from the modules' own PNG tuples

# ===== new code (ARMv4T Thumb). Symbols in caps are filled in at assembly =====
CODE = """
fx_tick:                    ; r0 = state 35 object, r1 = the actor powering up
    push {r4,r5,r6,r7,lr}
    sub sp,#0x14            ; sp+0..8 the ctor's three stack arguments, sp+0xC the position
    add r4,r1,#0
    ldr r3,=XFORM_TICK
    bl via_r3               ; bf_ki_pool's own tick first: it keeps r0 and r1
    ldrh r0,[r4,#0x12]
    cmp r0,#SPAWN_AT
    bne fx_done             ; one spawn, on the tick the 3/4 loop starts
    ldr r5,[r4,#0x48]       ; the actor's set header (bible row 105)
    ldr r0,=SET_GOLD
    cmp r5,r0
    beq fx_gold
    ldr r0,=SET_WHITE
    cmp r5,r0
    bne fx_done             ; every other power-up in the game keeps its vanilla look
    ldr r6,=LIST_WHITE
    b fx_spawn
fx_gold:
    ldr r6,=LIST_GOLD
fx_spawn:
    add r0,r4,#0
    add r0,#0xff
    add r0,#0x59            ; actor +0x158: his spot, both words 8.8 fixed point
    ldr r1,[r0,#0x0]
    asr r1,r1,#8
    str r1,[sp,#0xc]
    ldr r1,[r0,#0x4]
    asr r1,r1,#8
    str r1,[sp,#0x10]
    ldr r0,=STEP
    str r0,[sp,#0x0]        ; +0x38: 16.16 added a frame, so one record every 16 ticks
    ldr r0,=VRAM_BYTES
    str r0,[sp,#0x4]        ; the OBJ VRAM the ctor allocates, and obj +0xE
    mov r0,#LAYER
    str r0,[sp,#0x8]        ; obj +0x8: the sort key the actors carry, OBJ priority 2
    mov r0,#0x0
    add r1,sp,#0xc
    add r2,r6,#0
    mov r3,#FRAMES
    ldr r7,=EFFECT_CTOR
    bl via_r7
    cmp r0,#0x0
    beq fx_done             ; the heap is full: no aura, and no crash. The ctor does NOT check the
                            ; OBJ VRAM allocation, so a full VRAM is still its own risk
    ldr r1,[r4,#0x4]
    add r1,#0x1
    str r1,[r0,#0x4]        ; one past the actor's own sort word, so the aura draws ABOVE him
    ldr r2,=AURA_RAM
    str r0,[r2,#0x0]        ; the aura, for the leave that must take it back on an interruption
    ldr r3,=AURA_LIVE
    str r3,[r2,#0x4]
    add r1,r0,#0
    ldr r0,=WORLD_PTR
    ldr r0,[r0,#0x4]
    ldr r7,=WORLD_ADD
    bl via_r7
fx_done:
    add sp,#0x14
    pop {r4,r5,r6,r7,pc}

; ===== 2. the leave, state 35 +0xC (r0 = the state, r1 = the actor): an interrupted transform
;          takes its aura with it, which is what BF 0x0801C552 does in the same slot
fx_leave:
    push {r0,r1,r4,r5,lr}
    ldr r4,=AURA_RAM
    ldr r5,=AURA_LIVE
    ldr r0,[r4,#0x4]
    cmp r0,r5
    bne fx_skip             ; no aura of ours is out, or this IWRAM was never written
    mov r0,#0x0
    str r0,[r4,#0x4]
    ldr r5,[r4,#0x0]
    str r0,[r4,#0x0]        ; cleared on EVERY leave, so a pointer never outlives its transformation
    cmp r5,#0x0
    beq fx_skip
    ldr r0,[r5,#0x0]
    ldr r4,=EFFECT_VTABLE
    cmp r0,r4
    bne fx_skip             ; the block is no longer an effect object
    ldr r0,[r5,#0x34]
    cmp r0,#0x0
    beq fx_skip             ; its records ran out: it removed itself on the landing frame
    add r1,r5,#0
    ldr r0,=WORLD_LIST
    ldr r0,[r0,#0x0]
    ldr r3,=WORLD_REMOVE
    bl via_r3               ; the call the effect's own tick makes on itself
fx_skip:
    pop {r0,r1,r4,r5}
    pop {r3}
    mov lr,r3
    ldr r3,=OLD_LEAVE
    bx r3                   ; the vanilla leave, with r0 and r1 as the state machine passed them
via_r3:
    bx r3
via_r7:
    bx r7
"""


# ===== helpers =====

def _word(v: int) -> bytes:
    return struct.pack("<I", v & 0xFFFFFFFF)


def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def vtable_target(rom: bytes, vtable: int, slot: int) -> int:
    """A vtable word is an offset from the vtable START, never from the slot (bible B0541)."""
    return (vtable + _u32(rom, vtable - ROM_BASE + slot)) & M32


def _rgba(path):
    return Image.open(path).convert("RGBA")


def aura_indices(rom: bytes, path, swap: dict) -> bytes:
    """One aura frame as ROM tile bytes, every colour checked against THIS ROM's own OBJ palette.

    `swap` names the colour we draw instead of a Buu's Fury colour the palette does not hold. A
    colour that survives the swap and is still absent stops the build and is named, because a
    silent nearest match is a colour change nobody saw.
    """
    want = index_of(rom)
    img = _rgba(path)
    px = []
    for c in img.getdata():
        if c[3] == 0:
            px.append(0)
            continue
        if c[3] != 0xFF:
            raise ValueError(f"{path.name}: a part transparent pixel; the ROM has no alpha")
        rgb = swap.get(c[:3], c[:3])
        if rgb not in want:
            raise ValueError(f"{path.name}: colour #{c[0]:02X}{c[1]:02X}{c[2]:02X} "
                             f"(drawn as #{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}) is not in this ROM's OBJ palette")
        px.append(want[rgb])
    if img.size != (AURA_W, AURA_H):
        raise ValueError(f"{path.name} is {img.size}, and the record is {AURA_W}x{AURA_H}")
    out = Image.new("P", img.size)
    out.putdata(px)
    out.putpalette(flat_palette(rom))
    return image_to_tiles(out)


def dusted_frame(rom: bytes, his_png, dust_png) -> tuple:
    """(his frame as ROM tile bytes, the same frame with the dust) for one power-up frame.

    The dust lands on clear canvas or on his own black shadow and never on him, which is the rule
    aura_dust_sheet.add_dust used for the sheet the owner approved. `dust_png` None keeps frame 1
    still, as Buu's Fury does.
    """
    want, pal = index_of(rom), flat_palette(rom)
    (w, h), plain = frame_indices(his_png, want, pal, PISKEL_KEY)
    px = list(plain)
    if dust_png is not None:
        if DUST_RGB not in want:
            raise ValueError(f"the dust colour #{DUST_RGB[0]:02X}{DUST_RGB[1]:02X}{DUST_RGB[2]:02X} "
                             f"is not in this ROM's OBJ palette")
        tan, shadow = want[DUST_RGB], want.get(SHADOW_RGB)
        dust = _rgba(dust_png)
        if dust.size != (w, h):
            raise ValueError(f"{dust_png.name} is {dust.size}, and his frame is {(w, h)}")
        for i, c in enumerate(dust.getdata()):
            if c[3] and (px[i] == 0 or px[i] == shadow):
                px[i] = tan
    return _tiles(plain, (w, h), pal), _tiles(px, (w, h), pal)


def _tiles(px, size, pal) -> bytes:
    img = Image.new("P", size)
    img.putdata(list(px))
    img.putpalette(pal)
    return image_to_tiles(img)


def plan_dust(rom: bytes, headers: list, pngs) -> list:
    """[(file offset of the pixels, his bytes, the dusted bytes)] for one character's four frames.

    Raises unless every frame in the ROM is byte for byte what his own PNG reads as, so a module
    that already rewrote these frames, or a frame list in another order, stops the build here.
    """
    if len(headers) != len(pngs):
        raise ValueError(f"{len(headers)} frame headers and {len(pngs)} drawings: they must pair up")
    out = []
    for k, (head, png) in enumerate(zip(headers, pngs)):
        at = head - ROM_BASE + RAW_HEADER_LEN
        plain, dusted = dusted_frame(rom, png, DUST_PNGS[k - 1] if k else None)
        if len(plain) != FRAME_PX:
            raise ValueError(f"{png.name} is {len(plain)} bytes, and the record needs {FRAME_PX}")
        if bytes(rom[at:at + FRAME_PX]) != plain:
            raise ValueError(f"frame {k + 1} at rom:0x{at:X} is not what {png.name} reads as: "
                             f"another module already wrote these pixels")
        out.append((at, plain, dusted))
    return out


def _kits() -> dict:
    """Each earlier module's own PNG tuple, taken from the module rather than copied."""
    from patches import piccolo_powerup_art as pic
    from patches import vegeta_zplus as veg
    return {"vegeta_zplus": veg.POWER_UP_PNGS, "piccolo_powerup_art": pic.POWER_UP_PNGS}


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    if "powerup_fx" in alloc.notes:
        raise ValueError("powerup_fx already ran")
    if "bf_ki_pool" not in alloc.notes:
        raise ValueError("powerup_fx needs the bf_ki_pool notes: run the dev master first")
    jobs = [j for j in JOBS if j[0] in alloc.notes]
    if not jobs:
        raise ValueError("powerup_fx needs vegeta_zplus or piccolo_powerup_art: "
                         "without one of them no set holds the drawn power-up frames")

    # checks, before any write
    ki = alloc.notes["bf_ki_pool"]
    chained = vtable_target(rom, XFORM_VTABLE, XFORM_SLOT)
    if chained != (ki["labels"]["tick_xform"] | 1):
        raise ValueError(f"state 35 vtable 0x{XFORM_VTABLE:08X} +0x{XFORM_SLOT:X} names 0x{chained:08X}, "
                         f"not bf_ki_pool's tick_xform 0x{ki['labels']['tick_xform'] | 1:08X}")
    if vtable_target(rom, EFFECT_VTABLE, 0x08) != 0x08013657:
        raise ValueError(f"the effect vtable 0x{EFFECT_VTABLE:08X} +8 no longer names the effect tick")
    leave = vtable_target(rom, XFORM_VTABLE, LEAVE_SLOT)
    if leave != VANILLA_LEAVE:
        raise ValueError(f"state 35 vtable 0x{XFORM_VTABLE:08X} +0x{LEAVE_SLOT:X} names 0x{leave:08X}, "
                         f"not the vanilla leave 0x{VANILLA_LEAVE:08X}")
    namers(rom, AURA_RAM, alloc.used())        # raises when any ROM word already names our RAM block
    kits, plans, pixels = _kits(), {}, {}
    sets = {"gold": NO_SET, "white": NO_SET}
    for module, set_id, colour, _ in jobs:
        sets[colour] = set_at(rom, set_id) + ROM_BASE
        note = alloc.notes[module]
        headers = note["anim_frames"]["headers"] if "anim_frames" in note else note["headers"]
        plans[module] = plan_dust(rom, headers, kits[module])
        pixels[colour] = [aura_indices(rom, p, GOLD_SWAP if colour == "gold" else WHITE_SWAP)
                          for p in AURA_PNGS[colour]]
        if any(len(b) != FRAME_PX for b in pixels[colour]):
            raise ValueError(f"an aura frame is not {FRAME_PX} bytes")

    # 1. allocate the aura pixels and one record list per colour; nothing is written yet
    lists, blobs = {}, []
    for colour in ("gold", "white"):
        if colour not in pixels:
            lists[colour] = 0
            continue
        at = [alloc.alloc(FRAME_PX) for _ in pixels[colour]]
        blobs += list(zip(at, pixels[colour]))
        body = b"".join(struct.pack("<bbBBHHI", AURA_DX, AURA_DY, AURA_W, AURA_H, ATTR0, ATTR1,
                                    at[k] + ROM_BASE) for k in ORDER)
        lists[colour] = alloc.alloc(len(body))
        blobs.append((lists[colour], body))

    syms = {"XFORM_TICK": chained, "SPAWN_AT": SPAWN_AT, "STEP": STEP, "VRAM_BYTES": VRAM_BYTES,
            "LAYER": LAYER, "FRAMES": FRAMES, "EFFECT_CTOR": EFFECT_CTOR, "WORLD_ADD": WORLD_ADD,
            "WORLD_PTR": WORLD_PTR, "SET_GOLD": sets["gold"], "SET_WHITE": sets["white"],
            "EFFECT_VTABLE": EFFECT_VTABLE, "WORLD_REMOVE": WORLD_REMOVE, "WORLD_LIST": WORLD_LIST,
            "AURA_RAM": AURA_RAM, "AURA_LIVE": AURA_LIVE, "OLD_LEAVE": leave,
            "LIST_GOLD": (lists["gold"] + ROM_BASE) if lists["gold"] else 0,
            "LIST_WHITE": (lists["white"] + ROM_BASE) if lists["white"] else 0}
    size = len(assemble(CODE, ROM_BASE, syms)[0])
    code = alloc.alloc(size)
    blob, labels = assemble(CODE, code + ROM_BASE, syms)
    if len(blob) != size:                     # a size change would shift every later ROM byte
        raise ValueError(f"code assembled to 0x{len(blob):X} bytes, allocated 0x{size:X}")

    # 2. the aura art, the record lists and the code
    for at, data in blobs:
        rom[at:at + len(data)] = data
    rom[code:code + size] = blob

    # 3. the dust, into the frames the earlier modules wrote
    for module in plans:
        for at, _, dusted in plans[module]:
            rom[at:at + FRAME_PX] = dusted

    # 4. the two hooks: state 35's tick, and its leave
    hook = XFORM_VTABLE - ROM_BASE + XFORM_SLOT
    rom[hook:hook + 4] = _word((labels["fx_tick"] | 1) - XFORM_VTABLE)
    leave_hook = XFORM_VTABLE - ROM_BASE + LEAVE_SLOT
    rom[leave_hook:leave_hook + 4] = _word((labels["fx_leave"] | 1) - XFORM_VTABLE)

    alloc.notes["powerup_fx"] = {
        "code": code, "code_len": size, "hook": hook, "chained": chained, "lists": lists,
        "leave_hook": leave_hook, "chained_leave": leave, "ram": AURA_RAM, "ram_len": AURA_RAM_LEN,
        "sets": sets, "spawn_at": SPAWN_AT, "records": FRAMES, "step": STEP,
        "dust": {m: [at for at, _, _ in plans[m]] for m in plans},
        "labels": {k: v - ROM_BASE for k, v in labels.items() if not k.startswith(("fx_g", "fx_s", "fx_d"))}}
