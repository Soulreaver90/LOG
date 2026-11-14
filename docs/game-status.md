# LOG: what is in the game

What the hack does, in the order you play it. No code, no file names. The machinery is in
[status.md](status.md).

Every item has a **reference code**. The same code appears in `status.md` against the modules that
build it, so you can go from "what the player sees" to "what makes it happen" and back. The mapping
lives once, in the Reference table at the bottom of this page, and `make_status.py` reads it from
there. Nothing else holds it, so the two pages cannot disagree.

Written by hand and updated as work lands. If something here is wrong, it is wrong because I did not
update it, not because the game changed.

**Key**

| Mark | Meaning |
|---|---|
| **IN** | Built into a master. Played and approved. |
| **PLAY** | Built as a trial ROM. Waiting for you to play it. |
| **DESIGNED** | Decided, written down, not built yet. |
| **OPEN** | Not decided. Waiting on you. |

---

## 1. The Android saga

| Code | | What happens |
|---|---|---|
| AND-1 | **IN** | Vegeta goes Super Saiyan after his line to Android 19, as a scene. No permanent form, no ki kept. |

---

## 2. The Lookout and the gi

| Code | | What happens |
|---|---|---|
| LKT-1 | **IN** | Piccolo gives Super Saiyan Gohan his gi on Dende's Lookout, as a scene. |
| LKT-2 | **IN** | Gohan wears the purple gi once he is playable after the chamber: base, Super Saiyan, Super Saiyan 2 and Rage, with matching portraits in cutscenes and on the status page. |
| LKT-3 | **IN** | Cutscene Gohan keeps the armour until you take control, then wears the gi. |

---

## 3. The Time Chamber

| Code | | What happens |
|---|---|---|
| CHM-1 | **IN** | Goku and Gohan stay Super Saiyan from the chamber until Cell is beaten. No drain, no revert at zero ki. Goku turns Super Saiyan as he LEAVES the chamber, not as he enters it (your call, 2026-11-13). |
| CHM-2 | **IN** | A sparring fight, Gohan against Goku, in the Capsule Corp training room. This is the first step toward real Time Chamber fights. |
| CHM-3 | **DESIGNED** | Proper Time Chamber fights. The spar proves the shape works. |

---

## 4. The Cell Games

| Code | | What happens |
|---|---|---|
| CGS-1 | **IN** | Goku is Super Saiyan from the moment he arrives until he dies, as an NPC and when you control him. |
| CGS-2 | **IN** | Gohan is Super Saiyan through the Games, and his energy refills when the Cell fight starts. |
| CGS-3 | **IN** | Gohan can use Super Saiyan 2 after the story reaches it, with the +20 stat bonus and the right message: "Gohan has transformed into Super Saiyan 2!" |
| CGS-4 | **IN** | Cell spawns seven Cell Jrs. You fight one, then three at once, then three more end in a scene before "You wretched child". |
| CGS-5 | **IN** | Cell comes back from the self-destruct as Super Perfect Cell, with Super Saiyan 2 bolts. |
| CGS-6 | **IN** | Vegeta goes Super Saiyan when he attacks Super Perfect Cell. |
| CGS-7 | **IN** | The final Cell scene has the grand beam struggle, drawn as map art. |

---

## 5. The Future Trunks ending

This is the biggest single line of work and it is close to done.

