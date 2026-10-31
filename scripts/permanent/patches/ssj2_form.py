r"""
ssj2_form.py - Patch: usable Super Saiyan 2 for Gohan after story flag 195 (Task 6, Rulings 10-17).

Usage:   py -3 -I scripts\permanent\log2_build.py --out builds\log2_poc.gba gohan_gi ssj2_form
Input:   the ROM after patches.gohan_gi (alloc.notes["gohan_gi"]); art\hud_z2_usable.bin, hud_z2_dim.bin.
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["ssj2_form"].
         assemble(src, base, syms) -> (bytes, labels): the Thumb assembler status_bonus also uses.
Method:  1. Copy the live appearance table (22 entries, with gohan_gi's sets 157 and 158) to the expansion
            area, add entry 22 (set 159, form object below, +4 = +5 = 2) and set entry 5 +4 = 22.
            Repoint the 17 table literals. rom:0x42F0 stays on gohan_gi's unchanged copy (ext op 73).
         2. New form object (ROM word) and vtable: new apply (+20 STR, POW, END, Super Saiyan speeds) and
            tick (drain step 0x199A = twice 0xCCD); enter and leave are the Super Saiyan sound methods.
         3. Step gate on the ability 12 action (rom:0x1D99CC): when step_ok holds (transformed, +4 differs
            from +5 (only entry 5), flag 195 set, EP >= 10), send message 0x23 (transform); else run 0x0801353C.
         4. HUD hook: rom:0x8E8C and rom:0x8D14 call a routine that shows what B does next. Ability 12 gets
            the Z2 icon pair while the record is in entry 22 or step_ok holds, else the vanilla icon.
            step_ok is the one predicate the gate and the HUD share, so the icon cannot disagree with B.
Rules:   Source: docs\research\re-forms.md section 7. Every site is checked against its original bytes before any
         write. New code enters only through absolute pointers and calls base code through local bx stubs.
         Never touches the shared Super Saiyan pool 0x080174A0 or the Rage entry. Hand-assembled Thumb
         (no assembler installed); tests\test_ssj2.py checks it with the separate decoder thumb_dis.py.
"""
import re
import struct

import log_paths

# ===== constants =====
ROM_BASE = 0x08000000
ART = log_paths.ART
APPEARANCE, ENTRY, ENTRIES = 0x1D967C, 20, 22
SSJ, SSJ2, BASE_FORM = 5, 22, 2
SSJ2_SET, RAGE_PORTRAITS = 159, bytes([0x3D, 0x0C])                         # Rulings 13 and 18
TABLE_LITERALS = (0x1954, 0x1B3C, 0x3B30, 0x414C, 0x854C, 0x886C, 0x8B04, 0xA77C, 0xAA04, 0xB050,
                  0xC804, 0x10F18, 0x112BC, 0x13574, 0x14FF4, 0x26458, 0x26474)
REVERSE_LITERAL = 0x42F0                                                    # left on gohan_gi's copy
SET_TABLE_LITERAL, FIRST_SET_ID = 0x959C, 7                                 # gohan_gi's relocated set table
ABILITY_12_ACTION, VANILLA_ACTION = 0x1D99CC, 0x0801353D
HUD_LITERAL, ABILITY_TABLE = 0x8E8C, 0x081D9900
HUD_BLOCK = (0x8D10, bytes.fromhex("687a5e494019007e00014618b168281c19f003f8002801d0316800e07168"))
HUD_SITE = 0x8D14
HUD_PATCH = bytes.fromhex("281c19f008f8011c07e0")   # add r0,r5,#0 ; bl 0x8021d2a ; add r1,r0,#0 ; b 0x8008d2e
SSJ_ENTER, SSJ_LEAVE, SSJ_VT_10, SSJ_VT_14 = 0x08017377, 0x08017393, 0x080271E1, 0x08026391
FLAG_195 = (0x03000F5C, 3)                          # struct 0x03000E90 + 0xB4 + 195 / 8, bit 195 & 7
STEP_EP = 10                                        # Ruling 11; never below 9 (Ruling 15)
DRAIN_STEP = 2 * 0xCCD                              # Super Saiyan accumulator step 0xCCD (@0x080174A0)
SPEEDS = (0x3FE00000, 0x40400000)                   # 1.75 / 3.0, as Super Saiyan (Ruling 11)
Z2_ICONS = ("hud_z2_usable.bin", "hud_z2_dim.bin")  # approved 2026-10-16 (Rulings 12, 17)
ICON_LEN = 0x200

