r"""
plateau.py - Trial patch: map 7,100, a plateau TOP for the final fight, and the ending moves onto it.

Usage:   py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_plateau.txt --out <new .gba>
Input:   the ROM after build_list_trial_future.txt (dev r41, battle_arena, ending_fight, future_androids).
         It must run LAST of the four: it appends to the map table a THIRD time, it reads the live table
         base from the literal rom:0xEBD8 and the live count from rom:0xE0AE, and it edits one byte of
         the record ending_fight placed at ending table word 13.
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["plateau"], every write as
         (offset, length, name) in its "sites". `generate(rom)` returns the same tilemaps the patch
         writes, so a render and the ROM can never drift apart.

The design, in the owner's words (2026-11-07): "the entire middle section where the fight its all
closed off", "cell and trunks will be boxed in on a hill, surrounded by other hills and a rocky
cavern below", "maybe replace some of the side areas with actual clifs".

         1. THE ARENA IS THE TOP OF A PLATEAU, not a field inside a fence. The playable area is one
            closed irregular shape. Its boundary is a DROP: the player sees a stone lip, then lower
            ground far below. A drop explains itself, so he never asks why he cannot walk on.
         2. Map 7,15, the Vegeta against Android 19 field, is the source of every tile. Its BG3 is the
            base ground and its BG2 the raised terrain, each a 5 x 4 block grid. The clone grows both
            to 5 x 5, 1280 x 1280 px, and keeps 7,15's tile stream `+0x48`, chunk table `+0x4C` and
            ANIMATED tile group `+0x0C`/`+0x10`, so entry 0x037E, the animated grass in the motif's
            even row slot 2, keeps working.
         3. The grass, the stone lip, the plain ground weave, the ground detail and the rock
            formations are all read out of map 7,15 at build time and re-laid. No pixel is authored.
         4. The lip is an AUTOTILE keyed on the 8 neighbour mask, read from 7,15's own blob edges, so
            the arena rim and every satellite top get the edge tile vanilla would have used.
         5. Beyond the drop: lower ground, a cliff line following the arena rim, cliff groups in the
            side areas, a rock cavern in the south east, and further plateau tops near the map edge,
            so the eye reads depth. None of it is walkable, so none of it can be a gameplay mistake.
         6. COLLISION FOLLOWS THE ART. Open on the arena top and nowhere else. Every closed cell that
            touches an open one draws the lip, so the player never stops against nothing.
         7. The camera bound is written, not inherited. `Scene_BuildLayers` @0x08006152 reads layout
            `+0x08` and `+0x0A`, subtracts 1 and stores them at map view `+0x5C`/`+0x5E`, and the clamp
            `sub_080062E8` holds the camera there. For 1280 x 1280 that is (1041, 1121), so the view
            reaches the whole map. Map 7,15's own pair, (713, 609), would hide the east and south.
         8. BG0 and BG1 keep map 7,15's own record header, grid and scroll words and point EVERY block
            at one shared blank frame. BG1 is 7,15's priority 1 over-layer and would draw over the
            player. A blank frame is a block of entry 0, and tile 0 is 64 zero pixels (checked).
         9. The map entry is a COPY OF THE LIVE 6,100 ENTRY with two words changed: +0x00 to zone 7 and
            +0x2C to the plateau's own layout array. It carries combat 1, banner 0xDD, music 38, 0
            regions and battle_arena's own 2 item list.
        10. The ending reaches it through ONE byte. Record A loads the arena with
            `ext 39 (6, 100, 1, 248, 624)`; zigzag(6) is 0x0C and zigzag(7) is 0x0E, both one byte, so
            the zone byte 0x0C becomes 0x0E and no record moves.
Rules:   Every source byte is checked before the first write; a second run raises. No vanilla map entry,
         item, layout, layer record or tile is written. The ONE base overlap with the earlier modules is
         the 4 map table literals and the count byte, which is how each relocation hands the table on.
         The ONE expansion overlap is the single zone byte inside ending_fight's record A.
"""
import hashlib
import math
import struct

from rom.webfoot_decompress import decompress, unpack_frame
from rom.webfoot_lz_pack import pack
from scene.scene_lib import ext, record_end, words_naming

# ===== constants: the map table, read LIVE =====
ROM_BASE = 0x08000000
MAP_SIZE = 56
MAP_BASE_LITERAL, MAP_COUNT_BYTE = 0xEBD8, 0xE0AE
BASE_LITERALS = (0x5ADC, 0x5D5C, 0xEBD8)
ENTRY3, ENTRY3_LITERAL = 3, 0x195C
COUNT_FN = 0xE0AC
COUNT_CODE_HEAD, COUNT_CODE_TAIL = bytes.fromhex("ff20"), bytes.fromhex("307047")
MAP_COUNT_CAP = 0xFF + 0xFE

F_ZONE, F_AREA, F_VARIATIONS, F_REGION_COUNT, F_ITEM_COUNT = 0, 1, 2, 3, 4
F_COMBAT, F_BANNER, F_REGIONS, F_ITEMS = 8, 0x0C, 0x10, 0x14
F_MARKERS, F_MUSIC, F_LAYOUTS, F_ENTER, F_LEAVE = 0x20, 0x24, 0x2C, 0x30, 0x34

L_CLAMP, L_ANIM_COUNT, L_ANIM_LIST = 0x08, 0x0C, 0x10
L_BG0, L_BG1, L_BG2, L_BG3 = 0x14, 0x18, 0x1C, 0x20
L_PROP_COUNT, L_PROP_LIST, L_PROP_SHEET, L_COLLISION = 0x24, 0x28, 0x2C, 0x34
L_WARP_COUNT, L_WARP_LIST, L_TILE_STREAM, L_TILE_TABLE = 0x40, 0x44, 0x48, 0x4C
LAYOUT_SIZE = 0xCC

LAYER_CLASS = 0x080056A1
LAYER_GRID, LAYER_PTRS = 0x14, 0x18
BLOCK_TILES, BLOCK_SIZE = 32, 0x800
ENTRY_TILE = 0x3FF

