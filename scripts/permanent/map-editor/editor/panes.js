/*
  panes.js - Wire the three panes, and own the two ways a map arrives.

  Layout A, the one the owner chose: tiles left, map centre, layers and properties right.

  Seams for the tasks that follow, so neither has to rewrite this file's shape.
    onCanvasPointer(fn)  the tools get every pointer event on the map, in CELL coordinates,
                         with the button, so right click can paint collision.
    addRightPanel(node)  a later panel appends itself to the right pane under the properties it
                         already shows. The truth panel's own controls are static markup in
                         index.html, beside every other control on this page, and truth.js wires
                         them by id.
    addToolbarItem(node) a later tool's controls go in the centre pane's second bar.
    addOverlay(fn)       the truth panel's shading draws onto the overlay canvas, which sits
                         exactly over the map, without touching tools.js.
    redraw()             redraw the visible canvas from the layer canvases.
    refreshCounts()      redraw the right pane after an edit changed the tile list.

  THE OVERLAY IS ITS OWN CANVAS. The brush ghost follows the pointer, and recompositing four
  1280 x 1024 layers on every move to rub out the last ghost would make the map lag behind the
  hand. The overlay clears and redraws alone.

  THE TILE COUNT shows LOADED SLOTS, not the static stream. 7,15 streams 633 tiles and loads 635
  slots, because its one animated group owns 894 and 895. "633 / 896" would read as 263 slots
  free, when the stream can only grow to 894. The sub-line breaks the number into its two parts,
  so the owner can see which half is his to spend.
*/
import {
  state, subscribe, setDoc, setView, status, markClean,
  drawOrder, loadedSlots, groupTiles, cameraPair, gridCell, layerShiftCells,
} from "./state.js";
import { buildSheet, drawAllLayers, composite, layerSize, forget, sheetCanvas, drawGroupTile }
  from "./render.js";
import { groupAtSlot, isAnimatedCell } from "./cells.js";
import * as tools from "./tools.js";
import * as truth from "./truth.js";
import * as autosave from "./autosave.js";

const BLOCK_CAP = 8;       // 8 blocks is 2048 px, which is where the 256 cell collision grid stops
const THUMB = 48;          // the stamp preview box in the left pane, in CSS px
const pointerHooks = [];
const overlayHooks = [];
const atlasCache = new Map();
const atlasLoaded = new Map();      // chunk -> the <img>, once it has arrived
let canvas = null;
let ctx = null;
let overlay = null;
let octx = null;

const $ = (id) => document.getElementById(id);

// ===== seams =====

export function onCanvasPointer(fn) {
  pointerHooks.push(fn);
}

export function addRightPanel(node) {
  $("panels").append(node);
}

export function addToolbarItem(node) {
  $("toolbar").append(node);
}

export function addOverlay(fn) {
  overlayHooks.push(fn);
}

export function redraw() {
  if (!state.doc) return;
  composite(ctx, state.doc, state.view.shown);
}

export function paintOverlay() {
  if (!state.doc) return;
  octx.clearRect(0, 0, overlay.width, overlay.height);
  tools.drawOverlay(octx);
  for (const fn of overlayHooks) fn(octx, state.doc);
}

// ===== assets =====

async function loadAssets() {
  state.assets = await (await fetch("assets/assets.json")).json();
}

function atlasFor(chunk) {
  if (!atlasCache.has(chunk)) {
    atlasCache.set(chunk, new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => { atlasLoaded.set(chunk, img); resolve(img); };
      img.onerror = () => reject(new Error(`chunk ${chunk} has no atlas in assets\\chunks`));
      img.src = `assets/chunks/${chunk}.png`;
    }));
  }
  return atlasCache.get(chunk);
}

/* The atlas if it is here NOW, else a request for it. A ghost cannot wait for a promise. */
function atlasReady(chunk) {
  if (!atlasCache.has(chunk)) atlasFor(chunk).then(paintOverlay, () => {});
  return atlasLoaded.get(chunk) || null;
}

