# Art tables

Dialog portraits and OBJ palette entries for the hack. `inject.py` changes them and builds the next ROM in about one second.

| File | Holds |
|---|---|
| `portraits.json` | Dialog portrait id to PNG (`portraits\NNN_name.png`) and a note |
| `palette.json` | OBJ palette index to color `[r, g, b]`. Each channel is a multiple of 8 |
| `portraits\` | The stored PNGs: 64x64, indexed, OBJ palette |

## Commands

Run each command from the LOG root.

| Command | Does |
|---|---|
| `py -3 -P scripts\permanent\art\inject.py portrait <id> <png>` | Adds or replaces a portrait, then builds the next ROM |
| `py -3 -P scripts\permanent\art\inject.py portrait <id> <png> --snap` | Same, but maps off-palette colors to the nearest index |
| `py -3 -P scripts\permanent\art\inject.py palette <index> <r,g,b>` | Sets one OBJ palette entry (both ROM copies), then builds the next ROM |
| `py -3 -P scripts\permanent\art\inject.py check <png> [id]` | Validates a PNG only. Writes nothing |
| `py -3 -P scripts\permanent\art\inject.py list` | Prints the tables and the next build name |

**Example:**

```
py -3 -P scripts\permanent\art\inject.py portrait 40 art\portrait-sources\remaster\final_r22\cell_40.png
```

The command checks the PNG and builds `builds\log2_poc_rN.gba` from `scripts\permanent\build_list.txt`. It verifies the ROM and prints the SHA-1 and the diff regions. It copies the latest `.sav` and `.ss*` to the new name and adds one line to `docs\build-log.md`.

## Rules the check applies

- The PNG is 64x64. It can be indexed or RGB, but every pixel must be opaque.
- Each color must equal an OBJ palette color (with `palette.json` applied) that a vanilla dialog portrait uses or that `palette.json` sets. Index 0 and index 168 are never allowed. An off-palette color is reported with its nearest index. Add `--snap` to map it.
- The outer 3 px frame must equal the frame the id shows without the table. That is the vanilla portrait, or the `gohan_portraits` art for ids 115, 117 and 119.
- A portrait can use 64 colors at most, which is the size of the status page pool.
- Valid ids are 26-121, except 116, 118 and 120 (the status twins use the BG palette).

> [!NOTE]
> Each portrait has a fixed slot at `rom:0xF00000 + 0x1008 x id`. A new or changed portrait never moves another portrait or any code, so save states keep working.

> [!WARNING]
> Nothing is written when a check fails. The tool never overwrites a ROM, `.sav` or state file. A palette change to an index that a table portrait uses stops the build until you inject that portrait again.
