r"""
log_paths.py - Every LOG folder the build, the tools and the tests read or write, named ONCE, here.

Usage:   import log_paths    (scripts\permanent on sys.path, as for every tool, patch and test)
         log_paths.GI_BASE, log_paths.BUILDS / "log2_poc_r39.gba"
Rule:    code outside this file never spells a folder name. A folder move is a one-line change here.
         tests\test_no_folder_literals.py holds that rule and names its own exceptions.
Joins:   a file name below a folder stays at the use site (GOLDEN / "golden_gi_ssj2_d0.png"): a file is
         not a folder. A folder name needed as a bare string is FOLDER.name, never a literal.
Rebase:  under(root, FOLDER) re-roots a folder on another tree, for a test fixture or a temp copy.
         It follows the constant, so a move reaches the fixtures too.
"""
from pathlib import Path

# ===== LOG root =====
ROOT = Path(__file__).resolve().parents[2]

# ===== the roots =====
ART = ROOT / "art"                                               # every pixel we own, port or export
BUILDS = ROOT / "builds"                                         # every build ROM with its .sav and states
DATA = ROOT / "data"                                             # untouchable inputs: base ROMs, his saves
DOCS = ROOT / "docs"                                             # writing that outlives a task
SCRIPTS = ROOT / "scripts"                                       # the tools and the one-time task scripts
SCRATCH = ROOT / "scratch"                                       # throwaway, deletable without asking
TEST_DATA = ROOT / "test-data"                                   # small fixed inputs the tests read

# ===== data: inputs, never written =====
ROMS = DATA / "roms"                                             # the base cartridges
BASE_ROM = ROMS / "Dragon Ball Z - The Legacy of Goku II (USA).gba"     # THE base of every build
BF_ROM = ROMS / "Dragon Ball Z - Buu's Fury (USA).gba"                  # the art and HUD source
REFERENCE = DATA / "reference"                                   # reference images he supplied

# ===== art: our own and ported frames =====
CHARACTERS = ART / "characters"                                 # one folder per character
ART_REFERENCE = ART / "reference"                              # vanilla rips and review sheets
ART_UI = ART / "ui"                                            # HUD icon blobs and bar art
SHEETS = ART_REFERENCE / "sheets"                              # the loose review sheets
GOHAN_ART = CHARACTERS / "gohan"
PORTRAITS = ART / "portraits"                                    # exported vanilla portraits
ANIM = ART_REFERENCE / "anim"                                              # animation review strips (one folder per form)
ANIM_COMPARE = ANIM / "compare"                                  # the transform comparison strip
BASE_AUDIT = ART_REFERENCE / "base-audit"                                  # the gi base audit sheets
BASE_AUDIT_APPROVED = BASE_AUDIT / "approved"                    # frames he approved (patches.gi_base_audit)
CELL_AURA = CHARACTERS / "cell" / "aura"                                    # Super Perfect Cell aura frames
CELL_AURA_15 = CELL_AURA / "scale_15"                            # the scale the patch ships
GOLDEN = GOHAN_ART / "golden"                                          # his own finished frames: the gate for ours
HAND_FIXES = ART / "hand-fixes"                                  # per-frame hand fixes and their snapshots
KITS = ART / "kits"                                              # drawing kits: his working frames per task
LOCKS = ART / "locks"                                            # golden fingerprints (frame_lock)
PLATEAU_ART = ART / "maps" / "plateau"                                    # the plateau map document
PORTRAIT_KIT = PORTRAITS / "kit"                              # blank portrait slots for him to draw on
PORTRAIT_KIT_FRAMES = PORTRAIT_KIT / "frames"                    # the ring frame of each slot
PORTRAIT_KIT_BACKGROUNDS = PORTRAIT_KIT / "backgrounds"          # the background of each slot
PORTRAIT_KIT_PROOF = PORTRAIT_KIT / "proof"                      # the proof sheets of a kit round
PORTRAIT_SOURCES = PORTRAITS / "sources"                      # portrait remasters and my edits
SPRITES = ART_REFERENCE / "vanilla-sets"                                   # vanilla sprite sets exported from the base ROM
ART_TABLES = ART / "tables"                                      # portraits.json, palette.json (inject tool)
TABLE_PORTRAITS = ART_TABLES / "portraits"                       # the PNGs art_inject stages into the ROM
TRANSFORMATIONS = ART / "effects"                        # power-up effect frames
BF_REFERENCE = TRANSFORMATIONS / "_buus-fury-reference"          # exported from Buu's Fury
BF_AURA_FRAMES = BF_REFERENCE / "aura" / "frames"                # the gold aura frames, and our white recolour
BF_DUST_FRAMES = BF_REFERENCE / "dust"                           # the ground dust frames
TRUNKS_TANK = CHARACTERS / "trunks" / "tank"                                # the Trunks tank top set
WORK = ART / "work"                                              # old-method frames kept for before and after

