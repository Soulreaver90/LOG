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

  Seams   install(host) takes addOverlay, paintOverlay, refreshCounts and the map canvas, the same
          shape tools.js takes, so this file imports nothing from panes.js and the two cannot cycle.
          probe() returns every number the panel shows, for a check driven from the browser.
*/
import { state, subscribe, edit, status, cameraPair, VIEW_W, VIEW_H } from "./state.js";
import { layerSize } from "./render.js";

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

export function probe() {
  if (!state.doc) return { pinned, pinNote, open: false };
  const [gw, gh] = layerSize(state.doc);
  const seen = reach(state.doc);
  return { pinned, pinNote, open: true, world: [...state.doc.world], grid: [gw, gh],
           pair: seen.pair, reach: [seen.w, seen.h], maxScroll: seen.scroll,
           bands: bands(state.doc), box: { ...box }, showShade, showBox };
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

  const lost = bands(doc).reduce((total, band) => total + band.w * band.h, 0);
  $("truth-lost").textContent = lost
    ? `${lost.toLocaleString()} px of art the camera can never show. `
      + `Shaded on the map, right of ${seen.w} px and below ${seen.h} px.`
    : "The camera reaches every pixel of this map.";
  $("truth-lost").className = lost ? "bad" : "good";
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
  edit((d) => { d.world = [w, h]; });
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
