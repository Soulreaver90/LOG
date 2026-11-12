# One bible, one reader per section

**Decided:** 2026-11-06, by the owner, after a day in which the bible held three answers I then spent hours
rediscovering.

**Status:** agreed in principle. `whatis.py` already implements it for sections 1 and 14. The map reader is
the next one to build.

---

## The problem, measured

`docs\RE-BIBLE.md` is **1943 rows and 775 KB**. It is correct. It is also unsearchable by eye, and grep finds
a row only if you guess the word the row happens to use.

Three times on 2026-11-06 the bible already carried the answer and I did not find it:

| What I "discovered" | Where it already was | Cost |
|---|---|---|
| A map's warps live in `layout +0x40` and `+0x44` | **row 708**, written before the task, naming both fields and the `{dir, zone, area, var, x, y}` shape | most of a day, two wrong answers to the owner, one wasted agent brief |
| Collision is `byte cy*32 + (cx>>3)`, `bit cx&7`, 256 cells a row | **rows 1095 and 1721** | a verifier that reported the open doorway as fully closed, twice |
| `obj+0x48` is a set POINTER, not a set id | **row 105** | four actors read as unidentifiable, sets printed as 5876 and 40120 |

Row 708 is the clearest case. It is filed under regions, so it reads like a region row, and a grep for
"warp" returns 31 rows while a grep for `+0x40` returns 171.

> The bible worked. **Retrieval failed.** Writing the fact down a second time would not have helped.

## The decision

1. **Keep one bible. Do not split it.** It is the single source of truth and it was right every time.

2. **Build one READER per section, and make the reader the normal way to ask.** The reader is how a fact
   gets out of 1943 rows, the way `whatis.py` already is: nobody greps the bible for a function, they ask the
   tool.

3. **A reader holds no copy of a ROM fact.** It reads the addresses the bible row names and prints what the
   ROM actually holds. The row stays the truth and the tool stays the reader, so the two cannot drift into
   two different answers. A reader that caches a value becomes a second source of truth and is the thing this
   decision exists to prevent.

4. **A reader must resolve live structures, never hardcode them.** `map_view.py` and `scene_probe.py` both
   hardcode the map table at `0x409368` with 327 entries, so pointing either at a build reads the stale
   vanilla table and silently misses every appended map. Resolve from the literal at `rom:0xEBD8`.

## The readers

| Bible section | Reader | State |
|---|---|---|
| 1 How to search, 14 Engine map | `rom\whatis.py` | **built.** Answers an address, a RAM word, a function or a term, from `CODE_INDEX.md`, `RAM_LEDGER.csv` and the bible |
| 9 Maps | *(none)* | **the gap.** Nothing reads a map end to end, which is why the arena shipped three times with inherited doors |
| 4 Sprites, 5 Palette | `rom\rom_sheet.py`, `sprite_look.py`, `sprite_stats.py`, `sprite_guard.py` | built, several tools rather than one reader |
| 8 Story and script | `scene\scene_probe.py` | built, but it stops one pointer short of a map's real doors |
| 7 Save format | `rom\log2_save.py` | built |

### Next: the map reader

Extend `scene_probe.py --map`, do not write a third tool. `docs\tool-index.md` already lists two tools for
this surface and a third would be the failure this project keeps repeating.

One command, any of the 327 maps plus any appended one, printing:

- the entry fields BY NAME: banner `+0x0C`, music `+0x24` and whether it is a song id or a script,
  region count `+0x03` and list `+0x10`, item count `+0x04` and list `+0x14`, enter `+0x30`, leave `+0x34`
- the layout chain, per variation
- **BOTH door carriers, decoded, side by side**: the region list AND `layout +0x40`/`+0x44`, each with its
  destination map and landing spot
- the collision frame address, its container type, and open/closed counts
- the BG layer records

The arena bug would have been line one of that output.

## How this is enforced

`CLAUDE.md` already carries the two steps. They are correct and they were not followed:

> 2. Search `docs\RE-BIBLE.md` before you search the ROM. It indexes every known ROM fact.
> 3. Search `docs\tool-index.md` before you write any script. A tool almost always exists.

The addition this decision makes: **for a map fact, run the map reader before you grep the bible.** A reader
cannot be skimmed past the way a row can.

## Related

- `docs\tasks\2026-11-06-arena-fixes\warp-search.md`, how the warp carrier was found the slow way
- `docs\tasks\2026-11-06-arena-v3\report.md`, the agent that found row 708 independently
- bible rows tagged `WRP`, `ARN2`, `ARN3`, `ARN3B` and `ARN4`
- `docs\ledger\progress.md`, the 2026-11-06 entries