# ===== new code (ARMv4T Thumb). Symbols in caps are filled in at assembly =====
CODE = """
apply:                      ; r1 = player. Re-encodes 0x080172B0 with +20 in place of +10
    push {r4,lr}
    add r4,r1,#0
    ldr r0,=0x086f7e50
    ldr r0,[r0,#0x4]
    ldrb r1,[r0,#0x0]
    lsl r3,r1,#3
    sub r1,r3,r1
    lsl r1,r1,#2
    add r1,r1,r0
    add r1,#0xc             ; r1 = leader record
    ldrh r0,[r1,#0xa]
    lsr r2,r0,#8
    add r0,r4,#0
    add r0,#0xff
    add r0,#0x61            ; r0 = player +0x160
    add r2,#0x14
    strb r2,[r0,#0x0]
    ldrh r2,[r1,#0xc]
    lsr r2,r2,#8
    add r2,#0x14
    strb r2,[r0,#0x1]
    ldrh r1,[r1,#0xe]
    lsr r1,r1,#8
    add r1,#0x14
    strb r1,[r0,#0x2]
    mov r1,#0x80
    strb r1,[r0,#0x3]
    strb r1,[r0,#0x4]
    ldr r1,=SPEED_WALK
    add r0,#0x28
    ldr r2,=0x080265c5
    bl stub_r2
    add r0,r4,#0
    add r0,#0xff
    add r0,#0x8d
    ldr r1,=SPEED_RUN
    ldr r2,=0x080265c5
    bl stub_r2
    mov r0,#0x0
    add r4,#0xff
    add r4,#0x81
    str r0,[r4,#0x4]
    pop {r4,pc}
tick:                       ; r1 = player. Re-encodes 0x08017306 with its own drain step
    push {r3,r4,r5,lr}
    add r5,r1,#0
    add r0,r1,#0
    ldr r1,[r1,#0x0]
    ldr r2,[r1,#0x2c]
    add r2,r2,r1
    mov r1,#0x24
    bl stub_r2              ; in state 0x24 (revert)? then skip
    cmp r0,#0x0
    bne tick_end
    add r4,r5,#0
    add r4,#0xff
    add r4,#0x81
    ldr r0,[r4,#0x4]
    ldr r1,=DRAIN_STEP
    add r0,r0,r1
    str r0,[r4,#0x4]
    lsr r0,r0,#16
    beq tick_end
    ldr r0,=0x086f7e50
    ldr r0,[r0,#0x4]
    ldrb r1,[r0,#0x0]
    lsl r3,r1,#3
    sub r1,r3,r1
    lsl r1,r1,#2
    add r0,r1,r0
    add r0,#0xc
    mov r3,#0x4
    ldsh r2,[r0,r3]         ; EP
    add r1,r0,#4
    cmp r2,#0x1
    bge tick_dec
    mov r2,#0x0
    strh r2,[r1,#0x0]
    b tick_check
tick_dec:
    sub r2,#0x1
    strh r2,[r1,#0x0]
tick_check:
    ldrh r1,[r0,#0x4]
    cmp r1,#0x0
    bne tick_mask
    ldrh r0,[r0,#0x0]
    cmp r0,#0x0
    beq tick_mask
    ldr r1,[r5,#0x0]
    add r0,r5,#0
    ldr r2,[r1,#0x28]
    add r2,r2,r1
    mov r1,#0x24
    bl stub_r2              ; EP 0 and HP not 0: message 0x24 (revert)
tick_mask:
    ldr r0,[r4,#0x4]
    lsl r0,r0,#16
    lsr r0,r0,#16
    str r0,[r4,#0x4]
tick_end:
    pop {r3,r4,r5,pc}
step_ok:                    ; r0 = record. r2 = 1 when B steps up, else 0. Leaf: keeps r0, r1; uses r3
    ldrb r2,[r0,#0x8]
    lsl r3,r2,#2
    add r2,r3,r2
    lsl r2,r2,#2
    ldr r3,=TABLE
    add r2,r2,r3            ; r2 = relocated entry
    ldrb r3,[r2,#0x0]
    lsl r3,r3,#31
    beq step_no             ; not transformed
    ldrb r3,[r2,#0x4]
    ldrb r2,[r2,#0x5]
    cmp r2,r3
    beq step_no             ; no step target
    ldr r2,=FLAG_ADDR
    ldrb r2,[r2,#0x0]
    lsl r2,r2,#FLAG_SHIFT
    bpl step_no             ; flag 195 clear
    mov r3,#0x4
    ldsh r2,[r0,r3]
    cmp r2,#STEP_EP
    blt step_no             ; EP under the step cost
    mov r2,#0x1
    bx lr
step_no:
    mov r2,#0x0
    bx lr
gate:                       ; r0 = record, r1 = player. Both exits tail-call with the caller's lr and sp
    push {lr}
    bl step_ok
    pop {r3}
    mov lr,r3               ; ARMv4T Thumb cannot pop lr
    cmp r2,#0x0
    beq gate_vanilla
    ldr r2,[r1,#0x0]
    ldr r3,[r2,#0x28]
    add r3,r3,r2
    add r0,r1,#0
    mov r1,#0x23
    bx r3                   ; tail call: player message 0x23 (transform)
gate_vanilla:
    ldr r2,=0x0801353d
    bx r2                   ; tail call: vanilla action, r0 and r1 unchanged
hud:                        ; r0 = record, returns the icon in r0. Keeps r4-r7
    push {r4,r5,r6,lr}
    add r4,r0,#0
    ldrb r0,[r4,#0x9]
    add r0,r0,r4
    ldrb r5,[r0,#0x18]      ; ability id of the selected slot
    lsl r0,r5,#4
    ldr r1,=0x081d9900
    add r6,r0,r1
    ldr r1,[r6,#0x8]
    add r0,r4,#0
    bl stub_r1              ; r0 = ability test(record): bright or dim
    cmp r5,#0xc
    bne hud_vanilla
    ldrb r1,[r4,#0x8]
    cmp r1,#0x16
    beq hud_z2              ; in Super Saiyan 2
    add r5,r0,#0
    add r0,r4,#0
    bl step_ok
    add r0,r5,#0
    cmp r2,#0x0
    beq hud_vanilla         ; B reverts
hud_z2:
    ldr r1,=Z2
    cmp r0,#0x0
    bne hud_done
    ldr r1,=Z2_DIM
    b hud_done
hud_vanilla:
    ldr r1,[r6,#0x0]
    cmp r0,#0x0
    bne hud_done
    ldr r1,[r6,#0x4]
hud_done:
    add r0,r1,#0
    pop {r4,r5,r6,pc}
stub_r1:
    bx r1
stub_r2:
    bx r2
"""


