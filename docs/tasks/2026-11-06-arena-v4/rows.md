# Bible rows for arena v4, tag ARN4

Only facts that were NOT already in the bible. The collision indexing (rows 1095, 1721), `obj+0x48` as a set
POINTER (row 105) and the conversation spots were all already recorded, and are not repeated here.

## Section 9

| Fact | Tags | Evidence | Source |
|---|---|---|---|
| **The Capsule Corp SAVE POINT and the MAP POST on map 6,1 are painted into BG2, and only their SHADOWS are background.** The logo and the post themselves are sprites the map spawns; a cloned map that spawns nothing shows a shadow with nothing casting it, which is what arena v1 to v3 did. Shadow palette index is **73**, RGB (144,200,248), against the pale floor's 72, RGB (208,232,248). Save point shadow: 270 px in the box (246,344)-(274,359), filling 10 tiles at px (240,344)-(279,359), entries 483 to 492, each its own tile. Dome shadow: 602 px in (420,694)-(474,739), filling 18 tiles at px (416,688)-(479,743), entries 510 to 520 plus `0x0C9C` and 155, plus entry 55 on 5 tiles. **No shadow tile is shared with art to keep**, so painting them out is a tilemap ENTRY swap and needs no hand art | #map #decision | C (BG2 rendered and read per pixel, every tile entry decoded) | ARN4 |
| **The MAP POST at (408,568)-(457,617) has NO collision: 49 cells of 49 are open.** You walk straight through it. It is drawn in the ground layer, confirmed by rendering BG2 and BG3 alone and finding it there | #map | C (collision frame read with the engine's own indexing) | ARN4 |
| **The CAPSULE CORP DOORWAY at (224,88)-(273,105) is 21 cells of 21 OPEN, and the 0x20 px deeper at (224,56)-(273,88) is 21 open of 35.** The doorway was never solid. In vanilla the warp to map 6,2 fires before you cross it, so nothing stops you except the warp. **A cloned map with the warps zeroed therefore lets the player walk INTO the building**, which the owner play-tested on arena v3: his state 4 sits at (246,94) in front of the door and state 5 at (246,72) inside it. Zeroing `layout +0x40` and `+0x44` seals the transitions but NOT the geometry, so a sealed clone also needs its own collision frame with the doorway closed | #map #decision #debug | C (collision read, plus the owner's states 4 and 5) | ARN4 |

## Section 11

| Fact | Tags | Evidence | Source |
|---|---|---|---|
| **To find every actor in a save state, scan WRAM for consecutive u32 pairs that are both multiples of 256 and whose `>> 8` values land inside the map.** An anchor is `{u32 x<<8, u32 y<<8}` at obj+0x158, so the object base is the hit minus 0x158. On arena v3 state 2 this returned 8 candidates in one pass, among them the conversation's two actors at **(244,504)** and **(248,568)**, which walking the world object lists had failed to produce. State 3 holds neither and holds (248,680) instead, which is the proof that the fight REPLACES the conversation's actors rather than moving them | #tool #object #debug | C (scan of both states, cross-checked against the owner's screenshots) | ARN4 |
| Trap, mine: **`obj+0x48` is a set POINTER, not a set id** (bible row 105 already says so). Reading it as a u16 id printed nonsense like 5876 and 40120 and made four actors look unidentifiable. To get an id, match the pointer against the live set table that the ROM word at `rom:0x959C` names, index + 7 | #object #tool | C (row 105, confirmed by the failed read) | ARN4 |
| `map_view.py` caveats found in use: its boxes labelled **"warp" are REGION records from entry `+0x10`**, not the layout's own door list at `+0x40`/`+0x44`, and its own line prints `region cond ... warp rect ...`. It also HARDCODES the map table at `0x409368` and 327 entries, so `--rom <a build>` reads the STALE vanilla table: arena v3's table is at `rom:0x93b6fc` with the arena at index 327. Resolve the table from the literal at `rom:0xEBD8` instead | #tool #map | C (source read, confirmed against the built ROM) | ARN4 |
