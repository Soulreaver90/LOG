/*
  tools.js - The four tools, collision paint, and every write the document ever takes.

  Four tools, and one brush they share.
    tile    paint the brush as you drag. Sizes 1, 2, 4 and 8.
    fill    click floods the ground you clicked. Drag fills a rectangle. Both TILE the brush, so a
            grabbed patch repeats as a pattern. A 128 x 128 map is 16,384 cells, and placing ground
            one cell at a time is the spec's own anti-goal.
    stamp   drop the selected stamp once, with its collision.
    grab    drag a box over art you like, name it, and it becomes a stamp. This is the asset
            pipeline: the library grows out of the real game, so no one has to cut 327 maps up
            before the first map is composed.
  RIGHT DRAG paints collision, on its own grid, never derived from the art.

  WHY A STAMP IS NOT A LIST OF SLOTS. A cell holds a VRAM slot, and slot 300 of map 7,15 is not
  slot 300 of a blank map. So a stamp stores [chunk, tile, flips] per cell, which is a tile in the
  168 chunk pool and means the same thing in every map, and placing it appends the pairs the target
  map has not got. Two kinds of cell are stored as null, meaning "leave what is under me":
    - a cell whose slot belongs to an ANIMATED GROUP, which has no chunk pair at all. Map 7,15
      names slots 894 and 895 in 57 cells, and resolving those through doc.tiles would lift a tile
      from the far side of the map.
    - a cell whose art is entirely TRANSPARENT, tested against the slot sheet's own pixels. Never
      by `cell == 0`: on a copy of a game map slot 0 is real art.

  THE STREAM CAN RUN OUT, AND IT RUNS OUT EARLY. Placed art appends to doc.tiles, and the slot a
  tile lands in is its position in that list. Map 7,15 streams 633 tiles and its group owns 894 and
  895, so its stream can only grow to 894, not to the 896 budget. A placement that would cross
  either limit is refused with the number, because a stream that grows into a group's slots draws
  the group's art and looks like a corrupt map.

  COLLISION. A set bit is OPEN ground and a clear bit is solid (bible B1070, from collision_test
  @0x08005D6C: byte cy * 32 + (cx >> 3), bit cx & 7). A new map is all zeros, so it is all solid
  and the owner opens the ground he wants walkable. Opening is clamped to the WORLD, because
  map_file.validate refuses a document with open ground the camera can never reach, which is the
  plateau fault in its collision form.

  UNDO is one step per stroke, pointerdown to pointerup, and it carries the art and the collision
  of that stroke together. See history.js for why it stores diffs.
*/
import {
  state, notify, status, BLOCK_TILES, TILE_INDEX, FLIP_X, FLIP_Y, groupTiles,
} from "./state.js";
import { drawLayer, sheetCanvas } from "./render.js";
import * as history from "./history.js";

// ===== CONFIG =====

const GRID_CELLS = 256;                 // the collision grid is 256 x 256 cells of 8 px
const GRID_STRIDE = 32;                 // bytes per collision row
const TILE = 8;
const BRUSH_SIZES = [1, 2, 4, 8];
const EMPTY_PAIR = [0, 0];              // chunk 0 tile 0 is 64 zero bytes, so it is the eraser

// ===== what the owner is holding =====

let host = null;                        // the panes' hooks: redraw, refreshCounts, atlasReady, ...
let tool = "tile";
let brushSize = 1;
let brush = { kind: "tile", name: "chunk 0 tile 0", pair: [0, 0] };
let collisionPaint = "wall";            // what right drag writes: "wall" closes, "floor" opens
let showCollision = true;
let grabLayers = "scenery";             // which layers a grab takes: scenery, ground or all
let library = [];                       // the stamps, which outlive the open map
let stroke = null;                      // the open recorder, between pointerdown and pointerup
let drag = null;                        // a box drag: fill rectangle, or grab
let hover = null;
let collisionDirty = true;              // the collision overlay is cached and redrawn on demand
let collisionSheet = null;
const clearSlot = new Map();            // slot -> is its art entirely transparent

export function install(hooks) {
  host = hooks;
  history.onChange(() => host.refreshTools());
  wireKeys();
  loadLibrary();
}

