r"""
sprite_lab.py - Trial patch: a sprite lab. Gohan on a flat colour field, no HUD, no enemies, no scene,
                so a capture job can film every animation (me, 2026-10-30 11:15-11:20 PM:
                "Or a custom rom with a totally white background, our own debugger."
                "No enemies either and no action restriction.").

Usage:   py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_spritelab.txt
             --out builds\mockups\2026-10-31-sprite-lab\log2_poc_r40_spritelab.gba
Input:   r40 (or the padded base). It needs the vanilla player vtable word, the vanilla map 8,36 entry and
         the vanilla save pointer word. No earlier patch notes are read.
API:     apply(rom, alloc) -> None. File offsets in alloc.notes["sprite_lab"], every write as
         (offset, length, name) in its "sites". lab_colour() -> the chosen BGR555 word.
         enter_script() -> the enter-script bytes. gate_byte_address() -> the flag byte address.

CHANGE THE BACKGROUND COLOUR HERE: set LAB_COLOUR below to one of the LAB_COLOURS names.
         Default "lime". Never leave it on "white" for gi work: the gi carries a white swoosh, light greys
         and highlights, so a white field hides exactly the pixels the sheet is for (Ruling 49, the same
         lime the review sheets use).

Method:  1. A wrapper in free space takes the player object update, vtable slot vt_player +8
            (`rom:0x2560C`, vanilla `@0x08008766`, CONFIRMED by the codemap: that slot is its only
            reference). It runs every frame the world runs, on the field and in a cutscene, never in a
            menu. While the lab gate flag is clear it only tail-calls the vanilla update, so a ROM with
            this module behaves as r40 on every ordinary save.
         2. With the gate flag set it first clears DISPCNT bits 8-11 (BG0-BG3 off) and writes BG palette
            entry 0, the backdrop, with LAB_COLOUR. Nothing else on the GBA draws where no layer and no
            sprite draws, so the field becomes one flat colour and the sprite keeps its own OBJ palette,
            which this module never touches. The write is per frame because a map load fade, a transform
            flash and ext 42 all rewrite palette RAM; a one-shot write would be undone part way through a
            capture and would quietly spoil the sheet.
         3. The lab map 8,36 gets an enter script (entry +0x30, vanilla 0): `ext 86 (0)` turns the HUD off
            (`@0x0800AB82` toggles save header +1 bit 1, which builds or drops the HUD object) and
            `ext 31` puts the camera at LAB_CAMERA and stops the follow. The script then ends, so the
            player keeps full control: no scene, no action restriction.
            MEASURED 2026-10-31: the enter script does NOT run when the save drops the player straight on
            the map through Continue. Two proofs: IWRAM 0x03000FF4 reads 0x030020C0, the follow camera,
            not ext 31's scene camera 0x030020C8; and a build with LAB_CAMERA (0,0), well inside the
            clamp, gives a pixel-identical frame. So on the Continue path the HUD is off because the lab
            save clears header +1 bit 1, and the camera is the follow camera held at its clamp corner.
            The script is kept because it is correct and fires on a warp into the map; whether it does is
            not yet captured. See the report's PENDING table.
         4. No enemies: map 8,36 needs no patch. Every one of its five list words and all five list count
            bytes are 0, and its variation, enter and leave script words are 0, so the map builds no enemy,
            no NPC and no region. The module checks all of that before it writes and refuses otherwise.
Gate:    story flag LAB_FLAG, read straight out of the save slot RAM copy. It is per slot, so one save
         file holds the lab slot and a plain Ginger Town slot for a real-scenery comparison.
Rules:   Source: docs\tasks\2026-10-31-sprite-lab\sprite-lab.md. Every site is checked before the first
         write; the new space must be 0xFF and named by no ROM word (a named chunk stays unused, notes
         "skipped"); no earlier module may write the vtable word or the map entry; a second run raises.
         Hand-assembled Thumb through ssj2_form.assemble; tests\test_sprite_lab.py decodes it with
         thumb_dis. This module writes no byte below rom:0x800000 but the two hooked words.
Labels:  CONFIRMED = read from the game code or the ROM bytes. LIKELY = strong evidence, my test pending.
"""
import struct

from scene import scene_lib
from patches.bf_ki_pool import words_naming
from patches.ssj2_form import assemble

# ===== CONFIG: the lab background colour (edit LAB_COLOUR, then rebuild) =====
# BGR555, the GBA backdrop word. Lime is the review-sheet lime (191,255,7) of Ruling 49: no OBJ palette
# entry is within about 32 steps per channel, so no gi pixel can be mistaken for the field.
LAB_COLOURS = {
    "lime":    0x03F7,          # (191,255,7)  the review-sheet lime; the default
    "magenta": 0x7C1F,          # (248,0,248)  for judging a green or yellow aura
    "white":   0x7FFF,          # (248,248,248) hides the white swoosh and the light greys: last resort
    "black":   0x0000,          # (0,0,0)      for judging a light outline
}
LAB_COLOUR = "lime"

