r"""
listing.py - Annotated listing of one LoG II USA function, or the references to one address.

Usage:   (from scripts\permanent) py -3 -I disasm\listing.py <addr|name> [--refs] [--map PATH] [--rom PATH]
         <addr|name>  a GBA address (hex) or a symbols.py name (get_set) or sub_XXXXXXXX. An address inside a
                      function lists the whole function and marks that line with <==.
         --refs       instead of a listing: every literal-pool word in the code region equal to the address
                      (with the ldr sites that load it), and every aligned ROM word outside the code region.
Output:  header (name, address, size, mode, callers, bible row), then one line per instruction: address,
         bytes, text, comment. Comments name BL targets, literal values (functions, tables, RAM globals with
         an offset, strings), base-relative virtual calls, and bible rows that name an address in the body.
API:     listing(target, map_path, rom_path) -> [lines]; refs(target, map_path, rom_path) -> [lines].
Rules:   Reads scripts\permanent\disasm\data\codemap.json (the snapshot codemap.py writes) and the ROM; writes nothing. Function
         bodies come from codemap.explore with the codemap start set, so they match functions.csv.
         Adopted from scripts\one-time\2026-10-18-disasm-study\; this copy is the maintained one.
"""
import argparse
import bisect
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import codemap  # noqa: E402
import symbols  # noqa: E402

ROM_BASE = codemap.ROM_BASE
NEAR = 0x800                       # a table or RAM symbol names addresses up to this far past it


# ===== names =====

class Names:
    def __init__(self, funcs: dict):
        self.funcs = funcs
        self.starts = sorted(funcs)
        self.data = sorted((a, n) for n, a in symbols._BY_NAME.items() if symbols._KIND[a] != "func")
        self.data_addrs = [a for a, _ in self.data]
        self.sites = symbols.bible_addresses()

    def func(self, a: int) -> str:
        return symbols.name_of(a) or f"sub_{a:08X}"

    def containing(self, a: int):
        i = bisect.bisect_right(self.starts, a) - 1
        if i < 0:
            return None
        s = self.starts[i]
        mode, size, extent = self.funcs[s]
        return s if a < s + max(size, extent) else None

    def value(self, img, v: int) -> str:
        """Comment for a literal value: function, data symbol (+offset), string, or nothing."""
        if (v & ~1) in self.funcs and (v & 1 or self.funcs[v & ~1][0] == "A"):
            return self.func(v & ~1) + (" (Thumb)" if v & 1 else " (ARM)")
        i = bisect.bisect_right(self.data_addrs, v) - 1
        if i >= 0 and v - self.data[i][0] < NEAR:
            a, n = self.data[i]
            return n if v == a else f"{n}+{v - a:#x}"
        if img.off(v) is not None and ROM_BASE <= v:
            n = codemap._cstring(img, v)
            if n:
                s = img.data[img.off(v):img.off(v) + n].split(b"\0")[0].decode("ascii", "replace")
                return '"' + (s if len(s) < 48 else s[:45] + "...") + '"'
        return ""

    def site(self, a: int, start: int) -> str:
        rows = self.sites.get(a) or self.sites.get(a | 1) or []
        if not rows or a == start:
            return ""
        r = rows[0]
        text = r.text.replace("`", "")
        return f"bible s{r.section}: {text[:70]}{'...' if len(text) > 70 else ''}"


# ===== listing =====

def _load(map_path, rom_path):
    cm = json.loads(Path(map_path).read_text(encoding="utf-8"))
    img = codemap.Image(Path(rom_path).read_bytes())
    if img.sha1 != cm["sha1"]:
        raise ValueError("codemap.json was made from another ROM: re-run codemap.py")
    funcs = {int(k, 16): v for k, v in cm["functions"].items()}
    return cm, img, funcs


def _resolve(arg: str, names: Names) -> int:
    if arg in symbols._BY_NAME:
        return symbols.addr(arg)
    if arg.startswith("sub_"):
        return int(arg[4:], 16)
    return int(arg, 16)


def _callers(img, funcs, target):
    out = []
    for s, (mode, size, extent) in funcs.items():
        if mode != "T":
            continue
        a = s
        while a < s + extent:
            sz, kind, t = codemap.thumb_flow(img, a)
            if kind == "bl" and t == target:
                out.append(s)
                break
            a += sz
    return sorted(set(out))


