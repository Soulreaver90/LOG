r"""
masters.py - The two master ROM SHA-1 pins, in one place.

Why:     the allocator bumps through one free region, so a module that changes size moves every later
         allocation and both masters get a new SHA-1 with no build list change. The dev hash used to sit
         in three test files, so a re-pin reached one file and missed two.
Rule:    changing a value here is a deliberate act. Name the build that moved it in the same edit.
         Never read these from docs\build-log.md. The build writes that log, so a build checked against
         it only agrees with itself. The pin is a hand edited tripwire. That is its whole job.
Use:     from tests import masters, then masters.GOLDEN or masters.DEV.
Moved:   2026-11-13, by moving Goku's Super Saiyan set from the chamber door record to the
         chamber exit record. The insert grew two records, so every later allocation shifted.
"""

GOLDEN = "778ccff59eddf7d34f432ece7e9a929595b2425f"     # build_list.txt, the golden master (2026-11-13)
DEV = "49cdfd3c172d734956d74ecb6c6419d1a301da6e"        # build_list_dev.txt, the dev master (2026-11-13)
