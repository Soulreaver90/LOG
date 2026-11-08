/*
  truth.js - What the camera can actually reach, shown while he composes.

  WHY IT EXISTS. The plateau rim was drawn correctly and the owner could never see it. That map
  stored a camera limit of 449 on a 1024 px wide world, so the rightmost pixel the camera ever
  showed was 687. He walked to x = 857 and hit an invisible wall in front of correct scenery.
  Every full-map render looked perfect, and several were shown to him. Only play found the fault.

  Shows   a 240 x 160 screen box, one real screenful, dragged over the map
          a wash over every part of the art grid the camera can never reach
          the +0x08 and +0x0A words this map will carry, and the world they come from

  THE RULE IS PYTHON'S, AND IT IS READ FROM PYTHON AT RUN TIME. The pair is
  +0x08 = world_w - 239 and +0x0A = world_h - 159. Writing 239 and 159 here as well as in
  map_file.py is how two languages drift apart, so this module fetches map_file.py, parses
  VIEW_W, VIEW_H and the body of camera_pair, and recomputes the pair from PYTHON'S OWN numbers.
  It then compares that against state.cameraPair on five worlds. A disagreement, a parse failure
  or a failed fetch turns the shading OFF and says so in red. A truth panel that is not pinned to
  the rule it claims to show is worse than no panel, because the plateau looked right too.

  THE WORLD IS NOT THE BLOCK GRID. Over all 336 vanilla layouts the grid merely covers the world
  on 334 of them: map 7,15 is a 1280 px grid holding a 952 px world. So the wash is measured from
  doc.world, never from the grid, or a first map would be told that 328 px of real ground is
  unreachable.

  THE WASH IS A REGION AND THE COUNT IS ART. The wash marks where the camera can never go, which
  is a fact about the canvas. The number beside it used to be that region's AREA, and it read as
  "art you will never see": on map 7,15 it claimed 328 px of lost art on a map that loses none.
  Since the canvas became world pixels, every layer is drawn at minus its own offset, so a count
  of lost art has to be a count of CELLS THAT DRAW SOMETHING outside the reach, measured per layer
  in world cells. lostArt does that and nothing else. Map 7,15 and map 3,11 now report none.

  Seams   install(host) takes addOverlay, paintOverlay, refreshCounts and the map canvas, the same
          shape tools.js takes, so this file imports nothing from panes.js and the two cannot cycle.
          probe() returns every number the panel shows, for a check driven from the browser.
*/
import {
  state, subscribe, edit, status, cameraPair, VIEW_W, VIEW_H, layerShift, TILE_INDEX, SCROLL_ONE,
} from "./state.js";
import { layerSize, slotIsBlank } from "./render.js";

// ===== CONFIG =====

const PIN_WORLDS = [[1024, 1024], [1280, 1280], [688, 1280], [952, 768], [240, 160]];
const WASH = "rgba(9, 9, 14, 0.66)";          // dark, never red: red is the collision wash
const HATCH = "rgba(106, 169, 224, 0.34)";    // the blue token, so the two washes never read alike
const HATCH_STEP = 12;
const EDGE = "#6aa9e0";                       // the line the camera stops at
const BOX_INK = "#f0a860";                    // the gold token, the screen box
const BOX_SHADOW = "rgba(0, 0, 0, 0.75)";

let host = null;
let pinned = false;                           // no shading until Python's own rule agrees
let pinNote = "not checked yet";
let box = { x: 0, y: 0 };
let drag = null;
let showShade = true;
let showBox = true;
let moveMode = false;

const $ = (id) => document.getElementById(id);

// ===== the pin: Python's rule, read from Python =====

