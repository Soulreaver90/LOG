/*
  panes.js - Wire the three panes, and own the two ways a map arrives.

  Layout A, the one the owner chose: tiles left, map centre, layers and properties right.

  Seams for the tasks that follow, so neither has to rewrite this file's shape.
    onCanvasPointer(fn)  Task 5's tools get every pointer event on the map, in CELL coordinates,
                         with the button, so right click can paint collision.
    addRightPanel(node)  Task 6's truth panel, and any later panel, appends itself to the right
                         pane under the properties it already shows.
    addToolbarItem(node) Task 5's tool buttons go in the centre pane's bar.
    redraw()             redraw the visible canvas from the layer canvases.
    refreshCounts()      redraw the right pane after an edit changed the tile list.

  THE TILE COUNT shows LOADED SLOTS, not the static stream. 7,15 streams 633 tiles and loads 635
  slots, because its one animated group owns 894 and 895. "633 / 896" would read as 263 slots
  free, when the stream can only grow to 894. The sub-line breaks the number into its two parts,
  so the owner can see which half is his to spend.
*/
import {
  state, subscribe, setDoc, setView, status,
  drawOrder, loadedSlots, groupTiles, cameraPair,
} from "./state.js";
import { buildSheet, drawAllLayers, composite, layerSize, forget, sheetCanvas } from "./render.js";

const BLOCK_CAP = 8;       // 8 blocks is 2048 px, which is where the 256 cell collision grid stops
const pointerHooks = [];
const atlasCache = new Map();
let canvas = null;
let ctx = null;

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

export function redraw() {
  if (!state.doc) return;
  composite(ctx, state.doc, state.view.shown);
}

// ===== assets =====

async function loadAssets() {
  state.assets = await (await fetch("assets/assets.json")).json();
}

function atlasFor(chunk) {
  if (!atlasCache.has(chunk)) {
    atlasCache.set(chunk, new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error(`chunk ${chunk} has no atlas in assets\\chunks`));
      img.src = `assets/chunks/${chunk}.png`;
    }));
  }
  return atlasCache.get(chunk);
}

// ===== the left pane: the tiles this map loads, and the pool it may draw from =====

function tileButton(label, draw) {
  const cell = document.createElement("canvas");
  cell.width = 8;
  cell.height = 8;
  cell.className = "tile";
  cell.title = label;
  draw(cell.getContext("2d"));
  return cell;
}

function paintPalette() {
  const list = $("palette");
  list.replaceChildren();
  if (!state.doc) return;
  const slots = [...loadedSlots(state.doc, state.assets.tile_budget)].sort((a, b) => a - b);
  const sheet = sheetCanvas();
  for (const slot of slots) {
    list.append(tileButton(`slot ${slot}`, (c) =>
      c.drawImage(sheet, (slot % 32) * 8, Math.floor(slot / 32) * 8, 8, 8, 0, 0, 8, 8)));
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
      c.drawImage(atlas, (tile % 16) * 8, Math.floor(tile / 16) * 8, 8, 8, 0, 0, 8, 8)));
  }
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
  applyZoom();
}

function applyZoom() {
  canvas.style.width = `${canvas.width * state.view.zoom}px`;
  canvas.style.height = `${canvas.height * state.view.zoom}px`;
}

function cellAt(event) {
  const box = canvas.getBoundingClientRect();
  const x = Math.floor((event.clientX - box.left) / state.view.zoom / 8);
  const y = Math.floor((event.clientY - box.top) / state.view.zoom / 8);
  return { cx: x, cy: y, button: event.button, event };
}

function wirePointer() {
  for (const kind of ["pointerdown", "pointermove", "pointerup"]) {
    canvas.addEventListener(kind, (event) => {
      const where = cellAt(event);
      $("where").textContent = `cell ${where.cx}, ${where.cy}   px ${where.cx * 8}, ${where.cy * 8}`;
      for (const fn of pointerHooks) fn(kind, where);
    });
  }
  canvas.addEventListener("contextmenu", (e) => e.preventDefault());   // right click is a tool
}

// ===== opening a map =====

async function show(payload, title) {
  setDoc(payload.doc, payload.problems, title);
  forget();
  await buildSheet(state.doc, state.assets, atlasFor);
  drawAllLayers(state.doc);
  fitCanvas();
  redraw();
  paintLayers();
  paintPalette();
  refreshCounts();
  $("title").textContent = title;
  status(payload.problems.length ? `${title}: ${payload.problems.length} problem(s)` : `${title} open`,
         payload.problems.length ? "bad" : "good");
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

// ===== start =====

export async function start() {
  canvas = $("map");
  ctx = canvas.getContext("2d");
  wirePointer();

  await loadAssets();
  $("budget").textContent = state.assets.tile_budget;
  await fillMapPicker();
  await paintPool(0);

  $("chunksel").replaceChildren(...state.assets.chunks.map((c) => {
    const option = document.createElement("option");
    option.value = String(c.index);
    option.textContent = `chunk ${c.index}  (${c.tiles} tiles)`;
    return option;
  }));
  $("chunksel").onchange = () => paintPool(Number($("chunksel").value));

  $("open").onclick = () => {
    const [zone, area] = $("mapsel").value.split(",");
    ask(`/api/map?zone=${zone}&area=${area}&var=1`, `map ${zone},${area}`);
  };
  $("new").onclick = () => {
    // Clamped, not only limited by the input's max: a typed value ignores max. The collision grid
    // is 256 cells of 8 px, so a map past 8 blocks takes art that right click can never reach.
    const blocks = (id) => Math.min(Math.max(Number($(id).value) || 1, 1), BLOCK_CAP);
    const bw = blocks("bw");
    const bh = blocks("bh");
    $("bw").value = bw;
    $("bh").value = bh;
    ask(`/api/blank?bw=${bw}&bh=${bh}`, `new ${bw} x ${bh} blocks`);
  };
  $("zoom").oninput = () => setView({ zoom: Number($("zoom").value) });

  subscribe("view", () => {
    applyZoom();
    redraw();
    paintLayers();
    $("zoomnote").textContent = `${state.view.zoom}x`;
  });
  subscribe("status", () => {
    $("status").textContent = state.status.text;
    $("status").className = state.status.kind;
  });
  status("ready. Open a game map, or start a blank one.", "good");
}