export function reset() {
  history.clear();
  clearSlot.clear();
  stroke = null;
  drag = null;
}

export function current() {
  return { tool, brushSize, brush, collisionPaint, showCollision, grabLayers, library,
           sizes: BRUSH_SIZES, undo: history.counts() };
}

/*
  WHICH LAYERS A GRAB TAKES, and why it is a choice rather than a rule.
  A boulder in a vanilla map is drawn on two layers with GROUND under it on a third. Taking all
  three gives a boulder that carries a square of its donor's sand wherever it lands, which is
  wrong over grass, so "scenery" leaves the layer being painted on behind.
  A patch of varied ground is the other half of this tool, and it is the whole answer to a field
  of one tile, so "ground" takes that layer and nothing else. Taking its neighbours as well would
  carry the donor's decoration, which then draws IN FRONT of anything stamped on that spot later.
  "all" copies a composed piece of map whole. No rule can tell these three apart, so he says.
*/
export function setGrabLayers(which) {
  grabLayers = which;
  host.refreshTools();
}

function grabs(layer) {
  if (grabLayers === "all") return true;
  const ground = layer === state.view.selected;
  return grabLayers === "ground" ? ground : !ground;
}

export function setTool(name) {
  tool = name;
  drag = null;
  host.refreshTools();
  host.paintOverlay();
}

export function setBrushSize(size) {
  brushSize = size;
  host.refreshTools();
  host.paintOverlay();
}

export function setCollisionPaint(mode) {
  collisionPaint = mode;
  host.refreshTools();
}

export function setShowCollision(on) {
  showCollision = on;
  collisionDirty = true;
  host.paintOverlay();
}

/* A tile from either list in the left pane becomes the brush. */
export function pickTile(chunk, tile) {
  brush = { kind: "tile", name: `chunk ${chunk} tile ${tile}`, pair: [chunk, tile] };
  host.refreshTools();
  host.paintOverlay();
}

export function pickStamp(name) {
  const found = library.find((s) => s.name === name);
  if (!found) return;
  brush = { kind: "stamp", name, stamp: found };
  if (tool === "tile" || tool === "fill") host.refreshTools();
  host.paintOverlay();
}

export function pickEraser() {
  brush = { kind: "tile", name: "eraser", pair: EMPTY_PAIR };
  host.refreshTools();
  host.paintOverlay();
}

// ===== the document, read =====

const doc = () => state.doc;
const across = () => doc().blocks[0] * BLOCK_TILES;
const down = () => doc().blocks[1] * BLOCK_TILES;
const inGrid = (cx, cy) => cx >= 0 && cy >= 0 && cx < across() && cy < down();

function groupSpans() {
  return (doc().animated || []).map((g) => [g.first, g.first + groupTiles(g)]);
}

function inGroup(spans, slot) {
  return spans.some(([first, past]) => slot >= first && slot < past);
}

/*
  Is this slot's art entirely transparent? Read from the slot sheet, so it is the real pixels.
  The copy into a one tile canvas is not waste: the sheet's own context was made for drawing, and
  asking an existing context for willReadFrequently does nothing but log a warning.
*/
const peek = document.createElement("canvas");
peek.width = TILE;
peek.height = TILE;
const peekCtx = peek.getContext("2d", { willReadFrequently: true });

function slotIsClear(slot) {
  if (clearSlot.has(slot)) return clearSlot.get(slot);
  peekCtx.clearRect(0, 0, TILE, TILE);
  peekCtx.drawImage(sheetCanvas(), (slot % 32) * TILE, Math.floor(slot / 32) * TILE, TILE, TILE,
                    0, 0, TILE, TILE);
  const pixels = peekCtx.getImageData(0, 0, TILE, TILE).data;
  let clear = true;
  for (let n = 3; n < pixels.length; n += 4) {
    if (pixels[n] !== 0) { clear = false; break; }
  }
  clearSlot.set(slot, clear);
  return clear;
}

// ===== the tile stream, written =====

const pairKey = (chunk, tile) => `${chunk},${tile}`;

function streamIndex() {
  const index = new Map();
  doc().tiles.forEach(([chunk, tile], slot) => {
    const key = pairKey(chunk, tile);
    if (!index.has(key)) index.set(key, slot);
  });
  return index;
}

