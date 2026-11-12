# The ending's opening, rebuilt: Gohan flies off, Trunks at Capsule Corp, the time machine

Given by the owner 2026-11-09. **His words, verbatim:**

> "Lets start earlier, ill reive the transition later. When the game ends and gohan flies off, lets
> change it so music doesnt change, gohan flies off, then it fades to trunks at capsule corp with the
> journael entry update. Clicing next to the time machine initiates him moving tot he back like the
> cutscene and then it continues with the android build we already did"

## What he is asking for, as five beats

1. **The music does NOT change** when Gohan flies off. It carries through.
2. Gohan flies off. That already happens and he is keeping it.
3. It **fades to Trunks at Capsule Corp**, with the **journal entry update** shown.
4. **The player then has control.** Walking up to the time machine and interacting with it starts
   Trunks moving to the back, the way the cutscene does it today.
5. From there it continues into the future androids build, which is already done and approved.

**The change in kind:** beat 4 turns a scripted walk into something the player does. Today ending
table word 0 walks Trunks around on rails. He wants to stand there and press A on the time machine.

## What is there today, decoded from the shipped build

Ending table `rom:0x3B8140` word 0, `rom:0x9408CC`:

```
music(42)
load_map(6, 23, 1, 0, 192)          <- sunny Capsule Corp, the time machine (bible B1073)
camera_follow(132)                   <- set 132 is post-Cell Trunks (B0084, B0242)
walk(132, 288, 280) ; wait(120)
walk(132, 312, 216) ; walk(132, 352, 216)
face(132, 0) ; wait(80) ; face(132, 1) ; wait(80) ; face(132, 0) ; wait(40)
fade_out(180)
header_bit1(0)
appearance(3, 132) ; leader(3)
load_map_at(1, 100, 1, 496, 648)     <- the android map
wait(120) ; face(0,1) ; camera(384,552,2) ; fade_in(180)
camera_follow(0) ; walk(0,496,504) ; camera(384,368,2)
wait(60) ; face(9,2) ; wait(30) ; music(38)
```

How the ending is entered, from bible B0965 and B2076: the Dende farewell table `rom:0x3DD044`
record 87 `rom:0x3DCEDC` sets flag 196, flies Gohan home over a chain of `load_map_fade` ops and ends
`fade_out(300) ; ext125`. Record 88 `rom:0x3DD03C` is the type 5 jump into the ending table. **One A
press on Dende runs the farewell, the credits and the whole Trunks ending.**

## Open questions, to be MEASURED before any build

Nothing below is decided. Each is a measurement, not an opinion.

1. **What actually changes the music when Gohan flies off?** Candidates: the `music(42)` that opens
   word 0, the `load_map` of 6,23 reading that map's own `+0x24` (bible B1191: a load restarts the
   music unless the new map names the song already playing), or an op inside the farewell chain.
   Find which, then name the song that is playing, which is B1191's own stated rule.
2. **What is the "journal entry update"?** Find the op or the object the game already uses, and a
   vanilla site that shows one. Do not invent a presentation.
3. **How does the player get control at Capsule Corp?** The scene has to end, or hand off, so the
   map's own items run. Measure how a vanilla scene returns control.
4. **What makes the time machine interactable?** Map 6,23's item and region lists, read through
   `scene_probe --map 6,23`. Is there already an item on the time machine, and what starts it? A
   script region (`@0x0800C2C3`) and a scene item (`@0x0800D7E1`) are the two shapes.
5. **Does the android build still get entered correctly** once word 0 stops running straight through?
   `future_androids` and `ending_fight` both key off this chain, and `ending_fight` record A is ending
   word 13. Walk the whole chain before moving anything.

## Constraints that already apply

- `future_androids` is APPROVED and must keep working unchanged. Beat 5 is "continues with the
  android build we already did".
- The music rule is bible B1191 and B2176: `ext 38` and `ext 39` read the new map's `+0x24` and
  restart the music unless it names the song already playing. `ext 35` never reads it at all.