// ===== the left pane: the tiles this map loads, and the pool it may draw from =====

/*
  One thumbnail. `payload` is what a drop on the map carries, and clicking it picks the same
  thing as the brush. Drag and drop and click do the same thing on purpose: his words were drag
  and drop, and a click is faster once the tool is already Tile.
*/
function tileButton(label, draw, payload) {
  const cell = document.createElement("canvas");
  cell.width = 8;
  cell.height = 8;
  cell.className = "tile";
  cell.title = label;
  draw(cell.getContext("2d"));
  if (!payload) return cell;
  cell.draggable = true;
  cell.ondragstart = (event) => event.dataTransfer.setData("text/plain", JSON.stringify(payload));
  cell.onclick = () => (payload.kind === "anim"
    ? tools.pickAnimatedTile(payload.group, payload.tile)
    : tools.pickTile(payload.chunk, payload.tile));
  return cell;
}

function paintPalette() {
  const list = $("palette");
  list.replaceChildren();
  if (!state.doc) return;
  const slots = [...loadedSlots(state.doc, state.assets.tile_budget)].sort((a, b) => a - b);
  const sheet = sheetCanvas();
  const tiles = state.doc.tiles || [];
  for (const slot of slots) {
    // A slot an ANIMATED GROUP owns has no chunk tile behind it, so it carries the group and the
    // tile inside it instead. It is picked up like any other tile: the brush then places waving
    // grass by hand, which is the only way to touch up what a stamp laid down.
    const which = groupAtSlot(state.doc, slot);
    const pair = which < 0 && slot < tiles.length ? tiles[slot] : null;
    const payload = which >= 0
      ? { kind: "anim", group: which, tile: slot - state.doc.animated[which].first }
      : (pair ? { kind: "tile", chunk: pair[0], tile: pair[1] } : null);
    const label = which >= 0
      ? `slot ${slot}: animated group ${which}, tile ${slot - state.doc.animated[which].first}`
      : (pair ? `slot ${slot}: chunk ${pair[0]} tile ${pair[1]}` : `slot ${slot}: nothing loads it`);
    list.append(tileButton(
      label,
      (c) => c.drawImage(sheet, (slot % 32) * 8, Math.floor(slot / 32) * 8, 8, 8, 0, 0, 8, 8),
      payload));
  }
  $("palette-count").textContent = `${slots.length} loaded`;
}

async function paintPool(chunk) {
  const pool = $("pool");
  pool.replaceChildren();
  const entry = state.assets.chunks.find((c) => c.index === chunk);
  if (!entry) return;
  const atlas = await atlasFor(chunk);
  for (let tile = 0; tile < entry.tiles; tile += 1) {
    pool.append(tileButton(`chunk ${chunk} tile ${tile}`, (c) =>
      c.drawImage(atlas, (tile % 16) * 8, Math.floor(tile / 16) * 8, 8, 8, 0, 0, 8, 8),
      { kind: "tile", chunk, tile }));
  }
}

/* The stamp library: every stamp grabbed in any session, at its own size, capped to a box. */
function paintStamps() {
  const list = $("stamps");
  const library = tools.current().library;
  list.replaceChildren();
  $("stamp-count").textContent = library.length
    ? `${library.length} grabbed` : "drag a Grab box to make one";
  for (const stamp of library) {
    const view = document.createElement("canvas");
    view.width = stamp.w * 8;
    view.height = stamp.h * 8;
    view.className = "tile";
    const scale = Math.min(THUMB / view.width, THUMB / view.height, 3);
    view.style.width = `${Math.max(8, Math.round(view.width * scale))}px`;
    view.style.height = `${Math.max(8, Math.round(view.height * scale))}px`;
    view.title = `${stamp.name}  ${stamp.w} x ${stamp.h} cells`
                 + (stamp.collision ? ", carries its collision" : ", no collision");
    drawStamp(view.getContext("2d"), stamp);
    view.draggable = true;
    view.ondragstart = (event) =>
      event.dataTransfer.setData("text/plain", JSON.stringify({ kind: "stamp", name: stamp.name }));
    view.onclick = () => { tools.pickStamp(stamp.name); tools.setTool("stamp"); };

    const box = document.createElement("figure");
    box.className = "stamp";
    const acts = document.createElement("div");
    acts.className = "stampacts";
    if (stamp.collision) acts.append(stampAction("no wall", "strip",
      `Drop the collision from "${stamp.name}". It then paints art and no wall at all.`,
      () => stripStamp(stamp.name)));
    acts.append(stampAction("delete", "drop",
      `Remove "${stamp.name}" from the library. The file moves to library\\deleted\\.`,
      () => removeStamp(stamp.name)));
    box.append(view, acts);
    list.append(box);
  }
}

