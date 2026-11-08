/*
  cells.js - What one cell of a brush or a stamp means, and which VRAM slot it lands in.

  No DOM here, on purpose. This is the step that decides what a placement writes, so a node test
  can run the real mechanism rather than a copy of it.

  A PATCH CELL has three forms, and every reader must branch on them.
    null                 leave what is under me alone
    [chunk, tile, flips] a tile of the 168 chunk pool. The same art in every map, which is why a
                         stamp stores a pair and never a slot: slot 300 of map 7,15 is not slot
                         300 of a blank map.
    {g, t, f}            tile `t` of the patch's OWN animated group `g`, flipped by `f`. A group
                         slot has no chunk pair at all, so this form exists to carry it.

  WHY A GROUP TRAVELS WITH THE PATCH. An animated group is pixels, not a pool reference, so a
  stamp carries `animated: [{first, frames: [{duration, pixels}]}]`, copied whole from the map it
  was grabbed from. That is what lets a stamp place waving grass into a map that has never held
  it: the pixels are in the stamp. `first` is kept as provenance and is NEVER identity, for the
  same reason a cell is not a slot. Two groups are the same group when their frame pixels and
  their durations match.

  WHERE A NEW GROUP GOES. From the TOP of the 896 slot budget downward, which is where the game
  puts them: map 7,15 streams 633 static tiles and its one group owns 894 and 895, the last two
  slots of the budget. A group parked just past the static stream would
  cap the stream where it sits, because the stream grows upward and may never run into a group's
  slots (bible B1078: the loader DMAs count * 64 bytes to 0x06000000 + slot * 64, the same VRAM
  the +0x48 stream fills, so one slot cannot hold both).

  THE LIMITS ARE THE HARDWARE'S. 16 groups (the IWRAM state array), 64 tiles a group (the 0x1000
  byte load buffer, bible B1078) and the 896 slot budget. map_file._check_animated enforces the
  same three in Python, and a document that breaks one is refused at Save.

  A placement that cannot fit a group writes NOTHING in those cells and says which limit stopped
  it. It never substitutes a static look-alike: the owner asked for the animation by name.
*/

// ===== what a cell is =====

export function isAnimatedCell(cell) {
  return Boolean(cell) && !Array.isArray(cell);
}

export function animatedCell(group, tile, flips) {
  return { g: group, t: tile, f: flips || 0 };
}

export function groupTileCount(group) {
  const frames = (group || {}).frames || [];
  return frames.length ? Math.floor((frames[0].pixels || []).length / 64) : 0;
}

/* Two groups are one group when they animate the same way. Never by `first`, which is a slot. */
export function groupKey(group) {
  const frames = (group || {}).frames || [];
  return frames.map((f) => `${f.duration}:${Array.from(f.pixels || []).join(",")}`).join("|");
}

export function findGroup(doc, group) {
  const want = groupKey(group);
  return ((doc || {}).animated || []).findIndex((held) => groupKey(held) === want);
}

/*
  Which group of the document owns this VRAM slot, or -1. The LAST match wins, because the groups
  are loaded after the static stream and in list order, so a group that overlaps an earlier one
  draws over it, exactly as render.js lays its slot sheet and as the game loads. Map 6,99 is the
  one vanilla layout whose groups overlap the stream.
*/
export function groupAtSlot(doc, slot) {
  const groups = (doc || {}).animated || [];
  for (let k = groups.length - 1; k >= 0; k -= 1) {
    const first = groups[k].first;
    if (slot >= first && slot < first + groupTileCount(groups[k])) return k;
  }
  return -1;
}

/* [first, past) of every group the document already holds, plus any this placement has planned. */
function spansOf(doc, planned) {
  const spans = ((doc || {}).animated || [])
    .map((g) => [g.first, g.first + groupTileCount(g)]);
  for (const entry of planned) spans.push([entry.first, entry.first + groupTileCount(entry.group)]);
  return spans;
}

function inSpans(spans, slot) {
  return spans.some(([first, past]) => slot >= first && slot < past);
}

/*
  The highest free span of `count` slots that sits above the static stream and clear of every
  group. -1 when there is none. Downward from the top, so the stream keeps the room it has.
*/
export function freeGroupFirst(doc, count, budget, planned = []) {
  if (count <= 0) return -1;
  const spans = spansOf(doc, planned);
  const floor = ((doc || {}).tiles || []).length;
  for (let first = budget - count; first >= floor; first -= 1) {
    let clear = true;
    for (let n = 0; n < count && clear; n += 1) clear = !inSpans(spans, first + n);
    if (clear) return first;
  }
  return -1;
}

// ===== the plan: every cell of a patch, as a slot =====

const pairKey = (chunk, tile) => `${chunk},${tile}`;

