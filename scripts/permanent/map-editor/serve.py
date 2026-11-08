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
         POST /api/save         {"name", "doc", "retire", "replace"} through map_file.save, into maps\
         GET /api/stamps        the stamp library, every file in library\
         GET /api/stampname     the name an unnamed grab proposes, from next_stamp_name
         POST /api/stamp        {"name", "cells", ..., "replace"} into library\<name>.json
         POST /api/stamp/delete {"name"}: the file MOVES to library\deleted\, it is never unlinked
         POST /api/stamp/strip  {"name"}: drop a stamp's collision, old copy to library\deleted\
         GET /api/autosaves     the autosaves that are NEWER than the saved map of the same name
         GET /api/autosave?name=         one of them, for a Restore
         POST /api/autosave     {"name", "session", "doc"}: the live document, into autosave\
SAVING:  a saved map goes to maps\<name>.json through map_file.save, which VALIDATES it. The
         browser never writes the file itself: a download would land in the Downloads folder and
         would skip the one gate that stops an unsound map reaching a ROM. The stamp library
         lives in library\, one file per stamp, because it outlives the open map: a stamp grabbed
         from a game map is placed in a blank one.
REPLACING: a name already in use is a QUESTION and not a refusal, for a map AND for a stamp,
         because saving one map again is how the owner works on it and grabbing one piece of art
         twice is normal. /api/save and /api/stamp answer {"taken": name} and the page asks him.
         His yes sends the same write with "replace": true, which MOVES the old file aside, into
         maps\older\ or library\deleted\, and never unlinks it. The new map is validated BEFORE
         anything moves, so a write that cannot happen never costs him the copy he already holds.
AUTOSAVE: a map the owner has not saved yet lived ONLY in the page's memory until 2026-11-07, when
         a reload he was told to make threw away an evening of composing. So the page writes the
         live document here on every change, debounced, and autosave\ is that safety net. It is
         NOT the saved-map folder: nothing in it is validated, nothing in it reaches /api/saved,
         and it is offered back on the next start rather than loaded in silence. An autosave is
         overwritten freely, which is the opposite of every other write in this file, because its
         whole job is to hold the newest state. The page's SESSION id is what keeps that safe: a
         write from a different session moves the file aside into autosave\older\ first, so a
         second tab, or a fresh page that ignored the offer, can never erase the work it declined.
DELETING: a stamp the owner deletes MOVES to library\deleted\. He spends minutes grabbing one, and
         a misclick must be recoverable by hand. stamps() globs library\*.json, which is not
         recursive, so the deleted ones are never offered again.
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
import os
import re
import sys
import threading
import time
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
AUTOSAVE_IN = "autosave"                    # the live document, overwritten; never a saved map
OLDER_IN = "older"                          # under autosave\ and maps\: a copy about to be lost
DELETED_IN = "deleted"                      # under library\: a stamp the owner removed, kept whole
UNSAFE = re.compile(r"[^A-Za-z0-9 _-]")     # a name is a file name, so it holds nothing else
NAME_MAX = 60
STAMP_DEFAULT = re.compile(r"^stamp (\d+)$")   # the name an unnamed grab proposes

# One writer at a time. ThreadingHTTPServer answers requests concurrently, and two autosave posts
# landing together would interleave a replace with a read of the same file.
WRITING = threading.Lock()


# ===== saved maps and the stamp library =====

def safe_name(name: str) -> str:
    """A name with no path in it. A separator or a dot never survives, so no write leaves here."""
    cleaned = UNSAFE.sub("", (name or "").strip())[:NAME_MAX].strip()
    if not cleaned:
        raise ValueError("a name needs a letter or a number. Letters, numbers, spaces, dashes and "
                         "underscores are kept and everything else is dropped")
    return cleaned


class NameTaken(FileExistsError):
    """A map or a stamp of this name is on disk. The page ASKS; it does not report a failure."""


def save_map(doc: dict, name: str, root: Path = HERE, replace: bool = False) -> tuple:
    """Write a map the owner composed, and say what it moved aside: (path, retired file name).

    A taken name raises NameTaken and writes NOTHING, so the page can ask rather than refuse.
    replace MOVES the old file into maps\\older\\ and never unlinks it, so a wrong yes costs a
    trip to a folder. The new document is VALIDATED BEFORE anything moves: an unsound map must
    never raise the question, and must never take the place of a sound map that is already saved.
    """
    folder = root / MAPS_IN
    folder.mkdir(exist_ok=True)
    path = folder / f"{safe_name(name)}.json"
    if not path.exists():
        map_file.save(doc, path)                        # validates, and "x" so it cannot overwrite
        return path, ""
    problems = map_file.validate(doc)
    if problems:
        raise ValueError("this document is not sound:\n  " + "\n  ".join(problems))
    if not replace:
        raise NameTaken(f'a map called "{path.stem}" is already saved.')
    with WRITING:
        retired = _retire_file(path, folder / OLDER_IN)  # the move frees the name for "x" below
        map_file.save(doc, path)
    return path, retired.name


