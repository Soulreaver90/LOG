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
  map has not got. A cell whose art is entirely TRANSPARENT is stored as null, meaning "leave what
  is under me", tested against the slot sheet's own pixels. Never by `cell == 0`: on a copy of a
  game map slot 0 is real art.

  ANIMATED CELLS ARE CARRIED, NOT DROPPED. A slot that belongs to an ANIMATED GROUP has no chunk
  pair at all, and a grab used to store null there. Vanilla map 7,15 names its group's slots in 57
  cells, and the map the owner is composing from it names them in 224, which is its waving grass,
  so a grab of a field came back with 224 holes in it. A
  cell of a group is now stored as {g, t, f} and the stamp carries the group's own PIXELS, which
  is what lets it place that grass into a map that has never held it. cells.js owns that format
  and the slot every cell lands in. Every reader of a patch cell branches: patchPairs, writePatch,
  tilePatch and drawGhost here, drawStamp in panes.js.

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

  WORLD CELLS, EVERYWHERE. Every (cx, cy) in this file is a WORLD cell, the space the collision
  grid and the camera already use. A layer sits at its own offset (state.layerShift), so the cell
  of its own grid is reached through gridCell(), and putCell is the only place that converts for a
  write. Before this, a stroke on map 3,11's BG3 landed 24 cells from the collision it was aimed
  at, and a grab took its layers 8 and 24 cells apart from each other.

  UNDO is one step per stroke, pointerdown to pointerup, and it carries the art and the collision
  of that stroke together. See history.js for why it stores diffs.
*/
import {
  state, notify, status, BLOCK_TILES, TILE_INDEX, FLIP_X, FLIP_Y,
  gridCell, layerShiftCells, GROUP_MAX, GROUP_MAX_TILES,
} from "./state.js";
import { drawLayer, slotIsBlank, sheetCanvas } from "./render.js";
import {
  animatedCell, applyPlan, cellFlips, findGroup, groupAtSlot, isAnimatedCell, planPlacement,
} from "./cells.js";
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
let showAnimated = false;               // the animated tile wash, off until he asks for it
let grabLayers = "scenery";             // which layers a grab takes: scenery, ground or all
let grabCollision = "take";             // whether a grab keeps the collision under the box
let library = [];                       // the stamps, which outlive the open map
let stroke = null;                      // the open recorder, between pointerdown and pointerup
let drag = null;                        // a box drag: fill rectangle, or grab
let hover = null;
let collisionDirty = true;              // the collision overlay is cached and redrawn on demand
let collisionSheet = null;
let animatedDirty = true;               // the animated tile overlay, cached the same way
let animatedSheet = null;
let animatedShown = "";                 // the layers that sheet was built from, so a hide rebuilds
let lastRefusal = "";                   // the refusal already on the status line, said once

export function install(hooks) {
  host = hooks;
  history.onChange(() => host.refreshTools());
  wireKeys();
  loadLibrary();
}

export function reset() {
  history.clear();
  stroke = null;
  drag = null;
  collisionDirty = true;
  animatedDirty = true;
  lastRefusal = "";
}

