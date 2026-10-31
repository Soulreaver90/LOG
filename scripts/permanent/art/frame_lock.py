r"""
frame_lock.py - Lock I-approved frames of an art folder, then show which ones changed later.

Usage:   py -3 -I scripts\permanent\art\frame_lock.py lock <art_folder> [--note text] [--replace]
         py -3 -I scripts\permanent\art\frame_lock.py lock --golden [--note text] [--replace]
         py -3 -I scripts\permanent\art\frame_lock.py check <art_folder> [--sheet out.png]
         py -3 -I scripts\permanent\art\frame_lock.py check --golden [--sheet out.png]
Prints:  check: the changed, added and removed PNGs with their (anim, dir, index) keys. Exit code 1 on any change,
         2 when no lock exists, 0 when the folder equals its lock.
API:     fingerprint(path) -> sha1 hex of (width, height, pixel index bytes)
         lock_folder(folder, note, locks_root, only=None, replace=False) -> lock.json path
         check_folder(folder, locks_root, only=None) -> {"changed", "added", "removed"} (each {name: keys})
         changed_sheet(folder, lock_dir, names, out, scale) -> None
Rules:   A lock lives in art\locks\<folder name>\ as lock.json plus png\ (a copy of every PNG). The lock
         name is the folder name. The fingerprint covers pixel indexes only, never the PNG encoding or the palette.
         A lock is never overwritten without --replace, which moves the old lock to <folder name>_<yyyymmdd-hhmm>.
         Keys come from the folder manifest.json (gi layout with "keys", or the export layout with anim/dir/index).
         --golden locks exactly the GOLDEN_FILES as the set "golden": the 16 idle frames
         golden_gi_{base,ssj,ssj2,ssj2std}_d{0-3}.png and my 4 walk frames golden_gi_base_a1_d0_i{0-3}.png
         (me, 2026-10-18 9:48 AM; the lightning drafts stay out), plus the 64 reviewed r12fix hand frames
         hand_frames.GOLDEN_HAND (golden_gi_{base,ssj,ssj2std}_a<anim>_d<dir>_i<index>[_r17|_r18|_r19].png, r15,
         r17, r18 and r19 intakes); check then compares those 84 names only.
         ssj2 = the Rage (set 160) power-pose idle, ssj2std = the playable SSJ2 (set 159) standard idle
         (3:15 PM); both are the aura-free bodies.
         The tool never writes outside the locks folder.
Source:  My review rule (2026-10-18): a changed approved frame needs re-approval.
"""
import hashlib
import json
import shutil
import struct
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P and -I omit the script folder

from PIL import Image, ImageDraw

from art.gi_review import BACKGROUND
from art.hand_frames import GOLDEN_HAND
import log_paths

# ===== constants =====
ROOT = Path(__file__).resolve().parents[3]
LOCKS = log_paths.ART / "locks"
GOLDEN_DIR = log_paths.ART / "golden"
GOLDEN_NAME = "golden"
GOLDEN_IDLE = [f"golden_gi_{form}_d{d}.png" for form in ("base", "ssj", "ssj2", "ssj2std") for d in range(4)]
GOLDEN_WALK = [f"golden_gi_base_a1_d0_i{i}.png" for i in range(4)]   # gi_base keys 1.0.0-1.0.3, record size
GOLDEN_FILES = GOLDEN_IDLE + GOLDEN_WALK + GOLDEN_HAND   # GOLDEN_HAND: the 64 r12fix frames (hand_frames.py)
SHEET_SCALE = 6
BLACK = (0, 0, 0)

# ===== fingerprint and keys =====

def _indexes(path: Path) -> tuple:
    with Image.open(path) as img:
        if img.mode != "P":
            raise ValueError(f"{path.name}: mode {img.mode}, not an indexed (P) image")
        return img.size, img.tobytes()

def fingerprint(path: Path) -> str:
    (w, h), px = _indexes(Path(path))
    return hashlib.sha1(struct.pack("<II", w, h) + px).hexdigest()

def _keys_by_png(folder: Path) -> dict:
    """{png name: [[anim, dir, index], ...]} from manifest.json; empty when the folder has none."""
    path = folder / "manifest.json"
    if not path.exists():
        return {}
    keys = {}
    for e in json.loads(path.read_text(encoding="ascii")):
        for k in e.get("keys", [e] if "anim" in e else []):
            keys.setdefault(e["png"], []).append([k["anim"], k["dir"], k["index"]])
    return keys

def _names(folder: Path, only) -> list:
    return sorted(only) if only else sorted(p.name for p in folder.glob("*.png"))

# ===== lock =====

