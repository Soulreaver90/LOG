# Brief: name the disassembly functions we actually use

## Why

On 2026-11-05 every function that cost real debugging time was unnamed, and each had to be read
cold: `sub_0800A680` (the leader change), `sub_080086D4` (the player sprite constructor),
`sub_08008952` (the player object message handler), `sub_0800AAC6` (ext 104), `sub_08009D00`
(ext 52), `sub_08009852` and `sub_08009A88` (two of the three map ops).

203 of 1249 functions are named. 1046 are still `sub_<address>`. Naming the subsystems this
project actually touches is the single highest leverage thing available, and unlike art it can be
VERIFIED without the owner: the repo rebuilds byte exact.

## Scope, in priority order. Do NOT try to name all 1046

1. **Scene VM op handlers.** The ext handler table is at `rom:0x3B5D28`, 4 bytes per entry, and the
   base op table at `rom:0x3B5C00`. Every entry points at a handler. Name the handlers for the ops
   this project uses, which are listed with their current names in
   `C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\scripts\permanent\scene\scene_lib.py`
   in its op tables. That file is the naming hint, NOT evidence: confirm each from the handler.
2. **Sprite and actor handling**, the `0x08006xxx`-`0x08009xxx` cluster: selection, directories,
   spawn, remove, find by set, position and facing.
3. **Map loading**, around `sub_0800C584`, `sub_0800C664`, `sub_0800E0AC` and the three map ops.

Stop when you run out of confident names. Quality over count. A wrong name is worse than
`sub_<address>` because it will be trusted.

## Known-good names to apply, already CONFIRMED on 2026-11-05

Apply these first, they are settled and each is backed by the disassembly:

| Address | Proposed name | Evidence |
|---|---|---|
| `0x080086D4` | player sprite constructor | allocates 0x1A0 via `@0x0801F08C`, writes its vtable, `STR r4,[0x03001FA8]`, then builds the body from the party roster and loads graphics via `@0x08021D2C` |
| `0x08008952` | player object message handler | message 9 does `STR r4,[0x03001FA8]`, message 8 stores 0 there; both first call `@0x08021D2A` on the leader's definition |
| `0x0800A680` | leader change core | `STRB r4,[roster+0]` always; the appearance block behind `CMP r4,#0` / `BEQ` calls `Sprite_ObjectDirectory` and does `STR r0,[r4,#0x48]` |
| `0x08009D00` | ext 52 remove, DEFERRED | allocates 8 via `@0x0801F08C` and hands the job to `@0x0800E04C` |
| `0x0800AAC6` | ext 104 build item as enemy | reads the NPC position via `@0x0800791A` and facing from `[actor+0x10]`, destroys it via `@0x080068CA`, spawns the item via `@0x0800C75C` |
| `0x08009852` | ext 35 load_map | opens `MOV r1,#0x40` into `@0x0802664C`, then `@0x0800C664` |
| `0x08009A88` | ext 39 load_map_at | same five args, no fade path, calls `@0x0800C584` |
| `0x0800E0AC` | map entry count getter | `MOV r0,#0xFF ; ADD r0,#0x48 ; BX lr` = 327 |
| `0x0800AB82` | ext 86 HUD show/hide | into `@0x080040AA`, which toggles bit 1 of a flag byte and creates a kind 18 object |

Use the repo's own naming style, not these words verbatim.

## Rules

- Repo: `C:\Users\josephgonzalez\Documents\GitHub\legacyofgoku2-disasm`. Clean tree, on `master`.
- **Work on a local branch. `git -C <repo> checkout -b naming-2026-11-05`. NEVER push.**
- Read `docs\NAMING.md` and `docs\DEFINITION_OF_DONE.md` in that repo FIRST and follow them exactly,
  including the evidence class each name must carry in `docs\CODE_INDEX.md` and any ledger the repo
  keeps (`tools\code\NAMING_LEDGER.csv`).
- **The rebuild must stay byte exact.** Run the repo's own `check.cmd` (or its documented
  equivalent) before you start, after your first batch, and at the end. If it ever fails, stop and
  report; do not keep going.
- Commit on the branch in small batches with clear messages, so a bad name can be dropped.
- Absolute paths only. Never `cd`, `Set-Location` or `Push-Location`.
- No em dashes or en dashes. No byte order mark.
- Never put a Windows path inside a `python -c` argument or an executed shell heredoc: on this
  machine a quoted heredoc collapses backslashes and Python then reads `\t`, `\r` and `\2` as
  escapes. Build paths from forward slashes or `chr(92)`.
- Never pipe a test or check run into `tail` or `head`: the pipe reports the pipe's exit code.

## Report

Write `C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\docs\tasks\2026-11-05-disasm-naming\report.md`:
the branch name, how many functions you named, the byte-exact check result with the exit code you
observed, and a table of every name with its address and evidence class. Label anything you were
unsure of and LEFT unnamed, so the next pass starts there.

One report message, then stop. Do not add a byte order mark.