| Code | | What happens |
|---|---|---|
| FUT-1 | **PLAY** | The cutscene where Trunks beats Future 18 and Future 17 is now **two real fights**, one after the other, and you control Trunks from the moment the scene reaches that map. |
| FUT-2 | **PLAY** | The cutscene where Trunks kills Imperfect Cell is now **a real fight**. Cell keeps his own stats and the ki blast still finishes him. |
| FUT-3 | **PLAY** | That fight happens in **Capsule Corp in the rain**, a custom arena map built for it. |
| FUT-4 | **PLAY** | The Cell battle is **two parts**. Round two moves to **your own hand-made plateau map**, with its own dialogue and its own ending. |
| FUT-5 | **PLAY** | The last beat: Trunks fires a gold beam straight up, Cell takes three hits with explosions and screen rumble, then explodes. |
| FUT-6 | **PLAY** | The scouter reads Future 17, Future 18 and Future Cell by name, with their own weakened stats, instead of showing nothing. **New on 2026-11-14:** all three now also appear in the scouter **database list**, which was built for exactly 128 names and had no room for them. Two things there need your eye, because no test can see them: that the menu opens at all, and that scrolling reaches all 131 rows. |
| FUT-7 | **PLAY** | Trunks keeps a full Super Saiyan pool going into the Cell fight, instead of carrying the energy he spent on the androids. |
| FUT-8 | **PLAY** | Capsule Corp carries the goal star on the world map once the main story is over, like every other major quest. |
| FUT-9 | **PLAY** | Lose to Cell in the final arena and the game-over screen shows your own card instead of "You have died!". |
| FUT-10 | **OPEN** | **The hand-off.** The transition from the end of the game, Gohan at the tower, to taking control of Trunks. This is the piece that ties the ending together and it is not built. |

---

## 6. Transformations

| Code | | What happens |
|---|---|---|
| XFM-1 | **IN** | One Super Saiyan ki pool, drawn over the energy row in the Buu's Fury style. |
| XFM-2 | **IN** | Full-power Super Saiyan shows the yellow ki row, and Goku and Gohan lose the aura sound loop. |
| XFM-3 | **IN** | Ki does not drain while a scene plays. |
| XFM-4 | **IN** | A scripted fighter change clears the party transform cooldown. |
| XFM-5 | **PLAY** | **Vegeta Z+**, a second Super Saiyan grade reached from Super Saiyan. |
| XFM-6 | **PLAY** | **Piccolo Z+**, a grade above Super Namek, with his own icon and your Kami portrait. Z+ gives +10 and healing; plain Z gives +6 and none. |
| XFM-7 | **PLAY** | The power-up plays the **Buu's Fury aura**, gold for Vegeta and white for Piccolo, with ground dust. It starts on the charge loop so the wind-up stays clean, and an interrupt takes it away. |
| XFM-8 | **PLAY** | The ki bar **ramps up** while the transformation plays instead of appearing full at the end. |
| XFM-9 | **PLAY** | Piccolo's bar: plain green for base AND for Super Namek, with no ki pool. Only Z+ gets a pool, and it ramps to yellow and stays yellow. Built 2026-11-13. The cause was that Super Namek and Z+ share one form object, so the bar could not tell them apart. It now asks which appearance entry you are in. Super Vegeta and Gohan's Super Saiyan 2 keep their orange pool. |
| XFM-10 | **OPEN** | Two versions of Vegeta Z+ exist. One unlocks it through the Time Chamber exit using the game's own data. The other gives his power-up your drawn frames. Both are saved. Which wins, or do they combine? **The live module today is the drawn frames one, and it has no story gate at all: Z+ is available whenever Super Vegeta is.** That is the one any build carries right now. |
| XFM-11 | **OPEN** | **Trunks Z+**, the same second grade Vegeta has. **Waiting only on your drawing** of his grade 2 portrait. The portrait id that was believed to block this is NOT a blocker: measured 2026-11-14 in the r44 ROM, the live portrait list already runs to id 123, and Vegeta Z+ and Piccolo Z+ each added their own. Id 124 is free and the method is proven twice. |

---

## 7. Presentation

| Code | | What happens |
|---|---|---|
| PRS-1 | **IN** | Chapter title cards at each chapter's story point, on a new game and on Continue, in the Buu's Fury style. |
| PRS-2 | **IN** | The status page shows the form bonus as a gold bar, and the portrait in the dialog colours. |
| PRS-3 | **IN** | The second ki bar is **orange**, not red. |
| PRS-4 | **IN** | The player HUD and the boss bar use the **Buu's Fury look**. |
| PRS-5 | **OPEN** | Unselected characters on the file select and Switch Characters keep a skin-coloured dim. This is **written and tested but wired into no build**, so nobody has ever seen it. Do you want it in? |

