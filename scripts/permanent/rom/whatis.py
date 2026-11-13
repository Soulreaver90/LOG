r"""
whatis.py - What this project already knows about an address, a RAM word, a function or a term.

Usage:   (from scripts\permanent) py -3.14 -P rom\whatis.py <query> [options]
         <query>   rom:0x409368 | 0x08409368 | 0x0800A680 | 0x03001FA8 | sub_0800a680 | map_table
                   | set:56 | flag:195 | pal:88 | char:gohan (a bible tag, matched whole) | B0001 (a
                   bible row id, matched whole against the Id cell) | free text
         --stride N --count M   shape C: the exact extent of the structure that starts at the address
         --span BYTES           shape C: the extent when no stride is known
         --rom PATH             the ROM the three shapes scan (default the base USA ROM)
         --no-refs              print the written sources only, and skip the ROM scan
         --limit N              rows per source (default 12; 0 prints every row)
Prints:  one block per written source (bible, our symbol table, RAM ledger, code index, function
         bounds, generated .s, our own modules), then the three reference shapes with their own
         counts, then a verdict. A source with no hit prints "the search returned nothing" and its
         path, never "it does not exist".
API:     answer(query, **opts) -> [lines]; shapes(gba, rom_bytes, span, stride, count, declared) -> Shapes.
Rules:   READ ONLY. It never writes a ROM and never writes docs\RE-BIBLE.md. The bible rows come from
         disasm\symbols.bible_rows(), so there is one bible parser in the project, not two.
         A bible hit is cited by its id (`B0001`), never by its line number: a merge moves every line
         below its insert point, so a line number names a different fact the next day.
         Three shapes, reported apart, because a one-shape sweep missed the 4th map table literal
         rom:0x195C on 2026-11-05: a pointer into the MIDDLE of a table never holds the table's base.
         Shape C counts the word one past the end apart, because a loop bound that names the first
         byte AFTER a table is a real reference that no base-keyed shape and no inside-range shape
         can see. Shape C needs an extent. A declared one earns a verdict; a guessed one says so,
         and a RAM word with no extent skips shape C rather than calling every global in the next
         4 KB a hit. A BL caller is a fourth shape this tool does not run: use disasm\listing.py,
         which also gives the annotated instruction listing of one function.
         The text search over the bible reads the bare file-offset form too, so a row that uses the
         same value as a count or a size can match. Read the row, do not count it.
"""
import argparse
import csv
import json
import re
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent                   # scripts\permanent\rom
sys.path.insert(0, str(HERE.parent))                     # py -P keeps the script folder off sys.path
import log_paths                                          # noqa: E402
sys.path.insert(0, str(log_paths.DISASM))
import symbols                                            # noqa: E402

ROM_BASE = 0x08000000
ROM_END = 0x0A000000
RAM_LO = 0x02000000                                      # a bare value below this is read as a file offset
CODE_HI_FALLBACK = 0x28724                               # rom offset; used when codemap.json cannot be read
DEFAULT_SPAN = 0x1000                                    # shape C extent when no stride and count are given
BASE_ROM = log_paths.BASE_ROM

RAM_LEDGER = log_paths.DISASM_REPO_DOCS / "RAM_LEDGER.csv"
CODE_INDEX = log_paths.DISASM_REPO_DOCS / "CODE_INDEX.md"
FUNCTION_BOUNDS = log_paths.DISASM_REPO_BOUNDS / "FUNCTION_BOUNDS.csv"
FUNCTION_ENDS = log_paths.DISASM_REPO_BOUNDS / "FUNCTION_ENDS.csv"
# The DISASM repo's own build\code, never the gnu clone's. The gnu copy is a measured stale tree:
# 1333 files against 1476, 154 missing starts, and 29 shared starts whose bodies differ. Pointing a
# lookup tool there hands the reader a body that may belong to a different function. See CLAUDE.md.
GENERATED_CODE = log_paths.DISASM_REPO / "build" / "code"
MODULES = [log_paths.PATCHES,
           log_paths.SCENE / "scene_lib.py"]

