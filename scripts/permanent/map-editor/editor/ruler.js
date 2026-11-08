/*
  ruler.js - Stand a character on the map, so a hill has a size.

  WHY IT EXISTS. The 240 x 160 screen box says what fits on screen. It says nothing about how big
  a person is beside a tree or a hill, which is the question being asked while a map is composed.
  A standing character dropped on the ground answers it, and only that.

  THE ANCHOR IS THE ACTOR'S POINT, NEVER THE IMAGE CORNER. A frame is a padded box and the figure
  does not fill it. Imperfect Cell's stand is a 64 x 64 picture whose record carries dx -20,
  dy -56, so dropping it by its corner would stand him 20 px to the right and 8 px low, and every
  comparison would be wrong by that much. The PNG is drawn at (point + dx, point + dy), and the
  point is the cell the owner drops him on. export_assets.py measures dx and dy from the frame
  record itself, so nothing here guesses them.

  WHAT THE NUMBERS MEAN. sprites.json carries three boxes, all in pixels from the actor's point.
    box        the frame record's own box. Where the PNG goes. Mostly transparent padding.
    ink        the pixels this one standing frame really draws. THIS is the figure's size.
    envelope   every record of the whole set, which is the reach of its attacks and its falls.
  Bible B0246 reports set 28 reaching 56 px above the point. That is the ENVELOPE. The stand's ink
  reaches 40. Both are true, and a panel that showed one as the other would mislead, so the panel
  shows the stand's height and names the envelope beside it.

  IT IS NEVER PART OF THE DOCUMENT. It is not saved, not exported, never placed as tiles, and it
  does not mark the map dirty. This file imports `state` and `subscribe` to read the open map and
  nothing else: no `edit`, no `markDirty`, no `setView`, no history. A tool that dirtied his map
  would fire the autosave and put a star on his tab for a thing he only looked at.

  Seams  install(host) takes addOverlay, paintOverlay and the map canvas, the same shape tools.js
         and truth.js take, so this file imports nothing from panes.js.
         truth.js owns the ONE pointer drag on the map stack and asks grabbed() who was pressed,
         because two capture listeners on one element would move the box and the sprite together.
         probe() returns every number the panel shows, for a check driven from the browser.
*/
import { state, subscribe } from "./state.js";
import { layerSize } from "./render.js";

// ===== CONFIG =====

const SPRITES_URL = "assets/sprites/sprites.json";
const POINT_INK = "#7fc08a";                  // the green token: not gold (the screen box), not red
const POINT_SHADOW = "rgba(0, 0, 0, 0.75)";
const POINT_ARM = 5;                          // the cross at the actor's point, in map pixels
const GRAB_PAD = 2;                           // a thin figure is still easy to catch

let host = null;
let manifest = [];                            // the sprites.json entries, in the order exported
let images = new Map();                       // png name -> the loaded <img>
let chosen = null;                            // the entry being shown
let at = { x: 0, y: 0 };                      // the ACTOR'S POINT, in world pixels
let showSprite = false;
let note = "not loaded yet";

const $ = (id) => document.getElementById(id);

// ===== what is shown, and where =====

export function shown() {
  return Boolean(showSprite && chosen && state.doc && images.get(chosen.png));
}

/* The ink box in WORLD pixels: what the owner sees, and what he can grab. */
function inkBox() {
  const [x0, y0, x1, y1] = chosen.ink;
  return { x: at.x + x0, y: at.y + y0, w: x1 - x0, h: y1 - y0 };
}

/* Was this point pressed on the figure? truth.js asks before it moves the screen box. */
export function grabbed(point) {
  if (!shown()) return false;
  const box = inkBox();
  return point.x >= box.x - GRAB_PAD && point.x < box.x + box.w + GRAB_PAD
      && point.y >= box.y - GRAB_PAD && point.y < box.y + box.h + GRAB_PAD;
}

/*
  Clamped to the ART GRID and not to the camera's reach, because standing him on a corner the
  camera cannot show is a fair question to ask of a map that is still growing.
*/
function clamp(x, y) {
  const [gw, gh] = layerSize(state.doc);
  at = { x: Math.max(0, Math.min(Math.round(x), gw - 1)),
         y: Math.max(0, Math.min(Math.round(y), gh - 1)) };
}

/* Move the actor's point. */
export function place(x, y) {
  if (!state.doc) return;
  clamp(x, y);
  paint();
  host.paintOverlay();
}

export function probe() {
  return { shown: shown(), note, at: { ...at },
           set: chosen ? chosen.set : null, name: chosen ? chosen.name : null,
           box: chosen ? [...chosen.box] : null,
           ink: chosen ? [...chosen.ink] : null,
           envelope: chosen ? [...chosen.envelope] : null,
           // Where the PNG's top left corner lands in world pixels, which is what a screenshot
           // check measures against.
           drawAt: chosen ? [at.x + chosen.box[0], at.y + chosen.box[1]] : null,
           inkAt: chosen ? [at.x + chosen.ink[0], at.y + chosen.ink[1],
                            at.x + chosen.ink[2], at.y + chosen.ink[3]] : null };
}