function stampAction(label, kind, hint, run) {
  const button = document.createElement("button");
  button.className = `stampact ${kind}`;
  button.textContent = label;
  button.title = hint;
  button.onclick = (event) => { event.stopPropagation(); run(); };
  return button;
}

/*
  Both of these ask first, and both are recoverable by hand: the server MOVES the old file into
  library\deleted\ rather than unlinking it. He spends minutes grabbing a stamp, so a misclick
  must cost a trip to a folder and never the stamp.
*/
async function removeStamp(name) {
  if (!window.confirm(`Delete the stamp "${name}"?\n\n`
                      + "The file moves to map-editor\\library\\deleted\\, so it can be put back "
                      + "by hand.")) return;
  try {
    await tools.deleteStamp(name);
    status(`deleted "${name}". Its file is in library\\deleted\\.`, "good");
  } catch (problem) {
    status(`"${name}" was NOT deleted: ${problem.message}`, "bad");
  }
}

async function stripStamp(name) {
  if (!window.confirm(`Drop the collision from the stamp "${name}"?\n\n`
                      + "It will then place art alone and write no wall. The stamp as it is now "
                      + "is kept in map-editor\\library\\deleted\\.")) return;
  try {
    await tools.stripStampCollision(name);
    status(`"${name}" now carries no collision. The old copy is in library\\deleted\\.`, "good");
  } catch (problem) {
    status(`"${name}" was NOT changed: ${problem.message}`, "bad");
  }
}

/*
  A stamp preview, back to front. A static cell comes from its chunk atlas, and a chunk still
  loading draws next time. An ANIMATED cell comes from the group the stamp carries, drawn at its
  first frame, which is what the map itself shows at rest.
*/
function drawStamp(target, stamp) {
  const palette = state.assets.palettes[0];
  const transparent = state.assets.transparent_index;
  for (const [layer, cells] of Object.entries(stamp.cells)) {
    void layer;
    cells.forEach((cell, at) => {
      if (!cell) return;
      const dx = (at % stamp.w) * 8;
      const dy = Math.floor(at / stamp.w) * 8;
      if (isAnimatedCell(cell)) {
        drawGroupTile(target, (stamp.animated || [])[cell.g], cell.t, dx, dy, palette, transparent);
        return;
      }
      const atlas = atlasReady(cell[0]);
      if (!atlas) return;
      target.drawImage(atlas, (cell[1] % 16) * 8, Math.floor(cell[1] / 16) * 8, 8, 8, dx, dy, 8, 8);
    });
  }
}

// ===== the tools row =====