def saved_maps(root: Path = HERE) -> list:
    """Every saved map by name. The glob is maps\\*.json and is NOT recursive, so a copy a replace
    moved into maps\\older\\ is never offered back as a map of its own."""
    folder = root / MAPS_IN
    return sorted(p.stem for p in folder.glob("*.json")) if folder.is_dir() else []


def load_map(name: str, root: Path = HERE) -> dict:
    return map_file.load(root / MAPS_IN / f"{safe_name(name)}.json")


def _check_stamp_groups(stamp: dict) -> None:
    r"""A stamp cell names either a pool tile or one of the stamp's OWN animated groups.

    Three cell forms, and the editor's cells.js owns them: null leaves what is under it,
    [chunk, tile, flips] is a tile of the shared pool, and {"g", "t", "f"} is tile "t" of the
    stamp's animated group "g". A group travels as PIXELS, in stamp["animated"], which is what
    lets a stamp place waving grass into a map that never held it. A cell naming a group the
    stamp does not carry would place nothing and say nothing, so it is refused here, at the one
    door every stamp goes through. The three-element form is untouched: every stamp grabbed
    before this change loads exactly as it did.
    """
    groups = stamp.get("animated") or []
    if not isinstance(groups, list):
        raise ValueError('a stamp\'s "animated" is a list of groups, or is absent')
    for layer, cells in (stamp.get("cells") or {}).items():
        for n, cell in enumerate(cells if isinstance(cells, list) else []):
            if cell is None or isinstance(cell, list):
                continue
            if not isinstance(cell, dict) or not isinstance(cell.get("g"), int) \
                    or not isinstance(cell.get("t"), int):
                raise ValueError(f"stamp cell {layer}[{n}] is {cell!r}, which is neither a "
                                 f"[chunk, tile, flips] pair nor an animated cell")
            if not 0 <= cell["g"] < len(groups):
                raise ValueError(f"stamp cell {layer}[{n}] names animated group {cell['g']}, and "
                                 f"this stamp carries {len(groups)}. Its pixels travel with it, "
                                 f"so a cell cannot name a group that is not here")
            tiles = map_file.group_tiles(groups[cell["g"]])
            if not 0 <= cell["t"] < tiles:
                raise ValueError(f"stamp cell {layer}[{n}] names tile {cell['t']} of an animated "
                                 f"group of {tiles} tiles")


def save_stamp(stamp: dict, root: Path = HERE, replace: bool = False) -> tuple:
    """One grabbed stamp, and what it moved aside: (path, retired file name).

    The library is files, so it survives the page and the open map. A taken name raises NameTaken
    and writes NOTHING, exactly as a saved map does: grabbing one piece of art a second time is
    normal, and a refusal only sends him hunting for a free name. replace MOVES the old file into
    library\\deleted\\, where the delete control already puts things, and the move frees the name
    for the "x" below, so no write here can ever land on top of a stamp.
    """
    if not isinstance(stamp, dict) or not isinstance(stamp.get("cells"), dict):
        raise ValueError("a stamp carries a name, a width, a height and a cells object")
    _check_stamp_groups(stamp)
    folder = root / STAMPS_IN
    folder.mkdir(exist_ok=True)
    stamp = {**stamp, "name": safe_name(stamp.get("name"))}
    path = folder / f"{stamp['name']}.json"
    retired = ""
    with WRITING:
        if path.exists():
            if not replace:
                raise NameTaken(f'a stamp called "{stamp["name"]}" is already in the library.')
            retired = _retire_file(path, folder / DELETED_IN).name
        with open(path, "x", encoding="utf-8") as handle:       # "x": never overwrite
            json.dump(stamp, handle)
    return path, retired


