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
| CHM-1 | **IN** | Goku and Gohan stay Super Saiyan from the chamber until Cell is beaten. No drain, no revert at zero ki. |
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
| FUT-6 | **PLAY** | The scouter reads Future 17, Future 18 and Future Cell by name, with their own weakened stats, instead of showing nothing. |
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
| XFM-9 | **OPEN** | Does Piccolo's base form deserve a yellow bar at all, since it is only him dropping the turban? You were leaning to plain green for base, yellow for the power-up. |
| XFM-10 | **OPEN** | Two versions of Vegeta Z+ exist. One unlocks it through the Time Chamber exit using the game's own data. The other gives his power-up your drawn frames. Both are saved. Which wins, or do they combine? |

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
| ART-1 | **IN** | Gohan's gi across all four sets, including the aura shapes cycling on the idle. |
| ART-2 | **PLAY** | **Trunks wears the tank top** instead of the jacket, in both forms, with no scabbard and no strap. |
| ART-3 | **IN** | Your drawn power-up frames are in the ROM for both Vegeta and Piccolo. |
| ART-4 | **IN** | All 89 vanilla portraits exported, and the portrait kit rebuilt on the right background model. |
| ART-5 | **OPEN** | The dust colour Buu's Fury uses at the end of a transformation, grey or tan. Not settled. |

---

## What is waiting on you, in one place

1. **Push the repository.** 68 commits exist on this disk only, including every drawing now tracked.
2. **FUT-10, the Trunks hand-off**, Gohan at the tower to controlling Trunks. The ending needs it.
3. **Play the future line (FUT-1 to FUT-9)** and the Z+ pair (XFM-5 to XFM-8), and say what is wrong.
4. **The builds delete list**: 455 files, 2.13 GB.
5. **XFM-9**, Piccolo's base bar: green or yellow.
6. **XFM-10**, which Vegeta Z+ wins.
7. **Rename the Trunks tank art folder?** It is your live folder, so nobody touches it.

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
| XFM-9 | |
| XFM-10 | vegeta_zplus |
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
