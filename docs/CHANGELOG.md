# What this hack changes

Every difference between this build and a clean Legacy of Goku II ROM. One line per change, with the patch
module that makes it and the build it first appeared in.

Nothing here is a general improvement to the original game. Each item exists to make the two games read as
one story, or because the merged story needs it.

> [!NOTE]
> Builds are numbered `rN`. The number rises every time the main build list changes. `docs\build-log.md`
> records every ROM ever built with its SHA-1.

---

## Gohan's outfit and forms

| Change | Module | Build |
|---|---|---|
| Gohan wears the purple gi once the player controls him after the Time Chamber, and as Rage in the Cell fight | `gohan_gi` | r7 |
| Super Saiyan 2 is a usable form for Gohan after the story reaches the Cell Games | `ssj2_form` | r6 |
| The Super Saiyan 2 and Rage auras cycle their shapes on the idle tick instead of standing still | `ssj2_idle` | r9 |
| Rage adds +20 to STR, POW and END, the same as playable Super Saiyan 2 | `rage_stats` | r19 |
| The Cell fight message reads "Gohan has transformed into Super Saiyan 2!" | `rage_text` | r12 |
| Goku and Gohan stay Super Saiyan from the Time Chamber until Cell is beaten | `fullpower_ssj` | r28 |
| Gohan and Goku appear in Super Saiyan through the Cell Games | `cellgames_ssj` | r27 |
| Super Saiyan ki no longer drains while a cutscene plays | `scene_drain_pause` | r27 |

## Portraits and the status page

| Change | Module | Build |
|---|---|---|
| Playable Gohan has gi portraits in base, Super Saiyan and Super Saiyan 2 | `gohan_portraits` | r7 |
| Cutscene dialog uses the gi portraits once Gohan's record wears the gi | `cutscene_portraits` | r12 |
| Cutscene Gohan wears the armor before the chamber and the gi after | `npc_gi` | r12 |
| The status page shows the dialog portrait, in the dialog colours | `status_portrait` | r19 |
| The status page shows the form bonus as a gold bar segment on a 125 point scale | `status_bonus` | r9 |
| Art tables are written into the ROM: palette entries and dialog portraits | `art_inject` | r20 |

## Heads up display

| Change | Module | Build |
|---|---|---|
| The player HUD and the boss bar use the Buu's Fury look | `bf_hud` | r39 |
| One Super Saiyan ki pool, drawn yellow over the EP row, in the Buu's Fury style | `bf_ki_pool` | r39 |
| Full power Super Saiyan shows the yellow ki row and runs no aura loop for Goku or Gohan until Cell is beaten | `fullpower_hud` | r40 |
| A scripted fighter change clears the party transform cooldown | `relay_cooldown` | r40 |

## Story scenes

| Change | Module | Build |
|---|---|---|
| On Dende's Lookout, Piccolo gives Super Saiyan Gohan his gi | `piccolo_gi_scene` | r29 |
| Cell returns from the self destruct as Super Perfect Cell, with Super Saiyan 2 bolts | `superperfect_cell` | r30 |
| A beam struggle plays out on the Cell Games map | `beam_struggle` | r40 |
| Vegeta goes Super Saiyan when he attacks Super Perfect Cell | `vegeta_ssj_scene` | r40 |
| Vegeta goes Super Saiyan after his line to Android 19 | `vegeta_19_reveal` | **r41** |
| Cell spawns seven Cell Jrs. Gohan fights four at once as Super Saiyan 2, then Cell | `celljr_fight` | **r41** |
| A chapter title card appears at each chapter's story point | `chapter_cards` | **r41** |

## Prototypes, reachable in play

| Change | Module | Build |
|---|---|---|
| A sparring fight, Gohan in Demon Clothes against Goku, in the Capsule Corp basement | `chamber_spar` | r37 |

---

## Not in the golden build

The golden build (`build_list.txt`) uses finished art only. Two things are kept out of it on purpose.

| Item | Where it lives | Why |
|---|---|---|
| The gi sprite art | `build_list_dev.txt`, through `gohan_gi` | The drawings are not finished. The golden build relocates the same sprite sets and leaves the pixels vanilla, through `gohan_gi_vanilla`, so both builds stay structurally identical |
| `sprite_lab`, a flat capture field | `build_list_trial_spritelab.txt` | A tool for reviewing sprites, not something a player should reach |

## How a build is put together

The base ROM is never edited by hand. A build list names patch modules and the order to apply them, and
the build script starts from a clean ROM every time. The same list always produces the same file, byte for
byte, so a change that was not intended shows up as a different SHA-1.

    py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list.txt --out <name>.gba --log <name>.md
