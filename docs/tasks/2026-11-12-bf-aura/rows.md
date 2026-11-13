# Bible rows: Buu's Fury power-up aura

## Section 4

| Fact | Tags | Confidence | Source | Id |
| --- | --- | --- | --- | --- |
| Buu's Fury power-up aura: three 32x32 effect records at `rom:0x752D28` + 12 k, pixels `rom:0x752128`, `0x752528`, `0x752928`, `attr0=0x2000` (8bpp) `attr1=0x8000`, `dx=16` `dy=31` (bottom centre, the character's own anchor). Colours are BF OBJ indices 5 `#F8F800`, 29 `#F8F890`, 30 `#F8F8D8`, 110 `#F8D000`. Exported to `art\transformations\_buus-fury-reference\aura\` | #sprite #object | C (pixels rendered, fields decoded) | BFA | |
| The aura is an EFFECT RECORD (B1768 format), not a sprite set, so every sprite-set sweep of Buu's Fury misses it. The 41 BF sets holding 64x64 frames are all characters and bosses: a contact sheet of one frame each holds no effect | #sprite #object | C (contact sheet viewed) | BFA | |
| Effect record pixels are in GBA 8x8 tile order, 64 bytes a tile, tiles row major, because they go to OBJ VRAM unchanged. Read linearly they render as horizontal stripes of the right colours, which is what a wrong reader looks like here | #codec #sprite | C (both readings rendered) | BFA | |
| Effect record sweep of the Buu's Fury ROM: 7136 offsets pass the field test at 32x32 or larger, and 13 runs survive the list test (3 or more records, one size, pixel blocks adjacent). The 13 are dust clouds, energy balls, flame bursts and the aura. The field test alone is 99.4% noise | #sprite #tool | C (counts), L (a one record effect, or a run of two, is outside this shape) | BFA | |
| Only 1 of the aura's 4 colours is in the LoG II OBJ palette: `#F8F800` at index 8. `#F8F890`, `#F8F8D8` and `#F8D000` are absent, so the gold aura needs palette work before it can be built | #palette #sprite | C | BFA | |
| The aura draws ABOVE the character (owner, 2026-11-12): he animates inside it and the aura does not move with him, which is why it holds during the Buu's Fury screen shake. Drawn behind, the pale inner ring reads as a halo instead | #sprite #decision | L (owner's eye on the mockups) | BFA | |
| `scripts\one-time\2026-11-12-bf-effects\bf_effect_records.py` (whole-ROM effect record sweep, list test, contact sheet), `aura_zoom.py` (one region big, with record fields), `aura_export.py` (frames, loop GIFs, palette report, mockups over his own frames in gold, white and blue tinted white) | #tool | C | BFA | |
