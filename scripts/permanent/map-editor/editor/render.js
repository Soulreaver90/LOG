/*
  render.js - Turn a map document into pixels, the way the GBA does.

  Two steps, because they change at different rates.
    buildSheet(doc)   the SLOT SHEET: every VRAM slot the map loads, drawn once as 8x8 cells, in
                      four flip variants. It changes only when the map's tile list changes.
    drawLayer(doc, n) one BG layer's own canvas, as big as the block grid. It changes when a cell
                      changes, so Task 5 redraws a region of it rather than the whole map.
    composite(ctx)    the layers the owner has shown, back to front, onto the visible canvas.

  THE SLOT RULE, which is why this file has a header. A map's tiles are the static +0x48 stream
  PLUS each animated group at its own slot. The stream fills slots 0 upward; a group fills
  [first, first + tiles) and usually sits past the stream. Map 7,15 streams 633 tiles and its cells
  name slot 894, which its one group loads. A renderer that built its tile list from the stream
  alone drew nothing in every cell naming a group slot and showed the layer below: 509 false cells
  on the plateau, measured 2026-11-07. This mirrors scene_probe.loaded_tiles, including its order:
  the groups are laid AFTER the stream, so a group that overlaps the stream wins, as it does in
  play. Map 6,99 is the one vanilla layout that overlaps.

  TRANSPARENCY. A static tile's pixels arrive as a PNG the browser decodes, and the exporter marks
  colour index 0 with tRNS, so index 0 arrives with alpha 0 and needs no handling here. A group's
  pixels arrive as raw 8bpp indices in the document, so this file applies the same rule by hand
  through assets.transparent_index. Both must agree, or the group tiles draw a black box.

  FLIPS. A cell's 0x400 and 0x800 bits flip the tile. The sheet is drawn four times, once per flip
  pair, so a cell is one drawImage with no canvas transform. A 160 x 128 map is 20,480 cells a
  layer, and a save, transform and restore on each is what makes a redraw visible to the eye.
*/
import { BLOCK_PIXELS, TILE_INDEX, FLIP_X, FLIP_Y, drawOrder, groupTiles, layerShift }
  from "./state.js";

const TILE = 8;
const SHEET_COLUMNS = 32;

let sheet = null;          // the four flip variants, side by side: x = flips * sheetWidth
let sheetSlots = 0;
let sheetHeight = 0;       // one variant's height, which the vertical flip mirrors around
const layerCanvas = {};    // name -> canvas, one per BG layer of the open document

export function sheetCanvas() {
  return sheet;
}

// ===== the slot sheet =====

function blank(width, height) {
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  canvas.getContext("2d").imageSmoothingEnabled = false;
  return canvas;
}

function slotBox(slot) {
  return [(slot % SHEET_COLUMNS) * TILE, Math.floor(slot / SHEET_COLUMNS) * TILE];
}

/* One animated group tile, as ImageData, through the one shared 256 colour BG palette. */
function groupTileImage(ctx, pixels, start, palette, transparent) {
  const image = ctx.createImageData(TILE, TILE);
  for (let n = 0; n < TILE * TILE; n += 1) {
    const index = pixels[start + n];
    const [r, g, b] = palette[index];
    image.data[n * 4] = r;
    image.data[n * 4 + 1] = g;
    image.data[n * 4 + 2] = b;
    image.data[n * 4 + 3] = index === transparent ? 0 : 255;
  }
  return image;
}

/*
  Draw every slot the map loads, then mirror the result into the three flipped variants.
  `atlases` maps a chunk index to its loaded <img>. A chunk the document names but the manifest
  has not got is left empty rather than guessed, so a missing atlas shows as a hole and not as
  the wrong art.
*/
export async function buildSheet(doc, assets, atlasFor) {
  const budget = assets.tile_budget;
  const palette = assets.palettes[0];
  const transparent = assets.transparent_index;
  const rows = Math.ceil(budget / SHEET_COLUMNS);
  const width = SHEET_COLUMNS * TILE;
  const height = rows * TILE;

  const one = blank(width, height);
  const ctx = one.getContext("2d");

  const needed = new Set((doc.tiles || []).map(([chunk]) => chunk));
  const atlases = new Map();
  for (const chunk of needed) atlases.set(chunk, await atlasFor(chunk));

  (doc.tiles || []).slice(0, budget).forEach(([chunk, tile], slot) => {
    const atlas = atlases.get(chunk);
    if (!atlas) return;
    const [dx, dy] = slotBox(slot);
    ctx.drawImage(atlas, (tile % 16) * TILE, Math.floor(tile / 16) * TILE, TILE, TILE,
                  dx, dy, TILE, TILE);
  });

  for (const group of doc.animated || []) {
    const frame = (group.frames || [])[0];
    if (!frame) continue;
    for (let n = 0; n < groupTiles(group); n += 1) {
      const slot = group.first + n;
      if (slot >= budget) break;
      const [dx, dy] = slotBox(slot);
      // putImageData REPLACES, so a group that overlaps the stream wins here as it does in play
      ctx.putImageData(groupTileImage(ctx, frame.pixels, n * TILE * TILE, palette, transparent),
                       dx, dy);
    }
  }

  sheet = blank(width * 4, height);
  const out = sheet.getContext("2d");
  for (let flips = 0; flips < 4; flips += 1) {
    out.save();
    out.translate(flips * width, 0);
    if (flips & 1) { out.translate(width, 0); out.scale(-1, 1); }
    if (flips & 2) { out.translate(0, height); out.scale(1, -1); }
    out.drawImage(one, 0, 0);
    out.restore();
  }
  sheetSlots = budget;
  sheetHeight = height;
  blankSlot.clear();                 // the answers belong to the sheet that has just been replaced
  return sheet;
}