async function readPythonRule() {
  const url = new URL("../map_file.py", import.meta.url);
  const answer = await fetch(url);
  if (!answer.ok) throw new Error(`${url.pathname} answered ${answer.status}`);
  const text = await answer.text();
  const screen = text.match(/^VIEW_W,\s*VIEW_H\s*=\s*(\d+),\s*(\d+)/m);
  const rule = text.match(new RegExp([
    /def\s+camera_pair[\s\S]{0,900}?\n\s*return\s+/.source,
    /width_px\s*-\s*\(\s*VIEW_W\s*-\s*(\d+)\s*\)\s*,\s*/.source,
    /height_px\s*-\s*\(\s*VIEW_H\s*-\s*(\d+)\s*\)/.source,
  ].join("")));
  if (!screen || !rule) {
    throw new Error("map_file.py no longer reads 'VIEW_W, VIEW_H = 240, 160' and "
                    + "'return width_px - (VIEW_W - 1), height_px - (VIEW_H - 1)'");
  }
  return { w: Number(screen[1]), h: Number(screen[2]),
           dw: Number(rule[1]), dh: Number(rule[2]) };
}

/* Recompute the pair from Python's numbers, and make the browser's own rule match it exactly. */
function checkAgainst(py) {
  if (py.w !== VIEW_W || py.h !== VIEW_H) {
    throw new Error(`map_file.py says the screen is ${py.w} x ${py.h} px and state.js says `
                    + `${VIEW_W} x ${VIEW_H}`);
  }
  for (const [w, h] of PIN_WORLDS) {
    const want = [w - (py.w - py.dw), h - (py.h - py.dh)];
    const got = cameraPair(w, h);
    if (got[0] !== want[0] || got[1] !== want[1]) {
      throw new Error(`a ${w} x ${h} px world: map_file.py gives ${want}, state.js gives ${got}`);
    }
  }
  return `pinned to map_file.py: screen ${py.w} x ${py.h}, less ${py.dw}`;
}

// ===== the geometry, read back through the pair the ROM will carry =====

/*
  The hardware clamps the scroll to +0x08 - 1 and then draws 239 more pixels, so the last column
  the camera ever shows is pair + 238. Reading the reach back OUT of the pair, rather than from
  the world it came from, means the panel shows what the two bytes in the file will do.
*/
export function reach(doc) {
  const pair = cameraPair(doc.world[0], doc.world[1]);
  return { pair,
           w: pair[0] + VIEW_W - 1,
           h: pair[1] + VIEW_H - 1,
           scroll: [Math.max(0, pair[0] - 1), Math.max(0, pair[1] - 1)] };
}

/* The art grid minus the reach, as rectangles in map pixels. Empty when the camera covers it all. */
export function bands(doc) {
  const [gw, gh] = layerSize(doc);
  const seen = reach(doc);
  const out = [];
  if (seen.w < gw) out.push({ x: seen.w, y: 0, w: gw - seen.w, h: gh });
  if (seen.h < gh) out.push({ x: 0, y: seen.h, w: Math.min(seen.w, gw), h: gh - seen.h });
  return out;
}

/*
  The cells of real art no camera position can ever show, per layer. A cell is art when its slot
  draws a pixel (render.slotIsBlank, the same test the grab tool uses), never when it is nonzero:
  on a copy of a game map slot 0 is real art.

  THE SPAN COMES FROM THE HANDLER, SO IT COVERS PARALLAX TOO. A layer's source pixel at screen 0 is
  `(scroll x camera + offset) >> 10`, and the camera runs 0 to reach.scroll. So the grid pixels this
  layer can ever show are `[shift, (scroll x maxScroll >> 10) + shift + 239]` across, and the same
  down with 159. At scroll 1.0 that is exactly `[shift, shift + reach - 1]`, so one rule serves
  both and a parallax layer is not counted against a span it never had.
*/
function visibleSpan(doc, name) {
  const seen = reach(doc);
  const [sx, sy] = layerShift(doc, name);
  const scroll = doc.layers[name].scroll || [SCROLL_ONE, SCROLL_ONE];
  return [sx, Math.floor(scroll[0] * seen.scroll[0] / SCROLL_ONE) + sx + VIEW_W - 1,
          sy, Math.floor(scroll[1] * seen.scroll[1] / SCROLL_ONE) + sy + VIEW_H - 1];
}