# ===== constants: map 7,15, the source =====
SOURCE_ZONE, SOURCE_AREA = 7, 15
SOURCE_LAYOUTS, SOURCE_LAYOUT = 0x3FD368, 0x5A1324
SOURCE_LAYERS = (0x59D740, 0x59EC48, 0x59FBAC, 0x5A0E78)        # BG0, BG1, BG2, BG3
SOURCE_GRIDS = ((1, 1), (4, 4), (5, 4), (5, 4))
SOURCE_PROPS, SOURCE_PROP_LIST, SOURCE_PROP_SHEET = 6, 0x5A1284, 0x504A2C
SOURCE_COLLISION = 0x5A1008
SOURCE_TILE_STREAM, SOURCE_TILE_TABLE = 0x5A0EE0, 0x4DF574
SOURCE_TILES, SOURCE_TILES_SHA1 = 633, None     # the sha1 is pinned by _check_source at first run
SOURCE_CLAMP = (713, 609)
BLANK_TILE = 0
BASE_SLOT, RAISED_SLOT = 3, 2                   # on map 7,15: BG3 is the ground, BG2 the raised land

# ===== constants: the motifs, measured out of map 7,15 =====
GRASS_EVEN = (0x5F, 0x60, 0x37E, 0x61, 0x62, 0x63, 0x64, 0x65)
# Slot 2 is 0x037E. All 18 of its cells on map 7,15 sit at (even row, slot 2) and the map reads
# 0x5F 0x60 0x37E 0x61 0x62 in a line at ty 46, tx 74 to 78. Its tile index 894 is past the 633 tiles
# the static stream decodes, because the layout carries 1 ANIMATED tile group. It is animated grass.
GRASS_ODD = (0x57, 0x58, 0x59, 0x5A, 0x5B, 0x5C, 0x5D, 0x5E)
GRASS_PHASE, GRASS_SHEAR = 2, 4
GRASS = frozenset(GRASS_EVEN) | frozenset(GRASS_ODD)
PLAIN_GROUND = frozenset(range(0x66, 0x6F))     # the 9 tiles of 7,15's plain ground weave
BASE_MOTIF = 3                                  # the ground weave is sampled in 3 x 3 blocks

# ===== constants: the design =====
PLATEAU_ZONE, PLATEAU_AREA, PLATEAU_VARIATIONS = 7, 100, 1      # zone 7 uses areas 1..26
GRID = (5, 5)
MAP_TILES = (GRID[0] * BLOCK_TILES, GRID[1] * BLOCK_TILES)      # 160 x 160 tiles
MAP_PIXELS = (MAP_TILES[0] * 8, MAP_TILES[1] * 8)               # 1280 x 1280 px
VIEW = (240, 160)
CLAMP = (MAP_PIXELS[0] - VIEW[0] + 1, MAP_PIXELS[1] - VIEW[1] + 1)

# The arena top. It is pushed west of the map centre because the fight spots are, and its outline
# wobbles so it reads as land rather than as a fence.
ARENA_AT = (62.0, 74.0)
ARENA_AX, ARENA_AY, ARENA_N = 46.0, 50.0, 4.0
ARENA_LUMP = ((2, 0.7, 5.0), (3, 2.3, 4.2), (5, 1.1, 3.0), (7, 0.4, 1.8), (11, 2.0, 1.2))

# Satellite plateau tops beyond the drop: (centre x, centre y, radius) in cells. They are scenery.
SATELLITES = ((128, 26, 13), (132, 92, 11), (30, 130, 12), (92, 138, 10), (20, 24, 9),
              (142, 58, 8), (108, 148, 9), (14, 96, 8))

# Ground patches on the arena top, about 20 per cent of it.
CLUSTERS, CLUSTER_R, PER_CLUSTER = 26, 13, (18, 30)
PATCH_SIZES = (2, 3, 4, 5, 6, 8, 10, 13, 17, 22, 28, 36, 44, 55)
SPECK_RATE = 260
SMOOTH_PASSES = 3                               # rounds the stair steps off a grown patch outline

# The land beyond the drop.
RIM_CLIFF_STEP, RIM_CLIFF_OUT = 5, 9            # cells along the rim, and cells outside it
CAVERN_AT, CAVERN_R, CAVERN_N = (126, 126), 19, 16
SIDE_CLIFFS = ((14, 52), (10, 90), (22, 10), (150, 10), (152, 140), (60, 150), (30, 150),
               (148, 36), (6, 118), (112, 8), (84, 4), (44, 6), (8, 36), (6, 66), (12, 106),
               (36, 142), (84, 146), (120, 152), (154, 98), (152, 60), (144, 8), (66, 8),
               (28, 120), (18, 136), (100, 150), (140, 128), (8, 148), (156, 148))
BOULDERS = ((6, 20, 44), (7, 136, 12), (8, 30, 20), (9, 150, 116), (10, 8, 70), (11, 70, 142),
            (6, 118, 148), (7, 4, 150), (8, 154, 80), (9, 44, 138), (10, 156, 4), (11, 2, 4))

FIGHT_SPOTS = ((288, 392), (244, 504), (248, 568), (248, 624))
ENVELOPE = (20, 44, 56, 8)
FIGHT_CLEAR = 120                               # px: no cliff or boulder stands closer than this

FRAME_STRIDE, FRAME_SIZE, FRAME_CELLS = 32, 0x2000, 256
NEIGHBOURS = ((0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1))
NEAR4 = ((1, 0), (-1, 0), (0, 1), (0, -1))

# ===== constants: the modules this one composes on =====
ARENA = "battle_arena"
ENDING = "ending_fight"
ARENA_ZONE, ARENA_AREA = 6, 100
ARENA_MUSIC, ARENA_BANNER, ARENA_ITEMS = 38, 0xDD, 2
MAP_VARIATION = 1
TRUNKS_START = (248, 624)
OLD_LOAD = ext(39, ARENA_ZONE, ARENA_AREA, MAP_VARIATION, *TRUNKS_START)
NEW_LOAD = ext(39, PLATEAU_ZONE, PLATEAU_AREA, MAP_VARIATION, *TRUNKS_START)
LOAD_BYTE = 2


# ===== helpers =====

def _word(v: int) -> bytes:
    return struct.pack("<I", v)


def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _frame(rom: bytes, address: int) -> bytes:
    return unpack_frame(rom, address - ROM_BASE)[2]


def _packed_frame(payload: bytes) -> bytes:
    out = pack(payload, kind=1)
    if decompress(out, 8)[0] != payload or len(out) % 4:
        raise ValueError(f"the packed frame does not round trip, or is not 4 aligned ({len(out)} bytes)")
    return out


