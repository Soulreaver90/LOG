# Research 3: LoG II code map (read only)

2026-10-16: "look into the code further for LoG II, break it down and see what else." Later slices need a map of the whole engine: Buu's Fury story content moves onto this engine, stats carry over, blocking and knockback change, and new moves arrive. This is research only. Do not build a patch or a ROM.

## Start from what is known

Read `docs\RE-BIBLE.md` in full and the `docs\re-*.md` and `docs\research-*.md` files. Do not repeat that work. Extend it.

## Map these subsystems (each: entry points, key RAM, key ROM tables, confidence)

1. Boot, main loop and frame timing; interrupt handlers.
2. Object system: object list, vtables, the message system (known messages 7, 8, 0x21, 0x23, 0x24), object create and destroy.
3. Script engine: the opcode table, ext ops (known: 35, 42, 43, 46, 47, 49, 73, 112), how maps start scripts, how flags are set and read.
4. Maps: map table, map load, warps, tile and collision data, enemy spawns.
5. Combat: hit detection, the damage formula (0x0800F94E and the attacker side 0x0800F974), knockback, blocking, the hold-attack special, ki blasts and special moves, and what a "move" is in data.
6. Characters and party: party switching, per-character records (0x03000E90 struct layout per character), level and EXP curves, the level 50 cap, character-specific moves and forms.
7. Items and equipment, shops, and the inventory layout.
8. Menus and input: the menu state machine, the status page, journal, items; the input code the status research could not trace.
9. Sound and music driver (identify only: which engine, where the song table is).
10. Text: the font, the text record format, and where the English strings live.

## Output

- `docs\research\re-overview.md`: one section per subsystem, a short "how it works" paragraph, a table of addresses with CONFIRMED, LIKELY or SPECULATIVE labels, and a "what later slices need from here" line. End with a ranked list of the 10 most useful unknowns for the merge, each with a suggested way to answer it.
- RE-BIBLE lines for every new fact. LF line endings.
- Listings and scripts in `scripts\one-time\2026-10-17-engine-overview\`.

Time box: one run. Breadth first: a LIKELY map of all ten beats a CONFIRMED map of three. Never write under `data\`. Install nothing.