/*
  Every [chunk, tile] this placement needs, as slots, appending the ones the map has not got.
  Raises rather than appending past the budget or into an animated group's slots.
*/
function ensureTiles(pairs) {
  const index = streamIndex();
  const spans = groupSpans();
  const budget = state.assets.tile_budget;
  const added = [];
  for (const [chunk, tile] of pairs) {
    const key = pairKey(chunk, tile);
    if (index.has(key)) continue;
    const slot = doc().tiles.length + added.length;
    if (slot >= budget) {
      throw new Error(`this map already loads ${budget} tiles, which is the hardware's limit. `
                      + `Place art it already loads, or free some.`);
    }
    if (inGroup(spans, slot)) {
      throw new Error(`this map's tile stream stops at slot ${slot}, where an animated group `
                      + `begins. Place art it already loads.`);
    }
    index.set(key, slot);
    added.push([chunk, tile]);
  }
  if (added.length) {
    markTiles();
    doc().tiles.push(...added);
  }
  return index;
}

// ===== collision =====

function collisionOpen(cx, cy) {
  if (cx < 0 || cy < 0 || cx >= GRID_CELLS || cy >= GRID_CELLS) return 0;
  return (doc().collision[cy * GRID_STRIDE + (cx >> 3)] >> (cx & 7)) & 1;
}

/* Inside the world is the only place open ground may sit: validate refuses it anywhere else. */
function insideWorld(cx, cy) {
  return cx * TILE < doc().world[0] && cy * TILE < doc().world[1];
}

function putCollision(cx, cy, open) {
  if (cx < 0 || cy < 0 || cx >= GRID_CELLS || cy >= GRID_CELLS) return;
  if (open && !insideWorld(cx, cy)) return;
  const at = cy * GRID_STRIDE + (cx >> 3);
  const bit = 1 << (cx & 7);
  const was = doc().collision[at];
  const now = open ? was | bit : was & ~bit;
  if (now === was) return;
  stroke.collision.idx.push(at);
  stroke.collision.old.push(was);
  stroke.collision.now.push(now);
  doc().collision[at] = now;
  collisionDirty = true;
}

// ===== the stroke recorder =====

function begin(label) {
  stroke = { label, cells: {}, collision: { idx: [], old: [], now: [] },
             boxes: {}, tilesBefore: null, stampsBefore: null };
}

function markTiles() {
  if (stroke && !stroke.tilesBefore) stroke.tilesBefore = doc().tiles.map((p) => p.slice());
}

function markStamps() {
  if (stroke && !stroke.stampsBefore) {
    stroke.stampsBefore = (doc().stamps || []).map((s) => ({ ...s }));
  }
}

function putCell(layer, cx, cy, value) {
  if (!inGrid(cx, cy)) return;
  const cells = doc().layers[layer].cells;
  const at = cy * across() + cx;
  if (cells[at] === value) return;
  const rec = stroke.cells[layer] || (stroke.cells[layer] = { idx: [], old: [], now: [] });
  rec.idx.push(at);
  rec.old.push(cells[at]);
  rec.now.push(value);
  cells[at] = value;
  const box = stroke.boxes[layer] || (stroke.boxes[layer] = [cx, cy, cx + 1, cy + 1]);
  box[0] = Math.min(box[0], cx);
  box[1] = Math.min(box[1], cy);
  box[2] = Math.max(box[2], cx + 1);
  box[3] = Math.max(box[3], cy + 1);
}