function paintTools() {
  const now = tools.current();
  for (const button of document.querySelectorAll(".tool")) {
    button.classList.toggle("on", button.dataset.tool === now.tool);
  }
  $("size").replaceChildren(...now.sizes.map((size) => {
    const option = document.createElement("option");
    option.value = String(size);
    option.textContent = `${size} x ${size}`;
    return option;
  }));
  $("size").value = String(now.brushSize);
  $("size").disabled = now.brush.kind === "stamp";
  $("erase").classList.toggle("on", now.brush.name === "eraser");
  $("collmode").value = now.collisionPaint;
  $("showcoll").checked = now.showCollision;
  $("showanim").checked = now.showAnimated;
  // These two name LAYERS and not kinds of thing, and which layer they mean moves with the
  // selection. The game splits one picture across layers: on map 7,15 there are cells where BG3
  // draws nothing and BG1 or BG2 draws the art, so a grab of one layer comes back with a hole
  // there. Naming the layer in the option is what tells him which half he is taking.
  const here = state.view.selected.toUpperCase();
  $("grablayers").options[0].textContent = `every layer but ${here}`;
  $("grablayers").options[1].textContent = `${here} only`;
  $("grablayers").value = now.grabLayers;
  $("grabcoll").value = now.grabCollision;
  $("undo").disabled = !now.undo.done;
  $("redo").disabled = !now.undo.undone;
  $("brushnote").textContent = `brush: ${now.brush.name}`
    + (now.brush.kind === "stamp" ? ` (${now.brush.stamp.w} x ${now.brush.stamp.h})` : "")
    + `   layer ${state.view.selected.toUpperCase()}   ${now.undo.done} step(s) back`;
  paintStamps();
}

// ===== the right pane: layers, the grid, and the live counts =====

function paintLayers() {
  const list = $("layers");
  list.replaceChildren();
  if (!state.doc) return;
  for (const name of drawOrder(state.doc).reverse()) {       // front to back, the way the eye reads
    const layer = state.doc.layers[name];
    const row = document.createElement("label");
    row.className = "layerrow" + (state.view.selected === name ? " on" : "");

    const shown = document.createElement("input");
    shown.type = "checkbox";
    shown.checked = state.view.shown[name];
    shown.onchange = () => {
      state.view.shown[name] = shown.checked;
      setView({});
    };

    const pick = document.createElement("button");
    pick.className = "layername";
    pick.textContent = name.toUpperCase();
    pick.onclick = () => setView({ selected: name });

    const facts = document.createElement("span");
    const scroll = layer.scroll.map((s) => (s / 0x400).toFixed(2)).join(", ");
    facts.className = "layerfacts";
    facts.textContent = `prio ${layer.priority}  scroll ${scroll}`;
    facts.title = "Priority and scroll are read from the map and shown, never applied here.";

    row.append(shown, pick, facts);
    list.append(row);
  }
}

export function refreshCounts() {
  const doc = state.doc;
  if (!doc) return;
  const budget = state.assets.tile_budget;
  const slots = loadedSlots(doc, budget).size;
  const stream = (doc.tiles || []).length;
  const groups = (doc.animated || []).map((g) => `${groupTiles(g)} at ${g.first}`);

  $("tilecount").textContent = `${slots} / ${budget}`;
  $("tilecount").className = slots > budget ? "big over" : "big";
  $("tilesplit").textContent = groups.length
    ? `static ${stream}, animated ${groups.join(", ")}`
    : `static ${stream}, no animated groups`;

  const [gw, gh] = layerSize(doc);
  const [cx, cy] = cameraPair(doc.world[0], doc.world[1]);
  $("facts").replaceChildren(...[
    ["blocks", `${doc.blocks[0]} x ${doc.blocks[1]}  (${gw} x ${gh} px)`],
    ["world", `${doc.world[0]} x ${doc.world[1]} px`],
    ["camera", `+0x08 ${cx}   +0x0A ${cy}`],
    ["schema", String(doc.schema)],
  ].flatMap(([key, value]) => {
    const dt = document.createElement("dt");
    dt.textContent = key;
    const dd = document.createElement("dd");
    dd.textContent = value;
    return [dt, dd];
  }));

  const notes = [...state.problems.map((p) => ["bad", p]),
                 ...(doc.dropped || []).map((d) => ["warn", `dropped: ${d}`])];
  $("problems").replaceChildren(...notes.map(([kind, text]) => {
    const li = document.createElement("li");
    li.className = kind;
    li.textContent = text;
    return li;
  }));
  $("problems-head").textContent = notes.length ? `${notes.length} note(s)` : "no problems";
}