# ===== CONFIG: where the lab stands =====
LAB_MAP = (8, 36, 1)            # zone, area, variation. Entry rom:0x40C778: every list and script word 0
LAB_SPOT = (236, 180)           # the centre of the map's largest clear square (88 px, cells 24,17)
# View top-left. The map view clamps the camera to 0..+0x5C by 0..+0x5E, measured (72,80) on this map, so
# (72,80) is its far corner and the largest legal value. The follow camera already parks there with the
# player at LAB_SPOT, which is why the lab frames look fixed today. See the enter-script note below.
LAB_CAMERA = (72, 80)
LAB_FLAG = 350                  # the gate: no script op and no condition word names it (two shapes)

# ===== constants: sources (base and r40 bytes, read 2026-10-31) =====
ROM_BASE = 0x08000000
VT_PLAYER = 0x08025604                                   # symbols.py vt_player
HOOK = VT_PLAYER - ROM_BASE + 8                          # rom:0x2560C, the update slot
VANILLA_PLAYER_UPDATE = 0x08008767                       # Thumb @0x08008766
PLAYER_UPDATE_BODY = (0x8766, bytes.fromhex("10b5041cff308130006801684a685218"))
MAP_TABLE, MAP_COUNT, MAP_SIZE = 0x409368, 327, 56
ENTER_SCRIPT = 0x30                                      # entry +0x30 (map 8,46 rom:0x402DDC, bible CH8)
LIST_FIELDS = {0x10: 3, 0x14: 4, 0x18: 5, 0x1C: 6, 0x20: 7}   # list word offset -> its count byte
SCRIPT_FIELDS = (0x28, 0x30, 0x34)                       # variation, enter, leave: all 0 on the lab map
SAVE_PTR, SAVE = 0x086F7E50, 0x03000E90                  # base tick @0x0801702A: ldr r7,=.. ; ldr r0,[r7,#4]
O_STORY = 0xB4                                           # slot +0xB4, story flag bits, LSB first
HUD_OFF, CAMERA_SPEED = 0, 255                           # ext 86 (0) = HUD off; ext 31 speed
MAX_TRIES = 8

# ===== new code (ARMv4T Thumb). r0 = the player object, as vt_player +8 is called =====
# No `and`, `orr` or `bic`: ssj2_form.assemble encodes none of them (bible trap, CHF2). The DISPCNT
# rebuild splits the halfword into two fields that do not overlap and adds them, and the flag test
# isolates one bit with a pair of shifts.
CODE = """
lab_update:
    push {r4,lr}
    add r4,r0,#0            ; keep the player object: the vanilla update takes it in r0
    ldr r1,=GATE_BYTE
    ldrb r0,[r1,#0x0]
    lsl r0,r0,#GATE_LEFT    ; the gate bit goes to bit 31
    lsr r0,r0,#31
    cmp r0,#0x0
    beq lab_done            ; gate clear: this ROM behaves as r40
    ldr r1,=IO
    ldrh r0,[r1,#0x0]       ; DISPCNT
    lsl r2,r0,#24
    lsr r2,r2,#24           ; bits 0-7: video mode and the flags below the layers
    lsr r3,r0,#12
    lsl r3,r3,#12           ; bits 12-15: OBJ on, the windows
    add r0,r2,r3            ; bits 8-11 gone: BG0, BG1, BG2 and BG3 off
    strh r0,[r1,#0x0]
    ldr r1,=PAL
    ldr r0,=COLOUR
    strh r0,[r1,#0x0]       ; BG palette entry 0: the backdrop, the only thing left to see
lab_done:
    add r0,r4,#0
    ldr r3,=PLAYER_UPDATE
    bl via_r3               ; the vanilla player update, r0 untouched
    pop {r4,pc}
via_r3:
    bx r3
"""

def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]

def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")

# ===== the pieces a test can ask for on their own =====

def lab_colour() -> int:
    """The BGR555 backdrop word LAB_COLOUR names."""
    if LAB_COLOUR not in LAB_COLOURS:
        raise ValueError(f"LAB_COLOUR {LAB_COLOUR!r} is not one of {sorted(LAB_COLOURS)}")
    return LAB_COLOURS[LAB_COLOUR]

def gate_byte_address() -> int:
    """The RAM byte that holds the gate flag: slot +0xB4 + flag / 8 (log2_save.bit, LSB first)."""
    return SAVE + O_STORY + (LAB_FLAG >> 3)

def gate_left_shift() -> int:
    """The left shift that puts the gate bit at bit 31 of a byte loaded with ldrb."""
    return 31 - (LAB_FLAG & 7)

def enter_script() -> bytes:
    """The lab map's enter script: HUD off, camera placed, then end so the player keeps control."""
    return (scene_lib.ext(86, HUD_OFF)
            + scene_lib.ext(31, LAB_CAMERA[0], LAB_CAMERA[1], CAMERA_SPEED)
            + bytes([17]))

def map_entry(rom: bytes, zone: int, area: int) -> int:
    for i in range(MAP_COUNT):
        at = MAP_TABLE + i * MAP_SIZE
        if rom[at] == zone and rom[at + 1] == area:
            return at
    raise ValueError(f"no map entry for {zone},{area}")

