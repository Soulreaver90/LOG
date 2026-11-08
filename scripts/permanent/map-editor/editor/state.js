/*
  state.js - The one copy of what the editor is holding, and the one way to hear it change.

  Holds   assets   the manifest from assets.json, loaded once
          doc      the map document, exactly the shape map_file.py writes
          view     what the owner is looking at: zoom, which layers are shown, which is selected
  Change  set(patch) or edit(fn) mutates, then tells every subscriber what moved.
          subscribe("doc" | "view" | "assets" | "status" | "dirty", fn)
  Dirty   every change to the document raises it, and only a Save lowers it. autosave.js listens
          on "dirty", so one flag drives the marker in the page, the unload guard and the write.
          It is raised HERE, in edit(), because the truth panel's world size goes through edit()
          and never through the undo history, so a hook on history alone would miss it.
  Seam    Task 5's tools and Task 6's truth panel read the document here and push their changes
          through edit(), so undo has one place to watch. Nothing else keeps a second copy.
  Rule    the document is never repaired on the way in. Problems come from Python's validate() and
          are shown, so a map that the game would refuse looks wrong here too.
*/

const listeners = { doc: [], view: [], assets: [], status: [], dirty: [] };

export const state = {
  assets: null,          // {chunks: [{index, tiles, png}], palettes: [[[r,g,b] x 256]], tile_budget, transparent_index}
  doc: null,             // the map document, or null before the first open
  problems: [],          // validate() from the server, shown rather than fixed
  title: "",             // what the owner opened, for the header
  dirty: false,          // changed since the last Save. The page says so and guards the unload
  view: { zoom: 1, shown: { bg0: true, bg1: true, bg2: true, bg3: true }, selected: "bg3" },
};

export function subscribe(what, fn) {
  listeners[what].push(fn);
  return () => listeners[what].splice(listeners[what].indexOf(fn), 1);
}

export function notify(what) {
  for (const fn of listeners[what]) fn(state);
}

export function setDoc(doc, problems, title) {
  state.doc = doc;
  state.problems = problems || [];
  state.title = title;
  if (doc && !doc.layers[state.view.selected]) state.view.selected = Object.keys(doc.layers)[0];
  markClean();                       // what just arrived IS what the server holds
  notify("doc");
}

/*
  Raised on every change, not only on the first one, because the autosave's clock restarts on each
  one. The marker it repaints is one textContent write, so saying it twice costs nothing and
  missing it once costs the work.
*/
export function markDirty() {
  state.dirty = true;
  notify("dirty");
}

export function markClean() {
  state.dirty = false;
  notify("dirty");
}

export function setView(patch) {
  Object.assign(state.view, patch);
  notify("view");
}

/* Task 5 calls this: mutate the document in place, then one notify. */
export function edit(fn) {
  fn(state.doc);
  markDirty();
  notify("doc");
}

export function status(text, kind = "info") {
  state.status = { text, kind };
  notify("status");
}

// ===== the layer order, which is the hardware's and not a fixed list =====

/*
  Back to front. The GBA draws a HIGH priority number furthest away, and among equal priorities it
  draws the LOWER BG number in front. Map 7,15 reads [3,1,3,3], so its BG1 is a canopy that draws
  over the player and over BG0. A fixed bg3,bg2,bg1,bg0 order, which is what a full-map render uses,
  would put that canopy behind the trees it belongs in front of.
*/
export function drawOrder(doc) {
  return Object.keys(doc.layers).sort((a, b) => {
    const pa = doc.layers[a].priority, pb = doc.layers[b].priority;
    return pb - pa || b.localeCompare(a);
  });
}

// ===== the counts the right pane shows live =====