def next_stamp_name(root: Path = HERE) -> str:
    """The name an unnamed grab proposes: one past the highest "stamp N" this library has HELD.

    Numbering from the library COUNT was the defect. Once anything is deleted the count no longer
    matches the highest number in use, so the next grab proposed a name that was already taken.
    library\\deleted\\ is read too, so a number he deleted is never handed to a different stamp,
    and only the server can see that folder, which is why the page asks rather than counting.
    """
    folder = root / STAMPS_IN
    highest = 0
    for path in list(folder.glob("*.json")) + list((folder / DELETED_IN).glob("*.json")):
        found = STAMP_DEFAULT.match(path.stem)
        if found:
            highest = max(highest, int(found.group(1)))
    return f"stamp {highest + 1}"


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


def _retire_file(path: Path, folder: Path) -> Path:
    """Move a file out of the way, into folder, keeping both copies. Never overwrites."""
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / path.name
    if target.exists():
        target = folder / f"{path.stem}-{time.strftime('%Y%m%d-%H%M%S')}{path.suffix}"
    count = 1
    while target.exists():                              # two moves inside one second
        target = folder / f"{path.stem}-{time.strftime('%Y%m%d-%H%M%S')}-{count}{path.suffix}"
        count += 1
    os.replace(path, target)
    return target


def delete_stamp(name: str, root: Path = HERE) -> Path:
    """Remove a stamp from the library by MOVING it. A misclick stays recoverable by hand."""
    folder = root / STAMPS_IN
    path = folder / f"{safe_name(name)}.json"
    if not path.exists():
        raise FileNotFoundError(f'no stamp called "{safe_name(name)}" is in the library')
    with WRITING:
        return _retire_file(path, folder / DELETED_IN)


def strip_stamp(name: str, root: Path = HERE) -> dict:
    """Drop a stamp's collision grid and keep the old file in deleted\\, so the art survives a
    change of mind. A stamp that carries no collision paints no wall where it has no art."""
    folder = root / STAMPS_IN
    path = folder / f"{safe_name(name)}.json"
    if not path.exists():
        raise FileNotFoundError(f'no stamp called "{safe_name(name)}" is in the library')
    with WRITING:
        stamp = json.loads(path.read_text(encoding="utf-8"))
        if stamp.get("collision") is None:
            return stamp
        _retire_file(path, folder / DELETED_IN)
        stamp["collision"] = None
        with open(path, "x", encoding="utf-8") as handle:       # the move above freed the name
            json.dump(stamp, handle)
    return stamp


# ===== the autosave, which is the one thing standing between a reload and a lost evening =====

def autosave_key(title: str) -> str:
    """A file name for a document title. An unsafe character becomes a SPACE rather than nothing,
    so "map 7,15" and "map 71,5" stay two keys instead of collapsing into "map 715"."""
    return safe_name(UNSAFE.sub(" ", title or ""))


def autosave_write(body: dict, root: Path = HERE) -> dict:
    """Keep the live document. Unvalidated on purpose: work in progress is often not sound yet,
    and refusing to keep it is exactly the failure this folder exists to stop."""
    doc = body.get("doc")
    if not isinstance(doc, dict):
        raise ValueError("an autosave carries the document it is keeping")
    title = body.get("name") or ""
    key = autosave_key(title)
    session = str(body.get("session") or "")
    folder = root / AUTOSAVE_IN
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{key}.json"
    record = {"title": title, "session": session, "at": time.time(), "doc": doc}
    with WRITING:
        kept = None
        if path.exists() and _read_record(path).get("session") != session:
            # Another tab, or a page that was offered this file on start and did not take it.
            kept = _retire_file(path, folder / OLDER_IN).name
        part = path.with_name(f"{path.name}.part")
        part.write_text(json.dumps(record), encoding="utf-8")
        os.replace(part, path)                          # atomic, so a crash never halves the file
    return {"kept": key, "at": record["at"], "moved": kept}


def _read_record(path: Path) -> dict:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return record if isinstance(record, dict) else {}


def autosaves(root: Path = HERE) -> list:
    """Every autosave that is NEWER than the saved map of the same name, newest first.

    An autosave older than its saved map has nothing in it the owner does not already hold, so
    offering it would train him to dismiss the offer. One with no saved map at all is always
    offered: nothing else holds that work."""
    folder = root / AUTOSAVE_IN
    if not folder.is_dir():
        return []
    out = []
    # The lock, because a write replaces a file and Windows raises on a read that lands between
    # the two halves of that replace. The server answers requests on several threads.
    with WRITING:
        paths = sorted(folder.glob("*.json"))
        records = [(path, _read_record(path)) for path in paths]
    for path, record in records:
        if not record.get("doc"):
            continue
        saved = root / MAPS_IN / f"{path.stem}.json"
        saved_at = saved.stat().st_mtime if saved.exists() else None
        if saved_at is not None and record.get("at", 0) <= saved_at:
            continue
        out.append({"name": path.stem, "title": record.get("title") or path.stem,
                    "at": record.get("at", 0), "saved_at": saved_at})
    return sorted(out, key=lambda row: row["at"], reverse=True)


