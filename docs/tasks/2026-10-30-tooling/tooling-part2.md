# Tooling part 2: scene_lib and the scene tools (approved 2026-10-30 9:57 PM)

This is `tooling.md` items 1, 2, 3, 5 and 6, plus
its rebuild gate. **Item 4, story-point saves, and `scripts\permanent\rom\log2_save.py` belong to another task that is
running now: do not touch either.**

Read `docs\tasks\2026-10-30-tooling\tooling.md` for the full wording of each item, then the modules you will change
and `scripts\permanent\disasm\` for the op names. Search `docs\RE-BIBLE.md` (tags DS8, PGS, CJ2, C4T, CJ8) before you
read the ROM.

## Task

1. **`scene_lib.py`** (permanent): one place for the scene VM. Encoder and decoder for push, push lists, ext ops,
   end, jumps, text records and record headers. Named ext ops with their argument names, taken from the bible and the
   disassembly. Unknown ops stay usable by number. A table walker with the stray-word trap, record namers, and one
   safe copy-and-redirect helper that refuses a second namer. Then move the existing copies onto it: the encoders in
   `piccolo_gi_scene.py`, `relocate` in `npc_gi.py`, and the per-module copy code in the scene modules.
2. **`scene_probe.py`** (permanent CLI): print any table, record, map item or map's scene items as a readable listing
   with op names, text and namers. Plus "find where text X is used" and "which tables run on map M".
3. **`map_view.py`** (permanent CLI): render a map (BG layers, collision, items, warps) to a PNG, with optional
   planned actor positions. Reuse the card 4 `c4v_` and `c4w_` scripts rather than writing new geometry code.
4. **Scene test harness**: a helper the tests can call to run a record or table in the interpreter and report the ops
   run, spawns, positions and flags set.
5. **`docs\playbooks\scene-playbook.md`**: one page. How to add or change a scene with these tools, the traps, and the
   test pattern.

## The gate, and it is absolute

**No module may change its output.** Every build list must rebuild byte-identical: main `build_list.txt` to
`14d6b831`, and every `build_list_trial*.txt` to the SHA-1 its current ROM in `builds\mockups\` already has. Build to
a scratch path and compare; never overwrite a ROM. If a refactor would change one byte, keep the old code for that
module and report it. The full suite must pass.

Current trial SHA-1s to match: chapters `1bb86930`, Cell Jr `db015ae8`, gi base `d012a9f4`, Vegeta 19 `0598a127`.

## Report

Short. `docs\tasks\2026-10-30-tooling\tooling-part2-report.md`: SHIPPED and PENDING tables, one usage line per tool,
the rebuild proof as a list of (list, expected SHA-1, built SHA-1), the suite count, and every module you could not
move onto `scene_lib` with the reason. Label claims C, L or S. Bible rows (tag TLS) as `## Section N` table blocks in
`scripts\one-time\2026-10-30-tooling\bible_rows.md`.

## Limits

- You may edit the patch modules, their tests, and create the new tools. **Do not touch `log2_save.py`,
  `scripts\permanent\emu\`, any build list's module lines, `docs\RE-BIBLE.md`, `docs\ledger\`, `zhack\` or `data\`.**
- Never overwrite a ROM, save or state: build to a scratch path. Python: `py -3.14 -P`.
- Never `cd`, `Set-Location` or `Push-Location`. Use absolute paths in every command and in every script that opens a
  file. The last three tasks broke this rule. Do not repeat it.
- Work lean: build what the next scenes need, not every possible feature.