export function lostArt(doc) {
  const across = doc.blocks[0] * 32;
  const down = doc.blocks[1] * 32;
  const out = [];
  for (const name of Object.keys(doc.layers)) {
    const [x0, x1, y0, y1] = visibleSpan(doc, name);
    const cells = doc.layers[name].cells;
    let count = 0;
    for (let gy = 0; gy < down; gy += 1) {
      // A cell spans 8 px, so a cell the camera shows any part of is not lost.
      const inY = gy * 8 + 7 >= y0 && gy * 8 <= y1;
      for (let gx = 0; gx < across; gx += 1) {
        if (inY && gx * 8 + 7 >= x0 && gx * 8 <= x1) continue;
        if (slotIsBlank(cells[gy * across + gx] & TILE_INDEX)) continue;
        count += 1;
      }
    }
    if (count) out.push([name, count]);
  }
  return out;
}

/*
  lostArt walks every cell of every layer, which is 102,400 of them on the 1280 x 1280 plateau, and
  paint() runs on every pointermove of the screen box drag. The answer only changes when the
  document does, and the doc subscriber clears this.
*/
let lostCache = null;

export function lostArtCached(doc) {
  if (!lostCache) lostCache = lostArt(doc);
  return lostCache;
}

export function forgetLostArt() {
  lostCache = null;
}

export function probe() {
  if (!state.doc) return { pinned, pinNote, open: false };
  const [gw, gh] = layerSize(state.doc);
  const seen = reach(state.doc);
  return { pinned, pinNote, open: true, world: [...state.doc.world], grid: [gw, gh],
           pair: seen.pair, reach: [seen.w, seen.h], maxScroll: seen.scroll,
           bands: bands(state.doc), lostArt: lostArtCached(state.doc),
           box: { ...box }, showShade, showBox };
}

// ===== drawing on the overlay =====

export function drawOverlay(octx, doc) {
  if (!doc || !pinned) return;
  if (showShade) drawBands(octx, doc);
  if (showBox) drawBox(octx);
}

function drawBands(octx, doc) {
  const found = bands(doc);
  if (!found.length) return;
  for (const band of found) {
    octx.fillStyle = WASH;
    octx.fillRect(band.x, band.y, band.w, band.h);
    octx.save();
    octx.beginPath();
    octx.rect(band.x, band.y, band.w, band.h);
    octx.clip();
    octx.strokeStyle = HATCH;
    octx.lineWidth = 1;
    octx.beginPath();
    for (let at = band.x - band.h; at < band.x + band.w; at += HATCH_STEP) {
      octx.moveTo(at, band.y);
      octx.lineTo(at + band.h, band.y + band.h);
    }
    octx.stroke();
    octx.restore();
  }
  const seen = reach(doc);
  const [gw, gh] = layerSize(doc);
  octx.strokeStyle = EDGE;
  octx.lineWidth = 1;
  octx.beginPath();
  if (seen.w < gw) { octx.moveTo(seen.w + 0.5, 0); octx.lineTo(seen.w + 0.5, gh); }
  if (seen.h < gh) { octx.moveTo(0, seen.h + 0.5); octx.lineTo(gw, seen.h + 0.5); }
  octx.stroke();
}

/* One real screenful. The corner ticks survive art of any colour, which a plain outline does not. */
function drawBox(octx) {
  const { x, y } = box;
  octx.save();
  octx.lineWidth = 1;
  octx.strokeStyle = BOX_SHADOW;
  octx.strokeRect(x - 0.5, y - 0.5, VIEW_W + 1, VIEW_H + 1);
  octx.strokeStyle = BOX_INK;
  octx.strokeRect(x + 0.5, y + 0.5, VIEW_W - 1, VIEW_H - 1);
  octx.lineWidth = 3;
  const tick = 14;
  for (const [cx, dx] of [[x, 1], [x + VIEW_W, -1]]) {
    for (const [cy, dy] of [[y, 1], [y + VIEW_H, -1]]) {
      octx.beginPath();
      octx.moveTo(cx + dx * tick, cy + dy * 1.5);
      octx.lineTo(cx + dx * 1.5, cy + dy * 1.5);
      octx.lineTo(cx + dx * 1.5, cy + dy * tick);
      octx.stroke();
    }
  }
  octx.font = "10px ui-monospace, Consolas, monospace";
  octx.textBaseline = "bottom";
  const label = `screen 240 x 160 at ${x}, ${y}`;
  octx.lineWidth = 3;
  octx.strokeStyle = BOX_SHADOW;
  octx.strokeText(label, x + 3, y - 3);
  octx.fillStyle = BOX_INK;
  octx.fillText(label, x + 3, y - 3);
  octx.restore();
}

