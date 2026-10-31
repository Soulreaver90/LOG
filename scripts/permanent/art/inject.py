r"""
inject.py - One command to add or replace a dialog portrait or an OBJ palette entry, then build the next ROM.

Usage:   py -3 -P scripts\permanent\art\inject.py portrait <id> <png> [--snap] [--note TEXT]
         py -3 -P scripts\permanent\art\inject.py palette <index> <r,g,b>
         py -3 -P scripts\permanent\art\inject.py check <png> [id] [--snap]
         py -3 -P scripts\permanent\art\inject.py list
Does:    portrait/palette: check the input, stage the table change in memory, build the next
         builds\log2_poc_rN.gba from build_list_dev.txt, verify it (every table portrait and palette entry reads
         back; the diff from the previous build touches only art sites), then write the art copy and the table,
         the ROM, copies of the latest .sav and .ss* under the new name, and one line in docs\build-log.md.
         Nothing is written when a check fails. Exit code 0 = done or valid, 1 = refused.
Rules:   Never overwrites a ROM, .sav or state file (exclusive create). Refuses to build with a LOG_* environment
         variable set (the build follows build_list_dev.txt only: the working ROM carries the gi art).
         Art rules: art_tables.py. Layout: art_inject.py.
"""
import argparse
import hashlib
import os
import re
import shutil
import struct
import sys
import time
from bisect import bisect_right
from collections import namedtuple
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P and -I omit the script folder

from PIL import Image  # noqa: E402

from art import art_tables as at  # noqa: E402
import log2_build  # noqa: E402
import log_paths  # noqa: E402
from patches import art_inject  # noqa: E402
from rom.webfoot_decompress import ROM_BASE  # noqa: E402

# ===== CONFIG =====
ROM_NAME = re.compile(r"^log2_poc_r(\d+)\.gba$")
STATE_NAME = re.compile(r"^log2_poc_r(\d+)\.(sav|ss[1-9])$")
CHUNK = 0x1000

Pre = namedtuple("Pre", "rom alloc names rest")                       # build list up to art_inject, in memory
Art = namedtuple("Art", "px problems snapped canonical")              # a checked PNG
Built = namedtuple("Built", "rom sha prev problems lines sites")       # a verified in-memory build


class Where:
    """Every path the tool reads or writes; tests point it at a scratch folder."""

    def __init__(self, build=None, art=None, log=None, build_list=None, base=None):
        self.build = Path(build or log_paths.BUILDS)
        self.art = Path(art or at.ART_DIR)
        self.log = Path(log or log2_build.BUILD_LOG)
        self.build_list = Path(build_list or log2_build.DEV_LIST)
        self.base = Path(base or log2_build.BASE)
        self.portraits_json, self.palette_json = self.art / "portraits.json", self.art / "palette.json"


# ===== build files =====

def latest_build(build_dir: Path) -> tuple:
    """(N, path) of the highest log2_poc_rN.gba, or (0, None)."""
    found = [(int(m.group(1)), p) for p in build_dir.glob("log2_poc_r*.gba") if (m := ROM_NAME.match(p.name))]
    return max(found) if found else (0, None)


def latest_states(build_dir: Path) -> list:
    """The .sav and .ss1-.ss9 files of the highest N that has any."""
    by_n = {}
    for p in build_dir.glob("log2_poc_r*.*"):
        if m := STATE_NAME.match(p.name):
            by_n.setdefault(int(m.group(1)), []).append(p)
    return sorted(by_n[max(by_n)]) if by_n else []


def plan_outputs(where: Where) -> tuple:
    """(new ROM path, [(state source, state target)]); raises if any target exists."""
    n, _ = latest_build(where.build)
    out = where.build / f"log2_poc_r{n + 1}.gba"
    states = [(p, where.build / f"log2_poc_r{n + 1}{p.suffix}") for p in latest_states(where.build)]
    taken = [p.name for p in [out] + [d for _, d in states] if p.exists()]
    if taken:
        raise FileExistsError(f"refusing to overwrite {', '.join(taken)}")
    return out, states


def _exclusive_write(path: Path, data: bytes) -> None:
    with open(path, "xb") as f:
        f.write(data)


# ===== check =====

def prebuild(where: Where) -> Pre:
    names = log2_build.read_build_list(where.build_list)
    if "art_inject" not in names:
        raise ValueError(f"{where.build_list.name} has no art_inject line")
    i = names.index("art_inject")
    rom, alloc = log2_build.assemble(where.base, names[:i])
    return Pre(rom, alloc, names, names[i:])