export function current() {
  return { tool, brushSize, brush, collisionPaint, showCollision, showAnimated, grabLayers,
           grabCollision, library, sizes: BRUSH_SIZES, undo: history.counts() };
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

/*
  WHETHER A GRAB KEEPS THE COLLISION. "take" is the default because it is right for a rock: the
  player must walk around it wherever it lands. It is wrong for a patch of ground and for most
  scenery, because a stamp writes a wall into EVERY cell the grab found solid, including the cells
  where the stamp draws nothing at all, and the owner then has invisible walls in his map.
*/
export function setGrabCollision(which) {
  grabCollision = which;
  host.refreshTools();
}

/*
  Which layers a grab reads. These are LAYERS and not kinds of thing: "ground" is the one layer
  selected right now, and "scenery" is every other layer. The names are the owner's words for what
  he uses each setting for, and the option text in the page names the actual layer.
*/
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

/*
  WHERE THE ANIMATED TILES ARE. His map carries 224 of them and nothing on screen said so until a
  grab turned them into holes. Magenta, because the collision wash is red, the grab box is blue
  and the brush ghost is orange, and because the ground he is working on is green: magenta is the
  one strong hue that green cannot swallow.
*/
export function setShowAnimated(on) {
  showAnimated = on;
  animatedDirty = true;
  host.paintOverlay();
}

/* A tile from either list in the left pane becomes the brush. */
export function pickTile(chunk, tile) {
  brush = { kind: "tile", name: `chunk ${chunk} tile ${tile}`, pair: [chunk, tile] };
  host.refreshTools();
  host.paintOverlay();
}

/*
  One tile of an animated group becomes the brush, so waving grass can be painted by hand and a
  stamp can be touched up. The group is COPIED into the brush rather than pointed at, because he
  switches maps with a brush in his hand, and a brush that pointed at the old document's group
  would place a group that is no longer there.
*/
export function pickAnimatedTile(which, tile) {
  const group = (doc().animated || [])[which];
  if (!group) return;
  brush = {
    kind: "anim",
    name: `animated group ${which} tile ${tile}`,
    tile,
    group: { first: group.first,
             frames: (group.frames || []).map((f) => ({ duration: f.duration,
                                                        pixels: Array.from(f.pixels || []) })) },
  };
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
const inGrid = (gx, gy) => gx >= 0 && gy >= 0 && gx < across() && gy < down();
/* The canvas is the block grid in WORLD pixels, so this is where a cursor may be. */
const onCanvas = (cx, cy) => cx >= 0 && cy >= 0 && cx < across() && cy < down();

// ===== the tile stream and the animated groups, written =====

const limits = () => ({ budget: state.assets.tile_budget,
                        groupMax: GROUP_MAX, groupMaxTiles: GROUP_MAX_TILES });

/*
  What this patch needs, worked out by cells.js, then given to the map: the [chunk, tile] pairs it
  has not got, and the animated groups it has not got. Both are recorded for undo first.

  Raises when the static stream cannot fit, which stops the whole placement. A group that cannot
  fit refuses only its own cells, and `refusals` says which limit stopped it: his grass is worth
  one plain sentence and not a silent hole.
*/
function planFor(patch) {
  const plan = planPlacement(doc(), patch, limits());
  if (plan.addTiles.length) markTiles();
  if (plan.addGroups.length) markAnimated();
  applyPlan(doc(), plan);
  if (plan.addGroups.length) animatedDirty = true;
  sayRefusals(plan);
  return plan;
}

/* One sentence per refusal, and never the same one twice in a row while he drags. */
function sayRefusals(plan) {
  const note = [...new Set(plan.refusals)].join(". ");
  if (!note) { lastRefusal = ""; return; }
  if (note === lastRefusal) return;
  lastRefusal = note;
  status(note, "bad");
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
             boxes: {}, tilesBefore: null, stampsBefore: null, animatedBefore: null };
}

function markTiles() {
  if (stroke && !stroke.tilesBefore) stroke.tilesBefore = doc().tiles.map((p) => p.slice());
}

/* A placement may ADD an animated group, so undo has to be able to take one away again. The
   whole list is kept: it is a handful of groups of at most 64 tiles, and a diff of pixels would
   cost more to write than the list costs to copy. */
function markAnimated() {
  if (stroke && !stroke.animatedBefore) stroke.animatedBefore = copyGroups(doc().animated);
}

function copyGroups(groups) {
  return (groups || []).map((g) => ({
    first: g.first,
    frames: (g.frames || []).map((f) => ({ duration: f.duration, pixels: Array.from(f.pixels) })),
  }));
}

function markStamps() {
  if (stroke && !stroke.stampsBefore) {
    stroke.stampsBefore = (doc().stamps || []).map((s) => ({ ...s }));
  }
}

/* (cx, cy) is a WORLD cell. This is the one place a layer's own offset is applied to a write, and
   the recorded box is in that layer's grid, which is the space drawLayer redraws. */
function putCell(layer, cx, cy, value) {
  const [gx, gy] = gridCell(doc(), layer, cx, cy);
  if (!inGrid(gx, gy)) return;
  const cells = doc().layers[layer].cells;
  const at = gy * across() + gx;
  if (cells[at] === value) return;
  const rec = stroke.cells[layer] || (stroke.cells[layer] = { idx: [], old: [], now: [] });
  rec.idx.push(at);
  rec.old.push(cells[at]);
  rec.now.push(value);
  cells[at] = value;
  const box = stroke.boxes[layer] || (stroke.boxes[layer] = [gx, gy, gx + 1, gy + 1]);
  box[0] = Math.min(box[0], gx);
  box[1] = Math.min(box[1], gy);
  box[2] = Math.max(box[2], gx + 1);
  box[3] = Math.max(box[3], gy + 1);
}

/* Close the stroke: push one undo step, redraw what it touched, and refresh the counts. */
function commit() {
  if (!stroke) return;
  const touched = Object.keys(stroke.cells);
  const moved = touched.length || stroke.collision.idx.length
                || stroke.tilesBefore || stroke.stampsBefore || stroke.animatedBefore;
  if (!moved) { stroke = null; return; }

  const before = { cells: {}, collision: null, tiles: stroke.tilesBefore,
                   stamps: stroke.stampsBefore, animated: stroke.animatedBefore };
  const after = { cells: {}, collision: null,
                  tiles: stroke.tilesBefore ? doc().tiles.map((p) => p.slice()) : null,
                  stamps: stroke.stampsBefore ? (doc().stamps || []).map((s) => ({ ...s })) : null,
                  animated: stroke.animatedBefore ? copyGroups(doc().animated) : null };
  for (const [layer, rec] of Object.entries(stroke.cells)) {
    before.cells[layer] = { idx: rec.idx, values: rec.old };
    after.cells[layer] = { idx: rec.idx, values: rec.now };
  }
  if (stroke.collision.idx.length) {
    before.collision = { idx: stroke.collision.idx, values: stroke.collision.old };
    after.collision = { idx: stroke.collision.idx, values: stroke.collision.now };
  }
  const boxes = stroke.boxes;
  // A new group is new PIXELS, so the slot sheet has to be rebuilt for it exactly as a new tile
  // does. Without this the group's slots draw from a sheet that never held them.
  const grew = Boolean(stroke.tilesBefore || stroke.animatedBefore);
  const name = stroke.label;
  stroke = null;
  // The wash is rebuilt once a stroke ends, never inside it. A rebuild walks every cell of every
  // shown layer, and doing that on each pointer move of a drag would cost him the frame rate.
  animatedDirty = true;

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
  if (patch.animated) {
    doc().animated = copyGroups(patch.animated);
    animatedDirty = true;
  }
}

async function step(move) {
  if (!move) { status("nothing to step back to"); return; }
  applyPatch(move.patch, move.back);
  animatedDirty = true;
  if (move.patch.tiles || move.patch.animated) {
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
  One shape for all three kinds of brush: a w x h grid of cells per layer, the animated groups
  those cells may name, and an optional collision grid of the same size. A null cell leaves what
  is under it alone. cells.js owns what a cell may be.
*/
function brushPatch() {
  if (brush.kind === "stamp") {
    const stamp = brush.stamp;
    return { w: stamp.w, h: stamp.h, layers: stamp.cells, animated: stamp.animated || [],
             collision: stamp.collision || null };
  }
  const size = brushSize;
  if (brush.kind === "anim") {
    const one = new Array(size * size).fill(animatedCell(0, brush.tile, 0));
    return { w: size, h: size, layers: { [state.view.selected]: one },
             animated: [brush.group], collision: null };
  }
  const one = new Array(size * size).fill([brush.pair[0], brush.pair[1], 0]);
  return { w: size, h: size, layers: { [state.view.selected]: one }, animated: [], collision: null };
}

/* Place a patch with its top left at (px, py). Collision, when it carries one, goes with it. */
function writePatch(patch, px, py, plan) {
  for (const [layer, cells] of Object.entries(patch.layers)) {
    if (!doc().layers[layer]) continue;
    for (let y = 0; y < patch.h; y += 1) {
      for (let x = 0; x < patch.w; x += 1) {
        const cell = cells[y * patch.w + x];
        const slot = plan.slotOf(cell);
        if (slot === null) continue;          // a null cell, or a group this map could not take
        putCell(layer, px + x, py + y, slot | cellFlips(cell));
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

/* The same patch repeated over a list of WORLD cells, anchored to the world origin. */
function tilePatch(patch, cells, plan) {
  const layers = Object.entries(patch.layers).filter(([name]) => doc().layers[name]);
  for (const [cx, cy] of cells) {
    const sx = ((cx % patch.w) + patch.w) % patch.w;
    const sy = ((cy % patch.h) + patch.h) % patch.h;
    for (const [layer, source] of layers) {
      const cell = source[sy * patch.w + sx];
      const slot = plan.slotOf(cell);
      if (slot === null) continue;
      putCell(layer, cx, cy, slot | cellFlips(cell));
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
  for (const layer of layers) {
    if (!doc().layers[layer]) continue;
    const [sx, sy] = layerShiftCells(doc(), layer);          // the box arrives in WORLD cells
    const x0 = Math.max(0, box[0] + sx);
    const y0 = Math.max(0, box[1] + sy);
    const x1 = Math.min(across(), box[2] + sx);
    const y1 = Math.min(down(), box[3] + sy);
    if (x1 <= x0 || y1 <= y0) continue;
    drawLayer(doc(), layer, [x0, y0, x1, y1]);
  }
  host.redraw();
}

function paintAt(where) {
  const patch = brushPatch();
  const plan = planFor(patch);
  writePatch(patch, where.cx, where.cy, plan);
  showStep([where.cx, where.cy, where.cx + patch.w, where.cy + patch.h],
           Object.keys(patch.layers));
}

function stampAt(where) {
  const patch = brushPatch();
  const plan = planFor(patch);
  if (where.cx >= across() || where.cy >= down()) return;
  writePatch(patch, where.cx, where.cy, plan);
  markStamps();
  for (const layer of Object.keys(patch.layers)) {
    if (!doc().layers[layer]) continue;
    // The record names a LAYER, so it keeps that layer's own grid cell AND is clamped to that
    // layer's own grid. map_file._check_stamps refuses x + w past the block grid, and a layer at
    // a 24 cell offset reaches the right edge of its grid 24 cells before the canvas does.
    const [gx, gy] = gridCell(doc(), layer, where.cx, where.cy);
    const w = Math.min(patch.w, across() - gx);
    const h = Math.min(patch.h, down() - gy);
    if (gx < 0 || gy < 0 || w <= 0 || h <= 0) continue;
    doc().stamps.push({ name: brush.name, layer, x: gx, y: gy, w, h });
  }
}

/* Every cell joined to this one that holds the same value, four ways. (cx, cy) is a WORLD cell
   and so is every pair this returns; the walk itself runs over the layer's own grid. */
function floodRegion(layer, cx, cy) {
  const width = across();
  const height = down();
  const [sx, sy] = layerShiftCells(doc(), layer);
  const [gx, gy] = [cx + sx, cy + sy];
  if (!inGrid(gx, gy)) return [];
  const cells = doc().layers[layer].cells;
  const target = cells[gy * width + gx];
  const seen = new Uint8Array(width * height);
  const out = [];
  const stack = [gy * width + gx];
  seen[stack[0]] = 1;
  while (stack.length) {
    const at = stack.pop();
    if (cells[at] !== target) continue;
    const x = at % width;
    const y = Math.floor(at / width);
    out.push([x - sx, y - sy]);
    if (x > 0 && !seen[at - 1]) { seen[at - 1] = 1; stack.push(at - 1); }
    if (x < width - 1 && !seen[at + 1]) { seen[at + 1] = 1; stack.push(at + 1); }
    if (y > 0 && !seen[at - width]) { seen[at - width] = 1; stack.push(at - width); }
    if (y < height - 1 && !seen[at + width]) { seen[at + width] = 1; stack.push(at + width); }
  }
  return out;
}

/* The world cells of a dragged box, clipped to the canvas. */
function rectCells(x0, y0, x1, y1) {
  const out = [];
  for (let cy = Math.max(0, y0); cy <= Math.min(down() - 1, y1); cy += 1) {
    for (let cx = Math.max(0, x0); cx <= Math.min(across() - 1, x1); cx += 1) out.push([cx, cy]);
  }
  return out;
}

function fillCells(cells) {
  const patch = brushPatch();
  const plan = planFor(patch);
  tilePatch(patch, cells, plan);
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

/* (x0, y0) to (x1, y1) is a WORLD box. Each layer is read at its own offset, so one grab takes
   the piece of every layer that the owner actually sees under the box. Reading all four at the
   same grid cell took them up to 24 cells apart. */
function grabStamp(name, x0, y0, x1, y1) {
  const w = x1 - x0 + 1;
  const h = y1 - y0 + 1;
  const width = across();
  const tiles = doc().tiles;
  const cells = {};
  const drawn = new Uint8Array(w * h);      // did ANY layer taken put art in this cell
  const groups = [];                        // the animated groups this stamp carries, by pixels
  const groupSeat = new Map();              // document group index -> its index in `groups`
  let unknown = 0;
  let animated = 0;
  let kept = 0;

  /* A group is seated in the stamp the first time a cell names it, and its PIXELS come with it.
     That is what lets this stamp place its waving grass into a map that has never held it. */
  function seat(which) {
    if (groupSeat.has(which)) return groupSeat.get(which);
    const group = doc().animated[which];
    groupSeat.set(which, groups.length);
    groups.push({ first: group.first,
                  frames: (group.frames || []).map((f) => ({ duration: f.duration,
                                                             pixels: Array.from(f.pixels) })) });
    return groups.length - 1;
  }

  for (const layer of Object.keys(doc().layers)) {
    if (!grabs(layer)) continue;
    const source = doc().layers[layer].cells;
    const [sx, sy] = layerShiftCells(doc(), layer);
    const list = new Array(w * h).fill(null);
    let any = false;
    for (let y = 0; y < h; y += 1) {
      for (let x = 0; x < w; x += 1) {
        const gx = x0 + x + sx;
        const gy = y0 + y + sy;
        if (!inGrid(gx, gy)) continue;
        const value = source[gy * width + gx];
        const slot = value & TILE_INDEX;
        const flips = value & (FLIP_X | FLIP_Y);
        // THE GROUP IS TESTED FIRST, and a group cell is never run past slotIsBlank: the slot
        // sheet holds frame 0 alone, so a tile that is blank in frame 0 can be art in frame 1.
        const which = groupAtSlot(doc(), slot);
        if (which >= 0) {
          list[y * w + x] = animatedCell(seat(which), slot - doc().animated[which].first, flips);
          drawn[y * w + x] = 1;
          any = true;
          kept += 1;
          animated += 1;
          continue;
        }
        // Past the stream and in no group: this cell names a slot the SOURCE map never loads, so
        // there is nothing to take. It draws nothing in the game either.
        if (slot >= tiles.length) { unknown += 1; continue; }
        if (slotIsBlank(slot)) continue;
        list[y * w + x] = [tiles[slot][0], tiles[slot][1], flips];
        drawn[y * w + x] = 1;
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
  // A CELL THE GRAB LEFT EMPTY IS WORTH SAYING OUT LOUD. The game splits one picture across
  // layers, so a grab that reads only some of them comes back with a hole wherever the art sat on
  // a layer it did not read. The hole is invisible in the box and plain in the stamp.
  const blank = drawn.reduce((total, cell) => total + (cell ? 0 : 1), 0);
  const take = grabCollision === "take";
  return { stamp: { name, w, h, cells, animated: groups,
                    collision: take && anyOpen ? bits : null },
           unknown, animated, kept, blank, took: Object.keys(cells) };
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

async function postStamp(stamp, replace) {
  return (await fetch("/api/stamp", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...stamp, replace }),
  })).json();
}

/*
  A name already in the library is a QUESTION and not a refusal, exactly like a saved map: he
  grabs one piece of art twice while he is composing. The server wrote nothing to reach the
  question, so a No costs him nothing, and his Yes MOVES the old file into library\deleted\,
  which is where the delete control already puts things.
*/
async function keepStamp(stamp) {
  let answer = await postStamp(stamp, false);
  if (answer.taken) {
    const go = window.confirm(`A stamp called "${answer.taken}" is already in the library.\n\n`
                              + "Replace it? The stamp in the library now moves to "
                              + "map-editor\\library\\deleted\\, so it can be put back by hand.");
    if (!go) return { kept: false, replaced: "" };
    answer = await postStamp(stamp, true);
  }
  if (answer.error) throw new Error(answer.error);
  library = library.filter((s) => s.name !== stamp.name).concat([stamp]);
  library.sort((a, b) => a.name.localeCompare(b.name));
  host.refreshTools();
  return { kept: true, replaced: answer.replaced || "" };
}

/*
  The SERVER names an unnamed grab, because only the server sees library\deleted\. Numbering from
  the library count proposed a name that was already taken as soon as anything had been deleted.
*/
async function defaultStampName() {
  try {
    const answer = await (await fetch("/api/stampname")).json();
    if (answer.name) return answer.name;
  } catch (problem) {
    status(`the library could not be read: ${problem}. Is serve.py still running?`, "bad");
  }
  return `stamp ${library.length + 1}`;
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
    const layer = state.view.selected;
    const [gx, gy] = gridCell(doc(), layer, where.cx, where.cy);
    if (!inGrid(gx, gy)) return;
    const slot = doc().layers[layer].cells[gy * across() + gx] & TILE_INDEX;
    const which = groupAtSlot(doc(), slot);
    if (which >= 0) pickAnimatedTile(which, slot - doc().animated[which].first);
    else if (slot < doc().tiles.length) pickTile(doc().tiles[slot][0], doc().tiles[slot][1]);
    else status(`world ${where.cx}, ${where.cy} draws slot ${slot}, which this map never loads`, "bad");
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
  // The brush does not change inside a stroke, so only this first touch can add a tile or a
  // group. The sheet catches up while he drags, and the new slot draws blank for the frame or
  // two that takes. A GROUP counts here too: its pixels are new, so a drag that began by adding
  // one would paint from a sheet that never held it until he let go.
  if (stroke.tilesBefore || stroke.animatedBefore) redrawEverything();
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
  const name = host.stampName() || await defaultStampName();
  const made = grabStamp(name, x0, y0, Math.min(x1, across() - 1), Math.min(y1, down() - 1));
  if (!made.kept) {
    status(`nothing to grab at ${x0}, ${y0}: every cell in that box is empty`, "bad");
    return;
  }
  let answer;
  try {
    answer = await keepStamp(made.stamp);
  } catch (problem) {
    status(`${problem.message}`, "bad");
    return;
  }
  if (!answer.kept) {
    status(`"${name}" was NOT replaced and nothing was grabbed. Type another name in Grab name, `
           + "then drag the box again.", "info");
    return;
  }
  brush = { kind: "stamp", name, stamp: made.stamp };
  setTool("stamp");
  // WHAT IT TOOK, not what it lost. These cells used to be dropped and reported as "left out",
  // which described a loss he never agreed to. A grab now carries the group's pixels, so the
  // count is of art in hand.
  const note = made.animated
    ? `, ${made.animated} of them waving tiles from ${made.stamp.animated.length} animated `
      + `group(s), which travel with the stamp`
    : "";
  const lost = made.unknown
    ? `. ${made.unknown} cell(s) name a tile slot this map never loads, so there was nothing `
      + "there to take"
    : "";
  // The blank count, and where the missing art probably is. A hole in a stamp reads as a defect
  // in the grab, and it is nearly always the layer choice: another layer holds that art.
  const hole = made.blank
    ? `. ${made.blank} cell(s) came out EMPTY: nothing drew there on `
      + `${made.took.map((l) => l.toUpperCase()).join(", ") || "any layer taken"}`
      + (grabLayers === "all" ? ". That ground is empty in the map itself."
                              : ", and another layer may hold that art. Try every layer.")
    : "";
  // answer.replaced is the file the server moved aside, which a second replace timestamps.
  const old = answer.replaced
    ? `. The stamp it replaced is kept as library\\deleted\\${answer.replaced}` : "";
  status(`grabbed "${name}", ${made.stamp.w} x ${made.stamp.h} cells, ${made.kept} of them art`
         + `${made.stamp.collision ? ", with its collision" : ", no collision"}`
         + `${note}${lost}${hole}${old}`,
         made.blank ? "info" : "good");
}

// ===== changing a stamp that is already in the library =====

/*
  The file MOVES into library\deleted\ on the server. A stamp costs minutes of hunting a real map,
  so neither of these can be a one-way door. The brush is reset when it was holding the stamp,
  because a brush pointing at a library entry that is gone places nothing and says nothing.
*/
export async function deleteStamp(name) {
  const answer = await (await fetch("/api/stamp/delete", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  })).json();
  if (answer.error) throw new Error(answer.error);
  library = library.filter((s) => s.name !== name);
  if (brush.kind === "stamp" && brush.name === name) pickEraser();
  host.refreshTools();
}

/* Drop a stamp's collision, so it places art and writes no wall. The old file is kept. */
export async function stripStampCollision(name) {
  const answer = await (await fetch("/api/stamp/strip", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  })).json();
  if (answer.error) throw new Error(answer.error);
  library = library.map((s) => (s.name === name ? answer.stamp : s));
  if (brush.kind === "stamp" && brush.name === name) {
    brush = { kind: "stamp", name, stamp: answer.stamp };
  }
  host.refreshTools();
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

/*
  WHERE THE ANIMATED TILES ARE, cached exactly as the collision wash is. A world cell is marked
  when any SHOWN layer draws a slot that an animated group owns, read through that layer's own
  shift so the mark lands under the art it describes.

  MAGENTA, AND A DARK KEYLINE. The collision wash is red at 0.32, the grab box is blue and the
  brush ghost is orange, so the one free strong hue is magenta, and magenta is also the hue a
  green field cannot swallow. Measured on his own map at 3x: the wash alone reaches only 1.25
  luminance contrast over bright grass, so the mark is drawn as a dark keyline with a bright
  magenta line inside it. That pair reads on dark grass, bright grass and bare earth alike,
  which a single line cannot.
*/
function animatedLayer() {
  const [width, height] = [across() * TILE, down() * TILE];
  const shown = Object.keys(doc().layers).filter((name) => state.view.shown[name]).join(",");
  if (!animatedSheet || animatedSheet.width !== width || animatedSheet.height !== height) {
    animatedSheet = document.createElement("canvas");
    animatedSheet.width = width;
    animatedSheet.height = height;
    animatedDirty = true;
  }
  if (shown !== animatedShown) { animatedShown = shown; animatedDirty = true; }
  if (!animatedDirty) return animatedSheet;

  const ctx = animatedSheet.getContext("2d");
  ctx.clearRect(0, 0, width, height);
  ctx.lineWidth = 1;
  const marked = new Uint8Array(across() * down());
  for (const name of Object.keys(doc().layers)) {
    if (!state.view.shown[name]) continue;
    const cells = doc().layers[name].cells;
    const [sx, sy] = layerShiftCells(doc(), name);
    for (let cy = 0; cy < down(); cy += 1) {
      for (let cx = 0; cx < across(); cx += 1) {
        const gx = cx + sx;
        const gy = cy + sy;
        if (!inGrid(gx, gy)) continue;
        if (groupAtSlot(doc(), cells[gy * across() + gx] & TILE_INDEX) < 0) continue;
        marked[cy * across() + cx] = 1;
      }
    }
  }
  for (let cy = 0; cy < down(); cy += 1) {
    for (let cx = 0; cx < across(); cx += 1) {
      if (!marked[cy * across() + cx]) continue;
      const x = cx * TILE;
      const y = cy * TILE;
      ctx.fillStyle = "rgba(236, 72, 232, 0.45)";
      ctx.fillRect(x, y, TILE, TILE);
      ctx.strokeStyle = "rgba(32, 0, 36, 0.85)";
      ctx.strokeRect(x + 0.5, y + 0.5, TILE - 1, TILE - 1);
      ctx.strokeStyle = "rgba(255, 140, 255, 1)";
      ctx.strokeRect(x + 1.5, y + 1.5, TILE - 3, TILE - 3);
    }
  }
  animatedDirty = false;
  return animatedSheet;
}

/* The brush, drawn where it would land. Real art when its chunk atlas is loaded, an outline else. */
function drawGhost(ctx, patch, px, py) {
  // Each group is matched ONCE per ghost, not once per cell. findGroup compares whole frames, so
  // a 64 tile group is 65,536 numbers a comparison, and the ghost redraws on every mouse move.
  const groupFirst = new Map();
  const firstOf = (which) => {
    if (!groupFirst.has(which)) {
      const held = findGroup(doc(), (patch.animated || [])[which]);
      groupFirst.set(which, held < 0 ? null : doc().animated[held].first);
    }
    return groupFirst.get(which);
  };
  ctx.save();
  ctx.globalAlpha = 0.75;
  for (const [layer, cells] of Object.entries(patch.layers)) {
    if (!doc().layers[layer]) continue;
    for (let y = 0; y < patch.h; y += 1) {
      for (let x = 0; x < patch.w; x += 1) {
        const cell = cells[y * patch.w + x];
        if (!cell) continue;
        // An animated cell is drawn from the SLOT SHEET, which already holds every group this
        // map loads. A group the map has not got yet draws nothing here, because the ghost may
        // not add one: a hover must change no document.
        if (isAnimatedCell(cell)) {
          const sheet = sheetCanvas();
          const first = firstOf(cell.g);
          if (!sheet || first === null) continue;
          const slot = first + cell.t;
          ctx.drawImage(sheet, (slot % 32) * TILE, Math.floor(slot / 32) * TILE, TILE, TILE,
                        (px + x) * TILE, (py + y) * TILE, TILE, TILE);
          continue;
        }
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
  if (showAnimated) ctx.drawImage(animatedLayer(), 0, 0);

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
  if (!hover || !onCanvas(hover.cx, hover.cy)) return;
  if (tool === "tile" || tool === "stamp" || tool === "fill") {
    drawGhost(ctx, brushPatch(), hover.cx, hover.cy);
  }
}

/* A tile or a stamp dropped on the map from the left pane. His words: drag and drop. */
export function dropAt(payload, where) {
  if (!state.doc) return;
  if (payload.kind === "stamp") pickStamp(payload.name);
  else if (payload.kind === "anim") pickAnimatedTile(payload.group, payload.tile);
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
