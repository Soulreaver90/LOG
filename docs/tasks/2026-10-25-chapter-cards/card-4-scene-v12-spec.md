# Card 4 v12: move the whole scene to the default landing (final, 2026-10-31, with two annotated screenshots)

I: "card 4 is a mess. Lets use the default landing location, not the save point since its complicating
everything." He marked the open ground with red boxes on two mGBA screenshots. Those images are in the session, not
on disk, so the box geometry below is my reading of them and must be confirmed against the map before
anything is built.

## The change of ground

Stop landing near the save point. Use the **vanilla landing `LAND = (8,1,1,272,128)`**, the spot every later landing
already uses. Bible row 1114: map 8,1 region 0 is an always-on A-press rect (249,89)-(296,144) that holds the
landing point 272,128 and returns the player to the world map. That region is where the game itself puts the player,
so standing there is normal, and it is **not** a flight pad. An earlier probe script mislabelled it and the
My repeated that error to me; the C4E bible row has been corrected.

This removes the save point rect (56,48)-(105,97) from the problem entirely, which is what made v9 to v11 fight.

## My layout, per branch

He named three areas from my screenshot: a wide **top box**, a **far left box**, and the ground immediately
**beside the landing**.

| Leader | Landing / player | Far left box | Top box | Notes word for word |
|---|---|---|---|---|
| **Vegeta** | Vegeta lands; "trunks lands next to him" | **Gohan**, alone | **The trio**: Piccolo, Tien, Krillin | "have piccolo a bit lower and tien and krillen facing eachother, as if all 3 were talking" |
| **Piccolo** | Piccolo at his spot, with "krillin/tien to either side of piccolo, both facing him" | **Gohan**, same location as the Vegeta branch | **Vegeta and Trunks** ("in the box that the trio was in") | |
| **Gohan** | "gohan is alone at the landing/map point" | **Vegeta and Trunks** ("where gohan was") | **The trio**, "at the top like in vegeta" | |

Note: he wrote "piccolo/tien/trunks" for the Vegeta-branch trio. Trunks is beside Vegeta in that same sentence, so
read it as **Piccolo, Tien, Krillin**. Confirm with him if the build makes that reading look wrong.

## What must be worked out, not assumed

- The three areas must be found from the map data around (272,128), not from pixel positions in my screenshots.
  Use `map_view` and the clear-ground probe, then show him a plan picture per branch **and** a real capture.
- The camera for this part of the map is not the one v9 to v11 used. Re-derive the clamp.
- The text box still covers the bottom of the view, so no actor may sit where it draws.
- Keep every rule that still applies: no actor under a BG1 canopy, every fly-in and fly-off path clear, groups
  readable as groups.

## Gate

Capture all three branches with the capture loop and read every actor's spot and facing out of RAM, the same way as
v11. I see real frames, not plan pictures alone.

## Blocked until

The `repo-prep` task is moving the permanent tools into `rom\`, `art\` and `scene\` and rewriting imports. It may
touch `chapter_cards.py` import lines. Do not start v12 until it has reported and I have verified its
byte-identical gate.

---

# Brief (the sections above are the spec; these are the working rules)

**The permanent tools moved this morning.** They
are now `scripts\permanent\rom\`, `art\`, `scene\` and `emu\`; `log2_build.py`, `log_paths.py` and every
`build_list*.txt` stayed at the permanent root. Use `scene\map_view.py`, `scene\scene_lib.py` and `emu\capture.py`.
Read `docs\playbooks\capture-playbook.md` and `docs\playbooks\scene-playbook.md` before you start.

## Task

1. Move the card 4 arrival to the vanilla landing `(8,1,1,272,128)` and lay out all three branches as the table
   above says. Work the three areas out from the map data around (272,128) with `map_view` and a clear-ground probe.
   **Do not take coordinates off my screenshots:** the window is scaled, and a pixel guess is what put the
   team in the trees in v9.
2. Re-derive the camera for this part of the map. The v9 to v11 clamp does not apply here.
3. Keep the rules that still hold: no actor where the text box draws, none under a BG1 canopy, every fly-in and
   fly-off path clear, each group readable as a group.
4. Build `builds\mockups\2026-10-25-chapter-cards\log2_poc_r40_chapters_v12.gba` from
   `build_list_trial_chapters.txt` (check absent first). `.sav` an exclusive byte copy of the v11 save.
5. Update `test_chapter_cards.py` for every new spot and facing. No test may be weakened.
6. **Gate: capture all three branches yourself with `emu\capture.py` and read every actor's spot and facing from
   RAM.** Put the three frames and the RAM table in the report. A plan picture alone is not enough any more.

## Report

Short. `docs\tasks\2026-10-25-chapter-cards\card-4-scene-v12-report.md`: SHIPPED and PENDING tables, the SHA-1, a
spot-and-facing table per leader, the capture paths, the test count. Label every claim C, L or S. Bible rows (tag
C4M) in `scripts\one-time\2026-10-31-card-4-v12\bible_rows.md` as `## Section N` table blocks.

## Limits

- Edit only `chapter_cards.py` and `test_chapter_cards.py`. Python: `py -3.14 -P`. Never write under `data\`. Never
  overwrite a ROM or save. LF, no em or en dashes, no byte order mark.
- Never `cd`, `Set-Location` or `Push-Location`. Use absolute paths in every command and in every script that opens
  a file. **Seven tasks in a row have broken this. Do not be the eighth.**
- Do not touch `docs\RE-BIBLE.md`, `docs\ledger\`, `zhack\`, any build list, or anything under `scripts\permanent\`
  other than reading. Do not run the full suite.

