/*
  state.js - The one copy of what the editor is holding, and the one way to hear it change.

  Holds   assets   the manifest from assets.json, loaded once
          doc      the map document, exactly the shape map_file.py writes
          view     what the owner is looking at: zoom, which layers are shown, which is selected
  Change  set(patch) or edit(fn) mutates, then tells every subscriber what moved.
          subscribe("doc" | "view" | "assets" | "status", fn)
  Seam    Task 5's tools and Task 6's truth panel read the document here and push their changes
          through edit(), so undo has one place to watch. Nothing else keeps a second copy.
  Rule    the document is never repaired on the way in. Problems come from Python's validate() and
          are shown, so a map that the game would refuse looks wrong here too.
*/

const listeners = { doc: [], view: [], assets: [], status: [] };

export const state = {
  assets: null,          // {chunks: [{index, tiles, png}], palettes: [[[r,g,b] x 256]], tile_budget, transparent_index}
  doc: null,             // the map document, or null before the first open
  problems: [],          // validate() from the server, shown rather than fixed
  title: "",             // what the owner opened, for the header
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
  notify("doc");
}

export function setView(patch) {
  Object.assign(state.view, patch);
  notify("view");
}

/* Task 5 calls this: mutate the document in place, then one notify. */
export function edit(fn) {
  fn(state.doc);
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
export const VIEW_W = 240;
export const VIEW_H = 160;

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