export const BLOCK_TILES = 32;
export const BLOCK_PIXELS = 256;
export const TILE_INDEX = 0x3FF;
export const FLIP_X = 0x400;
export const FLIP_Y = 0x800;
export const SCROLL_ONE = 0x400;   // a layer's +0x04 and +0x08: 0x400 is 1.0 (bible tag BMS)
export const VIEW_W = 240;
export const VIEW_H = 160;
/* The two animated group limits, mirrored from map_file.py as the constants above are. They are
   not in assets.json because that manifest describes the ART, and these are the loader's own
   bounds: 16 groups in the IWRAM state array, and 64 tiles a group in the 0x1000 byte load
   buffer (bible B1078). map_file._check_animated refuses a document that breaks either. */
export const GROUP_MAX = 16;
export const GROUP_MAX_TILES = 64;

/*
  Every VRAM slot the map fills: the static +0x48 stream, then each animated group's own span.
  This mirrors map_file.loaded_slots. The static stream alone is NOT the map's tiles: 7,15 streams
  633 and its cells name slot 894, which an animated group loads. A renderer that stopped at the
  stream drew 509 false cells on the plateau and cost a day.
*/
export function loadedSlots(doc, budget) {
  const slots = new Set();
  const stream = Math.min((doc.tiles || []).length, budget);
  for (let n = 0; n < stream; n += 1) slots.add(n);
  for (const group of doc.animated || []) {
    const count = groupTiles(group);
    for (let n = 0; n < count && group.first + n < budget; n += 1) slots.add(group.first + n);
  }
  return slots;
}

export function groupTiles(group) {
  const frames = group.frames || [];
  return frames.length ? Math.floor((frames[0].pixels || []).length / 64) : 0;
}

/* The layout +0x08 and +0x0A words. Pinned to map_file.camera_pair: 1024 x 1024 gives 785, 865. */
export function cameraPair(widthPx, heightPx) {
  return [widthPx - (VIEW_W - 1), heightPx - (VIEW_H - 1)];
}

// ===== world pixels and layer cells, the one transform =====

/*
  A BG layer record's +0x0C and +0x10 are a scroll OFFSET, and the game ADDS them to the camera
  before it writes REG_BGxHOFS and REG_BGxVOFS (layer update sub_080055A4: the adds at 0x080055B4
  and 0x080055C8, the stores at 0x08005610 and 0x08005614). Raising a scroll register moves the
  view right, so the cell at layer grid (gx, gy) is seen at WORLD (gx - shift, gy - shift).

  THE CANVAS IS IN WORLD PIXELS. Collision and terrain are already world, and they are the only
  thing in the editor that was ever in the same space as the game. Map 3,11's lake sat 192 px off
  its own closed region until this landed, and the owner saw it by eye. So the picture, the cursor,
  the brush ghost, the collision wash and the screen box all live in world pixels, and a layer's
  own grid cell is reached through gridCell() and nowhere else.
*/
export function layerShift(doc, name) {
  const offset = ((doc.layers || {})[name] || {}).offset || [0, 0];
  return offset.map((word) => (word >= 0x80000000 ? word - 0x100000000 : word) >> 10);
}

/*
  The same shift in whole CELLS. Every layer that scrolls 1 to 1 stores a whole multiple of 64 px,
  so this is exact on all 1273 of them; the 21 that scroll off 1.0 include three layers storing 10,
  30 and 202 px, which floor to a cell and are only ever drawn at camera 0,0 anyway.
*/
export function layerShiftCells(doc, name) {
  return layerShift(doc, name).map((px) => Math.floor(px / 8));
}

/* The cell of THIS layer's own grid that is seen at world cell (wx, wy). */
export function gridCell(doc, name, wx, wy) {
  const [sx, sy] = layerShiftCells(doc, name);
  return [wx + sx, wy + sy];
}

// ===== where a stamp lands, and the box it records =====