// ===== dragging the box =====

/*
  The tools own every pointer event on the map canvas, and at the target a capture listener does
  NOT run first: listeners on the target itself run in the order they were added. So this listens
  on the canvas's PARENT in the capture phase, which does run first, and stops the event there.
  The middle button always moves the box, because tools.js ignores any button but 0 and 2.
*/
function wireDrag(canvas) {
  const stack = canvas.parentElement;
  const mapPoint = (event) => {
    const area = canvas.getBoundingClientRect();
    const scale = canvas.clientWidth / canvas.width;
    return { x: (event.clientX - area.left - canvas.clientLeft) / scale,
             y: (event.clientY - area.top - canvas.clientTop) / scale };
  };

  const mine = (event) => showBox && pinned && state.doc
    && (event.button === 1 || (moveMode && event.button === 0));

  stack.addEventListener("mousedown", (event) => {
    if (event.button === 1) event.preventDefault();      // or Windows Chrome starts autoscroll
  }, true);

  stack.addEventListener("pointerdown", (event) => {
    if (!mine(event)) return;
    event.stopPropagation();
    event.preventDefault();
    // Capture, so a release over the right pane or a scrollbar still comes back here. A synthetic
    // event carries no live pointer id, and refusing to capture one must not stop the drag.
    try { canvas.setPointerCapture(event.pointerId); } catch (ignored) { void ignored; }
    const at = mapPoint(event);
    const inside = at.x >= box.x && at.x < box.x + VIEW_W && at.y >= box.y && at.y < box.y + VIEW_H;
    drag = inside ? { dx: at.x - box.x, dy: at.y - box.y } : { dx: VIEW_W / 2, dy: VIEW_H / 2 };
    place(at.x - drag.dx, at.y - drag.dy);
  }, true);

  stack.addEventListener("pointermove", (event) => {
    if (!drag) return;
    // No button down means the release happened somewhere this listener never saw. End the drag
    // and let the event through: a drag left open follows a bare hand AND eats the tools' next
    // stroke, because the lines below would stop their pointerup.
    if (event.buttons === 0) { drag = null; return; }
    event.stopPropagation();
    const at = mapPoint(event);
    place(at.x - drag.dx, at.y - drag.dy);
  }, true);

  for (const kind of ["pointerup", "pointercancel"]) {
    stack.addEventListener(kind, (event) => {
      if (!drag) return;
      event.stopPropagation();
      drag = null;
    }, true);
    // The last resort, outside the map entirely, where nothing is left to stop.
    window.addEventListener(kind, () => { drag = null; });
  }
}

/* The box can only sit where the camera can sit: the scroll stops at +0x08 - 1. */
function clamp(x, y) {
  const seen = reach(state.doc);
  box = { x: Math.max(0, Math.min(Math.round(x), seen.scroll[0])),
          y: Math.max(0, Math.min(Math.round(y), seen.scroll[1])) };
}

/* The panel counts art, so it cannot be right until the slot sheet exists. panes.show() calls
   this once the sheet and the layer canvases are up, which is after the doc subscriber has run. */
export function refresh() {
  forgetLostArt();
  paint();
}

export function place(x, y) {
  if (!state.doc) return;
  clamp(x, y);
  paint();
  host.paintOverlay();
}

// ===== the panel =====

