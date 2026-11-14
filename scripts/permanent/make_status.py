r"""Regenerate docs\status.md, the TECHNICAL tracker: what is built, where it ships and what it is.

Why it is generated: a hand kept tracker rots, and a rotted tracker is worse than none. On 2026-11-13
the owner asked where the project stood and the whole future Trunks line was missed, because the only
record was 2,000 lines of dated ledger narrative.

What it answers: which modules exist, what each one does, which build list carries it, whether it has
a test, and the newest ROM built from each line with its SHA-1. It does NOT answer what the player
sees: that is docs\game-status.md, which is written by hand because only the owner knows the story.

It never builds and never runs the suite. Every hash here is the LAST RECORDED build from
docs\build-log.md, not a value measured now, and the page says so on its face.

Run: py -3.14 -P scripts\permanent\make_status.py
"""
import ast
import datetime as dt
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))  # scripts\permanent: -P omits the script folder
import log_paths  # noqa: E402

GOLDEN, DEV, CORE = "build_list.txt", "build_list_dev.txt", "build_list_core.txt"
BUILD_LINE = re.compile(r"^- (\d{4}-\d\d-\d\d \d\d:\d\d) build (\S+\.gba) patches=(\S+) sha1=([0-9a-f]{40})")
CODE_ROW = re.compile(r"^\|\s*([A-Z]{3}-\d+)\s*\|([^|]*)\|$")
MODULE_NAME = re.compile(r"^[a-z][a-z0-9_]*$")   # anything else is reported, never dropped
OUT = log_paths.DOCS / "status.md"
GAME = log_paths.DOCS / "game-status.md"


def modules_of(list_path: Path) -> list:
    """The patch modules a build list applies, in order, following its include lines."""
    out = []
    for raw in list_path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#")[0].strip()
        if not line:
            continue
        if line.startswith("include "):
            out += modules_of(list_path.parent / line.split(maxsplit=1)[1].strip())
        else:
            out.append(line)
    return out


def purpose(module: str) -> str:
    """The module's own one line summary: its docstring, minus the file name it starts with."""
    path = log_paths.PATCHES / f"{module}.py"
    if not path.is_file():
        return "NO MODULE FILE ON DISK"
    doc = ast.get_docstring(ast.parse(path.read_text(encoding="utf-8"))) or ""
    head = " ".join(doc.split("\n\n")[0].split())
    head = re.sub(rf"^{re.escape(module)}\.py\s*-\s*", "", head)
    head = re.sub(r"^(Trial )?[Pp]atch:\s*", "", head)
    return head or "no docstring"


def feature_codes() -> dict:
    """{module: [codes]} from the Reference table of game-status.md, the one place the mapping lives.

    A row with no module is a feature nothing builds yet, which is a legitimate state and is reported
    rather than treated as an error.

    The cell is matched loosely and each name is validated here, because an earlier version accepted
    only [a-z0-9_, ]: one stray bracket made the WHOLE row fail to match, so that code vanished from
    every health line at once rather than being reported. A guard against gaps must not have one.
    """
    out, empty, bad = {}, [], []
    for line in GAME.read_text(encoding="utf-8").splitlines():
        m = CODE_ROW.match(line.strip())
        if not m:
            continue
        code, names = m.group(1), [n.strip() for n in m.group(2).split(",") if n.strip()]
        if not names:
            empty.append(code)
        for name in names:
            if MODULE_NAME.match(name):
                out.setdefault(name, []).append(code)
            else:
                bad.append(f"{code} -> {name!r}")
    out["__unbuilt__"] = empty
    out["__malformed__"] = bad
    return out


def builds() -> dict:
    """{module tuple: (when, rom, sha1)} for the NEWEST recorded build of each module set."""
    out = {}
    for line in log_paths.BUILD_LOG.read_text(encoding="utf-8").splitlines():
        m = BUILD_LINE.match(line.strip())
        if m:
            when, rom, patches, sha = m.groups()
            out[tuple(patches.split(","))] = (when, rom, sha)
    return out


def rows_for_lines(recorded: dict) -> list:
    """One row per build list: its extra modules, and the newest ROM recorded for exactly that set.

    A trial list whose modules now equal a master's is SPENT: its work shipped and nothing is left in
    it. Saying so beats naming the master's ROM, which would read as a live trial ROM of its own.
    """
    core = modules_of(log_paths.BUILD_LISTS / CORE)
    masters = {tuple(modules_of(log_paths.BUILD_LISTS / GOLDEN)): "golden",
               tuple(modules_of(log_paths.BUILD_LISTS / DEV)): "dev"}
    rows = []
    for path in sorted(log_paths.BUILD_LISTS.glob("build_list*.txt")):
        if path.name == CORE:
            continue
        mods = modules_of(path)
        extra = [m for m in mods if m not in core] or ["(core only)"]
        if path.name not in (GOLDEN, DEV) and tuple(mods) in masters:
            rows.append((path.name, ", ".join(f"`{m}`" for m in extra),
                         f"SPENT: same modules as the {masters[tuple(mods)]} master", "", ""))
            continue
        when, rom, sha = recorded.get(tuple(mods), ("", "never built", ""))
        rows.append((path.name, ", ".join(f"`{m}`" for m in extra), rom, sha[:8], when))
    return rows