/* Close the stroke: push one undo step, redraw what it touched, and refresh the counts. */
function commit() {
  if (!stroke) return;
  const touched = Object.keys(stroke.cells);
  const moved = touched.length || stroke.collision.idx.length
                || stroke.tilesBefore || stroke.stampsBefore;
  if (!moved) { stroke = null; return; }

  const before = { cells: {}, collision: null, tiles: stroke.tilesBefore, stamps: stroke.stampsBefore };
  const after = { cells: {}, collision: null,
                  tiles: stroke.tilesBefore ? doc().tiles.map((p) => p.slice()) : null,
                  stamps: stroke.stampsBefore ? (doc().stamps || []).map((s) => ({ ...s })) : null };
  for (const [layer, rec] of Object.entries(stroke.cells)) {
    before.cells[layer] = { idx: rec.idx, values: rec.old };
    after.cells[layer] = { idx: rec.idx, values: rec.now };
  }
  if (stroke.collision.idx.length) {
    before.collision = { idx: stroke.collision.idx, values: stroke.collision.old };
    after.collision = { idx: stroke.collision.idx, values: stroke.collision.now };
  }
  const boxes = stroke.boxes;
  const grew = Boolean(stroke.tilesBefore);
  const name = stroke.label;
  stroke = null;

  history.push(before, after, boxes, name);
  if (grew) {
    redrawEverything();                       // it refreshes the counts and the palette itself
  } else {
    for (const [layer, box] of Object.entries(boxes)) drawLayer(doc(), layer, box);
    host.redraw();
    host.refreshCounts();
  }
  host.paintOverlay();
  notify("doc");
}

/*
  A stroke that added tiles rebuilds the slot sheet, which is async. Two of them at once would
  both build a sheet and the slower one would win, leaving the map drawn from a sheet that is one
  stroke behind. The chain runs them in order, so the last stroke is the one on screen.
*/
let rebuilding = Promise.resolve();

function redrawEverything() {
  rebuilding = rebuilding.then(async () => {
    await host.rebuildSheet();
    clearSlot.clear();
    for (const name of Object.keys(doc().layers)) drawLayer(doc(), name, null);
    host.redraw();
    host.refreshCounts();
    host.refreshPalette();
  });
  return rebuilding;
}

// ===== undo and redo =====

function applyPatch(patch, back) {
  for (const [layer, rec] of Object.entries(patch.cells || {})) {
    const cells = doc().layers[layer].cells;
    if (back) for (let n = rec.idx.length - 1; n >= 0; n -= 1) cells[rec.idx[n]] = rec.values[n];
    else for (let n = 0; n < rec.idx.length; n += 1) cells[rec.idx[n]] = rec.values[n];
  }
  const bits = patch.collision;
  if (bits) {
    if (back) for (let n = bits.idx.length - 1; n >= 0; n -= 1) doc().collision[bits.idx[n]] = bits.values[n];
    else for (let n = 0; n < bits.idx.length; n += 1) doc().collision[bits.idx[n]] = bits.values[n];
    collisionDirty = true;
  }
  if (patch.tiles) doc().tiles = patch.tiles.map((p) => p.slice());
  if (patch.stamps) doc().stamps = patch.stamps.map((s) => ({ ...s }));
}

async function step(move) {
  if (!move) { status("nothing to step back to"); return; }
  applyPatch(move.patch, move.back);
  if (move.patch.tiles) {
    await redrawEverything();
  } else {
    for (const [layer, box] of Object.entries(move.boxes || {})) drawLayer(doc(), layer, box);
    host.redraw();
    host.refreshCounts();
  }
  host.paintOverlay();
  notify("doc");
  status(`${move.back ? "stepped back" : "stepped forward"} one ${move.label || "change"}`);
}

export function undo() {
  return step(history.undo());
}

export function redo() {
  return step(history.redo());
}

// ===== the brush, as a patch anyone can place =====

/*
  One shape for both kinds of brush: a w x h grid of [chunk, tile, flips] per layer, plus an
  optional collision grid of the same size. A null cell leaves what is under it alone.
*/
function brushPatch() {
  if (brush.kind === "stamp") {
    const stamp = brush.stamp;
    return { w: stamp.w, h: stamp.h, layers: stamp.cells, collision: stamp.collision || null };
  }
  const size = brushSize;
  const one = new Array(size * size).fill([brush.pair[0], brush.pair[1], 0]);
  return { w: size, h: size, layers: { [state.view.selected]: one }, collision: null };
}

function patchPairs(patch) {
  const pairs = [];
  for (const cells of Object.values(patch.layers)) {
    for (const cell of cells) if (cell) pairs.push([cell[0], cell[1]]);
  }
  return pairs;
}