- Transition lengths come from vanilla, not from invention: the census is
  `scripts\one-time\2026-11-08-finale-poses\vanilla_transition_census.py`.
- He said "ill reive the transition later", so the plateau transition's remaining 64 frames stay as
  they are for now.

---

## MEASURED 2026-11-09 by the controller. Four of the five open questions are answered.

### 1. The music: it goes 18 then 42, and the fix is B1191's rule again

- Dende farewell record 87 `rom:0x3DCEDC` opens with **`music(18)`**. That is the track playing
  while Gohan flies home. It ends `fade_out(300) ; ext125`.
- Ending word 0 then runs **`music(42)`**, and map 6,23's own `+0x24` is **also 42**.

So the change he hears is **18 to 42**. The fix is the same rule as the plateau: name the song that
is playing. Drop word 0's `music(42)` and set map 6,23's `+0x24` to **18**.

**STILL OPEN, must be measured:** what `ext 125` does to the music. B2076 says one A press on Dende
runs the farewell, **the credits** and the ending, and `ext125` sits exactly where the credits would
start. If the credits stop or change the track, naming 18 on the map is not enough on its own.
Read the `ext 125` handler before building.

### 2. The journal entry update: the mechanism already exists

- Bible **B0706**: sound 62 is the vanilla "Journal Updated!" chime, and each of the 48 vanilla
  `@^Journal Updated!` records carries `ext 46 (62)` in the 24 bytes before it. There is a test,
  `test_vanilla_plays_62_right_before_every_journal_box`.
- Bible **B0826** names a worked example record, `rom:0x3D550A`.
- The journal CONTENT is not in the box. Bible **B0620** and **B0775**: the quest table is
  `rom:0x6D68DC`, 43 entries of `{category, done script, active script, text}`, and the done and
  active streams are flag tests (ext 19 and ext 21). The 43 texts are contiguous from `rom:0x6D6B8C`.

So "the journal entry update" is two separate things: the BOX, which is cheap and has a proven
shape, and the ENTRY, which is a quest table row driven by a flag. Adding a new row means relocating
a 43 entry table whose text pool sits behind it.

### 3. The time machine is background art. Nothing on this map is interactable.

Map 6,23 read end to end (`scratch\2026-11-09-ending-opening\map_6_23.txt`, picture
`map_6_23.png`):

| Field | Value |
| --- | --- |
| region list | **0 regions, pointer 0x0.** There is no region carrier at all |
| item list | **1 item**: factory `@0x0800D6DF`, npc, **set 132 at (48, 280)** |
| doors | 2, in the LAYOUT list: to map 6,1 and to map 6,5 |
| combat | 0, no attacking here |
| music `+0x24` | **42** |
| enter and leave scripts | both 0 |

The time machine sits on the pale pad at roughly **(320-400, 190-310)**, with the Capsule Corp dome
above it. Making it respond to an A press means ADDING a carrier this map does not have.

### 4. The Trunks at Capsule Corp today is an NPC PUPPET, not the player

This is the biggest finding and it shapes the whole job. In word 0 the ops drive **set 132** with
`camera_follow(132)` and `walk(132, ...)`. That is item 0, the NPC. The player does not become
Trunks until `appearance(3, 132) ; leader(3)`, which runs **after** the Capsule Corp beat, right
before the android map loads.

So for his beat 4, "the player walks up and presses A":

- the form and leader change must move EARLIER, in front of the Capsule Corp segment;
- the NPC puppet must not be standing there too, because two actors of one set make every op that
  names set 132 ambiguous. That is the same blocker `future_androids` already hit and documented;
- the scene has to hand control back, rather than running straight through on rails.

### 5. Does the android build still enter correctly? NOT YET CHECKED.

`ending_fight` record A is ending word 13 and `future_androids` keys off this same chain. Walk the
whole chain before moving anything.
