r"""
serve.py - Run the map editor: a local file server plus the three ROM reads the page needs.

Usage:   py -3.14 -P scripts\permanent\map-editor\serve.py
         It exports the tile assets on a first run, then opens http://127.0.0.1:8777/ in a browser.
         --port N picks another port. --no-browser skips the open. --rom PATH serves a build instead
         of the base ROM, so an appended map can be opened.
Routes:  GET /                  the editor page and its files, from THIS folder only
         GET /api/maps          [{zone, area, variations}] from the live map table
         GET /api/map?zone=&area=&var=   {"doc": ..., "problems": [...]} from map_file.read_map
         GET /api/blank?bw=&bh=          the same for a new empty map
Why a server: a page on file:// cannot fetch its own assets.json, and the ROM reads belong in Python,
         which already owns every structure. The browser composes and nothing else.
ONE SHAPE: /api/blank calls map_file.blank rather than building a document in JavaScript. A second
         copy of the document shape in another language is how the two drift apart.
MIME:     .js is forced to text/javascript. Windows maps it to text/plain through the registry on many
         machines, and the browser then refuses every ES module and shows a blank page with no clue.
CACHE:    every response is no-store, so an edit to a .js file shows on a reload rather than hiding
         behind the browser cache.
Read-only on the ROM, and nothing here writes under data\.
"""
import argparse
import json
import sys
import threading
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

for _folder in (Path(__file__).resolve().parent, Path(__file__).resolve().parents[1]):
    sys.path.insert(0, str(_folder))                  # -P omits the script folder; scene\ is one up

from scene import map_view                            # noqa: E402
from scene import scene_probe                         # noqa: E402
import export_assets                                  # noqa: E402
import map_file                                       # noqa: E402

# ===== CONFIG =====
HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
HOST, PORT = "127.0.0.1", 8777


def map_names() -> dict:
    """"zone,area" -> the name this project recorded, from docs\\research\\map-names.md.

    The file is optional and the picker works without it. Nothing here decodes the ROM's name pool:
    a plain string walk of rom:0xE2840 reads map 7,15 as Triceratops Jungle, which belongs to 4,50,
    so the pool is not a flat list and a decode would label every map wrong."""
    source = HERE.parents[2] / "docs" / "research" / "map-names.md"
    if not source.exists():
        return {}
    names = {}
    for line in source.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) != 4 or cells[1] in ("name", "---") or not cells[2]:
            continue
        for pair in cells[2].split():
            names[pair] = cells[1]
    return names


def map_list(rom: bytes) -> list:
    """Every map in THIS ROM's table, in table order, with the variation count the picker shows.

    The table base and count are read from the live ROM by scene_probe.map_table, so a build that
    relocated its table lists its own appended maps instead of the base ROM's dead copy."""
    table, count = scene_probe.map_table(rom)
    names, out = map_names(), []
    for k in range(count):
        at = table + scene_probe.MAP_SIZE * k
        zone, area = rom[at], rom[at + 1]
        out.append({"zone": zone, "area": area, "variations": rom[at + 0x02],
                    "name": names.get(f"{zone},{area}", "")})
    return out


class Handler(SimpleHTTPRequestHandler):
    """The editor's files, plus the /api reads. Everything outside this folder is unreachable."""

    rom = b""
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map,
                      ".js": "text/javascript", ".css": "text/css",
                      ".json": "application/json", ".png": "image/png"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(HERE), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        """One line per API call and per failure. 168 atlas requests would bury both."""
        quiet = len(args) > 1 and str(args[1]).startswith("2") and "/api/" not in str(args[0])
        if not quiet:
            super().log_message(fmt, *args)

    def _json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _route(self, path: str, query: dict) -> dict:
        def number(name, fallback=None):
            return int(query.get(name, [fallback])[0])

        if path == "/api/maps":
            return {"maps": map_list(self.rom)}
        if path == "/api/map":
            doc = map_file.read_map(self.rom, number("zone"), number("area"), number("var", 1))
            return {"doc": doc, "problems": map_file.validate(doc)}
        if path == "/api/blank":
            bw, bh = number("bw"), number("bh")
            doc = map_file.blank((bw, bh), (bw * map_file.BLOCK_PIXELS, bh * map_file.BLOCK_PIXELS))
            return {"doc": doc, "problems": map_file.validate(doc)}
        return None

    def do_GET(self):                                    # noqa: N802  (the base class names it)
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/api/"):
            return super().do_GET()
        try:
            payload = self._route(parsed.path, parse_qs(parsed.query))
        except Exception as problem:                     # a bad map number must reach the page, not the log
            return self._json({"error": f"{type(problem).__name__}: {problem}"}, 400)
        if payload is None:
            return self._json({"error": f"no route {parsed.path}"}, 404)
        return self._json(payload)


def ensure_assets() -> None:
    """Export the tile atlases on a first run. Without them the page opens with an empty palette."""
    if (ASSETS / "assets.json").exists():
        return
    print(f"exporting the tile assets to {ASSETS} (first run, about a minute)")
    export_assets.export(map_view.BASE.read_bytes(), ASSETS)


def main(argv: list) -> None:
    ap = argparse.ArgumentParser(description="Run the LOG map editor on this machine.")
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--rom", type=Path, default=map_view.BASE, help="serve a build instead of the base ROM")
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args(argv)

    ensure_assets()
    Handler.rom = args.rom.read_bytes()
    url = f"http://{HOST}:{args.port}/"
    with ThreadingHTTPServer((HOST, args.port), partial(Handler)) as httpd:
        print(f"map editor on {url}   ROM: {args.rom.name}   Ctrl+C to stop")
        if not args.no_browser:
            threading.Timer(0.5, webbrowser.open, (url,)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")


if __name__ == "__main__":
    main(sys.argv[1:])
