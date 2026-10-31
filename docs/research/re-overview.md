# LoG II engine overview: a code map (USA, ALFE)

Research 3. A breadth-first map of ten engine subsystems, so later slices know where to look. Read only: no patch and no ROM was built.

> [!NOTE]
> Labels: **C** = CONFIRMED (address plus bytes, disassembly, or a Ghidra decompile of that exact function), **L** = LIKELY (code read, meaning inferred), **S** = SPECULATIVE. A decompile is used as the evidence only where it shows the field offsets; the listings are in `scripts\one-time\2026-10-17-engine-overview\`.

Method: `scripts\one-time\2026-10-17-engine-overview\lib.py` (Thumb disassembly with `scripts\permanent\rom\thumb_dis.py`, BL caller index, literal search), Ghidra headless `Decomp.java` and `Dis.java` through `scripts\one-time\2026-10-16-task-5-gi-art\gh.sh` (ARM code: crt0 and the IRQ handler). Every new fact is also one line in `docs\RE-BIBLE.md` (source tag `OVW`).

---

## 1. Boot, main loop, frame timing, interrupts

**How it works.** The header branch goes to an ARM crt0. It sets the stacks, WAITCNT, clears IWRAM with DMA3, copies the IWRAM code block (decompressor and IRQ handler) from ROM, runs the C++ static constructors, then enters `main`. `main` probes SRAM (see the anti-piracy line), initialises the systems, runs two logo scenes, then loops forever over a scene object. Every game screen is a "scene" with a vtable. One frame is one VBlank: the loop halts with `swi 2` until the VBlank IRQ sets a flag. A scene can push a child scene; the push runs a nested frame loop until the child says it is done. This is how blocking script commands (dialog, map fades) work.

| Address | What | Label |
|---|---|---|
| `0x08000000` | `b 0x080000C0` (bytes `2E 00 00 EA`) | C |
| `0x080000C0` | ARM crt0: IRQ sp `0x03007FA0`, SYS sp `0x03007E00`, WAITCNT = `0x4014` (`0x080000E0`), DMA3 zero fill from `0x03000E7C` (0x2AA0 bytes), DMA3 copy `0x087FD6BC` to `0x03000000` (0xE7C bytes), lr = `0x08000159`, `b 0x0802369C` | C |
| `0x0802369C` | `ldr ip,=0x08021D75 ; bx ip` (bytes `00 C0 9F E5 1C FF 2F E1`) | C |
| `0x08021D74` | Runs the static constructor list `0x08023588`-`0x0802368F` (66 self-relative words) through `0x08021D28`, then returns to `main` | C |
| `0x08000158` | `main`. SRAM probe, `0x0801F248` system init, logo scene `0x0801EDE0` (vt `0x080237C0`, about 0xB4 frames), options load `0x08001E4A`, world reset `0x08006C24(0x03001120)`, second scene `0x0801D378` (vt `0x08023764`), then loop at `0x080001EE`: `0x0801ED3C` (intro, 0x12C10 bytes, vt `0x08023AB8`), set scene `0x0801F2CE`, run `0x0801F294` | C |
| `0x087FBDAC` | System table: save object `0x0300389C`, video/IRQ object `0x03000E3C`, input `0x0300229C`, sound `0x030026BC` | C |
| `0x0801F248` | System init: input init `0x0801EF56`, `0x0801EFA4`, IRQ init `0x08020D26`, VBlank callback = `0x0801F231`, IE \|= 1, sound init `0x08020AF4`, save init `0x08021454`, first input read | C |
| `0x03000E1C` | Scene manager: +0 current scene, +4 VBlank counter, +8 stack depth, +0xC saved scenes. Idle scene `0x030022B8` (vt `0x0802383C`) | C |
| `0x0801F294` | Frame loop: scene vt +0xC (update), sound `0x08020BD8`, wait `0x08020D40(video, 1)`, input `0x0801EEFC`, scene vt +0x14 (returns nonzero when done) | C |
| `0x0801F2CE` / `0x0801F2F4` | Replace scene (old +8 leave, new +4 enter) / push scene and run a nested frame loop until it is done, then pop. 21 and 63 callers | C |
| `0x08020D40` | VBlank wait: records the CPU load from VCOUNT into video +0x3C, then `swi 2` (Halt) until the IRQ bit is set in video +0x38 | C |
| `0x08020D26` | `[0x03007FFC]` = `0x03000824` (IWRAM IRQ handler), IE = 0x2000, IME = 1, DISPSTAT = 0x18 | C |
| `0x087FDEE0` (ROM copy of `0x03000824`) | ARM IRQ handler: scans IE & IF by priority, ORs the bit into video +0x38, re-enables IRQs in SYS mode (nested), calls the callback at `0x03000E3C + 4 * bit`. Game Pak IRQ (bit 13): `b .` hang at `0x087FDFAC` | C |
| `0x0801F230` | VBlank callback: `0x03000E20` += 1, then current scene vt +0x10 | C |
| `0x0800055E` | Title menu choice: 0 `0x08000CD8`, 1 `0x08000640`, 2 `0x080056B0`, 3 intro `0x0801ED3C` | C (code), S (meaning of each) |
| `0x08023884` | In-game scene vtable (made at `0x0800186E` by Continue). Update `0x08004EA8`: active camera object `[0x03000FF4]`, then world update `0x08006AD8`. Tick `0x08004EDC`: object OAM `0x08006AA6`, region triggers `0x08006250`, menu buttons `0x08004CAC` | C (calls), L (names) |
| `0x0800015C`-`0x080001A6` and `0x0800C390`-`0x0800C3E8` | SRAM probe: writes two test byte pairs to `0x0E000000`/`0x0E000001`, reads back, sets `[0x03001FC0]` = 1 if they stick, restores the bytes. Runs at boot and on every map load. Readers: ext 34, 35, 36, 37, 129 | C (code), L (this is the anti-piracy check of the wiki) |

**What later slices need from here.** The scene push (`0x0801F2F4`) is the hook for any new full-screen mode (a Buu's Fury style level-up box, a stat point screen). The build must never present writable SRAM, or `[0x03001FC0]` goes to 1.

---

## 2. Object system

**How it works.** The world object `0x03001120` holds a list of up to 128 active objects. Each frame it calls every object's update. Objects that return nonzero are sorted by depth and drawn; their OAM is built on the next tick. Objects talk through a message call (vtable +0x24) that the world can broadcast to all objects or use as a query (first nonzero answer wins). Actors also have a state machine: vtable +0x28 enters a state from a 48-entry table of IWRAM singleton state objects. Deletion is deferred: objects in the +0x610 list carry a reference count.

| Address | What | Label |
|---|---|---|
| `0x03001120` | World (a constructor stores vt `0x08023A0C` at `0x03001118`, 8 bytes before; not checked as the same object): +4 count, +8 active list, +0x208 draw count, +0x20C draw list, +0x40C second list (count + entries), +0x610 deferred list (+4 refcount), +0xBF8 menu copy (0xE00 bytes), +0xBFC sound state | C (offsets in code), L (names) |
| `0x080068B8` | `add(list, obj)`, 134 callers | C |
| `0x080068CA` | `remove(world, obj)`: replaces it with placeholder `0x03001F20`, calls obj vt +4 (delete); 57 callers | C |
| `0x08006942` | `replace(world, old, new)` | C |
| `0x08006DA6` / `0x08006E0A` / `0x08006E64` | Broadcast (OR of answers) / query (first nonzero) / count (nonzero answers); all call vt +0x24 on both lists | C |
| `0x08006AD8` | World update: vt +0xC per object, quicksort with `0x08027E74`, vt +0x10 draw (camera) into the draw list | C |
| `0x08006AA6` | Draw list: vt +0x14 per object (OAM) | C |
| `0x08006A38` / `0x080069A4` | Deferred list tick / flush (vt +0xC, then +8) | C |
| `0x08006F4A` / `0x08006FA4` | Menu pause (message 8, copy world to a 0xE00 buffer, save sound) / resume (restore, message 9) | C |
| `0x080075A8` > `0x080078E4` > `0x0800F80C` > `0x080086D4` | Class chain: sprite root > mover (vt `0x08024E84`, x/y 8.8 at +0x158/+0x15C) > combatant (vt `0x08025564`) > player (0x1A0 bytes, vt `0x08025604`, pointer `0x03001FA8`) | C |
| `0x0800D6DE` | NPC (0x16C bytes, vt `0x080257D0`) | C |
| Actor vtable | +4 delete, +0xC update, +0x10 draw, +0x14 OAM, +0x24 message(msg, arg), +0x28 set state(n), +0x2C in state(n), +0x38 apply hit, +0x3C heal, +0x40 take damage | C (player +0x24/+0x28/+0x2C/+0x38/+0x3C/+0x40), L (rest) |
| `0x080088BA` | Player +0x28: state object = `[0x083B5278 + 4n]` (`0x083B5268` + 0x10), entered through `0x0800763C`; +0x2C (`0x080088CA`) compares the current state | C |
| `0x083B5278` | 48 state slots (IWRAM objects); vtables set by the constructors, e.g. `0x08022FBC` | C |

**Messages (vtable +0x24).** Sender addresses from a sweep of `mov r1,#n` before the three world calls; a sender that loads n from a register would not appear.