/*
  A STAMP'S LAYER NAMES ARE PROVENANCE, NOT IDENTITY. It is the same rule that makes a stamp store
  a [chunk, tile] pair rather than a VRAM slot, and that keeps an animated group's `first` as a
  note: what the stamp recorded about the map it came from may mean something else in the map it
  lands in. Grass taken from BG3 is grass, and it has to go on the BG1 a cliff is drawn on.

  ONE LAYER LANDS ON THE SELECTED LAYER. No option and no question. That is what a stamp is for.

  SEVERAL LAYERS KEEP THEIR STACK, because the order is what makes a boulder with ground under it
  read correctly. The whole stack SLIDES along the draw order until its frontmost layer sits on
  the selected one. Sliding keeps the gaps inside the stack, and it is the identity when the stamp
  goes back on the layer it came from, which the common case of restamping the same map needs.

  THE SLIDE IS ONE STEP OF DRAW ORDER, NEVER OF BG NUMBER. Priority is per layer per map, so BG
  number is not the draw order: map 7,15 draws BG3, BG2, BG0, BG1 back to front. A BG-number slide
  of a BG2 + BG3 stamp onto BG0 would land it on BG0 and BG1 and come back REVERSED, with its back
  layer in front. A draw-order slide cannot reverse a stack, because it moves every layer of it by
  the same number of places.

  A STACK WITH NO ROOM BEHIND IT IS REFUSED WHOLE, and the message names the layers and the
  nearest selection that would hold it. Half an object is worse than none.

  A stamp records no priority, so the draw order used is the DESTINATION map's. Inside one map
  that is exact, and it is the most a stamp from another map can know.

  Returns {map, problem}: `map` is {stamp layer -> destination layer}, or null when `problem` is
  the sentence to show him.
*/
export function stampLanding(doc, selected, names) {
  const up = (name) => name.toUpperCase();
  const list = (of) => of.map(up).join(", ");
  if (!names.length) return { map: {}, problem: null };
  if (!(doc.layers || {})[selected]) {
    return { map: null, problem: `this map has not got a layer ${up(selected)}` };
  }
  if (names.length === 1) return { map: { [names[0]]: selected }, problem: null };

  const missing = names.filter((name) => !doc.layers[name]);
  if (missing.length) {
    return { map: null,
             problem: `this stamp is drawn across ${names.length} layers (${list(names)}) and this `
                      + `map has not got ${list(missing)}, so nothing was placed` };
  }
  const order = drawOrder(doc);                       // back to front
  const at = new Map(order.map((name, index) => [name, index]));
  const front = names.reduce((best, name) => (at.get(name) > at.get(best) ? name : best));
  const back = names.reduce((worst, name) => (at.get(name) < at.get(worst) ? name : worst));
  const shift = at.get(selected) - at.get(front);
  if (at.get(back) + shift < 0) {
    const nearest = order[at.get(front) - at.get(back)];
    return { map: null,
             problem: `this stamp is drawn across ${list(names)}, and this map has no room for `
                      + `that stack at or behind ${up(selected)}. Nothing was placed. Select `
                      + `${up(nearest)} or a layer in front of it.` };
  }
  const map = {};
  for (const name of names) map[name] = order[at.get(name) + shift];
  return { map, problem: null };
}

/*
  The box one layer of a stamp placement records, in that layer's OWN grid cells, clamped to that
  layer's OWN grid. The layer is the one it LANDS on, never the one it was grabbed from.
  map_file._check_stamps refuses x + w past the block grid, and a layer at a 24 cell offset reaches
  the right edge of its grid 24 cells before the canvas does. On map 7,15 BG1 sits at 8 cells and
  BG3 at 24, so one drop records two different boxes depending on where it lands.
  null when that layer has no room at the drop at all.
*/
export function stampRecord(doc, layer, cx, cy, w, h) {
  const [gx, gy] = gridCell(doc, layer, cx, cy);
  const across = doc.blocks[0] * BLOCK_TILES;
  const down = doc.blocks[1] * BLOCK_TILES;
  const box = { x: gx, y: gy, w: Math.min(w, across - gx), h: Math.min(h, down - gy) };
  if (box.x < 0 || box.y < 0 || box.w <= 0 || box.h <= 0) return null;
  return box;
}