// ===== the centre pane =====

function fitCanvas() {
  const [width, height] = layerSize(state.doc);
  canvas.width = width;
  canvas.height = height;
  overlay.width = width;
  overlay.height = height;
  applyZoom();
}

function applyZoom() {
  for (const target of [canvas, overlay]) {
    target.style.width = `${target.width * state.view.zoom}px`;
    target.style.height = `${target.height * state.view.zoom}px`;
  }
}

/*
  The WORLD cell under a pointer. The scale is read from the canvas itself rather than from the
  zoom, so a canvas the browser lays out one pixel off still names the cell the owner is looking
  at, and clientLeft takes the border off the rect, which is the border box edge.

  cx and cy are WORLD cells, the same space as the collision grid and as what the camera shows.
  A layer's own grid cell is state.gridCell(doc, layer, cx, cy), because each layer sits at its
  own offset. Every tool takes this pair and converts, so the cursor, the ghost and the stroke
  cannot land in three different places.
*/
function cellAt(event) {
  const box = canvas.getBoundingClientRect();
  const scale = canvas.clientWidth / canvas.width;
  const x = Math.floor((event.clientX - box.left - canvas.clientLeft) / scale / 8);
  const y = Math.floor((event.clientY - box.top - canvas.clientTop) / scale / 8);
  return { cx: x, cy: y, button: event.button, event };
}

/* World first, because that is what the game and the collision grid use, then the selected
   layer's own cell, because that is the cell a stroke writes. The two differ by the layer's
   offset: on map 3,11's BG3 they are 24 cells apart. */
function whereText(where) {
  const doc = state.doc;
  const layer = state.view.selected;
  const text = `world ${where.cx}, ${where.cy}   px ${where.cx * 8}, ${where.cy * 8}`;
  if (!doc || !doc.layers[layer]) return text;
  const [gx, gy] = gridCell(doc, layer, where.cx, where.cy);
  const [sx, sy] = layerShiftCells(doc, layer);
  return sx || sy ? `${text}   ${layer} cell ${gx}, ${gy}` : text;
}

function wirePointer() {
  for (const kind of ["pointerdown", "pointermove", "pointerup", "pointercancel"]) {
    canvas.addEventListener(kind, (event) => {
      // Capture on the way down, so a stroke that ends off the canvas still ends, and one drag
      // stays one undo step. A synthetic event carries no live pointer id, and refusing to
      // capture one must not stop the stroke.
      if (kind === "pointerdown") {
        try { canvas.setPointerCapture(event.pointerId); } catch (ignored) { void ignored; }
      }
      const where = cellAt(event);
      $("where").textContent = whereText(where);
      for (const fn of pointerHooks) fn(kind === "pointercancel" ? "pointerup" : kind, where);
    });
  }
  canvas.addEventListener("contextmenu", (e) => e.preventDefault());   // right click is a tool
  canvas.addEventListener("dragover", (event) => event.preventDefault());
  canvas.addEventListener("drop", (event) => {
    event.preventDefault();
    const text = event.dataTransfer.getData("text/plain");
    if (text) tools.dropAt(JSON.parse(text), cellAt(event));
  });
}

// ===== opening a map =====

async function show(payload, title) {
  setDoc(payload.doc, payload.problems, title);
  forget();
  tools.reset();                      // a step back into the map before this one is not a step back
  await buildSheet(state.doc, state.assets, atlasFor);
  drawAllLayers(state.doc);
  fitCanvas();
  redraw();
  paintLayers();
  paintPalette();
  refreshCounts();
  paintTools();
  truth.refresh();                    // its lost-art count needs the slot sheet, built just above
  paintOverlay();
  $("title").textContent = title;
  status(payload.problems.length ? `${title}: ${payload.problems.length} problem(s)` : `${title} open`,
         payload.problems.length ? "bad" : "good");
}

