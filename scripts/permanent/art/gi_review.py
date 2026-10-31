r"""
gi_review.py - Review renderers for the gi art: strips, the two step sheets and the step GIFs.

Usage:   py -3 -I scripts\permanent\art\gi_review.py all      (from the LOG root, after gi_post.py all)
         Commands: all | strips | base_step | ssj2_step | gif   (all = the four renderers)
Input:   art\gi_base\, gi_ssj\, gi_ssj2\, gi_ssj_v2\, gi_ssj2_v2\ and art\vanilla-sets\set56 (the armor frames).
Output:  art\gi_ssj2_v2\review\a<anim>.png (strips), art\anim\base_to_ssj_step.png and
         base_to_ssj_step_<armor|gi>.gif, art\anim\ssj_to_ssj2_step.png and .gif.
         Review images only: nothing here feeds the build.
API:     strips(art) -> [names]      base_step(art) -> {row: frames}      ssj2_step(art) -> None
         step_gif(art, folder, anim) -> frames      run_all(art) -> None
Rules:   The background is BACKGROUND, a lime no palette index uses (index 13 is gray, so gray hides sprite pixels).
         Labels are black. Frames sit by their record dx/dy, so a geometry error shows as a jump.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P and -I omit the script folder

import log_paths  # noqa: E402

# ===== constants =====
ROOT = Path(__file__).resolve().parents[3]
ART = log_paths.ART
BACKGROUND = (191, 255, 7)
LABEL = (0, 0, 0)
RED, YELLOW = (255, 0, 0), (255, 220, 0)
STRIP_SCALE, CELL_W, CELL_H, ORIGIN_X, ORIGIN_Y = 3, 48, 44, 24, 36    # strips: 3x, 48x44 cell, sprite origin in the cell
STEP_SCALE = 6                                                        # step sheets and GIFs: 6x
FRAME_MS = 167
HOLD, CYCLES = 2, 4                                                   # GIF loop: frame 0 twice, frames 1-3 four times


# ===== strips =====

def load_keys(folder: Path) -> dict:
    man = json.loads((folder / "manifest.json").read_text())
    keys = {}
    for e in man:
        for k in e["keys"]:
            keys[k["anim"], k["dir"], k["index"]] = (folder / e["png"], k)
    return keys


def strip_cell(path: Path, k: dict) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    if k["attr1"] & 0x1000:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    c = Image.new("RGBA", (CELL_W, CELL_H), BACKGROUND + (255,))
    c.alpha_composite(im, (ORIGIN_X + k["dx"], ORIGIN_Y + k["dy"]))
    return c.resize((CELL_W * STRIP_SCALE, CELL_H * STRIP_SCALE), Image.NEAREST)


def strips(art: Path = ART) -> list:
    """Per animation, each direction row shows gi_ssj2 over gi_ssj2_v2 at 3x. Red box = flagged, yellow = shifted."""
    out = art / "gi_ssj2_v2" / "review"
    out.mkdir(exist_ok=True)
    s, cw, ch = STRIP_SCALE, CELL_W, CELL_H
    old, new = load_keys(art / "gi_ssj2"), load_keys(art / "gi_ssj2_v2")
    flags = {r["png"]: r["status"] for r in json.loads((art / "gi_ssj2_v2" / "transplant.json").read_text())}
    for a in sorted({k[0] for k in old}):
        dirs = sorted({k[1] for k in old if k[0] == a})
        n = max(k[2] for k in old if k[0] == a) + 1
        sheet = Image.new("RGB", (n * (cw * s + 6) + 40, len(dirs) * (2 * ch * s + 16) + 20), BACKGROUND)
        d = ImageDraw.Draw(sheet)
        d.text((4, 4), f"anim {a}: per direction, top = old, bottom = new (red box = flagged, yellow = shifted)", fill=LABEL)
        for r, dr in enumerate(dirs):
            y = 20 + r * (2 * ch * s + 16)
            d.text((4, y + 4), f"d{dr}", fill=LABEL)
            for i in range(n):
                if (a, dr, i) not in old:
                    continue
                x = 40 + i * (cw * s + 6)
                sheet.paste(strip_cell(*old[a, dr, i]), (x, y))
                sheet.paste(strip_cell(*new[a, dr, i]), (x, y + ch * s + 4))
                st = flags.get(new[a, dr, i][0].name, "")
                if st.startswith("flag") or "shift" in st:
                    d.rectangle((x, y + ch * s + 4, x + cw * s - 1, y + 2 * ch * s + 3),
                                outline=RED if st.startswith("flag") else YELLOW, width=2)
        sheet.save(out / f"a{a:02d}.png")
    names = sorted(p.name for p in out.glob("*.png"))
    print("strips:", len(names), "files in", out)
    return names


# ===== step sheets and GIFs =====

def anim_frames(folder: Path, anim: int) -> list:
    """[(RGBA image, key)] of one animation, dir 0, ordered by frame index."""
    man = json.loads((folder / "manifest.json").read_text())
    out = {}
    for e in man:
        for k in e.get("keys", [e]):
            if k["anim"] == anim and k["dir"] == 0:
                out[k["index"]] = (Image.open(folder / e["png"]).convert("RGBA"), k)
    return [out[i] for i in sorted(out)]


def gif_frames(frames: list) -> list:
    """RGB frames at 6x, each placed by its dx/dy on the lime background."""
    s = STEP_SCALE
    gif = []
    for im, k in frames:
        big = im.resize((im.width * s, im.height * s), Image.NEAREST)
        g = Image.new("RGBA", (48 * s, 44 * s), BACKGROUND + (255,))
        g.paste(big, ((k["dx"] + 16) * s, (k["dy"] + 34) * s), big)
        gif.append(g.convert("RGB"))
    return gif


def step_loop(gif: list) -> list:
    return [gif[0]] * HOLD + gif[1:] * CYCLES                         # start pose held, then the flash frames cycle


def save_gif(loop: list, path: Path) -> None:
    loop[0].save(path, save_all=True, append_images=loop[1:], duration=FRAME_MS, loop=0)


def base_step(art: Path = ART) -> dict:
    """Base to SSJ step (anim 9 of the base set, dir 0): armor set 56 on top, gi set 157 below, by dx/dy at 6x."""
    s = STEP_SCALE
    anim = art / "anim"
    anim.mkdir(exist_ok=True)
    rows = {"armor": anim_frames(log_paths.SPRITES / "set56", 9), "gi": anim_frames(art / "gi_base", 9)}
    sheet = Image.new("RGB", (4 * 40 * s, 2 * 40 * s + 20), BACKGROUND)
    for r, (name, fr) in enumerate(rows.items()):
        for i, (im, k) in enumerate(fr):
            big = im.resize((im.width * s, im.height * s), Image.NEAREST)
            sheet.paste(big, (i * 40 * s + (k["dx"] + 12) * s, 20 + r * 40 * s + (k["dy"] + 28) * s), big)
        save_gif(step_loop(gif_frames(fr)), anim / f"base_to_ssj_step_{name}.gif")
    ImageDraw.Draw(sheet).text((4, 4), "base to SSJ step (anim 9), dir 0. Top: armor set 56 (game). Bottom: gi set 157", fill=LABEL)
    sheet.save(anim / "base_to_ssj_step.png")
    counts = {n: len(f) for n, f in rows.items()}
    print("base step:", counts)
    return counts


def ssj2_step(art: Path = ART) -> None:
    """Set 158 anim 9 sheet: old (gi_ssj) on top, new (gi_ssj_v2) below, placed by dx/dy at 6x."""
    s = STEP_SCALE
    anim = art / "anim"
    anim.mkdir(exist_ok=True)
    rows = [anim_frames(art / "gi_ssj", 9), anim_frames(art / "gi_ssj_v2", 9)]
    sheet = Image.new("RGB", (4 * 40 * s, 2 * 40 * s + 20), BACKGROUND)
    for r, fr in enumerate(rows):
        for i, (im, k) in enumerate(fr):
            big = im.resize((32 * s, 32 * s), Image.NEAREST)
            sheet.paste(big, (i * 40 * s + 4 * s, 20 + r * 40 * s + (k["dy"] + 28) * s), big)
    ImageDraw.Draw(sheet).text((4, 4), "set 158 anim 9 (SSJ to SSJ2 step), dir 0. Top: old. Bottom: new (golden SSJ2 head)", fill=LABEL)
    sheet.save(anim / "ssj_to_ssj2_step.png")
    print("ssj2 step sheet written")


def step_gif(art: Path = ART, folder: str = "gi_ssj_v2", anim: int = 9) -> list:
    """GIF of the SSJ to SSJ2 step only: set 158 anim 9, dir 0, frame 0 held, frames 1-3 cycle 4 times."""
    out = art / "anim"
    out.mkdir(exist_ok=True)
    loop = step_loop(gif_frames(anim_frames(art / folder, anim)))
    save_gif(loop, out / "ssj_to_ssj2_step.gif")
    print("step gif:", len(loop), "frames")
    return loop


# ===== CLI =====

def run_all(art: Path = ART) -> None:
    strips(art)
    base_step(art)
    ssj2_step(art)
    step_gif(art)


COMMANDS = {"all": run_all, "strips": strips, "base_step": base_step, "ssj2_step": ssj2_step, "gif": step_gif}


def main(argv: list) -> int:
    if len(argv) != 1 or argv[0] not in COMMANDS:
        print(__doc__.split("Input:")[0])
        return 2
    COMMANDS[argv[0]]()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
