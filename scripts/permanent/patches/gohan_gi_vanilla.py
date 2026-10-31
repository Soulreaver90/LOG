r"""
gohan_gi_vanilla.py - Patch: the golden master relocates Gohan's sets 157-160 and leaves the pixels vanilla.

Usage:   py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list.txt --out <new .gba>
Input:   the base ROM only. This patch opens no art folder, so a clone with no gi art still builds the master.
API:     apply(rom, alloc) -> None; notes in alloc.notes["gohan_gi"], the same six keys patches.gohan_gi
         publishes (appearance_copy, set_table, set_157, set_158, set_159, set_160). 17 modules read them.
Method:  patches.gohan_gi.apply_sets(rom, alloc, art=False). Every relocation, pointer and script edit of
         gohan_gi runs. Only the pixels differ: each new set takes the records and the frames of its own
         vanilla layout set (157 from 56, 158 and 159 from 59, 160 from 58).
         Sets 159 and 160 still publish 6 anim 0 records per dir, because the ssj2_idle hook stores
         body * 3 + shape and would otherwise run past the end of the list. The 4 added records per dir repeat
         the vanilla idle bodies: index k shows vanilla body k // 3, so the idle holds each body for 3 shapes.
Rules:   Me, 2026-10-31, the vanilla fill: no pixel is invented and nothing is copied out of art\golden\.
         Cost he accepted: the golden master has no aura cycle, and Gohan looks vanilla in every form.
         Line 1 of build_list.txt. Line 1 of build_list_dev.txt is gohan_gi, which paints the art instead.
         Source: docs\tasks\2026-10-31-golden-dev-split\split-brief.md (ADDENDUM) and golden-dev-split.md.
"""
from patches.gohan_gi import apply_sets


def apply(rom: bytearray, alloc) -> None:
    apply_sets(rom, alloc, art=False)
