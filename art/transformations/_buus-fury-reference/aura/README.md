# Buu's Fury power-up aura

The aura Buu's Fury draws around a character while he powers up. It is Webfoot's own art, exported
from the Buu's Fury ROM by `scripts\one-time\2026-11-12-bf-effects\aura_export.py`.

## Where it lives in the ROM

| Thing | Value |
|---|---|
| Records | `rom:0x752D28`, `rom:0x752D34`, `rom:0x752D40` |
| Pixels | `rom:0x752128`, `rom:0x752528`, `rom:0x752928` |
| Size | 32x32, three frames |
| Format | 8bpp, GBA 8x8 tile order, `attr0=0x2000` `attr1=0x8000` |
| Anchor | `dx=16`, `dy=31`: bottom centre, the same anchor the character uses |
| Colours | BF indices 5 `#F8F800`, 29 `#F8F890`, 30 `#F8F8D8`, 110 `#F8D000` |

The aura is an **effect record**, not a sprite set. That is why every sprite-set sweep missed it.
RE-BIBLE row B1768 holds the 12-byte record format: `{s8 dx, s8 dy, u8 w, u8 h, u16 attr0, u16 attr1,
u32 pixels}`.

## Layering

The aura is its own object drawn **above** the character. The character animates inside it, and the
aura does not move with him, which is why it still reads correctly during the Buu's Fury screen shake.

## Files

| File | What it is |
|---|---|
| `frames\01..03_bf_aura.png` | the three frames, exactly as the ROM holds them |
| `frames\01..03_bf_aura_white.png` | the white recolour |
| `frames\01..03_bf_aura_blue.png` | the blue tinted white recolour |
| `aura_gold.gif`, `aura_white.gif`, `aura_blue.gif` | the loop, 133 ms a frame |
| `mockup_vegeta_gold.png` | the gold aura over the approved Vegeta frames |
| `mockup_piccolo_white.png` | the white aura over the approved Piccolo frames |
| `mockup_piccolo_blue.png` | the blue tinted white aura over the same frames |

Each mockup sheet shows his own frames on the top row and the aura over them on the bottom row.

## Porting note

Only one of the four colours is already in the LoG II OBJ palette: `#F8F800` at index 8. The other
three need palette work before the gold aura can be built. Both recolours were chosen from entries
the LoG II OBJ palette already holds, so either one is buildable as drawn.

Piccolo takes the **white** aura and Vegeta the gold (owner, 2026-11-12). The blue tinted white is
kept only as the rejected comparison.

| Original | White (Piccolo) | Blue tinted white (rejected) |
|---|---|---|
| `#F8D000` | `#909090` | `#78A0A8` |
| `#F8F800` | `#C0C0C0` | `#A8B8E0` |
| `#F8F890` | `#E0F8F8` | `#C8D0F8` |
| `#F8F8D8` | `#F8F8F8` | `#E0F8F8` |

## Provenance

The owner was shown this aura by other modders. It was found independently in the Buu's Fury ROM, and
the three frames match that image. Nothing here comes from another modder's work.