function streamIndex(doc) {
  const index = new Map();
  (doc.tiles || []).forEach(([chunk, tile], slot) => {
    const key = pairKey(chunk, tile);
    if (!index.has(key)) index.set(key, slot);
  });
  return index;
}

function groupsOf(patch) {
  return patch.animated || [];
}

/*
  Work out what this patch needs before anything is written: which slots its cells land in, which
  [chunk, tile] pairs the map must gain, and which animated groups it must gain.

  Groups are resolved FIRST, because they are allocated from the top of the budget and the static
  stream may not grow into them. Raises when the static stream cannot fit, with the number, which
  is the one failure that must stop the whole placement: half a boulder is worse than none.
  A group that does not fit refuses only its own cells and is named in `refusals`.
*/
export function planPlacement(doc, patch, limits) {
  const { budget, groupMax, groupMaxTiles } = limits;
  const groups = groupsOf(patch);
  const wanted = new Set();
  let statics = false;

  for (const cells of Object.values(patch.layers || {})) {
    for (const cell of cells) {
      if (!cell) continue;
      if (isAnimatedCell(cell)) wanted.add(cell.g);
      else statics = true;
    }
  }

  // ----- the groups
  const addGroups = [];
  const refusals = [];
  const firstOf = new Map();                       // patch group index -> slot, or null when refused
  for (const which of [...wanted].sort((a, b) => a - b)) {
    const group = groups[which];
    const count = groupTileCount(group);
    if (!group || !count) {
      refusals.push("a cell names an animated group this stamp does not carry, so it was left as "
                    + "it was");
      firstOf.set(which, null);
      continue;
    }
    const held = findGroup(doc, group);
    if (held >= 0) { firstOf.set(which, doc.animated[held].first); continue; }
    if (count > groupMaxTiles) {
      refusals.push(`an animated group of ${count} tiles does not fit: the load buffer holds `
                    + `${groupMaxTiles}`);
      firstOf.set(which, null);
      continue;
    }
    if ((doc.animated || []).length + addGroups.length >= groupMax) {
      refusals.push(`this map already carries ${groupMax} animated groups, which is all the state `
                    + "array holds, so its waving tiles were left out");
      firstOf.set(which, null);
      continue;
    }
    const first = freeGroupFirst(doc, count, budget, addGroups);
    if (first < 0) {
      refusals.push(`there is no free run of ${count} slots under the ${budget} tile budget for an `
                    + "animated group, so its waving tiles were left out");
      firstOf.set(which, null);
      continue;
    }
    addGroups.push({ group, first });
    firstOf.set(which, first);
  }

  // ----- the static stream, which may not grow into any group, new ones included
  const index = streamIndex(doc);
  const spans = spansOf(doc, addGroups);
  const addTiles = [];
  if (statics) {
    for (const cells of Object.values(patch.layers || {})) {
      for (const cell of cells) {
        if (!cell || isAnimatedCell(cell)) continue;
        const [chunk, tile] = cell;
        if (!Number.isInteger(chunk) || !Number.isInteger(tile)
            || chunk < 0 || chunk > 0xFF || tile < 0 || tile > 0xFF) {
          throw new Error(`a cell of this patch is [${chunk}, ${tile}], which is not a chunk and a `
                          + "tile. Nothing was placed.");
        }
        const key = pairKey(chunk, tile);
        if (index.has(key)) continue;
        const slot = (doc.tiles || []).length + addTiles.length;
        if (slot >= budget) {
          throw new Error(`this map already loads ${budget} tiles, which is the hardware's limit. `
                          + "Place art it already loads, or free some.");
        }
        if (inSpans(spans, slot)) {
          throw new Error(`this map's tile stream stops at slot ${slot}, where an animated group `
                          + "begins. Place art it already loads.");
        }
        index.set(key, slot);
        addTiles.push([chunk, tile]);
      }
    }
  }

  const slotOf = (cell) => {
    if (!cell) return null;
    if (isAnimatedCell(cell)) {
      const first = firstOf.get(cell.g);
      return first === null || first === undefined ? null : first + cell.t;
    }
    const slot = index.get(pairKey(cell[0], cell[1]));
    return slot === undefined ? null : slot;
  };

  return { slotOf, addTiles, addGroups, refusals };
}

/* Everything the plan said the map must gain. The caller records undo BEFORE it calls this. */
export function applyPlan(doc, plan) {
  if (plan.addTiles.length) doc.tiles.push(...plan.addTiles.map((pair) => pair.slice()));
  for (const { group, first } of plan.addGroups) {
    if (!doc.animated) doc.animated = [];
    doc.animated.push({
      first,
      frames: (group.frames || []).map((f) => ({ duration: f.duration,
                                                 pixels: Array.from(f.pixels || []) })),
    });
  }
  return plan;
}

/* The flips of a cell, whichever form it is in. */
export function cellFlips(cell) {
  return (isAnimatedCell(cell) ? cell.f : cell[2]) || 0;
}