def check_png(pre: Pre, palette: dict, png: Path, pid: int = None, snap: bool = False) -> Art:
    """Size, colors (by value against the OBJ palette with the table applied), color count, frame ring."""
    pal, allowed = at.obj_palette(pre.rom, palette), at.allowed_indices(pre.rom, palette)
    with Image.open(png) as img:
        px, problems, snapped = at.to_pixels(img, pal, allowed, snap)
        canonical = at.is_canonical(img, pal, allowed)
    if px is not None:
        block = struct.unpack_from("<I", pre.rom, art_inject.BLOCK_LITERAL)[0] - ROM_BASE
        ref = at.live_frame(pre.rom, block, pid)[1] if pid is not None and at.valid_id(pid) else None
        found = at.check_pixels(pid if pid is not None else at.DIALOG_IDS[0], px, ref, allowed)
        problems = problems + found
    return Art(px, problems, snapped, canonical)


# ===== verify =====

def readback(rom: bytes, block: int, palette: dict, pixels: dict) -> list:
    problems = []
    for pid, px in sorted(pixels.items()):
        hdr, got = at.live_frame(rom, block, pid)
        if hdr != art_inject.slot(pid) or rom[hdr:hdr + 8] != art_inject.RAW_HEADER or got != px:
            problems.append(f"portrait {pid} does not read back equal to its PNG")
    for index, rgb in palette.items():
        _, rgb_at = art_inject.palette_sites(index)
        if at.obj_palette(rom)[index] != tuple(rgb) or tuple(rom[rgb_at:rgb_at + 3]) != tuple(rgb):
            problems.append(f"palette {index} does not read back {tuple(rgb)} in both copies")
    return problems


def diff_runs(a: bytes, b: bytes) -> list:
    """[(start, end)] of differing bytes; equal 4 KB chunks are skipped."""
    runs = []
    for c in range(0, len(b), CHUNK):
        if a[c:c + CHUNK] == b[c:c + CHUNK]:
            continue
        for i in range(c, min(c + CHUNK, len(b))):
            if a[i] != b[i]:
                if runs and runs[-1][1] == i:
                    runs[-1][1] = i + 1
                else:
                    runs.append([i, i + 1])
    return [tuple(r) for r in runs]


def art_sites(prev: bytes, rom: bytes, block: int, palette: dict, pixels: dict) -> list:
    """Sorted [(start, end, kind, id or index)]: the only places the new build may differ from prev."""
    sites = []
    for pid in pixels:
        word, new = block + 4 + 4 * pid, art_inject.slot(pid)
        sites += [(new, new + art_inject.FRAME, "slot", pid), (word, word + 4, "word", pid)]
        old = struct.unpack_from("<I", prev, word)[0] - ROM_BASE
        if old != new and old >= log2_build.BASE_SIZE and prev[old:old + 8] == art_inject.RAW_HEADER \
                and set(rom[old:old + art_inject.FRAME]) == {0xFF}:
            sites.append((old, old + art_inject.FRAME, "freed frame", pid))
    for index in palette:
        bgr, rgb_at = art_inject.palette_sites(index)
        sites += [(bgr, bgr + 2, "palette BGR555", index), (rgb_at, rgb_at + 3, "palette RGB", index)]
    return sorted(sites)


def classify(runs: list, sites: list) -> tuple:
    """({site index: differing bytes}, [(start, end)] outside every site)."""
    starts, hits, stray = [s[0] for s in sites], {}, []
    for a, b in runs:
        for i in range(a, b):
            k = bisect_right(starts, i) - 1
            if k >= 0 and i < sites[k][1]:
                hits[k] = hits.get(k, 0) + 1
            elif stray and stray[-1][1] == i:
                stray[-1][1] = i + 1
            else:
                stray.append([i, i + 1])
    return hits, [tuple(s) for s in stray]


def changed_pixels(prev: bytes, block: int, pixels: dict) -> list:
    changed = []
    for pid in sorted(pixels):
        try:
            old = at.live_frame(prev, block, pid)[1]
        except Exception:                           # the old word may name no readable frame
            old = None
        if old != pixels[pid]:
            changed.append(pid)
    return changed