# ===== Thumb assembler (the subset CODE uses) =====

def _reg(s: str) -> int:
    if not re.fullmatch(r"r[0-7]", s):
        raise ValueError(f"not a low register: {s}")
    return int(s[1])


def _rlist(s: str, extra: str) -> tuple:
    regs = [r.strip() for r in s.strip("{}").split(",")]
    has = extra in regs
    return sum(1 << _reg(r) for r in regs if r != extra), has


def _imm(s: str, syms: dict, bits: int, scale: int = 1) -> int:
    s = s.lstrip("#")
    v = syms[s] if s in syms else int(s, 0)
    if v % scale or not 0 <= v // scale < 1 << bits:
        raise ValueError(f"immediate {s} does not fit {bits} bits x{scale}")
    return v // scale


def _lines(src: str) -> list:
    out = []
    for raw in src.splitlines():
        line = raw.split(";")[0].strip()
        if line:
            out.append(line)
    return out


def assemble(src: str, base: int, syms: dict) -> tuple:
    """(code bytes, {label: GBA address}) for Thumb source at GBA address base; literal pool at the end."""
    items, labels, pool, pc = [], {}, [], base
    for line in _lines(src):
        if line.endswith(":"):
            labels[line[:-1]] = pc
            continue
        op, _, args = line.partition(" ")
        items.append((pc, op, args.replace(" ", "")))
        if op == "ldr" and "=" in args:
            value = args.split("=")[1].strip()
            value = syms[value] if value in syms else int(value, 0)
            if value not in pool:
                pool.append(value)
        pc += 4 if op == "bl" else 2
    pool_at = (pc + 3) & ~3
    out = bytearray()
    for pc, op, args in items:
        out += _encode(pc, op, args.split(",") if not args.startswith("{") else [args], labels, syms, pool, pool_at)
    out += b"\0" * (pool_at - base - len(out))
    out += b"".join(struct.pack("<I", v) for v in pool)
    return bytes(out), labels


