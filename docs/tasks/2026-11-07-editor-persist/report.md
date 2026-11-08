# Map editor: never lose work again, prune stamps, and fix the grab holes

Date: 2026-11-07. Files: `scripts\permanent\map-editor\` plus `scripts\permanent\tests\test_map_editor_io.py`.

## Why this task existed

The owner composed a map, was told to reload the page for an unrelated fix, and lost the work. The
editor held its document only in JavaScript memory. No autosave, no browser storage, no unload guard.
His stamps survived because a grab writes a file at once. His map did not, because a map was written
only on Save. His words: "I reloaded but none of the work I did carried over", "this is a huge
oversight".

## A. A reload, a crash or a closed tab cannot cost work

| Part | Where | What it does |
| --- | --- | --- |
| Autosave | `editor\autosave.js` (new), `serve.py` | Writes the live document to `map-editor\autosave\<key>.json` on every change, debounced |
| Dirty flag | `editor\state.js` | `state.dirty`, raised by `edit()` and the history hook, lowered only by a Save |
| Marker | `index.html`, `editor\style.css`, `editor\panes.js` | A gold dot in the header and a star on the tab title |
| Unload guard | `editor\autosave.js` | `beforeunload` is cancelled while the document is dirty |
| Leave guard | `editor\panes.js` | Open, Start, Open saved and Restore ask first, then flush to disk |
| Restore offer | `index.html`, `editor\panes.js` | A bar naming the kept work, which waits for an answer |
| Retire on Save | `serve.py` `/api/save` | The autosave moves to `autosave\older\`, after the real file is written |

**Debounce: 1 second idle, 8 second ceiling.** A history push is once per STROKE, not per cell, so a
long drag already costs one write. The idle timer collapses a burst and the ceiling forces a write
under a hand that never pauses. Sizes measured: map 7,15 is 344,789 bytes of JSON, a blank 2 x 2 is
98,869.

**The gap, stated plainly:** at most one idle second of work exists only in the tab. `sendBeacon` and
`fetch` keepalive both cap near 64 KB, which a map document exceeds five times over, and they fail
silently. The guard covers a deliberate reload and the autosave covers a crash.

**Leaving the open map from INSIDE the page** was the same defect through a new door. Open a copy,
Start, Open saved and Restore each threw the open map away without a word. All four now ask, name the
open map and flush to disk first, and a new document takes a new session id, so a same-title file
moves to `autosave\older\` rather than being written over.

**The autosave folder inverts three of this tool's rules on purpose.** It is not validated, because
work in progress is often unsound and refusing to keep it is the exact failure the folder exists to
stop. It is overwritten, but only by the session that owns it. It never reaches `/api/saved`. Both
are pinned by tests.

**Nothing in this change ever unlinks a file.** `autosave_retire`, `delete_stamp` and `strip_stamp`
all move. A name collision inside `older\` or `deleted\` takes a timestamp suffix.

**An autosave is OFFERED, never loaded silently.** On the morning after a good Save, a page that
loaded the newest autosave by itself would hand back a half-finished experiment, and the first stroke
would write over the saved map. An autosave OLDER than its saved map is not offered at all.

**A failed autosave is loud.** An old `serve.py` answers 404 and a stopped one answers nothing. Either
way the marker turns red and reads "unsaved and NOT kept".

## B. Deleting a stamp

A delete button on every stamp, with a confirm. The route MOVES the file to `library\deleted\`.
`stamps()` globs `library\*.json`, which is not recursive, so nothing under `deleted\` is offered
again. The brush resets to the eraser when it held the stamp that went.

## C. Grabbing without collision

A control beside the grab name: "with its collision" (the default, right for a rock) and "art only, no
collision". Plus a `no wall` button on every library stamp that carries collision, so an existing
stamp loses its collision in place, with the old file kept in `library\deleted\`.

**The measurement, over all 27 stamps.** `writePatch` was NOT changed: a stamp still writes a wall into
every cell the grab found solid, art or not. That decision is the owner's.

| Figure | Value |
| --- | --- |
| Stamps that carry a collision grid at all | 13 of 27 |
| Stamps with at least one solid cell that draws nothing | 8 of 27 |
| Worst single stamp | `stamp 8`, 134 such cells |
| Total such cells across the library | 312 |

`stamp 8` holds 165 cells, 134 of them solid, and all 134 draw nothing. Dropping it writes 134 cells of
invisible wall and no art.

## D. The grab holes, and a correction to the controller's own figure

`grabs()` means: `"ground"` is the ONE layer selected now, `"scenery"` is every OTHER layer, `"all"` is
all four. The labels named groups and the code names layers. The options now read "every layer but
BG3", "BG3 only" and "every layer", with the selected layer written in at run time.

**The controller's 1262 figure for map 7,15 was wrong. The true count is 0.** 1262 is reproduced
exactly by ignoring the per-layer scroll offsets, which is the defect fixed earlier the same day. The
controller re-measured and confirmed both numbers: 0 with the offsets applied, 1262 without.

| Map 7,15, counted in world space | Cells |
| --- | --- |
| BG0 draws | 0 |
| BG1 draws | 5,382 |
| BG2 draws | 2,204 |
| BG3 draws | 11,424 |
| BG3 blank and another layer draws | 0 |

**The holes are real and the cause is the DEFAULT setting.** BG1 and BG2 art sits entirely over cells
BG3 also draws, so the default grab, which takes every layer EXCEPT the selected one, leaves the ground
behind and returns a box that is mostly empty.

| Setting, with BG3 selected | Cells that come back empty, of 20,480 |
| --- | --- |
| BG3 only | 9,056 (44.2%) |
| every layer but BG3 (the default) | 14,092 (68.8%) |
| every layer | 9,056 (44.2%) |

The 9,056 under the two good settings are cells where nothing draws anywhere in the map. A live grab
through the page returned "91 of them art, 55 cell(s) came out EMPTY" under the default, and "266 of
them art" with no empty cells under "every layer". The grab now says so in its status line.

## Proof

| Check | Result |
| --- | --- |
| `test_map*.py` | 94 tests, OK, of which 21 are new |
| `test_roundtrip.py` | 22 tests, OK |
| `test_import_map.py` | 26 tests, OK |
| Round trip through `roundtrip.census` | 334 of 336 layouts unchanged, 0 failed, 2 skipped |
| Full suite, run by the controller on a quiet tree | 1,724 tests, 1 failure, the known `test_form_survives_the_leader_change` |
| Element ids reached from JS | 58 of 58 exist in `index.html` |
| Byte order mark, em dash, en dash | none in any touched file |

Live sessions ran on port 8788 with `--data` pointing at a scratch folder. Port 8777 was never
contacted. Confirmed afterwards by the controller: 27 stamps still in `library\`, 2 maps still in
`maps\`, and no `autosave\` or `library\deleted\` folder in the owner's tree.

## New option on serve.py

`--data DIR` moves `maps\`, `library\` and `autosave\` elsewhere, so a test server cannot touch the
owner's files. Two smaller hardenings went with it: `/api/save` no longer returns 400 for a map that
IS saved when the retire step fails, and the autosave reads take the write lock, because on Windows a
read can land between the two halves of an `os.replace`.

## Not done

- `writePatch` is unchanged. The measurement above is the input for a decision the owner makes.
- The owner's running server on 8777 still holds the old code until he restarts it.
