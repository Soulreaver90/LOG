r"""
hand_frames.py - Reviewed hand-fixed gi frames, placed by key into the art folder that each set builds from.

Usage:   Library. gi_art.py (gi_base, set 157, in its render loop), gi_post.py (gi_ssj_v2, set 158, after the step
         frames) and gi_aura.py (gi_ssj2_aura, set 159, after the bolts) call it, so every regeneration keeps the frames.
API:     golden_name(folder, key) -> file name     folder_frames(folder) -> {key: golden file name}
         drawn(folder, attrs, size) -> (index bytes, [golden names]) or None    place(folder_path, manifest) -> [notes]
         GOLDEN_HAND: every golden name of HAND (frame_lock.py locks them with --golden)
Method:  A golden is the frame as the record shows it (flips applied), 1x, mode P in the shared OBJ palette, the
         record's size. The placed PNG holds it in stored order: a key with the h-flip or v-flip bit gets it flipped
         back. One PNG serves every key that shares its frame header, so all listed keys of a PNG must give the same
         bytes, and an unlisted key may share it only as the dir 3 flip of a listed dir 2 key (it shows the mirror).
         Anything else raises: a split would add frames and move every later allocation of the build.
         A redrawn key gets a new golden named with its REVISION suffix (golden_..._r17.png to _r19.png); the
         old file stays on disk, out of HAND and out of the lock.
Source:  My r12fix frames, my review 2026-10-18 (art\hand-fixes\edits.py): snapshot snap_r15 for the
         r15 intake (docs\tasks\2026-10-18-r12fix-intake\r12fix-intake.md), snapshot snap_r17 for the r17 intake (r17-intake.md:
         1.2.0 of each set, 157 16.2.1 and anim 20, and 159 1.0.0, 1.0.2 and 13.0.3 with their aura bolts),
         snapshot snap_r18 for the r18 intake (r18-intake.md: CARRY, the base fixes carried to 158 and 159 by the
         r12fix "delta" op, and 159 1.2.0 with its aura bolts), snapshot snap_r19 for the r19 intake (r19-build.md:
         158 12.0.1-3 with the armor boot gray recolored to shoe and pants).
         Anim 20 has 2 frames per index: dir 2 is the h-flip of dir 0 and dir 3 of dir 1, all 4 dirs listed.
         My walk frames 1.0.0-1.0.3 stay in gi_art.OWNER_FRAMES.
         DERIVED: the hand frames of the derived sets 158 and 159 (gi_ssj_v4, gi_ssj2_aura_v4): head-only fixes and
         the v2 hand frames of keys that stay as today; a body fix goes on base only and reaches them through
         gi_one_body.py. They reuse the v2 golden names (SOURCE), so GOLDEN_HAND lists each name once.
Rules:   The goldens are read only. Index 0 is transparent.
"""
from pathlib import Path

from PIL import Image

import log_paths

# ===== constants =====
GOLDEN = log_paths.ART / "golden"
HFLIP, VFLIP = 0x1000, 0x2000
MIRROR_DIR, SOURCE_DIR = 3, 2
FORM = {"gi_base": "base", "gi_ssj_v2": "ssj", "gi_ssj2_aura": "ssj2std",   # sets 157, 158, 159 (frame_lock names)
        "gi_ssj_v4": "ssj", "gi_ssj2_aura_v4": "ssj2std"}                    # 158, 159 derived (gi_one_body.py)
LYING = [(3, d, 3) for d in range(3)]                                       # one shared frame per set
FLIGHT = [(20, d, i) for d in range(4) for i in range(4)]                   # world map flight, r17
CARRY = [(5, 0, 2), (8, 0, 3), (8, 2, 2), *[(12, 0, i) for i in range(4)], (16, 2, 1), (16, 2, 4)]   # r18, 158/159
HAND = {"gi_base": LYING + [(5, 0, 2), (8, 0, 3), (8, 2, 2), *[(12, 0, i) for i in range(4)],
                            (13, 0, 0), (13, 0, 2), (13, 0, 3), (16, 2, 4)]
                   + [(1, 2, 0), (16, 2, 1)] + FLIGHT,
        "gi_ssj_v2": [(1, 0, 0), (1, 0, 2)] + LYING + [(13, 0, 3)] + [(1, 2, 0)] + CARRY,
        "gi_ssj2_aura": [(1, 0, 0), (1, 0, 2)] + LYING + [(13, 0, 3)] + [(1, 2, 0)] + CARRY}