/* Place a patch with its top left at (px, py). Collision, when it carries one, goes with it. */
function writePatch(patch, px, py, index) {
  for (const [layer, cells] of Object.entries(patch.layers)) {
    if (!doc().layers[layer]) continue;
    for (let y = 0; y < patch.h; y += 1) {
      for (let x = 0; x < patch.w; x += 1) {
        const cell = cells[y * patch.w + x];
        if (!cell) continue;
        const slot = index.get(pairKey(cell[0], cell[1]));
        putCell(layer, px + x, py + y, slot | (cell[2] || 0));
      }
    }
  }
  // A STAMP ADDS WALLS AND NEVER REMOVES THEM. Only the cells the grab found SOLID are written.
  // A grab captures a box, and most of that box is the open ground the object stands on, so
  // writing the open cells too would punch a hole through any wall the box happened to cross.
  // Measured: a rock dropped over a hand painted wall opened 12 cells of it. It also makes a
  // grab from plain open ground change no collision at all, which is what it should do.
  if (!patch.collision) return;
  for (let y = 0; y < patch.h; y += 1) {
    for (let x = 0; x < patch.w; x += 1) {
      if (!patch.collision[y * patch.w + x]) putCollision(px + x, py + y, false);
    }
  }
}

/* The same patch repeated over a list of cell indices, anchored to the map origin. */
function tilePatch(patch, cells, index) {
  const layers = Object.entries(patch.layers).filter(([name]) => doc().layers[name]);
  const width = across();
  for (const at of cells) {
    const cx = at % width;
    const cy = Math.floor(at / width);
    const sx = ((cx % patch.w) + patch.w) % patch.w;
    const sy = ((cy % patch.h) + patch.h) % patch.h;
    for (const [layer, source] of layers) {
      const cell = source[sy * patch.w + sx];
      if (!cell) continue;
      putCell(layer, cx, cy, index.get(pairKey(cell[0], cell[1])) | (cell[2] || 0));
    }
  }
}

// ===== the tools =====

/*
  Draw what the hand has just written, before the hand stops. Only the cells the brush touched are
  redrawn, so a 4 x 4 brush costs 16 cells and not the map. Waiting for pointerup to draw would
  leave him dragging a ghost over art that never changes, on a tool he judges entirely by eye.
*/
function showStep(box, layers) {
  const x0 = Math.max(0, box[0]);
  const y0 = Math.max(0, box[1]);
  const x1 = Math.min(across(), box[2]);
  const y1 = Math.min(down(), box[3]);
  if (x1 <= x0 || y1 <= y0) return;
  for (const layer of layers) {
    if (doc().layers[layer]) drawLayer(doc(), layer, [x0, y0, x1, y1]);
  }
  host.redraw();
}

function paintAt(where) {
  const patch = brushPatch();
  const index = ensureTiles(patchPairs(patch));
  writePatch(patch, where.cx, where.cy, index);
  showStep([where.cx, where.cy, where.cx + patch.w, where.cy + patch.h],
           Object.keys(patch.layers));
}

function stampAt(where) {
  const patch = brushPatch();
  const index = ensureTiles(patchPairs(patch));
  const w = Math.min(patch.w, across() - where.cx);
  const h = Math.min(patch.h, down() - where.cy);
  if (w <= 0 || h <= 0) return;
  writePatch(patch, where.cx, where.cy, index);
  markStamps();
  for (const layer of Object.keys(patch.layers)) {
    if (!doc().layers[layer]) continue;
    doc().stamps.push({ name: brush.name, layer, x: where.cx, y: where.cy, w, h });
  }
}

/* Every cell joined to this one that holds the same value, four ways. */
function floodRegion(layer, cx, cy) {
  const width = across();
  const height = down();
  const cells = doc().layers[layer].cells;
  const target = cells[cy * width + cx];
  const seen = new Uint8Array(width * height);
  const out = [];
  const stack = [cy * width + cx];
  seen[stack[0]] = 1;
  while (stack.length) {
    const at = stack.pop();
    if (cells[at] !== target) continue;
    out.push(at);
    const x = at % width;
    const y = Math.floor(at / width);
    if (x > 0 && !seen[at - 1]) { seen[at - 1] = 1; stack.push(at - 1); }
    if (x < width - 1 && !seen[at + 1]) { seen[at + 1] = 1; stack.push(at + 1); }
    if (y > 0 && !seen[at - width]) { seen[at - width] = 1; stack.push(at - width); }
    if (y < height - 1 && !seen[at + width]) { seen[at + width] = 1; stack.push(at + width); }
  }
  return out;
}