| Msg | Meaning | Evidence | Label |
|---|---|---|---|
| 0 | Attack: hit test against a rect, then damage | player `0x08008944`, enemy `0x0800E5B8`; 16 broadcast and 5 query sites | C |
| 1 | Attack, alternate box (`0x0800793A`) | `0x08008944` | C |
| 2 | Overlap or vulnerability test (no damage) | `0x08008944`, `0x0800E5B8` | C |
| 3 | Interact (A button on a no-combat map) | `0x08007DE8` | C (sender), L (meaning) |
| 4 | Party add / remove (arg 2n+1 / 2n) | ext 29/30 | C |
| 5 | Find actor by sprite set | `0x08009370` | C |
| 6 | Find object by id (doors, arrival points) | `0x0800F034`, `0x0801038C` | C (sender), L (meaning) |
| 7 | Return the player | `0x08008944` | C |
| 8 / 9 | Menu pause / resume | `0x08006F4A`, `0x08006FA4` | C |
| 0x11 | Rect overlap, true if the actor is in state 6, 7, 8 or 0x10 | `0x08007B08`, sender `0x08011D0C` | C |
| 0x14 | Scouter scan: add a screen rect for each known enemy | `0x08007B08`, `0x0800E5B8`, sender `0x08018540` | C |
| 21 | Level-up broadcast | `0x08003D58` | C |
| 23 | Counted by ext 21 (item count) | `0x080095E4` | C (sender), S (meaning) |
| 10-16, 18, 19, 22 | Other senders: `0x0800DE20` (10-12), `0x0800B4AE` (13, 14), `0x0800E484` (15), `0x0800AC02` (16), `0x080040AA` (18), ball `0x080169B8` (19), `0x0801A6A0` (22) | sweep | L (numbers), S (meaning) |

