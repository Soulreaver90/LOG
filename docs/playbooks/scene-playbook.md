# Scene playbook

How to add or change a cutscene in LOG with the scene tools. One page. Briefs point here instead of restating it.

Python is `py -3.14 -P`. Absolute paths everywhere.

---

## The tools

| Tool | What it is for |
|---|---|
| `scripts\permanent\scene\scene_lib.py` | The scene VM: encode, decode, walk a table, name records, copy and redirect. Import it. |
| `scripts\permanent\scene\scene_probe.py` | Read a table, a record, a map or a line. CLI, read only. |
| `scripts\permanent\scene\map_view.py` | Render a map to a PNG, with collision, items, warps and planned actor spots. |
| `scripts\permanent\scene\scene_harness.py` | Run a record or a table in a test and report what it did. |

---

## 1. Read before you write

Search `docs\RE-BIBLE.md` first. It indexes every known ROM fact, and a scene you want is often already there.

Then read the real bytes:

```
py -3.14 -P scripts\permanent\scene\scene_probe.py --map 9,1
py -3.14 -P scripts\permanent\scene\scene_probe.py --table 0x3DBDD4
py -3.14 -P scripts\permanent\scene\scene_probe.py --record 0x3DBD5C
py -3.14 -P scripts\permanent\scene\scene_probe.py --find-text "I feel so weak"
```

`--map` lists the regions, the warps, the talk objects and the group items, each with the table it starts.
`--find-text` gives the record and the words that name it, which is what a copy has to repoint.

> [!NOTE]
> A scene owned through the map 14,3 group factory never appears in a region list. `--map` walks the item
> list too, so it finds those. A tool that reads only talk tables misses them (bible SS3).

---

## 2. Plan the positions on the real map

```
py -3.14 -P scripts\permanent\scene\map_view.py --map 9,1 ^
    --actor 312,400,Piccolo --actor 344,400,Gohan --actor 384,400,Goku ^
    --out <workspace>\scratch\plan.png
```

It prints, per actor, whether the spot is an open or a closed collision cell, and draws the warp and scene
boxes. Look at the PNG yourself before you commit a position to a module.

---

## 3. Write the scene

Import the encoders from `scene_lib`, never from a patch module:

```python
from scene.scene_lib import code, ext, push, text, spawn, walk_to, fade_in, fade_out, set_flag

def scene() -> dict:
    return {
        35: code(36, fade_out(30), spawn(158, 344, 400), fade_in(30)),
        36: text(37, 62, "Piccolo, can I have a new outfit just like yours?"),
    }
```

- `code(next, *ops)` writes a type 0 record, `text(next, portrait, line)` a type 1.
- A named op is exactly `ext(n, ...)`: `spawn(158, 344, 400)` and `ext(51, 158, 344, 400)` are the same bytes.
- An op `scene_lib` does not name still works: `ext(200, 1, 2)` or `call(200, 1, 2)`.
- `scene_lib.EXT_OPS` carries each op's argument names and a C, L or S label. Build only on a C row.

> [!WARNING]
> Every ext op pops the values pushed before it and pushes nothing. End a code record with an empty stack.
> One value left over replaces the next index (`@0x0800B19C`), which silently sends the scene elsewhere.

---

## 4. Copy a vanilla record instead of editing it

Never edit a vanilla record in place when another scene may share it. Copy it, edit the copy, and repoint
the words that name it. The old record stays, so a save paused in the old scene still ends.

```python
from scene.scene_lib import copy_and_redirect

at = copy_and_redirect(rom, alloc, src=0x3DB59C, length=0xCC,
                       namers=[0x3DBDDC],                 # every word that names it
                       edits={0x3DB5D0: ("1d03708d108660", "1d03768d108660")},
                       region=(0x3B0000, 0x420000))       # prove the namer list is complete
```

`copy_and_redirect` refuses a namer that does not name the record, and with `region=` it refuses to run when
a word inside that window names the record and the call did not list it.

> [!NOTE]
> The namer list is explicit on purpose. A built ROM keeps dead namers, and one live record can have two real
> namers: the chamber exit table is named by both type 5 words `rom:0x3CF7E4` and `rom:0x3D1530`.

---

## 5. The traps

| Trap | What goes wrong | What to do |
|---|---|---|
| Stray table word | A small word (`0x2164`, `0x1156`, `0x11`) often sits before word 0. A backward walk reads it as an END and shifts every index by one. | Never walk a table backward. Pass the address an item or an event names. `scene_lib.walk` is forward only; `stray_before` reports one. |
| Value left on the stack | The next index is replaced and the scene jumps. | End each code record with every push consumed. |
| A record that grows | A longer record cannot stay in its slot, and moving it moves every later allocation. | Keep the old slot size (`SLOTS` in `piccolo_gi_scene`), or append at the end of the list. |
| Two numberings | `02 1B` is base op 2 then ext 27. | `BASE_OPS` names the first, `EXT_OPS` the second. |
| A set with no anim | `ext 54` (fly) enters state 12; `set:31` has no anim 12. | Use `ext 53` (walk, anim 1) for a set without the fly pose. |
| `ext 73` on an unnamed set | The appearance assert hangs the game. | The reverse lookup copy must carry an entry naming that set. |

---

## 6. Test the scene

Use the harness. Do not write a second interpreter in a test file.

```python
from scene.scene_harness import run_record, run_table, State

class SceneTests(unittest.TestCase):
    def test_the_gi_scene_spawns_and_sets_the_flag(self):
        run = run_record(rom, at)
        self.assertFalse(run.approximate)          # no value the harness had to invent
        self.assertEqual(run.spawns[158], (344, 400))
        self.assertEqual(run.flags_set, {158})
        self.assertEqual(run.next_index, 32)
```

A `Run` reports `calls`, `ops_run`, `called("spawn")`, `spawns`, `positions`, `removed`, `poses`, `facing`,
`flags_set`, `flags_cleared`, `sounds`, `music`, `lines`, `indexes` and `next_index`.

> [!WARNING]
> `run.approximate` is True when an ext op pushed a result the harness does not model, so a branch taken
> after that point is a guess. Assert it is False in any test that checks a branch.

---

## 7. The gate

A scene change must not change any other module's output.

```
py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list.txt --out <scratch>\main.gba --log <scratch>\log.md
py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent
```

Build every list to a **scratch path**, never over a ROM in `builds\`, and compare the SHA-1 with the one the
current ROM already has. Main `build_list.txt` is `14d6b831`. A trial list matches its ROM in
`builds\mockups\`. If one byte moves and you did not mean it, stop and find out why before you go on.
