# Design: the future Trunks finale

Owner's plan, given 2026-11-07 between 11:20 AM and 12:10 PM. This is the TARGET. We build to it one
mockup at a time, which is his instruction, not an inference.

## The flow he wants

```
Cell Games ends
  NO credits music
  FADE                                    (no Gohan flight, no Chi-Chi)
  Trunks at Capsule Corp, PLAYABLE, the only playable character
  JOURNAL ENTRY: enter the time machine and end the nightmare
  the time machine, gated on Trunks at level 35
  ENTER
    future: 18 fight -> she collapses -> Trunks blasts her, NO transition
    17 walks in from off screen, dialogue, fight -> collapses -> blast
    Trunks: "I wish I could say that it's all over, but there is one more
             thing that has to be done"  "... Cell"
    Cell: Trunks starts NOT Super Saiyan
      half way: white flash + ping -> cutscene, Cell punched off screen,
                Trunks flies after him
    final arena: our own enclosed grassy plateau
      they talk, Cell's lines (he will supply), Trunks: "But count me as the last"
      fight, Cell turns Super Saiyan if he is not
      Cell beaten, does NOT explode
      cutscene: Cell powers up into the Kamehameha pose
                Trunks: "THE NIGHTMARE IS OVER CELL"
                huge blast (Vegeta's Big Bang borrowed, a Trunks super attack animation)
    Trunks detransforms: "Now I can finally say that it's really over.
                          Thanks to you father, and to you Gohan.
                          And especially to you Goku"
  Credits roll, then the end prompt
```

## The single most useful fact about this plan

**The scene already exists.** Ending scene table `rom:0x3B8140`, 27 words, IS the future Trunks sequence,
and `@^Sixteen years from the present day...` at `rom:0x3B81B0` is already its caption. We are expanding a
scene and making its beats playable, not inventing one.

| word | vanilla | becomes |
|---|---|---|
| 0 | loads map 6,23 then map 1,2, parks the camera | loads the sealed clone, player spawned |
| 4 | `rom:0x3B7C1C`, the NPC Super Saiyan transform (132 to 133) | the live-player transform |
| 8 | the set 11 beating | **FIGHT 1, Android 18** |
| 9, 10 | dialogue | dialogue, plus the collapse and blast beat |
| 11 | the set 9 beating | **FIGHT 2, Android 17** |
| 12 | dialogue | his new two-line replacement |
| 13 | loads map 6,1 | loads the arena, then the plateau |
| 22 | "THE NIGHTMARE IS OVER CELL!!!!!" at `rom:0x3B7FF6` | **moved to the finale** |
| 23 | the Cell beating | **FIGHT 3, then FIGHT 4 on the plateau** |
| 24-26 | "@^The End." / "Thanks for playing!" | after the new closing lines |

## Mockup ladder

Each rung is a ROM he can play. He judges by eye, we do not advance on a green suite alone.

1. **DONE and approved.** Two playable android fights, map 1,100 sealed clone, simple seams.
   His words: "the fights themselves work perfectly".
2. **IN FLIGHT.** Restore the Trunks transformation animation at word 4. His only defect on mockup 1.
3. **IN FLIGHT.** The plateau: our own large enclosed grassy map, reached by repointing the arena load.
4. The death beats: 18 collapses and is blasted with no transition, 17 walks in from off screen.
5. The Cell fight split: Trunks starts base, white flash and ping half way, punched off screen.
6. The plateau battle: the talk, Cell's lines, "But count me as the last", Cell turns Super Saiyan.
7. The finale: Cell in the Kamehameha pose, the moved nightmare line, the big blast.
8. The front half: fade from the Cell Games straight to playable Trunks at Capsule Corp, the journal
   entry, and the level 35 time machine gate.
9. Credits and the end prompt.

Order is mine and negotiable. 8 is last because every rung above it is playable without it.

## What is already solved, with the precedent

