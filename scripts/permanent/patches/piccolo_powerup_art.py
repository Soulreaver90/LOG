r"""
piccolo_powerup_art.py - Patch: set 104 (Super Namek) gains the power-up animation the owner drew for it.

Usage:   py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_piccolo_art.txt
         --out builds\mockups\2026-11-12-powerup-art\log2_piccolo_art_v1.gba
Input:   the ROM after the dev master, and the owner's four frames in art\kits\2026-11-12-piccolo-powerup
         (read, never written). File offsets and the frame headers in alloc.notes["piccolo_powerup_art"].
API:     apply(rom, alloc) -> None.
Method:  Set 104's anim 9 row is four null words in the base ROM and in the dev master. The record lookup
         @0x0800775A indexes the animation table by number with no existence test (bible B0041), so a
         power-up on set 104 follows a null record list and the game crashes. This writes the row: four
         raw type 0 frames and one record list that all four directions name, through vegeta_zplus's
         write_anim_row, which copies the record geometry from set 103's own anim 9 and refuses a
         mismatch. Set 103 (base Piccolo) is the turban and cape drop, his vanilla Z, and is untouched.
Scope:   ART ONLY. This adds no appearance entry, no form object, no portrait and no unlock, so nothing
         in the game reaches the new row yet. Piccolo Z+ itself is a separate task, and it needs this
         row to exist before a power-up on set 104 can play at all.
Rules:   Every check runs before the first write, so the module cannot run out of order or twice. The
         only base ROM bytes it changes are set 104's 16 byte anim 9 row; everything else is appended
         in the expansion area. No module file of the two masters is edited, so both master SHA-1s
         are unchanged. tests\test_piccolo_powerup_art.py proves the row against the owner's own PNGs.
"""
import log_paths
from patches.vegeta_zplus import POWER_UP, anim_row, hand_frames, plan_anim_frames, write_anim_row

# ===== constants =====
NAMEK_SET, BASE_SET = 104, 103          # Super Namek takes the row; base Piccolo lends its shape only
KIT = log_paths.PICCOLO_POWERUP_KIT
POWER_UP_PNGS = tuple(KIT / f"P_Frame{n}.png" for n in (1, 2, 3, 4))   # his order, and his_motion.gif's


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    if "piccolo_powerup_art" in alloc.notes:
        raise ValueError("piccolo_powerup_art already ran")
    frames = hand_frames(rom, POWER_UP_PNGS)
    plan_anim_frames(rom, NAMEK_SET, BASE_SET, frames, POWER_UP)        # checks, before any write
    before = anim_row(rom, BASE_SET, POWER_UP)
    note = write_anim_row(rom, NAMEK_SET, BASE_SET, frames, alloc, POWER_UP)
    if anim_row(rom, BASE_SET, POWER_UP) != before:
        raise ValueError(f"set {BASE_SET}'s own power-up row moved: the cape drop must not change")
    alloc.notes["piccolo_powerup_art"] = note