/*
  Does this slot draw nothing at all? Read from the slot sheet, so it is the real pixels, never
  `cell === 0`: on a copy of a game map slot 0 is real art. The cache is cleared by buildSheet, so
  it can never answer for a sheet that has been replaced. The copy into a one tile canvas is not
  waste: the sheet's own context was made for drawing, and asking an existing context for
  willReadFrequently does nothing but log a warning.
*/
const peek = document.createElement("canvas");
peek.width = TILE;
peek.height = TILE;
const peekCtx = peek.getContext("2d", { willReadFrequently: true });
const blankSlot = new Map();

export function slotIsBlank(slot) {
  if (!sheet) return true;              // no sheet yet: nothing is drawn, so nothing is art
  if (blankSlot.has(slot)) return blankSlot.get(slot);
  peekCtx.clearRect(0, 0, TILE, TILE);
  peekCtx.drawImage(sheet, (slot % SHEET_COLUMNS) * TILE, Math.floor(slot / SHEET_COLUMNS) * TILE,
                    TILE, TILE, 0, 0, TILE, TILE);
  const pixels = peekCtx.getImageData(0, 0, TILE, TILE).data;
  let blank = true;
  for (let n = 3; n < pixels.length; n += 4) {
    if (pixels[n] !== 0) { blank = false; break; }
  }
  blankSlot.set(slot, blank);
  return blank;
}

/* Where one cell's art sits in the sheet, flips included. */
function cellSource(cell, sheetWidth) {
  const slot = cell & TILE_INDEX;
  if (slot >= sheetSlots) return null;
  const flips = (cell & FLIP_X ? 1 : 0) | (cell & FLIP_Y ? 2 : 0);
  let [x, y] = slotBox(slot);
  if (flips & 1) x = sheetWidth - x - TILE;
  if (flips & 2) y = sheetHeight - y - TILE;
  return [flips * sheetWidth + x, y];
}

// ===== the layers =====

export function layerSize(doc) {
  return [doc.blocks[0] * BLOCK_PIXELS, doc.blocks[1] * BLOCK_PIXELS];
}

/*
  Redraw a rectangle of one layer, in CELLS. Task 5 calls it with the cells a brush touched.
  With no box it redraws the whole layer, which is what opening a map does.
*/
export function drawLayer(doc, name, box) {
  const [width, height] = layerSize(doc);
  if (!layerCanvas[name] || layerCanvas[name].width !== width || layerCanvas[name].height !== height) {
    layerCanvas[name] = blank(width, height);
  }
  const ctx = layerCanvas[name].getContext("2d");
  const across = doc.blocks[0] * 32;
  const down = doc.blocks[1] * 32;
  const [x0, y0, x1, y1] = box || [0, 0, across, down];
  const sheetWidth = sheet.width / 4;
  const cells = doc.layers[name].cells;

  ctx.clearRect(x0 * TILE, y0 * TILE, (x1 - x0) * TILE, (y1 - y0) * TILE);
  for (let cy = y0; cy < y1; cy += 1) {
    for (let cx = x0; cx < x1; cx += 1) {
      const source = cellSource(cells[cy * across + cx], sheetWidth);
      if (!source) continue;
      ctx.drawImage(sheet, source[0], source[1], TILE, TILE, cx * TILE, cy * TILE, TILE, TILE);
    }
  }
  return layerCanvas[name];
}

export function drawAllLayers(doc) {
  for (const name of Object.keys(doc.layers)) drawLayer(doc, name, null);
}

/*
  Paint the shown layers onto a target context, back to front, IN WORLD PIXELS. The background is
  opaque black, which is what map_view.compose starts from, so a hole reads as a hole and not as
  the page.

  THE OFFSET. A layer canvas is its own grid. The game adds the record's +0x0C and +0x10 to the
  camera before it writes the scroll registers, so a layer is seen at minus its own shift
  (state.layerShift). 364 of the 1294 vanilla tilemap layers carry one, usually 64 n px for layer
  n. Without this the editor drew BG1 64 px, BG2 128 px and BG3 192 px down and right of the game,
  and of its own collision wash, which is world. map_view.compose does the same thing in Python.
*/
export function composite(ctx, doc, shown) {
  const [width, height] = layerSize(doc);
  ctx.imageSmoothingEnabled = false;
  ctx.fillStyle = "#000";
  ctx.fillRect(0, 0, width, height);
  for (const name of drawOrder(doc)) {
    if (!shown[name] || !layerCanvas[name]) continue;
    const [sx, sy] = layerShift(doc, name);
    ctx.drawImage(layerCanvas[name], -sx, -sy);
  }
}

export function forget() {
  for (const name of Object.keys(layerCanvas)) delete layerCanvas[name];
}
