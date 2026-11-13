r"""
compare_code_trees.py - Prove how far the gnu clone's generated assembly has fallen behind the disasm repo.

Why:     CLAUDE.md sends every session to a generated `.s` file to read a handler with no build. Two
         trees hold those files and they are NOT the same tree. On 2026-11-05 the gnu copy was missing
         154 function starts and bundled code the disasm repo had since split out, so a read there can
         attribute a callee to the wrong function, and a miss there is not proof a function is absent.
Usage:   py -3.14 -P scripts\permanent\disasm\compare_code_trees.py [summary | reads 0x0800a784 ...]
         summary  counts, the starts each tree alone has, and every shared start whose body differs
         reads    one line per address: safe to have read, missing, or bodies differ
Reads:   GitHub\legacyofgoku2-disasm\build\code and GitHub\legacyofgoku2-gnu\build\code
Writes:  nothing.
Rules:   A function start is the first `|loc_XXXXXXXX|` label in the file, which both naming styles
         carry. Label lines are dropped before a body comparison, so a rename never reads as a change.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P omits the script folder
import log_paths  # noqa: E402

# ===== the two trees =====
DISASM = log_paths.DISASM_REPO_CODE
GNU = log_paths.GNU_REPO_CODE

LOC = re.compile(r"\|loc_([0-9A-Fa-f]{8})\|")


# ===== reading =====
def starts(folder: Path) -> dict:
    """Map each function start in the folder to its file. Files with no loc label are skipped."""
    out = {}
    for f in sorted(folder.glob("*.s")):
        m = LOC.search(f.read_text(encoding="utf-8", errors="replace")[:600])
        if m:
            out.setdefault(int(m.group(1), 16), f)
    return out


def body(path: Path) -> list:
    """The file's instruction lines, with every label line dropped."""
    return [l for l in path.read_text(encoding="utf-8", errors="replace").splitlines()
            if not l.startswith("|")]


# ===== reports =====
def summary() -> int:
    good, stale = starts(DISASM), starts(GNU)
    shared = sorted(set(good) & set(stale))
    differ = [a for a in shared if body(stale[a]) != body(good[a])]
    print(f"disasm {len(list(DISASM.glob('*.s')))} files, {len(good)} starts")
    print(f"gnu    {len(list(GNU.glob('*.s')))} files, {len(stale)} starts")
    print(f"in the disasm tree only: {len(sorted(set(good) - set(stale)))}")
    print(f"in the gnu tree only:    {len(sorted(set(stale) - set(good)))}")
    print(f"shared starts {len(shared)}, bodies differ in {len(differ)}:")
    for a in differ:
        print(f"  0x{a:08x}  gnu {len(body(stale[a]))} lines, disasm {len(body(good[a]))}")
    return 0


def reads(addresses: list) -> int:
    good, stale = starts(DISASM), starts(GNU)
    for raw in addresses:
        a = int(raw, 16)
        g, d = stale.get(a), good.get(a)
        if g is None and d is None:
            verdict = "not a function start in either tree"
        elif g is None:
            verdict = f"MISSING from the gnu tree, disasm has {d.name}"
        elif d is None:
            verdict = f"gnu only ({g.name}), the disasm tree starts no function here"
        elif body(g) == body(d):
            verdict = "same body, safe to have read"
        else:
            verdict = f"BODIES DIFFER: gnu {len(body(g))} lines, disasm {len(body(d))}"
        print(f"0x{a:08x}  {verdict}")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "reads":
        sys.exit(reads(args[1:]))
    sys.exit(summary())