**State ids (vtable +0x28, not messages).** 0x20 hurt, 0x21 death, 0x23 Saiyan transform, 0x24 revert, 0x25 Namek transform. The FRM "messages 0x23/0x24/0x25" are these state ids. Others (`scripts\one-time\2026-10-17-engine-overview\states.txt`): 0 = idle with control (vt `0x08025A84`; `0x08007F34`: d-pad to 1, a double tap within 20 frames to 13, A punch, B ability, 0x400 idle frames to 14), 1 = walk, 9 = power up, 16 = anim 16, 22 and 38 = stand variants, 34 = ki blast (ability 2), 35 = Saiyan transform, 36 = revert, 39 = hold special, 40-43 = punch (vt `0x08025D70`; the A press uses 40-42), 43-51 = ability moves, 51 = charged ball (ability 10). States 18, 19 and 20 point at the state 0 object, and a sweep finds no constant site that sets them (shape: `mov r1,#n` near a `[r,#0x28]` load and `bl 0x08021D2C`, `scripts\one-time\2026-10-17-engine-overview\stateuse.txt`). Ext 57 sets any state id from a script, so they are candidates, not proven free. Label: C (table and calls), L (names).

**What later slices need from here.** A new form, block or move is a new state object plus a slot in `0x083B5278`. The slot table has no literal of its own: code reaches it as `0x083B5268` + 0x10. `0x083B5268` has two literals (`0x08008868`, `0x08008AF8`) with 11 `ldr` users in the player code; only `0x080088BA` and `0x080088CA` add 0x10. A relocated slot table must keep `0x083B5268` +0 and +4 (world, struct) or repoint all 11 users.

---

## 3. Script engine

**How it works.** Scripts are a stack bytecode. `0x080092E4(vm, pc, ctx)` runs one script to its end in a single call. Commands that must wait (dialog, map load, fades) push a scene with `0x0801F2F4`, so the nested frame loop runs until they finish, then the script continues. Actor commands (walk, set state, face) go into a command queue through `0x0800E04C`. Base ops: 0 push u8, 1 push varint (7-bit groups, high bit continues, bit 0 = sign), 2 call ext (u8), 3 set var, 4-16 arithmetic and compare, 17 end (null handler), 18 jmp, 19 jz, 20 pop, 21-26 inc/dec, 27/28 loop, 29 push list (decoder: `scripts\one-time\2026-10-18-save-slots\sdis.py`).

| Address | What | Label |
|---|---|---|
| `0x080092E4` | Interpreter; `[0x03001FAC]` = current context; stops at a null handler (op 17) | C |
| `0x083B5C00` | 30 base op handlers (absolute pointers; entry 17 = 0) | C |
| `0x083B5D28` | 145 ext op handlers (absolute pointers); listing `scripts\one-time\2026-10-17-engine-overview\ext_ops.txt` | C |
| `0x083B5C78` | Script globals table: +0 sound `0x030026BC`, +4 `0x030026C8`, +8 world, +0xC actor command queue `0x030020F8` (ext 55 passes it to `0x0800E04C`), +0x10 map info `0x03002080`, +0x14 map view `0x03001090`, +0x18 `0x030020C0`, +0x1C `0x030020F4`, +0x20 save struct, +0x24 regions `0x03001FE0` | C (words), L (names) |
| ext 0-7 | Push `[0x03001FB0 + 4n]` (0-3) or a context word (4-7) | C |
| ext 8-16 | Getters: zone, area, variation, leader, string (12), leader STR/POW/END | C (8-11, 13-15 per sdis), L (12, 16) |
| ext 19 / 20 / 27 / 28 | Test flag / test not flag / set flag / clear flag (`0x08003E42`, `0x08003E5E`, `0x08003E74`) | C |
| ext 21 | Item count: `struct+0x12B+n` plus the message 23 count; not a give | C |
| ext 26 / 76 / 77 | Give item n (item +0x34 handler) / count += 1 / count -= n | C |
| ext 31 | Camera or walk vector (`0x0800DCA8` builds a velocity), then a pushed scene | C (code), L (meaning) |
| ext 35-39 | Map loads and warps (35 load map, 38/39 call `0x0800C584`) | C |
| ext 40-44, 67-69, 125 | Push a blocking scene (fade, flash, wait); vtables in the listing | C (push), L (meaning) |
| ext 52-58, 60, 62, 89, 93-96, 99, 100, 112, 121, 134-137, 140, 142, 144 | Queue an actor command through `0x0800E04C` (ext 57 = set state and wait) | C (queue call), L |
| ext 98 | Give EXP and level up (`0x08004214`, `0x08003CA0`, `0x08004276`) | C (calls), L |
| ext 131-133 | Push level-up gains `0x03001FC1`-`0x03001FC3` | C |
| ext 34, 129 | Read the SRAM probe flag `0x03001FC0` | C |
| `0x08003F06` | Condition evaluator: every map list item has a condition script | C |