def verify(prev: bytes, rom: bytes, block: int, palette: dict, pixels: dict, may_change: set) -> tuple:
    """(problems, report lines, site summary for the log). Only ids in may_change may show new pixels; any id may
    move to its slot with the same pixels (the one-time move from the r22 layout)."""
    problems = readback(rom, block, palette, pixels)
    lines = [f"verify {len(pixels)} portraits and {len(palette)} palette entries read back equal to the tables"]
    if prev is None:
        return problems, lines + ["diff   no previous build"], "no previous build"
    runs = diff_runs(prev, rom)
    sites = art_sites(prev, rom, block, palette, pixels)
    hits, stray = classify(runs, sites)
    total, changed = sum(b - a for a, b in runs), changed_pixels(prev, block, pixels)
    lines.append(f"diff   {total} bytes in {len(runs)} runs; portrait pixels changed: {changed or 'none'}")
    if set(changed) - may_change:
        problems.append(f"portrait pixels changed for ids {sorted(set(changed) - may_change)} that this command "
                        "does not name: was a table PNG edited by hand? Inject each one by its own command")
    lines += [f"       rom:0x{a:06X}-0x{b - 1:06X}  {kind} {key}: {hits[k]} bytes"
              for k, (a, b, kind, key) in enumerate(sites) if k in hits]
    problems += [f"unexpected change rom:0x{a:06X}-0x{b - 1:06X} ({b - a} bytes): not an art site" for a, b in stray]
    kinds = {}
    for k in hits:
        kinds.setdefault(sites[k][2], []).append(sites[k][3])
    groups = "; ".join(f"{kind} {','.join(map(str, sorted(keys)))}" for kind, keys in sorted(kinds.items()))
    return problems, lines, f"diff={total} bytes in {len(runs)} runs, art sites only ({groups or 'none'})"


# ===== build =====

def build_verified(where: Where, pre: Pre, palette: dict, table: dict, new: dict = None) -> Built:
    """Stage the tables (new = {id: pixels} not yet on disk), finish the build in memory, verify it. Only the ids
    in new may change their pixels."""
    pal, allowed, new = at.obj_palette(pre.rom, palette), at.allowed_indices(pre.rom, palette), new or {}
    pixels = {pid: at.png_pixels(where.art / e["png"], pal, allowed) for pid, e in table.items() if pid not in new}
    pixels.update(new)
    pre.alloc.notes["art_input"] = {"palette": palette, "portraits": pixels}
    log2_build.apply_patches(pre.rom, pre.alloc, pre.rest)
    rom = bytes(pre.rom)
    _, prev_path = latest_build(where.build)
    prev = prev_path.read_bytes() if prev_path else None
    problems, lines, summary = verify(prev, rom, pre.alloc.notes["art_inject"]["block"], palette, pixels, set(new))
    return Built(rom, hashlib.sha1(rom).hexdigest(), prev_path, problems, lines, summary)


def commit(where: Where, built: Built, outputs: tuple, names: list, action: str) -> list:
    """Write the ROM, the state copies and the log line; report lines."""
    out, states = outputs
    _exclusive_write(out, built.rom)
    for src, dst in states:
        _exclusive_write(dst, src.read_bytes())
    with where.log.open("a", encoding="utf-8", newline="\n") as f:
        f.write(f"- {datetime.now():%Y-%m-%d %H:%M} inject {out.name} {action} sha1={built.sha} "
                f"prev={built.prev.name if built.prev else 'none'} {built.sites} patches={','.join(names)} "
                f"states copied={','.join(d.name for _, d in states) or 'none'}\n")
    return [f"build  {out.name} sha1={built.sha}"] + [f"copied {s.name} -> {d.name}" for s, d in states] + \
        [f"log    {where.log.name} +1 line"]


def _write_art(target: Path, png: Path, art: Art, pal: list) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if art.canonical:                               # already the stored form: keep my bytes
        if not target.exists() or target.read_bytes() != png.read_bytes():
            shutil.copyfile(png, target)
        return
    img = Image.frombytes("P", (at.SIDE, at.SIDE), art.px)
    img.putpalette([c for rgb in pal for c in rgb])
    img.save(target)


# ===== commands =====

def _refuse(lines: list) -> int:
    print("\n".join(f"REFUSED {line}" for line in lines))
    return 1


def cmd_portrait(where: Where, pid: int, png: Path, snap: bool, note: str) -> int:
    if not at.valid_id(pid):
        return _refuse([f"id {pid}: use a dialog id 26-{at.MAX_ID} other than {sorted(at.STATUS_TWINS)}"])
    outputs, pre = plan_outputs(where), prebuild(where)
    table, palette = at.load_portraits(where.portraits_json), at.load_palette(where.palette_json)
    art = check_png(pre, palette, png, pid, snap)
    if art.problems:
        return _refuse([f"{png.name}: {p}" for p in art.problems])
    dest = Path("portraits") / f"{pid:03d}_{png.stem.removeprefix(f'{pid:03d}_')}.png"
    note = table.get(pid, {}).get("note", "") if note is None else note
    table, pal = {**table, pid: {"png": dest.as_posix(), "note": note}}, at.obj_palette(pre.rom, palette)
    built = build_verified(where, pre, palette, table, {pid: art.px})
    if built.problems:
        return _refuse(built.problems)
    _write_art(where.art / dest, png, art, pal)
    at.save_portraits(table, where.portraits_json)
    action = f"portrait {pid} {dest.name}" + (" (snapped)" if art.snapped else "")
    head = [f"check  {png.name}: {len(set(art.px))} colors, frame equals id {pid}'s frame"]
    head += [f"snap   {s}" for s in art.snapped]
    print("\n".join(head + built.lines + commit(where, built, outputs, pre.names, action)))
    return 0


