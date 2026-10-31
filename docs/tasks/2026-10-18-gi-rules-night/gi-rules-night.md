# gi_art.py: shoes, shading, torso shape and step lighting from the new goldens (approved 2026-10-17/18)

Personal GBA ROM hack (Legacy of Goku II). `scripts\permanent\art\gi_art.py` converts teen Gohan's armored sprite sets (56 base, 59 Super Saiyan, 58 Super Saiyan 2) into purple gi frames: `py -3 -I scripts\permanent\art\gi_art.py all` writes `art\gi_base\`, `gi_ssj\`, `gi_ssj2\`. Read its header, `docs\RE-BIBLE.md` (search "gi_art") and `docs\tasks\2026-10-17-gi-fix-step\gi-fix-step-report.md` (the last change to this file) first. I am asleep: you work unattended, so verify everything by eye and by test before you report.

## Ground truth: the 12 golden frames (read-only)

`art\golden\golden_gi_{base,ssj,ssj2}_d{0,1,2,3}.png` (d3 is the mirror of d2). I drew or approved every one tonight. They define the target look of every gi frame:

1. **Shoes.** The armor's tall boots became small shoes like Piccolo's (set 104): each shoe keeps its bottom 2 rows, a dark hem row (index 211) ends the trouser leg above it, and the rows above that are trouser. Prototype: `art\golden\work_r3\shade\rules.py` `shoes2` (the hem covers only the columns under trouser; a toe sticking out in profile stays shoe). The base side golden is my own hand version (toe forward on the hem row); compare.
2. **Shading rule C.** Every gi pixel (88, 89) becomes the base 89; per horizontal run of gi pixels: n = 2 lights the left pixel (88), n = 3-4 the left-centre pixel, n >= 5 even rows the centre pixel and odd rows the n - 2 middle pixels; a gi pixel on the row above a gap between the legs becomes 211. Prototype: `shade_c` in `art\golden\work_r3\shade\shade_c_mock.py`. I hand-edited the torso rows of the base goldens, so the goldens win where they differ.
3. **Torso and straps** (my base front, back and side, carried to SSJ and SSJ2): the gi strap goes over the top of each shoulder (strap tops 211 on the chin row at the neck edges; strap pixels 89 on the shoulder row), the torso outline beside the arm becomes the arm's own outline (rounder chest), and the chest V has 211 lines. Compare the goldens with their backups in `art\golden\work\backup_2256\`, `backup_2317\`, `backup_2345\`, `backup_0005\`, `backup_0010\`, `backup_0015\` to see exactly what changed.
4. **Step lighting** (10:45 PM: "In the transformation, that same lighting lights up further, but it remains flat in your versions"). In anim 9 frames 1-3 of every form (the lit step frames; the armored sources add light-blue 77 highlights there), the gi lights one step further: lit 88 becomes 87, base 89 next to a lit pixel becomes 88.

## Task

1. Implement 1, 2 and 4 as rules in gi_art.py, applied to every frame after the existing conversion. Keep the rules small and named; put each rule's why in one comment line.
2. Implement 3 as a rule where you can: the torso in a frame with the same view and the same torso geometry as the idle frame of its form and dir. Where a pose has a different torso (attacks, lying, flying), apply only what generalises (strap tops on the chin row, arm outline beside the torso) and list those frames. Do not invent art for poses the goldens do not show; report them.
3. The idle slots (anim 0 index 0, dirs 0-3) of gi_base and gi_ssj must equal the goldens byte for byte after `gi_art.py all`. If the converter cannot reach that by rule, put the golden in the idle slot the same way the SSJ2 chain does (`art\golden\work_r3\finish_v2.py`), and say so.
4. Tests in `scripts\permanent\tests\test_gi.py`: one per rule (shoe rows, hem, shading run cases n = 1..6, gap fold, step lighting only on anim 9 frames 1-3, idle slots equal goldens). `test_front_v_matches_golden` fails now because the base front golden changed; update it to the new goldens. Run the whole suite: `py -3 -I -m unittest discover -s scripts\permanent -p "test_*.py"` (97 tests, 96 pass now).
5. Run `gi_art.py all`, then the SSJ2 chain in this order: `art\golden\work_r3\transplant.py`, `finish_v2.py`, `bodyfix.py --apply`, `strips.py`, `transform158.py`, `base_step.py`. Read each header first. Golden idle slots in gi_ssj2_v2 must equal the SSJ2 goldens byte for byte.
6. View the changed frames at 6x on the lime background helper `art\golden\work_r3\sheet.py` (never a gray background: index 13 is gray) next to the armored originals, for every anim of each form. Judge by eye: shoes small, hem present, shading visible, no stray pixels, no gi on skin, belt row unchanged. Fix what you find. Write one strip per anim per form to `archive\2026-10-17-gi-art-rounds\gi-rules-night-work\`.
7. Update `docs\RE-BIBLE.md` rows for gi_art (rules, golden list, tests). Describe the system as it is, with no history wording.

## Limits

- Never edit `art\golden\golden_*.png` or anything under `data\`. Never build a ROM; never touch `builds\`.
- If `art\vanilla-sets\set56|58|59\` files look wrong (size differs from the manifest record), stop and report; re-export from the base ROM only with `scripts\permanent\rom\log2_sprites.py export` into a new folder for comparison.
- Python files: LF line ends, no byte order mark, no em or en dashes. Install nothing.

## Report

Save it as `docs\tasks\2026-10-18-gi-rules-night\gi-rules-night-report.md`: rule changes (file:line), frames changed per form per rule, the poses the torso rule skips, test count, the strip folder, and anything I must look at. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with status and a 3-line summary only.

