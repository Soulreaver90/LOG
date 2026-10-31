# Computer save report (my ask 2026-10-24 11:11 AM)

This report gives the key card facts and the test pair that opens the Capsule Corp computer with the Super Perfect Cell entry.

| Ask | Status |
|---|---|
| Find the key card, its door and the computer room | SHIPPED: item 41 "Red Card", door on map 6,4, computer on map 6,6 |
| Give a save that reaches the computer at once | SHIPPED: `log2_poc_r38_computer.sav`, slot 1 inside the computer room |
| Give the ROM link | SHIPPED: `log2_poc_r38_computer.gba` (byte copy of r38) |
| In-game check | PENDING: my test (steps below) |

---

## 1. Key card, door and computer room

The game reads one item to open the computer room. All addresses and decodes are on r38.

| Fact | Evidence | Label |
|---|---|---|
| Key card = **item 41 "Red Card"** ("Capsule Corp. Access"). Item 40 is the "Blue Card" (other Capsule Corp doors) | Item table `0x086ADE24` + 0x38 x 41: name id 140, description id 141 (string table `rom:0xE2840`) | CONFIRMED |
| Door: **map 6,4** (entry 148). With `flag:201` clear, region 1 (`rom:0x3FA050`, cond `0x000200C9`) is an A-press scene item `rom:0x3FA034`, rect (177,65)-(240,104), table `rom:0x3CEDF0`. With `flag:201` set, region 0 (cond `0x000100C9`) is the warp `rom:0x3FA01C`, rect (192,72)-(209,97), to 6,6 at (64,216) | Map table `rom:0x409368` entry 148, region list `rom:0x3FA048` | CONFIRMED |
| Door test: seq 1 `@0x083CED4C` = `push 41 ; ext 21 (item count) ; jz`. With the card: "Computer Room Access Granted" (`@0x083CED64`), then `@0x083CED88` SETFLAG 201 and ext 74. Without it: "Computer Room Access Denied / Authorization Level Red Required" (`@0x083CEDAA`) | Scene records decoded by `door.py` | CONFIRMED (bytes), LIKELY (seq 1 return = table word index) |
| The door does not take the card. The door records hold no item op, and the shape search finds no ext 76 or ext 77 (count minus) push of item 41 anywhere. Ext 74 (`@0x0800A998`) calls `@0x0800C2F8` on the running region object | Shapes A and B (`items.py`), record decode | CONFIRMED (by those shapes; a computed push would not show), LIKELY (ext 74 removes the door region) |
| Where the game gives the card: scene table `rom:0x3D0490` seq 11 `@0x083D0458` `push 41 ; ext 26`, "You received a Red Access Card!", after "GUARD: Newman, I should have known!" and "NEWMAN: Rats!". Me: event struct `rom:0x3FA714` of spawn `rom:0x3FA71C` (enemy type 74, set 146) on **map 6,11** | Three search shapes find only this give and the door count | CONFIRMED (bytes), LIKELY (given when Newman is beaten) |
| Computer room = **map 6,6** (entry 150). The computer is region 1 = {cond 0, item `rom:0x3FA360`}: factory `@0x080191CA`, rect (97,113)-(136,136), trigger `0x0800D87F` | Region list `rom:0x3FA370` | CONFIRMED |
| The computer opens on **A while facing up**. Trigger `@0x0800D87E` uses the object at IWRAM `0x0300209C`; its +4 byte must equal the player facing. That byte is 1 in all five r36 states | Listing `@0x0800D844`, state bytes (`facing.py`) | CONFIRMED (test), LIKELY (1 = up) |
| Database bits: the list loop `@0x0801923A`-`@0x08019262` reads byte +0x11A + (n >> 3), bit `1 << (n & 7)`. So the tool's bit n is entry n | Listing | CONFIRMED |
| Entry 19 on r38: name `Cell, "S. Perfect"` (`0x08908EEC`), text `0x08908F00` (my text), set 58, portrait 52, type 25 = HP 9876, STR 72, POW 71, END 78. Entry 13: `Cell, "Perfect"`, portrait 40, type 78 = HP 5160, STR 44, POW 46, END 50 | `entries.py` | CONFIRMED |

---

## 2. The test pair

The pair is a byte copy of r38 and the r38 scouter save with slot 1 changed. Both files were made by exclusive create (`open(..., "xb")`).

| File | SHA-1 |
|---|---|
| `builds\log2_poc_r38_computer.gba` | `7a7cb85fa5873c4a44d360b33b6755d4e71e18e3` (= r38) |
| `builds\log2_poc_r38_computer.sav` | `1d22232904b1fbd261677a0d16011b658a50cff6` |
| Source `builds\log2_poc_r38_scouter.sav` | `d2fa5e1a016ae40fe3b264eb21008b807d391a1f` |

Slot 1 changes:

