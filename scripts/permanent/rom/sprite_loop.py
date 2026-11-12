r"""
sprite_loop.py - Build a looping GIF and a labelled strip from any list of frames.

Why:     every art round needs the same two pictures, and before this existed they were rebuilt in a
         one-time folder each time. docs\tool-index.md exists for the same reason.
Usage:   py -3.14 -P scripts\permanent\rom\sprite_loop.py <out_stem> <frame.png> [<frame.png>...]
                  [--ms=170] [--zoom=14] [--palette=<png>] [--label=a,b,c]
         Each option takes an equals sign. A space makes the value look like another frame.
Writes:  <out_stem>.gif and <out_stem>_strip.png
Size:    every frame in one call must be one size, because a gif holds one canvas. A mixed list is
         refused with exit 2 before anything is written. It used to PASS a 32 wide frame listed
         after a 16 wide one, comparing it at 16 wide and never checking half of it.
Checks:  decodes the GIF back and compares every pixel against the source frames, because a GIF is
         requantized and can never be compared by bytes. Pillow writes NO gif frame for a frame
         identical to the one before it, and extends that frame's duration instead, so a held pose
         makes the gif shorter than the list. Our frame index maps to the gif's own index, every
         frame is still compared, and the output line counts the held frames.
Rules:   reads only, apart from the two files it names.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

# ===== CONFIG =====
BG = (28, 28, 36)
PAPER = (18, 18, 24)
INK = (235, 235, 245)
MS, ZOOM = 170, 14


def shot(data, w, h, pal, zoom):
    """One frame at zoom, index 0 drawn as the sheet background rather than black."""
    im = Image.frombytes("P", (w, h), bytes(data))
    im.putpalette(pal)
    rgb = im.convert("RGB")
    px = rgb.load()
    for y in range(h):
        for x in range(w):
            if not data[y * w + x]:
                px[x, y] = BG
    return rgb.resize((w * zoom, h * zoom), Image.NEAREST)


def same(left, right) -> bool:
    """True when two frames carry the same pixels, which is what the encoder collapses."""
    return left.size == right.size and left.tobytes() == right.tobytes()


def holds(shots) -> int:
    """How many frames repeat the frame before them. Pillow writes no gif frame for those."""
    return sum(1 for n in range(1, len(shots)) if same(shots[n], shots[n - 1]))


def main(argv) -> int:
    args = [a for a in argv if not a.startswith("--")]
    opt = {a.split("=")[0]: a.split("=", 1)[-1] for a in argv if a.startswith("--")}
    if len(args) < 2:
        print(__doc__)
        return 2
    stem, paths = Path(args[0]), [Path(p) for p in args[1:]]
    ms, zoom = int(opt.get("--ms", MS)), int(opt.get("--zoom", ZOOM))
    labels = opt.get("--label", "").split(",") if opt.get("--label") else [p.stem for p in paths]

    pal = Image.open(Path(opt["--palette"]) if "--palette" in opt else paths[0]).getpalette()
    frames = []
    for p in paths:
        with Image.open(p) as im:
            frames.append((bytearray(im.tobytes()), *im.size))
    sizes = sorted({(fw, fh) for _, fw, fh in frames})
    if len(sizes) > 1:
        # A gif has ONE canvas, and the decode check compared every frame at frame 0's size, so a
        # 16 wide frame first made a 32 wide frame pass with half of it never compared.
        print(f"  the frames are not all one size: {sizes}. One gif holds one canvas, so this "
              f"would report a pass on a frame it never compared. Split them into two calls.")
        return 2
    w, h = frames[0][1], frames[0][2]
    shots = [shot(d, fw, fh, pal, zoom) for d, fw, fh in frames]

    shots[0].save(f"{stem}.gif", save_all=True, append_images=shots[1:],
                  duration=ms, loop=0, disposal=2)

    strip = Image.new("RGB", (len(shots) * (w * zoom + 8) + 8, h * zoom + 26), PAPER)
    d = ImageDraw.Draw(strip)
    for n, s in enumerate(shots):
        ox = 8 + n * (w * zoom + 8)
        strip.paste(s, (ox, 22))
        d.text((ox, 6), labels[n] if n < len(labels) else str(n), INK)
    strip.save(f"{stem}_strip.png")

    bad, held = 0, 0
    with Image.open(f"{stem}.gif") as g:
        if g.n_frames != len(shots) - holds(shots):
            print(f"  {stem}.gif holds {g.n_frames} frames against {len(shots)} sent "
                  f"and {holds(shots)} held: the encoder collapsed something else")
            return 1
        for n in range(len(shots)):
            if n and same(shots[n], shots[n - 1]):
                held += 1                     # this frame shares the GIF frame before it
            g.seek(n - held)
            got = g.convert("RGB").resize((w, h), Image.NEAREST).load()
            want = shots[n].resize((w, h), Image.NEAREST).load()
            bad += sum(1 for y in range(h) for x in range(w) if got[x, y] != want[x, y])
    note = f"   {held} held frame(s) share a gif frame" if held else ""
    print(f"  {stem}.gif and {stem}_strip.png   {len(shots)} frames   "
          f"gif decode check: {bad} of {len(shots) * w * h} px differ{note}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
