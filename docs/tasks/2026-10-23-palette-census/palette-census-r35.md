# OBJ palette census on r35: which of the 256 indices are never drawn (final, 2026-10-23)

Personal GBA ROM hack (Legacy of Goku II, USA). Build: `builds\log2_poc_r35.gba` (SHA-1 `736c778a1d576a86143d052e8af7847fd10bbf50`).

## My ask

"100% confirm which ones are not being used. I will not accept uncertainty." I want a free OBJ palette slot to recolor to a darker green for the Super Perfect Cell portrait. A slot is free only when no graphic the game can show on the OBJ layer holds that index, directly or through a remap or tint table.

## Prior work to re-run, not trust

The r21 palette study found 10 clean indices (3, 7, 86, 94, 103, 172, 174, 178, 216, 218). Map props then showed 3, 86, 94, 216. 172 became the portrait skin color. So on r21 the candidates were 7, 103, 174, 178, 218. Builds r22 to r35 added sets, portraits, code and palette changes since then, so the r21 result is not proof for r35.

- Bible: `docs\RE-BIBLE.md` section 5 (rows tagged PSL, EFX, PLU) and section 5a (portraits). Read all of section 5 first.
- Tools: `scripts\one-time\2026-10-19-palette-slot\p0_*.py` to `p11_*.py` (census, remap tables, OBJ sources, DMA, test copy) and `scripts\one-time\2026-10-20-effects-trace\e*.py` (OBJ VRAM writers, layouts, props, items, expansion code). Their constants were set for r21; check each one against r35 before you reuse it.
- Sprite tools: `scripts\permanent\rom\log2_sprites.py`, `webfoot_decompress.py`. A quick main-loop scan is `scripts\one-time\2026-10-23-palette-census\palette_use\scan_sets.py` (vanilla set table only; it may miss relocated or added tables).

## Task

For every index 0-255, decide USED or NEVER DRAWN on r35, with evidence. Cover every path a pixel can take to the OBJ layer:

1. Sprite sets: the union of set offsets from every reader (vanilla table, any table copy or relocation in r35, appearance entries, script set args, map object fields, scouter +8, hand-built sets 157-159 and the r30 aura set 58). Use two independent search shapes and reconcile the counts. Decode every frame and apply every remap the set uses.
2. Dialog portraits: every live portrait block entry on r35, including remastered ones and id 52. Prove whether status portraits use the BG palette and are out of scope.
3. HUD, ability and Z2 icons, raw effect tiles, and every OBJ VRAM writer. Re-verify that r22-r35 code added no new OBJ VRAM writer.
4. Remap and tint tables (dim, gray, red and the others at `rom:0x6D0DD0`-`rom:0x6D1BCF`): any index a displayed index can turn into is USED.
5. Map props and layouts.
6. Any text or font drawn on OBJ.
7. Empirical cross-check: scan OBJ VRAM (8bpp tiles) and OAM in every save state file under `scratch\` (all builds) for each candidate index. Report how many states you scanned and from which areas.

## Report

Save `docs\tasks\2026-10-23-palette-census\palette-census-r35-report.md`:
- A table of the candidate indices (and any new ones you find) with each path's result and its evidence (file:line, counts, tool output path).
- The final NEVER DRAWN list.
- Residual risk, stated plainly: any path you could not close, with what would close it. Do not round a gap up to "unused".
- Bible rows in `scripts\one-time\2026-10-23-palette-census\bible_rows.md` (tag PCN, Section 5), in the format of `scripts\one-time\2026-10-23-r35-build\bible_rows.md`.

## Limits

- Read-only on every ROM, save and state. No build. Never write under `data\`. Work files in `scripts\one-time\2026-10-23-palette-census\`.
- Python: LF, no byte order mark, no em or en dashes. `py -3 -P`. Never `cd`; absolute paths only. Write and edit files with the Write and Edit tools.
- I am editing `art\base-audit\` and `scripts\one-time\2026-10-23-base-audit\`; do not touch them.
- Label every finding CONFIRMED, LIKELY or SPECULATIVE.

