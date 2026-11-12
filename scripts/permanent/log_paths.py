r"""
log_paths.py - Every LOG folder root the build, the tools and the tests read or write, in one place.

Usage:   import log_paths    (scripts\permanent on sys.path, as for every tool, patch and test)
         log_paths.ART / "gi_base", log_paths.BUILDS / "log2_poc_r39.gba"
Rules:   A folder move is a one-line change here. Names inside a root (gi_base, cell_aura\scale_15, golden, ...)
         stay as they are: the code joins them below the root.
"""
from pathlib import Path

# ===== LOG root =====
ROOT = Path(__file__).resolve().parents[2]

# ===== art =====
ART = ROOT / "art"                                               # gi frames, aura, HUD icons, golden, locks
HAND_FIXES = ART / "hand-fixes"                                  # per-frame hand fixes and their snapshots
PORTRAIT_SOURCES = ART / "portrait-sources"                      # portrait remasters and my edits
SPRITES = ART / "vanilla-sets"                                   # vanilla sprite sets exported from the base ROM
ART_TABLES = ART / "tables"                                      # portraits.json, palette.json (inject tool)

# ===== builds and saves =====
BUILDS = ROOT / "builds"                                         # every build ROM with its .sav and states
TEST_ROMS = ROOT / "scratch" / "test-roms"                       # ROMs the tests rebuild on every run
SAVES = ROOT / "test-data" / "saves"                             # save files the tests read
HUD_KI_MOCKUPS = BUILDS / "mockups" / "2026-10-24-hud-ki"        # ki HUD trial ROMs (test_bf_hud)

# ===== docs and tools =====
R35_BRIEF = ROOT / "docs" / "tasks" / "2026-10-23-r35-build" / "r35.md"  # test_superperfect_cell reads its text
DISASM = ROOT / "scripts" / "permanent" / "disasm"               # own disassembler (codemap, listing, symbols)

# ===== the byte exact disassembly repos (read only; outside the LOG root) =====
GITHUB = ROOT.parents[2] / "GitHub"                              # C:\Users\<me>\Documents\GitHub
DISASM_REPO = GITHUB / "legacyofgoku2-disasm"                    # THE tree: RAM_LEDGER, CODE_INDEX, build\code
GNU_REPO = GITHUB / "legacyofgoku2-gnu"                          # STALE, measured 2026-11-05: read nothing from
#   its build\code. 1333 files against the disasm repo's 1476, 154 missing function starts, and 29 of the 1090
#   shared starts have a LONGER body because they bundle code the disasm repo has since split out. Only
#   scripts\permanent\disasm\compare_code_trees.py may read it, to re-measure the gap.
#   The gap runs BOTH WAYS by filename, measured 2026-11-06, and the disasm tree still loses nothing: 103
#   code_<addr>.s files exist only in gnu, 101 of them are in the disasm CODE_INDEX under a FUNCTION name,
#   and the last 2 (0x08003AFE, 0x080042EA) have zero references in the whole disasm tree and decode as
#   garbage, so they are data the gnu tree mis-decoded as code. A missing code_<addr>.s is therefore never
#   proof a function is absent: look it up in CODE_INDEX.md, which is what whatis.py does.