// ===== drawing =====

export function drawOverlay(octx) {
  if (!shown()) return;
  // A canvas resize resets this, and panes.fitCanvas resizes the overlay on every map it opens.
  octx.imageSmoothingEnabled = false;
  const [dx, dy] = chosen.box;
  octx.drawImage(images.get(chosen.png), at.x + dx, at.y + dy);
  drawPoint(octx);
}

/* The point itself, so he can see WHERE the figure is standing and not guess from its feet. */
function drawPoint(octx) {
  octx.save();
  for (const [ink, width] of [[POINT_SHADOW, 3], [POINT_INK, 1]]) {
    octx.strokeStyle = ink;
    octx.lineWidth = width;
    octx.beginPath();
    octx.moveTo(at.x - POINT_ARM + 0.5, at.y + 0.5);
    octx.lineTo(at.x + POINT_ARM + 0.5, at.y + 0.5);
    octx.moveTo(at.x + 0.5, at.y - POINT_ARM + 0.5);
    octx.lineTo(at.x + 0.5, at.y + POINT_ARM + 0.5);
    octx.stroke();
  }
  octx.restore();
}

// ===== the panel =====

function paint() {
  const ready = manifest.length > 0;
  $("ruler-show").disabled = !ready;
  $("ruler-set").disabled = !ready || !showSprite;
  $("ruler-show").checked = showSprite;
  $("ruler-note").className = ready ? "hint" : "bad";
  if (!ready || !chosen) {
    $("ruler-note").textContent = note;
    return;
  }
  const [, y0, , y1] = chosen.ink;
  const tall = y1 - y0;
  const wide = chosen.ink[2] - chosen.ink[0];
  const up = -chosen.envelope[1];
  $("ruler-note").textContent =
    `${chosen.name} stands ${tall} px tall and ${wide} px wide, which is `
    + `${(tall / 8).toFixed(1)} tiles by ${(wide / 8).toFixed(1)}. His head is ${-y0} px above `
    + `the cross, his feet ${y1} px below it. Over every frame of this set he reaches ${up} px `
    + `up, so an attack or a fall needs more room than this stand shows.`;
}

function chooseSet(id) {
  chosen = manifest.find((s) => String(s.set) === String(id)) || manifest[0];
  paint();
  host.paintOverlay();
}

function wirePanel() {
  $("ruler-show").onchange = () => {
    showSprite = $("ruler-show").checked;
    // The middle of the first screenful is where a map is composed from. At 0, 0 his head would
    // be off the top of the canvas on every map, because the point is at his feet.
    if (showSprite && state.doc && !at.x && !at.y) clamp(120, 120);
    paint();
    host.paintOverlay();
  };
  $("ruler-set").onchange = () => chooseSet($("ruler-set").value);
}

// ===== start =====

/*
  The sprites are loaded ONCE, beside the atlases, and a missing export is not a failure: the
  owner's assets folder was written before this existed, and his running server will not export
  them until he restarts it. So the toggle goes dead with a line that says exactly that, rather
  than the page failing to start.
*/
async function loadSprites() {
  const answer = await fetch(SPRITES_URL);
  if (!answer.ok) throw new Error(`${SPRITES_URL} answered ${answer.status}`);
  const body = await answer.json();
  manifest = body.sprites || [];
  if (!manifest.length) throw new Error(`${SPRITES_URL} lists no sprites`);
  await Promise.all(manifest.map((sprite) => new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => { images.set(sprite.png, img); resolve(); };
    img.onerror = () => reject(new Error(`assets\\sprites\\${sprite.png} is not there`));
    img.src = `assets/sprites/${sprite.png}`;
  })));
}

export async function install(given) {
  host = given;
  wirePanel();
  host.addOverlay(drawOverlay);
  // READ ONLY, exactly like the truth panel's own subscriber. Painting the overlay from inside
  // setDoc would run against the canvas of the map being replaced, which is still the old size.
  // panes.show() repaints it once the new map's canvases are up.
  subscribe("doc", () => {
    if (state.doc) clamp(at.x || 120, at.y || 120);
    paint();
  });
  try {
    await loadSprites();
    $("ruler-set").replaceChildren(...manifest.map((sprite) => {
      const option = document.createElement("option");
      option.value = String(sprite.set);
      option.textContent = `${sprite.name}  (set ${sprite.set})`;
      return option;
    }));
    chosen = manifest[0];
    note = "";
  } catch (problem) {
    manifest = [];
    note = `no sprite to stand on the map: ${problem.message}. Stop serve.py, delete `
         + "map-editor\\assets\\sprites\\, and start it again: it exports them on the way up.";
  }
  paint();
}
