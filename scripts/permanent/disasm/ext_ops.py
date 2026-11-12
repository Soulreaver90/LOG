r"""
ext_ops.py - Profile all 145 scene-VM ext handlers from the disassembly: stack use, calls, RAM words.

Usage:   py -3.14 -P scripts\one-time\2026-11-06-op-catalogue\02_profile_handlers.py
Output:  <this folder>\handlers.md and handlers.json. Reads only; writes no ROM.
Reads:   ext handler table rom:0x3B5D28 in the base ROM, and the byte-exact disassembly at
         GitHub\legacyofgoku2-disasm\build\code (1476 generated .s files). NEVER the gnu repo, whose
         build\code is a stale 1333-file copy that bundles callees into the wrong function.

THE CALLING CONVENTION, read out of the handlers themselves:
  r0 enters holding the VM stack: {u32 depth at [r0+0], values at [r0+4+4*i] for i in 0..depth-1}.
  The TOP value therefore sits at [r0 + 4*depth].

  Handlers come in four shapes, and a counter that knows only the first gets three of them wrong.
  Each trap below was caught by disagreeing with an op we already knew:

  1. CONSUMER. Pops each argument inline: `SUB rX,#0x1` then `STR rX,[stack,#0x0]`. Arity is the
     number of those pairs. ext 31 camera pops 3. The SUB and the STR are NOT adjacent: an
     `LSL r2,r1,#0x2` for the slot address sits between them, so the pending decrement must survive
     every instruction except one that overwrites the decremented register itself.
     TRAP: r0 stops being the stack at the first BL. After `BL Sprite_Select` r0 is the actor and
     after `BL Heap_Alloc` r0 is a fresh struct, and stores into THAT struct look identical. Counting
     the whole body scored ext 55 face as 3 when it pops 2.
  2. PREDICATE. Reads the top slot and writes its RESULT BACK over it. Depth never changes, so the
     value is left for base op 19 `jz` to consume. ext 19 test_flag computes `ADD r4,depth*4,r0`,
     loads [r4+0], calls the bitmap test, and stores the answer to [r4+0]. One in, one out.
     Counting depth decrements scores it 0 and makes our correct table look wrong.
  3. ALIASED STACK. Moves the stack pointer out of r0 first (`ADD r1,r0,#0x0`) and pops through that
     register. ext 49 music does this, and a pattern keyed to [r0,#0x0] alone scores it 0.
  4. NON-VM. Ignores the stack and loads a global into r0 before its call. ext 63 does this, so
     following its callee and reporting the callee's pops is wrong. Delegation is therefore followed
     only when the stack pointer is still live at the first BL.
"""
import json
import re
import struct
from pathlib import Path

# ===== CONFIG =====
LOG = Path(r"C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG")
DISASM = Path(r"C:\Users\josephgonzalez\Documents\GitHub\legacyofgoku2-disasm")
ROM = LOG / "data" / "roms" / "Dragon Ball Z - The Legacy of Goku II (USA).gba"
OUT = LOG / "docs" / "research"
EXT_TABLE = 0x3B5D28
ROM_BASE, CODE_TOP = 0x08000000, 0x08800000
MAX_DELEGATE = 2

LABEL = re.compile(r"^\|(?:sub|loc)_([0-9A-Fa-f]{8})\|", re.M)
INSTR = re.compile(r"^\s+([A-Z][A-Z0-9]*)\s*(.*)$")
BL = re.compile(r"^\s*BL\s+\|([^|]+)\|")
DCD = re.compile(r"^\s*DCD\s+0x([0-9a-fA-F]{8})")
ALIAS = re.compile(r"^(?:ADD\s+r(\d+),\s*r(\d+),\s*#0x0|MOV\s+r(\d+),\s*r(\d+))$")
SUB1 = re.compile(r"^SUB\s+r(\d+),\s*#0x1$")
ADD1 = re.compile(r"^ADD\s+r(\d+),\s*r(\d+),\s*#0x1$")
STR0 = re.compile(r"^STR\s+r(\d+),\s*\[r(\d+),\s*#0x0\]$")
ADDRR = re.compile(r"^ADD\s+r(\d+),\s*r(\d+),\s*r(\d+)$")
WRITES = re.compile(r"^(?:LDR|LDRB|LDRH|MOV|ADD|SUB|LSL|LSR|ASR|AND|ORR|EOR|MUL|NEG|BIC|MVN)\s+r(\d+),")