def _hreg(s: str) -> int:
    regs = {**{f"r{i}": i for i in range(13)}, "sp": 13, "lr": 14, "pc": 15}
    if s not in regs:
        raise ValueError(f"not a register: {s}")
    return regs[s]


def _target(name: str, labels: dict, syms: dict) -> int:
    return labels[name] if name in labels else syms[name]


def _encode(pc: int, op: str, a: list, labels: dict, syms: dict, pool: list, pool_at: int) -> bytes:
    h = lambda v: struct.pack("<H", v)                                   # noqa: E731
    conds = {"beq": 0, "bne": 1, "bmi": 4, "bpl": 5, "bge": 10, "blt": 11, "bgt": 12, "ble": 13}
    if op in ("add", "sub") and a[0] == "sp":                            # format 13: sp +/- imm
        return h((0xB000 if op == "add" else 0xB080) | _imm(a[1], syms, 7, 4))
    if op == "add" and len(a) == 3 and a[1] == "sp":                     # format 12: rd = sp + imm
        return h(0xA800 | _reg(a[0]) << 8 | _imm(a[2], syms, 8, 4))
    if op in ("ldr", "str") and len(a) == 3 and a[1] == "[sp":           # format 11: sp-relative word
        return h((0x9800 if op == "ldr" else 0x9000) | _reg(a[0]) << 8 | _imm(a[2].strip("]"), syms, 8, 4))
    if op in ("str", "strb", "ldr", "ldrb") and len(a) == 3 and re.fullmatch(r"r[0-7]\]", a[2]):
        base = {"str": 0x5000, "strb": 0x5400, "ldr": 0x5800, "ldrb": 0x5C00}[op]    # format 7: [rb, ro]
        return h(base | _reg(a[2].strip("]")) << 6 | _reg(a[1].strip("[")) << 3 | _reg(a[0]))
    if op in ("push", "pop"):
        mask, lr = _rlist(a[0], "lr" if op == "push" else "pc")
        return h((0xB400 if op == "push" else 0xBC00) | lr << 8 | mask)
    if op in ("lsl", "lsr") and len(a) == 3:
        return h((0x0000 if op == "lsl" else 0x0800) | _imm(a[2], syms, 5) << 6 | _reg(a[1]) << 3 | _reg(a[0]))
    if op in ("add", "sub") and len(a) == 3:
        if a[2].startswith("#"):
            return h((0x1C00 if op == "add" else 0x1E00) | _imm(a[2], syms, 3) << 6 | _reg(a[1]) << 3 | _reg(a[0]))
        return h((0x1800 if op == "add" else 0x1A00) | _reg(a[2]) << 6 | _reg(a[1]) << 3 | _reg(a[0]))
    if op in ("mov", "cmp", "add", "sub") and len(a) == 2 and a[1].startswith("#"):
        return h({"mov": 0x2000, "cmp": 0x2800, "add": 0x3000, "sub": 0x3800}[op] | _reg(a[0]) << 8
                 | _imm(a[1], syms, 8))
    if op == "cmp" and len(a) == 2:
        return h(0x4280 | _reg(a[1]) << 3 | _reg(a[0]))
    if op == "mul" and len(a) == 2:                                      # format 4: rd = rd * rs (ssj2_idle)
        return h(0x4340 | _reg(a[1]) << 3 | _reg(a[0]))
    if op == "mov" and len(a) == 2:                                      # format 5: a high register on either side
        d, s = _hreg(a[0]), _hreg(a[1])
        if d < 8 and s < 8:
            raise ValueError(f"mov {a[0]},{a[1]}: ARMv4T format 5 needs a high register")
        return h(0x4600 | (d >> 3) << 7 | s << 3 | d & 7)
    if op == "bx":
        return h(0x4700 | _hreg(a[0]) << 3)
    if op == "ldr" and a[1].startswith("="):
        name = a[1][1:]
        value = syms[name] if name in syms else int(name, 0)
        words = (pool_at + 4 * pool.index(value) - ((pc + 4) & ~3)) // 4
        if not 0 <= words < 256:
            raise ValueError(f"ldr ={name} pool word {words} out of range 0-255")
        return h(0x4800 | _reg(a[0]) << 8 | words)
    if op == "ldsh":
        rb, ro = a[1].strip("["), a[2].strip("]")
        return h(0x5E00 | _reg(ro) << 6 | _reg(rb) << 3 | _reg(a[0]))
    if op in ("ldr", "str", "ldrb", "strb", "ldrh", "strh"):
        rb, off = a[1].strip("["), a[2].strip("]")
        base, scale = {"str": (0x6000, 4), "ldr": (0x6800, 4), "strb": (0x7000, 1), "ldrb": (0x7800, 1),
                       "strh": (0x8000, 2), "ldrh": (0x8800, 2)}[op]
        return h(base | _imm(off, syms, 5, scale) << 6 | _reg(rb) << 3 | _reg(a[0]))
    if op in conds:
        off = (_target(a[0], labels, syms) - (pc + 4)) // 2
        if not -128 <= off < 128:
            raise ValueError(f"{op} {a[0]} out of range")
        return h(0xD000 | conds[op] << 8 | off & 0xFF)
    if op == "b":
        off = (_target(a[0], labels, syms) - (pc + 4)) // 2
        if not -1024 <= off < 1024:
            raise ValueError(f"b {a[0]} out of range")
        return h(0xE000 | off & 0x7FF)
    if op == "bl":
        off = _target(a[0], labels, syms) - (pc + 4)
        if not -0x400000 <= off < 0x400000:
            raise ValueError(f"bl {a[0]} out of range (+/-4 MB)")
        return h(0xF000 | (off >> 12) & 0x7FF) + h(0xF800 | (off >> 1) & 0x7FF)
    raise ValueError(f"cannot encode {op} {','.join(a)}")


