# Finish gi_ssj2_v2: golden frames replace the idle frames, powered-down frames go back to the source,
# then the body rules run. Keeps transplant.json in step (status "golden" or "kept").
import sys; print(r'promoted to scripts\permanent\gi_post.py'); sys.exit(1)   # exit guard: a run here would write stale output
import json, shutil
from pathlib import Path
from PIL import Image
ART = Path(__file__).resolve().parents[2]
SRC, V2, GOLD = ART / "gi_ssj2", ART / "gi_ssj2_v2", ART / "golden"
GOLDEN = {"frame_2A15DC.png": 0, "frame_2A1878.png": 1, "frame_2A19AC.png": 2}
KEEP = {"frame_2A39F4.png", "frame_2A3AD0.png",           # anim 3 frames 2-3: black hair, powered down
        "frame_2B667C.png", "frame_2B6794.png", "frame_2B68A0.png"}   # anim 21 frames 1-3: hair turning back to black
man = {e["png"]: e for e in json.loads((V2 / "manifest.json").read_text())}
src = {e["png"]: e for e in json.loads((SRC / "manifest.json").read_text())}
rep = json.loads((V2 / "transplant.json").read_text())
for r in rep:
    p = r["png"]
    if p in GOLDEN:
        Image.open(GOLD / f"golden_gi_ssj2_d{GOLDEN[p]}.png").save(V2 / p, transparency=0)
        man[p]["w"] = man[p]["h"] = 32
        man[p]["keys"] = [dict(k) for k in src[p]["keys"]]; r["status"] = "golden"
    elif p in KEEP:
        shutil.copyfile(SRC / p, V2 / p)
        e = {k: v for k, v in src[p].items() if k not in ("head", "checks", "arms")}; man[p] = e; r["status"] = "kept"
(V2 / "manifest.json").write_text(json.dumps(list(man.values()), indent=1))
(V2 / "transplant.json").write_text(json.dumps(rep, indent=1))
print({s: sum(r["status"] == s for r in rep) for s in sorted({r["status"] for r in rep})})
