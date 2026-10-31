# shared-body-1240: report (pass cancelled, r12 restored)

Status: CANCELLED by me at 3:55 PM ("Just leave r12 as is"). No r13 was built. The tree is back to r12, proven below.

---

## 1. Acknowledgements

This section lists each of my message and what I did with it.

| Time | Message | Action |
|---|---|---|
| 3:15 PM | Power pose for Rage only; snapshot gi_ssj2_v2 to `art\gi_rage\` | Done before any change. `gi_rage` is a byte copy of r12 `gi_ssj2_v2` (162 files with manifest, transplant.json and review\, `diff -r` equal). Kept, as the 3:55 PM message asks. The `golden_gi_ssj2std_*` files were NOT added to `art\golden\`. |
| 3:19 PM | 8.0.3 decided (V under the neck, lifted foot) | Analysed (section 4), not shipped. |
| 3:29 PM | 13.0.3 arm purple | Cause found (section 4), not shipped. |
| 3:34 PM | Sash shift on detransform | Measured on r12 (section 4), not fixed. |
| 3:54 PM | Stop; b7 rule worse than r12 | Stopped. The b7 rule (shoulder pads by trim columns) is reverted with everything else. |
| 3:55 PM | Cancel; restore r12 | Done (section 2). |

---

## 2. Restore and proof

This section shows that the tree equals r12.

- **What changed during the pass:** only `scripts\permanent\art\gi_art.py`. I compared every file against the backup `archive\2026-10-17-gi-art-rounds\shared-body-1240-work\before\` (scripts, tests, patches, the 5 art folders, `docs\RE-BIBLE.md`). The art folders under `art` were never written: every regeneration went to the work folder `shared-body-1240-work\art\`.
- **Restored:** `gi_art.py` from `before\scripts\gi_art.py` (`cmp` equal). The cancelled work copy is kept as `shared-body-1240-work\gi_art_wip_cancelled.py` for reference only.
- **Proof (CONFIRMED by command output):**
  - Suite: `Ran 176 tests ... OK`.
  - `frame_lock.py check --golden`: exit 0, "0 difference(s)".
  - Rebuild in the work folder (`--out` and `--log` in the work folder, r12 patch list `gohan_gi ssj2_form gohan_portraits status_bonus`, no env vars): SHA-1 `50a9f95d8a60351bbda822bb0fb5fa1f219d795b`, equal to r12. I deleted that work ROM after the check. `builds\` and `docs\build-log.md` are unchanged.
  - Pixel compare of `art\gi_base`, `gi_ssj`, `gi_ssj2`, `gi_ssj_v2`, `gi_ssj2_v2` against the backup: 0 differing frames each.
- **Process slip (reported myself):** my first r12 check build ran as `cd <LOG> && py ... log2_build.py`. It wrote only to the work folder and had no other effect. All later commands used absolute paths.

---

## 3. Still bad in r12 (for me to draw)

This section lists every frame I saw as wrong. Sets 158 and 159 have the same defect where noted.

| Frame | Forms | What is wrong | Label |
|---|---|---|---|
| 13.0.0, 13.0.2 (front run) | 157, 158, 159 | Torso all skin: plate top row, fist and arm are all skin, no gi shows | CONFIRMED (my list, my 10x view) |
| 13.0.3 (front run) | 157, 158, 159 | Screen-left shoulder pad is gi purple, so the arm reads as a sleeve | CONFIRMED (3:29 PM, my dump) |
| 8.0.3 | 157, 158, 159 | Purple under the neck where the V belongs; the V sits 2 rows low. The lifted foot's sole reads as navy, the shoe sits low | CONFIRMED (3:19 PM, my dump) |
| 8.2.2 (side) | 157, 158, 159 | Horizontal limb painted as an arm (skin, wristband) | LIKELY a leg (swoosh round its end, one standing leg, a separate back fist) |
| 16.2.4 (side flying kick) | 157, 158, 159 | Sash runs along the kicking leg (12 px) | CONFIRMED |
| 16.2.3, 8.2.0, 8.2.3 | 157 (others by eye not checked) | Sash 9+ px wide, runs past the torso under the arms or leg | LIKELY (seen at 8x) |
| 5.2.2, 8.1.0, 16.1.3, 18.1.0-18.1.2 | 157 | Sash wider than the torso | LIKELY (seen at 6x) |
| 3.0.3, 3.1.3, 3.2.3 (lying) | 157, 158, 159 | Long horizontal sash along the whole body | CONFIRMED |
| 12.0.0-12.0.3 (front, flying) | 157 mostly | Legs all navy with skin columns | CONFIRMED |
| 2.0.3 | 157 | Legs a brown and navy mass (shoe 3-4 rows tall) | CONFIRMED |
| 5.0.2 | 157 | Brown mass at the lower left (4-row shoe on a bent leg) | CONFIRMED |
| 2.2.0, 2.2.2, 2.2.3 | 157, 158, 159 | Poses do not read (already on draw list) | CONFIRMED |
| 1.0.0, 1.0.2, 13.0.0, 13.0.2 | 158, 159 | My walk fixes live in 157 only; SSJ torso skin under the crossing arm | CONFIRMED (my list) |
| 21.d.3 (revert, last frame), all dirs | 158, 159 | Sash one row lower than frames 0-2 and the base idle (section 4.4) | CONFIRMED |
| 8.0.1 | none | I listed it, but the upper limb is the punching arm (it leaves at chin height; pose 8.0.0-8.0.2) and the lower limb is the kicking leg, already gi with a shoe (my 72.png fix). I see no defect | LIKELY |

---

## 4. Findings that are still useful

This section keeps the causes I traced, so a hand fix or a later pass does not start from zero. All are CONFIRMED by part maps and pixel dumps of the r12 converter unless marked.

### 4.1 Converter causes

- **13.0.0 / 13.0.2:** the fist in front of the chest hides the plate and its trim. Only the plate's top row shows (a 1-row white bar under the neck). The converter sorts that bar with the fist as a glove, so `torso_split` never runs and the whole chest is skin.
- **13.0.3:** the white shoulder pad joins the chest plate as one white fill part, so the pad is chest (gi purple). The glove beside it has no sleeve, so nothing marks the pad as arm. In set 59 13.0.3 the glove fill also joins the plate (no grey outline between them), so SSJ sees only 1 glove.
- **12.0.x:** the raised fists' arm line runs from the fist through the head into the legs, so the leg columns get skin. `finish` then turns every gi pixel beside that skin into 211, which is the navy.
- **Sash (16.2.4, 3.x.3, 8.2.0, 8.2.3, 16.2.3):** frames without a torso split (side views, lying) paint the whole waist row. On a lying body the waist row runs along the body.
- **2.0.3 / 5.0.2:** the 4-row front shoe rule (`shoe_top`, made for my walk front foot) fires on a bent leg whose white boot reaches up to the waist.
- **8.0.3:** a skin piece of the neck at (12,-4..-3) joins the face through its 23 outline, so `chin_of` returns row -4, not -5. The V opens at chin+1 = row -3, two rows low. The sole's grey outline pixels touch no white fill, so they become suit outline (211, navy) instead of shoe.

### 4.2 What failed in my attempt (so it is not repeated)

- A pad rule by trim columns ("white past the trim near a glove is arm") painted skin over the chest of 2.0.0, 2.0.1, 3.0.0, 4.0.1, 13.0.1 and others. Reason: the plate is often wider than its trim, and gloves sit beside it. I rejected this at 3:54 PM. Any arm rule must work by the limb's shape outside the torso window, never by color (me, 3:54 PM).
- The collar-bar rule alone (bar = chest) gave 13.0.x one gi row only. The fist still covers the chest, so it does not answer "torso all skin".

### 4.3 One body per pose (decision 1, not shipped)

- Set 59 against set 56 under the chin: 177 of 260 shared keys match at the same position. 219 match when a shift of up to 2 px is allowed (31 keys at (-1,0), for example the whole SSJ walk 1.0.x and run 13.0.0-13.0.2; 12.1.x at (0,2); 18.1.1-18.1.6 at (0,1)). 16 keys (anim 21) exist in set 59 only. Script: `shared-body-1240-work\bodydiff2.py`.
- Near misses: 0.2.x, 0.3.x and 8.0.3 differ by 1 px, 1.1.0 by 7 px (collar), 2.1.0 by 4 px, 13.0.3 by 10 px (the glove outline above).
- A shared body with a vertical shift moves the sash row at screen position against the base, so it would need the frame placed at the base position.

### 4.4 Sash rows and the detransform (3:34 PM)

- **Sequence:** from SSJ2, B (or 0 EP) sends message 0x24, the revert state. It plays anim 21 of the current set (set 159, 21.d.0 to 21.d.3: gold, dim gold, brown, black). Then the form becomes entry 2 and set 157 shows its idle 0.d.0. Source: `docs\research\re-forms.md` (0x24 revert, anim 21 row +0x19C) and RE-BIBLE row 125.
- **Measured on the r12 art folders at screen position (record dx/dy applied):**

| Step | Sash row | Sash columns (d0) |
|---|---|---|
| 159 idle 0.0.0 (power-pose golden) | -2 | 4-10 |
| 159 21.0.0, 21.0.1, 21.0.2 | -2 | 5-11 |
| 159 21.0.3 (black hair) | **-1** | 5-11 |
| 157 idle 0.0.0 | -2 | 5-11 |

  - In every dir, 21.d.3 puts the sash one row lower than 21.d.0-2 and than the base idle. Set 158 21.d.3 is the same. During the revert the sash drops 1 row at the last frame, then jumps back up when the base idle shows. This is the most likely cause of my "sash shifts" (CONFIRMED for the drop; that this is what I saw is LIKELY).
  - Dirs 0 and 1: the 159 idle sash starts 1 px left of the revert frames (4-10 against 5-11), a 1 px sideways step when the revert starts. Dir 2: 159 idle 5-10 against 5-11.
- **Goldens at screen position (report only, nothing edited):** all put the sash on row -2. In d0 the SSJ golden body is 1 px left of the base golden (sash 4-10 against 5-11). d1, d2 and d3 are equal. My std-idle mockup (`work_r3\idle_std\ssj2_std_d*.png`) has the SSJ golden's rows and columns.

---

## 5. Files

- Kept on purpose: `art\gi_rage\` (3:15 PM step 1).
- Work folder `archive\2026-10-17-gi-art-rounds\shared-body-1240-work\`: `before\` (r12 backup), `gi_art_wip_cancelled.py`, probe scripts (`bodydiff.py`, `bodydiff2.py`, `parts.py`, `padprobe.py`, `zt.py`, `zrow.py`, `ba.py`, `dw.py`, `cmpart.py`, `runw.py`), the work-in-progress art in `art\` (not used by any build), and the work sheets `z_*.png` and `b*.png`. In sheets `b1` to `b9`, the column labeled "now" is work in progress from the cancelled rules, not a result.
- Nothing written under `data\`. No ROM in `builds\` written. No golden file edited or added. Python files I wrote are LF, no byte order mark.
