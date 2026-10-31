# Research 2: status screen bonus bars and stat points (read only)

Design section 4 and slice 2 (`docs\design\2026-10-16-log-merge-design.md`): the status screen shows a form's bonus as a gold part of each stat bar, as the Europe ROM does. Slice 2 also adds Buu's Fury style stat point assignment. I asked to look at the Buu's Fury stat screen look. This is research only. Do not build a patch or a ROM.

## Scope

- LoG II USA (base ROM) and LoG II Europe (`data\roms\Dragon Ball Z - The Legacy of Goku II (Europe) (En,Fr,De,Es,It).gba`, SHA-1 in RE-BIBLE): code reverse engineering is allowed. Ghidra headless works through `scripts\one-time\2026-10-16-task-5-gi-art\gh.sh`.
- Buu's Fury: no code work (Ruling 34). Use only images: `data\sprites\...Buu's Fury - Miscellaneous - HUD.png` and any status screen art you find as data with the frame codec.

## Questions

1. **USA status page.** Map the routine at 0x0800379C: what it draws, where each stat bar comes from (base stat u16 at 0x03000EA6/A8/AA, value / 256), the bar tiles and palette, and the text. Label each fact.
2. **Europe bonus display.** Find the matching routine in the Europe ROM. Diff its logic against USA. CONFIRM how it gets the form bonus (live stat at player +0x160-0x162 minus base?) and how it draws the gold segment (tiles, palette index). List what a port to USA needs: code size, new tiles, palette entries (the shared OBJ palette must not change; BG palettes may have free slots, CONFIRM).
3. **Stat points.** Find where level-up adds stats in USA (the code that raises 0x03000EA6-AA). Say where a "points to assign" counter could live without changing the save format (Global Constraint), or say plainly that it needs a save field, and what that costs.
4. **Buu's Fury look.** From the images, describe the Buu's Fury status and stat-assignment layout. Say which parts fit LoG II's screen and which do not.
5. **Plan.** A short slice 2 outline for the status screen work: tasks, order, risks, and what I must decide.

## Output

- `docs\research\research-status-screen.md`: findings with CONFIRMED, LIKELY or SPECULATIVE labels and the slice 2 outline.
- Screenshots or crops you make go to `scripts\one-time\2026-10-17-status-screen-research\`.
- RE-BIBLE lines for new facts (`game:log2eu` for Europe facts). LF line endings.

Never write under `data\`. Install nothing.