# Derived sets (one body, me, 2026-10-22): 158 and 159 take the base body, so a derived key needs no hand frame
# (the 32 v2 keys above are all body fixes, scripts\one-time\2026-10-22-one-body\a5_hand.txt). A key that stays as today keeps today's
# frame: gi_ssj_v4 copies it from gi_ssj_v2 (hand frames placed), gi_ssj2_aura_v4 needs its v2 hand frame here.
KEPT_159 = [(16, 2, 1), (16, 2, 4)]                                         # vanilla poses differ (gi_one_body)
DERIVED = {"gi_ssj_v4": [], "gi_ssj2_aura_v4": KEPT_159}
REVISION = {"gi_ssj2_aura": {(1, 0, 0): "r17", (1, 0, 2): "r17", (13, 0, 3): "r17",   # r17: aura bolts back
                             (1, 2, 0): "r18"},                                        # r18: side walk bolts back
            "gi_ssj_v2": {(12, 0, 1): "r19", (12, 0, 2): "r19", (12, 0, 3): "r19"}}   # r19: no armor boot gray
SOURCE = {"gi_ssj_v4": "gi_ssj_v2", "gi_ssj2_aura_v4": "gi_ssj2_aura"}       # a derived set uses the v2 golden names


# ===== names =====

def golden_name(folder: str, key: tuple) -> str:
    a, d, i = key
    rev = REVISION.get(SOURCE.get(folder, folder), {}).get(key)
    return f"golden_gi_{FORM[folder]}_a{a}_d{d}_i{i}{'_' + rev if rev else ''}.png"


def folder_frames(folder: str) -> dict:
    return {k: golden_name(folder, k) for k in HAND.get(folder, DERIVED.get(folder, []))}


GOLDEN_HAND = list(dict.fromkeys(golden_name(f, k) for f, keys in (HAND | DERIVED).items() for k in keys))


# ===== placement =====

def _stored(name: str, attr1: int) -> Image.Image:
    with Image.open(GOLDEN / name) as im:
        img = im.copy()
    if img.mode != "P":
        raise ValueError(f"{name}: mode {img.mode}, not indexed")
    if attr1 & HFLIP:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if attr1 & VFLIP:
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
    return img


def drawn(folder: str, attrs: dict, size: tuple):
    """attrs = {key: attr1} of every key that shares one PNG of `folder`. (stored bytes, golden names) when a key
    is listed, else None."""
    table = folder_frames(folder)
    names = sorted({table[k] for k in attrs if k in table})
    if not names:
        return None
    data = {_stored(table[k], a).tobytes() for k, a in attrs.items() if k in table}
    sizes = {_stored(n, 0).size for n in names}
    if len(data) > 1:
        raise ValueError(f"{folder}: {names} share one frame but differ")
    if sizes != {tuple(size)}:
        raise ValueError(f"{folder}: {names} are {sizes}, the frame is {tuple(size)}")
    for (a, d, i), attr1 in attrs.items():
        twin = (a, SOURCE_DIR, i)
        mirror = d == MIRROR_DIR and twin in table and twin in attrs and (attr1 ^ attrs[twin]) & HFLIP
        if (a, d, i) not in table and not mirror:
            raise ValueError(f"{folder}: key {a}.{d}.{i} shares the frame of {names} but is not listed")
    return data.pop(), names


def place(folder: Path, manifest: list) -> list:
    """Write the listed goldens over the PNGs of `folder` (a final art folder) and note it in `manifest` entries.
    The caller writes manifest.json."""
    folder = Path(folder)
    table, found, notes = folder_frames(folder.name), set(), []
    for e in manifest:
        attrs = {(k["anim"], k["dir"], k["index"]): k["attr1"] for k in e["keys"]}
        with Image.open(folder / e["png"]) as old:
            size, palette = old.size, old.getpalette()
        hit = drawn(folder.name, attrs, size)
        if hit is None:
            continue
        data, names = hit
        img = Image.frombytes("P", size, data)
        img.putpalette(palette)
        img.save(folder / e["png"], transparency=0)
        e["notes"] = list(e.get("notes", [])) + [f"hand frame {', '.join(names)}"]
        found |= set(attrs) & set(table)
        notes.append(f"{e['png']}: {', '.join(names)}")
    missing = sorted(set(table) - found)
    if missing:
        raise ValueError(f"{folder.name}: no frame for hand keys {missing}")
    return notes