# --- gi: one folder per form, and the rounds that are still build inputs ---
GI_BASE = GOHAN_ART / "gi_base"                                        # set 157
GI_RAGE = GOHAN_ART / "gi_rage"                                        # the rage body the rage aura is drawn on
GI_RAGE_AURA = GOHAN_ART / "gi_rage_aura"                              # set 160
GI_SSJ = GOHAN_ART / "gi_ssj"                                          # the first Super Saiyan round
GI_SSJ_V2 = GOHAN_ART / "gi_ssj_v2"                                    # set 158 today
GI_SSJ_V4 = GOHAN_ART / "gi_ssj_v4"                                    # the one-body round
GI_SSJ2 = GOHAN_ART / "gi_ssj2"                                        # the first Super Saiyan 2 round
GI_SSJ2_V2 = GOHAN_ART / "gi_ssj2_v2"                                  # the transplanted round
GI_SSJ2_REVIEW = GI_SSJ2_V2 / "review"                           # its review sheets (never shipped)
GI_SSJ2_V4 = GOHAN_ART / "gi_ssj2_v4"                                  # the one-body round
GI_SSJ2_AURA = GOHAN_ART / "gi_ssj2_aura"                              # set 159 today
GI_SSJ2_AURA_V4 = GOHAN_ART / "gi_ssj2_aura_v4"                        # the one-body round

# --- kits, one per drawing task ---
PICCOLO_POWERUP_KIT = KITS / "2026-11-12-piccolo-powerup"        # patches.piccolo_powerup_art
VEGETA_POWERUP_KIT = KITS / "2026-11-12-vegeta-powerup"          # patches.vegeta_zplus
VEGETA_HIS_EDIT_V2 = VEGETA_POWERUP_KIT / "his-edit" / "v2"      # the sway frames he redrew, round 2
VEGETA_BUILD_READY = VEGETA_HIS_EDIT_V2 / "build-ready"          # of those, the ones the patch may take

# --- portrait sources ---
REMASTER = PORTRAIT_SOURCES / "remaster"                         # one folder per remastered portrait
SUPERPERFECT = REMASTER / "superperfect"                         # Super Perfect Cell, id 52
SUPERPERFECT_OWNER = SUPERPERFECT / "owner"                      # his own drawing of it

# --- art folders with NO reader under scripts\permanent, measured 2026-11-13. Named here so the map is
#     complete, and left as comments so their names stay out of the literal test:
#     finale, gi_base_v2, gi_ssj_v5, gi_ssj2_aura_v5 (dead rounds), mockups, music, palettes, gi_rage,
#     portraits_* sheets at the art root, and "Owner Build - Trunks Tank", which is HIS live art:
#     no tool, test or patch may read, write or list it.

# ===== builds and saves =====
MOCKUPS = BUILDS / "mockups"                                     # trial ROMs, one folder per type
HUD_KI_MOCKUPS = MOCKUPS / "2026-10-24-hud-ki"                   # ki HUD trial ROMs (test_bf_hud)
CHAPTER_MOCKUPS = MOCKUPS / "2026-10-25-chapter-cards"           # chapter card trial ROMs (test_capture)
ARENA_MOCKUPS = MOCKUPS / "2026-11-05-ending-arena"              # ending arena trial ROMs (test_scene_probe)
ARENA_V3_MOCKUPS = MOCKUPS / "2026-11-06-arena-v3"               # arena save states (test_state_dump)
PICCOLO_Z_MOCKUPS = MOCKUPS / "2026-11-12-piccolo-z-start"       # Piccolo Z start trial ROMs
TEST_ROMS = SCRATCH / "test-roms"                                # ROMs the tests rebuild on every run
SAVES = TEST_DATA / "saves"                                      # save files the tests read

