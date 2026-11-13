# throwaway: hand edits that turn the converted idle frames into golden frames. Each edit is (x, y, old, new):
# the old char is asserted so an edit never lands on the wrong pixel. Writes g_<form>_d<dir>.txt.
from pathlib import Path
W = Path(__file__).parent


def row(y, x0, old, new):
    assert len(old) == len(new)
    return [(x0 + i, y, o, n) for i, (o, n) in enumerate(zip(old, new)) if o != n]


EDITS = {
    # front: full bands (195 fill, 72 edge) across each forearm, torso outline instead of stray arm skin
    "gi_base_d0": row(21, 2, "Nn5xpPpPPx5ne", "NnnxpPpPPxnnN") + row(22, 5, "5xpppx5", "xpppppx"),
    "gi_ssj_d0": row(21, 1, "Nn5xpPpPPx5ne", "NnnxpPpPPxnnN"),
    # back: arms 2 px beside the back (the converter gave them 4), full bands
    "gi_base_d1": row(19, 1, "e4455xpx5544e", "e44xpppppx44e") + row(20, 1, "e355xppPx553e", "e35xpppPpx53e")
    + row(21, 1, "Nn55xPPPx55nN", "NnnxpPPPpxnnN"),
    "gi_ssj_d1": row(19, 1, "e44xPPPPx544e", "e44xPPPPPx44e") + row(20, 1, "e355xppx5553e", "e35xpppppx53e")
    + row(21, 1, "Nn5xppppx55nN", "NnnxppppPxnnN"),
    # side: the arm's front edge is skin outline
    "gi_base_d2": row(19, 11, "x", "e") + row(20, 11, "x", "e"),
    "gi_ssj_d2": row(19, 11, "x", "e") + row(20, 11, "x", "e"),
    # Super Saiyan 2 front: bands across the horizontal forearms (3 rows), no outline inside the arm
    "gi_ssj2_d0": [(9, 18, "N", "n"), (10, 18, "e", "4"), (20, 18, "e", "4"), (21, 18, "N", "n"),
                   (9, 19, "N", "n"), (21, 19, "N", "n"), (9, 20, "5", "N"), (21, 20, "5", "N")],
    # Super Saiyan 2 back: bands at the wrist column, back as wide as the plate was
    "gi_ssj2_d1": [(8, 18, "N", "e"), (9, 18, "e", "N"), (9, 19, "3", "n"), (9, 20, "4", "n"), (9, 21, "e", "N"),
                   (22, 18, "N", "e"), (21, 18, "e", "N"), (21, 19, "4", "n"), (21, 20, "4", "n"),
                   (21, 21, "e", "N")] + row(19, 12, "5xPPPx5", "xPPPPPx"),
    # Super Saiyan 2 side: bands across both forearms
    "gi_ssj2_d2": [(10, 18, "N", "n"), (10, 19, "N", "n"), (10, 20, "4", "N"),
                   (19, 18, "4", "N"), (19, 19, "N", "n"), (19, 20, "N", "n")],
}

if __name__ == "__main__":
    for name, edits in EDITS.items():
        rows = [list(r) for r in (W / f"{name}.txt").read_text().splitlines() if r]
        for x, y, old, new in edits:
            assert rows[y][x] == old, f"{name} ({x},{y}) is {rows[y][x]!r}, expected {old!r}"
            rows[y][x] = new
        (W / f"g_{name}.txt").write_bytes(("\n".join("".join(r) for r in rows) + "\n").encode())
        print(name, len(edits), "edits")
