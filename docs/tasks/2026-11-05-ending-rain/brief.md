# Brief: trace the rain and the filtered view in the ending

A STUDY. Read only. Write nothing outside your own two folders. Build no ROM. Run no test suite.

## The question

The ending's Capsule Corp scene shows rain and a washed out, filtered colour view. The owner wants the
new Imperfect Cell fight to keep that look while the fight is playable.

Answer, with addresses and bytes:

1. **What draws the rain?** Is it a sprite layer, a background layer, a scripted effect, or map data?
   Name the exact mechanism and where it is turned on and off.
2. **What makes the view filtered?** `palette_fx` is ext op 42. Is that what does it? If so, with which
   value, and where is it set and cleared? If not, say what does.
3. **Does either survive a real fight?** The ending is a cutscene. A fight starts enemies, a health bar
   and player control. Say whether the rain and the filter would still draw during that, and give the
   evidence. If you cannot tell without running it, say so plainly.
4. **What would turn them on for a fight?** The smallest change that keeps the look.

## Where to look

- Scene table `rom:0x3B8140` is the ending, 27 words. The Cell portion is words 16 to 23.
- `scripts\permanent\scene\scene_probe.py --table 0x3B8140` prints it.
- `scripts\permanent\scene\scene_lib.py` holds the op names. Ops it does not name print as `extNN`.
- `docs\RE-BIBLE.md` section 5 is palettes, section 9 is maps. Search it BEFORE you search the ROM.

## Hard constraints

- Write ONLY into `docs\tasks\2026-11-05-ending-rain\` and `scripts\one-time\2026-11-05-ending-rain\`.
- Do NOT edit `docs\RE-BIBLE.md`. Put your rows in
  `docs\tasks\2026-11-05-ending-rain\bible_rows.md` in the `## Section N` table shape. I merge them.
- Never write under `data\`. Never overwrite a ROM, a save or a state.
- Absolute paths only. Never `cd`, `Set-Location` or `Push-Location`.
- Never find a scene table start by walking backward. A stray word before word 0 reads as an END and
  shifts every index by one. Reach a table through the item, event or type 5 record that names it.
- `--find-text` in `scene_probe.py` is CASE SENSITIVE.
- Python is `py -3.14 -P`. Read `docs\tasks\global.md` first.
- Label every claim CONFIRMED (address plus bytes or disassembly), LIKELY or SPECULATIVE. Do not round
  LIKELY up to CONFIRMED.

One report message, then stop. Do not add a byte order mark.