function paint() {
  $("truth-pin").textContent = pinned ? "pinned" : "NOT PINNED";
  $("truth-pin").className = pinned ? "" : "bad";
  $("truth-note").textContent = pinNote;
  $("truth-note").className = pinned ? "hint" : "bad";
  $("truth-shade").checked = showShade;
  $("truth-box").checked = showBox;
  $("truth-move").checked = moveMode;
  for (const id of ["truth-shade", "truth-box", "truth-move"]) $(id).disabled = !pinned;

  const doc = state.doc;
  $("truth-w").disabled = !doc || !pinned;
  $("truth-h").disabled = !doc || !pinned;
  // An unpinned panel shows nothing but its reason. Its numbers come from the very rule that
  // just failed its check, and "shaded on the map" beside a map with no shading is a lie.
  if (!doc || !pinned) {
    $("truth-facts").replaceChildren();
    $("truth-lost").textContent = "";
    return;
  }
  const [gw, gh] = layerSize(doc);
  const seen = reach(doc);
  $("truth-w").value = doc.world[0];
  $("truth-h").value = doc.world[1];
  $("truth-w").max = gw;
  $("truth-h").max = gh;

  const rows = [
    ["camera", `+0x08 ${seen.pair[0]}   +0x0A ${seen.pair[1]}`],
    ["reaches", `x 0 to ${seen.w - 1}, y 0 to ${seen.h - 1} px`],
    ["art grid", `${gw} x ${gh} px`],
    ["screen at", `${box.x}, ${box.y} px`],
  ];
  $("truth-facts").replaceChildren(...rows.flatMap(([key, value]) => {
    const dt = document.createElement("dt");
    dt.textContent = key;
    const dd = document.createElement("dd");
    dd.textContent = value;
    return [dt, dd];
  }));

  const lost = lostArtCached(doc);
  const total = lost.reduce((sum, [, count]) => sum + count, 0);
  const shaded = bands(doc).length
    ? ` The shading marks where the camera cannot go, right of ${seen.w} px and below ${seen.h} px.`
    : "";
  // A PARALLAX layer is named as one. Its grid is deliberately wider than the ground it covers,
  // so a large count there is the backdrop's own design and not a fault in the map.
  const mark = (name) => {
    const scroll = doc.layers[name].scroll || [SCROLL_ONE, SCROLL_ONE];
    return scroll[0] === SCROLL_ONE && scroll[1] === SCROLL_ONE
      ? "" : `, parallax at ${(scroll[0] / SCROLL_ONE).toFixed(2)}`;
  };
  $("truth-lost").textContent = total
    ? `${total.toLocaleString()} cell(s) of art the camera can never show `
      + `(${lost.map(([name, count]) => `${name} ${count}${mark(name)}`).join(", ")}).${shaded}`
    : `The camera reaches every cell of art on this map.${shaded}`;
  $("truth-lost").className = total ? "bad" : "good";
}

function setWorld() {
  const doc = state.doc;
  if (!doc) return;
  const [gw, gh] = layerSize(doc);
  // Clamped both ways, so the one control that decides the camera cannot write a world the grid
  // fails to cover or one smaller than the screen. Both are refused by validate on the way out.
  const want = (id, cap, floor) =>
    Math.max(floor, Math.min(Math.round(Number($(id).value) || floor), cap));
  const w = want("truth-w", gw, VIEW_W);
  const h = want("truth-h", gh, VIEW_H);
  edit((d) => { d.world = [w, h]; });        // edit() notifies, which forgets the lost-art count
  place(box.x, box.y);                 // the reach may have shrunk under the box
  host.refreshCounts();                // the right pane's own camera row is not a doc subscriber
  const pair = cameraPair(w, h);
  status(`world ${w} x ${h} px, so the map carries +0x08 ${pair[0]} and +0x0A ${pair[1]}`, "info");
}

function wirePanel() {
  $("truth-shade").onchange = () => { showShade = $("truth-shade").checked; host.paintOverlay(); };
  $("truth-box").onchange = () => { showBox = $("truth-box").checked; host.paintOverlay(); };
  $("truth-move").onchange = () => { moveMode = $("truth-move").checked; };
  $("truth-w").onchange = setWorld;
  $("truth-h").onchange = setWorld;
}

// ===== start =====

export async function install(given) {
  host = given;
  wirePanel();
  wireDrag(host.canvas);
  host.addOverlay(drawOverlay);
  // The panel only reads here. panes.show() repaints the overlay itself once the new map's
  // canvases are sized, and painting it from inside setDoc would run against the old one.
  subscribe("doc", () => {
    forgetLostArt();
    if (state.doc) clamp(box.x, box.y);
    paint();
  });
  try {
    pinNote = checkAgainst(await readPythonRule());
    pinned = true;
  } catch (problem) {
    pinned = false;
    pinNote = `the camera rule here disagrees with map_file.py, so nothing is shaded: ${problem.message}`;
  }
  paint();
}
