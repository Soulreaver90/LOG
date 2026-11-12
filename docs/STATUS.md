# Status

What is finished, what is waiting, and what is still being drawn. Updated whenever a build ships or a
decision lands. `docs\CHANGELOG.md` says what the hack changes. This page says how far along each piece is.

> [!IMPORTANT]
> A thing is only "in the build" when it has been read back out of a built ROM. A file sitting in an art
> or review folder is not in the build. On 2026-10-31 that difference hid twelve days of finished drawings,
> so every art row below names the check that proves it.

---

## Builds

| Build list | What it is | SHA-1 |
|---|---|---|
| `build_list.txt` | Golden master. Finished work only | `acf1b15f` |
| `build_list_dev.txt` | Dev master. Golden plus the gi art being drawn | `ffbd2bfc` |
| `build_list_core.txt` | The 25 shared modules. Both masters include it | not built alone |

Both masters must rebuild to those SHA-1s from a clean ROM. If one does not, something changed that nobody
declared, and the tests say what.

## Code and scenes

Everything in `docs\CHANGELOG.md` is finished, in both masters, and play tested. Nothing is part built.

| Not in a master | State | Next step |
|---|---|---|
| `sprite_lab` | Finished, deliberately kept out | Stays on its own trial list. It is a sprite capture tool, not a game feature |
| `gi_base_audit` | Superseded | It paints 103 reviewed frames. The reviewed set is now 150 and lives elsewhere. Retire it |

## Art: the gi

One of the two unfinished parts, with the Trunks tank top below. Sprite set 157 is base Gohan, 158 is Super
Saiyan, 159 is Super Saiyan 2, 160 is Rage.

| Piece | State | Evidence |
|---|---|---|
| Reviewed frames for set 157 | 150 of 288 records | `art\base-audit\proposed` |
| Of those, signed off | 102 | `art\base-audit\approved`, a strict subset of proposed |
| Never drawn | the whole back view of anim 18, 7 records | see "the back view" below |
| Sets 158 and 159 | Derived from the base body plus the form's head | `gi_one_body.py`, not hand drawn |
| In the golden master | Nothing. Golden uses vanilla pixels | `gohan_gi_vanilla` |

### Coverage by animation, set 157

Where only part of a cycle is reviewed, play mixes new and old frames. That is the art, not a build fault.

| Animation | Reviewed | Note |
|---|---|---|
| 3, 9, 11, 14, 17, 20 | all records | complete |
| 5 | 11 of 12 | |
| 1 | 12 of 16 | never signed off |
| 12 | 12 of 16 | |
| 18, the kamehameha | 21 of 28 | never signed off. The 7 missing are the whole back view |
| 13 | 7 of 16 | never signed off |
| 0 | 3 of 8 | |

### The back view

Vanilla Gohan never lets a frame go dark: zero of its 162 records fall under 2 % bright pixels, in any
direction. The gi does it 33 times, and 29 of those are direction 1, the back. The cause is that the
vanilla armor puts white at the gloves and boots, which stay lit from every angle, and the gi replaced
them with bare hands and dark boots.

Every review sheet leads with direction 0, which is why this went unseen, and why all 7 undrawn kamehameha
records are also the back view. Full working in `docs\tasks\2026-10-31-sprite-diagnosis\`.

**Rule for any new sprite work: no record may sit under 2 % bright pixels, in any direction.**

## Art: the Trunks tank top

Trunks loses the jacket and wears the tank top underneath. Sprite set 128 is base Trunks, 134 is Super
Saiyan. Set 128 holds 288 records and each one has to be drawn by hand.

| Piece | State | Evidence |
|---|---|---|
| Read back out of a built ROM | 20 of 288 records: all 8 of anim 0, the 8 side walk records of anim 1 dirs 2 and 3, and the 4 anim 4 index 2 records | r4, ledger 2026-11-01 6:40 PM |
| Covered by art and the manifest | 24 of 288 records, the 20 above plus the 4 down walk records | `art\trunks_tank\manifest.json`, 13 rows, 16 headers, 24 keys |
| Anim 1 dir 0, the down walk | 4 frames drawn, approved by eye 2026-11-02, promoted into `art\` and the manifest, NOT yet in a ROM | `trunks_tank_base_front_walk_0..3.png` |
| The three front stand frames | Gained the 3 px scabbard end, 2026-11-02 | originals in `archive\backups\2026-11-02_pre-scabbard\` |
| Everything else | Still the jacket | anim 1 dir 1, and every combat, fly, crouch and special row |

> [!WARNING]
> The down walk is WIRED but UNBUILT. The manifest now names the four headers `0x34FF9C`, `0x3500A8`,
> `0x3501C0` and `0x3502D0`, and `_check_manifest` passes against the vanilla ROM, so a trial build would
> pick them up. Nothing has been read back out of a ROM yet, because he asked for no trial ROM on
> 2026-11-02. Per the note at the top of this page, that means they are not "in the build".

Anim 14, the sword draw idle, plays during a long stand and is still the jacket. `docs\sprite-guide.md`
holds the drawing rules this set taught us, and its pre-flight checklist is the thing to run first.

## Open decisions

| Question | Why it is open |
|---|---|
| Does the derived Super Saiyan body read correctly? | Needs a play test |
| One colour, `(248,200,192)`, is not in the game palette | 16 pixels across 4 anim 9 frames. Mapped to the top of the skin ramp those frames already use. The nearest entry by distance is a pink, not a skin tone |
| How reviewed art reaches the build | Done by hand today. It needs one route in, and a test that fails when signed-off art is missing from the build art |

## Carried work

Small things with no deadline: stale docstrings in five modules, the build script's ROM write is not an
exclusive create, seven alias build lists that could be deleted once nothing names them, and dead path
references inside dated reports.

## How to check an art claim yourself

`scripts\one-time\2026-10-31-gi-v2\sweep_art_against_build.py` compares every per frame PNG under `art\`
against the art the build actually reads, and prints what is not in. Run it before believing any row above.