def cmd_palette(where: Where, index: int, rgb: tuple) -> int:
    outputs, pre = plan_outputs(where), prebuild(where)
    palette = at.load_palette(where.palette_json)
    problems, warnings = at.check_palette_entry(pre.rom, {k: v for k, v in palette.items() if k != index}, index, rgb)
    if problems:
        return _refuse(problems)
    palette = {**palette, index: tuple(rgb)}
    built = build_verified(where, pre, palette, at.load_portraits(where.portraits_json))
    if built.problems:
        return _refuse(built.problems)
    at.save_palette(palette, where.palette_json)
    lines = [f"warn   {w}" for w in warnings] + built.lines
    print("\n".join(lines + commit(where, built, outputs, pre.names, f"palette {index} {tuple(rgb)}")))
    return 0


def cmd_check(where: Where, png: Path, pid: int, snap: bool) -> int:
    art = check_png(prebuild(where), at.load_palette(where.palette_json), png, pid, snap)
    if art.problems:
        return _refuse([f"{png.name}: {p}" for p in art.problems])
    frame = f", frame equals id {pid}'s frame" if pid is not None else " (no id given: frame not checked)"
    print("\n".join([f"snap   {s}" for s in art.snapped] + [f"OK     {png.name}: {len(set(art.px))} colors{frame}"]))
    return 0


def cmd_list(where: Where) -> int:
    table, palette = at.load_portraits(where.portraits_json), at.load_palette(where.palette_json)
    lines = [f"portraits: {len(table)} (frame at rom:0x{art_inject.slot(0):X} + 0x{art_inject.FRAME:X} x id)"]
    for pid, e in sorted(table.items()):
        path = where.art / e["png"]
        sha = hashlib.sha1(path.read_bytes()).hexdigest()[:8] if path.exists() else "MISSING"
        lines.append(f"  {pid:3d}  rom:0x{art_inject.slot(pid):06X}  {e['png']}  {sha}  {e.get('note', '')}")
    lines.append(f"palette: {len(palette)}" + ("" if palette else " (none)"))
    lines += [f"  {k:3d}  {tuple(v)}" for k, v in sorted(palette.items())]
    n, path = latest_build(where.build)
    lines.append(f"latest build: {path.name if path else 'none'}; next: log2_poc_r{n + 1}.gba")
    print("\n".join(lines))
    return 0


# ===== main =====

def _rgb(text: str) -> tuple:
    return tuple(int(c) for c in text.replace(" ", "").split(","))


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="inject.py", description="Add or replace a portrait or a palette entry.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("portrait", help="add or replace a dialog portrait, then build the next ROM")
    s.add_argument("id", type=int)
    s.add_argument("png", type=Path)
    s.add_argument("--snap", action="store_true", help="map off-palette colors to the nearest index")
    s.add_argument("--note", default=None)
    s = sub.add_parser("palette", help="set an OBJ palette entry (both ROM copies), then build the next ROM")
    s.add_argument("index", type=int)
    s.add_argument("rgb", type=_rgb, help="r,g,b: 8-bit channels, each a multiple of 8")
    s = sub.add_parser("check", help="validate a PNG only")
    s.add_argument("png", type=Path)
    s.add_argument("id", type=int, nargs="?")
    s.add_argument("--snap", action="store_true")
    sub.add_parser("list", help="print the tables")
    return p


def main(argv: list, where: Where = None) -> int:
    where, args = where or Where(), _parser().parse_args(argv)
    env = sorted(k for k in os.environ if k.startswith("LOG_"))
    if env and args.cmd in ("portrait", "palette"):
        return _refuse([f"unset {', '.join(env)}: the build follows build_list_dev.txt only"])
    try:
        if args.cmd == "portrait":
            return cmd_portrait(where, args.id, args.png, args.snap, args.note)
        if args.cmd == "palette":
            return cmd_palette(where, args.index, args.rgb)
        if args.cmd == "check":
            return cmd_check(where, args.png, args.id, args.snap)
        return cmd_list(where)
    except (ValueError, FileExistsError, FileNotFoundError) as e:    # a patch or table check failed: nothing written
        return _refuse([str(e)])


if __name__ == "__main__":
    t0 = time.perf_counter()
    code = main(sys.argv[1:])
    print(f"time   {time.perf_counter() - t0:.1f} s")
    sys.exit(code)
