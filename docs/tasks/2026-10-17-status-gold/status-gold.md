# Status screen: show the form bonus as a gold bar segment on a 125 scale (me, 2026-10-17 10:14-10:20 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Read `docs\research\research-status-screen.md` in full first. It maps the USA status page `0x0800379C`, the Europe fix, the blit, the bar image and the palette, with addresses and labels. Sources: `scripts\one-time\2026-10-17-status-screen-research\status_usa_379c.txt`, `status_eu_e3cc.txt`.

## Final decisions

1. **Gold segment.** STR, POW and END bars draw the base value as now, and the form bonus (live minus base, never below 0) as a gold segment after it.
2. **125 scale.** A full bar is 125 points. Vanilla is 4 points a segment with `w = 75 if v > 100 else (v >> 2) * 3`. On a 125 scale one 3 px segment is 5 points: `w = min(v, 125) / 5 * 3` (integer). Base 100 = 60 px; base 100 + 20 = 72 px. HP and EP bars do not change.
3. The number text: the vanilla text is "%d/100". With a bonus, "120/100" reads like an error. Propose the exact text (for example the live value alone, or base plus bonus) in the report. Keep the vanilla font and color, and do not widen the text past its current box.

## Task (research-status-screen.md section 5, tasks 2, 3, 5, 4 in that order)

1. Relocate the status page behind a long-jump veneer at `0x0800379C` into the expansion area. First build: byte-identical behavior (no visible change). Every call back into base code goes through a long call. Prove each relocated BL and literal against the listing.
2. Europe player lookup: live values from the player object even while the menu is open (section 2.3), so the number and the bar can include the bonus.
3. Reapply form stats after a stat item used in the menu (EU `0x080159FC` pattern), so live never lags base.
4. Gold segment and 125 scale: base part with the vanilla bar image, bonus part with a gold image (draft `scripts\one-time\2026-10-17-status-screen-research\gold_bar_75x8.bin`, menu palette indices 82 and 69; no palette change). Check the contrast against the yellow middle of the bar and pick the gold that reads best. Put the choice and a mock in the report.
5. New patch file `scripts\permanent\patches\status_bonus.py` in the style of the other patches (header block, `_expect` old-bytes checks, `apply(rom, alloc)`, notes). It runs after `ssj2_form`. Add tests `scripts\permanent\tests\test_status.py`: veneer bytes, relocated page integrity (every BL target and literal), bar width formula at 0, 4, 5, 99, 100, 120, 125, 126, 127, base 8 MB differs only at the veneer site, palette unchanged.
6. Run the whole suite: `py -3 -I -m unittest discover -s scripts\permanent -p "test_*.py"`.
7. Build a check ROM to a NEW path I give you in the dispatch. Append the build line to `docs\build-log.md`.
8. Update `docs\research\research-status-screen.md` (what is built, status of each section 5 task) and the RE-BIBLE rows. Describe the system as it is, with no history wording.

## Limits

- Never write under `data\`. Never overwrite any existing ROM in `builds\`. Do not touch `art\`.
- No palette is written. Install nothing. Python files: LF line ends, no byte order mark, no em or en dashes.
- Label findings CONFIRMED, LIKELY or SPECULATIVE with quoted evidence.
- If the relocation cannot be proven safe (an unresolved call, a computed branch), stop and report instead of guessing.

## Report

Save it as `docs\tasks\2026-10-17-status-gold\status-gold-report.md`: changes (file:line), veneer and relocated addresses, the bar formula, the text format chosen, the gold choice with a mock path, test count, ROM SHA-1, and my test plan (which save state, which screen, what to expect in base, Super Saiyan and Super Saiyan 2). Then reply with status and a 3-line summary only.