function rectCells(x0, y0, x1, y1) {
  const width = across();
  const out = [];
  for (let cy = Math.max(0, y0); cy <= Math.min(down() - 1, y1); cy += 1) {
    for (let cx = Math.max(0, x0); cx <= Math.min(width - 1, x1); cx += 1) out.push(cy * width + cx);
  }
  return out;
}

function fillCells(cells) {
  const patch = brushPatch();
  const index = ensureTiles(patchPairs(patch));
  tilePatch(patch, cells, index);
}

/* Right drag: collision, in whichever direction the toolbar is set to. */
function paintCollision(where) {
  const open = collisionPaint === "floor";
  for (let y = 0; y < brushSize; y += 1) {
    for (let x = 0; x < brushSize; x += 1) putCollision(where.cx + x, where.cy + y, open);
  }
}

export function fillCollision(open) {
  if (!doc()) return;
  begin("collision fill");
  const limitX = open ? Math.ceil(doc().world[0] / TILE) : GRID_CELLS;
  const limitY = open ? Math.ceil(doc().world[1] / TILE) : GRID_CELLS;
  for (let cy = 0; cy < limitY; cy += 1) {
    for (let cx = 0; cx < limitX; cx += 1) putCollision(cx, cy, open);
  }
  commit();
  status(open ? "every cell inside the world is walkable now" : "every cell is solid now");
}

// ===== grab: a box of real map becomes a stamp =====

function grabStamp(name, x0, y0, x1, y1) {
  const w = x1 - x0 + 1;
  const h = y1 - y0 + 1;
  const width = across();
  const spans = groupSpans();
  const tiles = doc().tiles;
  const cells = {};
  let skipped = 0;
  let kept = 0;

  for (const layer of Object.keys(doc().layers)) {
    if (!grabs(layer)) continue;
    const source = doc().layers[layer].cells;
    const list = new Array(w * h).fill(null);
    let any = false;
    for (let y = 0; y < h; y += 1) {
      for (let x = 0; x < w; x += 1) {
        const value = source[(y0 + y) * width + x0 + x];
        const slot = value & TILE_INDEX;
        if (slot >= tiles.length || inGroup(spans, slot)) { skipped += 1; continue; }
        if (slotIsClear(slot)) continue;
        const flips = value & (FLIP_X | FLIP_Y);
        list[y * w + x] = [tiles[slot][0], tiles[slot][1], flips];
        any = true;
        kept += 1;
      }
    }
    if (any) cells[layer] = list;
  }

  // Collision under the box. All solid means nothing was captured: on a blank map every cell is
  // solid, and a stamp that paints that back would wall off the ground wherever it was dropped.
  const bits = [];
  let anyOpen = false;
  for (let y = 0; y < h; y += 1) {
    for (let x = 0; x < w; x += 1) {
      const open = collisionOpen(x0 + x, y0 + y);
      bits.push(open);
      if (open) anyOpen = true;
    }
  }
  return { stamp: { name, w, h, cells, collision: anyOpen ? bits : null }, skipped, kept };
}

// ===== the stamp library, which outlives the open map =====

async function loadLibrary() {
  try {
    const payload = await (await fetch("/api/stamps")).json();
    library = payload.stamps || [];
  } catch (problem) {
    library = [];
  }
  host.refreshTools();
}

async function keepStamp(stamp) {
  const answer = await (await fetch("/api/stamp", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(stamp),
  })).json();
  if (answer.error) throw new Error(answer.error);
  library = library.filter((s) => s.name !== stamp.name).concat([stamp]);
  library.sort((a, b) => a.name.localeCompare(b.name));
  host.refreshTools();
}

// ===== the pointer, which is where every tool starts =====

export function pointer(kind, where) {
  if (!state.doc) return;
  hover = where;
  if (kind === "pointerdown") down_(where);
  else if (kind === "pointermove") move_(where);
  else up_(where);
  host.paintOverlay();
}