How maps start scripts: map entry +0x30 runs at the end of the load, the old map's +0x34 runs on the next load (`0x0800C390`), +0x28 picks the variation, and +0xC (name) and +0x24 (music) are scripts when the value is 0x10000 or more (`0x0800EBB6`, `0x0800EB58`). Label C.

**Cutscene records (L).** The script region (`0x083B0000`-`0x08409367`) is a run of records `{u8 seq, u8 0, u8 type, payload}`. Type 0 is a bytecode snippet ending in op 17; type 1 is a portrait byte then text (e.g. `0x083BAA70` `07 00 01 2B "Oh, Goku!..."`). The record handler table is `0x083EC84C` (6 entries `0x0800B428`-`0x0800B494`); the dialog box is `0x0800B1E2` (portrait `0x0800BAB4`). How a map or NPC selects the first record is not traced.

**What later slices need from here.** Buu's Fury story content will need its scripts and text re-encoded in this VM and record format; the ext op table is the full verb list.

---

## 4. Maps

**How it works.** A map is a 56-byte entry found by (zone, area) with a linear search (`0x0800EB7C`; count from `0x0800E0AC`, which returns the constant 0x147 = 327). Loading clears the world, picks the variation, loads the layout for that variation (four BG layers, tile chunks, a collision bitmap), then spawns the entry's lists. Each list item has a condition script. The player object is made after the lists: a walking player, or a flying player when the layout +0x3C is set (world map).

| Field (entry, `0x08409368`) | Meaning | Label |
|---|---|---|
| +0 / +1 | Zone / area | C |
| +2 | Variation count | L |
| +3 / +0x10 | Count / list of 8-byte region items `{cond, item}`; item `{factory, test, rect x0 y0 x1 y1, data}`. Warp regions use factory `0x0800C232` (item +0x10 low nibble = direction) | C (loop `0x0800C2F8`), L (warp) |
| +4 / +0x14 | Count / spawn list `{factory, cond, x, y, set, ...}`. Factories: enemy `0x0800E77E` 666 items, interactive `0x0800B710` 245, NPC `0x0800D6DE` 197 | C (`mapdump.py`) |
| +5 / +0x18 | List; `0x0800F034` swaps the object with message 6 id = item +4 | C |
| +6 / +0x1C | On-map item pickups: `0x0800FA6C` makes a 0x44-byte object from item table entry `item+4` (base `[0x0800FB68]` = `0x086ADE24`, +8 = world icon) and marks collision (`0x080063E0` on view +0x6C and +0x74). Message 23 likely counts these for ext 21 | C (code), L (pickup) |
| +7 / +0x20 | 8-byte list `{x, y, id, ...}`; `0x0801038C` makes an arrival marker linked by message 6 | C (code), L |
| +8 | Combat allowed; copied to map info `0x03002080` +0xC; 0 = A talks instead of punching (`0x08007DE8`). This is the "map word" of the Super Saiyan gate | C |
| +0xC | Area name text id or script; 0xDD = no banner (`0x0800C584`, banner object `0x0800C978`) | C (code), L (banner) |
| +0x24 | Music index into `0x081D4B2C` or script; 0xFF = keep | C |
| +0x28 / +0x2C | Variation script / layout array (1-based) | C |
| +0x30 / +0x34 | Enter / leave script | C |

