# Research notes

Facts gathered before the ROM review. Each item keeps its source and its trust level.
"Unverified" means: confirm in the ROM or in mGBA before building on it.

---

## ROM inventory (read by `scripts\permanent\rom\rom_info.py`, 2026-10-16)

| File | Code | Size | Save type | SHA-1 |
|---|---|---|---|---|
| Buu's Fury (USA) | BG3E | 8 MB | EEPROM_V124 | f1c4b07554d2a3b1ad2f325307051e775ce68087 |
| LoG II (Europe) (En,Fr,De,Es,It) | ALFP | 8 MB | EEPROM_V122 | db36ff52fcd63f753f9d66439aa3d2216701c326 |
| LoG II (USA) | ALFE | 8 MB | EEPROM_V122 | 18e0715dec419f3501c301511530d2edcd590f8b |

- Both games together are 16 MB. The GBA cartridge limit is 32 MB.
- Both use EEPROM saves (8 KB at most). The merged save must fit in that, unless the save type changes. A save type change risks the anti-piracy check.
- **Base ROM: LoG II (USA), SHA-1 18e0715d... (final decisions, 2026-10-16).** Every address in these notes is for this ROM unless tagged otherwise.
- My (from memory): the USA version does not show transformation stat gains on the status screen. The Europe version does. Use the Europe status screen code as the reference when the gold bonus bars are built.

## My sprite and portrait sheets (`data\sprites\`, `data\reference\`)

- **Gohan (Demon Clothes):** a full LoG II move set with Gohan in the purple gi, base form only. Reuse it for base-form Gohan after the Hyperbolic Time Chamber.
- **Gohan (Battle Suit), Super Saiyan and Super Saiyan 2:** full move sets in Saiyan armor.
- **Gi plan for Super Saiyan and Super Saiyan 2:** per frame, combine the gi body from Demon Clothes with the gold hair and face from the Battle Suit frames, then touch up by hand. Works only if the two sets have the same frames in the same order. Unverified.
- **Gi target look (final, 2026-10-16):** Demon Clothes is Gohan's Android saga outfit, so it needs edits to become the Cell Games gi:
  - Remove the neck piece (white scarf).
  - Feet match Piccolo's sprite: brown boots, not black shoes with white wraps.
  - Shift the purple toward Piccolo's gi purple.
  - Sash is red (the anime shows blue; I want red).
  - Wristbands are blue, as in the manga reference.
  - References: `data\reference\D6FHgvhUIAATrwf.jpg` (manga, Cell Games), `images.jpg`, `desawf2-...png` (Android saga outfit), Piccolo sprite sheet.
- **Portraits:** the International portrait sheet appears to show Gohan's Super Saiyan forms in the gi. The US sheet shows them in armor. Port the International portraits.

- All three dumps match the No-Intro database (`C:\Program Files\mGBA\nointro.dat`, mGBA 0.10.5).

## Sprite storage (USA ROM, capture 01, 2026-10-16)

Source: mGBA save state in Gohan's bedroom, read with `scripts\permanent\rom\state_dump.py` into `scripts\one-time\2026-10-16-first-probes\captures\01-gohan-base\`.