def _syms() -> dict:
    return {"GATE_BYTE": gate_byte_address(), "GATE_LEFT": gate_left_shift(),
            "IO": 0x04000000, "PAL": 0x05000000, "COLOUR": lab_colour(),
            "PLAYER_UPDATE": VANILLA_PLAYER_UPDATE}

# ===== checks =====

def _written(notes: dict) -> list:
    """(module, (offset, length)) of every earlier module's "sites": triples, or bare offsets."""
    out = []
    for name, n in notes.items():
        for site in n.get("sites", []) if isinstance(n, dict) else []:
            out.append((name, (site, 1) if isinstance(site, int) else tuple(site[:2])))
    return out

def _check(rom: bytearray, alloc) -> None:
    if "sprite_lab" in alloc.notes:
        raise ValueError("sprite_lab already ran")
    lab_colour()
    zone, area, var = LAB_MAP
    # 1. the hook word is the vanilla player update, in the vtable's own base-relative form
    _expect(rom, HOOK, struct.pack("<I", (VANILLA_PLAYER_UPDATE - VT_PLAYER) & 0xFFFFFFFF))
    _expect(rom, *PLAYER_UPDATE_BODY)
    _expect(rom, SAVE_PTR - ROM_BASE + 4, struct.pack("<I", SAVE))
    # 2. the lab map builds nothing and runs nothing
    entry = map_entry(rom, zone, area)
    if rom[entry + 2] != var:
        raise ValueError(f"map {zone},{area} entry rom:0x{entry:X} is variation {rom[entry + 2]}, not {var}")
    for off, count in LIST_FIELDS.items():
        if _u32(rom, entry + off) or rom[entry + count]:
            raise ValueError(f"map {zone},{area} list +0x{off:X} is {_u32(rom, entry + off):08X} "
                             f"with count {rom[entry + count]}: it is not an empty map, stop and report")
    for off in SCRIPT_FIELDS:
        if _u32(rom, entry + off):
            raise ValueError(f"map {zone},{area} script word +0x{off:X} is "
                             f"{_u32(rom, entry + off):08X}, expected 0")
    # 3. no earlier module wrote either hooked word
    for site in ((HOOK, 4, "vt_player +8"), (entry + ENTER_SCRIPT, 4, "lab map enter script")):
        for name, (s, n) in _written(alloc.notes):
            if s < site[0] + site[1] and site[0] < s + n:
                raise ValueError(f"{site[2]} rom:0x{site[0]:X} is also written by {name}: stop and report")

# ===== patch =====

def _chunk(rom: bytearray, alloc, size: int, skipped: list) -> int:
    """A free chunk that no ROM word names (rom_space rule); a named one stays unused."""
    for _ in range(MAX_TRIES):
        at = alloc.alloc(size)
        if set(rom[at:at + size]) != {0xFF}:
            raise ValueError(f"rom:0x{at:X} (0x{size:X} bytes) is not free")
        named = words_naming(rom, at + ROM_BASE, at + ROM_BASE + size, ())
        if not named:
            return at
        skipped.append((at, size, named))
    raise ValueError(f"no free chunk of 0x{size:X} bytes in {MAX_TRIES} tries")

def apply(rom: bytearray, alloc) -> None:
    _check(rom, alloc)
    entry = map_entry(rom, *LAB_MAP[:2])
    skipped = []

    body = enter_script()
    script_at = _chunk(rom, alloc, len(body), skipped)
    rom[script_at:script_at + len(body)] = body

    size = len(assemble(CODE, ROM_BASE, _syms())[0])
    code_at = _chunk(rom, alloc, size, skipped)
    blob, labels = assemble(CODE, code_at + ROM_BASE, _syms())
    if len(blob) != size:                                # pool padding depends on the address
        raise ValueError(f"the wrapper assembled to 0x{len(blob):X} bytes, allocated 0x{size:X}")
    rom[code_at:code_at + size] = blob

    rom[HOOK:HOOK + 4] = struct.pack("<I", ((labels["lab_update"] | 1) - VT_PLAYER) & 0xFFFFFFFF)
    rom[entry + ENTER_SCRIPT:entry + ENTER_SCRIPT + 4] = struct.pack("<I", script_at + ROM_BASE)

    alloc.notes["sprite_lab"] = {
        "wrapper": code_at, "size": size, "hook": HOOK, "entry": entry,
        "enter_script": script_at, "enter_script_size": len(body),
        "colour": LAB_COLOUR, "colour_word": lab_colour(), "map": LAB_MAP, "spot": LAB_SPOT,
        "camera": LAB_CAMERA, "flag": LAB_FLAG, "skipped": skipped,
        "sites": [(HOOK, 4, "vt_player +8 update word"),
                  (entry + ENTER_SCRIPT, 4, "lab map enter script word"),
                  (script_at, len(body), "lab map enter script"),
                  (code_at, size, "lab player update wrapper")]}