def autosave_read(name: str, root: Path = HERE) -> dict:
    with WRITING:                      # never read a file while a replace is halfway through it
        record = _read_record(root / AUTOSAVE_IN / f"{safe_name(name)}.json")
    if not record.get("doc"):
        raise FileNotFoundError(f'no autosave called "{safe_name(name)}" is kept')
    return record


def autosave_retire(title: str, root: Path = HERE) -> bool:
    """The work is in maps\\ now, so the net under it comes down. Returns whether one was there."""
    path = root / AUTOSAVE_IN / f"{autosave_key(title)}.json"
    if not path.exists():
        return False
    with WRITING:
        _retire_file(path, root / AUTOSAVE_IN / OLDER_IN)
    return True


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
    root = HERE                      # where maps\, library\ and autosave\ live. --data moves them
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
            return {"maps": saved_maps(self.root)}
        if path == "/api/load":
            doc = load_map(query.get("name", [""])[0], self.root)
            return {"doc": doc, "problems": map_file.validate(doc)}
        if path == "/api/stamps":
            return {"stamps": stamps(self.root)}
        if path == "/api/stampname":
            return {"name": next_stamp_name(self.root)}
        if path == "/api/autosaves":
            return {"autosaves": autosaves(self.root)}
        if path == "/api/autosave":
            record = autosave_read(query.get("name", [""])[0], self.root)
            # Validated for the NOTES panel and never refused: an autosave is offered back
            # whatever shape it is in, because the alternative is losing it.
            return {"doc": record["doc"], "title": record.get("title", ""),
                    "at": record.get("at", 0), "problems": map_file.validate(record["doc"])}
        return None

    def _write(self, path: str, body: dict) -> dict:
        if path == "/api/save":
            replace = body.get("replace") is True
            try:
                written, moved = save_map(body.get("doc"), body.get("name"), self.root, replace)
            except NameTaken:
                # A question and not a failure, so it carries no "error" and returns HERE. Nothing
                # was written, so nothing may be retired: a No must leave his net exactly as it is.
                return {"taken": safe_name(body.get("name"))}
            # Only after the real file is on disk. A refused save keeps its net. A failure to
            # retire is never fatal: the map IS saved, and reporting 400 for it would make the
            # owner save again under another name.
            try:
                retired = autosave_retire(body.get("retire") or "", self.root)
            except (OSError, ValueError):
                retired = False
            return {"saved": written.stem, "maps": saved_maps(self.root), "retired": retired,
                    "replaced": moved}
        if path == "/api/stamp":
            # The body IS the stamp, so "replace" is lifted out before it reaches the file.
            stamp = {key: value for key, value in body.items() if key != "replace"}
            try:
                kept, moved = save_stamp(stamp, self.root, body.get("replace") is True)
            except NameTaken:
                return {"taken": safe_name(body.get("name"))}     # a question, so it carries no error
            return {"kept": kept.stem, "replaced": moved}
        if path == "/api/stamp/delete":
            return {"deleted": body.get("name"),
                    "moved_to": str(delete_stamp(body.get("name"), self.root).parent.name),
                    "stamps": stamps(self.root)}
        if path == "/api/stamp/strip":
            return {"stamp": strip_stamp(body.get("name"), self.root)}
        if path == "/api/autosave":
            return autosave_write(body, self.root)
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
    ap.add_argument("--data", type=Path, default=HERE,
                    help="where maps\\, library\\ and autosave\\ live. A second server for a test "
                         "run points here, so it cannot touch the owner's own files.")
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args(argv)

    ensure_assets()
    Handler.rom = args.rom.read_bytes()
    Handler.root = args.data.resolve()
    url = f"http://{HOST}:{args.port}/"
    try:
        httpd = Server((HOST, args.port), partial(Handler))
    except OSError as problem:
        print(f"cannot serve on port {args.port}: {problem}\n"
              f"another map editor is probably still running. Stop it, or pass --port.")
        return
    with httpd:
        print(f"map editor on {url}   ROM: {args.rom.name}   files: {Handler.root}   Ctrl+C to stop")
        if not args.no_browser:
            threading.Timer(0.5, webbrowser.open, (url,)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")


if __name__ == "__main__":
    main(sys.argv[1:])