- OBJ mapping is 1D. Every sprite is **8bpp (256 colors) with one shared OBJ palette**. A sprite's colors are palette indices into that shared palette, so there is no 15-color budget for each sprite. New gi colors must exist in, or be added to, the shared palette.
- Gohan's frame on screen is one 16x32 OBJ (8 tiles, 512 bytes) at OBJ tile 960.
- The tile bytes are **not stored raw** in the ROM.
- **No BIOS LZ77 block exists** in the ROM (scan by `scripts\permanent\rom\find_compressed.py`). The BIOS RLE "hits" are false positives. So the game uses its own (Webfoot) compression.
- The decompressed frame sits in a WRAM staging buffer at `0x020315A0`. The buffer holds only the current frame and a few other objects, so the game decompresses each frame on demand.
- No code literal points at `0x020315A0`, so the buffer is allocated at run time.
- **The shared OBJ palette is stored raw at ROM `0x1DA6C8` (`0x081DA6C8`), 256 entries, 512 bytes.** CONFIRMED: 254 of 256 entries match OBJ palette RAM in captures 01 and 02. Entry 0 (transparent) and entry 168 are set at run time.
- OBJ palette RAM is identical in capture 01 (Gohan's house) and capture 02 (outdoor map), so it is probably one fixed palette for all characters.
- Colors the gi can reuse (index: color, from Piccolo in capture 02):
  - Piccolo gi purple: 88 `#6008a8`, 89 `#500080`, plus dark outline 211 `#202040`.
  - Purple-magenta: 229 `#782078`, 231 `#a820a8`.
  - Brown boots: 34 `#a84800`, 35 `#783000`.
  - Red: 26 `#a80810`, 30 `#f87070`.
  - Blue: 72 `#0038b0`, 77 `#2080f8`, 195 `#2060c8`.
- Gohan battle suit (capture 02, NPC): blue 79 `#4020d0`, 80 `#3010a8`, 81 `#200080`. Skin 114-117. Yellow 40-42.
- Capture 02 (`scripts\one-time\2026-10-16-first-probes\captures\02-gohan-gi\`): player Piccolo plus NPCs. Probes: `probe_obj5.bin` Piccolo, `probe_obj8.bin` armored Gohan, `obj_palette.png` swatch.

**Decompressor found (2026-10-16).** Full detail: `docs\research\re-sprite-decompression.md`. Tool: `scripts\permanent\rom\webfoot_decompress.py` (`frame`, `find`, `set`).

- I verified independently: header `0x299DE4` unpacks to capture 01's Gohan frame (SHA-1 2806...ff5), `0x304ADC` to Piccolo and `0x2900D4` to armored Gohan (capture 02), byte for byte. IWRAM code equals ROM `0x7FD6BC`. ROM SHA-1 unchanged.
- Codec: ARM routine copied to IWRAM `0x03000000` at boot; frame header `{u32 type, u32 size, stream}`; types 1 and 2 compressed, 0 raw; 72 callers, so backgrounds and UI use it too.
- Sprite set table at ROM `0x3B4E90` (set id N >= 7 uses entry N-7). Frame record: 12 bytes (dx, dy, w, h, attr0, attr1, header pointer).
- Gohan sets, by look in the task's contact sheet (`scripts\one-time\2026-10-16-first-probes\gohan_sets.png`): 53 Demon Clothes (purple gi, red), 55 armor variant, 56 battle armor (confirmed), 57 casual green (confirmed), 58 spiky gold hair with fewer animations (probably Rage / Super Saiyan 2), 59 Super Saiyan. Set 54 is Goku Super Saiyan, not Gohan.
- Not yet built: a compressor for putting new frames back. Type 0 (raw) frames may let a first test skip it. Unverified.

## Save format (2026-10-16)

Full detail: `docs\research\re-save-format.md`. Tool: `scripts\permanent\rom\log2_save.py` (`info`, `build`, `set`).

- EEPROM 8 KB; the game uses bytes 0x000-0x447. RAM shadow at `0x0203E000`.
- Options block at 0x000 (4 bytes, then Adler-32 + 0x12345678). Three slots at 0x10 + n*0x168, each 0x164 bytes plus Adler-32.
- In the .sav file each 8-byte block is byte-reversed against RAM. LIKELY; my in-game test proves it.
- Story flag 195 = Cell beaten. Flag 196 (Lookout farewell) clear = last playable point after Cell.
- Each character record stores an appearance id (Gohan post-Cell: 2, set 56).
- Test save: `test-data\saves\log2_lv40_postcell.sav`, SHA-1 3ecf1e40.... Slot 1 Capsule Corp save point, slot 2 East District 439 save point, slot 3 Capsule Corp post-Cell spawn. All six characters level 40. I re-checked all checksums.

---

## LoG II: debug menu (wiki page shared by me, looks like The Cutting Room Floor)

- Enable with a CodeBreaker code while the game starts, then hold Start at the title screen.
  - US versions: `0202B32D:02`
  - Japanese version: `0202B371:02`
- Features: music and sound test, teleport to any level.
- On teleport, all six characters are playable and upgraded to a fixed degree.
- **Use for this project:** a fast test path to the Cell Games, possibly in place of a hand-made save file.

## LoG II: anti-piracy check (same source)

- Triggers when Gohan first leaves East District 439 for the world map. The game returns to the title screen.
- The source guesses it checks the save type, as Buu's Fury does. Unverified.
- **Risk for this project:** a change to ROM size, save type or save layout can trip it. Find the check before any such change.

## LoG II: unused graphics (same source)

- **Super Vegeta:** an unused buffed Super Saiyan sprite (down and side poses). In game, the form reuses the normal Super Saiyan sprite.
- **Super Trunks:** the same, unused buffed sprite (down and side poses only).
- **Trunks Sword Blast:** frames exist only for his first outfit. In his Bulma armor outfit and in Super Saiyan, no frames exist. Super Saiyan uses the punch animation as a placeholder.
- **Goku Spirit Bomb, facing down:** the frame shows his old Saiyan and Namek saga gi (long belt, kanji). Probably a leftover from LoG1.

Candidate backlog items (not yet agreed with me):
- Restore the Super Vegeta and Super Trunks sprites, so the buffed forms look different.
- Draw Sword Blast frames for armor Trunks and Super Saiyan Trunks.
- Fix the Goku Spirit Bomb facing-down frame.

## LoG II: music (same source)

- The debug sound test has 44 tracks (00-43).
- Track 20 is "Super Saiyan Rage". Track 35 is "Super Saiyan Vegeta". Track 19 is "Super Namek".
- Track 27 is unused in game.

## LoG II: International (Japanese) release (forum post shared by me)

- HP and ki growth is about 1/10 of the US and PAL versions. Reported as harder and better balanced.
- Final decisions: use the English scale, not the International balance.
- My correction: the International release has no Gohan gi sprites. The gi must be drawn new.

## LoG II: transformation bonuses (from an outside source, unverified)

| Form | Characters | Claimed bonus |
|---|---|---|
| Super Saiyan | Goku, Gohan, Vegeta, Trunks | +10 to each core stat (matches my screenshot: 100 to 110) |
| Super Namek | Piccolo | +6 to each core stat (my memory: about +5) |
| Super Vegeta, Super Trunks | Vegeta, Trunks | +15 to each core stat, slower movement (my memory: about +15 STR) |
| Super Saiyan Rage | Gohan | Claimed x2 core stats, event only, no ki drain (my memory: maxed stats) |

Read the real values from the ROM. Do not build on this table.