def listing(arg: str, map_path, rom_path) -> list:
    cm, img, funcs = _load(map_path, rom_path)
    names = Names(funcs)
    want = _resolve(arg, names)
    start = want if want in funcs else names.containing(want)
    if start is None:
        return [f"{want:#010x} is not inside any function in codemap.json"]
    mode, size, extent = funcs[start]
    body = codemap.explore(img, start, mode, funcs)
    callers = _callers(img, funcs, start)
    vts = [f"{symbols.name_of(int(b, 16)) or b}+{4 * ts.index(f'{start:#x}'):#x}"
           for b, ts in list(cm["vtables"].items()) + list(cm["lists"].items()) if f"{start:#x}" in ts]
    out = [f"; {names.func(start)}  {start:#010x}  {'ARM' if mode == 'A' else 'Thumb'}  size {size:#x}  "
           f"extent {extent:#x}",
           f"; callers ({len(callers)}): " + ", ".join(names.func(c) for c in callers[:12])
           + (" ..." if len(callers) > 12 else ""),
           f"; vtable slots ({len(vts)}): " + ", ".join(vts[:8]) + (" ..." if len(vts) > 8 else ""),
           f"; bible: {symbols.bible_tag(start) or 'no row names this start'}"]
    labels = {t for a, (s, m) in body.insns.items()
              for _, kind, t in [(codemap.thumb_flow if m == "T" else codemap.arm_flow)(img, a)]
              if kind in ("b", "bcc") and t in body.insns and t != start}
    pool = {lit for lit in body.lits if not any(lit in range(a, a + s) for a, (s, _) in body.insns.items())}
    rows = sorted(list(body.insns.items()) + [(p, (4, "pool")) for p in pool])
    prev = None
    for a, (s, m) in rows:
        if prev is not None and a > prev:
            out.append(f"  ; {a - prev:#x} bytes not in this body")
        prev = a + s
        if a in labels:
            out.append(f".L_{a:08x}:")
        raw = img.data[img.off(a):img.off(a) + s]
        if m == "pool":
            v = img.u32(a)
            text, note = f".word {v:#010x}", names.value(img, v)
        else:
            text = codemap.thumb_text(img, a) if m == "T" else codemap.arm_text(img, a)
            note = _note(img, names, body, a, m, text)
        site = names.site(a, start)
        note = "; ".join(x for x in (note, site) if x)
        mark = "  <==" if a == want and want != start else ""
        out.append(f"{a:08x}  {raw.hex():<8}  {text:<28}{(' ; ' + note) if note else ''}{mark}")
    return out


def _note(img, names, body, a, m, text) -> str:
    op = text.split(" ")[0]
    if op == "bl" or op.startswith("b") and op[1:] in codemap.COND + [""]:
        t = int(text.split(" ")[1].split(",")[0], 16)
        if op == "bl":
            note = names.func(t)
            via = _virtual(img, body, a) if note.startswith("call_via") else ""
            return f"{note} {via}".strip()
        return "" if t in body.insns else f"-> {names.func(t)}" if t in names.funcs else ""
    if "=" in text:
        return names.value(img, int(text.split("=")[1], 16))
    return ""


def _virtual(img, body, a) -> str:
    """`ldr rX,[rY,#n] ; add rX,rX,rY ; bl call_via_rX`: a base-relative virtual call through vtable +n."""
    if not (a - 4 in body.insns and a - 2 in body.insns):
        return ""
    h1, h2 = img.u16(a - 4), img.u16(a - 2)
    if h1 >> 11 == 0xD and h2 >> 9 == 0x0C:                # ldr rX,[rY,#n] ; add rX,rX,rY
        return f"(virtual +{((h1 >> 6) & 31) * 4:#x})"
    return ""


def refs(arg: str, map_path, rom_path) -> list:
    cm, img, funcs = _load(map_path, rom_path)
    names = Names(funcs)
    v = _resolve(arg, names)
    pool = set(cm["pool"])
    out = [f"; references to {v:#010x} {symbols.name_of(v) or ''}".rstrip()]
    pat, hits, i = struct.pack("<I", v), [], img.data.find(struct.pack("<I", v))
    while i >= 0:
        if i % 4 == 0:
            hits.append(ROM_BASE + i)
        i = img.data.find(pat, i + 1)
    code = [h for h in hits if h < cm["code_hi"]]
    data = [h for h in hits if h >= cm["code_hi"]]
    out.append(f"; {len(code)} word(s) in the code region, {len(data)} outside it")
    for h in code:
        users = []
        for x in range(max(ROM_BASE, h - 1024), h, 2):
            hw = img.u16(x)
            if hw >> 11 == 9 and ((x + 4) & ~3) + (hw & 0xFF) * 4 == h:
                s = names.containing(x)
                users.append(f"{names.func(s)}+{x - s:#x} ({x:#010x})" if s is not None else f"{x:#010x}")
        kind = "pool" if h in pool else "word"
        out.append(f"  rom:{h - ROM_BASE:#x}  {kind}  ldr by: {', '.join(users) or 'none found'}")
    for h in data[:40]:
        out.append(f"  rom:{h - ROM_BASE:#x}  data word")
    if len(data) > 40:
        out.append(f"  ... {len(data) - 40} more")
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--refs", action="store_true")
    ap.add_argument("--map", default=str(codemap.OUT_DIR / "codemap.json"))
    ap.add_argument("--rom", default=str(codemap.ROMS / codemap.GAMES["usa"]))
    a = ap.parse_args(argv)
    print("\n".join((refs if a.refs else listing)(a.target, a.map, a.rom)))


if __name__ == "__main__":
    main(sys.argv[1:])
