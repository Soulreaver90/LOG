/*
  history.js - One stroke, one step back.

  A STROKE is everything between pointerdown and pointerup: one fill, one drag of the tile brush,
  one stamp drop, one run of collision paint. tools.js records both sides of a stroke and calls
  push(before, after). undo() hands back the side to apply. This file orders and stores; tools.js
  applies, because the document lives there and only one file should know its shape.

  DIFFS, NOT SNAPSHOTS. One 8 x 6 block map is 49,152 cells plus 8,192 collision bytes. Keeping a
  copy of that per step would cap the stack at a handful of steps, and the owner composes by eye,
  which means he experiments and steps back often. A patch carries only what the stroke touched.

  A PATCH, which this file never reads:
    {cells: {bg3: {idx: [...], values: [...]}, ...},
     collision: {idx: [...], values: [...]},
     tiles: [[chunk, tile], ...] or null,     the whole list, only when the stroke changed it
     stamps: [...] or null}
  BOXES are the cell rectangles the stroke touched, per layer, so undo redraws a region and not
  the whole map.
*/

export const DEPTH = 200;          // steps kept. 200 strokes of a 16 x 16 brush is about 50k cells

const done = [];                   // strokes that happened, oldest first
const undone = [];                 // strokes stepped back, newest last
let changed = () => {};

export function onChange(fn) {
  changed = fn;
}

export function clear() {
  done.length = 0;
  undone.length = 0;
  changed();
}

/* Record a stroke. A new stroke drops the redo stack, which is what every editor does. */
export function push(before, after, boxes, label) {
  done.push({ before, after, boxes, label });
  if (done.length > DEPTH) done.shift();
  undone.length = 0;
  changed();
}

export function undo() {
  const entry = done.pop();
  if (!entry) return null;
  undone.push(entry);
  changed();
  return { patch: entry.before, boxes: entry.boxes, label: entry.label, back: true };
}

export function redo() {
  const entry = undone.pop();
  if (!entry) return null;
  done.push(entry);
  changed();
  return { patch: entry.after, boxes: entry.boxes, label: entry.label, back: false };
}

export function counts() {
  return { done: done.length, undone: undone.length, last: done.length ? done[done.length - 1].label : "" };
}