/*
  REPLACING THE OPEN DOCUMENT IS A WAY OUT OF IT, exactly like a reload. beforeunload covers
  leaving the page and nothing covered this: Open a copy, Start and Open both threw the open map
  away without a word. So every one of them asks first, and whatever he decides, the work reaches
  the disk before the new map arrives.
*/
async function leaveOpenMap(what) {
  if (!state.dirty) return true;
  const keep = window.confirm(`"${state.title}" has changes that are not saved.\n\n`
                              + `${what}\n\nThe changes are kept in map-editor\\autosave\\ either `
                              + "way, and can be restored. Press Save first to keep them as a map.");
  if (!keep) return false;
  await autosave.flush();
  return true;
}

async function ask(url, title) {
  status(`reading ${title} ...`);
  const payload = await (await fetch(url)).json();
  if (payload.error) {
    status(`${title}: ${payload.error}`, "bad");
    return;
  }
  await show(payload, title);
}

/*
  Every map in the live table. The name is the project's own recorded one from
  docs\research\map-names.md, and is absent when that file is. Nothing here decodes the ROM's name
  pool: a plain walk of rom:0xE2840 reads 7,15 as Triceratops Jungle, which belongs to 4,50, so the
  pool is not a flat list of strings and a decode would label every map wrong.
*/
async function fillMapPicker() {
  const { maps } = await (await fetch("/api/maps")).json();
  const pick = $("mapsel");
  pick.replaceChildren(...maps.map((m) => {
    const option = document.createElement("option");
    option.value = `${m.zone},${m.area}`;
    option.textContent = `${m.zone},${m.area}` + (m.name ? `  ${m.name}` : "");
    return option;
  }));
  pick.value = "7,15";
}

// ===== saving, and opening a map he saved =====

/*
  The server writes the file, through map_file.save, which validates it and refuses to overwrite.
  The browser could offer a download instead, and it would land in the Downloads folder having
  passed no gate at all. A map that cannot reach a ROM should fail here, with its reason on the
  status line, and not later in a patch module.
*/
async function fillSavedPicker(names) {
  const list = names || (await (await fetch("/api/saved")).json()).maps;
  $("savedsel").replaceChildren(...list.map((name) => {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name;
    return option;
  }));
  $("openSaved").disabled = list.length === 0;
}

/* One send, so the first try and the replace get the same handling. null means it threw. */
async function postSave(name, under, replace) {
  try {
    return await (await fetch("/api/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, doc: state.doc, retire: under, replace }),
    })).json();
  } catch (problem) {
    // A stopped server must say so here. Silence on a Save is how a morning's work is lost.
    status(`the map was NOT saved: ${problem}. Is serve.py still running?`, "bad");
    return null;
  }
}

async function saveMap() {
  if (!state.doc) return;
  const name = $("savename").value.trim() || state.title;
  const under = state.title;                  // the title the autosaves were written under
  // Stop the clock and let any autosave in flight land first, so the two writes cannot cross.
  // Every exit below that is not a success restarts it with flush().
  await autosave.quiet();
  let answer = await postSave(name, under, false);
  if (answer && answer.taken) {
    /*
      A name he already holds is a QUESTION, because saving one map again is how he works on it.
      The server wrote nothing and retired nothing to reach here, so a No costs him nothing. The
      name in the question is the server's, which is the file on disk: safe_name can change his.
    */
    const go = window.confirm(`A map called "${answer.taken}" is already saved.\n\n`
                              + "Replace it? The copy on disk now moves to "
                              + "map-editor\\maps\\older\\, so it can be put back by hand.");
    if (!go) {
      status(`nothing was saved. "${answer.taken}" is untouched. Type another name to keep this `
             + "map beside it.", "info");
      await autosave.flush();
      return;
    }
    answer = await postSave(name, under, true);
  }
  if (!answer) {
    await autosave.flush();              // quiet() stopped the clock, so restart the net by hand
    return;
  }
  if (answer.error) {
    // A refused save keeps BOTH the dirty flag and the autosave. Nothing is retired until the
    // real file exists, so the net stays under him exactly while he still needs it.
    status(answer.error, "bad");
    await autosave.flush();
    return;
  }
  await fillSavedPicker(answer.maps);
  $("savedsel").value = answer.saved;
  // The document is now this saved map, so later autosaves key to the name it was saved under.
  state.title = answer.saved;
  $("title").textContent = answer.saved;
  markClean();
  autosave.forget();
  const where = `saved as "${answer.saved}", in map-editor\\maps\\${answer.saved}.json`;
  // answer.replaced is the file name the server moved aside, which a second replace timestamps.
  status(answer.replaced
         ? `${where}. The copy it replaced is kept as map-editor\\maps\\older\\${answer.replaced}`
         : where, "good");
}

