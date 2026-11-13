# What moves where: every area, measured

Companion to [the structure standard](2026-11-13-project-structure.md) and
[the full inventory](2026-11-13-project-inventory.md), which lists all 110 folders with their file
counts, sizes and readers. **Nothing has been moved.**

The owner, 2026-11-13: "drilldown into every folder... Builds are a mess. Even our tools arent
properly named or organized by function." And: "Scratch too."

## How a folder was judged

Every folder was matched against a corpus of 3,682 files under `scripts\` and `docs\`, read once,
with two shapes: the name as a quoted literal, and the name as an `<area>\<name>` path. **Only a
reader under `scripts\permanent\` blocks a move.** A one-time script or a doc mention is history.

A bare substring search was tried first and was useless: it reported 48 readers for `art\finale`,
which has none. "anim", "work", "finale" and "plateau" are ordinary words.

---

## `builds\`: the worst offender by size

| What | Count | Size |
|---|---|---|
| Loose at the root, no folder | 176 files (48 `.gba`, 46 `.sav`, 82 states) | about 800 MB |
| `mockups\` | 454 files across 20 dated folders | **2,336 MB** |

**Target.** `masters\` for the current golden and dev ROMs. `trials\<date>-<topic>\` for everything
else, one folder per TYPE with every version inside it, which is already his rule. `saves\` for the
seed saves the build script reads.

### The keep rule, SETTLED (owner, 2026-11-13)

**Each trial folder keeps its newest ROM, with that ROM's own save and state. Everything older goes,
saves and states included.** His words: "old saves for old builds are stale and not needed."

Measured breakdown of the 3,111 MB:

| Type | Files | MB |
|---|---:|---:|
| `.gba` | 193 | 3,094.9 |
| `.ss*` | 171 | 14.0 |
| `.sav` | 190 | 1.5 |

The ROMs are the whole problem. Any ROM rebuilds from its build list in seconds, so this loses
nothing that cannot be remade. Expect to free about 2.7 GB.

**Before the first delete:** list exactly what goes, by name, and get his yes on that list. A
delete is not reversible and a ROM he is mid-test on looks identical to one he is finished with.

## `scratch\`: 53 folders, 18,779 files

| Folder | Files | MB | Note |
|---|---:|---:|---|
| `capture` | 6,293 | 228 | emulator screenshots |
| `venv` | 2,450 | 68 | **a Python virtualenv living in scratch** |
| `gi-v2` | 2,341 | 391 | old gi rounds, 24 ROMs inside |
| `2026-11-12-trunks-check` | 2,036 | 2 | yesterday |
| `sprite-exports` | 1,597 | 2 | |
| `trunks` | 1,165 | 2 | |

Scratch is already correctly gitignored and deletable without asking. The faults are that it holds
a virtualenv, that 24 ROMs are hiding in `gi-v2`, and that only some folders are dated.

**Target.** Every scratch folder is `<date>-<topic>`. The virtualenv moves out of the project. ROMs
never live in scratch; they belong in `builds\trials\`.

## `scripts\`: the tools are better organised than they look

`scripts\permanent\` is already split by function, and that part is sound:

| Folder | `.py` | What |
|---|---:|---|
| `tests` | 82 | the suite |
| `patches` | 48 | the build modules |
| `rom` | 21 | ROM readers and writers |
| `art` | 17 | art pipeline |
| `scene` | 9 | maps and scenes |
| `map-editor` | 6 | |
| `disasm` | 5 | |
| `emu` | 3 | |

Three faults, none structural:

1. **21 `build_list*.txt` files sit loose among the tools.** They are build configuration, not
   tools. Target: `scripts\permanent\build-lists\`, with the two masters named plainly and the
   trials as `<topic>.txt`.
2. **Redundant prefixes.** `rom\log2_save.py` and `rom\log2_sprites.py` carry a `log2_` prefix
   inside a project that is entirely LoG II. `rom\rom_info.py`, `rom_sheet.py` and `rom_space.py`
   repeat their own folder.
3. **Family names are inconsistent.** `rom\` holds a `sprite_*` family of four, a `rom_*` family of
   three, a `find_*` family of two and nine singles. `art\` holds a `gi_*` family of five.

**Target.** Drop a prefix that repeats the folder. Keep a prefix that names a real family.

`scripts\one-time\` is 4,778 files in 150 folders. It is history and nothing blocks moving it. 123
of its folders share a name with a `docs\tasks\` folder.

## `art\`: measured, and most of it is live

34 folders, excluding his live `Owner Build - Trunks Tank\`, which was not opened or listed.

**Free to move today, no permanent reader:** `finale`, `gi_base_v2`, `gi_ssj_v5`, `gi_ssj2_aura_v5`.

Everything else has a permanent reader, including the folders that look abandoned: `gi_ssj_v2` (9),
`gi_ssj2_v2` (8), `gi_ssj2_aura` (8), `gi_ssj_v4` (4), `gi_ssj2_v4` (4), `gi_ssj2_aura_v4` (3).
**They are live build inputs. Renaming them without `log_paths.py` owning the names breaks builds.**

**His rule, 2026-11-13: "Ours will always be separate from vanilla, like our white aura effect."**
That becomes the top split:

```
art\ours\        characters\, portraits\, effects\, ui\     everything we drew or recoloured
art\vanilla\     sets exported from the base ROM, untouched
art\ported\      exported from Buu's Fury, official but not ours
```

The white aura is the case that proves it: the gold is ported, the white is ours.

---

## The order, unchanged

Nothing physical moves until `log_paths.py` names every folder the code reads and a test forbids
folder names as literals anywhere else. Then the move is one file, and both masters rebuilding to
their existing SHA-1s proves it changed nothing the game sees.