| Address | What | Label |
|---|---|---|
| `0x0800C584` | Map load and player spawn (walk `0x080086D4` or fly `0x080129B8`), HUD `0x08008B14` if struct +1 bit 1 | C |
| `0x0800C390` | Map load core (lists, music, scripts) | C |
| `0x03002080` | Map info: +0 zone, +1 area, +2 variation, +4 entry, +8 name id, +0xC combat flag | C (writes in `0x0800C390`), L (address of param) |
| `0x03001090` | Map view: +0x50 layout, +0x6C collision (0x2000 bytes), +0x70, +0x74 buffers | C |
| Layout record | +8/+0xA size, +0xC/+0x10 palette or anim list, +0x14-+0x20 four BG layer factories, +0x24/+0x28 animated layers (0x18 bytes), +0x34 collision (compressed), +0x38 second map, +0x3C world-map flag, +0x40/+0x44 extra regions, +0x48 tile index list, +0x4C tile chunk table | C (offsets in `0x08006152`, `0x08005FBA`, `0x080050C8`), L (names) |
| `0x08005D6C` | Collision test: rect in pixels, 1 bit per 8x8 cell, 256 cells per row (0x20 bytes), max 2048x2048; bit set = open | C |
| `0x0800638C` / `0x08006366` | Move tests with a box, used by the player and knockback | C |
| `0x03001FE0` | Region list (warps, triggers); A press tests it via `0x0800C06E` | C (calls), L |

**What later slices need from here.** New maps need new entries and the constant in `0x0800E0AC` raised; `ldr r1,=0x08409368` at `0x0800EB8A` is one table user, and the full user list is unknown 6. Walls are the collision bitmap, so "enemies bounce off walls" can use `0x08005D6C` directly.

---

## 5. Combat

**How it works.** An attack is a descriptor `{u8 side, rect x0 y0 x1 y1, hit}` that the attacker broadcasts as message 0. Side 0 hits the player, 1 hits enemies, 2 hits both. A target inside the rect computes damage with `0x0800F910` and reacts. The punch is resolved on the button press (`0x08007DE8`), before the punch animation (states 40-42, random). Holding A at the end of a punch starts the hold special (state 39) if record +0x14 bit 2 is set. B uses the selected ability; each ability tests EP, pays EP and enters a state that spawns the move.

**Damage formula (`0x0800F910`, C).** `hit = {+0 u8 facing, +4 multiplier (0x400 = 1.0), +8 move, +0xC attacker, +0x10 crit, +0x14 damage, +0x18 second value}`.

- Melee (move byte 0): S = attacker +0x160 (STR); crit = `rand16 < S * 0xA4` (`0x0802142E`), base = power x (crit + 1); G = defender +0x163.
- Ki (move byte nonzero): S = attacker +0x161 (POW); no crit; G = defender +0x164.
- `d = base * (0x80 - END) >> 7`, END = defender +0x162 (`0x0800F94E`).
- `f(S) = ((26S - 701) S + 115618) S >> 8`; `v = rand(26)` (`0x0802141C`).
- `damage = (((d * (256 + v) >> 8) * f(S)) >>> 18) * multiplier >> 10`. The 32-bit multiply is the `mul r0,r5` at `0x0800F974` inside the same routine; there is no separate attacker routine.
- `hit+0x18 = G * damage >> 7`.

Overflow (model `scripts\one-time\2026-10-17-engine-overview\dmgcalc.py`, END 0, best roll): ki moves never crit, so the real cases are ki power 0xC00 (ids 8, 13) wrapping at S 236 and the melee hold special 0x600 with a crit wrapping at S 236; the punch 0x400 does not wrap below 256. Vanilla stats (u8, cap 100 plus form bonus) never reach it. END over 0x80 makes `d` negative (FRM rule).

