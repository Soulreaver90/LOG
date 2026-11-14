# Save points

Jump straight to a moment in the game, on any build, without replaying to it.

> [!IMPORTANT]
> **The `.sav` files in `points\` are NOT in git.** `.gitignore` line 28 ignores `*.sav`, and it
> ignores `builds\` and `test-data\` outright. So a save file lives on one disk and one disk only.
> That is exactly how save points keep getting lost.
>
> **The recipe is the real save point, not the file.** Every point below is a named preset in
> `scripts\permanent\rom\log2_save.py`, which IS in git. Delete this whole folder and one command
> rebuilds every file in it. Treat `points\` as a cache.

---

## The points

| Point | Where it puts you | Preset |
|---|---|---|
| **chamber_exit** | The Time Chamber floor, Vegeta leading, **one scene trigger from Piccolo handing Gohan the gi**. | `chamber_exit` |
| **cellgames** | Dende's Lookout, Goku leading, just before the Cell Games. | `cellgames` |
| **cellgames2** | The same, with flag 191 just set and the arena maps unvisited. | `cellgames2` |
| **postcell** | Capsule Corporation after Cell, the general purpose late save. | `postcell` |
| **farewell** | Below Dende on the Lookout, **one A press from the ending**. | `farewell` |
| **spritelab** | A flat empty field with the HUD off and a fixed camera, for looking at sprites. | `spritelab` |

Each file holds three slots. The table says what slot 1 is. Slots 2 and 3 are usually spares at the
same spot, because a scene plays once and a lost run means replaying to it.

### Why chamber_exit reaches the gi scene

Measured, not assumed. Its flags are 151 SET, 156 SET, 157 CLEAR, 158 CLEAR.

1. The map 6,16 region fires its scene when flag 151 is set and 157 is clear. That scene SETS 157.
2. The chamber exit table `rom:0x3DBDD4` runs once 156 and 157 are both set.
3. The Piccolo gi handoff is part of that table, appended by `patches\piccolo_gi_scene.py`.

Bible rows B0671 and B0828. Flag 158 is still clear, so the exit has not run yet.

---

## Putting a point on a build

Two commands, both of which already existed. Run them from the LOG root.

**1. Make the save.**

```
py -3.14 -P scripts\permanent\rom\log2_save.py build test-data\saves\log2_lv40_postcell.sav saves\points\chamber_exit.sav --set chamber_exit
```

**2. Pair it with a new build.**

```
py -3.14 -P scripts\permanent\log2_build.py --list build_list_dev.txt --out builds\mockups\my_build.gba --save saves\points\chamber_exit.sav
```

`log2_build.py` never replaces a `.sav` that is already beside a ROM, so step 2 is safe to repeat.

**To put a point beside a ROM that already exists**, copy the ROM to a new folder and copy the point
in beside it, named to match the ROM. Never drop a save next to a ROM whose existing save holds real
progress, and never overwrite a save.

---

## What these are, and what they are not

- **A preset builds a level 40 test save.** It is a test point, not a real playthrough. The party is
  maxed, so it answers "does this scene run" and never "is this fight fair".
- **Keeping a real playthrough means keeping a binary**, because no recipe reproduces it. Where to
  back that up is the owner's call. Today it would live in `points\` and nowhere else.

## Battery saves against emulator save states

| | `.sav` | `.ss1`, `.ss2`, ... |
|---|---|---|
| What it is | the game's own battery save | a snapshot of the whole machine |
| Moves to another build? | **Yes.** Every build is the same game, so flags, maps and party carry over. | **No.** It is tied to one ROM image. |
| Can capture mid-scene? | No. Only where the game lets you save. | Yes, any frame. |
| Where it belongs | here, in `points\` | beside its own ROM, with the build recorded |

A save state is the only way to capture the middle of a cutscene, which is why they are worth
keeping. They are not interchangeable with a `.sav` and must never be filed as if they were.
`scripts\permanent\rom\state_dump.py` reads one.

---

## Known gap

Some points exist only as binaries, scattered in `builds\variants\`, with **no preset behind them**:
`_spar`, `_scouter` and `_computer`. Each was reached by building a whole variant ROM per revision,
which is the waste this folder exists to end. Giving each one a preset is the next step, and it is
the same job `chamber_exit` just went through: read the save, extract its flags, add the preset.

Until then those three live on one disk, like everything else here did.