---

## 8. Art

| Code | | What happens |
|---|---|---|
| ART-1 | **IN** | Gohan's gi across all four sets, including the aura shapes cycling on the idle. Part drawn: see the coverage below. |
| ART-2 | **PLAY** | **Trunks wears the tank top** instead of the jacket, in both forms, with no scabbard and no strap. Part drawn: see below. |
| ART-3 | **IN** | Your drawn power-up frames are in the ROM for both Vegeta and Piccolo. |
| ART-4 | **IN** | All 89 vanilla portraits exported, and the portrait kit rebuilt on the right background model. |
| ART-5 | **OPEN** | The dust colour Buu's Fury uses at the end of a transformation, grey or tan. Not settled. |

> [!IMPORTANT]
> A drawing is only **in the game** once it has been read back out of a built ROM. A file sitting in an
> art folder is not in the game. On 2026-10-31 that difference hid twelve days of finished drawings.

### ART-1, the gi: how much is actually drawn

Set 157 is base Gohan, 158 Super Saiyan, 159 Super Saiyan 2, 160 Rage. Where only part of a cycle is
reviewed, play mixes new and old frames. That is the art, not a build fault.

| Piece | State |
|---|---|
| Reviewed frames, set 157 | 150 of 288 records |
| Of those, signed off by you | 102 |
| Never drawn | the whole back view of the kamehameha, 7 records |
| Sets 158 and 159 | derived from the base body plus the form's head, not hand drawn |
| In the golden master | nothing: golden uses vanilla pixels |

Complete cycles: animations 3, 9, 11, 14, 17 and 20. Part done: 5 (11 of 12), 1 (12 of 16), 12 (12 of 16),
the kamehameha (21 of 28), 13 (7 of 16) and 0 (3 of 8). The kamehameha, 1 and 13 were never signed off.

**The back view is the weak spot.** Vanilla Gohan never lets a frame go dark: 0 of its 162 records fall
under 2 per cent bright pixels. Our gi does it 33 times, and 29 are the back. Every review sheet leads
with the front, which is why it went unseen, and why the 7 undrawn frames are also the back. The rule
that came out of it now lives in [sprite-guide.md](sprite-guide.md).

### ART-2, the Trunks tank: how much is actually drawn

Set 128 is base Trunks, 134 Super Saiyan. Set 128 holds 288 records and each is drawn by hand.

| Piece | State |
|---|---|
| Read back out of a built ROM | 20 of 288 records |
| Covered by art and the manifest | 24 of 288 |
| The down walk, 4 frames | approved by eye 2026-11-02, wired, **never built** |
| Everything else | still the jacket: the side stand, and every combat, fly, crouch and special row |

The sword draw idle plays during a long stand and is still the jacket.

