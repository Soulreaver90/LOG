# Data index

This page lists what is in `data\` and what each item is good for. Everything under `data\` is supplied by me and read-only.

## Folders

| Folder | What it is | Use in the merge |
|---|---|---|
| `roms\` | LoG II USA (base), LoG II Europe, Buu's Fury USA, mGBA states and the cheat file | Base ROM and references |
| `reference\` | Portrait sheets (`122601.png` International, `38248.png` USA), gi reference art, prototype Super Vegeta and Super Trunks | Portraits and art direction |
| `sprites\` (sheets) | Ripped sheets for LoG II and Buu's Fury characters, HUD, items and fonts | Art reference |
| `sprites\Buu_Fury_Character_Sprites\characters\` | 232 Buu's Fury character folders, one PNG per animation (`stand`, `walk`, `run`, `attack1-4`, `transform`, `flying`, `portrait` and others). From the LoG modding Discord (final, 2026-10-17) | Buu's Fury sprite ports, Super Saiyan 2 hair reference |
| `Inferred\all\bank-000` to `bank-186` | Buu's Fury tileset atlases: per bank a raw and an inferred tile layout plus `atlas.json` (profile `buus_fury_usa_rev0_01c1707f`, bank table `0x08179764`, 187 banks, 452 maps) | Moving Buu's Fury maps to the LoG II engine |
| `Sound\` | WAV sound effects: 62 Buu's Fury, 71 LoG II, 111 from another Webfoot game (`dbgt_t`, likely DBZ GT Transformation) | Sound effects for new moves and forms |
| `items\` | Buu's Fury item catalogs as JSON (equipment: body, hands, feet, accessories; story items; supplies) with icon sheets | The equipment slice (Buu's Fury part only) |

## Buu's Fury Gohan sets

| Folder | Look |
|---|---|
| `Gohan` | Teen Gohan, school outfit (white shirt, black vest) |
| `Gohan 2`, `Gohan 3` | Armored Gohan with the Z Sword (7 and 6 files) |
| `Gohan 4`, `Gohan 9` | Gohan in an orange gi (like Goku's) |
| `Gohan 5` | Great Saiyaman (helmet, cape) |
| `Gohan 6` | Great Saiyaman outfit without the helmet |
| `Gohan 7` | **Super Saiyan teen Gohan, school outfit** |
| `Gohan 8` | **Super Saiyan teen Gohan, Saiyaman outfit** |

`Gohan 7` and `Gohan 8` show older teen Gohan's Super Saiyan hair in the Buu's Fury style. I ruled them out as the hair target (2026-10-17): Cell saga Gohan has much fuller hair. The Super Saiyan 2 target is the fan mod look plus my reference images.

The folder names are the ripper's. The looks above come from a contact sheet of each set's `stand.png` (me, 2026-10-17).