def code_index() -> dict:
    """{address: (name, file)} from CODE_INDEX.md. The addresses are LOWERCASE hex; an uppercase
    pattern matches nothing and silently reports every handler as unnamed."""
    row = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*`0x([0-9a-f]{8})`\s*\|\s*`?([^`|]+?)`?\s*\|\s*$", re.M)
    text = (DISASM / "docs" / "CODE_INDEX.md").read_text(encoding="utf-8", errors="replace")
    return {int(a, 16): (n, f.strip()) for n, a, f in row.findall(text)}


def build_label_map() -> dict:
    """{address: file} for every sub_ and loc_ label. A handler start is not always a function start,
    and CODE_INDEX lists only function starts, so scanning every label is what finds the rest."""
    out = {}
    for f in (DISASM / "build" / "code").glob("*.s"):
        for addr in LABEL.findall(f.read_text(encoding="utf-8", errors="replace")):
            out.setdefault(int(addr, 16), f)
    return out


def body(path: Path, start: int) -> str:
    """From this handler's label down to the next sub_ label, so the next function is not included."""
    text = path.read_text(encoding="utf-8", errors="replace")
    marks = [(m.start(), int(m.group(1), 16), m.group(0)) for m in LABEL.finditer(text)]
    begin = next((pos for pos, addr, _ in marks if addr == start), None)
    if begin is None:
        return ""
    end = next((pos for pos, _, raw in marks if pos > begin and raw.startswith("|sub_")), len(text))
    return text[begin:end]


def profile_stack(text: str) -> dict:
    """{pops, predicate, stack_live_at_first_bl, first_bl}: how this handler uses the VM stack.

    Instructions are walked in order while tracking which registers still alias the incoming stack
    pointer. An alias dies the moment anything writes that register, and r0-r3 die at every call.
    That is what stops a store into a freshly allocated struct from counting as a pop."""
    alias, slot_regs = {0}, set()      # stack aliases; registers holding &stack[top]
    pops, pushes, predicate = 0, 0, False
    pending, pending_push = None, None   # a decremented / incremented depth awaiting its store
    first_bl, stack_live = None, None
    for raw in text.splitlines():
        m = INSTR.match(raw)
        if not m:
            continue
        line = f"{m.group(1)} {m.group(2).strip()}".strip()

        if m.group(1) == "BL":
            if first_bl is None:
                hit = BL.match(raw)
                first_bl = hit.group(1) if hit else m.group(2).strip()
                stack_live = bool(alias)
            alias -= {0, 1, 2, 3}
            slot_regs -= {0, 1, 2, 3}
            pending = pending_push = None
            continue

        sub = SUB1.match(line)
        if sub:
            pending = int(sub.group(1))
            continue

        inc = ADD1.match(line)             # depth + 1: this op PRODUCES a value (a getter)
        if inc:
            pending_push = int(inc.group(1))
            continue

        st = STR0.match(line)
        if st:
            src, dst = int(st.group(1)), int(st.group(2))
            if dst in alias and pending == src:
                pops += 1                       # shapes 1 and 3: a real depth decrement
            elif dst in alias and pending_push == src:
                pushes += 1                     # shape 5: a depth increment, so the op returns a value
            elif dst in slot_regs:
                predicate = True                # shape 2: result written back over the argument
            pending = pending_push = None
            continue

        add = ADDRR.match(line)                 # &stack[top] = stack + 4*depth
        if add:
            d, a, b = (int(g) for g in add.groups())
            slot_regs = (slot_regs | {d}) if (a in alias or b in alias) else (slot_regs - {d})
            alias.discard(d)
            if pending == d:
                pending = None
            continue

        al = ALIAS.match(line)
        if al:
            g = [x for x in al.groups() if x is not None]
            dst, src = int(g[0]), int(g[1])
            alias.add(dst) if src in alias else alias.discard(dst)
            if pending == dst:
                pending = None
            continue

        w = WRITES.match(line)
        if w:
            dead = int(w.group(1))
            alias.discard(dead)
            slot_regs.discard(dead)
            if pending == dead:
                pending = None          # the decremented value was overwritten before any store
            if pending_push == dead:
                pending_push = None
    return {"pops": pops, "pushes": pushes, "predicate": predicate,
            "stack_live_at_first_bl": bool(stack_live), "first_bl": first_bl}


def resolve(target: str, by_name: dict):
    """A BL target to an address: `sub_`/`loc_` plus hex, or a NAME from CODE_INDEX. Matching only the
    hex form missed every named callee, such as Bitmap_TestCell."""
    hit = re.fullmatch(r"(?:sub|loc)_([0-9A-Fa-f]{8})", target)
    return int(hit.group(1), 16) if hit else by_name.get(target)


def arity(text: str, labels: dict, by_name: dict, depth: int = 0) -> tuple:
    """(pops, pushes, predicate, delegated_to). A thin wrapper that touches nothing and hands the STILL LIVE
    stack to a callee is followed; one that loads a global into r0 first is not."""
    p = profile_stack(text)
    if p["pops"] or p["pushes"] or p["predicate"] or depth >= MAX_DELEGATE:
        return p["pops"], p["pushes"], p["predicate"], None
    if not p["first_bl"] or not p["stack_live_at_first_bl"]:
        return 0, 0, False, None
    callee = resolve(p["first_bl"], by_name)
    path = labels.get(callee) if callee else None
    if path is None:
        return 0, 0, False, None
    pops, pushes, pred, deeper = arity(body(path, callee), labels, by_name, depth + 1)
    return pops, pushes, pred, (deeper or f"0x{callee:08X}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rom = ROM.read_bytes()
    names, labels = code_index(), build_label_map()
    by_name = {n: a for a, (n, _) in names.items()}
    rows = []
    for n in range(512):
        word = struct.unpack_from("<I", rom, EXT_TABLE + 4 * n)[0]
        if not (ROM_BASE <= word < CODE_TOP and word & 1):
            break
        addr = word & ~1
        path = labels.get(addr)
        text = body(path, addr) if path else ""
        pops, pushes, pred, delegated = (arity(text, labels, by_name) if text
                                         else (None, 0, False, None))
        calls = []
        for raw in text.splitlines():
            hit = BL.match(raw)
            if hit:
                a = resolve(hit.group(1), by_name)
                calls.append(names.get(a, (hit.group(1), ""))[0] if a else hit.group(1))
        rows.append({"ext": n, "handler": addr, "name": names.get(addr, ("", ""))[0],
                     "file": path.name if path else "", "arity": pops, "pushes": pushes,
                     "predicate": pred,
                     "delegated_to": delegated, "calls": calls,
                     "ram": sorted({f"0x{w}" for w in DCD.findall(text)
                                    if 0x02000000 <= int(w, 16) <= 0x03FFFFFF})})
    (OUT / "scene-vm-ext-ops.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")

    out = [f"# Ext handler profile, {len(rows)} ops (ext 0 to {len(rows) - 1})", "",
           f"Table rom:0x{EXT_TABLE:X} in the base ROM. `arity` is how many values the op REMOVES from",
           "the VM stack. `pred` marks an op that instead replaces the top value with its result and",
           "leaves the depth alone, which is what a test feeding base op 19 `jz` must do.", "",
           "`pushes` marks an op that RETURNS a value: a getter, which takes no argument at all.", "",
           "| ext | handler | disasm name | pops | pushes | pred | via | calls | RAM words |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        out.append(f"| {r['ext']} | `0x{r['handler']:08X}` | {r['name'] or '-'} | "
                   f"{'?' if r['arity'] is None else r['arity']} | {r['pushes'] or ''} | "
                   f"{'yes' if r['predicate'] else ''} | "
                   f"{r['delegated_to'] or '-'} | {', '.join(r['calls'][:6]) or '-'} | "
                   f"{', '.join(r['ram'][:4]) or '-'} |")
    (OUT / "scene-vm-ext-ops.md").write_text("\n".join(out), encoding="utf-8")
    hist = {}
    for r in rows:
        key = "pred" if r["predicate"] else r["arity"]
        hist[key] = hist.get(key, 0) + 1
    print(f"{len(rows)} ext ops profiled")
    print("histogram:", ", ".join(f"{k}:{v}" for k, v in sorted(hist.items(), key=lambda kv: str(kv[0]))))
    print(f"wrote {OUT / 'scene-vm-ext-ops.md'}")


if __name__ == "__main__":
    main()