function down_(where) {
  // Alt picks the tile under the cursor into the brush. Cheap, and it saves hunting the pool list.
  if (where.event.altKey) {
    const slot = doc().layers[state.view.selected].cells[where.cy * across() + where.cx] & TILE_INDEX;
    if (slot < doc().tiles.length) pickTile(doc().tiles[slot][0], doc().tiles[slot][1]);
    else status(`cell ${where.cx}, ${where.cy} draws slot ${slot}, which no chunk tile owns`, "bad");
    return;
  }
  if (where.button === 2) {
    begin("collision");
    paintCollision(where);
    drag = { mode: "collision", last: `${where.cx},${where.cy}` };
    return;
  }
  if (where.button !== 0) return;

  if (tool === "fill" || tool === "grab") {
    drag = { mode: "box", x0: where.cx, y0: where.cy, x1: where.cx, y1: where.cy };
    return;
  }
  try {
    begin(tool);
    if (tool === "stamp") stampAt(where);
    else paintAt(where);
  } catch (problem) {
    stroke = null;
    status(`${problem.message}`, "bad");
    return;
  }
  if (tool === "stamp") { commit(); drag = null; return; }
  // The brush does not change inside a stroke, so only this first touch can add a tile. The sheet
  // catches up while he drags, and the new slot draws blank for the frame or two that takes.
  if (stroke.tilesBefore) redrawEverything();
  drag = { mode: "paint", last: `${where.cx},${where.cy}` };
}

function move_(where) {
  if (!drag) return;
  if (drag.mode === "box") {
    drag.x1 = where.cx;
    drag.y1 = where.cy;
    return;
  }
  if (!where.event.buttons) { up_(where); return; }    // the button came up off the canvas
  const here = `${where.cx},${where.cy}`;
  if (here === drag.last) return;
  drag.last = here;
  try {
    if (drag.mode === "collision") paintCollision(where);
    else paintAt(where);
  } catch (problem) {
    status(`${problem.message}`, "bad");
    endStroke();
  }
}

function up_(where) {
  if (!drag) return;
  const box = drag;
  drag = null;
  if (box.mode !== "box") { commit(); return; }

  const x0 = Math.min(box.x0, box.x1);
  const y0 = Math.min(box.y0, box.y1);
  const x1 = Math.max(box.x0, box.x1);
  const y1 = Math.max(box.y0, box.y1);
  if (tool === "grab") { finishGrab(x0, y0, x1, y1); return; }

  try {
    begin("fill");
    fillCells(x0 === x1 && y0 === y1
      ? floodRegion(state.view.selected, x0, y0)
      : rectCells(x0, y0, x1, y1));
  } catch (problem) {
    stroke = null;
    status(`${problem.message}`, "bad");
    return;
  }
  commit();
}

function endStroke() {
  commit();
  drag = null;
}

async function finishGrab(x0, y0, x1, y1) {
  const name = host.stampName() || `stamp ${library.length + 1}`;
  const made = grabStamp(name, x0, y0, Math.min(x1, across() - 1), Math.min(y1, down() - 1));
  if (!made.kept) {
    status(`nothing to grab at ${x0}, ${y0}: every cell in that box is empty`, "bad");
    return;
  }
  try {
    await keepStamp(made.stamp);
  } catch (problem) {
    status(`${problem.message}`, "bad");
    return;
  }
  brush = { kind: "stamp", name, stamp: made.stamp };
  setTool("stamp");
  const note = made.skipped ? `, ${made.skipped} animated cell(s) left out` : "";
  status(`grabbed "${name}", ${made.stamp.w} x ${made.stamp.h} cells, ${made.kept} of them art`
         + `${made.stamp.collision ? ", with its collision" : ""}${note}`, "good");
}

// ===== the overlay: collision, the brush ghost, and the box being dragged =====

function collisionLayer() {
  const [width, height] = [across() * TILE, down() * TILE];
  if (!collisionSheet || collisionSheet.width !== width || collisionSheet.height !== height) {
    collisionSheet = document.createElement("canvas");
    collisionSheet.width = width;
    collisionSheet.height = height;
    collisionDirty = true;
  }
  if (!collisionDirty) return collisionSheet;
  const ctx = collisionSheet.getContext("2d");
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "rgba(224, 64, 64, 0.32)";
  const limitX = Math.min(across(), GRID_CELLS);
  const limitY = Math.min(down(), GRID_CELLS);
  for (let cy = 0; cy < limitY; cy += 1) {
    let run = 0;
    for (let cx = 0; cx <= limitX; cx += 1) {
      const solid = cx < limitX && !collisionOpen(cx, cy);
      if (solid) { run += 1; continue; }
      if (run) ctx.fillRect((cx - run) * TILE, cy * TILE, run * TILE, TILE);
      run = 0;
    }
  }
  collisionDirty = false;
  return collisionSheet;
}