| need | precedent |
|---|---|
| a scripted beating becomes a real fight | `battle_arena.py`, `ending_fight.py`, mockup 1 |
| a sealed clone map, 0 regions, 0 doors | map 6,100 and map 1,100, both verified on the built ROM |
| a map carrying its own BG2 | map 6,100 |
| the live-player Super Saiyan transform | `cellgames_ssj.GOKU_TRANSFORM`, already shipped |
| white flash and ping mid-fight | `celljr_fight` relays, `ext 42` |
| an enemy inert until its own fight | the condition 0 NPC paired with a condition 1 enemy, vanilla's own pairing on map 11,4 |
| Trunks base versus Super Saiyan | sets 132 and 133 |
| rain, wind or cloud over a map | bible tag `OVL`: one BG0 record plus the layout's BLDCNT, EVA and EVB |
| a custom game-over card | game-over record `rom:0x3B6104` already branches on the map |
| a level gate with a refusal message | the Cell Games barrier, `ext 22` at `rom:0x408DD4` |
| telling the player the time machine is live | the journal, 43 entries of 16 bytes at `rom:0x6D68DC`, each with a done script and an active script. Entry 0 is already "Talk to Dende on the Lookout" |

## The level gate: SOLVED, and vanilla does it already

My earlier claim that no op reads a level was wrong. Bible row `B0624` held the answer.

**`ext 22` reads a character's level.** The Cell Games barrier already gates on it, decoded from the
base ROM at `rom:0x408DD4`:

```
push 4 ; ext 22      level(Goku)
push 39 ; gt         > 39, so level 40
and                  AND the leader is Goku
test_flag 195
```

Ours is the same shape with the character changed: `push 3 ; ext 22 ; push 39 ...` for Trunks. The
paired barrier object carries the refusal line, so the message, the test and the blocking object are
one copyable pattern.

**The number is 35, not 40, and the reason is measured.** Trunks lands at **level 29** on the vanilla
path: level 27 scripted at `flag:129`, +1 from the Time Chamber, then 40,000 and 50,000 EXP from his
two forced fights. EXP goes only to the leader (`B1863`), and Trunks leads for those two fights alone.

The raw EXP numbers mislead. `@0x0800E4D2` clamps every ordinary kill to `gap/128 .. gap/2` of the
LEADER's own next-level span, a floor as well as a ceiling, so cost per level is nearly flat however
high you climb. The dial is the number of levels demanded, not the EXP.

| from 29 | levels | kills on weak enemies | kills on a strong group |
|---|---|---|---|
| to 35 | 6 | about 830 | about 23 |
| to 40 | 11 | about 1,470 | about 68 |

35 is one honest training session. 40 doubles it right before the climax.

**Dependency:** the gate only works if Trunks can leave Capsule Corp and reach enemies. Seal him in a
room and the gate cannot be passed.

## The expensive one: the finale blast

Borrowing Vegeta's Big Bang onto Trunks is an effect and an animation crossing characters. It is the only
item here that is art work rather than script work, and it should be costed on its own before rung 7.

## Open, his call

- Is Trunks Super Saiyan for the androids and then base again for Cell, or base from the time machine on?
  The plan says he starts the Cell fight not Super Saiyan; mockup 1 has him transform at word 4.
- Does losing to future 18 or future 17 get its own game-over card, or only Cell? Parked, undecided.
- Cell's lines for the plateau talk. He is supplying them.
- Where the player can train once the gate stops them, and whether the world is open from Capsule Corp.
  Starting Trunks at the Lookout instead would make the walk to Capsule Corp do the levelling by itself.

## Settled today, so nobody re-asks

- The loss path is not a defect: a game over loads map 1,7 at (112,144), never the current map, proved by
  decoding `rom:0x3B6104` to `push_list [1, 7, 1, 112, 144]`.
- The easter egg card wording, no number: `@^Cell takes the time machine into the past...` then
  `@^The nightmare is just beginning.`
- The final arena is our own map. No vanilla map is a clearing: the greenest open area in the game is
  map 10,14 at 36.7% green in a 168x160 rectangle.
- The Gohan flight and the Chi-Chi scene are SCRAPPED (owner, 2026-11-07). Trunks flies away in the
  vanilla ending anyway, so the Cell Games fades straight to playable Trunks at Capsule Corp.
- **NPC Future Gohan must come off the future map.** He is `SOURCE_NPCS[0]` in `future_androids.py`:
  set 54, condition 0, at (216,368), item `rom:0x3ED754`, step `rom:0x3ED74C`. He is a standing NPC and
  nothing drives him. Two independent searches of the whole ending span `rom:0x3B7B08`-`0x3B8140` found
  no op naming set 54: a decode of the 13 code records, and a raw byte scan for `push 54 ; ext N` and a
  zigzag 54 push_list head. A record outside that span, or an op that computes 54 instead of pushing
  it, would not appear in either. Drop him the way the module already drops NPC Trunks.
