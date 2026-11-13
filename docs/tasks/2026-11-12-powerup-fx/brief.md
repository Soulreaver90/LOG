# Power-up effects in game: the dust and the Buu's Fury aura

Study and build in one agent. The design is decided. Do not re-open it.

## The goal

Two trial ROMs the owner can play:

1. **Vegeta Z+**, his existing `vegeta_zplus` trial, with the power-up **dust and aura playing**.
2. **Piccolo Z+**, a NEW form above Super Namek, with his four drawn frames, a portrait, and the same
   dust and aura.

The owner has waited through three builds that showed him nothing. Neither ROM is finished until the
effects are visible in the power-up.

## What is already measured. Do not re-measure it.

### The aura

| Thing | Value |
|---|---|
| Records | `rom:0x752D28`, `+12`, `+24` in the **Buu's Fury** ROM |
| Pixels | `rom:0x752128`, `0x752528`, `0x752928` |
| Shape | three 32x32 frames, 8bpp, GBA 8x8 tile order, `attr0=0x2000` `attr1=0x8000`, `dx=16` `dy=31` |
| Colours | BF OBJ indices 5 `#F8F800`, 29 `#F8F890`, 30 `#F8F8D8`, 110 `#F8D000` |
| Exported | `art\transformations\_buus-fury-reference\aura\frames\01..03_bf_aura.png`, and the white recolour `01..03_bf_aura_white.png` |

Bible rows B2403-B2409. The aura is an **effect record** (format in B1768), not a sprite set.

Only one of the four gold colours is in the LoG II OBJ palette: `#F8F800` at index 8. The white
recolour (`#909090`, `#C0C0C0`, `#E0F8F8`, `#F8F8F8`) was chosen from entries the LoG II OBJ palette
already holds, so it needs no palette work. **Vegeta takes the gold, Piccolo takes the white**
(owner, 2026-11-12). If the gold needs three palette entries, say what it costs before you take them.

### The dust

Buu's Fury draws it INTO its own frames: one colour `#D8B898`, rows 27-31, 34-71 px a frame, two
alternating shapes, and it REPLACES the shadow. Exported to
`art\transformations\_buus-fury-reference\dust\`. Our frames should use `#D8A860`, a tan his frames
already carry. The dust is pixels, so it needs no object.

### The timing, approved by the owner on the mockups

- Frames 1 and 2 are the wind up. **No aura.**
- The aura appears when the **3/4 loop** starts, and runs its own three frame cycle from its frame 1.
- The dust starts on **frame 2**, one frame before the aura.
- The aura draws **above** the character. He animates inside it and the aura does not move with him.

`scripts\one-time\2026-11-12-bf-effects\aura_timing.py` renders exactly this. Match it.

## The one thing that is NOT measured, and is the whole job

**Can the power-up spawn an object?** Bible B0605 and B0757 say our power-up state does not spawn
anything. The effect classes exist: B1768 names their record users and ctors, for example the anim
class `@0x08013750` with ctor `@0x080135E0` and six literal record lists. **Read those handlers.**
Decide and report which of these the build uses:

1. A spawned effect object, following an existing effect ctor, attached to the actor for the power up.
2. The dust and aura drawn into the frames as pixels. Cheap, but the frames have only 4-8 px of
   clear margin, so a 32x32 aura does not fit around a 32x32 character.
3. A second OAM sprite driven from the state 35 tick that `bf_ki_pool` already owns (`tick_xform`,
   vtable `0x08025D9C +0x04`).

Route 2 is already known not to fit for the aura. Route 1 or 3 is the answer. Pick on evidence from
the handlers, state why in the report, and name what you ruled out.

## Piccolo Z+, the form itself

Model it on `scripts\permanent\patches\vegeta_zplus.py`, which does the same job for Vegeta.

- **Stats, settled by the owner 2026-11-12, his words: "For piccolo, +10 and healing for Z+. Z is
  just +6 no healing."** So Super Namek (Z) keeps `piccolo_z_start`'s +6 with the heal removed, and
  Z+ is +10 with the HP healing restored. The heal is the block in the Super Namek tick
  `0x08017400` that adds max HP x 0x290 >> 16 every overflow, which `piccolo_z_start` moved off.
- **Unlock:** the Kami fusion's `ext 82 (1)` at `rom:0x3E0D75` is spare now that Z starts open. It
  grants Z+ instead.
- **Set:** 104, Super Namek, which is where his four drawn frames already live
  (`piccolo_powerup_art.py`). The appearance entry that names set 104 today is entry 21.
- **Portrait:** a new id. 121 was the last free one, so the portrait block must grow again.
  `npc_gi.py` proves the move: the block cannot grow in place, it relocates, and `rom:0xBE10` plus
  the hook's pool word follow it. Run the two shape reader census BEFORE editing it. Use Super
  Namek's own portrait art as the placeholder; the owner draws the real one later.
- Caution, LIKELY not CONFIRMED: a Z+ form object of its own may not fit `pool_ref`'s slack. Check
  before you design around it.

## Files you need

| File | Why |
|---|---|
| `scripts\permanent\patches\vegeta_zplus.py` | the working Z+ model, and `write_anim_row` |
| `scripts\permanent\patches\piccolo_powerup_art.py` | his four Piccolo frames, already on set 104 |
| `scripts\permanent\patches\bf_ki_pool.py` | owns the state 35 tick, the HUD overlay and both bar images |
| `scripts\permanent\patches\npc_gi.py` | the proven portrait block relocation |
| `docs\RE-BIBLE.md` | search it FIRST, sections 4, 5, 6 and 14 |
| `art\transformations\_buus-fury-reference\` | the exported aura and dust, and the mockups he approved |

## Rules

- Search `docs\RE-BIBLE.md` before you search the ROM. Read the handler before you trust a label.
  `GitHub\legacyofgoku2-disasm\build\code` is the byte exact tree. The `gnu` copy is stale.
- Never write under `data\`. Absolute paths only. Never `cd`.
- Build with `scripts\permanent\log2_build.py`. Trial lists only. Do not touch `build_list.txt`,
  `build_list_dev.txt` or `build_list_core.txt`.
- Run the full suite ONCE at the end, to completion, and report the summary line and the real exit
  code. Never pipe it into `tail`. The baseline is 34 failures, listed in
  `scratch\2026-11-12-ship\fails_base.txt`. Any new id is yours.
- Batch the builds. The owner has said twice that tiny rebuild cycles cost him. Build when there is
  something to see.
- One report message, then stop. Do not add a byte order mark.