**To check any art claim here yourself:** `scripts\one-time\2026-10-31-gi-v2\sweep_art_against_build.py`
compares every frame PNG under `art\` against the art the build actually reads, and prints what is not in.

---

## What is waiting on you, in one place

1. **Play the rough master.** `builds\mockups\2026-11-13-rough-master\log2_poc_r44_rough.gba`, with its
   save beside it. It is the dev master plus the whole future Trunks line and the whole Piccolo and
   Vegeta Z+ line, 41 modules.
   - Check **Piccolo's bar** first: base green, Super Namek green, Z+ ramping to yellow and staying yellow.
   - Then open the **scouter database list**. It was rebuilt overnight to hold 131 names instead of
     128, so Future 17, Future 18 and Future Cell can appear in it. Two things only your eye can
     answer: does the menu open at all, and does scrolling reach all three new names at the bottom?
   - `log2_poc_r43_rough.gba` beside it is last night's earlier build, before the scouter list work.
     Play r44.
2. **Push the repository.** 115 commits exist on this disk only, including every drawing now tracked.
3. **FUT-10, the Trunks hand-off**, Gohan at the tower to controlling Trunks. The ending needs it.
4. **The journal's 44th quest. I now recommend REPLACING one line, not growing the menu.**
   We measured the quest table and it has exactly one reader in the whole game, which I confirmed
   myself two ways. Nothing counts your quests, checks them for an ending, or looks one up by
   number. A journal entry is a line of text on a page, and nothing else.
   So replacing one costs you one vanilla line, and the obvious one to give up is
   "Talk to Dende on the Lookout". Growing the menu still works and still costs eight edits, but
   nothing forces it yet, and if it is ever wrong it corrupts a late save silently.
   Say replace, or say grow, or say keep all 43 and drop the idea.
5. **The builds delete list**: 455 files, 2.13 GB.
6. **XFM-10**, which Vegeta Z+ wins. The live module today is the drawn frames one, with no story gate.
6b. **Trunks Z+ needs one drawing from you**, his grade 2 portrait. Nothing else blocks it: the portrait list has room and the build method is proven. See XFM-11.
7. **Rename the Trunks tank art folder?** It is your live folder, so nobody touches it.
8. **The HUD mockup ruling, which is mine and you can overturn.** The orange Super Saiyan ki bar
   replaced the ki bar of the HUD mockup you approved on 2026-10-24. I ruled that the orange bar
   wins, because it is newer and you play with it. So four tests that said the build still matches
   that mockup whole were rewritten to claim only what is still true. The HUD itself is untouched
   and ships exactly as approved. If you want the mockup's ki bar back instead, say so and the
   orange bar comes out.

---

## Reference: which modules build each item

This table is the ONE place the mapping lives. `make_status.py` reads it and writes the same codes
into `status.md`, and it reports any code naming a module that does not exist, and any module no code
claims. A code with no module is not built yet.

`DEV-1` is not a player feature. It is the developer-only builds, listed so the health check does not
report them as modules nothing claims.

| Code | Modules |
|---|---|
| AND-1 | vegeta_19_reveal |
| LKT-1 | piccolo_gi_scene |
| LKT-2 | gohan_gi, gohan_portraits, status_portrait, cutscene_portraits, ssj2_idle |
| LKT-3 | npc_gi |
| CHM-1 | fullpower_ssj, fullpower_hud |
| CHM-2 | chamber_spar |
| CHM-3 | |
| CGS-1 | cellgames_ssj |
| CGS-2 | cellgames_ssj |
| CGS-3 | ssj2_form, rage_stats, rage_text |
| CGS-4 | celljr_fight |
| CGS-5 | superperfect_cell |
| CGS-6 | vegeta_ssj_scene |
| CGS-7 | beam_struggle |
| FUT-1 | future_androids |
| FUT-2 | ending_fight |
| FUT-3 | battle_arena |
| FUT-4 | plateau |
| FUT-5 | finale_blast |
| FUT-6 | scouter_future |
| FUT-7 | pool_refill |
| FUT-8 | worldmap_star |
| FUT-9 | gameover_card |
| FUT-10 | |
| XFM-1 | bf_ki_pool |
| XFM-2 | fullpower_hud |
| XFM-3 | scene_drain_pause |
| XFM-4 | relay_cooldown |
| XFM-5 | vegeta_zplus |
| XFM-6 | piccolo_zplus, piccolo_z_start |
| XFM-7 | powerup_fx |
| XFM-8 | ki_ramp |
| XFM-9 | piccolo_zplus, ki_ramp |
| XFM-10 | vegeta_zplus |
| XFM-11 | |
| PRS-1 | chapter_cards |
| PRS-2 | status_bonus, status_portrait |
| PRS-3 | bf_ki_pool |
| PRS-4 | bf_hud |
| PRS-5 | file_select_dim |
| DEV-1 | sprite_lab, gi_base_audit |
| ART-1 | gohan_gi, gohan_gi_vanilla, ssj2_idle |
| ART-2 | trunks_tank |
| ART-3 | piccolo_powerup_art, vegeta_zplus |
| ART-4 | art_inject |
| ART-5 | |
