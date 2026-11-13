# Shoe rule (refined) and shading rule C for the gi, as the owner approved them on the base goldens.
# Shoe: each 4-connected boot part keeps its bottom 2 rows; on the row above, columns under trouser become the hem
# (211) and the rest stays shoe (the toe in profile); higher rows become trouser (89, 211 at the part's edges).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from shade_c_mock import shade_c                               # noqa: E402,F401
BOOT, HEM, TROUSER, GI = {34, 35}, 211, 89, {88, 89, 211}


def shoes2(px, w, h):
    out = bytearray(px)
    seen = set()
    for start in range(w * h):
        if px[start] not in BOOT or start in seen:
            continue
        part, todo = set(), [start]
        while todo:
            i = todo.pop()
            if i in part or px[i] not in BOOT:
                continue
            part.add(i)
            x, y = i % w, i // w
            todo += [j for j, ok in ((i - 1, x > 0), (i + 1, x < w - 1), (i - w, y > 0), (i + w, y < h - 1)) if ok]
        seen |= part
        bottom = max(i // w for i in part)
        top = min(i // w for i in part)
        for i in sorted(part):
            x, y = i % w, i // w
            if y < bottom - 2:
                row = [j % w for j in part if j // w == y]
                out[i] = HEM if x in (min(row), max(row)) else TROUSER
            elif y == bottom - 2:
                above = out[i - w] if y > 0 else 0
                if above in GI or (y - 1 >= top and (i - w) in part):
                    out[i] = HEM
    return bytes(out)
