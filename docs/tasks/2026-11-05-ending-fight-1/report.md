# Ending fight 1: Trunks against Imperfect Cell, as a real fight

Trial module only. It is not in `build_list.txt`, `build_list_dev.txt` or `build_list_core.txt`.

## Verdict

**Built and verified on the bench. Not yet play-tested.**

| Check | Result |
|---|---|
| Independent rebuild from `build_list_trial_ending.txt` | SHA-1 `34f045fb591f1d18871e13ffbeea87f22e99aaa5`, identical to the agent's ROM |
| `test_ending_fight.py` | 28 tests, OK |
| Ending table word 23, `rom:0x3B819C` | `0x083B8016` to `0x0893B5F8`, so the scripted kill is replaced |
| Map 6,1 item count, `rom:0x40B324` | 7 to 8, so the new Cell is appended |
| Map 6,1 item list pointer, `rom:0x40B334` | `0x083F9C40` to `0x0893B760`, the copied list |

I read those three sites in the base ROM and in the built ROM myself. They are not an agent's claim.

## What it does

Cell's scripted death in the ending becomes a fight you play.

1. Word 23 of the ending table now runs a new record instead of the vanilla kill. That record removes
   the NPC Super Saiyan Trunks, makes Trunks the leader, puts you on the NPC's spot facing Cell, turns
   the NPC Cell into a live enemy, shows the HUD and the boss bar, and then hands you control.
2. The enemy is the vanilla Imperfect Cell item copied byte for byte. Type 60 is untouched, so HP 5210,
   AI 80 and the boss descriptor are all vanilla, which is what you asked for.
3. When he dies, the bar and HUD go off, Cell collapses, and a fade covers putting the vanilla geometry
   back. Then the **vanilla** blast block and the **vanilla** tail run, so the ending finishes as it
   always did.

The blast block carries exactly one edit, its attacker push, because Trunks is the player now and not
an NPC.

## To play-test

ROM and save: `builds\mockups\2026-11-05-ending-fight-1\log2_poc_r41_endingfight.gba`

> [!WARNING]
> **Do not save during this fight.** The study flagged a save point roughly 160 px east of the fight
> floor. Saving there would strand the run, because the ending scene is mid-flight. I have not
> re-confirmed the distance myself, so treat it as a caution rather than a measurement.

What to watch for:

- Control actually arrives, rather than the scene running on past you.
- The boss bar appears and drains.
- After he dies, the camera and both characters land back where the vanilla ending expects them.
- The blast plays and the ending completes.

## Not done

- The "3 years later" card before the Cell scene.
- The Android 18 and Android 17 fights, which still need blocker B1 solved.
- Saiyan armour Trunks, deferred by you.
