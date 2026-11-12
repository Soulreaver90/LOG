# Scene recipes: copy vanilla, do not invent it

Read this before writing a single scene op. Every recipe names the vanilla record to copy and the command
that lists the alternatives. Seven arena builds went out in one day because none of this was written down.

> **The rule this page exists to enforce:** count the population before copying an example. "Vanilla does
> it this way" needs a number. One matching record is not evidence.

## The five indexes

| Question | Command |
| --- | --- |
| What does ext op N do? | `docs\research\scene-vm-ext-ops.md` |
| Who uses op N, with what arguments? | `py -3.14 -P scripts\permanent\scene\op_usage.py --op N` |
| Which scenes do X? | `py -3.14 -P scripts\permanent\scene\scene_index.py --does fight` |
| What is on map Z,A? | `docs\research\map-index.md` |
| Where does this map's doors go? | `py -3.14 -P scripts\permanent\scene\warp_graph.py --from 6,1` |

---

## Recipe: start a fight

**Copy `rom:0x3E47DC`** (map 11,4, Piccolo against Android 17). The whole record is four ops:

```
ext104(enemy_set, item_index) ; bar_set(enemy_set, lo, hi) ; header_bit1(1) ; camera_follow(0)
```

**No fade. No map load. No wait.** Of the 35 records that raise a boss bar, exactly **1** also loads a map.
Of the 17 scenes that convert an NPC into an enemy, only 2 load a map and only 1 opens a fade at all. A cover at a fight start is the rarest shape in the game.

The smooth camera pan comes free: park `camera(x, y, speed)` earlier in the conversation, and
`camera_follow(0)` glides from that fixed point to the player.

`ext 104` is `Sprite_ReplaceWithEntry`. It takes the conversation NPC by set, reads its position and
facing, destroys it, and respawns from the map's item list **through the item's own factory**, so the new
enemy keeps the death event its item names. The item's condition is never tested on that path.

List the other 16: `scene_index.py --does fight`.

## Recipe: load a map in the middle of a scene

45 scenes do it. 62 records load a map, and **whether they carry a fade depends entirely on which load
op they use**. Counted per record, with the cover required BEFORE the load:

| op | builds a player? | sites with a cover | sites without | reading |
| --- | --- | --- | --- | --- |
| `ext 35` | **no** | 1 | **12** | carries its own fade |
| `ext 38` | yes | 12 | 17 | mostly its own fade |
| `ext 39` | yes | **28** | 1 | **no fade of its own: you must add one** |

So: using `ext 39`, write `fade_out(n)` before it and `fade_in(n)` after. Using `ext 35`, do not. That
matches what the handlers say, from a completely separate line of evidence.

Only `ext 38` and `ext 39` reach the player constructor. **`ext 35` builds no player at all**, and a bible
row claiming otherwise cost a whole build. `ext 39`'s x and y are the PLAYER's position; `ext 35`'s are not.

## Recipe: make the player a transformed character

`ext 73 (character, set)` then `push character ; ext 70`, **in that order, before a map load**. The load is
what builds the body. `appearance_revert` skips the record whose index equals the leader byte that
`set_leader` has just written, so the form survives its own leader change.

Only 9 scenes change a form. List them: `scene_index.py --does form`.

## Recipe: address the player in a conversation

Set 0 means the player in every actor op **except `ext 51 spawn`**, whose handler calls `npc_factory` and
never looks an actor up. So a conversation can be moved onto the player by repointing `face`, `walk`,
`attack`, `pose`, `move_to` and `face_target` to set 0, but a `spawn` must be deleted, not repointed.

Careful: `remove(set)` + `spawn(set)` next to each other is **one transformation**, not two ops. Deleting
half of it leaves nobody on screen.

## Recipe: copy a map as a template

A map carries things in more places than the entry's lists. Copying an entry and emptying its region and
item lists leaves all of this behind:

| What | Where | How many maps have it |
| --- | --- | --- |
| Doors | **layout** `+0x40` count, `+0x44` pointer list | 283 |
| Props (save point, signs, posts) | **layout** `+0x24` count, `+0x28` entries | 194 |
| Collision | layout `+0x34` | all |
| Music | entry `+0x24`, a song id **or a script** | 230 literal, 62 scripted |

Nine doors in ten are in the layout list, not the region list. If you delete a door, **close its collision
cells**, because in vanilla the warp is what stops the player walking into the wall behind it.

## Recipe: give or take an item

`push N ; ext 26` gives item N. `ext 76` takes one, `ext 77 (n, k)` takes k, `ext 21` pushes the count.
There are exactly **50 items, 0 to 49**; 46-49 are unused placeholders. Names: `docs\research\item-index.md`.

## Traps that have each cost a build

1. **A map load is a camera hand-back and it never eases.** A jump at a load is an uncovered load, not a
   missing camera op. The fix is a cover, or moving the load.
2. **`r0` is not the VM stack after the first `BL`** in a handler. Do not count pops across a whole body.
3. **A predicate op leaves its result on the stack** (depth unchanged) so `jz` can read it. ext 19 is one.
4. **ext 0-16 and 131-133 are getters**: zero arguments, they push a value.
5. **`ext 87` and `ext 92` are the same op**, one handler under two numbers.
6. A tool that hardcodes a base-ROM table address reads the dead table in a build, silently.
7. **Ask a table for its length with `scene_lib.table_length()`, never `table_end()`.** An END entry is
   an ordinary table word carrying a resume index, not a terminator, and tables interleave them. The
   first-END rule truncated 229 of 303 tables. Fixed 2026-11-07, and `table_end()` is kept as a floor.
8. **A record pointer is not only a word in the script region.** A build moves records into the
   expansion area `0x800000` to `0xF00000`, so a walker that checks only `0x3B0000` to `0x420000` reads
   a BUILD short and says nothing. Our own module tables were the worst victims: a copied table's first
   END entry can sit at index 2 of 33.