// ===== unsaved work: the marker, and the offer of an autosave on start =====

/*
  The marker is in the HEADER and not on the status line, because status() is replaced by the next
  thing that happens and the question "is my work safe" must be answerable at any moment. The tab
  title carries it too, so a tab in the background still says so.
*/
function paintMarker() {
  const note = autosave.info();
  const marker = $("dirty");
  if (note.failure) {
    marker.className = "marker lost";
    marker.textContent = `unsaved and NOT kept: ${note.failure}`;
  } else if (!state.dirty) {
    marker.className = "marker";
    marker.textContent = state.doc ? "no unsaved changes" : "";
  } else {
    marker.className = "marker unsaved";
    marker.textContent = note.at ? `unsaved, kept at ${autosave.clockText(note.at)}`
                                 : "unsaved, keeping it ...";
  }
  document.title = state.dirty ? "* LOG Map Editor" : "LOG Map Editor";
}

/*
  An autosave newer than the saved map of the same name is work that exists nowhere else. It is
  OFFERED and never loaded: on the morning after a good Save, loading the newest autosave by
  itself would hand back a half-finished experiment, and the first stroke would write over it.
*/
async function offerRestore() {
  const found = await autosave.candidates();
  if (!found.length) return;
  $("restoresel").replaceChildren(...found.map((row) => {
    const option = document.createElement("option");
    option.value = row.name;
    option.textContent = `${row.title}  (${autosave.clockText(row.at)}`
                         + `${row.saved_at ? ", newer than the saved map" : ", never saved"})`;
    return option;
  }));
  $("restore-text").textContent = found.length === 1
    ? "Unsaved work from a previous session is here:"
    : `${found.length} pieces of unsaved work from previous sessions are here:`;
  $("restore").hidden = false;
  status(`${found.length} piece(s) of unsaved work were kept. Restore one, or leave it and it `
         + "stays in map-editor\\autosave\\.", "bad");
}

async function restoreChosen() {
  const name = $("restoresel").value;
  if (!await leaveOpenMap(`Restore "${name}" instead?`)) return;
  try {
    await autosave.restore(name);
    $("restore").hidden = true;
    status(`restored "${state.title}" from the autosave. It is NOT saved yet: press Save.`, "good");
  } catch (problem) {
    status(`"${name}" was NOT restored: ${problem.message}`, "bad");
  }
}

// ===== start =====

