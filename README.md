# LOG

LOG joins two Game Boy Advance games into one. You start in Dragon Ball Z: The Legacy of Goku II and keep
playing straight through Dragon Ball Z: Buu's Fury, as a single game. It is a personal project and is not
shared or distributed.

## How it works

The original game is never edited by hand. Every change is a small Python file called a patch. A build list
is a text file that names the patches and the order to apply them. The build script starts from a clean copy
of the original ROM, applies each patch in turn, and writes a new ROM.

The point of doing it this way is that nothing is ever lost. The hack can be rebuilt from nothing at any
time, and the same build list always produces the exact same file, down to the last byte. If a rebuild comes
out different, something changed, and the tests say what.

## The two builds

There are two build lists, and they differ by one line.

- **Golden** is `build_list.txt`. It only uses art that is finished. This is the one that can be built from
  this repository on its own.
- **Dev** is `build_list_dev.txt`. It adds the Gohan gi sprites, which are still being drawn. Those sprites
  are not in this repository, so dev cannot be built from a fresh copy of it.

Both lists pull the other 22 patches from `build_list_core.txt`, so a change to the hack lands in both.

## Building it

You need your own legally dumped copies of both games, in `data\roms\`. Then run:

```
py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list.txt --out <name>.gba --log <name>.md
```

Run the tests with:

```
py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent
```

## Words used here

The notes use the game's own vocabulary. These are the words that come up first and most often.

| Word | What it means |
|---|---|
| **patch** | One small Python file that changes the ROM. The whole hack is a stack of them |
| **build list** | A text file naming the patches and the order to apply them |
| **set** | One character's whole sprite collection, picked by a number called a set id. Gohan in the armor is set 56 |
| **anim** | One animation inside a set, such as walking or standing. A set holds many |
| **dir** | Which way the character faces in that animation |
| **frame** | One picture. An animation is a short run of frames |
| **record** | One entry in a table. A sprite record is the packed bytes of one frame; a scene record is one cutscene |
| **palette index** | A number from 0 to 255 that picks a colour. Sprites never store colours, only these numbers |
| **scene** | A cutscene. The game stores it as a run of small numbered commands |
| **scene table** | A list of scene records, held by one region of one map |
| **seq** | A scene's position in its table, counted from the start |
| **ext** | One command inside a scene, such as "put this character in this outfit" or "show this line" |
| **word** | A four-byte value in the ROM that points at a table or a record. Moving a scene means repointing the words that name it |
| **flag** | One yes-or-no bit of story progress. Flag 195 means Cell is beaten |

## Where to start reading

- `docs\RE-BIBLE.md` is the most useful file here. It is one long searchable list of everything I have
  worked out about how the games store things: where the sprites are, how a cutscene is encoded, what each
  byte in a record means. Search it before digging into the ROM, because the answer is often already there.
- `docs\build-log.md` lists every ROM ever built with its fingerprint.
- `docs\design\` holds the plan for how the two games get joined.
- `docs\research\re-overview.md` explains how the game engine is put together.

## What is in each folder

| Folder | What it holds |
|---|---|
| `art\` | The pictures the game is built from: sprite frames, auras, portraits, palettes |
| `builds\` | Every ROM that has been built, with its save file. Test builds sit in `builds\mockups\` |
| `data\` | The original ROM dumps and anything ripped from them. Nothing here is ever written to |
| `docs\` | Everything written down: the bible, the designs, the research |
| `docs\tasks\` | One folder per job: what the job was, and what came of it |
| `scripts\permanent\` | The build script, the build lists, the patches, the tools and the tests |
| `scripts\permanent\patches\` | The patches themselves. One file per change to the game |
| `scripts\permanent\rom\` | Tools that read and write the ROM: sprites, saves, compression, free space |
| `scripts\permanent\scene\` | Tools for cutscenes: read one, write one, draw a map, run one in a test |
| `scripts\permanent\disasm\` | A disassembler written for this project, for reading the game's code |
| `scripts\one-time\` | Scripts written to answer one question, kept with the answers they printed |
| `test-data\saves\` | Save files the tests load |
| `archive\` | Old copies kept by date, in case something needs to be looked at again |
| `scratch\` | Throwaway. Anything here can be deleted and remade by running a command |

Only `art\`, `docs\`, `scripts\` and the files at the top level are in this repository. The rest is either
game data, which cannot be shared, or scratch, which is not worth sharing.
