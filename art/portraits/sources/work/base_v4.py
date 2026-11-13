"""Throwaway mockup v4: base gi torso drawn as a grid (bare arms, gi straps, muscled V chest), Piccolo colors."""
import sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, r"C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\scripts\permanent")
sys.path.insert(0, r"C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\scripts\permanent\patches")
import gohan_portraits as gp
W = Path(__file__).parent
rom = gp.BASE.read_bytes()
obj, stat = gp.palette(rom, gp.OBJ_PAL), gp.palette(rom, gp.STATUS_PAL)
CH = {"K": 1, "p": 97, "P": 233, "s": 115, "S": 114, "d": 116, "o": 35}
# left half, x3..x31; '.' background, '=' keep the id 59 pixel
LEFT = {
    48: "..................." + "==========",
    49: ".................." + "===========",
    50: "..............." + "KKK" + "P" + "==========",
    51: "..........." + "KKK" + "PPP" + "p" + "K" + "==========",
    52: "........" + "KK" + "PPPP" + "ppp" + "P" + "K" + "==========",
    53: "....." + "KK" + "PPPP" + "pppppp" + "P" + "K" + "s" + "SSSSS" + "ssss",
    54: ".." + "ooo" + "K" + "p" + "PP" + "ppppppppp" + "P" + "K" + "SSSS" + "sssss",
    55: "." + "o" + "SS" + "s" + "K" + "pppp" + "P" + "ppppppp" + "P" + "K" + "SSS" + "ssssss",
    56: "o" + "SS" + "ss" + "K" + "ppppp" + "P" + "ppppppp" + "P" + "K" + "dSSsssss",
    57: "s" + "S" + "sss" + "d" + "K" + "ppppp" + "P" + "pppppp" + "P" + "K" + "dSssssdo",
    58: "ssss" + "dd" + "K" + "pppppp" + "P" + "pppppp" + "P" + "K" + "osssssdo"[1:],
    59: "d" + "sss" + "dd" + "K" + "ppppppp" + "P" + "ppppp" + "P" + "K" + "doossdo",
    60: "d" + "sss" + "ddd" + "K" + "ppppppp" + "P" + "ppppp" + "P" + "K" + "sdoooo",
}
px = bytearray(gp.portrait(rom, 59))
bg = [px[47 * 64 + x] if px[47 * 64 + x] in (74, 75) else 75 for x in range(64)]
for y, row in LEFT.items():
    assert len(row) == 29, (y, len(row))
    for i, c in enumerate(row):
        for x, right in ((3 + i, False), (59 - i, True)):
            if c == "=":
                continue
            k = bg[x] if c == "." else CH[{"S": "s"}.get(c, c) if right else c]
            px[y * 64 + x] = k
    px[y * 64 + 60] = px[y * 64 + 59] if row[0] != "." else bg[60]
base = bytes(px)
dialog, status, rep = gp.convert(rom, [obj[k] for k in base])
assert dialog == base
gp._indexed(base, obj).save(W / "gi_base_dialog_v4.png")
gp._indexed(status, stat).save(W / "gi_base_status_v4.png")
big = lambda p, b: Image.open(p).convert("RGB").crop(b)
s = Image.new("RGB", (64 * 6 * 2 + 30 + 64 * 4, 64 * 6), (40, 40, 40))
s.paste(big(W / "gi_base_dialog_v4.png", (0, 0, 64, 64)).resize((384, 384), Image.NEAREST), (0, 0))
s.paste(big(W / "gi_base_status_v4.png", (0, 0, 64, 64)).resize((384, 384), Image.NEAREST), (394, 0))
s.paste(gp._indexed(gp.portrait(rom, 94), obj).convert("RGB").resize((256, 256), Image.NEAREST), (788, 0))
s.save(W / "v4.png")
print("ok, status err", max(c["status_err"] for c in rep))