def lock_folder(folder: Path, note: str, locks_root: Path, only=None, replace: bool = False, name: str = None) -> Path:
    folder, locks_root = Path(folder), Path(locks_root)
    name = name or folder.name
    target = locks_root / name
    if target.exists():
        if not replace:
            raise FileExistsError(f"lock {target} exists; pass --replace to move it aside and lock again")
        target.rename(locks_root / f"{name}_{datetime.now():%Y%m%d-%H%M}")
    keys, now = _keys_by_png(folder), datetime.now().isoformat(timespec="seconds")
    frames = {}
    (target / "png").mkdir(parents=True)
    for n in _names(folder, only):
        frames[n] = {"fingerprint": fingerprint(folder / n), "keys": keys.get(n, []), "time": now, "note": note}
        shutil.copyfile(folder / n, target / "png" / n)
    path = target / "lock.json"
    path.write_text(json.dumps({"version": 1, "folder": str(folder), "only": sorted(only) if only else None,
                                "note": note, "time": now, "frames": frames}, indent=1), encoding="ascii")
    return path

# ===== check =====

def _load_lock(folder: Path, locks_root: Path, name: str = None) -> tuple:
    lock_dir = Path(locks_root) / (name or Path(folder).name)
    path = lock_dir / "lock.json"
    if not path.exists():
        raise FileNotFoundError(f"no lock at {path}")
    return lock_dir, json.loads(path.read_text(encoding="ascii"))

def check_folder(folder: Path, locks_root: Path, only=None, name: str = None) -> dict:
    folder = Path(folder)
    lock_dir, lock = _load_lock(folder, locks_root, name)
    only = only or lock["only"]
    now_keys = _keys_by_png(folder)
    current = {n: fingerprint(folder / n) for n in _names(folder, only)}
    old = lock["frames"]
    return {"changed": {n: old[n]["keys"] or now_keys.get(n, []) for n in current if n in old and current[n] != old[n]["fingerprint"]},
            "added": {n: now_keys.get(n, []) for n in current if n not in old},
            "removed": {n: old[n]["keys"] for n in old if n not in current}}

def changed_sheet(folder: Path, lock_dir: Path, names: list, out: Path, scale: int = SHEET_SCALE) -> None:
    """One row per name: locked | current | changed pixels in black, all on lime."""
    rows = []
    for n in names:
        (lw, lh), lpx = _indexes(Path(lock_dir) / "png" / n)
        (cw, ch), cpx = _indexes(Path(folder) / n)
        w, h = max(lw, cw), max(lh, ch)
        mask = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for y in range(h):
            for x in range(w):
                a = lpx[y * lw + x] if x < lw and y < lh else 0
                b = cpx[y * cw + x] if x < cw and y < ch else 0
                if a != b:
                    mask.putpixel((x, y), BLACK + (255,))
        rows.append((n, [Image.open(Path(lock_dir) / "png" / n).convert("RGBA"), Image.open(Path(folder) / n).convert("RGBA"), mask], (w, h)))
    pad = 6 * scale
    width = pad + sum(max(r[2][0] for r in rows) * scale + pad for _ in range(3))
    sheet = Image.new("RGB", (width, sum(r[2][1] * scale + 3 * pad for r in rows) + pad), BACKGROUND)
    d = ImageDraw.Draw(sheet)
    y = pad
    for n, ims, (w, h) in rows:
        d.text((pad, y - pad + 2), n, fill=BLACK)
        for i, im in enumerate(ims):
            big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
            sheet.paste(big, (pad + i * (max(r[2][0] for r in rows) * scale + pad), y + pad // 2), big)
        y += h * scale + 3 * pad
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)

# ===== command line =====

def _main(argv: list) -> int:
    if not argv or argv[0] not in ("lock", "check"):
        print(__doc__)
        return 1
    cmd, args = argv[0], argv[1:]
    golden = "--golden" in args
    opt = {"--note": "", "--sheet": None}
    pos, i = [], 0
    while i < len(args):
        if args[i] in opt and i + 1 < len(args):
            opt[args[i]] = args[i + 1]
            i += 1
        elif not args[i].startswith("--"):
            pos.append(args[i])
        i += 1
    if golden:
        folder, only = GOLDEN_DIR, GOLDEN_FILES
    elif len(pos) == 1:
        folder, only = Path(pos[0]), None
    else:
        print(__doc__)
        return 1
    if cmd == "lock":
        print(lock_folder(folder, opt["--note"], LOCKS, only, "--replace" in args, GOLDEN_NAME if golden else None))
        return 0
    name = GOLDEN_NAME if golden else None
    try:
        lock_dir, _ = _load_lock(folder, LOCKS, name)
        result = check_folder(folder, LOCKS, only, name)
    except FileNotFoundError as e:
        print(e)
        return 2
    for kind in ("changed", "added", "removed"):
        for n, keys in sorted(result[kind].items()):
            print(f"{kind}: {n} keys {keys}")
    total = sum(len(v) for v in result.values())
    print(f"{total} difference(s)")
    if opt["--sheet"] and result["changed"]:
        changed_sheet(folder, lock_dir, sorted(result["changed"]), Path(opt["--sheet"]))
    return 1 if total else 0

if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