| Address | What | Label |
|---|---|---|
| `0x086DB2CC` | Move table, 8 bytes `{u8 kind 0 melee / 1 ki, u8 id, u16 0, u32 power 8.8}`, ids 0-15. Punch id 2 power 4.0 (`0x086DB2DC`), hold special id 4 power 6.0 (`0x086DB2EC`), enemy ki id 3, ability moves ids 6-13 (powers 0x40-0xC00) | C (bytes, users in `scripts\one-time\2026-10-17-engine-overview` notes) |
| `0x08007DE8` | A button: no-combat map = message 3 interact; else punch (side 1, multiplier 0x400, move id 2), sound 0x22 + rand(3) on a hit, then state 40 + rand(3) | C |
| `0x080085AC` | Punch state +0x14: A held (input +0x12 bit 0) and record +0x14 bit 2 = state 39 | C |
| `0x080083C2` | Hold special tick: charges while A is held, then moves along the facing at appearance +0xC speed with collision, hits (move id 4) on frames whose bit is set in appearance +8, ends at appearance +6 frames | C |
| `0x08008944` | Player message handler: 0/1 hit test (facing = attacker ^ 1, `0x0800F910`, vt +0x38) | C |
| `0x08008806` / `0x08008784` | Player apply hit (vt +0x38): take damage (vt +0x40), then state 0x20 / take damage: record HP -= damage, at 0 state 0x21 and a 200-frame game-over timer | C |
| `0x0800888C` | Player heal (vt +0x3C): HP += n up to max, green number | C |
| `0x0800E5B8` | Enemy message handler: side 1 or 2 hits, `0x0800F910`, then AI `0x0801AB2A(enemy+0x19C, hit)` | C |
| `0x0801AB2A` | Enemy AI behaviour list: calls the current behaviour's hit method (enemy knockback lives in each behaviour) | C (call), L |
| State 32 (`0x0800831C` enter, `0x0800E222` tick, `0x080082C8` move) | Player hurt: 32 frames, then state 0; moves 1 px a frame backwards along the facing (vector table `0x083B51C8`) with collision | C (code), L (that +8 runs each frame) |
| `0x0800F832` / `0x0800F8B6` | Damage / heal number popups (`0x080102A2`) | C |
| `0x081D9900` | Ability table (14 x 16): icon, dim icon, test, action. Action states (`abilities.txt`): 0 to 46, 1 to 47, 2 to 34, 3 to 48, 4 to 45, 6 to 5, 8 to 44, 9 to 49, 10 to 51, 13 to 50, 7 to 43 (`0x0801338A`); 11 and 12 toggle 0x24 (revert) or 0x25 / 0x23 | C (states), L (EP values in the listing) |
| Ability 2, state 34 (vt `0x08025D48`, enter `0x08014DE0`, `0x08014E86` flags a new B press) | Ki blast; every character except Hercule has it in slot 3 | C (code), L (name) |
| Ability 10, state 51 (vt `0x08025CCC`, `0x0801565C`, `0x080156B6`) | Charged ball (Goku slot 1, EP 20, cost 10): anim 19, EP -1 every 4 frames while B is held, fired on release (`0x080169B8`, message 19) | C (code), S (Spirit Bomb) |
| Blocking | No block state or block code found: 11 ASCII searches for "Block", "Equip" and others returned only dialog text; no state among the 48 has a guard shape | L |

**What later slices need from here.** A Buu's Fury block is a new state plus a damage scale in `0x08008806`; knockback today is fixed per state, not driven by damage, so "blocking reduces knockback" needs new code in the hurt state. New moves are new 8-byte move records and new ability states. The `+0x163`/`+0x164` defender bytes are the per-target melee/ki factor (enemies use them as "can be hit by" flags in message 2; the player's hurt enter clears them).

---

## 6. Characters and party

**How it works.** Six fixed 28-byte records live in the save struct `0x03000E90` at +0xC (layout in SAV). The leader index is struct +0. The player object is built from the leader's appearance entry. Level is not stored: it is computed from EXP.

| Address | What | Label |
|---|---|---|
| `0x081D9548` | Default records: Gohan HP 85 EP 20 STR/POW/END 3/5/3, abilities 4 3 12 2; Piccolo 95, 4/4/5, 9 8 11 2; Vegeta 105, 6/4/6, 0 7 12 2; Trunks 110, 6/3/4, 1 13 12 2; Goku 100, 5/7/6, 3 10 12 2; Hercule 50, 8/1/6, 6 6 6 6 | C |
| `0x081D9834` | EXP table, 50 entries (0, 50, 150 ... 22,965,105) | C |
| `0x080042EC` | The only literal of the EXP table; users `0x08004214` and `0x08004230` (level: `mov r2,#0xC4` entry 49, `mov r1,#0x31`), `0x0800425A`, `0x0800426A`, `0x08004276` | C |
| `0x08003CA0` | Level-up (SAV); random gains `0x081D95F0` | C |
| `0x0800A680` / `0x08011172` | Set leader / Switch Characters menu path | C (OUT) |
| Record +0x14 | Bit 0 in party, bit 2 hold special unlocked (menu page 1 and `0x080085AC`), bits 3-6 ability slots unlocked (pages 2 and 3 test bits 3 and 4) | C |
| Struct layout | Records end at +0xB4 where the story flags start; a seventh character needs a new struct slot. The EEPROM uses 0x448 of 0x2000 bytes | C |

**What later slices need from here.** The level bridge and the Buu's Fury cap change five functions through one literal. Goten, kid Trunks and Gotenks need a bigger record array, a new save layout and new appearance entries.

---

## 7. Items, equipment, shops, inventory

**How it works.** Inventory is 50 counts at struct +0x12B. The item table gives each item a name, a description, a world icon, a menu icon, a use effect and a pickup handler. Scripts count, give and take items through ext 21, 26, 76 and 77.

| Address | What | Label |
|---|---|---|
| `0x086ADE24` | Item table, 56 bytes x 50 (`items.txt`): +0 flags, +3 max count, +4 name text id, +6 description id, +8 world icon frame, +0x18 menu icon frame, +0x30 use effect, +0x34 pickup handler (`0x0800F3F1` for all named items) | C (bytes), L (+0, +8, +0x18) |
| Items | 0 Senzu Bean, 1/17 Golden Cap., 2-10 STR/PWR/END Cap. +1/+3/+5, 11-16 Health/Energy Bonus, 18-27 quest items, 28 Missing Nameks, 29-35 Dragon Balls 1-7, 36-45 keys and quest items, 46-49 unnamed (32x64 icons, handler `0x0800F441`) | C |
| Use effects | STR caps `0x0800F45B`, PWR `0x0800F4C3`, END `0x0800F52B`, HP bonus `0x0800F593`, EP bonus `0x0800F639`, Senzu `0x0800F6E9` | C (pointers), L (names) |
| `0x080046B0` | Item use from the menu (SAV) | C |
| Shops, money, equipment | 11 ASCII searches (Zeni, zeni, Buy, Shop, Equip, Money, gold, Block and others) found only map names and dialog; the 0x164-byte slot has no unaccounted field except 6 padding bytes | L (none exist) |

