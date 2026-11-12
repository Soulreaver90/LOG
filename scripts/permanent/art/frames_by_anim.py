r"""Lay a sprite set's exported frames out in one folder per animation, then per direction.

Why: a flat export is named by ROM header address, so the files sort by where they sit in the ROM
and not by the order they play. An artist redrawing a set needs to see one animation at a time, in
frame order. This reads the export's own manifest.json and copies each frame into
`anim<NN>_<name>\dir<D>_<name>\<index>_frame_<header>.png`, so the file order IS the play order.

The same frame is often shared by several records, so a shared frame appears in every row that uses
it. That is on purpose: each row has to be complete on its own.

Nothing is moved and no source file is written. The output folder is built fresh.

Anim and direction names are BY EYE, from bible B0078, which is confidence L. Treat a name as a
label, never as proof of what a row does.

Run: py -3.14 -P scripts\permanent\art\frames_by_anim.py --set 128
     py -3.14 -P scripts\permanent\art\frames_by_anim.py --set 128 --frames <my edited folder> --out <where>
"""
import argparse
import json
import shutil
from pathlib import Path

from PIL import Image

LOG = Path(__file__).resolve().parents[3]
SETS = LOG / "art" / "vanilla-sets"

# Bible B0078, by eye, confidence L. A missing number gets "anim<NN>".
ANIM_NAMES = {
    0: "stand", 1: "walk", 2: "hurt", 3: "knocked_down", 4: "idle_arms", 5: "punch",
    6: "melee_a", 7: "melee_b", 8: "melee_c", 9: "power_up", 10: "knocked_out",
    11: "arms_overhead", 12: "swim", 13: "run", 14: "crouch", 16: "special_a",
    17: "halo", 18: "special_b", 19: "special_c", 20: "fly", 21: "revert", 22: "stand_2",
}
DIR_NAMES = {0: "down", 1: "up", 2: "left", 3: "right"}
STRIP_PAD, STRIP_BG = 4, (0, 0, 0, 0)


def anim_folder(anim: int) -> str:
    return f"anim{anim:02d}_{ANIM_NAMES.get(anim, 'unknown')}"


def dir_folder(d: int) -> str:
    return f"dir{d}_{DIR_NAMES.get(d, 'unknown')}"


def rows(manifest: list) -> dict:
    """{(anim, dir): [record, ...]} with each row sorted by its frame index."""
    out = {}
    for rec in manifest:
        out.setdefault((rec["anim"], rec["dir"]), []).append(rec)
    for key in out:
        out[key].sort(key=lambda r: r["index"])
    return out


def strip(paths: list, to: Path) -> None:
    """One row laid left to right, so the play order is visible at a glance."""
    shots = [Image.open(p).convert("RGBA") for p in paths]
    w = sum(s.width for s in shots) + STRIP_PAD * (len(shots) + 1)
    h = max(s.height for s in shots) + STRIP_PAD * 2
    sheet = Image.new("RGBA", (w, h), STRIP_BG)
    x = STRIP_PAD
    for s in shots:
        sheet.paste(s, (x, h - STRIP_PAD - s.height), s)
        x += s.width + STRIP_PAD
    sheet.save(to)


def build(frames: Path, manifest: list, out: Path, set_id: str, strips_only: bool = False) -> dict:
    """Lay the frames out, or with strips_only just redraw each row's strip from what is on disk.

    THIS NEVER DELETES. An earlier version removed `out` first, which would have destroyed the
    owner's hand drawn frames the moment anyone re-ran the tool over his working folder. A frame
    file is replaced only when this run copies that exact path, and `strips_only` copies nothing,
    so it is always safe to run over work in progress.
    """
    out.mkdir(parents=True, exist_ok=True)
    stats, missing = {}, []
    for (anim, d), recs in sorted(rows(manifest).items()):
        folder = out / anim_folder(anim) / dir_folder(d)
        folder.mkdir(parents=True, exist_ok=True)
        present = []
        for rec in recs:
            to = folder / f"{rec['index']:02d}_{rec['png']}"
            if strips_only:
                # Redraw from what is on disk, so HIS edits are what the strip shows.
                if to.is_file():
                    present.append(to)
                else:
                    missing.append(to.name)
                continue
            src = frames / rec["png"]
            if not src.is_file():
                missing.append(rec["png"])
                continue
            shutil.copyfile(src, to)
            present.append(to)
        if present:
            strip(present, folder.parent / f"{dir_folder(d)}_strip.png")
        stats[(anim, d)] = len(present)
    if not strips_only:
        write_readme(out, stats, set_id, missing)
    return {"rows": len(stats), "files": sum(stats.values()), "missing": missing}


def write_readme(out: Path, stats: dict, set_id: str, missing: list) -> None:
    anims = sorted({a for a, _ in stats})
    lines = [f"# Set {set_id}, laid out by animation", "",
             "One folder per animation, then one per direction. A file name starts with its frame",
             "index, so the files play in the order they sort. A `_strip.png` beside each direction",
             "shows that row left to right.", "",
             "A frame shared by several rows is copied into each of them, so every row is complete.",
             "", "**Names are BY EYE, from bible B0078, confidence L.** A name is a label, not proof.",
             "", "| Anim | Name | dir0 down | dir1 up | dir2 left | dir3 right |",
             "| --- | --- | --- | --- | --- | --- |"]
    for anim in anims:
        cells = [str(stats.get((anim, d), 0)) or "-" for d in range(4)]
        lines.append(f"| {anim} | {ANIM_NAMES.get(anim, 'unknown')} | " + " | ".join(cells) + " |")
    if missing:
        lines += ["", f"**{len(missing)} frames named by the manifest were not in the source "
                      f"folder.** They are left out:", ""] + [f"- `{m}`" for m in sorted(set(missing))]
    (out / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--set", required=True, help="set id, for the default folders")
    ap.add_argument("--frames", help="folder holding the PNGs (default: the vanilla export)")
    ap.add_argument("--manifest", help="manifest.json (default: the vanilla export's)")
    ap.add_argument("--out", help="where to write (default: <export>-by-anim)")
    ap.add_argument("--strips", action="store_true",
                    help="redraw each row's strip from the frames ALREADY in --out, copying nothing. "
                         "Use this after hand editing frames, so the strips show your work.")
    a = ap.parse_args()

    export = SETS / f"set{a.set}"
    frames = Path(a.frames) if a.frames else export
    man = Path(a.manifest) if a.manifest else export / "manifest.json"
    out = Path(a.out) if a.out else SETS / f"set{a.set}-by-anim"

    needed = ((man, "manifest"),) if a.strips else ((frames, "frames folder"), (man, "manifest"))
    for p, what in needed:
        if not p.exists():
            raise SystemExit(f"no {what}: {p}")
    if a.strips and not out.exists():
        raise SystemExit(f"--strips needs an existing layout to redraw: {out}")

    got = build(frames, json.loads(man.read_text(encoding="utf-8")), out, a.set, a.strips)
    if a.strips:
        print(f"  set {a.set}: redrew {got['rows']} strips from the frames in {out}")
        print("  no frame file was copied, replaced or deleted")
    else:
        print(f"  set {a.set}: {got['rows']} rows, {got['files']} frame files")
        print(f"  from  {frames}")
        print(f"  wrote {out}")
    if got["missing"]:
        print(f"  WARNING: {len(got['missing'])} manifest frames were not in the source folder")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
