r"""
serve.py - Run the map editor: a local file server plus the three ROM reads the page needs.

Usage:   py -3.14 -P scripts\permanent\map-editor\serve.py
         It exports the tile assets on a first run, then opens http://127.0.0.1:8777/ in a browser.
         --port N picks another port. --no-browser skips the open. --rom PATH serves a build instead
         of the base ROM, so an appended map can be opened.
--rom:   the tile atlases are exported ONCE, from the base ROM's chunk pool. A build may give a map
         its own chunk table, as r40's map 14,4 does at 0x0890A92C, and that map's chunk k is then
         not the base pool's chunk k. /api/map reports that as a problem rather than drawing the
         wrong art in silence. See borrowed_pool.
Routes:  GET /                  the editor page and its files, from THIS folder only
         GET /api/maps          [{zone, area, variations}] from the live map table
         GET /api/map?zone=&area=&var=   {"doc": ..., "problems": [...]} from map_file.read_map
         GET /api/blank?bw=&bh=          the same for a new empty map
         GET /api/saved         the maps the owner has saved, by name
         GET /api/load?name=    one of them, through map_file.load
         POST /api/save         {"name", "doc"} through map_file.save, into maps\
         GET /api/stamps        the stamp library, every file in library\
         POST /api/stamp        one grabbed stamp into library\<name>.json
SAVING:  a saved map goes to maps\<name>.json through map_file.save, which VALIDATES it and
         refuses to overwrite. The browser never writes the file itself: a download would land in
         the Downloads folder and would skip the one gate that stops an unsound map reaching a
         ROM. The stamp library lives in library\, one file per stamp, because it outlives the
         open map: a stamp grabbed from a game map is placed in a blank one.
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
import re
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
import tile_stream                                    # noqa: E402

# ===== CONFIG =====
HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
HOST, PORT = "127.0.0.1", 8777
MAPS_IN, STAMPS_IN = "maps", "library"      # folders beside this file, made on the first save
UNSAFE = re.compile(r"[^A-Za-z0-9 _-]")     # a name is a file name, so it holds nothing else
NAME_MAX = 60


# ===== saved maps and the stamp library =====

def safe_name(name: str) -> str:
    """A name with no path in it. A separator or a dot never survives, so no write leaves here."""
    cleaned = UNSAFE.sub("", (name or "").strip())[:NAME_MAX].strip()
    if not cleaned:
        raise ValueError("a name needs a letter or a number. Letters, numbers, spaces, dashes and "
                         "underscores are kept and everything else is dropped")
    return cleaned


def save_map(doc: dict, name: str, root: Path = HERE) -> Path:
    """Write a map the owner composed. map_file.save validates it and never overwrites."""
    folder = root / MAPS_IN
    folder.mkdir(exist_ok=True)
    path = folder / f"{safe_name(name)}.json"
    if path.exists():
        raise FileExistsError(f'a map called "{path.stem}" is already saved. Pick another name.')
    map_file.save(doc, path)
    return path


def saved_maps(root: Path = HERE) -> list:
    folder = root / MAPS_IN
    return sorted(p.stem for p in folder.glob("*.json")) if folder.is_dir() else []


def load_map(name: str, root: Path = HERE) -> dict:
    return map_file.load(root / MAPS_IN / f"{safe_name(name)}.json")


def save_stamp(stamp: dict, root: Path = HERE) -> Path:
    """One grabbed stamp. The library is files, so it survives the page and the open map."""
    if not isinstance(stamp, dict) or not isinstance(stamp.get("cells"), dict):
        raise ValueError("a stamp carries a name, a width, a height and a cells object")
    folder = root / STAMPS_IN
    folder.mkdir(exist_ok=True)
    stamp = {**stamp, "name": safe_name(stamp.get("name"))}
    path = folder / f"{stamp['name']}.json"
    if path.exists():
        raise FileExistsError(f'a stamp called "{stamp["name"]}" is already in the library. '
                              f"Pick another name.")
    with open(path, "x", encoding="utf-8") as handle:           # "x": never overwrite
        json.dump(stamp, handle)
    return path


def stamps(root: Path = HERE) -> list:
    """Every stamp in the library. A file that will not parse is left out rather than fatal."""
    folder = root / STAMPS_IN
    if not folder.is_dir():
        return []
    out = []
    for path in sorted(folder.glob("*.json")):
        try:
            out.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            print(f"library: {path.name} will not parse, so it is not offered")
    return out


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


def borrowed_pool(rom: bytes, zone: int, area: int, var: int) -> list:
    """A problem when this map's chunk table is not the pool the atlases were exported from.

    The atlases come from the BASE ROM's pool at tile_stream.CHUNK_TABLE, once. A build may give a
    map its own table: r40's map 14,4 names 0x0890A92C. That map's chunk k is then NOT the base
    pool's chunk k, and the page would draw the wrong art with no sign of it, which is the spec's
    anti-goal. So it is reported, and the map still opens."""
    _index, entry = scene_probe.map_entry(rom, zone, area)
    table = tile_stream.chunk_table_of(rom, map_view.layout_of(rom, entry, var))
    if table == tile_stream.CHUNK_TABLE:
        return []
    return [f"map {zone},{area} names its own chunk table at 0x{table:08X}, and the tile atlases "
            f"come from the base pool at 0x{tile_stream.CHUNK_TABLE:08X}. Every tile this map "
            f"draws may be the wrong one. Re-export the assets from this ROM to edit it."]


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


class Server(ThreadingHTTPServer):
    """One server per port, loudly.

    ThreadingHTTPServer sets allow_reuse_address, and on Windows that lets a SECOND process bind a
    port a first process already holds. Measured 2026-11-07: a second run on 8777 started with no
    error while the first was serving, and the two then split the requests between them. A stale
    server left by an earlier session would therefore answer some of the owner's reads from an old
    ROM. Refusing the bind makes that a message on the console instead."""
    allow_reuse_address = False


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
            zone, area, var = number("zone"), number("area"), number("var", 1)
            doc = map_file.read_map(self.rom, zone, area, var)
            return {"doc": doc,
                    "problems": borrowed_pool(self.rom, zone, area, var) + map_file.validate(doc)}
        if path == "/api/blank":
            bw, bh = number("bw"), number("bh")
            doc = map_file.blank((bw, bh), (bw * map_file.BLOCK_PIXELS, bh * map_file.BLOCK_PIXELS))
            return {"doc": doc, "problems": map_file.validate(doc)}
        if path == "/api/saved":
            return {"maps": saved_maps()}
        if path == "/api/load":
            doc = load_map(query.get("name", [""])[0])
            return {"doc": doc, "problems": map_file.validate(doc)}
        if path == "/api/stamps":
            return {"stamps": stamps()}
        return None

    def _write(self, path: str, body: dict) -> dict:
        if path == "/api/save":
            return {"saved": save_map(body.get("doc"), body.get("name")).stem,
                    "maps": saved_maps()}
        if path == "/api/stamp":
            return {"kept": save_stamp(body).stem}
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

    def do_POST(self):                                   # noqa: N802  (the base class names it)
        """The two writes. Every refusal reaches the page as text the owner can act on."""
        parsed = urlparse(self.path)
        try:
            size = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(size) or b"{}")
            payload = self._write(parsed.path, body)
        except (ValueError, FileExistsError, OSError) as problem:
            return self._json({"error": f"{problem}"}, 400)
        if payload is None:
            return self._json({"error": f"no route {parsed.path}"}, 404)
        return self._json(payload)


def ensure_assets() -> None:
    """Export the tile atlases on a first run. Without them the page opens with an empty palette."""
    if (ASSETS / "assets.json").exists():
        return
    print(f"exporting the tile assets to {ASSETS} (first run: 168 atlases, 1 MB, measured 1.5 s)")
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
    try:
        httpd = Server((HOST, args.port), partial(Handler))
    except OSError as problem:
        print(f"cannot serve on port {args.port}: {problem}\n"
              f"another map editor is probably still running. Stop it, or pass --port.")
        return
    with httpd:
        print(f"map editor on {url}   ROM: {args.rom.name}   Ctrl+C to stop")
        if not args.no_browser:
            threading.Timer(0.5, webbrowser.open, (url,)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")


if __name__ == "__main__":
    main(sys.argv[1:])