- Map 6,6,1 (computer room) at position (116,160). The slot was at 6,1 (432,591).
- Item 41 Red Card = 1. Items 22 (Scouter) and 45 (Dragon Radar) are kept.
- Database bits 13 and 19 set. All other bits stay clear.
- Scouter switch (header +1 bit 2) kept on: header 0x07.
- Adler-32 redone with `log2_save.seal_slot`. `flag:201` stays clear.

> [!NOTE]
> The spot (116,160) is in no region. Every collision cell within 32 px of it is open (map 6,6 frame `rom:0x5E897C`). The cell data is CONFIRMED. How the saved position anchors the player box is LIKELY: 14 of 15 game arrival and save spots on maps 6,1, 6,2, 6,4 and 6,6 are on open cells.

### `log2_save.py info` (slot 1)

```
slot 1: checksum stored 0x49545a76 calc 0x49545a76 valid; in-use bit 1 -> shown
  leader 0 (Gohan)  header flags 0x07  map zone 6 area 6 var 1  pos (116,160)  +8 0x0
  story flags set: 155  (191 = Dragon Balls returned: 1, 195 = Cell beaten: 1, 196 = final goodbye: 0)
  visited maps 297/297  scouter entries 2/128  items {22: 1, 41: 1, 45: 1}
```

The options block is valid (`04 06 04 00`). Slots 2 and 3 are valid and equal to the source.

### Byte diff against the source (11 bytes, all in slot 1)

File offset f maps to RAM offset (f & ~7) | (7 - (f & 7)).

```
file 0x0014 -> RAM 0x0013 (slot 1 +0x003 area): 01 -> 06
file 0x012b -> RAM 0x012c (slot 1 +0x11c db bits byte 2, entries 16-23): 00 -> 08  (bit 19)
file 0x012c -> RAM 0x012b (slot 1 +0x11b db bits byte 1, entries 8-15): 00 -> 20   (bit 13)
file 0x0163 -> RAM 0x0164 (slot 1 +0x154 item 41): 00 -> 01
file 0x0170 -> RAM 0x0177 (slot 1 +0x167 Adler-32): 37 -> 49
file 0x0171 -> RAM 0x0176 (slot 1 +0x166 Adler-32): 52 -> 54
file 0x0173 -> RAM 0x0174 (slot 1 +0x164 Adler-32): 36 -> 76
file 0x0174 -> RAM 0x0173 (slot 1 +0x163 pos y): 02 -> 00
file 0x0175 -> RAM 0x0172 (slot 1 +0x162 pos y): 4f -> a0
file 0x0176 -> RAM 0x0171 (slot 1 +0x161 pos x): 01 -> 00
file 0x0177 -> RAM 0x0170 (slot 1 +0x160 pos x): b0 -> 74
```

The Adler-32 byte +0x165 did not change (0x5a in both). `make_save.py` asserts that no other RAM byte changed. The slot 1 journal is the same before and after (39 shown quests).

---

## 3. My steps

1. Load `builds\log2_poc_r38_computer.gba` in mGBA. mGBA loads the `.sav` with the same base name, `log2_poc_r38_computer.sav`.
2. Pick **slot 1**. Gohan starts in the Capsule Corp computer room, below the computer.
3. Push **Up** until Gohan stops at the computer (about 3 steps). He must face up.
4. Push **A**. The scouter database opens.
5. The list shows two rows: `Cell, "Perfect"` and `Cell, "S. Perfect"`.
6. Push **Down** to select `Cell, "S. Perfect"`.

A pass looks like this:

- The panel shows the name `Cell, "S. Perfect"`, my portrait 52 and Super Perfect Cell's sprite (set 58).
- The stats show HP 9876, STR 72, POW 71, END 78.
- Push A on the row. The text page shows my text ("After self-destructing, Cell regenerated from a single surviving cell..."). Use Up and Down to scroll it.
- The `Cell, "Perfect"` row shows portrait 40, HP 5160, STR 44, POW 46, END 50 and the shared Perfect text.

> [!WARNING]
> If you leave the room, the exit is the door at the bottom left. To come back in, stand at the computer room door on map 6,4 and push A. The Red Card gives "Computer Room Access Granted" and sets flag 201. If the door does not open at once, leave map 6,4 and come back (LIKELY: the warp region is built when the map loads).

If A does nothing at the computer, step left or right inside x 97-136 and push A again while facing up.

---

## 4. Files

- Bible rows: `scripts\one-time\2026-10-24-computer-save\bible_rows.md` (source tag `CSV`).
- Work scripts (LF, no byte order mark), all read-only on the ROM: `door.py` (scene tables), `items.py` (item names and item 41 users), `walk.py` (collision map and spot test), `facing.py` (trigger facing bytes from r36 states), `entries.py` (scouter entries), `make_save.py` (the pair), `proof.py` (SHA-1s, diff, journal).
- Not changed: `data\`, `scripts\permanent\`, `build_list.txt`, `art\`, `docs\`, `scripts\one-time\2026-10-24-hud-ki\`, and every existing ROM, save and state.
