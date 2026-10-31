# Research 1: Buu's Fury Goku and Piccolo sprites in LoG II (read only)

My idea (design 6.7): bring the Buu's Fury Goku and Piccolo sprites into LoG II. This is research only. Do not build a patch or a ROM.

## Scope (Ruling 34, me, 2026-10-16)

- No patch to the Buu's Fury ROM and no Buu's Fury code reverse engineering.
- Read-only asset work is allowed: my ripped sheets in `data\sprites\` (Buu's Fury Goku, Goku Super Saiyan, Goku Super Saiyan 3, Piccolo NPC) and, if the LoG II sprite decoder (`scripts\permanent\rom\webfoot_decompress.py`) reads the Buu's Fury ROM's sprite data as data, that too. Do not disassemble Buu's Fury code.

## Questions to answer

1. **Frame inventory.** For LoG II Goku (base, Super Saiyan) and Piccolo (with and without weights), list every (anim, dir, index) key from the ROM sets (find the set ids through the appearance table, `docs\research\re-forms.md`). For each Buu's Fury sheet, list the poses it shows. Map Buu's Fury poses to LoG II keys. Name every LoG II key with no Buu's Fury pose.
2. **Size.** Measure the Buu's Fury frames. LoG II player frames must fit a 1024-byte VRAM slot (32x32 8bpp, Ruling 35, `docs\RE-BIBLE.md`). Count the Buu's Fury frames that do not fit, and by how much.
3. **Color.** Map the Buu's Fury colors onto the shared LoG II OBJ palette at rom:0x1DA6C8 (it must not change). Report the worst color errors per character.
4. **Piccolo.** The Buu's Fury sheet is a non-playable Piccolo. In LoG II, Piccolo is playable, and his transform removes the turban and cape (the weights). List what the Buu's Fury sheet lacks: attacks, the transform, the uncaped frames. Say how big the Buu's Fury cape is against the LoG II frame box.
5. **Option table.** For Goku and for Piccolo, give the options (full port, partial port with LoG II frames kept for missing poses, head-only swap, keep LoG II), each with effort, risk and what the player would see.

## Output

- `docs\research\research-bf-sprites.md`: findings with CONFIRMED, LIKELY or SPECULATIVE labels, the inventory tables, the option table and a recommendation.
- Contact sheets in `scripts\one-time\2026-10-17-bf-sprites-research\`: each Buu's Fury pose next to the matching LoG II frame at 4x, with the 32x32 box drawn.
- RE-BIBLE lines for new facts (tag `game:bf` where a fact is about Buu's Fury). LF line endings.

Never write under `data\`. Install nothing.
