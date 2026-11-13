r"""
masters.py - The two master ROM SHA-1 pins, in one place.

Why:     the allocator bumps through one free region, so a module that changes size moves every later
         allocation and both masters get a new SHA-1 with no build list change. The dev hash used to sit
         in three test files, so a re-pin reached one file and missed two.
Rule:    changing a value here is a deliberate act. Name the build that moved it in the same edit.
         Never read these from docs\build-log.md. The build writes that log, so a build checked against
         it only agrees with itself. The pin is a hand edited tripwire. That is its whole job.
Use:     from tests import masters, then masters.GOLDEN or masters.DEV.
"""

GOLDEN = "acf1b15f46628255bdf00d025464b807ce7410a9"     # build_list.txt, the golden master (r41, 2026-10-31)
DEV = "ffbd2bfc766f7766d6ebe8c0f1905a53e6c4ce07"        # build_list_dev.txt, the dev master (r41, 2026-10-31)