# ===== scripts =====
PERMANENT = SCRIPTS / "permanent"                                # the tools, patches, tests and build lists
ONE_TIME = SCRIPTS / "one-time"                                  # history: one folder per finished task
BUILD_LISTS = PERMANENT                                          # build_list*.txt, among the tools today
PATCHES = PERMANENT / "patches"                                  # the build modules
TESTS = PERMANENT / "tests"                                      # the suite
SCENE = PERMANENT / "scene"                                      # map and scene readers
DISASM = PERMANENT / "disasm"                                    # own disassembler (codemap, listing, symbols)
DISASM_DATA = DISASM / "data"                                    # its committed outputs, NOT the LOG data\ folder
MAP_EDITOR = PERMANENT / "map-editor"                            # the browser map editor
MAP_EDITOR_ASSETS = MAP_EDITOR / "assets"                        # exported tiles and palettes it serves
MAP_EDITOR_MAPS = MAP_EDITOR / "maps"                            # HIS saved maps
MAP_EDITOR_LIBRARY = MAP_EDITOR / "library"                      # his saved stamps
MAP_EDITOR_DELETED = MAP_EDITOR_LIBRARY / "deleted"              # a stamp he removed, kept whole
MAP_EDITOR_AUTOSAVE = MAP_EDITOR / "autosave"                    # the live document, overwritten
MAP_EDITOR_EDITOR = MAP_EDITOR / "editor"                        # the browser sources (js, mjs)

# ===== docs =====
RESEARCH = DOCS / "research"                                     # generated ROM research (map, scene, item)
TASKS = DOCS / "tasks"                                           # one folder per task: brief, report, rows
BIBLE = DOCS / "RE-BIBLE.md"                                     # every known ROM fact
BUILD_LOG = DOCS / "build-log.md"                                # one line per build, always appended
TOOL_INDEX = DOCS / "tool-index.md"                              # every reusable tool
R35_BRIEF = TASKS / "2026-10-23-r35-build" / "r35.md"            # test_superperfect_cell reads its text

# ===== scratch =====
CAPTURE = SCRATCH / "capture"                                    # emulator screenshots (emu\capture.py)
ROUNDTRIP = SCRATCH / "roundtrip"                                # map editor round trip output

# ===== outside the LOG root =====
GITHUB = ROOT.parents[2] / "GitHub"                              # C:\Users\<me>\Documents\GitHub
BIZHAWK = ROOT.parents[3] / "Downloads" / "BizHawk-2.11.1-win-x64"   # the emulator capture.py drives

# ===== the byte exact disassembly repos (read only) =====
DISASM_REPO = GITHUB / "legacyofgoku2-disasm"                    # THE tree: RAM_LEDGER, CODE_INDEX, build\code
DISASM_REPO_DOCS = DISASM_REPO / "docs"                          # RAM_LEDGER.csv, CODE_INDEX.md
DISASM_REPO_CODE = DISASM_REPO / "build" / "code"                # 1476 generated .s files, one per function
DISASM_REPO_BOUNDS = DISASM_REPO / "tools" / "code"              # FUNCTION_BOUNDS.csv
GNU_REPO = GITHUB / "legacyofgoku2-gnu"                          # STALE, measured 2026-11-05: read nothing from
GNU_REPO_CODE = GNU_REPO / "build" / "code"
#   its build\code. 1333 files against the disasm repo's 1476, 154 missing function starts, and 29 of the 1090
#   shared starts have a LONGER body because they bundle code the disasm repo has since split out. Only
#   scripts\permanent\disasm\compare_code_trees.py may read it, to re-measure the gap.
#   The gap runs BOTH WAYS by filename, measured 2026-11-06, and the disasm tree still loses nothing: 103
#   code_<addr>.s files exist only in gnu, 101 of them are in the disasm CODE_INDEX under a FUNCTION name,
#   and the last 2 (0x08003AFE, 0x080042EA) have zero references in the whole disasm tree and decode as
#   garbage, so they are data the gnu tree mis-decoded as code. A missing code_<addr>.s is therefore never
#   proof a function is absent: look it up in CODE_INDEX.md, which is what whatis.py does.


# ===== rebase a folder on another tree =====

def under(root, folder) -> Path:
    r"""`folder` re-rooted on `root`, keeping its shape below the root it belongs to.

    under(tmp, GI_SSJ2) is tmp\gi_ssj2 today. Move GI_SSJ2 and the fixture follows, so a test copy and
    the real folder can never drift apart. `root` stands in for ART, BUILDS or whichever root holds it.
    """
    folder = Path(folder)
    for base in (ART, BUILDS, DATA, DOCS, SCRIPTS, SCRATCH, TEST_DATA, ROOT):
        if base in folder.parents:
            return Path(root) / folder.relative_to(base)
    raise ValueError(f"not a folder under a LOG root: {folder}")
