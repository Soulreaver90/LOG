# Test save: the Capsule Corp computer with Super Perfect Cell's scouter entry (final, 2026-10-24 11:11 AM)

Personal GBA ROM hack (Legacy of Goku II). Latest build:
`builds\log2_poc_r38.gba` (SHA-1 `7a7cb85fa5873c4a44d360b33b6755d4e71e18e3`).

## My ask (verbatim)

"For the scouter, does the capsule computer show it when you unlock the S perfect cell bio? I dont have the key card in the save
to open the door in capcsule corp to check the computer." Then: "Yes please provide a save and provie the rom link".

## Known (docs\RE-BIBLE.md, rows R31, R33, R35)

- The scouter database opens from a map object in map 6,6 (Capsule Corp; factory `@0x080191CA`, region list `rom:0x3FA370`
  item 3). The list (`@0x08019204`) shows entries whose database bit is set; the scan info screen sets the bit.
- Database bits: slot +0x11A, 16 bytes (bit n = entry n). Entry 19 is Super Perfect Cell (own name since r33).
- `scripts\permanent\rom\log2_save.py` reads, edits and seals saves (`info`, `set ... item=id,count map=zone,area,var pos=x,y`).

## Task

1. Find the key card: its item id, the door that tests it (map, condition), and where the computer room is. Quote addresses.
   Label CONFIRMED, LIKELY or SPECULATIVE.
2. Make, by exclusive create, `builds\log2_poc_r38_computer.gba` (byte copy of r38) and `.sav` from
   `builds\log2_poc_r38_scouter.sav` with slot 1 changed so I can reach the computer at once: give the key card
   (if found), set database bit 19 (Super Perfect Cell) and also bit 13 (Perfect Cell) so the list shows both rows, and place
   the player in Capsule Corp near the room or inside it at a walkable spot proved from map data. If you cannot prove a
   walkable spot, keep the slot's map and say how to walk there. Keep the scouter switch on. Seal the checksum with the tool.
3. Prove: `log2_save.py info` on the new .sav (slot 1 valid, bits, items, map, position), a byte diff of the .sav against its
   source naming every changed byte, SHA-1 of both files.
4. My steps: load, where to walk, what to press at the computer, what a pass looks like (a 'Cell, "S. Perfect"' row with the
   my portrait 52, his text and HP 9876, STR 72, POW 71, END 78).

## Report

`docs\tasks\2026-10-24-computer-save\computer-save-report.md`. Bible rows (tag CSV) in `scripts\one-time\2026-10-24-computer-save\bible_rows.md`, in the format of
`scripts\one-time\2026-10-23-r35-build\bible_rows.md`. Work files in `scripts\one-time\2026-10-24-computer-save\`.

## Limits

- Never write under `data\`. Never overwrite any ROM, save or state. No change to `scripts\permanent\`, `build_list.txt`, `art\`,
  `docs\`. Other work is running in `scripts\one-time\2026-10-24-hud-ki\`; do not touch it or `art\base-audit\`, `scripts\one-time\2026-10-23-base-audit\`.
- Python: LF, no byte order mark, no em or en dashes. `py -3 -P` (`-I` for log2_save.py). Never `cd`, in any shell, ever;
  absolute paths only. Create files with Python or Python `open(..., "x")`, never shell redirection, `sed`, `printf`,
  `cp`, `rm` or `mkdir`.

