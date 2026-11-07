# Brief: build the grassy plateau, our own map

Agent: study and build in one. Read `docs\tasks\global.md` first. Absolute paths only. Never `cd`.
Deliverable: a TRIAL ROM the owner can stand on the plateau in, with its `.sav` beside it.

## What he asked for

He showed a reference frame from the anime: a **flat, bright green plateau**, open sky, distant mesas,
scattered rock, where Trunks fights Cell. Then: "Even if the ingame is small, we can make our own map, it
should be enclosed, large is fine."

So: **our own map, enclosed, large, flat bright grass.**

## Why we are building rather than reusing. I measured this, do not repeat it.

I ranked all 327 maps by the fraction of bright green inside each one's largest solid open rectangle.
The best is map 10,14 at **36.7% green in a 168x160 area**, then 4,73 at 27.9%, 10,1 at 27.5%, 11,4 at
27.1%. **No vanilla map is a clearing.** They are all travel maps and every one mixes grass with path,
rock and water. Nothing in the ROM matches the reference.

**The thing that makes a plateau hard to draw is what makes it cheap here: it is flat.** A flat field is
a tilemap that repeats one or two tiles. This is tilemap generation, not art. Use grass tiles the ROM
already owns. Do NOT author new pixels.

## Every piece is already proven in this tree. Read these two modules first.

- `scripts\permanent\patches\battle_arena.py` clones a map into a NEW appended entry, relocates the map
  table, gives the clone **its own BG2** while inheriting the other layers, hand-builds a collision frame,
  and strips the entry to 0 regions and 0 items. That is almost exactly this job.
- `scripts\permanent\patches\future_androids.py` does the same a second time and **composes on top of
  battle_arena's relocation**, reading the LIVE table base at `rom:0xEBD8` and count at `rom:0xE0AE`.
  Your module is the THIRD such append and must compose the same way.

**Do not edit `future_androids.py`. Another agent is fixing its word 4 right now.**

## The map to build

- Clone a source map whose tile stream carries bright grass. **Triceratops Jungle (maps 4,50 to 4,59)**
  is the brightest grass in the game; 4,50's lower half is a large clean field. Verify by rendering
  before you commit to a source, and say which map you took the tiles from and why.
- **Its own BG2**, generated: a flat grass fill. Target a map of about **1024x1024** with an enclosed
  playable interior of at least **768x768**. He said large is fine.
- The other BG layers must not draw the source map's trees, water or buildings over the field. Decide how
  (blank records, or a source whose other layers are already empty) and say what you chose.
- **Enclosed.** The collision frame must close the border so he cannot walk off the field. `battle_arena`
  hand-builds a frame; reuse that method rather than inventing one.
- **0 regions, 0 doors in BOTH carriers, banner `0xDD`, combat on.** Verify on the BUILT ROM with
  `scene_probe.py --map`, and put the listing in your report.
- Scattered rock from the same tileset is welcome if it stops a large repeated tile reading as wallpaper.
  That is the one real risk in this job. Use your judgement, show it, and say what you did.

## How he reaches it

Point the ending's existing arena load at the plateau instead of map 6,100. `ending_fight.py` owns the
record that loads the arena; find the single word that names 6,100 and repoint it. Everything else in the
ending chain stays as it is. He then reaches the plateau by playing the sequence that already works.

Trial module on its own list, `build_list_trial_plateau.txt`, chaining the future androids list so the
whole sequence is present. **Do NOT touch `build_list.txt` or `build_list_core.txt`.** Golden must still
rebuild to `acf1b15f` and dev to `ffbd2bfc`.

## Do NOT do these

- Do not add the wind or rain overlay. He should judge the grass clean first. We know how to add it later
  (bible tag `OVL`: one BG0 record plus the layout's BLDCNT, EVA and EVB word).
- Do not change the fight, the dialogue or any record other than the one load word.
- Do not author new tile art.

## Rules

- `py -3.14 -P`. Never put a Windows path inside a Python string literal in a heredoc.
- Never write under `data\`. Never overwrite a ROM, save or state: check absence, then create exclusively.
- Never pipe a test run into `tail` or `head`. Run your own module's tests plus `test_battle_arena`,
  `test_ending_fight`, `test_build` and `test_golden`. Not the full suite.
- A trial ROM is not real until you read the changed bytes back OUT of the built ROM.
- Build into `builds\mockups\2026-11-07-plateau\`, one folder for this mockup type, versions inside it.
- Cite bible facts by TAG and address, never by a line number. Rows as `rows.md`, tag `PLT`.

Report: a RENDER of the finished plateau saved as a PNG so he can look at it, the `--map` listing from the
built ROM, what you changed, the ROM's SHA-1, your test counts with real exit codes, and the one thing you
are least sure reads well.

One report message, then stop. Do not add a byte order mark.