SOURCES = [("bible", log_paths.BIBLE),
           ("our symbol table", log_paths.DISASM / "symbols.py"), ("RAM ledger", RAM_LEDGER),
           ("code index", CODE_INDEX), ("function bounds", FUNCTION_BOUNDS),
           ("generated assembly", GENERATED_CODE), ("our modules", MODULES[0])]


# ===== the query =====

class Query:
    """kind is "rom", "ram" or "text". gba is the GBA address for the first two, else None."""

    def __init__(self, raw: str, gba=None, kind="text", note=""):
        self.raw, self.gba, self.kind, self.note = raw, gba, kind, note

    @property
    def off(self):
        return None if self.gba is None or not ROM_BASE <= self.gba < ROM_END else self.gba - ROM_BASE

    def needles(self) -> list:
        """Every written form of this address. Several shapes, because one shape misses rows."""
        if self.gba is None:
            return [self.raw]
        a = self.gba
        out = [f"0x{a:08X}", f"0x{a:X}", f"0x{a | 1:08X}", f"sub_{a:08x}", f"loc_{a:08x}", f"sub_{a | 1:08x}"]
        if self.off is not None:
            out += [f"rom:0x{self.off:X}", f"0x{self.off:X}", f"0x{self.off:08X}"]
        return sorted(set(out), key=len, reverse=True)

    def pattern(self):
        if self.kind == "tag":                           # set:5 must not match set:56
            return re.compile(re.escape(self.raw) + r"(?![0-9A-Za-z_])", re.IGNORECASE)
        if self.gba is None:                             # free text: a plain substring, no hex boundary
            return re.compile(re.escape(self.raw), re.IGNORECASE)
        body = "|".join(re.escape(n) for n in self.needles())
        # The right boundary stops rom:0x195 matching rom:0x195C.
        return re.compile(rf"(?<![0-9A-Za-z_])(?:{body})(?![0-9A-Fa-f])", re.IGNORECASE)


def parse(raw: str) -> Query:
    """A prefixed hex value, a sub_/loc_ label or a known name becomes an address. Anything else is text."""
    s = raw.strip()
    low = s.lower()
    if low.startswith("rom:0x"):
        return Query(s, ROM_BASE + int(low[6:], 16), "rom")
    # A bible row id is matched whole against the Id cell. A substring search would not do: measured
    # 2026-11-07, 13 of the 2030 ids also appear inside another row's hex byte string.
    if re.fullmatch(r"b\d{4}", low):
        return Query(s.upper(), None, "id")
    if re.fullmatch(r"(set|flag|pal|char|game):[0-9a-z_]+", low):     # a bible tag shape, section 1
        return Query(s, None, "tag")
    if re.fullmatch(r"(sub|loc)_[0-9a-f]{8}", low):
        return _by_value(s, int(low[4:], 16))
    if re.fullmatch(r"0x[0-9a-f]+", low):
        return _by_value(s, int(low, 16))
    named = _named_address(s)
    if named is not None:
        a, where = named
        q = _by_value(s, a)
        q.note = f"the name {s} resolves to {a:#010x} ({where})"
        return q
    return Query(s)


def _by_value(raw: str, v: int) -> Query:
    # Strip the Thumb bit only inside the code region. An odd data address such as the script byte
    # rom:0x3E9DFB is not a Thumb pointer, and rounding it down loses the row the reader asked for.
    if ROM_BASE <= v < ROM_END and v - ROM_BASE < code_hi():
        v &= ~1
    if ROM_BASE <= v < ROM_END:
        return Query(raw, v, "rom")
    if RAM_LO <= v < ROM_BASE:
        return Query(raw, v, "ram")
    if v < RAM_LO:
        return Query(raw, ROM_BASE + v, "rom", f"read as the file offset rom:{v:#x}")
    return Query(raw, v, "ram", "outside ROM and the usual RAM; searched as a bare value")


def _named_address(name: str):
    if name in symbols._BY_NAME:
        return symbols.addr(name), "disasm\\symbols.py"
    for row in _ram_ledger():
        if row["new"] == name:
            return int(row["address"], 16), "RAM_LEDGER.csv"
    for a, (fn, _) in _code_index().items():
        if fn == name:
            return a, "CODE_INDEX.md"
    return None


