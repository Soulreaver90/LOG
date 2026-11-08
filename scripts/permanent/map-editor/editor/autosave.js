/*
  autosave.js - The work exists somewhere other than this tab's memory, at every instant.

  WHY THIS FILE EXISTS. On 2026-11-07 the owner composed a map for an evening, was told to reload
  the page for a fix, and lost all of it. The document lived in JavaScript memory alone: no copy on
  disk, no warning on unload, nothing to go back to. His stamps survived because a grab writes a
  file the moment it happens. His map did not, because a map reached the disk only on Save.

  The four parts, and none of them is enough alone:
    1. every change schedules a write of the live document to autosave\, debounced
    2. a dirty document guards beforeunload, so the browser asks before a reload or a close
    3. a dirty document shows a MARKER in the page, so unsaved state is visible without reading
    4. an autosave newer than its saved map is OFFERED on the next start, never loaded in silence

  SILENTLY RESTORING IS ITS OWN WAY TO LOSE WORK. A page that loads the newest autosave by itself
  would, on the morning after a good Save, hand back a half-finished experiment instead of the map
  he saved, and the first stroke would autosave over the thing he wanted. So start() asks.

  THE SESSION ID is what makes an unanswered offer safe. Each page load makes one and sends it with
  every write. The server moves a file aside into autosave\older\ when the session that owns it
  changes, so a second tab, or this tab after he dismissed the offer, cannot erase what it declined.

  THE GAP. Everything between the last written autosave and now is still only in memory: at most
  one idle second of work, or one ceiling period under a hand that never pauses. sendBeacon would
  close it in theory and not in practice, because it caps near 64 KB and a map document is far past
  that (measured 2026-11-07: map 7,15 is 344,789 bytes of JSON, and a blank 2 x 2 is 98,869). So
  the window is kept short instead, and the unload guard covers the case the window cannot.
*/
import { state, subscribe, status, markDirty } from "./state.js";
import * as history from "./history.js";

// ===== CONFIG =====

const IDLE_MS = 1000;        // quiet time after the last change before the write goes out
const CEILING_MS = 8000;     // a hand that never pauses still writes this often

const newSession = () => `${Date.now().toString(36)}-${Math.floor(Math.random() * 1e9).toString(36)}`;
/*
  A NEW DOCUMENT GETS A NEW SESSION. Two blank 4 x 4 maps carry the same title, so without this the
  second one's first stroke would overwrite the first one's autosave in place and the first map
  would be gone. With it, the server sees a session it does not know and moves the old file into
  autosave\older\ before it writes. Nothing is ever on top of anything.
*/
let session = newSession();

let host = null;             // {paintMarker, show}
let timer = null;
let firstChangeAt = 0;       // when the current run of changes started, for the ceiling
let inFlight = false;
let queued = false;
let keptAt = 0;              // the time the server stamped on the last good write
let failure = "";            // the last refusal, which the marker shows in red

// ===== what the marker shows =====

export function info() {
  return { dirty: state.dirty, at: keptAt, failure, pending: timer !== null || inFlight };
}

/* 12-hour with AM/PM, which is how the owner reads a time. */
export function clockText(epochSeconds) {
  return new Date(epochSeconds * 1000)
    .toLocaleTimeString([], { hour: "numeric", minute: "2-digit", hour12: true });
}

// ===== the write =====

function schedule() {
  if (!state.doc || !state.dirty) return;
  const now = Date.now();
  if (!firstChangeAt) firstChangeAt = now;
  if (timer) clearTimeout(timer);
  // The ceiling, so a long run of strokes with no pause still reaches the disk.
  const wait = Math.min(IDLE_MS, Math.max(0, firstChangeAt + CEILING_MS - now));
  timer = setTimeout(write, wait);
  host.paintMarker();
}

async function write() {
  timer = null;
  firstChangeAt = 0;
  // A clean document is already on disk somewhere better than here. A timer still pending when a
  // new map arrives would otherwise keep that untouched map and offer it back as unsaved work.
  if (!state.doc || !state.dirty) return;
  if (inFlight) { queued = true; return; }        // one write at a time, and one waiting
  inFlight = true;
  try {
    const answer = await (await fetch("/api/autosave", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: state.title, session, doc: state.doc }),
    })).json();
    if (answer.error) throw new Error(answer.error);
    keptAt = answer.at;
    failure = "";
  } catch (problem) {
    // A SILENT FAILURE IS THE WHOLE DEFECT AGAIN. An old serve.py has no /api/autosave route and
    // answers 404, and a stopped one answers nothing. Either way he must see it and act.
    failure = `${problem.message || problem}`;
    status(`the work is NOT being kept: ${failure}. Save this map under a new name now, then `
           + "stop serve.py, start it again, and reload.", "bad");
  } finally {
    inFlight = false;
    host.paintMarker();
    if (queued) { queued = false; write(); }
  }
}

/* Stop the clock and let any write in flight land. Save calls this, so the two cannot race. */
export async function quiet() {
  if (timer) { clearTimeout(timer); timer = null; }
  firstChangeAt = 0;
  while (inFlight) await new Promise((done) => setTimeout(done, 25));
}

/*
  Everything in memory reaches the disk NOW. Anything that REPLACES the open document calls this
  first: opening a game map, starting a blank one, opening a saved one, restoring an autosave. The
  unload guard covers leaving the page, and this covers the same loss from inside it.
*/
export async function flush() {
  await quiet();
  if (state.dirty) await write();
  while (inFlight) await new Promise((done) => setTimeout(done, 25));
}

/* The map is in maps\ now. The server moved the autosave aside; the page forgets its clock. */
export function forget() {
  keptAt = 0;
  failure = "";
  queued = false;
  host.paintMarker();
}

// ===== the offer on start =====

/*
  Every autosave the server judges newer than the saved map of the same name. The judgement is the
  server's because it owns both files' times; the choice is the owner's because only he knows which
  of the two he meant.
*/
export async function candidates() {
  try {
    const answer = await (await fetch("/api/autosaves")).json();
    return answer.autosaves || [];
  } catch (problem) {
    void problem;                       // an old serve.py with no route: nothing to offer
    return [];
  }
}

/* Put an autosave back on screen. It is NOT clean: nothing in maps\ holds it yet. */
export async function restore(name) {
  const payload = await (await fetch(`/api/autosave?name=${encodeURIComponent(name)}`)).json();
  if (payload.error) throw new Error(payload.error);
  await host.show(payload, payload.title || name);
  markDirty();
  keptAt = payload.at;
  host.paintMarker();
  return payload;
}

// ===== start =====

export function install(hooks) {
  host = hooks;
  // "clear" is a new document arriving from the server, which is the one change that is not his.
  // It also starts a new session, so the map now on screen can never write over the one before it.
  history.onChange((reason) => {
    if (reason === "clear") session = newSession();
    else markDirty();
  });
  subscribe("dirty", schedule);

  window.addEventListener("beforeunload", (event) => {
    if (!state.dirty) return;
    event.preventDefault();
    event.returnValue = "";             // the older spelling, which some browsers still need
  });
  // A tab going to the background may never come back. Write what is pending while it still can.
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden" && state.dirty) write();
  });
}