export async function start() {
  canvas = $("map");
  ctx = canvas.getContext("2d");
  overlay = $("overlay");
  octx = overlay.getContext("2d");
  wirePointer();
  onCanvasPointer(tools.pointer);
  tools.install({
    redraw,
    refreshCounts,
    refreshPalette: paintPalette,
    refreshTools: paintTools,
    paintOverlay,
    atlasReady,
    rebuildSheet: () => buildSheet(state.doc, state.assets, atlasFor),
    stampName: () => $("stampname").value.trim(),
  });
  // The truth panel takes the same kind of host as the tools, so neither file imports this one
  // and the three cannot form an import cycle. It reads the camera rule out of map_file.py here.
  await truth.install({ addOverlay, paintOverlay, refreshCounts, canvas });
  // The net under every unsaved change. It hooks the history and the dirty flag, so no edit in
  // any other file has to remember to call it.
  autosave.install({ paintMarker, show });

  await loadAssets();
  $("budget").textContent = state.assets.tile_budget;
  await fillMapPicker();
  await fillSavedPicker();
  await paintPool(0);

  $("chunksel").replaceChildren(...state.assets.chunks.map((c) => {
    const option = document.createElement("option");
    option.value = String(c.index);
    option.textContent = `chunk ${c.index}  (${c.tiles} tiles)`;
    return option;
  }));
  $("chunksel").onchange = () => paintPool(Number($("chunksel").value));

  $("open").onclick = async () => {
    const [zone, area] = $("mapsel").value.split(",");
    if (!await leaveOpenMap(`Open map ${zone},${area} instead?`)) return;
    ask(`/api/map?zone=${zone}&area=${area}&var=1`, `map ${zone},${area}`);
  };
  $("new").onclick = async () => {
    // Clamped, not only limited by the input's max: a typed value ignores max. The collision grid
    // is 256 cells of 8 px, so a map past 8 blocks takes art that right click can never reach.
    const blocks = (id) => Math.min(Math.max(Number($(id).value) || 1, 1), BLOCK_CAP);
    const bw = blocks("bw");
    const bh = blocks("bh");
    if (!await leaveOpenMap(`Start a new ${bw} x ${bh} block map instead?`)) return;
    $("bw").value = bw;
    $("bh").value = bh;
    // A blank map is solid everywhere, so the red wash covers it and everything painted on it is
    // wall until Fill walkable runs. Saying so beats him asking why his field is not walkable.
    ask(`/api/blank?bw=${bw}&bh=${bh}`, `new ${bw} x ${bh} blocks`).then(() => {
      if (state.doc) status("a new map is SOLID everywhere. Press Fill walkable first, "
                            + "then paint the art.", "info");
    });
  };
  $("zoom").oninput = () => setView({ zoom: Number($("zoom").value) });
  $("openSaved").onclick = async () => {
    const name = $("savedsel").value;
    if (!await leaveOpenMap(`Open the saved map "${name}" instead?`)) return;
    ask(`/api/load?name=${encodeURIComponent(name)}`, name);
  };
  $("save").onclick = saveMap;

  for (const button of document.querySelectorAll(".tool")) {
    button.onclick = () => tools.setTool(button.dataset.tool);
  }
  $("size").onchange = () => tools.setBrushSize(Number($("size").value));
  $("erase").onclick = () => tools.pickEraser();
  $("collmode").onchange = () => tools.setCollisionPaint($("collmode").value);
  $("showcoll").onchange = () => tools.setShowCollision($("showcoll").checked);
  $("showanim").onchange = () => tools.setShowAnimated($("showanim").checked);
  $("grablayers").onchange = () => tools.setGrabLayers($("grablayers").value);
  $("grabcoll").onchange = () => tools.setGrabCollision($("grabcoll").value);
  $("restore-go").onclick = restoreChosen;
  $("restore-no").onclick = () => {
    $("restore").hidden = true;
    status("the kept work stays in map-editor\\autosave\\. Composing another map of the same name "
           + "moves it into autosave\\older\\ rather than over it.", "info");
  };
  $("floorall").onclick = () => tools.fillCollision(true);
  $("wallall").onclick = () => tools.fillCollision(false);
  $("undo").onclick = () => tools.undo();
  $("redo").onclick = () => tools.redo();
  paintTools();

  subscribe("view", () => {
    applyZoom();
    redraw();
    paintLayers();
    paintTools();                         // the brush paints onto the selected layer, so it is here
    $("zoomnote").textContent = `${state.view.zoom}x`;
  });
  subscribe("status", () => {
    $("status").textContent = state.status.text;
    $("status").className = state.status.kind;
  });
  subscribe("dirty", paintMarker);
  status("ready. Open a game map, or start a blank one.", "good");
  await offerRestore();                  // last, so its message is the one left on the line
}