**What later slices need from here.** Buu's Fury equipment and shops have no LoG II counterpart; they need a new save field and new menu pages. The item table cannot grow in place without checking its 50-entry users.

---

## 8. Menus and input

**How it works.** Input is read once a frame into `0x0300229C`. On the in-game scene, `0x08004CAC` checks buttons: on walking maps R opens one screen and Select the Scouter; Start opens the character menu when the leader has HP. Each opens the same way: fade out, pause the world (message 8), push the menu scene, resume (message 9), redraw the map, fade in. The character menu is a framework scene with a fade state machine, left/right to change character and up/down to change page.

| Address | What | Label |
|---|---|---|
| `0x0300229C` | Input: +0 ring index, +2 ring of 8 pressed words (cheat sequences, `0x0801EF64`), +0x12 held (KEYINPUT inverted), +0x14 pressed, +0x16 released, +1 soft-reset enable: A+B+Select+Start held plus a new press calls `0x0802135C` (`0x0801EF3C`) | C (code), L (reset) |
| `0x0801EEFC` | Input read; `[0x03002298]` = frame of the last press | C |
| `0x08004CAC` | Menu buttons: R (bit 8) to `0x08017A50` (size 0x80B0), Select (bit 2) to Scouter `0x08018540`, Start (bit 3) to character menu `0x08003480` (0x170 bytes, vt `0x080248CC` over `0x08023B3C`). R and Select also need struct +1 bit 2, which SAV calls debug-teleport only (L): a conflict, not resolved here | C (code), S (R screen = area map) |
| `0x08000C18` | Menu tick: fade in 32 steps (vt +0x1C), run (vt +0x24), fade out (vt +0x28), exit (vt +0x2C) | C |
| `0x0800273A` | Menu input (vt +0x24): calls page input vt +0x54 first; B or Start closes; left/right widgets change character (+0x114) | C |
| `0x08002A5A` | Page input (vt +0x54): calls vt +0x68, then up/down change page (+0x120) | C |
| `0x08003B72` | vt +0x68 = `mov r0,#0 ; bx lr`: the empty per-page input hook. A stat point editor on page 0 goes here | C |
| `0x0800350A` | Page count: 1 for character 5 (Hercule), else 4 | C |
| `0x08003B44` | Page draw: 0 status `0x0800379C`, 1 hold special `0x08003684`, 2 and 3 ability slots `0x08003520` | C |
| Ability input | B = selected ability (input +0x14 bit 1, `0x08007EDA`), L cycles slots (`0x08008B88`) | C (FRM) |

**What later slices need from here.** This answers the open status menu input question: hook vt +0x68 (`0x08003B72`) for the status page. The Journal string exists ("Credits", "Journal", "Exit" near `0x080E2CAB`); its screen is not traced.

---

## 9. Sound and music driver

**How it works (identify only).** A custom mixer, not MP2K: no "m4a", "Sappy", "MP2K", "Krawall", "GAX" or "MusyX" strings, and no literal for `0x03007FF0` (the MP2K SoundInfo pointer). Music is a tracker-style module with shared instrument and sample tables. Sound effects are raw PCM.

| Address | What | Label |
|---|---|---|
| `0x081D4B2C` | Music table, 44 entries of 20 bytes `{data, order or track list, instruments 0x0814A8A4, samples 0x0814AD60, u32 length}`; 44 matches the debug sound test | C (bytes, count), L (fields) |
| `0x080E15B0` | Sound effect table, 12-byte entries `{PCM pointer, u32 flag, u16 length, u16 rate 0x3E80 = 16000 Hz}`; entry 55 is used by the forms, so at least 56 entries | C (format of entries 0-9), L (count) |
| `0x08020A4C` | Play music: resets 15 channels of 0x60 bytes | C |
| `0x08020AF4` / `0x08020BD8` | Sound init / per-frame update | C (calls), L |
| `0x08020CE8`-`0x08020CFC` | Only literal users of SOUNDCNT and the FIFO A/B addresses (DirectSound) | C |
| `0x08030000`-`0x0814FFFF` | Sample data (raw 8-bit PCM by look) | L |
| `[0x086F7E50]` + 0x5C4 | Sound object used by ext 46/47 | C (T6) |

**What later slices need from here.** Buu's Fury music must be converted to this format or played by a second driver; the Buu's Fury driver was not examined.

---

## 10. Text

