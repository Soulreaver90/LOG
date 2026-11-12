# Ending fight v3: play test

ROM: `builds\mockups\2026-11-05-ending-fight-1\log2_poc_r41_endingfight_v3.gba`
SHA-1 `24fb180b44ce67a2fe88a83a88852581a132763f`. Its `.sav` matches v1 and v2, so progress carries.
Full suite 1211 tests, OK.

## What v3 does

```
leader(who=3)                                    roster becomes Trunks FIRST
load_map(zone=6, area=1, var=1, x=248, y=568)    the engine spawns the player there, as Trunks
face(set=0, dir=1)
spawn(set=28, x=244, y=504)
ext104(28, 7)                                    boss Cell
header_bit1(value=1)                             HUD
bar_show(set=28)                                 boss bar
```

No cutscene NPC is converted. The map reload clears the scene actors by itself.

## Why v2 drew no Trunks

`sub_0800A680`, the core of `ext 70`, always writes the new leader into the party roster
(`STRB r4, [r0, #0x0]`). That is why v2 showed Trunks' HUD with his sword icon. But the block that
installs the leader's **body** sits behind a guard:

```
LDR  r4, [0x03001FA8]      Sprite_CurrentDirectory
CMP  r4, #0x0
BEQ  loc_0800A6E8          skips the whole appearance block
     ... STR r0, [r4, #0x48]
```

That word is zero all through the ending. Leader changed, body never built. v3 does not rely on
that block at all: it sets the roster first and lets the map load build the player from it.

## What your v2 states proved

- v2 state 1 is not the nightmare quote. It is the moment just after record F, and it still shows
  a 16x32 Trunks. That sprite is the NPC being cleaned up, because `ext 52` queues a DEFERRED
  removal (`sub_08009D00` allocates through `0x0801F08C` and hands off to `0x0800E04C`).
- Between state 1 and state 2, `Handler_Depth` goes 1 to 0 and `0x03001FDC` goes 1 to 0. **The
  scene fully unwound and free play was reached.** So the scene machinery is not at fault, and the
  postcell state 2 I used earlier really was free play.
- `BG1` and `BG2` scroll are identical across both states, so the camera fix holds.

## What to check

1. Is Trunks there, and can you move him?
2. Does the view stay in the cutscene framing, or does the map reload shift it?
3. Does Cell fight, and does his bar move when you connect?

## Known risk

`load_map` mid record is exactly what the ending's own word 13 does, so it should be safe. If the
view jumps or the screen fades, the map reload is the cause, not the camera.

## Separate job this uncovered

The map 6,1 item list does NOT parse as 7 items of 0x20 bytes, which is what `ending_fight.py`
assumes with `SPAWNS = 0x3F9C40` and `ITEM_SIZE = 0x20`. The patch works, so the assumption is
either right in a way I have not seen or harmless by luck. It needs auditing before anyone relies
on it, and it is the blocker for spawning Cell from the map's item list instead of `ext 104`.
