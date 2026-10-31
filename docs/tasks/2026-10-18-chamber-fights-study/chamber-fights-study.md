# Feasibility study: two new Time Chamber sparring fights (final, 2026-10-18 6:55 PM)

Personal GBA ROM hack (Legacy of Goku II, USA, merged later with Buu's Fury). Read first: `docs\RE-BIBLE.md` (all sections, especially the map, script, object, combat and story rows), `docs\research\re-overview.md` (engine code map), `docs\research\re-outfit.md` (ext ops, spawns, the chamber exit script `@0x083DB59F`), `docs\design\2026-10-16-log-merge-design.md`, `docs\research\research-bf-sprites.md`.

## My ask

"Have a task review if it's feasible to add a new boss fight. Ideally two Time Chamber fights, Trunks vs Vegeta and Gohan vs Goku, all with armor. The Time Chamber exists and is used in a fight in Buu's Fury."

Context: the chamber scenes are before Gohan returns to player control. Gohan, Goku, Vegeta and Trunks all wear the armor there.

## My design (7:02 PM): four fights, two per pair

1. **Vegeta and Trunks enter the chamber:** a dialogue, then their first training fight. The player is Trunks, in his jacket outfit with his stats at that point. Vegeta is the tougher side.
2. **Before Vegeta and Trunks finish:** a time jump. Trunks is now in his armor, with a level and stat bump and access to his higher Super Saiyan grade (in game, the form with about +15 strength). He fights Vegeta again.
3. **Goku and Gohan enter:** a dialogue, then a fight in their outfits from before the chamber. The player is Gohan.
4. **Before Goku and Gohan leave:** a time jump. They are in the armor, and Gohan has Super Saiyan access with a level and stat bump. Gohan fights Goku.

- **Dialogue:** I supply it from the show, which the game's own dialogue follows. The study only needs the mechanism and the size.
- **My question:** does the base game give stat or level bumps at the chamber, or only new abilities and moves? Answer it from the scripts.

Added questions for this design:
- **Outfits per phase:** the set ids and appearance entries for each, with whether each exists in the ROM:
  - Trunks: jacket, then armor.
  - Gohan and Goku: before the chamber, then the armor.
- **Forms:** Trunks' Super Saiyan grades in LoG II: their form records, the stat bonus of each, how a form is unlocked (record +0x14 bits, flags) and whether a script can unlock one mid-scene. The same for Gohan's Super Saiyan.
- **Time jump:** can a script raise a character's level and stats? For example, a call to the level-up routine `@0x08003CA0` from a script, or an existing ext op. How do the game's own story bumps do it, if any?
- **Player switch:** can a script force the leader to Trunks for fights 1-2 and to Gohan for fights 3-4, then restore the party?

## This is a study, not a build

No ROM build, no patch, no change outside `scripts\one-time\2026-10-18-chamber-fights-study\` and the report. Buu's Fury is read-only: study how it stages its chamber fight to inform the design. Do not port BF code. Say what BF assets (map, tiles) would be reused, and how big that reuse would be.

## Questions to answer, each with evidence (addresses, script bytes, tables)

1. **How a LoG II boss fight works end to end:** take one or two real boss fights (for example the Vegeta fight and the Cell fight). Cover:
   - the trigger and the script ops that start the fight
   - the arena or map lock
   - the boss object and its factory
   - the AI or state machine
   - the HP bar or HUD
   - the music
   - the win and lose handling
   - the flags it sets
   - the rewards
2. **Enemy versions of playable characters:** can a boss object use any sprite set, for example Goku set 60, Vegeta's armor set, Trunks' set? Are the playable sets' anims complete enough for an enemy (attacks, hurt, knockdown, ki)? Is there an existing enemy AI that fits a sparring partner? Vegeta is a LoG II boss already; check whether his AI can drive a Goku or Trunks sprite.
3. **Playable character per fight:** Gohan vs Goku with the player as Gohan, and Trunks vs Vegeta. Which side is the player there, and is a forced leader switch possible (ext 70 or 115)? How do party records and appearances need to look (armor: the entries before the chamber exit)?
4. **The chamber map:** does LoG II have a chamber interior map? I say LoG II has scenes where Vegeta and Trunks wait inside it. Give its zone and area, its size, whether combat is allowed there (map entry +8), its enemy spawns and its scripts. Compare with BF's chamber map and its fight.
5. **Story placement:** where in the chamber scenes each fight would go, which flags gate them, how to return to the existing script after the fight, and what happens on a loss.
6. **Hooks and space:** is there free ext op room or a script call mechanism to add new script records? Where does new script data go (the expanded ROM)? Are new strings needed, and how is text stored (compressed type 2 records)?

7. **Dialogue (6:57 PM):** new lines before and after each fight.
   - How is cutscene text stored (type 2 compressed records, the codec)?
   - How is new text written and linked, which speaker and portrait ids are used, and how are the boxes laid out?
   - Can new strings live in the expanded ROM?
   - Give the size of one short scene of about 8 lines.
8. **Stats (6:57 PM):** where enemy and boss stats live (HP, attack, defense, speed, EXP, drops), with addresses and the table layout.
   - How existing bosses scale.
   - What numbers would fit a sparring fight at that point of the story: the player's expected level, and nearby bosses as anchors.
9. **Music (6:57 PM):** how a fight picks its track.
   - List the LoG II tracks a chamber fight could reuse.
   - Find the sound engine of each game (for example whether both use the same driver or song format), with evidence.
   - Is porting a BF track a data copy, or does it need driver work? Give the size and risk.

## Deliver

- A verdict per fight: feasible / feasible with limits / not feasible, with the main blockers.
- A component list with effort for each: S, M or L, with what each needs. It covers the map, the boss object and AI, the sprites, the script and trigger, the flags, the dialogue, the stats, the music, the HUD, and win and loss handling. Give a total for the whole addition.
- A smallest first prototype, for example Gohan vs Goku with an existing boss AI, a Goku sprite and the chamber map, plus the steps to build it.
- The risks: AI quality, missing enemy anims, softlocks, save state.
- Bible rows for every new confirmed fact, written at the end into `docs\RE-BIBLE.md`, tagged and labeled. Add only your own rows.

## Limits

- Install nothing. Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths.
- A shell heredoc collapses backslashes. write files with Python, and check them for control characters.
- Other tasks build ROMs in the same tree. Read ROMs only. Do not touch `scripts\permanent\`, `builds\`, `art\`.
- Label findings CONFIRMED, LIKELY or SPECULATIVE. If you cannot trace a piece, say so and do not guess.

## Report

Save it as `docs\tasks\2026-10-18-chamber-fights-study\chamber-fights-study-report.md`. Then reply with the verdicts, the prototype in 3 lines, and concerns only.