**How it works.** Menu text is null-terminated 8-bit ASCII with `\n` (0x0A) line breaks, drawn with a variable-width 1-bit font into an 8bpp canvas. UI strings come from one pointer table. Dialog text is inline in the cutscene records (section 3); 0x0B appears as a break inside dialog.

| Address | What | Label |
|---|---|---|
| `0x080E2840` | String pointer table, 260 entries (UI, item names, map names, menu text) | C |
| `0x08028724` | Font: 256 u16 offsets, glyph = u16 width then one u16 column bitmap per pixel column (e.g. "A" width 5, columns `0F80 0140 0140 0140 0F80`); 20 users | C (layout), L (16 px rows) |
| `0x0801F636` / `0x0801F702` | Draw string (align 0 left / 1 center / 2 right) / draw wrapped at a width | C |
| Text context | `{u8 align, u8 line height, +4 x, +8 y, +0xC font, +0x1C max y, +0x20 glyph draw (0x08020EC3)}` | C |
| `0x083B0000`-`0x08409367` | Dialog: 1,093 null-terminated runs of 6 or more printable bytes, about 42 KB | C (count, one shape) |
| Dialog records | `{u8 seq, 0, u8 type 1, u8 portrait}` then text; portrait byte is a dialog portrait id (e.g. 0x2B = 43, 0x42 = 66) | L |

**What later slices need from here.** Buu's Fury dialog must be re-encoded as type 1 records with LoG II portrait ids; new UI strings need a relocated string table (one table, 20 literal users).

---

## 11. The ten most useful unknowns for the merge

Ranked by how many later slices they block.

| # | Unknown | Why it matters | Suggested way to answer |
|---|---|---|---|
| 1 | How a map, NPC or trigger selects the first cutscene record, and what record types 2-5 do (`0x083EC84C`) | Every Buu's Fury scene must be written in this format | Decompile `0x0800B428`-`0x0800B494` and the NPC talk path (message 3 receiver); walk one known scene (`0x083EBFF8`) from its trigger |
| 2 | Enemy record layout `0x086D56AC` (24 bytes) and the AI behaviour list at enemy +0x19C | Buu's Fury enemies, knockback and wall bounce | Decompile `0x0800E77E` and `0x0801A9CC`; tabulate all 666 spawn items by type |
| 3 | Where knockback distance is set for enemies; whether `hit+0x18` feeds it | "Every hit pushes back" and "block reduces knockback" | Find readers of hit +0x18 (offset 0x18 loads after a `0x0800F910` call); trace one behaviour's hit method |
| 4 | Save layout growth for new characters (Goten, kid Trunks, Gotenks) | The six-record array ends at +0xB4 | List every reader of struct +0xC..+0xB3 (shape: record base `+0xC + n*0x1C`); design a v2 slot beyond 0x448 |
| 5 | Sound driver formats (music module, instrument and sample tables) | Buu's Fury music and new sound effects | Decompile `0x08020A4C`, `0x08020BD8` and the IWRAM mixer; render one track |
| 6 | Map table growth: users of `0x08409368` and the 0x147 constant | New Buu saga maps | Literal and immediate sweep for `0x08409368`, `0x147`, and `0x38` strides |
| 7 | Layout and tile formats (BG layer factories, tile chunk table, collision source) | Porting Buu's Fury maps | Decompile the four layer factories at layout +0x14-+0x20 for one map; decode one collision bitmap and overlay it on a capture |
| 8 | Region and warp item format (`0x0800C232` data, destination fields) | Linking new maps | Decompile the warp region tick and dump all region items |
| 9 | What the R button screen (`0x08017A50`) and the Journal are | Buu's Fury has its own map and journal screens | Decompile `0x08017A50`; one capture with R pressed |
| 10 | Spare state ids (18-20), state 31, and the R and Select gate (struct +1 bit 2) | Room for block and new move states; whether the Scouter needs a story bit | Sweep ext 57 arguments in all scripts (`sdis.py`); decompile state 31 (vt `0x080258C8`); find every writer of struct +1 bit 2 (SAV found only the debug teleport; op 86 at `0x080040AA` sets bit 1) |

---

## 12. Files

- Listings and scripts: `scripts\one-time\2026-10-17-engine-overview\` (`lib.py`, `q.py`, `mapdump.py` and `maps_all.txt`, `ctors.py` (fixed for pointer arithmetic) and `ctors.txt` (`ctors_old.txt` = the wrong first run), `states.txt`, `extdump.py` and `ext_ops.txt`, `abilities.py` and `abilities.txt`, `items.py` and `items.txt`, `stateuse.py` and `stateuse.txt`, `vtfind.py`, `dmgcalc.py` and `dmgcalc.txt`, `checks.txt`, `dec_*.txt` Ghidra decompiles, `dis_crt0.txt`, `dis_irq.txt`).
- Bible lines: `docs\RE-BIBLE.md` section 14 and the corrections in sections 8 and 13 (source `OVW`).