def main() -> None:
    core = modules_of(log_paths.BUILD_LISTS / CORE)
    golden, dev = modules_of(log_paths.BUILD_LISTS / GOLDEN), modules_of(log_paths.BUILD_LISTS / DEV)
    recorded = builds()
    every = {}
    for path in sorted(log_paths.BUILD_LISTS.glob("build_list*.txt")):
        for module in modules_of(path):
            every.setdefault(module, set()).add(path.name)
    for path in sorted(log_paths.PATCHES.glob("*.py")):
        every.setdefault(path.stem, set())

    out = ["# LOG technical status", "",
           f"Generated by `scripts\\permanent\\make_status.py` on {dt.date.today():%Y-%m-%d}. "
           "Do not edit by hand: run the tool.", "",
           "Every SHA-1 here is the **last recorded** build from the build log, not a value measured "
           "now. Rebuild to confirm one.", "",
           "What the PLAYER sees is in [game-status.md](game-status.md). This page is the machinery.",
           "", "---", "", "## The two masters", "",
           "| Master | List | Modules | Last recorded SHA-1 |", "|---|---|---:|---|"]
    for name, path_name, mods in (("Golden", GOLDEN, golden), ("Dev", DEV, dev)):
        _, _, sha = recorded.get(tuple(mods), ("", "", ""))
        out.append(f"| {name} | `{path_name}` | {len(mods)} | `{sha[:8] or 'not in the build log'}` |")

    out += ["", f"Both include `{CORE}`, which is {len(core)} modules.", "",
            "---", "", "## Lines of work", "",
            "One row per build list. **Extra modules** are what it adds on top of the core list.", "",
            "| Build list | Extra modules | Newest ROM | SHA-1 | Built |", "|---|---|---|---|---|"]
    for name, extra, rom, sha, when in rows_for_lines(recorded):
        out.append(f"| `{name}` | {extra} | `{rom}` | `{sha}` | {when} |")

    codes = feature_codes()
    unbuilt = codes.pop("__unbuilt__")
    malformed = codes.pop("__malformed__")
    out += ["", "---", "", "## Every module", "",
            "**Code** is the game-status.md item this module builds. `golden` and `dev` mean the module "
            "ships in that master. A module with no list is written but wired into nothing.", "",
            "| Module | Code | What it does | Ships in | Test |", "|---|---|---|---|---|"]
    for module in sorted(every):
        where = []
        if module in golden:
            where.append("**golden**")
        if module in dev:
            where.append("**dev**")
        trials = sorted(n for n in every[module] if n.startswith("build_list_trial"))
        where += [f"`{n.replace('build_list_trial_', '').replace('.txt', '')}`" for n in trials]
        test = log_paths.TESTS / f"test_{module}.py"
        out.append(f"| `{module}` | {', '.join(codes.get(module, [])) or '-'} | {purpose(module)} | "
                   f"{', '.join(where) or 'NOTHING'} | {'yes' if test.is_file() else '**none**'} |")

    named = {m for m in codes if m not in every}
    orphan = [m for m in sorted(every) if m not in codes and not m.startswith("_")]
    out += ["", "---", "", "## Cross-reference health", "",
            "Checked on every run, against the Reference table of "
            "[game-status.md](game-status.md).", ""]
    out.append(f"- **Features with no module yet:** {', '.join(unbuilt) or 'none'}")
    out.append(f"- **Codes naming a module that does not exist:** {', '.join(sorted(named)) or 'none'}"
               + ("  <- FIX THIS" if named else ""))
    out.append(f"- **Modules no feature claims:** {', '.join(f'`{m}`' for m in orphan) or 'none'}")
    out.append(f"- **Reference rows that are not a module name:** {', '.join(malformed) or 'none'}"
               + ("  <- FIX THIS" if malformed else ""))
    out.append("")
    OUT.write_text("\n".join(out), encoding="utf-8", newline="\r\n")
    print(f"wrote {OUT} ({len(every)} modules, {len(rows_for_lines(recorded))} build lists)")


if __name__ == "__main__":
    main()