# ===== patch =====

def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _word(v: int) -> bytes:
    return struct.pack("<I", v & 0xFFFFFFFF)


def apply(rom: bytearray, alloc) -> None:
    if "gohan_gi" not in alloc.notes:                                    # Ruling 14
        raise ValueError("ssj2_form needs the gohan_gi notes: run gohan_gi first")
    gi = alloc.notes["gohan_gi"]
    for off in TABLE_LITERALS:
        _expect(rom, off, _word(APPEARANCE + ROM_BASE))
    _expect(rom, REVERSE_LITERAL, _word(gi["appearance_copy"] + ROM_BASE))
    _expect(rom, ABILITY_12_ACTION, _word(VANILLA_ACTION))
    _expect(rom, HUD_LITERAL, _word(ABILITY_TABLE))
    _expect(rom, *HUD_BLOCK)
    _expect(rom, APPEARANCE + ENTRY * SSJ, bytes.fromhex("019e3e0d0402"))   # gi Super Saiyan 158, +4 = 4, +5 = 2
    _expect(rom, APPEARANCE + ENTRY * BASE_FORM + 1, bytes([157]))
    set_table = struct.unpack_from("<I", rom, SET_TABLE_LITERAL)[0] - ROM_BASE
    _expect(rom, set_table + 4 * (SSJ2_SET - FIRST_SET_ID), _word(gi[f"set_{SSJ2_SET}"] + ROM_BASE))
    icons = [(ART / name).read_bytes() for name in Z2_ICONS]
    if any(len(i) != ICON_LEN for i in icons):
        raise ValueError("Z2 icon files must be 0x200 bytes each")

    # 1. allocate everything and build entry 22; nothing is written until the code size is checked
    table = alloc.alloc(ENTRY * (ENTRIES + 1))
    obj = alloc.alloc(4 + 24)                                            # form object word, then its vtable
    vtable = obj + 4
    z2, z2_dim = alloc.alloc(ICON_LEN), alloc.alloc(ICON_LEN)
    entry = bytearray(rom[APPEARANCE + ENTRY * SSJ:APPEARANCE + ENTRY * SSJ + ENTRY])
    entry[1], entry[2:4], entry[4], entry[5] = SSJ2_SET, RAGE_PORTRAITS, BASE_FORM, BASE_FORM
    entry[0x10:0x14] = _word(obj + ROM_BASE)

    # 2-4. code, form object, vtable, icons
    syms = {"TABLE": table + ROM_BASE, "Z2": z2 + ROM_BASE, "Z2_DIM": z2_dim + ROM_BASE,
            "FLAG_ADDR": FLAG_195[0], "FLAG_SHIFT": 31 - FLAG_195[1], "STEP_EP": STEP_EP,
            "DRAIN_STEP": DRAIN_STEP, "SPEED_WALK": SPEEDS[0], "SPEED_RUN": SPEEDS[1]}
    size = len(assemble(CODE, ROM_BASE, syms)[0])
    code = alloc.alloc(size)
    blob, labels = assemble(CODE, code + ROM_BASE, syms)
    if len(blob) != size:                    # a size change would shift every later ROM byte
        raise ValueError(f"code assembled to 0x{len(blob):X} bytes, allocated 0x{size:X}")
    rom[table:table + ENTRY * ENTRIES] = rom[APPEARANCE:APPEARANCE + ENTRY * ENTRIES]
    rom[table + ENTRY * ENTRIES:table + ENTRY * (ENTRIES + 1)] = entry
    rom[table + ENTRY * SSJ + 4] = SSJ2
    rom[code:code + size] = blob
    rom[obj:obj + 4] = _word(vtable + ROM_BASE)
    targets = (labels["apply"] | 1, labels["tick"] | 1, SSJ_ENTER, SSJ_LEAVE, SSJ_VT_10, SSJ_VT_14)
    rom[vtable:vtable + 24] = b"".join(_word(t - (vtable + ROM_BASE)) for t in targets)
    rom[z2:z2 + ICON_LEN], rom[z2_dim:z2_dim + ICON_LEN] = icons

    # 5. repoint
    for off in TABLE_LITERALS:
        rom[off:off + 4] = _word(table + ROM_BASE)
    rom[ABILITY_12_ACTION:ABILITY_12_ACTION + 4] = _word(labels["gate"] | 1)
    rom[HUD_LITERAL:HUD_LITERAL + 4] = _word(labels["hud"] | 1)
    rom[HUD_SITE:HUD_SITE + len(HUD_PATCH)] = HUD_PATCH

    alloc.notes["ssj2_form"] = {"table": table, "form_object": obj, "vtable": vtable, "code": code,
                                "z2": z2, "z2_dim": z2_dim,
                                **{k: v - ROM_BASE for k, v in labels.items() if not k.startswith(("tick_", "gate_", "hud_", "step_no"))}}