def _expect(rom: bytes, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _written(notes: dict) -> list:
    out = []
    for name, n in notes.items():
        for site in n.get("sites", []) if isinstance(n, dict) else []:
            out.append((name, (site, 1) if isinstance(site, int) else tuple(site)[:2]))
    return out


def map_table(rom: bytes) -> tuple:
    return _u32(rom, MAP_BASE_LITERAL) - ROM_BASE, 0xFF + rom[MAP_COUNT_BYTE]


def map_entry(rom: bytes, zone: int, area: int) -> tuple:
    table, count = map_table(rom)
    for k in range(count):
        at = table + MAP_SIZE * k
        if rom[at] == zone and rom[at + 1] == area:
            return k, at
    raise ValueError(f"no map {zone},{area} in the live map table rom:0x{table:X} ({count} entries)")


def spot_hash(tx: int, ty: int, salt: int) -> int:
    """A value that depends on the CELL, not on the scan order, so no generator period leaks."""
    v = (tx * 0x27D4EB2D) ^ (ty * 0x165667B1) ^ (salt * 0x9E3779B1)
    v &= 0xFFFFFFFF
    v ^= v >> 15
    v = (v * 0x2545F491) & 0xFFFFFFFF
    v ^= v >> 13
    return v


def source_tiles(rom: bytes) -> list:
    """Map 7,15's 8x8 tiles, in index order, decoded without Pillow. A build must not need it."""
    raw = _frame(rom, _u32(rom, SOURCE_LAYOUT + L_TILE_STREAM))
    idx = list(struct.unpack(f"<{len(raw) // 2}H", raw))
    for i in range(1, len(idx)):
        idx[i] = (idx[i] + idx[i - 1] + 1) & 0xFFFF
    table, chunks, out = _u32(rom, SOURCE_LAYOUT + L_TILE_TABLE) - ROM_BASE, {}, []
    for e in idx:
        hi, lo = e >> 8, e & 0xFF
        if hi not in chunks:
            chunks[hi] = _frame(rom, _u32(rom, table + 4 * hi))
        out.append(chunks[hi][64 * lo:64 * lo + 64])
    return out


def slot_reader(rom: bytes, slot: int):
    """(at(tx, ty), across tiles, down tiles) for one of map 7,15's BG slots."""
    rec = SOURCE_LAYERS[slot]
    across, down = rom[rec + LAYER_GRID], rom[rec + LAYER_GRID + 1]
    blocks = {}
    for k in range(across * down):
        at = _u32(rom, rec + LAYER_PTRS + 4 * k)
        blocks[k] = _frame(rom, at) if at else bytes(BLOCK_SIZE)   # a null block draws nothing

    def at(tx, ty):
        if not (0 <= tx < across * BLOCK_TILES and 0 <= ty < down * BLOCK_TILES):
            return 0
        k = (ty // BLOCK_TILES) * across + tx // BLOCK_TILES
        return struct.unpack_from("<H", blocks[k],
                                  2 * ((ty % BLOCK_TILES) * BLOCK_TILES + tx % BLOCK_TILES))[0]
    return at, across * BLOCK_TILES, down * BLOCK_TILES


# ===== learn: read the motifs out of map 7,15 =====

def learn(rom: bytes) -> dict:
    """Every piece the plateau is built from, read out of map 7,15 at build time.

    Classification is by ENTRY, never by colour, so no palette and no image library is needed. A cell
    DRAWS when its tile holds a non-zero byte, or when its tile index is past the static stream, which
    means an animated tile."""
    tiles = source_tiles(rom)
    base, tw, th = slot_reader(rom, BASE_SLOT)
    raised, _, _ = slot_reader(rom, RAISED_SLOT)

    def draws(e):
        n = e & ENTRY_TILE
        return n >= len(tiles) or any(tiles[n])

    def is_grass(tx, ty):
        return 0 <= tx < tw and 0 <= ty < th and raised(tx, ty) in GRASS

    # The plain ground weave, as whole aligned 3 x 3 blocks of clean vanilla ground, each kept with
    # the phase vanilla gave it. A block is taken only where nothing is raised above it.
    weave, detail, src_ground = [], {}, set()
    for ty in range(th):
        for tx in range(tw):
            if draws(raised(tx, ty)) or not draws(base(tx, ty)):
                continue
            src_ground.add((tx, ty))
            if base(tx, ty) & ENTRY_TILE not in PLAIN_GROUND:
                detail[base(tx, ty)] = detail.get(base(tx, ty), 0) + 1
    for by in range(0, th - BASE_MOTIF, BASE_MOTIF):
        for bx in range(0, tw - BASE_MOTIF, BASE_MOTIF):
            cells = [(bx + dx, by + dy) for dy in range(BASE_MOTIF) for dx in range(BASE_MOTIF)]
            if all(c in src_ground and base(*c) & ENTRY_TILE in PLAIN_GROUND for c in cells):
                weave.append([base(*c) for c in cells])

    # The lip autotile: what 7,15 draws at a grass boundary, keyed on the 8 neighbour grass mask.
    edge_in, edge_out = {}, {}
    for ty in range(th):
        for tx in range(tw):
            e = raised(tx, ty)
            if not draws(e):
                continue
            m = sum(1 << i for i, (dx, dy) in enumerate(NEIGHBOURS) if is_grass(tx + dx, ty + dy))
            if m in (0, 0xFF) and is_grass(tx, ty):
                continue
            table = edge_in if is_grass(tx, ty) else edge_out
            if m:
                table.setdefault(m, {})[e] = table.setdefault(m, {}).get(e, 0) + 1

    # Rock formations: connected runs of raised cells with no grass in them, small enough to copy.
    seen, donors = set(), []
    for ty in range(th):
        for tx in range(tw):
            if (tx, ty) in seen or not draws(raised(tx, ty)) or is_grass(tx, ty):
                continue
            if any(is_grass(tx + dx, ty + dy) for dx, dy in NEIGHBOURS):
                continue
            stack, cells = [(tx, ty)], set()
            while stack:
                c = stack.pop()
                if c in cells or not (0 <= c[0] < tw and 0 <= c[1] < th):
                    continue
                if not draws(raised(*c)) or is_grass(*c):
                    continue
                cells.add(c)
                stack += [(c[0] + dx, c[1] + dy) for dx, dy in NEIGHBOURS]
            seen |= cells
            x0, x1 = min(c[0] for c in cells), max(c[0] for c in cells)
            y0, y1 = min(c[1] for c in cells), max(c[1] for c in cells)
            if len(cells) < 12 or x1 - x0 > 20 or y1 - y0 > 14:
                continue
            donors.append({"w": x1 - x0 + 1, "h": y1 - y0 + 1, "n": len(cells), "from": (x0, y0),
                           "grid": {(c[0] - x0, c[1] - y0): raised(*c) for c in cells}})
    donors.sort(key=lambda d: -d["n"])
    return {"tiles": tiles, "draws": draws, "base": base, "raised": raised, "size": (tw, th),
            "weave": weave, "detail": detail, "src_ground": src_ground,
            "edge_in": edge_in, "edge_out": edge_out, "donors": donors}


# ===== the shapes =====

def grass_entry(tx: int, ty: int) -> int:
    row = GRASS_EVEN if ty % 2 == 0 else GRASS_ODD
    return row[(tx + GRASS_PHASE + GRASS_SHEAR * (ty // 2)) % len(row)]


def _lumpy(dx: float, dy: float, ax: float, ay: float, lump) -> bool:
    ang = math.atan2(dy, dx)
    bump = sum(c * math.sin(k * ang + p) for k, p, c in lump)
    a, b = ax + bump, ay + bump
    if a <= 0 or b <= 0:
        return False
    return (abs(dx) / a) ** ARENA_N + (abs(dy) / b) ** ARENA_N <= 1.0


def arena_cells() -> set:
    """The plateau top: one closed irregular shape, the only walkable ground on the map."""
    return {(tx, ty) for ty in range(MAP_TILES[1]) for tx in range(MAP_TILES[0])
            if _lumpy(tx - ARENA_AT[0], ty - ARENA_AT[1], ARENA_AX, ARENA_AY, ARENA_LUMP)}


def satellite_cells() -> set:
    """Further plateau tops beyond the drop. Scenery: nothing here is walkable."""
    out = set()
    for i, (cx, cy, r) in enumerate(SATELLITES):
        for ty in range(cy - r - 4, cy + r + 5):
            for tx in range(cx - r - 4, cx + r + 5):
                if not (0 <= tx < MAP_TILES[0] and 0 <= ty < MAP_TILES[1]):
                    continue
                ang = math.atan2(ty - cy, tx - cx)
                a = r + 2.3 * math.sin(3 * ang + i) + 1.2 * math.sin(5 * ang + 2 * i)
                if (tx - cx) ** 2 + (ty - cy) ** 2 <= a * a:
                    out.add((tx, ty))
    return out


def grow(seed, want, salt, limit):
    """A patch outline: flood from the seed, taking the lowest-noise neighbour each step."""
    blob, cand = set(), {seed}
    while cand and len(blob) < want:
        c = min(cand, key=lambda q: spot_hash(q[0], q[1], salt))
        cand.discard(c)
        if c not in limit:
            continue
        blob.add(c)
        for dx, dy in NEAR4:
            n = (c[0] + dx, c[1] + dy)
            if n in limit and n not in blob:
                cand.add(n)
    return blob


def smooth(blob, limit):
    """Round the axis-aligned stair steps off a grown outline.

    A cell with one neighbour or none is a spur and goes. A gap with three neighbours is filled. The
    owner called the unsmoothed shapes "excessive blocky patches"."""
    for _ in range(SMOOTH_PASSES):
        near8 = lambda c, s: sum((c[0] + dx, c[1] + dy) in s for dx, dy in NEIGHBOURS)
        keep = {c for c in blob if near8(c, blob) >= 4}
        edge = {(c[0] + dx, c[1] + dy) for c in blob for dx, dy in NEIGHBOURS} - blob
        add = {c for c in edge if c in limit and near8(c, blob) >= 5}
        blob = keep | add
    return blob


def _pick(counts, roll):
    total = sum(counts.values())
    r = roll % total
    for e, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        r -= n
        if r < 0:
            return e
    return next(iter(counts))


def _nearest(table, m):
    return table[m] if m in table else table[min(table, key=lambda k: bin(k ^ m).count("1"))]


def _clear_of_fight(cells) -> bool:
    for cx, cy in cells:
        for sx, sy in FIGHT_SPOTS:
            if max(abs(cx * 8 + 4 - sx), abs(cy * 8 + 4 - sy)) < FIGHT_CLEAR:
                return False
    return True


# ===== generate the two tilemaps and the collision =====

def generate(rules: dict) -> dict:
    """{base, raised, open, patches, formations}: everything the patch writes and a render draws."""
    arena = arena_cells()
    sats = satellite_cells() - {c for c in arena
                                for c in ((c[0] + dx, c[1] + dy) for dx in range(-4, 5)
                                          for dy in range(-4, 5))}
    sats -= arena
    high = arena | sats

    # 1. The base ground over the whole map, in 3 x 3 vanilla blocks, with one-cell detail over it.
    base = {}
    for by in range(0, MAP_TILES[1], BASE_MOTIF):
        for bx in range(0, MAP_TILES[0], BASE_MOTIF):
            block = rules["weave"][spot_hash(bx, by, 0x51A7) % len(rules["weave"])]
            for dy in range(BASE_MOTIF):
                for dx in range(BASE_MOTIF):
                    if bx + dx < MAP_TILES[0] and by + dy < MAP_TILES[1]:
                        base[(bx + dx, by + dy)] = block[dy * BASE_MOTIF + dx]
    for ty in range(MAP_TILES[1]):
        for tx in range(MAP_TILES[0]):
            if spot_hash(tx, ty, 0x9D1E) % 24 == 0:
                base[(tx, ty)] = _pick(rules["detail"], spot_hash(tx, ty, 0x31A7))

    # 2. The high ground: grass inside, the lip autotile on every boundary, inside and out.
    raised = {}
    for ty in range(MAP_TILES[1]):
        for tx in range(MAP_TILES[0]):
            m = sum(1 << i for i, (dx, dy) in enumerate(NEIGHBOURS)
                    if (tx + dx, ty + dy) in high)
            if (tx, ty) in high:
                raised[(tx, ty)] = (grass_entry(tx, ty) if m == 0xFF
                                    else _pick(_nearest(rules["edge_in"], m),
                                               spot_hash(tx, ty, 0x1B3)))
            elif m:
                raised[(tx, ty)] = _pick(_nearest(rules["edge_out"], m), spot_hash(tx, ty, 0x2C9))

    # 3. Ground patches on the arena top, clustered, grown and then smoothed.
    anchors = sorted(c for c in rules["src_ground"]
                     if all((c[0] + dx, c[1] + dy) in rules["src_ground"]
                            for dx in range(0, 10) for dy in range(0, 10)))
    field, holes, patches = set(arena), set(), []
    lo_c, hi_c = min(c[0] for c in field), max(c[0] for c in field)
    lo_r, hi_r = min(c[1] for c in field), max(c[1] for c in field)
    for k in range(CLUSTERS):
        h = spot_hash(k, 0x5EED, 0x11C7)
        cx = int(lo_c + (hi_c - lo_c) * ((h % 1000) / 1000.0))
        cy = int(lo_r + (hi_r - lo_r) * (((h >> 10) % 1000) / 1000.0))
        howmany = PER_CLUSTER[0] + (h >> 20) % (PER_CLUSTER[1] - PER_CLUSTER[0] + 1)
        for j in range(howmany):
            g = spot_hash(k * 31 + j, 0xA17E, 0x2F5B)
            ang = (g % 360) * math.pi / 180.0
            rad = (g >> 11) % CLUSTER_R
            seed = (int(cx + rad * math.cos(ang)), int(cy + rad * math.sin(ang)))
            apart = {(c[0] + dx, c[1] + dy) for c in holes for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
            room = field - apart
            if seed not in room:
                continue
            cells = smooth(grow(seed, PATCH_SIZES[(g >> 19) % len(PATCH_SIZES)],
                                0x3C00 + k * 17 + j, room), room)
            if not cells:
                continue
            ax, ay = anchors[(g >> 23) % len(anchors)]
            sx, sy = min(c[0] for c in cells), min(c[1] for c in cells)
            for c in cells:
                raised.pop(c, None)
                src = (ax + c[0] - sx, ay + c[1] - sy)
                base[c] = (rules["base"](*src) if src in rules["src_ground"]
                           else _pick(rules["detail"], spot_hash(c[0], c[1], 0x6B1 + k)))
            holes |= cells
            patches.append(len(cells))
    for ty in range(MAP_TILES[1]):                       # a few lone specks as grain between them
        for tx in range(MAP_TILES[0]):
            if (tx, ty) not in field or (tx, ty) in holes:
                continue
            if spot_hash(tx, ty, 0x51EC) % SPECK_RATE:
                continue
            if all((tx + dx, ty + dy) in arena for dx, dy in NEIGHBOURS):
                raised.pop((tx, ty), None)
                base[(tx, ty)] = _pick(rules["detail"], spot_hash(tx, ty, 0x7C3B))
                holes.add((tx, ty))
                patches.append(1)

    # 4. The land beyond the drop: a cliff line under the rim, cliff groups in the side areas, a rock
    #    cavern in the south east, and boulders. None of it is walkable, so none of it can go wrong.
    formations = []
    rim = sorted({c for c in high if any((c[0] + dx, c[1] + dy) not in high for dx, dy in NEAR4)})
    spots = []
    for i, (rx, ry) in enumerate(rim):
        if i % RIM_CLIFF_STEP:
            continue
        vx, vy = rx - ARENA_AT[0], ry - ARENA_AT[1]
        n = math.hypot(vx, vy) or 1.0
        spots.append((min(max(int(rx + RIM_CLIFF_OUT * vx / n), 6), MAP_TILES[0] - 7),
                      min(max(int(ry + RIM_CLIFF_OUT * vy / n), 6), MAP_TILES[1] - 7), "rim"))
    spots += [(x, y, "side") for x, y in SIDE_CLIFFS]
    for i in range(CAVERN_N):                            # the rocky cavern below, south east
        a = 2 * math.pi * i / CAVERN_N
        j = spot_hash(i, 0x3D1, 0x77)
        r = CAVERN_R + (j % 9) - 4
        spots.append((int(CAVERN_AT[0] + r * math.cos(a) * 0.95),
                      int(CAVERN_AT[1] + r * math.sin(a) * 0.65), "cavern"))
    for i, (tx, ty, what) in enumerate(spots):
        d = rules["donors"][spot_hash(tx, ty, 0x7A1 + i) % min(6, len(rules["donors"]))]
        cells = {(tx + cx - d["w"] // 2, ty + cy - d["h"] // 2): e
                 for (cx, cy), e in d["grid"].items()}
        cells = {c: e for c, e in cells.items()
                 if 0 <= c[0] < MAP_TILES[0] and 0 <= c[1] < MAP_TILES[1] and c not in high}
        if len(cells) < 5 or not _clear_of_fight(cells):
            continue
        raised.update(cells)
        formations.append((what, tx, ty, len(cells)))
    for which, tx, ty in BOULDERS:
        if which >= len(rules["donors"]):
            continue
        d = rules["donors"][which]
        cells = {(tx + cx, ty + cy): e for (cx, cy), e in d["grid"].items()
                 if 0 <= tx + cx < MAP_TILES[0] and 0 <= ty + cy < MAP_TILES[1]}
        if not cells or any(c in high for c in cells) or not _clear_of_fight(cells):
            continue
        raised.update(cells)
        formations.append(("boulder", tx, ty, len(cells)))

    # 5. Collision: the arena top and nothing else, reached by a flood so no pocket is left behind.
    opened, stack = set(), [(int(ARENA_AT[0]), int(ARENA_AT[1]))]
    while stack:
        c = stack.pop()
        if c in opened or c not in arena:
            continue
        opened.add(c)
        stack += [(c[0] + dx, c[1] + dy) for dx, dy in NEAR4]
    return {"base": base, "raised": raised, "open": opened, "arena": arena, "high": high,
            "patches": patches, "formations": formations, "holes": holes}


def collision(opened) -> bytes:
    out = bytearray(FRAME_SIZE)
    for cx, cy in opened:
        out[cy * FRAME_STRIDE + (cx >> 3)] |= 1 << (cx & 7)
    return bytes(out)


def is_open(bits: bytes, cx: int, cy: int) -> bool:
    if not (0 <= cx < FRAME_CELLS and 0 <= cy < FRAME_CELLS):
        return False
    return bool(bits[cy * FRAME_STRIDE + (cx >> 3)] & (1 << (cx & 7)))


def envelope_cells(spot: tuple) -> list:
    left, right, up, down = ENVELOPE
    return [(cx, cy) for cy in range((spot[1] - up) // 8, (spot[1] + down) // 8 + 1)
            for cx in range((spot[0] - left) // 8, (spot[0] + right) // 8 + 1)]


def blocks_of(cells: dict) -> dict:
    out = {}
    for k in range(GRID[0] * GRID[1]):
        ox, oy = (k % GRID[0]) * BLOCK_TILES, (k // GRID[0]) * BLOCK_TILES
        block = bytearray(BLOCK_SIZE)
        for t in range(BLOCK_TILES * BLOCK_TILES):
            e = cells.get((ox + t % BLOCK_TILES, oy + t // BLOCK_TILES), 0)
            struct.pack_into("<H", block, 2 * t, e)
        out[k] = bytes(block)
    return out


def layer_record(header: bytes, grid: tuple, block_at: dict) -> bytes:
    """A layer record: one of map 7,15's 0x18 byte headers, a new grid, and new block pointers."""
    out = bytearray(header[:LAYER_PTRS])
    out[LAYER_GRID], out[LAYER_GRID + 1] = grid
    for k in range(grid[0] * grid[1]):
        out += _word(block_at[k] + ROM_BASE)
    return bytes(out)


def plateau_layout(source: bytes, layers: dict, collision_at: int) -> bytes:
    """Map 7,15's layout with its doors and props dropped, its own collision, its own camera pair and
    three of its four layer records replaced. The animated tile group `+0x0C`/`+0x10` is CARRIED, so
    entry 0x037E keeps drawing; the tile stream `+0x48` and chunk table `+0x4C` are carried too."""
    out = bytearray(source)
    struct.pack_into("<HH", out, L_CLAMP, *CLAMP)
    out[L_WARP_COUNT:L_WARP_COUNT + 4] = _word(0)
    out[L_WARP_LIST:L_WARP_LIST + 4] = _word(0)
    out[L_PROP_COUNT:L_PROP_COUNT + 4] = _word(0)
    out[L_PROP_LIST:L_PROP_LIST + 4] = _word(0)
    out[L_COLLISION:L_COLLISION + 4] = _word(collision_at + ROM_BASE)
    for off, at in layers.items():
        out[off:off + 4] = _word(at + ROM_BASE)
    return bytes(out)


def plateau_entry(arena: bytes, layouts_at: int) -> bytes:
    out = bytearray(arena)
    out[F_ZONE] = PLATEAU_ZONE
    out[F_LAYOUTS:F_LAYOUTS + 4] = _word(layouts_at + ROM_BASE)
    return bytes(out)


# ===== checks =====

def _check_source(rom: bytearray) -> tuple:
    index, at = map_entry(rom, SOURCE_ZONE, SOURCE_AREA)
    _expect(rom, at + F_LAYOUTS, _word(SOURCE_LAYOUTS + ROM_BASE))
    _expect(rom, SOURCE_LAYOUTS, _word(SOURCE_LAYOUT + ROM_BASE))
    for off, want in ((L_BG0, SOURCE_LAYERS[0]), (L_BG1, SOURCE_LAYERS[1]), (L_BG2, SOURCE_LAYERS[2]),
                      (L_BG3, SOURCE_LAYERS[3]), (L_PROP_LIST, SOURCE_PROP_LIST),
                      (L_PROP_SHEET, SOURCE_PROP_SHEET), (L_COLLISION, SOURCE_COLLISION),
                      (L_TILE_STREAM, SOURCE_TILE_STREAM), (L_TILE_TABLE, SOURCE_TILE_TABLE)):
        _expect(rom, SOURCE_LAYOUT + off, _word(want + ROM_BASE))
    _expect(rom, SOURCE_LAYOUT + L_PROP_COUNT, _word(SOURCE_PROPS))
    _expect(rom, SOURCE_LAYOUT + L_WARP_COUNT, _word(0))
    if struct.unpack_from("<HH", rom, SOURCE_LAYOUT + L_CLAMP) != SOURCE_CLAMP:
        raise ValueError(f"map 7,15's camera pair is"
                         f" {struct.unpack_from('<HH', rom, SOURCE_LAYOUT + L_CLAMP)},"
                         f" expected {SOURCE_CLAMP}")
    if _u32(rom, SOURCE_LAYOUT + L_ANIM_COUNT) != 1:
        raise ValueError("map 7,15 no longer carries exactly 1 animated tile group, which entry"
                         " 0x037E depends on")
    namers = words_naming(rom, SOURCE_LAYOUTS)
    stray = [w for w in namers
             if (rom[w - F_LAYOUTS], rom[w - F_LAYOUTS + 1]) != (SOURCE_ZONE, SOURCE_AREA)]
    if at + F_LAYOUTS not in namers or stray:
        raise ValueError(f"map 7,15's layout array is named by {[hex(w) for w in namers]};"
                         f" {[hex(w) for w in stray]} are not map 7,15 entries")
    for n, rec in enumerate(SOURCE_LAYERS):
        if _u32(rom, rec) != LAYER_CLASS:
            raise ValueError(f"map 7,15's BG{n} rom:0x{rec:X} is class 0x{_u32(rom, rec):08X}")
        if (rom[rec + LAYER_GRID], rom[rec + LAYER_GRID + 1]) != SOURCE_GRIDS[n]:
            raise ValueError(f"map 7,15's BG{n} grid is"
                             f" {(rom[rec + LAYER_GRID], rom[rec + LAYER_GRID + 1])},"
                             f" expected {SOURCE_GRIDS[n]}")
    tiles = source_tiles(rom)
    sha = hashlib.sha1(b"".join(bytes(t) for t in tiles)).hexdigest()
    if len(tiles) != SOURCE_TILES:
        raise ValueError(f"map 7,15 decodes to {len(tiles)} tiles, expected {SOURCE_TILES}")
    if SOURCE_TILES_SHA1 and sha != SOURCE_TILES_SHA1:
        raise ValueError(f"map 7,15's tiles hash {sha}, expected {SOURCE_TILES_SHA1}")
    if any(tiles[BLANK_TILE]):
        raise ValueError(f"tile {BLANK_TILE} is not 64 zero pixels, so a blank block would draw")
    for e in sorted(GRASS):
        n = e & ENTRY_TILE
        if n < len(tiles) and not any(tiles[n]):
            raise ValueError(f"grass entry 0x{e:04X} names tile 0x{n:X}, which draws nothing")
    return index, sha


def _check_design(rom: bytearray, out: dict) -> None:
    bits = collision(out["open"])
    for spot in FIGHT_SPOTS:
        for cx, cy in envelope_cells(spot):
            if not is_open(bits, cx, cy):
                raise ValueError(f"the fight spot {spot} draws into the closed cell ({cx},{cy})")
    on_border = [c for c in out["open"]
                 if c[0] in (0, MAP_TILES[0] - 1) or c[1] in (0, MAP_TILES[1] - 1)]
    if on_border:
        raise ValueError(f"{len(on_border)} walkable cells touch the map border, for example"
                         f" {sorted(on_border)[:4]}")
    mute = [c for c in ((cx, cy) for cy in range(MAP_TILES[1]) for cx in range(MAP_TILES[0]))
            if c not in out["open"] and c not in out["raised"]
            and any((c[0] + dx, c[1] + dy) in out["open"] for dx, dy in NEAR4)]
    if mute:
        raise ValueError(f"{len(mute)} closed cells face open ground and draw nothing, for example"
                         f" {sorted(mute)[:4]}")
    if len(out["open"]) < 4810:
        raise ValueError(f"the arena holds {len(out['open'])} open cells, under the 4810 of map 14,3,"
                         f" the largest vanilla boss arena")
    if len(OLD_LOAD) != len(NEW_LOAD) or OLD_LOAD[LOAD_BYTE + 1:] != NEW_LOAD[LOAD_BYTE + 1:] \
            or OLD_LOAD[:LOAD_BYTE] != NEW_LOAD[:LOAD_BYTE]:
        raise ValueError(f"the map load is not a one byte change: {OLD_LOAD.hex()} to {NEW_LOAD.hex()}")


def _check(rom: bytearray, alloc) -> tuple:
    if "plateau" in alloc.notes:
        raise ValueError("plateau already ran")
    for name in (ARENA, ENDING):
        if name not in alloc.notes:
            raise ValueError(f"{name} has not run: the plateau composes on its notes")

    table, count = map_table(rom)
    for lit in BASE_LITERALS:
        _expect(rom, lit, _word(table + ROM_BASE))
    _expect(rom, ENTRY3_LITERAL, _word(table + MAP_SIZE * ENTRY3 + ROM_BASE))
    if words_naming(rom, table) != list(BASE_LITERALS):
        raise ValueError(f"the live map table base is named by {words_naming(rom, table)}")
    _expect(rom, COUNT_FN, COUNT_CODE_HEAD)
    _expect(rom, MAP_COUNT_BYTE + 1, COUNT_CODE_TAIL)
    if count >= MAP_COUNT_CAP:
        raise ValueError(f"the live map count is {count}: the count byte cannot hold one more")
    pairs = [(rom[table + MAP_SIZE * k], rom[table + MAP_SIZE * k + 1]) for k in range(count)]
    if len(set(pairs)) != count:
        raise ValueError(f"(zone, area) is not unique across the {count} live map entries")
    if (PLATEAU_ZONE, PLATEAU_AREA) in pairs:
        raise ValueError(f"map {PLATEAU_ZONE},{PLATEAU_AREA} already exists")

    source_index, source_sha = _check_source(rom)

    arena_index, arena_at = map_entry(rom, ARENA_ZONE, ARENA_AREA)
    arena = bytes(rom[arena_at:arena_at + MAP_SIZE])
    if arena[F_VARIATIONS] != PLATEAU_VARIATIONS or arena[F_REGION_COUNT] != 0 \
            or arena[F_ITEM_COUNT] != ARENA_ITEMS:
        raise ValueError(f"map {ARENA_ZONE},{ARENA_AREA} carries {arena[F_VARIATIONS]} variations,"
                         f" {arena[F_REGION_COUNT]} regions and {arena[F_ITEM_COUNT]} items")
    for off, want, what in ((F_COMBAT, 1, "combat"), (F_BANNER, ARENA_BANNER, "the banner"),
                            (F_REGIONS, 0, "the region list"), (F_MUSIC, ARENA_MUSIC, "the music"),
                            (F_MARKERS, 0, "the marker list"), (F_ENTER, 0, "the enter script"),
                            (F_LEAVE, 0, "the leave script")):
        if _u32(arena, off) != want:
            raise ValueError(f"map {ARENA_ZONE},{ARENA_AREA} +0x{off:02X} ({what}) is"
                             f" 0x{_u32(arena, off):X}, expected 0x{want:X}")
    if _u32(arena, F_ITEMS) - ROM_BASE != alloc.notes[ARENA]["items"]:
        raise ValueError(f"map {ARENA_ZONE},{ARENA_AREA} does not name battle_arena's own item list")

    arrive = alloc.notes[ENDING]["arrive"]
    record = bytes(rom[arrive:record_end(rom, arrive)])
    if record.count(OLD_LOAD) != 1:
        raise ValueError(f"record A rom:0x{arrive:X} holds {record.count(OLD_LOAD)} copies of the"
                         f" arena load, expected exactly 1")
    load_at = arrive + record.index(OLD_LOAD)

    elsewhere = []
    for name in (ARENA, ENDING, "future_androids"):
        for site in alloc.notes.get(name, {}).get("sites", []):
            start, size = (site, 1) if isinstance(site, int) else tuple(site)[:2]
            if start == arrive:
                continue
            found = bytes(rom[start:start + size]).count(OLD_LOAD)
            if found:
                elsewhere.append((name, start, found))
    if elsewhere:
        raise ValueError(f"the arena load is also written at {elsewhere}")

    guarded = ((SOURCE_LAYOUTS, 4, "map 7,15's layout array"),
               (SOURCE_LAYOUT, LAYOUT_SIZE, "map 7,15's layout struct"),
               (SOURCE_COLLISION, 4, "map 7,15's collision frame"),
               (SOURCE_TILE_STREAM, 4, "map 7,15's tile stream"),
               (COUNT_FN, 2, "the map count getter")) \
        + tuple((rec, LAYER_PTRS + 4 * (g[0] * g[1]), f"map 7,15's BG{n} record")
                for n, (rec, g) in enumerate(zip(SOURCE_LAYERS, SOURCE_GRIDS)))
    for name, (start, size) in _written(alloc.notes):
        for lo, n, what in guarded:
            if start < lo + n and lo < start + size:
                raise ValueError(f"{what} rom:0x{lo:X} is also written by {name}: stop and report")
    return table, count, arena, load_at, source_index, arena_index, source_sha


def _check_overlaps(notes: dict, sites: list, load_at: int) -> None:
    expected = {(lit, 4) for lit in BASE_LITERALS} \
        | {(ENTRY3_LITERAL, 4), (MAP_COUNT_BYTE, 1), (load_at + LOAD_BYTE, 1)}
    for start, size, what in sites:
        for name, (lo, n) in _written(notes):
            if start >= lo + n or lo >= start + size:
                continue
            if (start, size) not in expected:
                raise ValueError(f"this module's write of {what} at rom:0x{start:X} lands on {name}'s"
                                 f" rom:0x{lo:X}, which is not one of the expected hand-offs")


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    table, count, arena, load_at, source_index, arena_index, source_sha = _check(rom, alloc)
    rules = learn(rom)
    out = generate(rules)
    _check_design(rom, out)
    sites = []

    def place(data: bytes, name: str) -> int:
        at = alloc.alloc(len(data))
        if set(rom[at:at + len(data)]) != {0xFF}:
            raise ValueError(f"rom:0x{at:X} (0x{len(data):X} bytes) is not free")
        rom[at:at + len(data)] = data
        sites.append((at, len(data), name))
        return at

    def put(at: int, data: bytes, name: str) -> None:
        rom[at:at + len(data)] = data
        sites.append((at, len(data), name))

    n_blocks = GRID[0] * GRID[1]
    ground_at = {k: place(_packed_frame(b), f"the plateau's ground block {k}")
                 for k, b in sorted(blocks_of(out["base"]).items())}
    high_at = {k: place(_packed_frame(b), f"the plateau's high-ground block {k}")
               for k, b in sorted(blocks_of(out["raised"]).items())}
    bg3 = place(layer_record(bytes(rom[SOURCE_LAYERS[3]:SOURCE_LAYERS[3] + LAYER_PTRS]),
                             GRID, ground_at),
                f"the plateau's BG3 record ({GRID[0]}x{GRID[1]} blocks, the ground)")
    bg2 = place(layer_record(bytes(rom[SOURCE_LAYERS[2]:SOURCE_LAYERS[2] + LAYER_PTRS]),
                             GRID, high_at),
                f"the plateau's BG2 record ({GRID[0]}x{GRID[1]} blocks, the high ground)")

    blank = place(_packed_frame(bytes(BLOCK_SIZE)),
                  "the blank block BG0 and BG1 draw (tile 0, no pixel)")
    blanked = {}
    for n, off in ((0, L_BG0), (1, L_BG1)):
        rec, grid = SOURCE_LAYERS[n], SOURCE_GRIDS[n]
        blanked[off] = place(layer_record(bytes(rom[rec:rec + LAYER_PTRS]), grid,
                                          {k: blank for k in range(grid[0] * grid[1])}),
                             f"the plateau's BG{n} record (all {grid[0] * grid[1]} blocks blank)")

    frame = place(_packed_frame(collision(out["open"])),
                  f"the plateau's collision frame ({len(out['open'])} open cells, the arena top only)")
    layers = dict(blanked)
    layers[L_BG3], layers[L_BG2] = bg3, bg2
    layout = place(plateau_layout(bytes(rom[SOURCE_LAYOUT:SOURCE_LAYOUT + LAYOUT_SIZE]),
                                  layers, frame),
                   f"the plateau's layout copy (own ground, high ground, collision and camera pair"
                   f" {CLAMP}; doors and props dropped)")
    layouts = place(_word(layout + ROM_BASE), f"the plateau layout array ({PLATEAU_VARIATIONS} variation)")
    entry = plateau_entry(arena, layouts)
    new = place(bytes(rom[table:table + MAP_SIZE * count]) + entry,
                f"the map table copy ({count + 1} entries)")

    for lit in BASE_LITERALS:
        put(lit, _word(new + ROM_BASE), f"map table literal rom:0x{lit:X}")
    put(ENTRY3_LITERAL, _word(new + MAP_SIZE * ENTRY3 + ROM_BASE), f"map entry {ENTRY3} literal")
    put(MAP_COUNT_BYTE, bytes([rom[MAP_COUNT_BYTE] + 1]),
        f"map count getter: {count} becomes {count + 1}")
    put(load_at + LOAD_BYTE, NEW_LOAD[LOAD_BYTE:LOAD_BYTE + 1],
        f"record A's map load: map {ARENA_ZONE},{ARENA_AREA} becomes map {PLATEAU_ZONE},{PLATEAU_AREA}")
    _expect(rom, load_at, NEW_LOAD)
    _check_overlaps(alloc.notes, sites, load_at)

    opened = out["open"]
    x0, x1 = min(c[0] for c in opened), max(c[0] for c in opened)
    y0, y1 = min(c[1] for c in opened), max(c[1] for c in opened)
    alloc.notes["plateau"] = {
        "table": new, "entry": new + MAP_SIZE * count, "entry_index": count,
        "old_table": table, "old_count": count,
        "source_index": source_index, "source_sha1": source_sha, "arena_index": arena_index,
        "zone": PLATEAU_ZONE, "area": PLATEAU_AREA, "variation": PLATEAU_VARIATIONS,
        "layout": layout, "layouts": layouts, "collision": frame,
        "bg0": blanked[L_BG0], "bg1": blanked[L_BG1], "bg2": bg2, "bg3": bg3, "blank": blank,
        "ground_blocks": ground_at, "high_blocks": high_at, "grid": GRID, "pixels": MAP_PIXELS,
        "clamp": CLAMP, "blocks_each": n_blocks,
        "open_cells": len(opened),
        "open_box": ((x1 - x0 + 1) * 8, (y1 - y0 + 1) * 8),
        "patches": len(out["patches"]), "formations": len(out["formations"]),
        "load_at": load_at, "items": _u32(arena, F_ITEMS) - ROM_BASE,
        "sites": sorted(sites)}