# ===== the written sources =====

def _rows(path: Path) -> list:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


_CACHE = {}


def _cached(key, make):
    if key not in _CACHE:
        try:
            _CACHE[key] = make()
        except (OSError, ValueError, KeyError) as exc:
            _CACHE[key] = exc
    return _CACHE[key]


def _ram_ledger():
    v = _cached("ram", lambda: _rows(RAM_LEDGER))
    return [] if isinstance(v, OSError) else v


def _code_index() -> dict:
    def make():
        out = {}
        for line in CODE_INDEX.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\|\s*`([^`]+)`\s*\|\s*`0x([0-9a-f]{8})`\s*\|\s*`?([^`|]+)`?\s*\|", line)
            if m:
                out[int(m.group(2), 16)] = (m.group(1), m.group(3).strip())
        return out
    v = _cached("index", make)
    return {} if isinstance(v, OSError) else v


def _bounds():
    def make():
        ends = sorted((int(r["address"], 16), int(r["end"], 16), r["mode"], r["reason"])
                      for r in _rows(FUNCTION_ENDS))
        roles = {int(r["address"], 16): (r["role"], r["evidence"]) for r in _rows(FUNCTION_BOUNDS)}
        return ends, roles
    v = _cached("bounds", make)
    return ([], {}) if isinstance(v, OSError) else v


def containing(a: int):
    """(start, end, mode, reason, role, evidence) of the function that holds a, or None.

    FUNCTION_ENDS.csv is the first shape and carries a real end. It covers 1409 of the 3431
    FUNCTION_BOUNDS.csv rows, so a site in the gap falls back to the nearest start above which
    it sits, with end 0 to say the end is not recorded.
    """
    ends, roles = _bounds()
    hit = None
    for start, end, mode, reason in ends:                # sorted; a linear walk is fast enough
        if start <= a < end:
            hit = (start, end, mode, reason) + roles.get(start, ("", ""))
        elif start > a:
            break
    if hit is not None:
        return hit
    if ROM_BASE <= a and a - ROM_BASE >= code_hi():      # data: no function reaches past the code region
        return None
    below = [s for s in roles if s <= a]
    if not below:
        return None
    start = max(below)
    role, evidence = roles[start]
    if role == "fragment" and evidence.startswith("0x"):
        start, (role, evidence) = int(evidence, 16), roles.get(int(evidence, 16), (role, evidence))
    return (start, 0, "?", "end not recorded", role, evidence)


def _bible_hits(q: Query) -> list:
    if q.kind == "id":                                   # whole-cell, never a substring
        return [row for row in symbols.bible_rows() if row.id == q.raw]
    pat = q.pattern()
    out = []
    for row in symbols.bible_rows():
        blob = " | ".join((row.text, row.tags, row.label, row.src))
        if pat.search(blob):
            out.append(row)
    return out


def _module_hits(q: Query) -> list:
    pat = q.pattern()
    files = []
    for m in MODULES:
        files += sorted(m.glob("*.py")) if m.is_dir() else [m]
    out = []
    for f in files:
        try:
            lines = f.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for n, line in enumerate(lines, 1):
            if pat.search(line):
                out.append((f, n, line.strip()))
    return out


# ===== the three reference shapes =====

class Shapes:
    def __init__(self):
        self.a_gba, self.a_thumb, self.a_off, self.b, self.c, self.c_end = [], [], [], [], [], []
        self.span = self.code_hi = 0
        self.stride = self.count = None
        self.declared = False                            # True when the caller gave shape C a real extent

    @property
    def a_all(self):
        return sorted(set(self.a_gba + self.a_thumb))


def code_hi() -> int:
    """The end of the code region, from the committed codemap snapshot when it can be read."""
    def make():
        return json.loads((log_paths.DISASM_DATA / "codemap.json")
                          .read_text(encoding="utf-8"))["code_hi"] - ROM_BASE
    v = _cached("codehi", make)
    return CODE_HI_FALLBACK if isinstance(v, (OSError, KeyError, ValueError)) else v


def shapes(gba: int, data: bytes, span, stride=None, count=None, declared=False) -> Shapes:
    """Shape A: words equal to the address. Shape B: the pc-relative loads. Shape C: words inside the span.

    span None skips shape C, and shape B then names only the loads of the address itself.
    """
    s = Shapes()
    span = span or 0
    s.span, s.code_hi, s.stride, s.count, s.declared = span, code_hi(), stride, count, declared
    words = memoryview(data).cast("I")
    off = gba - ROM_BASE if ROM_BASE <= gba < ROM_END else None
    for i, v in enumerate(words):
        if v == gba:
            s.a_gba.append(i * 4)
        elif v == gba | 1:                              # the Thumb pointer form a caller stores
            s.a_thumb.append(i * 4)
        elif off is not None and v == off:
            s.a_off.append(i * 4)
        elif gba < v < gba + span:                      # strictly inside: the base itself is shape A
            s.c.append((i * 4, v))
        elif span and v == gba + span:                  # one past the end: a loop bound or the next table
            s.c_end.append(i * 4)
    for a in range(0, s.code_hi - 1, 2):
        hw = struct.unpack_from("<H", data, a)[0]
        if hw >> 11 != 9:                               # 0x4800-0x4FFF: ldr Rd,[pc,#imm*4], any Rd
            continue
        lit = ((a + 4) & ~3) + (hw & 0xFF) * 4
        if lit + 4 > len(data):
            continue
        v = struct.unpack_from("<I", data, lit)[0]
        if v in (gba, gba | 1) or gba < v <= gba + span or (off is not None and v == off):
            s.b.append((a, lit, v))
    return s


def verdict(s: Shapes, gba: int) -> list:
    """Say plainly where the shapes disagree, because the disagreement is itself the finding."""
    out, a_all = [], s.a_all
    missed = [(o, v) for o, v in s.c if o < s.code_hi]       # shape C and shape A are disjoint by build
    orphan = [o for o in a_all if o < s.code_hi and not any(lit == o for _, lit, _ in s.b)]
    seen = set(a_all) | {o for o, _ in s.c} | set(s.c_end) | set(s.a_off)
    loose = [(a, lit) for a, lit, v in s.b if lit not in seen]
    if missed and s.declared:
        out.append(f"SHAPES DISAGREE: shape C found {len(missed)} code-region word(s) that shape A cannot see, "
                   f"because they point INTO the span, not at {gba:#010x}.")
        out += _entries(missed, gba, s)
        out.append("  Treat this as the finding. A scan for the base address alone would have reported "
                   f"{len(a_all)} references, not {len(a_all) + len(missed)}.")
    elif missed:
        out.append(f"SHAPE C ran on a GUESSED span of {s.span:#x} bytes and found {len(missed)} code-region "
                   "word(s) inside it. Each one is invisible to shape A.")
        out += _entries(missed, gba, s)
        out.append("  This is not yet a verdict. Give the real extent with --stride and --count, or --span, "
                   "and run it again.")
    if s.c_end:
        out.append(f"NOTE: {len(s.c_end)} word(s) hold {gba + s.span:#010x}, one past the end. A loop bound "
                   "or the next structure's base. No shape keyed on the base address can see it, and "
                   "shape C's own range ends one word short of it.")
        out.append("  " + ", ".join(f"rom:{o:#x}" for o in s.c_end[:8]))
    if orphan:
        out.append(f"NOTE: {len(orphan)} code-region word(s) equal to the address that no pc-relative load "
                   f"names: {', '.join(f'rom:{o:#x}' for o in orphan[:8])}. Each is data, or loaded another way.")
    if loose:
        out.append(f"BUG: {len(loose)} load site(s) whose literal is in neither shape A nor shape C. "
                   "Shape B cannot hit a word the other two miss; read the code before trusting this run.")
    if not out and not s.span:
        out.append("Shapes A and B agree: every load site names a word equal to the address. Shape C did "
                   "not run, so nothing here rules out a word pointing INTO a structure at this address.")
    elif not out:
        out.append("The three shapes agree: every code-region word shape C sees is equal to the address, "
                   "and every load site names one of them.")
    return out


def _entries(hits: list, gba: int, s: Shapes, cap=10) -> list:
    out = []
    for o, v in hits[:cap]:
        where = f" (entry {(v - gba) // s.stride}, +{(v - gba) % s.stride:#x})" if s.stride else ""
        out.append(f"  rom:{o:#x} holds {v:#010x} = base +{v - gba:#x}{where}")
    if len(hits) > cap:
        out.append(f"  ... {len(hits) - cap} more")
    return out


# ===== the answer =====

def answer(query: str, rom_path=None, span=None, stride=None, count=None,
           refs=True, limit=12) -> list:
    q = parse(query)
    cut = (lambda xs: xs) if not limit else (lambda xs: xs[:limit])
    out = [f"== whatis {q.raw}", f"   read as: {q.kind} {'' if q.gba is None else f'{q.gba:#010x}'}"
           + (f" (rom:{q.off:#x})" if q.off is not None else "")]
    if q.note:
        out.append(f"   note: {q.note}")
    out.append("")
    found = []

    rows = _bible_hits(q)
    out.append(f"-- bible: {len(rows)} row(s) in {_rel(log_paths.BIBLE)}")
    if rows:
        found.append("bible")
        for r in cut(rows):
            out.append(f"  {r.id or 'NO ID'}  [s{r.section} {r.label} {r.src}] {r.tags}  (line {r.line_no})")
            out.append(f"    {_trim(r.text)}")
        if limit and len(rows) > limit:
            out.append(f"  ... {len(rows) - limit} more row(s); pass --limit 0 for all")
        out.append("  Cite the id, not the line number: the line number moves on every merge. "
                   "`whatis B0001` finds the row again.")
    else:
        out.append("  the search returned nothing")
    out.append("")

    out += _symbol_block(q, found) + [""] + _ram_block(q, found) + [""] \
        + _code_block(q, found) + [""] + _module_block(q, found, cut) + [""]

    if q.gba is None:
        out.append("-- references: not searched. The three shapes need an address, and this query is text.")
    elif not refs:
        out.append("-- references: skipped (--no-refs)")
    else:
        out += _ref_block(q, rom_path or BASE_ROM, span, stride, count)

    if not found:
        out += ["", f"Nothing written about {q.raw}: the search returned nothing in any source below.",
                "Sources searched:"]
        for name, path in SOURCES:
            out.append(f"  {name}: {path}")
        out.append("That is the state of our notes, not a statement that the thing does not exist.")
    return out


def _symbol_block(q: Query, found: list) -> list:
    """Our own name for the address, and the conflict when another source names it differently."""
    out = [f"-- our symbol table: {_rel(log_paths.DISASM / 'symbols.py')}"]
    if q.gba is None:
        names = [n for n in symbols._BY_NAME if q.raw.lower() in n.lower()]
        return out + ([f"  names holding {q.raw}: " + ", ".join(sorted(names)[:12])] if names
                      else ["  the search returned nothing in its names"])
    mine = symbols.name_of(q.gba) or symbols.name_of(q.gba | 1)
    if mine:
        found.append("our symbol table")
        out.append(f"  {q.gba:#010x} is named {mine} (kind {symbols._KIND[symbols.addr(mine)]})")
    else:
        out.append(f"  the search returned nothing: no symbol names {q.gba:#010x}")
    # The disasm repo names functions in PascalCase and we use snake_case, so 61 of our symbols
    # already read differently there. That is a convention gap, not a contradiction, so this line
    # is neutral: it shows both names and lets the reader judge.
    theirs = [(r["new"], "RAM_LEDGER.csv") for r in _ram_ledger() if int(r["address"], 16) == q.gba]
    theirs += [(n, "CODE_INDEX.md") for a, (n, _) in _code_index().items()
               if a == q.gba and not n.startswith("sub_")]
    for name, src in theirs:
        if name != mine:
            out.append(f"  also named {name} ({src}). Open the handler before you trust either name.")
    return out


def _ram_block(q: Query, found: list) -> list:
    rows = _ram_ledger()
    out = [f"-- named RAM words: {_rel(RAM_LEDGER)}"]
    if not rows:
        return out + ["  could not read the file; the disassembly repo may be missing"]
    hit = [r for r in rows if q.gba is not None and int(r["address"], 16) == q.gba] \
        or [r for r in rows if q.gba is None and q.raw.lower() in r["new"].lower()]
    if not hit:
        return out + [f"  the search returned nothing in its {len(rows)} row(s)"]
    found.append("RAM ledger")
    for r in hit:
        out.append(f"  {r['old']}  {r['new']}  [{r['evidence_class']}]")
        out.append(f"    {_trim(r['evidence'])}")
    return out


def _code_block(q: Query, found: list) -> list:
    out = [f"-- function index and bounds: {_rel(CODE_INDEX)}"]
    if q.gba is None:
        return out + ["  not searched: this query is text, and both files are keyed by address"]
    idx = _code_index()
    if not idx:
        out.append("  could not read CODE_INDEX.md; the disassembly repo may be missing")
    elif q.gba in idx:
        found.append("code index")
        name, fname = idx[q.gba]
        out.append(f"  {q.gba:#010x} is the start of {name}, file {fname}")
        out.append(f"    {_sfile(fname, q.gba)}")
    else:
        out.append(f"  the search returned nothing: {q.gba:#010x} is not a function start in its "
                   f"{len(idx)} row(s)")
    hold = containing(q.gba)
    if hold is None:
        out.append(f"  no function in {_rel(FUNCTION_ENDS)} contains {q.gba:#010x}")
    else:
        start, end, mode, reason, role, evidence = hold
        found.append("function bounds")
        name = idx.get(start, (f"sub_{start:08x}", ""))[0]
        out.append(f"  contained by {name} {start:#010x}-{end:#010x} ({mode}, end {reason or 'census'}), "
                   f"+{q.gba - start:#x} in")
        out.append(f"    role {role or 'unknown'} ({evidence or 'no evidence column'}), "
                   f"file {_sfile(idx.get(start, ('', 'none'))[1], start)}")
    return out


def _sfile(fname: str, gba=None) -> str:
    """Two shapes: the name CODE_INDEX gives, then the address name the emitter writes."""
    if not fname or fname == "none":
        return "no generated .s file (the boot transcription or a container carries this start)"
    p = GENERATED_CODE / fname
    if p.exists():
        return str(p)
    alt = GENERATED_CODE / f"code_{gba:08x}.s" if gba is not None else None
    if alt is not None and alt.exists():
        return f"{alt}  (on disk under the address name; CODE_INDEX names {fname})"
    return f"{p}  (NOT on disk under either name)"


def _module_block(q: Query, found: list, cut) -> list:
    hits = _module_hits(q)
    out = [f"-- our own modules: {_rel(MODULES[0])}\\*.py and {_rel(MODULES[1])}",
           f"  {len(hits)} line(s)" if hits else "  the search returned nothing"]
    if hits:
        found.append("our modules")
        for f, n, line in cut(hits):
            out.append(f"  {f.name}:{n}  {_trim(line)}")
        if len(hits) > len(cut(hits)):
            out.append(f"  ... {len(hits) - len(cut(hits))} more line(s)")
    out.append("  A module that computes an address (MAP_TABLE + 3 * 56) cannot show in a static search.")
    return out


def _span_for(q: Query, span, stride, count):
    """(span, why, declared). Shape C needs an extent. A declared extent earns a verdict; a guess does not.

    span None means shape C is skipped, because a guessed span over RAM reports every other global
    as a hit and buries the one that matters.
    """
    if stride and count:
        return stride * count, f"({count} entries of {stride} bytes, declared)", True
    if span:
        return span, "(--span, declared)", True
    hold = containing(q.gba)
    if hold and hold[0] == q.gba and hold[1] > hold[0]:
        return hold[1] - hold[0], "(this function's own body)", True
    if q.kind == "ram":
        return None, "", False
    return DEFAULT_SPAN, "(GUESSED; pass --stride and --count for a table, or --span)", False


def _ref_block(q: Query, rom_path, span, stride, count) -> list:
    span, why, declared = _span_for(q, span, stride, count)
    try:
        data = Path(rom_path).read_bytes()
    except OSError as exc:
        return [f"-- references: could not read {rom_path} ({exc})"]
    s = shapes(q.gba, data, span, stride, count, declared)
    out = [f"-- references in {Path(rom_path).name}, three shapes, counted apart",
           f"   shape C span {span:#x} bytes {why}" if span else
           "   shape C not run: a RAM word has no extent on disk. Pass --span, or --stride and --count."]
    out.append(f"  shape A (aligned words equal to {q.gba:#010x}): {len(s.a_gba)}")
    for o in s.a_gba[:20]:
        out.append(f"    rom:{o:#x}{'  code region' if o < s.code_hi else '  data'}")
    if len(s.a_gba) > 20:
        out.append(f"    ... {len(s.a_gba) - 20} more")
    out.append(f"  shape A (words equal to the Thumb pointer {q.gba | 1:#010x}): {len(s.a_thumb)}")
    for o in s.a_thumb[:12]:
        out.append(f"    rom:{o:#x}{'  code region' if o < s.code_hi else '  data'}")
    if len(s.a_thumb) > 12:
        out.append(f"    ... {len(s.a_thumb) - 12} more")
    if q.off is not None:
        out.append(f"  shape A (words equal to the bare offset {q.off:#x}): {len(s.a_off)}"
                   + (f"  {', '.join(f'rom:{o:#x}' for o in s.a_off[:8])}" if s.a_off else ""))
    out.append(f"  shape B (pc-relative loads in rom:0x0-rom:{s.code_hi:#x}): {len(s.b)} site(s)")
    for a, lit, v in s.b[:20]:
        hold = containing(ROM_BASE + a)
        where = _code_index().get(hold[0], (f"sub_{hold[0]:08x}", ""))[0] + f"+{ROM_BASE + a - hold[0]:#x}" \
            if hold else "no function"
        out.append(f"    ldr at rom:{a:#x} ({where}) reads rom:{lit:#x} = {v:#010x}")
    if len(s.b) > 20:
        out.append(f"    ... {len(s.b) - 20} more")
    if q.gba - ROM_BASE < s.code_hi and ROM_BASE <= q.gba:
        out.append("  (a BL caller is a fourth shape this tool does not run: use disasm\\listing.py)")
    if span:
        code_c = [(o, v) for o, v in s.c if o < s.code_hi]
        out.append(f"  shape C (words landing INSIDE {q.gba:#010x}-{q.gba + span:#010x}): {len(s.c)}, "
                   f"{len(code_c)} in the code region")
        out += ["  " + line for line in _entries(code_c, q.gba, s, cap=20)]
        if len(s.c) - len(code_c):
            out.append(f"    {len(s.c) - len(code_c)} further word(s) in the data region, first: "
                       + ", ".join(f"rom:{o:#x}" for o, _ in s.c[len(code_c):][:6]))
        out.append(f"  shape C, one past the end (words equal to {q.gba + span:#010x}): {len(s.c_end)}"
                   + (f"  {', '.join(f'rom:{o:#x}' for o in s.c_end[:8])}" if s.c_end else ""))
    return out + [""] + verdict(s, q.gba)


def _trim(text: str, width=150) -> str:
    text = " ".join(text.split())
    return text if len(text) <= width else text[:width - 3] + "..."


def _rel(p: Path) -> str:
    try:
        return str(p.relative_to(log_paths.ROOT))
    except ValueError:
        return str(p)


def main(argv):
    ap = argparse.ArgumentParser(description="What this project already knows about an address or a term.")
    ap.add_argument("query")
    ap.add_argument("--rom", default=str(BASE_ROM))
    ap.add_argument("--span", type=lambda x: int(x, 0))
    ap.add_argument("--stride", type=lambda x: int(x, 0))
    ap.add_argument("--count", type=lambda x: int(x, 0))
    ap.add_argument("--no-refs", dest="refs", action="store_false")
    ap.add_argument("--limit", type=int, default=12)
    a = ap.parse_args(argv)
    print("\n".join(answer(a.query, a.rom, a.span, a.stride, a.count, a.refs, a.limit)))


if __name__ == "__main__":
    main(sys.argv[1:])
