# Tooling pass: stop retracing our steps (final, 2026-10-30 9:55 PM)

Me: "Let's create tooling, stop retracing our
steps, let's make use of what we learned, what we have built and the disassembly code to make things easier and
automate."

Read `scripts\permanent\` (the tools and `patches\`), `scripts\permanent\disasm\` (symbols, code map, listing), the
test interpreter the tests use, and the bible sections on the scene VM, ext ops, map items and saves. Skim the
`scripts\one-time\` probe scripts of the last two weeks (`s1`-`s5`, `c4s_`, `c4b_`, `c4v_`, `v7_`, `fadefix_`) to see
what each study rebuilt by hand.

## Task

1. **`scene_lib.py`** (permanent): one place for the scene VM.
   - Encoder and decoder: push, push lists (varint, doubled values), ext ops, end, jumps, text records, record headers.
   - Named ext ops from the bible and the disassembly (spawn 51, remove 52, fly 54 and 121, walk 53 and 136, pose 57,
     flash 42 and 43, sound 46, wait 69, camera 31, map load 38 and 39, bar 85 and 90, card 145, leader 70, and the
     rest the bible names), each with its argument names. Unknown ops stay usable by number.
   - Table walker with the stray-word trap, record namers ("which words name this record"), and one safe
     copy-and-redirect helper that refuses a second namer.
   - Move the existing modules' copies onto it (the encoders now in `piccolo_gi_scene.py`, `relocate` in `npc_gi.py`,
     and the per-module copy code). **Proof: every build list rebuilds byte-identical** (main r40 and every trial list),
     and the full suite passes.
2. **`scene_probe.py`** (permanent CLI): print any table, record, map item or map's scene items as a readable listing
   with op names, text and namers. Also "find where text X is used" and "which tables run on map M".
3. **`map_view.py`** (permanent CLI): render a map (BG layers, collision, items, warps) with optional planned actor
   positions, to a PNG. Reuse what the card 4 v9 task built (`c4v_` scripts).
4. **Story-point saves**: a `log2_save.py` command that makes a slot at a named story point (flags, map, position,
   leader, party) from a small preset table, with the known traps (visited bits, leader forcing) built in.
5. **Scene test harness**: a helper the tests can call to run a record or table in the interpreter and report the ops
   run, spawns, positions and flags set.
6. **`docs\playbooks\scene-playbook.md`**: one page: how to add or change a scene with these tools, the traps, and the
   test pattern. Briefs will point to it.

## Report

Short: `docs\tasks\2026-10-30-tooling\tooling-report.md`. SHIPPED and PENDING tables, each tool with one usage line,
the byte-identical proof (list, SHA-1 before and after), suite count. Bible rows (tag TLS, a few) in
`scripts\one-time\2026-10-30-tooling\bible_rows.md` as `## Section N` table blocks.

## Limits

- No module may change its output: byte-identical rebuilds are the gate. If a refactor would change a byte, keep the
  old code for that module and report it.
- Python: `py -3.14 -P`. Base ROM: `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba`. Never write under
  `data\`. Never overwrite a ROM, save or state. LF, no em or en dashes.
- Never `cd`, `Set-Location` or `Push-Location`. Use absolute paths in every command and in every script that opens a
  file. Do not touch `docs\RE-BIBLE.md`, `docs\ledger\` or `LOG\zhack\`.
- Work lean: build what the next scenes need, not every possible feature.