/* The brush, drawn where it would land. Real art when its chunk atlas is loaded, an outline else. */
function drawGhost(ctx, patch, px, py) {
  ctx.save();
  ctx.globalAlpha = 0.75;
  for (const [layer, cells] of Object.entries(patch.layers)) {
    if (!doc().layers[layer]) continue;
    for (let y = 0; y < patch.h; y += 1) {
      for (let x = 0; x < patch.w; x += 1) {
        const cell = cells[y * patch.w + x];
        if (!cell) continue;
        const atlas = host.atlasReady(cell[0]);
        if (!atlas) continue;
        ctx.drawImage(atlas, (cell[1] % 16) * TILE, Math.floor(cell[1] / 16) * TILE, TILE, TILE,
                      (px + x) * TILE, (py + y) * TILE, TILE, TILE);
      }
    }
  }
  ctx.restore();
  ctx.strokeStyle = "#f0a860";
  ctx.lineWidth = 1;
  ctx.strokeRect(px * TILE + 0.5, py * TILE + 0.5, patch.w * TILE - 1, patch.h * TILE - 1);
}

export function drawOverlay(ctx) {
  if (!state.doc) return;
  if (showCollision) ctx.drawImage(collisionLayer(), 0, 0);

  if (drag && drag.mode === "box") {
    const x0 = Math.min(drag.x0, drag.x1) * TILE;
    const y0 = Math.min(drag.y0, drag.y1) * TILE;
    const w = (Math.abs(drag.x1 - drag.x0) + 1) * TILE;
    const h = (Math.abs(drag.y1 - drag.y0) + 1) * TILE;
    ctx.fillStyle = tool === "grab" ? "rgba(106, 169, 224, 0.22)" : "rgba(240, 168, 96, 0.22)";
    ctx.fillRect(x0, y0, w, h);
    ctx.strokeStyle = tool === "grab" ? "#6aa9e0" : "#f0a860";
    ctx.lineWidth = 1;
    ctx.strokeRect(x0 + 0.5, y0 + 0.5, w - 1, h - 1);
    return;
  }
  if (!hover || !inGrid(hover.cx, hover.cy)) return;
  if (tool === "tile" || tool === "stamp" || tool === "fill") {
    drawGhost(ctx, brushPatch(), hover.cx, hover.cy);
  }
}

/* A tile or a stamp dropped on the map from the left pane. His words: drag and drop. */
export function dropAt(payload, where) {
  if (!state.doc) return;
  if (payload.kind === "stamp") pickStamp(payload.name);
  else pickTile(payload.chunk, payload.tile);
  setTool(payload.kind === "stamp" ? "stamp" : "tile");
  try {
    begin("drop");
    if (payload.kind === "stamp") stampAt(where);
    else paintAt(where);
  } catch (problem) {
    stroke = null;
    status(`${problem.message}`, "bad");
    return;
  }
  commit();
}

// ===== keys =====

function wireKeys() {
  window.addEventListener("keydown", (event) => {
    const typing = /^(INPUT|SELECT|TEXTAREA)$/.test(document.activeElement.tagName);
    if (typing) return;
    if (event.key === "Escape") {
      // A box being dragged has written nothing, so it is dropped. A paint or collision stroke
      // has already changed the map, so it is closed instead: cells undo cannot reach are worse
      // than a stroke that ended early.
      if (drag && drag.mode !== "box") commit();
      drag = null;
      stroke = null;
      host.paintOverlay();
      return;
    }
    if (!event.ctrlKey) return;
    const key = event.key.toLowerCase();
    if (key === "z" && !event.shiftKey) { event.preventDefault(); undo(); }
    else if (key === "y" || (key === "z" && event.shiftKey)) { event.preventDefault(); redo(); }
  });
}
