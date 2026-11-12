# Brief: what is useful to LOG in the dragonbyte-z repository

**Study only. Read-only. NEVER RUN ANY CODE FROM THAT REPOSITORY.** It is a third-party clone, so the
project's untrusted-download rule applies: read it, do not execute it, do not import from it into our tree
during this task. Follow `docs\tasks\global.md`.

Target: `C:\Users\josephgonzalez\Documents\GitHub\dragonbyte-z` (cloned 2026-11-06, HEAD `5e8c3b9`).
It is MPL-2.0. It was written by a fellow modder the owner knows on Discord, so this is collaboration, not
salvage. Credit their work by name in the catalogue.

## The owner's ask, in his words

> "mayve have an agent do an extensive review, find whats useful for our needs, from reserach to tools to
> tests and note them. I argue we can keep them all in our single repo (ignored) for local dev work."

So the deliverable is a **catalogue of concrete, actionable items**, plus a recommendation on which pieces to
vendor into our repo under a gitignored folder for local development.

## What I already established, so do not redo it

I was wrong three times about this repo by searching too narrowly. Learn from that: use several search
shapes, and never conclude a category is absent from one grep.

- **Their `SCRIPT_VM.md` is the LoG2 bytecode VM**, byte-exact round-tripped, 804 tests, canonical LoG2
  SHA-256 `6e6c370c...56ff75`. Their base dispatch table is `0x083B5C00`; our ext handler table is
  `rom:0x3B5D28`, exactly `0x128` later, which our bible row 1037 already states. Same machine, documented
  from the other end. Their LoG2 corpus is the "static43 family", not the whole game.
- **`LOGX_*` means Legacy of Goku GENERALLY**, LoG1, LoG2 or Buu's Fury, which is Legacy of Goku 3
  internally. The engine is shared, so their sprite, tile, layer, frame and codec research should carry to
  our ROM with addresses re-derived. Treat that series as high priority, not as Buu's Fury only.
- **Six research docs name the LoG2 ROM by SHA:** `SCRIPT_VM.md`, `CELL_PALETTE_ROUTE_C.md`,
  `LOGII_AUTHORED_IMAGE_ROUTE.md`, `LOGII_TEXT_FORMAT.md`, `MAP_RECORD_EDITING_VERIFICATION.md`,
  `rom_editor_coverage.json`.
- **`tools/runtime/` holds 112 mGBA Lua scripts** driving stock mGBA 0.10.5, the owner's build. The API they
  use: `emu:read`/`readRange` (348), `callbacks:add` (107), `emu:setKeys`/`addKey`/`clearKey` (140),
  `emu:getGameCode` (94), `emu:setBreakpoint`/`clearBreakpoint` (102), `emu:screenshot` (54),
  `emu:readRegister` (53), `emu:saveStateFile`/`loadStateFile`, `emu:setRangeWatchpoint`, `emu:reset`.
  **Caveat:** their `ROM010_RUNTIME_PROBE_RELIABILITY.md` records a run that came back ENVIRONMENT BLOCKED,
  `mgba_api_probe.lua` exists because `emu:setBreakpoint` failed on one build, and they later wrote a C patch
  for native reads. So reads, input, screenshots and state files look solid; breakpoints and registers do not.
- **`LOGII_16MIB_RUNTIME.md`** independently measured that a 16 MiB LoG2 image boots and reads above the 8 MB
  boundary. That corroborates our own expansion decision.
- **A real trap their `SCRIPT_VM.md` exposed in OUR code:** "Negative zero is representable and must
  round-trip unchanged. Do not canonicalize encoding." Our `scene_lib.zigzag()` cannot emit negative zero
  (`-0 == 0` in Python) and strips redundant `0x80` padding. Real examples in the script region:
  `rom:0x3b0034` is `01` and re-encodes to `00`; `rom:0x3b0017` is `804e` and re-encodes to `4e`;
  `rom:0x3b0106` is `8080c403` and re-encodes to `c403`. We are safe today only because `relocate()` copies
  untouched ops verbatim. **Confirm that and propose the guard test**, but do not change code.

## What to produce

`docs\tasks\2026-11-06-dragonbyte-review\catalogue.md`, organised so the owner can act on it:

1. **Ranked, actionable items.** For each: what it is, the file path in their repo, what LOG gains, the
   effort, and whether it is blocked on anything. Rank by value to LOG, highest first. Be specific: "their
   `X.md` gives the Y format, which would replace our hand-derived Z" beats "useful graphics research".
2. **An applicability column on every item**, one of: **DIRECT** (their evidence is LoG2), **SHARED ENGINE**
   (addresses must be re-derived for our ROM, formats should carry), or **BUU ONLY** (no path to LoG2).
   Say which shape proved it, and do not call something BUU ONLY on a single grep.
3. **Where we are AHEAD**, so the owner can trade back. I know of one: their Buu's Fury collision work is
   BLOCKED at the evidence gate with no codec, while our LoG2 collision format is confirmed from
   `collision_test @0x08005D6C` with stride and bit order pinned. Find the others. Check our bible's section
   list against their coverage.
4. **A vendoring recommendation.** Which specific files or folders to copy into our repo under one gitignored
   folder for local dev, and which to leave in the clone and simply read. State the MPL-2.0 position per
   item: facts are free, a copied FILE stays MPL-2.0 and keeps its notice. LOG is private and undistributed
   today, so copyleft obligations do not trigger, but the notice travels with the file.
5. **Their tests**, which the owner named explicitly. What do they test, is any of it a harness we could
   point at our ROM, and is any of it a conformance suite for a shared format.
6. **The mGBA Lua route, assessed honestly.** Our biggest workflow cost is that the owner hand-makes save
   states so I can measure. Say whether their scripts show a reliable path to reading memory and driving
   input on stock mGBA 0.10.5, name the scripts worth starting from, and state plainly what is NOT proven.

## Rules

- Read our `docs\RE-BIBLE.md` section list and `docs\tool-index.md` first, so "useful to LOG" means useful
  against what we already have, not useful in the abstract.
- Label every claim CONFIRMED, LIKELY or SPECULATIVE. Quote the file and line for anything load-bearing.
- Say "the search returned nothing", never "it does not exist".
- Do not copy their code into our tree in this task. Recommend, do not vendor.
- No em or en dashes, no byte order mark. Any study script goes in
  `scripts\one-time\2026-11-06-dragonbyte-review\`.
- If you learn a ROM fact about OUR game that we can verify, put it in `rows.md` with tag `DBZ`, but only
  when their evidence is DIRECT or you verified it against our ROM yourself.

One report message, then stop. Do not add a byte order mark.
